# K-th smallest with a Fenwick tree

A ticket queue keeps the waiting times (whole minutes from `0` to `m - 1`) of the customers in line. Customers join and leave, and the manager asks for the median and other order statistics. Write `MinuteBag` (chapter section 13):

- `MinuteBag(m)`: an empty multiset of values in `0 .. m - 1`;
- `insert(v)`: add one copy of `v`;
- `remove(v)`: remove one copy of `v`; return `True`, or `False` (and change nothing) if there is no copy;
- `size()`: how many values are stored;
- `kth(k)`: the `k`-th smallest stored value (`k = 1` is the smallest), or `-1` if `k < 1` or `k > size()`.

`kth` must use the **binary descent** over the Fenwick tree: `O(log m)`, not a binary search with a `prefix` call per step.

## Example

```python
>>> bag = MinuteBag(10)
>>> for v in (7, 3, 3, 9, 1, 3, 7):
...     bag.insert(v)
>>> [bag.kth(k) for k in range(1, 8)], bag.kth(8), bag.kth(0)
([1, 3, 3, 3, 7, 7, 9], -1, -1)
>>> bag.remove(3), bag.remove(3), bag.remove(5)
(True, True, False)
>>> [bag.kth(k) for k in range(1, 6)], bag.size()
([1, 3, 7, 7, 9], 5)
```

## Constraints

- `1 <= m <= 10**6` (not only powers of two); up to 2 * 10**5 operations.

## Think about

1. In the descent, why does the cell `t[pos + pw]` cover exactly the positions `pos + 1 .. pos + pw`?
2. When do you move `pos` forward, and what happens to `k`?
3. How do you know whether a copy of `v` exists before removing it?
