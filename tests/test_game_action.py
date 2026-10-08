"""Test unitaire IN-MEMORY du handler serveur de déplacement (émulateur).

Injecte une fixture GA001 directement dans GameActionHandler.handle_movement
(aucune socket) et vérifie le nouvel état du joueur + le paquet broadcast.
Fixture : "aaadbKfiV" -> cellules [0, 100, 559] (arrivée = 559).
"""
from __future__ import annotations

from app.network.game_action import GameActionHandler


def test_movement_met_a_jour_cellule_et_broadcast():
    h = GameActionHandler()
    res = h.handle_movement(player_id=1353357, current_cell=0, raw_path="aaadbKfiV")
    assert res["ok"] is True
    assert res["from"] == 0
    assert res["to"] == 559              # cellule d'arrivée = dernière du chemin
    assert res["path"] == [0, 100, 559]
    assert res["broadcast"] == "GA;1;1353357;aaadbKfiV"
    # État serveur mis à jour.
    assert h.players[1353357]["cell_id"] == 559


def test_movement_chemin_vide_refuse():
    h = GameActionHandler()
    res = h.handle_movement(player_id=1, current_cell=5, raw_path="")
    assert res["ok"] is False
    assert res["broadcast"] is None
    assert 1 not in h.players            # état inchangé


def test_movement_cellule_hors_map_refuse():
    h = GameActionHandler()
    # "a__" : cellule "__" = 63*64 + 63 = 4095 > 559 -> hors map
    res = h.handle_movement(player_id=1, current_cell=0, raw_path="a__")
    assert res["ok"] is False
    assert res["reason"] == "cellule hors map"
    assert 1 not in h.players


def test_movement_deux_joueurs_independants():
    h = GameActionHandler()
    h.handle_movement(player_id=1, current_cell=0, raw_path="aaa")     # -> 0
    h.handle_movement(player_id=2, current_cell=0, raw_path="fiV")     # -> 559
    assert h.players[1]["cell_id"] == 0
    assert h.players[2]["cell_id"] == 559
