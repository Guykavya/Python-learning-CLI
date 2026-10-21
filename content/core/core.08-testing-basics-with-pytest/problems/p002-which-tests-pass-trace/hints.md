## Hint 1

First list which functions pytest even collects. What must a function's name start with?

## Hint 2

For each collected test compute the left side of `==` on paper. `add(-1, 1)` is `0`. Does `0 == 1`? And `add("1", 1)`: what does `+` do with a string and an int?

## Hint 3

A test that raises *any* exception (not only `AssertionError`) is reported as FAILED. Count the failures, then the passes.
