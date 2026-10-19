"""Tests du décodage protocole — basés sur un ÉCHANTILLON RÉEL capturé.

Aucune dépendance Scapy (app.network.protocol est pur).
"""
from __future__ import annotations

from app.network.protocol import (
    BANK_MESSAGE_PREFIX,
    HDV_AVG_PRICE_PREFIX,
    HDV_ITEM_PRICE_PREFIX,
    parse_bank_storage,
    parse_hdv_avg_price,
    parse_hdv_item_prices,
)


def test_prefix_is_el():
    assert BANK_MESSAGE_PREFIX == "EL"


def test_parse_real_bank_sample():
    # Corps du message 'EL' réel (préfixe déjà retiré, comme le fait le sniffer).
    payload = "O13e1af55~5f2~2cdf~~7e#1##;O13e1af59~2ed~14e6~~;O13e1af5a~2ea~12e~~"
    inv = parse_bank_storage(payload)
    # 0x5f2=1522 -> 0x2cdf=11487 ; 0x2ed=749 -> 0x14e6=5350 ; 0x2ea=746 -> 0x12e=302
    assert inv == {1522: 11487, 749: 5350, 746: 302}


def test_aggregates_same_gid():
    # Deux piles du même objet (gid 0x2ea=746) : les quantités s'additionnent.
    payload = "O1~2ea~10~~;O2~2ea~5~~"  # 0x10=16 + 0x5=5
    assert parse_bank_storage(payload) == {746: 21}


def test_ignores_garbage():
    assert parse_bank_storage("") == {}
    assert parse_bank_storage("Oxx~~") == {}
    assert parse_bank_storage("O1~nothex~5~~") == {}


# --- Hôtel de vente (HDV) : échantillons réels de data/hdv.pcapng ------------

def test_hdv_prefixes():
    assert HDV_AVG_PRICE_PREFIX == "EHP"
    assert HDV_ITEM_PRICE_PREFIX == "EHl"


def test_parse_hdv_avg_price_real():
    # 'EHP<gid>|<prixMoyen>' (préfixe retiré) : prix moyen unitaire.
    assert parse_hdv_avg_price("1022|267") == (1022, 267)
    assert parse_hdv_avg_price("376|26") == (376, 26)


def test_parse_hdv_avg_price_rejects_garbage():
    assert parse_hdv_avg_price("1022") is None          # pas de séparateur
    assert parse_hdv_avg_price("xx|10") is None          # gid non numérique
    assert parse_hdv_avg_price("1022|") is None          # prix manquant


def test_parse_hdv_item_prices_resource():
    # RESSOURCE empilable : '<qty>;;<lot1>;<lot10>;<lot100>;<gid>'. On retient le
    # lot de 1 (prix unitaire courant) ; virgule = décimale client.
    assert parse_hdv_item_prices("376|756;;19,0;138,0;2688,0;376") == {
        "item_id": 376, "price": 19}
    assert parse_hdv_item_prices("1022|37048;;190,0;;;1022") == {
        "item_id": 1022, "price": 190}
    # pas de lot de 1 en vente -> price None (l'appelant retombe sur le prix moyen).
    assert parse_hdv_item_prices("2586|2476;;;847,0;7996,0;2586") == {
        "item_id": 2586, "price": None}


def test_parse_hdv_item_prices_equipment_takes_min():
    # ÉQUIPEMENT : liste d'ordres '<inst>;<stats#…>;<prix>,0;;;<gid>|…'. Le 1er ordre
    # (29999999) N'EST PAS le moins cher -> on doit retenir le MIN (23000000).
    payload = ("8991|487581;76#31##0d0+49,f1#3##0d0+3;29999999,0;;;8991"
               "|364034;76#26##0d0+38;24500000,0;;;8991"
               "|364022;76#21##0d0+33;23000000,0;;;8991"
               "|183708728;76#32##0d0+50;134999969,0;;;8991")
    assert parse_hdv_item_prices(payload) == {"item_id": 8991, "price": 23000000}
    # les bonus de stats (… +49,f1 …) ne doivent JAMAIS être pris pour un prix.
    assert parse_hdv_item_prices("8991|1;76#31##0d0+49;5000,0;;;8991")["price"] == 5000
