- **`drop_duplicates("order_id")` after the bad merge.** The row count looks right, but you keep an arbitrary attempt:
  order 1001 might keep its *failed* row and be reported as unpaid.
- **Dividing the total by the number of payments.** Patching the number instead of the grain; it breaks on the next
  report.
- **`validate="1:1"` on the original merge.** Good instinct: it raises `MergeError` and shows the problem. But the
  fix is still to aggregate first.
- **`how="inner"`.** Order 1004 (no payment) would vanish from the revenue.
- **Leaving `n_payments` as `NaN` or `paid` as `object`.** The report needs `0` and `False` for orders with no attempt.
