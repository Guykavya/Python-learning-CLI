# Is this coin system canonical?

A coin system is **canonical** when "largest coin first" pays **every** amount with the fewest coins (chapter section 9). US coins are canonical; `[1, 3, 4]` is not (6 = 4 + 1 + 1, but 3 + 3 is shorter). Write `is_canonical(coins)` that decides it.

Rules:

- `coins` is a list of distinct positive integers that **contains 1**, in **any order**. It may have just one coin.
- Return `True` or `False`.
- You cannot test every amount: there are infinitely many. Use the fact from chapter section 9 (Kozen and Zaks): sorted as `c1 < c2 < ... < ck`, if the system is **not** canonical, then the **smallest** amount where greedy loses is **less than `c(k-1) + ck`**, the sum of the two largest coins. So checking every amount from 1 up to `c(k-1) + ck - 1` is a complete test.
- For each amount you need the true fewest number of coins. Do not run a separate search for every amount; build **one table** `best[a]` for all amounts up to the bound, from small to large: the last coin of a best answer for `a` is some coin `c`, and what is left, `a - c`, is paid in the best way, so `best[a] = 1 + min(best[a - c])` over the coins `c <= a`.

## Example

```python
>>> is_canonical([1, 5, 10, 25])
True
>>> is_canonical([1, 3, 4])
False
>>> is_canonical([25, 1, 10])      # 30: greedy 25+1+1+1+1+1, best 10+10+10
False
>>> is_canonical([1])
True
```

## Constraints

- `1 <= len(coins) <= 10`, every coin `<= 10**4`. One test has two large coins whose first failure is above 10,000, so checking a fixed range like "up to 1000" is not enough; the bound depends on the coins.

## Think about

Where exactly does the bound end: is the amount `c(k-1) + ck` itself needed? For `[1, 3, 4]` the bound is 7 and the first failure is 6. What happens if your loop stops one amount too early?
