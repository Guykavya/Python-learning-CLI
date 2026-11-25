## Approach

Relative references (`B{r}`) follow the row; the absolute reference (`$M$1`) is pasted as it is. Without the `$` signs a formula filled down would read `M2`, `M3`, ... and use empty cells.

## Code

```python
def add_margin_column(ws, n_rows, rate_cell="$M$1"):
    ws["E1"] = "margin"
    for r in range(2, n_rows + 2):
        ws[f"E{r}"] = f"=B{r}*C{r}-B{r}*D{r}*(1+{rate_cell})"
```

## Complexity

O(n_rows).

## Another way

Give the cell a **name** (`HandlingRate`) and write `(1+HandlingRate)`: no `$` to forget, and the formula explains itself (problem 8 does this for the data columns).
