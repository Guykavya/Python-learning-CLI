## Approach

Check the type of the **value** first (only strings are at risk: `-5` as a number is a number), then override the guess openpyxl made from the first character.

## Code

```python
def write_safe(ws, row, col, value):
    cell = ws.cell(row, col, value)
    if isinstance(value, str) and value[:1] in ("=", "+", "-", "@"):
        cell.data_type = "s"
    return cell
```

## Complexity

O(1).

## Another way

Prefix such text with an apostrophe or a space (`'=1+1`): it is also safe, but changes the text; marking the cell type keeps the text exactly as typed.
