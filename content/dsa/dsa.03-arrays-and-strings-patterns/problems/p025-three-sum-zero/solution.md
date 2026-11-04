## Approach

Sorting does two jobs. It turns "two values with sum `-a[i]`" into the two-pointer pair search, and it puts
equal values next to each other, so duplicates can be skipped by comparing with the neighbour.

- The outer loop fixes the smallest value of the triplet. If `a[i]` equals `a[i-1]`, every triplet starting with
  it was already found, so skip it.
- The inner two-pointer loop finds every pair to the right of `i` with sum `-a[i]`. After a match, both pointers
  move inward, and `l` skips values equal to the one just used. (`r` then meets a different partner, so it does
  not need its own skip.)

The triplets come out sorted by `x` (outer loop goes up) and then by `y` (`l` goes up), which is the required order.

## Code

```python
n = int(input())
a = sorted(int(x) for x in input().split())

triplets = []
for i in range(n - 2):
    if i > 0 and a[i] == a[i - 1]:
        continue                      # same first value as before: same triplets again
    l, r = i + 1, n - 1
    while l < r:
        s = a[i] + a[l] + a[r]
        if s < 0:
            l += 1
        elif s > 0:
            r -= 1
        else:
            triplets.append(f"{a[i]} {a[l]} {a[r]}")
            l += 1
            r -= 1
            while l < r and a[l] == a[l - 1]:
                l += 1                # skip copies of the middle value
print(len(triplets))
for t in triplets:
    print(t)
```

Example, sorted: `-4 -1 -1 0 1 2`.

- `i = 0` (`-4`): needs a pair summing to 4. The largest pair is `1 + 2 = 3`: none.
- `i = 1` (`-1`): `l` at `-1`, `r` at `2`: sum 0, record `-1 -1 2`. Move both: `l` at `0`, `r` at `1`: sum 0,
  record `-1 0 1`. The pointers cross.
- `i = 2` (`-1` again): skipped.
- `i = 3` (`0`): `1 + 2 = 3 > 0`, move `r`; the pointers meet.

## Complexity

Sorting is O(n log n). The outer loop runs `n` times and each two-pointer pass is O(n), so O(n^2) in all. Extra
memory O(1) besides the output.

## Another way

Keep a set of triplet tuples and, for each pair `i < j`, look up `-a[i] - a[j]` in a dictionary of values to
the right. That is also O(n^2) on average, but the set of tuples handles duplicates for you; you then sort the
result for the output order. It uses more memory and is usually slower than two pointers.
