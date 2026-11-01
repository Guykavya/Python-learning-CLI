import pytest

from solution import Field, Observable, fields, history, subscribe, undo, unsubscribe


class Settings(Observable):
    volume = Field(default=5)
    theme = Field(default="light")

    def louder(self):
        self.volume = self.volume + 1


def recorder(obj):
    log = []
    subscribe(obj, lambda o, name, old, new: log.append((o, name, old, new)))
    return log


def test_defaults_and_class_access():
    s = Settings()
    assert s.volume == 5 and s.theme == "light", "A field that was never set returns its default."
    assert isinstance(Settings.volume, Field), "Reading through the class (instance is None) returns the descriptor."
    assert Settings.volume.name == "volume", "__set_name__ should store the attribute name on the descriptor."


def test_values_are_per_object():
    a, b = Settings(), Settings()
    a.volume = 9
    assert b.volume == 5, (
        "Each object needs its own value. Store it in obj.__dict__[name], not on the descriptor (shared by all objects)."
    )
    assert a.__dict__["volume"] == 9, "The value lives in the object's __dict__ under the field name."


def test_init_sets_initial_values_quietly():
    s = Settings(volume=1, theme="dark")
    assert (s.volume, s.theme) == (1, "dark"), "Observable.__init__(**values) sets the initial values."
    assert history(s) == [], "Initial values from __init__ must not be recorded in history."
    with pytest.raises(TypeError):
        Settings(colour="red")


def test_subscribers_get_obj_name_old_new():
    s = Settings(theme="dark")
    log = recorder(s)
    s.volume = 7
    s.theme = "blue"
    assert log == [(s, "volume", 5, 7), (s, "theme", "dark", "blue")], (
        "Call each subscriber as callback(obj, name, old, new). The first old value of volume is its default, 5."
    )


def test_same_value_is_ignored():
    s = Settings()
    log = recorder(s)
    s.volume = 5
    s.volume = 6
    s.volume = 6
    assert log == [(s, "volume", 5, 6)], "Assigning a value equal to the current one must not notify."
    assert history(s) == [("volume", 5, 6)], "... and must not be recorded in history."


def test_subscribers_per_object_and_in_order():
    a, b = Settings(), Settings()
    calls = []
    subscribe(a, lambda o, n, old, new: calls.append("first"))
    subscribe(a, lambda o, n, old, new: calls.append("second"))
    b.volume = 1
    assert calls == [], "Subscribers of a must not hear about changes to b: keep subscribers per object."
    a.volume = 1
    assert calls == ["first", "second"], "Notify subscribers in the order they subscribed."


def test_subscribe_returns_callback_and_unsubscribe():
    s = Settings()
    seen = []

    @(lambda f: subscribe(s, f))
    def on_change(obj, name, old, new):
        seen.append(name)

    assert on_change is not None and callable(on_change), "subscribe must return the callback (usable as a decorator)."
    s.theme = "dark"
    unsubscribe(s, on_change)
    s.theme = "light"
    assert seen == ["theme"], "After unsubscribe, the callback must not be called any more."


def test_history_is_per_object_and_a_copy():
    a, b = Settings(), Settings()
    a.volume = 1
    a.louder()
    b.theme = "x"
    assert history(a) == [("volume", 5, 1), ("volume", 1, 2)], "History lists (name, old, new), oldest first."
    assert history(b) == [("theme", "light", "x")], "Each object has its own history."
    h = history(a)
    h.clear()
    assert len(history(a)) == 2, "history(obj) must return a copy, so callers cannot erase the real history."


def test_undo():
    s = Settings()
    log = recorder(s)
    s.volume = 8
    s.theme = "dark"
    assert undo(s) == ("theme", "light", "dark"), "undo returns the change it reverted, as (name, old, new)."
    assert s.theme == "light", "undo sets the field back to its old value."
    assert log[-1] == (s, "theme", "dark", "light"), "undo notifies subscribers with (obj, name, new, old): the reverse change."
    assert history(s) == [("volume", 5, 8)], "undo removes the entry and does NOT add a new one for the revert."
    assert undo(s) == ("volume", 5, 8) and s.volume == 5, "A second undo reverts the change before that."
    assert undo(s) is None, "With nothing left to undo, undo returns None."
    assert len(log) == 4, "Two changes plus two undos: four notifications in total."


def test_fields_in_definition_order_with_inheritance():
    assert fields(Settings) == ("volume", "theme"), "fields(cls) lists Field names in definition order."
    assert fields(Settings()) == ("volume", "theme"), "fields also accepts an object."

    class Advanced(Settings):
        debug = Field(default=False)
        label = "not a field"

    assert fields(Advanced) == ("volume", "theme", "debug"), (
        "A subclass lists the parent's fields first, then its own. Plain attributes and methods are not fields."
    )
    adv = Advanced(debug=True)
    log = recorder(adv)
    adv.volume = 0
    assert adv.debug is True and log == [(adv, "volume", 5, 0)], "Inherited fields keep working in subclasses."
    assert fields(Settings) == ("volume", "theme"), "Creating a subclass must not change the parent's fields."


def test_fields_found_without_annotations():
    class Plain(Observable):
        a = Field(1)
        b = Field(2)

    class Annotated(Observable):
        x: int = Field(0)
        note: str = "hi"

    assert fields(Plain) == ("a", "b"), "Fields without annotations must be found: scan vars(cls) for Field objects."
    assert fields(Annotated) == ("x",), (
        "Only Field objects are fields; an annotated plain value is not. Do not read __annotations__."
    )
