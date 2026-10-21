## Hint 1

How is the reverse of `"hello"` related to the reverse of `"ello"`?

## Hint 2

`reverse(text) = reverse(text[1:]) + text[0]`. The base case: strings of length 0 or 1 are their own reverse.

## Hint 3

```
def _check(s):                  # s already cleaned
    if len(s) <= 1: return True
    if s[0] != s[-1]: return False
    return _check(s[1:-1])

def is_palindrome(text):
    cleaned = "".join(ch.lower() for ch in text if ch.isalnum())
    return _check(cleaned)
```
