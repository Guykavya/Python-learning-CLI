# The pivot's numbers in pandas

Chapter section 8.3. To check an Excel PivotTable you need its numbers in pandas. A pivot of **revenue by region (rows) and category (columns)** has row totals, column totals and a corner total, labelled **Grand Total**, and Excel sorts the labels **alphabetically, ignoring case**, with the totals last.

Write `pivot_expected(orders)` for a DataFrame with the columns `region`, `category` and `revenue`:

- `orders.pivot_table(index="region", columns="category", values="revenue", aggfunc="sum", margins=True, margins_name="Grand Total")` is the starting point;
- sort the **rows** and the **columns** by `str.lower()` of the label, with `Grand Total` **last** in both;
- round every value to **2 decimals**;
- a combination with no rows is `0.0` (not `NaN`).

## Example

Labels `b`, `A`, `c` give the order `A`, `b`, `c`, `Grand Total` (pandas alone would give `A`, `b`, `c` too, but `a`, `B` would be sorted after `B`: capital letters first).
