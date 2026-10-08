"""Extrait les stats de résistance (fixe et %) depuis le cache data/details/.

Alimente la table item_stats. Focalisé sur les résistances élémentaires
(neutre/feu/eau/terre/air), au format texte du wiki :
    '+6 à 10 de résistance neutre'      -> res_neutre, fixe, 6..10
    '+6 à 10 % de résistance neutre'    -> res_neutre, %,   6..10
    '+15 % de résistance neutre'        -> res_neutre, %,   15..15

Exclut '... face aux combattants' (mécanique de bouclier différente).

Usage : python -m scripts.parse_stats
"""
from __future__ import annotations

import glob
import json
import logging
import re

from app.db.connection import close_pool, init_pool, transaction
from app.db.repositories import replace_item_stats

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("parse_stats")

# +<min>[ à <max>][ %] de résistance <element>
RES_RE = re.compile(
    r"\+?(\d+)(?:\s*à\s*(\d+))?\s*(%?)\s*de\s+résistance\s+(neutre|feu|eau|terre|air)",
    re.IGNORECASE,
)


def extract_rows(cache_glob="data/details/*.json"):
    best = {}  # (item_id, stat, is_percent) -> (vmin, vmax) ; garde le meilleur max
    for path in glob.glob(cache_glob):
        try:
            obj = json.load(open(path, encoding="utf-8"))
        except Exception:
            continue
        stats = obj.get("stats")
        if not stats:
            continue
        item_id = int(obj["id"])
        for line in stats:
            if not isinstance(line, str) or "face aux combattants" in line:
                continue
            for m in RES_RE.finditer(line):
                vmin = int(m.group(1))
                vmax = int(m.group(2)) if m.group(2) else vmin
                is_percent = m.group(3) == "%"
                stat = "res_" + m.group(4).lower()
                key = (item_id, stat, is_percent)
                if key not in best or vmax > best[key][1]:
                    best[key] = (vmin, vmax)
    return [(iid, stat, isp, vmin, vmax) for (iid, stat, isp), (vmin, vmax) in best.items()]


def main():
    rows = extract_rows()
    logger.info("%d lignes de stats de résistance extraites", len(rows))
    init_pool()
    try:
        with transaction() as cur:
            n = replace_item_stats(cur, rows)
        logger.info("item_stats peuplée : %d lignes.", n)
    finally:
        close_pool()


if __name__ == "__main__":
    main()
