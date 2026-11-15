## Approach

Simulate the two loops. Pass 1 bubbles the largest value (8 is already last, 5 moves next to it). Later passes fix the next largest values.

## Expected output

```text
pass 1 [1, 4, 2, 5, 8] 3
pass 2 [1, 2, 4, 5, 8] 4
pass 3 [1, 2, 4, 5, 8] 4
pass 4 [1, 2, 4, 5, 8] 4
sorted: [1, 2, 4, 5, 8]
```

## Why

Every swap fixes exactly one inversion, so the final count equals the number of inversions in `[5, 1, 4, 2, 8]`: (5,1), (5,4), (5,2), (4,2) = 4. After pass 2 the list is already sorted; passes 3 and 4 are wasted without an early exit.
