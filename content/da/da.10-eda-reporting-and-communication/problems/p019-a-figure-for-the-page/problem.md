# A figure for the page

Chapter section 6.5. The finding needs one figure that shows **how much each cause contributed** to the rise, with its uncertainty. `summary` is a DataFrame indexed by cause, with the
columns `estimate`, `CI low` and `CI high` (percentage points). It also contains two rows that are not causes: `observed rise (model)` and `left unexplained`.

Write `fig_contributions(summary)` that returns a matplotlib Figure:

- drop the two non-cause rows; one **horizontal bar per cause**, sorted by estimate **ascending** (the largest ends up at the top);
- an error bar for each cause from `CI low` to `CI high` (`ax.errorbar(..., xerr=..., fmt="none")`);
- a vertical line at 0;
- x label: `Contribution to the rise in monthly churn (percentage points, 95% interval)`;
- title (left-aligned, `loc="left"`): `"{cause} explains {value:.1f} of the {total:.1f}-point rise"`, where `cause` is the cause with the **largest** estimate and `total` is the estimate of
  `observed rise (model)`.

## Example

With the chapter's numbers the title is `late deliveries explains 1.4 of the 1.4-point rise` and the bars from bottom to top are customer mix, September shift, price change, late deliveries.
