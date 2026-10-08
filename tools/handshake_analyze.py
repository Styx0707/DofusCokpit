#!/usr/bin/env python3
"""Isole le flux de HANDSHAKE Dofus Retro dans un PCAP — PAR CONTENU, pas par
port (le 443 est pollué par du TLS web). Objectif : voir l'échange de clé C->S.

On réassemble TOUS les flux TCP (les deux sens), on jette le TLS/HTTP, et on
garde les flux « Dofus » (messages ASCII à préfixes connus, ou présence de
l'octet de chiffrement 0xC3B9 = « ù »). Pour chaque flux Dofus on imprime la
timeline chronologique bidirectionnelle, en mettant en évidence :
  - le message `HC<connexionKey>` (serveur->client, EN CLAIR) ;
  - `CRYPTO_METHOD` / négociation ;
  - le 1er message chiffré C->S (préfixe 0xC3B9) et CE QUI LE PRÉCÈDE
    (c'est là que la clé réseau est livrée).

Usage : py tools/handshake_analyze.py <capture.pcapng> [...]
"""
from __future__ import annotations

import collections
import sys

DELIM = b"\x00"
ENC_PREFIX = b"\xc3\xb9"          # « ù » : préfixe des messages chiffrés C->S
# Préfixes de messages Dofus Retro EN CLAIR (connexion + jeu), pour identifier le flux.
DOFUS_PREFIXES = (b"HC", b"HG", b"HQ", b"AT", b"Ad", b"Af", b"Ak", b"Ax", b"AX",
                  b"Ak", b"GM", b"GA", b"GDM", b"ALK", b"ASK", b"EL", b"GTS",
                  b"Am", b"AV", b"AF", b"AN", b"BN", b"Ta")
KEY_HINTS = (b"HC", b"CRYPTO", b"connexionKey")


def is_tls_or_http(first: bytes) -> bool:
    if first[:1] in (b"\x16", b"\x14", b"\x15", b"\x17") and first[1:2] == b"\x03":
        return True                                   # record TLS
    return first[:4] in (b"GET ", b"POST", b"HEAD", b"PUT ") or first[:2] == b"\x17\x03"


def ascii_(raw: bytes, n: int = 90) -> str:
    return "".join(chr(c) if 32 <= c < 127 else "." for c in raw[:n])


def is_private(ip: str) -> bool:
    return (ip.startswith("192.168.") or ip.startswith("10.")
            or ip.startswith("127.")
            or any(ip.startswith(f"172.{x}.") for x in range(16, 32)))


def run(path: str) -> None:
    from scapy.all import IP, Raw, TCP, rdpcap

    pkts = [p for p in rdpcap(path) if TCP in p and Raw in p and IP in p]
    pkts.sort(key=lambda p: float(p.time))

    # réassemblage par flux ORIENTÉ (src,sport -> dst,dport), découpe sur \x00
    buffers: dict = collections.defaultdict(bytes)
    first_bytes: dict = {}
    # messages groupés par CONNEXION (paire non orientée)
    conns: dict = collections.defaultdict(list)       # conn -> [(ts, okey, msg)]
    for p in pkts:
        ip, t = p[IP], p[TCP]
        okey = (ip.src, t.sport, ip.dst, t.dport)
        load = bytes(p[Raw].load)
        if okey not in first_bytes:
            first_bytes[okey] = load[:8]
        buffers[okey] += load
        *complete, remainder = buffers[okey].split(DELIM)
        buffers[okey] = remainder
        conn = tuple(sorted([(ip.src, t.sport), (ip.dst, t.dport)]))
        for raw in complete:
            if raw:
                conns[conn].append((float(p.time), okey, raw))

    print(f"\n######## {path} — {len(conns)} connexions TCP ########")
    found = 0
    for conn, msgs in conns.items():
        okeys = {ok for _, ok, _ in msgs}
        if any(is_tls_or_http(first_bytes.get(ok, b"")) for ok in okeys):
            continue
        blob = b"\x00".join(m for _, _, m in msgs)
        dofus = any(m.startswith(DOFUS_PREFIXES) for _, _, m in msgs) or ENC_PREFIX in blob
        if not dofus:
            continue
        found += 1
        enc_first = next((i for i, (_, _, m) in enumerate(msgs) if m.startswith(ENC_PREFIX)), None)
        has_hc = any(m.startswith(b"HC") for _, _, m in msgs)
        print(f"\n=== FLUX DOFUS {conn}  ({len(msgs)} msgs, "
              f"HC={'oui' if has_hc else 'non'}, 1er chiffré C->S @ "
              f"{enc_first if enc_first is not None else '—'}) ===")
        # fenêtre : du début jusqu'à quelques messages après le 1er chiffré
        end = (enc_first + 3) if enc_first is not None else min(len(msgs), 40)
        for i, (ts, ok, m) in enumerate(msgs[:end]):
            # sens : le client est l'IP privée (LAN) ; sinon on retombe sur le HC.
            d = "C->S" if is_private(ok[0]) else "S->C"
            enc = m.startswith(ENC_PREFIX)
            flag = ""
            if i == enc_first:
                flag = "  <<<<< 1er CHIFFRÉ C->S"
            elif enc:
                flag = "  [chiffré]"
            elif any(h in m for h in KEY_HINTS):
                flag = "  <<< clé/handshake ?"
            print(f"  [{i:3}] {d} len={len(m):>4}{flag}  {ascii_(m)!r}")
            if m.startswith(b"HC"):
                print(f"        connexionKey = {m[2:].decode('latin-1')!r}")
    if not found:
        print("  (aucun flux Dofus identifié — capture sans la session de connexion ?)")


if __name__ == "__main__":
    for f in sys.argv[1:]:
        run(f)
