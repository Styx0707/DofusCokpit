"""Seed le dictionnaire d'objets (id -> nom) depuis data/items_all.json (API wiki).

Met à jour les noms provisoires ('Objet #<id>') créés par l'ingestion de banque.
Usage : python -m scripts.seed_names [data/items_all.json]
"""
from __future__ import annotations

import json
import logging
import sys

from app.db.connection import close_pool, init_pool, transaction
from app.db.repositories import upsert_items
from app.models import Item

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("seed_names")


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "data/items_all.json"
    with open(path, encoding="utf-8") as fh:
        data = json.load(fh)
    items = [Item(item_id=int(x["id"]), name=x["name"]) for x in data if x.get("name")]
    logger.info("%d objets à seeder depuis %s", len(items), path)

    init_pool()
    try:
        with transaction() as cur:
            n = upsert_items(cur, items)
        logger.info("Noms d'objets seedés : %d", n)
    finally:
        close_pool()


if __name__ == "__main__":
    main()
