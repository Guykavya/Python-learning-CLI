- Believing `groupby` works like SQL `GROUP BY`. It does not sort; it only joins neighbours.
- Sorting with plain `sorted(records)` but grouping with `key=day_of`: it works here because
  lines start with the date, but sort and group should use the **same** key.
- Sorting the lines **before** removing blank lines and then calling `day_of("")`, which fails
  with `IndexError`.
- Writing `sorted(lines)` in the pipeline but still looping over the old unsorted `records`.
