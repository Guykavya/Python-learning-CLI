# Fenwick: range update, point query

A road has `n` lamp posts. Repair crews add or remove light bulbs on whole stretches of posts ("+2 bulbs on posts 10 to 40"), and an inspector asks how many bulbs one post has right now. Write `RangeAdder` (chapter section 11). Ranges are **half-open and 0-indexed**.

- `RangeAdder(a)`: start from the values `a`;
- `add(l, r, v)`: add `v` to every element of `a[l:r]` in `O(log n)`;
- `get(i)`: the current `a[i]` in `O(log n)`.

## Example

```python
>>> ra = RangeAdder([5, 3, 8, 6, 2, 7, 4, 1])
>>> ra.add(2, 6, 10)
>>> ra.add(0, 8, -1)
>>> ra.add(4, 5, 100)
>>> [ra.get(i) for i in range(8)]
[4, 2, 17, 15, 111, 16, 3, 0]
```

## Constraints

- Up to 2 * 10**5 posts and 2 * 10**5 operations, on long stretches.

## Think about

1. In a **difference array** `d`, what does "add `v` to `a[l:r]`" change? (dsa.03, section 4.)
2. How is `a[i]` recovered from `d`? Which Fenwick operation is that?
3. What do you do when `r == n`?
