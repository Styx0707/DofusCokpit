"""Télécharge un MAX d'icônes d'items/ressources et les stocke en local.

Contexte : la source historique (pages wiki.moon-bot.io) n'expose PLUS les
icônes d'items (site passé en page statique ; `/icons/item_*.png` -> 404).
solomonk.fr est derrière Cloudflare (503) et le CDN Rétro d'Ankama indexe par
gfxId (indisponible ici). La meilleure source libre restante est **dofusdb.fr**,
mais elle est indexée par SES ids, pas par le gid 1.29. On matche donc par
**nom exact** (normalisé sans accents/casse) : fiable (aucune icône ne part sur
un autre objet) mais partiel (les items Rétro renommés/absents dans Dofus 3 ne
matchent pas — ~60 % de couverture observée).

Icône trouvée -> téléchargée dans app/static/icons/<gid>.png et
items.icon = /ui/icons/<gid>.png (servie en local, pas de hotlink).

Usage :
    python -m scripts.fetch_icons                 # défaut: scope=useful, items sans icône
    python -m scripts.fetch_icons --scope all     # TOUS les items du dictionnaire
    python -m scripts.fetch_icons --scope bank    # seulement la banque
    python -m scripts.fetch_icons --all           # re-télécharge même si icône déjà présente
    python -m scripts.fetch_icons --workers 8 --limit 500
"""
from __future__ import annotations

import argparse
import concurrent.futures
import json
import os
import ssl
import threading
import unicodedata
import urllib.parse
import urllib.request

from app.db.connection import close_pool, init_pool, transaction

ICON_DIR = "app/static/icons"
API = "https://api.dofusdb.fr/items?lang=fr&$limit=5&name.fr="
CTX = ssl._create_unverified_context()
HEADERS = {"User-Agent": "Mozilla/5.0 dofus-cockpit/1.0", "Accept": "application/json"}

SCOPE_SQL = {
    "all": "SELECT item_id FROM items",
    "bank": "SELECT DISTINCT item_id FROM bank_inventory WHERE quantity > 0",
    "resources": "SELECT DISTINCT ingredient_item_id AS item_id FROM recipe_ingredients",
    "useful": """
        SELECT item_id FROM bank_inventory WHERE quantity > 0
        UNION SELECT ingredient_item_id FROM recipe_ingredients
        UNION SELECT item_id FROM character_equipment
        UNION SELECT item_id FROM build_targets
    """,
}

_print_lock = threading.Lock()


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", s or "").encode("ascii", "ignore").decode().lower()
    return " ".join(s.split())


def _get(url: str, as_json: bool):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20, context=CTX) as r:
        data = r.read()
    return json.loads(data.decode("utf-8", "replace")) if as_json else data


def _resolve_icon(gid: int, name: str, level) -> bytes | None:
    """Cherche l'item par nom exact sur dofusdb, renvoie les octets de l'icône
    (meilleure correspondance : nom normalisé identique + image ; niveau en
    départage) ou None."""
    try:
        d = _get(API + urllib.parse.quote(name), as_json=True)
    except Exception:
        return None
    candidates = []
    for it in d.get("data", []):
        nm = it.get("name") or {}
        nm = nm.get("fr") if isinstance(nm, dict) else nm
        img = it.get("img")
        if img and _norm(nm) == _norm(name):
            candidates.append(it)
    if not candidates:
        return None
    # départage : niveau le plus proche du nôtre quand on le connaît.
    if level is not None:
        candidates.sort(key=lambda it: abs((it.get("level") or 0) - level))
    try:
        return _get(candidates[0]["img"], as_json=False)
    except Exception:
        return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--scope", choices=sorted(SCOPE_SQL), default="useful")
    ap.add_argument("--all", action="store_true", help="re-télécharger même si icône déjà présente")
    ap.add_argument("--limit", type=int, default=0, help="limite le nb d'items traités (0 = tous)")
    ap.add_argument("--workers", type=int, default=8)
    args = ap.parse_args()

    os.makedirs(ICON_DIR, exist_ok=True)
    init_pool()
    try:
        where = "" if args.all else "WHERE i.icon IS NULL"
        sql = (f"SELECT i.item_id, i.name, i.level FROM items i "
               f"JOIN ({SCOPE_SQL[args.scope]}) s ON s.item_id = i.item_id {where} ORDER BY i.item_id")
        with transaction(commit=False) as cur:
            cur.execute(sql)
            todo = [(r["item_id"], r["name"], r["level"]) for r in cur.fetchall()]
        if args.limit:
            todo = todo[:args.limit]
        print(f"scope={args.scope} : {len(todo)} items à couvrir (sans icône{'' if not args.all else ' — forcé'})")

        updates: dict[int, str] = {}
        done = 0

        def work(row):
            gid, name, level = row
            data = _resolve_icon(gid, name, level)
            if not data:
                return None
            with open(os.path.join(ICON_DIR, f"{gid}.png"), "wb") as fh:
                fh.write(data)
            return gid, f"/ui/icons/{gid}.png"

        with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
            for res in pool.map(work, todo):
                done += 1
                if res:
                    updates[res[0]] = res[1]
                if done % 100 == 0:
                    with _print_lock:
                        print(f"  … {done}/{len(todo)} traités, {len(updates)} icônes")

        with transaction() as cur:
            for gid, path in updates.items():
                cur.execute("UPDATE items SET icon = %s WHERE item_id = %s", (path, gid))
        pct = (100 * len(updates) // len(todo)) if todo else 0
        print(f"icônes récupérées : {len(updates)}/{len(todo)} ({pct}%) | sans correspondance : {len(todo) - len(updates)}")
    finally:
        close_pool()


if __name__ == "__main__":
    main()
