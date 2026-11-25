## Hint 1

If you know, for each key value, how many rows `a` has and how many rows `b` has, how many join rows does that value
produce? What do you do with key values that appear on one side only? How can you count rows per key value without a `groupby` surprise
with missing values?

## Hint 2

```text
count_a = how many rows of a have each key value   (a tuple of the key columns; missing -> None)
count_b = the same for b
total = sum over key values in a of count_a[value] * count_b[value]     (0 if b has none)
```

A `collections.Counter` returns 0 for a value it has not seen.
