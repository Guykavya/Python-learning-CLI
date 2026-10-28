import tomllib

import pytest

from solution import load_config


def test_defaults_when_missing(tmp_path):
    assert load_config(tmp_path / "none.toml") == {"host": "localhost", "port": 8000, "debug": False, "tags": []}, "A missing file gives the defaults."


def test_file_overrides(tmp_path):
    p = tmp_path / "app.toml"
    p.write_text('port = 9000\ntags = ["a", "b"]\n', encoding="utf-8")
    assert load_config(p) == {"host": "localhost", "port": 9000, "debug": False, "tags": ["a", "b"]}, "File values replace defaults; other defaults stay."


def test_extra_keys_kept(tmp_path):
    p = tmp_path / "app.toml"
    p.write_text('name = "démo"\ndebug = true\n\n[db]\nuser = "x"\n', encoding="utf-8")
    cfg = load_config(str(p))
    assert cfg["name"] == "démo" and cfg["debug"] is True, "Keys not in the defaults must be kept, and booleans stay booleans."
    assert cfg["db"] == {"user": "x"}, "Tables become nested dicts."


def test_fresh_data_each_call(tmp_path):
    first = load_config(tmp_path / "none.toml")
    first["tags"].append("leak")
    first["port"] = 1
    second = load_config(tmp_path / "none.toml")
    assert second["tags"] == [], "The defaults were changed by an earlier call. Copy them (deepcopy) so the tags list is not shared."
    assert second["port"] == 8000, "Return a new dict every time."


def test_bad_toml_raises(tmp_path):
    p = tmp_path / "bad.toml"
    p.write_text("port = = 9\n")
    with pytest.raises(tomllib.TOMLDecodeError):
        load_config(p)


def test_empty_file(tmp_path):
    p = tmp_path / "empty.toml"
    p.write_text("")
    assert load_config(p)["port"] == 8000, "An empty file is valid TOML: all defaults."
