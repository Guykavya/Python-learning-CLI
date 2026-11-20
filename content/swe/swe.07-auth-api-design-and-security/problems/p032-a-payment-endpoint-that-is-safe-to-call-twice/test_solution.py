import sys
import threading

import pytest
from fastapi.testclient import TestClient

import solution
from solution import PaymentService, ProviderError, build_app

ASHA = {"Authorization": "Bearer t-asha"}
RAVI = {"Authorization": "Bearer t-ravi"}


class FakeProvider:
    """Counts charges. `gate` makes charge() wait (a slow provider); `fail_times` makes the first calls fail."""

    def __init__(self, gate=None, fail_times=0):
        self.gate = gate
        self.fail_times = fail_times
        self.started = threading.Event()
        self.charges = []
        self._lock = threading.Lock()

    def charge(self, user, amount_cents):
        self.started.set()
        if self.gate is not None and not self.gate.wait(3):
            raise RuntimeError("test bug: the gate was never opened")
        with self._lock:
            if self.fail_times > 0:
                self.fail_times -= 1
                raise ProviderError("provider is down")
            self.charges.append((user, amount_cents))
            return f"ch_{len(self.charges)}"


def run_in_thread(fn, *args, **kwargs):
    box = {}

    def target():
        try:
            box["result"] = fn(*args, **kwargs)
        except BaseException as exc:                      # noqa: BLE001
            box["error"] = exc

    t = threading.Thread(target=target, daemon=True)
    t.start()
    return t, box


def post(client, key, amount=2500, headers=ASHA):
    h = dict(headers)
    if key is not None:
        h["Idempotency-Key"] = key
    return client.post("/payments", json={"amount_cents": amount}, headers=h)


@pytest.fixture
def setup():
    provider = FakeProvider()
    with TestClient(build_app(provider)) as client:
        yield provider, client


# ---------- the service on its own ----------

def test_first_call_charges_once_and_returns_201():
    provider = FakeProvider()
    svc = PaymentService(provider)
    status, body, replayed = svc.create("asha", "k1", {"amount_cents": 2500})
    assert (status, replayed) == (201, False), f"First call: (201, ..., False); got {(status, replayed)}"
    assert body == {"charge_id": "ch_1", "amount_cents": 2500}, f"Body must be the charge id and the amount; got {body}"
    assert provider.charges == [("asha", 2500)], f"The provider must be charged once with (user, amount); got {provider.charges}"


def test_repeat_returns_the_stored_response_and_does_not_charge():
    provider = FakeProvider()
    svc = PaymentService(provider)
    first = svc.create("asha", "k1", {"amount_cents": 2500})
    again = svc.create("asha", "k1", {"amount_cents": 2500})
    assert again == (first[0], first[1], True), f"The repeat must return the same status and body with replayed=True; got {again}"
    assert len(provider.charges) == 1, f"A repeat must not charge again; charges: {provider.charges}"


@pytest.mark.parametrize("calls", [2, 3, 10])
def test_n_calls_one_charge(calls):
    provider = FakeProvider()
    svc = PaymentService(provider)
    results = [svc.create("asha", "k1", {"amount_cents": 700}) for _ in range(calls)]
    assert len(provider.charges) == 1, f"{calls} calls with one key must charge exactly once; got {len(provider.charges)}"
    assert {(c, tuple(b.items())) for c, b, _ in results} == {(201, tuple(results[0][1].items()))}, "All answers must be identical"
    assert [r[2] for r in results] == [False] + [True] * (calls - 1), "Only the first call is not a replay"


def test_same_key_other_body_is_422():
    provider = FakeProvider()
    svc = PaymentService(provider)
    svc.create("asha", "k1", {"amount_cents": 2500})
    status, body, replayed = svc.create("asha", "k1", {"amount_cents": 9900})
    assert status == 422 and replayed is False, f"Same key with a different amount: 422, not a replay; got {status}"
    assert "detail" in body, "Error bodies are {'detail': ...}"
    assert len(provider.charges) == 1, "The mismatching request must not charge"


def test_a_new_key_is_a_new_payment():
    provider = FakeProvider()
    svc = PaymentService(provider)
    a = svc.create("asha", "k1", {"amount_cents": 2500})
    b = svc.create("asha", "k2", {"amount_cents": 2500})
    assert b[0] == 201 and b[2] is False and b[1]["charge_id"] != a[1]["charge_id"], "A different key is a different payment"
    assert len(provider.charges) == 2


def test_keys_are_scoped_per_user():
    provider = FakeProvider()
    svc = PaymentService(provider)
    a = svc.create("asha", "shared-key", {"amount_cents": 2500})
    r = svc.create("ravi", "shared-key", {"amount_cents": 4000})
    assert r[0] == 201 and r[2] is False, (
        f"Ravi's use of the same key text is his own payment, not a replay or a 422; got {r}. Key the records on (user, key).")
    assert r[1]["amount_cents"] == 4000 and r[1]["charge_id"] != a[1]["charge_id"], "Ravi must not receive Asha's stored response"
    assert provider.charges == [("asha", 2500), ("ravi", 4000)]


def test_replay_returns_a_copy():
    svc = PaymentService(FakeProvider())
    svc.create("asha", "k1", {"amount_cents": 2500})
    _, body, _ = svc.create("asha", "k1", {"amount_cents": 2500})
    body["amount_cents"] = -1
    assert svc.create("asha", "k1", {"amount_cents": 2500})[1]["amount_cents"] == 2500, (
        "Changing a returned body must not change the stored response: return a copy")


def test_provider_failure_is_502_and_the_key_is_released():
    provider = FakeProvider(fail_times=1)
    svc = PaymentService(provider)
    first = svc.create("asha", "k1", {"amount_cents": 2500})
    assert first[0] == 502 and first[2] is False, f"A ProviderError gives 502; got {first[0]}"
    assert provider.charges == []
    retry = svc.create("asha", "k1", {"amount_cents": 2500})
    assert retry[0] == 201 and retry[2] is False, (
        f"A failure must not be stored: the retry with the same key must run and succeed; got {retry}. Delete the record after a failure.")
    assert len(provider.charges) == 1


def test_other_exceptions_release_the_key_and_propagate():
    class Boom(FakeProvider):
        def charge(self, user, amount_cents):
            raise KeyError("bug in the provider adapter")

    svc = PaymentService(Boom())
    with pytest.raises(KeyError):
        svc.create("asha", "k1", {"amount_cents": 2500})
    svc.provider = FakeProvider()
    status = svc.create("asha", "k1", {"amount_cents": 2500})[0]
    assert status == 201, f"After an unexpected error the key must be free again (got {status}, probably 409 'in progress' forever)"


def test_a_request_in_progress_gets_409_without_waiting_or_charging():
    gate = threading.Event()
    provider = FakeProvider(gate=gate)
    svc = PaymentService(provider)
    first, box1 = run_in_thread(svc.create, "asha", "k1", {"amount_cents": 2500})
    try:
        assert provider.started.wait(2), "The first call never reached the provider"
        second, box2 = run_in_thread(svc.create, "asha", "k1", {"amount_cents": 2500})
        second.join(1.5)
        assert not second.is_alive(), (
            "The second call with the same key is still waiting: you hold the lock while calling the provider. "
            "Release the lock before provider.charge and answer 409 at once.")
        status, body, replayed = box2["result"]
        assert (status, replayed) == (409, False), f"While the first call is running the second gets 409; got {status}"
        assert "detail" in body
        assert provider.charges == [], "Nothing may be charged by the second call"
    finally:
        gate.set()
    first.join(3)
    assert box1["result"][0] == 201, f"The first call must finish with 201; got {box1}"
    again = svc.create("asha", "k1", {"amount_cents": 2500})
    assert again[0] == 201 and again[2] is True, "After the first call finished, a repeat is a replay"
    assert len(provider.charges) == 1, f"One payment in total; got {provider.charges}"


def test_different_body_while_in_progress_is_422_not_409():
    gate = threading.Event()
    provider = FakeProvider(gate=gate)
    svc = PaymentService(provider)
    first, box1 = run_in_thread(svc.create, "asha", "k1", {"amount_cents": 2500})
    try:
        assert provider.started.wait(2)
        t, box = run_in_thread(svc.create, "asha", "k1", {"amount_cents": 1})
        t.join(1.5)
        assert not t.is_alive(), "Do not hold the lock while calling the provider"
        assert box["result"][0] == 422, f"A different body with a used key is 422 even while the first call runs; got {box['result'][0]}"
    finally:
        gate.set()
    first.join(3)


@pytest.fixture
def fast_switching():
    old = sys.getswitchinterval()
    sys.setswitchinterval(1e-6)                      # make the threads interleave as often as possible
    yield
    sys.setswitchinterval(old)


def test_many_threads_one_key_one_charge(fast_switching):
    for round_number in range(40):
        provider = FakeProvider()
        svc = PaymentService(provider)
        gate = threading.Barrier(10, timeout=5)
        results = []

        def attempt():
            gate.wait()
            results.append(svc.create("asha", f"key-{round_number}", {"amount_cents": 1000}))

        threads = [threading.Thread(target=attempt, daemon=True) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join(5)
        assert len(results) == 10, "Some thread never finished"
        assert len(provider.charges) == 1, (
            f"10 simultaneous requests with one key charged {len(provider.charges)} times. "
            "Look up and claim the key in ONE step under the lock.")
        assert {r[0] for r in results} <= {201, 409}, f"Only 201 (first or replay) and 409 are allowed; got {sorted({r[0] for r in results})}"
        assert [r[0] for r in results].count(201) >= 1


# ---------- the HTTP layer ----------

def test_http_first_call_and_replay(setup):
    provider, client = setup
    r1 = post(client, "key-0001")
    assert r1.status_code == 201 and r1.json() == {"charge_id": "ch_1", "amount_cents": 2500}, f"First call: 201 and the charge; got {r1.status_code} {r1.text}"
    assert "idempotent-replayed" not in r1.headers, "The first answer is not a replay"
    r2 = post(client, "key-0001")
    assert r2.status_code == 201 and r2.json() == r1.json(), "The repeat returns the same status and body"
    assert r2.headers.get("idempotent-replayed") == "true", "A replay carries the header Idempotent-Replayed: true"
    assert len(provider.charges) == 1


@pytest.mark.parametrize("calls", [2, 3, 10])
def test_http_n_calls_one_charge(setup, calls):
    provider, client = setup
    answers = [post(client, "key-0001", 1800).json() for _ in range(calls)]
    assert len(provider.charges) == 1, f"{calls} identical requests must charge once; got {len(provider.charges)}"
    assert all(a == answers[0] for a in answers), "Every answer must be identical"


def test_http_mismatch_new_key_and_users(setup):
    provider, client = setup
    post(client, "key-0001", 2500)
    assert post(client, "key-0001", 9900).status_code == 422, "Same key, other amount: 422"
    assert len(provider.charges) == 1
    assert post(client, "key-0002", 2500).status_code == 201 and len(provider.charges) == 2, "A new key is a new payment"
    r = post(client, "key-0001", 4000, RAVI)
    assert r.status_code == 201 and r.json()["amount_cents"] == 4000, "Ravi's key-0001 is his own payment"
    assert provider.charges[-1] == ("ravi", 4000)


def test_http_input_checks(setup):
    provider, client = setup
    assert post(client, None).status_code == 400, "Missing Idempotency-Key: 400"
    assert client.post("/payments", json={"amount_cents": 2500}, headers={"Idempotency-Key": "k"}).status_code == 401, "No token: 401"
    assert client.post("/payments", json={"amount_cents": 2500}, headers={"Authorization": "Bearer nope", "Idempotency-Key": "k"}).status_code == 401, "Unknown token: 401"
    for bad in (-5, 0, 1_000_001):
        assert post(client, "k-bad", bad).status_code == 422, f"amount {bad} is invalid: 422"
    assert client.post("/payments", json={"amount_cents": 5, "extra": 1}, headers=ASHA | {"Idempotency-Key": "k-extra"}).status_code == 422, "Extra fields are refused"
    assert provider.charges == [], "None of the refused requests may charge"


def test_http_409_has_retry_after():
    gate = threading.Event()
    provider = FakeProvider(gate=gate)
    app = build_app(provider)
    assert isinstance(app.state.service, PaymentService), "build_app must put the PaymentService in app.state.service"
    first, _ = run_in_thread(app.state.service.create, "asha", "key-0009", {"amount_cents": 2500})
    try:
        assert provider.started.wait(2)
        client = TestClient(app)                      # no `with`: leaving it must not wait for a blocked request
        second, box = run_in_thread(post, client, "key-0009")
        second.join(2)
        assert not second.is_alive(), "The HTTP call waited for the first one: do not hold the lock during the provider call"
        r = box["result"]
        assert r.status_code == 409, f"A call while the first is running must be 409; got {r.status_code}"
        assert r.headers.get("retry-after") == "1", "A 409 carries Retry-After: 1"
    finally:
        gate.set()
    first.join(3)
    assert len(provider.charges) == 1


def test_http_502_on_provider_failure_then_retry_works():
    provider = FakeProvider(fail_times=1)
    with TestClient(build_app(provider)) as client:
        assert post(client, "key-0003").status_code == 502, "A ProviderError gives 502"
        r = post(client, "key-0003")
        assert r.status_code == 201 and "idempotent-replayed" not in r.headers, "The retry after a failure is a normal first run"
        assert len(provider.charges) == 1
