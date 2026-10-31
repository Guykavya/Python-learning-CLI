import inspect
from collections import Counter

import pytest

import solution
from solution import Copier, Device, Printer, Scanner


@pytest.fixture(autouse=True)
def reset_connections():
    Device.connections = 0
    yield
    Device.connections = 0


def make(cls, *args, **kwargs):
    try:
        return cls(*args, **kwargs)
    except TypeError as e:
        pytest.fail(
            f"{cls.__name__}(...) raised TypeError: {e}. Printer and Scanner take name through **kwargs and "
            "pass it on; Copier passes name=name, dpi=dpi, colour=colour as keywords to super().__init__."
        )
    except AttributeError as e:
        pytest.fail(
            f"{cls.__name__}(...) raised AttributeError: {e}. Call super().__init__(...) FIRST: Device creates "
            "self.log, so nobody can append to it before Device.__init__ has run."
        )


def test_mro_is_the_diamond():
    assert [c.__name__ for c in Copier.__mro__] == ["Copier", "Printer", "Scanner", "Device", "object"], (
        "Keep the class structure: Copier(Printer, Scanner), Printer(Device), Scanner(Device)."
    )


def test_one_connection_per_copier():
    make(Copier, "office", dpi=600, colour=False)
    assert Device.connections == 1, (
        f"One Copier opened {Device.connections} connections. Device.__init__ must run once: "
        "use super().__init__ instead of calling Printer.__init__ and Scanner.__init__ by name."
    )
    make(Copier, "hall")
    assert Device.connections == 2, "Two copiers, two connections."


def test_copier_log_keeps_every_class():
    c = make(Copier, "office", dpi=600, colour=False)
    assert c.log == ["Device", "Scanner", "Printer", "Copier"], (
        f"Got {c.log}. Each __init__ calls super().__init__ FIRST, then appends its own name. "
        "If 'Printer' is missing, Device.__init__ ran twice and replaced self.log."
    )


def test_copier_attributes():
    c = make(Copier, "office", dpi=600, colour=False, copies_per_minute=30)
    assert (c.name, c.dpi, c.colour, c.copies_per_minute) == ("office", 600, False, 30), (
        "Copier must pass name, dpi and colour along the chain as keywords so that each class gets its own."
    )


def test_copier_defaults():
    c = make(Copier, "hall")
    assert (c.dpi, c.colour, c.copies_per_minute) == (300, True, 20), "Defaults: dpi=300, colour=True, copies_per_minute=20."


def test_device_init_runs_once(monkeypatch):
    calls = Counter()
    original = vars(Device)["__init__"]

    def counting_init(self, *args, **kwargs):
        calls["Device"] += 1
        original(self, *args, **kwargs)

    monkeypatch.setattr(Device, "__init__", counting_init)
    make(Copier, "office")
    assert calls["Device"] == 1, f"Device.__init__ ran {calls['Device']} times for one Copier. It must run exactly once."


def test_single_branches_still_work():
    p = make(Printer, name="p1", dpi=1200)
    s = make(Scanner, name="s1")
    assert (p.name, p.dpi, p.log) == ("p1", 1200, ["Device", "Printer"]), "A Printer alone: MRO Printer, Device."
    assert (s.name, s.colour, s.log) == ("s1", True, ["Device", "Scanner"]), "A Scanner alone: MRO Scanner, Device."
    assert Device.connections == 2, "One connection per device."


def test_plain_device():
    d = make(Device, "lamp")
    assert (d.name, d.log, Device.connections) == ("lamp", ["Device"], 1), "Device sets name, log = ['Device'] and counts one connection."


def test_unknown_keywords_rejected():
    for build in (lambda: Printer(name="p1", colour=False), lambda: Copier("office", speed=5)):
        try:
            build()
        except TypeError:
            continue
        pytest.fail(
            "A keyword nobody takes (colour for a Printer, speed for a Copier) must raise TypeError. "
            "Device must end the chain with super().__init__(**kwargs) so object.__init__ refuses leftovers."
        )


def test_no_class_called_by_name():
    for cls in (Printer, Scanner, Copier):
        source = inspect.getsource(vars(cls)["__init__"])
        for parent in ("Device.__init__", "Printer.__init__", "Scanner.__init__"):
            assert parent not in source, (
                f"{cls.__name__}.__init__ still calls {parent}(...) by name. Use super().__init__(...) instead."
            )


def test_connections_is_a_class_attribute():
    assert "connections" in vars(Device), "connections lives on the class Device (a class attribute)."
    d = make(Device, "lamp")
    assert "connections" not in vars(d), "Use Device.connections += 1, not self.connections += 1 (that makes an instance attribute)."
