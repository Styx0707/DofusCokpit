"""Capture N messages de banque bruts pour identifier le format binaire.

N'écrit RIEN en base : imprime (et archive si CAPTURE_DEBUG_DUMP est défini)
le payload EsK en repr + hex. Ouvre la banque en jeu pendant l'exécution.

Usage :
    sudo -E python -m scripts.capture_sample [nb_messages]

Puis colle le résultat pour caler ``app.network.sniffer.parse_bank_storage``.
"""
from __future__ import annotations

import logging
import sys
from typing import Dict

from app.network.sniffer import DofusBankSniffer

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("capture")


def main() -> None:
    target = int(sys.argv[1]) if len(sys.argv) > 1 else 1
    seen = {"n": 0}

    def on_bank(inventory: Dict[int, int]) -> None:
        seen["n"] += 1
        logger.info(
            "Message banque #%d : %d objets -> %s",
            seen["n"], len(inventory), dict(list(inventory.items())[:10]),
        )
        if seen["n"] >= target:
            raise KeyboardInterrupt  # stoppe proprement la boucle sniff

    logger.info("En attente de %d ouverture(s) de banque… (Ctrl+C pour stopper)", target)
    DofusBankSniffer(on_bank=on_bank).start()


if __name__ == "__main__":
    main()
