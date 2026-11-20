# Rod cutting

A steel rod of length `n` can be cut into pieces of whole lengths. A piece of length `k` sells for `price[k - 1]`. Write `rod_cut(price, n)` that returns the most money you can get by cutting the rod (or not cutting it at all) and selling all the pieces (chapter section 11, "Rod cutting").

## Example

```python
>>> prices = [1, 5, 8, 9, 10, 17, 17, 20]
>>> rod_cut(prices, 4)      # 2 + 2: 5 + 5 beats the whole rod (9)
10
>>> rod_cut(prices, 8)      # 2 + 6: 5 + 17 beats the whole rod (20)
22
>>> rod_cut(prices, 1)
1
>>> rod_cut(prices, 0)      # no rod, no money
0
```

## Constraints

- `0 <= n <= len(price) <= 3000`; prices from 0 to 10**6.
- `O(n**2)` time.

## Think about

1. Where is the **first** cut? If the first piece has length `k`, what is left, and what is the best you can do with it?
2. This is an unbounded knapsack (p038). What are the items, their weights and their values?
3. Why does a plain recursion "try every first piece, then recurse" take exponential time?
