#!/usr/bin/env python3
"""Affiche les chaînes voisines autour d'identifiants crypto ciblés dans le SWF
décompressé. En AS2, le constant-pool groupe les chaînes d'une même portée :
les voisins de `getRandomNetworkKey` révèlent souvent l'algo."""
import sys
import zlib

SWF = sys.argv[1] if len(sys.argv) > 1 else r"C:\Users\vip19\loader.swf"
TARGETS = ["getRandomNetworkKey", "RSACrypto", "CRYPTO_METHOD", "CRYPTO_LINK",
           "b64_hmac_md5", "_bUseRsaCrypto", "setKey", "getKey", "aksSend",
           "sendMessage", "checksum", "Aks"]


def load_swf(path: str) -> bytes:
    data = open(path, "rb").read()
    if data[:3] == b"CWS":
        return zlib.decompress(data[8:])
    return data[8:]


def strings(data: bytes, mn: int = 3):
    out, cur, start = [], bytearray(), 0
    for i, b in enumerate(data):
        if 32 <= b < 127:
            if not cur:
                start = i
            cur.append(b)
        else:
            if len(cur) >= mn:
                out.append((start, cur.decode("ascii")))
            cur = bytearray()
    if len(cur) >= mn:
        out.append((start, cur.decode("ascii")))
    return out


def main():
    data = load_swf(SWF)
    strs = strings(data)
    idx = {i: s for i, (_, s) in enumerate(strs)}
    print(f"{len(strs)} chaînes.\n")

    for target in TARGETS:
        positions = [i for i, s in idx.items() if s == target]
        if not positions:
            # recherche partielle
            positions = [i for i, s in idx.items() if target in s][:2]
        for pos in positions[:2]:
            print("=" * 80)
            print(f"VOISINS DE [{target}] (chaîne #{pos})")
            print("=" * 80)
            lo, hi = max(0, pos - 18), min(len(strs), pos + 19)
            for k in range(lo, hi):
                mark = " >>>" if k == pos else "    "
                print(f"{mark} {idx[k]!r}")
            print()


if __name__ == "__main__":
    main()
