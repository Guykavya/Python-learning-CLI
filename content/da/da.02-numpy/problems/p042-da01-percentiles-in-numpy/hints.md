## Hint 1

Ch. 14.2 says which NumPy method equals `statistics`' `"inclusive"`, and which one equals its default `"exclusive"`. For nearest rank, list the candidates that always return a data value (`lower`, `higher`, `nearest`, `inverted_cdf`, ...) and try each one on `[10, 20, 30, 40]` at `p = 25, 30, 50, 51`. Compare with the rank rule by hand.

## Hint 2

A dict from the da.01 name to the NumPy name keeps the function short. The exclusive check needs no NumPy: compute the position `(n + 1) * p / 100` yourself before calling `np.percentile`.

## Hint 3

```text
NAMES = {"inclusive": "linear", "exclusive": "weibull", "nearest_rank": <your finding>}
x = float array; empty -> ValueError; p outside [0, 100] -> ValueError
method not in NAMES -> ValueError naming it
exclusive: pos = (n + 1) * p / 100; pos < 1 or pos > n -> ValueError
return float(np.percentile(x, p, method=NAMES[method]))
```
