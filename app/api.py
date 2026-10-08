"""API REST (FastAPI) : persos/stuff, stock, recettes, optimisation, suivi de build.

- Docs : http://localhost:8000/docs
- Persos & stuff : http://localhost:8000/ui/
- Suivi ressources / build : http://localhost:8000/ui/build.html
"""
from __future__ import annotations

import contextlib
import json
import logging
import os
import time
import urllib.request
from dataclasses import asdict
from fastapi import Body, FastAPI, Query
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from typing import Dict, List, Optional

from app.core.optimizer import (
    compute_craftable,
    compute_near_craftable,
    resolve_crafting,
    simulate_crafting_plan,
)
from app.core.repop_monitor import get_monitor
from app.db.build_repo import (
    get_build_resources,
    get_build_targets,
    get_build_trees,
    set_build_targets,
    set_manual,
    update_target_quantity,
)
from app.db.characters_repo import get_roster
from app.db.connection import close_pool, init_pool, transaction
from app.db.repop_repo import get_map_history, record_appearance
from app.db.repositories import (
    get_accounts_summary,
    get_all_recipes,
    get_bank_detail,
    get_bank_status,
    get_consolidated_summary,
    get_full_stock,
    get_items_metadata,
    get_items_with_stat,
    replace_bank_inventory,
    upsert_market_prices,
    upsert_bank_inventory,
)


def _wire_repop_persistence() -> None:
    """Recharge l'historique des apparitions (heatmap durable) et branche la
    persistance sur le moniteur. Tolérant : si la table n'existe pas encore
    (applique sql/007_repop_history.sql), on log et on continue sans persistance."""
    monitor = get_monitor()
    try:
        with transaction(commit=False) as cur:
            loaded = monitor.load_history(get_map_history(cur))
        logging.getLogger("api").info("Historique repop rechargé : %d maps.", loaded)
    except Exception:
        logging.getLogger("api").warning(
            "Historique repop non chargé (table map_appearances absente ? "
            "applique sql/007_repop_history.sql).", exc_info=True)

    def _persist(ap: dict) -> None:
        try:
            with transaction() as cur:
                record_appearance(cur, ap["map_id"], ap["ts"], ap["is_target"],
                                   ap["is_archi"], ap["monster_ids"], ap["coord"], ap["zone"])
        except Exception:
            logging.getLogger("api").debug("record_appearance a échoué.", exc_info=True)

    monitor.on_appearance = _persist


def _persist_bank(inventory: Dict[int, int]) -> None:
    """Snapshot de banque ``EL`` capté en live -> remplace INTÉGRALEMENT la
    banque du compte ``main`` (setup mono-compte). Même chemin que
    ``scripts.ingest_pcap``, mais déclenché automatiquement par le watcher dès
    que la banque est ouverte en jeu. Tolérant : une erreur n'arrête pas le
    watcher."""
    if not inventory:
        return
    try:
        with transaction() as cur:
            n = replace_bank_inventory(cur, inventory, "main")
        logging.getLogger("api").info("Banque auto-sync (live) : %d objets.", n)
    except Exception:
        logging.getLogger("api").warning("Auto-sync banque échoué.", exc_info=True)


def _persist_prices(prices: Dict[int, int]) -> None:
    """Prix HDV (``EHP``/``EHl``) captés en live -> met à jour le prix marché des
    objets. Déclenché par le watcher dès que l'hôtel de vente est consulté en jeu.
    Tolérant : une erreur n'arrête pas le watcher."""
    if not prices:
        return
    try:
        with transaction() as cur:
            n = upsert_market_prices(cur, prices)
        logging.getLogger("api").info("Prix marché auto-sync (live) : %d objets.", n)
    except Exception:
        logging.getLogger("api").warning("Auto-sync prix échoué.", exc_info=True)


@contextlib.asynccontextmanager
async def lifespan(_app: FastAPI):
    init_pool()
    _wire_repop_persistence()
    # Suivi live des repops : si un dossier de captures est fourni, un watcher
    # ingère les fichiers du ring-buffer dumpcap (voir app.network.live_watch).
    stop_watcher = None
    live_dir = os.getenv("LIVE_CAPTURE_DIR")
    if live_dir:
        from app.network.live_watch import start_watcher
        stop_watcher = start_watcher(get_monitor(), live_dir,
                                     on_bank=_persist_bank, on_prices=_persist_prices)
    # Proxy d'échange (MITM, officiel) : si une cible upstream est fournie, on se
    # place entre le vrai client et le serveur de jeu pour injecter les échanges
    # (voir app.network.proxy). Désactivé par défaut (aucune variable -> None).
    _start_proxy()
    yield
    if stop_watcher is not None:
        stop_watcher.set()
    if _proxy is not None:
        _proxy.stop()
    close_pool()


# Proxy d'échange, instancié à la demande (PROXY_UPSTREAM_HOST défini).
_proxy = None


def _start_proxy() -> None:
    """Démarre le proxy MITM si ``PROXY_UPSTREAM_HOST`` est défini. Variables :
    PROXY_LISTEN_HOST (déf. 0.0.0.0), PROXY_LISTEN_PORT (déf. 443),
    PROXY_UPSTREAM_HOST (IP réelle du serveur de jeu), PROXY_UPSTREAM_PORT (déf. 443)."""
    global _proxy
    upstream = os.getenv("PROXY_UPSTREAM_HOST")
    if not upstream:
        return
    from app.network.proxy import DofusProxy
    _proxy = DofusProxy(
        listen_host=os.getenv("PROXY_LISTEN_HOST", "0.0.0.0"),
        listen_port=int(os.getenv("PROXY_LISTEN_PORT", "443")),
        upstream_host=upstream,
        upstream_port=int(os.getenv("PROXY_UPSTREAM_PORT", "443")),
    )
    try:
        _proxy.start()
    except OSError:
        logging.getLogger("api").error(
            "Proxy d'échange : impossible de binder %s:%s (port < 1024 -> admin requis ?).",
            os.getenv("PROXY_LISTEN_HOST", "0.0.0.0"), os.getenv("PROXY_LISTEN_PORT", "443"),
            exc_info=True)
        _proxy = None


app = FastAPI(title="Dofus Cockpit — Dofus Retro multibox", version="2.3.0", lifespan=lifespan)


@app.get("/")
def root():
    return RedirectResponse(url="/ui/")


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


# --- Persos & stuff ---------------------------------------------------------

@app.get("/roster")
def read_roster() -> List[dict]:
    with transaction(commit=False) as cur:
        return get_roster(cur)


# --- Banque / stock ---------------------------------------------------------

@app.get("/stock")
def read_stock(account: Optional[str] = Query(None)) -> List[dict]:
    with transaction(commit=False) as cur:
        return [asdict(s) for s in get_full_stock(cur, account)]


@app.get("/bank/detail")
def read_bank_detail(account: Optional[str] = Query(None)) -> List[dict]:
    """Banque enrichie (icône, type, niveau, qté, prix vendeur/marché/effectif,
    valeur de ligne) pour le tableau de bord banque. account=None -> agrégé."""
    with transaction(commit=False) as cur:
        return get_bank_detail(cur, account)


@app.get("/bank/status")
def read_bank_status() -> dict:
    """Statut express de la banque (page Démarrage) : nb objets, valeur, MAJ, prix."""
    with transaction(commit=False) as cur:
        return get_bank_status(cur)


@app.get("/accounts")
def read_accounts() -> List[dict]:
    with transaction(commit=False) as cur:
        return get_accounts_summary(cur)


@app.get("/summary")
def read_summary() -> List[dict]:
    with transaction(commit=False) as cur:
        return get_consolidated_summary(cur)


@app.get("/recipes")
def read_recipes() -> List[dict]:
    with transaction(commit=False) as cur:
        return [asdict(r) for r in get_all_recipes(cur)]


# --- Suivi de build ---------------------------------------------------------

@app.get("/build")
def read_build() -> List[dict]:
    with transaction(commit=False) as cur:
        return get_build_targets(cur)


@app.put("/build")
def write_build(targets: List[dict] = Body(..., description="[{item_id, quantity, label}]")) -> dict:
    with transaction() as cur:
        n = set_build_targets(cur, targets)
    return {"targets": n}


@app.put("/build/target")
def write_build_target(id: int = Body(...), quantity: int = Body(...)) -> dict:
    with transaction() as cur:
        update_target_quantity(cur, id, quantity)
    return {"id": id, "quantity": max(0, quantity)}


@app.put("/build/manual")
def write_build_manual(item_id: int = Body(...), quantity: int = Body(...)) -> dict:
    with transaction() as cur:
        q = set_manual(cur, item_id, quantity)
    return {"item_id": item_id, "quantity": q}


@app.get("/build/resources")
def read_build_resources(expand: bool = Query(False)) -> List[dict]:
    with transaction(commit=False) as cur:
        return get_build_resources(cur, expand)


@app.get("/build/tree")
def read_build_tree() -> List[dict]:
    """Arbre de craft de chaque cible (recette + sous-crafts en cascade)."""
    with transaction(commit=False) as cur:
        return get_build_trees(cur)


# --- Optimisation de craft --------------------------------------------------

def _enriched_craftable() -> List[dict]:
    with transaction(commit=False) as cur:
        stock = get_full_stock(cur)
        recipes = get_all_recipes(cur)
        meta = get_items_metadata(cur)
    rows: List[dict] = []
    for c in compute_craftable(recipes, stock):
        m = meta.get(c.result_item_id) or {}
        price = m.get("price") or 0
        d = asdict(c)
        d["result_type"] = m.get("type")
        d["result_level"] = m.get("level")
        d["unit_price"] = m.get("price")
        d["total_value"] = price * c.max_crafts
        rows.append(d)
    return rows


@app.get("/craftable")
def read_craftable(
        item_type: Optional[str] = Query(None, alias="type"),
        min_level: Optional[int] = Query(None, ge=0),
        max_level: Optional[int] = Query(None, ge=0),
        sort: str = Query("crafts", pattern="^(crafts|value|level|name)$"),
        limit: int = Query(100, ge=1, le=5000),
) -> List[dict]:
    rows = _enriched_craftable()
    if item_type:
        t = item_type.lower()
        rows = [d for d in rows if (d["result_type"] or "").lower() == t]
    if min_level is not None:
        rows = [d for d in rows if (d["result_level"] or 0) >= min_level]
    if max_level is not None:
        rows = [d for d in rows if (d["result_level"] or 0) <= max_level]
    keyfn = {
        "crafts": lambda d: -d["max_crafts"],
        "value": lambda d: -d["total_value"],
        "level": lambda d: -(d["result_level"] or 0),
        "name": lambda d: (d["result_name"] or "").lower(),
    }[sort]
    rows.sort(key=keyfn)
    return rows[:limit]


@app.get("/craftable/near")
def read_near_craftable(
        max_missing: int = Query(2, ge=1, le=10, alias="max_missing",
                                 description="Nb max de ressources DISTINCTES manquantes"),
        item_type: Optional[str] = Query(None, alias="type"),
        min_level: Optional[int] = Query(None, ge=0),
        max_level: Optional[int] = Query(None, ge=0),
        sort: str = Query("missing", pattern="^(missing|value|level|name)$"),
        include_ready: bool = Query(False, description="inclure aussi les recettes déjà fabricables (manque 0)"),
        limit: int = Query(100, ge=1, le=5000),
) -> List[dict]:
    """Recettes « à portée » : il manque au plus `max_missing` ressources
    distinctes. Chaque ligne liste les ressources qui manquent (nom + quantité).
    `include_ready=true` ajoute les recettes déjà fabricables (manque 0, avec
    `max_crafts`)."""
    with transaction(commit=False) as cur:
        stock = get_full_stock(cur)
        recipes = get_all_recipes(cur)
        meta = get_items_metadata(cur)
    rows: List[dict] = []
    for c in compute_near_craftable(recipes, stock, max_missing, include_ready):
        m = meta.get(c.result_item_id) or {}
        d = asdict(c)
        d["result_type"] = m.get("type")
        d["result_level"] = m.get("level")
        d["unit_price"] = m.get("price")
        d["icon"] = m.get("icon")
        rows.append(d)
    if item_type:
        t = item_type.lower()
        rows = [d for d in rows if (d["result_type"] or "").lower() == t]
    if min_level is not None:
        rows = [d for d in rows if (d["result_level"] or 0) >= min_level]
    if max_level is not None:
        rows = [d for d in rows if (d["result_level"] or 0) <= max_level]
    keyfn = {
        "missing": lambda d: (d["missing_kinds"], d["missing_total"], (d["result_name"] or "").lower()),
        "value": lambda d: -(d["unit_price"] or 0),
        "level": lambda d: -(d["result_level"] or 0),
        "name": lambda d: (d["result_name"] or "").lower(),
    }[sort]
    rows.sort(key=keyfn)
    return rows[:limit]


@app.get("/craftable/by-stat")
def read_craftable_by_stat(
        stat: str = Query("res_neutre"),
        percent: Optional[bool] = Query(None),
        sort: str = Query("stat", pattern="^(stat|crafts|value|level)$"),
        limit: int = Query(100, ge=1, le=5000),
) -> List[dict]:
    with transaction(commit=False) as cur:
        stock = get_full_stock(cur)
        recipes = get_all_recipes(cur)
        meta = get_items_metadata(cur)
        stats = get_items_with_stat(cur, stat)
    rows: List[dict] = []
    for c in compute_craftable(recipes, stock):
        entries = stats.get(c.result_item_id)
        if not entries:
            continue
        m = meta.get(c.result_item_id) or {}
        for e in entries:
            if percent is not None and e["is_percent"] != percent:
                continue
            rows.append({
                "result_item_id": c.result_item_id, "result_name": c.result_name,
                "result_type": m.get("type"), "result_level": m.get("level"),
                "max_crafts": c.max_crafts, "limiting_item_name": c.limiting_item_name,
                "stat": stat, "is_percent": e["is_percent"],
                "value_min": e["value_min"], "value_max": e["value_max"],
                "unit_price": m.get("price"), "total_value": (m.get("price") or 0) * c.max_crafts,
            })
    keyfn = {
        "stat": lambda d: -d["value_max"], "crafts": lambda d: -d["max_crafts"],
        "value": lambda d: -d["total_value"], "level": lambda d: -(d["result_level"] or 0),
    }[sort]
    rows.sort(key=keyfn)
    return rows[:limit]


@app.get("/types")
def read_types() -> List[dict]:
    counts: Dict[str, int] = {}
    for d in _enriched_craftable():
        t = d["result_type"] or "(inconnu)"
        counts[t] = counts.get(t, 0) + 1
    return sorted(({"type": t, "count": n} for t, n in counts.items()), key=lambda x: -x["count"])


@app.get("/plan")
def read_plan(cascade: bool = Query(False)) -> dict:
    with transaction(commit=False) as cur:
        stock = get_full_stock(cur)
        recipes = get_all_recipes(cur)
    plan = resolve_crafting(recipes, stock) if cascade else simulate_crafting_plan(recipes, stock)
    return asdict(plan)


@app.put("/bank")
def write_bank(
        inventory: Dict[int, int] = Body(...),
        account: str = Query("main"),
        replace: bool = Query(True),
) -> dict:
    with transaction() as cur:
        count = (replace_bank_inventory(cur, inventory, account) if replace
                 else upsert_bank_inventory(cur, inventory, account))
    return {"account": account, "updated": count, "mode": "replace" if replace else "upsert"}


# --- Suivi live des repops de monstres --------------------------------------

@app.get("/live/state")
def read_live_state() -> dict:
    """État courant du moniteur : groupes par map + compte à rebours de repop."""
    from app.network import protocol
    snap = get_monitor().snapshot(time.time())
    snap["exit_cells"] = protocol.EXIT_CELLS
    return snap


@app.post("/live/ingest")
def live_ingest(path: str = Query(..., description="Chemin d'une capture .pcapng côté serveur")) -> dict:
    """Ingest une capture Wireshark dans le moniteur (import paresseux de scapy)."""
    from app.network.pcap_feed import feed_pcap
    return feed_pcap(get_monitor(), path)


@app.post("/live/reset")
def live_reset() -> dict:
    """Vide l'état du moniteur (repart de zéro)."""
    get_monitor().reset()
    return {"status": "reset"}


@app.post("/live/names/reload")
def live_reload_names() -> dict:
    """Recharge les noms de monstres depuis data/monster_names.json (à chaud,
    après un scripts.fetch_monster_names — pas besoin de redémarrer)."""
    from app.network import protocol
    return {"monster_names": protocol.reload_monster_names()}


@app.post("/live/maps/coord")
def set_map_coord(map_id: int = Body(...), x: int = Body(...), y: int = Body(...)) -> dict:
    """Enregistre les coordonnées [x, y] d'une map (le protocole ne donne que
    l'id interne). Persiste dans data/map_coords.json puis recharge à chaud."""
    from app.network import protocol
    path = "data/map_coords.json"
    coords: Dict[str, list] = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            coords = json.load(fh)
    coords[str(map_id)] = [x, y]
    with open(path, "w", encoding="utf-8") as fh:
        json.dump({k: coords[k] for k in sorted(coords, key=int)}, fh, ensure_ascii=False, indent=2)
    protocol.reload_map_coords()
    return {"map_id": map_id, "coord": [x, y], "known": len(protocol.MAP_COORDS)}


@app.post("/live/maps/reload")
def reload_map_coords() -> dict:
    """Recharge coords + zones à chaud (après scripts.import_map_coords)."""
    from app.network import protocol
    return {"coords": protocol.reload_map_coords(), "zones": protocol.reload_map_zones()}


@app.post("/live/exitcell")
def set_exit_cell(direction: str = Body(...), cell: int = Body(...)) -> dict:
    """Enregistre la cellule de sortie de map (0..559) observée en jeu pour une
    direction cardinale (N/S/E/O). La grille étant identique sur toutes les maps,
    une seule valeur par direction suffit. Persiste dans data/map_exit_cells.json."""
    from app.network import protocol
    direction = direction.strip().upper()
    if direction not in ("N", "S", "E", "O"):
        return {"ok": False, "reason": "direction invalide (attendu N/S/E/O)"}
    path = "data/map_exit_cells.json"
    cells: Dict[str, int] = {}
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            cells = json.load(fh)
    cells[direction] = cell
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(cells, fh, ensure_ascii=False, indent=2)
    protocol.reload_exit_cells()
    return {"ok": True, "direction": direction, "cell": cell, "exit_cells": protocol.EXIT_CELLS}


@app.get("/live/route")
def live_route(
        maps: Optional[str] = Query(None, description="ids csv à couvrir (prioritaire)"),
        zone: Optional[str] = Query(None, description="nom de sous-zone à couvrir"),
        accounts: int = Query(1, ge=1, le=8),
) -> dict:
    """Tournée optimisée (serpentin) sur un ensemble de maps. Sélection : `maps`
    explicite, sinon toute la `zone`, sinon auto (maps chaudes du moniteur, ou à
    défaut les zones des comptes actifs). `accounts` découpe en segments."""
    from app.core.route import plan_route, split_route
    from app.network import protocol

    if maps:
        ids = [int(x) for x in maps.split(",") if x.strip().lstrip("-").isdigit()]
    elif zone:
        ids = [mid for mid, z in protocol.MAP_ZONES.items() if z == zone]
    else:
        snap = get_monitor().snapshot(time.time())
        ids = [m["map_id"] for m in snap["maps"] if m.get("target_hits") or m.get("archi_hits")]
        if not ids:
            zones = {a["zone"] for a in snap["accounts"] if a.get("zone")}
            ids = [mid for mid, z in protocol.MAP_ZONES.items() if z in zones]

    coords = {mid: tuple(protocol.MAP_COORDS[mid]) for mid in set(ids) if mid in protocol.MAP_COORDS}
    if not coords:
        return {"count": 0, "total_steps": 0, "connected": True, "stops": [], "segments": []}

    def _stop(mid: int) -> dict:
        return {"map_id": mid, "coord": list(protocol.MAP_COORDS.get(mid, [])) or None,
                "zone": protocol.MAP_ZONES.get(mid)}

    plan = plan_route(coords)
    segments = split_route(plan["order"], accounts)
    return {
        "count": len(coords),
        "total_steps": plan["total_steps"],
        "loop_back_steps": plan["loop_back_steps"],
        "connected": plan["connected"],
        "n_components": plan["n_components"],
        "stops": [_stop(m) for m in plan["order"]],
        "segments": [[_stop(m) for m in seg] for seg in segments],
    }


def _moonbot_name(monster_id: int) -> Optional[str]:
    """Nom d'un monstre via l'API moon-bot (best-effort, None si échec)."""
    url = f"https://wiki.moon-bot.io/api/monster/{monster_id}.json"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Dofus-tool/1.0"})
        with urllib.request.urlopen(req, timeout=10) as r:
            name = (json.loads(r.read().decode("utf-8", "ignore")) or {}).get("name")
        return name.strip() if isinstance(name, str) and name.strip() else None
    except Exception:  # noqa: BLE001
        return None


@app.post("/live/archi")
def add_archi(id: int = Body(..., embed=True), remove: bool = Body(False, embed=True)) -> dict:
    """Marque (ou retire avec remove=true) un id de monstre comme ARCHIMONSTRE.
    Persiste data/archi_ids.json, tente de récupérer son nom (moon-bot), recharge
    tout à chaud. L'archi a un id distinct -> il est ensuite flaggé sur la carte."""
    from app.network import protocol
    path = "data/archi_ids.json"
    ids: List[int] = []
    if os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            ids = [int(x) for x in json.load(fh)]
    ids = [i for i in ids if i != id] + ([] if remove else [id])
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(sorted(set(ids)), fh, ensure_ascii=False)
    protocol.reload_archi_ids()

    name = None
    if not remove:
        name = _moonbot_name(id)
        if name:
            names_path = "data/monster_names.json"
            names: Dict[str, str] = {}
            if os.path.exists(names_path):
                with open(names_path, encoding="utf-8") as fh:
                    names = json.load(fh)
            names[str(id)] = name
            with open(names_path, "w", encoding="utf-8") as fh:
                json.dump({k: names[k] for k in sorted(names, key=int)}, fh,
                          ensure_ascii=False, indent=2)
            protocol.reload_monster_names()
    return {"id": id, "name": name, "removed": remove,
            "archi_ids": sorted(protocol.ARCHI_IDS)}


@app.get("/route/path")
def route_path(fx: int = Query(...), fy: int = Query(...),
               tx: int = Query(...), ty: int = Query(...)) -> dict:
    """Pathfinding A -> B sur la grille de maps (BFS, adjacence Manhattan==1).

    Rend le chemin (liste de [x,y]), les directions cardinales à suivre, et la
    PROCHAINE direction (`next`) — c'est ce dont l'auto-clic a besoin à chaque map.
    `reachable=false` si start/goal hors grille ou pas de chemin par cases voisines.
    """
    from app.core.route import find_path, path_directions
    from app.network import protocol
    positions = {tuple(xy) for xy in protocol.MAP_COORDS.values()}
    path = find_path(positions, (fx, fy), (tx, ty))
    dirs = path_directions(path)
    return {
        "from": [fx, fy], "to": [tx, ty],
        "reachable": bool(path),
        "steps": len(dirs),
        "path": [list(p) for p in path],
        "directions": dirs,
        "next": dirs[0] if dirs else None,
    }


@app.get("/map/exit")
def map_exit(map_id: int = Query(...), dir: str = Query(...)) -> dict:
    """Cellule de sortie (0-559) d'une map dans une direction (N/S/E/O).

    Résolution par map (les 4 sorties varient d'une map à l'autre — le Nord va
    de 21 à 25 selon la map) :
      1. `learned`  — apprise en direct par l'ExitLearner au fil des déplacements
                      (bot OU joueur), la plus fréquente observée pour cette map.
      2. `file`     — data/map_exits.json (minée par tools/mine_exits.py).
      3. `default`  — case médiane de bord, repli tant que rien n'est appris.
    `source` indique d'où vient la valeur ; `known=false` seulement si direction
    inconnue."""
    path = "data/map_exits.json"
    exits: Dict[str, dict] = {}
    if os.path.exists(path):
        try:
            with open(path, encoding="utf-8") as fh:
                exits = json.load(fh)
        except Exception:  # noqa: BLE001
            exits = {}
    d = dir.strip().upper()
    from app.network.exit_learner import get_learner
    # 1) appris en direct (le plus précis, par map)
    cell = get_learner().get_exit(map_id, d)
    src = "learned"
    # 2) repli fichier miné
    if cell is None:
        cell = (exits.get(str(map_id)) or {}).get(d)
        src = "file" if cell is not None else src
    # 3) défaut : médianes de bord / sommets, tant que la sortie n'est pas apprise
    if cell is None:
        cell = {"N": 25, "S": 459, "E": 289, "O": 276}.get(d)
        src = "default" if cell is not None else "unknown"
    return {"map_id": map_id, "dir": d, "cell": cell,
            "known": cell is not None, "source": src}


# --- Échange via proxy MITM (émission de paquets, serveur officiel) ----------

@app.get("/proxy/connections")
def proxy_connections() -> dict:
    """Connexions proxifiées actuelles + perso identifié (via l'ASK d'entrée en
    jeu). Vide si le proxy n'est pas activé (PROXY_UPSTREAM_HOST non défini)."""
    if _proxy is None:
        return {"enabled": False, "connections": []}
    return {"enabled": True, "connections": [
        {"id": c.id, "character_id": c.character_id, "name": c.character_name,
         "identified": c.character_id is not None}
        for c in _proxy.connections()
    ]}


@app.post("/proxy/exchange")
def proxy_exchange(
        giver: str = Body(..., embed=True, description="perso donneur (nom ou id)"),
        receiver: str = Body(..., embed=True, description="perso receveur (nom ou id)"),
        items: Dict[int, int] = Body(..., embed=True,
                                     description="{item_id: quantité} à transférer"),
        kamas: int = Body(0, embed=True),
) -> dict:
    """Injecte un échange donneur -> receveur dans les connexions des deux vrais
    clients (les persos doivent être en jeu, même map, à portée). ``giver`` /
    ``receiver`` acceptent un id de perso (numérique) ou une sous-chaîne de nom."""
    if _proxy is None:
        return {"ok": False, "reason": "proxy désactivé (définis PROXY_UPSTREAM_HOST)"}
    from app.network.proxy import run_proxy_exchange

    def _key(v: str):
        return int(v) if str(v).lstrip("-").isdigit() else v

    return run_proxy_exchange(_proxy, _key(giver), _key(receiver),
                              {int(k): int(v) for k, v in (items or {}).items()}, kamas)


# --- Pilotage du walker (auto-clic) : file de jobs live.html <-> AutoIt -------

def _find_account(snap: dict, label: str, start: Optional[list]) -> Optional[dict]:
    """Retrouve le compte ciblé dans le snapshot. Priorité à la POSITION de
    départ (robuste aux labels homonymes), repli sur le label."""
    accs = snap.get("accounts", [])
    if start is not None:
        for a in accs:
            c = a.get("coord")
            if c and int(c[0]) == int(start[0]) and int(c[1]) == int(start[1]):
                return a
    for a in accs:
        if label and (a.get("name") == label or a.get("label") == label):
            return a
    return None


@app.post("/walk/goto")
def walk_goto(label: str = Body("", embed=True),
              fx: Optional[int] = Body(None, embed=True),
              fy: Optional[int] = Body(None, embed=True),
              tx: int = Body(..., embed=True),
              ty: int = Body(..., embed=True)) -> dict:
    """Enfile un déplacement pour le walker : amener un compte en [tx, ty].

    `fx,fy` = position de départ (celle du marqueur cliqué sur la carte) — sert à
    cibler le bon perso même si plusieurs partagent le label. À défaut, on résout
    par `label`. Vérifie l'atteignabilité sur la grille de maps avant d'enfiler."""
    from app.core.route import find_path
    from app.network import protocol
    from app.network.walk_jobs import get_store
    snap = get_monitor().snapshot(time.time())
    start = [fx, fy] if fx is not None and fy is not None else None
    acc = _find_account(snap, label, start)
    if acc is None or not acc.get("coord"):
        return {"ok": False, "reason": "compte introuvable/non positionné "
                                       "(bouge-le en jeu pour qu'il apparaisse)"}
    start = list(acc["coord"])
    positions = {tuple(xy) for xy in protocol.MAP_COORDS.values()}
    path = find_path(positions, tuple(start), (tx, ty))
    if not path:
        return {"ok": False, "reason": f"[{tx},{ty}] injoignable depuis "
                                       f"[{start[0]},{start[1]}] (grille)"}
    who = acc.get("name") or acc.get("label") or label
    job = get_store().submit(who, start, [tx, ty])
    return {"ok": True, "job": job, "start": start, "steps": len(path) - 1}


@app.get("/walk/job")
def walk_job() -> dict:
    """Le walker AutoIt interroge cet endpoint : job courant (ou vide).
    Chaque appel sert de battement de coeur (heartbeat) du walker."""
    from app.network.walk_jobs import get_store
    store = get_store()
    store.mark_poll(time.time())
    return {"job": store.current()}


@app.post("/walk/status")
def walk_status(job_id: int = Body(..., embed=True),
                state: str = Body("", embed=True),
                message: str = Body("", embed=True),
                x: Optional[int] = Body(None, embed=True),
                y: Optional[int] = Body(None, embed=True),
                map_id: Optional[int] = Body(None, embed=True)) -> dict:
    """Le walker rapporte son avancement (état + position courante)."""
    from app.network.walk_jobs import get_store
    pos = [x, y] if x is not None and y is not None else None
    job = get_store().update(job_id, state=state or None,
                             message=message or None, pos=pos, map_id=map_id)
    return {"ok": job is not None, "job": job}


@app.post("/walk/cancel")
def walk_cancel() -> dict:
    """live.html annule le job en cours (le walker le voit au prochain poll)."""
    from app.network.walk_jobs import get_store
    return {"job": get_store().cancel()}


@app.get("/walk/state")
def walk_state() -> dict:
    """live.html suit l'avancement du job + l'état en ligne du walker."""
    from app.network.walk_jobs import get_store
    store = get_store()
    return {"job": store.current(),
            "walker_online": store.walker_online(time.time())}


@app.post("/walk/focus")
def walk_focus(name: str = Body(..., embed=True)) -> dict:
    """live.html demande d'activer la fenêtre d'un perso (clic sur son marqueur).
    Le walker lit cette demande à son prochain poll et fait le WinActivate."""
    from app.network.walk_jobs import get_store
    return {"focus": get_store().set_focus(name)}


@app.get("/walk/focus")
def walk_focus_get() -> dict:
    """Le walker interroge la demande de focus courante (dédup par id côté walker)."""
    from app.network.walk_jobs import get_store
    return {"focus": get_store().focus()}


@app.post("/walk/sweep")
def walk_sweep(names: List[str] = Body(..., embed=True)) -> dict:
    """Demande au walker d'activer CHAQUE fenêtre de `names` une par une (le
    pop-up envoie l'ordre voulu, ex. inverse de la barre des tâches)."""
    from app.network.walk_jobs import get_store
    names = [n for n in (names or []) if n and n.strip()]
    sw = get_store().set_sweep(names)
    return {"ok": True, "count": len(names), "sweep": sw}


@app.get("/walk/sweep")
def walk_sweep_get() -> dict:
    """Le walker lit le balayage courant (dédup par id côté walker)."""
    from app.network.walk_jobs import get_store
    return {"sweep": get_store().sweep()}


@app.post("/walk/windows")
def walk_windows(names: List[str] = Body(..., embed=True)) -> dict:
    """Le walker rapporte la liste des fenêtres Dofus ouvertes (noms de perso).
    Source réelle des clients pour board.html (le sniffer ne voit que ceux qui
    bougent)."""
    from app.network.walk_jobs import get_store
    n = get_store().report_windows(names, time.time())
    return {"ok": True, "count": n}


# --- Donjons : enchaînement de salles (farm multi-comptes) ------------------
# Un donjon = suite ordonnée de salles reliées par une cellule de transition.
# La page dungeon.html capture cette suite, puis fait sortir toute l'équipe
# d'une salle vaincue d'un clic (combat manuel pour l'instant).

@app.get("/dungeon")
def list_dungeons() -> List[dict]:
    from app.network import dungeon_store
    return dungeon_store.list_dungeons()


@app.get("/dungeon/transitions")
def dungeon_transitions(limit: int = Query(50, ge=1, le=500)) -> dict:
    """Dernières transitions de map observées (from -> to via cell). Sert à
    auto-remplir les cellules de sortie pendant la capture d'un donjon."""
    from app.network.exit_learner import get_learner
    return {"transitions": get_learner().recent_transitions(limit)}


@app.get("/dungeon/{dungeon_id}")
def get_dungeon(dungeon_id: str) -> dict:
    from app.network import dungeon_store
    return dungeon_store.get_dungeon(dungeon_id) or {
        "id": dungeon_id, "name": "", "rooms": []}


@app.put("/dungeon/{dungeon_id}")
def put_dungeon(dungeon_id: str, name: str = Body(""),
                rooms: List[dict] = Body(...)) -> dict:
    from app.network import dungeon_store
    return dungeon_store.save_dungeon(dungeon_id, name, rooms)


@app.delete("/dungeon/{dungeon_id}")
def delete_dungeon(dungeon_id: str) -> dict:
    from app.network import dungeon_store
    return {"deleted": dungeon_store.delete_dungeon(dungeon_id)}


@app.post("/dungeon/step")
def dungeon_step(team: List[str] = Body(...), map_id: int = Body(...),
                 cells: List[int] = Body(...)) -> dict:
    """Enfile un pas de donjon : rejouer le parcours `cells` (cases à cliquer
    dans l'ordre, la dernière = porte/trappe) de la salle `map_id` pour chaque
    fenêtre de `team`. À appeler une fois la salle vaincue — fait passer toute
    l'équipe à la salle suivante."""
    from app.network.walk_jobs import get_store
    team = [t for t in (team or []) if t and t.strip()]
    cells = [int(c) for c in (cells or [])]
    if not team:
        return {"ok": False, "reason": "équipe vide (aucune fenêtre ciblée)"}
    if not cells:
        return {"ok": False, "reason": "aucune case de sortie pour cette salle"}
    job = get_store().submit_dungeon_step(team, map_id, cells)
    return {"ok": True, "job": job}


# --- Tableau de bord multi-comptes : groupes (Arène / Farm) -----------------

@app.get("/board/groups")
def read_board_groups() -> Dict[str, str]:
    """Mapping nom_de_perso -> groupe (arene/farm/…) pour board.html."""
    from app.network import account_groups
    return account_groups.load_groups()


@app.put("/board/groups")
def write_board_group(name: str = Body(...), group: str = Body("")) -> Dict[str, str]:
    """Assigne un compte à un groupe (group vide = retire l'assignation)."""
    from app.network import account_groups
    return account_groups.set_group(name, group)


@app.get("/board/rules")
def read_board_rules() -> List[dict]:
    """Règles d'auto-rangement par motif de nom (prefix/suffix/contains -> group)."""
    from app.network import account_groups
    return account_groups.load_rules()


@app.put("/board/rules")
def write_board_rules(rules: List[dict] = Body(..., embed=True)) -> List[dict]:
    from app.network import account_groups
    return account_groups.save_rules(rules)


@app.get("/board/order")
def read_board_order() -> List[str]:
    """Ordre de balayage personnalisé (liste de noms) pour le pop-up."""
    from app.network import account_groups
    return account_groups.load_order()


@app.put("/board/order")
def write_board_order(order: List[str] = Body(..., embed=True)) -> List[str]:
    from app.network import account_groups
    return account_groups.save_order(order)


@app.get("/board/windows")
def read_board_windows() -> dict:
    """Fenêtres Dofus ouvertes (rapportées par le walker) = liste réelle des
    comptes pour board.html, indépendante du sniffer."""
    from app.network.walk_jobs import get_store
    return get_store().windows(time.time())


# Tableau de bord statique (monté en dernier pour ne pas masquer les routes API).
app.mount("/ui", StaticFiles(directory="app/static", html=True), name="ui")
