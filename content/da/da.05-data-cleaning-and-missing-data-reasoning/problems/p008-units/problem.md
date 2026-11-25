# Units

Chapter section 3.5. Two sources report weight in different units: one in grams, one in kilograms, one in pounds.
Adding or averaging them as they are gives nonsense. The cure is to find the unit of each value, convert everything to
**one** unit, and say the unit in the column name (`weight_kg`). An unknown unit must **stop** the conversion: guessing
a factor is worse than failing.

Write `to_kg(values, units)`:

- `values` and `units` are two lists of the same length: `values[i]` is a number measured in `units[i]`.
- The known units and their factors to kilograms:

| unit | factor |
|---|---|
| `g` | 0.001 |
| `kg` | 1 |
| `lb` | 0.45359237 |

- Unit text is read **ignoring case and spaces at the ends**: `" KG "` is `kg`.
- Return a **list of floats**, the converted values, in the same order.
- A missing value (`None` or `nan`) stays `nan`.
- An **unknown unit** raises `ValueError`, and the error message must contain the unit text (stripped, as written), so
  the user can see what to add to the table. The error is raised even if the value is missing.

## Example

```python
print([round(x, 3) for x in to_kg([500, 2, 10, 1.5], ["g", "KG", " lb ", "kg"])])
try:
    to_kg([1, 2], ["kg", "stone"])
except ValueError as e:
    print(e)
```

```text
[0.5, 2.0, 4.536, 1.5]
unknown unit 'stone'
```
