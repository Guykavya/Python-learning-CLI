import copy
import hashlib

import pytest

from solution import load_secret, pseudonymise, pseudonymise_rows

KEY = b"test-key-0123456789"
OTHER_KEY = b"another-key-9876543210"
VAR = "PAGEBOUND_PSEUDO_KEY"


def test_known_values():
    got = pseudonymise("asha@example.com", KEY)
    assert got == "55671d1637abb1e4", (
        f"Got {got!r}. Use hmac.new(key, value.encode('utf-8'), hashlib.sha256).hexdigest() and keep "
        "the first 16 hex characters. hashlib.sha256(key + value) is NOT the same as HMAC."
    )
    assert pseudonymise("ravi@example.com", KEY) == "38a2d145463f6be2"
    assert pseudonymise("asha@example.com", OTHER_KEY) == "c8130faab2512366"


def test_shape_is_16_lowercase_hex_characters():
    got = pseudonymise("meera@example.com", KEY)
    assert len(got) == 16 and all(c in "0123456789abcdef" for c in got), (
        f"Got {got!r}; a pseudonym is the first 16 characters of the hex digest."
    )


def test_stable_across_calls_so_joins_still_work():
    a = pseudonymise("asha@example.com", KEY)
    b = pseudonymise("asha@example.com", KEY)
    assert a == b, (
        "The same email gave two different pseudonyms. Do not add randomness or a timestamp: the "
        "point is that the same customer gets the same key in every run, so you can still count "
        "and join customers."
    )


def test_normalises_before_hashing():
    assert pseudonymise("  Asha@Example.COM ", KEY) == pseudonymise("asha@example.com", KEY), (
        "' Asha@Example.COM ' and 'asha@example.com' are the same customer. Strip and lower-case "
        "before hashing, or one customer becomes two."
    )


def test_different_keys_give_different_pseudonyms():
    assert pseudonymise("asha@example.com", KEY) != pseudonymise("asha@example.com", OTHER_KEY), (
        "The pseudonym must depend on the secret key."
    )


def test_not_a_plain_hash():
    plain = hashlib.sha256(b"asha@example.com").hexdigest()[:16]
    assert pseudonymise("asha@example.com", KEY) != plain, (
        "This is a plain sha256 of the email. Anyone can hash a list of known emails and look the "
        "result up (a dictionary attack). A keyed HMAC cannot be recomputed without the secret."
    )


def test_none_stays_none():
    assert pseudonymise(None, KEY) is None, "No email means no customer key: return None."


def test_load_secret_from_a_mapping():
    assert load_secret({VAR: "s3cret-value-long-enough"}) == b"s3cret-value-long-enough", (
        "load_secret returns the value as bytes (hmac needs bytes)."
    )


def test_load_secret_strips_spaces():
    assert load_secret({VAR: "  s3cret-value-long-enough\n"}) == b"s3cret-value-long-enough", (
        "Strip the value: a trailing newline from a .env file would silently change every pseudonym."
    )


def test_load_secret_defaults_to_os_environ(monkeypatch):
    monkeypatch.setenv(VAR, "from-the-real-environment")
    assert load_secret() == b"from-the-real-environment", (
        "With no argument, read os.environ at CALL time (not a copy made when the module was imported)."
    )


@pytest.mark.parametrize("env", [{}, {VAR: ""}, {VAR: "   "}, {"OTHER": "x" * 30}])
def test_missing_secret_is_a_clear_error(env):
    with pytest.raises(RuntimeError) as info:
        load_secret(env)
    assert VAR in str(info.value), (
        f"The error message {str(info.value)!r} must name {VAR}, so the operator knows what to set. "
        "Never fall back to a default key written in the code."
    )


def test_short_secret_is_refused_without_printing_it():
    with pytest.raises(RuntimeError) as info:
        load_secret({VAR: "abc123"})
    assert "abc123" not in str(info.value), (
        "The error message contains the secret itself. Error messages end up in logs; say what is "
        "wrong (too short), never the value."
    )
    assert VAR in str(info.value)


def test_rows_replace_the_email_column():
    rows = [
        {"id": 1, "email": "asha@example.com", "city": "Pune"},
        {"id": 2, "email": " ASHA@example.com", "city": "Pune"},
        {"id": 3, "email": None, "city": "Goa"},
    ]
    got = pseudonymise_rows(rows, KEY)
    assert [list(r) for r in got] == [["id", "customer_key", "city"]] * 3, (
        f"Keys are {[list(r) for r in got]}. Replace 'email' by 'customer_key' at the same position."
    )
    assert [r["customer_key"] for r in got] == ["55671d1637abb1e4", "55671d1637abb1e4", None], (
        f"Customer keys are {[r['customer_key'] for r in got]}."
    )
    assert "example.com" not in repr(got), "An email is still somewhere in the output rows."


def test_rows_custom_field_names_and_missing_field():
    rows = [{"order": 7, "buyer": "ravi@example.com"}, {"order": 8}]
    got = pseudonymise_rows(rows, KEY, field="buyer", out_field="buyer_key")
    assert got == [{"order": 7, "buyer_key": "38a2d145463f6be2"}, {"order": 8, "buyer_key": None}], (
        f"Got {got}. Use the field/out_field arguments; a row without the field gets None."
    )


def test_rows_input_is_not_changed():
    rows = [{"id": 1, "email": "asha@example.com"}]
    before = copy.deepcopy(rows)
    pseudonymise_rows(rows, KEY)
    assert rows == before, "pseudonymise_rows changed its input; build new dicts."
