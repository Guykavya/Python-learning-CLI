## Hint 1

When an exception leaves the body of a generator, the generator is finished, exactly as if its
body had reached the end. What does `next()` on a finished generator do? Does `x = 2` ever get a turn?

## Hint 2

In `safe`, the `try` is **inside** the loop. If `10 // x` fails, which line runs next? Does the
exception leave the generator at all? Then the `for` loop goes on to the next `x`.

## Hint 3

For the `for v in risky([1, 0, 5])` part, write down `total` after each item. The error leaves the
loop before `5` is reached. And remember `list(...)` collects all items first, so the generator's
own prints appear **before** the printed list.
