## Hint 1

You already know how to peel the last digit off with `n % 10`. If you peel `1234` you get 4, then 3, then 2, then 1. That is the order you want. How can you glue digits together into a number, one at a time?

## Hint 2

Start with `rev = 0`. To add a digit `d` on the right of `rev`, do `rev = rev * 10 + d`. For example `43 * 10 + 2` is `432`. Remember the sign before you start, and work with `abs(n)`.

## Hint 3

```
negative = n < 0
n = abs(n)
rev = 0
while n > 0:
    d = n % 10
    rev = rev * 10 + d
    n = n // 10
if negative: rev = -rev
print rev
```
