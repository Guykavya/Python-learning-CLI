# Extended Euclid

For non-negative integers `a` and `b`, the extended Euclid algorithm finds `g = gcd(a, b)` and integers `x`, `y` with
`a*x + b*y = g`. There are many valid pairs `(x, y)`, so to make the output exact, use **this** algorithm:

```
ext(a, b):
    if b == 0:
        return (a, 1, 0)
    (g, x1, y1) = ext(b, a % b)
    return (g, y1, x1 - (a // b) * y1)
```

Why does it work? If `b*x1 + (a % b)*y1 = g`, and `a % b = a - (a // b)*b`, then
`a*y1 + b*(x1 - (a // b)*y1) = g`.

## Input

- Line 1: `q`, the number of queries.
- Then `q` lines, each with `a` and `b`.

## Output

For each query, one line `g x y`, exactly as that algorithm returns them.

## Example

Input:

```
3
240 46
17 5
0 5
```

Output:

```
2 -9 47
1 -2 7
5 0 1
```

Check the first line: `240 * (-9) + 46 * 47 = -2160 + 2162 = 2`.

## Constraints

- `1 <= q <= 20000`
- `0 <= a, b <= 10^18`

Use `input()` without a prompt message. The recursion is only about 90 levels deep for numbers up to 10^18 (the
Fibonacci numbers are the worst case), so recursion is safe here. You may also write the loop version, which must
give the same numbers.
