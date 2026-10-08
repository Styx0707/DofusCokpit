"""Orchestrateur haut-niveau au-dessus de ``DofusClient``.

Combine le client TCP (machine d'état) et les encodeurs (``encoder``,
``exchange``) pour offrir une API fluide : connexion complète, déplacement,
et surtout ÉCHANGE joueur->joueur (l'objet de cet outil).

Comme ``DofusClient``, vise un ÉMULATEUR / serveur privé (session indépendante).
"""
from __future__ import annotations

import logging
import time
from typing import Dict, List, Optional, Tuple

from app.network.client import (
    ClientState,
    DofusClient,
    DofusClientBuilder,
    LoginCredentials,
)
from app.network.encoder import encode_movement_path
from app.network.exchange import encode_accept, encode_ready, plan_give

logger = logging.getLogger("dofus.bot")


class DofusBot:
    """API confort : login/char/move/poll + échange d'objets entre persos."""

    def __init__(self, client: DofusClient) -> None:
        self.client = client
        self.current_cell = 0

    @classmethod
    def builder(cls) -> "DofusBotBuilder":
        return DofusBotBuilder()

    # -- Connexion -----------------------------------------------------------

    def login(self, creds: LoginCredentials) -> bool:
        """Chaîne auth complète : connect_auth -> login -> connect_game."""
        if not self.client.connect_auth():
            return False
        if not self.client.login(creds):
            return False
        return self.client.connect_game()

    def select_character(self, character_id: int, name: str) -> bool:
        return self.client.select_character(character_id, name)

    def disconnect(self) -> None:
        self.client.disconnect()

    # -- Gameplay ------------------------------------------------------------

    def move_to(self, waypoints: List[Tuple[int, int]]) -> bool:
        """Encode les points d'inflexion et émet le GA001. Exige d'être en jeu."""
        if self.client.state != ClientState.GAME_ACTIVE:
            logger.warning("move_to refusé : pas en jeu (%s)", self.client.state.value)
            return False
        path = encode_movement_path(waypoints)
        return self.client.send_movement(path)

    def poll(self, max_messages: int = 10) -> List[str]:
        return self.client.receive_messages(max_messages=max_messages)

    def poll_blocking(self, timeout: float = 5.0, max_messages: int = 100) -> List[str]:
        """Collecte les messages jusqu'à ``timeout`` secondes (ou ``max_messages``)."""
        out: List[str] = []
        deadline = time.monotonic() + timeout
        while time.monotonic() < deadline and len(out) < max_messages:
            msgs = self.client.receive_messages(max_messages=max_messages - len(out))
            if msgs:
                out.extend(msgs)
            else:
                time.sleep(0.02)
        return out

    def is_connected(self) -> bool:
        return self.client.state in (
            ClientState.AUTH_CONNECTED, ClientState.LOGGED_IN,
            ClientState.GAME_CONNECTED, ClientState.GAME_ACTIVE,
        )

    def last_error(self) -> Optional[str]:
        return self.client.last_error

    # -- Échange (le cœur de l'outil) ----------------------------------------

    def exchange_give(self, target_id: int, objects: Dict[int, int],
                      kamas: int = 0, lock: bool = True,
                      step_delay: float = 0.15) -> bool:
        """Transfère ``objects`` ({object_uid: quantité}) et ``kamas`` vers le
        perso ``target_id`` (CÔTÉ DONNEUR : ouvre l'échange, dépose, valide si
        ``lock`` via ``EK``). Le receveur doit accepter + valider de son côté
        (cf. ``exchange_accept``) ; ``tools/quick_exchange.py`` orchestre les deux.

        ``objects`` est indexé par UID D'INSTANCE (cf. exchange.py), pas par id
        d'item. Émet la séquence message par message, espacée de ``step_delay`` s."""
        if self.client.state != ClientState.GAME_ACTIVE:
            logger.warning("exchange_give refusé : pas en jeu (%s)", self.client.state.value)
            return False
        for message in plan_give(target_id, objects, kamas=kamas):
            if not self.client.send(message):
                return False
            if step_delay:
                time.sleep(step_delay)
        if lock and not self.client.send(encode_ready()):   # EK = validation
            return False
        logger.info("échange : %d objet(s) + %d kama(s) déposé(s) vers #%s",
                    len(objects), kamas, target_id)
        return True

    def exchange_accept(self, lock: bool = True, step_delay: float = 0.15) -> bool:
        """CÔTÉ RECEVEUR : accepte la demande d'échange entrante (``EA``, sans
        argument) et valide (``EK``) si ``lock`` — rien à déposer côté receveur."""
        if self.client.state != ClientState.GAME_ACTIVE:
            logger.warning("exchange_accept refusé : pas en jeu (%s)", self.client.state.value)
            return False
        if not self.client.send(encode_accept()):
            return False
        if lock:
            time.sleep(step_delay)
            return self.client.send(encode_ready())
        return True


class DofusBotBuilder:
    """Builder fluent du bot (délègue au builder du client)."""

    def __init__(self) -> None:
        self._cb = DofusClientBuilder()

    def auth(self, host: str, port: int) -> "DofusBotBuilder":
        self._cb.auth(host, port)
        return self

    def game(self, host: str, port: int) -> "DofusBotBuilder":
        self._cb.game(host, port)
        return self

    def delimiter(self, delim: str) -> "DofusBotBuilder":
        self._cb.delimiter(delim)
        return self

    def build(self) -> DofusBot:
        return DofusBot(self._cb.build())
