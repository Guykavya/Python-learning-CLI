## Hint 1

First take the column you filter on: `values = table[:, col]`. Then build one boolean mask per condition. How do you combine two masks with "and", and how do you flip a mask ("not")? What does `table[mask]` return when the mask has one entry per row?

## Hint 2

```text
values = table[:, col]
keep = (values >= lo) & (values <= hi)            # brackets around EACH comparison
if exclude is not None:
    keep = keep & ~(table[:, exclude] != 0)        # or: & (table[:, exclude] == 0)
return table[keep]                                # whole rows, shape (k, ncols)

outside: table[(values < lo) | (values > hi)]
```
