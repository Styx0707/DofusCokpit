"""Brisage « Rune Ga Pa » : rentabilité du craft-pour-briser des équipements +PA.

Contexte métier
---------------
Certains équipements donnent « +1 PA ». Cassés (brisage / forgemagie), ils
produisent des **Rune Ga Pa** (la grande rune de Point d'Action, item 1557),
très recherchées. Cette page répond à trois questions, pour un lot d'items curés
(voir ``PA_BRISAGE_TARGET_IDS``) :

1. **Taux d'obtention** de la Ga Pa par objet brisé. Tous les items visés étant
   « +1 PA », ce taux est IDENTIQUE pour tous : il ne dépend que du briseur
   (taux de brisage / focalisation), pas de l'objet. On l'expose donc comme un
   PARAMÈTRE calibrable (``rate`` = Ga Pa obtenues par objet « +1 PA » brisé),
   multiplié par la valeur PA de l'objet (futur-proof pour d'éventuels +2/+3 PA).
2. **Nombre de crafts possibles** avec le stock de banque courant (même logique
   que ``optimizer.compute_craftable`` : min sur les ingrédients DIRECTS).
3. **Kamas potentiels** générés par les futures Ga Pa : ``expected_ga_pa ×
   prix_unitaire_Ga_Pa``, et le NET une fois déduit le coût marché des
   ingrédients.

Source des données
------------------
Recette / niveau / valeur PA sont lus depuis le cache ``data/details/<id>.json``
(le même que ``scripts.fetch_recipes`` / ``scripts.seed_items_full``), source
GARANTIE et indépendante du sous-ensemble seedé en base (``data/recipes.json``).
Le stock de banque et les prix viennent, eux, de la base (injectés par l'appelant).

La fonction de calcul ``compute_pa_brisage`` est PURE (pas d'IO) -> testable ;
le chargement JSON est isolé dans ``load_pa_targets`` / ``load_detail``.
"""
from __future__ import annotations

import json
import re
from functools import lru_cache
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Tuple

from app.models import BrisageIngredient, PaBrisageRow

# Rune « Ga Pa » (grande rune de Point d'Action) : le produit du brisage.
GA_PA_RUNE_ID = 1557
GA_PA_RUNE_NAME = "Rune Ga Pa"

# Niveau max par défaut des équipements à briser (le bas niveau est le filon
# classique pour farmer la Ga Pa). Réglable via l'API (``max_level``).
MAX_BRISAGE_LEVEL = 120

# Types d'objets BRISABLES (équipement + armes). Sert à l'auto-découverte des
# cibles : on exclut familiers, Dofus, trophées, toniques, montures, objets de
# quête, cartes, potions, nourriture, etc. (non brisables / hors sujet).
_BRISABLE_TYPES = {
    "Amulette", "Anneau", "Chapeau", "Cape", "Ceinture", "Botte", "Bottes",
    "Bouclier", "Dague", "Dagues", "Epée", "Épée", "Marteau", "Arc",
    "Baguette", "Bâton", "Baton", "Hache", "Pelle", "Faux",
}

# Sélection HISTORIQUE (première demande). N'est PLUS la liste par défaut :
# ``load_pa_targets()`` auto-découvre désormais TOUS les équipements +PA
# craftables ≤ MAX_BRISAGE_LEVEL (cf. ``discover_pa_targets``). Conservée pour
# référence / usage via ``load_pa_targets(target_ids=...)``.
PA_BRISAGE_TARGET_IDS: List[int] = [
    8445,   # Collier du Rat Noir
    323,    # Amulette du Kam Assutra  (« amu kamasutra »)
    1619,   # L'Abramu                 (« abramu »)
    6464,   # Anneau de l'Invocateur Satisfait
    8273,   # Collier du Dragon Cochon
    7251,   # Amulette Terrdala        (« terdala »)
    7253,   # Amulette Aerdala
    1908,   # Casque du Chafer         (« casque chafer »)
    10836,  # Boufbamu                 (« boufamulette »)
    159,    # La Broche Céleste
]

# Poids de forgemagie (formule de brisage Dofus — forums JOL « Les taux de
# brisage » / papycha) :
#     taux = (niveau × poids_ligne × coefficient) / (100 × poids_rune)
# avec poids_ligne = valeur_carac × poids_unitaire_carac × niveau × FOCUS + 1
# (le niveau intervient deux fois -> croissance ≈ quadratique, cf. ga_pa_rate).
POIDS_PA = 100                           # poids unitaire d'un Point d'Action
GA_MULTIPLIER = 10                       # une rune Ga = 10 runes de base (Pa = ×3)
POIDS_GA_PA = POIDS_PA * GA_MULTIPLIER   # poids de la rune Ga Pa = 1000

# Facteur de focalisation du « poids de ligne » : poids_ligne = valeur × poids_PA
# × niveau × FOCUS + 1. Valeur documentée ≈ 0,015 ; calée ici sur le taux de
# référence réel Amulette du Kam Assutra (niv 43, +1 PA) = 8,49 %.
FOCUS_FACTOR = 0.01507

# Coefficient de brisage : multiplicateur global (≈ ×3 en Retro ; un émulateur
# qui booste les drops augmente ce coef). Défaut 3 -> reproduit les taux de
# référence (Kam Assutra niv 43 ≈ 8,49 %, Collier du Rat Noir niv 103 ≈ 48 %).
# À CALIBRER sur ton serveur.
DEFAULT_COEF = 3.0


def ga_pa_rate(level: Optional[int], pa_value: int, coef: float) -> float:
    """Taux d'obtention (nb moyen) de Rune Ga Pa par objet brisé.

    Formule de brisage Dofus : ``taux = niveau × poids_ligne × coef /
    (100 × poids_Ga_Pa)`` avec ``poids_ligne = valeur_PA × POIDS_PA × niveau ×
    FOCUS_FACTOR + 1``. Le niveau intervenant deux fois, le taux croît ≈ au CARRÉ
    du niveau -> un « +1 PA » niv 43 (≈ 8,5 %) rapporte bien moins qu'un niv 103
    (≈ 48 %). Peut dépasser 1 à très haut niveau / coef élevé."""
    lvl = level or 0
    poids_ligne = pa_value * POIDS_PA * lvl * FOCUS_FACTOR + 1
    return (lvl * poids_ligne * coef) / (100.0 * POIDS_GA_PA)


_DETAILS_DIR = Path(__file__).resolve().parents[2] / "data" / "details"
_PA_RE = re.compile(r"\+\s*(\d+)\s*PA\b")


def _clean(s: Optional[str]) -> str:
    """Le cache wiki stocke les apostrophes échappées « \\' » -> on nettoie."""
    return (s or "").replace("\\'", "'").replace('\\"', '"')


def _parse_pa(stats: List[str]) -> int:
    """Valeur « +N PA » lue dans les lignes de stats texte (0 si absente)."""
    for s in stats or []:
        m = _PA_RE.search(s)
        if m:
            return int(m.group(1))
    return 0


@lru_cache(maxsize=8192)
def _read_detail(path_str: str) -> Optional[dict]:
    """Lecture + parse d'une fiche, mémoïsée (le cache disque ne change pas en
    cours d'exécution). NE PAS muter le dict renvoyé (partagé)."""
    p = Path(path_str)
    if not p.exists():
        return None
    try:
        with p.open(encoding="utf-8") as fh:
            return json.load(fh)
    except (OSError, json.JSONDecodeError):
        return None


def load_detail(item_id: int, details_dir: Path = _DETAILS_DIR) -> Optional[dict]:
    """Charge la fiche ``data/details/<id>.json`` (None si absente/illisible)."""
    return _read_detail(str(Path(details_dir) / f"{item_id}.json"))


def _target_from_detail(d: dict) -> dict:
    """Normalise une fiche en cible de brisage (item_id, name, level, type,
    pa_value, recipe)."""
    return {
        "item_id": int(d["id"]),
        "name": _clean(d.get("name")) or f"Objet #{d.get('id')}",
        "level": d.get("level"),
        "type": _clean(d.get("type")) or None,
        "pa_value": _parse_pa(d.get("stats", [])),
        "recipe": [
            {
                "item_id": int(r["item_id"]),
                "name": _clean(r.get("name")),
                "quantity": int(r.get("qty", 0)),
            }
            for r in d.get("recipe", []) if r.get("item_id")
        ],
    }


@lru_cache(maxsize=16)
def discover_pa_targets(
        max_level: int = MAX_BRISAGE_LEVEL,
        details_dir: Path = _DETAILS_DIR,
) -> Tuple[dict, ...]:
    """Auto-découvre dans le cache ``data/details`` TOUS les équipements BRISABLES
    (cf. ``_BRISABLE_TYPES``) qui donnent « +N PA », sont CRAFTABLES (recette non
    vide) et de niveau ≤ ``max_level``. Trié par niveau puis id. Mémoïsé (le cache
    disque est figé en cours d'exécution). Renvoie un tuple (hashable) de cibles."""
    out: List[dict] = []
    for path in Path(details_dir).glob("*.json"):
        d = _read_detail(str(path))
        if not d or not d.get("recipe"):
            continue
        if _clean(d.get("type")) not in _BRISABLE_TYPES:
            continue
        if (d.get("level") or 0) > max_level:
            continue
        if _parse_pa(d.get("stats", [])) <= 0:
            continue
        out.append(_target_from_detail(d))
    out.sort(key=lambda t: ((t["level"] or 0), t["item_id"]))
    return tuple(out)


def load_pa_targets(
        target_ids: Optional[List[int]] = None,
        max_level: int = MAX_BRISAGE_LEVEL,
        details_dir: Path = _DETAILS_DIR,
) -> Tuple[List[dict], List[int]]:
    """Cibles de brisage. Par défaut (``target_ids=None``) : AUTO-DÉCOUVERTE de
    tous les équipements +PA craftables ≤ ``max_level`` (cf. ``discover_pa_targets``).
    Si ``target_ids`` est fourni, charge exactement ces ids depuis le cache.

    Renvoie ``(targets, missing_ids)`` ; ``missing_ids`` = ids explicites dont la
    fiche est absente (toujours vide en mode auto-découverte)."""
    if target_ids is None:
        return list(discover_pa_targets(max_level, details_dir)), []
    targets: List[dict] = []
    missing: List[int] = []
    for iid in target_ids:
        d = load_detail(iid, details_dir)
        if d is None:
            missing.append(iid)
        else:
            targets.append(_target_from_detail(d))
    return targets, missing


def ingredient_recipes(
        item_ids: Iterable[int],
        details_dir: Path = _DETAILS_DIR,
) -> Dict[int, List[Tuple[int, int]]]:
    """Construit ``{item_id: [(sous_item_id, qté)]}`` pour tous les items
    ATTEIGNABLES depuis ``item_ids`` qui possèdent une recette (parcours en
    largeur du cache ``data/details``). Sert à valoriser au coût de craft
    (cf. ``effective_costs``)."""
    recipes: Dict[int, List[Tuple[int, int]]] = {}
    seen: set = set()
    frontier = set(item_ids)
    while frontier:
        nxt: set = set()
        for iid in frontier:
            if iid in seen:
                continue
            seen.add(iid)
            d = load_detail(iid, details_dir)
            rec = [(int(r["item_id"]), int(r.get("qty", 0)))
                   for r in (d.get("recipe", []) if d else []) if r.get("item_id")]
            if rec:
                recipes[iid] = rec
                nxt.update(sub_id for sub_id, _ in rec if sub_id not in seen)
        frontier = nxt
    return recipes


def effective_costs(
        item_ids: Iterable[int],
        recipes: Dict[int, List[Tuple[int, int]]],
        price_map: Dict[int, Optional[int]],
) -> Dict[int, dict]:
    """Coût d'approvisionnement MINIMAL par item : ``min(prix HDV, coût de craft)``.

    Pour un ingrédient lui-même craftable (ex. La Broche Céleste, qui est AUSSI
    dans la recette du Collier du Rat Noir), on compare son prix d'achat HDV au
    coût de fabrication récursif (somme des coûts d'appro de SES ingrédients) et
    on retient le moins cher. Fonction PURE : ``recipes`` = {id: [(sous_id, qté)]},
    ``price_map`` = {id: prix HDV ou None}.

    Renvoie ``{id: {"cost", "source", "buy", "craft"}}`` ; ``cost``/``craft`` =
    None si non valorisable. Garde anti-cycle (recette revue dans sa propre chaîne
    ignorée) + mémoïsation."""
    memo: Dict[int, dict] = {}

    def resolve(iid: int, stack: frozenset) -> dict:
        if iid in memo:
            return memo[iid]
        buy = price_map.get(iid)
        craft: Optional[int] = None
        rec = recipes.get(iid)
        if rec and iid not in stack:
            total = 0
            ok = True
            for sub_id, qty in rec:
                sub = resolve(sub_id, stack | {iid})
                if sub["cost"] is None:
                    ok = False
                    break
                total += sub["cost"] * qty
            if ok:
                craft = total
        candidates = [c for c in (buy, craft) if c is not None]
        cost = min(candidates) if candidates else None
        if cost is None:
            source = None
        elif craft is not None and (buy is None or craft <= buy):
            source = "craft"
        else:
            source = "buy"
        entry = {"cost": cost, "source": source, "buy": buy, "craft": craft}
        memo[iid] = entry
        return entry

    return {iid: resolve(iid, frozenset()) for iid in item_ids}


def _bank_scenario(ingredients: List[BrisageIngredient], unit_revenue: int) -> Optional[dict]:
    """Scénario « stock banque GRATUIT » : les ressources déjà en banque ne coûtent
    rien ; on n'achète que le manquant et on MAXIMISE le nombre de crafts rentables.

    Pour ``n`` crafts, le coût d'achat ne porte que sur le dépassement du stock :
    ``buy(n) = Σ prix_i × max(0, n×qté_i − banque_i)``. Le profit net
    ``revenu×n − buy(n)`` est CONCAVE en ``n`` (coût marginal croissant à mesure que
    la banque s'épuise) -> on s'arrête dès qu'un craft de plus n'augmente plus le
    net. Si le revenu couvre même le rachat COMPLET (``revenu ≥ coût plein``), c'est
    rentable à l'infini (``unbounded``). Renvoie None si un ingrédient n'a pas de prix."""
    if not ingredients or any(i.unit_price is None for i in ingredients):
        return None

    def buy(n: int) -> int:
        return sum(i.unit_price * max(0, n * i.quantity - i.available) for i in ingredients)

    full_unit = sum(i.unit_price * i.quantity for i in ingredients)
    bank_unit_cost = buy(1)
    bank_unit_margin = unit_revenue - bank_unit_cost

    if unit_revenue >= full_unit:   # rentable même en rachetant tout -> illimité
        return {
            "bank_unit_cost": bank_unit_cost,
            "bank_unit_margin": bank_unit_margin,
            "bank_buy_profitable": bank_unit_margin > 0,
            "max_profitable_crafts": None,
            "max_profit_total": None,
            "bank_unbounded": True,
        }

    # Net concave : on monte n tant que le net progresse (coût marginal < revenu).
    max_k = max((i.available // i.quantity for i in ingredients if i.quantity), default=0)
    best_n, best_net, prev = 0, 0, 0
    for n in range(1, max_k + 3):   # au-delà, coût marginal = coût plein > revenu
        net = unit_revenue * n - buy(n)
        if net > best_net:
            best_net, best_n = net, n
        if n > 1 and net < prev:
            break
        prev = net
    return {
        "bank_unit_cost": bank_unit_cost,
        "bank_unit_margin": bank_unit_margin,
        "bank_buy_profitable": bank_unit_margin > 0,
        "max_profitable_crafts": best_n,
        "max_profit_total": best_net,
        "bank_unbounded": False,
    }


def compute_pa_brisage(
        targets: List[dict],
        stock: Dict[int, int],
        price_map: Dict[int, Optional[int]],
        coef: float = DEFAULT_COEF,
        ga_pa_price: Optional[int] = None,
        cost_map: Optional[Dict[int, dict]] = None,
) -> List[PaBrisageRow]:
    """Calcule, par item visé : taux d'obtention Ga Pa (formule de brisage),
    crafts possibles (stock banque), coût marché des ingrédients, Ga Pa attendues
    et kamas (bruts / nets). Fonction PURE.

    - ``stock``       = {item_id: quantité en banque}.
    - ``price_map``   = {item_id: prix effectif unitaire ou None}.
    - ``coef``        = coefficient de brisage serveur, en % (cf. ``ga_pa_rate``).
    - ``ga_pa_price`` = prix unitaire de revente de la Ga Pa (None/0 -> 0 kamas).
    - ``cost_map``    = coûts d'appro optimaux ``min(achat, craft)`` par item
                        (cf. ``effective_costs``) ; si None, chaque ingrédient est
                        valorisé au seul prix HDV de ``price_map``.

    Un ingrédient sans prix connu rend la recette NON valorisée (``priced=False``,
    ``unit_cost``/``total_cost``/``net_kamas`` = None) : on ne devine aucun prix,
    mais on affiche quand même crafts et Ga Pa (l'obtention ne dépend pas du prix).
    """
    price = ga_pa_price or 0
    rows: List[PaBrisageRow] = []
    for t in targets:
        recipe = t["recipe"]

        # Crafts possibles = min sur les ingrédients DIRECTS (cf. compute_craftable).
        craftable = 0
        limiting_id: Optional[int] = None
        limiting_name: Optional[str] = None
        if recipe:
            best: Optional[int] = None
            for ing in recipe:
                qn = ing["quantity"]
                if qn <= 0:
                    continue
                possible = stock.get(ing["item_id"], 0) // qn
                if best is None or possible < best:
                    best = possible
                    limiting_id = ing["item_id"]
                    limiting_name = ing["name"]
            craftable = best or 0

        ingredients: List[BrisageIngredient] = []
        unit_cost = 0
        priced = bool(recipe)
        for ing in recipe:
            iid = ing["item_id"]
            buy = price_map.get(iid)
            if cost_map is not None:
                eff = cost_map.get(iid) or {}
                up = eff.get("cost")
                craft_c = eff.get("craft")
                src = eff.get("source")
            else:
                up, craft_c, src = buy, None, ("buy" if buy is not None else None)
            if up is None:
                priced = False
            else:
                unit_cost += up * ing["quantity"]
            ingredients.append(BrisageIngredient(
                item_id=iid, name=ing["name"], quantity=ing["quantity"],
                available=stock.get(iid, 0), unit_price=up,
                buy_price=buy, craft_cost=craft_c, source=src,
            ))

        unit_cost_val: Optional[int] = unit_cost if priced else None
        total_cost: Optional[int] = unit_cost * craftable if priced else None

        pa = t["pa_value"]
        rate = ga_pa_rate(t["level"], pa, coef)   # Ga Pa par objet brisé (dépend du niveau)
        expected = craftable * rate
        gross = int(round(expected * price))
        net: Optional[int] = (gross - total_cost) if total_cost is not None else None

        # Rentabilité « acheter les ressources pour 1 craft puis briser » : on
        # valorise TOUTES les ressources au prix marché (coût d'opportunité), donc
        # acheter ce qui manque ne change pas l'arbitrage. Marge = revenu de
        # brisage d'1 objet − coût marché de ses ingrédients.
        unit_rev = int(round(rate * price))
        unit_margin: Optional[int] = (unit_rev - unit_cost_val) if unit_cost_val is not None else None
        margin_pct: Optional[float] = (round(unit_margin / unit_cost_val * 100, 1)
                                       if unit_cost_val else None)
        buy_profitable: Optional[bool] = (unit_margin > 0) if unit_margin is not None else None

        # Prix d'achat unitaire MAX rentable, par ingrédient : au-delà, 1 craft n'est
        # plus rentable (les AUTRES ingrédients étant à leur coût effectif). Le prix
        # HDV fluctuant, c'est le plafond à ne pas dépasser à l'achat :
        #     max_i = (revenu − coût des autres ingrédients) / quantité_i
        # Calculé seulement si tous les AUTRES ingrédients ont un prix connu.
        n_unpriced = sum(1 for ing in ingredients if ing.unit_price is None)
        sum_priced = sum((ing.unit_price or 0) * ing.quantity
                         for ing in ingredients if ing.unit_price is not None)
        for ing in ingredients:
            others_unpriced = n_unpriced - (1 if ing.unit_price is None else 0)
            if ing.quantity <= 0 or others_unpriced > 0:
                ing.max_unit_price = None
                continue
            own = (ing.unit_price or 0) * ing.quantity if ing.unit_price is not None else 0
            others_cost = sum_priced - own
            ceil = (unit_rev - others_cost) // ing.quantity
            ing.max_unit_price = ceil if ceil > 0 else 0

        # Scénario « banque gratuite » : max de crafts rentables en épuisant le stock.
        bank = _bank_scenario(ingredients, unit_rev) or {}

        rows.append(PaBrisageRow(
            item_id=t["item_id"], name=t["name"], level=t["level"], type=t["type"],
            pa_value=pa, craftable_now=craftable,
            limiting_item_id=limiting_id, limiting_item_name=limiting_name,
            unit_cost=unit_cost_val, total_cost=total_cost, priced=priced,
            ga_pa_rate=round(rate, 4), expected_ga_pa=round(expected, 2),
            gross_kamas=gross, net_kamas=net,
            unit_revenue=unit_rev, unit_margin=unit_margin, margin_pct=margin_pct,
            buy_profitable=buy_profitable,
            bank_unit_cost=bank.get("bank_unit_cost"),
            bank_unit_margin=bank.get("bank_unit_margin"),
            bank_buy_profitable=bank.get("bank_buy_profitable"),
            max_profitable_crafts=bank.get("max_profitable_crafts"),
            max_profit_total=bank.get("max_profit_total"),
            bank_unbounded=bank.get("bank_unbounded", False),
            ingredients=ingredients,
        ))
    return rows
