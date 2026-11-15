## Hint 1

`type_text`: a letter is a push, `#` is a pop when the stack is not empty.

For `backspace_equal`, write a helper `next_kept(s, i)` that starts at index `i` and moves left until it stands on a letter that survives (or reaches `-1`). Keep a counter `skip` of pending backspaces: a `#` adds one; a letter with `skip > 0` is deleted and uses one up.

## Hint 2

```
def next_kept(s, i):
    skip = 0
    while i >= 0:
        if s[i] == "#": skip += 1
        elif skip: skip -= 1
        else: return i
        i -= 1
    return -1

i, j = len(a) - 1, len(b) - 1
loop:
    i = next_kept(a, i); j = next_kept(b, j)
    if i < 0 or j < 0: return i < 0 and j < 0
    if a[i] != b[j]: return False
    i -= 1; j -= 1
```
