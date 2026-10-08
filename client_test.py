import socket
import time
from app.network.encoder import encode_movement_path

# Cible locale par défaut (ton émulateur)
HOST = "host.docker.internal"
PORT = 5555

def inject_movement(sock: socket.socket, waypoints: list[tuple[int, int]]):
    """
    Génère la trame GA001 et l'envoie sur le socket actif.
    Format attendu pour waypoints : [(direction, cell_id), ...]
    """
    # 1. Génération de la charge utile via ton encodeur
    payload = encode_movement_path(waypoints)

    # 2. Formatage avec le préfixe GA001 et le délimiteur de fin obligatoire (\x00)
    packet = f"GA001{payload}\x00".encode("utf-8")

    print(f"[*] Envoi de la trame : {packet!r}")
    sock.sendall(packet)

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        print(f"[*] Connexion à {HOST}:{PORT}...")
        s.connect((HOST, PORT))

        # Réception de la bannière (Hello Game)
        banner = s.recv(1024).decode("utf-8", errors="ignore")
        print(f"[<] Serveur : {banner.strip()}")

        # IMPORTANT : Sur un serveur réel ou un émulateur complet, tu dois
        # t'authentifier (AT) et sélectionner ton perso (AS) avant d'envoyer un GA001.
        # Si tu testes directement ton GameActionHandler isolé, tu peux émettre direct.

        time.sleep(0.5) # Légère pause pour simuler le délai client

        # Exemple de waypoints (à remplacer par la sortie de ton A*)
        # Exemple : Direction 1 vers la cellule 280, puis direction 2 vers 310
        chemin_test = [(1, 280), (2, 310)]

        inject_movement(s, chemin_test)

        # Attente de la confirmation (GKK ou GA;1;...)
        response = s.recv(1024).decode("utf-8", errors="ignore")
        print(f"[<] Réponse   : {response.strip()}")

if __name__ == "__main__":
    main()