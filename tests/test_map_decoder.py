"""Tests du décodage des cellules de map (Map_Data) — marchabilité / LoS / sol.

Fixtures construites à la main : ``_make_cell`` fabrique une cellule (10 chars
pseudo-base64) avec des champs connus, selon le layout binaire porté d'Arakne :
  data[0] : bit0 = ligne de vue, bit5 (32) = active
  data[1] : bits0-3 = niveau de sol
  data[2] : bits3-5 (56) = movement (0..7)  -> walkable si >= 2
"""
from __future__ import annotations

from app.network.map_decoder import (
    decode_map_data,
    decrypt_map_data,
    get_blocked_cells,
    get_walkable_cells,
)
from app.network.protocol import MOVEMENT_HASH


def _make_cell(movement: int = 0, los: bool = False, level: int = 0,
               active: bool = True) -> str:
    d = [0] * 10
    d[0] = (1 if los else 0) | (32 if active else 0)
    d[1] = level & 15
    d[2] = (movement << 3) & 56
    return "".join(MOVEMENT_HASH[x] for x in d)


def test_decode_cells_walkability():
    m = (_make_cell(movement=4, los=True, level=3)     # 0 : marchable
         + _make_cell(movement=0, los=False, level=0)  # 1 : obstacle
         + _make_cell(movement=1, los=True, level=5))  # 2 : interactif (non marchable)
    cells = decode_map_data(m)
    assert len(cells) == 3
    assert cells[0] == {"walkable": True, "movement": 4, "line_of_sight": True,
                        "active": True, "ground_level": 3, "ground_slope": 0}
    assert cells[1]["walkable"] is False and cells[1]["movement"] == 0
    assert cells[1]["line_of_sight"] is False
    assert cells[2]["walkable"] is False and cells[2]["movement"] == 1
    assert cells[2]["line_of_sight"] is True and cells[2]["ground_level"] == 5


def test_walkable_blocked_sets():
    m = _make_cell(4, True) + _make_cell(0, False) + _make_cell(1, True)
    cells = decode_map_data(m)
    assert get_walkable_cells(cells) == {0}
    assert get_blocked_cells(cells) == {1, 2}


def test_incomplete_trailing_ignored():
    m = _make_cell(4, True) + "abc"     # 13 chars -> 1 cellule complète, reste ignoré
    assert len(decode_map_data(m)) == 1


def test_empty():
    assert decode_map_data("") == {}


def test_decrypt_vector():
    # Vecteur calculé à la main : clé 'ab' (hex 6162) -> offset checksum = 0 ;
    # "cd" xor "ab" = octets 0x02,0x06 -> hex "0206".
    assert decrypt_map_data("0206", "6162") == "cd"


def test_decode_with_key_end_to_end():
    plain = _make_cell(movement=4, los=True, level=3)          # cellule pseudo-base64
    cipher = bytes(c ^ 0x41 for c in plain.encode("latin-1")).hex()
    # clé hexa "41" -> octet 0x41 ; offset = checksum(0x41)*2 = 2, %1 = 0.
    assert decode_map_data(cipher, "41") == decode_map_data(plain)
    assert decode_map_data(cipher, "41")[0]["walkable"] is True
