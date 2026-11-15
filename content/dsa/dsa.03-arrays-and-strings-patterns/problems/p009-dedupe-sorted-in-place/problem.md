# Remove duplicates from a sorted array in place

The array is sorted, so equal values sit next to each other. Remove the repeats **in place**: move the distinct
values to the front of the same list, in order, and count them. Call the count `k`. What stays in `a[k:]` does not
matter.

Use a **slow** pointer `w` (where the next distinct value will be written) and a **fast** pointer `r` (which reads
every element). When `a[r]` differs from the last value written, `a[w] = a[r]` and `w += 1`.

## Input

- Line 1: `n`.
- Line 2: `n` integers in non-decreasing order (an empty line when `n = 0`).

## Output

- Line 1: `k`.
- Line 2: the first `k` elements of the array after your loop, separated by spaces (empty when `k = 0`).

## Example

Input:

```
8
1 1 2 3 3 3 7 7
```

Output:

```
4
1 2 3 7
```

After the loop the list is `1 2 3 7 3 3 7 7`: the first 4 cells hold the answer and the rest is leftover.

## Constraints

- `0 <= n <= 200000`
- `-10^9 <= a[i] <= 10^9`
