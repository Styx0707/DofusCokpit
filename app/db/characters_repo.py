"""Repository des personnages et de leur équipement (multi-comptes).

Équipement visible (ALK, sans slots/jets) ou complet (ASK, slots + jets réels).
"""
from __future__ import annotations

from psycopg2.extras import execute_values
from typing import List, Optional

from app.network.protocol import decode_effects


def replace_account_characters(cur, account: str, characters: List[dict]) -> int:
    """Remplace tout le roster d'un compte (équipement VISIBLE, sans slots)."""
    cur.execute("DELETE FROM characters WHERE account = %s", (account,))
    if not characters:
        return 0
    execute_values(
        cur,
        """
        INSERT INTO characters (account, character_id, name, level, class_id, class_name, sex)
        VALUES %s
        """,
        [(account, c["character_id"], c["name"], c.get("level"),
          c.get("class_id"), c.get("class_name"), c.get("sex")) for c in characters],
    )
    equipment = [
        (account, c["character_id"], slot, gid, None, None, None)
        for c in characters
        for slot, gid in enumerate(c.get("equipment", []))
    ]
    if equipment:
        execute_values(
            cur,
            """
            INSERT INTO character_equipment
                (account, character_id, slot_index, item_id, slot, slot_name, stats)
            VALUES %s
            """,
            equipment,
        )
    return len(characters)


def get_account_for_character(cur, character_id: int) -> Optional[str]:
    cur.execute("SELECT account FROM characters WHERE character_id = %s LIMIT 1", (character_id,))
    row = cur.fetchone()
    return row["account"] if row else None


def replace_character_full_equipment(cur, account: str, char: dict) -> int:
    """Écrit l'équipement COMPLET (slots + jets) d'un perso, depuis un ASK."""
    cur.execute(
        """
        INSERT INTO characters (account, character_id, name, level, class_id, class_name, sex)
        VALUES (%s, %s, %s, %s, %s, %s, %s) ON CONFLICT (account, character_id) DO
        UPDATE SET
            name = EXCLUDED.name, level = EXCLUDED.level,
            class_id = EXCLUDED.class_id, class_name = EXCLUDED.class_name, sex = EXCLUDED.sex
        """,
        (account, char["character_id"], char["name"], char.get("level"),
         char.get("class_id"), char.get("class_name"), char.get("sex")),
    )
    cur.execute(
        "DELETE FROM character_equipment WHERE account = %s AND character_id = %s",
        (account, char["character_id"]),
    )
    rows = [
        (account, char["character_id"], e["slot"], e["item_id"], e["slot"], e["slot_name"], e.get("stats"))
        for e in char.get("equipment", [])
    ]
    if rows:
        execute_values(
            cur,
            """
            INSERT INTO character_equipment
                (account, character_id, slot_index, item_id, slot, slot_name, stats)
            VALUES %s
            """,
            rows,
        )
    return len(rows)


def get_roster(cur) -> List[dict]:
    """Roster groupé, avec équipement + jets décodés + icône pour les persos complets."""
    cur.execute(
        """
        SELECT c.account,
               c.character_id,
               c.name,
               c.level,
               c.class_name,
               c.sex,
               ce.slot_index,
               ce.slot,
               ce.slot_name,
               ce.stats,
               ce.item_id,
               i.name AS item_name,
               i.icon AS item_icon
        FROM characters c
                 LEFT JOIN character_equipment ce
                           ON ce.account = c.account AND ce.character_id = c.character_id
                 LEFT JOIN items i ON i.item_id = ce.item_id
        ORDER BY c.account, c.level DESC, c.character_id,
                 COALESCE(ce.slot, ce.slot_index)
        """
    )
    accounts: dict = {}
    chars: dict = {}
    for r in cur.fetchall():
        acc = accounts.setdefault(r["account"], {"account": r["account"], "characters": []})
        ckey = (r["account"], r["character_id"])
        char = chars.get(ckey)
        if char is None:
            char = {
                "character_id": r["character_id"], "name": r["name"], "level": r["level"],
                "class_name": r["class_name"], "sex": r["sex"], "full": False, "equipment": [],
            }
            chars[ckey] = char
            acc["characters"].append(char)
        if r["item_id"] is not None:
            if r["slot"] is not None:
                char["full"] = True
            char["equipment"].append({
                "item_id": r["item_id"],
                "name": r["item_name"] or f"Objet #{r['item_id']}",
                "icon": r["item_icon"],
                "slot": r["slot"],
                "slot_name": r["slot_name"],
                "effects": decode_effects(r["stats"]) if r["stats"] else [],
            })
    return list(accounts.values())
