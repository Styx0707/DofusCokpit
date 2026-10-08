"""Décodage des cellules d'une map Dofus 1.29 (`Map_Data` du message GDM).

Parsing PUR (lecture) : transforme la chaîne de cellules en propriétés par
cellule (marchabilité, ligne de vue, niveau de sol). Sert au handler serveur
pour valider la marchabilité réelle d'un déplacement.

Portage fidèle de l'implémentation open-source Arakne/php-map-parser (LGPL-3.0,
Vincent Quatrevieux), elle-même dérivée du client Dofus 1.29 :
- alphabet pseudo-base64 (identique à protocol.MOVEMENT_HASH), 1 cellule = 10 chars ;
- layout binaire de la cellule (Compressor.as) ;
- déchiffrement XOR des maps chiffrées (Aks.as) — clé hexa + offset checksum.

Références :
  https://github.com/Arakne/php-map-parser
  https://github.com/Emudofus/Dofus/blob/1.29/ank/battlefield/utils/Compressor.as
"""
from __future__ import annotations

import urllib.parse
from typing import Dict, Optional, Set

from app.network.protocol import MOVEMENT_HASH

CELL_LEN = 10  # une cellule = 10 caractères pseudo-base64


def _b64_ord(char: str) -> int:
    """Valeur (0..63) d'un caractère pseudo-base64 Dofus."""
    idx = MOVEMENT_HASH.find(char)
    if idx < 0:
        raise ValueError(f"caractère base64 invalide : {char!r}")
    return idx


# --- Déchiffrement XOR des maps chiffrées (Dofus 1.29 Aks) ------------------

def _urldecode(data: bytes) -> bytes:
    """Équivalent de urldecode() PHP : '+' -> espace, puis %XX -> octet."""
    return urllib.parse.unquote_to_bytes(data.replace(b"+", b" "))


def _checksum(value: bytes) -> int:
    """Checksum réseau Dofus : somme des (octet % 16), modulo 16 -> [0..15]."""
    return sum(b % 16 for b in value) % 16


def decrypt_map_data(raw_hex: str, key_hex: str, key_offset: Optional[int] = None) -> str:
    """Déchiffre des données de map chiffrées (hexa) avec la clé (hexa).

    Réplique XorCipher/MapKey d'Arakne : clé = urldecode(hex2bin(key_hex)) ;
    offset par défaut = checksum(clé) * 2 ; clé pivotée de `offset`, répétée,
    XOR octet-à-octet avec hex2bin(raw_hex), puis urldecode du résultat.
    """
    key = _urldecode(bytes.fromhex(key_hex))
    if not key:
        raise ValueError("clé de déchiffrement vide")
    value = bytes.fromhex(raw_hex)
    if key_offset is None:
        key_offset = _checksum(key) * 2
    key_offset %= len(key)
    rotated = key[key_offset:] + key[:key_offset]
    repeated = (rotated * (len(value) // len(rotated) + 1))[:len(value)]
    xored = bytes(a ^ b for a, b in zip(repeated, value))
    return _urldecode(xored).decode("latin-1")


# --- Décodage des cellules --------------------------------------------------

def _decode_cell(data: list) -> dict:
    """10 entiers (0..63) -> propriétés de la cellule."""
    movement = (data[2] & 56) >> 3          # 0..7
    return {
        # marchable côté SERVEUR : 0 = non marchable, 1 = objet interactif (non
        # marchable serveur bien que cliquable), 2..7 = marchable (poids décroissant).
        "walkable": movement >= 2,
        "movement": movement,
        "line_of_sight": (data[0] & 1) == 1,
        "active": ((data[0] & 32) >> 5) == 1,
        "ground_level": data[1] & 15,        # altitude / niveau de sol (0..15)
        "ground_slope": (data[4] & 60) >> 2,  # pente (0..15 ; 1 = plat)
    }


def decode_map_data(raw_data: str, decryption_key: Optional[str] = None) -> Dict[int, dict]:
    """Décode le `Map_Data` d'une map -> {cell_id: {walkable, movement,
    line_of_sight, active, ground_level, ground_slope}}.

    - decryption_key fourni (hexa) : `raw_data` est de l'hexa chiffré -> déchiffré
      d'abord (voir decrypt_map_data).
    - sinon : `raw_data` est déjà la chaîne pseudo-base64 des cellules.

    Les cell_id sont l'index de la cellule (0, 1, 2, …). Un éventuel dernier bloc
    incomplet (< 10 chars) est ignoré.
    """
    data = decrypt_map_data(raw_data, decryption_key) if decryption_key else raw_data
    cells: Dict[int, dict] = {}
    for cell_id, start in enumerate(range(0, len(data) - CELL_LEN + 1, CELL_LEN)):
        chunk = data[start:start + CELL_LEN]
        cells[cell_id] = _decode_cell([_b64_ord(c) for c in chunk])
    return cells


def get_walkable_cells(map_data: Dict[int, dict]) -> Set[int]:
    """Ids des cellules marchables (côté serveur)."""
    return {cid for cid, c in map_data.items() if c["walkable"]}


def get_blocked_cells(map_data: Dict[int, dict]) -> Set[int]:
    """Ids des cellules NON marchables."""
    return {cid for cid, c in map_data.items() if not c["walkable"]}
