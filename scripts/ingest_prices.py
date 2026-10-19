"""Ingeste les PRIX MARCHÉ (HDV) d'une capture .pcap/.pcapng dans PostgreSQL.

Pendant « prix » de scripts.ingest_pcap (qui, lui, ne charge que la banque).
Réutilise EXACTEMENT le chemin de production (app.network.pcap_feed.feed_pcap +
callback on_prices) : même agrégation que le watcher live — on retient le
PREMIER PRIX, càd le prix du lot de 1 (``EHl`` x1 = l'offre la plus basse en
vente), le prix MOYEN (``EHP``) ne servant que de repli. Alimenté par un fichier
-> rejoue une capture existante sans avoir à reconsulter l'HDV en jeu.

Met à jour items.market_price (UPDATE only : n'insère pas d'objets inconnus) ;
la valorisation (banque, crafts rentables…) utilise COALESCE(market_price, price).

Usage : python -m scripts.ingest_prices [data/hdv.pcapng]
"""
from __future__ import annotations

import logging
import sys
from typing import Dict

from app.core.repop_monitor import get_monitor
from app.db.connection import close_pool, init_pool, transaction
from app.db.repositories import upsert_market_prices
from app.network.pcap_feed import feed_pcap

logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
logger = logging.getLogger("ingest_prices")


def main():
    path = sys.argv[1] if len(sys.argv) > 1 else "data/hdv.pcapng"

    init_pool()
    try:
        updated = 0

        def persist(prices: Dict[int, int]) -> None:
            nonlocal updated
            with transaction() as cur:
                updated = upsert_market_prices(cur, prices)

        summary = feed_pcap(get_monitor(), path, on_prices=persist)
        logger.info(
            "Capture %s : %d messages lus, %d prix HDV captés, %d objets mis à jour.",
            path, summary["messages"], summary["hdv_prices"], updated,
        )
        if not summary["hdv_prices"]:
            logger.error("Aucun prix HDV (EHP/EHl) trouvé dans la capture.")
            sys.exit(1)
    finally:
        close_pool()


if __name__ == "__main__":
    main()
