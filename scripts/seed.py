"""Seed du dictionnaire d'objets et des recettes.

Usage :
    python -m scripts.seed [chemin.json]

Sans argument, charge ``data/recipes.json``. Format attendu :

{
  "items":   [ {"id": 289, "name": "Gelano"}, ... ],
  "recipes": [
     {"result_item_id": 289, "result_quantity": 1,
      "ingredients": {"311": 5, "340": 2}},   // {ingredient_item_id: quantite}
     ...
  ]
}

Idempotent : ré-exécutable sans dupliquer (upsert + remplacement des ingrédients).
"""
from __future__ import annotations

import json
import logging
import sys
from pathlib import Path
from typing import Dict, List

from app.db.connection import close_pool, init_pool, transaction
from app.db.repositories import upsert_items, upsert_recipe
from app.models import Item

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("seed")

DEFAULT_PATH = Path(__file__).resolve().parent.parent / "data" / "recipes.json"


def load_payload(path: Path) -> dict:
    with path.open(encoding="utf-8") as fh:
        return json.load(fh)


def seed(path: Path) -> None:
    payload = load_payload(path)
    items: List[Item] = [Item(item_id=int(it["id"]), name=it["name"]) for it in payload.get("items", [])]
    recipes = payload.get("recipes", [])

    init_pool()
    try:
        with transaction() as cur:
            n_items = upsert_items(cur, items)
            n_recipes = 0
            for rec in recipes:
                # Les clés JSON sont des chaînes -> conversion en int.
                ingredients: Dict[int, int] = {int(k): int(v) for k, v in rec["ingredients"].items()}
                upsert_recipe(
                    cur,
                    result_item_id=int(rec["result_item_id"]),
                    ingredients=ingredients,
                    result_quantity=int(rec.get("result_quantity", 1)),
                )
                n_recipes += 1
        logger.info("Seed terminé : %d objets, %d recettes.", n_items, n_recipes)
    finally:
        close_pool()


def main() -> None:
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT_PATH
    if not path.exists():
        logger.error("Fichier de seed introuvable : %s", path)
        sys.exit(1)
    seed(path)


if __name__ == "__main__":
    main()
