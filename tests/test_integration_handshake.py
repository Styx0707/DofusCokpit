"""Test d'intégration du HANDSHAKE d'un ÉMULATEUR LOCAL (dev).

Se connecte en TCP à un émulateur Dofus 1.29 tournant EN LOCAL (host/port via
les variables d'env EMU_HOST / EMU_PORT), lit le message d'accueil (`HG`) et
rejoue les premiers paquets de négociation en vérifiant les réponses.

- SKIPPÉ si EMU_PORT n'est pas défini -> aucun échec quand l'ému n'est pas lancé
  (la suite reste verte en CI).
- Cible volontairement LOCALE : c'est un harnais de test pour TON serveur, pas
  un client de jeu. Lancer : EMU_PORT=5555 pytest -q tests/test_integration_handshake.py

⚠️ La séquence NEGOTIATION dépend de ton émulateur / ta version : renseigne-la
(ci-dessous). Le test de négociation se skippe tant qu'elle est vide, plutôt que
d'affirmer des octets non vérifiés.
"""
from __future__ import annotations

import os
import socket

import pytest

HOST = os.getenv("EMU_HOST", "127.0.0.1")
PORT = int(os.getenv("EMU_PORT", "0"))          # 0 = non configuré -> skip
DELIM = b"\x00"                                  # délimiteur de message Dofus

pytestmark = pytest.mark.skipif(
    PORT == 0, reason="EMU_PORT non défini (émulateur local absent)")


class EmuClient:
    """Client de test minimal : messages Dofus délimités par l'octet nul."""

    def __init__(self, host: str, port: int, timeout: float = 5.0) -> None:
        self.sock = socket.create_connection((host, port), timeout=timeout)
        self.sock.settimeout(timeout)
        self._buf = b""

    def recv_message(self) -> str:
        """Lit le prochain message complet (jusqu'au \\x00)."""
        while DELIM not in self._buf:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise ConnectionError("connexion fermée par le serveur")
            self._buf += chunk
        msg, _, self._buf = self._buf.partition(DELIM)
        return msg.decode("utf-8", "replace")

    def send(self, text: str) -> None:
        self.sock.sendall(text.encode("utf-8") + DELIM)

    def close(self) -> None:
        try:
            self.sock.close()
        except OSError:
            pass


# --- À ADAPTER à ton émulateur : (message envoyé, préfixe de réponse attendu) --
# Exemple typique après HG (à vérifier contre TON serveur) : version client puis
# ticket d'auth. Laisse vide pour ne tester que l'accueil HG.
NEGOTIATION: list[tuple[str, str]] = [
    # ("1.29.1", "AT"),          # ex. version -> réponse
    # ("Aticket_de_test", "Ad"), # ex. ticket  -> réponse
]


@pytest.fixture
def conn():
    client = EmuClient(HOST, PORT)
    try:
        yield client
    finally:
        client.close()


def test_welcome_is_hg(conn):
    """À la connexion, l'émulateur envoie le message d'accueil `HG`."""
    hello = conn.recv_message()
    assert hello.startswith("HG"), f"message d'accueil inattendu : {hello!r}"


def test_negotiation_sequence(conn):
    """Après HG, le serveur répond correctement aux paquets de négociation."""
    assert conn.recv_message().startswith("HG")
    if not NEGOTIATION:
        pytest.skip("NEGOTIATION vide : renseigne la séquence de ton émulateur")
    for sent, expected_prefix in NEGOTIATION:
        conn.send(sent)
        reply = conn.recv_message()
        assert reply.startswith(expected_prefix), (
            f"après envoi {sent!r} : attendu un message commençant par "
            f"{expected_prefix!r}, reçu {reply!r}")
