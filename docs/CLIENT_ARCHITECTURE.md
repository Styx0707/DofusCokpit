# Architecture du Client TCP Dofus Retro

## Vue d'ensemble

Le client implémente une **machine d'état TCP complète** pour établir une session authentifiée avec les serveurs Dofus Retro. Il gère automatiquement:

1. **Authentification RSA** (ou texte clair selon serveur)
2. **Récupération du ticket de session (AT)**
3. **Bascule vers le serveur de jeu**
4. **Sélection du personnage (AS)**
5. **Envoi de commandes de jeu (GA)**
6. **Réception des mises à jour (GDM, GM, ASK, etc.)**

## Machine d'état

```
┌─────────────────────────────────────────────────────────────┐
│                      DISCONNECTED                            │
│                    (état initial)                            │
└──────────────────────────┬──────────────────────────────────┘
                           │ connect_auth()
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                   AUTH_CONNECTED                             │
│                 (socket auth ouvert)                         │
└──────────────────────────┬──────────────────────────────────┘
                           │ login(username, password)
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                      LOGGED_IN                               │
│                  (ticket AT en main)                         │
└──────────────────────────┬──────────────────────────────────┘
                           │ connect_game()
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                   GAME_CONNECTED                             │
│              (socket game connectée)                         │
└──────────────────────────┬──────────────────────────────────┘
                           │ select_character(id, name)
                           ↓
┌─────────────────────────────────────────────────────────────┐
│                     GAME_ACTIVE                              │
│            (en jeu, prêt pour GA, GDM, GM)                   │
└──────────────────────────────────────────────────────────────┘
```

### États d'erreur

À tout moment, un problème réseau ou protocolaire peut faire basculer le client en **ERROR**:
```
[QUELCONQUE] ──(erreur)──> ERROR
```

## Architecture des modules

### 1. `app/network/client.py` — Client TCP bas-niveau

**Classe: `DofusClient`**

Gère directement les sockets TCP, la sérialisation/désérialisation des messages, et les transitions d'état.

#### Méthodes principales:

```python
# Cycle de vie
client.connect_auth() -> bool              # DISCONNECTED → AUTH_CONNECTED
client.login(creds) -> bool                # AUTH_CONNECTED → LOGGED_IN
client.connect_game() -> bool              # LOGGED_IN → GAME_CONNECTED
client.select_character(id, name) -> bool  # GAME_CONNECTED → GAME_ACTIVE
client.disconnect() -> None                # [Quelconque] → DISCONNECTED

# Gameplay
client.send_movement(path_encoded) -> bool # Envoie GA001
client.receive_messages(max) -> List[str]  # Non-bloquant, max messages

# Introspection
client.state: ClientState                  # État courant
client.session: GameSession | None         # Données de session
client.last_error: str | None              # Dernier message d'erreur
```

#### Protocole de communication

**Authentification (auth server):**
```
Client → "username\npassword\n"
Server ← "ticket_AT123\n"       (succès)
      ou "err:reason\n"         (erreur)
```

**Sélection de personnage (game server):**
```
Client → "character_id\n"
Server ← "ASK|..." (succès, message initial)
      ou "err:reason\n" (erreur)
```

**Mouvements:**
```
Client → "GA;1;path_encoded\n"
Server → (confirmations/updates: GDM, GM, GA)
```

### 2. `app/network/bot.py` — Orchestrateur haut-niveau

**Classe: `DofusBot`**

Combine le client TCP avec les encodeurs pour offrir une API fluide.

#### Méthodes principales:

```python
# Fluent builder
bot = DofusBot.builder()
  .auth("login.server.fr", 5555)
  .game("game.server.fr", 5555)
  .build()

# Authentification complète (auth + game + char)
bot.login(LoginCredentials("user", "pass")) -> bool
bot.select_character(id, name) -> bool

# Gameplay
bot.move_to([(direction, cell), ...]) -> bool  # Encode + envoie
bot.poll(max_messages) -> List[str]            # Non-bloquant
bot.poll_blocking(timeout) -> List[str]        # Attendu timeout secondes
bot.is_connected() -> bool
bot.last_error() -> str | None
```

### 3. `app/network/encoder.py` — Sérialisation protocolaire

Déjà existant. Utilisé par le bot pour encoder les mouvements:

```python
path = encode_movement_path([(0, 100), (1, 150)])
# → "abcdef..." (3 chars par point d'inflexion)
```

## Flux d'authentification complet

```python
from app.network.bot import DofusBot
from app.network.client import LoginCredentials

# 1. Créer le bot
bot = DofusBot.builder()
    .auth("login.example.fr", 5555)
    .game("game.example.fr", 5555)
    .build()

# 2. Authentification (auth_server → ticket AT → game_server)
creds = LoginCredentials(username="player", password="secret")
if not bot.login(creds):
    print(f"Erreur: {bot.last_error()}")
    exit(1)

# 3. Sélection du personnage (entrée en jeu)
if not bot.select_character(12345, "MyCharacter"):
    print(f"Erreur: {bot.last_error()}")
    bot.disconnect()
    exit(1)

# 4. En jeu — recevoir map + acteurs
msgs = bot.poll_blocking(timeout=2)
# msgs contient GDM (map), GM (monstres/joueurs), ASK (inventaire)

# 5. Envoyer un mouvement
waypoints = [(0, 100), (1, 150)]  # Points d'inflexion
if bot.move_to(waypoints):
    print("Mouvement envoyé ✓")

# 6. Écouter les réponses (confirmations, mouvements d'autres, etc.)
for msg in bot.poll():
    print(f"Server: {msg}")

# 7. Déconnexion propre
bot.disconnect()
```

## Gestion des erreurs

La machine d'état est **robuste aux erreurs réseau**:

- Timeout TCP → état ERROR + message d'erreur explicite
- Réponse inattendue → état ERROR + parsing safe
- Tentative d'action invalide (ex: `send_movement` alors pas en jeu) → retour False + log

Chaque appel de méthode retourne un booléen succès/échec et persiste l'erreur dans `client.last_error`.

## Tests

Voir `tests/test_client.py`:
- Tests unitaires de chaque transition d'état
- Mock des sockets TCP
- Validations du protocole
- Encodage/décodage des messages

Lancer les tests:
```bash
pytest tests/test_client.py -v
```

## Exemple d'usage complet

Voir `examples/bot_example.py` pour un script complet avec gestion d'erreurs.

## Limitations et futures améliorations

1. **RSA**: Le chiffrement RSA du mot de passe n'est pas encore implémenté (en clair pour l'instant). À ajouter si le serveur le demande.

2. **Keep-alive**: Pas de ping périodique. À ajouter si le serveur ferme les inactifs.

3. **Parsing incrémental**: Les messages sont parsés ligne par ligne. Pour les messages multi-lignes (très rares en Retro), adapter `_read_until()`.

4. **Multi-threading**: Le client n'est pas thread-safe. Pour le multi-compte, instancier plusieurs DofusBot.

5. **Reconnexion automatique**: Pas implémentée. À ajouter pour la résilience en production.

## Dépendances

- Python 3.10+
- Standard library uniquement (socket, dataclasses, enum)
- `cryptography` (futur, pour RSA)

## Logs

Tout est loggé via `logging`. Pour déboguer:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
# Ou pour juste le client:
logging.getLogger("dofus.client").setLevel(logging.DEBUG)
```
