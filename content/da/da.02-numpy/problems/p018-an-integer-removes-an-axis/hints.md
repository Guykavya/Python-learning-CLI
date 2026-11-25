## Hint 1

Go axis by axis through the shape `(3, 4, 5)`. For each position in the index: integer → drop that length; slice → keep (new length); list → replace by the list's length; `None` → insert a 1; missing at the end → keep. Where does `...` put the remaining axes?

## Hint 2

```text
a[1]          -> drop 3            -> (4, 5)
a[:, [1]]     -> keep 3, 4 -> 1, keep 5
a[..., 0]     -> ... = the first two axes, drop the last
a[:, None, :, 0] -> keep 3, insert 1, keep 4, drop 5
a[1, 2, 3]    -> drop all three: a single number has shape ()
```
