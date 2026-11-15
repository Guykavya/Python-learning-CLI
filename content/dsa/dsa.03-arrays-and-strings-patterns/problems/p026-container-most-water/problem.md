# Container with the most water

`n` vertical walls stand at positions `1, 2, ..., n`; wall `i` has height `h[i]`. Pick two walls `i < j`. Together
with the ground they hold water up to the **shorter** wall, so the container holds

```
min(h[i], h[j]) * (j - i)
```

units (the walls themselves have no thickness, and the walls between `i` and `j` do not matter). Print the
largest amount any pair of walls can hold.

## Input

- Line 1: `n`.
- Line 2: `n` integers, the heights.

## Output

One line: the largest area.

## Example

Input:

```
9
1 8 6 2 5 4 8 3 7
```

Output:

```
49
```

Walls 2 (height 8) and 9 (height 7): `min(8, 7) * (9 - 2) = 7 * 7 = 49`.

## Constraints

- `2 <= n <= 200000`
- `0 <= h[i] <= 10000`

Trying every pair is O(n^2): too slow for `n = 200000`. Use `input()` without a prompt message.
