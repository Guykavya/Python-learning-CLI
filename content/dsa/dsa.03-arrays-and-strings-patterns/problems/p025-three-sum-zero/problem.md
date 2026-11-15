# Three numbers that sum to zero

Find every **different** triplet of values `x <= y <= z` that you can take from three different positions of
the array, with `x + y + z = 0`. Two triplets are the same when they have the same three values, even if
they come from different positions.

## Output order (exact)

- Line 1: the number of different triplets `T`.
- Then `T` lines, one triplet per line: `x y z` in non-decreasing order, separated by single spaces.
- The lines are sorted by `x`, then by `y` (as numbers, smallest first). Since `z = -x - y`, that fixes the order.

If there is no triplet, print only `0`.

## Input

- Line 1: `n`.
- Line 2: `n` integers.

## Example

Input:

```
6
-1 0 1 2 -1 -4
```

Output:

```
2
-1 -1 2
-1 0 1
```

The values `-1 0 1` can be picked in two ways (either `-1`), but it is printed once. `-1 -1 2` uses both copies
of `-1`. There is no triplet with `-4`: it would need two numbers summing to 4.

## Constraints

- `1 <= n <= 2000`
- `-10^5 <= a[i] <= 10^5`

Three nested loops are O(n^3), about 1.3 * 10^9 steps for `n = 2000`: too slow. Aim for O(n^2).
Use `input()` without a prompt message.
