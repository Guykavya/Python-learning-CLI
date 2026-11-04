## Hint 1

Keep a window `s[l..r]` that never contains a repeat, and grow it one character to the right at a time. When the
new character `s[r]` is already inside the window, the window is broken. Which characters must leave, and from
which side?

## Hint 2

Remove characters from the **left** (`l += 1`) until `s[r]` is no longer in the window. Keep the window's
characters in a set, so "is it inside?" is O(1). After adding `s[r]`, the window is valid again: compare its
length `r - l + 1` with the best. Use `>` (not `>=`) so that a tie keeps the earlier start.

## Hint 3

```
seen = empty set; l = 0; best_len = 0; best_start = 0
for r in 0..n-1:
    while s[r] in seen:
        seen.remove(s[l]); l += 1
    seen.add(s[r])
    if r - l + 1 > best_len: best_len = r - l + 1; best_start = l
print best_len, then s[best_start : best_start + best_len]
```
