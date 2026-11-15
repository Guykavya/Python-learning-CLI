# Longest repeated substring

Find the length of the **longest substring that occurs at least twice** in `s` (the two occurrences may overlap).
Print `0` if no letter repeats.

Two ideas combine:

1. **Monotone**: if a substring of length `k` occurs twice, then its prefix of length `k - 1` also occurs twice. So
   "some substring of length `k` repeats" is true for small `k` and false for large `k`: **binary search** the length.
2. **Check one length in O(n)**: roll a hash over all windows of length `k` and look for a repeated hash (a set). This is the
   previous problem with a twist.

Use `B = 911382323` and `M = 2^61 - 1` and letters `a = 1, ..., z = 26`.

## Input

One line: `s`.

## Output

One integer.

## Example

Input:

```
banana
```

Output:

```
3
```

`ana` occurs at positions 1 and 3 (overlapping). No substring of length 4 occurs twice. For `abcd` the answer is `0`.

## Constraints

- `1 <= len(s) <= 100000`
