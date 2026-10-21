# Reverse a string by recursion

Write `reverse(text)` **recursively**. Do not use `[::-1]`, `reversed` or a loop.

Then write `is_palindrome(text)`, also recursive, that returns `True` when `text` reads the same
forwards and backwards, **ignoring case and every character that is not a letter or digit**.
Clean the text once, then recurse on the cleaned string (a helper function is a good idea).

**Examples**

```python
reverse("hello")         # 'olleh'
reverse("")              # ''
reverse("a")             # 'a'
is_palindrome("Racecar")                          # True
is_palindrome("A man, a plan, a canal: Panama!")  # True
is_palindrome("hello")                            # False
is_palindrome("")                                 # True
```
