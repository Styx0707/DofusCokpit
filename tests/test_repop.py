"""Tests du suivi de repop : décodage GDM/GM (échantillon RÉEL) + moniteur.

Aucune dépendance Scapy (protocol et repop_monitor sont purs).
Échantillons issus de data/pandala.pcapng (île de Pandala).
"""
from __future__ import annotations

from app.core.repop_monitor import RepopMonitor
from app.network.protocol import (
    BAMBOUTO_SACRE_ID,
    parse_map_actors,
    parse_map_change,
)

# --- Décodage protocole ------------------------------------------------------

def test_parse_map_change():
    assert parse_map_change("GDM|8158|0907151356|54425b444c60") == 8158
    assert parse_map_change("GDM|8157|0902171654|6d7c666a") == 8157
    assert parse_map_change("GM|+37;2;0") is None  # pas un GDM


def test_parse_map_actors_groups():
    # 3 groupes de monstres réels de la map 8158 (version tronquée aux champs utiles).
    gm = ("GM|+370;5;21;-1;566;-3;1260^110;52"
          "|+82;7;15;-2;517;-3;1260^100;45"
          "|+346;5;10;-3;517,566,549;-3;1260^100,1260^90,1274^100;45,40,70")
    groups = parse_map_actors(gm)
    assert len(groups) == 3
    assert all(g["op"] == "add" for g in groups)

    solo = groups[0]
    assert solo["cell"] == 370 and solo["group_id"] == -1
    assert solo["monsters"] == [{"id": 566, "level": 52}]

    trio = groups[2]
    assert trio["cell"] == 346
    assert [m["id"] for m in trio["monsters"]] == [517, 566, 549]
    assert [m["level"] for m in trio["monsters"]] == [45, 40, 70]


def test_parse_map_actors_player():
    # Le joueur (id positif + nom) est renvoyé avec kind='player' (pas un groupe).
    player = "GM|+37;2;0;1353357;Styxh-[Gal];9;90^100;0;0,0,0,1353557;fbfad6"
    assert parse_map_actors(player) == [
        {"op": "add", "kind": "player", "cell": 37,
         "sprite_id": 1353357, "name": "Styxh-[Gal]"}
    ]


def test_parse_map_actors_remove():
    # Format de retrait SUPPOSÉ (à confirmer sur une capture de combat) : le '-'
    # est l'opération, on reconstruit l'id négatif du groupe (-3).
    removed = parse_map_actors("GM|-3")
    assert removed == [{"op": "remove", "kind": "group", "cell": None,
                        "group_id": -3, "monsters": []}]


def test_bambouto_sacre_id():
    # Groupe réel de la map 8157 contenant le Bambouto Sacré (546).
    gm = "GM|+370;5;21;-1;524,524,546,524,524,548;-3;0;18,18,87,16,18,19"
    (grp,) = parse_map_actors(gm)
    assert BAMBOUTO_SACRE_ID == 546
    assert any(m["id"] == BAMBOUTO_SACRE_ID for m in grp["monsters"])


# --- Moniteur ----------------------------------------------------------------

STREAM = ("10.0.0.2", 51000)


def _add(cell, gid, monsters):
    return {"op": "add", "cell": cell, "group_id": gid, "monsters": monsters}


def _remove(gid):
    return {"op": "remove", "cell": None, "group_id": gid, "monsters": []}


def test_monitor_tracks_groups_and_target():
    mon = RepopMonitor(target_ids=(546,))
    mon.on_map_change(STREAM, 8157, 1000.0)
    mon.on_actors(STREAM, [
        _add(343, -1, [{"id": 517, "level": 40}]),
        _add(370, -2, [{"id": 546, "level": 87}]),
    ], 1000.0)

    snap = mon.snapshot(1001.0)
    (mp,) = [m for m in snap["maps"] if m["map_id"] == 8157]
    assert mp["active"] is True
    assert mp["target_present"] is True
    assert len(mp["groups"]) == 2
    target_group = [g for g in mp["groups"] if g["is_target"]][0]
    assert target_group["monsters"][0]["name"] == "Bambouto Sacré"


def test_monitor_learns_repop_interval():
    mon = RepopMonitor(target_ids=(546,))
    mon.on_map_change(STREAM, 8157, 0.0)
    mon.on_actors(STREAM, [_add(370, -1, [{"id": 546, "level": 87}])], 0.0)
    # Groupe tué à t=10, repop d'un groupe cible à t=310 -> intervalle 300 s.
    mon.on_actors(STREAM, [_remove(-1)], 10.0)
    assert mon.snapshot(11.0)["maps"][0]["target_present"] is False
    mon.on_actors(STREAM, [_add(372, -2, [{"id": 546, "level": 80}])], 310.0)
    assert mon.estimate_repop(8157) == 300.0

    # Nouveau kill à t=400 : le compte à rebours part de l'estimation (300 s).
    mon.on_actors(STREAM, [_remove(-2)], 400.0)
    (mp,) = mon.snapshot(450.0)["maps"]
    assert mp["target_present"] is False
    assert mp["repop_estimate_s"] == 300.0
    assert mp["repop_countdown_s"] == 250.0  # 400 + 300 - 450


def test_monitor_flags_archi():
    from app.network import protocol
    saved = protocol.ARCHI_IDS
    protocol.ARCHI_IDS = {546}
    try:
        mon = RepopMonitor(target_ids=(546,))
        mon.on_map_change(STREAM, 8157, 0.0)
        mon.on_actors(STREAM, [_add(370, -1, [{"id": 546, "level": 90}])], 0.0)
        (mp,) = mon.snapshot(1.0)["maps"]
        assert mp["archi_present"] is True
        assert mp["groups"][0]["monsters"][0]["archi"] is True
    finally:
        protocol.ARCHI_IDS = saved


def test_monitor_resolves_character_name():
    mon = RepopMonitor(target_ids=(546,))
    # Map A : notre perso Styxh + un autre joueur de passage (Bob).
    mon.on_map_change(STREAM, 8157, 0.0)
    mon.on_actors(STREAM, [
        {"op": "add", "kind": "player", "cell": 37, "sprite_id": 1, "name": "Styxh"},
        {"op": "add", "kind": "player", "cell": 40, "sprite_id": 2, "name": "Bob"},
    ], 0.0)
    # Map B : seul Styxh a suivi -> il est présent sur les 2 maps du flux.
    mon.on_map_change(STREAM, 8158, 1.0)
    mon.on_actors(STREAM, [
        {"op": "add", "kind": "player", "cell": 50, "sprite_id": 1, "name": "Styxh"},
    ], 1.0)
    (acc,) = mon.snapshot(2.0)["accounts"]
    assert acc["name"] == "Styxh"


def test_monitor_emits_appearance():
    mon = RepopMonitor(target_ids=(546,))
    events = []
    mon.on_appearance = events.append
    mon.on_map_change(STREAM, 8157, 1000.0)
    mon.on_actors(STREAM, [
        _add(343, -1, [{"id": 517, "level": 40}]),   # ni cible ni archi -> rien
        _add(370, -2, [{"id": 546, "level": 87}]),   # cible -> 1 apparition
    ], 1000.0)
    assert len(events) == 1
    e = events[0]
    assert e["map_id"] == 8157
    assert e["is_target"] is True and e["is_archi"] is False
    assert 546 in e["monster_ids"] and e["ts"] == 1000.0


def test_monitor_load_history():
    # Ré-amorçage type DB (get_map_history) : la heatmap survit au redémarrage.
    mon = RepopMonitor(target_ids=(546,))
    n = mon.load_history([
        {"map_id": 8157, "target_hits": 5, "archi_hits": 2,
         "last_target_ts": 1000.0, "last_archi_ts": 900.0},
    ])
    assert n == 1
    (mp,) = [m for m in mon.snapshot(2000.0)["maps"] if m["map_id"] == 8157]
    assert mp["target_hits"] == 5 and mp["archi_hits"] == 2
    assert mp["active"] is False and mp["target_present"] is False  # historique seul


def test_monitor_no_estimate_before_cycle():
    mon = RepopMonitor(target_ids=(546,))
    mon.on_map_change(STREAM, 8157, 0.0)
    mon.on_actors(STREAM, [_add(370, -1, [{"id": 546, "level": 87}])], 0.0)
    mon.on_actors(STREAM, [_remove(-1)], 5.0)
    (mp,) = mon.snapshot(6.0)["maps"]
    # Aucun cycle mort->repop observé : pas de compte à rebours inventé.
    assert mp["repop_estimate_s"] is None
    assert mp["repop_countdown_s"] is None
