## Approach

| # | Count of body executions | Compared with `2 * 10**7` |
|---|---|---|
| 1 | `150**3 = 3,375,000` | below: `OK` |
| 2 | `10**5 * 10**5 = 10**10` | far above: `TLE` |
| 3 | `10**5 * about 17 = 1.7 * 10**6` (the `while` runs 17 times: `2**17 = 131072 >= 10**5`) | below: `OK` |
| 4 | `20000 * 20001 / 2 = 200,010,000` | 10 times above: `TLE` |
| 5 | about `n * ln ln n` is about `2.6 * 10**6` inner steps, plus `10**6` for the outer loop | below: `OK` |
| 6 | `n * ln n` with `n = 3 * 10**6` and `ln n` about 15: about `4.5 * 10**7` | above: `TLE` |

Answer:

```text
1: OK
2: TLE
3: OK
4: TLE
5: OK
6: TLE
```

Only the order of magnitude matters here; none of the programs is within a factor 2 of the limit.

## Why it matters

This is the check you make in the first minute of every problem: constraints decide the algorithm. A triangular double loop (program 4) has half the cost of a full one, which is still `10**8` for `n = 20000`: halving does not rescue a quadratic algorithm.

## Complexity

The six programs are `O(n^3)`, `O(n^2)`, `O(n log n)`, `O(n^2)`, `O(n log log n)` and `O(n log n)`.

## Another way

Time the loops with the harness of chapter section 3 on a smaller `n` and scale. The estimate is still faster than running.
