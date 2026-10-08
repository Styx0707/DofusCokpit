-- 008_item_prices.sql
-- Prix MARCHÉ / HDV éditable par l'utilisateur, DISTINCT du prix vendeur PNJ
-- (items.price, quasi inutile pour le trading). La valorisation (banque, craft,
-- plans) utilise COALESCE(market_price, price) : le prix marché prime dès qu'il
-- est renseigné, sinon on retombe sur le prix vendeur.
-- Idempotent. Appliqué au 1er démarrage ; sur une base existante, exécuter :
--   docker compose exec -T db psql -U dofus -d dofus -f /docker-entrypoint-initdb.d/008_item_prices.sql
-- (ou voir README).

ALTER TABLE items
    ADD COLUMN IF NOT EXISTS market_price BIGINT;
ALTER TABLE items
    ADD COLUMN IF NOT EXISTS price_updated_at TIMESTAMPTZ;
