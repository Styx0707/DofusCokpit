"""Tests du proxy MITM : framing, étiquetage via ASK, injection, orchestration.

Aucune socket réelle : des sockets factices capturent ce qui est « envoyé ».
La boucle de relai réseau (threads/accept) n'est pas testée ici — seule la
logique pure (découpage, identification, séquence d'injection) l'est."""
from app.network.encoder import encode_character_inventory
from app.network.exchange import (
    encode_accept, encode_move_object, encode_ready, encode_request, encode_set_kamas,
)
from app.network.proxy import DofusProxy, ProxyConnection, run_proxy_exchange, split_messages


class FakeSock:
    """Socket factice : mémorise tout ce qu'on lui envoie (sendall)."""

    def __init__(self):
        self.sent = b""

    def sendall(self, data):
        self.sent += data

    def close(self):
        pass

    def messages(self):
        """Messages envoyés, découpés sur \\x00 (sans le reste partiel)."""
        return [m.decode() for m in self.sent.split(b"\x00") if m]


def _conn(conn_id=1, char_id=None, name=None):
    c = ProxyConnection(conn_id, FakeSock(), FakeSock())
    c.character_id = char_id
    c.character_name = name
    return c


class TestFraming:
    def test_split_complete_and_remainder(self):
        complete, rem = split_messages(b"AAA\x00BBB\x00CC")
        assert complete == [b"AAA", b"BBB"]
        assert rem == b"CC"

    def test_split_no_delimiter(self):
        complete, rem = split_messages(b"partial")
        assert complete == []
        assert rem == b"partial"

    def test_roundtrip_bytes_preserved(self):
        """Re-sérialiser message + \\x00 reproduit le flux (relai transparent)."""
        stream = b"GDM|8158\x00GM|+370\x00"
        complete, rem = split_messages(stream)
        rebuilt = b"".join(m + b"\x00" for m in complete) + rem
        assert rebuilt == stream


class TestLabeling:
    def test_ask_identifies_connection(self):
        conn = _conn()
        ask = encode_character_inventory({
            "character_id": 12345, "name": "Styxh", "level": 100,
            "class_id": 4, "sex": 0, "equipment": [],
        })
        conn.observe_server_message(ask.encode())
        assert conn.character_id == 12345
        assert conn.character_name == "Styxh"

    def test_non_ask_ignored(self):
        conn = _conn()
        conn.observe_server_message(b"GDM|8158|0|x")
        assert conn.character_id is None


class TestInjection:
    def test_inject_appends_delimiter(self):
        conn = _conn()
        assert conn.inject_to_server("ER1|202") is True
        assert conn.server_sock.sent == b"ER1|202\x00"


class TestFind:
    def _proxy_with(self, *conns):
        p = DofusProxy("127.0.0.1", 5555, "up", 5555)
        for c in conns:
            p._conns[c.id] = c
        return p

    def test_find_by_id(self):
        p = self._proxy_with(_conn(1, 101, "Styxh"), _conn(2, 202, "Zhendar"))
        assert p.find(202).character_name == "Zhendar"

    def test_find_by_name_substring_ci(self):
        p = self._proxy_with(_conn(1, 101, "Styxh-[Gal]"))
        assert p.find("styxh").character_id == 101

    def test_find_missing(self):
        p = self._proxy_with(_conn(1, 101, "Styxh"))
        assert p.find("Nobody") is None


class TestRunExchange:
    def _proxy(self):
        p = DofusProxy("127.0.0.1", 5555, "up", 5555)
        g = _conn(1, 101, "Styxh")
        r = _conn(2, 202, "Zhendar")
        p._conns[1] = g
        p._conns[2] = r
        return p, g, r

    def test_full_sequence_injected(self):
        p, g, r = self._proxy()
        res = run_proxy_exchange(p, "Styxh", "Zhendar", {31582328: 10, 31582327: 5},
                                 kamas=5000, step_delay=0)
        assert res["ok"] is True

        # Donneur : demande(vers id receveur) -> 2 dépôts (par UID) -> kamas -> EK.
        assert g.server_sock.messages() == [
            encode_request(202), encode_move_object(31582328, 10),
            encode_move_object(31582327, 5), encode_set_kamas(5000), encode_ready(),
        ]
        # Receveur : accepte (EA) -> valide (EK).
        assert r.server_sock.messages() == [encode_accept(), encode_ready()]

    def test_skips_zero_qty(self):
        p, g, r = self._proxy()
        run_proxy_exchange(p, "Styxh", "Zhendar", {311: 0, 340: 2}, step_delay=0)
        assert encode_move_object(340, 2) in g.server_sock.messages()
        assert encode_move_object(311, 0) not in g.server_sock.messages()

    def test_missing_connection(self):
        p, g, r = self._proxy()
        res = run_proxy_exchange(p, "Styxh", "Ghost", {311: 1}, step_delay=0)
        assert res["ok"] is False
        assert "introuvable" in res["reason"]

    def test_unidentified_connection(self):
        p = DofusProxy("127.0.0.1", 5555, "up", 5555)
        p._conns[1] = _conn(1, None, None)   # pas encore d'ASK
        p._conns[2] = _conn(2, 202, "Zhendar")
        # find by name échoue sur la non identifiée -> introuvable
        res = run_proxy_exchange(p, "whoever", "Zhendar", {311: 1}, step_delay=0)
        assert res["ok"] is False
