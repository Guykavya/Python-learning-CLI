## Hint 1

Go through the program in order and note every line that prints something. Which lines print: `show(cart)`, the `print` calls, anything else?

## Hint 2

`show` prints while it runs, and returns `None`. So `r2 = show(cart)` prints one line **and** stores `None`. What does `print(r1, r2)` then show?

## Hint 3

`nums.sort()` sorts the list in place and returns `None`. So `print(nums.sort())` prints `None`, but `nums` itself changes. `sorted(...)` is the one that returns a new list.
