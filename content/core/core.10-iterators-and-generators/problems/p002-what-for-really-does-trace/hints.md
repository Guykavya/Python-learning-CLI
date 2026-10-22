## Hint 1

`iter(x)` asks an iterable for a fresh iterator. `next(it)` asks the iterator for the next item. What happens when there is no next item? What does `next(it, default)` do instead?

## Hint 2

Go line by line. After the `while` loop ends, `it` is still the same exhausted iterator. Ask yourself what `next(it, "empty")` and `list(it)` give for an exhausted iterator.
