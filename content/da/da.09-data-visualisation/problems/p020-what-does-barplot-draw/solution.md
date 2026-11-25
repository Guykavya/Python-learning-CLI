## Approach

The bars are `tea = (2+4+6)/3 = 4`, `espresso = 12`, `pastry = (6+10)/2 = 8`, in first-appearance order. `errorbar=None` removes the interval lines, so `ax.lines` is empty (0).
The mean of the **rows** is `40 / 6 = 6.67`; the mean of the **bars** is `(4 + 12 + 8) / 3 = 8.00`. The tea group has three rows and counts three times in the first mean but once in the second.

## Code

```text
[4.0, 12.0, 8.0]
['tea', 'espresso', 'pastry']
0
6.67
8.00
```

## Complexity

Not applicable (a trace problem).

## Another way

`df.groupby("g", sort=False)["v"].mean()` computes the same bar heights, and is how you check any seaborn summary by hand.
