## Hint 1

Think about how many different values an 8-byte integer can hold, and which of them could mean "no value". Is there a spare one? What does a *float* have that an integer lacks?

## Hint 2

```text
1. int64: raw bytes, every pattern is a number   -> no room for "missing"
   float64: has NaN                              -> the only NumPy type that fits
2. Int64: values + a mask of missing positions   -> stays integer, gap is <NA>
   cost: ...
3. convert before cleaning or after? what do you learn from the gaps first?
```
Write one short paragraph for each of the three questions.
