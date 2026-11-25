## Approach

The five observed values are 4, 8, 6, 10, 2: sum 30, mean 6, squared distances from 6 are 4, 4, 0, 16, 16 (sum 40).

1. `dropna`: 5 values, mean 6.00, std = sqrt(40 / 4) = sqrt(10) = 3.16.
2. fill with the mean (6): 8 values, mean still 6.00; the three new values are at distance 0, so the sum of squares
   stays 40 but is divided by 7: sqrt(40 / 7) = sqrt(5.714) = 2.39. The spread **shrank**.
3. fill with zero: 8 values with sum 30, mean 30 / 8 = 3.75. Squared distances from 3.75:
   .0625, 14.0625, 18.0625, 5.0625, 14.0625, 39.0625, 3.0625, 14.0625 -> sum 107.5; std = sqrt(107.5 / 7) = 3.92.
   The mean **dropped** by more than a third and the spread **grew**, because the zeros are far from the real values.
4. `v.count()` is 5 (non-missing), `len(v)` is 8.

## Output

```text
dropna 5 6.00 3.16
mean 8 6.00 2.39
zero 8 3.75 3.92
5 8
```

(Hand-traced first, then run on pandas 3.1.1: both agree.)

## Another way

Check your arithmetic with a tiny helper in the terminal. For the real work: a zero is a claim ("the true value is
0"). Use it only when zero is true (a product that was not sold), never as a neutral placeholder.
