#!/usr/bin/env python3
"""Runner AUTONOME du proxy d'échange (host Windows, hors Docker).

Lance le proxy MITM sur le host (là où tourne le client Dofus), SANS DB ni
FastAPI : stdlib + ``app.network`` (parsing pur). Offre une petite invite pour
lister les connexions et déclencher un échange, le tout dans le MÊME process que
le proxy (il faut que ce soit lui qui tienne les sockets des clients).

Prérequis (une fois)
--------------------
1. IP réelle du serveur de jeu : une capture pendant que tu es en jeu (IP distante
   sur :443). C'est le ``--upstream-host``.
2. Redirige le client vers le proxy : dans C:\\Windows\\System32\\drivers\\etc\\hosts
   mappe le host de jeu -> 127.0.0.1. (L'auth/login reste en direct.)
3. Lance ce runner en ADMIN (binder :443 exige les privilèges).

Lancement (PowerShell, fenêtre admin, depuis la racine du repo)
---------------------------------------------------------------
    py tools\\dofus_proxy.py --upstream-host <IP_RÉELLE> --verbose

Puis, une fois tes deux persos en jeu (même map, à portée) :
    > list
    > give Styxh Zhendar 311:10,340:5 5000
    > quit

CAPTURE D'OPCODES : lance avec --verbose, fais UN échange À LA MAIN en jeu ; les
messages client->serveur loggés (c->s ...) donnent les vrais préfixes à reporter
dans app/network/exchange.py (constantes EXCHANGE_*).

⚠️ Manipuler les paquets est contraire aux CGU d'Ankama (risque de ban). Sur tes
propres comptes, en connaissance de cause.
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path
from typing import Dict

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.network.proxy import DofusProxy, run_proxy_exchange   # noqa: E402

log = logging.getLogger("dofus.proxy.runner")


def _parse_items(raw: str) -> Dict[int, int]:
    """'311:10,340:5' -> {311: 10, 340: 5}."""
    items: Dict[int, int] = {}
    for tok in raw.split(","):
        tok = tok.strip()
        if not tok:
            continue
        if ":" not in tok:
            raise ValueError(f"objet invalide '{tok}' (attendu id:qté)")
        sid, sqty = tok.split(":", 1)
        items[int(sid)] = items.get(int(sid), 0) + int(sqty)
    return items


def _key(v: str):
    """Numérique -> id de perso ; sinon sous-chaîne de nom."""
    return int(v) if v.lstrip("-").isdigit() else v


def _cmd_list(proxy: DofusProxy) -> None:
    conns = proxy.connections()
    if not conns:
        print("  (aucune connexion — ouvre tes clients et entre en jeu)")
        return
    for c in conns:
        tag = c.character_name or "(non identifié — attends l'entrée en jeu)"
        print(f"  conn#{c.id}  {tag}"
              + (f"  id={c.character_id}" if c.character_id is not None else ""))


def _cmd_give(proxy: DofusProxy, parts: list) -> None:
    if len(parts) < 3:
        print("  usage: give <donneur> <receveur> <id:qté,...> [kamas]")
        return
    giver, receiver, items_raw = parts[0], parts[1], parts[2]
    kamas = int(parts[3]) if len(parts) > 3 else 0
    try:
        items = _parse_items(items_raw)
    except ValueError as exc:
        print(f"  {exc}")
        return
    res = run_proxy_exchange(proxy, _key(giver), _key(receiver), items, kamas)
    if res.get("ok"):
        print(f"  ✅ échange injecté : {res['giver']} -> {res['receiver']} "
              f"({items}, {kamas} kamas)")
    else:
        print(f"  ❌ {res.get('reason')}")
        if res.get("connections"):
            print(f"     connexions connues : {res['connections']}")


def main() -> int:
    p = argparse.ArgumentParser(
        description="Proxy d'échange MITM autonome (host).",
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    p.add_argument("--upstream-host", required=True,
                   help="IP RÉELLE du serveur de jeu (trouvée par capture)")
    p.add_argument("--upstream-port", type=int, default=443)
    p.add_argument("--listen-host", default="0.0.0.0")
    p.add_argument("--listen-port", type=int, default=443)
    p.add_argument("-v", "--verbose", action="store_true",
                   help="logs DEBUG (affiche les messages client->serveur = capture d'opcodes)")
    args = p.parse_args()

    logging.basicConfig(
        level=logging.DEBUG if args.verbose else logging.INFO,
        format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")

    proxy = DofusProxy(args.listen_host, args.listen_port,
                       args.upstream_host, args.upstream_port)
    try:
        proxy.start()
    except OSError as exc:
        print(f"Impossible de binder {args.listen_host}:{args.listen_port} : {exc}")
        print("Port < 1024 -> lance PowerShell EN ADMIN, ou choisis --listen-port 8443.")
        return 1

    print(f"Proxy actif {args.listen_host}:{args.listen_port} -> "
          f"{args.upstream_host}:{args.upstream_port}")
    print("Commandes : 'list', 'give <donneur> <receveur> <id:qté,...> [kamas]', 'quit'.")
    try:
        while True:
            try:
                line = input("> ").strip()
            except EOFError:
                break
            if not line:
                continue
            parts = line.split()
            cmd, rest = parts[0].lower(), parts[1:]
            if cmd in ("quit", "exit", "q"):
                break
            elif cmd in ("list", "ls", "l"):
                _cmd_list(proxy)
            elif cmd in ("give", "g"):
                _cmd_give(proxy, rest)
            else:
                print("  commandes : list | give <donneur> <receveur> <id:qté,...> [kamas] | quit")
    except KeyboardInterrupt:
        pass
    finally:
        proxy.stop()
        print("Proxy arrêté.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
