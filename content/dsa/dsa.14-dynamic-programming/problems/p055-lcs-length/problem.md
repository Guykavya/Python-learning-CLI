# LCS length

Write `lcs_length(a, b)` that returns the length of the **longest common subsequence** of the strings `a` and `b`: the longest string whose characters appear in both, in the same order, not necessarily next to each other (chapter section 14).

## Example

```python
>>> lcs_length("abcde", "ace")
3
>>> lcs_length("AGGTAB", "GXTXAYB")     # GTAB
4
>>> lcs_length("abc", "xyz")
0
>>> lcs_length("", "abc")
0
>>> lcs_length("aaaa", "aa")
2
```

## Constraints

- `0 <= len(a), len(b) <= 400`. Characters are compared exactly (`"A" != "a"`).
- Time `O(len(a) * len(b))`. A recursion without a memo is exponential.

## Think about

Look at the **last** characters `a[i-1]` and `b[j-1]` of the prefixes `a[:i]` and `b[:j]`. If they are equal, what can you do with them? If they differ, at least one of them is not in the common subsequence: which two smaller problems are left?
