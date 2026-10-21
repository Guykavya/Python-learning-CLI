## Hint 1

If you multiply a running result by `a` once per loop round, how many rounds do you need for `a` to the power `b`?
And what should the result be before any rounds have happened?

## Hint 2

Start the result at `1`, not at `a` and not at `0`. Then `b = 0` needs no special case: the loop simply runs zero times.

## Hint 3

```
read a, read b
result = 1
repeat b times:
    result = result * a
print result
```
