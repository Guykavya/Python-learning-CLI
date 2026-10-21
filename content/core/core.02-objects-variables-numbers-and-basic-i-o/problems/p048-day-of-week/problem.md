# Day of the week from a date

Read a date as three whole numbers: day, month, year (Gregorian calendar, year 1583 or later).
Print the ISO weekday number: 1 for Monday up to 7 for Sunday.

Use **Zeller's congruence**:

```
h = (q + (13 * (m + 1)) // 5 + K + K // 4 + J // 4 + 5 * J) % 7
```

where

- `q` is the day of the month,
- `m` is the month, **but January and February count as months 13 and 14 of the previous year**,
- `K` is the year within the century (`year % 100`) and `J` is the century (`year // 100`),
  using that adjusted year,
- the result `h` means 0 = Saturday, 1 = Sunday, 2 = Monday, ..., 6 = Friday.

**Rules:** no `if` (you have not learned it). Do the January/February adjustment with arithmetic.
Do not import `datetime` or `calendar`.

**Example**

Input:
```
15
8
1947
```
Output:
```
5
```

15 August 1947 was a Friday.
