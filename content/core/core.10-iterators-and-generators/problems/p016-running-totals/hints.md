## Hint 1

`accumulate(xs)` adds by default. How can you change what it does with the running value and the next item? Look at its second parameter.

## Hint 2

`accumulate(xs, func)` calls `func(running, item)`. Which built-in takes two values and returns the bigger one?

## Hint 3

```
running_totals: list(accumulate(numbers))
running_max:    list(accumulate(numbers, max))
```
