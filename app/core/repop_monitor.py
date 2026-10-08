"""Moniteur temps réel des groupes de monstres par map (suivi de repop).

Alimenté par un flux de messages Dofus décodés (voir app.network.protocol) :
- un changement de map (GDM) place un « stream » (une connexion = un perso/compte)
  sur une map ;
- la liste d'acteurs (GM) ajoute/retire des groupes de monstres sur cette map.

Le moniteur agrège l'état PAR MAP (plusieurs comptes possibles), repère les
groupes contenant une cible (déf. Bambouto Sacré, id 546) et estime le délai de
repop en mesurant le temps entre la disparition d'un groupe cible (tué) et la
réapparition d'un groupe cible sur la même map. L'estimation S'AUTO-CALIBRE :
tant qu'aucun cycle mort->repop n'a été observé, le compte à rebours reste nul
(non calibré) — on n'invente pas de chiffre.

État en mémoire, protégé par un verrou : conçu pour le process unique de l'API.
"""
from __future__ import annotations

import logging
import statistics
import threading
from typing import Callable, Dict, Iterable, List, Optional, Set

from app.network import protocol

logger = logging.getLogger(__name__)


def _monster_view(m: dict) -> dict:
    # On ne stocke que id+niveau ; le NOM est résolu à l'affichage (snapshot),
    # pour qu'un rechargement de MONSTER_NAMES renomme l'état déjà ingéré.
    return {"id": m["id"], "level": m["level"]}


def _named(m: dict) -> dict:
    return {
        "id": m["id"],
        "name": protocol.MONSTER_NAMES.get(m["id"], f"#{m['id']}"),
        "level": m["level"],
        "archi": m["id"] in protocol.ARCHI_IDS,
    }


class RepopMonitor:
    def __init__(
            self,
            target_ids: Iterable[int] = (protocol.BAMBOUTO_SACRE_ID,),
            keep_intervals: int = 20,
    ) -> None:
        self.target_ids: Set[int] = set(target_ids)
        self.keep_intervals = keep_intervals
        self._lock = threading.Lock()
        self.stream_map: Dict[object, int] = {}   # stream -> map courante
        self.maps: Dict[int, dict] = {}            # map_id -> état
        self.last_ts: Optional[float] = None
        # Identification du perso du compte : le joueur present sur TOUTES les maps
        # d'un flux est le proprietaire (les autres joueurs varient). On compte les
        # apparitions par nom et on retient le plus frequent.
        self.stream_char_counts: Dict[object, Dict[str, int]] = {}
        self.stream_char: Dict[object, str] = {}   # stream -> nom du perso (déduit)
        # Dernière activité par stream : un même perso peut avoir PLUSIEURS streams
        # (le stream = connexion TCP ; une reconnexion/relog en ouvre une nouvelle,
        # jamais supprimée). On s'en sert pour ne garder, par nom, que le stream
        # le plus récent — sinon le perso apparaît en double (board.html, carte).
        self.stream_ts: Dict[object, float] = {}
        # Combat : mapping GLOBAL id de combattant -> nom (via PM ou GM), et tour
        # courant par flux. Global + PERSISTANT (jamais vidé au changement de map) :
        # une fois un perso nommé (au début d'un combat), il se résout dans TOUS les
        # combats suivants, même si un fichier de capture est sauté. turn = {id,name,ts}.
        self.fighter_names: Dict[int, str] = {}
        self.turn: Dict[object, dict] = {}
        # Ordre des tours (noms, dédup consécutif) — mémoire persistante côté
        # serveur pour que le pop-up puisse REMBOBINER même ouvert après le combat.
        self.play_order: List[str] = []
        # Callback optionnel appelé (HORS verrou) à chaque apparition cible/archi,
        # pour persistance. Signature : (appearance: dict) -> None.
        self.on_appearance: Optional[Callable[[dict], None]] = None

    # -- helpers --------------------------------------------------------------
    def _map(self, map_id: int) -> dict:
        return self.maps.setdefault(map_id, {
            "groups": {},            # group_id -> group dict
            "monsters_seen": {},     # monster_id -> nb d'apparitions
            "target_gone_at": None,  # ts de disparition du dernier groupe cible
            "last_target_seen": None,
            "intervals": [],         # deltas mort->repop observés (s)
            "target_hits": 0,        # nb d'apparitions d'un groupe cible (historique)
            "archi_hits": 0,         # nb d'apparitions d'un archi (historique)
            "last_target_ts": None,
            "last_archi_ts": None,
            "updated": None,
        })

    def _group_is_target(self, group: dict) -> bool:
        return any(mon["id"] in self.target_ids for mon in group["monsters"])

    # -- ingestion ------------------------------------------------------------
    def on_map_change(self, stream, map_id: int, ts: float) -> None:
        with self._lock:
            self.last_ts = ts
            self.stream_ts[stream] = ts
            self.stream_map[stream] = map_id
            m = self._map(map_id)
            # (Re)chargement de map : le serveur renvoie la liste complète des
            # acteurs juste après ; on repart d'un état de groupes vide.
            m["groups"] = {}
            m["updated"] = ts
            # changer de map = fin du tour courant (mais on GARDE le mapping
            # id->nom : il est persistant, les ids de perso sont stables).
            self.turn.pop(stream, None)

    def on_fighter_name(self, stream, fid: int, name: str, ts: float) -> None:
        """PM : associe un id de combattant à un nom de perso (pour ce flux)."""
        with self._lock:
            self.last_ts = ts
            self.stream_ts[stream] = ts
            self.fighter_names[fid] = name

    def on_turn_start(self, stream, fid: int, ts: float) -> None:
        """GTS : le combattant fid commence son tour (« qui joue »)."""
        with self._lock:
            self.last_ts = ts
            self.stream_ts[stream] = ts
            name = self.fighter_names.get(fid)
            self.turn[stream] = {"id": fid, "name": name, "ts": ts}
            # mémorise l'ordre des tours (dédup consécutif, plusieurs flux voient
            # le même tour) pour le rembobinage post-combat.
            if name and (not self.play_order or self.play_order[-1] != name):
                self.play_order.append(name)
                if len(self.play_order) > 200:
                    self.play_order = self.play_order[-200:]

    def on_actors(self, stream, actors: List[dict], ts: float) -> None:
        appearances: List[dict] = []
        with self._lock:
            self.last_ts = ts
            self.stream_ts[stream] = ts
            map_id = self.stream_map.get(stream)
            if map_id is None:
                return
            m = self._map(map_id)
            for a in actors:
                if a.get("kind") == "player":
                    if a["op"] == "add":
                        self._note_player(stream, a.get("name", ""))
                        # id de sprite = id de combattant (GTS) -> nom. C'est par
                        # ici que les combattants de DONJON (PvM) sont nommés
                        # (l'arène passait par PM~ ; GM couvre les deux).
                        sid, nm = a.get("sprite_id"), a.get("name")
                        if sid is not None and nm:
                            self.fighter_names[sid] = nm
                    continue
                if a["op"] == "add":
                    ap = self._add_group(map_id, m, a, ts)
                    if ap:
                        appearances.append(ap)
                elif a["op"] == "remove":
                    self._remove_group(m, a, ts)
            m["updated"] = ts
        # Persistance HORS verrou (IO DB) : ne bloque pas snapshot() ni l'ingestion.
        self._emit_appearances(appearances)

    def _emit_appearances(self, appearances: List[dict]) -> None:
        cb = self.on_appearance
        if not cb:
            return
        for ap in appearances:
            try:
                cb(ap)
            except Exception:
                logger.exception("on_appearance a échoué (apparition non persistée)")

    def _note_player(self, stream, name: str) -> None:
        if not name:
            return
        counts = self.stream_char_counts.setdefault(stream, {})
        counts[name] = counts.get(name, 0) + 1
        # Perso du compte = nom le plus fréquent sur ce flux (présent partout).
        self.stream_char[stream] = max(counts, key=counts.get)

    def _add_group(self, map_id: int, m: dict, actor: dict, ts: float) -> Optional[dict]:
        """Ajoute un groupe ; retourne une apparition {..} si cible/archi (à
        persister), sinon None."""
        group = {
            "group_id": actor["group_id"],
            "cell": actor["cell"],
            "monsters": [_monster_view(x) for x in actor["monsters"]],
            "first_seen": ts,
        }
        m["groups"][actor["group_id"]] = group
        for x in actor["monsters"]:
            m["monsters_seen"][x["id"]] = m["monsters_seen"].get(x["id"], 0) + 1
        is_archi = any(mon["id"] in protocol.ARCHI_IDS for mon in group["monsters"])
        is_target = self._group_is_target(group)
        if is_archi:
            m["archi_hits"] += 1
            m["last_archi_ts"] = ts
        if is_target:
            m["target_hits"] += 1
            m["last_target_ts"] = ts
            # Réapparition d'une cible : si une cible avait disparu, on mesure
            # l'intervalle mort->repop (auto-calibration).
            if m["target_gone_at"] is not None:
                delta = ts - m["target_gone_at"]
                if delta > 0:
                    m["intervals"] = (m["intervals"] + [delta])[-self.keep_intervals:]
                m["target_gone_at"] = None
            m["last_target_seen"] = ts
        if is_target or is_archi:
            return {
                "map_id": map_id, "ts": ts,
                "is_target": is_target, "is_archi": is_archi,
                "monster_ids": [x["id"] for x in actor["monsters"]],
                "coord": protocol.MAP_COORDS.get(map_id),
                "zone": protocol.MAP_ZONES.get(map_id),
            }
        return None

    def _remove_group(self, m: dict, actor: dict, ts: float) -> None:
        group = m["groups"].pop(actor["group_id"], None)
        if group and self._group_is_target(group):
            m["target_gone_at"] = ts

    # -- lecture --------------------------------------------------------------
    def estimate_repop(self, map_id: int) -> Optional[float]:
        m = self.maps.get(map_id)
        if not m or not m["intervals"]:
            return None
        return statistics.median(m["intervals"])

    def _map_view(self, map_id: int, m: dict, active_maps: Set[int], now: float) -> dict:
        groups = sorted(
            m["groups"].values(),
            key=lambda g: g["cell"] if g["cell"] is not None else 1_000_000,
        )
        target_present = any(self._group_is_target(g) for g in groups)
        archi_present = any(mo["id"] in protocol.ARCHI_IDS
                            for g in groups for mo in g["monsters"])
        est = statistics.median(m["intervals"]) if m["intervals"] else None
        countdown = None
        if not target_present and m["target_gone_at"] is not None and est is not None:
            countdown = max(0.0, m["target_gone_at"] + est - now)
        return {
            "map_id": map_id,
            "coord": protocol.MAP_COORDS.get(map_id),  # [x, y] ou None
            "zone": protocol.MAP_ZONES.get(map_id),    # nom de sous-zone ou None
            "active": map_id in active_maps,
            "target_present": target_present,
            "archi_present": archi_present,
            "target_hits": m["target_hits"],
            "archi_hits": m["archi_hits"],
            "last_target_ago_s": round(now - m["last_target_ts"], 1) if m["last_target_ts"] else None,
            "last_archi_ago_s": round(now - m["last_archi_ts"], 1) if m["last_archi_ts"] else None,
            "groups": [{
                "group_id": g["group_id"],
                "cell": g["cell"],
                "is_target": self._group_is_target(g),
                "monsters": [_named(mo) for mo in g["monsters"]],
                "age_s": round(now - g["first_seen"], 1) if g["first_seen"] else None,
            } for g in groups],
            "repop_estimate_s": round(est, 1) if est is not None else None,
            "repop_samples": len(m["intervals"]),
            "repop_countdown_s": round(countdown, 1) if countdown is not None else None,
            "updated_ago_s": round(now - m["updated"], 1) if m["updated"] else None,
        }

    def snapshot(self, now: float) -> dict:
        with self._lock:
            # Dédup des streams : par NOM de perso, on ne garde que le stream le
            # plus récent (reconnexions = streams fantômes qui doublaient le perso).
            # Les streams non encore nommés sont tous conservés (indéterminés).
            best_by_name: Dict[str, object] = {}
            for s in self.stream_map:
                nm = self.stream_char.get(s)
                if not nm:
                    continue
                cur = best_by_name.get(nm)
                if cur is None or self.stream_ts.get(s, 0.0) >= self.stream_ts.get(cur, 0.0):
                    best_by_name[nm] = s
            kept = set(best_by_name.values())
            visible_streams = {s: mid for s, mid in self.stream_map.items()
                               if self.stream_char.get(s) is None or s in kept}
            active_maps = set(visible_streams.values())
            maps_out = [self._map_view(mid, m, active_maps, now)
                        for mid, m in self.maps.items()]
            # Maps actives d'abord, puis celles avec une cible, puis par id.
            maps_out.sort(key=lambda x: (
                not x["active"],
                not (x["target_present"] or x["archi_present"]),
                not x["target_present"],
                x["map_id"],
            ))
            # Position de chaque COMPTE (1 par flux/connexion) pour la mini-carte.
            view_by_map = {mv["map_id"]: mv for mv in maps_out}
            accounts = []
            for i, (stream, mid) in enumerate(
                    sorted(visible_streams.items(), key=lambda kv: (kv[1], str(kv[0])))):
                mv = view_by_map.get(mid, {})
                accounts.append({
                    "label": f"C{i + 1}",
                    "name": self.stream_char.get(stream),
                    "map_id": mid,
                    "coord": protocol.MAP_COORDS.get(mid),
                    "zone": protocol.MAP_ZONES.get(mid),
                    "target": bool(mv.get("target_present")),
                    "archi": bool(mv.get("archi_present")),
                    "groups": len(mv.get("groups", [])),
                })
            # « Qui joue » : noms des combattants dont c'est le tour, vus
            # récemment (un tour dure ~30 s ; au-delà de 50 s on considère le
            # combat fini / l'info périmée). Dédupliqué (plusieurs flux voient le
            # même combat).
            turn_names: List[str] = []
            seen_turn = set()
            for t in self.turn.values():
                nm = t.get("name")
                if nm and (now - t["ts"]) <= 50.0 and nm not in seen_turn:
                    seen_turn.add(nm)
                    turn_names.append(nm)
            return {
                "turn_names": turn_names,
                "play_order": list(self.play_order),
                "target_ids": sorted(self.target_ids),
                "target_names": [protocol.MONSTER_NAMES.get(i, f"#{i}")
                                 for i in sorted(self.target_ids)],
                "archi_ids": sorted(protocol.ARCHI_IDS),
                "streams": len(visible_streams),
                "last_event_ago_s": round(now - self.last_ts, 1) if self.last_ts else None,
                "accounts": accounts,
                "maps": maps_out,
            }

    def load_history(self, rows: Iterable[dict]) -> int:
        """Ré-amorce les compteurs par map depuis la DB (get_map_history) au
        démarrage : la heatmap / le Top maps survivent au redémarrage. Ces maps
        apparaissent inactives (pas de perso, pas de groupe courant) mais avec
        leur historique target_hits/archi_hits."""
        n = 0
        with self._lock:
            for r in rows:
                m = self._map(int(r["map_id"]))
                m["target_hits"] = int(r.get("target_hits") or 0)
                m["archi_hits"] = int(r.get("archi_hits") or 0)
                m["last_target_ts"] = r.get("last_target_ts")
                m["last_archi_ts"] = r.get("last_archi_ts")
                n += 1
        return n

    def reset(self) -> None:
        with self._lock:
            self.stream_map.clear()
            self.maps.clear()
            self.stream_char_counts.clear()
            self.stream_char.clear()
            self.stream_ts.clear()
            self.fighter_names.clear()
            self.turn.clear()
            self.play_order.clear()
            self.last_ts = None


# Singleton partagé par l'API (un seul process).
_MONITOR: Optional[RepopMonitor] = None


def get_monitor() -> RepopMonitor:
    global _MONITOR
    if _MONITOR is None:
        _MONITOR = RepopMonitor()
    return _MONITOR
