# Split array largest sum

Split the list `a` into exactly `m` **non-empty contiguous pieces** (you cannot reorder or skip elements). The *cost* of a split is the largest piece sum. Print the **smallest possible cost**.

This is the same idea as shipping packages, with a twist: here the number of pieces must be exactly `m`. Think about why "at most `m` pieces with every sum `<= S`" gives the same answer as "exactly `m` pieces", when `m <= n` (you can always cut a piece into smaller ones without making the maximum bigger).
Check for a limit `S`: scan left to right, add to the current piece while the sum stays `<= S`, otherwise start a new piece. Count the pieces; `S` works if the count is `<= m`.

## Input

- Line 1: `n m`.
- Line 2: `n` integers.

## Output

One integer.

## Constraints

- `1 <= m <= n <= 100000`
- `0 <= a[i] <= 10^9` (zeros are allowed)

## Example

Input:

```
5 2
7 2 5 10 8
```

Output:

```
18
```

(Pieces `[7, 2, 5]` and `[10, 8]` give 14 and 18. Better is not possible: `[7, 2, 5, 10]` and `[8]` give 24.)
