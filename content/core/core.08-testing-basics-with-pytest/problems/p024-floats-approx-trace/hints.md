## Hint 1

Evaluate each line on its own. For the first two, remember what `0.1 + 0.2` prints in Python.

## Hint 2

For `approx`, compute the difference and compare with the tolerance: `1.0` vs `1.0001` differ by `0.0001`; the default tolerance is `1e-6` of the expected value. Then try `abs=0.001`.

## Hint 3

`0 == pytest.approx(1e-12)`: the expected value is 1e-12; the default absolute tolerance is also `1e-12`, so the difference 1e-12 is within tolerance. Be careful with `3 * 0.1`.
