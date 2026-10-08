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
