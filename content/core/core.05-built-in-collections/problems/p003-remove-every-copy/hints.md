## Hint 1

Instead of removing from the old list, could you build a **new** list holding only the words you keep?

## Hint 2

`kept = [w for w in words if w != target]`. How many were removed? Compare two lengths.

## Hint 3

Print `" ".join(kept)` if `kept` is not empty, else `(empty)`. Then `len(words) - len(kept)`.
