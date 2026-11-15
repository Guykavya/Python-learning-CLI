## Hint 1

If the meetings were in order of start time, which pairs would you have to check for a clash? All pairs, or fewer?

## Hint 2

After sorting by start, a clash exists if and only if some meeting starts **before** the previous one ends: `start[i] < end[i-1]`. Only neighbours need checking.

## Hint 3

```
meetings.sort()
for i in range(1, n):
    if meetings[i][0] < meetings[i-1][1]: print('NO'); stop
print('YES')
```
