## Hint 1

Times are easier to step through as **minutes since midnight**. 09:00 is 540.

## Hint 2

Slot starts go from `start` in steps of `length`. The last allowed start is `end - length`.
What `stop` makes a `range` include that value?

## Hint 3

`for s in range(start, end - length + 1, length):` then turn `s` and `s + length` back into
`HH:MM` with `divmod(s, 60)` and `:02d`.
