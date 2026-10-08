"""Tests des encodeurs serveur->client : aller-retour avec les décodeurs
(encode -> decode == structure d'origine), utile pour valider un émulateur.

Échantillons réels issus de data/pandala.pcapng comme fixtures.
"""
from __future__ import annotations

import pytest

from app.network.encoder import (
    encode_bank_storage,
    encode_character_inventory,
    encode_character_list,
    encode_map_actors,
    encode_map_change,
    encode_movement_path,
)
from app.network.game_action import GameActionHandler
from app.network.protocol import (
    BANK_MESSAGE_PREFIX,
    CHARACTER_LIST_PREFIX,
    decode_movement_path,
    parse_bank_storage,
    parse_character_inventory,
    parse_character_list,
    parse_map_actors,
    parse_map_change,
)


def test_bank_roundtrip():
    inv = {1522: 11487, 749: 5350, 746: 302}
    msg = encode_bank_storage(inv)
    assert msg.startswith(BANK_MESSAGE_PREFIX)
    assert parse_bank_storage(msg[len(BANK_MESSAGE_PREFIX):]) == inv


def test_map_change_roundtrip():
    assert parse_map_change(encode_map_change(8158)) == 8158
    assert parse_map_change(encode_map_change(8157, version="0902171654")) == 8157


def test_group_roundtrip():
    actor = {"op": "add", "kind": "group", "cell": 346, "group_id": -3,
             "monsters": [{"id": 517, "level": 45},
                          {"id": 566, "level": 40},
                          {"id": 549, "level": 70}]}
    assert parse_map_actors(encode_map_actors([actor])) == [actor]


def test_player_roundtrip():
    actor = {"op": "add", "kind": "player", "cell": 37,
             "sprite_id": 1353357, "name": "Styxh-[Gal]"}
    assert parse_map_actors(encode_map_actors([actor])) == [actor]


def test_remove_roundtrip():
    actor = {"op": "remove", "kind": "group", "cell": None,
             "group_id": -3, "monsters": []}
    assert parse_map_actors(encode_map_actors([actor])) == [actor]


def test_multi_actors_roundtrip():
    actors = [
        {"op": "add", "kind": "group", "cell": 370, "group_id": -1,
         "monsters": [{"id": 566, "level": 52}]},
        {"op": "add", "kind": "player", "cell": 82,
         "sprite_id": 999, "name": "Mule-2"},
    ]
    assert parse_map_actors(encode_map_actors(actors)) == actors


def test_character_list_roundtrip():
    # Écran de sélection : 2 persos (équip visible en gid, classe/sexe via gfx).
    chars = [
        {"character_id": 1, "name": "Styxh", "level": 200, "class_id": 12,
         "class_name": "Pandawa", "sex": 0, "equipment": [746, 7154]},
        {"character_id": 2, "name": "Mule", "level": 1, "class_id": 1,
         "class_name": "Feca", "sex": 1, "equipment": []},
    ]
    msg = encode_character_list(chars)
    assert msg.startswith(CHARACTER_LIST_PREFIX)
    assert parse_character_list(msg[len(CHARACTER_LIST_PREFIX):]) == chars


def test_character_inventory_roundtrip():
    # Entrée en jeu : équipement porté trié par slot (0 Amu, 1 Arme, 6 Coiffe).
    char = {
        "character_id": 1353357, "name": "Styxh", "level": 200,
        "class_id": 12, "class_name": "Pandawa", "sex": 0,
        "equipment": [
            {"slot": 0, "slot_name": "Amulette", "item_id": 746, "stats": "7c#1e#28#0,"},
            {"slot": 1, "slot_name": "Arme", "item_id": 7154, "stats": ""},
            {"slot": 6, "slot_name": "Coiffe", "item_id": 8272, "stats": "7d#32#3c#0,"},
        ],
    }
    assert parse_character_inventory(encode_character_inventory(char)) == char


def test_character_inventory_sans_equip():
    char = {"character_id": 42, "name": "Nu", "level": 1, "class_id": 8,
            "class_name": "Iop", "sex": 0, "equipment": []}
    assert parse_character_inventory(encode_character_inventory(char)) == char


def test_movement_path_roundtrip_waypoints():
    # Structure de waypoints compressés (direction, cell_id) — un par point
    # d'inflexion, pas par cellule traversée (cf. decode_movement_path).
    waypoints = [(0, 0), (3, 100), (5, 559)]
    path = encode_movement_path(waypoints)
    assert decode_movement_path(path) == waypoints


def test_movement_path_rejette_direction_hors_alphabet():
    with pytest.raises(ValueError):
        encode_movement_path([(8, 0)])


def test_movement_path_rejette_cell_hors_alphabet():
    with pytest.raises(ValueError):
        encode_movement_path([(0, 4096)])


def test_movement_path_nourrit_le_handler_emulateur():
    # Le rêve concret : on encode un chemin, on le fait "recevoir" par le
    # handler serveur qu'on a écrit nous-mêmes (aucune socket, aucun jeu tiers)
    # et on observe le perso arriver à destination dans SON état.
    waypoints = [(0, 0), (3, 100), (5, 559)]
    path = encode_movement_path(waypoints)
    handler = GameActionHandler()
    res = handler.handle_movement(player_id=1, current_cell=0, raw_path=path)
    assert res["ok"] is True
    assert res["path"] == [0, 100, 559]
    assert res["to"] == 559
    assert handler.players[1]["cell_id"] == 559


# Trames réelles (raw_path d'un message client->serveur "GA0;1;<id>;<raw_path>"),
# capturées dans data/gamouv.pcapng et consorts : décoder puis ré-encoder doit
# reproduire la trame BYTE POUR BYTE — aucune interpolation, aucune perte.
REAL_MOVEMENT_FIXTURES = [
    "afrdfF",        # data/game.pcapng — ligne droite, 2 points d'inflexion
    "aaMfax",        # data/gamouv.pcapng (map 7983)
    "abEcfgbfZchk",  # data/gamouv.pcapng — 4 segments (changements d'angle)
    "ag8gdufcNgaw",  # data/gamouv.pcapng (map 7982) — retour du trajet précédent
    "aaLfaw",        # data/pandala.pcapng (map 8158)
]


@pytest.mark.parametrize("raw_path", REAL_MOVEMENT_FIXTURES)
def test_movement_path_reencode_trame_reelle(raw_path):
    waypoints = decode_movement_path(raw_path)
    assert encode_movement_path(waypoints) == raw_path


def test_fixture_reencode_stable():
    # Fixture réelle (map 8158) : decode -> re-encode -> re-decode == même modèle.
    gm = ("GM|+346;5;10;-3;517,566,549;-3;1260^100,1260^90,1274^100;45,40,70")
    once = parse_map_actors(gm)
    twice = parse_map_actors(encode_map_actors(once))
    assert once == twice
    assert twice[0]["group_id"] == -3
    assert [m["id"] for m in twice[0]["monsters"]] == [517, 566, 549]
