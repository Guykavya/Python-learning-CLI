## Hint 1

`np.percentile` accepts a list of percentiles: what does `np.percentile(x, [25, 75])` return? Once you have the two fences, how do you build **one** mask for "below the low fence OR above the high fence"?

## Hint 2

```text
x = float copy of the input
q1, q3 = np.percentile(x, [25, 75]);   iqr = q3 - q1
low, high = q1 - k*iqr, q3 + k*iqr
outside = (x < low) | (x > high)
cleaned = np.where(outside, np.median(x), x)      # a new array
return cleaned, int(outside.sum())
```
