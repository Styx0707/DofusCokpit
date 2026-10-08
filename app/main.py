"""Point d'entrée : câble sniffer -> repositories -> optimiseur.

Ce module orchestre les couches sans porter de logique métier :
1. sniffer capture la banque,
2. repositories persistent l'inventaire,
3. optimizer calcule les crafts possibles.
"""
from __future__ import annotations

import logging
from dataclasses import asdict
from typing import Dict

from app.core.optimizer import compute_craftable, simulate_crafting_plan
from app.db.connection import close_pool, init_pool, transaction
from app.db.repositories import get_all_recipes, get_full_stock, replace_bank_inventory
from app.network.sniffer import DofusBankSniffer

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("dofus.main")


def persist_and_report(inventory: Dict[int, int]) -> None:
    """Callback sniffer : persiste la banque puis calcule les crafts possibles."""
    # 1) Persistance atomique du scan complet.
    with transaction() as cur:
        replace_bank_inventory(cur, inventory)

    # 2) Relecture (lecture seule) du stock + recettes.
    with transaction(commit=False) as cur:
        stock = get_full_stock(cur)
        recipes = get_all_recipes(cur)

    # 3) Optimisation (fonctions pures).
    craftable = compute_craftable(recipes, stock)
    plan = simulate_crafting_plan(recipes, stock)

    logger.info("=== %d recette(s) fabricable(s) ===", len(craftable))
    for c in craftable:
        logger.info(
            "%s x%d (limité par %s)",
            c.result_name, c.max_crafts, c.limiting_item_name,
        )

    # Structures JSON-ready pour une future API REST :
    #   craftable_json = [asdict(c) for c in craftable]
    #   plan_json      = {"steps": [asdict(s) for s in plan.steps],
    #                     "remaining_stock": plan.remaining_stock}
    _ = [asdict(c) for c in craftable]
    _ = asdict(plan)


def main() -> None:
    init_pool()
    sniffer = DofusBankSniffer(on_bank=persist_and_report)
    try:
        sniffer.start()
    finally:
        close_pool()


if __name__ == "__main__":
    main()
