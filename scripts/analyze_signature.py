#!/usr/bin/env python3
"""Décompose le CHAMP CRYPTO (304 chars fixe) des enveloppes Dofus Retro.

Le champ crypto semble être 2 tokens base64 collés : [nonce ==][blob].
On mesure les tailles exactes en octets et on inspecte l'entropie / structure
pour deviner l'algo (IV+AES ? RSA ? nonce+MAC ?).
"""
import base64
import os
import re
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
CAP = os.path.join(HERE, "..", "data", "c2s_hex.txt")
SEP = b"\xc3\xb9"


def read_lines():
    with open(CAP, encoding="utf-16") as fh:
        return [ln.strip() for ln in fh if ln.strip()]


def split_crypto(field: str):
    """Coupe le champ crypto sur la 1re fin de padding base64 (== ou =).
    Retourne (token1, token2)."""
    m = re.search(r"={1,2}", field)
    if not m:
        return field, ""
    cut = m.end()
    return field[:cut], field[cut:]


def b64(s):
    try:
        return base64.b64decode(s + "=" * ((4 - len(s) % 4) % 4))
    except Exception:
        return None


def entropy(data: bytes) -> float:
    if not data:
        return 0.0
    c = Counter(data)
    import math
    n = len(data)
    return -sum((v / n) * math.log2(v / n) for v in c.values())


def main():
    lines = read_lines()
    print("=" * 90)
    print("DÉCOMPOSITION DU CHAMP CRYPTO")
    print("=" * 90)

    tok1_lens, tok2_lens = set(), set()
    tok1_bytes_lens, tok2_bytes_lens = set(), set()
    all_tok1, all_tok2 = [], []

    for i, line in enumerate(lines):
        raw = bytes.fromhex(line.split("\t")[-1]).rstrip(b"\x00").rstrip(b"\n")
        parts = [p for p in raw.split(SEP) if p]
        crypto = parts[0].decode("latin-1")
        msg = parts[1].decode("latin-1") if len(parts) > 1 else ""

        t1, t2 = split_crypto(crypto)
        b1, b2 = b64(t1), b64(t2)
        tok1_lens.add(len(t1)); tok2_lens.add(len(t2))
        if b1 is not None:
            tok1_bytes_lens.add(len(b1)); all_tok1.append(b1)
        if b2 is not None:
            tok2_bytes_lens.add(len(b2)); all_tok2.append(b2)

        if i < 4:
            print(f"\nPaquet {i+1}  msg={msg!r}")
            print(f"  token1 = {len(t1)} chars -> {len(b1) if b1 else '?'} octets   {t1}")
            print(f"  token1 hex: {b1.hex() if b1 else '?'}")
            print(f"  token2 = {len(t2)} chars -> {len(b2) if b2 else '?'} octets")
            print(f"  token2 hex[:48]: {b2[:48].hex() if b2 else '?'}")

    print("\n" + "=" * 90)
    print("TAILLES")
    print("=" * 90)
    print(f"token1 (nonce?) : chars={sorted(tok1_lens)}  octets={sorted(tok1_bytes_lens)}")
    print(f"token2 (sig?)   : chars={sorted(tok2_lens)}  octets={sorted(tok2_bytes_lens)}")

    # Entropie : du vrai aléa/chiffré ~8 bits/octet ; du texte ~4-5.
    if all_tok1:
        e1 = sum(entropy(b) for b in all_tok1) / len(all_tok1)
        print(f"\nEntropie moyenne token1 : {e1:.2f} bits/octet "
              f"({'aléatoire/chiffré' if e1 > 7 else 'structuré'})")
    if all_tok2:
        e2 = sum(entropy(b) for b in all_tok2) / len(all_tok2)
        print(f"Entropie moyenne token2 : {e2:.2f} bits/octet "
              f"({'aléatoire/chiffré' if e2 > 7 else 'structuré'})")

    # Octets communs en tête/queue du token2 (en-tête d'algo ? padding fixe ?)
    if len(all_tok2) > 1:
        head_common = 0
        for k in range(min(len(b) for b in all_tok2)):
            if len({b[k] for b in all_tok2}) == 1:
                head_common += 1
            else:
                break
        tail_common = 0
        for k in range(1, min(len(b) for b in all_tok2) + 1):
            if len({b[-k] for b in all_tok2}) == 1:
                tail_common += 1
            else:
                break
        print(f"\ntoken2 : {head_common} octets de tête communs, "
              f"{tail_common} octets de queue communs "
              f"(=> {'champ fixe détecté' if head_common or tail_common else 'tout varie (chiffré/signé)'})")


if __name__ == "__main__":
    main()
