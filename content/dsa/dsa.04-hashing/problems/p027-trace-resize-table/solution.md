## Walkthrough

| step | key | size | count | count / size | resize? |
|---|---|---|---|---|---|
| 1 | 8 | 4 | 1 | 0.25 | no |
| 2 | 5 | 4 | 2 | 0.5 | no |
| 3 | 12 | 4 | 3 | 0.75 | no (not greater) |
| 4 | 3 | 4 | 4 | 1.0 | yes, to 8 |
| 5 | 9 | 8 | 5 | 0.625 | no |
| 6 | 20 | 8 | 6 | 0.75 | no |
| 7 | 7 | 8 | 7 | 0.875 | yes, to 16 |

Before the first resize the table is `[[8, 12], [5], [], [3]]`. Re-inserting with `% 8` gives bucket 0 for 8, bucket 4
for 12 (12 % 8 = 4), bucket 5 for 5, bucket 3 for 3. The keys 8 and 12 collided with size 4 and no longer collide with size 8.

## Output

```
4 1 [[8], [], [], []]
4 2 [[8], [5], [], []]
4 3 [[8, 12], [5], [], []]
resize to 8
8 4 [[8], [], [], [3], [12], [5], [], []]
8 5 [[8], [9], [], [3], [12], [5], [], []]
8 6 [[8], [9], [], [3], [12, 20], [5], [], []]
resize to 16
16 7 [[], [], [], [3], [20], [5], [], [7], [8], [9], [], [], [12], [], [], []]
```

## Key ideas

- Resize when the **load factor** `count / size` passes a limit; this keeps chains short on average.
- The bucket of a key depends on the size, so every key must be **rehashed** into the new table.
- Doubling means a resize is rare (4 -> 8 -> 16), so the cost of rehashing averages out to O(1) per insert (amortised).
