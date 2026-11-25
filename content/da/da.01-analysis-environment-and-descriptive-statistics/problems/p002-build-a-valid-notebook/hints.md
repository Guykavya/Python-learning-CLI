## Hint 1

Which keys does a markdown cell have, and which two extra keys does a code cell need? Where will you get an id that is different for every cell (the index is enough)?

## Hint 2

```text
cells_out = []
for index, (kind, text) in enumerate(cells):
    if kind not in ("markdown", "code"): raise ValueError(...)
    cell = {"cell_type": kind, "id": f"cell-{index}", "metadata": {}, "source": text}
    if kind == "code": cell["outputs"] = []; cell["execution_count"] = None
    cells_out.append(cell)
return {"nbformat": 4, "nbformat_minor": 5, "metadata": {}, "cells": cells_out}
```
