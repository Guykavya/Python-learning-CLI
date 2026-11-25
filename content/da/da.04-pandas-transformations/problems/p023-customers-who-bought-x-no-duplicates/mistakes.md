- **Merging customers with all their lines.** Every purchase becomes a row: C3 appears three times, and order columns
  come along.
- **`drop_duplicates()` on the merged result without choosing columns.** Two lines with different `qty` are not
  duplicates, so repeats survive.
- **Starting from the lines.** `lines[lines["product_id"] == "P7"]` gives purchases, not customers; C9 (unknown) would
  appear and city and segment would be missing.
