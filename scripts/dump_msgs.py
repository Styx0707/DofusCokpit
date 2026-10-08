"""Dump exploratoire : codes de message + messages 'liste d'objets' d'une capture.

Usage : python -m scripts.dump_msgs <capture.pcapng>
"""
from __future__ import annotations

import collections
import re
import sys
from scapy.all import IP, Raw, TCP, rdpcap


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "data/inv_styxh.pcapng"
    flows = collections.defaultdict(dict)
    for p in rdpcap(path):
        if TCP in p and Raw in p and IP in p:
            t = p[TCP]
            pl = bytes(p[Raw].load)
            if pl:
                flows[(p[IP].src, t.sport, p[IP].dst, t.dport)][t.seq] = pl

    codes = collections.Counter()
    item_msgs = []
    for v in flows.values():
        data = b"".join(v[s] for s in sorted(v)).decode("utf-8", "replace")
        for m in data.split("\x00"):
            if not m:
                continue
            mm = re.match(r"^[A-Za-z]{1,4}", m)
            if mm:
                codes[mm.group(0)] += 1
            if m.count("~") >= 3:
                item_msgs.append(m)

    print("=== codes ===")
    for c, n in codes.most_common(60):
        print(f"{n:4} {c}")
    print("\n=== messages riches en '~' (listes d'objets), top 6 ===")
    item_msgs.sort(key=lambda s: s.count("~"), reverse=True)
    for m in item_msgs[:6]:
        print(f"--- len={len(m)} tildes={m.count('~')} head={m[:8]!r}")
        print(m[:500])
        print()


if __name__ == "__main__":
    main()
