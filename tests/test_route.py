"""Tests de l'optimiseur de tournée (serpentin, métriques, découpe)."""
from __future__ import annotations

from app.core.route import connected_components, plan_route, snake_order, split_route

# Grille 3x2 :  y=0 -> maps 1,2,3 (x=0,1,2) ; y=1 -> maps 4,5,6 (x=0,1,2)
GRID = {1: (0, 0), 2: (1, 0), 3: (2, 0), 4: (0, 1), 5: (1, 1), 6: (2, 1)}


def test_snake_order_alterne_les_lignes():
    # Ligne y=0 gauche->droite, ligne y=1 droite->gauche (serpentin).
    assert snake_order(GRID) == [1, 2, 3, 6, 5, 4]


def test_plan_route_metriques():
    plan = plan_route(GRID)
    assert plan["order"] == [1, 2, 3, 6, 5, 4]
    assert plan["total_steps"] == 5          # 5 sauts d'1 case
    assert plan["loop_back_steps"] == 1      # 4 (0,1) -> 1 (0,0)
    assert plan["connected"] is True
    assert plan["n_components"] == 1


def test_split_en_deux_comptes():
    order = plan_route(GRID)["order"]
    assert split_route(order, 2) == [[1, 2, 3], [6, 5, 4]]


def test_split_remplit_les_segments_vides():
    assert split_route([10], 3) == [[10], [], []]


def test_composantes_non_connexes():
    coords = {1: (0, 0), 2: (1, 0), 9: (50, 50)}  # 9 isolée
    plan = plan_route(coords)
    assert plan["connected"] is False
    assert plan["n_components"] == 2
