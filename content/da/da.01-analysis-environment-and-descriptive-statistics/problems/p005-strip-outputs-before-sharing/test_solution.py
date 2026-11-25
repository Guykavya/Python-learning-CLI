import copy

from solution import strip_outputs


def make():
    return {"nbformat": 4, "nbformat_minor": 5, "metadata": {"kernelspec": {"name": "python3"}}, "cells": [
        {"cell_type": "markdown", "id": "m", "metadata": {}, "source": "# T"},
        {"cell_type": "code", "id": "a", "metadata": {"execution": {"iopub.status.busy": "t"}, "tags": ["x"]},
         "source": "1 + 1", "outputs": [{"output_type": "stream", "name": "stdout", "text": "2\n"}], "execution_count": 7},
        {"cell_type": "code", "id": "b", "metadata": {}, "source": "x", "outputs": [], "execution_count": None},
    ]}


def test_outputs_and_counts_cleared():
    clean = strip_outputs(make())
    for cell in clean["cells"]:
        if cell["cell_type"] == "code":
            assert cell["outputs"] == [], "Every code cell must end with outputs == []."
            assert cell["execution_count"] is None, "execution_count must be None (never run), not 0 and not the old number."


def test_execution_metadata_removed_other_kept():
    clean = strip_outputs(make())
    assert clean["cells"][1]["metadata"] == {"tags": ["x"]}, "Remove only the 'execution' key from cell metadata; keep tags and the rest."


def test_everything_else_unchanged():
    nb = make()
    clean = strip_outputs(nb)
    assert clean["metadata"] == nb["metadata"], "Top-level metadata must stay."
    assert [c["source"] for c in clean["cells"]] == ["# T", "1 + 1", "x"], "Sources and order must stay."
    assert "outputs" not in clean["cells"][0], "Do not add 'outputs' to markdown cells."


def test_input_not_mutated():
    nb = make()
    before = copy.deepcopy(nb)
    clean = strip_outputs(nb)
    assert nb == before, "you changed the caller's notebook: the mutation trap of Ch. 3.4. Copy first (copy.deepcopy), then clean the copy."
    assert clean is not nb and clean["cells"] is not nb["cells"], "Return a new notebook, not the same object."


def test_clean_notebook_is_stable():
    once = strip_outputs(make())
    assert strip_outputs(once) == once, "Stripping an already clean notebook should change nothing."
