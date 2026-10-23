import pytest

from target import ticket_price


def test_babies_are_free():
    assert ticket_price(0) == 0, "Age 0 is free."
    assert ticket_price(4) == 0, "Age 4 is the last free age."


def test_child_range():
    assert ticket_price(5) == 50, "Age 5 is the first child age."
    assert ticket_price(12) == 50, "Age 12 is the last child age."


def test_adult_range():
    assert ticket_price(13) == 100, "Age 13 is the first adult age."
    assert ticket_price(59) == 100, "Age 59 is the last adult age."


def test_senior_range():
    assert ticket_price(60) == 60, "Age 60 is the first senior age."
    assert ticket_price(95) == 60, "Seniors have no upper limit."


def test_negative_age():
    with pytest.raises(ValueError):
        ticket_price(-1)
