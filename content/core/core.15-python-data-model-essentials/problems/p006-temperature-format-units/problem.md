# Temperature with unit format specs

Build a small spec language for temperatures. A spec is an optional precision `.N` followed by an
optional unit letter `C`, `F` or `K`.

Write `Temperature(celsius)` in `solution.py` (the value is always stored in Celsius):

- `format(t, spec)` returns `"<number> <unit>"`, for example `"100.0 C"`.
- The unit defaults to `C`; the precision defaults to `.1`.
- `F` converts with `c * 9 / 5 + 32`; `K` with `c + 273.15`.
- Valid specs: `""`, `"C"`, `"F"`, `"K"`, `".2"`, `".0F"`, `".2K"` and so on.
- Anything else (like `"X"`, `"2F"`, `"F.2"`) raises `ValueError`.
- `repr(t)` is `Temperature(100)`.

**Example**

```python
t = Temperature(100)
print(f"{t}")        # 100.0 C
print(f"{t:F}")      # 212.0 F
print(f"{t:.2K}")    # 373.15 K
print(f"{t:.0F}")    # 212 F
```
