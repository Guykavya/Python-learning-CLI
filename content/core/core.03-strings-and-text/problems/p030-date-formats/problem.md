# Reformat a date

Read a date in ISO format `YYYY-MM-DD` (spaces around it are possible). Print it three other ways:

```
DD/MM/YYYY
D Mon YYYY
YYYYMMDD
```

- The first form keeps two-digit day and month.
- The second form has the day **without** a leading zero and the first three letters of the English month name.
- The third form has no separators.

**Example**

Input:
```
2026-01-05
```
Output:
```
05/01/2026
5 Jan 2026
20260105
```

Hint for the month name without `if` or lists: the string `"JanFebMarAprMayJunJulAugSepOctNovDec"` has every month at a predictable position.
