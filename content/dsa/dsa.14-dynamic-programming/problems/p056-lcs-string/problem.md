# The LCS string itself

p055 returned the **length** of the longest common subsequence. Now write `lcs_string(a, b)` that returns **one** longest common subsequence as a string (chapter section 14, "Rebuilding the LCS string").

## Example

```python
>>> lcs_string("abcde", "ace")
'ace'
>>> lcs_string("AGGTAB", "GXTXAYB")
'GTAB'
>>> lcs_string("abc", "xyz")
''
>>> lcs_string("ABCBDAB", "BDCABA")     # 'BCBA', 'BDAB' or 'BCAB' are all right
'BCBA'
```

Often there are several longest common subsequences, and you may return **any** of them. So the tests do not compare your string with one fixed answer. They check that it is a subsequence of `a`, a subsequence of `b`, and that its length is the LCS length.

## Constraints

- `0 <= len(a), len(b) <= 400`.
- Time `O(len(a) * len(b))`.

## Think about

The table `f` from p055 tells you the length at every cell. Standing at `(i, j)`: when do you know that `a[i-1]` is part of the answer? When the characters differ, which neighbour still holds the same length, so that moving there loses nothing?
