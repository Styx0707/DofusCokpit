"""Client TCP Dofus Retro — machine d'état auth -> game -> en jeu.

Contrairement au reste du module ``app.network`` (sniffer PASSIF + encodeurs de
fixtures), ce client OUVRE une connexion et ÉMET des messages vers un serveur.

⚠️ Il établit une SESSION INDÉPENDANTE du vrai client de jeu. Sur un serveur
Dofus Retro officiel, un compte déjà connecté par le client officiel sera
déconnecté si on ouvre une 2ᵉ session : ce client vise donc un ÉMULATEUR / serveur
privé (cf. ``app.network.game_action`` et ``app.network.encoder``, pensés « pour
un émulateur open-source »), pas à doubler une session officielle.

Le protocole Dofus est textuel, un message par trame, terminé par un délimiteur.
Le vrai serveur Retro utilise l'octet nul ``\\x00`` ; les tests unitaires (mocks)
raisonnent en lignes ``\\n``. Le délimiteur est donc configurable (``delimiter``),
par défaut ``\\n`` pour rester test-compatible — passe ``\\x00`` face à un vrai ému.
"""
from __future__ import annotations

import logging
import socket
from dataclasses import dataclass
from enum import Enum
from typing import List, Optional

logger = logging.getLogger("dofus.client")


class ClientState(Enum):
    """États de la machine à états du client (cf. docs/CLIENT_ARCHITECTURE.md)."""
    DISCONNECTED = "disconnected"
    AUTH_CONNECTED = "auth_connected"
    LOGGED_IN = "logged_in"
    GAME_CONNECTED = "game_connected"
    GAME_ACTIVE = "game_active"
    ERROR = "error"


@dataclass
class LoginCredentials:
    """Identifiants d'un compte (texte clair — cf. limites RSA dans les docs)."""
    username: str
    password: str


@dataclass
class GameSession:
    """Données de session courante : ticket d'auth + perso sélectionné."""
    account_id: int
    ticket_at: str
    character_id: int
    character_name: str


class DofusClient:
    """Socket TCP + sérialisation + transitions d'état.

    Chaque méthode de transition renvoie un booléen succès/échec et, en cas
    d'échec, bascule en ``ERROR`` avec ``last_error`` renseigné (sauf refus de
    transition depuis un mauvais état, qui renvoie simplement False)."""

    def __init__(self, auth_host: str, auth_port: int,
                 game_host: str, game_port: int, *,
                 delimiter: str = "\n", timeout: float = 5.0) -> None:
        self.auth_host = auth_host
        self.auth_port = auth_port
        self.game_host = game_host
        self.game_port = game_port
        self.delimiter = delimiter
        self.timeout = timeout

        self.state = ClientState.DISCONNECTED
        self.session: Optional[GameSession] = None
        self.sock: Optional[socket.socket] = None
        self.last_error: Optional[str] = None
        self._recv_buf = ""

    # -- Cycle de vie --------------------------------------------------------

    def connect_auth(self) -> bool:
        """DISCONNECTED/ERROR -> AUTH_CONNECTED (ouvre le socket d'auth)."""
        if self.state not in (ClientState.DISCONNECTED, ClientState.ERROR):
            return self._fail(f"connect_auth refusé depuis l'état {self.state.value}")
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(self.timeout)
            self.sock.connect((self.auth_host, self.auth_port))
        except OSError as exc:
            return self._fail(f"connexion auth échouée : {exc}")
        self._recv_buf = ""
        self.state = ClientState.AUTH_CONNECTED
        logger.info("auth connecté (%s:%s)", self.auth_host, self.auth_port)
        return True

    def login(self, creds: Optional[LoginCredentials]) -> bool:
        """AUTH_CONNECTED -> LOGGED_IN : envoie les identifiants, lit le ticket AT.

        Réponse serveur : le ticket (ligne quelconque) en cas de succès, ou une
        ligne commençant par ``err`` (ex. ``err:Invalid credentials``) en échec."""
        if self.state != ClientState.AUTH_CONNECTED or creds is None:
            return self._fail("login refusé (pas authentifié ou identifiants absents)")
        try:
            self._send_raw(f"{creds.username}{self.delimiter}{creds.password}")
            reply = self._recv_line()
        except OSError as exc:
            return self._fail(f"login — erreur réseau : {exc}")
        if reply is None:
            return self._fail("login — aucune réponse du serveur")
        if reply.lower().startswith("err"):
            return self._fail(f"auth refusée : {reply.split(':', 1)[-1].strip()}")
        self.session = GameSession(account_id=0, ticket_at=reply.strip(),
                                   character_id=0, character_name="")
        self.state = ClientState.LOGGED_IN
        logger.info("authentifié, ticket AT reçu")
        return True

    def connect_game(self) -> bool:
        """LOGGED_IN -> GAME_CONNECTED : ferme le socket auth, ouvre le game."""
        if self.state != ClientState.LOGGED_IN:
            return self._fail(f"connect_game refusé depuis l'état {self.state.value}")
        if self.sock is not None:
            try:
                self.sock.close()
            except OSError:
                pass
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.settimeout(self.timeout)
            self.sock.connect((self.game_host, self.game_port))
        except OSError as exc:
            return self._fail(f"connexion game échouée : {exc}")
        self._recv_buf = ""
        self.state = ClientState.GAME_CONNECTED
        logger.info("game connecté (%s:%s)", self.game_host, self.game_port)
        return True

    def select_character(self, character_id: int, character_name: str) -> bool:
        """GAME_CONNECTED -> GAME_ACTIVE : envoie l'id du perso, lit le 1er message."""
        if self.state != ClientState.GAME_CONNECTED or self.session is None:
            return self._fail(f"select_character refusé depuis {self.state.value}")
        try:
            self._send_raw(str(character_id))
            reply = self._recv_line()
        except OSError as exc:
            return self._fail(f"select_character — erreur réseau : {exc}")
        if reply is not None and reply.lower().startswith("err"):
            return self._fail(f"sélection refusée : {reply.split(':', 1)[-1].strip()}")
        self.session.character_id = character_id
        self.session.character_name = character_name
        self.state = ClientState.GAME_ACTIVE
        logger.info("en jeu : %s (#%s)", character_name, character_id)
        return True

    def disconnect(self) -> None:
        """[Quelconque] -> DISCONNECTED : ferme le socket et oublie la session."""
        if self.sock is not None:
            try:
                self.sock.close()
            except OSError:
                pass
        self.sock = None
        self.session = None
        self._recv_buf = ""
        self.state = ClientState.DISCONNECTED

    # -- Gameplay ------------------------------------------------------------

    def send_movement(self, path_encoded: str) -> bool:
        """Envoie un ordre de déplacement GA001 (format client->serveur GA;1;<path>)."""
        return self.send(f"GA;1;{path_encoded}")

    def send(self, message: str) -> bool:
        """Émet un message de jeu brut (sans délimiteur, ajouté ici). Exige GAME_ACTIVE."""
        if self.state != ClientState.GAME_ACTIVE:
            logger.warning("send refusé : état %s (attendu GAME_ACTIVE)", self.state.value)
            return False
        try:
            self._send_raw(message)
        except OSError as exc:
            self._fail(f"send — erreur réseau : {exc}")
            return False
        return True

    def receive_messages(self, max_messages: int = 10) -> List[str]:
        """Lit (non bloquant au-delà du timeout socket) jusqu'à ``max_messages``
        messages complets déjà bufferisés + ce qu'un unique recv rapporte."""
        messages: List[str] = []
        if self.sock is None:
            return messages
        try:
            chunk = self.sock.recv(4096)
            if chunk:
                self._recv_buf += chunk.decode("utf-8", errors="ignore")
        except (BlockingIOError, socket.timeout):
            pass
        except OSError as exc:
            self._fail(f"receive — erreur réseau : {exc}")
            return messages

        while self.delimiter in self._recv_buf and len(messages) < max_messages:
            line, _, self._recv_buf = self._recv_buf.partition(self.delimiter)
            line = line.strip()
            if line:
                messages.append(line)
        return messages

    # -- Internes ------------------------------------------------------------

    def _send_raw(self, message: str) -> None:
        assert self.sock is not None
        self.sock.sendall((message + self.delimiter).encode("utf-8"))

    def _recv_line(self, max_reads: int = 64) -> Optional[str]:
        """Lit une ligne complète (jusqu'au délimiteur) en accumulant si besoin."""
        assert self.sock is not None
        reads = 0
        while self.delimiter not in self._recv_buf:
            if reads >= max_reads:
                return None
            chunk = self.sock.recv(4096)
            reads += 1
            if not chunk:
                break
            self._recv_buf += chunk.decode("utf-8", errors="ignore")
        if self.delimiter in self._recv_buf:
            line, _, self._recv_buf = self._recv_buf.partition(self.delimiter)
            return line
        line, self._recv_buf = self._recv_buf, ""
        return line or None

    def _fail(self, reason: str) -> bool:
        self.last_error = reason
        self.state = ClientState.ERROR
        logger.error("client en erreur : %s", reason)
        return False


class DofusClientBuilder:
    """Builder fluent : ``DofusClientBuilder().auth(h, p).game(h, p).build()``."""

    def __init__(self) -> None:
        self._auth_host = "localhost"
        self._auth_port = 5555
        self._game_host = "localhost"
        self._game_port = 5555
        self._delimiter = "\n"

    def auth(self, host: str, port: int) -> "DofusClientBuilder":
        self._auth_host, self._auth_port = host, port
        return self

    def game(self, host: str, port: int) -> "DofusClientBuilder":
        self._game_host, self._game_port = host, port
        return self

    def delimiter(self, delim: str) -> "DofusClientBuilder":
        self._delimiter = delim
        return self

    def build(self) -> DofusClient:
        return DofusClient(self._auth_host, self._auth_port,
                           self._game_host, self._game_port,
                           delimiter=self._delimiter)
