"""Groupes de comptes (Arène / Farm / …) dans data/account_groups.json.

Simple mapping nom_de_perso -> id_de_groupe, pour le tableau de bord multi-compte
(board.html) : regrouper visuellement les 15 comptes par activité, jongler entre
eux (WinActivate), et limiter l'équipe de donjon au groupe « farm » pour ne pas
déplacer par erreur les comptes d'arène.

Clé = nom de perso (= sous-chaîne de titre de fenêtre, celle qu'utilise
WinActivate), identité stable d'un compte. Écriture atomique, état pur fichier.
"""
from __future__ import annotations

import json
import os
import threading
from typing import Dict

_PATH = os.getenv("ACCOUNT_GROUPS_PATH", "data/account_groups.json")
_RULES_PATH = os.getenv("ACCOUNT_GROUP_RULES_PATH", "data/account_group_rules.json")
_ORDER_PATH = os.getenv("SWEEP_ORDER_PATH", "data/sweep_order.json")
_lock = threading.Lock()


def load_order() -> list:
    """Ordre de balayage personnalisé (liste de noms) — défini par l'utilisateur
    dans board.html, utilisé par le pop-up pour activer les fenêtres dans CET
    ordre (ex. Patriotstyx -> … -> Zhendar)."""
    try:
        with open(_ORDER_PATH, encoding="utf-8") as fh:
            data = json.load(fh)
        return [str(x) for x in data] if isinstance(data, list) else []
    except (OSError, ValueError):
        return []


def save_order(names: list) -> list:
    out = [str(n).strip() for n in (names or []) if str(n).strip()]
    with _lock:
        tmp = _ORDER_PATH + ".tmp"
        os.makedirs(os.path.dirname(_ORDER_PATH) or ".", exist_ok=True)
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=2)
        os.replace(tmp, _ORDER_PATH)
    return out


def load_rules() -> list:
    """Règles d'auto-rangement par motif de nom (évite d'assigner 15 comptes à la
    main). Liste ordonnée ; 1re qui matche gagne. Chaque règle :
      {"prefix"|"suffix"|"contains": "<motif>", "group": "<id>"}
    appliquée au nom SANS le tag de guilde, insensible à la casse. Une assignation
    manuelle (account_groups.json) a toujours priorité sur une règle."""
    try:
        with open(_RULES_PATH, encoding="utf-8") as fh:
            data = json.load(fh)
        return data if isinstance(data, list) else []
    except (OSError, ValueError):
        return []


def save_rules(rules: list) -> list:
    out = []
    for r in (rules or []):
        if not isinstance(r, dict) or not r.get("group"):
            continue
        rule = {"group": str(r["group"]).strip()}
        for k in ("prefix", "suffix", "contains"):
            if r.get(k):
                rule[k] = str(r[k]).strip()
        if len(rule) > 1:   # au moins un critère en plus de group
            out.append(rule)
    with _lock:
        tmp = _RULES_PATH + ".tmp"
        os.makedirs(os.path.dirname(_RULES_PATH) or ".", exist_ok=True)
        with open(tmp, "w", encoding="utf-8") as fh:
            json.dump(out, fh, ensure_ascii=False, indent=2)
        os.replace(tmp, _RULES_PATH)
    return out


def load_groups() -> Dict[str, str]:
    try:
        with open(_PATH, encoding="utf-8") as fh:
            data = json.load(fh)
        return {str(k): str(v) for k, v in data.items()} if isinstance(data, dict) else {}
    except (OSError, ValueError):
        return {}


def _save(data: Dict[str, str]) -> None:
    tmp = _PATH + ".tmp"
    os.makedirs(os.path.dirname(_PATH) or ".", exist_ok=True)
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump({k: data[k] for k in sorted(data)}, fh, ensure_ascii=False, indent=2)
    os.replace(tmp, _PATH)


def set_group(name: str, group: str) -> Dict[str, str]:
    """Assigne (ou retire si group vide) un compte à un groupe. Retourne la map."""
    name = (name or "").strip()
    group = (group or "").strip()
    with _lock:
        data = load_groups()
        if not name:
            return data
        if group:
            data[name] = group
        else:
            data.pop(name, None)
        _save(data)
        return data
