## Hint 1

Take the pieces one at a time and make each a small function that takes a DataFrame and returns a DataFrame: formats,
duplicates, suspects, validate. Which order is forced (what must be parsed before it can be compared)? Where do you keep
the reason that a reading was removed, so that it is not lost when the value becomes missing? What does a
`log` entry need to count?

## Hint 2

```text
formats:    station = strip, "-" -> " ", title;  ts = parse ISO or day-first by regex test;  flag from -999 / missing
duplicates: drop_duplicates(subset=[station, ts], keep="first"), sort, reset_index
suspects:   per station: rolling(7, center=True, min_periods=3).median() -> spike if pm25 > 3 * that
            run id of equal consecutive values -> stuck if run length >= 6;  mask pm25, keep the flag
validate:   pandera schema (lazy) -> failing row labels from failure_cases -> drop them, count them
A = mean per station;  B = interpolate(time, limit=3, inside) then polyfit pm25 ~ humidity per station for the rest
report = text with the log lines, the flag counts and one "station | A: x | B: y" line per station
```
