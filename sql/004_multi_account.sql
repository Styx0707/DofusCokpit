-- 004_multi_account.sql
-- Passe la banque en multi-comptes : chaque ligne appartient à un `account`.
-- Idempotent. Sur base existante, exécuter manuellement (voir README).

ALTER TABLE bank_inventory
    ADD COLUMN IF NOT EXISTS account TEXT NOT NULL DEFAULT 'main';

-- Repointe la clé primaire sur (account, item_id).
ALTER TABLE bank_inventory DROP CONSTRAINT IF EXISTS bank_inventory_pkey;
ALTER TABLE bank_inventory
    ADD PRIMARY KEY (account, item_id);

CREATE INDEX IF NOT EXISTS idx_bank_inventory_item ON bank_inventory (item_id);
