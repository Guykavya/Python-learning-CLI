import typing
from typing import get_type_hints

import solution
from solution import apply_patch, describe, with_defaults

KEYS = {"host": str, "port": int, "debug": bool, "timeout": float}


def test_config_shape():
    Config = getattr(solution, "Config", None)
    assert Config is not None and typing.is_typeddict(Config), "Define Config as a TypedDict."
    assert get_type_hints(Config) == KEYS, "Config keys: host: str, port: int, debug: bool, timeout: float."
    assert Config.__required_keys__ == frozenset({"host", "port"}), "host and port are required."
    assert Config.__optional_keys__ == frozenset({"debug", "timeout"}), (
        "debug and timeout are optional: mark them NotRequired[...], or put them in a subclass with total=False."
    )


def test_patch_shape():
    Patch = getattr(solution, "Patch", None)
    assert Patch is not None and typing.is_typeddict(Patch), "Define Patch as a TypedDict."
    assert get_type_hints(Patch) == KEYS, "Patch has the same four keys and types as Config."
    assert Patch.__required_keys__ == frozenset(), "In a Patch NO key is required: use total=False."
    assert Patch.__optional_keys__ == frozenset(KEYS), "All four keys are optional in a Patch."


def test_function_hints():
    C, P = solution.Config, solution.Patch
    assert get_type_hints(with_defaults) == {"cfg": C, "return": C}, "with_defaults(cfg: Config) -> Config."
    assert get_type_hints(apply_patch) == {"cfg": C, "patch": P, "return": C}, "apply_patch(cfg: Config, patch: Patch) -> Config."
    assert get_type_hints(describe) == {"cfg": C, "return": str}, "describe(cfg: Config) -> str."


def test_with_defaults_fills_missing_keys():
    cfg = {"host": "db", "port": 5432}
    assert with_defaults(cfg) == {"host": "db", "port": 5432, "debug": False, "timeout": 30.0}, "Add debug=False and timeout=30.0 when missing."
    assert cfg == {"host": "db", "port": 5432}, "Do not change the input: return a new dict."


def test_with_defaults_keeps_present_falsy_values():
    cfg = {"host": "h", "port": 1, "debug": True, "timeout": 0.0}
    assert with_defaults(cfg) == cfg, "debug=True and timeout=0.0 are present: keep them. 0.0 is falsy but not missing (use 'in', not truthiness)."
    cfg2 = {"host": "h", "port": 1, "debug": False}
    assert with_defaults(cfg2)["debug"] is False and with_defaults(cfg2)["timeout"] == 30.0, "A present debug=False stays False; the missing timeout is added."


def test_apply_patch():
    cfg = {"host": "db", "port": 5432}
    assert apply_patch(cfg, {"port": 1}) == {"host": "db", "port": 1}, "Only the keys in the patch change."
    assert apply_patch(cfg, {}) == cfg, "An empty patch changes nothing."
    assert apply_patch(cfg, {"debug": True, "timeout": 0.0}) == {"host": "db", "port": 5432, "debug": True, "timeout": 0.0}, "A patch may add optional keys, even falsy values like 0.0."
    assert cfg == {"host": "db", "port": 5432}, "Do not change cfg: return a new dict."


def test_apply_patch_does_not_change_the_patch():
    patch = {"host": "new"}
    out = apply_patch({"host": "old", "port": 1}, patch)
    assert out["host"] == "new" and patch == {"host": "new"}, "The patch dict stays as it was."


def test_describe():
    assert describe({"host": "db", "port": 5432}) == "db:5432", "Minimal config: 'host:port'."
    assert describe({"host": "db", "port": 5432, "debug": True}) == "db:5432 (debug)", "debug=True adds ' (debug)'."
    assert describe({"host": "db", "port": 5432, "debug": False}) == "db:5432", "debug=False adds nothing."
    assert describe({"host": "db", "port": 5432, "debug": True, "timeout": 2.5}) == "db:5432 (debug) timeout=2.5", "timeout is added at the end."
    assert describe({"host": "db", "port": 1, "timeout": 0.0}) == "db:1 timeout=0.0", "timeout=0.0 is present, so it is shown."
