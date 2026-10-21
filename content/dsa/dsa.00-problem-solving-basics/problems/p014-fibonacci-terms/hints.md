## Hint 1

You never need the whole sequence, only the last two terms. If `a` is the current term and `b` is the next one, what are the current and next terms one step later?

## Hint 2

Start with `a = 0`, `b = 1`. Each step: print `a`, then move forward with `a, b = b, a + b`. Doing both updates at once matters: if you update `a` first, its old value is lost. To keep everything on one line, print with `end=" "`. Spaces at the end of the line are ignored by the tests.

## Hint 3

```
a, b = 0, 1
repeat n times:
    print(a, end=" ")
    a, b = b, a + b
if n > 0: print()
```
