# Lazy: range assign, range sum

A hotel sets the price of whole blocks of nights at once ("nights 10 to 40 now cost 120"), sometimes to `0` for a free promotion, and asks for the total price of a stay. Write `AssignSum` (chapter section 9). Ranges are **half-open and 0-indexed**.

- `AssignSum(a)`;
- `assign(l, r, v)`: set every element of `a[l:r]` to `v`;
- `query(l, r)`: the sum of `a[l:r]`.

Both in `O(log n)`.

## Example

```python
>>> s = AssignSum([5, 3, 8, 6, 2, 7, 4, 1])
>>> s.assign(2, 6, 9)
>>> s.query(0, 8), s.query(2, 6), s.query(1, 3)
(49, 36, 12)
>>> s.assign(0, 8, 0)               # assigning ZERO is a real update
>>> s.query(0, 8)
0
>>> s.assign(3, 5, 4)
>>> s.query(0, 8), s.query(4, 5)
(8, 4)
```

## Constraints

- Up to 10**5 elements and 10**5 operations; values from `-10**9` to `10**9`, including `0`.

## Think about

1. A node gets an assignment while it still has an **older** pending assignment. Which one wins, and what does that mean for the tag?
2. What marker means "no pending assignment"? Why is `0` a bad choice, and what does `if self.tag[node]:` do with a pending `0`?
3. How does an assignment change a node's sum?
