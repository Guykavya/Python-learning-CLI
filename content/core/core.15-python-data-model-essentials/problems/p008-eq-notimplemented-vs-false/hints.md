## Hint 1

Take each comparison one at a time and write the chain: who is asked first, what they answer, and whether a second object is asked. Remember `print(...)` inside `__eq__` happens *during* the comparison, before the `print` of the result.

## Hint 2

```
Strict(1) == Always()
  1. Strict.__eq__ -> prints, returns NotImplemented
  2. Always.__eq__ (reflected) -> prints, returns True
  => True
Loose(1) == Always()
  1. Loose.__eq__ -> returns False   (the search stops)
```
