"""Mine les CELLULES DE SORTIE par map depuis les captures.

Principe : le serveur diffuse en clair le deplacement du perso
  GA0;1;<actorId>;<chemin>
et un changement de map = message GDM. La DERNIERE cellule du dernier chemin
GA0 juste avant un GDM = la cellule par laquelle on a quitte la map.

On agrege sur toutes les transitions : pour chaque (map de depart, direction),
on garde la cellule de sortie la plus frequente. La direction vient du delta de
coords [x,y] entre map de depart et map d'arrivee (MAP_COORDS).

Sortie : data/map_exits.json = { "<map_id>": { "N": cell, "S": cell, ... } }
+ un focus sur la map de calibration (par defaut [23,-42]) pour caler la
transformation cellule -> ecran.
"""
from __future__ import annotations

import collections
import glob
import json
import os
import sys

sys.path.insert(0, "/srv")

from app.network import protocol
from app.network.pcap_feed import iter_messages


def _compass(a, b):
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


def mine(paths):
    # etat par stream : map_id courant + derniere cellule GA0 vue
    cur_map = {}
    last_cell = {}
    # (from_map_id, direction) -> Counter des cellules de sortie
    exits = collections.defaultdict(collections.Counter)
    events = []

    for path in paths:
        try:
            for ts, stream, msg in iter_messages(path):
                if msg.startswith("GA0;1;"):
                    parts = msg.split(";")
                    if len(parts) >= 4 and parts[3]:
                        wp = protocol.decode_movement_path(parts[3])
                        if wp:
                            last_cell[stream] = wp[-1][1]   # derniere cellule du chemin
                elif msg.startswith(protocol.MAP_DATA_PREFIX):   # GDM
                    new_map = protocol.parse_map_change(msg)
                    old_map = cur_map.get(stream)
                    if old_map is not None and new_map is not None and old_map != new_map:
                        oc = protocol.MAP_COORDS.get(old_map)
                        nc = protocol.MAP_COORDS.get(new_map)
                        cell = last_cell.get(stream)
                        if oc and nc and cell is not None:
                            d = _compass(oc, nc)
                            if d:
                                exits[(old_map, d)][cell] += 1
                                events.append((old_map, tuple(oc), d, cell, new_map))
                    cur_map[stream] = new_map
                    last_cell.pop(stream, None)
        except Exception as e:  # noqa: BLE001
            print("skip", path, e)

    # consolide : cellule majoritaire par (map, direction)
    table = collections.defaultdict(dict)
    for (mid, d), counter in exits.items():
        cell, n = counter.most_common(1)[0]
        table[mid][d] = {"cell": cell, "n": n, "alt": dict(counter)}
    return table, events


def main():
    folder = sys.argv[1] if len(sys.argv) > 1 else "/srv/data/live"
    files = sorted(glob.glob(os.path.join(folder, "*.pcapng")) +
                   glob.glob(os.path.join(folder, "*.pcap")))
    print(f"{len(files)} captures")
    table, events = mine(files)
    print(f"{len(events)} transitions observees, {len(table)} maps avec sortie(s)")

    # resume : maps zone Pandala
    pandala = {mid: t for mid, t in table.items()
               if "Pandala" in (protocol.MAP_ZONES.get(mid) or "")}
    print(f"\n=== {len(pandala)} maps Pandala avec sorties ===")
    for mid in sorted(pandala, key=lambda m: protocol.MAP_COORDS.get(m, [0, 0])):
        co = protocol.MAP_COORDS.get(mid)
        dirs = {d: v["cell"] for d, v in table[mid].items()}
        print(f"  map {mid} {co} -> {dirs}")

    # focus calibration : la map [23,-42]
    print("\n=== cellules de sortie des maps en [23,-42] (calibration) ===")
    for mid, co in protocol.MAP_COORDS.items():
        if list(co) == [23, -42] and mid in table:
            print(f"  map {mid} : " + str({d: v["cell"] for d, v in table[mid].items()}))

    out = {str(mid): {d: v["cell"] for d, v in t.items()} for mid, t in table.items()}
    with open("/srv/data/map_exits.json", "w", encoding="utf-8") as fh:
        json.dump(out, fh, ensure_ascii=False, indent=0)
    print(f"\n-> data/map_exits.json ecrit ({len(out)} maps)")


if __name__ == "__main__":
    main()
