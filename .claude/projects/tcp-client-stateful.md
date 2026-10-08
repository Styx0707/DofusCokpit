---
name: tcp-client-stateful
description: Machine d'état TCP complète pour Dofus Retro (auth→game→mouvements)
metadata:
  type: project
---

## Machine d'état TCP Dofus Retro — Livraison complète

**Date**: 2026-09-30  
**Status**: ✅ Livré et testé  

### Qu'est-ce qui a été livré

Une **implémentation complète d'un client TCP stateful** pour Dofus Retro capable de:
1. S'authentifier (username/password → ticket AT)
2. Se connecter au serveur de jeu
3. Sélectionner un personnage
4. Envoyer des commandes de jeu (mouvements GA001)
5. Recevoir les mises à jour du serveur

**Why**: Permettre la création de bots headless autonomes maintenant une session authentifiée.

**How to apply**: Utiliser `DofusBot.builder().auth(...).game(...).build()` → `login()` → `select_character()` → `move_to()`.

### Fichiers produits

**Code** (~550 lignes, zéro dépendances):
- `app/network/client.py` — Client TCP + machine d'état (~350)
- `app/network/bot.py` — Orchestrateur haut-niveau (~120)

**Tests** (21 cas):
- `tests/test_client.py` — 14 tests unitaires
- `tests/test_integration.py` — 7 tests d'intégration

**Documentation**:
- `docs/TCP_CLIENT_README.md` — Vue d'ensemble + API
- `docs/CLIENT_ARCHITECTURE.md` — Diagrammes + protocole détaillé
- `docs/SERVER_INTEGRATION.md` — Configuration serveur + optimisations
- `examples/bot_example.py` — Flux complet
- `DELIVERY_SUMMARY.md` — Résumé de livraison

### Machine d'état (5 états)

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
                          select_character(id, name)
                                      │
                                      ↓
                               GAME_ACTIVE
                            (envoi GA001 ✓)
```

Plus: état **ERROR** depuis n'importe quel état si problème réseau.

### API résumée

```python
# Haut-niveau (recommandé)
bot = DofusBot.builder() \
    .auth("login.srv.fr", 5555) \
    .game("game.srv.fr", 5555) \
    .build()

bot.login(LoginCredentials("user", "pass"))
bot.select_character(12345, "CharName")
bot.move_to([(0, 100)])  # direction, cell
for msg in bot.poll():
    print(msg)
bot.disconnect()
```

### Protocole implémenté

**Auth server**: `"user\npass\n"` → `"ticket_AT123\n"` ou `"err:...\n"`
**Game server**: `"char_id\n"` → `"ASK|..."` ou `"err:...\n"`
**Mouvements**: `"GA;1;path_encoded\n"` → réactions du serveur

Extensible pour RSA chiffrement (via `cryptography` futur).

### Architecture par layer

```
DofusBot (haut-niveau)
  └─ move_to() / login() / poll()
     ↓
DofusClient (bas-niveau, stateful)
  └─ send_movement() / receive_messages()
     ↓
socket.socket TCP
  └─ auth_server + game_server
```

### Points forts

✅ Machine d'état stricte (transitions contrôlées)
✅ Zéro dépendances externes (stdlib Python 3.10+)
✅ 21 tests couvrant l'architecture complète
✅ Gestion robuste des erreurs et timeouts
✅ Documentation détaillée (3 docs + exemples)
✅ Builder fluent pour configuration simple
✅ Non-bloquant pour réception messages
✅ Intégration 100% compatible avec le projet

### Limitations connues

1. **RSA pas implémenté** — pwd en texte clair (standard Dofus Retro)
   → À ajouter si serveur le demande (dépendance `cryptography`)

2. **Pas de keep-alive** — serveur peut fermer inactifs
   → À ajouter si timeout observé (ping périodique)

3. **Single-threaded** — créer N `DofusBot` pour N comptes
   → Utiliser `concurrent.futures.ThreadPoolExecutor` pour paralléliser

Tous les points sont documentés dans `SERVER_INTEGRATION.md` avec solutions.

### Testing

```bash
# Tests unitaires
pytest tests/test_client.py -v

# Tests d'intégration
pytest tests/test_integration.py -v

# Tous
pytest tests/ -v
```

Couvre: transitions d'état, erreurs réseau, parsing, timeouts, builders, pipeline complet.

### Prochaines étapes pour l'utilisateur

1. Adapter `auth_host`, `auth_port`, `game_host`, `game_port` à votre serveur
2. Tester avec `examples/bot_example.py`
3. Implémenter un pathfinder pour générer waypoints auto
4. Ajouter IA de farming (analyse `GM` → mouvements)
5. Support multi-compte (ThreadPoolExecutor + N bots)

### Notes d'intégration

- Aucune rupture de compatibilité avec le code existant
- Utilise les **encodeurs existants** (`encoder.py`)
- Utilise les **parsers existants** (`protocol.py`)
- Zéro changement à `requirements.txt`
- Tous les nouveaux modules sont testés et documentés

### À retenir

- Machine d'état **garantit les transitions valides**
- Builder fluent pour **configuration simple**
- Non-bloquant pour **scalabilité**
- Extensible pour **RSA + keep-alive + reconnexion**
