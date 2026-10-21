## Hint 1

Store each point as `Point(x, y)` in a list. A namedtuple's fields are read as `p.x` and `p.y`.

## Hint 2

Keep a `best` point. Loop over the points and replace `best` only when the new point is
**strictly** farther. That keeps the first among equals.

## Hint 3

`best._replace(x=best.x + 1)` returns a new point. `sum(p.x for p in points)` adds the x values.
