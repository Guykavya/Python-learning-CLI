# Pair with a given sum in a sorted array

The array is sorted in non-decreasing order. Find two **different positions** `i < j` with `a[i] + a[j] == target`.

Use the standard two-pointer rule:

```
i = first position, j = last position
while i < j:
    s = a[i] + a[j]
    if s == target: found (i, j), stop
    if s < target:  i moves right   (the sum must grow)
    else:           j moves left    (the sum must shrink)
```

Print the pair this rule finds, as 1-based positions `i j`, or `-1` if there is no pair.

**Which pair, when there are several?** The rule above decides. It always finds the pair with the **smallest
possible `i`**, and for that `i`, the **largest possible `j`**. (`i` never passes a position that has a partner; `j`
only moves left past values that are too big.) Any method that gives that pair is accepted.

## Input

- Line 1: `n`.
- Line 2: `n` integers in non-decreasing order.
- Line 3: `target`.

## Output

`i j` (1-based, `i < j`) or `-1`.

## Example

Input:

```
6
1 2 4 5 7 11
9
```

Output:

```
2 5
```

`1 + 11 = 12` is too big, so `j` moves left. `1 + 7 = 8` is too small, so `i` moves right. `2 + 7 = 9`: found at
positions 2 and 5. (The pair `4 + 5` also sums to 9, but the rule finds `2 + 7` first.)

## Constraints

- `1 <= n <= 200000`
- `-10^9 <= a[i], target <= 2 * 10^9`
