"""Importe, depuis le dump SQL de l'émulateur Naia (Chnossos/Naia), pour TOUTES
les maps Dofus 1.29 :
- data/map_coords.json : {mapId: [x, y]}     (coordonnées affichées en jeu)
- data/map_zones.json  : {mapId: "sous-zone"} (nom de la sous-zone, ex. Pandala)

Les ids du dump = ids du protocole (GDM) -> mapping direct. Tables Naia :
  maps(ID, Pos_X, Pos_Y, Width, Height, Subarea, Map_Data, ...)  -> 6 premiers champs
  subarea_data(ID, Area, Alignment_Side, Name)                   -> Subarea -> nom

Usage (dans le conteneur) :
    python -m scripts.import_map_coords
Puis rechargement à chaud : POST /live/maps/reload.
"""
from __future__ import annotations

import json
import os
import re
import urllib.request

BASE = "https://raw.githubusercontent.com/Chnossos/Naia/master/sql/game"
DATA = os.path.join(os.path.dirname(__file__), "..", "data")
UA = "Mozilla/5.0 Dofus-tool/1.0"

# maps : ('ID', 'Pos_X', 'Pos_Y', 'Width', 'Height', 'Subarea', ...
MAP_RE = re.compile(
    rb"INSERT INTO `maps` VALUES \('(-?\d+)',\s*'(-?\d+)',\s*'(-?\d+)',"
    rb"\s*'(-?\d+)',\s*'(-?\d+)',\s*'(-?\d+)'")
# subarea_data : ('ID', 'Area', 'Alignment', 'Name')
SUB_RE = re.compile(
    r"INSERT INTO `subarea_data` VALUES \(\s*'(\d+)'\s*,\s*'-?\d+'\s*,"
    r"\s*'-?\d+'\s*,\s*'((?:\\.|[^'])*)'\s*\)")


def _open(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers={"User-Agent": UA}), timeout=120)


def _unescape(s: str) -> str:
    return s.replace("\\'", "'").replace('\\"', '"').replace("\\\\", "\\")


def load_subarea_names() -> dict:
    with _open(f"{BASE}/subarea_data.sql") as fh:
        text = fh.read().decode("utf-8", "ignore")
    return {int(m.group(1)): _unescape(m.group(2)) for m in SUB_RE.finditer(text)}


def main() -> None:
    print("Sous-zones…")
    sub_names = load_subarea_names()
    print(f"  {len(sub_names)} sous-zones")

    print("Maps (coords + zone)…")
    coords, zones, skipped = {}, {}, 0
    with _open(f"{BASE}/maps.sql") as fh:
        for line in fh:
            m = MAP_RE.search(line)
            if not m:
                continue
            mid, x, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
            sub = int(m.group(6))
            if mid == 0:
                continue
            name = sub_names.get(sub)
            if name:
                zones[str(mid)] = name
            if x == 0 and y == 0:
                skipped += 1        # intérieurs non positionnés -> pas de coord
                continue
            coords[str(mid)] = [x, y]

    with open(os.path.join(DATA, "map_coords.json"), "w", encoding="utf-8") as f:
        json.dump({k: coords[k] for k in sorted(coords, key=int)}, f, ensure_ascii=False)
    with open(os.path.join(DATA, "map_zones.json"), "w", encoding="utf-8") as f:
        json.dump({k: zones[k] for k in sorted(zones, key=int)}, f, ensure_ascii=False)

    print(f"{len(coords)} coords, {len(zones)} zones ({skipped} intérieurs [0,0] sans coord)")
    for probe in ("8157", "8158", "7411"):
        print(f"  map {probe} -> {coords.get(probe)}  {zones.get(probe)!r}")


if __name__ == "__main__":
    main()
