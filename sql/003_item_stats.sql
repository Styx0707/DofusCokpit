-- 003_item_stats.sql
-- Stats d'objet extraites du dictionnaire (résistances, etc.).
-- Générique : `stat` = clé (ex. 'res_neutre'), `is_percent` distingue fixe / %.
-- Une plage de jet est stockée (value_min..value_max).

CREATE TABLE IF NOT EXISTS item_stats
(
    item_id
    INTEGER
    NOT
    NULL
    REFERENCES
    items
(
    item_id
) ON DELETE CASCADE,
    stat TEXT NOT NULL, -- ex: res_neutre, res_feu, ...
    is_percent BOOLEAN NOT NULL, -- true = %, false = fixe
    value_min INTEGER NOT NULL,
    value_max INTEGER NOT NULL,
    PRIMARY KEY
(
    item_id,
    stat,
    is_percent
)
    );

CREATE INDEX IF NOT EXISTS idx_item_stats_stat ON item_stats (stat, is_percent);
