import pytest

from solution import Config

DATA = {
    "debug": True,
    "name": "shop",
    "db": {"host": "localhost", "port": 5432, "pool": {"min": 1, "max": 10}},
    "ports": [80, 443],
}


def fresh():
    return Config({
        "debug": True,
        "name": "shop",
        "db": {"host": "localhost", "port": 5432, "pool": {"min": 1, "max": 10}},
        "ports": [80, 443],
    })


def test_top_level_values():
    cfg = fresh()
    assert cfg.debug is True and cfg.name == "shop", "cfg.key must return data['key']."
    assert cfg.ports == [80, 443], "Lists come back unchanged (only dicts are wrapped)."


def test_nested_dicts_are_wrapped():
    cfg = fresh()
    assert isinstance(cfg.db, Config), "A dict value must come back wrapped in a Config, so dotted access continues."
    assert cfg.db.host == "localhost" and cfg.db.port == 5432
    assert cfg.db.pool.max == 10, "Wrapping must work at any depth: cfg.db.pool.max."


def test_missing_key_is_attribute_error_not_key_error():
    cfg = fresh()
    try:
        cfg.cache
    except AttributeError:
        pass
    except KeyError:
        pytest.fail(
            "A missing key leaked out as KeyError. Attribute access must raise AttributeError: "
            "catch the KeyError and raise AttributeError(...) from None."
        )
    else:
        pytest.fail("Reading a missing key must raise AttributeError.")


def test_hasattr_and_getattr_default_work():
    cfg = fresh()
    assert hasattr(cfg, "cache") is False, "hasattr needs AttributeError for missing keys."
    assert hasattr(cfg, "debug") is True
    assert getattr(cfg.db, "user", "root") == "root", "getattr(obj, name, default) needs AttributeError too."


def test_error_message_shows_the_dotted_path():
    cfg = fresh()
    with pytest.raises(AttributeError) as err:
        cfg.db.prt
    assert "db.prt" in str(err.value), (
        f"The message must contain the full path 'db.prt', got {str(err.value)!r}. "
        "Give nested Configs their path (for example a second parameter) when you create them."
    )
    with pytest.raises(AttributeError) as err:
        cfg.db.pool.avg
    assert "db.pool.avg" in str(err.value), f"Three levels deep: expected 'db.pool.avg' in {str(err.value)!r}"
    with pytest.raises(AttributeError) as err:
        cfg.missing
    assert "'missing'" in str(err.value), f"At the top level the path is just the key: {str(err.value)!r}"


def test_dir_lists_keys_and_methods():
    cfg = fresh()
    names = dir(cfg)
    for key in ("debug", "name", "db", "ports"):
        assert key in names, f"dir(cfg) must list the key {key!r}. Write __dir__."
    assert "to_dict" in names, (
        "dir(cfg) must still list normal attributes like to_dict. Combine super().__dir__() with the keys."
    )
    assert "pool" in dir(cfg.db), "dir of a nested Config lists its own keys."


def test_to_dict_returns_equal_plain_dict():
    cfg = fresh()
    d = cfg.to_dict()
    assert d == DATA, "to_dict() must return a dict equal to the original data."
    assert type(d) is dict and type(d["db"]) is dict, "to_dict() must return plain dicts, not Config objects."
    assert cfg.db.to_dict() == DATA["db"], "to_dict() works on a nested Config too."


def test_to_dict_is_a_deep_copy():
    cfg = fresh()
    d = cfg.to_dict()
    d["name"] = "changed"
    d["db"]["host"] = "remote"
    d["db"]["pool"]["max"] = 99
    d["ports"].append(8080)
    assert cfg.name == "shop", "Changing the returned dict must not change the config."
    assert cfg.db.host == "localhost", (
        "Changing a NESTED part of the returned dict changed the config: to_dict() must copy every "
        "level (a deep copy), not just the top dict."
    )
    assert cfg.db.pool.max == 10, "Deep copy: the third level must be copied too."
    assert cfg.ports == [80, 443], "Lists inside the data must be copied too."


def test_method_wins_over_a_key_with_the_same_name():
    cfg = Config({"to_dict": 1, "x": 2})
    assert callable(cfg.to_dict), (
        "cfg.to_dict must still be the method. __getattr__ is only called when normal lookup FAILS, "
        "and the method is found on the class first."
    )
    assert cfg.to_dict() == {"to_dict": 1, "x": 2}, "The key 'to_dict' is still part of the data."


def test_empty_config():
    cfg = Config({})
    assert cfg.to_dict() == {}
    assert not hasattr(cfg, "anything")
