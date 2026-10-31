import inspect

import pytest

import solution
from solution import WeatherReport


class FakeClient:
    """A hand-written fake: canned data plus a record of the calls."""

    def __init__(self, data):
        self.data = data
        self.calls = []

    def temperature(self, city):
        self.calls.append(city)
        return self.data[city]


def test_hot():
    assert WeatherReport(FakeClient({"Delhi": 35})).line("Delhi") == "Delhi: 35C, hot"


@pytest.mark.parametrize("temp, label", [(30, "hot"), (29.9, "mild"), (6, "mild"), (5, "cold"), (-3, "cold")])
def test_label_borders(temp, label):
    got = WeatherReport(FakeClient({"X": temp})).line("X")
    assert got == f"X: {temp}C, {label}", (
        f"{temp} should be '{label}': 30 and above is hot, 5 and below is cold (borders included).")


def test_float_is_printed_as_given():
    assert WeatherReport(FakeClient({"Pune": 21.5})).line("Pune") == "Pune: 21.5C, mild", (
        "Print the number as the client gave it; do not round it.")


def test_unknown_city():
    assert WeatherReport(FakeClient({})).line("Atlantis") == "Atlantis: no data", (
        "A KeyError from the client means 'no data'.")


def test_other_errors_are_not_hidden():
    class Broken:
        def temperature(self, city):
            raise ConnectionError("down")

    with pytest.raises(ConnectionError):
        WeatherReport(Broken()).line("Delhi")


def test_lines_keep_order_and_ask_once_per_city():
    client = FakeClient({"A": 40, "B": 1, "C": 20})
    got = WeatherReport(client).lines(["C", "A", "B"])
    assert got == ["C: 20C, mild", "A: 40C, hot", "B: 1C, cold"], "lines must keep the order of the input."
    assert client.calls == ["C", "A", "B"], "Ask the client exactly once per city."


def test_class_builds_no_client_of_its_own():
    source = inspect.getsource(solution)
    for word in ("import requests", "urllib", "socket", "http.client", "import os"):
        assert word not in source, f"{word!r}: the class must get its client from outside, not create one."
