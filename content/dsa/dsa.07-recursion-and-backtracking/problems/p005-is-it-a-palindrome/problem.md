# Is it a palindrome?

Write `is_palindrome(s)` that returns `True` if the string `s` reads the same forwards and backwards, and `False` otherwise. Use **recursion on the two ends**: compare the first and the last character, then check the part between them.

Compare the string exactly as it is: upper and lower case are different, and spaces count like any other character.
Not allowed: `s[::-1]`, `reversed`, and loops.

## Example

```python
>>> is_palindrome("level")
True
>>> is_palindrome("abba")
True
>>> is_palindrome("abca")
False
>>> is_palindrome("Aa")
False
```

## Constraints

- `0 <= len(s) <= 1600`

## Think about

Use two indexes `lo` and `hi` instead of slicing `s[1:-1]`: then each call does `O(1)` work. Which two base cases do odd and even lengths reach?
