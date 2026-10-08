# ✨ Nouvelle fonctionnalité : Client TCP Dofus Retro avec machine d'état

**Ajouté le**: 2026-09-30

Un **client TCP stateful complet** capable de s'authentifier auprès d'un serveur Dofus Retro, de gérer une session en jeu, et d'envoyer des commandes (mouvements).

## 🎯 Rapide démarrage

### Cas d'usage simple

```python
from app.network.bot import DofusBot
from app.network.client import LoginCredentials

# 1. Créer un bot
bot = DofusBot.builder() \
    .auth("login.example.fr", 5555) \
    .game("game.example.fr", 5555) \
    .build()

# 2. S'authentifier
creds = LoginCredentials(username="player", password="secret")
if bot.login(creds):
    # 3. Sélectionner un personnage
    bot.select_character(12345, "MyCharacter")
    
    # 4. Envoyer un mouvement
    bot.move_to([(0, 100)])  # direction 0, cellule 100
    
    # 5. Écouter les réponses
    for msg in bot.poll():
        print(f"Server: {msg}")
    
    bot.disconnect()
```

## 📚 Documentation complète

- **[TCP_CLIENT_README.md](docs/TCP_CLIENT_README.md)** — Vue d'ensemble, API, checklist
- **[CLIENT_ARCHITECTURE.md](docs/CLIENT_ARCHITECTURE.md)** — Diagrammes, protocole, limitations
- **[SERVER_INTEGRATION.md](docs/SERVER_INTEGRATION.md)** — Configuration serveur, optimisations

## 📂 Fichiers nouveaux

```
app/network/
├── client.py              ← Client TCP + machine d'état (350 lignes)
└── bot.py                 ← Orchestrateur haut-niveau (120 lignes)

tests/
├── test_client.py         ← 14 tests unitaires
└── test_integration.py    ← 7 tests d'intégration

examples/
└── bot_example.py         ← Exemple d'usage complet

docs/
├── TCP_CLIENT_README.md         ← Guide de démarrage
├── CLIENT_ARCHITECTURE.md       ← Détails techniques
└── SERVER_INTEGRATION.md        ← Configuration serveur
```

## 🔧 Machine d'état

Transitions garanties:
```
DISCONNECTED → AUTH_CONNECTED → LOGGED_IN → GAME_CONNECTED → GAME_ACTIVE
                                 (ticket AT)
```

À tout moment, une erreur réseau bascule en **ERROR**.

## ✨ Caractéristiques

✅ **Authentification RSA/texte clair**  
✅ **Gestion de session (ticket AT)**  
✅ **Bascule auth → game server**  
✅ **Sélection de personnage (AS)**  
✅ **Envoi de mouvements (GA001)**  
✅ **Réception non-bloquante**  
✅ **Gestion robuste des erreurs**  
✅ **Zéro dépendances externes**  
✅ **21 tests (unitaires + intégration)**  

## 🧪 Tests

```bash
# Tests unitaires
pytest tests/test_client.py -v

# Tests d'intégration
pytest tests/test_integration.py -v

# Tous les tests
pytest tests/test_*.py -v
```

## 🎓 Exemple complet

Voir `examples/bot_example.py` pour un flux complet avec gestion d'erreurs.

## 🚀 Prochaines étapes

1. **Adapter les coordonnées serveur** dans `bot_example.py`
2. **Tester avec un serveur de test** (local ou publique)
3. **Ajouter un pathfinder** pour générer automatiquement les waypoints
4. **Implémenter une IA de farming** en analysant les `GM` (monstres)

## ⚠️ Limitations

- RSA chiffrement pas encore implémenté (texte clair pour l'instant)
- Pas de keep-alive (à ajouter si serveur timeout)
- Single-threaded (créer N bots pour N comptes)

Voir `docs/SERVER_INTEGRATION.md` pour solutions.

## 📝 Note

Tous les nouveaux modules respectent l'architecture existante et n'ajoutent **zéro dépendance externe**. Compatibilité 100% avec le reste du projet.
