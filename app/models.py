"""Modèles de domaine.

Dataclasses volontairement « plates » : sérialisables en JSON via
``dataclasses.asdict()`` sans adaptateur, prêtes pour une future API REST.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass
class Item:
    item_id: int
    name: str
    type: Optional[str] = None  # catégorie (Anneau, Amulette, Alliage, …)
    level: Optional[int] = None
    price: Optional[int] = None  # prix vendeur


@dataclass
class Ingredient:
    item_id: int
    name: str
    quantity: int


@dataclass
class Recipe:
    recipe_id: int
    result_item_id: int
    result_name: str
    result_quantity: int
    ingredients: List[Ingredient] = field(default_factory=list)


@dataclass
class StockEntry:
    item_id: int
    name: str
    quantity: int


@dataclass
class CraftableRecipe:
    """Résultat du calcul « en isolation » (une recette vs tout le stock)."""
    recipe_id: int
    result_item_id: int
    result_name: str
    max_crafts: int
    result_quantity_total: int  # max_crafts * result_quantity
    limiting_item_id: Optional[int]  # ingrédient qui plafonne le craft
    limiting_item_name: Optional[str]


@dataclass
class MissingIngredient:
    """Ressource qui manque pour fabriquer UNE fois une recette."""
    item_id: int
    name: str
    needed: int       # requis pour 1 craft
    available: int    # en stock (banque + agrégé)
    missing: int      # needed - available (> 0)


@dataclass
class NearCraftableRecipe:
    """Recette NON fabricable mais « à portée » : il ne manque que quelques
    ressources distinctes (shortfall calculé pour 1 craft)."""
    recipe_id: int
    result_item_id: int
    result_name: str
    result_quantity: int
    missing: List[MissingIngredient] = field(default_factory=list)
    missing_kinds: int = 0   # nb de ressources DISTINCTES manquantes (0 = déjà fabricable)
    missing_total: int = 0   # somme des quantités manquantes
    max_crafts: int = 0      # si déjà fabricable : nb de crafts possibles (sinon 0)


@dataclass
class MissingBuy:
    """Ressource manquante à ACHETER pour fabriquer 1 fois (stock déjà déduit)."""
    item_id: int
    name: str
    missing: int       # quantité à acheter (needed - available, > 0)
    unit_price: int    # prix effectif unitaire
    buy_cost: int      # missing * unit_price


@dataclass
class StockPull:
    """Ressource déjà POSSÉDÉE à retirer de la banque pour fabriquer 1 fois."""
    item_id: int
    name: str
    qty: int           # quantité prélevée sur le stock = min(needed, available)
    unit_price: int    # prix effectif unitaire
    value: int         # qty * unit_price (valeur marché de ce qu'on sort)


@dataclass
class ProfitableCraft:
    """Rentabilité d'une recette : revente du produit − coût MARCHÉ des
    ingrédients, au prix effectif (``market_price`` sinon prix vendeur)."""
    recipe_id: int
    result_item_id: int
    result_name: str
    result_quantity: int
    unit_cost: int             # coût de TOUS les ingrédients pour 1 craft
    unit_revenue: int          # revente du produit (result_quantity * prix)
    unit_profit: int           # unit_revenue - unit_cost (marge si tout acheté)
    margin_pct: Optional[float]  # unit_profit / unit_cost * 100 (None si coût 0)
    craftable_now: int         # nb de crafts possibles avec le stock courant
    missing_buy_cost: int      # coût d'achat des SEULES ressources manquantes (1 craft)
    profit_after_missing: int  # unit_revenue - missing_buy_cost (stock possédé = gratuit)
    missing: List[MissingBuy] = field(default_factory=list)   # ressources à ACHETER
    from_stock: List[StockPull] = field(default_factory=list)  # ressources à RETIRER en banque


@dataclass
class CraftStep:
    """Une étape du plan glouton (stock virtuel)."""
    recipe_id: int
    result_item_id: int
    result_name: str
    crafted: int
    consumed: Dict[int, int] = field(default_factory=dict)  # {item_id: quantité déduite}


@dataclass
class CraftPlan:
    steps: List[CraftStep] = field(default_factory=list)
    remaining_stock: Dict[int, int] = field(default_factory=dict)  # {item_id: quantité restante}


@dataclass
class BrisageIngredient:
    """Ingrédient d'une recette de brisage, enrichi du stock et du coût d'appro."""
    item_id: int
    name: str
    quantity: int               # requis pour 1 craft
    available: int              # en banque (tous comptes)
    unit_price: Optional[int]   # coût d'appro EFFECTIF retenu = min(achat, craft) (None si inconnu)
    buy_price: Optional[int] = None    # prix d'achat HDV (effectif marché/vendeur)
    craft_cost: Optional[int] = None   # coût de craft récursif (None si non craftable/valorisable)
    source: Optional[str] = None       # "buy" ou "craft" : option retenue (la moins chère)
    max_unit_price: Optional[int] = None  # prix d'achat unitaire MAX rentable (au-delà, 1 craft n'est plus rentable)


@dataclass
class PaBrisageRow:
    """Ligne « craft-pour-briser » : un équipement +PA et sa rentabilité en
    Rune Ga Pa (voir ``app.core.brisage``)."""
    item_id: int
    name: str
    level: Optional[int]
    type: Optional[str]
    pa_value: int                       # +N PA de l'objet (1 pour tous les items visés)
    craftable_now: int                  # crafts possibles avec le stock de banque
    limiting_item_id: Optional[int]     # ingrédient qui plafonne le craft
    limiting_item_name: Optional[str]
    unit_cost: Optional[int]            # coût marché des ingrédients pour 1 craft (None si non valorisable)
    total_cost: Optional[int]           # unit_cost * craftable_now
    priced: bool                        # tous les ingrédients ont un prix connu
    ga_pa_rate: float                   # taux d'obtention Ga Pa / objet brisé (formule de brisage, ≈ quadratique en niveau)
    expected_ga_pa: float               # Ga Pa attendues = craftable_now * ga_pa_rate
    gross_kamas: int                    # expected_ga_pa * prix_unitaire_Ga_Pa
    net_kamas: Optional[int]            # gross_kamas - total_cost (None si non valorisable)
    # Rentabilité « acheter les ressources pour crafter+briser », par craft :
    unit_revenue: int                   # kamas de brisage pour 1 craft = ga_pa_rate * prix_Ga_Pa
    unit_margin: Optional[int]          # unit_revenue - unit_cost (marge à l'achat ; None si non valorisable)
    margin_pct: Optional[float]         # unit_margin / unit_cost * 100
    buy_profitable: Optional[bool]      # True si rentable d'acheter les ressources (unit_margin > 0)
    # Scénario « stock banque gratuit » : les ressources déjà en banque ne comptent
    # pas, on n'achète que le manquant, et on maximise le nb de crafts rentables.
    bank_unit_cost: Optional[int] = None       # coût d'achat du SEUL manquant pour 1 craft (banque gratuite)
    bank_unit_margin: Optional[int] = None     # unit_revenue - bank_unit_cost
    bank_buy_profitable: Optional[bool] = None  # True si le 1er craft (banque) est rentable
    max_profitable_crafts: Optional[int] = None  # nb de crafts rentables en épuisant la banque (None = illimité/inconnu)
    max_profit_total: Optional[int] = None      # profit total à ce nb de crafts (None = illimité/inconnu)
    bank_unbounded: bool = False               # True = rentable même en rachetant tout -> crafts illimités
    ingredients: List[BrisageIngredient] = field(default_factory=list)


@dataclass
class FarmSpot:
    """Piste de farm pour une ressource : un lieu (zone) ou un monstre, avec la
    raison du rapprochement et un indice de confiance."""
    label: str                          # nom de la zone ou du monstre
    kind: str                           # "zone" ou "monster"
    via: str                            # provenance : "drop" (table xixou, fiable), "live"
    #                                     (sniffer), "nom de zone" / "nom de monstre" (heuristique)
    rate: Optional[int] = None          # taux de drop en % (si via == "drop" et kind == "monster")


@dataclass
class FarmResource:
    """Ressource-feuille (matière première) à réunir pour les crafts de brisage,
    avec sa source (métier de récolte / butin) et où la farmer (cf. ``app.core.farm``)."""
    item_id: int
    name: str
    type: Optional[str]
    qty_needed: int                     # quantité totale pour le plan (toutes cibles)
    in_bank: int                        # déjà en banque
    to_buy: int                         # manquant = max(0, qty_needed - in_bank)
    unit_price: Optional[int]           # prix d'appro unitaire (HDV) ; None si inconnu
    buy_cost: Optional[int]             # coût d'achat du manquant = to_buy * unit_price
    source_kind: str                    # "harvest" (récolte métier), "drop" (butin), "unknown"
    profession: Optional[str]           # métier de récolte si source_kind == "harvest"
    spots: List[FarmSpot] = field(default_factory=list)   # pistes de farm (zones / monstres)
    used_in: List[int] = field(default_factory=list)      # item_ids des cibles qui l'utilisent
