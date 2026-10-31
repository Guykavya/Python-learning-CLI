## Hint 1

The `type` statement looks like an assignment with a keyword: `type Name = <the type>`. What changes when the right-hand side mentions `Name` itself, as in the definition of `Json`? Why would a plain `Json = dict[str, Json] | ...` fail?

## Hint 2

`count_leaves` follows the shape of the data. Ask of the value: is it a dict? a list? or anything else (a leaf)? A dict and a list each call `count_leaves` again on their contents. What is the leaf case that stops the recursion? (`bool` is a kind of `int`, but both are leaves, so the order of your checks is not a problem here.)

## Hint 3

```
type Point = tuple[float, float]
type Matrix = list[list[float]]
type Json = dict[str, Json] | list[Json] | str | int | float | bool | None

distance(a, b): return math.hypot(a[0] - b[0], a[1] - b[1])
scale(m, k):    return [[x * k for x in row] for row in m]
count_leaves(v):
    if dict: sum of count_leaves over v.values()
    if list: sum of count_leaves over v
    else:    1
```
