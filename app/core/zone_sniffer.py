"""Catalogue des maps / monstres / archimonstres d'une ZONE (sous-zone Dofus).

Agrège un flux de messages Dofus Retro DÉJÀ décodables (voir app.network.protocol)
pour produire, par map d'une sous-zone donnée, la liste des monstres aperçus
(id, nom, niveaux observés, nombre d'apparitions) et le flag archimonstre.

Pur (aucune dépendance réseau) : on lui pousse des couples ``(stream, message)``
déjà réassemblés — exactement le même format que app.network.pcap_feed. Un
``stream`` = une connexion (perso/compte) ; on suit la map courante de chaque
flux via GDM, puis on rattache les groupes de monstres (GM) à cette map.

La sous-zone d'une map vient de protocol.MAP_ZONES (table côté client) ; le filtre
``zone_filter`` est une sous-chaîne insensible à la casse (ex. "grobe" matche
"L'Ile de Grobe" ET "Pont de Grobe"). None = toutes les zones.

Note archimonstres : en Retro un archi a un id de monstre DISTINCT, donc il
apparaît dans GM avec son propre id -> détectable DÈS qu'il est dans
protocol.ARCHI_IDS. Tant que la liste est vide, aucun monstre n'est flaggé archi ;
le catalogue liste malgré tout TOUS les ids rencontrés, ce qui sert à repérer les
ids candidats à ajouter dans data/archi_ids.json.
"""
from __future__ import annotations

import collections
import threading
from typing import Dict, Iterable, List, Optional, Sequence, Set, Tuple

# Règles d'alerte « groupe » par défaut : (id de monstre, nombre mini dans UN même
# groupe). 583 = Fantôme Pandikaze -> alerte dès qu'un groupe en contient >= 2.
DEFAULT_GROUP_ALERT_RULES: Sequence[Tuple[int, int]] = ((583, 2),)

# Seuil « gros groupe » : si la SOMME des niveaux des monstres d'un même groupe
# dépasse ce seuil, le groupe est marqué ``over`` (indicateur sur la carte).
GROUP_LEVEL_WARN = 949

from app.network import protocol

MAP_DATA_PREFIX = protocol.MAP_DATA_PREFIX    # "GDM"
MAP_ACTORS_PREFIX = protocol.MAP_ACTORS_PREFIX  # "GM"


class ZoneSniffer:
    """Agrège maps + monstres d'une (ou toutes les) sous-zone(s).

    État par map : ``{visits, monsters: {id: {levels: set, sightings: int}}}``.
    """

    def __init__(self, zone_filter: Optional[str] = "Grobe",
                 group_alert_rules: Sequence[Tuple[int, int]] = DEFAULT_GROUP_ALERT_RULES,
                 group_level_warn: int = GROUP_LEVEL_WARN) -> None:
        self.zone_filter: Optional[str] = zone_filter.lower() if zone_filter else None
        self.stream_map: Dict[object, int] = {}   # stream -> map courante
        self.maps: Dict[int, dict] = {}            # map_id -> état (zones gardées)
        # Lecteur (catalog) et écrivain (feed via /live/stream) peuvent tourner
        # dans des threads différents côté API -> verrou pour ne pas muter les
        # dicts pendant une itération de lecture.
        self._lock = threading.Lock()
        # Journal d'ALERTES (événements d'apparition de groupe) : archimonstre
        # présent, ou règle « groupe » satisfaite (ex. >= 2 Fantôme Pandikaze).
        # Détecté à l'AJOUT d'un groupe (GM +), pas sur l'état cumulé. Borné ;
        # chaque alerte a un ``seq`` monotone pour que le client ne notifie que
        # les nouvelles (cf. alerts_since).
        self.group_alert_rules: Tuple[Tuple[int, int], ...] = tuple(group_alert_rules)
        self.group_level_warn = group_level_warn
        self.alerts: "collections.deque[dict]" = collections.deque(maxlen=300)
        self._alert_seq = 0

    # -- filtre ---------------------------------------------------------------
    def _keep(self, map_id: int) -> bool:
        if self.zone_filter is None:
            return True
        zone = protocol.MAP_ZONES.get(map_id) or ""
        return self.zone_filter in zone.lower()

    def _map(self, map_id: int) -> dict:
        return self.maps.setdefault(map_id, {"visits": 0, "monsters": {}, "groups": {}})

    # -- ingestion ------------------------------------------------------------
    def on_map_change(self, stream, map_id: int) -> None:
        """GDM : le flux ``stream`` charge la map ``map_id``."""
        self.stream_map[stream] = map_id
        if self._keep(map_id):
            m = self._map(map_id)
            m["visits"] += 1
            # (Re)chargement de map : le serveur renvoie la liste complète des
            # acteurs juste après -> on repart de groupes vides pour que l'état
            # « groupes courants » (survol de la carte) reste à jour.
            m["groups"] = {}

    def on_actors(self, stream, actors: List[dict], ts: Optional[float] = None) -> None:
        """GM (déjà décodé par protocol.parse_map_actors) : rattache les groupes
        de monstres à la map courante du flux, et émet des alertes à l'ajout d'un
        groupe (archi présent / règle « groupe » satisfaite)."""
        map_id = self.stream_map.get(stream)
        if map_id is None or not self._keep(map_id):
            return
        m = self._map(map_id)
        for a in actors:
            if a.get("kind") != "group":
                continue
            if a.get("op") == "remove":
                # groupe tué / parti -> retiré de l'état « groupes courants »
                m["groups"].pop(a.get("group_id"), None)
                continue
            if a.get("op") != "add":
                continue
            monsters = a.get("monsters", [])
            mon_ids = [mon["id"] for mon in monsters]
            # état « groupes courants » de la map (pour le survol de la carte)
            m["groups"][a.get("group_id")] = {
                "cell": a.get("cell"),
                "monsters": [{"id": mon["id"], "level": mon.get("level")} for mon in monsters],
            }
            for mon in monsters:
                entry = m["monsters"].setdefault(mon["id"], {"levels": set(), "sightings": 0})
                entry["sightings"] += 1
                if mon.get("level") is not None:
                    entry["levels"].add(mon["level"])
            self._record_group_alerts(map_id, a.get("group_id"), mon_ids, ts)

    def _record_group_alerts(self, map_id: int, group_id, mon_ids: List[int],
                             ts: Optional[float]) -> None:
        """Évalue les conditions d'alerte sur UN groupe ajouté et journalise les
        événements correspondants (sous le verrou de feed)."""
        reasons: List[Tuple[str, str]] = []
        # 1) archimonstre présent dans le groupe
        archi = [mid for mid in mon_ids if mid in protocol.ARCHI_IDS]
        if archi:
            names = ", ".join(sorted({protocol.MONSTER_NAMES.get(a, f"#{a}") for a in archi}))
            reasons.append(("archi", f"Archimonstre : {names}"))
        # 2) règles « groupe » : un id présent >= n fois dans le même groupe
        counts: Dict[int, int] = {}
        for mid in mon_ids:
            counts[mid] = counts.get(mid, 0) + 1
        for rid, rmin in self.group_alert_rules:
            c = counts.get(rid, 0)
            if c >= rmin:
                nm = protocol.MONSTER_NAMES.get(rid, f"#{rid}")
                reasons.append((f"grp{rid}", f"{c}× {nm}"))
        for reason, label in reasons:
            self._alert_seq += 1
            self.alerts.append({
                "seq": self._alert_seq,
                "ts": ts,
                "map_id": map_id,
                "zone": protocol.MAP_ZONES.get(map_id),
                "coord": protocol.MAP_COORDS.get(map_id),
                "group_id": group_id,
                "reason": reason,
                "label": label,
                "key": f"{map_id}:{group_id}:{reason}",
                "monsters": [{
                    "id": mid,
                    "name": protocol.MONSTER_NAMES.get(mid, f"#{mid}"),
                    "archi": mid in protocol.ARCHI_IDS,
                } for mid in mon_ids],
            })

    def feed(self, messages: Iterable[Tuple[object, str]], ts: Optional[float] = None) -> int:
        """Ingest un itérable de ``(stream, message)`` serveur->client. Ne traite
        que GDM (map) et GM (acteurs) ; retourne le nombre de messages pertinents.

        ``ts`` (epoch) horodate les alertes émises (None pour l'amorçage hors-ligne)."""
        used = 0
        with self._lock:
            for stream, msg in messages:
                if not msg:
                    continue
                if msg.startswith(MAP_DATA_PREFIX):
                    mid = protocol.parse_map_change(msg)
                    if mid is not None:
                        self.on_map_change(stream, mid)
                        used += 1
                elif msg.startswith(MAP_ACTORS_PREFIX):
                    actors = protocol.parse_map_actors(msg)
                    if actors:
                        self.on_actors(stream, actors, ts)
                        used += 1
        return used

    def alerts_since(self, since_seq: int = 0, zone: Optional[str] = None) -> dict:
        """Alertes dont le ``seq`` est > ``since_seq`` (optionnellement filtrées par
        sous-zone), + le ``max_seq`` courant pour le prochain appel. Le client
        amorce ``since_seq = max_seq`` au démarrage pour ignorer l'historique."""
        flt = zone.lower() if zone else None
        with self._lock:
            out = [a for a in self.alerts
                   if a["seq"] > since_seq
                   and (flt is None or flt in (a["zone"] or "").lower())]
            return {"max_seq": self._alert_seq, "alerts": out}

    # -- lecture --------------------------------------------------------------
    def _zone_map_ids(self, flt: Optional[str]) -> Set[int]:
        """Tous les ids de map de la (des) zone(s) correspondant à ``flt``, d'après
        protocol.MAP_ZONES — pour repérer les maps PAS ENCORE visitées."""
        if flt is None:
            return set()
        return {mid for mid, z in protocol.MAP_ZONES.items()
                if flt in (z or "").lower()}

    def catalog(self, zone: Optional[str] = None) -> dict:
        """Snapshot JSON-sérialisable : maps triées, monstres nommés, rollups zone.

        ``zone`` (sous-chaîne) FILTRE la sortie à la lecture, indépendamment du
        filtre d'ingestion : l'API ingère toutes les zones (zone_filter=None) et
        choisit la zone affichée ici. None -> on retombe sur self.zone_filter."""
        flt = zone.lower() if zone else self.zone_filter

        def matches(mid: int) -> bool:
            if flt is None:
                return True
            return flt in (protocol.MAP_ZONES.get(mid) or "").lower()

        maps_out: List[dict] = []
        monster_totals: Dict[int, int] = {}
        archi_ids_seen: Set[int] = set()
        with self._lock:
            for mid, m in sorted(self.maps.items()):
                if not matches(mid):
                    continue
                monsters: List[dict] = []
                archi_here = False
                for mon_id, e in sorted(m["monsters"].items()):
                    is_archi = mon_id in protocol.ARCHI_IDS
                    archi_here = archi_here or is_archi
                    if is_archi:
                        archi_ids_seen.add(mon_id)
                    monster_totals[mon_id] = monster_totals.get(mon_id, 0) + e["sightings"]
                    monsters.append({
                        "id": mon_id,
                        "name": protocol.MONSTER_NAMES.get(mon_id, f"#{mon_id}"),
                        "archi": is_archi,
                        "levels": sorted(e["levels"]),
                        "sightings": e["sightings"],
                    })
                groups: List[dict] = []
                has_big = False
                for gid, g in sorted(
                        m["groups"].items(),
                        key=lambda kv: kv[1]["cell"] if kv[1]["cell"] is not None else 1_000_000):
                    tot = sum((x["level"] or 0) for x in g["monsters"])
                    over = tot > self.group_level_warn
                    has_big = has_big or over
                    groups.append({
                        "group_id": gid,
                        "cell": g["cell"],
                        "total_level": tot,
                        "over": over,
                        "monsters": [{
                            "id": x["id"],
                            "name": protocol.MONSTER_NAMES.get(x["id"], f"#{x['id']}"),
                            "level": x["level"],
                            "archi": x["id"] in protocol.ARCHI_IDS,
                        } for x in g["monsters"]],
                    })
                maps_out.append({
                    "map_id": mid,
                    "zone": protocol.MAP_ZONES.get(mid),
                    "coord": protocol.MAP_COORDS.get(mid),
                    "visits": m["visits"],
                    "archi_present": archi_here,
                    "has_big_group": has_big,
                    "groups": groups,
                    "monsters": monsters,
                })
            seen_ids = {mid for mid in self.maps if matches(mid)}

        monsters_distinct = [{
            "id": mid,
            "name": protocol.MONSTER_NAMES.get(mid, f"#{mid}"),
            "archi": mid in protocol.ARCHI_IDS,
            "sightings": total,
        } for mid, total in sorted(monster_totals.items(),
                                   key=lambda kv: (-kv[1], kv[0]))]

        zone_map_ids = self._zone_map_ids(flt)
        missing = sorted(zone_map_ids - seen_ids) if zone_map_ids else []

        return {
            "zone_filter": flt,
            "maps_seen": len(maps_out),
            "maps_total_in_zone": len(zone_map_ids) or None,
            "maps_missing": missing,
            "monsters_distinct": monsters_distinct,
            "archi_ids_seen": sorted(archi_ids_seen),
            "group_level_warn": self.group_level_warn,
            "maps": maps_out,
        }
