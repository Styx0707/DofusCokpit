"""Analyse une capture .pcap/.pcapng et repère les flux TCP Dofus en clair.

Réassemble chaque flux TCP directionnel (par numéro de séquence), mesure la part
d'octets imprimables, et pour les flux « texte » affiche les messages découpés
sur l'octet nul (délimiteur Dofus). Aide à identifier le message de banque et
son encodage réel, quel que soit le port.

Usage :
    python -m scripts.parse_pcap data/game.pcapng [port] [--needle EsK]

- port    : ne garde que les flux impliquant ce port (optionnel).
- --needle: surligne les messages contenant cette sous-chaîne (def. "EsK").
"""
from __future__ import annotations

import collections
import re
import string
import sys
from scapy.all import IP, Raw, TCP, rdpcap

PRINTABLE = set(bytes(string.printable, "ascii"))
PRINTABLE_RATIO_MIN = 0.60
HEADER_RE = re.compile(r"^[A-Za-z]{1,3}")


def parse_args(argv):
    path = argv[1] if len(argv) > 1 else "data/game.pcapng"
    port = None
    needle = "EsK"
    rest = argv[2:]
    i = 0
    while i < len(rest):
        if rest[i] == "--needle" and i + 1 < len(rest):
            needle = rest[i + 1]
            i += 2
        else:
            try:
                port = int(rest[i])
            except ValueError:
                pass
            i += 1
    return path, port, needle


def reassemble(pkts, port):
    """{(src,sport,dst,dport): bytes} — payloads concaténés par ordre de séquence."""
    flows = collections.defaultdict(dict)  # dirkey -> {seq: payload}
    for p in pkts:
        if TCP not in p or Raw not in p or IP not in p:
            continue
        ip, tcp = p[IP], p[TCP]
        if port is not None and port not in (tcp.sport, tcp.dport):
            continue
        payload = bytes(p[Raw].load)
        if payload:
            flows[(ip.src, tcp.sport, ip.dst, tcp.dport)][tcp.seq] = payload
    return {k: b"".join(v[s] for s in sorted(v)) for k, v in flows.items()}


def main():
    path, port, needle = parse_args(sys.argv)
    print(f"Lecture {path} (port={port or 'tous'}, needle={needle!r})")
    pkts = rdpcap(path)
    flows = reassemble(pkts, port)
    if not flows:
        print("Aucun flux TCP avec données. Le perso était-il en jeu / banque ouverte ?")
        return

    all_msgs = []  # (dirkey, message_str) pour l'analyse globale

    for dirkey, data in sorted(flows.items(), key=lambda kv: len(kv[1]), reverse=True):
        src, sport, dst, dport = dirkey
        ratio = sum(1 for c in data if c in PRINTABLE) / len(data)
        head = f"{src}:{sport} -> {dst}:{dport}  ({len(data)} o, {ratio:.0%} imprimable)"
        print("\n===== FLUX", head, "=====")
        if ratio < PRINTABLE_RATIO_MIN:
            print("  [binaire/chiffré probable] hex[:80] =", data[:80].hex())
            continue
        messages = [m for m in data.split(b"\x00") if m]
        print(f"  {len(messages)} message(s) texte :")
        for m in messages[:40]:
            txt = m.decode("utf-8", "replace")
            all_msgs.append((dirkey, txt))
            flag = "  <<< NEEDLE" if needle and needle in txt else ""
            print(f"    | {txt[:180]}{flag}")
        for m in messages[40:]:
            all_msgs.append((dirkey, m.decode("utf-8", "replace")))

    # --- Analyse globale : messages « liste d'objets » (bourrés de '~') -------
    print("\n##### CANDIDATS LISTE D'OBJETS (triés par nb de '~') #####")
    cand = sorted(all_msgs, key=lambda t: t[1].count("~"), reverse=True)[:12]
    for dirkey, s in cand:
        header = HEADER_RE.match(s)
        hdr = header.group(0) if header else "?"
        print(f"  [~x{s.count('~'):<4} len={len(s):<6} hdr={hdr:<3}] {s[:90]!r}")

    # --- Inventaire des codes de message rencontrés --------------------------
    codes = collections.Counter()
    for _, s in all_msgs:
        mobj = HEADER_RE.match(s)
        if mobj:
            codes[mobj.group(0)] += 1
    print("\n##### CODES DE MESSAGE (préfixe alpha) : count #####")
    for code, n in codes.most_common(40):
        print(f"  {code:<4} : {n}")


if __name__ == "__main__":
    main()
