# Annotate the variables

`starter.py` creates seven module-level variables with no hints. Copy it to `solution.py` and add
a hint to every variable, **keeping the same values**.

| Variable | Holds |
|---|---|
| `count` | a whole number, starts at `0` |
| `price` | a decimal number, starts at `9.5` |
| `title` | text, starts as `"Report"` |
| `tags` | a list of strings, starts empty |
| `stock` | a dict from product name (text) to quantity (whole number), starts empty |
| `origin` | a pair of whole numbers `(0, 0)` |
| `nickname` | text, or nothing yet, starts as `None` |

Note that `tags` and `stock` start **empty**, so mypy could not work out their types by itself. That
is why hints on variables matter.

The tests read the hints with `typing.get_type_hints(solution)` and also check the values.

**Example**

```python
count: int = 0
nickname: str | None = None
```
