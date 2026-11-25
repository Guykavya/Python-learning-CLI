import warnings

import pytest

from solution import make_notebook

nbformat = pytest.importorskip("nbformat")

CELLS = [("markdown", "# Title"), ("code", "x = 1"), ("code", "print(x)"), ("markdown", "done")]


def test_top_level_fields():
    nb = make_notebook(CELLS)
    assert nb["nbformat"] == 4 and nb["nbformat_minor"] == 5, "Use nbformat 4 and nbformat_minor 5 (the version with cell ids)."
    assert nb["metadata"] == {}, "Top-level 'metadata' must exist (an empty dict is fine)."
    assert len(nb["cells"]) == 4, "One notebook cell per (kind, text) pair, in order."


def test_cell_fields():
    nb = make_notebook(CELLS)
    for cell, (kind, text) in zip(nb["cells"], CELLS):
        assert cell["cell_type"] == kind, "cell_type must be the kind you were given."
        assert cell["source"] == text, "source is the text as one string."
        assert cell["metadata"] == {}, "Every cell needs a 'metadata' dict."
    code = nb["cells"][1]
    assert code["outputs"] == [], "A code cell starts with outputs = []."
    assert code["execution_count"] is None, "A code cell that never ran has execution_count None (JSON null), not 0."
    assert "outputs" not in nb["cells"][0], "Markdown cells must not have 'outputs'."


def test_ids_are_unique_and_valid():
    import re
    nb = make_notebook(CELLS * 10)
    ids = [c["id"] for c in nb["cells"]]
    assert len(set(ids)) == len(ids), "Cell ids must be unique: use the position in the id."
    assert all(re.fullmatch(r"[A-Za-z0-9_-]{1,64}", i) for i in ids), "An id is 1 to 64 characters of letters, digits, '-' or '_'."


def test_validates_without_warnings():
    nb = make_notebook(CELLS)
    with warnings.catch_warnings():
        warnings.simplefilter("error")
        nbformat.validate(nbformat.from_dict(nb))


def test_empty_notebook_validates():
    nb = make_notebook([])
    assert nb["cells"] == [], "No cells in, no cells out."
    nbformat.validate(nbformat.from_dict(nb))


def test_unknown_kind():
    with pytest.raises(ValueError, match="raw"):
        make_notebook([("raw", "x")])
