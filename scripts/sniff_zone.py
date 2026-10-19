r"""Sniffer de ZONE : catalogue maps / monstres / archimonstres d'une sous-zone.

Rejoue un flux Dofus Retro décodé (voir app.network.protocol) et agrège, pour
chaque map de la zone ciblée, les monstres aperçus (id, nom, niveaux) + le flag
archimonstre (protocol.ARCHI_IDS).

Sources (par ordre de priorité) :
  --pcap FICHIER   une ou plusieurs captures .pcap/.pcapng (messages COMPLETS)
  --jsonl FICHIER  un dump data/live_feed.jsonl (produit par scripts/frida_live.py)
                   NB : le feed tronque chaque message à 300 car. -> un GROS GM
                   peut perdre des groupes en fin de ligne. Préfère --pcap ou
                   --watch (live) pour un catalogue exhaustif.
  (défaut)         data/live_feed.jsonl

Exemples :
  py scripts/sniff_zone.py                      # Grobe, depuis live_feed.jsonl
  py scripts/sniff_zone.py --zone "Grobe"       # idem, explicite
  py scripts/sniff_zone.py --pcap data/pandala.pcapng --zone Pandala
  py scripts/sniff_zone.py --watch 2            # suit live_feed.jsonl en continu
  py scripts/sniff_zone.py --zone "" --json data/zones_all.json   # toutes zones
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from typing import Iterator, List, Tuple

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

from app.core.zone_sniffer import ZoneSniffer  # noqa: E402
from app.network import protocol  # noqa: E402

LIVE_FEED = os.path.join(ROOT, "data", "live_feed.jsonl")


def iter_jsonl(path: str, start: int = 0) -> Tuple[List[Tuple[str, str]], int]:
    """Lit les lignes de ``path`` à partir de l'octet ``start`` -> (messages, offset).

    Ne garde que le sens serveur->client (``dir == "S->C"``) et le champ ``raw``.
    Retourne aussi le nouvel offset pour un suivi incrémental (--watch)."""
    msgs: List[Tuple[str, str]] = []
    with open(path, "rb") as fh:
        fh.seek(start)
        data = fh.read()
        offset = fh.tell()
    text = data.decode("utf-8", "ignore")
    # Ne traite que les lignes complètes (terminées par \n) ; garde le reste pour
    # le prochain tour en reculant l'offset jusqu'au dernier \n.
    last_nl = text.rfind("\n")
    if last_nl < 0:
        return [], start
    offset = start + len(text[: last_nl + 1].encode("utf-8"))
    for line in text[: last_nl + 1].splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            o = json.loads(line)
        except ValueError:
            continue
        if o.get("dir") != "S->C":
            continue
        raw = o.get("raw")
        if raw:
            msgs.append((o.get("stream", "?"), raw))
    return msgs, offset


def iter_pcap(paths: List[str]) -> Iterator[Tuple[str, str]]:
    """Rejoue une ou plusieurs captures -> (stream, message) serveur->client."""
    from app.network.pcap_feed import iter_messages
    for path in paths:
        for _ts, stream, msg in iter_messages(path):
            yield (f"{stream[0]}:{stream[1]}", msg)


# ---- affichage --------------------------------------------------------------

def _fmt_levels(levels: List[int]) -> str:
    if not levels:
        return "lv?"
    if len(levels) == 1:
        return f"lv{levels[0]}"
    return f"lv{levels[0]}-{levels[-1]}"


def print_report(cat: dict) -> None:
    zf = cat["zone_filter"] or "(toutes zones)"
    print(f"\n=== Zone « {zf} » ===")
    seen, total = cat["maps_seen"], cat["maps_total_in_zone"]
    cover = f"{seen}/{total}" if total else str(seen)
    print(f"Maps vues : {cover}" + (f"  | manquantes : {len(cat['maps_missing'])}"
                                     if total else ""))
    print(f"Monstres distincts : {len(cat['monsters_distinct'])}"
          f"  | archis repérés : {len(cat['archi_ids_seen'])}")

    for mv in cat["maps"]:
        xy = mv["coord"]
        coord = f"[{xy[0]},{xy[1]}]" if xy else "[?,?]"
        print(f"\n  map {mv['map_id']} {coord}  ({mv['visits']} visite(s))"
              + ("  ★ARCHI" if mv["archi_present"] else ""))
        if not mv["monsters"]:
            print("    (aucun groupe de monstres capturé sur cette map)")
        for mon in mv["monsters"]:
            star = "★ " if mon["archi"] else "  "
            print(f"    {star}{mon['id']:>5}  {mon['name']:<34} "
                  f"{_fmt_levels(mon['levels']):>10}  x{mon['sightings']}")

    if cat["monsters_distinct"]:
        print("\n  -- Monstres de la zone (tous, par fréquence) --")
        for mon in cat["monsters_distinct"]:
            star = "★ " if mon["archi"] else "  "
            print(f"    {star}{mon['id']:>5}  {mon['name']:<34} x{mon['sightings']}")

    if cat["maps_missing"]:
        print(f"\n  Maps de la zone PAS ENCORE visitées ({len(cat['maps_missing'])}) :")
        print("    " + ", ".join(str(m) for m in cat["maps_missing"]))
    if not protocol.ARCHI_IDS:
        print("\n  (data/archi_ids.json vide : aucun monstre flaggé archi. Ajoute "
              "les ids d'archis repérés ci-dessus pour les mettre en évidence.)")


def main() -> int:
    ap = argparse.ArgumentParser(description="Catalogue maps/monstres/archis d'une zone.")
    ap.add_argument("--zone", default="Grobe",
                    help="sous-chaîne de sous-zone (défaut: Grobe ; \"\" = toutes)")
    ap.add_argument("--pcap", nargs="+", metavar="FICHIER",
                    help="capture(s) .pcap/.pcapng (messages complets)")
    ap.add_argument("--jsonl", metavar="FICHIER", default=LIVE_FEED,
                    help="dump live_feed.jsonl (défaut: data/live_feed.jsonl)")
    ap.add_argument("--watch", type=float, metavar="SECONDES", default=0,
                    help="suit le jsonl en continu, réaffiche toutes les N s")
    ap.add_argument("--json", metavar="FICHIER",
                    help="écrit le catalogue JSON dans ce fichier")
    args = ap.parse_args()

    zone = args.zone if args.zone != "" else None
    sniffer = ZoneSniffer(zone_filter=zone)

    if args.pcap:
        n = sniffer.feed(iter_pcap(args.pcap))
        print(f"(pcap : {n} messages map/acteurs traités)")
    elif args.watch:
        return _run_watch(sniffer, args.jsonl, args.watch, args.json)
    else:
        if not os.path.exists(args.jsonl):
            print(f"Source introuvable : {args.jsonl}", file=sys.stderr)
            return 2
        msgs, _ = iter_jsonl(args.jsonl)
        sniffer.feed(msgs)
        print(f"({len(msgs)} messages S->C lus depuis {os.path.basename(args.jsonl)})")

    cat = sniffer.catalog()
    print_report(cat)
    if args.json:
        with open(args.json, "w", encoding="utf-8") as fh:
            json.dump(cat, fh, ensure_ascii=False, indent=2)
        print(f"\nCatalogue écrit -> {args.json}")
    return 0


def _run_watch(sniffer: ZoneSniffer, path: str, interval: float, json_out) -> int:
    """Suit ``path`` (live_feed.jsonl) en incrémental et réaffiche le catalogue."""
    offset = 0
    print(f"=== WATCH {os.path.basename(path)} (zone « {sniffer.zone_filter or 'toutes'} ») "
          f"— Ctrl-C pour stopper ===")
    try:
        while True:
            if os.path.exists(path):
                msgs, offset = iter_jsonl(path, offset)
                if msgs:
                    sniffer.feed(msgs)
                    cat = sniffer.catalog()
                    os.system("cls" if os.name == "nt" else "clear")
                    print_report(cat)
                    if json_out:
                        with open(json_out, "w", encoding="utf-8") as fh:
                            json.dump(cat, fh, ensure_ascii=False, indent=2)
            time.sleep(max(0.5, interval))
    except KeyboardInterrupt:
        print("\n=== stop ===")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
