## Hint 1

Use a list: the front is index 0 and the back is the end. Split each command with `split()`.

## Hint 2

`queue.pop(0)` removes the front. `queue.remove(name)` removes a name from the middle. Check
`name in queue` before removing or joining.

## Hint 3

A `match parts:` with cases like `case ["join", name]:` and `case ["serve"]:` reads cleanly, or
use `if`/`elif` on `parts[0]`.
