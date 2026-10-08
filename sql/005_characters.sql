-- 005_characters.sql
-- Personnages par compte + équipement visible (issu du message ALK).
-- Idempotent.

CREATE TABLE IF NOT EXISTS characters
(
    account
    TEXT
    NOT
    NULL,
    character_id
    BIGINT
    NOT
    NULL,
    name
    TEXT
    NOT
    NULL,
    level
    INTEGER,
    class_id
    INTEGER,
    class_name
    TEXT,
    sex
    INTEGER,
    updated_at
    TIMESTAMPTZ
    NOT
    NULL
    DEFAULT
    now
(
),
    PRIMARY KEY
(
    account,
    character_id
)
    );

CREATE TABLE IF NOT EXISTS character_equipment
(
    account
    TEXT
    NOT
    NULL,
    character_id
    BIGINT
    NOT
    NULL,
    slot_index
    INTEGER
    NOT
    NULL,
    item_id
    INTEGER
    NOT
    NULL,
    PRIMARY
    KEY
(
    account,
    character_id,
    slot_index
),
    FOREIGN KEY
(
    account,
    character_id
)
    REFERENCES characters
(
    account,
    character_id
) ON DELETE CASCADE
    );

CREATE INDEX IF NOT EXISTS idx_characters_account ON characters (account);
