## Hint 1

Write the three slots `a b c` for each call and fill them in order: positionals, then keywords, then defaults.

## Hint 2

`order(c=1, a=2)` has no positionals. `a` gets 2 and `c` gets 1 by keyword; `b` is still empty, so it gets its default.

## Hint 3

In `tag`, `sep` has a default that is used whenever the call does not name it. A string default can contain several characters.
