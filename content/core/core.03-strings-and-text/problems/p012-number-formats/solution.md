## Code

```python
x = float(input())
print(f"{x:,.2f}")
print(f"{x:.1%}")
print(f"{x:.3e}")
print(f"{x:+.1f}")
```

## Reading each spec

| Spec | Parts |
|---|---|
| `,.2f` | grouping, precision 2, fixed point |
| `.1%` | precision 1, percent (multiplies by 100) |
| `.3e` | precision 3, scientific |
| `+.1f` | sign always, precision 1, fixed point |

The order inside a spec is fixed: fill and align, sign, `#`, `0`, width, grouping, precision, type.

## Another way

`format(x, ",.2f")` gives the same text without an f-string.
