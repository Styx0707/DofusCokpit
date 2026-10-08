"""Trouve le PORT du protocole de jeu en clair dans une capture.

Ne suppose plus le port 443. Regroupe par port serveur présumé et cherche,
dans chaque sens, des messages LISIBLES du protocole (GDM/GM/EL/ALK/AS/GA...).
Affiche quels ports portent du texte clair et lesquels sont binaires (TLS).
"""
from __future__ import annotations
import collections
import sys

MARKERS = ("GDM", "GM|", "EL", "ALK", "ASK", "AS", "GA", "GKE", "Af", "cC", "BN")


def scan(path):
    from scapy.all import IP, Raw, TCP, rdpcap
    pkts = [p for p in rdpcap(path) if TCP in p and Raw in p and IP in p]
    pkts.sort(key=lambda p: float(p.time))

    # compte, par port, les octets lisibles vs binaires dans chaque sens
    by_port = collections.defaultdict(lambda: {"pkts": 0, "printable": 0, "bytes": 0,
                                               "samples": []})
    for p in pkts:
        tcp = p[TCP]
        load = bytes(p[Raw].load)
        if not load:
            continue
        # port "de jeu" = le plus petit des deux (le serveur écoute sur un port fixe)
        port = min(tcp.sport, tcp.dport)
        d = by_port[port]
        d["pkts"] += 1
        d["bytes"] += len(load)
        printable = sum(1 for b in load if 32 <= b < 127 or b in (0, 10, 13))
        d["printable"] += printable
        # échantillon lisible ?
        if len(d["samples"]) < 6:
            txt = load.decode("latin-1")
            if any(m in txt for m in MARKERS):
                ascii_ = "".join(c if 32 <= ord(c) < 127 else "." for c in txt)
                d["samples"].append((tcp.sport, tcp.dport, ascii_[:80]))

    print(f"\n######## {path} ########")
    print(f"{'port':>6} {'pkts':>6} {'%lisible':>9}  exemples")
    for port, d in sorted(by_port.items(), key=lambda kv: -kv[1]["bytes"]):
        ratio = 100 * d["printable"] / max(1, d["bytes"])
        tag = "CLAIR" if ratio > 85 else ("mixte" if ratio > 50 else "binaire/TLS")
        print(f"{port:>6} {d['pkts']:>6} {ratio:>8.1f}% {tag}")
        for sp, dp, s in d["samples"]:
            arrow = "C->S" if dp == port else "S->C"
            print(f"         {arrow} {s}")


if __name__ == "__main__":
    for f in sys.argv[1:]:
        scan(f)
