"""Proxy MITM Dofus Retro — relaie le trafic du VRAI client et y INJECTE des
messages (ici : la séquence d'échange), sans ouvrir de 2ᵉ session.

Pourquoi un proxy et pas un client headless : sur un serveur Retro OFFICIEL, un
compte déjà connecté par le client officiel est déconnecté si on ouvre une 2ᵉ
session. Pour émettre des paquets tout en gardant le client en ligne, il faut
donc ÉCRIRE dans sa connexion existante. Le trafic Retro étant EN CLAIR sur le
port 443 (cf. ``sniffer.py``/``config.py`` — pas de TLS), un simple relai TCP
suffit : on se place entre le client et le serveur et on insère nos messages.

Montage (une seule fois) :
  1. Trouver l'IP du serveur de jeu (une capture le donne : IP distante port 443).
  2. Rediriger le client vers le proxy : entrée ``hosts`` du host de jeu -> 127.0.0.1,
     et lancer le proxy avec ``upstream`` = l'IP RÉELLE trouvée en 1.
  3. Lancer le proxy sur le port 443 (admin requis pour binder < 1024).
  Le serveur d'auth (login) reste en direct : seul le serveur de JEU est proxifié.

Sens du flux :
  - client -> serveur : relayé message par message (aligné sur ``\\x00``) pour que
    l'INJECTION tombe toujours sur une frontière de message (jamais au milieu
    d'un paquet du client) ; chaque message est aussi loggé (découverte d'opcodes).
  - serveur -> client : relayé brut (faible latence) ; on en OBSERVE une copie pour
    ÉTIQUETER la connexion (le message ``ASK`` donne id + nom du perso).

⚠️ Manipuler les paquets est contraire aux CGU d'Ankama (risque de bannissement).
À n'utiliser que sur tes propres comptes, en connaissance de cause.
"""
from __future__ import annotations

import logging
import socket
import threading
import time
from typing import Dict, List, Optional, Tuple

from app.network.protocol import parse_character_inventory

logger = logging.getLogger("dofus.proxy")

DELIMITER = b"\x00"


def split_messages(buffer: bytes) -> Tuple[List[bytes], bytes]:
    """Découpe un buffer en (messages complets, reste). Réciproque exacte du
    réassemblage du sniffer : on isole ce qui précède chaque ``\\x00`` et on
    garde la fin partielle. Re-sérialiser ``msg + \\x00`` reproduit les octets
    d'origine (délimiteurs simples), ce qui rend le relai transparent."""
    *complete, remainder = buffer.split(DELIMITER)
    return complete, remainder


class ProxyConnection:
    """Une connexion client<->serveur proxifiée. Porte l'étiquette du perso
    (remplie en observant ``ASK``) et sait injecter un message vers le serveur."""

    def __init__(self, conn_id: int, client_sock: socket.socket,
                 server_sock: socket.socket) -> None:
        self.id = conn_id
        self.client_sock = client_sock
        self.server_sock = server_sock
        self.character_id: Optional[int] = None
        self.character_name: Optional[str] = None
        self._send_lock = threading.Lock()   # sérialise les écritures vers le serveur
        self.alive = True

    def inject_to_server(self, message: str) -> bool:
        """Insère un message client->serveur (``message`` SANS délimiteur) dans la
        connexion existante, comme si le client l'avait émis. Thread-safe : pris
        sous le même verrou que le relai, donc jamais au milieu d'un paquet."""
        data = message.encode("utf-8") + DELIMITER
        try:
            with self._send_lock:
                self.server_sock.sendall(data)
            logger.info("conn#%s inject -> %r", self.id, message[:48])
            return True
        except OSError as exc:
            logger.warning("conn#%s injection échouée : %s", self.id, exc)
            return False

    def label(self) -> str:
        return self.character_name or f"conn#{self.id}"

    def observe_server_message(self, message: bytes) -> None:
        """Étiquette la connexion à partir d'un message serveur->client. ``ASK``
        (entrée en jeu) porte id + nom du perso -> on sait à qui parle ce flux."""
        if not message.startswith(b"ASK"):
            return
        parsed = parse_character_inventory(message.decode("utf-8", "ignore"))
        if parsed:
            self.character_id = parsed["character_id"]
            self.character_name = parsed["name"]
            logger.info("conn#%s identifiée : %s (#%s)",
                        self.id, self.character_name, self.character_id)


class DofusProxy:
    """Relai TCP multi-connexions avec injection. Un proxy = un port d'écoute
    (le serveur de jeu proxifié) ; chaque client Dofus qui s'y connecte devient
    une ``ProxyConnection`` étiquetée, utilisable pour l'injection d'échange."""

    def __init__(self, listen_host: str, listen_port: int,
                 upstream_host: str, upstream_port: int) -> None:
        self.listen_host = listen_host
        self.listen_port = listen_port
        self.upstream_host = upstream_host
        self.upstream_port = upstream_port

        self._conns: Dict[int, ProxyConnection] = {}
        self._lock = threading.Lock()
        self._seq = 0
        self._listener: Optional[socket.socket] = None
        self._stop = threading.Event()

    # -- Cycle de vie --------------------------------------------------------

    def start(self) -> None:
        """Démarre l'écoute dans un thread daemon (non bloquant)."""
        self._listener = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._listener.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._listener.bind((self.listen_host, self.listen_port))
        self._listener.listen(16)
        threading.Thread(target=self._accept_loop, name="proxy-accept",
                         daemon=True).start()
        logger.info("proxy à l'écoute %s:%s -> %s:%s", self.listen_host,
                    self.listen_port, self.upstream_host, self.upstream_port)

    def stop(self) -> None:
        self._stop.set()
        if self._listener is not None:
            try:
                self._listener.close()
            except OSError:
                pass

    def _accept_loop(self) -> None:
        while not self._stop.is_set():
            try:
                client_sock, addr = self._listener.accept()
            except OSError:
                break   # listener fermé
            try:
                server_sock = socket.create_connection(
                    (self.upstream_host, self.upstream_port), timeout=10)
            except OSError as exc:
                logger.error("upstream injoignable (%s) — connexion client fermée", exc)
                client_sock.close()
                continue
            conn = self._register(client_sock, server_sock)
            logger.info("conn#%s ouverte depuis %s", conn.id, addr)
            threading.Thread(target=self._pump_client_to_server, args=(conn,),
                             name=f"proxy-c2s-{conn.id}", daemon=True).start()
            threading.Thread(target=self._pump_server_to_client, args=(conn,),
                             name=f"proxy-s2c-{conn.id}", daemon=True).start()

    def _register(self, client_sock: socket.socket,
                  server_sock: socket.socket) -> ProxyConnection:
        with self._lock:
            self._seq += 1
            conn = ProxyConnection(self._seq, client_sock, server_sock)
            self._conns[conn.id] = conn
            return conn

    def _drop(self, conn: ProxyConnection) -> None:
        conn.alive = False
        for sock in (conn.client_sock, conn.server_sock):
            try:
                sock.close()
            except OSError:
                pass
        with self._lock:
            self._conns.pop(conn.id, None)
        logger.info("conn#%s fermée (%s)", conn.id, conn.label())

    # -- Relais --------------------------------------------------------------

    def _pump_client_to_server(self, conn: ProxyConnection) -> None:
        """Client -> serveur, aligné sur les messages (injection boundary-safe)."""
        buf = b""
        try:
            while not self._stop.is_set():
                chunk = conn.client_sock.recv(4096)
                if not chunk:
                    break
                buf += chunk
                complete, buf = split_messages(buf)
                for msg in complete:
                    with conn._send_lock:
                        conn.server_sock.sendall(msg + DELIMITER)
                    if msg:
                        logger.debug("conn#%s c->s %r", conn.id, msg[:48])
        except OSError:
            pass
        finally:
            self._drop(conn)

    def _pump_server_to_client(self, conn: ProxyConnection) -> None:
        """Serveur -> client, relai brut + observation (étiquetage via ASK)."""
        buf = b""
        try:
            while not self._stop.is_set():
                chunk = conn.server_sock.recv(4096)
                if not chunk:
                    break
                conn.client_sock.sendall(chunk)   # passthrough brut, faible latence
                buf += chunk
                complete, buf = split_messages(buf)
                for msg in complete:
                    if msg:
                        conn.observe_server_message(msg)
        except OSError:
            pass
        finally:
            self._drop(conn)

    # -- Registre / API ------------------------------------------------------

    def connections(self) -> List[ProxyConnection]:
        with self._lock:
            return list(self._conns.values())

    def find(self, name_or_id) -> Optional[ProxyConnection]:
        """Retrouve une connexion par id de perso (int) ou sous-chaîne de nom
        (comme le walker cible une fenêtre par sous-chaîne de titre)."""
        with self._lock:
            conns = list(self._conns.values())
        if isinstance(name_or_id, int):
            for c in conns:
                if c.character_id == name_or_id:
                    return c
            return None
        needle = str(name_or_id).strip().lower()
        for c in conns:
            if c.character_name and needle in c.character_name.lower():
                return c
        return None


def run_proxy_exchange(proxy: DofusProxy, giver: str, receiver: str,
                       objects: Dict[int, int], kamas: int = 0,
                       step_delay: float = 0.2) -> dict:
    """Injecte la séquence d'échange complète entre deux connexions proxifiées.

    ``giver``/``receiver`` : nom de perso (sous-chaîne) ou id. ``objects`` =
    {object_uid: quantité} (UID d'instance, pas id d'item). Les deux persos
    doivent être en jeu, sur la même map et à portée. Déroulé : le donneur
    demande + dépose, le receveur accepte + valide, le donneur valide -> le
    serveur valide et pousse l'état aux deux vrais clients.

    ⚠️ Ne fonctionne que contre un serveur SANS signature par message : l'officiel
    rejette les messages injectés (cf. en-tête de exchange.py)."""
    from app.network.exchange import (
        encode_accept, encode_ready, encode_request, encode_move_object,
        encode_set_kamas,
    )

    g = proxy.find(giver)
    r = proxy.find(receiver)
    if g is None or r is None:
        return {"ok": False, "reason": f"connexion introuvable "
                f"(donneur={giver!r}:{g is not None}, receveur={receiver!r}:{r is not None})",
                "connections": [c.label() for c in proxy.connections()]}
    if r.character_id is None or g.character_id is None:
        return {"ok": False, "reason": "persos pas encore identifiés (attendre l'ASK "
                "d'entrée en jeu des deux côtés)"}

    def _pace(conn: ProxyConnection, message: str) -> None:
        conn.inject_to_server(message)
        time.sleep(step_delay)

    # 1) donneur : ouvre + dépose objets (par UID d'instance) + kamas (pas de
    #    validation tant que le receveur n'a pas accepté).
    _pace(g, encode_request(r.character_id))
    for object_uid, qty in objects.items():
        if qty and qty > 0:
            _pace(g, encode_move_object(object_uid, qty))
    if kamas > 0:
        _pace(g, encode_set_kamas(kamas))

    # 2) receveur : accepte (EA, rien à déposer) puis valide (EK).
    _pace(r, encode_accept())
    _pace(r, encode_ready())

    # 3) donneur : valide (EK) -> les deux prêts -> validation serveur.
    g.inject_to_server(encode_ready())

    return {"ok": True, "giver": g.label(), "receiver": r.label(),
            "objects": objects, "kamas": kamas}
