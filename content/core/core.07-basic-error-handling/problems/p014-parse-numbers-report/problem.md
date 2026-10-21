# Parse a batch and report every problem

A user pasted a list of readings. Write `parse_numbers(items)` that returns a tuple
`(numbers, errors)`:

- `numbers`: every item that `float()` can convert **and** that is a finite number, as floats,
  in order.
- `errors`: one message per bad item, in order, using the item's position counted **from 1**:
  - not convertible: `"item <n>: <item!r> is not a number"`
  - converts, but is `nan` or infinite: `"item <n>: <item!r> is not a finite number"`
    (`float("nan")` and `float("inf")` work, but such values break averages; `math.isfinite`
    tells you).

One bad item must not stop the rest (section 16). If an item is not text at all (for example
`None`), `float` raises `TypeError`: that is a bug in the caller, so let it propagate.

**Example**

```python
parse_numbers(["3.5", "abc", " 7 ", "", "nan", "-2"])
# ([3.5, 7.0, -2.0],
#  ["item 2: 'abc' is not a number",
#   "item 4: '' is not a number",
#   "item 5: 'nan' is not a finite number"])
```
