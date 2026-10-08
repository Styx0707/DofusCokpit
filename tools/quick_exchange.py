#!/usr/bin/env python3
"""Échange rapide d'objets/kamas d'un perso vers un autre — PILOTE LES 2 COMPTES.

Ouvre deux sessions (donneur + receveur), les met en jeu, puis déroule la
fenêtre d'échange de bout en bout : le donneur demande l'échange et dépose, le
receveur accepte, les deux verrouillent, le serveur valide.

⚠️ Session INDÉPENDANTE du client officiel -> vise un ÉMULATEUR / serveur privé
(un compte déjà connecté par le client officiel serait kické). Les opcodes
d'échange (app/network/exchange.py) sont à confirmer sur capture pour un vrai
serveur Retro.

Prérequis en jeu : les deux persos doivent être sur la MÊME MAP et à portée
(l'échange joueur<->joueur se fait au contact), déjà connectés/sélectionnés par
cet outil.

Exemples
--------
Transfert minimal (émulateur local, pas d'auth) :
  python tools/quick_exchange.py \\
      --host 127.0.0.1 --port 5555 \\
      --giver-id 101 --giver-name Styxh \\
      --receiver-id 202 --receiver-name Zhendar \\
      --item 311:10 --item 340:5 --kamas 5000

Avec authentification (serveur privé) :
  python tools/quick_exchange.py --host game.srv.fr --port 5555 \\
      --giver-id 101 --giver-name Styxh --giver-user acc1 --giver-pass *** \\
      --receiver-id 202 --receiver-name Zhendar --receiver-user acc2 --receiver-pass *** \\
      --item 311:10
"""
from __future__ import annotations

import argparse
import logging
import sys
import time
from pathlib import Path
from typing import Dict, Optional, Tuple

# Permet `python tools/quick_exchange.py` depuis la racine du repo.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.network.bot import DofusBot              # noqa: E402
from app.network.client import LoginCredentials   # noqa: E402
from app.network.exchange import parse_done        # noqa: E402

log = logging.getLogger("quick_exchange")


def _parse_items(raw: list[str]) -> Dict[int, int]:
    """['311:10', '340:5'] -> {311: 10, 340: 5}. Rejette les entrées mal formées."""
    items: Dict[int, int] = {}
    for tok in raw or []:
        if ":" not in tok:
            raise SystemExit(f"--item invalide '{tok}' (attendu item_id:quantité)")
        sid, sqty = tok.split(":", 1)
        try:
            item_id, qty = int(sid), int(sqty)
        except ValueError:
            raise SystemExit(f"--item invalide '{tok}' (entiers attendus)")
        if qty <= 0:
            raise SystemExit(f"--item '{tok}' : quantité doit être > 0")
        items[item_id] = items.get(item_id, 0) + qty
    return items


def _connect(name: str, host: str, port: int, char_id: int, char_name: str,
             delimiter: str, creds: Optional[LoginCredentials]) -> DofusBot:
    """Construit un bot, (auth), connecte au game, sélectionne le perso. Lève sur échec."""
    builder = DofusBot.builder().auth(host, port).game(host, port).delimiter(delimiter)
    bot = builder.build()
    if creds is not None:
        if not bot.login(creds):
            raise SystemExit(f"[{name}] login échoué : {bot.last_error()}")
    else:
        # Pas d'auth : on saute directement au serveur de jeu.
        if not bot.client.connect_game():
            raise SystemExit(f"[{name}] connexion game échouée : {bot.last_error()}")
    if not bot.select_character(char_id, char_name):
        bot.disconnect()
        raise SystemExit(f"[{name}] sélection perso échouée : {bot.last_error()}")
    log.info("[%s] en jeu : %s (#%d)", name, char_name, char_id)
    return bot


def _creds(user: Optional[str], pwd: Optional[str]) -> Optional[LoginCredentials]:
    if user and pwd:
        return LoginCredentials(username=user, password=pwd)
    return None


def run_exchange(giver: DofusBot, giver_id: int, receiver: DofusBot, receiver_id: int,
                 items: Dict[int, int], kamas: int, timeout: float) -> bool:
    """Déroule l'échange et attend la validation (ERV). True si transfert validé."""
    # 1) le donneur ouvre + dépose ; verrou différé (lock=False) le temps que le
    #    receveur accepte, pour éviter de verrouiller une fenêtre pas encore ouverte.
    log.info("donneur : demande d'échange + dépôt de %d objet(s), %d kama(s)…",
             len(items), kamas)
    if not giver.exchange_give(receiver_id, items, kamas=kamas, lock=False):
        log.error("donneur : dépôt échoué (%s)", giver.last_error())
        return False

    # 2) le receveur accepte (EA, sans rien déposer) et valide sa part vide (EK).
    log.info("receveur : acceptation + validation…")
    if not receiver.exchange_accept(lock=True):
        log.error("receveur : acceptation échouée (%s)", receiver.last_error())
        return False

    # 3) le donneur valide à son tour (EK) -> les deux prêts -> le serveur valide.
    from app.network.exchange import encode_ready
    if not giver.client.send(encode_ready()):
        log.error("donneur : validation finale échouée (%s)", giver.last_error())
        return False

    # 4) attendre l'accusé de validation (ERV) d'un côté ou de l'autre.
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        for who, bot in (("donneur", giver), ("receveur", receiver)):
            for msg in bot.poll(max_messages=50):
                done = parse_done(msg)
                if done is True:
                    log.info("✅ échange VALIDÉ (accusé côté %s)", who)
                    return True
                if done is False:
                    log.error("❌ échange ANNULÉ (accusé côté %s)", who)
                    return False
        time.sleep(0.1)
    log.warning("⏳ pas d'accusé de validation reçu avant %.0fs "
                "(échange peut-être OK — vérifie en jeu ; opcodes à confirmer ?)", timeout)
    return False


def main() -> int:
    p = argparse.ArgumentParser(
        description="Échange rapide d'objets/kamas d'un perso vers un autre.",
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    p.add_argument("--host", required=True, help="hôte du serveur de jeu (émulateur)")
    p.add_argument("--port", type=int, required=True, help="port du serveur de jeu")
    p.add_argument("--delimiter", default="\\x00",
                   help=r"délimiteur de message (défaut \x00, celui du vrai Retro)")

    p.add_argument("--giver-id", type=int, required=True, help="id du perso DONNEUR")
    p.add_argument("--giver-name", required=True, help="nom du perso donneur")
    p.add_argument("--giver-user", help="login du compte donneur (si auth)")
    p.add_argument("--giver-pass", help="mot de passe du compte donneur (si auth)")

    p.add_argument("--receiver-id", type=int, required=True, help="id du perso RECEVEUR")
    p.add_argument("--receiver-name", required=True, help="nom du perso receveur")
    p.add_argument("--receiver-user", help="login du compte receveur (si auth)")
    p.add_argument("--receiver-pass", help="mot de passe du compte receveur (si auth)")

    p.add_argument("--item", action="append", default=[], metavar="ID:QTE",
                   help="objet à transférer (répétable), ex. 311:10")
    p.add_argument("--kamas", type=int, default=0, help="kamas à transférer")
    p.add_argument("--timeout", type=float, default=10.0,
                   help="attente max de l'accusé de validation (s)")
    p.add_argument("-v", "--verbose", action="store_true", help="logs détaillés (DEBUG)")
    args = p.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")

    items = _parse_items(args.item)
    if not items and args.kamas <= 0:
        raise SystemExit("rien à transférer : précise au moins un --item ou --kamas")
    delimiter = args.delimiter.encode().decode("unicode_escape")  # "\\x00" -> "\x00"

    giver = receiver = None
    try:
        giver = _connect("donneur", args.host, args.port, args.giver_id, args.giver_name,
                         delimiter, _creds(args.giver_user, args.giver_pass))
        receiver = _connect("receveur", args.host, args.port, args.receiver_id,
                            args.receiver_name, delimiter,
                            _creds(args.receiver_user, args.receiver_pass))
        ok = run_exchange(giver, args.giver_id, receiver, args.receiver_id,
                          items, args.kamas, args.timeout)
        return 0 if ok else 1
    finally:
        for bot in (giver, receiver):
            if bot is not None:
                bot.disconnect()


if __name__ == "__main__":
    sys.exit(main())
