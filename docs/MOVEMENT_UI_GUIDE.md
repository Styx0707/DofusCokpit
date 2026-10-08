# Interface de Mouvement — Guide d'intégration

## Ce qui a été livré

### 1. **Pathfinder** (`app/core/pathfinder.py`)
- A* simplifié pour calcul de chemin d'une cellule à l'autre
- Compresse automatiquement le chemin en waypoints (points d'inflexion)
- Retourne une liste `[(direction, cell_id), ...]` prête pour GA001

### 2. **API Bot** (`app/network/bot_api.py`)
Trois nouveaux endpoints:

#### `POST /bot/login` — Authentifier un bot
```json
{
  "auth_host": "login.server.fr",
  "auth_port": 5555,
  "game_host": "game.server.fr",
  "game_port": 5555,
  "account_id": 1,
  "username": "player",
  "password": "secret",
  "character_id": 12345,
  "character_name": "MyChar"
}
```

Retourne:
```json
{
  "status": "connected",
  "account_id": 1,
  "character_id": 12345,
  "character_name": "MyChar",
  "ticket_at": "token..."
}
```

#### `POST /bot/move` — Envoyer un mouvement (A→B)
```json
{
  "account_id": 1,
  "character_id": 12345,
  "start_cell": 100,
  "goal_cell": 250
}
```

Retourne:
```json
{
  "status": "success",
  "account_id": 1,
  "character_id": 12345,
  "start_cell": 100,
  "goal_cell": 250,
  "waypoints": [[0, 100], [1, 150], [2, 200], [3, 250]],
  "waypoint_count": 4
}
```

#### `POST /bot/disconnect` — Déconnecter un bot
```json
{
  "account_id": 1,
  "character_id": 12345
}
```

#### `GET /bot/status` — Vérifier le statut
Optionnel: `?account_id=1&character_id=12345` pour un bot spécifique.

### 3. **Interface UI** (section à ajouter à `live.html`)

Voir `app/static/live_movement.html` pour la structure complète.

**Section à insérer entre les divs "topmaps" et "routebox":**

```html
<div class="minimap" id="movebox">
    <div class="mmhead">🚀 Mouvement simple (A → B)</div>
    <div style="padding: 10px;">
        <div style="display: flex; gap: 10px; margin: 8px 0; align-items: center;">
            <label>Compte:</label>
            <select id="moveaccount" style="flex: 1;">
                <option value="">Choisir…</option>
            </select>
        </div>
        <div style="display: flex; gap: 10px; margin: 8px 0; align-items: center;">
            <label style="width: 60px;">De (cell):</label>
            <input id="movecellstart" type="number" min="0" max="559" style="width: 80px;">
        </div>
        <div style="display: flex; gap: 10px; margin: 8px 0; align-items: center;">
            <label style="width: 60px;">À (cell):</label>
            <input id="movecellgoal" type="number" min="0" max="559" style="width: 80px;">
        </div>
        <div style="display: flex; gap: 10px; margin: 8px 0;">
            <button id="movesubmit" style="flex: 1;">📍 Envoyer</button>
        </div>
        <div id="moveresult"></div>
    </div>
</div>
```

**CSS à ajouter au `<style>`:**

```css
.moveinput {
    width: 80px;
    background: var(--surface);
    color: var(--ink);
    border: 1px solid var(--line);
    border-radius: 6px;
    padding: 6px 8px;
    font-size: 13px;
}

#moveresult {
    margin-top: 10px;
    padding: 8px;
    border-radius: 6px;
    font-size: 12px;
    display: none;
}

#moveresult.success {
    background: rgba(47, 191, 47, 0.15);
    border: 1px solid var(--good);
    color: var(--good);
    display: block;
}

#moveresult.error {
    background: rgba(240, 88, 74, 0.15);
    border: 1px solid var(--bad);
    color: var(--bad);
    display: block;
}
```

**JavaScript à ajouter au `<script>`:**

```javascript
// Peupler la liste des comptes
function refreshMoveAccounts() {
    const sel = $("moveaccount");
    const opts = (accounts || [])
        .map((a, i) => `<option value="${i}">${a.name || a.label}</option>`)
        .join("");
    if (opts) {
        sel.innerHTML = '<option value="">Choisir…</option>' + opts;
    }
}

// Envoyer un mouvement
$("movesubmit").onclick = async () => {
    const idx = parseInt($("moveaccount").value, 10);
    const start = parseInt($("movecellstart").value, 10);
    const goal = parseInt($("movecellgoal").value, 10);
    const result = $("moveresult");
    
    if (Number.isNaN(idx) || idx < 0 || idx >= (accounts || []).length) {
        result.textContent = "❌ Choisir un compte valide";
        result.className = "error";
        return;
    }
    if (Number.isNaN(start) || Number.isNaN(goal) || start < 0 || start > 559 || goal < 0 || goal > 559) {
        result.textContent = "❌ Cellules invalides (0-559)";
        result.className = "error";
        return;
    }
    
    result.textContent = "Calcul du chemin…";
    result.className = "success";
    
    const acc = accounts[idx];
    try {
        const r = await fetch("/bot/move", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({
                account_id: acc.account_id || 1,
                character_id: acc.character_id || 0,
                start_cell: start,
                goal_cell: goal,
            }),
        });
        const j = await r.json();
        
        if (r.ok) {
            const wp = j.waypoints || [];
            result.innerHTML = `✅ Mouvement envoyé<br><b>${wp.length} waypoint(s)</b><br>`
                + `${j.start_cell} → ${j.goal_cell}`;
            result.className = "success";
        } else {
            result.textContent = "❌ " + (j.detail || j.error || "Erreur serveur");
            result.className = "error";
        }
    } catch (e) {
        result.textContent = "❌ Erreur réseau: " + e.message;
        result.className = "error";
    }
};

// Rafraîchir la liste des comptes à chaque poll
const origRender = render;
render = function() {
    origRender();
    refreshMoveAccounts();
};
```

## Usage

### Étape 1: Authentifier un bot
```bash
curl -X POST http://localhost:8000/bot/login \
  -H "Content-Type: application/json" \
  -d '{
    "auth_host": "localhost",
    "auth_port": 5555,
    "game_host": "localhost",
    "game_port": 5555,
    "account_id": 1,
    "username": "testuser",
    "password": "testpass",
    "character_id": 999,
    "character_name": "TestChar"
  }'
```

### Étape 2: Envoyer un mouvement
```bash
curl -X POST http://localhost:8000/bot/move \
  -H "Content-Type: application/json" \
  -d '{
    "account_id": 1,
    "character_id": 999,
    "start_cell": 100,
    "goal_cell": 350
  }'
```

### Étape 3: Vérifier le statut
```bash
curl http://localhost:8000/bot/status
```

## Limitations

1. **Pas d'obstacles** — Le pathfinder ignore les murs/objets. Le serveur validera et rejettera si bloqué.
2. **Pas de cell ID de grille** — Les coordonnées sont des cellules Dofus (0-559), pas des [x,y] de la minimap.
3. **Pas de persistance** — Les bots sont en mémoire. Redémarrage = déconnexion automatique.
4. **Pas d'optimisation de chaîne** — Chaque waypoint est encodé indépendamment.

## Prochaines étapes

1. **Intégrer la section HTML** dans `app/static/live.html`
2. **Adapter les IDs de compte** — Le formulaire UI nécessite l'ID réel du compte pour l'API
3. **Tester avec un serveur réel** — Adapter `auth_host`, `auth_port`, `game_host`, `game_port`
4. **Ajouter un pathfinder réel** — Inclure les obstacles (données de map déchiffrées)
5. **Persistance** — Sauvegarder/restaurer les sessions bots

## Tests rapides

### Pathfinder
```python
from app.core.pathfinder import calculate_route

# Chemin de la cellule 100 à 250
waypoints = calculate_route(100, 250)
print(waypoints)  # [(0, 100), (1, 150), (2, 200), (3, 250)]
```

### API bot
```bash
# Tous les endpoints retournent JSON
curl http://localhost:8000/bot/status | python -m json.tool
```
