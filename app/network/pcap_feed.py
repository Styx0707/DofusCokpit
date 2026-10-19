"""Alimente un RepopMonitor depuis une capture .pcap/.pcapng.

Sert deux usages :
- ingestion hors-ligne d'une capture Wireshark (endpoint POST /live/ingest) ;
- ingestion des fichiers d'un ring-buffer dumpcap pour le suivi « live »
  (voir app.network.live_watch).

Réassemble les flux TCP comme le sniffer live (buffer par flux + découpe sur
l'octet nul) et rejoue les messages GDM/GM dans l'ordre chronologique. Scapy est
importé PARESSEUSEMENT (lourd) pour ne pas alourdir le démarrage de l'API.
"""
from __future__ import annotations

import collections
import time
from typing import Iterator, Tuple

from app.core.repop_monitor import RepopMonitor
from app.network import protocol

DELIMITER = b"\x00"
GAME_PORT = 443


def iter_messages(path: str, port: int = GAME_PORT) -> Iterator[Tuple[float, tuple, str]]:
    """Rejoue un pcap -> (ts_epoch, stream, message) en ordre chronologique.

    Sens serveur->client uniquement (le serveur émet depuis `port`). `stream`
    identifie le client destinataire (ip, port) = un perso/compte distinct.
    """
    from scapy.all import IP, Raw, TCP, rdpcap  # import paresseux (scapy lourd)

    pkts = [p for p in rdpcap(path) if TCP in p and Raw in p and IP in p]
    pkts.sort(key=lambda p: float(p.time))
    buffers = collections.defaultdict(bytes)
    for p in pkts:
        ip, tcp = p[IP], p[TCP]
        if tcp.sport != port:          # on ne suit que serveur -> client
            continue
        stream = (ip.dst, tcp.dport)   # le client (perso/compte) destinataire
        buffers[stream] += bytes(p[Raw].load)
        *complete, remainder = buffers[stream].split(DELIMITER)
        buffers[stream] = remainder
        for raw in complete:
            if not raw:
                continue
            msg = raw.decode("utf-8", "ignore").strip()
            if msg:
                yield float(p.time), stream, msg


def feed_pcap(monitor: RepopMonitor, path: str, port: int = GAME_PORT,
              on_bank=None, on_prices=None, on_messages=None) -> dict:
    """Ingest une capture complète dans le moniteur. Retourne un résumé.

    `on_bank`, si fourni, est appelé une seule fois avec ``{item_id: quantite}``
    quand un message de banque ``EL`` est présent (snapshot complet). On retient
    le PLUS GROS ``EL`` du fichier pour ne pas écraser la banque avec un snapshot
    partiel (ex. ``EL`` coupé à la frontière de deux fichiers du ring-buffer).

    `on_prices`, si fourni, est appelé une fois avec ``{item_id: prix_unitaire}``
    agrégé sur tous les messages HDV du fichier : on retient le PREMIER PRIX, càd
    le prix du lot de 1 (``EHl`` x1 = l'offre la PLUS BASSE en vente) ; si plusieurs
    messages existent pour un même objet, on garde le minimum. Le prix MOYEN
    (``EHP``) ne sert que de repli quand aucun lot n'est en vente. Message vide ->
    pas d'appel.
    """
    from app.network.exit_learner import get_learner
    learner = get_learner()
    maps, adds, removes, messages = set(), 0, 0, 0
    best_bank: dict = {}
    hdv_avg: dict = {}   # gid -> prix moyen (EHP), repli uniquement
    hdv_x1: dict = {}    # gid -> PREMIER PRIX = prix du lot de 1 (EHl x1), le plus bas
    zpairs: list = []    # (stream, msg) pour on_messages (ZoneSniffer) si demandé
    last_ts = None
    for ts, stream, msg in iter_messages(path, port):
        messages += 1
        last_ts = ts
        if on_messages is not None:
            zpairs.append((stream, msg))
        learner.on_message(stream, msg)   # apprentissage auto des sorties E/O
        if on_bank is not None and msg.startswith(protocol.BANK_MESSAGE_PREFIX):
            inv = protocol.parse_bank_storage(msg[len(protocol.BANK_MESSAGE_PREFIX):])
            if len(inv) > len(best_bank):
                best_bank = inv
        elif on_prices is not None and msg.startswith(protocol.HDV_AVG_PRICE_PREFIX):
            r = protocol.parse_hdv_avg_price(msg[len(protocol.HDV_AVG_PRICE_PREFIX):])
            if r is not None and r[1] > 0:
                hdv_avg[r[0]] = r[1]
        elif on_prices is not None and msg.startswith(protocol.HDV_ITEM_PRICE_PREFIX):
            r = protocol.parse_hdv_item_prices(msg[len(protocol.HDV_ITEM_PRICE_PREFIX):])
            if r is not None and r.get("price"):
                prev = hdv_x1.get(r["item_id"])
                price = r["price"]
                # plusieurs EHl pour un même objet -> on garde le PLUS BAS
                hdv_x1[r["item_id"]] = price if prev is None else min(prev, price)
        elif msg.startswith(protocol.MAP_DATA_PREFIX):
            map_id = protocol.parse_map_change(msg)
            if map_id is not None:
                monitor.on_map_change(stream, map_id, ts)
                maps.add(map_id)
        elif msg.startswith(protocol.MAP_ACTORS_PREFIX):
            actors = protocol.parse_map_actors(msg)
            if actors:
                monitor.on_actors(stream, actors, ts)
                adds += sum(1 for a in actors if a["op"] == "add")
                removes += sum(1 for a in actors if a["op"] == "remove")
        elif msg.startswith(protocol.FIGHTER_PM_PREFIX):   # PM~ : id combattant -> nom
            r = protocol.parse_fighter_name(msg)
            if r is not None:
                monitor.on_fighter_name(stream, r[0], r[1], ts)
        elif msg.startswith(protocol.TURN_START_PREFIX):   # GTS : début de tour
            fid = protocol.parse_turn_start(msg)
            if fid is not None:
                monitor.on_turn_start(stream, fid, ts)
    if on_messages is not None and zpairs:
        on_messages(zpairs, last_ts)   # -> ZoneSniffer (catalogue + groupes + alertes par zone)
    if on_bank is not None and best_bank:
        on_bank(best_bank)
    prices: dict = {}
    if on_prices is not None:
        prices = dict(hdv_avg)  # repli : prix moyen (EHP) si aucun lot en vente…
        prices.update(hdv_x1)   # …puis PREMIER PRIX = lot de 1 (le plus bas), prioritaire
        if prices:
            on_prices(prices)
    return {"path": path, "messages": messages, "maps": sorted(maps),
            "group_adds": adds, "group_removes": removes,
            "bank_items": len(best_bank), "hdv_prices": len(prices)}


def feed_messages(monitor: RepopMonitor, messages, on_bank=None, on_prices=None,
                  ts: float = None) -> dict:
    """Ingest un LOT de messages serveur->client DÉJÀ réassemblés (flux live, sans
    pcap). ``messages`` = itérable de ``(stream, message_texte)``.

    Même dispatch que ``feed_pcap`` (RepopMonitor + apprentissage des sorties E/O +
    auto-sync banque ``EL`` / prix HDV ``EHP``/``EHl``), mais alimenté par un flux
    temps réel (hook socket du client, ``scripts/frida_live.py``) au lieu d'un
    fichier. ``stream`` identifie le client (perso/compte)."""
    from app.network.exit_learner import get_learner
    learner = get_learner()
    if ts is None:
        ts = time.time()
    maps, adds, removes, count = set(), 0, 0, 0
    best_bank: dict = {}
    hdv_avg: dict = {}
    hdv_x1: dict = {}
    for stream, msg in messages:
        if not msg:
            continue
        count += 1
        learner.on_message(stream, msg)
        if on_bank is not None and msg.startswith(protocol.BANK_MESSAGE_PREFIX):
            inv = protocol.parse_bank_storage(msg[len(protocol.BANK_MESSAGE_PREFIX):])
            if len(inv) > len(best_bank):
                best_bank = inv
        elif on_prices is not None and msg.startswith(protocol.HDV_AVG_PRICE_PREFIX):
            r = protocol.parse_hdv_avg_price(msg[len(protocol.HDV_AVG_PRICE_PREFIX):])
            if r is not None and r[1] > 0:
                hdv_avg[r[0]] = r[1]
        elif on_prices is not None and msg.startswith(protocol.HDV_ITEM_PRICE_PREFIX):
            r = protocol.parse_hdv_item_prices(msg[len(protocol.HDV_ITEM_PRICE_PREFIX):])
            if r is not None and r.get("price"):
                prev = hdv_x1.get(r["item_id"])
                hdv_x1[r["item_id"]] = r["price"] if prev is None else min(prev, r["price"])
        elif msg.startswith(protocol.MAP_DATA_PREFIX):
            map_id = protocol.parse_map_change(msg)
            if map_id is not None:
                monitor.on_map_change(stream, map_id, ts)
                maps.add(map_id)
        elif msg.startswith(protocol.MAP_ACTORS_PREFIX):
            actors = protocol.parse_map_actors(msg)
            if actors:
                monitor.on_actors(stream, actors, ts)
                adds += sum(1 for a in actors if a["op"] == "add")
                removes += sum(1 for a in actors if a["op"] == "remove")
        elif msg.startswith(protocol.FIGHTER_PM_PREFIX):
            r = protocol.parse_fighter_name(msg)
            if r is not None:
                monitor.on_fighter_name(stream, r[0], r[1], ts)
        elif msg.startswith(protocol.TURN_START_PREFIX):
            fid = protocol.parse_turn_start(msg)
            if fid is not None:
                monitor.on_turn_start(stream, fid, ts)
    if on_bank is not None and best_bank:
        on_bank(best_bank)
    prices: dict = {}
    if on_prices is not None:
        prices = dict(hdv_avg)
        prices.update(hdv_x1)
        if prices:
            on_prices(prices)
    return {"messages": count, "maps": sorted(maps),
            "group_adds": adds, "group_removes": removes,
            "bank_items": len(best_bank), "hdv_prices": len(prices)}
