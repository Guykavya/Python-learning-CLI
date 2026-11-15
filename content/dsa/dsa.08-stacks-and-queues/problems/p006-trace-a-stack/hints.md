## Hint 1

The `pop` lines print the value that was removed **and** the list after removing it. Which item is removed: the one pushed first or the one pushed last?

## Hint 2

After `push 4`, `push 7`, `pop` the list is `[4]`. Continue from there: `push 1` gives `[4, 1]`, `push 9` gives `[4, 1, 9]`. Now each `pop` takes the rightmost item.
