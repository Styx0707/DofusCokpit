# Intégration avec un serveur Dofus Retro réel

## Configuration des coordonnées serveur

Avant de lancer le bot, vous devez connaître les coordonnées du serveur auquel vous vous connectez.

### Serveurs de test locaux

Si vous testez localement (émulateur Dofus Retro):

```python
from app.network.bot import DofusBot
from app.network.client import LoginCredentials

bot = DofusBot.builder() \
    .auth("127.0.0.1", 5555)      # Serveur d'auth local
    .game("127.0.0.1", 5555)      # Serveur de jeu local
    .build()

creds = LoginCredentials(username="testplayer", password="testpass")
bot.login(creds)
```

### Serveurs publics Dofus Retro

Pour les serveurs publics (ex: Dofus Retro officiel, serveurs privés), les coordonnées sont généralement:

```python
# Exemple : Dofus Retro officiel (adapte avec les vraies coordonnées)
bot = DofusBot.builder() \
    .auth("login.dofusretro.com", 443)
    .game("game.dofusretro.com", 443)
    .build()
```

Remplacez avec les coordonnées réelles du serveur cible.

## Protocole d'authentification

### Cas 1: Authentification en texte clair (mode courant)

Le serveur d'auth reçoit les identifiants en texte clair:

```
Client → "username\npassword\n"
Server ← "ticket_AT123456\n"
```

**Implémentation actuelle**: Supporté (classe `DofusClient.login()`).

### Cas 2: Authentification avec chiffrement RSA

Certains serveurs demandent un chiffrement du mot de passe avec une clé RSA.

**Protocole**:
```
Client → "username\n"
Server ← "rsa_modulus|rsa_exponent\n"
Client → (password_chiffré_en_RSA)
Server ← "ticket_AT123456\n"
```

**À implémenter**: Ajouter `cryptography` et adapter `client.login()`.

### Détection du protocole

Le client devrait d'abord essayer texte clair. Si la réponse commence par une clé RSA (hexadécimal), basculer en mode RSA.

```python
# Pseudocode (non implémenté actuellement)
def login_with_auto_detection(self, creds):
    response = self._read_auth_response()
    if response.looks_like_rsa_key():
        return self._login_with_rsa(creds, response)
    else:
        return self._login_plaintext(creds)
```

## Flux complet : du login à la première action

```python
#!/usr/bin/env python3

from app.network.bot import DofusBot
from app.network.client import LoginCredentials
import logging

logging.basicConfig(level=logging.INFO)

# 1. Instancier et configurer
bot = DofusBot.builder() \
    .auth("login.example.fr", 5555) \
    .game("game.example.fr", 5555) \
    .build()

# 2. Authentifier
creds = LoginCredentials(username="player", password="secret")
if not bot.login(creds):
    print(f"Login failed: {bot.last_error()}")
    exit(1)
print("✓ Logged in, got ticket AT")

# 3. Sélectionner un personnage
# (À adapter : récupérer l'ID/nom d'un personnage réel)
CHAR_ID = 12345
CHAR_NAME = "MyCharacter"

if not bot.select_character(CHAR_ID, CHAR_NAME):
    print(f"Character select failed: {bot.last_error()}")
    bot.disconnect()
    exit(1)
print(f"✓ Selected character: {CHAR_NAME}")

# 4. Attendre la map initiale
print("Waiting for map initialization...")
initial_msgs = bot.poll_blocking(timeout=3)
print(f"Received {len(initial_msgs)} initial messages:")
for msg in initial_msgs[:5]:
    if msg.startswith("GDM"):
        print(f"  - Map loaded: {msg[:40]}...")
    elif msg.startswith("GM"):
        print(f"  - Actors: {msg[:40]}...")
    elif msg.startswith("ASK"):
        print(f"  - Inventory: {msg[:40]}...")

# 5. Envoyer une action (exemple: déplacement)
print("\nSending movement command...")
waypoints = [(0, 100)]  # Direction 0, cellule 100
if bot.move_to(waypoints):
    print("✓ Movement sent")
    
    # Attendre la réponse du serveur
    responses = bot.poll_blocking(timeout=2)
    for msg in responses:
        if msg.startswith("GA"):
            print(f"  Server confirmed: {msg[:60]}...")

# 6. Maintenir la session active
print("\nListening for server updates (30s)...")
import time
for i in range(30):
    msgs = bot.poll()
    if msgs:
        print(f"[{i}s] Received {len(msgs)} messages")
    time.sleep(1)

# 7. Déconnexion propre
bot.disconnect()
print("✓ Disconnected")
```

## Gestion des erreurs et reconnexion

### Erreurs courants

| Erreur | Cause | Solution |
|--------|-------|----------|
| `Connection refused` | Serveur offline ou port fermé | Vérifier host/port |
| `Auth failed: Invalid credentials` | Mauvais identifiants | Vérifier username/password |
| `Timeout on character selection` | Serveur lent / surchargé | Augmenter le timeout |
| `Connection closed by server` | Serveur a fermé la session | Implémenter keep-alive |

### Reconnexion automatique (non implémentée)

Vous pouvez wrapper le bot pour gérer les reconnexions:

```python
def login_with_retry(bot, creds, max_retries=3):
    for attempt in range(max_retries):
        try:
            if bot.login(creds):
                return True
        except Exception as e:
            print(f"Attempt {attempt+1}/{max_retries} failed: {e}")
            time.sleep(2 ** attempt)  # Backoff exponentiel
    return False
```

## Optimisations pour un vrai bot

### 1. Keep-alive (ping/pong)

Implémenter un ping périodique pour éviter les timeouts:

```python
def keep_alive(bot, interval=30):
    """Envoie un ping au serveur chaque interval secondes."""
    import time, threading
    
    def pinger():
        while bot.is_connected():
            time.sleep(interval)
            # À adapter selon le protocole du serveur
            # ex: bot.client.sock.sendall(b"ping\n")
    
    thread = threading.Thread(target=pinger, daemon=True)
    thread.start()
```

### 2. Gestion du buffer de réception

Pour les serveurs qui envoient beaucoup de messages rapidement (combats, zones peuplées):

```python
def drain_messages(bot, timeout=1):
    """Récupère TOUS les messages disponibles (jusqu'au timeout)."""
    all_msgs = []
    deadline = time.time() + timeout
    while time.time() < deadline:
        msgs = bot.poll(max_messages=100)
        if not msgs:
            time.sleep(0.01)
        else:
            all_msgs.extend(msgs)
    return all_msgs
```

### 3. Parsing des messages

Créer des parsers pour chaque type de message:

```python
from app.network.protocol import parse_character_inventory, parse_map_actors, parse_map_change

def process_message(msg):
    if msg.startswith("ASK"):
        inventory = parse_character_inventory("ASK" + msg)
        return {"type": "inventory", "data": inventory}
    elif msg.startswith("GM"):
        actors = parse_map_actors(msg)
        return {"type": "actors", "data": actors}
    elif msg.startswith("GDM"):
        map_id = parse_map_change(msg)
        return {"type": "map_change", "data": map_id}
    else:
        return {"type": "unknown", "raw": msg}
```

## Debugging et logging

### Activer les logs détaillés

```python
import logging

# Log TOUT
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
)

# Ou juste le client
logging.getLogger("dofus.client").setLevel(logging.DEBUG)
```

### Capturer le trafic réseau

Pour inspecter exactement ce qui est envoyé/reçu:

```python
# Dans client.py, adapter send/receive pour dumper les bytes:
def send_movement(self, path):
    msg = f"GA;1;{path}\n"
    print(f"SEND: {msg.encode('utf-8')}")  # Voir exactement ce qui est envoyé
    self.sock.sendall(msg.encode("utf-8"))
```

Ou utiliser Wireshark pour capturer le trafic TCP en temps réel.

## Performance

### Nombre de connexions

Un `DofusBot` = une paire de sockets TCP (auth + game). Pour N comptes, créer N bots:

```python
bots = []
for i in range(5):
    bot = DofusBot.builder()...build()
    creds = LoginCredentials(username=f"acc{i}", password="...")
    bot.login(creds)
    bots.append(bot)

# Utiliser en parallèle
import concurrent.futures
with concurrent.futures.ThreadPoolExecutor() as exe:
    exe.map(lambda b: b.move_to([...]), bots)
```

### Latence

- Auth: ~100-300ms (TCP handshake + crypto)
- Character select: ~50-100ms
- Movement send: <10ms
- Message parsing: <1ms

Pour un bot farm rapide, paralléliser les bots.
