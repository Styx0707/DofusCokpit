"""Tests du moteur d'optimisation — aucune DB ni réseau requis (fonctions pures)."""
from __future__ import annotations

from app.core.optimizer import compute_craftable, compute_near_craftable, simulate_crafting_plan
from app.models import Ingredient, Recipe, StockEntry


def _recipe(rid, result_id, name, ings, result_qty=1):
    return Recipe(
        recipe_id=rid,
        result_item_id=result_id,
        result_name=name,
        result_quantity=result_qty,
        ingredients=[Ingredient(item_id=i, name=f"ing{i}", quantity=q) for i, q in ings],
    )


def test_compute_craftable_isolation():
    stock = [StockEntry(1, "Bois", 10), StockEntry(2, "Fer", 4)]
    recipes = [_recipe(100, 900, "Epee", [(1, 2), (2, 1)])]  # 2 bois + 1 fer

    craftable = compute_craftable(recipes, stock)

    assert len(craftable) == 1
    epee = craftable[0]
    assert epee.max_crafts == 4  # limité par le fer (4/1) < bois (10/2=5)
    assert epee.limiting_item_id == 2
    assert epee.result_quantity_total == 4


def test_near_craftable_lists_only_reachable_recipes():
    # Stock : assez de bois, pas de fer, pas de cuir.
    stock = [StockEntry(1, "Bois", 10), StockEntry(2, "Fer", 1)]
    recipes = [
        _recipe(100, 900, "Epee", [(1, 2), (2, 1)]),             # fabricable -> exclue
        _recipe(101, 901, "Hache", [(1, 2), (2, 3)]),            # manque 2 fer -> 1 ressource
        _recipe(102, 902, "Armure", [(1, 2), (2, 3), (3, 5)]),   # manque fer + cuir -> 2 ressources
        _recipe(103, 903, "Panoplie", [(3, 5), (4, 5), (5, 5)]), # manque 3 ressources -> au-delà du seuil
    ]

    near = compute_near_craftable(recipes, stock, max_missing_kinds=2)

    names = [n.result_name for n in near]
    assert names == ["Hache", "Armure"]            # triées par nb manquant croissant, Epee/Panoplie exclues
    hache = near[0]
    assert hache.missing_kinds == 1
    assert hache.missing_total == 2                # besoin 3 fer, en stock 1 -> manque 2
    assert hache.missing[0].item_id == 2
    assert hache.missing[0].missing == 2
    # le seuil borne le nombre de ressources distinctes manquantes
    assert all(n.missing_kinds <= 2 for n in near)


def test_near_craftable_include_ready():
    stock = [StockEntry(1, "Bois", 10), StockEntry(2, "Fer", 1)]
    recipes = [
        _recipe(100, 900, "Epee", [(1, 2), (2, 1)]),   # fabricable : 1 craft (limité par le fer)
        _recipe(101, 901, "Hache", [(1, 2), (2, 3)]),  # manque 2 fer
    ]

    near = compute_near_craftable(recipes, stock, max_missing_kinds=2, include_ready=True)

    by = {n.result_name: n for n in near}
    assert by["Epee"].missing_kinds == 0 and by["Epee"].missing == [] and by["Epee"].max_crafts == 1
    assert by["Hache"].missing_kinds == 1
    assert near[0].result_name == "Epee"  # manque 0 trié en premier


def test_plan_deducts_shared_resources_virtually():
    # Deux recettes se disputent le même ingrédient (id=1).
    stock = [StockEntry(1, "Bois", 10)]
    recipes = [
        _recipe(100, 900, "Planche", [(1, 4)]),  # consomme 4 bois
        _recipe(101, 901, "Batonnet", [(1, 3)]),  # consomme 3 bois
    ]

    plan = simulate_crafting_plan(recipes, stock)

    # Planche d'abord : 10//4 = 2 -> 8 bois consommés, reste 2.
    # Batonnet ensuite : 2//3 = 0 -> aucune fabrication.
    crafted = {s.result_name: s.crafted for s in plan.steps}
    assert crafted["Planche"] == 2
    assert "Batonnet" not in crafted
    assert plan.remaining_stock.get(1) == 2


def test_plan_uses_intermediate_product_as_virtual_resource():
    # La recette B consomme l'objet produit par la recette A.
    stock = [StockEntry(1, "Minerai", 6)]
    recipes = [
        _recipe(100, 50, "Lingot", [(1, 2)]),  # 2 minerais -> 1 lingot (=> 3 lingots)
        _recipe(101, 900, "Epee", [(50, 3)]),  # 3 lingots -> 1 epee
    ]

    plan = simulate_crafting_plan(recipes, stock)

    crafted = {s.result_name: s.crafted for s in plan.steps}
    assert crafted["Lingot"] == 3
    assert crafted["Epee"] == 1  # rendu possible par les lingots virtuels
