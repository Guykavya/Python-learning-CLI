# Monthly line with honest gaps

Chapter sections 2 and 4. Riverside was closed for part of 2024. A line chart that is drawn **straight across** missing months claims sales
that never happened. A gap must look like a gap.

Write `monthly_line(df)`. `df` has columns `date` (timestamps, daily rows) and `revenue`.

1. Add up `revenue` per **month** (month start timestamps such as `2024-03-01`).
2. Build the **complete** range of months from the first to the last month in the data. A month with **no rows** has revenue `NaN`
   (not 0, not interpolated). A month that has rows keeps its sum, even if that sum is 0.
3. Draw one line of month against revenue and return the Figure. Matplotlib breaks a line at `NaN`, which is exactly the gap we want.

## Example

Rows in January, February and April give four x positions (Jan, Feb, Mar, Apr); the y value of March is `NaN`.
