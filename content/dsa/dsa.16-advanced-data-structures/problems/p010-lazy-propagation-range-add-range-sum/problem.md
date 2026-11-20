# Lazy propagation: range add, range sum

A game gives bonus points to whole groups of ranked players at once ("+5 to ranks 100 to 400") and asks for the total points of a group of ranks. Write `LazySum` (chapter section 8). Ranges are **half-open and 0-indexed**.

- `LazySum(a)`;
- `add(l, r, v)`: add `v` to every element of `a[l:r]`;
- `query(l, r)`: the sum of `a[l:r]` (0 for an empty range).

Both must be `O(log n)`, also when the range is long.

## Example

```python
>>> lz = LazySum([5, 3, 8, 6, 2, 7, 4, 1])
>>> lz.query(0, 8), lz.query(2, 7)
(36, 27)
>>> lz.add(1, 6, 10)
>>> lz.query(0, 8), lz.query(2, 7), lz.query(0, 1), lz.query(5, 6)
(86, 67, 5, 17)
>>> lz.add(0, 8, -1)
>>> lz.query(0, 8), lz.query(3, 4)
(78, 15)
```

## Constraints

- Up to 10**5 elements and 10**5 operations, values and additions up to 10**9 in size (Python integers do not overflow).
- The tests compare with a plain list on 2,000 random operations, then time 10**5 operations on long ranges, where a point update per element is far too slow.

## Think about

1. When `add` covers a node completely, how does the node's sum change, and why can you stop there?
2. What is the lazy tag, and what does it promise about the node's own sum and about its children's sums?
3. Which operations must **push** the tag down, and when exactly: before or after visiting the children?
