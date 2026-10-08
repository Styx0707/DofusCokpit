"""Persistance de l'historique des apparitions (cible / archimonstre) par map.

Table map_appearances : permet de recharger la heatmap et le Top maps après un
redémarrage de l'API. On n'écrit QUE les apparitions cible/archi (éparses).
"""
from __future__ import annotations

from typing import List, Optional, Sequence


def record_appearance(
        cur,
        map_id: int,
        ts_epoch: float,
        is_target: bool,
        is_archi: bool,
        monster_ids: Optional[Sequence[int]] = None,
        coord: Optional[Sequence[int]] = None,
        zone: Optional[str] = None,
) -> None:
    """Insère une apparition (une ligne)."""
    x, y = (coord[0], coord[1]) if coord else (None, None)
    cur.execute(
        """
        INSERT INTO map_appearances
            (ts_epoch, map_id, coord_x, coord_y, zone, is_target, is_archi, monster_ids)
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (float(ts_epoch), int(map_id), x, y, zone,
         bool(is_target), bool(is_archi), [int(m) for m in (monster_ids or [])]),
    )


def get_map_history(cur) -> List[dict]:
    """Agrégat par map : compteurs cible/archi + dernier horodatage (epoch).

    Utilisé au démarrage pour ré-amorcer le moniteur (heatmap / Top maps)."""
    cur.execute(
        """
        SELECT map_id,
               COUNT(*) FILTER (WHERE is_target)       AS target_hits,
               COUNT(*) FILTER (WHERE is_archi)        AS archi_hits,
               MAX(ts_epoch) FILTER (WHERE is_target)  AS last_target_ts,
               MAX(ts_epoch) FILTER (WHERE is_archi)   AS last_archi_ts
        FROM map_appearances
        GROUP BY map_id
        """
    )
    return [dict(r) for r in cur.fetchall()]


def get_recent_appearances(cur, limit: int = 100) -> List[dict]:
    """Dernières apparitions (pour une vue historique éventuelle)."""
    cur.execute(
        """
        SELECT recorded_at, ts_epoch, map_id, coord_x, coord_y, zone,
               is_target, is_archi, monster_ids
        FROM map_appearances
        ORDER BY id DESC
        LIMIT %s
        """,
        (int(limit),),
    )
    return [dict(r) for r in cur.fetchall()]
