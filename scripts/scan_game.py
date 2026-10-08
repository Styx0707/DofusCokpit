"""Rejoue une capture .pcap/.pcapng et affiche les messages Dofus en CLAIR,
en ordre chronologique et horodatés — outil de RECONNAISSANCE de protocole.

Contrairement à ``parse_pcap`` (qui réassemble par flux et par n° de séquence,
donc perd l'ordre global), ce script **rejoue** exactement la logique du sniffer
live : buffer par flux TCP, découpe sur l'octet nul, et livre chaque message
dans l'ordre d'arrivée des paquets. C'est ce qu'il faut pour corréler un
évènement de jeu (changement de map, apparition/repop d'un groupe) au code de
message qui apparaît à cet instant.

Deux modes :
  (défaut)   fil chronologique brut + histogramme des codes + 1 exemple/code.
  --groups   suit la map courante (GDM) et affiche les GROUPES DE MONSTRES
             décodés (GM), avec leurs IDs de monstres + niveaux, par map.
             Sert à identifier l'ID d'un monstre (ex. Bambouto Divin) et à
             repérer les repops.

Usage :
    python -m scripts.scan_game data/pandala.pcapng [options]

Options :
    --groups        mode groupes de monstres par map (décodé)
    --port N        ne garde que les flux impliquant ce port (déf. 443)
    --dir s2c|c2s|both  sens à afficher (déf. s2c : serveur -> client)
    --code A,B,GDM  n'affiche que ces codes (préfixe alpha du message)
    --needle TXT    n'affiche que les messages contenant TXT (ex: un id monstre)
    --limit N       n'affiche que les N premiers messages (déf. 0 = tous)
    --min-ratio R   part d'octets imprimables mini pour juger un flux « texte »
                    (déf. 0.60 ; écarte les vrais flux TLS binaires sur 443)
"""
from __future__ import annotations

import collections
import re
import string
import sys
from scapy.all import IP, Raw, TCP, rdpcap

from app.network import protocol

PRINTABLE = set(bytes(string.printable, "ascii"))
HEADER_RE = re.compile(r"^[A-Za-z]{1,3}")
DELIMITER = b"\x00"


def parse_args(argv):
    opts = {
        "path": "data/pandala.pcapng", "port": 443, "dir": "s2c",
        "codes": None, "needle": None, "limit": 0, "min_ratio": 0.60,
        "groups": False,
    }
    rest = argv[1:]
    i = 0
    positional_seen = False
    while i < len(rest):
        tok = rest[i]
        if tok == "--groups":
            opts["groups"] = True; i += 1
        elif tok == "--port" and i + 1 < len(rest):
            opts["port"] = int(rest[i + 1]); i += 2
        elif tok == "--dir" and i + 1 < len(rest):
            opts["dir"] = rest[i + 1]; i += 2
        elif tok == "--code" and i + 1 < len(rest):
            opts["codes"] = [c.strip() for c in rest[i + 1].split(",") if c.strip()]
            i += 2
        elif tok == "--needle" and i + 1 < len(rest):
            opts["needle"] = rest[i + 1]; i += 2
        elif tok == "--limit" and i + 1 < len(rest):
            opts["limit"] = int(rest[i + 1]); i += 2
        elif tok == "--min-ratio" and i + 1 < len(rest):
            opts["min_ratio"] = float(rest[i + 1]); i += 2
        elif not tok.startswith("--") and not positional_seen:
            opts["path"] = tok; positional_seen = True; i += 1
        else:
            i += 1
    return opts


def code_of(txt: str) -> str:
    m = HEADER_RE.match(txt)
    return m.group(0) if m else "?"


def keep_direction(sport: int, dport: int, port: int, want: str) -> bool:
    if want == "both":
        return True
    server_to_client = (sport == port)  # serveur émet depuis le port de jeu
    return server_to_client if want == "s2c" else (not server_to_client)


def replay(pkts, opts):
    """Rejoue les paquets en ordre chronologique -> liste (t_rel, dirtag, code, txt)."""
    port = opts["port"]
    # Tri par horodatage de capture : c'est l'ordre réel des évènements.
    pkts = sorted((p for p in pkts if TCP in p and Raw in p and IP in p),
                  key=lambda p: float(p.time))
    if not pkts:
        return []
    t0 = float(pkts[0].time)

    buffers: dict = collections.defaultdict(bytes)
    out = []
    for p in pkts:
        ip, tcp = p[IP], p[TCP]
        if port not in (tcp.sport, tcp.dport):
            continue
        if not keep_direction(tcp.sport, tcp.dport, port, opts["dir"]):
            continue
        key = (ip.src, tcp.sport, ip.dst, tcp.dport)
        buffers[key] += bytes(p[Raw].load)
        *complete, remainder = buffers[key].split(DELIMITER)
        buffers[key] = remainder
        t_rel = float(p.time) - t0
        dirtag = "s2c" if tcp.sport == port else "c2s"
        for raw in complete:
            if not raw:
                continue
            ratio = sum(1 for c in raw if c in PRINTABLE) / len(raw)
            if ratio < opts["min_ratio"]:
                continue  # segment TLS binaire probable
            txt = raw.decode("utf-8", "replace").strip()
            if txt:
                out.append((t_rel, dirtag, code_of(txt), txt))
    return out


def run_groups(msgs):
    """Suit la map courante (GDM) et affiche les groupes de monstres (GM)."""
    current_map = None
    per_map = collections.defaultdict(collections.Counter)  # map -> Counter(monster_id)
    print("  (t+temps ; map suivie via GDM ; groupes via GM, id négatif)")
    for t_rel, _dir, code, txt in msgs:
        if code == "GDM":
            current_map = protocol.parse_map_change(txt)
            print(f"\n== t+{t_rel:7.3f}  MAP {current_map} ==")
            continue
        if code == "GM":
            for actor in protocol.parse_map_actors(txt):
                if actor["op"] == "remove":
                    print(f"  t+{t_rel:7.3f}  map {current_map}  RETRAIT groupe {actor['group_id']}")
                    continue
                compo = ", ".join(
                    f"{protocol.MONSTER_NAMES.get(m['id'], m['id'])}(niv {m['level']})"
                    for m in actor["monsters"]
                )
                target = any(m["id"] == protocol.BAMBOUTO_SACRE_ID
                             for m in actor["monsters"])
                flag = "  <<< CIBLE" if target else ""
                print(f"  t+{t_rel:7.3f}  map {current_map}  cell {actor['cell']:>4} "
                      f"groupe {actor['group_id']:>3} : {compo}{flag}")
                for m in actor["monsters"]:
                    per_map[current_map][m["id"]] += 1

    print("\n##### MONSTRES VUS PAR MAP (id: nb d'apparitions) #####")
    for mp in sorted(per_map, key=lambda x: (x is None, x)):
        counts = ", ".join(f"{mid}×{n}" for mid, n in per_map[mp].most_common())
        print(f"  map {mp} : {counts}")


def run_raw(msgs, opts):
    """Fil chronologique brut + histogramme + exemples (mode reconnaissance)."""
    shown = 0
    for t_rel, dirtag, code, txt in msgs:
        if opts["codes"] is not None and not any(txt.startswith(c) for c in opts["codes"]):
            continue
        if opts["needle"] is not None and opts["needle"] not in txt:
            continue
        print(f"  t+{t_rel:7.3f}  [{code:<3}] {dirtag}  {txt[:200]}")
        shown += 1
        if opts["limit"] and shown >= opts["limit"]:
            print(f"  … (limite {opts['limit']} atteinte)")
            break

    codes = collections.Counter(code for _, _, code, _ in msgs)
    print(f"\n##### CODES rencontrés ({len(msgs)} messages, dir={opts['dir']}) #####")
    for code, n in codes.most_common(50):
        print(f"  {code:<4} : {n}")

    print("\n##### 1 EXEMPLE PAR CODE #####")
    example = {}
    for _, _, code, txt in msgs:
        example.setdefault(code, txt)
    for code in sorted(example):
        print(f"  {code:<4} | {example[code][:120]!r}")


def main():
    opts = parse_args(sys.argv)
    print(f"Lecture {opts['path']} (port={opts['port']}, dir={opts['dir']}, "
          f"mode={'groupes' if opts['groups'] else 'brut'}, "
          f"code={opts['codes'] or 'tous'}, needle={opts['needle']!r})")
    msgs = replay(rdpcap(opts["path"]), opts)
    if not msgs:
        print("Aucun message texte. Bon port ? Perso en jeu pendant la capture ?")
        return
    if opts["groups"]:
        run_groups(msgs)
    else:
        run_raw(msgs, opts)


if __name__ == "__main__":
    main()
