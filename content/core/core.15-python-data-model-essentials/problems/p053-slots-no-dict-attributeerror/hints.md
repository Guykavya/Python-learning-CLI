## Hint 1

Go through the classes first: which of `P`, `Q`, `R`, `S` have a `__dict__`? `P` and `R` declare only slots. `Q` declares nothing, so it gets a normal `__dict__`. `S` lists `"__dict__"` in its slots on purpose. Then decide for each statement whether it is allowed.

## Hint 2

Careful at `print(p.y)`: `y` is a slot of `P`, but `__init__` only sets `x`. The slot exists, but is empty. For `del p.x` and then `print(p.x)`: deleting empties the slot again.
