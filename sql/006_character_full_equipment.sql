-- 006_character_full_equipment.sql
-- Équipement complet (option B, message ASK) : slot réel + libellé + jets bruts.
-- slot = position 0-15 ; slot_name = libellé ; stats = chaîne d'effets brute.
-- Idempotent.

ALTER TABLE character_equipment ADD COLUMN IF NOT EXISTS slot      INTEGER;
ALTER TABLE character_equipment ADD COLUMN IF NOT EXISTS slot_name TEXT;
ALTER TABLE character_equipment ADD COLUMN IF NOT EXISTS stats     TEXT;
