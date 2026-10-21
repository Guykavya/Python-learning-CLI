## Approach

Clock arithmetic is modular arithmetic. Count minutes since midnight, subtract, and wrap the
result into the range 0 to 1439 with `% 1440`.

## Code

```python
sh = int(input())
sm = int(input())
eh = int(input())
em = int(input())
diff = ((eh * 60 + em) - (sh * 60 + sm)) % 1440
hours, minutes = divmod(diff, 60)
print(f"{hours} h {minutes} min")
```

## Why `%` does the right thing

22:30 is 1350 minutes, 06:00 is 360. The difference is `-990`. In Python, `-990 % 1440` is `450`
because the result takes the sign of the divisor. 450 minutes is 7 h 30 min.
In C or Java, `%` would give `-990` here, and you would need to add 1440 yourself.

## Another way

`(diff + 1440) % 1440` is a habit from other languages. In Python plain `% 1440` is enough.
