"""Cherche dans une capture les messages contenant des objets EQUIPES.

Un objet équipé a une position de slot (0-15) dans le token
O<uid>~<gid>~<qty>~<position>~... (en banque la position est vide).
Sert à identifier le message d'inventaire (équipement complet).

Usage : python -m scripts.find_equip <capture.pcapng>
"""
from __future__ import annotations

import collections
import re
import sys
from scapy.all import IP, Raw, TCP, rdpcap


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "data/game.pcapng"
    flows = collections.defaultdict(dict)
    for p in rdpcap(path):
        if TCP in p and Raw in p and IP in p:
            t = p[TCP]
            pl = bytes(p[Raw].load)
            if pl:
                flows[(p[IP].src, t.sport, p[IP].dst, t.dport)][t.seq] = pl

    tok = re.compile(r"O[0-9a-f]+~[0-9a-f]+~[0-9a-f]*~([0-9]|1[0-5])~")
    by_code = collections.Counter()
    samples = []
    for v in flows.values():
        data = b"".join(v[s] for s in sorted(v)).decode("utf-8", "replace")
        for msg in data.split("\x00"):
            if not msg:
                continue
            if tok.search(msg):
                m = re.match(r"^[A-Za-z]{1,4}", msg)
                code = m.group(0) if m else "?"
                by_code[code] += 1
                if len(samples) < 12:
                    samples.append((code, msg[:200]))

    print(f"[{path}] messages avec objets equipes (position 0-15), par code:")
    print(" ", dict(by_code) or "AUCUN")
    for c, s in samples:
        print(f"  {c} :: {s}")


if __name__ == "__main__":
    main()
