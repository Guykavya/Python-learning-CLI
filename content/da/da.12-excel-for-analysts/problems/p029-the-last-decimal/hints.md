## Hint 1

`round(0.125, 2)`: 0.125 is exactly a half, so round to even gives 0.12. `round(2.5)` is 2. For 1.005 and 2.675 the stored value is slightly **below** the half. `xl_round` sees 1.005 and 2.675 as exact halves and rounds them up.

## Hint 2

`xl_round` returns floats, so `3.0` prints as `3.0`. For the last two lines: each 10.004 rounds to 10.00 (sum 40.00), while the total 40.016 rounds to 40.02.
