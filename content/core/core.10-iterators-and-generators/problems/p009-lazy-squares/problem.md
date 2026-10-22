# lazy_squares: a generator expression

Write `lazy_squares(numbers)` in `solution.py`. It returns a **generator** (not a list) that gives
`n * n` for each `n` in `numbers`, one at a time. Use a generator expression: the same shape as a list
comprehension, but with round brackets.

The tests check that nothing is computed (and nothing is pulled from `numbers`) until you ask for values.

**Examples**

```python
g = lazy_squares([1, 2, 3])
next(g)        # 1
list(g)        # [4, 9]
sum(lazy_squares(range(4)))   # 14
```
