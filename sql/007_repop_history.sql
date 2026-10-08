-- Historique des apparitions de groupes CIBLE / ARCHIMONSTRE par map.
-- Sert à recharger la heatmap et le Top maps après un redémarrage de l'API,
-- et à des analyses temporelles (fréquence par map / zone).
-- On ne persiste QUE les apparitions cible/archi (données éparses), pas chaque
-- groupe de monstres.
CREATE TABLE IF NOT EXISTS map_appearances
(
    id
    BIGSERIAL
    PRIMARY
    KEY,
    recorded_at
    TIMESTAMPTZ
    NOT
    NULL
    DEFAULT
    now
(
), -- écriture de la ligne
    ts_epoch DOUBLE PRECISION NOT NULL, -- horodatage de l'évènement (capture/live)
    map_id INTEGER NOT NULL,
    coord_x INTEGER,
    coord_y INTEGER,
    zone TEXT,
    is_target BOOLEAN NOT NULL DEFAULT FALSE,
    is_archi BOOLEAN NOT NULL DEFAULT FALSE,
    monster_ids INTEGER [] NOT NULL DEFAULT '{}'
    );

CREATE INDEX IF NOT EXISTS idx_map_appearances_map ON map_appearances (map_id);
CREATE INDEX IF NOT EXISTS idx_map_appearances_ts ON map_appearances (ts_epoch);
