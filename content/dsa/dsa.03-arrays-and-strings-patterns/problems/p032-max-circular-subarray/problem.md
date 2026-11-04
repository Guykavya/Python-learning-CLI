# Maximum circular subarray sum

The array is **circular**: after the last element comes the first one again. A subarray may wrap around the end,
like `a[n-2], a[n-1], a[0], a[1]`, but it may use each position at most once and must contain at least one
element. Print the largest possible sum.

## Input

- Line 1: `n`.
- Line 2: `n` integers.

## Output

One line: the maximum circular subarray sum.

## Example

Input:

```
5
5 -3 -4 2 5
```

Output:

```
12
```

The best subarray wraps: `2 5 5` (positions 4, 5, 1). It skips the middle part `-3 -4`.

## More examples

- `-3 -2 -3` gives `-2`: when every number is negative, the best is the single largest element.
- `1 -2 3 -2` gives `3`: here the best subarray does not wrap.

## Constraints

- `1 <= n <= 200000`
- `-10^4 <= a[i] <= 10^4`

Use `input()` without a prompt message.
