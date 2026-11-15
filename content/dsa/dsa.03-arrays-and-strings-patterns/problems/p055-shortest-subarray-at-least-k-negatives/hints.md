## Hint 1

Write the prefix sums of `2 -1 2`: `0 2 1 3`. A subarray ending before index `i` and starting at `j` is good when
`P[i] - P[j] >= 3`. For `i = 3`, which `j` work? For a fixed `i`, do you want the earliest or the latest good `j`?

## Hint 2

Two kinds of useless starts:

- a start `j` that already gave a good subarray for some end `i`: later ends only make it longer, so record
  `i - j` and drop it (from the **front**);
- a start `j` with `P[j] >= P[i]` for a later index `i`: `i` is closer to every future end and has a smaller prefix,
  so `j` will never beat it (drop from the **back**).

What is left in the deque has increasing indices **and** increasing prefix values.

## Hint 3

```
P = prefix sums, P[0] = 0
dq = empty deque; best = n + 1
for i in 0..n:
    while dq and P[i] - P[dq[0]] >= k: best = min(best, i - dq.popleft())
    while dq and P[dq[-1]] >= P[i]:    dq.pop()
    dq.append(i)
print best if best <= n else -1
```
