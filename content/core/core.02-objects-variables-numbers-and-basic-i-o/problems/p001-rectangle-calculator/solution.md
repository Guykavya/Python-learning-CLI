## Approach

`input()` always returns a `str`. Turn it into a number with `float()`, compute,
then format with the `.2f` format spec so whole numbers still show `.00`.

## Code

```python
width = float(input())
height = float(input())
print(f"Area: {width * height:.2f}")
print(f"Perimeter: {2 * (width + height):.2f}")
```

## Why `.2f` and not `round()`

`round(4.0, 2)` gives `4.0`, which prints as `4.0`, not `4.00`. Rounding changes the
**value**; a format spec controls the **display**. Here the task is about display.

## Another way

`format(value, ".2f")` or `"%.2f" % value` do the same. f-strings are the modern, readable choice.
