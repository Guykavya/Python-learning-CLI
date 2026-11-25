- **"The merge ran without error, so it is right."** A merge never errors on lost or duplicated rows unless you ask it
  to (`validate=`).
- **Only counting rows.** Losing 3 rows and duplicating 3 others leaves the count unchanged; a total catches it.
- **Joining `returns` on `order_id` only.** A returned line is identified by order **and** product; half a key gives a
  many-to-many join.
- **Fixing a fan-out with `drop_duplicates()` after the merge.** Find the duplicated key and fix the lookup instead.
