# Solve an equation by bisection

The function `f(x) = x^3 + x` is increasing for `x >= 0`. For each given integer `c` find the real number `x >= 0` with `f(x) = c`, and print it with exactly 6 digits after the decimal point.

For real numbers there is no "next index": halve the interval **a fixed number of times** (100 halvings shrink any starting interval of width up to `10^5` far below the precision of a float) instead of looping `while hi - lo > eps`. A loop with a too small `eps` can run forever, because near `10^5` the floats have gaps of about `10^-11` and `hi - lo` may never go below `10^-15`.

Your output is accepted if it differs from the exact value by at most `10^-5`.

## Input

- Line 1: `t`. Then `t` lines with one integer `c` each.

## Output

`t` lines, each the value of `x` with 6 decimals (for example `1.000000`).

## Constraints

- `1 <= t <= 10000`, `0 <= c <= 10^15`

## Example

Input:

```
3
0
2
10
```

Output:

```
0.000000
1.000000
2.000000
```

(`2^3 + 2 = 10`.)
