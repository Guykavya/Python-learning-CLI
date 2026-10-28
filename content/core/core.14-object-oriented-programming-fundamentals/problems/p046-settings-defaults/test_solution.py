import pytest

from solution import DevSettings, ProductionSettings, Settings


def test_class_defaults():
    assert (Settings.debug, Settings.host, Settings.port, Settings.workers) == (False, "localhost", 8000, 1), (
        "Keep the defaults as class attributes of Settings."
    )
    assert DevSettings.debug is True, "DevSettings sets debug = True."
    assert (ProductionSettings.host, ProductionSettings.port, ProductionSettings.workers) == ("0.0.0.0", 80, 4), (
        "ProductionSettings overrides host, port and workers."
    )


def test_names():
    assert Settings.names() == ["debug", "host", "port", "workers"], (
        "names() lists class attributes that do not start with '_' and are not callable, sorted. Methods are not settings."
    )
    assert ProductionSettings.names() == ["debug", "host", "port", "workers"], "Inherited settings count too."


def test_names_include_subclass_settings():
    class CacheSettings(Settings):
        cache_size = 128

    assert CacheSettings.names() == ["cache_size", "debug", "host", "port", "workers"], "A subclass can add a setting."
    assert CacheSettings(cache_size=256).cache_size == 256, "The new setting can be overridden on the subclass."
    with pytest.raises(TypeError):
        Settings(cache_size=1)


def test_override_and_fall_through():
    s = Settings(port=9000)
    assert s.port == 9000, "An override is stored on the object."
    assert s.host == "localhost", "A setting that was not given falls through to the class default."
    assert s.overrides() == {"port": 9000}, (
        "Only the given overrides may be stored on the object. Do not copy every default onto it."
    )
    assert Settings().overrides() == {}, "No overrides: nothing stored on the object."


def test_class_default_change_is_seen():
    s = Settings(port=9000)
    old = Settings.workers
    try:
        Settings.workers = 3
        assert s.workers == 3, (
            "Changing the class default must show in objects that did not override it. "
            "That only works if __init__ does not copy the defaults onto the object."
        )
        assert s.port == 9000, "An override still hides the class value."
    finally:
        Settings.workers = old


def test_unknown_setting():
    with pytest.raises(TypeError, match="unknown setting"):
        Settings(colour="red")
    with pytest.raises(TypeError, match="unknown setting"):
        Settings(as_dict=1)
    with pytest.raises(TypeError, match="unknown setting"):
        Settings(_secret=1)


def test_type_must_match_exactly():
    for kwargs in ({"port": "80"}, {"port": 80.0}, {"port": True}, {"debug": 1}, {"host": None}):
        try:
            Settings(**kwargs)
        except TypeError:
            continue
        pytest.fail(
            f"Settings(**{kwargs}) was accepted. Compare types exactly with type(value) is type(default); "
            "isinstance(True, int) is True, so isinstance lets bools through."
        )
    assert Settings(debug=True).debug is True, "A bool for a bool setting is fine."


def test_as_dict():
    p = ProductionSettings(workers=8)
    assert p.as_dict() == {"debug": False, "host": "0.0.0.0", "port": 80, "workers": 8}, (
        "as_dict gives every setting's current value: overrides first, then the class (and parent) defaults."
    )
    assert list(p.as_dict()) == ["debug", "host", "port", "workers"], "Keys in sorted order."
    assert DevSettings().as_dict()["debug"] is True, "DevSettings default debug is True."


def test_reset():
    s = Settings(port=9000, debug=True)
    s.reset("port")
    assert s.port == 8000, "After reset the class default shows again."
    assert s.overrides() == {"debug": True}, "reset removes only that override."
    s.reset("port")
    assert s.port == 8000, "Resetting a setting with no override does nothing."
    with pytest.raises(TypeError):
        s.reset("colour")


def test_reset_never_touches_the_class():
    s = Settings()
    s.reset("port")
    assert Settings.port == 8000, "reset must not delete or change the class default."


def test_with_changes():
    p = ProductionSettings(workers=8)
    p2 = p.with_changes(debug=True)
    assert type(p2) is ProductionSettings, "with_changes returns an object of the SAME class (type(self)), not plain Settings."
    assert p2.overrides() == {"workers": 8, "debug": True}, "The new object has the old overrides plus the changes."
    assert p.overrides() == {"workers": 8}, "with_changes must not change the original object."
    p3 = p.with_changes(workers=2)
    assert p3.workers == 2, "A change replaces an old override."
    with pytest.raises(TypeError):
        p.with_changes(port="x")


def test_objects_are_separate():
    a = Settings(port=1)
    b = Settings()
    assert b.port == 8000, "One object's override must not change another object or the class."
    assert Settings.port == 8000, "Overrides never change the class default."
