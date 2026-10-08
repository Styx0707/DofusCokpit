"""Tests du décodage d'un chemin de déplacement (GA001, client->serveur).

Parsing PUR : reconstitue la liste des POINTS D'INFLEXION (direction, cell_id)
d'un chemin déjà émis (réception côté serveur) — le client compresse les lignes
droites, chaque bloc est un segment, pas une cellule adjacente (cf. docstring
de decode_movement_path). Fixtures construites à la main depuis l'alphabet
base-64 Dofus :
  index : a=0, b=1, d=3, f=5, i=8 ; K=36, V=47
  cellule = index(c1) * 64 + index(c2)
  bloc = 1 char direction + 2 chars cellule d'arrivée du segment
"""
from __future__ import annotations

from app.network.protocol import MOVEMENT_HASH, decode_movement_path


def test_alphabet():
    assert len(MOVEMENT_HASH) == 64
    assert MOVEMENT_HASH[0] == "a"
    assert MOVEMENT_HASH[36] == "K"
    assert MOVEMENT_HASH[47] == "V"


def test_vide():
    assert decode_movement_path("") == []


def test_un_segment_cellule_0():
    # "aaa" : direction 'a'(0) + cellule "aa" = 0
    assert decode_movement_path("aaa") == [(0, 0)]


def test_un_segment_cellule_100():
    # "dbK" : direction 'd'(3) + cellule "bK" = 1*64 + 36 = 100
    assert decode_movement_path("dbK") == [(3, 100)]


def test_cellule_max():
    # "fiV" : direction 'f'(5) + cellule "iV" = 8*64 + 47 = 559 (dernière cellule)
    assert decode_movement_path("fiV") == [(5, 559)]


def test_chemin_multi_segments():
    assert decode_movement_path("aaadbKfiV") == [(0, 0), (3, 100), (5, 559)]


def test_bloc_incomplet_ignore():
    # 5 caractères : le bloc final tronqué "db" est ignoré.
    assert decode_movement_path("aaadb") == [(0, 0)]


def test_caractere_hors_alphabet_ignore():
    # Caractère de cellule invalide -> bloc ignoré silencieusement.
    assert decode_movement_path("a!x") == []
