"""Encodeurs des messages du protocole Dofus Retro (l'inverse de
``app.network.protocol``). Utile pour un ÉMULATEUR open-source : produire les
messages que le serveur envoie au client, et fabriquer des fixtures de test.

Portée volontairement limitée à la SÉRIALISATION en texte protocolaire —
aucun envoi réseau, aucune connexion au jeu, ici ou ailleurs dans ce module.
Essentiellement des messages serveur->client (GDM/GM/EL) ; ``encode_movement_path``
fait exception (c'est un message client->serveur, GA001) mais reste une fixture
pure : elle sert à nourrir ``GameActionHandler.handle_movement`` EN MÉMOIRE dans
les tests (cf. tests/test_encoder.py), pas à piloter une connexion réelle. Elle
encode des WAYPOINTS COMPRESSÉS (points d'inflexion), pas des cellules
interpolées — cf. docstring de ``protocol.decode_movement_path``.

Chaque encodeur produit une forme CANONIQUE qui se re-décode à l'identique
(``parse_x(encode_x(data)) == data``), ce qui est exactement ce dont un
émulateur a besoin pour valider ses handlers.
"""
from __future__ import annotations

from typing import Dict, List, Tuple

from app.network.protocol import (
    BANK_MESSAGE_PREFIX,
    CHARACTER_LIST_PREFIX,
    INVENTORY_PREFIX,
    MAP_ACTORS_PREFIX,
    MAP_DATA_PREFIX,
    MOVEMENT_HASH,
)


def encode_bank_storage(inventory: Dict[int, int], uid_start: int = 1) -> str:
    """{item_id: quantite} -> message 'EL' complet (nombres en hexa)."""
    tokens = []
    for i, (gid, qty) in enumerate(inventory.items()):
        if qty <= 0:
            continue
        tokens.append(f"O{uid_start + i:x}~{gid:x}~{qty:x}~~")
    return f"{BANK_MESSAGE_PREFIX}{';'.join(tokens)}"


def encode_map_change(map_id: int, version: str = "0", data: str = "") -> str:
    """id de map -> message 'GDM' (GDM|<mapId>|<version>|<data>)."""
    return f"{MAP_DATA_PREFIX}|{map_id}|{version}|{data}"


def _encode_group(actor: dict) -> str:
    """Groupe de monstres -> token '+cell;dir;anim;groupId;ids;flag;gfx;levels'
    (indices alignés sur parse_map_actors : [0]cell [3]id [4]ids [7]niveaux)."""
    ids = ",".join(str(m["id"]) for m in actor["monsters"])
    levels = ",".join(str(m.get("level") if m.get("level") is not None else 0)
                      for m in actor["monsters"])
    gfx = ",".join("0" for _ in actor["monsters"]) or "0"
    return f"+{actor['cell']};0;0;{actor['group_id']};{ids};0;{gfx};{levels}"


def _encode_player(actor: dict) -> str:
    """Sprite joueur -> token '+cell;dir;anim;id;nom;...' (id positif + nom)."""
    return f"+{actor['cell']};0;0;{actor['sprite_id']};{actor['name']};0;0;0"


def _encode_remove(actor: dict) -> str:
    """Retrait d'un groupe (id négatif) -> token '-<n>' (n = -group_id)."""
    return f"-{-int(actor['group_id'])}"


def encode_map_actors(actors: List[dict]) -> str:
    """Liste d'acteurs -> message 'GM' (groupes de monstres, joueurs, retraits).

    Réciproque de parse_map_actors : chaque acteur porte 'kind' ('group'|'player')
    et 'op' ('add'|'remove')."""
    tokens = []
    for a in actors:
        if a.get("op") == "remove":
            tokens.append(_encode_remove(a))
        elif a.get("kind") == "player":
            tokens.append(_encode_player(a))
        else:
            tokens.append(_encode_group(a))
    return f"{MAP_ACTORS_PREFIX}|{'|'.join(tokens)}"


def encode_character_list(characters: List[dict], subscription: str = "1") -> str:
    """Liste de persos -> message 'ALK' (écran de sélection).

    Réciproque de parse_character_list. Chaque perso : dict {character_id, name,
    level, class_id, sex, equipment:[gid,...]}. Token :
    <id>;<nom>;<niv>;<gfx=classe*10+sexe>;<c1>;<c2>;<c3>;<equip visible hexa csv>.
    """
    tokens = []
    for c in characters:
        gfx = c["class_id"] * 10 + c["sex"]
        equip = ",".join(f"{g:x}" for g in c.get("equipment", []))
        tokens.append(f"{c['character_id']};{c['name']};{c['level']};{gfx};0;0;0;{equip}")
    body = f"{subscription}|{len(characters)}|" + "|".join(tokens)
    return f"{CHARACTER_LIST_PREFIX}{body}"


def encode_character_inventory(character: dict) -> str:
    """Perso + équipement porté -> message 'ASK' (entrée en jeu).

    Réciproque de parse_character_inventory. character : dict {character_id, name,
    level, class_id, sex, equipment:[{slot, item_id, stats}]}. En-tête :
    ASK|<id>|<nom>|<niv>|<classe>|<sexe>|<gfx>|<c1>|<c2>|<c3>|<items> ; chaque item
    équipé = <uid>~<gid hexa>~<qty>~<slot hexa>~<stats>.
    """
    items = ";".join(
        f"{i + 1}~{e['item_id']:x}~1~{e['slot']:x}~{e.get('stats', '')}"
        for i, e in enumerate(character.get("equipment", []))
    )
    header = "|".join((
        INVENTORY_PREFIX, str(character["character_id"]), character["name"],
        str(character["level"]), str(character["class_id"]), str(character["sex"]),
        "0", "0", "0", "0",
    ))
    return f"{header}|{items}"


def encode_movement_path(waypoints: List[Tuple[int, int]]) -> str:
    """Liste de points d'inflexion ``(direction, cell_id)`` -> chemin GA001.

    Réciproque exacte de ``protocol.decode_movement_path`` : chaque waypoint
    devient un bloc de 3 caractères [direction, cell//64, cell%64] dans
    l'alphabet MOVEMENT_HASH — un bloc par POINT D'INFLEXION, pas par cellule
    traversée (le client officiel compresse les lignes droites ; cf. docstring
    de decode_movement_path). Fixture pure : aucun envoi réseau.
    """
    tokens = []
    for direction, cell in waypoints:
        if not (0 <= direction < 8):
            raise ValueError(f"direction hors bornes (0..7, 8 directions) : {direction}")
        if not (0 <= cell < len(MOVEMENT_HASH) ** 2):
            raise ValueError(f"cell hors bornes de l'alphabet (0..4095) : {cell}")
        c1, c2 = divmod(cell, 64)
        tokens.append(MOVEMENT_HASH[direction] + MOVEMENT_HASH[c1] + MOVEMENT_HASH[c2])
    return "".join(tokens)
