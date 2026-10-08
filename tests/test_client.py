"""Tests unitaires du client TCP Dofus Retro.

Valide la machine d'état et les transitions entre états.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
import socket

from app.network.client import (
    DofusClient, DofusClientBuilder, LoginCredentials, ClientState, GameSession
)
from app.network.bot import DofusBot


class TestDofusClient:
    """Tests de la machine d'état du client TCP."""

    def test_initial_state(self):
        """Le client démarre en état DISCONNECTED."""
        client = DofusClient("localhost", 5555, "localhost", 5555)
        assert client.state == ClientState.DISCONNECTED
        assert client.session is None
        assert client.sock is None

    def test_connect_auth_success(self):
        """connect_auth() doit créer un socket et passer en AUTH_CONNECTED."""
        client = DofusClient("localhost", 5555, "localhost", 5555)

        with patch('socket.socket') as mock_socket_class:
            mock_sock = MagicMock()
            mock_socket_class.return_value = mock_sock

            result = client.connect_auth()

            assert result is True
            assert client.state == ClientState.AUTH_CONNECTED
            assert client.sock is mock_sock
            mock_sock.connect.assert_called_once_with(("localhost", 5555))

    def test_connect_auth_failure(self):
        """connect_auth() doit passer en ERROR en cas de problème de réseau."""
        client = DofusClient("localhost", 5555, "localhost", 5555)

        with patch('socket.socket') as mock_socket_class:
            mock_socket_class.side_effect = OSError("Connection refused")

            result = client.connect_auth()

            assert result is False
            assert client.state == ClientState.ERROR
            assert "Connection refused" in client.last_error

    def test_connect_auth_from_wrong_state(self):
        """connect_auth() doit refuser si déjà connecté."""
        client = DofusClient("localhost", 5555, "localhost", 5555)
        client.state = ClientState.LOGGED_IN

        result = client.connect_auth()

        assert result is False
        assert client.state == ClientState.ERROR

    def test_login_success(self):
        """login() avec auth server simulé doit récupérer le ticket AT."""
        client = DofusClient("localhost", 5555, "localhost", 5555)
        client.state = ClientState.AUTH_CONNECTED

        mock_sock = MagicMock()
        client.sock = mock_sock

        # Simuler la réponse du serveur: un ticket AT
        mock_sock.recv.return_value = b"ticket_abc123\n"

        creds = LoginCredentials(username="user", password="pass")
        result = client.login(creds)

        assert result is True
        assert client.state == ClientState.LOGGED_IN
        assert client.session is not None
        assert client.session.ticket_at == "ticket_abc123"
        mock_sock.sendall.assert_called_once()

    def test_login_auth_failure(self):
        """login() doit gérer les erreurs d'authentification."""
        client = DofusClient("localhost", 5555, "localhost", 5555)
        client.state = ClientState.AUTH_CONNECTED

        mock_sock = MagicMock()
        client.sock = mock_sock

        # Simuler une réponse d'erreur du serveur
        mock_sock.recv.return_value = b"err:Invalid credentials\n"

        creds = LoginCredentials(username="user", password="wrong")
        result = client.login(creds)

        assert result is False
        assert client.state == ClientState.ERROR
        assert "Invalid credentials" in client.last_error

    def test_login_from_wrong_state(self):
        """login() doit refuser si pas authentifié."""
        client = DofusClient("localhost", 5555, "localhost", 5555)
        client.state = ClientState.DISCONNECTED

        creds = LoginCredentials(username="user", password="pass")
        result = client.login(creds)

        assert result is False

    def test_connect_game_success(self):
        """connect_game() doit fermer auth et ouvrir game server."""
        client = DofusClient("localhost", 5555, "localhost", 5555)
        client.state = ClientState.LOGGED_IN
        client.session = GameSession(account_id=1, ticket_at="ticket123",
                                      character_id=0, character_name="")

        mock_old_sock = MagicMock()
        client.sock = mock_old_sock

        with patch('socket.socket') as mock_socket_class:
            mock_new_sock = MagicMock()
            mock_socket_class.return_value = mock_new_sock

            result = client.connect_game()

            assert result is True
            assert client.state == ClientState.GAME_CONNECTED
            mock_old_sock.close.assert_called_once()
            mock_new_sock.connect.assert_called_once_with(("localhost", 5555))

    def test_select_character_success(self):
        """select_character() doit passer en GAME_ACTIVE."""
        client = DofusClient("localhost", 5555, "localhost", 5555)
        client.state = ClientState.GAME_CONNECTED
        client.session = GameSession(account_id=1, ticket_at="ticket123",
                                      character_id=0, character_name="")

        mock_sock = MagicMock()
        client.sock = mock_sock
        mock_sock.recv.return_value = b"ASK|12345|...\n"  # Message initial

        result = client.select_character(12345, "TestChar")

        assert result is True
        assert client.state == ClientState.GAME_ACTIVE
        assert client.session.character_id == 12345
        assert client.session.character_name == "TestChar"

    def test_send_movement_success(self):
        """send_movement() doit envoyer GA001 depuis GAME_ACTIVE."""
        client = DofusClient("localhost", 5555, "localhost", 5555)
        client.state = ClientState.GAME_ACTIVE

        mock_sock = MagicMock()
        client.sock = mock_sock

        result = client.send_movement("abcdef")

        assert result is True
        mock_sock.sendall.assert_called_once()
        call_args = mock_sock.sendall.call_args[0][0]
        assert b"GA;1;abcdef" in call_args

    def test_send_movement_wrong_state(self):
        """send_movement() doit refuser si pas en jeu."""
        client = DofusClient("localhost", 5555, "localhost", 5555)
        client.state = ClientState.GAME_CONNECTED

        result = client.send_movement("abcdef")

        assert result is False

    def test_disconnect(self):
        """disconnect() doit fermer la connexion et revenir en DISCONNECTED."""
        client = DofusClient("localhost", 5555, "localhost", 5555)
        client.state = ClientState.GAME_ACTIVE

        mock_sock = MagicMock()
        client.sock = mock_sock

        client.disconnect()

        assert client.state == ClientState.DISCONNECTED
        assert client.sock is None
        assert client.session is None
        mock_sock.close.assert_called_once()

    def test_receive_messages_parses_complete_lines(self):
        """receive_messages() doit parser les messages séparés par \\n."""
        client = DofusClient("localhost", 5555, "localhost", 5555)
        client.state = ClientState.GAME_ACTIVE

        mock_sock = MagicMock()
        client.sock = mock_sock

        # Simuler 2 messages complets
        mock_sock.recv.return_value = b"GDM|8158|...\nGM|+370;5;21;...\n"

        messages = client.receive_messages(max_messages=10)

        assert len(messages) == 2
        assert messages[0].startswith("GDM|")
        assert messages[1].startswith("GM|")


class TestDofusClientBuilder:
    """Tests du builder du client."""

    def test_builder_defaults(self):
        """Builder doit créer un client avec host/port par défaut."""
        builder = DofusClientBuilder()
        client = builder.build()

        assert client.auth_host == "localhost"
        assert client.auth_port == 5555
        assert client.game_host == "localhost"
        assert client.game_port == 5555

    def test_builder_custom_hosts(self):
        """Builder doit accepter les hôtes personnalisés."""
        client = (DofusClientBuilder()
                  .auth("auth.example.fr", 443)
                  .game("game.example.fr", 443)
                  .build())

        assert client.auth_host == "auth.example.fr"
        assert client.auth_port == 443
        assert client.game_host == "game.example.fr"
        assert client.game_port == 443


class TestDofusBot:
    """Tests du bot haut-niveau."""

    def test_bot_initialization(self):
        """Bot doit s'initialiser avec un client."""
        client = DofusClient("localhost", 5555, "localhost", 5555)
        bot = DofusBot(client)

        assert bot.client is client
        assert bot.current_cell == 0

    def test_bot_builder(self):
        """Builder du bot doit créer un bot avec client prêt."""
        bot = DofusBot.builder() \
            .auth("auth.example.fr", 5555) \
            .game("game.example.fr", 5555) \
            .build()

        assert isinstance(bot, DofusBot)
        assert bot.client.auth_host == "auth.example.fr"
        assert bot.client.game_host == "game.example.fr"

    def test_bot_move_to_encodes_path(self):
        """Bot.move_to() doit encoder le chemin et l'envoyer."""
        client = DofusClient("localhost", 5555, "localhost", 5555)
        client.state = ClientState.GAME_ACTIVE

        mock_sock = MagicMock()
        client.sock = mock_sock

        bot = DofusBot(client)

        # Waypoints: direction 0, cellule 100; direction 1, cellule 150
        waypoints = [(0, 100), (1, 150)]
        result = bot.move_to(waypoints)

        assert result is True
        mock_sock.sendall.assert_called_once()

    def test_bot_move_to_wrong_state(self):
        """Bot.move_to() doit refuser si pas en jeu."""
        client = DofusClient("localhost", 5555, "localhost", 5555)
        client.state = ClientState.DISCONNECTED

        bot = DofusBot(client)
        result = bot.move_to([(0, 100)])

        assert result is False


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
