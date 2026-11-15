## Hint 1

Keep `need` (counts of `t`) and `have` (counts inside the window), plus one number `missing`: how many characters
of `t`, with multiplicity, the window still lacks. When you add `s[right]`, when does `missing` go down? (Only if the
window had **fewer** of that character than needed.) The window is good exactly when `missing == 0`.

## Hint 2

When the window becomes good, it may have extra characters on the left. Shrink with `while missing == 0`: record the
window, remove `s[left]`, and if that drops `have` below `need` for that character, `missing` goes up and the loop
ends. Record only when strictly shorter, so the earliest of equal lengths stays.

## Hint 3

```
missing = len(t); left = 0; best = none
for right in 0..len(s)-1:
    ch = s[right]; have[ch] += 1
    if have[ch] <= need[ch]: missing -= 1
    while missing == 0:
        if right - left + 1 < best length: best = (left, right)
        out = s[left]; have[out] -= 1
        if have[out] < need[out]: missing += 1
        left += 1
print s[best] or -1
```
