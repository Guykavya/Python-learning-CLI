## Approach

Do not touch the array during the updates. Record only where each addition starts (`+v` at `l`) and where it stops
(`-v` at `r + 1`). A prefix sum of these marks at position `i` adds up every `v` whose range has started at or
before `i` and not yet stopped, which is exactly the total added to `i`.

## Code

```python
n = int(input())
a = [int(x) for x in input().split()]
q = int(input())

d = [0] * (n + 2)
for _ in range(q):
    l, r, v = map(int, input().split())
    d[l] += v
    d[r + 1] -= v

run = 0
for i in range(1, n + 1):
    run += d[i]
    a[i - 1] += run

print(*a)
```

## Complexity

O(n + q) time: two steps per update and one pass at the end. O(n) extra memory for `d`.

## Another way

Loop over each range and add `v` to every cell: O(n * q), fine for tiny inputs and too slow here. The difference
array is the reverse of the prefix sum: prefix sums turn "many range reads" cheap, difference arrays turn "many range
writes" cheap. The trick only works when all updates come before the reads.
