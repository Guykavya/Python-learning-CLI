# timedelta: days between, business days, age

Subtracting two dates gives a `timedelta`; adding a `timedelta` to a date gives a new date. The
library handles month lengths and leap years for you, so never compute dates with "30 days per
month" or "365 days per year".

```python
date(2025, 3, 1) - date(2025, 2, 1)    # timedelta(days=28)
date(2024, 2, 28) + timedelta(days=1)   # date(2024, 2, 29)  (2024 is a leap year)
date(2025, 3, 14).weekday()             # 4   (Monday is 0, Sunday is 6)
```

Write four functions in `solution.py`:

1. `days_between(a: date, b: date) -> int`: the number of days between the two dates, never
   negative (the order of the arguments does not matter).
2. `add_business_days(start: date, n: int) -> date`: move `n` working days (Monday to Friday)
   forward, or backward if `n` is negative. Weekends are skipped while counting.
   `n == 0` returns `start` unchanged, even if it is a weekend day.
3. `age_on(birth: date, today: date) -> int`: completed years of age on `today`. A person born
   on 29 February has their birthday on 1 March in years that are not leap years.
4. `format_duration(td: timedelta) -> str`: `"<days>d HH:MM:SS"`, for example `"1d 02:03:04"`.
   Microseconds are dropped. A negative duration raises `ValueError`.

**Example**

```python
days_between(date(2025, 3, 1), date(2025, 2, 1))     # 28
add_business_days(date(2025, 3, 14), 1)              # date(2025, 3, 17)  Friday -> Monday
age_on(date(2000, 6, 15), date(2025, 6, 14))         # 24  (birthday is tomorrow)
format_duration(timedelta(hours=26, seconds=5))      # '1d 02:00:05'
```
