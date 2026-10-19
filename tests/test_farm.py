"""Tests du planificateur de farm (``app.core.farm``).

Les fonctions de calcul (``classify_source``, ``flatten_resources``,
``find_spots``, ``compute_farm_plan``) sont PURES : on leur fournit des index de
zones/monstres factices. ``classify_source`` est aussi vérifiée sur le cache réel
``data/details`` (présent dans le repo) pour les types courants."""
from __future__ import annotations

import json
from collections import Counter

from app.core import farm
from app.core.farm import (
    classify_source,
    compute_farm_plan,
    family_tokens,
    find_spots,
    flatten_resources,
    live_zones_from_catalog,
    load_drops_index,
    load_monsters,
    rank_kamas,
    rank_targets,
    rank_zones,
    spots_from_drops,
)
from app.models import FarmResource


def _res(item_id, name, typ, to_buy, kind, used_in):
    return FarmResource(item_id=item_id, name=name, type=typ, qty_needed=to_buy,
                        in_bank=0, to_buy=to_buy, unit_price=None, buy_cost=None,
                        source_kind=kind, profession=None, used_in=used_in)


def test_classify_source_by_type():
    assert classify_source("Minerai") == ("harvest", "Mineur")
    assert classify_source("Pierre précieuse")[0] == "harvest"
    assert classify_source("Pierre brute")[1] == "Mineur / Bijoutier"
    assert classify_source("Bois") == ("harvest", "Bûcheron")
    assert classify_source("Écorce") == ("harvest", "Bûcheron")
    assert classify_source("Fleur") == ("harvest", "Alchimiste")
    assert classify_source("Poisson") == ("harvest", "Pêcheur")
    # Butins de monstre
    assert classify_source("Os") == ("drop", None)
    assert classify_source("Carapace") == ("drop", None)
    assert classify_source("Peau") == ("drop", None)
    # Générique / inconnu
    assert classify_source("Ressource") == ("unknown", None)
    assert classify_source(None) == ("unknown", None)
    assert classify_source("") == ("unknown", None)


def test_classify_robust_to_accent_variants():
    # Normalisation sans accents -> insensible aux variantes d'encodage du cache.
    assert classify_source("minerai") == classify_source("Minerai")
    assert classify_source("GELÉE")[0] == "drop"


def test_family_tokens_strips_stopwords_and_leading_noun():
    assert family_tokens("Pollen de Blop") == ["pollen", "blop"]   # ≤2 mots : gardés
    assert family_tokens("Oeil d'Ouginak") == ["oeil", "ouginak"]
    assert family_tokens("Testicules du Mulou Charmant") == ["mulou", "charmant"]  # >2 : 2 derniers
    assert family_tokens("Etoffe du Rat Noir") == ["rat", "noir"]
    assert family_tokens("Fer") == ["fer"]


def test_flatten_resources_descends_to_leaves():
    # 900 = 2×(id1) + 1×(id2) ; id1 = 3×(id3) ; id2, id3 feuilles.
    recipes = {900: [(1, 2), (2, 1)], 1: [(3, 3)]}
    acc: Counter = Counter()
    flatten_resources(900, 4, recipes, acc)   # 4 crafts de 900
    assert acc == {3: 24, 2: 4}               # 4×2×3 = 24 feuilles id3 ; 4×1 id2
    assert 900 not in acc and 1 not in acc     # intermédiaires non comptés


def test_flatten_resources_handles_cycles():
    recipes = {1: [(2, 1)], 2: [(1, 1)]}       # cycle 1<->2
    acc: Counter = Counter()
    flatten_resources(1, 1, recipes, acc)       # ne doit pas boucler
    assert sum(acc.values()) >= 1


def test_find_spots_matches_zone_and_monster_names():
    zone_index = (("prairie des blops", "Prairie des Blops"),
                  ("le coin des bouftous", "Le coin des Bouftous"))
    monster_index = (("le ouassingue", "Le Ouassingue"),)
    # Ressource dont le nom pointe une zone.
    spots = find_spots("Pollen de Blop", zone_index, monster_index)
    assert any(s.kind == "zone" and s.label == "Prairie des Blops" for s in spots)
    # Ressource dont le nom pointe un monstre.
    spots = find_spots("Etoffe de Ouassingue", zone_index, monster_index)
    assert any(s.kind == "monster" and s.label == "Le Ouassingue" for s in spots)


def test_find_spots_live_zone_prioritised():
    zone_index = (("foret lointaine", "Foret Lointaine"),)
    monster_index = (("bouftou", "Bouftou"),)
    live = {"bouftou": ["Le coin des Bouftous"]}
    spots = find_spots("Patte de Bouftou", zone_index, monster_index, live)
    # La zone vue en live doit remonter en tête.
    assert spots[0].kind == "zone" and spots[0].via == "live"
    assert spots[0].label == "Le coin des Bouftous"


def test_live_zones_from_catalog():
    cat = {"maps": [
        {"zone": "Le coin des Bouftous", "monsters": [{"name": "Bouftou"}, {"name": "Boufton Blanc"}]},
        {"zone": "", "monsters": [{"name": "Ignoré"}]},
    ]}
    out = live_zones_from_catalog(cat)
    assert out["bouftou"] == ["Le coin des Bouftous"]
    assert "ignore" not in out                 # zone vide -> ignorée
    assert live_zones_from_catalog(None) == {}


def test_compute_farm_plan_aggregates_and_values():
    # Cible 900 : recette 2×Minerai(1) + 1×Os(2) ; Minerai craftable ? non (feuille).
    targets = [{"item_id": 900, "name": "Amu", "level": 100, "type": "Amulette",
                "recipe": [{"item_id": 1, "name": "Fer", "quantity": 2},
                           {"item_id": 2, "name": "Os de Bouftou", "quantity": 3}]}]
    recipes = {}                                 # 1 et 2 sont des feuilles
    stock = {1: 5}                               # 5 Fer déjà en banque
    price_map = {1: 10, 2: 100}
    details = {
        1: {"id": 1, "name": "Fer", "type": "Minerai"},
        2: {"id": 2, "name": "Os de Bouftou", "type": "Os"},
    }
    monster_index = (("bouftou", "Bouftou"),)
    zone_index = (("le coin des bouftous", "Le coin des Bouftous"),)

    def fake_detail(iid, *a, **k):
        return details.get(iid)

    orig = farm.load_detail
    farm.load_detail = fake_detail
    try:
        rows = compute_farm_plan(targets, {900: 4}, recipes, stock, price_map,
                                 zone_index=zone_index, monster_index=monster_index)
    finally:
        farm.load_detail = orig

    by_id = {r.item_id: r for r in rows}
    fer, os_ = by_id[1], by_id[2]
    assert fer.qty_needed == 8 and fer.in_bank == 5 and fer.to_buy == 3
    assert fer.buy_cost == 30 and fer.source_kind == "harvest" and fer.profession == "Mineur"
    assert os_.qty_needed == 12 and os_.to_buy == 12 and os_.buy_cost == 1200
    assert os_.source_kind == "drop"
    # L'Os de Bouftou pointe vers la zone/monstre Bouftou.
    assert any("Bouftou" in s.label for s in os_.spots)
    assert fer.used_in == [900] and os_.used_in == [900]
    # Tri par coût d'achat décroissant : l'Os (1200) avant le Fer (30).
    assert rows[0].item_id == 2


def test_spots_from_drops_ranks_and_dedups():
    sources = [
        {"monster": "Tiwabbit", "rate": 5, "zones": ["Ile des Wabbits"]},
        {"monster": "Wabbit", "rate": 32, "zones": ["Ile des Wabbits", "Sous-terrains"]},
    ]
    spots = spots_from_drops(sources)
    # Zones remontées en tête, dédoublonnées (Ile des Wabbits une seule fois).
    zones = [s.label for s in spots if s.kind == "zone"]
    assert zones.count("Ile des Wabbits") == 1
    assert spots[0].kind == "zone" and spots[0].via == "drop"
    # Monstre le mieux dropeur d'abord, avec son taux.
    mons = [s for s in spots if s.kind == "monster"]
    assert mons[0].label == "Wabbit" and mons[0].rate == 32
    assert all(s.via == "drop" for s in spots)


def test_load_drops_index(tmp_path):
    (tmp_path / "drops.json").write_text(json.dumps({
        "305": {"name": "Dent de Wabbit", "sources": [{"monster": "Wabbit", "rate": 32, "zones": ["Ile"]}]},
        "999": {"name": "Sans source", "sources": []},
    }), encoding="utf-8")
    idx = load_drops_index(str(tmp_path))
    assert 305 in idx and idx[305][0]["monster"] == "Wabbit"
    assert 999 not in idx                       # sources vides -> ignoré
    assert load_drops_index(str(tmp_path / "absent")) == {}


def test_compute_farm_plan_prefers_confirmed_drops_over_heuristic():
    targets = [{"item_id": 900, "name": "A", "level": 50, "type": "Amulette",
                "recipe": [{"item_id": 2, "name": "Os de Bouftou", "quantity": 1}]}]
    details = {2: {"id": 2, "name": "Os de Bouftou", "type": "Os"}}
    orig = farm.load_detail
    farm.load_detail = lambda iid, *a, **k: details.get(iid)
    try:
        # Sans drops : heuristique de nom (via != "drop").
        rows_h = compute_farm_plan(targets, {900: 1}, {}, {}, {},
                                   zone_index=(("le coin des bouftous", "Le coin des Bouftous"),),
                                   monster_index=(("bouftou", "Bouftou"),))
        # Avec drops : pistes confirmées (via == "drop", taux porté).
        drops = {2: [{"monster": "Boufton", "rate": 50, "zones": ["Le coin des Bouftous"]}]}
        rows_d = compute_farm_plan(targets, {900: 1}, {}, {}, {},
                                   zone_index=(), monster_index=(), drops_index=drops)
    finally:
        farm.load_detail = orig
    assert all(s.via != "drop" for s in rows_h[0].spots)
    assert rows_d[0].spots and all(s.via == "drop" for s in rows_d[0].spots)
    assert any(s.kind == "monster" and s.rate == 50 for s in rows_d[0].spots)


def test_rank_zones_scores_speed_and_excludes_generics():
    resources = [
        _res(1, "Dent", "Os", 10, "drop", [900]),
        _res(2, "Peau", "Peau", 5, "drop", [901]),
        _res(3, "Eau", "Ressource", 99, "unknown", [900, 901]),   # générique -> exclu
        _res(4, "Os plein", "Os", 5, "drop", [900]),              # to_buy traité ci-dessous
    ]
    resources[3].to_buy = 0                                        # déjà en banque -> exclu
    drops = {
        1: [{"monster": "Wabbit", "rate": 40, "zones": ["Zone A"]}],
        2: [{"monster": "Bouftou", "rate": 10, "zones": ["Zone A", "Zone B"]}],
        3: [{"monster": "Boulanger", "rate": 100, "zones": ["Zone A"]}],  # générique
        4: [{"monster": "Y", "rate": 100, "zones": ["Zone A"]}],          # to_buy 0
    }
    gpu = {1: 0.5, 2: 0.5, 3: 9.9, 4: 0.5}
    out = rank_zones(resources, drops, gpu)
    by = {z["zone"]: z for z in out}
    # Zone A en tête : score = 40%×0.5 + 10%×0.5 = 0.25 ; Zone B = 10%×0.5 = 0.05.
    assert out[0]["zone"] == "Zone A"
    assert abs(by["Zone A"]["score"] - 0.25) < 1e-9
    assert abs(by["Zone B"]["score"] - 0.05) < 1e-9
    # Eau (générique) et Os plein (to_buy 0) NE gonflent PAS Zone A malgré 100%.
    assert by["Zone A"]["resource_count"] == 2
    assert by["Zone A"]["target_count"] == 2          # nourrit 900 et 901


def test_rank_targets_metrics_and_bottleneck():
    targets = [{"item_id": 900, "name": "Amu Facile", "level": 50,
                "recipe": [{"item_id": 1, "name": "Dent", "quantity": 10},
                           {"item_id": 2, "name": "Fer", "quantity": 5},
                           {"item_id": 3, "name": "Eau", "quantity": 99}]}]
    details = {
        1: {"id": 1, "name": "Dent", "type": "Os"},        # butin
        2: {"id": 2, "name": "Fer", "type": "Minerai"},     # récolte
        3: {"id": 3, "name": "Eau", "type": "Ressource"},   # générique -> ni/ni, +Eau
    }
    drops = {1: [{"monster": "Wabbit", "rate": 50, "zones": ["Zone A"]}]}
    orig = farm.load_detail
    farm.load_detail = lambda iid, *a, **k: details.get(iid)
    try:
        out = rank_targets(targets, {900: 1}, {}, {900: 0.4}, drops)
    finally:
        farm.load_detail = orig
    r = out[0]
    assert r["harvest"] == 1 and r["butins"] == 1 and r["needs_eau"] is True
    assert r["fights"] == 20                       # 10 / (50/100)
    assert abs(r["gapa_per_100"] - 2.0) < 1e-9     # 0.4 / 20 × 100
    assert r["bottleneck"]["name"] == "Dent" and r["bottleneck"]["rate"] == 50
    assert r["bottleneck"]["monster"] == "Wabbit" and r["bottleneck"]["zone"] == "Zone A"
    # cible sans craft demandé -> ignorée
    assert rank_targets(targets, {900: 0}, {}, {900: 0.4}, drops) == []


def test_rank_kamas_values_level_filter_and_zone_rollup():
    monsters = {
        "tofu": {"name": "Tofu", "level_min": 2, "level_max": 6, "zones": ["Z1"],
                 "drops": [{"item_id": 10, "name": "Plume", "rate": 50},
                           {"item_id": 11, "name": "Sans prix", "rate": 100}]},
        "boss": {"name": "Boss", "level_min": 100, "level_max": 100, "zones": ["Z2"],
                 "drops": [{"item_id": 10, "name": "Plume", "rate": 100}]},
        "vide": {"name": "Vide", "level_min": 5, "level_max": 5, "zones": ["Z1"],
                 "drops": [{"item_id": 99, "name": "X", "rate": 100}]},
    }
    price = {10: 1000, 11: None, 99: None}
    out = rank_kamas(monsters, price, level_max=50)
    names = [m["name"] for m in out["monsters"]]
    assert "Boss" not in names          # niveau 100 > 50 -> filtré
    assert "Vide" not in names          # drops sans prix -> valeur 0 -> exclu
    tofu = next(m for m in out["monsters"] if m["name"] == "Tofu")
    assert tofu["value_per_fight"] == 500      # 0,5 × 1000 (le drop sans prix ignoré)
    assert tofu["value_per_level"] == 250      # 500 / niveau 2
    assert tofu["top_drops"][0]["name"] == "Plume"
    z1 = next(z for z in out["zones"] if z["zone"] == "Z1")
    assert z1["best_monster"] == "Tofu" and z1["best_value"] == 500 and z1["best_level"] == 2


def test_rank_kamas_price_max_guards_outliers():
    monsters = {
        "m": {"name": "M", "level_min": 10, "level_max": 10, "zones": ["Z"],
              "drops": [{"item_id": 1, "name": "Normal", "rate": 50},
                        {"item_id": 2, "name": "Aberrant", "rate": 100}]},
    }
    price = {1: 1000, 2: 50_000_000}      # item 2 = prix HDV aberrant
    # Sans garde-fou : l'aberrant domine.
    no_cap = rank_kamas(monsters, price)["monsters"][0]
    assert no_cap["value_per_fight"] == 50_000_500 and no_cap["top_drops"][0]["name"] == "Aberrant"
    # Avec plafond : l'aberrant est écarté, compté dans outliers.
    out = rank_kamas(monsters, price, price_max=1_000_000)
    assert out["outliers"] == 1
    m = out["monsters"][0]
    assert m["value_per_fight"] == 500 and all(d["name"] != "Aberrant" for d in m["top_drops"])


def test_rank_kamas_exclude_special():
    monsters = {
        "tofu": {"name": "Tofu", "level_min": 2, "level_max": 2, "zones": ["Z"],
                 "drops": [{"item_id": 1, "name": "Plume", "rate": 50}]},
        "coffre": {"name": "Coffre Sombre", "level_min": 1, "level_max": 1, "zones": ["Z"],
                   "drops": [{"item_id": 1, "name": "Plume", "rate": 100}]},
        "vlad": {"name": "Dopeul Dark Vlad", "level_min": 120, "level_max": 120, "zones": ["D"],
                 "drops": [{"item_id": 1, "name": "Plume", "rate": 100}]},
    }
    price = {1: 1000}
    full = rank_kamas(monsters, price)
    assert {m["name"] for m in full["monsters"]} == {"Tofu", "Coffre Sombre", "Dopeul Dark Vlad"}
    farm_only = rank_kamas(monsters, price, exclude_special=True)
    assert {m["name"] for m in farm_only["monsters"]} == {"Tofu"}
    assert farm_only["specials"] == 2      # coffre + dopeul écartés


def test_load_monsters_missing(tmp_path):
    assert load_monsters(str(tmp_path)) == {}


def test_compute_farm_plan_skips_zero_crafts_and_unpriced():
    targets = [{"item_id": 900, "name": "A", "level": 10, "type": "Amulette",
                "recipe": [{"item_id": 1, "name": "X", "quantity": 1}]}]
    details = {1: {"id": 1, "name": "X", "type": "Ressource"}}
    orig = farm.load_detail
    farm.load_detail = lambda iid, *a, **k: details.get(iid)
    try:
        # 0 craft voulu -> aucune ressource.
        assert compute_farm_plan(targets, {900: 0}, {}, {}, {}, (), ()) == []
        # Prix inconnu -> buy_cost None, non valorisé.
        rows = compute_farm_plan(targets, {900: 2}, {}, {}, {}, (), ())
    finally:
        farm.load_detail = orig
    assert rows[0].unit_price is None and rows[0].buy_cost is None
    assert rows[0].qty_needed == 2
