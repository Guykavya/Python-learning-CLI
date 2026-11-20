## Hint 1

Keep the rightmost segment `[l, r)` found so far that matches a prefix: `s[l:r] == s[:r - l]`. For a position `i < r`, the character `s[i]` is a copy of `s[i - l]`, so the match at `i` is at least `min(r - i, z[i - l])`: as long as `z[i - l]`, but you only **know** the text up to `r`.

## Hint 2

Start `z[i]` from that value (or 0 if `i >= r`), then extend with fresh comparisons `s[z[i]] == s[i + z[i]]`. If `i + z[i] > r`, the new match reaches further right: make it the new box `l, r = i, i + z[i]`.

## Hint 3

```
z = [0] * n; z[0] = n; l = r = 0
for i in 1..n-1:
    if i < r: z[i] = min(r - i, z[i - l])
    while i + z[i] < n and s[z[i]] == s[i + z[i]]: z[i] += 1
    if i + z[i] > r: l, r = i, i + z[i]
```
