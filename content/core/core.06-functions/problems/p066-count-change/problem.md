# Ways to make change

Write `count_ways(amount, coins)` that returns how many different ways `amount` can be made from
the coin values in `coins`, using each coin value any number of times. Order does not matter:
`1+2` and `2+1` are the same way.

- `count_ways(0, coins)` is `1` (the empty way).
- No coins and a positive amount: `0`.
- The list `coins` must not change.
- It must be fast: `count_ways(500, [1, 2, 5, 10, 20, 50, 100, 200])` must finish in well under a
  second. Use recursion **with memoisation**, and keep the memo **inside one call** of
  `count_ways` (for example in a dict used by an inner function), never in a default argument.

**Examples**

```python
count_ways(4, [1, 2])          # 3   (1+1+1+1, 1+1+2, 2+2)
count_ways(5, [1, 2, 5])       # 4
count_ways(3, [2])             # 0
count_ways(0, [7])             # 1
count_ways(200, [1, 2, 5, 10, 20, 50, 100, 200])   # 73682
```
