# Money in paise, not floats

Chapter section 3.6: never store money as a float. `0.1 + 0.2` is `0.30000000000000004` in binary floating point, and sums of such errors reach the bill. Store **integer paise** (1 rupee = 100 paise). Write

```python
to_paise(text)        # "12.30" -> 1230
order_total(lines)    # lines: list of (qty, unit_paise) -> total in paise (an int)
```

`to_paise` rules:

- Parse the text with `decimal.Decimal` (never `float`). Surrounding spaces are ignored. `"1299"` is `129900`.
- Round to a whole paisa with **half away from zero** (`ROUND_HALF_UP` in `decimal`): `"12.345"` is `1235`, `"0.005"` is `1`, `"-1.005"` is `-101`.
- Text that is not a number (`""`, `"abc"`, `"1,5"`, `"nan"`, `"inf"`) raises `ValueError`.

`order_total` adds `qty * unit_paise` for every line; an empty list gives `0`.

## Example

```python
to_paise("12.30")                       # 1230
to_paise("0.10") + to_paise("0.20")     # 30  == to_paise("0.30")
order_total([(2, 25000), (1, 30000)])   # 80000
```
