"""Tests de app.core.zone_sniffer.ZoneSniffer (agrégation maps/monstres par zone).

Hermétique : on patche les tables de protocol (MAP_ZONES / MONSTER_NAMES /
ARCHI_IDS) pour ne pas dépendre des fichiers data/.
"""
from __future__ import annotations

import pytest

from app.core.zone_sniffer import ZoneSniffer
from app.network import protocol


@pytest.fixture(autouse=True)
def fake_tables(monkeypatch):
    monkeypatch.setattr(protocol, "MAP_ZONES", {
        8504: "L'Ile de Grobe", 8505: "L'Ile de Grobe",
        8530: "Pont de Grobe", 100: "Plaine des Scarafeuilles",
    })
    monkeypatch.setattr(protocol, "MAP_COORDS", {8504: [10, -20]})
    monkeypatch.setattr(protocol, "MONSTER_NAMES", {517: "Fantome Bulbe", 566: "Bambouto"})
    monkeypatch.setattr(protocol, "ARCHI_IDS", {566})


def _gm_group(cell: int, gid: int, ids, levels):
    # Format GM réel : +cell;?;?;<gid négatif>;<ids csv>;?;?;<niveaux csv>
    return (f"GM|+{cell};5;10;{gid};{','.join(map(str, ids))};0;0;"
            f"{','.join(map(str, levels))}")


def test_filtre_zone_et_niveaux():
    s = ZoneSniffer(zone_filter="Grobe")
    s.feed([
        ("c1", "GDM|8504|0|x"),
        ("c1", _gm_group(346, -3, [517, 566], [45, 80])),
        ("c1", "GDM|100|0|x"),                     # hors zone -> ignoré
        ("c1", _gm_group(10, -1, [999], [12])),
    ])
    cat = s.catalog()
    assert cat["maps_seen"] == 1
    m = cat["maps"][0]
    assert m["map_id"] == 8504
    assert m["coord"] == [10, -20]
    assert m["archi_present"] is True          # 566 est archi
    by_id = {mon["id"]: mon for mon in m["monsters"]}
    assert by_id[517]["name"] == "Fantome Bulbe"
    assert by_id[517]["levels"] == [45]
    assert by_id[566]["archi"] is True
    assert 999 not in by_id                     # map hors zone non cataloguée


def test_pont_de_grobe_matche_le_filtre():
    s = ZoneSniffer(zone_filter="grobe")  # insensible à la casse
    s.feed([("c1", "GDM|8530|0|x"), ("c1", _gm_group(5, -1, [517], [50]))])
    cat = s.catalog()
    assert {mv["map_id"] for mv in cat["maps"]} == {8530}
    assert cat["maps"][0]["zone"] == "Pont de Grobe"


def test_niveaux_multiples_et_sightings():
    s = ZoneSniffer(zone_filter="Grobe")
    s.feed([
        ("c1", "GDM|8504|0|x"),
        ("c1", _gm_group(1, -1, [517], [45])),
        ("c1", "GDM|8505|0|x"),
        ("c1", "GDM|8504|0|x"),                 # revient : 2 visites
        ("c1", _gm_group(2, -1, [517], [60])),
    ])
    cat = s.catalog()
    m = next(mv for mv in cat["maps"] if mv["map_id"] == 8504)
    assert m["visits"] == 2
    mon = m["monsters"][0]
    assert mon["levels"] == [45, 60]
    assert mon["sightings"] == 2


def test_maps_manquantes_de_la_zone():
    s = ZoneSniffer(zone_filter="Grobe")
    s.feed([("c1", "GDM|8504|0|x")])
    cat = s.catalog()
    # zone « grobe » = {8504, 8505, 8530} dans la table patchée ; vu = {8504}
    assert cat["maps_total_in_zone"] == 3
    assert cat["maps_missing"] == [8505, 8530]


def test_zone_none_garde_tout():
    s = ZoneSniffer(zone_filter=None)
    s.feed([("c1", "GDM|100|0|x"), ("c1", _gm_group(1, -1, [999], [12]))])
    cat = s.catalog()
    assert cat["maps_seen"] == 1
    assert cat["maps"][0]["map_id"] == 100
    assert cat["maps_total_in_zone"] is None


def test_actors_sans_map_courante_ignores():
    s = ZoneSniffer(zone_filter="Grobe")
    # GM avant tout GDM : pas de map courante -> ne crashe pas, rien catalogué
    s.feed([("c1", _gm_group(1, -1, [517], [45]))])
    assert s.catalog()["maps_seen"] == 0


def test_alerte_archi_sur_la_map():
    s = ZoneSniffer(zone_filter="Grobe")  # ARCHI_IDS={566} (fixture)
    s.feed([("c1", "GDM|8504|0|x"),
            ("c1", _gm_group(1, -1, [517, 566], [45, 80]))], ts=100.0)
    res = s.alerts_since(0)
    archi = [a for a in res["alerts"] if a["reason"] == "archi"]
    assert len(archi) == 1
    assert archi[0]["map_id"] == 8504
    assert archi[0]["zone"] == "L'Ile de Grobe"
    assert archi[0]["ts"] == 100.0
    assert "Bambouto" in archi[0]["label"]      # 566 = nom patché


def test_alerte_groupe_regle_seuil():
    # règle : >= 2 monstres d'id 517 dans un même groupe
    s = ZoneSniffer(zone_filter="Grobe", group_alert_rules=((517, 2),))
    s.feed([("c1", "GDM|8504|0|x"),
            ("c1", _gm_group(1, -1, [517, 517, 566], [45, 45, 80]))])
    by_reason = {a["reason"]: a for a in s.alerts_since(0)["alerts"]}
    assert "grp517" in by_reason
    assert by_reason["grp517"]["label"].startswith("2×")
    # un seul 517 -> pas d'alerte de groupe
    s2 = ZoneSniffer(zone_filter="Grobe", group_alert_rules=((517, 2),))
    s2.feed([("c1", "GDM|8505|0|x"), ("c1", _gm_group(1, -1, [517, 566], [45, 80]))])
    assert not [a for a in s2.alerts_since(0)["alerts"] if a["reason"] == "grp517"]


def test_alerts_since_incremental():
    s = ZoneSniffer(zone_filter="Grobe")
    s.feed([("c1", "GDM|8504|0|x"), ("c1", _gm_group(1, -1, [566], [80]))])
    first = s.alerts_since(0)
    seq = first["max_seq"]
    assert seq >= 1
    # rien de neuf depuis seq
    assert s.alerts_since(seq)["alerts"] == []
    # nouvelle apparition -> nouvelle alerte, seq incrémenté
    s.feed([("c1", _gm_group(2, -2, [566], [80]))])
    nxt = s.alerts_since(seq)
    assert len(nxt["alerts"]) == 1
    assert nxt["alerts"][0]["seq"] > seq


def test_alerts_filtre_zone():
    s = ZoneSniffer(zone_filter=None)  # ingère toutes zones
    s.feed([("c1", "GDM|100|0|x"), ("c1", _gm_group(1, -1, [566], [80]))])  # zone hors Grobe
    assert s.alerts_since(0, zone="Grobe")["alerts"] == []
    assert len(s.alerts_since(0)["alerts"]) == 1


def _map(cat, map_id):
    return next(mv for mv in cat["maps"] if mv["map_id"] == map_id)


def test_groupes_courants_dans_catalog():
    s = ZoneSniffer(zone_filter="Grobe")
    s.feed([("c1", "GDM|8504|0|x"), ("c1", _gm_group(10, -1, [517, 566], [45, 80]))])
    g = _map(s.catalog(), 8504)["groups"]
    assert len(g) == 1
    assert g[0]["cell"] == 10
    assert g[0]["total_level"] == 125
    assert g[0]["over"] is False
    assert {x["id"] for x in g[0]["monsters"]} == {517, 566}
    assert any(x["archi"] for x in g[0]["monsters"])          # 566 = archi (fixture)


def test_indicateur_gros_groupe():
    s = ZoneSniffer(zone_filter="Grobe")  # seuil défaut 949
    s.feed([("c1", "GDM|8504|0|x"),
            ("c1", _gm_group(5, -1, [517, 517, 517], [400, 400, 200]))])  # somme 1000
    cat = s.catalog()
    m = _map(cat, 8504)
    assert m["has_big_group"] is True
    assert m["groups"][0]["over"] is True
    assert m["groups"][0]["total_level"] == 1000
    assert cat["group_level_warn"] == 949


def test_seuil_configurable_et_retrait_groupe():
    s = ZoneSniffer(zone_filter="Grobe", group_level_warn=100)
    s.feed([("c1", "GDM|8504|0|x"), ("c1", _gm_group(5, -3, [517], [120]))])
    assert _map(s.catalog(), 8504)["groups"][0]["over"] is True     # 120 > 100
    s.feed([("c1", "GM|-3")])                                       # groupe -3 tué/parti
    assert _map(s.catalog(), 8504)["groups"] == []


def test_rechargement_map_vide_les_groupes():
    s = ZoneSniffer(zone_filter="Grobe")
    s.feed([("c1", "GDM|8504|0|x"), ("c1", _gm_group(1, -1, [517], [45]))])
    assert len(_map(s.catalog(), 8504)["groups"]) == 1
    s.feed([("c1", "GDM|8504|0|x")])                               # rechargement map
    assert _map(s.catalog(), 8504)["groups"] == []
    # l'agrégat cumulatif de monstres, lui, est conservé
    assert any(mo["id"] == 517 for mo in _map(s.catalog(), 8504)["monsters"])
