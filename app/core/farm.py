"""Planificateur de farm pour le brisage « Rune Ga Pa ».

Part des équipements +PA RENTABLES à briser (cf. ``app.core.brisage``), APLATIT
leurs recettes jusqu'aux ressources-FEUILLES (celles sans recette = matières
premières), agrège les quantités requises, puis pour chaque ressource indique :

1. sa **source** : métier de RÉCOLTE (Mineur / Bûcheron / Alchimiste / Pêcheur /
   Paysan), déduit du *type* de l'objet, OU **butin de monstre** ;
2. **où la farmer** : zones / monstres candidats, déduits en rapprochant le NOM
   de la ressource des noms de zones (``data/map_zones.json``) et de monstres
   (``data/monster_names.json``).

Il n'existe PAS de table de butin (monstre -> drops) dans le jeu de données : le
rapprochement est donc HEURISTIQUE (ex. « Pollen de Blop » -> zone « Prairie des
Blops » ; « Etoffe de Ouassingue » -> monstre « Le Ouassingue »). Chaque piste
porte la raison du rapprochement (``via``) pour que l'utilisateur juge la
confiance. Les ressources de métier (minerais, fleurs…) sont fiables ; les butins
dépendent de ce rapprochement de noms.

Les fonctions de CALCUL sont PURES (pas d'IO) -> testables ; le chargement des
tables (zones, monstres) est isolé dans ``load_zone_index`` / ``load_monster_index``
et mémoïsé.
"""
from __future__ import annotations

import json
import re
import unicodedata
from collections import Counter
from functools import lru_cache
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from app.core.brisage import load_detail
from app.models import FarmResource, FarmSpot

_DATA_DIR = Path(__file__).resolve().parents[2] / "data"

# --- Classification de la source par TYPE d'objet ---------------------------
# Rapprochement par SOUS-CHAÎNE sur le type normalisé (sans accents) -> robuste
# aux variantes d'encodage du cache wiki. Premier match l'emporte.
_HARVEST_RULES: Tuple[Tuple[str, str], ...] = (
    ("minerai", "Mineur"),
    ("pierre", "Mineur / Bijoutier"),   # Pierre brute / précieuse = minée puis taillée
    ("bois", "Bûcheron"),
    ("ecorce", "Bûcheron"),
    ("racine", "Bûcheron"),
    ("bourgeon", "Bûcheron"),
    ("cereale", "Paysan"),
    ("graine", "Paysan"),
    ("fleur", "Alchimiste"),
    ("plante", "Alchimiste"),
    ("champignon", "Alchimiste"),
    ("poisson", "Pêcheur"),
)

# Types-feuilles de MATIÈRE issue d'un monstre (butin). Le reste des feuilles non
# classées (dont le fourre-tout « Ressource ») est traité en ``unknown`` : on
# tente quand même le rapprochement de zone/monstre par le nom.
_DROP_TYPES: frozenset = frozenset({
    "os", "oeil", "peau", "poil", "poudre", "etoffe", "cuir", "viande", "plume",
    "carapace", "ecaille", "corne", "dent", "aile", "patte", "queue", "oreille",
    "langue", "gelee", "laine", "tissu", "essence", "sang", "griffe", "crin",
    "tentacule", "nageoire", "mandibule", "antenne", "cervelle", "crane",
})

# Mots-outils ignorés quand on extrait le « nom de famille » du monstre depuis le
# nom d'une ressource (ex. « Oeil d'Ouginak » -> ["ouginak"]).
_STOPWORDS: frozenset = frozenset({
    "de", "du", "des", "la", "le", "les", "d", "au", "aux", "en", "a", "l",
})


def _norm(s: Optional[str]) -> str:
    """Minuscule, sans accents ni ponctuation (apostrophes du cache incluses)."""
    s = unicodedata.normalize("NFKD", (s or "").replace("\\'", "'"))
    s = "".join(c for c in s if not unicodedata.combining(c))
    return re.sub(r"[^a-z0-9 ]+", " ", s.lower()).strip()


def _singular(w: str) -> str:
    """Dé-pluralise grossièrement (Rats -> Rat, Blops -> Blop) pour matcher les
    noms de zone/monstre souvent au pluriel/singulier."""
    return w[:-1] if len(w) > 3 and w.endswith("s") else w


def classify_source(item_type: Optional[str]) -> Tuple[str, Optional[str]]:
    """``type`` d'objet -> ``(source_kind, profession)``.

    - ``("harvest", "<métier>")`` pour une ressource de récolte (minerai, fleur…) ;
    - ``("drop", None)`` pour une matière de butin (os, peau, carapace…) ;
    - ``("unknown", None)`` sinon (type générique « Ressource », inconnu…).
    """
    n = _norm(item_type)
    if not n:
        return "unknown", None
    for key, prof in _HARVEST_RULES:
        if key in n:
            return "harvest", prof
    first = n.split(" ", 1)[0]
    if first in _DROP_TYPES or n in _DROP_TYPES:
        return "drop", None
    return "unknown", None


def family_tokens(name: Optional[str]) -> List[str]:
    """Jetons « nom de la créature/zone » extraits d'un nom de ressource : on
    retire les mots-outils et on garde les 2 derniers mots significatifs (ex.
    « Etoffe du Rat Noir » -> ["rat", "noir"], « Pollen de Blop » -> ["blop"])."""
    words = [w for w in _norm(name).split() if w and w not in _STOPWORDS]
    return words[-2:] if len(words) > 2 else words


# --- Aplatissement des recettes jusqu'aux feuilles --------------------------
def flatten_resources(
        item_id: int,
        quantity: int,
        recipes: Dict[int, List[Tuple[int, int]]],
        acc: Counter,
        _stack: Optional[frozenset] = None,
) -> None:
    """Ajoute à ``acc`` les ressources-FEUILLES (items sans recette) nécessaires
    pour ``quantity`` unités de ``item_id``, en descendant récursivement
    ``recipes`` (= {id: [(sous_id, qté)]}). Garde anti-cycle. Fonction PURE."""
    stack = _stack or frozenset()
    rec = recipes.get(item_id)
    if rec and item_id not in stack:
        for sub_id, sub_qty in rec:
            flatten_resources(sub_id, quantity * sub_qty, recipes, acc, stack | {item_id})
    else:
        acc[item_id] += quantity


# --- Index zones / monstres (IO isolé, mémoïsé) -----------------------------
@lru_cache(maxsize=2)
def load_zone_index(data_dir: Optional[str] = None) -> Tuple[Tuple[str, str], ...]:
    """``((zone_normalisée, zone_affichée), …)`` depuis ``data/map_zones.json``
    (dédupliqué). Figé en cours d'exécution -> mémoïsé."""
    path = Path(data_dir or _DATA_DIR) / "map_zones.json"
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ()
    seen: Dict[str, str] = {}
    for disp in raw.values():
        n = _norm(disp)
        if n and n not in seen:
            seen[n] = disp.strip()
    return tuple(seen.items())


@lru_cache(maxsize=2)
def load_monster_index(data_dir: Optional[str] = None) -> Tuple[Tuple[str, str], ...]:
    """``((monstre_normalisé, monstre_affiché), …)`` depuis
    ``data/monster_names.json``. Mémoïsé."""
    path = Path(data_dir or _DATA_DIR) / "monster_names.json"
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return ()
    out: Dict[str, str] = {}
    for disp in raw.values():
        n = _norm(disp)
        if n and n not in out:
            out[n] = disp.strip()
    return tuple(out.items())


@lru_cache(maxsize=2)
def load_drops_index(data_dir: Optional[str] = None) -> Dict[int, Tuple[dict, ...]]:
    """``{item_id: (source, …)}`` depuis ``data/drops.json`` (tables de butin xixou,
    cf. ``scripts/ingest_drops.py``). Chaque source = ``{monster, slug, rate, zones}``.
    Vide si le fichier est absent -> on retombe sur l'heuristique de noms. Mémoïsé."""
    path = Path(data_dir or _DATA_DIR) / "drops.json"
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}
    out: Dict[int, Tuple[dict, ...]] = {}
    for k, v in raw.items():
        try:
            srcs = tuple(v.get("sources", []))
        except AttributeError:
            continue
        if srcs:
            out[int(k)] = srcs
    return out


def spots_from_drops(sources: Iterable[dict], limit: int = 6) -> List[FarmSpot]:
    """Pistes de farm CONFIRMÉES (table de butin) : par source (triée par taux déc.),
    un spot monstre (avec taux) puis ses zones. Zones remontées en tête, dé-doublonné."""
    spots: List[FarmSpot] = []
    seen: set = set()

    def add(label: str, kind: str, rate: Optional[int] = None) -> None:
        key = (kind, label)
        if label and key not in seen:
            seen.add(key)
            spots.append(FarmSpot(label=label, kind=kind, via="drop", rate=rate))

    for src in sorted(sources, key=lambda s: -(s.get("rate") or 0)):
        add(src.get("monster") or "", "monster", src.get("rate"))
        for z in src.get("zones", []):
            add(z, "zone")
    spots.sort(key=lambda s: s.kind != "zone")   # zones (actionnables) d'abord
    return spots[:limit]


def live_zones_from_catalog(catalog: Optional[dict]) -> Dict[str, List[str]]:
    """``{monstre_normalisé: [zones où il a été vu en live]}`` depuis un snapshot
    de ``ZoneSniffer.catalog()``. Alimente la piste « live » de ``find_spots``.
    Tolérant (catalogue absent/partiel -> dict vide)."""
    out: Dict[str, List[str]] = {}
    for m in (catalog or {}).get("maps", []):
        zone = (m.get("zone") or "").strip()
        if not zone:
            continue
        for mon in m.get("monsters", []):
            key = _norm(mon.get("name"))
            if not key:
                continue
            bucket = out.setdefault(key, [])
            if zone not in bucket:
                bucket.append(zone)
    return out


def find_spots(
        name: str,
        zone_index: Iterable[Tuple[str, str]],
        monster_index: Iterable[Tuple[str, str]],
        live_zones_by_monster: Optional[Dict[str, List[str]]] = None,
        limit: int = 4,
) -> List[FarmSpot]:
    """Pistes de farm pour la ressource ``name`` par rapprochement de noms.

    1. nom de MONSTRE dont un MOT correspond à un jeton de famille -> piste
       monstre (``via`` = "nom de monstre") ; si ce monstre a été vu en live, on
       ajoute ses zones (``via`` = "live") ;
    2. nom de ZONE dont un MOT correspond à un jeton -> piste zone (``via`` =
       "nom de zone").

    Rapprochement au MOT (après dé-pluralisation des deux côtés), pas en
    sous-chaîne : « os » ne matche donc PAS « BoOS » / « OSamodas ». Les jetons de
    moins de 3 lettres sont ignorés (trop ambigus). Fonction PURE (les index/‹live›
    sont fournis). Dé-doublonnée, bornée."""
    stems = {_singular(t) for t in family_tokens(name) if len(t) >= 3}
    if not stems:
        return []
    spots: List[FarmSpot] = []
    seen: set = set()

    def add(label: str, kind: str, via: str) -> None:
        key = (kind, label)
        if label and key not in seen:
            seen.add(key)
            spots.append(FarmSpot(label=label, kind=kind, via=via))

    def matches(norm_name: str) -> bool:
        return bool(stems & {_singular(w) for w in norm_name.split()})

    live = live_zones_by_monster or {}
    for mon_norm, mon_disp in monster_index:
        if matches(mon_norm):
            add(mon_disp, "monster", "nom de monstre")
            for z in live.get(mon_norm, []):
                add(z, "zone", "live")

    for zone_norm, zone_disp in zone_index:
        if matches(zone_norm):
            add(zone_disp, "zone", "nom de zone")

    # Zones (plus actionnables) d'abord, puis monstres ; live prioritaire.
    spots.sort(key=lambda s: (s.via != "live", s.kind != "zone"))
    return spots[:limit]


# --- Plan de farm (pur) -----------------------------------------------------
def compute_farm_plan(
        targets: List[dict],
        crafts: Dict[int, int],
        recipes: Dict[int, List[Tuple[int, int]]],
        stock: Dict[int, int],
        price_map: Dict[int, Optional[int]],
        zone_index: Iterable[Tuple[str, str]],
        monster_index: Iterable[Tuple[str, str]],
        live_zones_by_monster: Optional[Dict[str, List[str]]] = None,
        drops_index: Optional[Dict[int, Iterable[dict]]] = None,
) -> List[FarmResource]:
    """Agrège les ressources-FEUILLES à réunir pour fabriquer, par cible,
    ``crafts[item_id]`` exemplaires (puis les briser), avec leur source et leurs
    pistes de farm. Fonction PURE.

    - ``targets``   : cibles de brisage (``{item_id, recipe:[{item_id, quantity}]}``) ;
    - ``crafts``    : nb de crafts voulu par cible (0 -> cible ignorée) ;
    - ``recipes``   : {id: [(sous_id, qté)]} pour l'aplatissement (cf.
                      ``brisage.ingredient_recipes``) ;
    - ``stock``     : {id: quantité en banque} ; ``price_map`` : {id: prix HDV}.

    Renvoie les ressources triées par coût d'achat du manquant décroissant (les
    plus chères à réunir d'abord), les non-valorisées (prix inconnu) ensuite."""
    agg: Counter = Counter()
    users: Dict[int, set] = {}
    for t in targets:
        n = crafts.get(t["item_id"], 0)
        if n <= 0:
            continue
        for ing in t["recipe"]:
            before = dict(agg)
            flatten_resources(ing["item_id"], ing["quantity"] * n, recipes, agg)
            for leaf in agg:
                if agg[leaf] != before.get(leaf, 0):
                    users.setdefault(leaf, set()).add(t["item_id"])

    rows: List[FarmResource] = []
    for leaf_id, qty in agg.items():
        d = load_detail(leaf_id) or {}
        name = (d.get("name") or f"#{leaf_id}").replace("\\'", "'")
        typ = (d.get("type") or None)
        kind, prof = classify_source(typ)
        in_bank = stock.get(leaf_id, 0)
        to_buy = max(0, qty - in_bank)
        unit_price = price_map.get(leaf_id)
        buy_cost = unit_price * to_buy if unit_price is not None else None
        spots: List[FarmSpot] = []
        if kind in ("drop", "unknown"):
            confirmed = (drops_index or {}).get(leaf_id)
            if confirmed:
                spots = spots_from_drops(confirmed)          # table de butin (fiable)
            else:
                spots = find_spots(name, zone_index, monster_index, live_zones_by_monster)
        rows.append(FarmResource(
            item_id=leaf_id, name=name, type=typ,
            qty_needed=qty, in_bank=in_bank, to_buy=to_buy,
            unit_price=unit_price, buy_cost=buy_cost,
            source_kind=kind, profession=prof, spots=spots,
            used_in=sorted(users.get(leaf_id, ())),
        ))

    rows.sort(key=lambda r: (r.buy_cost is None, -(r.buy_cost or 0)))
    return rows


def rank_zones(
        resources: List[FarmResource],
        drops_index: Dict[int, Iterable[dict]],
        gapa_per_unit: Dict[int, float],
        limit: int = 12,
) -> List[dict]:
    """Classe les ZONES par RENDEMENT Ga Pa : « combien de Ga Pa je débloque par
    combat ici ». Fonction PURE.

    Pour chaque ressource de BUTIN (type ``drop``) encore à réunir (``to_buy > 0``),
    on lit ses sources (``drops_index``) : par zone, le MEILLEUR taux de drop et un
    monstre. Score de la zone = Σ_ressources ``(meilleur_taux/100) × gapa_per_unit[r]``
    — l'espérance de Ga Pa « débloquée » par combat (une ressource qui tombe souvent
    et qui sert une cible à fort taux Ga Pa pèse plus). Une zone qui fournit PLUSIEURS
    ressources utiles cumule (= farm groupé). ``gapa_per_unit[r]`` = poids Ga Pa de la
    ressource = MEILLEUR ``taux_Ga_Pa`` parmi les cibles qui l'utilisent (cf. appelant) :
    on ne somme PAS sur les cibles, sinon les matières ubiquitaires (ex. Eau) écrasent
    le classement alors qu'1 unité ne sert qu'1 craft.

    Les ressources de type générique (``unknown`` : « Ressource », Eau…) sont EXCLUES :
    non caractéristiques, mieux vaut les acheter. Heuristique de rendement : ignore
    taille de groupe, PP, et le fait qu'il faut TOUS les ingrédients d'un craft — c'est
    un indicateur « où ça tombe le plus vite », pas un temps exact."""
    zones: Dict[str, dict] = {}
    for r in resources:
        if r.source_kind != "drop" or r.to_buy <= 0:
            continue
        gpu = gapa_per_unit.get(r.item_id, 0.0)
        if gpu <= 0:
            continue
        best: Dict[str, Tuple[int, str]] = {}   # zone -> (meilleur taux, monstre)
        for s in drops_index.get(r.item_id) or []:
            rate = s.get("rate") or 0
            mon = s.get("monster") or ""
            for z in s.get("zones", []):
                if z and (z not in best or rate > best[z][0]):
                    best[z] = (rate, mon)
        for z, (rate, mon) in best.items():
            entry = zones.setdefault(z, {"zone": z, "score": 0.0, "resources": [],
                                         "monsters": set(), "targets": set()})
            entry["score"] += (rate / 100.0) * gpu
            entry["resources"].append({"item_id": r.item_id, "name": r.name,
                                       "rate": rate, "monster": mon, "to_buy": r.to_buy})
            if mon:
                entry["monsters"].add(mon)
            entry["targets"].update(r.used_in)

    out: List[dict] = []
    for z in zones.values():
        z["resources"].sort(key=lambda x: -x["rate"])
        out.append({
            "zone": z["zone"],
            "score": round(z["score"], 3),
            "resource_count": len(z["resources"]),
            "resources": z["resources"][:8],
            "monsters": sorted(z["monsters"])[:6],
            "target_count": len(z["targets"]),
        })
    out.sort(key=lambda z: (-z["score"], -z["resource_count"]))
    return out[:limit]


def rank_targets(
        targets: List[dict],
        crafts: Dict[int, int],
        recipes: Dict[int, List[Tuple[int, int]]],
        rate_by_id: Dict[int, float],
        drops_index: Dict[int, Iterable[dict]],
        limit: int = 60,
) -> List[dict]:
    """Classe les CIBLES +PA par rentabilité de FARM. Pour chaque cible retenue
    (``crafts[item_id] > 0``), aplatit la recette d'1 craft et calcule :

    - ``ga_pa_rate`` (Ga Pa par objet cassé) ;
    - ``harvest`` = nb de ressources de RÉCOLTE métier (à minimiser) ;
    - ``butins`` = nb de butins monstre (type ``drop``) avec source connue, ``zones`` ;
    - ``fights`` = combats estimés pour les butins = Σ ``qté / (meilleur_taux/100)``
      (ignore taille de groupe/PP -> surestime ; sert au comparatif) ;
    - ``gapa_per_100`` = ``ga_pa_rate / fights × 100`` = rendement Ga Pa par combat ;
    - ``bottleneck`` = le butin au taux le plus BAS (= ce qui rend le craft difficile),
      avec monstre + zone ; ``needs_eau`` si la recette contient de l'Eau.

    Les ressources de type générique (Eau/« Ressource ») ne comptent NI en récolte NI
    en butin (voir ``needs_eau``). Tri par rendement décroissant. Non pur (lit le cache
    ``data/details`` via ``load_detail``)."""
    out: List[dict] = []
    for t in targets:
        tid = t["item_id"]
        if crafts.get(tid, 0) <= 0:
            continue
        leaf: Counter = Counter()
        for ing in t["recipe"]:
            flatten_resources(ing["item_id"], ing["quantity"], recipes, leaf)
        if not leaf:
            continue
        harvest = butins = 0
        zones: set = set()
        fights = 0.0
        bottleneck: Optional[dict] = None
        needs_eau = False
        for lid, q in leaf.items():
            d = load_detail(lid) or {}
            kind, _ = classify_source(d.get("type"))
            if kind == "harvest":
                harvest += 1
                continue
            if kind != "drop":
                if "eau" in _norm(d.get("name")):
                    needs_eau = True
                continue
            srcs = list(drops_index.get(lid) or [])
            if not srcs:
                continue
            butins += 1
            best = max(srcs, key=lambda s: s.get("rate") or 0)
            zone = (best.get("zones") or ["?"])[0]
            zones.add(zone)
            rate = best.get("rate") or 0
            if rate:
                fights += q / (rate / 100.0)
            if bottleneck is None or rate < bottleneck["rate"]:
                bottleneck = {"name": (d.get("name") or "").replace("\\'", "'"),
                              "rate": rate, "qty": q,
                              "monster": best.get("monster") or "", "zone": zone}
        gpr = rate_by_id.get(tid, 0.0)
        out.append({
            "item_id": tid, "name": t.get("name"), "level": t.get("level"),
            "ga_pa_rate": round(gpr, 3), "harvest": harvest, "butins": butins,
            "zones": len(zones), "fights": round(fights),
            "gapa_per_100": round(gpr / fights * 100, 3) if fights else None,
            "bottleneck": bottleneck, "needs_eau": needs_eau,
        })
    out.sort(key=lambda a: -(a["gapa_per_100"] or 0))
    return out[:limit]


@lru_cache(maxsize=2)
def load_monsters(data_dir: Optional[str] = None) -> dict:
    """Bestiaire complet ``data/monsters.json`` (cf. ``scripts/ingest_monsters.py``) :
    ``{slug: {name, level_min, level_max, zones[], drops:[{item_id, name, rate}]}}``.
    Vide si absent. Mémoïsé."""
    path = Path(data_dir or _DATA_DIR) / "monsters.json"
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return {}


# Monstres NON farmables en boucle (coffres, boss quotidiens / événementiels, PvP) :
# exclus du classement kamas quand ``exclude_special=True`` (match par mot du nom).
_NON_FARMABLE: Tuple[str, ...] = (
    "coffre", "dopeul", "halouine", "noel", "nowel", "pere noel",
    "prisme", "gardien", "chef de guilde", "percepteur",
)


def _is_special(name: Optional[str]) -> bool:
    n = _norm(name)
    return any(tok in n for tok in _NON_FARMABLE)


def rank_kamas(
        monsters: dict,
        price_map: Dict[int, Optional[int]],
        level_max: Optional[int] = None,
        limit: int = 50,
        price_max: Optional[int] = None,
        exclude_special: bool = False,
) -> dict:
    """Classe MONSTRES et ZONES par VALEUR DE BUTIN par combat (kamas), pour un
    perso de niveau ≤ ``level_max``. Fonction PURE.

    - ``monsters``   : bestiaire (cf. ``load_monsters``) ;
    - ``price_map``  : ``{item_id: prix HDV}`` (les drops sans prix sont ignorés) ;
    - ``level_max``  : ne garde que les monstres de ``level_min`` ≤ ce seuil (None = tous).

    Par monstre : ``value_per_fight`` = Σ sur ses drops valorisés de ``taux/100 × prix``
    (espérance de kamas par kill, ignore PP/quantité>1/taille de groupe -> comparatif),
    ``value_per_level`` = ``value_per_fight / niveau`` (favorise le bas niveau qui lâche
    cher). Par zone : le MEILLEUR monstre accessible (max ``value_per_fight``).

    ``price_max`` : ignore tout drop dont le prix unitaire DÉPASSE ce plafond
    (garde-fou anti-prix-aberrant du dump HDV — ex. Cuisse de Wabbit à 15M au lieu
    de ~1 : bug prix au lot vs à l'unité). ``None`` = pas de filtre ; le nb de drops
    écartés est renvoyé dans ``outliers``.

    ``exclude_special`` : écarte les monstres NON farmables en boucle (coffres, boss
    quotidiens/événementiels « …d'Halouine », Dopeuls, Prismes, Gardiens, Percepteurs —
    cf. ``_NON_FARMABLE``) ; leur nombre est renvoyé dans ``specials``.

    Renvoie ``{"monsters", "zones", "outliers", "specials"}`` triés par valeur déc."""
    mons: List[dict] = []
    outliers = 0
    specials = 0
    for slug, m in monsters.items():
        lvl = m.get("level_min")
        if level_max is not None and lvl is not None and lvl > level_max:
            continue
        if exclude_special and _is_special(m.get("name")):
            specials += 1
            continue
        drops_valued = []
        total = 0.0
        for d in m.get("drops", []):
            iid = d.get("item_id")
            price = price_map.get(iid) if iid is not None else None
            if not price:
                continue
            if price_max is not None and price > price_max:
                outliers += 1
                continue
            ev = (d.get("rate") or 0) / 100.0 * price
            total += ev
            drops_valued.append({"name": d.get("name"), "rate": d.get("rate"),
                                 "price": price, "ev": round(ev)})
        if total <= 0:
            continue
        drops_valued.sort(key=lambda x: -x["ev"])
        lv = lvl or 1
        mons.append({
            "slug": slug, "name": m.get("name") or slug,
            "level_min": lvl, "level_max": m.get("level_max"),
            "value_per_fight": round(total),
            "value_per_level": round(total / max(lv, 1)),
            "zones": m.get("zones", []),
            "top_drops": drops_valued[:5],
        })

    # Rollup zone : le meilleur monstre (value_per_fight) accessible dans la zone.
    zmap: Dict[str, dict] = {}
    for mo in mons:
        for z in mo["zones"]:
            e = zmap.setdefault(z, {"zone": z, "best_value": 0, "best_monster": None,
                                    "best_level": None, "monster_count": 0})
            e["monster_count"] += 1
            if mo["value_per_fight"] > e["best_value"]:
                e["best_value"] = mo["value_per_fight"]
                e["best_monster"] = mo["name"]
                e["best_level"] = mo["level_min"]

    mons.sort(key=lambda a: -a["value_per_fight"])
    zones = sorted(zmap.values(), key=lambda z: -z["best_value"])
    return {"monsters": mons[:limit], "zones": zones[:limit],
            "outliers": outliers, "specials": specials}
