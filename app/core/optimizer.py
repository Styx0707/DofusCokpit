"""Moteur d'optimisation de craft.

Fonctions PURES : aucune dépendance BDD ni réseau. Elles prennent des
dataclasses (Recipe, StockEntry) et renvoient des dataclasses sérialisables
-> facilement testables et exposables via une API REST.

Trois angles :
1. ``compute_craftable``       : par recette, combien de fois fabricable EN
   ISOLATION (sans concurrence entre recettes).
2. ``simulate_crafting_plan``  : planificateur glouton EN UN SEUL PASSAGE, stock
   virtuel déduit étape par étape.
3. ``resolve_crafting``        : résolution en POINT FIXE (passes répétées)
   pour les chaînes de dépendances profondes, indépendamment de l'ordre.
"""
from __future__ import annotations

from typing import Callable, Dict, List, Optional, Tuple

from app.models import (
    CraftableRecipe,
    CraftPlan,
    CraftStep,
    Ingredient,
    MissingBuy,
    MissingIngredient,
    NearCraftableRecipe,
    ProfitableCraft,
    Recipe,
    StockEntry,
    StockPull,
)


def _stock_to_dict(stock: List[StockEntry]) -> Dict[int, int]:
    return {entry.item_id: entry.quantity for entry in stock}


def max_crafts_for_recipe(
        recipe: Recipe, stock: Dict[int, int]
) -> Tuple[int, Optional[Ingredient]]:
    """Nombre maximal de fabrications de `recipe` avec `stock`.

    Renvoie (count, ingredient_limitant). L'ingredient limitant est celui qui
    plafonne le craft — utile pour afficher « il te manque X ».
    """
    if not recipe.ingredients:
        return 0, None
    best_count: Optional[int] = None
    limiting: Optional[Ingredient] = None
    for ing in recipe.ingredients:
        available = stock.get(ing.item_id, 0)
        possible = available // ing.quantity
        if best_count is None or possible < best_count:
            best_count = possible
            limiting = ing
    return (best_count or 0), limiting


def compute_craftable(
        recipes: List[Recipe], stock: List[StockEntry]
) -> List[CraftableRecipe]:
    """Liste des recettes fabricables et leur nombre d'occurrences (en isolation).

    Chaque recette est evaluee comme si elle disposait de tout le stock : les
    quantites NE tiennent PAS compte de la concurrence entre recettes sur les
    ressources communes (voir ``simulate_crafting_plan`` / ``resolve_crafting``).
    """
    stock_map = _stock_to_dict(stock)
    result: List[CraftableRecipe] = []
    for recipe in recipes:
        count, limiting = max_crafts_for_recipe(recipe, stock_map)
        if count <= 0:
            continue
        result.append(
            CraftableRecipe(
                recipe_id=recipe.recipe_id,
                result_item_id=recipe.result_item_id,
                result_name=recipe.result_name,
                max_crafts=count,
                result_quantity_total=count * recipe.result_quantity,
                limiting_item_id=limiting.item_id if limiting else None,
                limiting_item_name=limiting.name if limiting else None,
            )
        )
    result.sort(key=lambda c: c.max_crafts, reverse=True)
    return result


def compute_near_craftable(
        recipes: List[Recipe], stock: List[StockEntry], max_missing_kinds: int = 2,
        include_ready: bool = False
) -> List[NearCraftableRecipe]:
    """Recettes « à portée » : il manque au plus `max_missing_kinds` ressources
    DISTINCTES pour en fabriquer UNE (shortfall calculé pour 1 craft). Les recettes
    déjà fabricables (manque 0) sont EXCLUES par défaut ; avec ``include_ready=True``
    elles sont incluses (``missing=[]``, ``missing_kinds=0``, ``max_crafts``>0).
    Triées de la plus proche (0 manque d'abord) à la plus lointaine.
    """
    stock_map = _stock_to_dict(stock)
    out: List[NearCraftableRecipe] = []
    for recipe in recipes:
        if not recipe.ingredients:
            continue
        count, _ = max_crafts_for_recipe(recipe, stock_map)
        if count > 0:
            if not include_ready:
                continue  # déjà fabricable -> exclue (sauf include_ready)
            out.append(NearCraftableRecipe(
                recipe_id=recipe.recipe_id,
                result_item_id=recipe.result_item_id,
                result_name=recipe.result_name,
                result_quantity=recipe.result_quantity,
                missing=[], missing_kinds=0, missing_total=0, max_crafts=count,
            ))
            continue
        missing: List[MissingIngredient] = []
        for ing in recipe.ingredients:
            available = stock_map.get(ing.item_id, 0)
            short = ing.quantity - available
            if short > 0:
                missing.append(MissingIngredient(
                    item_id=ing.item_id, name=ing.name,
                    needed=ing.quantity, available=available, missing=short,
                ))
        if not missing or len(missing) > max_missing_kinds:
            continue
        out.append(NearCraftableRecipe(
            recipe_id=recipe.recipe_id,
            result_item_id=recipe.result_item_id,
            result_name=recipe.result_name,
            result_quantity=recipe.result_quantity,
            missing=missing,
            missing_kinds=len(missing),
            missing_total=sum(m.missing for m in missing),
        ))
    out.sort(key=lambda r: (r.missing_kinds, r.missing_total, r.result_name.lower()))
    return out


def compute_profitable_crafts(
        recipes: List[Recipe],
        price_map: Dict[int, Optional[int]],
        stock: Optional[List[StockEntry]] = None,
        min_margin_pct: Optional[float] = None,
) -> List[ProfitableCraft]:
    """Rentabilité de chaque recette : revente du produit − coût MARCHÉ des
    ingrédients, au prix EFFECTIF (``market_price`` sinon vendeur). Fonction PURE.

    ``price_map`` = {item_id: prix_unitaire ou None}. Une recette dont le PRODUIT
    ou un INGRÉDIENT n'a pas de prix connu est EXCLUE (non valorisable) : on ne
    devine jamais un prix manquant.

    Si ``stock`` est fourni, on calcule en plus, pour 1 craft : le coût d'achat
    des SEULES ressources manquantes (le stock déjà possédé est traité comme
    acquis) et combien de fois la recette est fabricable avec le stock courant.

    ``min_margin_pct`` filtre sur la marge (unit_profit / unit_cost). Trié par
    marge unitaire (``unit_profit``) décroissante.
    """
    stock_map = _stock_to_dict(stock) if stock else {}
    out: List[ProfitableCraft] = []
    for recipe in recipes:
        if not recipe.ingredients:
            continue
        result_price = price_map.get(recipe.result_item_id)
        if result_price is None:
            continue  # produit non valorisable
        unit_cost = 0
        missing_buy_cost = 0
        missing: List[MissingBuy] = []
        from_stock: List[StockPull] = []
        priced = True
        for ing in recipe.ingredients:
            unit_price = price_map.get(ing.item_id)
            if unit_price is None:
                priced = False
                break  # un ingrédient non valorisable -> recette exclue
            unit_cost += unit_price * ing.quantity
            have = stock_map.get(ing.item_id, 0)
            used = min(ing.quantity, have)   # prélevé sur le stock (à retirer en banque)
            if used > 0:
                from_stock.append(StockPull(
                    item_id=ing.item_id, name=ing.name, qty=used,
                    unit_price=unit_price, value=unit_price * used,
                ))
            short = ing.quantity - have      # reste à acheter
            if short > 0:
                cost = unit_price * short
                missing_buy_cost += cost
                missing.append(MissingBuy(
                    item_id=ing.item_id, name=ing.name, missing=short,
                    unit_price=unit_price, buy_cost=cost,
                ))
        if not priced:
            continue
        missing.sort(key=lambda m: m.buy_cost, reverse=True)
        from_stock.sort(key=lambda s: s.value, reverse=True)
        unit_revenue = result_price * recipe.result_quantity
        unit_profit = unit_revenue - unit_cost
        margin_pct = round(unit_profit / unit_cost * 100, 1) if unit_cost > 0 else None
        if min_margin_pct is not None and (margin_pct is None or margin_pct < min_margin_pct):
            continue
        craftable_now, _ = max_crafts_for_recipe(recipe, stock_map)
        out.append(ProfitableCraft(
            recipe_id=recipe.recipe_id,
            result_item_id=recipe.result_item_id,
            result_name=recipe.result_name,
            result_quantity=recipe.result_quantity,
            unit_cost=unit_cost,
            unit_revenue=unit_revenue,
            unit_profit=unit_profit,
            margin_pct=margin_pct,
            craftable_now=craftable_now,
            missing_buy_cost=missing_buy_cost,
            profit_after_missing=unit_revenue - missing_buy_cost,
            missing=missing,
            from_stock=from_stock,
        ))
    out.sort(key=lambda c: c.unit_profit, reverse=True)
    return out


def _apply_craft(recipe: Recipe, count: int, virtual: Dict[int, int]) -> Dict[int, int]:
    """Applique `count` fabrications de `recipe` au stock virtuel (mutation).

    Deduit les ingredients, credite l'objet produit (ressource virtuelle),
    et renvoie le detail {item_id: quantite consommee} de cette application.
    """
    consumed: Dict[int, int] = {}
    for ing in recipe.ingredients:
        used = ing.quantity * count
        virtual[ing.item_id] = virtual.get(ing.item_id, 0) - used
        consumed[ing.item_id] = used
    produced = count * recipe.result_quantity
    virtual[recipe.result_item_id] = virtual.get(recipe.result_item_id, 0) + produced
    return consumed


def simulate_crafting_plan(
        recipes: List[Recipe],
        stock: List[StockEntry],
        priority: Optional[Callable[[Recipe], object]] = None,
) -> CraftPlan:
    """Planificateur glouton EN UN SEUL PASSAGE sur un stock VIRTUEL.

    A chaque etape : on fabrique une recette au maximum possible, on deduit ses
    ingredients du stock virtuel, et on CREDITE l'objet produit dans ce meme
    stock (il devient une ressource virtuelle exploitable par une recette
    ULTERIEURE dans l'ordre). L'ordre de traitement (`priority`) arbitre qui
    « gagne » les ressources partagees. Le stock REEL en base n'est jamais
    modifie.

    Limite : une recette n'est traitee qu'une fois -> une dependance dont le
    fournisseur vient APRES le consommateur dans l'ordre n'est pas resolue.
    Utiliser ``resolve_crafting`` pour ce cas.
    """
    virtual: Dict[int, int] = _stock_to_dict(stock)
    ordered = sorted(recipes, key=priority) if priority is not None else list(recipes)

    steps: List[CraftStep] = []
    for recipe in ordered:
        count, _ = max_crafts_for_recipe(recipe, virtual)
        if count <= 0:
            continue
        consumed = _apply_craft(recipe, count, virtual)
        steps.append(
            CraftStep(
                recipe_id=recipe.recipe_id,
                result_item_id=recipe.result_item_id,
                result_name=recipe.result_name,
                crafted=count,
                consumed=consumed,
            )
        )

    remaining = {item_id: qty for item_id, qty in virtual.items() if qty > 0}
    return CraftPlan(steps=steps, remaining_stock=remaining)


def resolve_crafting(
        recipes: List[Recipe],
        stock: List[StockEntry],
        priority: Optional[Callable[[Recipe], object]] = None,
        max_passes: int = 1000,
) -> CraftPlan:
    """Resolution en POINT FIXE : repete des passes gloutonnes jusqu'a ce qu'une
    passe complete ne produise plus aucun craft.

    Gere les chaines de dependances profondes INDEPENDAMMENT de l'ordre : un
    produit intermediaire fabrique lors d'une passe (ex. lingot) debloque une
    recette de niveau superieur (ex. epee) a la passe suivante. Les compteurs
    sont agreges par recette sur l'ensemble des passes.

    Securite anti-boucle : `max_passes` plafonne les iterations, au cas ou des
    recettes formeraient un cycle net-neutre en ressources.

    Note : `remaining_stock` inclut les objets PRODUITS non reconsommes (tu les
    possedes desormais), pas seulement les matieres premieres restantes.
    """
    virtual: Dict[int, int] = _stock_to_dict(stock)
    ordered = sorted(recipes, key=priority) if priority is not None else list(recipes)
    by_recipe = {r.recipe_id: r for r in ordered}

    totals: Dict[int, int] = {}  # recipe_id -> total fabrique
    consumed_totals: Dict[int, Dict[int, int]] = {}  # recipe_id -> {item_id: qte}

    passes = 0
    while passes < max_passes:
        passes += 1
        progressed = False
        for recipe in ordered:
            count, _ = max_crafts_for_recipe(recipe, virtual)
            if count <= 0:
                continue
            progressed = True
            consumed = _apply_craft(recipe, count, virtual)
            acc = consumed_totals.setdefault(recipe.recipe_id, {})
            for item_id, qty in consumed.items():
                acc[item_id] = acc.get(item_id, 0) + qty
            totals[recipe.recipe_id] = totals.get(recipe.recipe_id, 0) + count
        if not progressed:
            break

    steps = [
        CraftStep(
            recipe_id=rid,
            result_item_id=by_recipe[rid].result_item_id,
            result_name=by_recipe[rid].result_name,
            crafted=total,
            consumed=consumed_totals.get(rid, {}),
        )
        for rid, total in totals.items()
    ]
    remaining = {item_id: qty for item_id, qty in virtual.items() if qty > 0}
    return CraftPlan(steps=steps, remaining_stock=remaining)
