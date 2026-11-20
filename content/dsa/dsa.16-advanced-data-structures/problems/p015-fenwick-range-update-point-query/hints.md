## Hint 1

Let `d[j]` be the total added at position `j` minus the total added at `j - 1`. A range add on `[l, r)` is two point changes: `d[l] += v` and `d[r] -= v`. The value at `i` is the original `a[i]` plus `d[0] + ... + d[i]`.

## Hint 2

So keep a Fenwick tree over `d`: range add = two `add` calls, point query = one `prefix(i + 1)` plus the original value.

## Hint 3

```
add(l, r, v): fw.add(l, v); if r < n: fw.add(r, -v)
get(i):       return base[i] + fw.prefix(i + 1)
```
