"""Tests d'intégration simples pour valider l'architecture complète.

Peut être lancé sans serveur réel (mocks TCP).
"""
import pytest
from unittest.mock import MagicMock, patch

# Test que tous les imports marchent
def test_imports():
    """Vérifie que tous les modules peuvent être importés."""
    from app.network.client import (
        DofusClient, DofusClientBuilder, LoginCredentials,
        ClientState, GameSession
    )
    from app.network.bot import DofusBot, DofusBotBuilder
    from app.network.encoder import encode_movement_path
    from app.network.protocol import decode_movement_path

    assert DofusClient is not None
    assert DofusBot is not None
    assert encode_movement_path is not None
    assert decode_movement_path is not None


def test_full_pipeline():
    """Test complet: builder → auth → game → move."""
    from app.network.bot import DofusBot
    from app.network.client import LoginCredentials, ClientState

    # Builder fluent
    bot = DofusBot.builder() \
        .auth("auth.example.fr", 5555) \
        .game("game.example.fr", 5555) \
        .build()

    # Vérifier que le client est prêt
    assert bot.client.state == ClientState.DISCONNECTED
    assert bot.is_connected() is False

    # Mock la connexion
    with patch('socket.socket') as mock_socket_class:
        mock_sock = MagicMock()
        mock_socket_class.return_value = mock_sock
        mock_sock.recv.side_effect = [
            b"ticket_abc123\n",  # Auth response
            b"ASK|12345|...\n",   # Character selection response
        ]

        # Étape 1: Connexion
        assert bot.client.connect_auth() is True
        assert bot.client.state == ClientState.AUTH_CONNECTED

        # Étape 2: Login
        creds = LoginCredentials(username="player", password="secret")
        assert bot.client.login(creds) is True
        assert bot.client.state == ClientState.LOGGED_IN
        assert bot.client.session.ticket_at == "ticket_abc123"

        # Étape 3: Reconnexion au game server
        assert bot.client.connect_game() is True
        assert bot.client.state == ClientState.GAME_CONNECTED

        # Étape 4: Sélection personnage
        assert bot.client.select_character(12345, "MyChar") is True
        assert bot.client.state == ClientState.GAME_ACTIVE
        assert bot.client.session.character_name == "MyChar"

        # Étape 5: Envoi mouvement
        assert bot.client.send_movement("abcdef") is True

        # Étape 6: Réception messages
        mock_sock.recv.side_effect = [b"GDM|8158|...\nGM|+370;...\n"]
        messages = bot.client.receive_messages(max_messages=10)
        assert len(messages) == 2


def test_encoder_decoder_roundtrip():
    """Valide que encoder/decoder sont inverses."""
    from app.network.encoder import encode_movement_path
    from app.network.protocol import decode_movement_path

    # Waypoints: direction 0→cellule 100, direction 1→cellule 150
    waypoints = [(0, 100), (1, 150)]

    # Encoder
    encoded = encode_movement_path(waypoints)
    assert isinstance(encoded, str)
    assert len(encoded) > 0

    # Decoder (inverse)
    decoded = decode_movement_path(encoded)
    assert decoded == waypoints


def test_error_handling():
    """Test des transitions d'erreur."""
    from app.network.client import DofusClient, ClientState

    client = DofusClient("localhost", 5555, "localhost", 5555)

    # Tentative de login sans auth → ERROR
    assert client.login(None) is False
    assert client.state == ClientState.ERROR

    # Tentative de reconnexion depuis ERROR → fonctionne
    client.state = ClientState.DISCONNECTED
    with patch('socket.socket') as mock_socket_class:
        mock_sock = MagicMock()
        mock_socket_class.return_value = mock_sock
        assert client.connect_auth() is True
        assert client.state == ClientState.AUTH_CONNECTED


def test_bot_builder_fluent_interface():
    """Valide la fluent API."""
    from app.network.bot import DofusBotBuilder

    bot = (DofusBotBuilder()
           .auth("auth.srv.fr", 443)
           .game("game.srv.fr", 443)
           .build())

    assert bot.client.auth_host == "auth.srv.fr"
    assert bot.client.auth_port == 443
    assert bot.client.game_host == "game.srv.fr"
    assert bot.client.game_port == 443


def test_message_parsing():
    """Valide que les parsers fonctionnent."""
    from app.network.protocol import (
        parse_character_list, parse_character_inventory,
        parse_map_change, parse_map_actors
    )

    # ALK: Liste de personnages
    chars = parse_character_list("1|1|12345;MyChar;50;19;0;0;0;1234,5678")
    assert len(chars) == 1
    assert chars[0]["character_id"] == 12345
    assert chars[0]["name"] == "MyChar"

    # GDM: Changement de map
    map_id = parse_map_change("GDM|8158|0|data")
    assert map_id == 8158

    # GM: Acteurs de map (groupe de monstres)
    actors = parse_map_actors("GM|+370;0;0;-1;566;0;0;52")
    assert len(actors) == 1
    assert actors[0]["group_id"] == -1
    assert actors[0]["monsters"][0]["id"] == 566


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
