"""Handler serveur d'actions de jeu (émulateur) — RÉCEPTION d'un déplacement.

``handle_movement`` reçoit l'action GA001 d'un client (chemin encodé), la DÉCODE
(lecture, cf. protocol.decode_movement_path), valide la trajectoire, met à jour
la cellule du joueur côté SERVEUR et renvoie le paquet à diffuser aux clients
présents sur la map (``GA;1;<player_id>;<path>``).

Logique purement serveur, en mémoire : aucune connexion réseau, aucune émission
d'ordre de déplacement — c'est le traitement d'un ordre DÉJÀ ÉMIS par un client.
"""
from __future__ import annotations

from typing import Dict

from app.network.protocol import decode_movement_path

MAX_CELL = 559  # cellule maximale d'une map Dofus 1.29 (0..559)


class GameActionHandler:
    def __init__(self) -> None:
        # État serveur minimal : cellule courante par joueur.
        self.players: Dict[int, Dict[str, int]] = {}

    def handle_movement(self, player_id: int, current_cell: int, raw_path: str) -> dict:
        """Traite un déplacement GA001.

        - Décode le chemin en points d'inflexion (direction, cell_id) puis n'en
          garde que les cellules — cf. protocol.decode_movement_path : le chemin
          est compressé (un bloc par segment en ligne droite), pas une cellule
          par pas ; on ne reconstitue pas les cellules intermédiaires.
        - Valide : chemin non vide, cellules (départ incluse) dans les bornes map.
        - Met à jour la cellule du joueur = cellule d'ARRIVÉE (dernière du chemin).
        - Retourne {ok, player_id, from, to, path, broadcast}. En cas de refus,
          l'état n'est PAS modifié et broadcast=None.

        NB : la validation de MARCHABILITÉ complète (murs/obstacles, continuité du
        chemin) nécessite les cellules de la map (décodage de Map_Data) — hors
        périmètre ici ; on valide les bornes.
        """
        cells = [cell for _, cell in decode_movement_path(raw_path)]
        if not cells:
            return {"ok": False, "reason": "chemin vide", "broadcast": None}
        if not (0 <= current_cell <= MAX_CELL) or any(not (0 <= c <= MAX_CELL) for c in cells):
            return {"ok": False, "reason": "cellule hors map", "broadcast": None}

        destination = cells[-1]
        self.players.setdefault(player_id, {})["cell_id"] = destination
        return {
            "ok": True,
            "player_id": player_id,
            "from": current_cell,
            "to": destination,
            "path": cells,
            "broadcast": f"GA;1;{player_id};{raw_path}",
        }
