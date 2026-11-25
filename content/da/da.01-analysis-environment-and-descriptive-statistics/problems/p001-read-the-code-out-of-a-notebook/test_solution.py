import copy

from solution import code_cells


def test_example_with_both_source_shapes():
    nb = {"cells": [
        {"cell_type": "markdown", "source": ["# Title"]},
        {"cell_type": "code", "source": ["x = 1\n", "print(x)"]},
        {"cell_type": "code", "source": "y = 2"},
    ]}
    assert code_cells(nb) == ["x = 1\nprint(x)", "y = 2"], "Join a list of lines with '' (they already end in newline) and keep a string source as it is."


def test_skips_markdown_and_raw():
    nb = {"cells": [
        {"cell_type": "raw", "source": "x = 1"},
        {"cell_type": "markdown", "source": "y = 2"},
        {"cell_type": "code", "source": ["z = 3"]},
    ]}
    assert code_cells(nb) == ["z = 3"], "Only cells with cell_type 'code' count: raw and markdown cells are skipped."


def test_empty_notebooks():
    assert code_cells({"cells": []}) == [], "No cells: return an empty list."
    assert code_cells({"cells": [{"cell_type": "markdown", "source": "hi"}]}) == [], "No code cells: return an empty list."


def test_empty_source_list_is_empty_string():
    nb = {"cells": [{"cell_type": "code", "source": []}]}
    assert code_cells(nb) == [""], "A code cell with source [] is an empty string, not a missing cell."


def test_order_and_no_mutation():
    nb = {"cells": [{"cell_type": "code", "source": [f"a{i} = {i}\n", "pass"]} for i in range(5)]}
    before = copy.deepcopy(nb)
    out = code_cells(nb)
    assert out == [f"a{i} = {i}\npass" for i in range(5)], "Keep the cells in notebook order."
    assert nb == before, "You changed the caller's notebook; read it, do not edit it."
