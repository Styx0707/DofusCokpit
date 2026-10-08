"""Récupère les recettes de tous les objets via l'API wiki (détail par objet).

- Cache disque par objet (data/details/<id>.json) -> reprenable, idempotent,
  poli (ne re-télécharge jamais).
- Concurrence modérée (8 threads) pour ne pas marteler le wiki communautaire.
- Produit data/recipes_full.json au schéma attendu par scripts.seed.

SSL : contexte non vérifié volontairement — données PUBLIQUES en lecture seule,
aucune donnée sensible ; évite les soucis de CA dans l'image slim.

Usage : python -m scripts.fetch_recipes [data/items_all.json]
"""
from __future__ import annotations

import concurrent.futures
import json
import logging
import os
import ssl
import sys
import urllib.request

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("fetch_recipes")

BASE = "https://wiki.moon-bot.io/api/item/{}.json"
CACHE_DIR = "data/details"
OUT = "data/recipes_full.json"
SSL_CTX = ssl._create_unverified_context()


def fetch_one(item_id: int):
    cache_path = os.path.join(CACHE_DIR, f"{item_id}.json")
    if os.path.exists(cache_path):
        try:
            with open(cache_path, encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            pass  # cache corrompu -> re-fetch
    try:
        req = urllib.request.Request(BASE.format(item_id), headers={"User-Agent": "dofus-craft-tool/1.0"})
        with urllib.request.urlopen(req, timeout=20, context=SSL_CTX) as resp:
            raw = resp.read().decode("utf-8")
        obj = json.loads(raw)
        with open(cache_path, "w", encoding="utf-8") as fh:
            fh.write(raw)
        return obj
    except Exception as exc:
        logger.debug("échec %s : %s", item_id, exc)
        return None


def main():
    os.makedirs(CACHE_DIR, exist_ok=True)
    path = sys.argv[1] if len(sys.argv) > 1 else "data/items_all.json"
    with open(path, encoding="utf-8") as fh:
        ids = [int(x["id"]) for x in json.load(fh) if x.get("id") is not None]
    logger.info("%d objets à interroger…", len(ids))

    recipes = []
    done = errors = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as ex:
        futures = {ex.submit(fetch_one, i): i for i in ids}
        for fut in concurrent.futures.as_completed(futures):
            done += 1
            obj = fut.result()
            if obj is None:
                errors += 1
            elif obj.get("recipe"):
                ingredients = {}
                for ing in obj["recipe"]:
                    iid = ing.get("item_id")
                    qty = ing.get("qty")
                    if iid and qty:
                        ingredients[int(iid)] = ingredients.get(int(iid), 0) + int(qty)
                if ingredients:
                    recipes.append({
                        "result_item_id": int(obj["id"]),
                        "result_quantity": 1,  # l'API ne fournit pas la quantité produite
                        "ingredients": ingredients,
                    })
            if done % 500 == 0:
                logger.info("%d/%d traités, %d recettes, %d erreurs", done, len(ids), len(recipes), errors)

    with open(OUT, "w", encoding="utf-8") as fh:
        json.dump({"items": [], "recipes": recipes}, fh, ensure_ascii=False)
    logger.info("FINI : %d recettes -> %s (%d erreurs de fetch)", len(recipes), OUT, errors)


if __name__ == "__main__":
    main()
