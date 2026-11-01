from collections import Counter

import pytest

from solution import count_nodes, uses_name

LOOP = """
def total(items):
    result = 0
    for item in items:
        result = result + price(item)
    print(result)
    return result
"""


def test_returns_a_counter():
    counts = count_nodes("x = 1 + 2")
    assert isinstance(counts, Counter), "count_nodes must return a collections.Counter."
    assert counts["Call"] == 0, "A Counter returns 0 for node types that never appear."


def test_simple_assignment():
    counts = count_nodes("x = 1 + 2")
    assert counts["Module"] == 1, "ast.walk yields the root Module node too; count it."
    assert counts["Assign"] == 1, "One assignment statement means one Assign node."
    assert counts["BinOp"] == 1, "1 + 2 is a single BinOp node."
    assert counts["Constant"] == 2, "Both 1 and 2 are Constant nodes; did you stop at the top level?"
    assert counts["Name"] == 1, "x is the only Name node."


def test_nested_nodes_are_counted():
    counts = count_nodes(LOOP)
    assert counts["FunctionDef"] == 1, "The def is one FunctionDef node."
    assert counts["For"] == 1, "The for loop is nested inside the function; ast.walk reaches it."
    assert counts["Call"] == 2, "price(item) and print(result) are two Call nodes deep inside the tree."
    assert counts["Return"] == 1, "One return statement."


def test_empty_source():
    assert count_nodes("") == Counter({"Module": 1}), "Empty source still parses to one empty Module node."


def test_invalid_source_raises():
    with pytest.raises(SyntaxError):
        count_nodes("x = ")


def test_uses_name_reads_and_writes():
    assert uses_name("print(total)", "total") is True, "total is read here: an ast.Name node."
    assert uses_name("total = 5", "total") is True, "An assigned variable is also an ast.Name node (Store context)."
    assert uses_name(LOOP, "result") is True, "Search the whole tree, including function bodies."
    assert uses_name(LOOP, "price") is True, "The function being called, price, is a Name node too."


def test_uses_name_ignores_strings_attributes_and_parameters():
    assert uses_name("print('total')", "total") is False, (
        "Text inside a string is a Constant, not a Name. A substring search of the source gives the wrong answer."
    )
    assert uses_name("obj.total = 5", "total") is False, "obj.total is an Attribute node; only obj is a Name."
    assert uses_name("def f(total):\n    pass", "total") is False, "A parameter is an ast.arg node, not ast.Name."
    assert uses_name("totals = 1", "total") is False, "Compare the whole name: totals is not total."


def test_uses_name_missing():
    assert uses_name("x = 1", "y") is False, "Return False (not None) when the name is not found."
