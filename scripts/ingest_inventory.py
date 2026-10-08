"""Ingeste l'équipement COMPLET (option B) depuis une capture d'entrée en jeu.

Décode tous les messages 'ASK' (perso + inventaire). Chaque ASK porte le
character_id -> on retrouve le compte via le roster déjà ingéré (table
characters). Une capture peut contenir plusieurs persos (entrées successives).

Usage :
    python -m scripts.ingest_inventory [capture.pcapng] [--account fallback]
"""
from __future__ import annotations

import collections
import logging
import sys
from scapy.all import IP, Raw, TCP, rdpcap

from app.db.characters_repo import get_account_for_character, replace_character_full_equipment
from app.db.connection import close_pool, init_pool, transaction
from app.network.protocol import INVENTORY_PREFIX, parse_character_inventory

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("ingest_inventory")


def extract_inventories(pkts):
    """Renvoie {character_id: char} en gardant l'ASK le plus complet par perso."""
    flows = collections.defaultdict(dict)
    for p in pkts:
        if TCP not in p or Raw not in p or IP not in p:
            continue
        tcp = p[TCP]
        payload = bytes(p[Raw].load)
        if payload:
            flows[(p[IP].src, tcp.sport, p[IP].dst, tcp.dport)][tcp.seq] = payload

    best = {}
    for segs in flows.values():
        data = b"".join(segs[s] for s in sorted(segs)).decode("utf-8", "replace")
        for msg in data.split("\x00"):
            if msg.startswith(INVENTORY_PREFIX):
                char = parse_character_inventory(msg)
                if char:
                    prev = best.get(char["character_id"])
                    if prev is None or len(char["equipment"]) > len(prev["equipment"]):
                        best[char["character_id"]] = char
    return best


def parse_args(argv):
    path, fallback = "data/inv_styxh.pcapng", None
    rest, i = argv[1:], 0
    while i < len(rest):
        if rest[i] == "--account" and i + 1 < len(rest):
            fallback = rest[i + 1];
            i += 2
        else:
            path = rest[i];
            i += 1
    return path, fallback


def main():
    path, fallback = parse_args(sys.argv)
    chars = extract_inventories(rdpcap(path))
    logger.info("%d perso(s) avec inventaire dans %s", len(chars), path)
    if not chars:
        logger.error("Aucun message 'ASK' trouvé.")
        sys.exit(1)

    init_pool()
    try:
        with transaction() as cur:
            done = 0
            for char in chars.values():
                account = get_account_for_character(cur, char["character_id"]) or fallback
                if not account:
                    logger.warning("  %s : compte inconnu (roster non ingéré ?) -> ignoré. "
                                   "Utilise --account.", char["name"])
                    continue
                n = replace_character_full_equipment(cur, account, char)
                logger.info("  [%s] %s : %d pièces équipées", account, char["name"], n)
                done += 1
        logger.info("Terminé : %d perso(s) mis à jour.", done)
    finally:
        close_pool()


if __name__ == "__main__":
    main()
