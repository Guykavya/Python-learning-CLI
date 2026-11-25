## Model answer

1. **Price band: calculated column.** It is a property of one product, it does not depend on the slicers, and it must be a column to be used as a slicer or an axis. (Even better: create it in Power Query or pandas before loading.)
2. **Margin % of the report: measure.** It must be recomputed for whatever the reader selected and it is a ratio of two sums (`DIVIDE([Margin], [Revenue])`); a stored per-row ratio would not respond to slicers and its average would be wrong.
3. **Running total: measure.** It depends on the dates visible in the current filter context (the last date of the visual), so it cannot be fixed per row; it is built with a time-intelligence function such as `DATESYTD` or a `CALCULATE` over the dates up to the current one.
4. **Age group: calculated column.** It is a property of one customer, derived from the age (row context), and used as an axis or a slicer.
5. **Distinct customers who bought: measure.** `DISTINCTCOUNT` over the customers in the current filter context; distinct counts are not additive, so they cannot be stored per row or summed.
6. **Revenue per store: measure.** The numbers come from the facts in the context of each store row of the table; the store is the **axis** (a column of the store table), the revenue is the measure.

The rule: **columns slice, measures calculate**; row context for what belongs to one row, filter context for totals.

**Checklist: your answer should mention**
- [ ] price band and age group: columns (property of one row, used to slice)
- [ ] margin %, running total, distinct customers, revenue per store: measures
- [ ] a column is stored at load time with a row context; a measure is computed at query time in the filter context
- [ ] ratios and distinct counts are not additive: never stored per row
