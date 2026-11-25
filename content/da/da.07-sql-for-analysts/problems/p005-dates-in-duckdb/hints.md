## Hint 1

Take the lines one at a time and ask what SQL does, not what you would expect from a calendar app. For the first line: which day of the week is 1 January 2025, and where does a week start in DuckDB?

## Hint 2

```text
week start      -> go back to the Monday on or before the date
month + 1 month -> same day next month, or the last day if that day does not exist
date_diff month -> how many month boundaries lie between the two dates (compare year*12+month)
date_diff day   -> days between the two dates (January has 31 days, February 2025 has 28)
7 / 2 vs 7 // 2 -> true division vs floor division
1 / 0           -> not an error in DuckDB; NULLIF(0, 0) -> NULL (printed None)
```
