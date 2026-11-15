# Streaks of consecutive days (gaps and islands)

A user was active on some days. A *streak* is a run of consecutive calendar days. Finding the streaks is the famous "gaps and islands" problem,
and the trick is:

> Subtract the row number from the date. Inside one streak both go up by 1 per row, so the difference is the same for the whole streak. A gap changes it.

In SQLite, `date(day, '-3 days')` subtracts days from a date string. `date(day, '-' || n || ' days')` lets `n` come from a column.

```sql
CREATE TABLE activity (day TEXT PRIMARY KEY);
INSERT INTO activity VALUES ('2024-01-01'),('2024-01-02'),('2024-01-03'),('2024-01-05'),('2024-01-07'),('2024-01-08');
```

Write one query returning `start_day`, `end_day`, `days` (how many days in the streak) for every streak, ordered by `start_day`.
A single isolated day is a streak of length 1. The dates are unique. Remember leap years and month/year ends: do not compare strings numerically.

**Example**

| start_day | end_day | days |
|---|---|---|
| 2024-01-01 | 2024-01-03 | 3 |
| 2024-01-05 | 2024-01-05 | 1 |
| 2024-01-07 | 2024-01-08 | 2 |
