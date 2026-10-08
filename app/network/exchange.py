"""Protocole d'ÉCHANGE joueur->joueur Dofus Retro (encodage + décodage).

Objet : transférer objets/kamas d'un perso à un autre en émettant les messages
de la fenêtre d'échange, sans manipuler le client à la souris.

════════════════════════════════════════════════════════════════════════════
OPCODES CONFIRMÉS PAR CAPTURE (officiel, 2026-10-06, data/c2s_hex.txt)
════════════════════════════════════════════════════════════════════════════
Séquence réelle client->serveur relevée pendant un échange manuel :
    ER1|<cibleId>        demande d'échange, type 1 = joueur, cible = id joueur
    EA                   acceptation (le receveur), SANS argument
    EMG<kamas>           dépôt de kamas
    EMO+<objetUID>|<qté> ajout d'un objet par son UID D'INSTANCE (+ ajoute, - retire)
    EK                   validation (pressé par les DEUX ; bascule prêt/pas prêt)
    EV                   (quitter/annuler — NON observé, supposé)

⚠️  OBJET PAR UID D'INSTANCE, PAS PAR ID DE TEMPLATE : EMO+ prend l'uid unique de
la pile dans l'inventaire (champ <uid> des messages 'ASK'/'EL'), pas l'id d'item.

════════════════════════════════════════════════════════════════════════════
⚠️  INJECTION IMPOSSIBLE SUR L'OFFICIEL — SIGNATURE PAR MESSAGE
════════════════════════════════════════════════════════════════════════════
La capture montre que CHAQUE message client->serveur est enveloppé dans un bloc
cryptographique de taille constante (~304 o) : ``ù<signature>ù<message>\\n``. Le
serveur officiel REJETTE un message sans enveloppe valide. On ne peut donc PAS
forger ER/EMO/EK par injection (il faudrait reproduire la signature = clé de
session + algo du client Flash). Sur l'officiel, piloter le VRAI client (walker)
est la seule voie : il signe lui-même ses paquets.

Ces encodeurs restent valides pour un ÉMULATEUR / serveur privé SANS signature
(le serveur du repo), et comme référence du protocole. L'applicateur serveur
``ExchangeHandler`` complète l'émulateur (miroir de ``GameActionHandler``). Les
accusés serveur->client (parse_*) n'ont PAS été capturés -> à confirmer.
"""
from __future__ import annotations

from typing import Dict, Iterator, List, Optional

# --- Opcodes client -> serveur (confirmés par capture, sauf EV) -------------
EXCHANGE_REQUEST = "ER"    # ER<type>|<cibleId>       (type 1 = joueur)
EXCHANGE_ACCEPT = "EA"     # EA                        (receveur accepte, sans arg)
EXCHANGE_MOVE_OBJECT = "EMO"  # EMO+<uid>|<qté> / EMO-<uid>|<qté>
EXCHANGE_MOVE_KAMAS = "EMG"   # EMG<kamas>
EXCHANGE_READY = "EK"      # EK                        (valide ; bascule, les 2 persos)
EXCHANGE_LEAVE = "EV"      # EV                        (quitter — supposé, non observé)

EXCHANGE_TYPE_PLAYER = 1   # type d'échange joueur<->joueur

# --- Accusés serveur -> client (NON capturés — hypothétiques, à confirmer) ---
EXCHANGE_MOVE_ACK = "EMK"   # EMK<who>|<uid>|<qté>
EXCHANGE_READY_ACK = "EKK"  # EKK<who>|<0|1>
EXCHANGE_DONE = "ERV"       # ERV<0|1>


# ============================ ENCODAGE (client) ============================= #

def encode_request(target_id: int, kind: int = EXCHANGE_TYPE_PLAYER) -> str:
    """Demande d'échange vers le perso ``target_id`` : ``ER1|<id>`` (confirmé)."""
    return f"{EXCHANGE_REQUEST}{kind}|{int(target_id)}"


def encode_accept() -> str:
    """Acceptation de la demande d'échange (receveur) : ``EA`` (confirmé, sans arg)."""
    return EXCHANGE_ACCEPT


def encode_move_object(object_uid: int, qty: int) -> str:
    """Ajoute (qty>0) / retire (qty<0) ``|qty|`` de l'objet d'UID ``object_uid`` :
    ``EMO+<uid>|<qté>`` (confirmé). ``object_uid`` = UID D'INSTANCE, pas id d'item."""
    if qty == 0:
        raise ValueError("quantité nulle")
    sign = "+" if qty > 0 else "-"
    return f"{EXCHANGE_MOVE_OBJECT}{sign}{int(object_uid)}|{abs(int(qty))}"


def encode_set_kamas(kamas: int) -> str:
    """Dépôt de kamas : ``EMG<kamas>`` (confirmé)."""
    if kamas < 0:
        raise ValueError("kamas négatifs")
    return f"{EXCHANGE_MOVE_KAMAS}{int(kamas)}"


def encode_ready() -> str:
    """Validation de sa part de l'échange : ``EK`` (confirmé ; bascule prêt)."""
    return EXCHANGE_READY


def encode_leave() -> str:
    """Quitte / annule l'échange : ``EV`` (supposé, non observé)."""
    return EXCHANGE_LEAVE


def plan_give(target_id: int, objects: Dict[int, int], kamas: int = 0) -> List[str]:
    """Séquence côté DONNEUR : demande + dépôt de chaque objet + kamas (SANS la
    validation finale ``EK``, pressée après l'acceptation du receveur).

    ``objects`` = {object_uid: quantité>0}. Les quantités <= 0 sont ignorées."""
    msgs: List[str] = [encode_request(target_id)]
    for object_uid, qty in objects.items():
        if qty and qty > 0:
            msgs.append(encode_move_object(object_uid, qty))
    if kamas > 0:
        msgs.append(encode_set_kamas(kamas))
    return msgs


# ============================ DÉCODAGE (serveur) ============================ #
# ⚠️ Non capturés (seul le sens client->serveur l'a été) : formats hypothétiques.

def parse_move_ack(message: str) -> Optional[dict]:
    """``EMK<who>|<uid>|<qté>`` -> {who, object_uid, qty} (who 0=soi, 1=autre)."""
    if not message.startswith(EXCHANGE_MOVE_ACK):
        return None
    parts = message[len(EXCHANGE_MOVE_ACK):].split("|")
    if len(parts) < 3:
        return None
    try:
        return {"who": int(parts[0]), "object_uid": int(parts[1]), "qty": int(parts[2])}
    except ValueError:
        return None


def parse_ready_ack(message: str) -> Optional[dict]:
    """``EKK<who>|<0|1>`` -> {who, ready}."""
    if not message.startswith(EXCHANGE_READY_ACK):
        return None
    parts = message[len(EXCHANGE_READY_ACK):].split("|")
    if len(parts) < 2:
        return None
    try:
        return {"who": int(parts[0]), "ready": parts[1].strip() in ("1", "true", "True")}
    except ValueError:
        return None


def parse_done(message: str) -> Optional[bool]:
    """``ERV<0|1>`` -> True (validé) / False (annulé), ou None si autre message."""
    if not message.startswith(EXCHANGE_DONE):
        return None
    return message[len(EXCHANGE_DONE):].strip() in ("1", "true", "True")


# ====================== APPLICATEUR SERVEUR (ému, mémoire) ================== #

class ExchangeHandler:
    """État serveur minimal d'un échange à deux (émulateur, en mémoire). Comme
    ``GameActionHandler`` : aucun réseau, aucune règle métier (poids/pods), on
    suit juste les deux parts et on applique le transfert à la validation.

    Les objets sont suivis par UID d'instance (clé des dicts ``objects``)."""

    def __init__(self, giver_id: int, receiver_id: int) -> None:
        self.giver_id = giver_id
        self.receiver_id = receiver_id
        self.open = True
        self.parts: Dict[int, dict] = {
            giver_id: {"objects": {}, "kamas": 0, "ready": False},
            receiver_id: {"objects": {}, "kamas": 0, "ready": False},
        }
        self.done: Optional[bool] = None   # None=en cours, True=validé, False=annulé

    def apply_move(self, player_id: int, object_uid: int, qty: int) -> dict:
        """Ajoute (qty>0) / retire (qty<0) un objet pour ``player_id`` (borné à 0)."""
        if not self.open or self.done is not None:
            return {"ok": False, "reason": "échange clos"}
        if player_id not in self.parts:
            return {"ok": False, "reason": "joueur hors échange"}
        objs = self.parts[player_id]["objects"]
        new_qty = objs.get(object_uid, 0) + qty
        if new_qty <= 0:
            objs.pop(object_uid, None)
        else:
            objs[object_uid] = new_qty
        for p in self.parts.values():   # tout dépôt annule les 2 « prêt »
            p["ready"] = False
        return {"ok": True, "who": player_id, "object_uid": object_uid,
                "qty": objs.get(object_uid, 0)}

    def apply_kamas(self, player_id: int, kamas: int) -> dict:
        if not self.open or self.done is not None:
            return {"ok": False, "reason": "échange clos"}
        if player_id not in self.parts or kamas < 0:
            return {"ok": False, "reason": "joueur hors échange ou kamas invalides"}
        self.parts[player_id]["kamas"] = kamas
        for p in self.parts.values():
            p["ready"] = False
        return {"ok": True, "who": player_id, "kamas": kamas}

    def apply_ready(self, player_id: int, ready: bool = True) -> dict:
        """Bascule la part de ``player_id`` à ``ready``. Les DEUX prêts -> validé."""
        if not self.open or self.done is not None:
            return {"ok": False, "reason": "échange clos"}
        if player_id not in self.parts:
            return {"ok": False, "reason": "joueur hors échange"}
        self.parts[player_id]["ready"] = ready
        if all(p["ready"] for p in self.parts.values()):
            self.done = True
            self.open = False
            return {"ok": True, "who": player_id, "ready": True, "done": True,
                    "transfer": self._transfer()}
        return {"ok": True, "who": player_id, "ready": ready, "done": False}

    def apply_leave(self, player_id: int) -> dict:
        self.open = False
        self.done = False
        return {"ok": True, "who": player_id, "done": False}

    def _transfer(self) -> dict:
        return {
            "giver": {"id": self.giver_id, **self.parts[self.giver_id]},
            "receiver": {"id": self.receiver_id, **self.parts[self.receiver_id]},
        }


def apply_messages(handler: ExchangeHandler, player_id: int,
                   messages: Iterator[str]) -> List[dict]:
    """Rejoue des messages client (ceux de ``plan_give`` p.ex.) sur un
    ``ExchangeHandler`` du point de vue de ``player_id``. Pour tester sans réseau."""
    out: List[dict] = []
    for msg in messages:
        if msg.startswith(EXCHANGE_MOVE_OBJECT):   # EMO+/EMO-
            body = msg[len(EXCHANGE_MOVE_OBJECT):]
            sign = -1 if body[:1] == "-" else 1
            uid, _, qty = body.lstrip("+-").partition("|")
            out.append(handler.apply_move(player_id, int(uid), sign * int(qty)))
        elif msg.startswith(EXCHANGE_MOVE_KAMAS):   # EMG
            out.append(handler.apply_kamas(player_id, int(msg[len(EXCHANGE_MOVE_KAMAS):])))
        elif msg.startswith(EXCHANGE_READY):        # EK
            out.append(handler.apply_ready(player_id, True))
        elif msg.startswith(EXCHANGE_LEAVE):        # EV
            out.append(handler.apply_leave(player_id))
        # EXCHANGE_REQUEST (ER) / EXCHANGE_ACCEPT (EA) : ouverture, gérés en amont
    return out
