from datetime import datetime

import pytest
from fastapi.testclient import TestClient

from solution import Line, Order, app, to_api

ITEMS = [{"name": "pen", "price_paise": 1050, "qty": 2}, {"name": "book", "price_paise": 29900, "qty": 1}]
BODY = {"items": ITEMS, "created_at": "2026-03-01T09:30:00"}


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def test_total_is_computed():
    order = Order.model_validate(BODY)
    assert order.total_paise == 32000, f"total_paise = 1050*2 + 29900*1 = 32000, got {order.total_paise!r}"
    assert Order(items=[], created_at=datetime(2026, 1, 1)).total_paise == 0, "An empty order totals 0."


def test_computed_field_is_in_the_plain_dump():
    dumped = Order.model_validate(BODY).model_dump()
    assert dumped.get("total_paise") == 32000, (
        "A plain @property is NOT dumped; decorate it with @computed_field (above @property). "
        f"model_dump() gave keys {sorted(dumped)}")
    assert "created_at" in dumped, "Without by_alias=True, model_dump uses the Python name created_at."


def test_to_api_uses_output_names_and_drops_none():
    out = to_api(Order.model_validate(BODY))
    assert out == {"items": ITEMS, "createdAt": "2026-03-01T09:30:00", "total_paise": 32000}, (
        "to_api must use mode='json' (date as a string), by_alias=True (createdAt) and exclude_none=True "
        f"(no coupon key); got {out}")


def test_to_api_keeps_a_coupon_that_was_given():
    out = to_api(Order.model_validate({**BODY, "coupon": "SAVE10"}))
    assert out.get("coupon") == "SAVE10", f"exclude_none removes only None values; got {out}"


def test_preview_response(client):
    r = client.post("/orders/preview", json=BODY)
    assert r.status_code == 200, r.text
    body = r.json()
    assert "createdAt" in body and "created_at" not in body, (
        f"FastAPI writes the response by alias: expected createdAt, got keys {sorted(body)}")
    assert body.get("total_paise") == 32000, f"The computed field must be in the response; got keys {sorted(body)}"
    assert "coupon" not in body, "coupon was not sent (None): response_model_exclude_none=True leaves it out."


def test_preview_with_coupon(client):
    body = client.post("/orders/preview", json={**BODY, "coupon": "SAVE10"}).json()
    assert body.get("coupon") == "SAVE10", f"A real coupon is kept; got {body}"


def test_input_uses_the_python_name(client):
    r = client.post("/orders/preview", json={"items": [], "createdAt": "2026-03-01T09:30:00"})
    assert r.status_code == 422, (
        "serialization_alias changes only the OUTPUT name; input still needs created_at. "
        f"Got {r.status_code}: {r.text}")
    found = [(e["loc"], e["type"]) for e in r.json()["detail"]]
    assert (["body", "created_at"], "missing") in found, f"Got {found}"


def test_line_rules_still_apply(client):
    r = client.post("/orders/preview", json={"items": [{"name": "pen", "price_paise": 100, "qty": 0}], "created_at": "2026-03-01T09:30:00"})
    found = [(e["loc"], e["type"]) for e in r.json()["detail"]]
    assert (["body", "items", 0, "qty"], "greater_than_equal") in found, f"qty must be at least 1; got {found}"


def test_line_model_unchanged():
    assert Line(name="x", price_paise=0, qty=1).price_paise == 0, "A free line (price 0) is allowed: ge=0."
