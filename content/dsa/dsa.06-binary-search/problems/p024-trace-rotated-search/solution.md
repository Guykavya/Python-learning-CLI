## Approach

At each step find the sorted half, test the target against its bounds, then move `lo` or `hi` past `mid`.

## Expected output

```text
mid 3 a[mid] 15 left half sorted -> lo 4 hi 7
mid 5 a[mid] 2 right half sorted -> lo 6 hi 7
lo 6 mid 6 hi 7 found
```

## Why

Step 1: `lo = 0`, `hi = 7`, `mid = 3`, `a[3] = 15`. `a[0] = 6 <= 15`, so the left half is sorted. `6 <= 3 < 15` is False, so 3 is not in it: `lo = 4`.
Step 2: `lo = 4`, `hi = 7`, `mid = 5`, `a[5] = 2`. `a[4] = 19 > 2`, so the right half `[2, 3, 4]` is the sorted one. `2 < 3 <= 4` is True, so `lo = 6`.
Step 3: `lo = 6`, `hi = 7`, `mid = 6`, `a[6] = 3`: found. Three probes for eight elements.
