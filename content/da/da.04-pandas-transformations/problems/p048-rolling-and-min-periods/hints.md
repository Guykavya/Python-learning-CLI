## Hint 1

Write the window of each row as a list. Trailing window of 3 at row *i*: rows *i−2*, *i−1*, *i*. Centred window of 3
at row *i*: rows *i−1*, *i*, *i+1*. Rows that do not exist are simply not there. Then ask: are there at least
`min_periods` values (default: the full window size)?

## Hint 2

```text
s.rolling(2).mean():           [1] [1,2] [2,3] [3,4]          -> nan, 1.5, 2.5, 3.5
min_periods=1:                 [1] counts too                 -> 1.0 first
t.rolling(3).sum():            [10] [10,20] [10,20,30] ...    -> nan, nan, 60, 90, 120
center=True:                   [10,20] [10,20,30] ... [40,50] -> first and last not full
center + min_periods=1:        partial windows are summed
count the NaN of the centred mean
```
