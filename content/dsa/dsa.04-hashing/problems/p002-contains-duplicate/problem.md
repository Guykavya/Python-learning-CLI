# Does any value repeat?

Given `n` integers, print `YES` if some value appears **at least twice**, and `NO` if all values are different.

The obvious program compares every pair: two nested loops, `n^2 / 2` comparisons. With `n = 200000` that is
2 * 10^10 steps. A **set** answers "have I seen this value before?" in O(1) on average, so one pass is enough.

## Input

- Line 1: `n`.
- Line 2: `n` integers (an empty line when `n = 0`).

## Output

`YES` or `NO`.

## Example

Input:

```
5
4 8 15 8 23
```

Output:

```
YES
```

`8` appears twice. With `4 8 15 16 23` the answer is `NO`. With `n = 0` the answer is `NO`.

## Constraints

- `0 <= n <= 200000`
- `-10^9 <= a[i] <= 10^9`
