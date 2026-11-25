## Approach

Build each cell dict from a small recipe, adding the two code-only keys when needed. Ids from the position are unique and valid (`cell-0`, `cell-1`, ...). Validation is the second opinion: `nbformat.validate` knows the schema, you only have to feed it a correct dict.

## Code

```python
def make_notebook(cells):
    out = []
    for index, (kind, text) in enumerate(cells):
        if kind not in ("markdown", "code"):
            raise ValueError(f"unknown cell kind: {kind!r}")
        cell = {"cell_type": kind, "id": f"cell-{index}", "metadata": {}, "source": text}
        if kind == "code":
            cell["outputs"] = []
            cell["execution_count"] = None
        out.append(cell)
    return {"nbformat": 4, "nbformat_minor": 5, "metadata": {}, "cells": out}
```

## Complexity

O(number of cells).

## Another way

`nbformat.v4.new_notebook()` and `new_code_cell(...)` build the same structure (with random ids). Writing it by hand shows that a notebook is only a dict.
