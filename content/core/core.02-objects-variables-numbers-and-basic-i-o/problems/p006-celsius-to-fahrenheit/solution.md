## Approach

Convert the text to a `float`, apply the formulas, and let the format spec decide the decimals.

## Code

```python
c = float(input())
f = c * 9 / 5 + 32
k = c + 273.15
print(f"F: {f:.1f}")
print(f"K: {k:.2f}")
```

## Why the format spec matters

`0 + 273.15` is stored as a float that is very slightly off from 273.15. Printing it with `:.2f`
always shows `273.15`. Printing the raw float could show more digits for some inputs.
`:.1f` and `:.2f` round only the **display**, never the stored value.

## Another way

`f = c * 1.8 + 32` is the same formula. `9 / 5` is exactly `1.8` as a decimal, but remember
that `1.8` itself is stored as a binary approximation.
