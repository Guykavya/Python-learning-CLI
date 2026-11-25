## Hint 1

For each line ask two questions: what is the result **dtype** (does the scalar adapt to `uint8`, or does it force a bigger type)? And does the value fit in that dtype?

## Hint 2

```text
uint8 + python int (fits in uint8)   -> uint8, wraps silently (mod 256)
uint8 + python int (does not fit)    -> error before any arithmetic
uint8 + np.int64 scalar               -> int64 (a NumPy scalar is "strong")
uint8 + python float                  -> float64 (an integer type cannot hold .5)
float32 + python float                -> float32 (weak float adapts)
```
