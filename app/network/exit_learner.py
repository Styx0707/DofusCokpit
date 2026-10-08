"""Apprentissage AUTO des cellules de sortie de map, en direct depuis le sniffer.

Le serveur diffuse en clair le deplacement du perso (GA0;1;id;chemin) et un
changement de map (GDM). La derniere cellule du dernier chemin GA0 juste avant
un GDM = la cellule par laquelle on a quitte la map. On l'enregistre pour
(map de depart, direction) et on garde la plus frequente.

=> la table E/O se remplit toute seule au fil des deplacements (bot OU joueur),
sans re-miner. Singleton partage avec l'API (meme processus que le watcher live).

Persistance : data/map_exits.json (memes fichier/format que tools/mine_exits.py).
Les 4 directions sont apprises (le Nord/Sud varie selon la map) ; /map/exit
retombe sur des valeurs par defaut si une sortie n'est pas encore apprise.
"""
from __future__ import annotations

import collections
import json
import os
import threading
from typing import Optional

from app.network import protocol
from app.network.protocol import decode_movement_path

_EXITS_PATH = os.getenv("MAP_EXITS_PATH", "data/map_exits.json")


def _compass(a, b) -> Optional[str]:
    dx, dy = b[0] - a[0], b[1] - a[1]
    if dx > 0:
        return "E"
    if dx < 0:
        return "O"
    if dy > 0:
        return "S"
    if dy < 0:
        return "N"
    return None


class ExitLearner:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._cur_map: dict = {}     # stream -> map_id courant
        self._last_cell: dict = {}   # stream -> derniere cellule GA0
        self._move_cells: dict = {}  # stream -> cases cliquees sur la map courante
        #                              (séquence ordonnée, pour rejouer un parcours
        #                              de salle avec obstacles/trous, pas juste la sortie)
        # map_id -> dir -> Counter(cell)
        self._exits: dict = collections.defaultdict(lambda: collections.defaultdict(collections.Counter))
        self._learned = 0
        # Transitions BRUTES (from_map, to_map) -> Counter(cell). Contrairement à
        # _exits (clé = direction cardinale, nécessite des coords monde), ceci
        # marche SANS [x,y] : indispensable pour les donjons, dont les salles ne
        # sont pas sur la grille monde. Sert à auto-remplir les cellules de sortie
        # pendant la capture d'un donjon (voir /dungeon/transitions).
        self._trans_counts: dict = collections.defaultdict(collections.Counter)
        self._transitions: collections.deque = collections.deque(maxlen=200)
        self._trans_seq = 0
        self._load()

    # --- alimentation depuis le flux ---------------------------------------
    def on_message(self, stream, msg: str) -> None:
        """Analyse un message serveur->client (appelé par le feed live/pcap)."""
        if msg.startswith("GA0;1;"):
            parts = msg.split(";")
            if len(parts) >= 4 and parts[3]:
                wp = decode_movement_path(parts[3])
                if wp:
                    dest = wp[-1][1]
                    self._last_cell[stream] = dest
                    # accumule la case cliquée : la suite des clics sur cette map
                    # = le parcours (contournement de trous/obstacles compris).
                    self._move_cells.setdefault(stream, []).append(dest)
        elif msg.startswith(protocol.MAP_DATA_PREFIX):   # GDM = changement de map
            new_map = protocol.parse_map_change(msg)
            if new_map is not None:
                self._on_map_change(stream, new_map)

    def _on_map_change(self, stream, new_map) -> None:
        old_map = self._cur_map.get(stream)
        if old_map is not None and old_map != new_map:
            oc = protocol.MAP_COORDS.get(old_map)
            nc = protocol.MAP_COORDS.get(new_map)
            cell = self._last_cell.get(stream)
            cells = list(self._move_cells.get(stream, []))
            if not cells and cell is not None:
                cells = [cell]
            if cells:
                # Transition brute (sans coords) : le PARCOURS complet par lequel
                # on a quitté old_map vers new_map (cells), la dernière case étant
                # la porte/trappe. Clé ordonnée (from, to). cells sert à rejouer
                # un parcours de salle à obstacles (« éviter les trous »).
                exit_c = cells[-1]
                with self._lock:
                    self._trans_counts[(old_map, new_map)][exit_c] += 1
                    self._transitions.append({
                        "from": old_map, "to": new_map,
                        "cell": exit_c, "cells": cells, "seq": self._trans_seq,
                    })
                    self._trans_seq += 1
            if oc and nc and cell is not None:
                d = _compass(tuple(oc), tuple(nc))
                if d:                         # apprend N/S/E/O (le Nord varie par map : 21-25)
                    with self._lock:
                        self._exits[old_map][d][cell] += 1
                        self._learned += 1
                    self._persist()
        self._cur_map[stream] = new_map
        self._last_cell.pop(stream, None)
        self._move_cells[stream] = []   # nouvelle salle = parcours vierge

    # --- lecture ------------------------------------------------------------
    def get_exit(self, map_id: int, direction: str) -> Optional[int]:
        """Cellule de sortie la plus frequente pour (map, direction), ou None."""
        c = self._exits.get(map_id, {}).get(direction.upper())
        if not c:
            return None
        return c.most_common(1)[0][0]

    def stats(self) -> dict:
        return {"maps": len(self._exits), "appris_session": self._learned}

    def recent_transitions(self, limit: int = 50) -> list:
        """Dernières transitions de map observées (plus récentes d'abord).
        Alimente la capture de donjon côté UI (auto-remplissage des sorties)."""
        with self._lock:
            items = list(self._transitions)[-limit:]
        return list(reversed(items))

    def transition_cell(self, from_map: int, to_map: int) -> Optional[int]:
        """Cellule la plus fréquente par laquelle on passe de from_map à to_map
        (ordre important : l'aller et le retour n'ont pas la même porte)."""
        with self._lock:
            c = self._trans_counts.get((from_map, to_map))
            if not c:
                return None
            return c.most_common(1)[0][0]

    # --- persistance --------------------------------------------------------
    def _load(self) -> None:
        try:
            with open(_EXITS_PATH, encoding="utf-8") as fh:
                data = json.load(fh)
            for mid, dirs in data.items():
                for d, cell in dirs.items():
                    if d in ("N", "S", "E", "O") and cell is not None:
                        self._exits[int(mid)][d][int(cell)] += 1
        except (OSError, ValueError, TypeError):
            pass

    def _persist(self) -> None:
        """Réécrit map_exits.json = {map_id: {dir: cellule majoritaire}} (E/O)."""
        try:
            out: dict = {}
            with self._lock:
                for mid, dirs in self._exits.items():
                    out[str(mid)] = {d: c.most_common(1)[0][0]
                                     for d, c in dirs.items() if c}
            tmp = _EXITS_PATH + ".tmp"
            os.makedirs(os.path.dirname(_EXITS_PATH) or ".", exist_ok=True)
            with open(tmp, "w", encoding="utf-8") as fh:
                json.dump(out, fh, ensure_ascii=False)
            os.replace(tmp, _EXITS_PATH)
        except OSError:
            pass


_learner: Optional[ExitLearner] = None


def get_learner() -> ExitLearner:
    global _learner
    if _learner is None:
        _learner = ExitLearner()
    return _learner
