#!/usr/bin/env python3
"""Trouve la CLÉ AES de session en scannant le KEY-SCHEDULE EMPAQUETÉ dans la
mémoire du client (technique findaes/aeskeyfind).

Pourquoi ça marche ici : la sonde `probe_aes` a confirmé des tables AES packées
(S-box, Te0) dans le process -> l'implémentation est native, donc le schedule
étendu (176/208/240 o) est stocké en octets contigus, pas en Array AS boxé.

Principe : l'expansion de clé AES vérifie, pour tout mot NON-core,
    W[i] = W[i-Nk] XOR W[i-1]      (i % Nk != 0, et != 4 pour Nk=8)
soit au niveau octet :  b[k] = b[k-4] XOR b[k-4*Nk].
On calcule C[k] = b[k] ^ b[k-4] ^ b[k-4*Nk] pour TOUTE la région d'un coup via
un XOR de grands entiers (en C sous le capot), puis on cherche les plages de
zéros (= 3 mots non-core consécutifs) à la regex. Chaque candidat est confirmé
par une vraie expansion de clé comparée à la mémoire -> 0 faux positif.
Enfin on valide les clés trouvées en déchiffrant les enveloppes Dofus.

Usage : py scripts/find_aes_schedule.py [pid ...]
"""
from __future__ import annotations

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from extract_key import (FIELD_RE, decode_field, dofus_pids, full_decrypt,  # noqa: E402,F401
                         iter_regions, printable_ratio)
import pyaes  # noqa: E402

SBOX = bytes([
 0x63,0x7c,0x77,0x7b,0xf2,0x6b,0x6f,0xc5,0x30,0x01,0x67,0x2b,0xfe,0xd7,0xab,0x76,
 0xca,0x82,0xc9,0x7d,0xfa,0x59,0x47,0xf0,0xad,0xd4,0xa2,0xaf,0x9c,0xa4,0x72,0xc0,
 0xb7,0xfd,0x93,0x26,0x36,0x3f,0xf7,0xcc,0x34,0xa5,0xe5,0xf1,0x71,0xd8,0x31,0x15,
 0x04,0xc7,0x23,0xc3,0x18,0x96,0x05,0x9a,0x07,0x12,0x80,0xe2,0xeb,0x27,0xb2,0x75,
 0x09,0x83,0x2c,0x1a,0x1b,0x6e,0x5a,0xa0,0x52,0x3b,0xd6,0xb3,0x29,0xe3,0x2f,0x84,
 0x53,0xd1,0x00,0xed,0x20,0xfc,0xb1,0x5b,0x6a,0xcb,0xbe,0x39,0x4a,0x4c,0x58,0xcf,
 0xd0,0xef,0xaa,0xfb,0x43,0x4d,0x33,0x85,0x45,0xf9,0x02,0x7f,0x50,0x3c,0x9f,0xa8,
 0x51,0xa3,0x40,0x8f,0x92,0x9d,0x38,0xf5,0xbc,0xb6,0xda,0x21,0x10,0xff,0xf3,0xd2,
 0xcd,0x0c,0x13,0xec,0x5f,0x97,0x44,0x17,0xc4,0xa7,0x7e,0x3d,0x64,0x5d,0x19,0x73,
 0x60,0x81,0x4f,0xdc,0x22,0x2a,0x90,0x88,0x46,0xee,0xb8,0x14,0xde,0x5e,0x0b,0xdb,
 0xe0,0x32,0x3a,0x0a,0x49,0x06,0x24,0x5c,0xc2,0xd3,0xac,0x62,0x91,0x95,0xe4,0x79,
 0xe7,0xc8,0x37,0x6d,0x8d,0xd5,0x4e,0xa9,0x6c,0x56,0xf4,0xea,0x65,0x7a,0xae,0x08,
 0xba,0x78,0x25,0x2e,0x1c,0xa6,0xb4,0xc6,0xe8,0xdd,0x74,0x1f,0x4b,0xbd,0x8b,0x8a,
 0x70,0x3e,0xb5,0x66,0x48,0x03,0xf6,0x0e,0x61,0x35,0x57,0xb9,0x86,0xc1,0x1d,0x9e,
 0xe1,0xf8,0x98,0x11,0x69,0xd9,0x8e,0x94,0x9b,0x1e,0x87,0xe9,0xce,0x55,0x28,0xdf,
 0x8c,0xa1,0x89,0x0d,0xbf,0xe6,0x42,0x68,0x41,0x99,0x2d,0x0f,0xb0,0x54,0xbb,0x16])
RCON = [0x00,0x01,0x02,0x04,0x08,0x10,0x20,0x40,0x80,0x1b,0x36,0x6c,0xd8,0xab,0x4d]


def expand(key: bytes) -> bytes:
    """Schedule de CHIFFREMENT AES (176/208/240 o), layout standard."""
    nk = len(key) // 4
    nr = nk + 6
    total = 4 * (nr + 1)
    w = [list(key[4 * i:4 * i + 4]) for i in range(nk)]
    for i in range(nk, total):
        t = list(w[i - 1])
        if i % nk == 0:
            t = t[1:] + t[:1]                      # RotWord
            t = [SBOX[b] for b in t]               # SubWord
            t[0] ^= RCON[i // nk]
        elif nk > 6 and i % nk == 4:
            t = [SBOX[b] for b in t]               # SubWord (AES-256)
        w.append([w[i - nk][j] ^ t[j] for j in range(4)])
    return bytes(b for word in w for b in word)


# Nk -> (décalage octet 4*Nk, offset du 1er mot non-core 4*(Nk+1), longueur schedule)
PARAMS = {
    4: (16, 20, 176),
    6: (24, 28, 208),
    8: (32, 36, 240),
}
# Plage de zéros ISOLÉE (bornée par du non-zéro) = 3 mots non-core entre deux
# mots core : c'est la signature d'un vrai schedule. Les lookaround excluent les
# grandes zones nulles (sinon des millions de matches qui écroulent le scan).
ZERO_RUN = re.compile(rb"(?<!\x00)\x00{12,24}(?!\x00)")
CHUNK = 16 * 1024 * 1024
OVERLAP = 512


def find_in_chunk(buf: bytes, keys: set):
    """buf = tranche mémoire ; remplit `keys` avec les clés dont le schedule
    complet est présent en mémoire."""
    big = int.from_bytes(buf, "little")
    n = len(buf)
    for nk, (shift, qoff, slen) in PARAMS.items():
        # C[k] = buf[k] ^ buf[k-4] ^ buf[k-shift]  (0 <=> relation non-core vérifiée)
        d = big ^ (big << 32) ^ (big << (8 * shift))
        c = d.to_bytes(n + shift + 1, "little")[:n]
        for m in ZERO_RUN.finditer(c):
            s, e = m.start(), m.end()
            for q in range(s, e - 11):             # alignements possibles du mot non-core
                p = q - qoff
                if p < 0 or p + slen > n:
                    continue
                key = buf[p:p + 4 * nk]
                if len(set(key)) < 6:              # clé plate (zone nulle) -> skip
                    continue
                if expand(key) == buf[p:p + slen]:
                    keys.add(key)


def collect(pid: int):
    keys: set = set()
    samples = []
    total = 0
    for data in iter_regions(pid):
        total += len(data)
        # 1) schedules AES (par tranches pour borner la RAM des grands entiers)
        step = CHUNK - OVERLAP
        for off in range(0, len(data), step):
            find_in_chunk(data[off:off + CHUNK], keys)
        # 2) enveloppes Dofus (pour valider les clés) — latin-1 + utf-16-le
        for enc in ("latin-1", "utf-16-le"):
            txt = data.decode(enc, errors="ignore")
            for mt in FIELD_RE.finditer(txt):
                dec = decode_field(mt.group(1), mt.group(3))
                if dec:
                    samples.append(dec)
    return keys, samples, total


def cbc_decrypt(key, iv, ct):
    aes = pyaes.AES(key)
    out, prev = bytearray(), iv
    for i in range(0, len(ct), 16):
        blk = ct[i:i + 16]
        dec = bytes(aes.decrypt(list(blk)))
        out += bytes(a ^ b for a, b in zip(dec, prev))
        prev = blk
    return bytes(out)


def validate(keys, samples):
    uniq = {(iv, ct) for iv, ct in samples}
    samples = list(uniq)
    print(f"\n=== VALIDATION : {len(keys)} clé(s) AES vs {len(samples)} enveloppes ===")
    if not keys:
        print("Aucun key-schedule AES empaqueté trouvé en mémoire.")
        return None
    for key in sorted(keys):
        hits, shown = 0, None
        for iv, ct in samples[:40]:
            pt = cbc_decrypt(key, iv, ct)
            if printable_ratio(pt) >= 0.85:
                hits += 1
                shown = shown or pt
        tag = f"{hits}/{min(40, len(samples))}" if samples else "n/a"
        print(f"  key={key.hex()}  Dofus-CBC imprimable {tag}"
              + (f"  ex={shown[:48]!r}" if shown else ""))
        if samples and hits >= max(3, min(40, len(samples)) // 3):
            print("\n" + "=" * 70)
            print(f"🔑 CLÉ DE SESSION DOFUS = {key.hex()}  ({len(key)} o)")
            print("=" * 70)
            return key
    print("\n-> Des schedules AES existent mais aucun ne déchiffre les enveloppes "
          "Dofus (probablement des clés TLS/Chromium). La clé jeu n'est pas packée.")
    return None


if __name__ == "__main__":
    pids = [int(x) for x in sys.argv[1:]] or dofus_pids()
    all_keys, all_samples = set(), []
    for pid in pids:
        print(f"### PID {pid}")
        k, s, total = collect(pid)
        print(f"  lu {total/1024/1024:.0f} Mo | schedules AES: {len(k)} | enveloppes: {len(s)}")
        all_keys |= k
        all_samples += s
    validate(all_keys, all_samples)
