import hashlib
import hmac
import json

import pytest

from solution import receive

SECRET = b"whsec_test_secret"
NOW = 1_700_000_000
BODY = b'{"id": "evt_1", "amount": 500}'


def sign(body, ts, secret=SECRET):
    return hmac.new(secret, f"{ts}.".encode() + body, hashlib.sha256).hexdigest()


def test_valid_request_is_ok():
    got = receive(BODY, NOW, sign(BODY, NOW), NOW, SECRET)
    assert got == "ok", f"A correctly signed, fresh request must give 'ok', got {got!r}. The signed text is f'{{ts}}.' + body."


def test_changed_body_is_a_bad_signature():
    got = receive(BODY.replace(b"500", b"900"), NOW, sign(BODY, NOW), NOW, SECRET)
    assert got == "bad signature", "A changed body must be refused with 'bad signature'."


def test_wrong_secret_is_a_bad_signature():
    assert receive(BODY, NOW, sign(BODY, NOW, b"other"), NOW, SECRET) == "bad signature"


def test_the_timestamp_is_part_of_the_signature():
    sig = sign(BODY, NOW - 10)
    assert receive(BODY, NOW, sig, NOW, SECRET) == "bad signature", (
        "The signature was made for another timestamp. Sign f'{ts}.' + body, otherwise an attacker can replay an old body with a new timestamp.")


def test_odd_spacing_is_signed_as_received():
    raw = b'{"id":"evt_2",   "amount":  500,\n "note": "caf\xc3\xa9"}'
    assert receive(raw, NOW, sign(raw, NOW), NOW, SECRET) == "ok", "Verify the raw bytes exactly as received."


def test_reserialised_json_does_not_verify():
    raw = b'{"id":"evt_2",   "amount":  500}'
    again = json.dumps(json.loads(raw)).encode()           # same data, different bytes
    assert again != raw
    assert receive(again, NOW, sign(raw, NOW), NOW, SECRET) == "bad signature", "Never parse and re-serialise before checking: spacing and key order change the bytes."


@pytest.mark.parametrize("delta,expected", [(0, "ok"), (299, "ok"), (300, "ok"), (301, "stale"), (3600, "stale")])
def test_old_timestamps_boundary(delta, expected):
    ts = NOW - delta
    assert receive(BODY, ts, sign(BODY, ts), NOW, SECRET) == expected, (
        f"A request {delta} s old must give {expected!r}: accept up to and including 300 seconds, refuse 301.")


@pytest.mark.parametrize("delta,expected", [(300, "ok"), (301, "stale")])
def test_future_timestamps_boundary(delta, expected):
    ts = NOW + delta
    assert receive(BODY, ts, sign(BODY, ts), NOW, SECRET) == expected, "A timestamp in the future is checked with abs(): +-300 seconds."


@pytest.mark.parametrize("junk", ["", "0" * 64, "zz", "abc", "é" * 64, sign(BODY, NOW).upper()[:10]])
def test_junk_signatures_are_bad_never_a_crash(junk):
    assert receive(BODY, NOW, junk, NOW, SECRET) == "bad signature"


def test_uses_constant_time_comparison(monkeypatch):
    calls = []
    real = hmac.compare_digest
    monkeypatch.setattr(hmac, "compare_digest", lambda a, b: calls.append(1) or real(a, b))
    receive(BODY, NOW, sign(BODY, NOW), NOW, SECRET)
    assert calls, "Compare the signatures with hmac.compare_digest, not ==."


def test_empty_body_works():
    assert receive(b"", NOW, sign(b"", NOW), NOW, SECRET) == "ok"
