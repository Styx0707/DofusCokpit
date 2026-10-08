"""Tests du protocole d'échange joueur->joueur (opcodes confirmés par capture).

Opcodes réels (data/c2s_hex.txt) : ER1|<id>, EA, EMG<k>, EMO+<uid>|<q>, EK.
"""
import pytest

from app.network.exchange import (
    ExchangeHandler,
    apply_messages,
    encode_accept,
    encode_move_object,
    encode_ready,
    encode_request,
    encode_set_kamas,
    parse_done,
    parse_move_ack,
    parse_ready_ack,
    plan_give,
)


class TestEncoding:
    def test_request_format(self):
        assert encode_request(1353359) == "ER1|1353359"

    def test_accept_has_no_arg(self):
        assert encode_accept() == "EA"

    def test_ready_has_no_arg(self):
        assert encode_ready() == "EK"

    def test_kamas_prefix(self):
        assert encode_set_kamas(2000) == "EMG2000"

    def test_move_object_add_and_remove(self):
        assert encode_move_object(31582328, 1) == "EMO+31582328|1"
        assert encode_move_object(31582328, -3) == "EMO-31582328|3"

    def test_move_object_rejects_zero(self):
        with pytest.raises(ValueError):
            encode_move_object(1, 0)

    def test_kamas_rejects_negative(self):
        with pytest.raises(ValueError):
            encode_set_kamas(-1)


class TestPlanGive:
    def test_order_request_objects_kamas(self):
        """plan_give : demande puis objets (ordre d'insertion) puis kamas, PAS d'EK."""
        msgs = plan_give(202, {31582328: 1, 31582327: 2}, kamas=2000)
        assert msgs == [
            encode_request(202),
            encode_move_object(31582328, 1),
            encode_move_object(31582327, 2),
            encode_set_kamas(2000),
        ]
        assert encode_ready() not in msgs   # la validation est émise séparément

    def test_skips_zero_and_negative(self):
        msgs = plan_give(1, {10: 0, 20: -3, 30: 2}, kamas=0)
        assert msgs == [encode_request(1), encode_move_object(30, 2)]


class TestParseAcks:
    def test_parse_move_ack(self):
        assert parse_move_ack("EMK0|31582328|1") == {
            "who": 0, "object_uid": 31582328, "qty": 1}

    def test_parse_move_ack_other_message(self):
        assert parse_move_ack("GDM|8158|0|x") is None

    def test_parse_ready_ack(self):
        assert parse_ready_ack("EKK1|1") == {"who": 1, "ready": True}

    def test_parse_done(self):
        assert parse_done("ERV1") is True
        assert parse_done("ERV0") is False
        assert parse_done("EMK0|1|1") is None


class TestExchangeHandler:
    def test_full_transfer(self):
        h = ExchangeHandler(giver_id=101, receiver_id=202)
        give = plan_give(202, {31582328: 1, 31582327: 2}, kamas=2000)
        results = apply_messages(h, 101, give[1:])   # [1:] = sans la demande (ER)
        assert all(r["ok"] for r in results)
        assert h.parts[101]["objects"] == {31582328: 1, 31582327: 2}
        assert h.parts[101]["kamas"] == 2000

        assert h.apply_ready(202, True)["done"] is False
        done = h.apply_ready(101, True)
        assert done["done"] is True
        assert done["transfer"]["giver"]["objects"] == {31582328: 1, 31582327: 2}
        assert done["transfer"]["receiver"]["objects"] == {}

    def test_ek_via_apply_messages(self):
        """Un 'EK' rejoué valide bien la part du joueur."""
        h = ExchangeHandler(101, 202)
        apply_messages(h, 202, [encode_ready()])
        assert h.parts[202]["ready"] is True

    def test_deposit_resets_ready(self):
        h = ExchangeHandler(101, 202)
        h.apply_ready(202, True)
        h.apply_move(101, 31582328, 5)
        assert h.parts[202]["ready"] is False

    def test_remove_object_bounded(self):
        h = ExchangeHandler(101, 202)
        h.apply_move(101, 31582328, 3)
        res = h.apply_move(101, 31582328, -10)
        assert res["qty"] == 0
        assert 31582328 not in h.parts[101]["objects"]

    def test_leave_cancels(self):
        h = ExchangeHandler(101, 202)
        h.apply_move(101, 31582328, 5)
        assert h.apply_leave(101)["done"] is False
        assert h.apply_move(101, 31582327, 1)["ok"] is False

    def test_move_rejects_outsider(self):
        h = ExchangeHandler(101, 202)
        assert h.apply_move(999, 31582328, 1)["ok"] is False
