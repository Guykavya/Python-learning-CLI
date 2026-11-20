# Longest palindromic substring

Write two functions that both return the **longest contiguous substring** of `s` that is a palindrome (chapter section 16):

1. `longest_pal_dp(s)` with the table `is_pal[i][j]`, filled by length;
2. `longest_pal_expand(s)` by expanding around every centre, with no table.

If several substrings have the longest length, return the one that **starts first** (leftmost). The empty string gives `""`.

## Example

```python
>>> longest_pal_dp("babad"), longest_pal_expand("babad")    # "aba" is as long, but starts later
('bab', 'bab')
>>> longest_pal_expand("cbbd")                              # even length: the centre is a gap
'bb'
>>> longest_pal_expand("forgeeksskeegfor")
'geeksskeeg'
>>> longest_pal_dp("abc")                                   # every single letter is a palindrome
'a'
```

## Constraints

- `0 <= len(s) <= 3000`, any characters.
- `O(n**2)` time for both. `longest_pal_expand` uses `O(1)` extra memory; the table needs `O(n**2)`.

## Think about

1. In the table, `is_pal[i][j]` depends on `is_pal[i + 1][j - 1]`. Why can't you fill it row by row from the top?
2. A palindrome has a centre. How many centres does a string of length `n` have, counting the gaps between letters?
3. For the tie rule: in which order do your loops meet two palindromes of the same length? Do you need `>` or `>=` when you compare with the best so far?
4. On the string `"aaaa...a"` (3000 letters), which of the two methods does more work? And on a random string?
