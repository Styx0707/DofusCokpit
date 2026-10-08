"""Charge la liste des items cibles du build depuis un JSON.

Format : [{"item_id": 8272, "quantity": 8, "label": "Amulette team"}, ...]
Usage  : python -m scripts.seed_build [data/build_targets.json]
"""
from __future__ import annotations

import json
import logging
import sys

from app.db.build_repo import set_build_targets
from app.db.connection import close_pool, init_pool, transaction

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "data/build_targets.json"
    targets = json.load(open(path, encoding="utf-8"))
    init_pool()
    try:
        with transaction() as cur:
            n = set_build_targets(cur, targets)
        logging.info("Build chargé : %d item(s) cible depuis %s", n, path)
    finally:
        close_pool()


if __name__ == "__main__":
    main()
