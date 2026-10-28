from collections import ChainMap

import pytest

from solution import build_config, env_overrides, source_of


def layers():
    defaults = {"host": "localhost", "port": 8000, "debug": False, "workers": 2}
    file_cfg = {"port": 9000, "workers": 4}
    env = {"debug": "1"}
    cli = {"port": 7000, "host": None, "workers": None}
    return defaults, file_cfg, env, cli


def test_env_overrides():
    got = env_overrides({"APP_DEBUG": "1", "HOME": "/home/k", "APP_LOG_LEVEL": "INFO", "PATH": "/bin"})
    assert got == {"debug": "1", "log_level": "INFO"}, "Keep only APP_ keys, remove the prefix, lower-case the rest; values stay strings."


def test_env_overrides_prefix():
    got = env_overrides({"MY_X": "a", "APP_X": "b", "MYX": "c"}, prefix="MY_")
    assert got == {"x": "a"}, "Use the prefix argument, not a hard-coded 'APP_'. 'MYX' does not start with 'MY_'."
    assert env_overrides({}) == {}, "No variables, no overrides."


def test_env_overrides_prefix_only_at_start():
    got = env_overrides({"XAPP_Y": "1", "MY_APP_Z": "2"})
    assert got == {}, "Only keys that START with the prefix count: use key.startswith(prefix), not 'prefix in key'."


def test_returns_chainmap():
    cfg = build_config(*layers())
    assert isinstance(cfg, ChainMap), "Return a ChainMap (a live view), not a merged dict copy."
    assert len(cfg.maps) == 5, "Five layers: runtime, cli, env, file, defaults."


def test_priority():
    cfg = build_config(*layers())
    assert cfg["port"] == 7000, "cli beats file and defaults: put the layers in the ChainMap highest priority FIRST."
    assert cfg["debug"] == "1", "env beats defaults."
    assert cfg["workers"] == 4, "cli 'workers' is None, so it is skipped; the file value 4 wins over the default 2."
    assert cfg["host"] == "localhost", "cli 'host' is None: it must not hide the default. Leave out None values from the cli layer."


def test_none_cli_values_removed():
    cfg = build_config(*layers())
    assert None not in cfg.values(), "No None values should come through from the cli layer."


def test_source_of():
    cfg = build_config(*layers())
    assert source_of(cfg, "port") == "cli", "port comes from the cli layer."
    assert source_of(cfg, "debug") == "env", "debug comes from the env layer."
    assert source_of(cfg, "workers") == "file", "workers comes from the file layer (cli was None)."
    assert source_of(cfg, "host") == "defaults", "host comes from defaults."
    with pytest.raises(KeyError):
        source_of(cfg, "nope")


def test_runtime_writes_stay_in_front_layer():
    defaults, file_cfg, env, cli = layers()
    cfg = build_config(defaults, file_cfg, env, cli)
    cfg["port"] = 1
    cfg["new"] = "x"
    assert cfg["port"] == 1, "A runtime assignment wins over every layer."
    assert source_of(cfg, "port") == "runtime", "Writes go into the first map, the runtime layer."
    assert cli == {"port": 7000, "host": None, "workers": None}, "The caller's cli dict must not change."
    assert defaults["port"] == 8000 and "new" not in defaults, "The caller's defaults must not change: a ChainMap writes to its FIRST map only."
    del cfg["port"]
    assert cfg["port"] == 7000, "Deleting the runtime value uncovers the cli value again."


def test_layers_are_live():
    defaults, file_cfg, env, cli = layers()
    cfg = build_config(defaults, file_cfg, env, cli)
    defaults["timeout"] = 30
    env["host"] = "example.org"
    assert cfg["timeout"] == 30, "A ChainMap is a view: a key added to defaults later must be visible. Do not copy defaults."
    assert cfg["host"] == "example.org", "A key added to env later must be visible and beat defaults."


def test_empty_layers():
    cfg = build_config({}, {}, {}, {})
    assert dict(cfg) == {}, "All layers empty: an empty config."
    with pytest.raises(KeyError):
        cfg["x"]
