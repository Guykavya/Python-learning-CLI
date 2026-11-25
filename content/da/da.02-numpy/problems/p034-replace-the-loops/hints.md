## Hint 1

Apply the recipe of Ch. 12.1 to each loop. In words, what does one pass compute from one element? Which `if`/`elif` becomes `np.where` (or `np.select`), which "previous element" becomes `np.diff`, which "cap at the limit" becomes `np.clip`?

## Hint 2

`nearest_loop` has two loops: over the values and over the centres. Build the whole table of distances at once, shape `(len(values), len(centres))`, with a column of values minus a row of centres (Ch. 11.6). Along which axis do you look for the smallest distance? What does `argmin` do with ties?

## Hint 3

```text
tax_vec:     x = float array
             where(x <= 25_000, 0.0, where(x <= 75_000, (x - 25_000) * 0.10, 5_000 + (x - 75_000) * 0.30))
change_vec:  clip(diff(float array), -limit, limit)
nearest_vec: abs(v[:, None] - c[None, :]).argmin(axis=1)
```
