## Approach

Keep four zones at all times:

```
[ 0 0 0 | 1 1 1 | ? ? ? ? | 2 2 2 ]
  0..low-1  low..mid-1  mid..high  high+1..n-1
```

Each step looks at the first unknown value `a[mid]` and puts it in its zone:

- a `0` is swapped to position `low`. What comes back from `low` is a `1` (or, at the start, the same `0`), which is
  already sorted, so `mid` moves on too.
- a `1` is already in the right zone: `mid += 1`.
- a `2` is swapped to position `high`, and the 2-zone grows. What comes back from `high` is still **unknown**, so `mid`
  stays and that value is examined next.

The loop ends when the unknown zone is empty (`mid > high`).

## Code

```python
n = int(input())
a = [int(x) for x in input().split()]

# a[0..low-1] are 0s, a[low..mid-1] are 1s, a[mid..high] unknown, a[high+1..n-1] are 2s.
low, mid, high = 0, 0, n - 1
while mid <= high:
    if a[mid] == 0:
        a[low], a[mid] = a[mid], a[low]
        low += 1
        mid += 1
    elif a[mid] == 1:
        mid += 1
    else:
        a[mid], a[high] = a[high], a[mid]
        high -= 1              # do NOT move mid: the value swapped in is still unknown

print(" ".join(map(str, a)))
```

The example `2 0 2 1 1 0`:

| low | mid | high | a[mid] | action | array after |
|---|---|---|---|---|---|
| 0 | 0 | 5 | 2 | swap with a[5], high = 4 | 0 0 2 1 1 2 |
| 0 | 0 | 4 | 0 | swap with a[0], low = mid = 1 | 0 0 2 1 1 2 |
| 1 | 1 | 4 | 0 | swap with a[1], low = mid = 2 | 0 0 2 1 1 2 |
| 2 | 2 | 4 | 2 | swap with a[4], high = 3 | 0 0 1 1 2 2 |
| 2 | 2 | 3 | 1 | mid = 3 | 0 0 1 1 2 2 |
| 2 | 3 | 3 | 1 | mid = 4 > high: stop | 0 0 1 1 2 2 |

## Complexity

O(n) time: each step either moves `mid` forward or `high` back, so at most `n` steps. O(1) extra memory.

## Another way

Count the 0s, 1s and 2s, then write that many of each. Also O(n), and simpler, but it rebuilds the values instead of
moving the original items. When each item is a record with a key (sort students by grade group, keeping the records),
the three-pointer partition still works and counting does not.
