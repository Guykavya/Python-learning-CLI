# Factory machines

A factory has `n` machines. Machine `i` needs `k[i]` seconds to make **one** product, and it works without breaks, all machines in parallel. What is the **shortest time** in which the factory can make `t` products in total?

In `T` seconds machine `i` makes `T // k[i]` products, so the factory makes `sum(T // k[i])`. That is non-decreasing in `T`: a monotone predicate `made(T) >= t`.
The answer can be as large as `10^18` (for example one machine with `k = 10^9` and `t = 10^9`), so you cannot try times one by one.

## Input

- Line 1: `n t`.
- Line 2: `n` integers `k[i]`.

## Output

One integer: the minimum time.

## Constraints

- `1 <= n <= 200000`, `1 <= t <= 10^9`
- `1 <= k[i] <= 10^9`

## Example

Input:

```
3 7
3 2 5
```

Output:

```
8
```

(In 8 seconds: 8//3 + 8//2 + 8//5 = 2 + 4 + 1 = 7. In 7 seconds: 2 + 3 + 1 = 6.)
