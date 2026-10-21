## Approach

A string's reverse is the reverse of everything after the first character, followed by that first
character. Strings of length 0 or 1 are the base case. For palindromes, clean once in the public
function, then let a recursive helper compare the outer characters and recurse on the middle.

## Code

```python
def reverse(text):
    """Return text reversed, recursively."""
    if len(text) <= 1:
        return text
    return reverse(text[1:]) + text[0]


def _check(s):
    if len(s) <= 1:
        return True
    if s[0] != s[-1]:
        return False
    return _check(s[1:-1])


def is_palindrome(text):
    """Return True if text is a palindrome ignoring case and non-alphanumerics (recursively)."""
    cleaned = "".join(ch.lower() for ch in text if ch.isalnum())
    return _check(cleaned)
```

## Complexity

Both make O(n) calls, but each slice copies the string, so O(n²) time in total and O(n) stack
depth. Fine for short strings; for long ones use slicing or two indices in a loop.

## Another way

Pass indices instead of slicing: `_check(s, lo, hi)` compares `s[lo]` and `s[hi]` and recurses on
`(lo + 1, hi - 1)`. That avoids copying, making it O(n) time.
