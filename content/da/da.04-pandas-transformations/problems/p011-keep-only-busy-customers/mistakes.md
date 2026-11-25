- **`>` instead of `>=`.** "At least 3" includes exactly 3.
- **`value_counts()` and then indexing the counts.** That gives customer ids, not their order rows; you then need an
  `isin` step to get the rows back.
- **Filtering rows by their own value.** `orders[...]` on a row's column cannot see how many orders the customer has.
- **`reset_index()` on the result.** The task keeps the original index labels.
