-- 001_init_schema.sql
-- Schéma d'initialisation de l'outil d'optimisation de craft Dofus Retro.
-- Idempotent : rejouable sans casser une base existante.
-- Monté automatiquement par le conteneur postgres via /docker-entrypoint-initdb.d.

BEGIN;

-- 1) Dictionnaire des objets du jeu -------------------------------------------
CREATE TABLE IF NOT EXISTS items
(
    item_id
    INTEGER
    PRIMARY
    KEY, -- ID interne Dofus
    name
    TEXT
    NOT
    NULL,
    created_at
    TIMESTAMPTZ
    NOT
    NULL
    DEFAULT
    now
(
)
    );

-- Recherche insensible à la casse par nom.
CREATE INDEX IF NOT EXISTS idx_items_name ON items (lower (name));

-- 2) Recettes -----------------------------------------------------------------
-- Une recette produit `result_quantity` exemplaires de `result_item_id`.
-- En Dofus Retro un objet a au plus une recette -> UNIQUE(result_item_id).
CREATE TABLE IF NOT EXISTS recipes
(
    recipe_id
    SERIAL
    PRIMARY
    KEY,
    result_item_id
    INTEGER
    NOT
    NULL
    REFERENCES
    items
(
    item_id
) ON DELETE CASCADE,
    result_quantity INTEGER NOT NULL DEFAULT 1 CHECK
(
    result_quantity >
    0
),
    UNIQUE
(
    result_item_id
)
    );

-- Table de liaison recette <-> ingrédients (modèle normalisé).
CREATE TABLE IF NOT EXISTS recipe_ingredients
(
    recipe_id
    INTEGER
    NOT
    NULL
    REFERENCES
    recipes
(
    recipe_id
) ON DELETE CASCADE,
    ingredient_item_id INTEGER NOT NULL REFERENCES items
(
    item_id
)
  ON DELETE RESTRICT,
    quantity INTEGER NOT NULL CHECK
(
    quantity >
    0
),
    PRIMARY KEY
(
    recipe_id,
    ingredient_item_id
)
    );

-- Accélère « quelles recettes consomment cet objet ? ».
CREATE INDEX IF NOT EXISTS idx_recipe_ingredients_item
    ON recipe_ingredients (ingredient_item_id);

-- 3) Inventaire de banque -----------------------------------------------------
-- État courant de la banque, mis à jour dynamiquement par le sniffer.
CREATE TABLE IF NOT EXISTS bank_inventory
(
    item_id
    INTEGER
    PRIMARY
    KEY
    REFERENCES
    items
(
    item_id
) ON DELETE CASCADE,
    quantity BIGINT NOT NULL CHECK
(
    quantity
    >=
    0
), -- BIGINT : stacks importants
    updated_at TIMESTAMPTZ NOT NULL DEFAULT now
(
)
    );

COMMIT;
