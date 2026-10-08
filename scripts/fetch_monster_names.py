"""Récupère les NOMS des monstres (id template client 1.29) depuis l'API
wiki.moon-bot.io et écrit data/monster_names.json — chargé automatiquement par
app.network.protocol (MONSTER_NAMES).

Source : https://wiki.moon-bot.io/api/monster/<id>.json (mêmes ids que le
protocole ; vérifié 546 = Bambouto Sacré). JSON propre, pas de scraping HTML.
(solomonk.fr utilise aussi ces ids mais est protégé par Cloudflare -> 503.)

Usage :
    python -m scripts.fetch_monster_names 517 524 531 546 549 566 ...
    python -m scripts.fetch_monster_names           # jeu Pandala par défaut

Fusionne avec le JSON existant (n'écrase pas les ids déjà connus, sauf --force).
"""
from __future__ import annotations

import json
import os
import sys
import time
import urllib.request

OUT_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "monster_names.json")
URL = "https://wiki.moon-bot.io/api/monster/{id}.json"
UA = "Mozilla/5.0 Dofus-tool/1.0"

# Ids Pandala rencontrés en capture (défaut si aucun argument).
DEFAULT_IDS = [6, 61, 515, 517, 518, 520, 522, 523, 524, 525, 527, 528, 529,
               530, 531, 532, 535, 546, 548, 549, 566]


def fetch_name(monster_id: int) -> str | None:
    req = urllib.request.Request(URL.format(id=monster_id), headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode("utf-8", "ignore"))
    except Exception as exc:  # noqa: BLE001 - on passe au suivant
        print(f"  {monster_id}: ERREUR {exc}")
        return None
    name = (data or {}).get("name")
    return name.strip() if isinstance(name, str) and name.strip() else None


def main() -> None:
    args = [a for a in sys.argv[1:] if a != "--force"]
    force = "--force" in sys.argv
    ids = [int(a) for a in args] if args else DEFAULT_IDS

    existing: dict = {}
    if os.path.exists(OUT_PATH):
        with open(OUT_PATH, encoding="utf-8") as fh:
            existing = json.load(fh)

    for mid in ids:
        if not force and str(mid) in existing:
            print(f"  {mid}: déjà connu ({existing[str(mid)]}) — skip")
            continue
        name = fetch_name(mid)
        if name:
            existing[str(mid)] = name
            print(f"  {mid}: {name}")
        time.sleep(0.3)  # courtoisie envers le site

    ordered = {str(k): existing[str(k)] for k in sorted(int(k) for k in existing)}
    with open(OUT_PATH, "w", encoding="utf-8") as fh:
        json.dump(ordered, fh, ensure_ascii=False, indent=2)
    print(f"\n{len(ordered)} noms -> {os.path.normpath(OUT_PATH)}")


if __name__ == "__main__":
    main()
