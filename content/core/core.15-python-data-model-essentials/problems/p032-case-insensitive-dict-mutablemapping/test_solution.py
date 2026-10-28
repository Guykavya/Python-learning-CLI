import pytest

from solution import CaseInsensitiveDict


def test_is_a_mutable_mapping():
    from collections.abc import MutableMapping
    assert issubclass(CaseInsensitiveDict, MutableMapping), "Inherit from collections.abc.MutableMapping: define 5 methods and get get/pop/update/items/... free."


def test_lookup_ignores_case():
    d = CaseInsensitiveDict()
    d["Content-Type"] = "text/html"
    assert d["content-type"] == "text/html", "Store the key under key.lower() so any case finds it."
    assert d["CONTENT-TYPE"] == "text/html", "Look up with key.lower() in __getitem__ too."


def test_original_case_is_kept_for_iteration():
    d = CaseInsensitiveDict()
    d["Accept"] = 1
    assert list(d) == ["Accept"], "Iteration yields the key as it was written, not lowercased. Store (original_key, value) pairs."
    assert list(d.keys()) == ["Accept"] and list(d.items()) == [("Accept", 1)], "keys() and items() come free from MutableMapping once __iter__ and __getitem__ exist."


def test_overwriting_with_other_case_updates_both():
    d = CaseInsensitiveDict({"Host": "a"})
    d["HOST"] = "b"
    assert len(d) == 1, "'Host' and 'HOST' are the same key: one entry."
    assert d["host"] == "b", "The value is replaced."
    assert list(d) == ["HOST"], "The most recently used spelling wins."


def test_missing_key_raises_keyerror_with_original_key():
    d = CaseInsensitiveDict({"a": 1})
    with pytest.raises(KeyError) as info:
        d["B"]
    assert info.value.args == ("B",), "KeyError should carry the key the caller used ('B'), not the lowercased one."
    with pytest.raises(KeyError):
        del d["zzz"]


def test_non_string_keys_rejected_on_write_and_never_found():
    d = CaseInsensitiveDict()
    with pytest.raises(TypeError):
        d[1] = "x"
    assert (1 in d) is False, "`in` with a non-string key is simply False (no exception)."
    assert (None in d) is False, "Do not call .lower() on non-strings inside __contains__."


def test_contains_and_len_and_delete():
    d = CaseInsensitiveDict(A=1, b=2)
    assert "a" in d and "B" in d, "`in` must ignore case: MutableMapping's default __contains__ uses __getitem__, which already does."
    assert len(d) == 2, "len counts distinct keys case-insensitively."
    del d["A"]
    assert "a" not in d and len(d) == 1, "del removes the entry whatever the case used."


def test_constructor_forms():
    assert dict(CaseInsensitiveDict({"X": 1}, y=2)) == {"X": 1, "y": 2}, "The constructor accepts a mapping and/or keyword arguments (use self.update(...))."
    assert dict(CaseInsensitiveDict([("K", 1), ("k", 2)])) == {"k": 2}, "update() also takes pairs; the later one wins."
    assert len(CaseInsensitiveDict()) == 0, "No arguments: empty."


def test_free_methods_from_mixin():
    d = CaseInsensitiveDict({"Name": "Asha"})
    assert d.get("NAME") == "Asha" and d.get("age") is None and d.get("age", 5) == 5, "get() comes free; it relies on __getitem__ raising KeyError."
    assert d.pop("name") == "Asha" and len(d) == 0, "pop() comes free via __getitem__ and __delitem__."
    assert d.setdefault("Token", "t") == "t" and d["TOKEN"] == "t", "setdefault() comes free."
    d.update({"token": "u"}, Extra=1)
    assert d["TOKEN"] == "u" and d["extra"] == 1 and len(d) == 2, "update() merges case-insensitively."
    d.clear()
    assert len(d) == 0, "clear() comes free."


def test_equality_ignores_key_case():
    a = CaseInsensitiveDict({"A": 1, "b": 2})
    assert a == CaseInsensitiveDict({"a": 1, "B": 2}), "Two case-insensitive dicts with the same keys (ignoring case) and values are equal."
    assert a == {"a": 1, "B": 2}, "Comparing with a plain dict also ignores the case of the keys."
    assert a != {"a": 1}, "Different keys: not equal."
    assert a != CaseInsensitiveDict({"a": 1, "b": 3}), "Different values: not equal."
    assert (a == 5) is False, "Comparing with a non-mapping is False."


def test_copy_is_independent():
    a = CaseInsensitiveDict({"Key": [1]})
    b = a.copy()
    b["key"] = 2
    assert a["KEY"] == [1], "copy() must create a new CaseInsensitiveDict with its own storage."
    assert isinstance(b, CaseInsensitiveDict) and b["Key"] == 2, "copy() returns the same type."


def test_repr():
    d = CaseInsensitiveDict({"Host": "x"})
    assert repr(d) == "CaseInsensitiveDict({'Host': 'x'})", "repr: CaseInsensitiveDict({...}) with the original-case keys."
