## Approach

1. `s.rolling(2).mean()`: windows `[1]`, `[1, 2]`, `[2, 3]`, `[3, 4]`. The first is not full: `[nan, 1.5, 2.5, 3.5]`.
2. With `min_periods=1` the first window counts with one value: `[1.0, 1.5, 2.5, 3.5]`.
3. `t.rolling(3).sum()`: the first two windows are not full; then 10+20+30 = 60, 20+30+40 = 90, 30+40+50 = 120:
   `[nan, nan, 60.0, 90.0, 120.0]`.
4. `center=True`: row 0's window is rows −1, 0, 1 (only two exist), row 4's is rows 3, 4, 5 (only two exist):
   `[nan, 60.0, 90.0, 120.0, nan]`. Same sums, shifted one place earlier.
5. With `min_periods=1` the two partial windows are summed: 10+20 = 30 and 40+50 = 90:
   `[30.0, 60.0, 90.0, 120.0, 90.0]`.
6. The centred mean has `NaN` at the first and the last row: `2`.

## Code

The expected output is in `expected.txt`, produced by running the program with pandas 3.1.1.

## Complexity

Each rolling sum or mean is O(n): the window is updated as it slides.

## Another way

To see the windows themselves, use plain Python: `[t.tolist()[max(0, i - 2): i + 1] for i in range(5)]` lists the
trailing windows; `[t.tolist()[max(0, i - 1): i + 2] for i in range(5)]` the centred ones.
