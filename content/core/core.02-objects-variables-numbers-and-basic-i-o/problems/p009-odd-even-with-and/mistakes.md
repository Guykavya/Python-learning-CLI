- Writing `n & 1 == 1`. Comparisons bind tighter than `&`, so this is `n & (1 == 1)`, which is
  `n & True`, which prints `1` or `0` instead of `True` or `False`.
- Expecting `-7 >> 1` to be `-3`. Right shift rounds toward negative infinity, just like `//`.
- Printing `n & 1` alone. It gives `1` or `0`, not a bool.
