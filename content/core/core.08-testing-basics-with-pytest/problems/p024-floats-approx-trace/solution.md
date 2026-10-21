## Walkthrough

1. `0.1 + 0.2 == 0.3` is `False`: the sum is `0.30000000000000004`.
2. The sum prints as `0.30000000000000004`.
3. The difference is about `5.5e-17`, far below `1e-9`: `True`.
4. `approx(0.3)` accepts it (difference about 5.5e-17 is within `1e-6 * 0.3`): `True`.
5. `approx` works on either side of `==`: `True`.
6. `1.0` against `approx(1.0001)`: difference `1e-4` is bigger than `1e-6 * 1.0001`: `False`.
7. With `abs=0.001` the tolerance is 0.001: `True`.
8. `100` against `approx(100.00001)`: difference `1e-5`, tolerance `1e-6 * 100.00001 = 1e-4`: `True`.
9. `round(0.30000000000000004, 2)` is `0.3`: `True`. Rounding is another way to compare, but it changes the value, so `approx` is cleaner.
10. `3 * 0.1` is `0.30000000000000004`: `False`.
11. `10 / 4` is exactly `2.5` in binary: `True`.
12. `approx(1e-12)` has an absolute tolerance of `1e-12`, so `0` is within it: `True`.

## The exact output

```text
False
0.30000000000000004
True
True
True
False
True
True
True
False
True
True
```
