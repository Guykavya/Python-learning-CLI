## Hint 1

Write the format string by copying the example text and replacing each part by its code: `"2025-03-14 09:05:30"` → `"%Y-%m-%d %H:%M:%S"`. `strptime` always returns a `datetime`; which method of a datetime gives just the `date` part?

## Hint 2

There is no portable code for "day without leading zero": `%-d` works on Linux but fails on Windows, and `%#d` is Windows only. Build that part yourself: `dt.day` is an `int`, so `str(dt.day)` has no zero. Format the rest with `%a`, `%b`, `%Y`, `%H:%M`.

## Hint 3

```
parse_log_stamp(t): return datetime.strptime(t, "%Y-%m-%d %H:%M:%S")
parse_us_date(t):   return datetime.strptime(t, "%m/%d/%Y").date()
to_iso(dt):         return dt.isoformat()
pretty(dt):         return f"{dt:%a} {dt.day} {dt:%b %Y, %H:%M}"
```
