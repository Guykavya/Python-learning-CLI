## Hint 1

`pd.date_range(start, end, freq="D")` gives the days. Which `.dt` attributes (or `strftime` formats) give the other columns? Remember that `DateKey` must be an integer, not text.

## Hint 2

```text
d = pd.date_range(start, end, freq="D")
DateKey = d.strftime("%Y%m%d").astype(int); Quarter = "Q" + d.quarter.astype(str)
MonthName = d.strftime("%b"); YearMonth = d.strftime("%Y-%m")
```
