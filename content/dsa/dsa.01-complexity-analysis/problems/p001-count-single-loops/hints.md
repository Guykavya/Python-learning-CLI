## Hint 1

Do not trace twenty iterations one by one. For each loop, ask: what is the first value, what is the last
value, and what is the step? Then count the values.

## Hint 2

`range(0, 20, 3)` gives 0, 3, 6, ... Stop before 20. `range(5, 21)` gives 5 up to 20 inclusive.
For the `while` loop, list the values of `i` that pass the test `i <= 20`.

## Hint 3

The last loop adds 1 every time, and an extra 1 when `i` is a multiple of 4. How many multiples of 4 are
there among 0, 1, ..., 19? Do not forget 0.
