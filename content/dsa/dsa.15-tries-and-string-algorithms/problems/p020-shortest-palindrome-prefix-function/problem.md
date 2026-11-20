# Shortest palindrome (prefix function)

You may add characters **only at the front** of `s`. Write `shortest_palindrome(s)` that returns the shortest palindrome you can make this way (chapter section 11, "Shortest palindrome by adding letters in front").

Here `s` may contain **any** characters, including `#`. The chapter's trick `s + "#" + reversed(s)` is therefore not safe as written: find a separator that cannot appear in `s`.

## Example

```python
>>> shortest_palindrome("aacecaaa")
'aaacecaaa'
>>> shortest_palindrome("abcd")
'dcbabcd'
>>> shortest_palindrome("aba")
'aba'
>>> shortest_palindrome("#a")         # with a '#' separator the chapter's code returns '#a'
'a#a'
>>> shortest_palindrome("")
''
```

## Constraints

- `0 <= len(s) <= 3 * 10**5`; any characters.
- `O(n)`. Checking every prefix for being a palindrome is `O(n**2)`.

## Think about

1. Why is the answer "the reverse of what is left after the **longest palindromic prefix**, then `s`"?
2. Why is the longest palindromic prefix of `s` a border of `s + sep + reversed(s)`?
3. With `s = "#a"` and the separator `#`, which border of `#a#a#` crosses the separator, and why is that wrong?
4. How can you build a sequence whose separator is guaranteed not to occur in `s`? (Hint: the prefix function works on any list, not only on strings.)
