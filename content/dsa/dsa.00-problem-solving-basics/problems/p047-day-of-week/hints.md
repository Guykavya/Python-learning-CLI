## Hint 1

Before any weekday maths, what makes a date impossible? List every way: bad month, day too small,
day too big for that month. Which of these depends on the year?

## Hint 2

Compute `leap` (True/False) first, then `length` (days in the month) with if/elif on the month.
Only if the month is 1..12 and `1 <= day <= length` do you go on to Zeller. For Zeller, if the month
is 1 or 2, add 12 to the month and subtract 1 from the year *before* computing `K` and `J`.

## Hint 3

```
read day, month, year
leap = year % 4 == 0 and (year % 100 != 0 or year % 400 == 0)
if month < 1 or month > 12: print invalid
else:
    length = 31, 30 for 4/6/9/11, 29 or 28 for 2
    if day < 1 or day > length: print invalid
    else:
        m, y = month, year;  if m < 3: m += 12; y -= 1
        K = y % 100; J = y // 100
        h = (day + 13*(m+1)//5 + K + K//4 + J//4 + 5*J) % 7
        if h == 0: Saturday  elif h == 1: Sunday ...  elif h == 6: Friday
```
