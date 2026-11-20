# Longest palindromic substring in O(n)

Use one Manacher array (p026, chapter section 15) to answer two kinds of questions about a long text:

- `longest_palindrome(s)`: the longest palindromic substring of `s`; if several have the longest length, the one that **starts first**. `""` for an empty string.
- `palindrome_queries(s, queries)`: `queries` is a list of pairs `(l, r)` with `0 <= l < r <= len(s)`; return a list of booleans, `True` when `s[l:r]` is a palindrome. Each query must cost `O(1)` after the `O(n)` preparation.

## Example

```python
>>> longest_palindrome("babad")          # 'aba' is as long but starts later
'bab'
>>> longest_palindrome("cbbd"), longest_palindrome("forgeeksskeegfor")
('bb', 'geeksskeeg')
>>> palindrome_queries("abacdcaba", [(0, 3), (0, 9), (1, 4), (3, 6)])
[True, True, False, True]
```

## Constraints

- `0 <= len(s) <= 2 * 10**5`; up to 2 * 10**5 queries.
- `O(n + q)`. Checking each query with `s[l:r] == s[l:r][::-1]` is `O(r - l)` per query: too slow for long ranges.

## Think about

1. If `p[i]` is the largest value, where does the palindrome start in `s`?
2. Which index of the transformed string is the centre of `s[l:r]`? (Try `s[0:3]` and `s[1:3]` by hand.)
3. Why is `s[l:r]` a palindrome exactly when the palindrome at that centre is **at least** as long as `r - l`?
4. With `max(range(len(p)), key=...)`, which index wins a tie? Is that the leftmost palindrome?
