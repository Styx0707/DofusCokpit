"""Ingeste le contenu de banque d'une capture .pcap/.pcapng dans PostgreSQL.

Réutilise EXACTEMENT le décodeur de production (app.network.protocol) et le
repository (replace_bank_inventory) : même chemin que le sniffer live, mais
alimenté par un fichier — idéal pour rejouer/tester sans re-capturer.

Usage : python -m scripts.ingest_pcap [data/game.pcapng] [--account compte01]
"""
from __future__ import annotations

import collections
import logging
import sys
from scapy.all import IP, Raw, TCP, rdpcap

from app.db.connection import close_pool, init_pool, transaction
from app.db.repositories import replace_bank_inventory
from app.network.protocol import BANK_MESSAGE_PREFIX, parse_bank_storage

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("ingest")


def reassemble(pkts):
    flows = collections.defaultdict(dict)
    for p in pkts:
        if TCP not in p or Raw not in p or IP not in p:
            continue
        tcp = p[TCP]
        payload = bytes(p[Raw].load)
        if payload:
            flows[(p[IP].src, tcp.sport, p[IP].dst, tcp.dport)][tcp.seq] = payload
    return [b"".join(v[s] for s in sorted(v)) for v in flows.values()]


def extract_bank(pkts):
    best = {}
    for data in reassemble(pkts):
        text = data.decode("utf-8", "replace")
        for msg in text.split("\x00"):
            if msg.startswith(BANK_MESSAGE_PREFIX):
                inv = parse_bank_storage(msg[len(BANK_MESSAGE_PREFIX):])
                if len(inv) > len(best):
                    best = inv
    return best


def parse_args(argv):
    path = "data/game.pcapng"
    account = "main"
    rest = argv[1:]
    i = 0
    while i < len(rest):
        if rest[i] == "--account" and i + 1 < len(rest):
            account = rest[i + 1]
            i += 2
        else:
            path = rest[i]
            i += 1
    return path, account


def main():
    path, account = parse_args(sys.argv)
    inventory = extract_bank(rdpcap(path))
    logger.info("Banque extraite de %s : %d objets (compte '%s').", path, len(inventory), account)
    if not inventory:
        logger.error("Aucun message de banque 'EL' trouvé dans la capture.")
        sys.exit(1)

    init_pool()
    try:
        with transaction() as cur:
            n = replace_bank_inventory(cur, inventory, account)
        logger.info("Persisté : %d objets pour le compte '%s'.", n, account)
    finally:
        close_pool()


if __name__ == "__main__":
    main()
