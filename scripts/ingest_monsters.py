"""Crawl COMPLET du bestiaire xixou.io -> ``data/monsters.json``.

Pour chaque monstre Retro (bestiaire-sitemap.xml), récupère niveau + zones +
table de drops COMPLÈTE (ressource, taux). Chaque ressource est reliée à son
``item_id`` moon-bot (via ``data/items_all.json``, match par nom normalisé) pour
pouvoir la valoriser au prix HDV côté app (``/farm/kamas``).

Sortie ``data/monsters.json`` :
  {"<slug>": {"name","level_min","level_max","zones":[...],
              "drops":[{"item_id"|null,"name","rate"}, ...]}, ...}

Réutilise le cache HTML ``data/cache_xixou/monstres/`` (déjà peuplé par
ingest_drops). Usage : ``py scripts/ingest_monsters.py [--delay 0.2] [--limit N]``.
Réseau : stdlib ``urllib`` + SSL non vérifié (cf. app/api.py).
"""
from __future__ import annotations

import argparse
import html
import json
import re
import ssl
import sys
import time
import unicodedata
import urllib.request
from pathlib import Path

BASE = "https://xixou.io"
ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "cache_xixou" / "monstres"
OUT = ROOT / "data" / "monsters.json"
_CTX = ssl._create_unverified_context()
_UA = {"User-Agent": "Mozilla/5.0 (DofusCokpit monsters ingest)"}


def _norm(s: str) -> str:
    s = unicodedata.normalize("NFKD", (s or "").replace("\\'", "'"))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9]+", " ", s.lower()).strip()


def fetch(url: str, delay: float, cache_key: str) -> str | None:
    cpath = CACHE / cache_key
    if cpath.exists():
        return cpath.read_text(encoding="utf-8")
    try:
        req = urllib.request.Request(url, headers=_UA)
        with urllib.request.urlopen(req, timeout=30, context=_CTX) as r:
            txt = r.read().decode("utf-8", "replace")
    except Exception as e:  # noqa: BLE001
        print(f"    ! {url} : {e}")
        return None
    cpath.parent.mkdir(parents=True, exist_ok=True)
    cpath.write_text(txt, encoding="utf-8")
    time.sleep(delay)
    return txt


_DROP_ROW = re.compile(
    r'<a href="https://xixou\.io/encyclopedie/ressources/([^"/]+)/"[^>]*>([^<]+)</a>\s*</td>\s*<td>([0-9.]+)%',
    re.S)
_ZONE = re.compile(r'/encyclopedie/zones/[^"/]+/">([^<]+)</a>')
_JSONLD_NAME = re.compile(r'"@type":"ItemPage","name":"([^"—]+)')
_LEVEL = re.compile(r'Niveau\s*(\d+)(?:\s*(?:à|a|-)\s*(\d+))?', re.I)


def parse_monster(h: str, name_to_id: dict) -> dict:
    zblock = ""
    m = re.search(r"<h2>Zones d'apparition</h2>(.*?)</ul>", h, re.S)
    if m:
        zblock = m.group(1)
    zones = [html.unescape(z).strip() for z in _ZONE.findall(zblock)]

    drops = []
    md = re.search(r"<h2>Drops.*?</table>", h, re.S)
    if md:
        seen = set()
        for slug, nm, rate in _DROP_ROW.findall(md.group(0)):
            nm = html.unescape(nm).strip()
            if slug in seen:
                continue
            seen.add(slug)
            try:
                r = round(float(rate))
            except ValueError:
                continue
            drops.append({"item_id": name_to_id.get(_norm(nm)), "name": nm, "rate": r})

    nm = _JSONLD_NAME.search(h)
    name = html.unescape(nm.group(1)).strip() if nm else ""
    lvl = _LEVEL.search(h)
    lmin = int(lvl.group(1)) if lvl else None
    lmax = int(lvl.group(2)) if (lvl and lvl.group(2)) else lmin
    return {"name": name, "level_min": lmin, "level_max": lmax, "zones": zones, "drops": drops}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--delay", type=float, default=0.2)
    ap.add_argument("--limit", type=int, default=0)
    args = ap.parse_args()

    # nom normalisé -> item_id (catalogue complet moon-bot)
    items = json.loads((ROOT / "data" / "items_all.json").read_text(encoding="utf-8"))
    name_to_id = {}
    for it in items:
        n = _norm(it.get("name"))
        if n and n not in name_to_id:
            name_to_id[n] = int(it["id"])
    print(f"{len(name_to_id)} noms d'items indexés.")

    sm = fetch(f"{BASE}/bestiaire-sitemap.xml", args.delay, "../bestiaire-sitemap.xml") or ""
    slugs = re.findall(r"/encyclopedie/monstres/([^/<]+)/</loc>", sm)
    if args.limit:
        slugs = slugs[: args.limit]
    print(f"{len(slugs)} monstres à traiter.")

    out = {}
    matched = total_drops = 0
    for i, slug in enumerate(slugs, 1):
        h = fetch(f"{BASE}/encyclopedie/monstres/{slug}/", args.delay, f"{slug}.html")
        if not h:
            continue
        mon = parse_monster(h, name_to_id)
        out[slug] = mon
        total_drops += len(mon["drops"])
        matched += sum(1 for d in mon["drops"] if d["item_id"])
        if i % 100 == 0:
            print(f"    … {i}/{len(slugs)}")

    OUT.write_text(json.dumps(out, ensure_ascii=False), encoding="utf-8")
    print(f"\n{OUT} écrit : {len(out)} monstres, {total_drops} lignes de drop, "
          f"{matched} reliées à un item_id ({100*matched//max(total_drops,1)}%).")


if __name__ == "__main__":
    main()
