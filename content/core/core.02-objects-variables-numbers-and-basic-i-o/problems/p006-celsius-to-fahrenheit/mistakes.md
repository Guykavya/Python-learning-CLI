- Using `int(input())`: `36.6` raises `ValueError: invalid literal for int() with base 10: '36.6'`.
- Writing `c * 9 / (5 + 32)` or `(c + 32) * 9 / 5`: wrong formula from wrong brackets.
- Using `round(f, 1)` and printing it: `round(212.0, 1)` prints `212.0`, but `round(273.15, 2)`
  could print `273.15` or a longer form for other values. The format spec is the reliable display tool.
