"""Optimiseur de tournée (rotation) entre maps pour le farm / archi-hunt.

Pur (aucune IO). À partir des coordonnées [x, y] des maps sélectionnées, bâtit
un parcours en SERPENTIN (boustrophédon) : on balaie ligne par ligne (Y, nord
-> sud), en alternant le sens en X à chaque ligne — le trajet qu'un joueur suit
naturellement pour couvrir une zone. Deux maps distantes de 1 en Manhattan sont
adjacentes (un changement de map).

Contient aussi un pathfinding POINT À POINT (``find_path`` / ``next_direction``)
utilisé pour piloter un déplacement A -> B (auto-clic) : BFS sur la même grille
d'adjacence, qui rend la liste des directions cardinales à suivre.
"""
from __future__ import annotations

from collections import deque
from typing import Dict, List, Optional, Tuple

Coord = Tuple[int, int]


def _manhattan(a: Coord, b: Coord) -> int:
    return abs(a[0] - b[0]) + abs(a[1] - b[1])


def snake_order(coords: Dict[int, Coord]) -> List[int]:
    """Ordre serpentin : par Y croissant, X alterné une ligne sur deux."""
    by_row: Dict[int, List[int]] = {}
    for mid, (x, y) in coords.items():
        by_row.setdefault(y, []).append(mid)
    order: List[int] = []
    for i, y in enumerate(sorted(by_row)):
        row = sorted(by_row[y], key=lambda m: coords[m][0])
        if i % 2:                     # une ligne sur deux à l'envers -> serpentin
            row.reverse()
        order.extend(row)
    return order


def connected_components(coords: Dict[int, Coord]) -> List[List[int]]:
    """Composantes reliées par adjacence de grille (Manhattan == 1)."""
    by_pos = {xy: mid for mid, xy in coords.items()}
    seen: set = set()
    comps: List[List[int]] = []
    for start in coords:
        if start in seen:
            continue
        stack, comp = [start], []
        seen.add(start)
        while stack:
            m = stack.pop()
            comp.append(m)
            x, y = coords[m]
            for nb_xy in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
                nb = by_pos.get(nb_xy)
                if nb is not None and nb not in seen:
                    seen.add(nb)
                    stack.append(nb)
        comps.append(comp)
    return comps


def plan_route(coords: Dict[int, Coord]) -> dict:
    """Parcours serpentin + métriques (pas entre stops, total, bouclage)."""
    order = snake_order(coords)
    steps = [_manhattan(coords[order[i - 1]], coords[order[i]])
             for i in range(1, len(order))]
    loop_back = _manhattan(coords[order[-1]], coords[order[0]]) if len(order) > 1 else 0
    comps = connected_components(coords)
    return {
        "order": order,
        "steps": steps,                       # len == len(order) - 1
        "total_steps": sum(steps),
        "loop_back_steps": loop_back,         # coût pour reboucler (rotation continue)
        "connected": len(comps) <= 1,
        "n_components": len(comps),
    }


def split_route(order: List[int], n: int) -> List[List[int]]:
    """Découpe l'ordre serpentin en n segments contigus (1 par compte)."""
    n = max(1, n)
    if not order:
        return [[] for _ in range(n)]
    size = -(-len(order) // n)                # ceil
    segments = [order[i:i + size] for i in range(0, len(order), size)]
    while len(segments) < n:
        segments.append([])
    return segments[:n]


# --- Pathfinding point à point (A -> B) ------------------------------------ #
# Direction cardinale entre deux maps voisines (grille [x, y], Y croissant =
# Sud, comme l'UI). Sert à savoir quel "soleil" cliquer.
def _direction(a: Coord, b: Coord) -> Optional[str]:
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


def find_path(positions: set, start: Coord, goal: Coord) -> List[Coord]:
    """BFS sur la grille de maps (adjacence Manhattan == 1) de start à goal.

    `positions` = ensemble des [x, y] où une map existe (valeurs de MAP_COORDS).
    Retourne la liste des positions de start à goal INCLUS, ou [] si injoignable
    (start/goal absents de la grille, ou pas de chemin par cases adjacentes).
    Le plus court chemin en nombre de changements de map (BFS non pondéré).
    """
    start, goal = tuple(start), tuple(goal)
    if start not in positions or goal not in positions:
        return []
    if start == goal:
        return [start]
    prev: Dict[Coord, Optional[Coord]] = {start: None}
    q = deque([start])
    while q:
        cur = q.popleft()
        if cur == goal:
            break
        x, y = cur
        for nb in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)):
            if nb in positions and nb not in prev:
                prev[nb] = cur
                q.append(nb)
    if goal not in prev:
        return []
    path: List[Coord] = []
    node: Optional[Coord] = goal
    while node is not None:
        path.append(node)
        node = prev[node]
    return path[::-1]


def path_directions(path: List[Coord]) -> List[str]:
    """Directions cardinales (N/S/E/O) entre positions consécutives du chemin."""
    out: List[str] = []
    for i in range(1, len(path)):
        d = _direction(path[i - 1], path[i])
        if d:
            out.append(d)
    return out


def next_direction(positions: set, start: Coord, goal: Coord) -> Optional[str]:
    """Direction du PROCHAIN pas de A vers B (None si arrivé ou injoignable).

    Recalculée à chaque map -> le déplacement s'adapte si le perso finit
    ailleurs que prévu (changement de map raté, téléport, etc.)."""
    path = find_path(positions, start, goal)
    if len(path) < 2:
        return None
    return _direction(path[0], path[1])
