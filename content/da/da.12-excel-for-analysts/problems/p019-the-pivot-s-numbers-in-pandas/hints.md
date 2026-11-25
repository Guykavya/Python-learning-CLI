## Hint 1

`pivot_table(..., fill_value=0)` removes the NaN. The margin row and column are already called "Grand Total"; how do you put everything else in case-insensitive order and the total at the end?

## Hint 2

```text
pt = orders.pivot_table(..., margins=True, margins_name="Grand Total", fill_value=0)
rows = sorted([r for r in pt.index if r != "Grand Total"], key=str.lower) + ["Grand Total"]
cols likewise; return pt.loc[rows, cols].round(2)
```
