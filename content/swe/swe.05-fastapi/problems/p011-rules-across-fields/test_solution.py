import pytest
from fastapi.testclient import TestClient
from pydantic import ValidationError

from solution import Booking, app


@pytest.fixture
def client():
    with TestClient(app) as c:
        yield c


def booking(start="2026-03-01", end="2026-03-04", guests=2, room="double"):
    return {"start": start, "end": end, "guests": guests, "room": room}


def errors(response):
    assert response.status_code == 422, f"Expected a 422, got {response.status_code}: {response.text}"
    return [(e["loc"], e["type"]) for e in response.json()["detail"]]


def test_good_bookings(client):
    r = client.post("/bookings", json=booking(guests=4))
    assert r.status_code == 201, f"4 guests in a double for 3 nights is fine; got {r.status_code}: {r.text}"
    assert r.json() == {"room": "double", "guests": 4, "nights": 3}
    r = client.post("/bookings", json=booking(end="2026-03-02", guests=2, room="single"))
    assert r.status_code == 201, f"2 guests in a single for 1 night is fine (the limits are inclusive); got {r.text}"
    assert r.json()["nights"] == 1


@pytest.mark.parametrize("end, why", [
    ("2026-03-01", "zero nights: end equal to start is not 'after'"),
    ("2026-02-27", "end before start"),
])
def test_end_must_be_after_start(client, end, why):
    found = errors(client.post("/bookings", json=booking(end=end)))
    assert found == [(["body"], "value_error")], (
        f"{why}: expected ONE error at ['body'] (a model validator's error belongs to the whole body); got {found}")


@pytest.mark.parametrize("guests, room", [(5, "double"), (3, "single")])
def test_too_many_guests_for_the_room(client, guests, room):
    found = errors(client.post("/bookings", json=booking(guests=guests, room=room)))
    assert found == [(["body"], "value_error")], (
        f"{guests} guests do not fit in a {room} (MAX_GUESTS); expected one error at ['body'], got {found}")


def test_order_of_the_rules():
    with pytest.raises(ValidationError) as info:
        Booking(**booking(end="2026-02-27", guests=9))
    message = str(info.value)
    assert "end must be after start" in message, (
        "When both rules fail, the date rule is checked first and its ValueError stops the validator; "
        f"got: {message}")


def test_field_errors_come_first_and_alone(client):
    found = errors(client.post("/bookings", json=booking(end="2026-02-27", guests=0)))
    assert found == [(["body", "guests"], "greater_than_equal")], (
        "guests=0 breaks Field(ge=1). An 'after' model validator does not run while a field is invalid, "
        f"so this is the ONLY error; got {found}")


def test_unknown_room_is_a_field_error(client):
    found = errors(client.post("/bookings", json=booking(room="suite")))
    assert found == [(["body", "room"], "literal_error")], f"room is Literal['single', 'double']; got {found}"


def test_model_works_in_python():
    b = Booking(start="2026-01-10", end="2026-01-12", guests=1, room="single")
    assert (b.end - b.start).days == 2, "The model validator must return self, or the model is lost."
