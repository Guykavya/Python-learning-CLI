## Hint 1

Write the ten rows as a small table (day 1, day 2, day 3) and cross out exact repeats on each day. How many different users does each day have?

## Hint 2

```text
day 1: users 1, 2, 3
day 2: users 2, 3, 4 (user 2 appears twice)
day 3: users 1, 3 (user 3 appears twice)
line 2 adds the three daily counts; line 3 counts different users overall; line 4 counts rows
last line: days 2 and 3 only: the sum of their counts, and the distinct users in those two days
```
