-- 002_item_metadata.sql
-- Enrichit le dictionnaire d'objets avec type / niveau / prix vendeur.
-- Idempotent. Appliqué au 1er démarrage (fresh install) ; sur une base
-- existante, exécuter manuellement (voir README).

ALTER TABLE items
    ADD COLUMN IF NOT EXISTS type TEXT;
ALTER TABLE items
    ADD COLUMN IF NOT EXISTS level INTEGER;
ALTER TABLE items
    ADD COLUMN IF NOT EXISTS price BIGINT;

CREATE INDEX IF NOT EXISTS idx_items_type ON items (type);
CREATE INDEX IF NOT EXISTS idx_items_level ON items (level);
