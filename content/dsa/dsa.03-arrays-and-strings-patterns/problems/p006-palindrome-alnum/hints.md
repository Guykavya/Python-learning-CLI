## Hint 1

If you compare the first and last characters of `"No 'x' in Nixon"` directly you get `N` and `n`. What two things
must happen before a comparison makes sense?

## Hint 2

Move `i` right while `i < j` and `s[i]` is not alphanumeric. Do the same for `j`, moving left. Then compare
`s[i].lower()` with `s[j].lower()`. If they differ the answer is `no`; otherwise step both pointers inwards.

## Hint 3

```
i, j = 0, len(s) - 1
while i < j:
    while i < j and not s[i].isalnum(): i += 1
    while i < j and not s[j].isalnum(): j -= 1
    if s[i].lower() != s[j].lower(): answer no, stop
    i += 1; j -= 1
answer yes
```
