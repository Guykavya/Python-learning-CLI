# Arbitrage? (a negative cycle in logarithms)

There are `n` currencies `0 .. n-1`. `rates` is a list of `(a, b, r)`: one unit of currency `a` buys `r` units of currency `b` (`r > 0`). Exchanges are one-way: the rate back, if there is one, is a separate entry.

**Arbitrage** is a cycle of exchanges that starts and ends in the same currency and gives back **more** than you started with: the product of the rates along the cycle is greater than 1. Write `has_arbitrage(n, rates)`: `True` if some cycle has a product greater than `1 + 1e-9`, else `False`.

Rates are floats, so a market where every cycle gives back **exactly** 1 in exact arithmetic (for example `2.0` and then `0.5`, or prices that are all consistent) may give `0.9999999999999999` or `1.0000000000000002` on a computer. Those must count as **no** arbitrage: use a tolerance. The tests never contain a cycle whose true product is between `1` and `1.001`.

## The trick

Bellman-Ford finds cycles with a negative **sum**, but here the rates are **multiplied**. Logarithms turn products into sums: `log(r1 * r2 * r3) = log r1 + log r2 + log r3`, and a product `> 1` means a log-sum `> 0`. Use the weight `-log(r)` on each edge: arbitrage is then a **negative cycle** (chapter section 12). The cycle can be anywhere, so start with distance 0 for **every** currency (as if a new source had 0-edges to all of them).

## Example

```python
>>> has_arbitrage(3, [(0, 1, 0.5), (1, 2, 4.0), (2, 0, 0.55)])
True
>>> has_arbitrage(2, [(0, 1, 2.0), (1, 0, 0.5)])
False
```

In the first market `1 -> 0.5 -> 2.0 -> 1.1` of currency 0 again: 10 % profit. In the second, `2.0 * 0.5 = 1`: no profit.

## Constraints

- `1 <= n <= 60`, `0 <= len(rates) <= 2000`, `1e-3 <= r <= 1e3`. Use `math.log` (from the standard library).

## Think about

Why `-log(r)` and not `log(r)`? Why does starting Bellman-Ford from currency 0 alone miss some markets?
