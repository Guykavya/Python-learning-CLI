## Hint 1

Convert both times to "minutes since midnight". What is the difference for 22:30 to 06:00?

## Hint 2

The difference is negative when midnight is crossed. Python's `%` with a positive divisor always
gives a result from 0 to divisor - 1. What is `-990 % 1440`?

## Hint 3

```
diff = ((eh * 60 + em) - (sh * 60 + sm)) % 1440
hours, minutes = divmod(diff, 60)
```
