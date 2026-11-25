# Build a valid notebook

Chapter section 2.5. A notebook of format `4.5` needs more than a list of cells: every cell must have a **unique `id`** (1 to 64 letters, digits, `-` or `_`), a `metadata` dict, and code cells need `outputs` and `execution_count`. A file without ids still validates today but prints a warning that will become an error, so we always write ids.

Write `make_notebook(cells)`. `cells` is a list of `(kind, text)` pairs, with `kind` either `"markdown"` or `"code"`. Return a notebook dict:

- top level: `"nbformat": 4`, `"nbformat_minor": 5`, `"metadata": {}`, `"cells": [...]`;
- every cell: `"cell_type"`, a unique `"id"`, `"metadata": {}` and `"source"` (the text as **one string**);
- code cells also: `"outputs": []` and `"execution_count": None`;
- any other kind: raise `ValueError` that names the bad kind.

## Example

```python
nb = make_notebook([("markdown", "# Title"), ("code", "x = 1")])
nb["cells"][1]["outputs"]            # []
nb["cells"][1]["execution_count"]    # None
```

The tests run `nbformat.validate` on your result and fail on any warning.
