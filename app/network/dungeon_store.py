"""Stockage des définitions de donjon dans data/dungeons.json.

Un donjon n'est PAS sur la grille monde [x,y] : c'est une suite ORDONNÉE de
salles (map_ids vus dans GDM), reliées par une cellule de transition — la
porte / trappe qu'on clique pour passer à la salle suivante. On stocke donc,
par salle :
  - map_id    : id interne de la salle ;
  - label     : nom lisible (« Salle bleue », « Boss »…) ;
  - exit_cell : cellule 0-559 à cliquer pour aller à la salle SUIVANTE
                (None pour la dernière = salle du boss).

Format fichier : { "<id>": {"id", "name", "rooms": [...], "updated"} }.
Écriture atomique (tmp + replace). État pur fichier, pas de DB — même esprit
que data/archi_ids.json, data/map_exits.json, etc.
"""
from __future__ import annotations

import json
import os
import threading
import time
from typing import Dict, List, Optional

_PATH = os.getenv("DUNGEONS_PATH", "data/dungeons.json")
_lock = threading.Lock()


def _load() -> Dict[str, dict]:
    try:
        with open(_PATH, encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def _save(data: Dict[str, dict]) -> None:
    tmp = _PATH + ".tmp"
    os.makedirs(os.path.dirname(_PATH) or ".", exist_ok=True)
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)
    os.replace(tmp, _PATH)


def _norm_rooms(rooms) -> List[dict]:
    """Valide/normalise les salles : map_id entier obligatoire, `path_cells` =
    liste ordonnée de cases à cliquer (le parcours de la salle, pour contourner
    trous/obstacles), `exit_cell` = dernière case (dérivée), label texte. Les
    entrées sans map_id valide sont ignorées."""
    out: List[dict] = []
    for r in rooms or []:
        try:
            mid = int(r["map_id"])
        except (KeyError, TypeError, ValueError):
            continue
        cells: List[int] = []
        for c in (r.get("path_cells") or []):
            try:
                cells.append(int(c))
            except (TypeError, ValueError):
                pass
        cell = r.get("exit_cell")
        try:
            cell = int(cell) if cell not in (None, "") else None
        except (TypeError, ValueError):
            cell = None
        # path_cells fait foi ; sinon on retombe sur exit_cell seul.
        if cells:
            cell = cells[-1]
        elif cell is not None:
            cells = [cell]
        out.append({"map_id": mid, "label": str(r.get("label") or ""),
                    "path_cells": cells, "exit_cell": cell})
    return out


def list_dungeons() -> List[dict]:
    """Résumés (sans le détail des salles) pour le sélecteur de l'UI."""
    out = [{"id": d.get("id"), "name": d.get("name"),
            "rooms": len(d.get("rooms") or []), "updated": d.get("updated")}
           for d in _load().values()]
    return sorted(out, key=lambda x: (x.get("name") or "").lower())


def get_dungeon(dungeon_id: str) -> Optional[dict]:
    return _load().get(dungeon_id)


def save_dungeon(dungeon_id: str, name: str, rooms) -> dict:
    with _lock:
        data = _load()
        rec = {"id": dungeon_id, "name": name or dungeon_id,
               "rooms": _norm_rooms(rooms), "updated": time.time()}
        data[dungeon_id] = rec
        _save(data)
        return rec


def delete_dungeon(dungeon_id: str) -> bool:
    with _lock:
        data = _load()
        if dungeon_id in data:
            del data[dungeon_id]
            _save(data)
            return True
        return False
