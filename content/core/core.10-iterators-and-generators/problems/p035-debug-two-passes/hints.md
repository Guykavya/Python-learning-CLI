## Hint 1

Run Ravi's `stats` on a generator by hand. After `list(numbers)`, where is the generator? What does
`sum()` of a finished generator return? What does `max()` of it do?

## Hint 2

For `stats`, one `for` loop can update three variables at once. What should `largest` start as so
that negative numbers work and an empty input gives `None`?

For `shares`, two passes are really needed. You cannot rewind a generator. What can you make once
that *can* be read twice?

## Hint 3

```
stats:
    count, total, largest = 0, 0, None
    for x in numbers:
        count += 1; total += x
        if largest is None or x > largest: largest = x
    return count, total, largest

shares:
    data = list(numbers)
    total = sum(data)
    if total == 0: raise ValueError(...)
    return [x / total for x in data]
```
