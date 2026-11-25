# Was it run top to bottom?

Chapter section 3.3. After "Restart and run all", the code cells of a notebook have `execution_count` values `1, 2, 3, ...` in page order. Anything else is a warning sign: a cell that **never ran**, or a cell run **before something above it**.

Write `run_order_problems(nb)` that returns the list of **indexes in `nb["cells"]`** (counting every cell, markdown included) of the suspicious code cells, in increasing order. A code cell is suspicious if:

- its `execution_count` is `None` (never run), or
- its `execution_count` is **not greater than the largest count seen in any earlier code cell**. (Cells that never ran add nothing to "the largest seen".)

Markdown and raw cells are never reported. A clean notebook gives `[]`.

## Example

Code-cell counts, in page order, and what you report (positions among code cells):

| counts | reported |
|---|---|
| `1, 2, 3` | none |
| `1, 3, 2` | the third cell (2 is not above 3) |
| `None, 1` | the first |
| `5, 3, 4` | the second and the third (both are below 5) |
