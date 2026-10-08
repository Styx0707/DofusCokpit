#!/usr/bin/env python3
"""Extrait la région de la fonction d'envoi + les constantes crypto (RSA modulus,
séparateur ù, longues chaînes hex/b64) de la classe réseau obfusquée."""
import os
import re

F = os.path.join(os.path.dirname(__file__), "..", "data", "ffdec_full",
                 "scripts", "__Packages", "dofus", "%16%02%11", "%15%1C%04.as")

lines = open(F, encoding="utf-8", errors="replace").read().splitlines()
print(f"{len(lines)} lignes\n")

# 1) Région autour de .send(  (L1433)
print("=" * 90)
print("RÉGION SEND (L1400-1470)")
print("=" * 90)
for i in range(1399, min(1470, len(lines))):
    print(f"{i+1:>5}: {lines[i].rstrip()[:140]}")

# 2) Toutes les longues constantes (RSA modulus/exponent, clés) : >= 40 chars hex/b64
print("\n" + "=" * 90)
print("LONGUES CONSTANTES (clés RSA ? modulus ?)")
print("=" * 90)
seen = set()
for i, ln in enumerate(lines):
    for m in re.findall(r'"([A-Za-z0-9+/=]{40,})"', ln):
        if m not in seen:
            seen.add(m)
            print(f"L{i+1}: ({len(m)}) {m[:120]}")
    for m in re.findall(r'"([0-9a-fA-F]{40,})"', ln):
        if m not in seen:
            seen.add(m)
            print(f"L{i+1}: HEX({len(m)}) {m[:120]}")

# 3) Le séparateur ù (0xF9) et les occurrences de "10001" (exposant RSA classique)
print("\n" + "=" * 90)
print("SÉPARATEUR ù / EXPOSANT RSA 10001 / mots crypto")
print("=" * 90)
for i, ln in enumerate(lines):
    if "ù" in ln or "\\xf9" in ln or "\\u00f9" in ln:
        print(f"L{i+1} [ù]: {ln.strip()[:130]}")
    if "10001" in ln:
        print(f"L{i+1} [10001]: {ln.strip()[:130]}")
    if "setPublic" in ln or "RSAKey" in ln or "modulus" in ln.lower():
        print(f"L{i+1} [rsa]: {ln.strip()[:130]}")
