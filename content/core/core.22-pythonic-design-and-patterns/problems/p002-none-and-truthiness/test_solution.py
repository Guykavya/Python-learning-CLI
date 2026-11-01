import ast
from pathlib import Path

import solution
from solution import config_get, describe, first_non_empty

TREE = ast.parse(Path(solution.__file__).read_text())


def test_describe_plain_values():
    assert describe(None) == "missing", "None is 'missing'. Test it with 'is None'."
    assert describe(True) == "yes", "True is 'yes'."
    assert describe(False) == "no", "False is 'no'."
    assert describe(42) == "value 42", "Other values print as 'value ' plus repr."
    assert describe("hi") == "value 'hi'", "Use repr(value), so strings show their quotes."
    assert describe([1]) == "value [1]", "A non-empty list is just a value."


def test_describe_falsy_values_are_not_missing():
    assert describe(0) == "zero", "0 is a real number, not 'empty' and not 'no'. Check it on its own."
    assert describe(0.0) == "zero", "0.0 is also zero."
    assert describe("") == "empty text", "'' is an empty string, not None."
    assert describe([]) == "empty list", "[] is an empty list, not None."


def test_describe_one_is_not_true():
    assert describe(1) == "value 1", "1 == True is True in Python, so 'value == True' wrongly says 'yes'. Use 'is True'."
    assert describe(1.0) == "value 1.0", "1.0 == True too. Compare booleans with 'is'."


def test_first_non_empty_keeps_falsy_values():
    assert first_non_empty([None, None, 5]) == 5, "Skip None, return the first real value."
    assert first_non_empty([None, 0, 5]) == 0, "0 is a real value: only None counts as empty."
    assert first_non_empty([None, "", "x"]) == "", "'' is a real value too."
    assert first_non_empty([[], 1]) == [], "[] is a real value too."
    assert first_non_empty([False, 1]) is False, "False is a real value too."


def test_first_non_empty_default():
    assert first_non_empty([]) is None, "Nothing found: return the default (None)."
    assert first_non_empty([None, None], default="d") == "d", "All None: return the default."
    assert first_non_empty([None], default=0) == 0, "The default can itself be falsy."


def test_config_get():
    cfg = {"port": 0, "name": "", "debug": False, "tags": [], "host": "h", "gone": None}
    assert config_get(cfg, "host", "x") == "h", "A normal value is returned."
    assert config_get(cfg, "port", 8080) == 0, "port = 0 was set on purpose; only a missing key uses the default."
    assert config_get(cfg, "name", "anon") == "", "An empty name was set on purpose."
    assert config_get(cfg, "debug", True) is False, "debug = False was set on purpose."
    assert config_get(cfg, "tags", ["a"]) == [], "An empty list was set on purpose."
    assert config_get(cfg, "missing", 7) == 7, "A missing key gives the default."
    assert config_get(cfg, "gone", 7) == 7, "A value of None counts as 'not set': use the default."


def test_no_equality_with_none_or_booleans():
    for node in ast.walk(TREE):
        if isinstance(node, ast.Compare):
            for op, right in zip(node.ops, node.comparators):
                if isinstance(op, (ast.Eq, ast.NotEq)) and isinstance(right, ast.Constant) \
                        and (right.value is None or right.value is True or right.value is False):
                    raise AssertionError(
                        "Found '== None', '== True' or '== False'. Use 'is None' / 'is True' / 'is False'. "
                        "They are singletons, and == can be fooled (1 == True)."
                    )
