## Approach

A string is a palindrome if its two end characters are equal **and** the inside is a palindrome. A string of length 0 or 1 is a palindrome. Two indexes move towards each other; the recursion stops early at the first mismatch.

## Code

```python
def is_palindrome(s):
    def check(lo, hi):
        if lo >= hi:                 # 0 or 1 characters left
            return True
        if s[lo] != s[hi]:
            return False             # early exit
        return check(lo + 1, hi - 1)

    return check(0, len(s) - 1)
```

## Complexity

`O(n)` time, depth `n / 2`. The slicing version `s[0] == s[-1] and is_palindrome(s[1:-1])` is `O(n^2)` because of the copies.

## Another way

The same idea with a loop: `while lo < hi: ...`. In real code `s == s[::-1]` is the usual one-liner.
