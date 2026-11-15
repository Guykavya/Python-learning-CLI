# Minimum arrows to burst balloons

Each balloon covers the **closed** interval `[xs, xe]` on a line. One arrow shot straight up at position `x` bursts every balloon with `xs <= x <= xe`
(balloons that only touch at `x` are burst too). Print the **minimum number of arrows** needed to burst all balloons.

## Input

- Line 1: `n`.
- Next `n` lines: `xs xe`.

## Output

One integer.

## Constraints

- `0 <= n <= 200000`
- `-10^9 <= xs <= xe <= 10^9`

Hint: **sort by right end**, then be greedy. The first arrow should go as far right as it can while still bursting the balloon that ends first.

## Example 1

Input:

```
4
10 16
2 8
1 6
7 12
```

Output:

```
2
```

## Example 2

Input:

```
2
1 2
2 3
```

Output:

```
1
```
