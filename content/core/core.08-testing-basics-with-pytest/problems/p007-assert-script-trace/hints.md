## Hint 1

Go function by function. For each `assert`, first evaluate the condition and decide `True` or `False`, then see whether the message is printed.

## Hint 2

`t3` has parentheses around **both** the condition and the message. What is `(1 == 2, "...")`? Is a non-empty tuple true or false? In `t5`, remember `0.1 + 0.2` in chapter 2.

## Hint 3

`t5` stops at its **second** assert, so the message printed is `float sum`. `t8` passes the first assert; `[1, 2] is [1, 2]` compares two different list objects.
