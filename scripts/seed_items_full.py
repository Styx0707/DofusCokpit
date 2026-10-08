"""Seed le dictionnaire d'objets AVEC métadonnées (nom, type, niveau, prix).

- Nom / type / niveau : depuis data/items_all.json (liste de l'API wiki).
- Prix vendeur : depuis le cache data/details/<id>.json (rempli par fetch_recipes).

Usage : python -m scripts.seed_items_full [data/items_all.json]
"""
from __future__ import annotations

import json
import logging
import os
import sys

from app.db.connection import close_pool, init_pool, transaction
from app.db.repositories import upsert_items
from app.models import Item

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("seed_items_full")

CACHE_DIR = "data/details"


def load_price(item_id: int):
    path = os.path.join(CACHE_DIR, f"{item_id}.json")
    if not os.path.exists(path):
        return None
    try:
        with open(path, encoding="utf-8") as fh:
            return json.load(fh).get("price")
    except Exception:
        return None


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "data/items_all.json"
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)

    items = []
    for x in data:
        if not x.get("name"):
            continue
        iid = int(x["id"])
        items.append(Item(
            item_id=iid,
            name=x["name"],
            type=x.get("type"),
            level=x.get("level"),
            price=load_price(iid),
        ))
    with_price = sum(1 for it in items if it.price)
    logger.info("%d objets (dont %d avec prix vendeur > 0 en cache)", len(items), with_price)

    init_pool()
    try:
        with transaction() as cur:
            n = upsert_items(cur, items)
        logger.info("Objets seedés (nom+type+niveau+prix) : %d", n)
    finally:
        close_pool()


if __name__ == "__main__":
    main()
