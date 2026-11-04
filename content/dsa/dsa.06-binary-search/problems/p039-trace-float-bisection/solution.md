## Approach

Square each `mid` by hand (1.5 * 1.5 = 2.25 >= 2, so `hi` moves; 1.25 * 1.25 = 1.5625 < 2, so `lo` moves).

## Expected output

```text
1 1.0 1.5 0.5
2 1.25 1.5 0.25
3 1.375 1.5 0.125
4 1.375 1.4375 0.0625
5 1.40625 1.4375 0.03125
6 1.40625 1.421875 0.015625
estimate 1.4140625
true value 1.4142135623730951
```

## Why

Step 1: `mid = 1.5`, `2.25 >= 2` so `hi = 1.5`. Step 2: `mid = 1.25`, `1.5625 < 2` so `lo = 1.25`. Step 3: `mid = 1.375`, `1.890625 < 2`, `lo = 1.375`. Step 4: `mid = 1.4375`, `2.066... >= 2`, `hi = 1.4375`. Step 5: `mid = 1.40625`, below, so `lo`. Step 6: `mid = 1.421875`, above, so `hi`.
Every step halves the width: 0.5, 0.25, ..., 0.015625 = 1/64. After 20 steps the width is `2^-20`, about `10^-6`.
For real numbers there is no gap between neighbours, so `mid + 1` would jump over the answer: the endpoints are moved to `mid`. A fixed count is safer because with a tiny `eps` the loop `while hi - lo > eps` may never finish when floats cannot get that close.
