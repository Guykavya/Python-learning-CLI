# Four lists, sum zero

Four lists `A`, `B`, `C`, `D` each have `n` integers. Count the quadruples `(i, j, k, l)` (one position from each list,
`0 <= i, j, k, l < n`) with `A[i] + B[j] + C[k] + D[l] = 0`.

Four nested loops are `n^4`. **Meet in the middle:** all sums `A[i] + B[j]` go into a dictionary (there are `n^2`),
then every `C[k] + D[l]` looks up its negation: `n^2` more steps.

## Input

- Line 1: `n`.
- Lines 2 to 5: the lists `A`, `B`, `C`, `D`, `n` integers each.

## Output

One integer: the number of quadruples.

## Example

Input:

```
2
1 2
-2 -1
-1 2
0 2
```

Output:

```
2
```

`(0, 0, 0, 1)`: `1 - 2 - 1 + 2 = 0`. `(1, 1, 0, 0)`: `2 - 1 - 1 + 0 = 0`.

## Constraints

- `1 <= n <= 500`
- `-10^6 <= value <= 10^6`
