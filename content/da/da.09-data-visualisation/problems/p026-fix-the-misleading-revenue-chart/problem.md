# Fix the misleading revenue chart

Chapter section 6. The function in `starter.py` was written for a slide called "Revenue is soaring!". It draws:

- bars for **only the last 3 months** (a cherry-picked window);
- on a y axis that **starts at 95% of the smallest bar** (a truncated axis);
- with **no unit** on the y axis;
- under a title that makes a claim without a number.

Fix `revenue_chart(df)`. `df` has a `date` column (month start timestamps) and a `revenue` column (US dollars), one row per month.

1. Draw **every month** of `df` (bars or a line, your choice).
2. The y axis **starts at 0**.
3. The y label contains the unit `USD`.
4. The title states the change **from the first to the last month** in numbers that match the data: `Revenue grew 25% from Jan 2023 to Dec 2024` or
   `Revenue fell 20% from ...`. Percent is `round(abs(last / first - 1) * 100)`; use `grew` when `last >= first`, otherwise `fell`; month names as `%b %Y`.

Return the Figure.

## Example

For a table that starts at 100 000 in January 2023 and ends at 125 000 in December 2024, the title is `Revenue grew 25% from Jan 2023 to Dec 2024`.
