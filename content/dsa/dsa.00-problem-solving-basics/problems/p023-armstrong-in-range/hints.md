## Hint 1

For one number, how do you count its digits with `//`? How do you get each digit with `% 10`?
Why do you need the digit count **before** you can start adding powers?

## Hint 2

For each `x` in the range: copy `x` into a temporary variable and count digits (careful: 0 has one digit).
Then copy `x` again and add `digit ** k` for each digit. Keep a flag `found` so you know whether to print `none` at the end.

## Hint 3

```
read lo, hi
found = False
for x from lo to hi inclusive:
    k = 1, t = x // 10
    while t > 0: k = k + 1, t = t // 10
    total = 0, t = x
    while t > 0: total = total + (t % 10) ** k, t = t // 10
    if total == x: print x, found = True
if not found: print "none"
```
