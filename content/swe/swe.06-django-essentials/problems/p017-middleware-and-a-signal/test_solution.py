import re

import pytest
from django.test import Client

from solution import Item, LowStockAlert


# ---------- Part 1: the middleware ----------

def test_every_response_has_a_generated_id():
    r = Client().get("/whoami/")
    rid = r.get("X-Request-ID")
    assert rid, "The response must carry an X-Request-ID header: set it on the response returned by get_response."
    assert re.fullmatch(r"[0-9a-f]{32}", rid), f"A generated id is uuid.uuid4().hex (32 hex characters), got {rid!r}."
    assert r.json() == {"request_id": rid}, "request.request_id must be set before the view runs and equal the header."


def test_ids_differ_between_requests():
    c = Client()
    a, b = c.get("/whoami/")["X-Request-ID"], c.get("/whoami/")["X-Request-ID"]
    assert a != b, "Each request needs its own id: create it inside __call__, not in __init__ (which runs once)."


def test_a_valid_incoming_id_is_kept():
    r = Client().get("/whoami/", headers={"X-Request-ID": "trace-me_123"})
    assert r["X-Request-ID"] == "trace-me_123", "A valid incoming X-Request-ID must be reused."
    assert r.json()["request_id"] == "trace-me_123", "request.request_id must hold the incoming id."


@pytest.mark.parametrize("bad", ["has space", "a" * 65, "new\tline", "semi;colon", "<script>"])
def test_an_invalid_incoming_id_is_replaced(bad):
    r = Client().get("/whoami/", headers={"X-Request-ID": bad})
    rid = r["X-Request-ID"]
    assert rid != bad and re.fullmatch(r"[0-9a-f]{32}", rid), (
        f"{bad!r} is not 1-64 letters, digits, - or _: it must be replaced by a new uuid hex, got {rid!r}.")


def test_a_64_character_id_is_still_valid():
    ok = "a" * 64
    assert Client().get("/whoami/", headers={"X-Request-ID": ok})["X-Request-ID"] == ok, "Length 64 is allowed."


def test_the_header_is_also_on_a_404():
    r = Client().get("/no-such-page/")
    assert r.status_code == 404
    assert r.get("X-Request-ID"), "The header belongs on every response, also a 404: the middleware wraps the whole chain."


# ---------- Part 2: the signal ----------

def alerts(item):
    return list(LowStockAlert.objects.filter(item=item).order_by("id").values_list("quantity", flat=True))


def test_alert_only_once_per_crossing():
    item = Item.objects.create(name="pen", quantity=10)          # threshold 5
    seen = []
    for q in [7, 4, 3, 4, 0, 5, 4, 9]:
        item.quantity = q
        item.save()
        seen.append(LowStockAlert.objects.count())
    assert seen == [0, 1, 1, 1, 1, 1, 2, 2], (
        f"Alert counts after saves 7,4,3,4,0,5,4,9 must be [0, 1, 1, 1, 1, 1, 2, 2], got {seen}. "
        "One alert when the stock goes from >= threshold to < threshold; none while it stays below; "
        "5 is not below 5, so returning to 5 resets the crossing.")
    assert alerts(item) == [4, 4], f"Each alert stores the quantity that caused it, expected [4, 4], got {alerts(item)}."


def test_no_alert_while_the_stock_is_high():
    item = Item.objects.create(name="pen", quantity=10)
    for q in [9, 8, 5, 6]:
        item.quantity = q
        item.save()
    assert LowStockAlert.objects.count() == 0, "5 and above is not low: no alert."


def test_creating_an_item_below_its_threshold_gives_one_alert():
    item = Item.objects.create(name="rare", quantity=2)
    assert alerts(item) == [2], f"A new item born below the threshold gets one alert, got {alerts(item)}."
    item.name = "rarer"
    item.save()
    assert alerts(item) == [2], "Saving another field while still low must not repeat the alert."


def test_creating_an_item_at_the_threshold_gives_no_alert():
    Item.objects.create(name="ok", quantity=5)
    assert LowStockAlert.objects.count() == 0, "quantity == threshold is not below the threshold."


def test_the_threshold_of_each_item_is_used():
    a = Item.objects.create(name="a", quantity=20, threshold=20)
    b = Item.objects.create(name="b", quantity=20, threshold=10)
    for item in (a, b):
        item.quantity = 15
        item.save()
    assert alerts(a) == [15] and alerts(b) == [], (
        "Use instance.threshold, not a fixed 5: item a (threshold 20) is low at 15, item b (threshold 10) is not.")


def test_a_freshly_loaded_copy_also_works():
    item = Item.objects.create(name="pen", quantity=10)
    for q in [4, 3, 8, 2]:
        copy = Item.objects.get(pk=item.pk)
        copy.quantity = q
        copy.save()
    assert alerts(item) == [4, 2], (
        f"Reloading the row before each save must give the same result: expected [4, 2], got {alerts(item)}.")
