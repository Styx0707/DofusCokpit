"""Décodage du protocole Dofus Retro (texte, en clair) — SANS dépendance réseau.

Messages décodés (formats identifiés par capture réelle) :
1) Banque `EL`            : O<uid>~<gid>~<qty>~<pos>~<stats> ; ...            (hexa)
2) Liste persos `ALK`     : ALK<abo>|<nb>|<id>;<nom>;<niv>;<classe*10+sexe>;...;<equip visible>;...
3) Inventaire complet `ASK`: ASK|<id>|<nom>|<niv>|<classe>|<sexe>|...|<items>
   items = <uid>~<gid>~<qty>~<position>~<stats>. position 0-15 = slot équipé.
   <stats> = effets séparés par ',' : <effectId>#<min>#<max>#<dé> (tout en hexa).
4) Changement de map `GDM`: GDM|<mapId>|<version>|<data chiffrée>            (mapId décimal)
5) Acteurs de map `GM`    : GM|+<cell>;<dir>;<?>;<id>;<...> [|+... |-...]
   id NÉGATIF => groupe de monstres ; champ suivant = IDs monstres CSV, +3 = niveaux CSV.
"""
from __future__ import annotations

import json
import os
from typing import Dict, List, Optional, Tuple

BANK_MESSAGE_PREFIX = "EL"
CHARACTER_LIST_PREFIX = "ALK"
INVENTORY_PREFIX = "ASK"
MAP_DATA_PREFIX = "GDM"
MAP_ACTORS_PREFIX = "GM"
# Combat (en clair serveur->client) :
#  - GTS<id>|<tempsMs>|<?>  : début de tour du combattant <id> (« qui joue »)
#  - PM~<id>;<nom>;<niv>;…  : mapping id de combattant -> perso (joueurs du combat)
TURN_START_PREFIX = "GTS"
FIGHTER_PM_PREFIX = "PM~"
# Hôtel de vente (HDV) — serveur->client (format identifié par capture réelle,
# data/hdv.pcapng, 2026-10-08) :
#  - EHP<gid>|<prixMoyen>                         : prix MOYEN unitaire (kamas)
#  - EHl<gid>|<?>;;<lot1>;<lot10>;<lot100>;<gid>  : prix TOTAL des lots 1/10/100 en vente
#    (virgule = séparateur décimal du client ; lot de 1 = prix unitaire courant)
#  - EHL<cat>|<gid>;<gid>;…                       : liste des gids d'une catégorie
HDV_AVG_PRICE_PREFIX = "EHP"
HDV_ITEM_PRICE_PREFIX = "EHl"

# Noms de monstres (id template client 1.29 = ids solomonk.fr / dofusdb.fr).
# Base = 546 confirmé (Bambouto Sacré, « le Divin », niv ~77, vu niv 87 map 8157) ;
# le reste est chargé depuis data/monster_names.json, produit par
# scripts.fetch_monster_names (scrape solomonk.fr). Fichier absent -> juste la base.
def _load_monster_names() -> Dict[int, str]:
    names: Dict[int, str] = {546: "Bambouto Sacré"}
    path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "monster_names.json")
    try:
        with open(path, encoding="utf-8") as fh:
            names.update({int(k): v for k, v in json.load(fh).items()})
    except (OSError, ValueError):
        pass
    return names


MONSTER_NAMES = _load_monster_names()


def reload_monster_names() -> int:
    """Recharge MONSTER_NAMES depuis le JSON (après un scripts.fetch_monster_names,
    sans redémarrer l'API). Retourne le nombre de noms connus."""
    global MONSTER_NAMES
    MONSTER_NAMES = _load_monster_names()
    return len(MONSTER_NAMES)


# Coordonnées [x, y] par id de map. Le protocole ne transmet QUE l'id interne
# (GDM) ; les [x,y] affichés en jeu viennent d'une table côté client. On la tient
# nous-mêmes dans data/map_coords.json {"<mapId>": [x, y]} (saisie via l'UI).
def _load_map_coords() -> Dict[int, list]:
    coords: Dict[int, list] = {}
    path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "map_coords.json")
    try:
        with open(path, encoding="utf-8") as fh:
            coords = {int(k): v for k, v in json.load(fh).items()}
    except (OSError, ValueError):
        pass
    return coords


MAP_COORDS = _load_map_coords()


def reload_map_coords() -> int:
    global MAP_COORDS
    MAP_COORDS = _load_map_coords()
    return len(MAP_COORDS)


# Sous-zone (nom) par id de map : data/map_zones.json {"<mapId>": "Bordure d'Aerdala"}
# (produit par scripts.import_map_coords depuis subarea_data.sql).
def _load_map_zones() -> Dict[int, str]:
    zones: Dict[int, str] = {}
    path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "map_zones.json")
    try:
        with open(path, encoding="utf-8") as fh:
            zones = {int(k): v for k, v in json.load(fh).items()}
    except (OSError, ValueError):
        pass
    return zones


MAP_ZONES = _load_map_zones()


def reload_map_zones() -> int:
    global MAP_ZONES
    MAP_ZONES = _load_map_zones()
    return len(MAP_ZONES)


# Cellule de "sortie" de map par direction cardinale (N/S/E/O) : la grille de
# cellules (0..559) a la même forme sur toutes les maps Dofus Retro, donc la
# cellule qui déclenche un changement de map dans une direction donnée est en
# principe la même partout. Aucune valeur par défaut (pas de source fiable ici) ;
# saisie manuelle (observée en jeu) via l'UI / POST /live/exitcell, persistée
# dans data/map_exit_cells.json {"N": cellId, "S": ..., "E": ..., "O": ...}.
def _load_exit_cells() -> Dict[str, int]:
    path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "map_exit_cells.json")
    try:
        with open(path, encoding="utf-8") as fh:
            return {k: int(v) for k, v in json.load(fh).items() if v is not None}
    except (OSError, ValueError):
        return {}


EXIT_CELLS = _load_exit_cells()


def reload_exit_cells() -> int:
    global EXIT_CELLS
    EXIT_CELLS = _load_exit_cells()
    return len(EXIT_CELLS)


# Ids des ARCHIMONSTRES (data/archi_ids.json = liste d'ids). En Retro, un archi
# a un id de monstre DISTINCT (même sprite, nom spécial) : il apparaît donc dans
# un groupe avec son propre id -> détectable dans GM. La liste se remplit au fil
# des rencontres (l'id surgit sur la carte) ; éditable via l'UI / POST /live/archi.
def _load_archi_ids() -> set:
    path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "archi_ids.json")
    try:
        with open(path, encoding="utf-8") as fh:
            return {int(x) for x in json.load(fh)}
    except (OSError, ValueError, TypeError):
        return set()


ARCHI_IDS = _load_archi_ids()


def reload_archi_ids() -> int:
    global ARCHI_IDS
    ARCHI_IDS = _load_archi_ids()
    return len(ARCHI_IDS)


# Cible de farm par défaut du moniteur de repop.
BAMBOUTO_SACRE_ID = 546

CLASSES = {
    1: "Feca", 2: "Osamodas", 3: "Enutrof", 4: "Sram", 5: "Xelor", 6: "Ecaflip",
    7: "Eniripsa", 8: "Iop", 9: "Cra", 10: "Sadida", 11: "Sacrieur", 12: "Pandawa",
}

EQUIP_SLOTS = {
    0: "Amulette", 1: "Arme", 2: "Anneau", 3: "Ceinture", 4: "Anneau",
    5: "Bottes", 6: "Coiffe", 7: "Cape", 8: "Familier",
    9: "Dofus", 10: "Dofus", 11: "Dofus", 12: "Dofus", 13: "Dofus", 14: "Dofus",
    15: "Bouclier",
}

# effectId (décimal) -> libellé. Vérifiés (valeur cohérente avec la fiche wiki)
# + PA/PM confirmés utilisateur (Retro : pas de cap à 12, les +PA se cumulent).
# Résistances : élément vérifié sur Styxh (neutre/terre/eau) ; fixe/% inféré ;
# feu/air à confirmer quand un perso en portera. Reste non listé -> brut (#id).
EFFECT_NAMES = {
    125: "Vitalité", 124: "Sagesse", 119: "Agilité", 123: "Chance", 126: "Intelligence",
    112: "Dommages", 138: "% Dommages", 115: "Coups Critiques", 117: "Portée",
    176: "Prospection", 174: "Initiative", 182: "Invocations",
    111: "PA", 128: "PM",
    108: "PDV rendus", 91: "Vol de vie", 94: "Vol de vie",
    # Résistances (fixe + %)
    240: "Rés Terre", 241: "Rés Eau", 244: "Rés Neutre",
    118: "Rés Terre %", 214: "Rés Neutre %",
}

# effectId -> élément (pour la pastille de couleur côté UI).
ELEMENT_OF = {
    91: "eau", 94: "feu",
    240: "terre", 241: "eau", 244: "neutre",
    118: "terre", 214: "neutre",
}


def decode_effects(stats: str) -> List[dict]:
    """Décode la chaîne d'effets d'un item -> [{id, label, value, element, known}].

    Ne garde que les effets d'équipement (id <= 300) pour écarter le bruit
    (jauges de familier, signature, conditions…).
    """
    out: List[dict] = []
    if not stats:
        return out
    for eff in stats.split(","):
        eff = eff.strip()
        if not eff:
            continue
        parts = eff.split("#")
        try:
            eid = int(parts[0], 16)
        except (ValueError, IndexError):
            continue
        if eid > 300:
            continue
        mn = int(parts[1], 16) if len(parts) > 1 and parts[1] else 0
        mx = int(parts[2], 16) if len(parts) > 2 and parts[2] else 0
        label = EFFECT_NAMES.get(eid)
        value = f"{mn}-{mx}" if mx and mx != mn else str(mn)
        out.append({
            "id": eid, "label": label or f"#{eid}", "value": value,
            "element": ELEMENT_OF.get(eid), "known": label is not None,
        })
    return out


def parse_bank_storage(payload: str) -> Dict[int, int]:
    """Corps d'un message 'EL' (préfixe déjà retiré) -> {item_id: quantite}."""
    inventory: Dict[int, int] = {}
    for token in payload.split(";"):
        token = token.strip()
        if not token:
            continue
        if token.startswith("O"):
            token = token[1:]
        parts = token.split("~")
        if len(parts) < 3:
            continue
        try:
            gid = int(parts[1], 16)
            quantity = int(parts[2], 16)
        except ValueError:
            continue
        if quantity > 0:
            inventory[gid] = inventory.get(gid, 0) + quantity
    return inventory


def parse_hdv_avg_price(payload: str) -> Optional[Tuple[int, int]]:
    """Corps d'un message 'EHP' (préfixe retiré) : ``<gid>|<prixMoyen>``. Le prix
    moyen est UNITAIRE, en kamas. -> (item_id, prix) ou None."""
    gid, sep, rest = payload.partition("|")
    if not sep or not gid.strip().isdigit():
        return None
    tok = rest.split(";")[0].split(",")[0].strip()
    try:
        return int(gid), int(tok)
    except ValueError:
        return None


def parse_hdv_item_prices(payload: str) -> Optional[Dict[str, Optional[int]]]:
    """Corps d'un message 'EHl' (préfixe retiré) :
    ``<gid>|<?>;;<lot1>;<lot10>;<lot100>;<gid>``. Les prix sont les TOTAUX des lots
    actuellement en vente (lot de 1 = prix unitaire le plus bas). La virgule est le
    séparateur décimal du client -> on garde la partie entière.
    -> {item_id, x1, x10, x100} (valeur absente = None)."""
    gid, sep, rest = payload.partition("|")
    if not sep or not gid.strip().isdigit():
        return None
    fields = rest.split(";")

    def num(i: int) -> Optional[int]:
        if i < len(fields):
            tok = fields[i].split(",")[0].strip()
            if tok.isdigit():
                return int(tok)
        return None

    return {"item_id": int(gid), "x1": num(2), "x10": num(3), "x100": num(4)}


def parse_character_list(payload: str) -> List[dict]:
    """Corps d'un message 'ALK' (préfixe retiré) -> liste de persos (équip visible)."""
    characters: List[dict] = []
    for token in payload.split("|"):
        fields = token.split(";")
        if len(fields) < 8 or not fields[0].isdigit():
            continue
        try:
            character_id = int(fields[0])
            level = int(fields[2])
            gfx = int(fields[3])
        except ValueError:
            continue
        class_id, sex = gfx // 10, gfx % 10
        equipment = [int(g, 16) for g in fields[7].split(",") if g.strip()]
        characters.append({
            "character_id": character_id, "name": fields[1], "level": level,
            "class_id": class_id, "class_name": CLASSES.get(class_id, "?"),
            "sex": sex, "equipment": equipment,
        })
    return characters


def parse_character_inventory(message: str) -> Optional[dict]:
    """Message 'ASK' complet -> perso + équipement porté (slots + jets)."""
    if not message.startswith(INVENTORY_PREFIX):
        return None
    parts = message.split("|")
    if len(parts) < 11 or not parts[1].isdigit():
        return None
    try:
        character_id = int(parts[1])
        level = int(parts[3])
        class_id = int(parts[4])
        sex = int(parts[5])
    except ValueError:
        return None

    equipment = []
    body = "|".join(parts[10:])
    for token in body.split(";"):
        fields = token.split("~")
        if len(fields) < 4 or not fields[3].strip():
            continue
        try:
            slot = int(fields[3], 16)
            gid = int(fields[1], 16)
        except ValueError:
            continue
        if slot in EQUIP_SLOTS:
            equipment.append({
                "slot": slot, "slot_name": EQUIP_SLOTS[slot], "item_id": gid,
                "stats": fields[4] if len(fields) > 4 else "",
            })

    equipment.sort(key=lambda e: e["slot"])
    return {
        "character_id": character_id, "name": parts[2], "level": level,
        "class_id": class_id, "class_name": CLASSES.get(class_id, "?"),
        "sex": sex, "equipment": equipment,
    }


# --- Suivi des maps / groupes de monstres (repop) ---------------------------
# Formats identifiés par capture réelle (data/pandala.pcapng, île de Pandala) :
#   GDM|8158|0907151356|<data>            -> le client charge la map 8158
#   GM|+370;5;21;-1;566;-3;1260^110;52;…  -> groupe (id -1) : monstre 566 niv 52
#   GM|+346;5;10;-3;517,566,549;-3;…;45,40,70;…  -> groupe (id -3) : 3 monstres
# Un sprite dont le champ [3] est NÉGATIF est un groupe de monstres (le joueur a
# un id positif + un champ nom). Champ [4] = IDs de monstres (CSV), [7] = niveaux.

def parse_map_change(message: str) -> Optional[int]:
    """Message 'GDM' -> id (décimal) de la map que le client vient de charger."""
    if not message.startswith(MAP_DATA_PREFIX):
        return None
    parts = message.split("|")
    if len(parts) < 2:
        return None
    try:
        return int(parts[1])
    except ValueError:
        return None


def parse_turn_start(message: str) -> Optional[int]:
    """'GTS<id>|<tempsMs>|<?>' -> id du combattant dont c'est le tour, ou None."""
    if not message.startswith(TURN_START_PREFIX):
        return None
    body = message[len(TURN_START_PREFIX):].split("|", 1)[0].strip()
    try:
        return int(body)
    except ValueError:
        return None


def parse_fighter_name(message: str) -> Optional[Tuple[int, str]]:
    """'PM~<id>;<nom>;<niv>;…' -> (id, nom) : mapping combattant -> perso, ou None."""
    if not message.startswith(FIGHTER_PM_PREFIX):
        return None
    parts = message[len(FIGHTER_PM_PREFIX):].split(";")
    if len(parts) < 2:
        return None
    try:
        fid = int(parts[0])
    except ValueError:
        return None
    name = parts[1].strip()
    return (fid, name) if name else None


def _parse_int_csv(field: str) -> List[int]:
    """CSV d'entiers tolérant : ignore les jetons non numériques (ex. '1260^110')."""
    out: List[int] = []
    for tok in field.split(","):
        tok = tok.strip()
        head = tok.split("^", 1)[0]  # '1260^110' -> '1260'
        if head.lstrip("-").isdigit():
            out.append(int(head))
    return out


def parse_map_actors(message: str) -> List[dict]:
    """Message 'GM' -> sprites ajoutés/retirés. Ne retient que les GROUPES DE
    MONSTRES (id de sprite négatif).

    Retour : liste de dicts
      {op: 'add'|'remove', cell, group_id, monsters: [{id, level}]}.
    Le retrait 'GM|-<id>' (groupe tué / quitté) est renvoyé sans compo (à
    confirmer sur une capture de combat) ; l'ajout est validé sur capture réelle.
    """
    if not message.startswith(MAP_ACTORS_PREFIX):
        return []
    body = message[len(MAP_ACTORS_PREFIX):].lstrip("|")
    out: List[dict] = []
    for chunk in body.split("|"):
        chunk = chunk.strip()
        if not chunk or chunk[0] not in "+-":
            continue
        op = "add" if chunk[0] == "+" else "remove"
        fields = chunk[1:].split(";")

        if op == "remove":
            # Retrait 'GM|-<n>' : format SUPPOSÉ (pas encore de capture de kill).
            # Les ajouts de groupes utilisent un id négatif (-1,-2,-3…) ; on
            # reconstruit donc -n pour relier le retrait au groupe suivi. Un
            # retrait de joueur (id positif) ne matchera aucun groupe -> ignoré
            # côté moniteur. À revalider dès qu'on capture un combat.
            head = fields[0].strip()
            if head.isdigit():
                out.append({"op": "remove", "kind": "group", "cell": None,
                            "group_id": -int(head), "monsters": []})
            continue

        if len(fields) < 5 or not fields[0].strip().isdigit():
            continue
        try:
            cell = int(fields[0])
            sprite_id = int(fields[3])
        except (ValueError, IndexError):
            continue
        if sprite_id >= 0:
            # Joueur / PNJ : champ [4] = nom. On l'émet pour identifier le perso
            # du compte (celui présent sur TOUTES les maps d'un même flux).
            name = fields[4].strip() if len(fields) > 4 else ""
            if name and not name.lstrip("-").isdigit():
                out.append({"op": "add", "kind": "player", "cell": cell,
                            "sprite_id": sprite_id, "name": name})
            continue

        monster_ids = _parse_int_csv(fields[4])
        levels = _parse_int_csv(fields[7]) if len(fields) > 7 else []
        monsters = [
            {"id": mid, "level": levels[i] if i < len(levels) else None}
            for i, mid in enumerate(monster_ids)
        ]
        out.append({"op": "add", "kind": "group", "cell": cell,
                    "group_id": sprite_id, "monsters": monsters})
    return out


# Alphabet base-64 Dofus : cellules et directions d'un chemin de déplacement y
# sont encodées (une cellule 0..559 tient sur 2 caractères, 64*64 = 4096 > 560).
MOVEMENT_HASH = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"


def decode_movement_path(raw_path: str) -> List[Tuple[int, int]]:
    """Décode le chemin d'une action de déplacement (GA001, client->serveur).

    Le client officiel COMPRESSE le trajet : chaque bloc de 3 caractères encode
    un POINT D'INFLEXION (pas une cellule adjacente) — confirmé sur trame réelle
    (un déplacement en ligne droite tient sur un seul bloc ; un trajet avec
    changements d'angle n'émet qu'un bloc par segment). Bloc :
      - [0] direction (0..7 = index dans MOVEMENT_HASH) du segment qui MÈNE à ce
        point (départ du segment = point d'inflexion précédent, ou la cellule
        courante du joueur pour le 1er bloc) ;
      - [1:3] cellule d'arrivée du segment : cell_id = index(c1) * 64 + index(c2).
    Retourne la liste ordonnée des points d'inflexion ``(direction, cell_id)``.
    Ne retourne PAS les cellules intermédiaires du segment : les interpoler
    demande la géométrie réelle de la grille de cellules, qu'on n'a pas de
    source fiable pour confirmer ici (cf. limitation documentée dans
    GameActionHandler — Map_Data est chiffré). Parsing PUR (lecture) : ne
    déplace rien. Les blocs incomplets ou hors alphabet sont ignorés
    silencieusement.
    """
    waypoints: List[Tuple[int, int]] = []
    for i in range(0, len(raw_path) - 2, 3):
        d = MOVEMENT_HASH.find(raw_path[i])
        c1 = MOVEMENT_HASH.find(raw_path[i + 1])
        c2 = MOVEMENT_HASH.find(raw_path[i + 2])
        if d < 0 or c1 < 0 or c2 < 0:
            continue
        waypoints.append((d, c1 * 64 + c2))
    return waypoints
