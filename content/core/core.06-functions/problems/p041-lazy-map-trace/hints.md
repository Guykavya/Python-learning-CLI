## Hint 1

When does `noisy` actually run: when `map(noisy, ...)` is created, or when values are taken from it?

## Hint 2

`list(m)` takes every value. A second `list(m)` finds the iterator already exhausted.

## Hint 3

`any(...)` stops at the first truthy value, so it pulls only as many values as it needs. Values it did not take are still waiting in the iterator.
