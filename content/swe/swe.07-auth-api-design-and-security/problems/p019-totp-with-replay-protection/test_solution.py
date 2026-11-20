import hmac

import pytest

from solution import hotp, totp, verify_totp

KEY = b"12345678901234567890"       # the secret of the RFC test vectors

HOTP_VECTORS = ["755224", "287082", "359152", "969429", "338314", "254676", "287922", "162583", "399871", "520489"]
TOTP_VECTORS = [(59, "94287082"), (1111111109, "07081804"), (1111111111, "14050471"),
                (1234567890, "89005924"), (2000000000, "69279037"), (20000000000, "65353130")]


@pytest.mark.parametrize("counter", range(10))
def test_hotp_rfc_4226_appendix_d(counter):
    got = hotp(KEY, counter)
    assert got == HOTP_VECTORS[counter], (
        f"hotp(counter={counter}) gave {got!r}, RFC 4226 says {HOTP_VECTORS[counter]!r}. "
        "Steps: HMAC-SHA1 of the 8-byte big-endian counter; offset = last byte & 0x0F; "
        "4 bytes from the offset, top bit cleared (& 0x7FFFFFFF); modulo 10**digits; pad with zeros.")


@pytest.mark.parametrize("at,expected", TOTP_VECTORS)
def test_totp_rfc_6238_sha1_vectors(at, expected):
    got = totp(KEY, at, digits=8)
    assert got == expected, f"totp at T={at} gave {got!r}, RFC 6238 says {expected!r}. The counter is int(at) // step."


def test_codes_keep_their_leading_zeros():
    assert totp(KEY, 1111111109, digits=8) == "07081804", "Pad with zeros to the full number of digits (zfill)."
    assert all(len(hotp(KEY, i)) == 6 for i in range(200)), "A 6-digit code is always 6 characters long."


def test_a_code_is_constant_inside_one_30_second_slot():
    assert totp(KEY, 3000) == totp(KEY, 3029.9) != totp(KEY, 3030), "The slot is int(at) // 30: seconds 3000..3029 share one code."


def test_step_parameter():
    assert totp(KEY, 100, step=60) == hotp(KEY, 1)


NOW = 1_700_000_010          # slot 56666667, inside the slot
SLOT = NOW // 30


def test_current_code_is_accepted_and_returns_the_slot():
    got = verify_totp(KEY, totp(KEY, NOW), NOW)
    assert got == SLOT, f"On success return the slot number (int(now) // 30 = {SLOT}) so the caller can remember it; got {got!r}."


def test_one_slot_of_drift_each_way_is_accepted():
    assert verify_totp(KEY, hotp(KEY, SLOT - 1), NOW) == SLOT - 1, "The previous slot is accepted (the phone clock runs slow)."
    assert verify_totp(KEY, hotp(KEY, SLOT + 1), NOW) == SLOT + 1, "The next slot is accepted (the phone clock runs fast)."


def test_two_slots_away_is_refused():
    assert verify_totp(KEY, hotp(KEY, SLOT - 2), NOW) is None, "Only +-1 slot is allowed; wider windows make guessing easier."
    assert verify_totp(KEY, hotp(KEY, SLOT + 2), NOW) is None


def test_replay_of_the_same_code_is_refused():
    code = totp(KEY, NOW)
    used = verify_totp(KEY, code, NOW)
    assert verify_totp(KEY, code, NOW + 5, last_step=used) is None, (
        "The same code was accepted twice. Refuse any slot <= last_step: the code is still arithmetically right, only memory stops the replay.")


def test_an_older_code_after_a_newer_one_is_refused():
    used = verify_totp(KEY, totp(KEY, NOW), NOW)
    assert verify_totp(KEY, hotp(KEY, SLOT - 1), NOW, last_step=used) is None, "After slot S was used, slots <= S are dead."


def test_a_later_slot_is_accepted_after_an_earlier_use():
    used = verify_totp(KEY, totp(KEY, NOW), NOW)
    later = NOW + 30
    assert verify_totp(KEY, totp(KEY, later), later, last_step=used) == SLOT + 1, "The next slot's code must work after the previous one was used."


def test_wrong_codes_give_none():
    right = totp(KEY, NOW)
    wrong = "000000" if right != "000000" else "000001"
    assert verify_totp(KEY, wrong, NOW) is None


@pytest.mark.parametrize("junk", ["", "12345", "1234567", "abcdef", "12 456", " 123456", "12345é", "١٢٣٤٥٦", "-12345", None, 123456])
def test_malformed_codes_give_none_and_never_raise(junk):
    assert verify_totp(KEY, junk, NOW) is None


def test_a_code_with_a_leading_zero_works():
    # find a moment whose code starts with 0
    t = next(t for t in range(NOW, NOW + 30 * 400, 30) if hotp(KEY, t // 30).startswith("0"))
    assert verify_totp(KEY, hotp(KEY, t // 30), t) == t // 30, "A code such as '047291' is text, not the number 47291: keep it a string."


def test_constant_time_compare_is_used(monkeypatch):
    calls = []
    real = hmac.compare_digest
    monkeypatch.setattr(hmac, "compare_digest", lambda a, b: calls.append(1) or real(a, b))
    verify_totp(KEY, totp(KEY, NOW), NOW)
    assert calls, "Compare codes with hmac.compare_digest, not ==."
