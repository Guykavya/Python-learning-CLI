# Shortest common supersequence

A **supersequence** of `a` is a string that contains `a` as a subsequence (the letters of `a` appear in it in order, not necessarily next to each other). Write `shortest_supersequence(a, b)` that returns a **shortest** string that is a supersequence of both `a` and `b`.

Several answers can be shortest. Any of them is accepted: the tests **check** your string (both `a` and `b` are subsequences of it, and its length is the shortest possible) instead of comparing it with one fixed answer.

## Example

```python
>>> shortest_supersequence("abac", "cab")      # "cabac" is another correct answer
'cabac'
>>> len(shortest_supersequence("abac", "cab"))
5
>>> shortest_supersequence("abc", "")
'abc'
>>> shortest_supersequence("abc", "abc")
'abc'
```

Check the first answer: `c a b a c` contains `a b a c` (skip the first `c`) and `c a b` (the first three letters).

## Constraints

- `0 <= len(a), len(b) <= 400`, lowercase letters.
- `O(len(a) * len(b))` time. The tests use two strings of 400 letters, so a recursion without a memo does not finish.

## Think about

Section 15 says the shortest length is `len(a) + len(b) - LCS(a, b)`: letters of the LCS are written **once**, every other letter once each. So build the LCS table of section 14 and walk back from the corner as in `lcs_string`. On a match, you write the letter once. When you step up or left, which letter do you have to write so that it is not lost? And what is left when one index reaches 0?
