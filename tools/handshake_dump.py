"""Cherche la LIVRAISON de la clé de chiffrement dans le handshake en clair.

Hypothèse : le serveur (sens serveur->client, EN CLAIR) envoie la clé/seed AES au
client pendant l'ouverture de session, AVANT le 1er message chiffré client->serveur
(préfixe 'ù' = 0xC3B9). Si c'est le cas, la clé est dans la capture, en clair.

Ce script rejoue les 2 sens sur port 443 (null-framing), en ordre chronologique,
et affiche tout jusqu'au 1er message chiffré C->S inclus — c'est la fenêtre où la
clé doit apparaître. Met en évidence les valeurs qui ressemblent à une clé
(hex/base64 de 16/24/32 octets).
"""
from __future__ import annotations
import base64
import collections
import re
import sys

PORT = 443
DELIM = b"\x00"
B64 = re.compile(r'[A-Za-z0-9+/]{20,}={0,2}')
HEX = re.compile(r'\b[0-9a-fA-F]{32,64}\b')


def keyish(txt):
    """Repère des chaînes qui pourraient coder 16/24/32 octets (clé AES)."""
    hits = []
    for m in B64.finditer(txt):
        s = m.group()
        try:
            n = len(base64.b64decode(s + "=" * (-len(s) % 4)))
            if n in (16, 24, 32):
                hits.append(f"b64[{n}o]={s}")
        except Exception:
            pass
    for m in HEX.finditer(txt):
        if len(m.group()) in (32, 48, 64):
            hits.append(f"hex[{len(m.group())//2}o]={m.group()}")
    return hits


def run(path):
    from scapy.all import IP, Raw, TCP, rdpcap
    pkts = [p for p in rdpcap(path) if TCP in p and Raw in p and IP in p]
    pkts.sort(key=lambda p: float(p.time))
    buffers = collections.defaultdict(bytes)
    timeline = []
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
            if raw:
                timeline.append((float(p.time), c2s, raw))

    print(f"\n######## {path} — {len(timeline)} messages port 443 ########")
    first_enc = None
    for i, (ts, c2s, raw) in enumerate(timeline):
        enc = raw[:2] == b"\xc3\xb9"  # préfixe 'ù'
        if c2s and enc and first_enc is None:
            first_enc = i
    # fenêtre : tout jusqu'au 1er chiffré C->S (+ quelques-uns après)
    end = (first_enc + 2) if first_enc is not None else min(len(timeline), 60)
    for i, (ts, c2s, raw) in enumerate(timeline[:end]):
        txt = "".join(c if 32 <= ord(c) < 127 else "." for c in raw.decode("latin-1"))
        enc = raw[:2] == b"\xc3\xb9"
        d = "C->S" if c2s else "S->C"
        flag = " <<< 1er CHIFFRE" if i == first_enc else (" [chiffre]" if enc else "")
        print(f"[{i:3}] {d}{flag} {txt[:76]!r}")
        for k in keyish(txt):
            print(f"        KEY? {k}")
    if first_enc is None:
        print("  (aucun message chiffré C->S dans ce fichier — pas le début de session)")


if __name__ == "__main__":
    for f in sys.argv[1:]:
        run(f)
