# Minimum days to make bouquets

A garden has `n` flowers in a row. Flower `i` blooms on day `bloom[i]` and stays bloomed afterwards. A bouquet needs `k` **adjacent** bloomed flowers, and each flower can be used in only one bouquet.
Print the **smallest day** on which you can make at least `m` bouquets, or `-1` if it is impossible (not enough flowers: `m * k > n`).

On day `d` the bloomed flowers are those with `bloom[i] <= d`. Count greedily: walk left to right, count the current run of bloomed flowers, and every time the run reaches `k` make a bouquet and restart the run at 0. A flower that has not bloomed also resets the run.
More days never reduces the number of bouquets, so the predicate is monotone.

## Input

- Line 1: `n m k`.
- Line 2: `n` bloom days.

## Output

One integer: the minimum day, or `-1`.

## Constraints

- `1 <= n <= 100000`, `1 <= m, k`, `m * k <= 10^10`
- `1 <= bloom[i] <= 10^9`

## Example

Input:

```
5 3 1
1 10 3 10 2
```

Output:

```
3
```

(On day 3 the flowers with days 1, 3 and 2 have bloomed: three single-flower bouquets. On day 2 only two flowers are ready.)
