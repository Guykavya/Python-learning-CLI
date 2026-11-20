import hmac
import re

import pytest

from solution import ApiKeys


def parts(key):
    pk, prefix, secret = key.split("_", 2)
    return pk, prefix, secret


def test_key_has_the_shape_pk_prefix_secret():
    key = ApiKeys().create("acme")
    pk, prefix, secret = parts(key)
    assert pk == "pk", f"A key starts with 'pk_', got {key[:6]!r}."
    assert re.fullmatch(r"[0-9a-f]{8}", prefix), f"The prefix is 8 hex characters (secrets.token_hex(4)); got {prefix!r}. It must contain no underscore, or the key cannot be split."
    assert len(secret) >= 40, "The secret part comes from secrets.token_urlsafe(32): 43 characters."


def test_a_created_key_checks_out_to_its_owner():
    keys = ApiKeys()
    key = keys.create("acme")
    assert keys.check(key) == "acme", "check(key) must return the owner of a valid key."


def test_two_owners_two_keys():
    keys = ApiKeys()
    a, b = keys.create("acme"), keys.create("globex")
    assert a != b
    assert keys.check(a) == "acme" and keys.check(b) == "globex"


def test_one_owner_can_have_several_keys_at_once():
    keys = ApiKeys()
    old, new = keys.create("acme"), keys.create("acme")
    assert keys.check(old) == "acme" and keys.check(new) == "acme", "Rotation needs two active keys for one owner at the same time."


def test_the_secret_is_never_stored():
    keys = ApiKeys()
    key = keys.create("acme")
    _, prefix, secret = parts(key)
    dump = repr(vars(keys))
    assert secret not in dump, "The secret is stored in plain text. Keep only its SHA-256 hash: a leaked table must not contain working keys."
    assert key not in dump
    assert prefix in dump, "The prefix is not secret; it is the lookup key of the row."


def test_wrong_secret_wrong_prefix_and_junk_give_none():
    keys = ApiKeys()
    key = keys.create("acme")
    pk, prefix, secret = parts(key)
    bad = [
        key[:-1] + ("A" if key[-1] != "A" else "B"),      # one character changed
        f"pk_{prefix}_",                                   # empty secret
        f"pk_00000000_{secret}",                           # unknown prefix
        f"xx_{prefix}_{secret}",                           # wrong marker
        secret,                                            # no structure at all
        "",
        "pk_",
        "pk__",
        f"pk_{prefix}_{secret}_extra",                     # extra text after the secret
        f"pk_{prefix}_{secret[:-1]}",                      # truncated
        f"pk_{prefix}_ééé",                 # non-ASCII text must not crash
    ]
    for presented in bad:
        assert keys.check(presented) is None, f"{presented[:30]!r} was accepted; only the exact key is valid."


def test_revoke_kills_one_key_only():
    keys = ApiKeys()
    old, new = keys.create("acme"), keys.create("acme")
    keys.revoke(parts(old)[1])
    assert keys.check(old) is None, "A revoked key must stop working at once."
    assert keys.check(new) == "acme", "Revoking one key must not touch the owner's other keys."


def test_revoking_an_unknown_prefix_is_harmless():
    keys = ApiKeys()
    key = keys.create("acme")
    keys.revoke("ffffffff")
    assert keys.check(key) == "acme"


def test_comparison_is_constant_time(monkeypatch):
    calls = []
    real = hmac.compare_digest
    monkeypatch.setattr(hmac, "compare_digest", lambda a, b: calls.append(1) or real(a, b))
    keys = ApiKeys()
    key = keys.create("acme")
    keys.check(key)
    assert calls, "Compare the stored hash with the presented hash using hmac.compare_digest (module style: hmac.compare_digest), not ==."


def test_secret_part_may_contain_underscores_and_dashes():
    keys = ApiKeys()
    seen = 0
    for _ in range(300):
        key = keys.create("acme")
        secret = parts(key)[2]
        if "_" in secret or "-" in secret:
            seen += 1
        assert keys.check(key) == "acme", f"A valid key was refused: {key!r}. The secret can contain '_' (token_urlsafe), so split into at most 3 parts: key.split('_', 2)."
    assert seen > 0
