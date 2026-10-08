"""Suivi de build : items cibles à crafter + agrégation des ressources + arbres de craft.

- build_targets : liste d'items à fabriquer (quantité éditable).
- build_manual  : quantités "acquises" à la main (achat/farm hors banque).
- get_build_resources(expand) : ingrédients DIRECTS (défaut) ou décomposés
  jusqu'aux ressources brutes (expand=True), vs banque + acquis.
- get_build_trees : arbre de craft récursif (sous-crafts développés).
"""
from __future__ import annotations

from psycopg2.extras import execute_values
from typing import Dict, List


def set_build_targets(cur, targets: List[dict]) -> int:
    cur.execute("TRUNCATE build_targets RESTART IDENTITY")
    rows = [(t.get("label"), int(t["item_id"]), int(t.get("quantity", 1)))
            for t in targets if t.get("item_id")]
    if rows:
        execute_values(cur, "INSERT INTO build_targets (label, item_id, quantity) VALUES %s", rows)
    return len(rows)


def update_target_quantity(cur, target_id: int, quantity: int) -> None:
    cur.execute("UPDATE build_targets SET quantity = %s WHERE id = %s", (max(0, int(quantity)), int(target_id)))


def set_manual(cur, item_id: int, quantity: int) -> int:
    q = max(0, int(quantity))
    cur.execute(
        """
        INSERT INTO build_manual (item_id, quantity)
        VALUES (%s, %s) ON CONFLICT (item_id) DO
        UPDATE SET quantity = EXCLUDED.quantity
        """,
        (int(item_id), q),
    )
    return q


def get_build_targets(cur) -> List[dict]:
    cur.execute(
        """
        SELECT bt.id,
               bt.label,
               bt.item_id,
               i.name,
               i.type,
               i.level,
               i.icon,
               bt.quantity
        FROM build_targets bt
                 JOIN items i ON i.item_id = bt.item_id
        ORDER BY bt.id
        """
    )
    return [dict(r) for r in cur.fetchall()]


def _recipe_index(cur) -> Dict[int, list]:
    """{result_item_id: [{item_id, name, icon, quantity, craftable}, ...]}."""
    cur.execute(
        """
        SELECT r.result_item_id,
               ing.item_id,
               ing.name,
               ing.icon,
               ri.quantity,
               EXISTS (SELECT 1 FROM recipes r2 WHERE r2.result_item_id = ing.item_id) AS craftable
        FROM recipes r
                 JOIN recipe_ingredients ri ON ri.recipe_id = r.recipe_id
                 JOIN items ing ON ing.item_id = ri.ingredient_item_id
        ORDER BY r.result_item_id, ing.name
        """
    )
    idx: Dict[int, list] = {}
    for row in cur.fetchall():
        idx.setdefault(row["result_item_id"], []).append({
            "item_id": row["item_id"], "name": row["name"], "icon": row["icon"],
            "quantity": row["quantity"], "craftable": row["craftable"],
        })
    return idx


def _accumulate_base(idx, item_id, qty, out, seen, depth):
    """Développe récursivement un ingrédient craftable jusqu'aux ressources brutes."""
    ings = idx.get(item_id)
    if ings and depth > 0 and item_id not in seen:
        for ing in ings:
            _accumulate_base(idx, ing["item_id"], qty * ing["quantity"], out, seen | {item_id}, depth - 1)
    else:
        out[item_id] = out.get(item_id, 0) + qty


def _finalize(cur, need: Dict[int, int]) -> List[dict]:
    """Croise un dict {item_id: needed} avec banque (tous comptes) + acquis manuels."""
    if not need:
        return []
    ids = list(need.keys())
    cur.execute(
        """
        SELECT i.item_id,
               i.name,
               i.type,
               i.icon,
               COALESCE(bk.qty, 0)                                                 AS in_bank,
               COALESCE(m.quantity, 0)                                             AS acquired,
               EXISTS (SELECT 1 FROM recipes r WHERE r.result_item_id = i.item_id) AS craftable
        FROM items i
                 LEFT JOIN (SELECT item_id, SUM(quantity) ::bigint AS qty FROM bank_inventory GROUP BY item_id) bk
                           ON bk.item_id = i.item_id
                 LEFT JOIN build_manual m ON m.item_id = i.item_id
        WHERE i.item_id = ANY (%s)
        """,
        (ids,),
    )
    rows = []
    for r in cur.fetchall():
        d = dict(r)
        d["needed"] = need[r["item_id"]]
        have = d["in_bank"] + d["acquired"]
        d["have"] = have
        d["remaining"] = max(0, d["needed"] - have)
        d["pct"] = round(min(100, 100 * have / d["needed"])) if d["needed"] else 100
        rows.append(d)
    rows.sort(key=lambda d: (-d["remaining"], d["name"]))
    return rows


def get_build_resources(cur, expand: bool = False) -> List[dict]:
    """Ressources nécessaires vs banque + acquis.

    expand=False : ingrédients directs des cibles (les sous-crafts apparaissent
                   comme lignes 'craftable').
    expand=True  : décompose les sous-crafts jusqu'aux ressources brutes.
    """
    if expand:
        idx = _recipe_index(cur)
        cur.execute("SELECT item_id, quantity FROM build_targets")
        need: Dict[int, int] = {}
        for row in cur.fetchall():
            for ing in idx.get(row["item_id"], []):
                _accumulate_base(idx, ing["item_id"], ing["quantity"] * row["quantity"], need, {row["item_id"]}, 8)
        return _finalize(cur, need)

    cur.execute(
        """
        SELECT ri.ingredient_item_id AS item_id,
               SUM(ri.quantity * bt.quantity) ::bigint AS needed
        FROM build_targets bt
                 JOIN recipes r ON r.result_item_id = bt.item_id
                 JOIN recipe_ingredients ri ON ri.recipe_id = r.recipe_id
        GROUP BY ri.ingredient_item_id
        """
    )
    need = {r["item_id"]: r["needed"] for r in cur.fetchall()}
    return _finalize(cur, need)


def get_build_trees(cur, max_depth: int = 5) -> List[dict]:
    """Pour chaque cible : arbre de craft (recette + sous-crafts en cascade)."""
    idx = _recipe_index(cur)
    cur.execute(
        """
        SELECT bt.item_id, i.name, i.icon, bt.quantity, bt.label
        FROM build_targets bt
                 JOIN items i ON i.item_id = bt.item_id
        ORDER BY bt.id
        """
    )
    out = []
    for r in cur.fetchall():
        tree = _expand_tree(idx, r["item_id"], r["name"], r["icon"], max_depth, set())
        tree["quantity"] = r["quantity"]
        tree["label"] = r["label"]
        out.append(tree)
    return out


def _expand_tree(idx, item_id, name, icon, depth, seen):
    node = {"item_id": item_id, "name": name, "icon": icon}
    ings = idx.get(item_id)
    if ings and depth > 0 and item_id not in seen:
        node["ingredients"] = []
        for ing in ings:
            child = _expand_tree(idx, ing["item_id"], ing["name"], ing["icon"], depth - 1, seen | {item_id})
            child["quantity"] = ing["quantity"]
            child["craftable"] = ing["craftable"]
            node["ingredients"].append(child)
    return node
