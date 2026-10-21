# Best single trade

You are given the price of one share on each of `n` days. You may **buy once** and then **sell once on
a later day**. Find the largest profit (sell price minus buy price) and the days to do it.

Buying and selling on the same day is not allowed. If no trade makes money, you do not trade.

## Input

The first line is `n`. Then `n` lines follow, each with one price (a positive integer), for day 1,
day 2, ..., day `n`. Use `input()` without a prompt message.

## Output

- If a positive profit is possible, print two lines:

  ```
  profit P
  buy B sell S
  ```

  where `B < S` are day numbers counting from 1.
- Otherwise print only one line: `profit 0`.

**Ties.** If several trades give the same best profit, choose the one with the **earliest sell day**.
If that sell day can be reached from several buy days with the same lowest price, choose the
**earliest buy day**.

## Examples

Prices `7 1 5 3 6 4`:

```
profit 5
buy 2 sell 5
```

Prices `3 8 1 5` (the lowest price, day 3, comes too late to beat buying on day 1):

```
profit 5
buy 1 sell 2
```

Buying on day 3 and selling on day 4 gives only 4, so the best trade happens before the lowest price.

Prices `9 7 4 2` (falling all the time):

```
profit 0
```

## Constraints

- 1 <= n <= 100000
- 1 <= each price <= 10^9
- Time limit: 5 seconds. Trying every pair of days is about 5 billion pairs and is far too slow.

## Before you code

Think about one sell day at a time. If you sell on day `S`, which buy day is best? What single number
must you remember from all the earlier days to answer that instantly? Write your plan, including how
the two tie rules turn into `<` versus `<=` and `>` versus `>=`, as comments at the top of `solution.py`.
