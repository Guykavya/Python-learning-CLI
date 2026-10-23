## Hint 1

When is the default `[]` created: each time the function is called, or once, when `def` runs? So do the calls `add_tag("x")` and `add_tag("y")` use the same list?

## Hint 2

`a` and `b` are two names for **what**? Print `a` after the second call: has the list changed since the first call? Then look at `add_tag_safe`: where is its list created?

## Hint 3

`add_tag("z", mine)` passes a list, so the default is not used. But the default list still exists and still holds `"x"` and `"y"`. What does `add_tag("w")` add to, and what does `__defaults__` hold at the end?
