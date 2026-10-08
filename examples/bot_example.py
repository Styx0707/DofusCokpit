#!/usr/bin/env python3
"""Exemple d'utilisation du client Dofus Retro headless.

Démontre:
  1. Connexion auth + récupération du ticket AT
  2. Connexion au serveur de jeu
  3. Sélection du personnage
  4. Envoi d'un ordre de déplacement GA001
  5. Écoute des messages du serveur

À adapter avec vos identifiants et coordonnées serveur réels.
"""
import logging
import sys
from pathlib import Path

# Ajouter le répertoire parent au PATH pour importer app
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.network.bot import DofusBot
from app.network.client import LoginCredentials


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s"
)


def main():
    """Démonstration complète du flux d'authentification + gameplay."""

    # Configuration du bot
    bot = DofusBot.builder() \
        .auth("login.example.fr", 5555) \
        .game("game.example.fr", 5555) \
        .build()

    # 1. Authentification
    print("[1/5] Authentification...")
    creds = LoginCredentials(username="player_name", password="player_password")
    if not bot.login(creds):
        print(f"❌ Connexion échouée: {bot.last_error()}")
        return False

    print("✅ Authentification réussie")

    # 2. Sélection du personnage
    print("\n[2/5] Sélection du personnage...")
    CHARACTER_ID = 12345  # À remplacer par un vrai ID
    CHARACTER_NAME = "MyCharacter"  # À remplacer
    if not bot.select_character(CHARACTER_ID, CHARACTER_NAME):
        print(f"❌ Sélection échouée: {bot.last_error()}")
        bot.disconnect()
        return False

    print(f"✅ Connecté en tant que {CHARACTER_NAME}")

    # 3. Attendre les messages initiaux (map, acteurs, etc.)
    print("\n[3/5] Réception de la map initiale...")
    initial_msgs = bot.poll_blocking(timeout=2)
    print(f"   Reçu {len(initial_msgs)} messages")
    for msg in initial_msgs[:3]:  # Afficher les 3 premiers
        print(f"   → {msg[:60]}...")

    # 4. Envoyer un ordre de déplacement
    print("\n[4/5] Envoi d'un ordre de déplacement...")
    # Exemple : déplacement simple (direction 0, cellule 100)
    # En pratique, on calculerait le chemin réel avec une IA pathfinding
    waypoints = [(0, 100), (1, 150)]  # 2 segments
    if bot.move_to(waypoints):
        print(f"✅ Mouvement envoyé: {waypoints}")
    else:
        print(f"❌ Mouvement échoué: {bot.last_error()}")

    # 5. Écouter les réponses du serveur
    print("\n[5/5] En écoute des mises à jour du serveur...")
    for i in range(5):
        msgs = bot.poll(max_messages=10)
        if msgs:
            print(f"   Itération {i+1}: {len(msgs)} messages")
            for msg in msgs:
                print(f"     → {msg[:60]}...")
        else:
            print(f"   Itération {i+1}: Aucun message")
        import time
        time.sleep(0.5)

    # Déconnexion
    print("\n[6/6] Déconnexion...")
    bot.disconnect()
    print("✅ Déconnecté")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
