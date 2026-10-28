from datetime import date, datetime
from pathlib import Path

import pytest

from solution import dump_json


def test_set_and_date():
    out = dump_json({"tags": {"b", "a"}, "when": date(2024, 1, 5)})
    assert out == '{"tags": ["a", "b"], "when": "2024-01-05"}', "A set becomes a sorted list and a date becomes its isoformat() text."


def test_datetime_and_path():
    out = dump_json({"p": Path("x/y"), "t": datetime(2024, 1, 5, 10, 30)})
    assert out == '{"p": "%s", "t": "2024-01-05T10:30:00"}' % str(Path("x/y")), "A Path becomes str(path); a datetime becomes its isoformat()."


def test_nested():
    out = dump_json({"a": [{"s": {3, 1, 2}}], "b": {"d": date(2000, 2, 29)}})
    assert out == '{"a": [{"s": [1, 2, 3]}], "b": {"d": "2000-02-29"}}', "default= is also used inside nested lists and dicts."


def test_plain_data_unchanged():
    assert dump_json({"b": [1, 2.5, None, True], "a": "é"}) == '{"a": "\\u00e9", "b": [1, 2.5, null, true]}', "Plain data must give the normal json.dumps result, with sort_keys=True."


def test_unknown_object_raises():
    with pytest.raises(TypeError):
        dump_json({"x": object()})


def test_unknown_complex_raises():
    with pytest.raises(TypeError):
        dump_json([1 + 2j])


def test_set_order_is_stable():
    words = {"pear", "apple", "fig", "kiwi", "banana"}
    assert dump_json(words) == '["apple", "banana", "fig", "kiwi", "pear"]', "Sort the set so the output is the same on every run."
