"""Décode les JETS (effets réels) des items équipés d'un ASK + libellés wiki.

Pour chaque item porté : affiche les effets bruts (id, min, max en déc) et les
lignes de stats texte du wiki (data/details/<gid>.json) pour caler le mapping.

Usage : python -m scripts.decode_jets <capture.pcapng>
"""
from __future__ import annotations

import collections
import json
import os
import sys
from scapy.all import IP, Raw, TCP, rdpcap

from app.network.protocol import EQUIP_SLOTS


def parse_effects(stats: str):
    out = []
    for eff in stats.split(","):
        if not eff.strip():
            continue
        p = eff.split("#")
        try:
            eid = int(p[0], 16)
        except (ValueError, IndexError):
            continue
        mn = int(p[1], 16) if len(p) > 1 and p[1] else 0
        mx = int(p[2], 16) if len(p) > 2 and p[2] else 0
        out.append((eid, mn, mx, eff))
    return out


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "data/inv_styxh.pcapng"
    names = {int(x["id"]): x["name"] for x in json.load(open("data/items_all.json", encoding="utf-8"))}

    flows = collections.defaultdict(dict)
    for p in rdpcap(path):
        if TCP in p and Raw in p and IP in p:
            t = p[TCP];
            pl = bytes(p[Raw].load)
            if pl:
                flows[(p[IP].src, t.sport, p[IP].dst, t.dport)][t.seq] = pl
    ask = ""
    for v in flows.values():
        data = b"".join(v[s] for s in sorted(v)).decode("utf-8", "replace")
        for m in data.split("\x00"):
            if m.startswith("ASK") and len(m) > len(ask):
                ask = m

    body = "|".join(ask.split("|")[10:])
    for it in body.split(";"):
        f = it.split("~")
        if len(f) < 5 or not f[3].strip():
            continue
        slot = int(f[3], 16)
        if slot not in EQUIP_SLOTS:
            continue
        gid = int(f[1], 16)
        print(f"\n### slot {slot} {EQUIP_SLOTS[slot]} : {names.get(gid, gid)} (gid {gid})")
        print("  effets bruts :", [(hex(e[0]), e[0], e[1], e[2]) for e in parse_effects(f[4])])
        det = os.path.join("data/details", f"{gid}.json")
        if os.path.exists(det):
            st = json.load(open(det, encoding="utf-8")).get("stats", [])
            print("  wiki stats   :", st)


if __name__ == "__main__":
    main()
