"""Ingeste le(s) roster(s) (persos + équipement visible) depuis une capture.

Gère une capture contenant PLUSIEURS comptes : chaque connexion de compte
produit un message 'ALK'. Les rosters sont dédupliqués (par ensemble d'IDs de
persos) et ordonnés par ordre d'apparition (temps du 1er paquet).

Usage :
    python -m scripts.ingest_roster [capture.pcapng] [options]

Options :
    --list                 Prévisualise sans écrire en base.
    --prefix compte        Préfixe des comptes auto-nommés (def. "compte") -> compte01..
    --account NOM          Force un nom unique (seulement si 1 seul roster).
    --start N              Numéro de départ pour l'auto-nommage (def. 1).
"""
from __future__ import annotations

import collections
import logging
import sys
from scapy.all import IP, Raw, TCP, rdpcap

from app.db.characters_repo import replace_account_characters
from app.db.connection import close_pool, init_pool, transaction
from app.network.protocol import CHARACTER_LIST_PREFIX, parse_character_list

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("ingest_roster")


def extract_rosters(pkts):
    """Renvoie la liste des rosters distincts, ordonnés par 1er paquet vu."""
    flows = collections.defaultdict(dict)
    ftime = {}
    for p in pkts:
        if TCP not in p or Raw not in p or IP not in p:
            continue
        tcp = p[TCP]
        key = (p[IP].src, tcp.sport, p[IP].dst, tcp.dport)
        payload = bytes(p[Raw].load)
        if payload:
            flows[key][tcp.seq] = payload
            ftime[key] = min(ftime.get(key, float(p.time)), float(p.time))

    found = []
    for key, segs in flows.items():
        data = b"".join(segs[s] for s in sorted(segs)).decode("utf-8", "replace")
        for msg in data.split("\x00"):
            if msg.startswith(CHARACTER_LIST_PREFIX):
                chars = parse_character_list(msg[len(CHARACTER_LIST_PREFIX):])
                if chars:
                    found.append((ftime[key], chars))

    found.sort(key=lambda r: r[0])
    # Déduplication : un même compte peut renvoyer plusieurs ALK (reconnexion).
    seen, rosters = set(), []
    for _, chars in found:
        sig = frozenset(c["character_id"] for c in chars)
        if sig in seen:
            continue
        seen.add(sig)
        rosters.append(chars)
    return rosters


def parse_args(argv):
    opts = {"path": "data/select_compteXX.pcapng", "list": False,
            "prefix": "compte", "account": None, "start": 1}
    rest, i = argv[1:], 0
    while i < len(rest):
        a = rest[i]
        if a == "--list":
            opts["list"] = True;
            i += 1
        elif a == "--prefix" and i + 1 < len(rest):
            opts["prefix"] = rest[i + 1];
            i += 2
        elif a == "--account" and i + 1 < len(rest):
            opts["account"] = rest[i + 1];
            i += 2
        elif a == "--start" and i + 1 < len(rest):
            opts["start"] = int(rest[i + 1]);
            i += 2
        else:
            opts["path"] = a;
            i += 1
    return opts


def main():
    o = parse_args(sys.argv)
    rosters = extract_rosters(rdpcap(o["path"]))
    logger.info("%d roster(s) distinct(s) dans %s", len(rosters), o["path"])
    if not rosters:
        logger.error("Aucun message 'ALK' trouvé.")
        sys.exit(1)

    # Attribution des noms de comptes.
    if o["account"] and len(rosters) == 1:
        names = [o["account"]]
    else:
        if o["account"]:
            logger.warning("--account ignoré : %d rosters -> auto-nommage.", len(rosters))
        names = [f"{o['prefix']}{o['start'] + i:02d}" for i in range(len(rosters))]

    for name, chars in zip(names, rosters):
        preview = ", ".join(f"{c['name']} n{c['level']} {c['class_name']}" for c in chars[:8])
        logger.info("[%s] %d perso(s) : %s", name, len(chars), preview)

    if o["list"]:
        logger.info("(--list) aucune écriture en base.")
        return

    init_pool()
    try:
        with transaction() as cur:
            total = sum(replace_account_characters(cur, name, chars)
                        for name, chars in zip(names, rosters))
        logger.info("Persisté : %d perso(s) sur %d compte(s).", total, len(rosters))
    finally:
        close_pool()


if __name__ == "__main__":
    main()
