## Approach

Read the numbers one by one and keep only five pieces of state:

- `prev`: the value just before the current one,
- `cur_start`, `cur_len`: the streak that ends at the current position,
- `best_start`, `best_len`: the best streak seen so far.

The first value starts a streak of length 1 at position 1. For each next value `x` at position `pos`:

1. If `x > prev`, the current streak grows: `cur_len += 1`.
2. Otherwise it breaks, and a new streak of length 1 starts at `pos`.
3. **After every number** (not only on a break), if `cur_len > best_len`, copy the current streak into
   the best. Checking every time means a streak ending at the last position is not forgotten. Using
   strictly `>` keeps the earliest streak on ties.

The end position is `best_start + best_len - 1`, so it does not need its own variable.

## Trace

Values `5 1 2 3 2 4 6 7`:

| pos | x | prev | x > prev? | cur_start | cur_len | best_start | best_len |
|---|---|---|---|---|---|---|---|
| 1 | 5 | | | 1 | 1 | 1 | 1 |
| 2 | 1 | 5 | no | 2 | 1 | 1 | 1 |
| 3 | 2 | 1 | yes | 2 | 2 | 2 | 2 |
| 4 | 3 | 2 | yes | 2 | 3 | 2 | 3 |
| 5 | 2 | 3 | no | 5 | 1 | 2 | 3 |
| 6 | 4 | 2 | yes | 5 | 2 | 2 | 3 |
| 7 | 6 | 4 | yes | 5 | 3 | 2 | 3 |
| 8 | 7 | 6 | yes | 5 | 4 | 5 | 4 |

Output: `length 4`, `from 5 to 8`.

## Code

```python
n = int(input())

prev = int(input())
cur_start = 1        # where the current streak began
cur_len = 1
best_start = 1
best_len = 1

for pos in range(2, n + 1):
    x = int(input())
    if x > prev:
        cur_len += 1
    else:
        cur_start = pos      # the streak is broken; a new one starts here
        cur_len = 1
    # Check after every number, so a streak that ends at the last position is counted.
    if cur_len > best_len:   # strictly greater: keep the earliest on ties
        best_len = cur_len
        best_start = cur_start
    prev = x

print(f"length {best_len}")
print(f"from {best_start} to {best_start + best_len - 1}")
```

## Complexity

One pass with constant work per number: O(n) time and O(1) memory. With `n = 100000` it runs in a
fraction of a second (most of the time goes into `input()`).

## Another way

**Update the best only when a streak ends, plus once after the loop.** You compare `cur_len` with the
best inside the `else` branch (before resetting), and then once more after the loop for the final streak.
It does slightly fewer comparisons but has the classic "forgot the last streak" trap, so the
check-every-time version is safer. If you were allowed to store the values, you could also try every
start position and extend it (O(n^2)), which is a good brute-force checker but far too slow for 10^5 values.

## Edge cases

- `n = 1`: the loop does not run; the answer is length 1 from 1 to 1.
- All equal or strictly decreasing: every streak has length 1; the earliest is position 1.
- The longest streak at the very end: caught because the best is updated after every number.
- Ties: strict `>` keeps the first one found.
