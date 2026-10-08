"""Isole LE flux TCP Dofus (celui dont le S->C est du GM/GA0 en clair) à travers
plusieurs fichiers ring-buffer, puis cherche une clé (16/24/32 o) dans son S->C
en clair AVANT le 1er message chiffré C->S.

Le port 443 est pollué par du TLS (Docker, web) : on ne se fie donc PAS au port,
on identifie le flux de jeu par son contenu (messages 'GM|' / 'GA0;' en clair).
"""
from __future__ import annotations
import base64
import collections
import glob
import re
import sys

PORT = 443
DELIM = b"\x00"
B64 = re.compile(r'[A-Za-z0-9+/]{20,}={0,2}')
HEX = re.compile(r'(?<![0-9a-fA-F])[0-9a-fA-F]{32,64}(?![0-9a-fA-F])')


def keyish(txt):
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


def load(paths):
    from scapy.all import IP, Raw, TCP, rdpcap
    pkts = []
    for path in paths:
        try:
            for p in rdpcap(path):
                if TCP in p and Raw in p and IP in p:
                    t = p[TCP]
                    if PORT in (t.sport, t.dport):
                        pkts.append(p)
        except Exception as e:
            print(f"  skip {path}: {e}")
    pkts.sort(key=lambda p: float(p.time))
    return pkts


def run(paths):
    from scapy.all import IP, TCP, Raw
    pkts = load(paths)
    # réassemble par flux orienté (4-tuple), découpe sur \x00
    buffers = collections.defaultdict(bytes)
    # par flux "session" (paire non-orientée) : liste (ts, c2s, msg)
    streams = collections.defaultdict(list)
    for p in pkts:
        ip, t = p[IP], p[TCP]
        c2s = t.dport == PORT
        conn = tuple(sorted([(ip.src, t.sport), (ip.dst, t.dport)]))
        okey = (ip.src, t.sport, ip.dst, t.dport)
        buffers[okey] += bytes(p[Raw].load)
        *complete, remainder = buffers[okey].split(DELIM)
        buffers[okey] = remainder
        for raw in complete:
            if raw:
                streams[conn].append((float(p.time), c2s, raw))

    # identifie le(s) flux de JEU : S->C contient GM| ou GA0;
    print(f"{len(streams)} flux port-443 au total")
    game = []
    for conn, msgs in streams.items():
        s2c_txt = " ".join(r.decode("latin-1") for ts, c2s, r in msgs if not c2s)
        if "GM|" in s2c_txt or "GA0;" in s2c_txt:
            game.append(conn)
    print(f"{len(game)} flux identifiés comme DOFUS (GM/GA0 en clair)\n")

    for conn in game:
        msgs = sorted(streams[conn], key=lambda x: x[0])
        first_enc = next((i for i, (ts, c2s, r) in enumerate(msgs)
                          if c2s and r[:2] == b"\xc3\xb9"), None)
        print(f"=== flux {conn} : {len(msgs)} msgs, 1er chiffré C->S @ index {first_enc} ===")
        # tout le S->C AVANT le 1er chiffré : la clé devrait y être
        window = msgs if first_enc is None else msgs[:first_enc]
        found = False
        for ts, c2s, raw in window:
            if c2s:
                continue
            txt = raw.decode("latin-1")
            hits = keyish(txt)
            if hits:
                found = True
                ascii_ = "".join(c if 32 <= ord(c) < 127 else "." for c in txt)
                print(f"  S->C {ascii_[:60]!r}")
                for h in hits:
                    print(f"      -> {h}")
        # montre aussi les 12 premiers S->C bruts (le handshake d'ouverture)
        print("  --- 12 premiers S->C du flux (handshake) ---")
        shown = 0
        for ts, c2s, raw in msgs:
            if c2s:
                continue
            ascii_ = "".join(c if 32 <= ord(c) < 127 else "." for c in raw.decode("latin-1"))
            print(f"    {ascii_[:70]!r}")
            shown += 1
            if shown >= 12:
                break
        if not found:
            print("  >>> AUCUNE valeur clé (16/24/32o) trouvée en clair avant le chiffrement")
        print()


if __name__ == "__main__":
    args = sys.argv[1:]
    paths = []
    for a in args:
        paths.extend(sorted(glob.glob(a)))
    run(paths)
