"""Couche d'accès aux données (Repository Pattern).

Règles :
- Chaque fonction reçoit un curseur (fourni par ``app.db.connection.transaction``)
  et ne gère donc pas elle-même commit/rollback : c'est l'appelant qui décide
  du périmètre transactionnel.
- Requêtes exclusivement paramétrées (pas de f-string dans le SQL).
- Retour en dataclasses / types simples -> sérialisables JSON.
"""
from __future__ import annotations

import logging
from psycopg2.extras import execute_values
from typing import Dict, Iterable, List, Optional

from app.models import Ingredient, Item, Recipe, StockEntry

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Écriture — dictionnaire d'objets
# ---------------------------------------------------------------------------

def upsert_items(cur, items: Iterable[Item]) -> int:
    """Insère ou met à jour le dictionnaire d'objets (nom + métadonnées).

    COALESCE : une métadonnée non fournie (None) n'écrase PAS la valeur
    existante -> on peut seeder les noms puis enrichir type/level/price.
    """
    rows = [(it.item_id, it.name, it.type, it.level, it.price) for it in items]
    if not rows:
        return 0
    execute_values(
        cur,
        """
        INSERT INTO items (item_id, name, type, level, price)
        VALUES %s ON CONFLICT (item_id) DO
        UPDATE SET
            name = EXCLUDED.name,
            type = COALESCE (EXCLUDED.type, items.type),
            level = COALESCE (EXCLUDED.level, items.level),
            price = COALESCE (EXCLUDED.price, items.price)
        """,
        rows,
    )
    return len(rows)


def _ensure_items_exist(cur, item_ids: Iterable[int]) -> None:
    """Garantit l'intégrité référentielle avant d'écrire dans bank_inventory.

    Les objets inconnus (découverts par le sniffer) sont créés avec un nom
    provisoire, à compléter ensuite via ``upsert_items`` depuis un dump du jeu.
    """
    rows = [(item_id, f"Objet #{item_id}") for item_id in item_ids]
    if not rows:
        return
    execute_values(
        cur,
        """
        INSERT INTO items (item_id, name)
        VALUES %s ON CONFLICT (item_id) DO NOTHING
        """,
        rows,
    )


# ---------------------------------------------------------------------------
# Écriture — recettes
# ---------------------------------------------------------------------------

def upsert_recipe(
        cur,
        result_item_id: int,
        ingredients: Dict[int, int],
        result_quantity: int = 1,
) -> int:
    """Crée ou met à jour une recette et remplace ses ingrédients.

    `ingredients` = {ingredient_item_id: quantity}. Suppose que les objets
    (résultat + ingrédients) existent déjà dans `items` (voir upsert_items).
    Renvoie le recipe_id. À exécuter dans une transaction.
    """
    _ensure_items_exist(cur, [result_item_id, *ingredients.keys()])
    cur.execute(
        """
        INSERT INTO recipes (result_item_id, result_quantity)
        VALUES (%s, %s) ON CONFLICT (result_item_id)
        DO
        UPDATE SET result_quantity = EXCLUDED.result_quantity
            RETURNING recipe_id
        """,
        (result_item_id, result_quantity),
    )
    recipe_id = cur.fetchone()["recipe_id"]

    cur.execute("DELETE FROM recipe_ingredients WHERE recipe_id = %s", (recipe_id,))
    rows = [(recipe_id, iid, qty) for iid, qty in ingredients.items() if qty > 0]
    if rows:
        execute_values(
            cur,
            """
            INSERT INTO recipe_ingredients (recipe_id, ingredient_item_id, quantity)
            VALUES %s
            """,
            rows,
        )
    return recipe_id


# ---------------------------------------------------------------------------
# Écriture — stats d'objet
# ---------------------------------------------------------------------------

def replace_item_stats(cur, rows: Iterable[tuple]) -> int:
    """Remplace toute la table item_stats.

    `rows` = itérable de (item_id, stat, is_percent, value_min, value_max).
    """
    rows = list(rows)
    cur.execute("TRUNCATE item_stats")
    if rows:
        execute_values(
            cur,
            """
            INSERT INTO item_stats (item_id, stat, is_percent, value_min, value_max)
            VALUES %s
            """,
            rows,
        )
    return len(rows)


# ---------------------------------------------------------------------------
# Écriture — inventaire de banque (multi-comptes)
# ---------------------------------------------------------------------------

def upsert_bank_inventory(cur, inventory: Dict[int, int], account: str = "main") -> int:
    """Insert-or-update de la banque d'UN compte depuis {item_id: quantity}.

    Ne supprime PAS les objets absents (mise à jour partielle du compte).
    """
    if not inventory:
        return 0
    _ensure_items_exist(cur, inventory.keys())
    rows = [(account, item_id, quantity) for item_id, quantity in inventory.items()]
    execute_values(
        cur,
        """
        INSERT INTO bank_inventory (account, item_id, quantity, updated_at)
        VALUES %s ON CONFLICT (account, item_id)
        DO
        UPDATE SET quantity = EXCLUDED.quantity,
            updated_at = now()
        """,
        rows,
        template="(%s, %s, %s, now())",
    )
    logger.info("Upsert banque [%s] : %d objets.", account, len(rows))
    return len(rows)


def replace_bank_inventory(cur, inventory: Dict[int, int], account: str = "main") -> int:
    """Remplace INTÉGRALEMENT la banque d'UN compte (scan complet).

    N'affecte que le compte visé (les autres comptes sont préservés).
    """
    cur.execute("DELETE FROM bank_inventory WHERE account = %s", (account,))
    return upsert_bank_inventory(cur, inventory, account)


def upsert_market_prices(cur, prices: Dict[int, int]) -> int:
    """Met à jour le prix MARCHÉ (``market_price``) + ``price_updated_at`` depuis
    ``{item_id: prix_unitaire}`` (prix HDV captés via dump). N'insère pas d'items
    inconnus (UPDATE only). Prix <= 0 ignorés. Retourne le nb de lignes touchées."""
    rows = [(int(iid), int(p)) for iid, p in prices.items() if p and int(p) > 0]
    if not rows:
        return 0
    execute_values(
        cur,
        """
        UPDATE items AS i
        SET market_price = v.price, price_updated_at = now()
        FROM (VALUES %s) AS v(item_id, price)
        WHERE i.item_id = v.item_id
        """,
        rows,
    )
    logger.info("Prix marché (HDV) : %d objets mis à jour.", cur.rowcount)
    return cur.rowcount


# ---------------------------------------------------------------------------
# Lecture
# ---------------------------------------------------------------------------

def get_full_stock(cur, account: Optional[str] = None) -> List[StockEntry]:
    """Stock (quantités > 0). account=None -> AGRÉGÉ sur tous les comptes."""
    if account is None:
        cur.execute(
            """
            SELECT bi.item_id, i.name, SUM(bi.quantity) ::bigint AS quantity
            FROM bank_inventory bi
                     JOIN items i ON i.item_id = bi.item_id
            GROUP BY bi.item_id, i.name
            HAVING SUM(bi.quantity) > 0
            ORDER BY i.name
            """
        )
    else:
        cur.execute(
            """
            SELECT bi.item_id, i.name, bi.quantity
            FROM bank_inventory bi
                     JOIN items i ON i.item_id = bi.item_id
            WHERE bi.account = %s
              AND bi.quantity > 0
            ORDER BY i.name
            """,
            (account,),
        )
    return [StockEntry(item_id=r["item_id"], name=r["name"], quantity=r["quantity"]) for r in cur.fetchall()]


def get_consolidated_summary(cur) -> List[dict]:
    """Par objet : quantité totale (tous comptes) + répartition par compte."""
    cur.execute(
        """
        SELECT bi.item_id,
               i.name,
               i.type,
               i.level,
               COALESCE(i.market_price, i.price) AS price,
               bi.account,
               bi.quantity
        FROM bank_inventory bi
                 JOIN items i ON i.item_id = bi.item_id
        WHERE bi.quantity > 0
        ORDER BY i.name
        """
    )
    agg: Dict[int, dict] = {}
    for r in cur.fetchall():
        row = agg.get(r["item_id"])
        if row is None:
            row = {
                "item_id": r["item_id"],
                "name": r["name"],
                "type": r["type"],
                "level": r["level"],
                "unit_price": r["price"],
                "total_quantity": 0,
                "accounts": {},
            }
            agg[r["item_id"]] = row
        row["total_quantity"] += r["quantity"]
        row["accounts"][r["account"]] = r["quantity"]
    for row in agg.values():
        row["total_value"] = (row["unit_price"] or 0) * row["total_quantity"]
        row["n_accounts"] = len(row["accounts"])
    return list(agg.values())


def get_accounts_summary(cur) -> List[dict]:
    """Par compte : nb d'objets distincts, quantité totale, valeur totale."""
    cur.execute(
        """
        SELECT bi.account,
               COUNT(*)::int                                  AS n_items, SUM(bi.quantity)::bigint                        AS total_quantity, SUM(bi.quantity * COALESCE(i.market_price, i.price, 0)) ::bigint AS total_value
        FROM bank_inventory bi
                 JOIN items i ON i.item_id = bi.item_id
        WHERE bi.quantity > 0
        GROUP BY bi.account
        ORDER BY total_value DESC, bi.account
        """
    )
    return [dict(r) for r in cur.fetchall()]


def get_bank_detail(cur, account: Optional[str] = None) -> List[dict]:
    """Banque ENRICHIE pour le tableau de bord : icône, type, niveau, quantité,
    prix vendeur + prix marché + prix effectif (COALESCE), valeur de ligne et date
    de MAJ du prix. ``account=None`` -> agrégé tous comptes. Trié par valeur desc."""
    if account is None:
        cur.execute(
            """
            SELECT i.item_id, i.name, i.type, i.level, i.icon,
                   i.price                            AS vendor_price,
                   i.market_price                     AS market_price,
                   COALESCE(i.market_price, i.price)  AS unit_price,
                   i.price_updated_at                 AS price_updated_at,
                   SUM(bi.quantity)::bigint           AS quantity
            FROM bank_inventory bi
                     JOIN items i ON i.item_id = bi.item_id
            GROUP BY i.item_id, i.name, i.type, i.level, i.icon,
                     i.price, i.market_price, i.price_updated_at
            HAVING SUM(bi.quantity) > 0
            """
        )
    else:
        cur.execute(
            """
            SELECT i.item_id, i.name, i.type, i.level, i.icon,
                   i.price                            AS vendor_price,
                   i.market_price                     AS market_price,
                   COALESCE(i.market_price, i.price)  AS unit_price,
                   i.price_updated_at                 AS price_updated_at,
                   bi.quantity                        AS quantity
            FROM bank_inventory bi
                     JOIN items i ON i.item_id = bi.item_id
            WHERE bi.account = %s AND bi.quantity > 0
            """,
            (account,),
        )
    rows = []
    for r in cur.fetchall():
        d = dict(r)
        d["line_value"] = (d["unit_price"] or 0) * d["quantity"]
        d["priced"] = d["market_price"] is not None
        d["price_updated_at"] = d["price_updated_at"].isoformat() if d["price_updated_at"] else None
        rows.append(d)
    rows.sort(key=lambda d: (-d["line_value"], d["name"]))
    return rows


def get_bank_status(cur) -> dict:
    """Résumé express de la banque (page Démarrage / statut) : nb d'objets,
    quantité totale, valeur estimée, date de dernière MAJ, nb d'objets avec prix
    marché connu."""
    cur.execute(
        """
        SELECT COUNT(*)::int                                                           AS items,
               COALESCE(SUM(bi.quantity), 0)::bigint                                   AS total_qty,
               COALESCE(SUM(bi.quantity * COALESCE(i.market_price, i.price, 0)), 0)::bigint AS total_value,
               MAX(bi.updated_at)                                                      AS last_update
        FROM bank_inventory bi
                 JOIN items i USING (item_id)
        WHERE bi.quantity > 0
        """
    )
    r = dict(cur.fetchone())
    cur.execute("SELECT COUNT(*)::int AS n FROM items WHERE market_price IS NOT NULL")
    r["priced_items"] = cur.fetchone()["n"]
    r["last_update"] = r["last_update"].isoformat() if r["last_update"] else None
    return r


def get_items_metadata(cur) -> Dict[int, dict]:
    """{item_id: {type, level, price}} — `price` = prix EFFECTIF : prix marché
    (``market_price``) s'il est renseigné, sinon prix vendeur (``price``). Sert à
    enrichir/valoriser côté API (craftable, plans…)."""
    cur.execute("SELECT item_id, type, level, icon, COALESCE(market_price, price) AS price FROM items")
    return {
        r["item_id"]: {"type": r["type"], "level": r["level"], "icon": r["icon"], "price": r["price"]}
        for r in cur.fetchall()
    }


def get_items_with_stat(cur, stat: str) -> Dict[int, list]:
    """{item_id: [{is_percent, value_min, value_max}, ...]} pour un `stat` donné."""
    cur.execute(
        "SELECT item_id, is_percent, value_min, value_max FROM item_stats WHERE stat = %s",
        (stat,),
    )
    out: Dict[int, list] = {}
    for r in cur.fetchall():
        out.setdefault(r["item_id"], []).append({
            "is_percent": r["is_percent"],
            "value_min": r["value_min"],
            "value_max": r["value_max"],
        })
    return out


def get_all_recipes(cur) -> List[Recipe]:
    """Renvoie toutes les recettes avec leurs ingrédients (une requête, regroupée)."""
    cur.execute(
        """
        SELECT r.recipe_id,
               r.result_item_id,
               res.name    AS result_name,
               r.result_quantity,
               ing.item_id AS ingredient_id,
               ing.name    AS ingredient_name,
               ri.quantity AS ingredient_quantity
        FROM recipes r
                 JOIN items res ON res.item_id = r.result_item_id
                 JOIN recipe_ingredients ri ON ri.recipe_id = r.recipe_id
                 JOIN items ing ON ing.item_id = ri.ingredient_item_id
        ORDER BY r.recipe_id, ing.name
        """
    )
    recipes: Dict[int, Recipe] = {}
    for row in cur.fetchall():
        recipe = recipes.get(row["recipe_id"])
        if recipe is None:
            recipe = Recipe(
                recipe_id=row["recipe_id"],
                result_item_id=row["result_item_id"],
                result_name=row["result_name"],
                result_quantity=row["result_quantity"],
            )
            recipes[recipe.recipe_id] = recipe
        recipe.ingredients.append(
            Ingredient(
                item_id=row["ingredient_id"],
                name=row["ingredient_name"],
                quantity=row["ingredient_quantity"],
            )
        )
    return list(recipes.values())
