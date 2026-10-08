"""Dump BRUT des segments TCP dans les deux sens, sans hypothèse de framing.

But : voir les octets réels sur le fil. On compare serveur->client (censé être
lisible EL/GDM/GM) et client->serveur (les actions du joueur) pour savoir si ce
dernier est en clair, obfusqué, ou chiffré.
"""
from __future__ import annotations
import sys

PORT = 443


def dump(path, limit=40):
    from scapy.all import IP, Raw, TCP, rdpcap
    pkts = [p for p in rdpcap(path) if TCP in p and Raw in p and IP in p]
    pkts.sort(key=lambda p: float(p.time))

    def show(direction, want_dport):
        print(f"\n===== {direction} =====")
        n = 0
        for p in pkts:
            tcp = p[TCP]
            is_c2s = tcp.dport == PORT
            if is_c2s != want_dport:
                continue
            load = bytes(p[Raw].load)
            ascii_ = "".join(chr(b) if 32 <= b < 127 else "." for b in load)
            print(f"[{n}] len={len(load)}")
            print(f"    hex  : {load[:64].hex()}")
            print(f"    ascii: {ascii_[:64]}")
            n += 1
            if n >= limit:
                break

    show("SERVEUR -> CLIENT (sport==443)", want_dport=False)
    show("CLIENT -> SERVEUR (dport==443)", want_dport=True)


if __name__ == "__main__":
    for f in sys.argv[1:]:
        print(f"\n######## {f} ########")
        dump(f)
