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

from app.core.brisage import (
    DEFAULT_COEF,
    GA_PA_RUNE_ID,
    GA_PA_RUNE_NAME,
    MAX_BRISAGE_LEVEL,
    compute_pa_brisage,
    effective_costs,
    ingredient_recipes,
    load_pa_targets,
)
from app.core.farm import (
    compute_farm_plan,
    flatten_resources,
    live_zones_from_catalog,
    load_drops_index,
    load_monster_index,
    load_monsters,
    load_zone_index,
    rank_kamas,
    rank_targets,
    rank_zones,
)
from app.core.optimizer import (
    compute_craftable,
    compute_near_craftable,
    compute_profitable_crafts,
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


# ZoneSniffer global : catalogue maps/monstres/archis PAR ZONE, alimenté par le
# même flux live que le RepopMonitor (/live/stream). Ingère TOUTES les zones ; la
# zone affichée est choisie à la lecture (/live/zone?zone=…). Amorcé une fois
# depuis data/live_feed.jsonl pour un catalogue immédiat sans attendre le live.
_zone_sniffer = None


def get_zone_sniffer():
    global _zone_sniffer
    if _zone_sniffer is None:
        from app.core.zone_sniffer import ZoneSniffer
        _zone_sniffer = ZoneSniffer(zone_filter=None)
        _bootstrap_zone_sniffer(_zone_sniffer)
    return _zone_sniffer


def _bootstrap_zone_sniffer(sniffer) -> None:
    """Amorce le sniffer depuis data/live_feed.jsonl (produit par
    scripts/frida_live.py) s'il existe. Tolérant : une erreur n'empêche pas
    l'API de démarrer ni le live d'alimenter le sniffer ensuite."""
    path = os.path.join("data", "live_feed.jsonl")
    if not os.path.exists(path):
        return
    try:
        pairs = []
        with open(path, encoding="utf-8") as fh:
            for line in fh:
                line = line.strip()
                if not line:
                    continue
                try:
                    o = json.loads(line)
                except ValueError:
                    continue
                if o.get("dir") == "S->C" and o.get("raw"):
                    pairs.append((o.get("stream", "?"), o["raw"]))
        n = sniffer.feed(pairs)
        logging.getLogger("api").info("ZoneSniffer amorcé (live_feed.jsonl) : %d messages.", n)
    except Exception:
        logging.getLogger("api").debug("Bootstrap ZoneSniffer échoué.", exc_info=True)


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
        stop_watcher = start_watcher(
            get_monitor(), live_dir,
            on_bank=_persist_bank, on_prices=_persist_prices,
            # alimente AUSSI le catalogue de zone (page Grobe) : sans ça, seul le
            # RepopMonitor était mis à jour par le ring-buffer dumpcap.
            on_messages=lambda pairs, ts: get_zone_sniffer().feed(pairs, ts=ts))
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


# --- Brisage « Rune Ga Pa » (lié à la banque) -------------------------------

@app.get("/brisage/pa")
def read_pa_brisage(
        coef: float = Query(DEFAULT_COEF, ge=0, le=4000,
                            description="coefficient de brisage serveur en % (dynamique, 1–4000)"),
        price: Optional[int] = Query(None, ge=0, description="prix unitaire Ga Pa en kamas ; défaut = prix base de la rune"),
        max_level: int = Query(MAX_BRISAGE_LEVEL, ge=1, le=200,
                               description="niveau max des équipements +PA auto-découverts"),
) -> dict:
    """Brisage « Rune Ga Pa » : auto-découvre tous les équipements +PA craftables
    de niveau ≤ ``max_level`` (cf. ``app.core.brisage.discover_pa_targets``) et
    renvoie par objet le taux d'obtention Ga Pa (formule de brisage, croît avec le
    niveau), le nb de crafts possibles avec le stock de banque, le coût d'appro des
    ingrédients (min achat/craft), les Ga Pa attendues et les kamas (bruts / nets).

    Recette / niveau / valeur PA proviennent du cache ``data/details`` ; stock et
    prix de la base. ``coef`` (coefficient de brisage, propre au serveur) et
    ``price`` (prix de la rune) sont calibrables."""
    targets, missing = load_pa_targets(max_level=max_level)
    with transaction(commit=False) as cur:
        stock = {s.item_id: s.quantity for s in get_full_stock(cur)}
        meta = get_items_metadata(cur)
    price_map = {iid: m.get("price") for iid, m in meta.items()}
    rune_meta = meta.get(GA_PA_RUNE_ID) or {}
    ga_pa_price = price if price is not None else rune_meta.get("price")

    # Coût d'appro optimal par ingrédient = min(achat HDV, craft récursif) : un
    # ingrédient craftable (ex. La Broche Céleste dans le Collier du Rat Noir) est
    # valorisé au moins cher entre l'acheter et le fabriquer.
    ingredient_ids = {ing["item_id"] for t in targets for ing in t["recipe"]}
    recipes = ingredient_recipes(ingredient_ids)
    cost_map = effective_costs(ingredient_ids, recipes, price_map)

    rows = compute_pa_brisage(targets, stock, price_map, coef=coef,
                              ga_pa_price=ga_pa_price, cost_map=cost_map)
    data = []
    for r in rows:
        d = asdict(r)
        d["icon"] = (meta.get(d["item_id"]) or {}).get("icon")
        data.append(d)
    totals = {
        "recipes": len(data),
        "craftable_now": sum(r["craftable_now"] for r in data),
        "expected_ga_pa": round(sum(r["expected_ga_pa"] for r in data), 2),
        "gross_kamas": sum(r["gross_kamas"] for r in data),
        "net_kamas": sum((r["net_kamas"] or 0) for r in data),
        "craft_cost": sum((r["total_cost"] or 0) for r in data),
        "profitable_buys": sum(1 for r in data if r["buy_profitable"]),
        "bank_profitable": sum(1 for r in data if r["bank_buy_profitable"]),
        "bank_profit_total": sum((r["max_profit_total"] or 0) for r in data),
        "bank_unbounded": sum(1 for r in data if r["bank_unbounded"]),
    }
    return {
        "rows": data,
        "totals": totals,
        "params": {"coef": coef, "ga_pa_price": ga_pa_price, "max_level": max_level},
        "rune": {
            "item_id": GA_PA_RUNE_ID,
            "name": GA_PA_RUNE_NAME,
            "unit_price": ga_pa_price,
            "icon": rune_meta.get("icon"),
            "priced": rune_meta.get("price") is not None,
        },
        "missing_targets": missing,
    }


# --- Plan de farm (ressources de brisage -> où farmer) ----------------------

@app.get("/farm/plan")
def read_farm_plan(
        coef: float = Query(DEFAULT_COEF, ge=0, le=4000,
                            description="coefficient de brisage serveur en % (cf. /brisage/pa)"),
        price: Optional[int] = Query(None, ge=0, description="prix unitaire Ga Pa ; défaut = prix base"),
        max_level: int = Query(MAX_BRISAGE_LEVEL, ge=1, le=200,
                               description="niveau max des équipements +PA auto-découverts"),
        crafts: int = Query(1, ge=1, le=10000, description="exemplaires à crafter par cible (base 'unit')"),
        basis: str = Query("unit", pattern="^(unit|bank)$",
                           description="'unit' = `crafts` par cible ; 'bank' = nb de crafts rentables en épuisant la banque"),
        only_profitable: bool = Query(True, description="ne garder que les cibles rentables à l'achat des ressources"),
) -> dict:
    """Plan de farm : à partir des équipements +PA RENTABLES à briser, aplatit les
    recettes jusqu'aux ressources-FEUILLES, agrège les quantités et indique pour
    chacune sa source (métier de récolte / butin) et où la farmer (zones/monstres
    rapprochés par nom — cf. ``app.core.farm``). Heuristique pour les butins (pas
    de table de drop dans les données) ; fiable pour les ressources de métier."""
    targets, missing = load_pa_targets(max_level=max_level)
    with transaction(commit=False) as cur:
        stock = {s.item_id: s.quantity for s in get_full_stock(cur)}
        meta = get_items_metadata(cur)
    price_map = {iid: m.get("price") for iid, m in meta.items()}
    rune_meta = meta.get(GA_PA_RUNE_ID) or {}
    ga_pa_price = price if price is not None else rune_meta.get("price")

    ingredient_ids = {ing["item_id"] for t in targets for ing in t["recipe"]}
    recipes = ingredient_recipes(ingredient_ids)
    cost_map = effective_costs(ingredient_ids, recipes, price_map)
    rows = compute_pa_brisage(targets, stock, price_map, coef=coef,
                              ga_pa_price=ga_pa_price, cost_map=cost_map)

    # Combien crafter par cible : filtre rentabilité + base (unit / banque).
    want: Dict[int, int] = {}
    kept_targets: List[dict] = []
    for r in rows:
        if only_profitable and not r.buy_profitable:
            continue
        if basis == "bank":
            n = r.max_profitable_crafts if r.max_profitable_crafts is not None else crafts
        else:
            n = crafts
        if n and n > 0:
            want[r.item_id] = n
            kept_targets.append({
                "item_id": r.item_id, "name": r.name, "level": r.level,
                "crafts": n, "unit_margin": r.unit_margin,
                "ga_pa_rate": r.ga_pa_rate,          # Ga Pa par objet cassé (vitesse)
                "icon": (meta.get(r.item_id) or {}).get("icon"),
            })

    targets_by_id = {t["item_id"]: t for t in targets}
    plan_targets = [targets_by_id[i] for i in want]

    live = live_zones_from_catalog(get_zone_sniffer().catalog(zone=None))
    resources = compute_farm_plan(
        plan_targets, want, recipes, stock, price_map,
        zone_index=load_zone_index(), monster_index=load_monster_index(),
        live_zones_by_monster=live, drops_index=load_drops_index(),
    )

    data = []
    for res in resources:
        d = asdict(res)
        d["icon"] = (meta.get(res.item_id) or {}).get("icon")
        data.append(d)

    # Poids Ga Pa d'une ressource = MEILLEUR taux Ga Pa parmi les cibles qui
    # l'utilisent (pas la somme : une unité ne sert qu'un craft ; sommer gonflerait
    # les matières ubiquitaires). Sert à classer les zones (cf. rank_zones).
    from collections import Counter as _Counter
    rate_by_id = {r.item_id: r.ga_pa_rate for r in rows}
    gapa_weight: Dict[int, float] = {}
    for iid in want:
        leaf: _Counter = _Counter()
        for ing in targets_by_id[iid]["recipe"]:
            flatten_resources(ing["item_id"], ing["quantity"], recipes, leaf)
        rate = rate_by_id.get(iid, 0.0)
        for rid, q in leaf.items():
            if q > 0 and rate > gapa_weight.get(rid, 0.0):
                gapa_weight[rid] = rate
    zone_ranking = rank_zones(resources, load_drops_index(), gapa_weight)
    target_ranking = rank_targets(plan_targets, want, recipes, rate_by_id, load_drops_index())

    # Regroupements pour la vue « où farmer ».
    by_profession: Dict[str, dict] = {}
    by_zone: Dict[str, dict] = {}
    for res in resources:
        if res.source_kind == "harvest" and res.profession:
            g = by_profession.setdefault(res.profession, {"profession": res.profession,
                                                          "resources": 0, "to_buy_cost": 0})
            g["resources"] += 1
            g["to_buy_cost"] += res.buy_cost or 0
        for sp in res.spots:
            if sp.kind != "zone":
                continue
            z = by_zone.setdefault(sp.label, {"zone": sp.label, "resources": 0,
                                              "to_buy_cost": 0, "confirmed": False})
            z["resources"] += 1
            z["to_buy_cost"] += res.buy_cost or 0
            # Piste fiable = table de butin (drop) ou vue en live (sniffer).
            z["confirmed"] = z["confirmed"] or (sp.via in ("drop", "live"))

    totals = {
        "targets": len(kept_targets),
        "resources": len(data),
        "harvest": sum(1 for r in resources if r.source_kind == "harvest"),
        "drop": sum(1 for r in resources if r.source_kind in ("drop", "unknown")),
        "drop_confirmed": sum(1 for r in resources
                              if any(sp.via == "drop" for sp in r.spots)),
        "to_buy_cost": sum((r.buy_cost or 0) for r in resources),
        "unpriced": sum(1 for r in resources if r.unit_price is None),
    }
    return {
        "resources": data,
        "targets": sorted(kept_targets, key=lambda t: -(t["ga_pa_rate"] or 0)),
        "target_ranking": target_ranking,
        "zone_ranking": zone_ranking,
        "by_profession": sorted(by_profession.values(), key=lambda g: -g["to_buy_cost"]),
        "by_zone": sorted(by_zone.values(), key=lambda g: (-g["resources"], -g["to_buy_cost"])),
        "totals": totals,
        "params": {"coef": coef, "ga_pa_price": ga_pa_price, "max_level": max_level,
                   "crafts": crafts, "basis": basis, "only_profitable": only_profitable},
        "missing_targets": missing,
    }


# --- Meilleurs spots kamas (valeur des drops / combat / niveau) -------------

@app.get("/farm/kamas")
def read_farm_kamas(
        level_max: Optional[int] = Query(None, ge=1, le=200,
                                         description="niveau max du perso ; ne garde que les monstres ≤ ce niveau"),
        limit: int = Query(50, ge=1, le=300, description="nb de monstres/zones renvoyés"),
        price_max: Optional[int] = Query(1_000_000, ge=0,
                                         description="ignore les drops dont le prix unitaire dépasse ce plafond "
                                                     "(garde-fou anti-prix HDV aberrant ; 0 = désactivé)"),
        exclude_special: bool = Query(True,
                                      description="écarte les monstres non farmables en boucle "
                                                  "(coffres, boss événementiels/quotidiens, prismes, percepteurs)"),
) -> dict:
    """Meilleurs spots de farm KAMAS : classe monstres & zones par VALEUR DE BUTIN
    par combat, valorisée aux prix HDV de la base (``get_items_metadata``). Idéal
    pour « où farm pour du kamas, accessible à bas niveau ». Les drops viennent du
    bestiaire xixou (``data/monsters.json`` / ``scripts/ingest_monsters.py``) ; un
    drop sans prix connu en base est ignoré. ``value_per_level`` favorise les
    monstres faibles qui lâchent cher."""
    monsters = load_monsters()
    with transaction(commit=False) as cur:
        meta = get_items_metadata(cur)
    price_map = {iid: m.get("price") for iid, m in meta.items()}
    ranked = rank_kamas(monsters, price_map, level_max=level_max, limit=limit,
                        price_max=(price_max or None), exclude_special=exclude_special)
    return {
        "monsters": ranked["monsters"],
        "zones": ranked["zones"],
        "params": {"level_max": level_max, "limit": limit, "price_max": price_max,
                   "exclude_special": exclude_special},
        "coverage": {
            "monsters_total": len(monsters),
            "items_priced": sum(1 for v in price_map.values() if v),
            "outliers_skipped": ranked.get("outliers", 0),
            "specials_skipped": ranked.get("specials", 0),
            "has_bestiary": bool(monsters),
        },
    }


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


@app.get("/craftable/profit")
def read_profitable_crafts(
        item_type: Optional[str] = Query(None, alias="type"),
        min_level: Optional[int] = Query(None, ge=0),
        max_level: Optional[int] = Query(None, ge=0),
        min_margin: Optional[float] = Query(None, description="marge minimale en %"),
        sort: str = Query("profit", pattern="^(profit|margin|net|level|name)$"),
        limit: int = Query(100, ge=1, le=5000),
) -> List[dict]:
    """Recettes RENTABLES : revente du produit − coût marché des ingrédients, au
    prix effectif (``market_price`` sinon vendeur). Les recettes dont le produit
    ou un ingrédient n'a pas de prix connu sont EXCLUES (non valorisables).

    - ``unit_profit``          : marge pour 1 craft si l'on achète TOUS les ingrédients.
    - ``profit_after_missing`` : marge si l'on n'achète QUE les ressources manquantes
                                 (le stock déjà possédé est traité comme gratuit).
    - ``craftable_now``        : nb de crafts réalisables avec le stock courant.

    Tri : ``profit`` (marge unitaire), ``margin`` (%), ``net`` (profit_after_missing)."""
    with transaction(commit=False) as cur:
        stock = get_full_stock(cur)
        recipes = get_all_recipes(cur)
        meta = get_items_metadata(cur)
    price_map = {iid: m.get("price") for iid, m in meta.items()}
    rows: List[dict] = []
    for c in compute_profitable_crafts(recipes, price_map, stock, min_margin):
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
        "profit": lambda d: -d["unit_profit"],
        "margin": lambda d: -(d["margin_pct"] or 0),
        "net": lambda d: -d["profit_after_missing"],
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


@app.get("/live/zone")
def read_live_zone(zone: str = Query("Grobe", description="sous-chaîne de sous-zone ; vide = toutes")) -> dict:
    """Catalogue maps/monstres/archis d'une sous-zone, agrégé en live (+ amorçage
    depuis data/live_feed.jsonl). ``zone`` filtre à la lecture (vide -> toutes)."""
    return get_zone_sniffer().catalog(zone=zone or None)


@app.get("/live/zone/alerts")
def read_live_zone_alerts(since: int = Query(0, description="ne renvoie que les alertes seq > since"),
                          zone: str = Query("Grobe", description="sous-chaîne de sous-zone ; vide = toutes")) -> dict:
    """Alertes d'apparition (archimonstre dans un groupe, ou règle « groupe » comme
    >= 2 Fantôme Pandikaze) depuis ``since``. Le client amorce ``since = max_seq``
    au 1er appel pour ignorer l'historique, puis notifie les nouvelles."""
    return get_zone_sniffer().alerts_since(since, zone=zone or None)


@app.post("/live/names/fetch")
def fetch_monster_name(id: int = Body(..., embed=True)) -> dict:
    """Récupère le nom d'un monstre (moon-bot) et le persiste dans
    data/monster_names.json (recharge à chaud) — pour nommer les #id d'une zone."""
    from app.network import protocol
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
    return {"id": id, "name": name, "known": len(protocol.MONSTER_NAMES)}


@app.post("/live/ingest")
def live_ingest(path: str = Query(..., description="Chemin d'une capture .pcapng côté serveur")) -> dict:
    """Ingest une capture Wireshark dans le moniteur (import paresseux de scapy)."""
    from app.network.pcap_feed import feed_pcap
    return feed_pcap(get_monitor(), path,
                     on_messages=lambda pairs, ts: get_zone_sniffer().feed(pairs, ts=ts))


@app.post("/live/stream")
def live_stream(messages: List[str] = Body(..., embed=True),
                stream: str = Body("live", embed=True)) -> dict:
    """Ingest LIVE d'un lot de messages serveur->client DÉJÀ en clair (hook socket
    du client via scripts/frida_live.py) — même dispatch que /live/ingest mais SANS
    pcap. Alimente le RepopMonitor (repops, « qui joue ») + auto-sync banque ``EL``
    et prix HDV ``EHP``/``EHl``. ``stream`` = id du perso/compte (constant en
    mono-compte, distinct par socket en multi-compte)."""
    from app.network.pcap_feed import feed_messages
    pairs = [(stream, m) for m in messages if m]
    get_zone_sniffer().feed(pairs, ts=time.time())   # catalogue + alertes par zone
    return feed_messages(get_monitor(), pairs,
                         on_bank=_persist_bank, on_prices=_persist_prices)


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
