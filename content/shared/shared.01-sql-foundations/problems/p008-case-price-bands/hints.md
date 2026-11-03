## Hint 1

Which band has the lowest limit? Because CASE stops at the first true branch, do you need to write the lower bound of every band, or only the upper one?

## Hint 2

```
CASE
  WHEN price < 10 THEN 'budget'
  WHEN <next test> THEN 'standard'
  ELSE 'premium'
END AS band
```

Test the exact boundaries 10.00 and 20.00 in your head.
