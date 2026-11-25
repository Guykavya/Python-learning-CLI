# Strip outputs before sharing

Chapter sections 2.5 and 3.4. Before a notebook goes into version control or to a colleague, its saved **outputs** and **execution counts** should be cleared: they make the diff noisy and can leak data.

Write `strip_outputs(nb)` that returns a **new** notebook dict in which:

- every code cell has `"outputs": []` and `"execution_count": None`;
- every cell's `metadata` has no `"execution"` key (the timing record some front-ends store); other metadata keys stay;
- everything else (cell order, sources, markdown cells, top-level metadata) is unchanged.

The input `nb` must **not** be changed. (This is the mutation trap of Ch. 3.4: a function that edits its argument surprises its caller.)

## Example

```python
nb = {"nbformat": 4, "nbformat_minor": 5, "metadata": {}, "cells": [
    {"cell_type": "code", "id": "a", "metadata": {"execution": {"iopub.status.busy": "t"}, "tags": ["x"]},
     "source": "1 + 1", "outputs": [{"output_type": "stream", "name": "stdout", "text": "2\n"}], "execution_count": 7}]}
clean = strip_outputs(nb)
clean["cells"][0]["outputs"]          # []
clean["cells"][0]["execution_count"]  # None
clean["cells"][0]["metadata"]         # {'tags': ['x']}
nb["cells"][0]["execution_count"]     # still 7
```
