"""The audit findings as tests: each one is red on the insecure app and must be green on yours."""
import hashlib
import inspect
import logging
import time

import jwt
import pytest
from fastapi.testclient import TestClient

from solution import build_hardened_app

PASSWORD = "correct horse battery"

pytestmark = pytest.mark.filterwarnings("ignore:The HMAC key")      # the forged-token test uses a short key on purpose


class Clock:
    def __init__(self):
        self.t = time.time()

    def __call__(self):
        return self.t


@pytest.fixture
def world():
    clock = Clock()
    app = build_hardened_app(clock=clock, scrypt_n=2**10)           # a cheap scrypt cost keeps the tests fast
    with TestClient(app, raise_server_exceptions=False) as client:
        class World:
            pass
        w = World()
        w.clock, w.app, w.client, w.db = clock, app, client, app.state.db

        def signup(name, password=PASSWORD):
            r = client.post("/register", json={"name": name, "password": password})
            assert r.status_code in (200, 201), f"/register must still work (2xx with {{'id': ...}}); got {r.status_code} {r.text}"
            uid = r.json()["id"]
            r = client.post("/login", json={"name": name, "password": password})
            assert r.status_code == 200 and "access_token" in r.json(), f"/login with the right password must give a token; got {r.status_code} {r.text}"
            return uid, {"Authorization": f"Bearer {r.json()['access_token']}"}

        w.signup = signup
        w.login = lambda name, password: client.post("/login", json={"name": name, "password": password})
        yield w


def balance(w, uid):
    return w.db.execute("SELECT balance_cents FROM accounts WHERE user_id = ?", (uid,)).fetchone()[0]


# ------------------------------------------------ Finding 1: login (enumeration and throttling)

def test_f1_unknown_user_and_wrong_password_look_the_same(world):
    world.signup("asha")
    unknown = world.login("nobody", "whatever-password")
    wrong = world.login("asha", "whatever-password")
    assert unknown.status_code == wrong.status_code == 401, (
        f"Both failures must be 401; got {unknown.status_code} (unknown name) and {wrong.status_code} (wrong password). "
        "A 404 'no such user' tells an attacker which names exist.")
    assert unknown.json() == wrong.json(), f"The bodies must be identical: {unknown.json()} vs {wrong.json()}"


def test_f1_throttle_after_five_failures(world):
    world.signup("asha")
    for i in range(5):
        r = world.login("asha", f"wrong-guess-{i}")
        assert r.status_code == 401, f"Failure {i + 1} of 5 is still an ordinary 401; got {r.status_code}"
    r = world.login("asha", "wrong-guess-6")
    assert r.status_code == 429, f"The 6th attempt within the minute must be 429 Too Many Requests; got {r.status_code}"
    wait = r.headers.get("retry-after", "")
    assert wait.isdigit() and 1 <= int(wait) <= 60, f"A 429 needs Retry-After with whole seconds (1 to 60); got {wait!r}"


def test_f1_throttled_name_is_refused_even_with_the_right_password_until_the_window_ends(world):
    world.signup("asha")
    for i in range(5):
        world.login("asha", f"wrong-guess-{i}")
    assert world.login("asha", PASSWORD).status_code == 429, "While throttled, even the right password gets 429 (no free guesses)"
    world.clock.t += 61
    r = world.login("asha", PASSWORD)
    assert r.status_code == 200, (
        f"61 seconds later the failures are outside the 60-second window and the right password must work; got {r.status_code}. "
        "Count failures with the injected clock, and throttle (do not lock for ever).")


def test_f1_unknown_names_are_throttled_too(world):
    for i in range(5):
        assert world.login("ghost", f"guess-{i}").status_code == 401
    assert world.login("ghost", "guess-6").status_code == 429, (
        "Throttle by the name that was typed, whether or not it exists; otherwise a 429 would reveal that the name is real")


def test_f1_one_name_throttled_does_not_block_another_user(world):
    world.signup("asha")
    world.signup("ravi")
    for i in range(6):
        world.login("asha", f"wrong-{i}")
    assert world.login("ravi", PASSWORD).status_code == 200, "Ravi must not be blocked by attempts against asha"


def test_f1_successful_logins_do_not_count(world):
    world.signup("asha")
    for _ in range(7):
        assert world.login("asha", PASSWORD).status_code == 200, "Only FAILED attempts count towards the limit"


# ------------------------------------------------ Finding 2: password storage

def test_f2_passwords_are_stored_with_a_salted_hash(world):
    world.signup("asha")
    world.signup("ravi")
    stored = [r[0] for r in world.db.execute("SELECT password_hash FROM users ORDER BY id")]
    assert len(stored) == 2 and all(isinstance(s, str) and s for s in stored), "users.password_hash must hold a non-empty text"
    assert all(PASSWORD not in s for s in stored), "The password itself must never be stored"
    plain = {hashlib.sha256(PASSWORD.encode()).hexdigest(), hashlib.md5(PASSWORD.encode()).hexdigest(), hashlib.sha1(PASSWORD.encode()).hexdigest()}
    assert not (set(stored) & plain), "A plain unsalted SHA-256/MD5/SHA-1 can be looked up in a table of known hashes: use scrypt with a random salt"
    assert stored[0] != stored[1], (
        "Two users with the SAME password must get DIFFERENT stored values: add a random salt per password")


def test_f2_wrong_passwords_still_fail_and_right_ones_work_after_hashing(world):
    world.signup("asha")
    assert world.login("asha", PASSWORD + "x").status_code == 401, "A wrong password must be refused"
    assert world.login("asha", PASSWORD.upper()).status_code == 401, "Case matters"
    assert world.login("asha", PASSWORD).status_code == 200, "The right password must still log in"


def test_f2_the_default_scrypt_cost_is_strong():
    default = inspect.signature(build_hardened_app).parameters["scrypt_n"].default
    assert default >= 2**14, f"The default scrypt_n must be at least 2**14 (16384); got {default!r}. Tests lower it, production must not."


# ------------------------------------------------ Finding 3: tokens

def test_f3_tokens_have_a_short_expiry(world):
    uid, headers = world.signup("asha")
    token = headers["Authorization"].removeprefix("Bearer ")
    claims = jwt.decode(token, options={"verify_signature": False})
    assert "exp" in claims, f"The token needs an exp claim; claims: {claims}"
    lifetime = claims["exp"] - world.clock()
    assert 0 < lifetime <= 3600, f"The token must live at most one hour (exp - now was {lifetime:.0f} s)"
    assert claims.get("sub") == str(uid), f"sub must be the user id as text ({str(uid)!r}); got {claims.get('sub')!r}"


def test_f3_expired_tokens_are_refused_using_the_injected_clock(world):
    uid, headers = world.signup("asha")
    claims = jwt.decode(headers["Authorization"].removeprefix("Bearer "), options={"verify_signature": False})
    exp = claims["exp"]
    world.clock.t = exp - 1
    assert world.client.post("/orders", json={"total_cents": 100}, headers=headers).status_code == 201, "One second before exp the token is valid"
    world.clock.t = exp
    r = world.client.post("/orders", json={"total_cents": 100}, headers=headers)
    assert r.status_code == 401, (
        f"At now >= exp the token is expired: expected 401, got {r.status_code}. PyJWT checks exp against the REAL clock, "
        "so switch that off (options={'verify_exp': False}) and compare exp with clock() yourself.")


def test_f3_a_token_signed_with_the_old_secret_is_refused(world):
    uid, headers = world.signup("asha")
    forged = jwt.encode({"sub": str(uid), "exp": int(world.clock()) + 600}, "secret", algorithm="HS256")
    r = world.client.post("/orders", json={"total_cents": 100}, headers={"Authorization": f"Bearer {forged}"})
    assert r.status_code == 401, (
        f"A token signed with the guessable key 'secret' was accepted ({r.status_code}): anyone can forge tokens for any user. "
        "Use a long random secret (secrets.token_urlsafe(48)).")


def test_f3_alg_none_and_garbage_tokens_are_refused(world):
    uid, _ = world.signup("asha")
    unsigned = jwt.encode({"sub": str(uid), "exp": int(world.clock()) + 600}, None, algorithm="none")
    for bad in (unsigned, "garbage", ""):
        r = world.client.post("/orders", json={"total_cents": 100}, headers={"Authorization": f"Bearer {bad}"})
        assert r.status_code == 401, f"The token {bad[:20]!r} must give 401, got {r.status_code}"


# ------------------------------------------------ Finding 4: object-level authorisation (the two-actor test)

def test_f4_a_user_cannot_read_another_users_order(world):
    asha_id, asha = world.signup("asha")
    ravi_id, ravi = world.signup("ravi")
    order_id = world.client.post("/orders", json={"total_cents": 4200}, headers=asha).json()["id"]
    own = world.client.get(f"/orders/{order_id}", headers=asha)
    assert own.status_code == 200 and own.json()["total_cents"] == 4200, (
        f"The owner must still read her own order (a server that refuses everything is not secure, it is broken); got {own.status_code} {own.text}")
    other = world.client.get(f"/orders/{order_id}", headers=ravi)
    assert other.status_code == 404, (
        f"Ravi asked for Asha's order and got {other.status_code} {other.text}. Scope the query: WHERE id = ? AND owner_id = ?, "
        "and answer 404 (not 403), so the id does not even prove the order exists.")
    missing = world.client.get("/orders/9999", headers=ravi)
    assert missing.status_code == other.status_code and missing.json() == other.json(), (
        "A foreign order and a missing order must look identical to Ravi")


def test_f4_every_user_sees_only_his_own_orders(world):
    _, asha = world.signup("asha")
    _, ravi = world.signup("ravi")
    ids = {}
    for name, headers in (("asha", asha), ("ravi", ravi)):
        ids[name] = world.client.post("/orders", json={"total_cents": 100 if name == "asha" else 200}, headers=headers).json()["id"]
    assert world.client.get(f"/orders/{ids['ravi']}", headers=ravi).json()["total_cents"] == 200
    assert world.client.get(f"/orders/{ids['ravi']}", headers=asha).status_code == 404, "Asha must not read Ravi's order either"


def test_f4_anonymous_users_get_401(world):
    _, asha = world.signup("asha")
    order_id = world.client.post("/orders", json={"total_cents": 100}, headers=asha).json()["id"]
    assert world.client.get(f"/orders/{order_id}").status_code == 401, "No token: 401"


# ------------------------------------------------ Finding 5: payments

def test_f5_repeating_a_payment_with_the_same_key_charges_once(world):
    uid, headers = world.signup("asha")
    start = balance(world, uid)
    answers = [world.client.post("/payments", json={"amount_cents": 2500}, headers=headers | {"Idempotency-Key": "pay-0001"}) for _ in range(3)]
    assert [a.status_code for a in answers] == [201, 201, 201], f"A replay answers like the first call (201); got {[a.status_code for a in answers]}"
    assert len({a.json()["payment_id"] for a in answers}) == 1, "All three answers must carry the SAME payment_id"
    assert balance(world, uid) == start - 2500, f"Three calls with one key must debit once: balance {start} -> {balance(world, uid)}"
    assert world.db.execute("SELECT COUNT(*) FROM payments WHERE user_id = ?", (uid,)).fetchone()[0] == 1, "One row in payments"


def test_f5_a_new_key_is_a_new_payment_and_a_reused_key_with_another_body_is_422(world):
    uid, headers = world.signup("asha")
    start = balance(world, uid)
    assert world.client.post("/payments", json={"amount_cents": 1000}, headers=headers | {"Idempotency-Key": "k-a"}).status_code == 201
    assert world.client.post("/payments", json={"amount_cents": 1000}, headers=headers | {"Idempotency-Key": "k-b"}).status_code == 201
    assert balance(world, uid) == start - 2000, "A different key is a different payment"
    r = world.client.post("/payments", json={"amount_cents": 7777}, headers=headers | {"Idempotency-Key": "k-a"})
    assert r.status_code == 422, f"Same key, other amount: 422; got {r.status_code}"
    assert balance(world, uid) == start - 2000, "The conflicting request must not charge"


def test_f5_keys_belong_to_one_user(world):
    asha_id, asha = world.signup("asha")
    ravi_id, ravi = world.signup("ravi")
    a = world.client.post("/payments", json={"amount_cents": 1000}, headers=asha | {"Idempotency-Key": "shared"})
    r = world.client.post("/payments", json={"amount_cents": 3000}, headers=ravi | {"Idempotency-Key": "shared"})
    assert r.status_code == 201 and r.json()["payment_id"] != a.json()["payment_id"], (
        f"Ravi's key text 'shared' is his own payment, not Asha's replay; got {r.status_code} {r.text}")
    assert balance(world, ravi_id) == 100000 - 3000 and balance(world, asha_id) == 100000 - 1000


def test_f5_the_key_header_is_required_and_funds_are_still_checked(world):
    uid, headers = world.signup("asha")
    r = world.client.post("/payments", json={"amount_cents": 100}, headers=headers)
    assert r.status_code == 400, f"A payment without Idempotency-Key is refused with 400; got {r.status_code}"
    assert balance(world, uid) == 100000, "The refused request must not charge"
    assert world.client.post("/payments", json={"amount_cents": 90000}, headers=headers | {"Idempotency-Key": "big-1"}).status_code == 201
    r = world.client.post("/payments", json={"amount_cents": 90000}, headers=headers | {"Idempotency-Key": "big-2"})
    assert r.status_code == 402, f"Not enough money left: 402; got {r.status_code}"
    assert balance(world, uid) == 10000, "The balance must never go below zero or change on a 402"


# ------------------------------------------------ Finding 6: redirects

@pytest.mark.parametrize("target", ["/", "/orders", "/orders?page=2", "https://shop.example/bye", "http://shop.example/bye?x=1"])
def test_f6_allowed_redirect_targets_are_followed(world, target):
    r = world.client.get("/logout", params={"next": target}, follow_redirects=False)
    assert 300 <= r.status_code < 400, f"/logout must redirect; got {r.status_code}"
    assert r.headers["location"] == target, f"next={target!r} is local or on an allowed host and must be followed; got {r.headers['location']!r}"


@pytest.mark.parametrize("target", [
    "https://evil.example/", "//evil.example", "/\\evil.example", "https://shop.example.evil.example/", "https://shop.example@evil.example/",
    "https://evil.example/shop.example", "javascript:alert(1)", "ftp://shop.example/x", "evil.example", "///evil.example", "https:evil.example",
])
def test_f6_foreign_redirect_targets_go_home(world, target):
    r = world.client.get("/logout", params={"next": target}, follow_redirects=False)
    assert 300 <= r.status_code < 400, f"/logout must still redirect; got {r.status_code}"
    assert r.headers["location"] == "/", f"next={target!r} must not be followed (open redirect); expected '/', got {r.headers['location']!r}"


def test_f6_no_next_goes_home(world):
    assert world.client.get("/logout", follow_redirects=False).headers["location"] == "/"


# ------------------------------------------------ Finding 7: logs

def test_f7_no_secrets_in_the_logs(world, caplog):
    caplog.set_level(logging.DEBUG)
    secret_pw = "Tr0ub4dor&3-never-log-me"
    world.signup("asha", PASSWORD)
    world.login("asha", secret_pw)                                       # a failed login with a distinctive password
    ok = world.login("asha", PASSWORD)
    token = ok.json()["access_token"]
    world.client.post("/payments", json={"amount_cents": 100}, headers={"Authorization": f"Bearer {token}", "Idempotency-Key": "log-1"})
    text = "\n".join(record.getMessage() for record in caplog.records)
    assert secret_pw not in text, "The attempted password appears in a log line: never log passwords, not even wrong ones"
    assert PASSWORD not in text, "The real password appears in a log line"
    assert token not in text, "The access token appears in a log line: a token in a log is a stolen session waiting to happen"
    assert "asha" in text, "Log the failed login (with the user name, without the password); it is the evidence a security team needs"


# ------------------------------------------------ Finding 8: errors

def check_error_shape(r, expected_status=None):
    assert r.status_code >= 400, f"expected an error status, got {r.status_code} {r.text}"
    if expected_status is not None:
        assert r.status_code == expected_status, f"expected {expected_status}, got {r.status_code} {r.text}"
    body = r.json()
    assert isinstance(body, dict) and isinstance(body.get("error"), str) and body["error"], (
        f"Every error answers {{'error': '<message>'}}; got {r.status_code} {r.text}")
    assert "trace" not in body, f"A stack trace in the body ({list(body)}): log it, do not send it"
    assert "Traceback" not in r.text and 'File "' not in r.text, "No traceback text in an error body"


def test_f8_every_client_error_has_the_same_shape(world):
    _, asha = world.signup("asha")
    check_error_shape(world.client.get("/orders/1"), 401)
    check_error_shape(world.client.get("/orders/9999", headers=asha), 404)
    check_error_shape(world.client.get("/no-such-route"), 404)
    check_error_shape(world.client.post("/orders", json={}, headers=asha))
    check_error_shape(world.client.post("/orders", json={"total_cents": "abc"}, headers=asha))
    check_error_shape(world.client.post("/login", json=["not", "an", "object"]))
    r = world.login("nobody", "x" * 12)
    check_error_shape(r, 401)


def test_f8_bad_input_is_a_client_error_not_a_server_error(world):
    _, asha = world.signup("asha")
    for payload in ({}, {"total_cents": "abc"}, {"total_cents": -5}, {"total_cents": None}):
        r = world.client.post("/orders", json=payload, headers=asha)
        assert 400 <= r.status_code < 500, f"POST /orders {payload} is the client's mistake: 4xx (422), got {r.status_code}. Validate input with a Pydantic model."
    r = world.client.post("/register", json={"name": "x"})
    assert 400 <= r.status_code < 500, f"A register body without a password is a 4xx; got {r.status_code}"


def test_f8_unexpected_failures_return_a_generic_500(world):
    _, asha = world.signup("asha")
    world.db.close()                                                     # simulate a broken database
    r = world.client.get("/orders/1", headers=asha)
    check_error_shape(r, 500)
    assert "closed database" not in r.text.lower() and "sqlite" not in r.text.lower(), (
        f"The 500 body must not leak internal details (database, file paths, exception text); got {r.text}")
