"""Capture réseau Dofus Retro via Scapy.

Responsabilité UNIQUE : sniffer le trafic, réassembler les messages Dofus
(fragmentés sur plusieurs segments TCP), détecter le message de contenu de
banque (`EL`), et livrer un dict {item_id: quantity} à un callback.

Le DÉCODAGE du protocole est délégué à ``app.network.protocol`` (pur, sans
Scapy) : capture et parsing restent découplés et testables séparément.

⚠️ Le trafic de jeu Dofus Retro officiel est en CLAIR mais sur le **port 443**
(mêlé au HTTPS). Le filtre BPF par défaut cible donc 443 ; on ne retient que les
messages dont l'en-tête est `EL` (les payloads TLS binaires sont ignorés).
"""
from __future__ import annotations

import logging
from scapy.all import Packet, Raw, sniff
from scapy.layers.inet import TCP
from typing import Callable, Dict, Optional, Tuple

from app.config import Settings, get_settings
from app.network.protocol import BANK_MESSAGE_PREFIX, parse_bank_storage

logger = logging.getLogger(__name__)

# Callback invoqué quand une banque complète a été décodée.
BankCallback = Callable[[Dict[int, int]], None]
# Fonction de parsing : corps du message (str) -> {item_id: quantity}.
BankParser = Callable[[str], Dict[int, int]]

# Séparateur de fin de message Dofus (octet nul).
MESSAGE_DELIMITER = b"\x00"


class DofusBankSniffer:
    def __init__(
            self,
            on_bank: BankCallback,
            settings: Optional[Settings] = None,
            parser: Optional[BankParser] = None,
    ) -> None:
        self.on_bank = on_bank
        self.settings = settings or get_settings()
        self.parser: BankParser = parser or parse_bank_storage
        # Buffer de réassemblage par flux TCP (clé = 4-tuple).
        self._buffers: Dict[Tuple, bytes] = {}

    # -- Boucle de capture ----------------------------------------------------
    def start(self, count: int = 0) -> None:
        """Démarre la capture (bloquant). count=0 -> infini."""
        logger.info(
            "Démarrage capture (iface=%s, filtre='%s', debug_dump=%s)",
            self.settings.capture_interface or "auto",
            self.settings.capture_bpf_filter,
            self.settings.capture_debug_dump or "off",
        )
        try:
            sniff(
                iface=self.settings.capture_interface,
                filter=self.settings.capture_bpf_filter,
                prn=self._handle_packet,
                store=False,
                count=count,
            )
        except PermissionError:
            logger.error(
                "Privilèges insuffisants pour la capture "
                "(NET_RAW/NET_ADMIN requis sur le conteneur)."
            )
            raise
        except OSError as exc:
            # Interface introuvable, libpcap absent, etc.
            logger.error("Erreur d'interface/capture réseau : %s", exc)
            raise
        except KeyboardInterrupt:
            logger.info("Capture interrompue par l'utilisateur.")

    # -- Traitement paquet ----------------------------------------------------
    def _handle_packet(self, pkt: Packet) -> None:
        # Un paquet corrompu ne doit JAMAIS tuer la boucle de sniff.
        try:
            if not pkt.haslayer(TCP) or not pkt.haslayer(Raw):
                return
            tcp = pkt[TCP]
            key = (pkt.src, tcp.sport, pkt.dst, tcp.dport)

            buffer = self._buffers.get(key, b"") + bytes(pkt[Raw].load)
            # Réassemblage : on isole les messages complets, on garde le reste.
            *complete, remainder = buffer.split(MESSAGE_DELIMITER)
            self._buffers[key] = remainder

            for raw_message in complete:
                self._dispatch(raw_message)
        except Exception:
            logger.exception("Paquet ignoré (erreur de traitement).")

    def _dispatch(self, raw_message: bytes) -> None:
        message = raw_message.decode("utf-8", errors="ignore").strip()
        if not message.startswith(BANK_MESSAGE_PREFIX):
            return
        body = message[len(BANK_MESSAGE_PREFIX):]

        # Mode diagnostic : archive le payload brut pour caler le parser.
        if self.settings.capture_debug_dump:
            self._dump_raw(raw_message, body)

        inventory = self.parser(body)
        if not inventory:
            return
        logger.info("Banque décodée : %d objets distincts.", len(inventory))
        try:
            self.on_bank(inventory)
        except Exception:
            # Une erreur côté persistance ne doit pas arrêter la capture.
            logger.exception("Callback on_bank en échec (banque non persistée).")

    def _dump_raw(self, raw_message: bytes, body: str) -> None:
        """Écrit le message brut (repr + hex) dans le fichier de debug."""
        try:
            with open(self.settings.capture_debug_dump, "a", encoding="utf-8") as fh:
                fh.write("---- EL ----\n")
                fh.write(f"repr : {body!r}\n")
                fh.write(f"hex  : {raw_message.hex()}\n\n")
        except OSError as exc:
            logger.warning("Impossible d'écrire le dump debug : %s", exc)
