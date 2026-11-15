## Hint 1

Split `s` into its first character and the rest. Where does the first character end up in the reversed string?

## Hint 2

`reverse(s) = reverse(s[1:]) + s[0]`. Which input stops the recursion?

## Hint 3

```
def reverse(s):
    if s == "": return ""
    return reverse(s[1:]) + s[0]
```
