## Approach

Run the loop by hand. Each line shows the range before the comparison; the next range is either `mid + 1 .. hi` or `lo .. mid - 1`.

## Expected output

```text
lo 0 mid 4 hi 9 a[mid] 16
lo 5 mid 7 hi 9 a[mid] 56
lo 5 mid 5 hi 6 a[mid] 23
lo 6 mid 6 hi 6 a[mid] 38
not found, lo 7 hi 6
probes 4
```

## Why

The range starts as 0..9 (10 candidates) and shrinks to 5..9 (5), 5..6 (2), 6..6 (1), then empty: 10, 5, 2, 1, 0 candidates. That is `floor(log2(10)) + 1 = 4` probes in the worst case.
The loop ends with `lo = 7` and `hi = 6`. After a failed search `lo` is the **insertion point**: the index where 40 would have to be inserted (`a[6] = 38 < 40 < 56 = a[7]`).
