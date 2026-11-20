# Network delay time

A network has `n` servers numbered **`1 .. n`** (as on LeetCode, not from 0). `times` is a list of `(u, v, t)`: a signal sent from server `u` reaches server `v` after `t` milliseconds (one-way links, `t >= 0`).

A signal starts at server `k` at time 0 and spreads over all links at once. Write `network_delay_time(times, n, k)`: the time when **every** server has received the signal, or `-1` if some server never receives it.

This is the example from chapter section 10: every server receives the signal at its shortest-path distance from `k`, so the answer is the **largest** of those distances.

## Example

```python
>>> network_delay_time([(2, 1, 1), (2, 3, 1), (3, 4, 1)], 4, 2)
2
>>> network_delay_time([(1, 2, 1)], 2, 1)
1
>>> network_delay_time([(1, 2, 1)], 2, 2)
-1
```

In the first example the signal reaches 1 and 3 after 1 ms and 4 after 2 ms. In the last one, server 1 has no incoming link from 2.

## Constraints

- `1 <= n <= 10**4`, `0 <= len(times) <= 6 * 10**4`, `0 <= t <= 100`. A server may have no links at all.

## Think about

What is the answer when `n = 1`? Why must the servers without any link still be part of your distance table?
