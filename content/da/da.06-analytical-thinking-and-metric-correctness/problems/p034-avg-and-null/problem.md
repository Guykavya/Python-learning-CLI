# AVG and NULL

Chapter section 10.4. In SQL, `AVG(x)` is `SUM(x) / COUNT(x)`: it **skips NULL**, exactly as `Series.mean()` skips
`NaN`. When `NULL` means "this job was not rated", skipping is what we want. Replacing `NULL` by `0` with
`COALESCE(rating, 0)` is the classic mistake: a missing rating becomes a rating of zero.

The table `visits` has one row per visit of a technician to a job:

```text
visits(visit_id INTEGER, technician TEXT, rating INTEGER)      rating is 1 to 5, or NULL when the customer gave none
```

In `solution.py`, define `QUERY`, one `SELECT` that returns **one row per technician**, sorted by `technician`, with
the columns

1. `technician`
2. `rated`: how many visits have a rating
3. `avg_rating`: the average rating of the **rated** visits, rounded to 2 decimals with `ROUND(..., 2)`;
   `NULL` for a technician with no rated visit at all (do **not** turn it into 0)

## Example

```sql
CREATE TABLE visits (visit_id INTEGER, technician TEXT, rating INTEGER);
INSERT INTO visits VALUES (1, 'Asha', 5), (2, 'Asha', NULL), (3, 'Asha', NULL), (4, 'Bala', 4), (5, 'Bala', 2);
```

The result is two rows: `('Asha', 1, 5.0)` and `('Bala', 2, 3.0)`. With `COALESCE(rating, 0)` Asha would get
`1.67`, a technician who looks bad because customers did not answer.
