## Approach

Line 1: the eight values add to 25+31-1+40+999+30+35+33 = 1192, so the mean is 1192 / 8 = 149.0. Sorted, the values are
-1, 25, 30, 31, 33, 35, 40, 999; the median is the average of the 4th and 5th: (31 + 33) / 2 = 32.0.

Line 2: `isin([-1, 999])` marks two positions; `mask` turns them into `NaN`. So 2 values are missing and 6 are counted.

Line 3: without the codes the six values are 25, 31, 40, 30, 35, 33, which add to 194; 194 / 6 = 32.33 (rounded). Their
sorted order is 25, 30, 31, 33, 35, 40; the median is (31 + 33) / 2 = 32.0 again.

Line 4: a Series with `NaN` has a float dtype, so every number prints as a float, and the missing values print as `nan`.

Line 5: the largest value was 999 and is now 40.

The program prints:

```text
149.0 32.0
2 6
32.33 32.0
[25.0, 31.0, nan, 40.0, nan, 30.0, 35.0, 33.0]
999 40
```

## Complexity

Not applicable. The point: two codes out of eight moved the mean from 32.33 to 149.0 (an error of 117) and did not
move the median at all, because the median looks at the middle of the sorted values, not at how far the extremes are.

## Another way

Check your answer by running the code after writing the answer. Then change the codes to 99 and 0: the mean changes
again but the median barely does. That is why a "typical age" is better reported as the median until the codes are
removed, and why the codes must be removed before any mean is trusted.
