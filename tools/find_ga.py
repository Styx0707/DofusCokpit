"""Isole les messages 'GA' (déplacement) dans les DEUX sens, sur port 443, en
clair. Objectif : voir exactement ce que le CLIENT envoie pour se déplacer
(C->S) vs ce que le SERVEUR rediffuse (S->C).

Réassemble par flux+sens, découpe sur \\x00 (framing du protocole en clair).
"""
from __future__ import annotations
import collections
import sys

PORT = 443
DELIM = b"\x00"


def find(path):
    from scapy.all import IP, Raw, TCP, rdpcap
    pkts = [p for p in rdpcap(path) if TCP in p and Raw in p and IP in p]
    pkts.sort(key=lambda p: float(p.time))
    buffers = collections.defaultdict(bytes)
    out = []
    for p in pkts:
        ip, tcp = p[IP], p[TCP]
        if PORT not in (tcp.sport, tcp.dport):
            continue
        c2s = tcp.dport == PORT
        key = (ip.src, tcp.sport, ip.dst, tcp.dport)
        buffers[key] += bytes(p[Raw].load)
        *complete, remainder = buffers[key].split(DELIM)
        buffers[key] = remainder
        for raw in complete:
            if not raw:
                continue
            txt = raw.decode("latin-1")
            if "GA" in txt:
                out.append((float(p.time), "C->S" if c2s else "S->C", raw))
    out.sort(key=lambda t: t[0])
    print(f"\n######## {path} — {len(out)} messages contenant 'GA' ########")
    for ts, direction, raw in out[:60]:
        txt = "".join(c if 32 <= ord(c) < 127 else "." for c in raw.decode("latin-1"))
        print(f"[{ts:.3f}] {direction}  text={txt[:70]!r}")
        print(f"                 hex ={raw[:48].hex()}")


if __name__ == "__main__":
    for f in sys.argv[1:]:
        find(f)
