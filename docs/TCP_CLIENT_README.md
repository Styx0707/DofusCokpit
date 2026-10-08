# Client TCP Dofus Retro — Livraison complète

Ce document récapitule la **machine d'état TCP stateful** implémentée pour connecter un bot Dofus Retro à un serveur réel.

## 🎯 Ce qui a été livré

### 1. **Machine d'état TCP complète** (`app/network/client.py`)
   - Authentification (username/password → ticket AT)
   - Bascule auth → game server
   - Sélection du personnage
   - Envoi de mouvements (GA001)
   - Réception de messages (GDM, GM, ASK, etc.)
   - Gestion robuste des erreurs et timeouts

### 2. **API haut-niveau** (`app/network/bot.py`)
   - Builder fluent pour configuration simple
   - Méthodes convenantes: `login()`, `select_character()`, `move_to()`, `poll()`
   - Intégration automatique des encodeurs

### 3. **Tests unitaires** (`tests/test_client.py`)
   - Couverture complète de la machine d'état
   - Mocks des sockets TCP
   - Validations du protocole
   - Lancer: `pytest tests/test_client.py -v`

### 4. **Exemple d'usage** (`examples/bot_example.py`)
   - Flux complet: auth → char select → move → listen
   - Gestion d'erreurs
   - À adapter avec vos coordonnées serveur

### 5. **Documentation**
   - `docs/CLIENT_ARCHITECTURE.md` — architecture détaillée et diagrammes
   - `docs/SERVER_INTEGRATION.md` — guide pour connecter à un serveur réel
   - Cette file

## 🚀 Démarrage rapide

### Installation (zéro dépendance externe)

Aucune installation. Le client utilise uniquement la stdlib Python 3.10+.

```bash
python3 --version  # Vérifier >= 3.10
```

### Exemple minimal

```python
from app.network.bot import DofusBot
from app.network.client import LoginCredentials

# Créer un bot
bot = DofusBot.builder() \
    .auth("localhost", 5555)      # Serveur d'auth
    .game("localhost", 5555)      # Serveur de jeu
    .build()

# Authentifier
if bot.login(LoginCredentials("player", "password")):
    # Sélectionner un personnage
    if bot.select_character(12345, "MyChar"):
        # Envoyer un mouvement
        bot.move_to([(0, 100)])  # direction 0, cellule 100
        
        # Écouter les réponses
        for msg in bot.poll(max_messages=10):
            print(msg)
    
    bot.disconnect()
```

## 📊 Diagramme d'état

```
DISCONNECTED ──connect_auth()──> AUTH_CONNECTED
                                      │
                              login(username, pwd)
                                      │
                                      ↓
                                 LOGGED_IN (AT ✓)
                                      │
                             connect_game()
                                      │
                                      ↓
                              GAME_CONNECTED
                                      │
                          select_character()
                                      │
                                      ↓
                               GAME_ACTIVE
                              (envoi GA001 ✓)
                                      │
                         send_movement(), receive_messages()
```

## 🔧 Configuration serveur

### Serveur local de test
```python
bot = DofusBot.builder().auth("127.0.0.1", 5555).game("127.0.0.1", 5555).build()
```

### Dofus Retro officiel
```python
bot = DofusBot.builder() \
    .auth("login.dofusretro.com", 443) \
    .game("game.dofusretro.com", 443) \
    .build()
```

### Serveur privé
```python
bot = DofusBot.builder() \
    .auth("auth.myserver.fr", 5555) \
    .game("game.myserver.fr", 5555) \
    .build()
```

Adaptez `host` et `port` selon votre serveur cible.

## 📝 API complète

### DofusClient (bas-niveau)

```python
from app.network.client import DofusClient, LoginCredentials, ClientState

client = DofusClient(auth_host, auth_port, game_host, game_port)

# Cycle de vie
client.connect_auth() -> bool
client.login(LoginCredentials) -> bool
client.connect_game() -> bool
client.select_character(id, name) -> bool

# Gameplay
client.send_movement(path_encoded: str) -> bool
client.receive_messages(max=10) -> List[str]
client.disconnect() -> None

# Introspection
client.state -> ClientState
client.session -> GameSession | None
client.last_error -> str | None
```

### DofusBot (haut-niveau)

```python
from app.network.bot import DofusBot, DofusBotBuilder

# Builder
bot = DofusBot.builder() \
    .auth(host, port) \
    .game(host, port) \
    .build()

# Authentification
bot.login(LoginCredentials) -> bool
bot.select_character(id, name) -> bool

# Gameplay
bot.move_to([(direction, cell), ...]) -> bool
bot.poll(max_messages=10) -> List[str]
bot.poll_blocking(timeout=5) -> List[str]

# État
bot.is_connected() -> bool
bot.last_error() -> str | None
bot.disconnect() -> None
```

## 🧪 Tests

Lancer les tests:
```bash
pytest tests/test_client.py -v
```

Points testés:
- Transitions d'état valides
- Rejets des actions invalides
- Parsing des messages
- Gestion des erreurs réseau
- Timeouts

## 🐛 Debugging

### Logs détaillés
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Introspection d'état
```python
print(f"State: {bot.client.state.value}")
print(f"Error: {bot.last_error()}")
print(f"Session: {bot.client.session}")
```

### Capture de trafic réseau
Utiliser Wireshark sur le port TCP (5555, 443, etc.) pour voir exactement ce qui est envoyé/reçu.

## 📦 Structure du projet

```
app/network/
  ├── client.py          # Machine d'état TCP
  ├── bot.py             # Orchestrateur haut-niveau
  ├── encoder.py         # Sérialisation (existant)
  ├── protocol.py        # Parsing (existant)
  └── (autres modules)

tests/
  └── test_client.py     # Tests unitaires

examples/
  └── bot_example.py     # Exemple complet

docs/
  ├── TCP_CLIENT_README.md      # Cette file
  ├── CLIENT_ARCHITECTURE.md    # Détails architecture
  └── SERVER_INTEGRATION.md     # Guide intégration serveur
```

## 🔐 Sécurité

### Mot de passe
- **Actuellement**: Envoyé en texte clair (adapté à Dofus Retro 1.29)
- **Futur**: Support du chiffrement RSA via `cryptography`

### Session
- Le ticket AT est gardé en mémoire dans `client.session`
- Pas de persistance en base (par design)
- Passe à l'état ERROR si le serveur ferme la connexion

### Recommendations
- Utiliser HTTPS/TLS si possible (adapter `socket.ssl` si nécessaire)
- Ne pas loguer les identifiants
- Gérer les secrets via variables d'environnement

## ⚠️ Limitations connues

1. **RSA non implémenté** — mot de passe en texte clair
2. **Pas de keep-alive** — le serveur peut fermer inactifs
3. **Single-threaded** — pour N comptes, créer N bots
4. **Pas de reconnexion auto** — à implémenter par wrapper
5. **Buffer de réception basique** — adapté pour messages lents, peut déborder en haute charge

## 🚀 Prochaines étapes

1. **Tester avec un serveur réel** — adapter `auth_host`, `auth_port`, `game_host`, `game_port`
2. **Implémenter un pathfinder** — pour générer automatiquement les waypoints
3. **Ajouter une IA de farming** — utiliser `bot.poll()` pour réagir aux monstres
4. **Optimiser pour multi-compte** — ThreadPoolExecutor + N bots
5. **Ajouter keep-alive** — ping périodique pour éviter déconnexions

## 📚 Ressources

- `docs/CLIENT_ARCHITECTURE.md` — diagrammes, protocole détaillé
- `docs/SERVER_INTEGRATION.md` — cas d'usage avancés, performances
- `examples/bot_example.py` — flux complet avec gestion d'erreurs
- `tests/test_client.py` — exemples de test, états valides/invalides

## 💡 Tips

**Déboguer une authentication échouée:**
```python
creds = LoginCredentials("user", "pass")
if bot.login(creds):
    print("✓ Login OK")
else:
    print(f"✗ {bot.last_error()}")
```

**Attendre une réponse du serveur:**
```python
bot.move_to(waypoints)
responses = bot.poll_blocking(timeout=2)  # Attendre 2s max
```

**Traiter les messages reçus:**
```python
from app.network.protocol import parse_map_change, parse_map_actors

for msg in bot.poll():
    if msg.startswith("GDM"):
        map_id = parse_map_change(msg)
        print(f"Entered map: {map_id}")
    elif msg.startswith("GM"):
        actors = parse_map_actors(msg)
        print(f"Actors: {actors}")
```

## ✅ Checklist avant déploiement

- [ ] Tester localement avec un émulateur
- [ ] Adapter host/port au serveur cible
- [ ] Gérer les identifiants de manière sécurisée
- [ ] Implémenter keep-alive si nécessaire
- [ ] Tester la reconnexion après timeout
- [ ] Activer les logs en production
- [ ] Monitorer l'utilisation CPU/mémoire
- [ ] Respecter les ToS du serveur (rate limiting, etc.)

---

**Version**: 1.0  
**Date**: 2026-09-30  
**Auteur**: Claude Agent  
**Status**: Prêt pour intégration et test
