## Hint 1

After `type hi` and `type _there`, `undo_stack` is `['', 'hi']` and the text is `'hi_there'`. The `undo` pushes `'hi_there'` onto `redo_stack` and pops `'hi'`. Now `type !` comes: what happens to `redo_stack`?

## Hint 2

A `redo` with an empty `redo_stack` changes nothing, but the line is still printed. Write the stacks as lists, not only their sizes: `undo_stack = ['', 'hi']`, `redo_stack = []` after `redo redo`, and so on.
