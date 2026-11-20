# Fenwick tree: update and prefix sum

Write the Fenwick tree (binary indexed tree) of chapter section 10. The **public** interface is **0-indexed and half-open**, like the rest of this module; inside, the tree is **1-indexed**.

- `Fenwick(n)`: `n` zeros; `self.t` is a list of `n + 1` numbers and `t[0]` is never used;
- `add(i, v)`: `a[i] += v` (0-indexed `i`);
- `prefix(r)`: the sum of `a[0:r]`, the first `r` elements (`prefix(0)` is 0).

Cell `t[k]` (for `k >= 1`) must hold the sum of the `lowbit(k) = k & -k` elements that end at 1-indexed position `k`. The tests look at `t`.

## Example

```python
>>> fw = Fenwick(8)
>>> for i, x in enumerate([5, 3, 8, 6, 2, 7, 4, 1]):
...     fw.add(i, x)
>>> fw.t[1:]
[5, 8, 8, 22, 2, 9, 4, 36]
>>> fw.prefix(8), fw.prefix(4), fw.prefix(0)
(36, 22, 0)
>>> fw.add(3, 94)
>>> fw.t[1:], fw.prefix(5)
([5, 8, 8, 116, 2, 9, 4, 130], 118)
```

## Constraints

- `n` up to 2 * 10**5; up to 2 * 10**5 operations, each `O(log n)`.

## Think about

1. Which cells contain 1-indexed position `k`? How do you get from one to the next?
2. Which cells tile the prefix `1..k`, and how do you get from one to the next?
3. What happens to `k += k & -k` when `k = 0`? Why does the class add 1 to the user's index?
