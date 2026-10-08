#!/usr/bin/env python3
"""Cherche les fonctions crypto dans les .as obfusqués et imprime leur contexte."""
import glob
import os

ROOT = os.path.join(os.path.dirname(__file__), "..", "data", "ffdec_full",
                    "scripts", "__Packages", "dofus")

TERMS = ["getRandomNetworkKey", "onPacketSent", "applyPacketToSend",
         "RSACrypto", "CRYPTO_METHOD", "CRYPTO_LINK", "b64_hmac_md5", "b64_md5",
         "connexionKey", "fromCharCode", "\\u00f9", "rsa", "Rsa", "encrypt",
         "setPublicKey", "getRandomNetwork"]


def main():
    files = glob.glob(os.path.join(ROOT, "**", "*.as"), recursive=True)
    for f in files:
        try:
            lines = open(f, encoding="utf-8", errors="replace").read().splitlines()
        except OSError:
            continue
        hits = []
        for i, ln in enumerate(lines):
            for t in TERMS:
                if t in ln:
                    hits.append((i, t))
                    break
        if hits:
            print("#" * 90)
            print(f"FICHIER: {os.path.relpath(f, ROOT)}  ({len(lines)} lignes)")
            print("#" * 90)
            for i, t in hits[:60]:
                print(f"  L{i+1:>5} [{t}]  {lines[i].strip()[:110]}")


if __name__ == "__main__":
    main()
