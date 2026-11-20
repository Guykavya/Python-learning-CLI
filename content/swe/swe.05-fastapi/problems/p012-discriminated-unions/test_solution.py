import pytest
from fastapi.testclient import TestClient

from solution import app

CARD = {"method": "card", "amount_paise": 49900, "number": "4111111111111111", "expiry": "08/29"}
BANK = {"method": "bank", "amount_paise": 150000, "account": "001234567890", "ifsc": "HDFC0001234"}
UPI = {"method": "upi", "amount_paise": 2500, "vpa": "asha.k@okbank"}


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def errors(response):
    assert response.status_code == 422, f"Expected a 422, got {response.status_code}: {response.text}"
    return [(e["loc"], e["type"]) for e in response.json()["detail"]]


@pytest.mark.parametrize("body, summary", [
    (CARD, "card ending 1111"),
    (BANK, "bank HDFC0001234"),
    (UPI, "upi asha.k@okbank"),
])
def test_each_method_is_accepted(client, body, summary):
    r = client.post("/payments", json=body)
    assert r.status_code == 201, f"A valid {body['method']} payment must give 201; got {r.status_code}: {r.text}"
    assert r.json() == {"method": body["method"], "amount_paise": body["amount_paise"], "summary": summary}, f"Got {r.json()}"


def test_bad_card_is_checked_only_as_a_card(client):
    found = errors(client.post("/payments", json={**CARD, "number": "4111"}))
    assert found == [(["body", "card", "number"], "string_pattern_mismatch")], (
        "With Field(discriminator='method') only the Card model is tried, so there is ONE error at "
        f"['body', 'card', 'number']. A plain union would also report Bank and Upi failures. Got {found}")


def test_bad_expiry(client):
    found = errors(client.post("/payments", json={**CARD, "expiry": "13/29"}))
    assert found == [(["body", "card", "expiry"], "string_pattern_mismatch")], f"Month 13 does not exist; got {found}"


def test_bank_missing_ifsc(client):
    body = {k: v for k, v in BANK.items() if k != "ifsc"}
    found = errors(client.post("/payments", json=body))
    assert found == [(["body", "bank", "ifsc"], "missing")], f"Only the Bank model is checked; got {found}"


def test_bad_vpa(client):
    found = errors(client.post("/payments", json={**UPI, "vpa": "no-at-sign"}))
    assert found == [(["body", "upi", "vpa"], "string_pattern_mismatch")], f"Got {found}"


def test_amount_from_the_base_class(client):
    found = errors(client.post("/payments", json={**UPI, "amount_paise": 0}))
    assert found == [(["body", "upi", "amount_paise"], "greater_than")], (
        f"amount_paise comes from PaymentBase (gt=0) and is checked in every model; got {found}")


def test_unknown_method_gives_one_clear_error(client):
    found = errors(client.post("/payments", json={"method": "cash", "amount_paise": 100}))
    assert found == [(["body"], "union_tag_invalid")], (
        f"An unknown method must give exactly ONE error of type union_tag_invalid at ['body'], not one per model; got {found}")


def test_missing_method(client):
    found = errors(client.post("/payments", json={"amount_paise": 100, "number": "4111111111111111"}))
    assert found == [(["body"], "union_tag_not_found")], f"Without 'method' there is nothing to dispatch on; got {found}"
