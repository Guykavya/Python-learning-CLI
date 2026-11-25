# Read the code out of a notebook

Chapter section 2.5: a notebook is just a JSON file. Its `"cells"` list holds dicts with a `"cell_type"` (`"code"`, `"markdown"` or `"raw"`) and a `"source"`. The `"source"` is stored **either as a list of lines (each line keeps its `\n`) or as one string**; both are legal, and real files contain both.

Write `code_cells(nb)`: `nb` is a notebook already loaded as a dict. Return a list with the source text of every **code** cell, in order, each as one string. Skip markdown and raw cells. A notebook with no cells (or no code cells) gives `[]`. Do not change `nb`.

## Example

```python
nb = {"cells": [
    {"cell_type": "markdown", "source": ["# Title"]},
    {"cell_type": "code", "source": ["x = 1\n", "print(x)"]},
    {"cell_type": "code", "source": "y = 2"},
]}
code_cells(nb)   # ['x = 1\nprint(x)', 'y = 2']
```
