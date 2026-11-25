## Hint 1

Keep one row of six boxes on paper for `a`'s memory. For each new name, ask: does it point into those boxes (view), or does it get its own boxes (copy)? Only writes into `a`'s boxes change what `a.tolist()` prints.

## Hint 2

```text
s = a[1:4]        view of boxes 1..3
f = a[[0, 2]]     copy (own boxes)
r = a.reshape     view of all six boxes, read as 2 rows of 3: r[1, 0] is box 3
m = a[a > 4]      copy (own boxes)
a[mask] = 7       writes into a's boxes where the mask is True (mask computed from the CURRENT a)
```
At the end, read `s` and `r` from `a`'s final boxes.
