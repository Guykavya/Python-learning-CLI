# DSU class

Write a class `DSU` (disjoint set union, also called Union-Find, chapter section 9) for the elements `0 .. n-1`. At the start every element is alone in its own group.

| Method | Returns |
|---|---|
| `DSU(n)` | a new structure with `n` groups of one element |
| `find(x)` | the **representative** (root) of `x`'s group; two elements are in the same group exactly when their roots are equal |
| `union(x, y)` | merges the groups of `x` and `y`; returns `True` if they were different groups, `False` if they were already together |
| `connected(x, y)` | `True` if `x` and `y` are in the same group |
| `count()` | the current number of groups |
| `size(x)` | the number of elements in `x`'s group |

Use both tricks of the chapter:

- **union by size**: hang the root of the smaller group under the root of the bigger one;
- **path compression**: after `find(x)` has found the root, make every element on the way point straight at it.

Write `find` with **loops**, not recursion: before compression flattens it, a path can be very long, and the tests do `100,000` unions in an order that builds long paths for a careless `union`.

## Example

```python
>>> d = DSU(5)
>>> d.union(0, 1), d.union(2, 3), d.union(1, 3)
(True, True, True)
>>> d.union(0, 2)                  # already together
False
>>> d.connected(3, 0), d.connected(4, 0)
(True, False)
>>> d.count(), d.size(2), d.size(4)
(2, 4, 1)
```

## Constraints

- `1 <= n <= 2 * 10**5`, up to `2 * 10**5` operations. Each operation must be nearly `O(1)` (amortised); one test runs 100,000 unions and 100,000 queries with a time limit.

## Think about

Which number must you look at to decide which root goes under which: the size of the **element** or the size of its **root's** group? Why must `union` call `find` first instead of just setting `parent[x] = y`?
