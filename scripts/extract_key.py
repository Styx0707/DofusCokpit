#!/usr/bin/env python3
"""Extrait la CLÉ AES de session Dofus Retro depuis la mémoire du client.

Aucune capture réseau : on lit la mémoire des process du jeu, on y retrouve le
CHAMP CRYPTO des enveloppes par sa FORME (IV b64 `…22==` + cipher b64 de taille
multiple de 16, indépendamment de l'encodage latin-1/UTF-16LE et du séparateur),
on récolte les candidats-clés (runs hex/b64 de 16/24/32 o), et on teste chaque
clé en AES-CBC/ECB. Oracle : un bon déchiffrement donne un plaintext très
imprimable + padding PKCS7 valide (et contient le message si connu).

Usage :
  py scripts/extract_key.py            # tous les process "Dofus Retro"
  py scripts/extract_key.py <pid>      # un PID précis
"""
from __future__ import annotations

import base64
import ctypes
import ctypes.wintypes as w
import re
import subprocess
import sys

import pyaes

# Console Windows en cp1252 : les emojis (❌/🔑) et accents font planter print().
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

PROCESS_QUERY_INFORMATION = 0x0400
PROCESS_VM_READ = 0x0010
MEM_COMMIT = 0x1000
PAGE_GUARD = 0x100
READABLE = {0x02, 0x04, 0x20, 0x40}
k32 = ctypes.WinDLL("kernel32", use_last_error=True)


class MBI(ctypes.Structure):
    _fields_ = [("BaseAddress", ctypes.c_void_p), ("AllocationBase", ctypes.c_void_p),
                ("AllocationProtect", w.DWORD), ("PartitionId", w.WORD),
                ("RegionSize", ctypes.c_size_t), ("State", w.DWORD),
                ("Protect", w.DWORD), ("Type", w.DWORD)]


def iter_regions(pid: int):
    h = k32.OpenProcess(PROCESS_QUERY_INFORMATION | PROCESS_VM_READ, False, pid)
    if not h:
        print(f"  (OpenProcess {pid} échoué: {ctypes.get_last_error()})")
        return
    try:
        addr, mbi = 0, MBI()
        while addr < 0x7FFFFFFFFFFF:
            if not k32.VirtualQueryEx(h, ctypes.c_void_p(addr), ctypes.byref(mbi),
                                      ctypes.sizeof(mbi)):
                break
            size, prot = mbi.RegionSize, mbi.Protect & 0xFF
            if (mbi.State == MEM_COMMIT and prot in READABLE
                    and not (mbi.Protect & PAGE_GUARD) and size):
                buf = (ctypes.c_char * size)()
                read = ctypes.c_size_t(0)
                if k32.ReadProcessMemory(h, ctypes.c_void_p(addr), buf, size,
                                         ctypes.byref(read)) and read.value:
                    yield bytes(buf[:read.value])
            addr += size if size else 0x1000
    finally:
        k32.CloseHandle(h)


# Champ crypto, forme distinctive INDÉPENDANTE de la taille du message et du
# séparateur :  IV + [sép] + cipher
#   IV     = base64 de 16 octets  -> 22 chars b64 + "=="  (toujours "==")
#   sép    = 0 à 4 octets non-b64 éventuels (ù = \xc3\xb9, \x00, |, ...)
#   cipher = base64 d'un multiple de 16 octets (AES bloc) -> run b64 >= 22 chars,
#            padding 0/1/2 "=" SELON la longueur (ne PAS exiger "==").
# L'ancien regex figeait le cipher à 278 chars (msg de 208 o) + "==" : il ne
# matchait qu'UNE seule taille de message -> 0 enveloppe dès que la taille change.
IV_B64 = r"[A-Za-z0-9+/]{22}=="
CIPHER_B64 = r"[A-Za-z0-9+/]{22,20000}={0,2}"
FIELD_RE = re.compile(rf"({IV_B64})([^A-Za-z0-9+/]{{0,4}})({CIPHER_B64})")
# message clair juste après le champ (après le séparateur ù / octet(s))
TAIL_RE = re.compile(r"[\x00-\x20\xb9\xf9]{0,3}([A-Za-z0-9|+\-/]{2,32})")
# clés : runs hex (16/24/32 o) ou b64 (16/24/32 o) stockés en texte.
HEX_RE = re.compile(r"(?<![0-9a-fA-F])[0-9a-fA-F]{32,64}(?![0-9a-fA-F])")
B64_RE = re.compile(r"(?<![A-Za-z0-9+/])[A-Za-z0-9+/]{22,44}={0,2}(?![A-Za-z0-9+/])")


def decode_field(iv_b64: str, cipher_run: str):
    """Valide l'enveloppe par sa STRUCTURE, pas par sa taille :
    IV = 16 octets, cipher = multiple de 16 (>= 16).

    Quand le cipher ne finit PAS par du padding (longueur ≡ 0 mod 3), le run
    base64 glouton mord sur le clair qui suit (ex. un message `GM|…` commence
    par des chars base64) : on rogne la queue pour garder le plus grand préfixe
    aligné qui déchiffre en un multiple de 16 octets."""
    try:
        iv = base64.b64decode(iv_b64)
    except Exception:
        return None
    if len(iv) != 16:
        return None
    run = cipher_run.rstrip("=")
    for cut in range(8):                       # tolère jusqu'à 7 chars de débord
        length = len(run) - cut
        if length < 22 or length % 4 == 1:     # 1 mod 4 = base64 invalide
            continue
        try:
            ct = base64.b64decode(run[:length] + "=" * (-length % 4))
        except Exception:
            continue
        if len(ct) >= 16 and len(ct) % 16 == 0:
            return iv, ct                      # cut croissant -> plus long préfixe valide
    return None


def scan(pid: int):
    samples, cands, total = [], set(), 0
    for data in iter_regions(pid):
        total += len(data)
        for enc in ("latin-1", "utf-16-le"):
            try:
                txt = data.decode(enc, errors="ignore")
            except Exception:
                continue
            for m in FIELD_RE.finditer(txt):
                dec = decode_field(m.group(1), m.group(3))
                if dec:
                    tail = TAIL_RE.match(txt, m.end())
                    msg = tail.group(1) if tail else ""
                    samples.append((dec[0], dec[1], msg))
            for m in HEX_RE.finditer(txt):
                h = m.group(0)
                if len(h) in (32, 48, 64):
                    cands.add(bytes.fromhex(h))
            for m in B64_RE.finditer(txt):
                try:
                    s = m.group(0)
                    b = base64.b64decode(s + "=" * (-len(s) % 4))
                    if len(b) in (16, 24, 32):
                        cands.add(b)
                except Exception:
                    pass
    return samples, cands, total


# ── AES bas niveau (pyaes pur-python : pas de backend C dispo). On construit
#    le key-schedule UNE fois par clé (pyaes.AES) et on réutilise l'objet pour
#    tous les blocs/échantillons. ~20 µs/bloc, ~49k blocs/s.
def dec_block(aes, block16: bytes) -> bytes:
    return bytes(aes.decrypt(list(block16)))


def last_block_pkcs7(aes, mode: str, iv: bytes, ct: bytes) -> bool:
    """Oracle RAPIDE : ne déchiffre QUE le dernier bloc (1 AES au lieu de N) et
    teste le padding PKCS7. En CBC le dernier clair = D(ct[-16:]) XOR ct[-32:-16]
    (ou XOR iv si bloc unique) — on n'a pas besoin des blocs précédents."""
    dec = dec_block(aes, ct[-16:])
    if mode == "CBC":
        prev = ct[-32:-16] if len(ct) >= 32 else iv
        dec = bytes(a ^ b for a, b in zip(dec, prev))
    n = dec[-1]
    return 1 <= n <= 16 and dec[-n:] == bytes([n]) * n


def full_decrypt(aes, mode: str, iv: bytes, ct: bytes) -> bytes:
    out, prev = bytearray(), iv
    for i in range(0, len(ct), 16):
        blk = ct[i:i + 16]
        dec = dec_block(aes, blk)
        if mode == "CBC":
            dec = bytes(a ^ b for a, b in zip(dec, prev))
            prev = blk
        out += dec
    return bytes(out)


def printable_ratio(b: bytes) -> float:
    return sum(1 for c in b if 9 <= c <= 13 or 32 <= c <= 126) / len(b)


def pkcs7_ok(b: bytes) -> bool:
    n = b[-1]
    return 1 <= n <= 16 and b[-n:] == bytes([n]) * n


def edge_blocks(aes, mode: str, iv: bytes, ct: bytes):
    """Déchiffre UNIQUEMENT le 1er et le dernier bloc de clair (2 blocs AES).
    CBC : P0 = D(ct[0:16]) XOR iv ; Pn = D(ct[-16:]) XOR ct[-32:-16]. Aucun des
    blocs du milieu n'est requis -> oracle rapide ET indépendant du padding."""
    first = dec_block(aes, ct[:16])
    last = dec_block(aes, ct[-16:])
    if mode == "CBC":
        first = bytes(a ^ b for a, b in zip(first, iv))
        prev = ct[-32:-16] if len(ct) >= 32 else iv
        last = bytes(a ^ b for a, b in zip(last, prev))
    return first, last


def crack(samples, cands):
    uniq = {(s[0], s[1]): s[2] for s in samples}
    samples = [(iv, ct, msg) for (iv, ct), msg in uniq.items()]
    cands = [k for k in cands if len(k) in (16, 24, 32)]
    print(f"Échantillons uniques : {len(samples)} | candidats-clés : {len(cands)}")
    if not samples or not cands:
        return None

    # ORACLE AGNOSTIQUE AU PADDING. Les frames font tous 208 o (taille fixe) :
    # probablement AUCUN PKCS7. On score donc chaque clé par le nombre d'enveloppes
    # (sur une sonde) dont le 1er ET le dernier bloc déchiffré sont « très
    # imprimables » (le protocole Dofus est du texte : GM|, GA0;, …).
    # Bruit : P(un bloc de 16 o aléatoires ait ≥70% d'imprimables) ≈ 1e-5, les deux
    # blocs ≈ 1e-10 — donc MÊME 2 enveloppes validées = signal décisif, pas chance.
    THR = 0.70
    probe = samples[:48]                       # 48 enveloppes suffisent pour trancher
    for mode in ("CBC", "ECB"):
        scored = []
        for key in cands:
            aes = pyaes.AES(key)
            hits = 0
            for iv, ct, _ in probe:
                f, l = edge_blocks(aes, mode, iv, ct)
                if printable_ratio(f) >= THR and printable_ratio(l) >= THR:
                    hits += 1
            if hits >= 2:
                scored.append((hits, key, aes))
        scored.sort(key=lambda x: -x[0])
        if scored:
            top = ", ".join(f"{s}/{len(probe)}" for s, _, _ in scored[:5])
            print(f"  {mode}: {len(scored)} clé(s) au-dessus du bruit — top {top}")
        else:
            print(f"  {mode}: aucune clé ne rend 2 enveloppes imprimables (bruit)")
            continue
        # vérif finale : déchiffrement COMPLET, le clair doit être majoritairement texte
        for hits, key, aes in scored[:10]:
            for iv, ct, msg in samples:
                f, l = edge_blocks(aes, mode, iv, ct)
                if printable_ratio(f) < THR or printable_ratio(l) < THR:
                    continue
                pt = full_decrypt(aes, mode, iv, ct)
                if printable_ratio(pt) >= THR:
                    print("\n" + "=" * 70)
                    print(f"🔑 CLÉ TROUVÉE ({mode})  sonde={hits}/{len(probe)}  "
                          f"imprimable={printable_ratio(pt):.0%}")
                    print("=" * 70)
                    print(f"key hex : {key.hex()}")
                    print(f"key b64 : {base64.b64encode(key).decode()}")
                    print(f"iv  hex : {iv.hex()}")
                    print(f"pkcs7   : {pkcs7_ok(pt)}  (info — padding peut être absent)")
                    print(f"plaintext repr : {pt[:160]!r}")
                    print(f"plaintext hex  : {pt.hex()}")
                    return key
    print("❌ aucune clé candidate ne déchiffre (oracle imprimable 1er+dernier bloc).")
    print("   -> la clé AES n'est pas une chaîne hex/b64 en RAM : PIVOT handshake AS.")
    return None


def dofus_pids():
    out = subprocess.check_output(
        ["powershell", "-Command",
         "Get-Process | Where-Object {$_.ProcessName -match 'Dofus'} | "
         "Sort-Object WorkingSet64 -Descending | ForEach-Object {$_.Id}"],
        text=True)
    return [int(x) for x in out.split()]


if __name__ == "__main__":
    pids = [int(sys.argv[1])] if len(sys.argv) > 1 else dofus_pids()
    all_samples, all_cands = [], set()
    for pid in pids:
        print(f"\n### PID {pid}")
        s, c, total = scan(pid)
        print(f"  lu {total/1024/1024:.0f} Mo | champs crypto: {len(s)} | candidats: {len(c)}")
        all_samples += s
        all_cands |= c

    # Aperçu : quelques enveloppes détectées (pour juger si c'est du vrai crypto
    # ou du base64 aléatoire capté par la forme). msg = clair qui suit le champ.
    uniq = {(iv, ct): msg for iv, ct, msg in all_samples}
    print(f"\n=== {len(uniq)} enveloppes uniques (aperçu des 8 premières) ===")
    for (iv, ct), msg in list(uniq.items())[:8]:
        print(f"  iv={iv.hex()} ct_len={len(ct):>3}o msg={msg!r}")

    print("\n=== CRACK GLOBAL ===")
    crack(all_samples, all_cands)
