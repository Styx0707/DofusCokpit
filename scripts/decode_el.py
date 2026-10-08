"""Décode le message de banque 'EL' d'une capture pour verrouiller le format.

Trouve le plus gros message commençant par 'EL', découpe les objets et affiche
les champs en hexa + décimal, pour identifier lequel est le GID (template) et
lequel est la quantité.

Usage : python -m scripts.decode_el data/game.pcapng
"""
from __future__ import annotations

import collections
import sys
from scapy.all import IP, Raw, TCP, rdpcap


def reassemble(pkts):
    flows = collections.defaultdict(dict)
    for p in pkts:
        if TCP not in p or Raw not in p or IP not in p:
            continue
        ip, tcp = p[IP], p[TCP]
        payload = bytes(p[Raw].load)
        if payload:
            flows[(ip.src, tcp.sport, ip.dst, tcp.dport)][tcp.seq] = payload
    return [b"".join(v[s] for s in sorted(v)) for v in flows.values()]


def find_el(streams):
    best = ""
    for data in streams:
        try:
            text = data.decode("utf-8", "replace")
        except Exception:
            continue
        for msg in text.split("\x00"):
            if msg.startswith("EL") and msg.count("~") > best.count("~"):
                best = msg
    return best


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "data/game.pcapng"
    el = find_el(reassemble(rdpcap(path)))
    if not el:
        print("Aucun message 'EL' trouvé.")
        return

    body = el[2:]  # retire 'EL'
    items = [t for t in body.split(";") if t]
    print(f"Message EL : {len(items)} objets\n")
    print(f"{'#':>3}  {'raw':<32}  fields(hex)")
    print("-" * 80)
    for idx, tok in enumerate(items[:25]):
        raw = tok[1:] if tok.startswith("O") else tok  # retire 'O'
        parts = raw.split("~")
        hexs = " | ".join(parts)
        print(f"{idx:>3}  {tok[:30]:<32}  {hexs}")

    # Statistiques par colonne pour repérer GID vs quantité.
    cols = collections.defaultdict(list)
    for tok in items:
        raw = tok[1:] if tok.startswith("O") else tok
        for i, p in enumerate(raw.split("~")):
            p = p.split("#")[0]  # ignore la partie stats après '#'
            if p:
                try:
                    cols[i].append(int(p, 16))
                except ValueError:
                    pass
    print("\nStatistiques par colonne (décimal, hors 'uid' col0) :")
    for i in sorted(cols):
        vals = cols[i]
        if not vals:
            continue
        print(f"  col{i}: n={len(vals):<5} min={min(vals):<8} max={max(vals):<10} "
              f"exemples={vals[:6]}")


if __name__ == "__main__":
    main()
