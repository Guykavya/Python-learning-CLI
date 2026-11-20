# Longest palindromic subsequence

A **subsequence** keeps some letters of `s` in their order, possibly with gaps (`"bbbb"` is a subsequence of `"bbbab"`; `"ace"` is a subsequence of `"abcde"`). Write `longest_pal_subseq(s)` that returns a **longest subsequence of `s` that is a palindrome**, as a string.

Chapter section 17 computes only the length. Here you also rebuild the string from the table (chapter section 9: reconstruction).

## Example

```python
>>> longest_pal_subseq("bbbab")
'bbbb'
>>> longest_pal_subseq("character")     # also 'carac'
'carac'
>>> longest_pal_subseq("cbbd")
'bb'
>>> longest_pal_subseq("")
''
```

When several palindromes have the longest length, any one of them is accepted. The tests check that your string is a palindrome, is a subsequence of `s`, and has the right length.

## Constraints

- `0 <= len(s) <= 1000`, lowercase letters.
- `O(n**2)` time and memory.

## Think about

1. `f(i, j)` = the length of the longest palindromic subsequence of `s[i..j]`. If `s[i] == s[j]`, why is it always safe to use both ends?
2. Which order fills the table, so that `f(i + 1, j - 1)`, `f(i + 1, j)` and `f(i, j - 1)` are ready when `f(i, j)` needs them?
3. To rebuild the string, start at `(0, n - 1)`. When the ends match, where do the two letters go? When they do not, which way do you move? What happens when `i == j` in the middle?
