- **`on="store_id"`.** Every sales day meets every target day of its store: the row count grows (fan-out) and the
  table gets `date_x` and `date_y`.
- **`how="inner"`.** Days without a target disappear from the sales report.
- **Filling missing targets with 0.** Then every day without a target counts as a hit.
- **Comparing text dates with datetimes.** Both tables must use the same type for `date`, or nothing matches (Ch. 6.9).
