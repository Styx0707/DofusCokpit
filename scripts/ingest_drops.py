"""Ingestion des tables de butin depuis xixou.io -> ``data/drops.json``.

Pour chaque ressource-FEUILLE nécessaire aux crafts de brisage qui n'est PAS une
ressource de métier (butin / type générique, cf. ``app.core.farm.classify_source``),
on récupère sur xixou.io les monstres qui la droppent, leurs zones et le taux.

Sens de crawl (évite de deviner les slugs et la troncature des listes) :
  1. page RESSOURCE ``/encyclopedie/ressources/<slug>/`` -> slugs des monstres dropeurs ;
  2. page MONSTRE ``/encyclopedie/monstres/<slug>/`` -> zones + table de drops complète
     (slug de ressource -> taux). La jointure ressource<->monstre se fait sur le SLUG.
Les slugs de ressources sont validés contre ``ressources-sitemap.xml`` (match exact,
sinon rapprochement flou). Cache disque (``data/cache_xixou/``) -> reprise + politesse
(aucune page re-téléchargée).

Sortie ``data/drops.json`` :
  {"<item_id>": {"name": "...", "slug": "...",
                 "sources": [{"monster": "Bouftou", "slug": "bouftou", "rate": 80,
                              "zones": ["La forêt d'Amakna", ...]}, ...]}, ...}

Usage : ``py scripts/ingest_drops.py [--max-level 120] [--limit N] [--delay 0.3]``
Réseau : stdlib ``urllib`` + contexte SSL non vérifié (cf. app/api.py).
"""
from __future__ import annotations

import argparse
import difflib
import html
import json
import re
import ssl
import sys
import time
import unicodedata
import urllib.request
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.core.brisage import ingredient_recipes, load_detail, load_pa_targets  # noqa: E402
from app.core.farm import classify_source, flatten_resources  # noqa: E402

BASE = "https://xixou.io"
ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "cache_xixou"
OUT = ROOT / "data" / "drops.json"
_CTX = ssl._create_unverified_context()
_UA = {"User-Agent": "Mozilla/5.0 (DofusCokpit drops ingest)"}


def slugify(name: str) -> str:
    """Nom -> slug xixou : sans accents, minuscule, tout non [a-z0-9] -> '-'.
    Ex. « Oeil d'Ouginak » -> « oeil-d-ouginak » (comme « bouftou-d-halouine »)."""
    n = unicodedata.normalize("NFKD", (name or "").replace("\\'", "'"))
    n = "".join(c for c in n if not unicodedata.combining(c))
    return re.sub(r"-+", "-", re.sub(r"[^a-z0-9]+", "-", n.lower())).strip("-")


def fetch(url: str, delay: float, cache_key: str | None = None) -> str | None:
    """GET mémoïsé sur disque. ``cache_key`` = chemin relatif dans CACHE. None sur 404/err."""
    cpath = (CACHE / cache_key) if cache_key else None
    if cpath and cpath.exists():
        return cpath.read_text(encoding="utf-8")
    try:
        req = urllib.request.Request(url, headers=_UA)
        with urllib.request.urlopen(req, timeout=30, context=_CTX) as r:
            txt = r.read().decode("utf-8", "replace")
    except Exception as e:  # noqa: BLE001  (404, timeout, SSL…) -> on log et on continue
        print(f"    ! {url} : {e}")
        return None
    if cpath:
        cpath.parent.mkdir(parents=True, exist_ok=True)
        cpath.write_text(txt, encoding="utf-8")
    time.sleep(delay)
    return txt


def sitemap_slugs(kind: str, delay: float) -> set[str]:
    """Slugs d'un type (``ressources``/``bestiaire``) depuis son sitemap xixou."""
    h = fetch(f"{BASE}/{kind}-sitemap.xml", delay, f"{kind}-sitemap.xml") or ""
    return set(re.findall(rf"/encyclopedie/[^/]+/([^/<]+)/</loc>", h))


_DROP_ROW = re.compile(
    r'<a href="https://xixou\.io/encyclopedie/ressources/([^"/]+)/"[^>]*>([^<]+)</a>\s*</td>\s*<td>([0-9.]+)%',
    re.S)
_MON_LINK = re.compile(r'/encyclopedie/monstres/([^"/]+)/"')
_ZONE = re.compile(r'/encyclopedie/zones/[^"/]+/">([^<]+)</a>')
_JSONLD_NAME = re.compile(r'"@type":"ItemPage","name":"([^"—]+)')


def parse_monster(h: str) -> dict:
    """Page monstre -> ``{"name", "zones":[...], "drops": {res_slug: rate_int}}``."""
    # Zones : uniquement le <ul> de la section « Zones d'apparition ».
    zblock = ""
    m = re.search(r"<h2>Zones d'apparition</h2>(.*?)</ul>", h, re.S)
    if m:
        zblock = m.group(1)
    zones = [html.unescape(z).strip() for z in _ZONE.findall(zblock)]
    # Drops : table de la section « Drops ».
    drops: dict[str, int] = {}
    md = re.search(r"<h2>Drops.*?</table>", h, re.S)
    if md:
        for slug, _name, rate in _DROP_ROW.findall(md.group(0)):
            try:
                drops[slug] = max(drops.get(slug, 0), round(float(rate)))
            except ValueError:
                pass
    nm = _JSONLD_NAME.search(h)
    name = html.unescape(nm.group(1)).strip() if nm else ""
    return {"name": name, "zones": zones, "drops": drops}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--max-level", type=int, default=120)
    ap.add_argument("--limit", type=int, default=0, help="limite le nb de ressources (debug)")
    ap.add_argument("--delay", type=float, default=0.3, help="pause entre requêtes réseau (s)")
    args = ap.parse_args()

    # 1) Ressources-feuilles de BUTIN à résoudre (on ignore les ressources de métier).
    targets, _ = load_pa_targets(max_level=args.max_level)
    recipes = ingredient_recipes({ing["item_id"] for t in targets for ing in t["recipe"]})
    from collections import Counter
    agg: Counter = Counter()
    for t in targets:
        for ing in t["recipe"]:
            flatten_resources(ing["item_id"], ing["quantity"], recipes, agg)
    needed: dict[int, dict] = {}
    for leaf_id in agg:
        d = load_detail(leaf_id) or {}
        kind, _prof = classify_source(d.get("type"))
        if kind == "harvest":
            continue
        name = (d.get("name") or "").replace("\\'", "'")
        if name:
            needed[leaf_id] = {"name": name, "slug": None}
    print(f"{len(targets)} cibles, {len(agg)} feuilles, {len(needed)} ressources de butin à résoudre.")

    # 2) Slugs de ressources (validation contre le sitemap).
    res_slugs = sitemap_slugs("ressources", args.delay)
    print(f"ressources-sitemap : {len(res_slugs)} slugs.")
    items = list(needed.items())[: args.limit or None]
    for iid, info in items:
        s = slugify(info["name"])
        if s in res_slugs:
            info["slug"] = s
        else:
            close = difflib.get_close_matches(s, res_slugs, n=1, cutoff=0.82)
            info["slug"] = close[0] if close else None
            if not close:
                print(f"    ? slug introuvable pour {info['name']!r} ({s})")

    # 3) Pages ressources -> slugs de monstres dropeurs.
    monster_slugs: set[str] = set()
    for iid, info in items:
        if not info["slug"]:
            continue
        h = fetch(f"{BASE}/encyclopedie/ressources/{info['slug']}/", args.delay,
                  f"ressources/{info['slug']}.html")
        if h:
            info["droppers"] = sorted(set(_MON_LINK.findall(h)))
            monster_slugs.update(info["droppers"])
    print(f"{len(monster_slugs)} monstres dropeurs à charger.")

    # 4) Pages monstres -> zones + drops (cache).
    monsters: dict[str, dict] = {}
    for i, ms in enumerate(sorted(monster_slugs), 1):
        h = fetch(f"{BASE}/encyclopedie/monstres/{ms}/", args.delay, f"monstres/{ms}.html")
        if h:
            monsters[ms] = parse_monster(h)
        if i % 20 == 0:
            print(f"    … {i}/{len(monster_slugs)} monstres")

    # 5) Jointure sur le slug de ressource -> data/drops.json.
    out: dict[str, dict] = {}
    resolved = 0
    for iid, info in items:
        if not info["slug"]:
            continue
        sources = []
        for ms in info.get("droppers", []):
            mon = monsters.get(ms)
            if not mon:
                continue
            rate = mon["drops"].get(info["slug"])
            if rate is None:
                continue
            sources.append({"monster": mon["name"] or ms, "slug": ms,
                            "rate": rate, "zones": mon["zones"]})
        sources.sort(key=lambda s: -s["rate"])
        if sources:
            resolved += 1
        out[str(iid)] = {"name": info["name"], "slug": info["slug"], "sources": sources}

    OUT.write_text(json.dumps(out, ensure_ascii=False, indent=1), encoding="utf-8")
    print(f"\n{OUT} écrit : {len(out)} ressources, {resolved} avec au moins une source de butin.")


if __name__ == "__main__":
    main()
