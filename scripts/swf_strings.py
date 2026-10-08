#!/usr/bin/env python3
"""Décompresse un SWF (CWS/zlib) et extrait les chaînes ASCII, puis cherche
des indices de crypto (AES, base64, hash, noms de fonctions de signature)."""
import re
import sys
import zlib

SWF = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\vip19\loader.swf"


def load_swf(path: str) -> bytes:
    data = open(path, "rb").read()
    sig = data[:3]
    if sig == b"CWS":      # zlib compressé
        return b"FWS" + data[3:8] + zlib.decompress(data[8:])
    if sig == b"ZWS":      # LZMA
        import lzma
        return data  # on ne gère pas LZMA ici
    return data            # FWS non compressé


def strings(data: bytes, mn: int = 4):
    out, cur = [], bytearray()
    for b in data:
        if 32 <= b < 127:
            cur.append(b)
        else:
            if len(cur) >= mn:
                out.append(cur.decode("ascii"))
            cur = bytearray()
    if len(cur) >= mn:
        out.append(cur.decode("ascii"))
    return out


def main():
    data = load_swf(SWF)
    print(f"SWF décompressé : {len(data)} octets")
    strs = strings(data)
    print(f"Chaînes ASCII (>=4) : {len(strs)}")

    # Alphabet base64 (standard) -> indice d'encodage custom
    b64alpha = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
    for s in strs:
        if b64alpha[:40] in s or "+/" in s and len(s) > 40:
            print(f"\n[B64 ALPHABET?] {s[:120]}")

    keywords = ["aes", "rijndael", "sbox", "s-box", "cipher", "crypt", "encrypt",
                "decrypt", "md5", "sha", "hmac", "rsa", "sign", "signature",
                "key", "secret", "nonce", "random", "base64", "checksum",
                "blowfish", "des", "cbc", "iv", "pad", "pkcs"]
    hits = {}
    low = [(s, s.lower()) for s in strs]
    for s, sl in low:
        for kw in keywords:
            if kw in sl:
                hits.setdefault(kw, set()).add(s)

    print("\n" + "=" * 80)
    print("MOTS-CLÉS CRYPTO TROUVÉS")
    print("=" * 80)
    for kw in keywords:
        if kw in hits:
            vals = sorted(hits[kw])[:12]
            print(f"\n[{kw}] ({len(hits[kw])} chaînes)")
            for v in vals:
                print(f"    {v[:100]}")


if __name__ == "__main__":
    main()
