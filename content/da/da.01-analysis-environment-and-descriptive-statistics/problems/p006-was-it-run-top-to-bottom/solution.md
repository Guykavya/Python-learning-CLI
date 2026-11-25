## Approach

Keep the **largest** count seen so far. A cell is in order only if it beats that maximum; comparing with the previous cell alone would accept `5, 3, 4`'s last cell (4 > 3) although it was run before the cell that has count 5.

## Code

```python
def run_order_problems(nb):
    largest = 0
    bad = []
    for index, cell in enumerate(nb["cells"]):
        if cell["cell_type"] != "code":
            continue
        count = cell.get("execution_count")
        if count is None:
            bad.append(index)
        elif count <= largest:
            bad.append(index)
        else:
            largest = count
    return bad
```

## Complexity

O(number of cells), O(1) extra space besides the result.

## Another way

Compare `sorted(counts) == counts` and `None not in counts` for a yes/no answer; the running maximum is what tells you *which* cells to blame.
