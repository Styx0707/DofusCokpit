"""Extrait les messages CLIENT -> SERVEUR d'une capture (sens inverse du sniffer).

Le sniffer/pcap_feed ne lit que serveur->client (sport==443). Les actions du
joueur (déplacement GA, etc.) partent dans l'autre sens : client->serveur
(dport==443). Ce script réassemble ce sens-là et affiche les messages, en
mettant en avant ceux qui ressemblent à une action de jeu (GA...).

Usage (dans le conteneur, scapy dispo) :
  python tools/extract_client_messages.py data/live/<fichier>.pcapng
  python tools/extract_client_messages.py --all data/live   # scanne un dossier
"""
from __future__ import annotations

import collections
import glob
import os
import sys

DELIMITER = b"\x00"
GAME_PORT = 443


def iter_client_messages(path, port=GAME_PORT):
    """Rejoue un pcap -> (ts, stream, message) pour le sens CLIENT->SERVEUR."""
    from scapy.all import IP, Raw, TCP, rdpcap

    pkts = [p for p in rdpcap(path) if TCP in p and Raw in p and IP in p]
    pkts.sort(key=lambda p: float(p.time))
    buffers = collections.defaultdict(bytes)
    for p in pkts:
        ip, tcp = p[IP], p[TCP]
        if tcp.dport != port:            # client -> serveur uniquement
            continue
        stream = (ip.src, tcp.sport)     # le client émetteur
        buffers[stream] += bytes(p[Raw].load)
        *complete, remainder = buffers[stream].split(DELIMITER)
        buffers[stream] = remainder
        for raw in complete:
            if raw:
                yield float(p.time), stream, raw


def analyse(path):
    print(f"\n=== {path} ===")
    counts = collections.Counter()
    ga_samples = []
    total = 0
    for ts, stream, raw in iter_client_messages(path):
        total += 1
        msg = raw.decode("utf-8", "ignore")
        # préfixe = lettres initiales (commande du protocole)
        head = ""
        for ch in msg:
            if ch.isalpha():
                head += ch
            else:
                break
        counts[head[:4] or "?"] += 1
        if msg.startswith("GA"):
            ga_samples.append((ts, msg, raw.hex()))
    print(f"  {total} messages client->serveur")
    print(f"  préfixes: {dict(counts.most_common(20))}")
    if ga_samples:
        print(f"\n  --- {len(ga_samples)} messages GA (déplacement) ---")
        for ts, msg, hexs in ga_samples[:15]:
            print(f"  [{ts:.3f}] text={msg!r}")
            print(f"            hex ={hexs}")
    else:
        print("  (aucun message GA trouvé dans ce fichier)")
    return total, len(ga_samples)


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return
    if args[0] == "--all":
        folder = args[1] if len(args) > 1 else "data/live"
        files = sorted(glob.glob(os.path.join(folder, "*.pcapng")) +
                       glob.glob(os.path.join(folder, "*.pcap")))
        grand_total = grand_ga = 0
        for f in files:
            try:
                t, g = analyse(f)
                grand_total += t
                grand_ga += g
            except Exception as e:  # noqa: BLE001
                print(f"  ERREUR {f}: {e}")
        print(f"\n==== TOTAL: {grand_total} messages, {grand_ga} GA ====")
    else:
        for f in args:
            analyse(f)


if __name__ == "__main__":
    main()
