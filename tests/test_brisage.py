"""Tests du moteur de brisage « Ga Pa ».

``ga_pa_rate`` / ``compute_pa_brisage`` sont PURS (pas d'IO) ; ``load_pa_targets``
lit le cache réel ``data/details`` (présent dans le repo). Les valeurs attendues
sont dérivées de ``ga_pa_rate`` pour rester robustes au calage des constantes."""
from __future__ import annotations

from app.core.brisage import (
    DEFAULT_COEF,
    GA_PA_RUNE_ID,
    POIDS_GA_PA,
    POIDS_PA,
    compute_pa_brisage,
    effective_costs,
    ga_pa_rate,
    ingredient_recipes,
    load_pa_targets,
)


def _target(item_id, pa, recipe, name="Item", level=100, typ="Amulette"):
    return {
        "item_id": item_id, "name": name, "level": level, "type": typ,
        "pa_value": pa,
        "recipe": [{"item_id": i, "name": f"ing{i}", "quantity": q} for i, q in recipe],
    }


def test_ga_pa_rate_matches_reference_and_scaling():
    assert POIDS_PA == 100 and POIDS_GA_PA == 1000
    # Ancre réelle fournie par l'utilisateur : Amulette du Kam Assutra, niv 43,
    # +1 PA -> 8,49 % (au coefficient Retro 3).
    assert round(ga_pa_rate(43, 1, 3) * 100, 2) == 8.49
    # Croissance ≈ quadratique en niveau : niv 103 >> 5× le niv 43.
    assert ga_pa_rate(103, 1, 3) > 5 * ga_pa_rate(43, 1, 3)
    assert ga_pa_rate(100, 1, 3) > ga_pa_rate(40, 1, 3)    # monotone en niveau
    assert ga_pa_rate(100, 2, 3) > ga_pa_rate(100, 1, 3)   # monotone en valeur PA
    assert ga_pa_rate(None, 1, 3) == 0.0                   # niveau inconnu -> 0
    assert ga_pa_rate(100, 1, 0) == 0.0                    # coefficient nul -> 0
    # Linéaire dans le coefficient (multiplicateur global).
    assert round(ga_pa_rate(43, 1, 6), 6) == round(2 * ga_pa_rate(43, 1, 3), 6)


def test_compute_crafts_cost_and_kamas():
    targets = [_target(900, 1, [(1, 2), (2, 1)], level=100)]  # 2 bois + 1 fer, niv 100
    stock = {1: 10, 2: 4}
    price_map = {1: 100, 2: 50}

    rows = compute_pa_brisage(targets, stock, price_map, coef=3, ga_pa_price=10_000)
    r = rows[0]
    rate = ga_pa_rate(100, 1, 3)

    assert r.craftable_now == 4                  # limité par le fer (4/1) < bois (10/2=5)
    assert r.limiting_item_id == 2
    assert r.priced is True
    assert r.unit_cost == 250                    # 100*2 + 50*1
    assert r.total_cost == 1000                  # 250 * 4
    assert r.ga_pa_rate == round(rate, 4)
    assert r.expected_ga_pa == round(4 * rate, 2)
    assert r.gross_kamas == round(4 * rate * 10_000)
    assert r.net_kamas == r.gross_kamas - 1000
    # Rentabilité à l'achat (par craft) :
    assert r.unit_revenue == round(rate * 10_000)
    assert r.unit_margin == r.unit_revenue - 250
    assert r.margin_pct == round(r.unit_margin / 250 * 100, 1)
    assert r.buy_profitable is (r.unit_margin > 0)


def test_unpriced_ingredient_leaves_cost_and_net_none_but_keeps_ga_pa():
    targets = [_target(900, 1, [(1, 1), (2, 1)], level=100)]
    rows = compute_pa_brisage(targets, {1: 5, 2: 5}, {1: 100}, coef=3, ga_pa_price=1000)
    r = rows[0]
    rate = ga_pa_rate(100, 1, 3)
    assert r.priced is False
    assert r.unit_cost is None
    assert r.total_cost is None
    assert r.net_kamas is None                   # pas de coût -> pas de net
    assert r.craftable_now == 5                  # crafts/Ga Pa restent calculés
    assert r.expected_ga_pa == round(5 * rate, 2)
    assert r.unit_revenue == round(rate * 1000)  # revenu ne dépend pas du coût
    assert r.unit_margin is None                 # coût inconnu -> marge non calculable
    assert r.buy_profitable is None


def test_no_price_means_zero_kamas():
    targets = [_target(900, 1, [(1, 1)], level=100)]
    rows = compute_pa_brisage(targets, {1: 3}, {1: 10}, coef=3, ga_pa_price=None)
    assert rows[0].gross_kamas == 0
    assert rows[0].net_kamas == -30              # 0 - (10 * 3)
    assert rows[0].unit_revenue == 0
    assert rows[0].buy_profitable is False       # 0 revenu, coût > 0


def test_buy_margin_can_be_negative():
    # Bas niveau (taux faible) + ressources chères -> achat non rentable.
    targets = [_target(900, 1, [(1, 1)], level=40)]
    rows = compute_pa_brisage(targets, {1: 3}, {1: 500}, coef=3, ga_pa_price=1000)
    r = rows[0]
    assert r.unit_revenue == round(ga_pa_rate(40, 1, 3) * 1000)
    assert r.unit_cost == 500
    assert r.unit_margin == r.unit_revenue - 500
    assert r.unit_margin < 0
    assert r.buy_profitable is False             # ❌ pas rentable d'acheter


def test_empty_recipe_is_not_craftable():
    targets = [_target(900, 1, [], level=100)]
    rows = compute_pa_brisage(targets, {}, {}, coef=3, ga_pa_price=1000)
    r = rows[0]
    assert r.craftable_now == 0
    assert r.priced is False
    assert r.expected_ga_pa == 0.0
    assert r.ga_pa_rate == round(ga_pa_rate(100, 1, 3), 4)  # le taux ne dépend pas du stock


def test_effective_cost_picks_cheaper_of_buy_or_craft():
    recipes = {900: [(1, 2)]}          # crafter 900 = 2 × item #1 (brut)
    # #1 = 300 -> craft 600 < achat 1000 -> on crafte
    eff = effective_costs([900], recipes, {900: 1000, 1: 300})
    assert eff[900]["buy"] == 1000
    assert eff[900]["craft"] == 600
    assert eff[900]["cost"] == 600
    assert eff[900]["source"] == "craft"
    # #1 = 600 -> craft 1200 > achat 1000 -> on achète
    eff2 = effective_costs([900], recipes, {900: 1000, 1: 600})
    assert eff2[900]["cost"] == 1000
    assert eff2[900]["source"] == "buy"
    # pas de prix d'achat mais craftable -> coût = craft
    eff3 = effective_costs([900], recipes, {900: None, 1: 300})
    assert eff3[900]["cost"] == 600 and eff3[900]["source"] == "craft"
    # ni achat ni sous-coût connu -> None
    assert effective_costs([900], recipes, {1: None})[900]["cost"] is None


def test_compute_uses_effective_cost_map():
    targets = [_target(900, 1, [(50, 1)], level=100)]   # 1 × item #50
    # #50 : 1000 à l'achat, 400 à crafter -> on retient 400
    cost_map = {50: {"cost": 400, "source": "craft", "buy": 1000, "craft": 400}}
    rows = compute_pa_brisage(targets, {50: 5}, {50: 1000}, coef=3,
                              ga_pa_price=10_000, cost_map=cost_map)
    r = rows[0]
    assert r.unit_cost == 400                 # coût d'appro OPTIMAL, pas le HDV 1000
    ing = r.ingredients[0]
    assert ing.buy_price == 1000
    assert ing.craft_cost == 400
    assert ing.source == "craft"
    assert ing.unit_price == 400


def test_bank_scenario_uses_free_stock_and_caps_crafts():
    # A cher (1000) couvert par la banque (3 en stock), B bon marché (10) toujours acheté.
    targets = [_target(900, 1, [(1, 1), (2, 1)], level=100)]
    rows = compute_pa_brisage(targets, {1: 3, 2: 0}, {1: 1000, 2: 10},
                              coef=3, ga_pa_price=1100)
    r = rows[0]
    rate = ga_pa_rate(100, 1, 3)
    assert r.unit_revenue == round(rate * 1100)       # ≈ 501
    assert r.buy_profitable is False                  # achat complet NON rentable (coût plein 1010)
    assert r.bank_unit_cost == 10                      # 1er craft : A gratuit (banque), on achète B
    assert r.bank_unit_margin == r.unit_revenue - 10
    assert r.bank_buy_profitable is True
    assert r.max_profitable_crafts == 3                # rentable tant que la banque couvre A
    assert r.bank_unbounded is False
    assert r.max_profit_total == 3 * r.unit_revenue - 30   # revenu×3 − achat de B ×3


def test_bank_scenario_unbounded_when_full_buy_profitable():
    targets = [_target(900, 1, [(1, 1)], level=100)]
    rows = compute_pa_brisage(targets, {1: 0}, {1: 10}, coef=3, ga_pa_price=10_000)
    r = rows[0]
    assert r.buy_profitable is True                   # revenu >> coût -> rentable même en achetant tout
    assert r.bank_unbounded is True
    assert r.max_profitable_crafts is None            # illimité
    assert r.max_profit_total is None


def test_bank_scenario_none_when_unpriced():
    targets = [_target(900, 1, [(1, 1), (2, 1)], level=100)]
    rows = compute_pa_brisage(targets, {1: 5, 2: 5}, {1: 100}, coef=3, ga_pa_price=1000)
    r = rows[0]
    assert r.bank_unit_margin is None
    assert r.bank_buy_profitable is None
    assert r.max_profitable_crafts is None
    assert r.bank_unbounded is False


def test_max_unit_price_ceiling():
    targets = [_target(900, 1, [(1, 2), (2, 1)], level=100)]   # A×2, B×1
    rows = compute_pa_brisage(targets, {}, {1: 100, 2: 50}, coef=3, ga_pa_price=10_000)
    r = rows[0]
    rev = r.unit_revenue
    byid = {i.item_id: i for i in r.ingredients}
    assert byid[1].max_unit_price == (rev - 50) // 2    # plafond A : autres = B (50)
    assert byid[2].max_unit_price == (rev - 200) // 1   # plafond B : autres = A (2×100)


def test_max_unit_price_zero_when_never_profitable():
    targets = [_target(900, 1, [(1, 2), (2, 1)], level=100)]
    rows = compute_pa_brisage(targets, {}, {1: 100, 2: 50}, coef=3, ga_pa_price=100)
    r = rows[0]
    assert r.unit_revenue < 50                 # revenu < coût des autres pour A -> jamais rentable
    assert {i.item_id: i for i in r.ingredients}[1].max_unit_price == 0


def test_max_unit_price_known_even_if_self_unpriced():
    targets = [_target(900, 1, [(1, 2), (2, 1)], level=100)]
    rows = compute_pa_brisage(targets, {}, {1: 100}, coef=3, ga_pa_price=10_000)  # B (id 2) sans prix
    r = rows[0]
    byid = {i.item_id: i for i in r.ingredients}
    assert byid[2].max_unit_price == (r.unit_revenue - 200) // 1   # plafond calculable pour B
    assert byid[1].max_unit_price is None      # A : un AUTRE ingrédient (B) sans prix -> inconnu


def test_ingredient_recipes_from_real_cache():
    rec = ingredient_recipes([159])    # La Broche Céleste (ingrédient du Rat Noir)
    assert 159 in rec                  # elle a bien une recette
    assert 441 in [sid for sid, _ in rec[159]]   # Cuivre en sous-ingrédient


def test_auto_discovered_targets_from_real_cache():
    targets, missing = load_pa_targets()         # mode défaut = auto-découverte ≤ 120
    assert missing == []
    assert len(targets) >= 40                     # ~46 équipements +PA craftables ≤ 120
    assert all(t["pa_value"] >= 1 for t in targets)
    assert all(t["recipe"] for t in targets)      # tous craftables
    assert all((t["level"] or 0) <= 120 for t in targets)

    ids = {t["item_id"] for t in targets}
    assert {8445, 323, 159}.issubset(ids)         # Rat Noir, Kam Assutra, Broche Céleste
    rat = next(t for t in targets if t["item_id"] == 8445)
    assert rat["name"] == "Collier du Rat Noir" and rat["level"] == 103
    assert GA_PA_RUNE_ID == 1557
    assert DEFAULT_COEF == 3.0


def test_max_level_filter_and_explicit_ids():
    few, _ = load_pa_targets(max_level=50)
    many, _ = load_pa_targets(max_level=120)
    assert all((t["level"] or 0) <= 50 for t in few)
    assert len(few) < len(many)                   # le plafond de niveau réduit la liste

    # Mode explicite : charge exactement les ids demandés (+ ids manquants signalés).
    targets, missing = load_pa_targets(target_ids=[8445, 99999999])
    assert [t["item_id"] for t in targets] == [8445]
    assert missing == [99999999]
