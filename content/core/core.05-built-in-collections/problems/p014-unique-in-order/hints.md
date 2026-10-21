## Hint 1

You need two things: a fast "have I seen this?" check, and the names in order. Which collection
is good at each?

## Hint 2

Keep a `seen` set and an `order` list. For each name, if it is not in `seen`, add it to both.

## Hint 3

`list(dict.fromkeys(names))` also removes duplicates while keeping first-seen order, in one line.
