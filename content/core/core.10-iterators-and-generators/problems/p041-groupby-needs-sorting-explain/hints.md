## Hint 1

Write the keys of `sales` in a row: `tea coffee tea juice coffee`. Draw a line every time the key
changes. That is exactly how `groupby` cuts the input.

## Hint 2

For part 3: does `groupby` copy the items of a group anywhere? Where does a `group` read its items
from? What must `groupby` do with the unread items of a group before it can tell you the next key?

## Hint 3

Answer in order: 1) "neighbours only", 2) sorting puts equal keys together + cost + when not needed,
3) groups share one iterator, 4) `list(group)` right away, 5) dict for unsorted totals.
