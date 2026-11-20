# Square-root decomposition

Write `BlockSum` (chapter section 16): cut the array into blocks of size `B = max(1, math.isqrt(n))` and keep the sum of each block. Ranges are **half-open and 0-indexed**.

- `BlockSum(a)`: `self.B` is the block size, `self.blocks[b]` the sum of `a[b*B : (b+1)*B]` (the last block may be shorter);
- `update(i, v)`: `a[i] = v` in `O(1)`;
- `query(l, r)`: return a pair `(total, touched)`: the sum of `a[l:r]`, and the number of **steps** the query took, where adding one single element counts 1 and adding one whole block's sum counts 1.

`touched` makes the cost visible: it must be at most `2 * (B - 1) + n // B + 1` for every query.

## Example

```python
>>> bs = BlockSum(list(range(1, 101)))        # n = 100, B = 10
>>> bs.B, bs.blocks[:3]
(10, [55, 155, 255])
>>> bs.query(0, 100), bs.query(7, 93), bs.query(3, 5)
((5050, 10), (4343, 14), (9, 2))
>>> bs.update(50, 0)
>>> bs.query(7, 93)
(4292, 14)
```

`query(7, 93)` adds 3 single elements (7, 8, 9), 8 whole blocks (10 to 89) and 3 single elements (90, 91, 92): 14 steps instead of 86.

## Constraints

- Up to 10**5 elements and 2 * 10**4 operations.

## Think about

1. Which part of `[l, r)` can use whole blocks, and which parts must be added element by element?
2. Why is `B = sqrt(n)` a good choice? What happens to a query with `B = 1` or `B = n`?
3. How does `update` keep `blocks` correct in `O(1)`?
