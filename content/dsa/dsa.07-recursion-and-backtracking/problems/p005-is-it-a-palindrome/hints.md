## Hint 1

When is a string surely a palindrome without looking further? (Think of length 0 and length 1.) When is it surely **not** one after looking at only two characters?

## Hint 2

Keep two indexes, `lo` from the left and `hi` from the right. If they meet or cross, everything matched.

## Hint 3

```
def check(lo, hi):
    if lo >= hi: return True
    if s[lo] != s[hi]: return False
    return check(lo + 1, hi - 1)
return check(0, len(s) - 1)
```
