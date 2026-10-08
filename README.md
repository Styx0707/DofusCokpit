# Dofus Retro — Optimiseur de craft & scan de banque

Backend Python modulaire : lit le contenu de la banque (capture réseau Scapy ou
import d'une capture Wireshark), le persiste dans PostgreSQL, calcule les
recettes fabricables, et expose le tout en REST.

## Architecture

```
app/
├── config.py              # Configuration via variables d'environnement
├── models.py              # Dataclasses de domaine (JSON-ready)
├── api.py                 # API REST FastAPI (lecture + optimisation)
├── db/
│   ├── connection.py      # Pool + context managers de transaction
│   └── repositories.py    # Repository Pattern (upsert items/recipes/bank, lecture)
├── network/
│   ├── protocol.py        # Décodage protocole Dofus (pur, sans Scapy) — message 'EL'
│   └── sniffer.py         # Capture Scapy + réassemblage TCP + dispatch
└── core/
    └── optimizer.py       # Moteur : isolation / glouton / point fixe
scripts/
├── seed.py                # Seed items/recettes depuis un JSON {items,recipes}
├── seed_names.py          # Seed les noms d'objets depuis data/items_all.json
├── fetch_recipes.py       # Télécharge toutes les recettes (API wiki, cache disque)
├── ingest_pcap.py         # Importe la banque d'un .pcapng dans PostgreSQL
├── parse_pcap.py          # Analyse une capture : flux en clair, codes de message
├── decode_el.py           # Décode le message de banque 'EL' (debug format)
└── capture_sample.py      # Capture live des messages de banque (repr+hex)
sql/001_init_schema.sql    # Schéma (appliqué au 1er démarrage du conteneur DB)
tests/                     # Tests moteur + protocole (sans DB ni réseau)
```

## Protocole (découvert par capture réelle)

Le client **Dofus Retro officiel** parle un protocole **texte en clair** sur le **port 443** (pas de TLS). Le contenu de
banque arrive dans un message :

```
EL O<uid>~<gid>~<quantité>~<position>~<stats> ; O<uid>~... ; ...
```

Nombres en **hexadécimal** ; `gid` = ID d'objet, on agrège les quantités par gid.
Décodage : `app/network/protocol.py` (couvert par `tests/test_protocol.py` sur un
échantillon réel).

## Démarrage

**Le plus simple — le launcher** : double-clique **`DofusCockpit.exe`** (à la racine, à côté de
`docker-compose.yml`). Panneau de contrôle : démarre DB+API, lance la capture réseau (choix de l'interface) et ouvre
l'app. Pré-requis installés une fois : **Docker Desktop** + **Wireshark**. La page **Démarrage**
(`http://localhost:8000/ui/steps.html`) récapitule les étapes et affiche le statut live (API, banque, prix).

Reconstruire l'exe : `powershell -ExecutionPolicy Bypass -File scripts\build_exe.ps1` (PyInstaller ; Python 3.11/3.12
recommandé). L'exe ne fait qu'**orchestrer** Docker + dumpcap — il ne les embarque pas (trop lourds).

**En ligne de commande** (équivalent) :

```bash
cp .env.example .env
docker compose up -d --build db api      # docs API : http://localhost:8000/docs
```

### Installer sur un autre PC (Windows x64)

La base (dictionnaire d'objets, recettes, icônes, banque, prix) vit dans un volume Docker — **vide** sur une machine
neuve. Pour un transfert sans re-seeder :

1. **Sur le PC source** : `powershell -File scripts\db_dump.ps1` → crée `data\db_backup.dump` (~0,2 Mo), puis
   `powershell -ExecutionPolicy Bypass -File scripts\package.ps1` → produit **`DofusCockpit-package.zip`** (~55 Mo :
   code + exe + dump + icônes, sans `.git`/`build`/caches/captures/décompiles SWF).
2. **Copie le `.zip`** sur l'autre PC et dézippe-le (tout est dedans : exe, icônes `app/static/icons/`, dump).
3. **Sur le nouveau PC** : installe **Docker Desktop** + **Wireshark** (une fois), lance Docker, puis :
   ```powershell
   powershell -ExecutionPolicy Bypass -File scripts\setup.ps1
   ```
   `setup.ps1` crée `.env`, démarre les conteneurs et **restaure** `data\db_backup.dump` (ou seed depuis le wiki si le
   dump est absent). Ensuite : double-clic **`DofusCockpit.exe`**.

L'exe est un binaire **Windows x64** : il tourne tel quel. S'il refuse de démarrer, reconstruis-le sur place avec
`scripts\build_exe.ps1`. Scripts annexes : `db_restore.ps1` (restaurer seul).

## Données items + recettes (dictionnaire du jeu)

Source : API publique du wiki communautaire **wiki.moon-bot.io** (IDs = GID du
client 1.29). Pipeline :

```bash
# 1) Liste des objets (id, nom) — 11 716 objets
curl -o data/items_all.json https://wiki.moon-bot.io/api/items.json
docker compose run --rm -v "${PWD}/data:/srv/data" api python -m scripts.seed_names

# 2) Recettes (détail par objet, mis en cache dans data/details/) — ~2300 recettes
docker compose run --rm -v "${PWD}/data:/srv/data" api python -m scripts.fetch_recipes
docker compose run --rm -v "${PWD}/data:/srv/data" api python -m scripts.seed data/recipes_full.json
```

### Icônes d'items

`scripts/fetch_icons.py` télécharge les icônes en local (`app/static/icons/<gid>.png`, servies via `/ui/icons/`).
Le wiki moon-bot n'expose plus les icônes d'items ; la source est **dofusdb.fr**, matchée par **nom exact** (fiable
mais partielle : les items spécifiques Rétro absents de Dofus 3 ne matchent pas). `--scope all|bank|resources|useful`
(déf. `useful` = banque ∪ ingrédients ∪ équipement ∪ build), `--all` pour re-télécharger, `--workers N`.

```bash
docker compose run --rm -v "${PWD}/scripts:/srv/scripts" api python -m scripts.fetch_icons --scope useful
```

## Alimenter la banque

**A. Depuis une capture Wireshark (recommandé sous Windows)** — capture,
ouvre ta banque en jeu, enregistre en `data/game.pcapng`, puis :

```bash
docker compose run --rm -v "${PWD}/data:/srv/data" api python -m scripts.ingest_pcap data/game.pcapng
```

**B. Capture live (Linux + NET_RAW)** : `docker compose up backend`. **C. Manuel / tests** : `PUT /bank` avec
`{item_id: quantity}`.

**D. Auto-sync (recommandé, mono-compte)** — si le watcher live des repops tourne déjà (`LIVE_CAPTURE_DIR` + ring-buffer
`dumpcap`, voir plus bas), **ouvrir sa banque en jeu suffit** : le message `EL` est
capté dans le flux, décodé et la banque du compte `main` est remplacée automatiquement (même chemin que
`scripts.ingest_pcap`, zéro commande). Latence ≈ durée d'un fichier du ring + settle (quelques s).

## Prix des ressources (hôtel de vente, via dump)

Les prix viennent du **dump réseau de l'hôtel de vente**, pas d'une saisie manuelle. Quand le watcher live tourne
(option D ci-dessus), **ouvrir l'HDV et parcourir des catégories** suffit : le serveur émet le **prix moyen** de chaque
objet (message `EHP<gid>|<prix>`) et les prix des lots 1/10/100 en vente (`EHl`). Ils sont décodés
(`app/network/protocol.py`, couvert par `tests/test_protocol.py` sur un échantillon réel) et écrits dans
`items.market_price` (+ `price_updated_at`).

Toute la valorisation (banque, craftable, plans) utilise alors `COALESCE(market_price, price)` : **prix marché
prioritaire, sinon prix vendeur PNJ**. Page banque : **http://localhost:8000/ui/bank.html** (badge vert `marché` vs gris
`vendeur`). Schéma : `sql/008_item_prices.sql` (sur une base existante, l'appliquer manuellement).

## API REST

| Méthode | Route             | Description                                                           |
|---------|-------------------|-----------------------------------------------------------------------|
| GET     | `/health`         | Ping                                                                  |
| GET     | `/stock`          | Stock complet de la banque                                            |
| GET     | `/bank/detail`    | Banque enrichie (type, niveau, prix vendeur/marché/effectif, valeur)  |
| GET     | `/recipes`        | Toutes les recettes + ingrédients                                     |
| GET     | `/craftable`      | Recettes fabricables + occurrences (en isolation)                     |
| GET     | `/craftable/near` | Recettes à portée (`?max_missing=N` ressources distinctes manquantes) |
| GET     | `/plan`           | Plan de craft (stock virtuel). `?cascade=true` = point fixe           |
| PUT     | `/bank`           | Met à jour la banque (`?replace=true` = scan complet)                 |

## Tests

```bash
docker compose run --rm -v "${PWD}/tests:/srv/tests" api \
  sh -c "pip install -q pytest && PYTHONPATH=/srv pytest -q tests"
```

## Suivi live des repops de monstres (Pandala / Bambouto Sacré)

Décode le **changement de map** (`GDM`) et les **groupes de monstres** (`GM`, id de
sprite négatif = groupe ; champ `[4]` = IDs monstres, `[7]` = niveaux) pour suivre, **par map où tu as un perso**, les
groupes présents et estimer le repop de ta cible (déf. **Bambouto Sacré**, id `546`). Page live :
**http://localhost:8000/ui/live.html**.

```bash
docker compose up -d --build db api

# A. Analyse d'une capture (repérer les groupes/ids par map)
docker compose run --rm -v "${PWD}/scripts:/srv/scripts" api \
  python -m scripts.scan_game data/pandala.pcapng --groups     # flag <<< CIBLE

# B. Injecter une capture dans le moniteur (puis ouvrir la page live)
curl -X POST "http://localhost:8000/live/ingest?path=data/pandala.pcapng"
```

**Temps réel sous Windows** (Docker ne peut pas sniffer la carte de l'hôte → on
partage des fichiers). Capture continue côté hôte avec `dumpcap` (livré avec
Wireshark) dans un dossier surveillé :

```powershell
mkdir data\live
dumpcap -i <iface> -f "tcp port 443" -b duration:5 -b files:50 -w data\live\dofus.pcapng
```

Puis relancer l'API avec `LIVE_CAPTURE_DIR=/srv/data/live` : le watcher ingère
chaque fichier du ring-buffer et la page se met à jour toute seule. Le compte à
rebours de repop **s'auto-calibre** en observant les cycles mort→repop (aucun
chiffre inventé tant qu'un cycle n'a pas été vu).

| Méthode | Route          | Description                                |
|---------|----------------|--------------------------------------------|
| GET     | `/live/state`  | État courant : groupes par map + repop     |
| POST    | `/live/ingest` | Ingest une capture (`?path=data/…​.pcapng`) |
| POST    | `/live/reset`  | Vide l'état du moniteur                    |

> ⚠️ Retrait de groupe (`GM|-…`) et délai de repop **restent à confirmer** sur une
> capture de combat (rester sur une map Bambouto, tuer un groupe, attendre le repop).

## ⚠️ Avertissement

Sniffer le jeu officiel peut contrevenir aux CGU d'Ankama (risque de sanction).
Les données items/recettes sont la propriété d'Ankama (dump communautaire, usage
perso). Outil fourni pour un usage en lecture seule sur tes propres données.

```
