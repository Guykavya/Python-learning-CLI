## Hint 1

Which built-in returns a new sorted list? And which argument flips the direction?

## Hint 2

`sorted(a)` is ascending, `sorted(a, reverse=True)` is descending. Remember `a.sort()` returns `None`, so never print its result.

## Hint 3

```
a = list of ints
print(' '.join(map(str, sorted(a))))
print(' '.join(map(str, sorted(a, reverse=True))))
```
