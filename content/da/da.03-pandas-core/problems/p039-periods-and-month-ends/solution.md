## Approach

Take the lines one at a time.

1. `to_period("M")` turns each date into its month: `2024-01`, `2024-02`, `2023-12`.
2. `31 Jan 2024 + DateOffset(months=1)`: the month becomes February. There is no 31 February, so pandas clips to the last day, 29 February (2024 is a leap year).
3. `31 Jan + MonthEnd(1)`: 31 January **is** a month end, so `MonthEnd(1)` steps to the next one: 29 February. Same answer as line 2, for a different reason.
4. `31 Jan + MonthEnd(0)`: zero steps from a month end means stay: 31 January.
5. `15 Jan`: it is not a month end, so both `MonthEnd(1)` and `MonthEnd(0)` roll forward to 31 January.
6. `31 Mar - 1 month`: February again, clipped to 29 February.
7. `days_in_month` for February of 2024, 2023 and 2100: 29, 28, 28 (2100 is divisible by 100 but not by 400, so it is not a leap year).
8. `Period("2024-01") + 1` is the next month, `2024-02`.

## Code

The expected output is in `expected.txt`, produced by running the program above on pandas 3.1.1.

## Complexity

Every operation is vectorised or a single call. The result of calendar arithmetic depends on the calendar, not on the number of days.

## Another way

To get the last day of each row's month without any offset, convert to a period and back: `s.dt.to_period("M").dt.end_time.dt.normalize()`. To get "the same day next month" for a whole column, `s + pd.DateOffset(months=1)` works on a Series too.
