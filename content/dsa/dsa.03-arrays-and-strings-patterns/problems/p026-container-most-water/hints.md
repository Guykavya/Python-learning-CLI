## Hint 1

Start with the widest container: the first and the last wall. Any other container is narrower. To have a
chance of beating the current area, what must a narrower container have?

## Hint 2

Say `h[l] < h[r]`. Every container that keeps wall `l` and uses a wall to the left of `r` is narrower **and** still
limited by `h[l]` (or something lower). So none of them can beat `min(h[l], h[r]) * (r - l)`. Wall `l` is finished:
move `l` inward. Which wall do you move when the heights are equal?

## Hint 3

```
l, r = 0, n - 1; best = 0
while l < r:
    best = max(best, min(h[l], h[r]) * (r - l))
    if h[l] < h[r]: l += 1
    else: r -= 1
print best
```
