- **Numbering in the input order.** `cumcount` follows the rows as they stand; without sorting, "1" is just the first
  row you happened to receive.
- **Returning the sorted frame from `number_orders`.** The task keeps the original order and index.
- **`cumcount()` without `+ 1`.** It starts at 0.
- **Assigning with `.values` / `.to_numpy()`.** That drops the labels and pastes the numbers in sorted order onto
  unsorted rows: every customer gets the wrong numbers.
