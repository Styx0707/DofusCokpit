"""File d'attente de deplacements pour le walker AutoIt (auto-clic).

live.html poste un job (compte + destination [x,y]) ; le walker le recupere,
marche jusqu'a destination via l'auto-clic, et rapporte son avancement. Aucun
paquet reseau : le vrai client joue.

Un seul job actif a la fois (un client pilote a la fois) — suffisant et simple.
Un nouveau job remplace le precedent (le walker detecte le changement d'id).

Cible par POSITION de depart (start), pas par label : robuste aux labels
instables (plusieurs persos homonymes). Le label n'est que cosmetique.
"""
from __future__ import annotations

import threading
import time
from typing import Optional

# etats : pending -> running -> done | failed | canceled
_ACTIVE = ("pending", "running")


class WalkJobStore:
    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._job: Optional[dict] = None
        self._seq = 0
        self._last_poll = 0.0   # dernier GET /walk/job = battement de coeur du walker
        self._focus = None      # demande de mise au 1er plan {name, id}
        self._focus_seq = 0
        self._windows: list = []    # noms de fenetres Dofus rapportes par le walker
        self._windows_ts = 0.0      # (ground truth des clients ouverts, pour board.html)
        self._sweep = None          # balayage demande : {id, names:[...]}
        self._sweep_seq = 0

    def set_sweep(self, names: list) -> dict:
        """Demande au walker d'activer CHAQUE fenetre de `names`, une par une
        (le pop-up envoie l'ordre voulu, ex. inverse de la barre des taches)."""
        with self._lock:
            self._sweep_seq += 1
            self._sweep = {"id": self._sweep_seq,
                           "names": [str(n) for n in (names or []) if str(n).strip()]}
            return dict(self._sweep)

    def sweep(self) -> Optional[dict]:
        with self._lock:
            return dict(self._sweep) if self._sweep else None

    def report_windows(self, names: list, now: float) -> int:
        """Le walker énumère les fenêtres Dofus ouvertes (WinList) et les rapporte :
        c'est la liste RÉELLE des clients, indépendante du sniffer (qui ne voit un
        compte que s'il bouge). Sert au tableau de bord à afficher les 15 comptes."""
        with self._lock:
            clean = []
            for n in (names or []):
                n = str(n).strip()
                # un nom de perso n'a pas d'espace ; écarte un éventuel titre parasite
                # (onglet navigateur « Dofus Retro — Comptes », launcher…).
                if n and " " not in n and "Dofus" not in n:
                    clean.append(n)
            self._windows = clean
            self._windows_ts = now
            return len(self._windows)

    def windows(self, now: float, window: float = 15.0) -> dict:
        """Fenêtres rapportées récemment (vides si le walker n'a rien posté < window s)."""
        with self._lock:
            fresh = self._windows_ts > 0 and (now - self._windows_ts) <= window
            return {
                "windows": list(self._windows) if fresh else [],
                "reported_ago_s": round(now - self._windows_ts, 1) if self._windows_ts else None,
            }

    def set_focus(self, name: str) -> dict:
        """live.html demande d'activer la fenetre d'un perso (clic sur la carte)."""
        with self._lock:
            self._focus_seq += 1
            self._focus = {"name": name, "id": self._focus_seq}
            return dict(self._focus)

    def focus(self) -> Optional[dict]:
        with self._lock:
            return dict(self._focus) if self._focus else None

    def mark_poll(self, now: float) -> None:
        """Appelé à chaque interrogation du walker (sert de heartbeat)."""
        with self._lock:
            self._last_poll = now

    def walker_online(self, now: float, window: float = 6.0) -> bool:
        """True si le walker a interrogé l'API récemment (< window secondes)."""
        with self._lock:
            return self._last_poll > 0 and (now - self._last_poll) <= window

    def submit(self, label: str, start: list, dest: list) -> dict:
        with self._lock:
            self._seq += 1
            self._job = {
                "id": self._seq,
                "kind": "walk",          # déplacement A->B sur la grille monde
                "label": label,
                "start": [int(start[0]), int(start[1])],
                "dest": [int(dest[0]), int(dest[1])],
                "state": "pending",
                "message": "en attente du walker…",
                "pos": None,
                "map_id": None,
                "created": time.time(),
                "updated": time.time(),
            }
            return dict(self._job)

    def submit_dungeon_step(self, team: list, map_id: int, cells: list,
                            label: str = "") -> dict:
        """Un « pas de donjon » : rejouer le PARCOURS `cells` (cases à cliquer
        dans l'ordre, pour contourner trous/obstacles ; la dernière = porte) de
        la salle `map_id` pour CHAQUE fenêtre de `team` (noms de perso =
        sous-chaînes de titre). Fait sortir toute l'équipe d'une salle vaincue
        vers la suivante. Le combat reste manuel — à enfiler une fois la salle
        gagnée. `target_map` évite de toucher à `map_id` (réservé au report de la
        map courante par le walker). `cell` (dernière case) gardé pour compat."""
        with self._lock:
            self._seq += 1
            team = [str(t) for t in team if str(t).strip()]
            cells = [int(c) for c in (cells or [])]
            self._job = {
                "id": self._seq,
                "kind": "dungeon_step",
                "label": label or (team[0] if team else ""),
                "team": team,
                "target_map": int(map_id),
                "cells": cells,
                "cell": cells[-1] if cells else None,
                "start": None,
                "dest": None,
                "state": "pending",
                "message": "en attente du walker…",
                "pos": None,
                "map_id": None,
                "created": time.time(),
                "updated": time.time(),
            }
            return dict(self._job)

    def current(self) -> Optional[dict]:
        with self._lock:
            return dict(self._job) if self._job else None

    def update(self, job_id: int, state: Optional[str] = None,
               message: Optional[str] = None, pos: Optional[list] = None,
               map_id: Optional[int] = None) -> Optional[dict]:
        with self._lock:
            if not self._job or self._job["id"] != job_id:
                return None
            if state:
                self._job["state"] = state
            if message is not None:
                self._job["message"] = message
            if pos is not None:
                self._job["pos"] = pos
            if map_id is not None:
                self._job["map_id"] = map_id
            self._job["updated"] = time.time()
            return dict(self._job)

    def cancel(self) -> Optional[dict]:
        with self._lock:
            if self._job and self._job["state"] in _ACTIVE:
                self._job["state"] = "canceled"
                self._job["message"] = "annule par l'utilisateur"
                self._job["updated"] = time.time()
            return dict(self._job) if self._job else None

    def clear(self) -> None:
        with self._lock:
            self._job = None


_store: Optional[WalkJobStore] = None


def get_store() -> WalkJobStore:
    global _store
    if _store is None:
        _store = WalkJobStore()
    return _store
