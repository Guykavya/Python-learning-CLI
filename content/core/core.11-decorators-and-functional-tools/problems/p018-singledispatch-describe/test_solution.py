from solution import describe


def test_ints():
    assert describe(5) == "int 5 (odd)", "Register a version for int: 'int N (odd)' or 'int N (even)'."
    assert describe(-4) == "int -4 (even)", "-4 % 2 is 0, so -4 is even."
    assert describe(0) == "int 0 (even)", "0 is even."


def test_bool_has_its_own_version():
    assert describe(True) == "bool True", "bool is a subclass of int. Register a separate version for bool, or True looks like 'int 1 (odd)'."
    assert describe(False) == "bool False", "Same for False."


def test_str():
    assert describe("ab") == "text 'ab' of length 2", "Use {x!r} so the text gets quotes, and len(x)."
    assert describe("") == "text '' of length 0", "Empty text has length 0."


def test_list_recurses():
    assert describe([1, "a"]) == "list of 2: [int 1 (odd), text 'a' of length 1]", "Describe each item by calling describe() again, and join with ', '."
    assert describe([]) == "list of 0: []", "An empty list has empty brackets."
    assert describe([[True]]) == "list of 1: [list of 1: [bool True]]", "Nested lists work because the list version calls describe on each item."


def test_fallback():
    assert describe(2.5) == "unknown: 2.5", "Types without a version use the base function: 'unknown: ' + repr(x)."
    assert describe({"k": 1}) == "unknown: {'k': 1}", "A dict is not registered, so it is unknown."
    assert describe(None) == "unknown: None", "None is unknown too."


def test_uses_singledispatch():
    registry = getattr(describe, "registry", None)
    assert registry is not None, "Make describe with @functools.singledispatch, not an if/elif chain."
    for t in (int, bool, str, list):
        assert t in registry, f"Register a version for {t.__name__} with @describe.register."
