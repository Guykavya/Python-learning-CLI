## Approach

Each line is one SQL expression whose result was measured in DuckDB 2.0.

1. 1 Jan 2025 is a Wednesday; the Monday on or before is 30 Dec 2024, so the output is `2024-12-30`.
2. `dayname` is `Wednesday`.
3. 31 March plus one month is "31 April", which does not exist: DuckDB clips to the last day of April, `2025-04-30`.
4. `date_diff('month', 31 Jan, 1 Feb)` counts month boundaries crossed: January to February is one boundary, so `1`, although only one day passed.
5. 1 Jan to 31 Jan stay in the same month: `0`.
6. 31 Jan to 1 Mar: 28 days to reach 28 Feb, plus 1, is `29`.
7. `date_trunc('month', ...)` of 28 Feb is `2025-02-01`.
8. `7 / 2` is `3.5` (true division in DuckDB), `7 // 2` is `3`: the line prints `3.5 3`.
9. `1 / 0` is `inf`, `NULLIF(0, 0)` is `NULL`, printed `None`: the line prints `inf None`.

## Check

Run the program and compare. Every line is the plain output of the code.

## Another way

For "months between two dates" that means elapsed whole months, compute `(year2 - year1) * 12 + (month2 - month1)` and subtract 1 when the day of month has not been reached yet. For cohort tables (Ch. 6), the boundary-counting `date_diff('month', ...)` is exactly what you want, because both dates are already truncated to the first of their month.
