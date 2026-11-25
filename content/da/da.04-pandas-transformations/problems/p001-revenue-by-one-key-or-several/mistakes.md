- **Leaving the keys in the index.** `groupby(keys)["revenue"].sum()` is a Series with a (Multi)Index. It prints nicely
  but `result["store_id"]` fails. Use `as_index=False` or `reset_index()`.
- **`groupby(keys).sum()` on the whole frame.** It also sums `order_id`, which is a label, not a quantity, and
  it glues the text of `product_id` together (`"P1P2"`), which is meaningless. Select `["revenue"]` first.
- **Sorting by `revenue` instead of the keys.** The task asks for key order; `groupby` already gives it.
- **Turning the result into a MultiIndex frame with `[["revenue"]]` and forgetting to flatten it.**
