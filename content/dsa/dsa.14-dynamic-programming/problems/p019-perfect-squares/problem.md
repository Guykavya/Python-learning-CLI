# Perfect squares

Write `num_squares(n)` that returns the **fewest perfect squares** (`1, 4, 9, 16, ...`) that add up to exactly `n`. A square may be used more than once.

## Example

```python
>>> num_squares(12)       # 4 + 4 + 4 (greedy 9 + 1 + 1 + 1 uses 4)
3
>>> num_squares(13)       # 4 + 9
2
>>> num_squares(16)       # 16 itself
1
>>> num_squares(7)        # 4 + 1 + 1 + 1
4
```

## Constraints

- `1 <= n <= 10**4`.
- About `n * sqrt(n)` steps: one million for `n = 10**4`, well under a second. A recursion without a memo is exponential, and a recursion with a memo goes down by 1 at a time: 10,000 calls deep.

## Think about

This is p017 in disguise. What are the "coins"? Is the greedy rule "take the biggest square that fits" ever right? Try 12.
