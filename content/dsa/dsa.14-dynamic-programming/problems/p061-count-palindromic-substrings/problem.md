# Count palindromic substrings

Write `count_palindromes(s)` that returns how many **substrings** of `s` are palindromes. A substring is contiguous, and substrings at **different positions count separately**, even when they are the same text (chapter section 16).

## Example

```python
>>> count_palindromes("abc")       # "a", "b", "c"
3
>>> count_palindromes("aaa")       # "a" x3, "aa" x2, "aaa" x1
6
>>> count_palindromes("abba")      # "a", "b", "b", "a", "bb", "abba"
6
>>> count_palindromes("")
0
```

## Constraints

- `0 <= len(s) <= 2000`, any characters.
- `O(n^2)` time. Checking every substring with `s[i:j] == s[i:j][::-1]` is `O(n^3)`.
- Either method of section 16 works: the `is_pal[i][j]` table filled by length (or with `i` going down), or expanding around each of the `2n - 1` centres.

## Think about

A palindrome of length 5 centred at index `i` contains a palindrome of length 3 with the same centre. So when an expansion step succeeds, how many **new** palindromes did it find? And in the table version, which smaller cell does `is_pal[i][j]` need?
