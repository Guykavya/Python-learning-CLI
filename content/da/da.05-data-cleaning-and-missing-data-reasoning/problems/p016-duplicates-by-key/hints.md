## Hint 1

If you sort by the ordering column, where does the row you want to keep end up inside each key group? Which `keep=`
value of `drop_duplicates(subset=...)` then picks it? What does a *stable* sort promise about rows with equal sort
values, and why does that help with ties? Finally, how do you get the original order back, and how do you get the
removed rows?

## Hint 2

```text
work = df with a fresh 0..n-1 index (so positions and labels agree)
winners = labels left after: sort by order_by (stable), drop_duplicates(subset=key, keep="last")
mask = which rows of work are winners
kept    = df[mask]        # original labels, original order
removed = df[~mask]
```
`sort_values(order_by, kind="stable")` keeps equal values in their original order.
