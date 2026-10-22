## Hint 1

`sum(squares)` runs the generator all the way to the end. What does a generator that has reached the end give to the next `sum`?

## Hint 2

A list is never consumed. For `bool(gen)`: objects are truthy unless they define emptiness (like lists do). Does a generator know how many items it has left?
