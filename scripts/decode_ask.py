"""Décode le message ASK (perso + inventaire complet) pour caler les positions de slot.

Usage : python -m scripts.decode_ask <capture.pcapng>
"""
from __future__ import annotations

import collections
import json
import sys
from scapy.all import IP, Raw, TCP, rdpcap


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "data/inv_styxh.pcapng"
    items = {int(x["id"]): x["name"] for x in json.load(open("data/items_all.json", encoding="utf-8"))}

    flows = collections.defaultdict(dict)
    for p in rdpcap(path):
        if TCP in p and Raw in p and IP in p:
            t = p[TCP]
            pl = bytes(p[Raw].load)
            if pl:
                flows[(p[IP].src, t.sport, p[IP].dst, t.dport)][t.seq] = pl

    ask = ""
    for v in flows.values():
        data = b"".join(v[s] for s in sorted(v)).decode("utf-8", "replace")
        for m in data.split("\x00"):
            if m.startswith("ASK") and len(m) > len(ask):
                ask = m

    if not ask:
        print("Aucun ASK trouvé.")
        return

    parts = ask.split("|")
    print("header:", parts[:10])
    body = "|".join(parts[10:])
    items_tok = [t for t in body.split(";") if t.strip()]
    print("nb items:", len(items_tok))

    poscount = collections.Counter()
    small = []
    for it in items_tok:
        f = it.split("~")
        if len(f) < 4:
            continue
        pos = f[3]
        poscount[pos] += 1
        try:
            p = int(pos, 16)
        except ValueError:
            continue
        if p <= 20:
            small.append((p, int(f[1], 16)))

    print("\ndistribution des positions (top 25):")
    for pos, n in poscount.most_common(25):
        print(f"  pos={pos!r:>6} : {n}")

    print("\nitems en position <=20 (candidats slots équipés) :")
    for p, g in sorted(small):
        print(f"  pos {p:>2} -> gid {g:<6} {items.get(g, '?')}")


if __name__ == "__main__":
    main()
