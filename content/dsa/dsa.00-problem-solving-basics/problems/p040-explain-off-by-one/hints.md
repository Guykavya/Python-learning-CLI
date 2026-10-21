## Hint 1

What numbers does `range(1, 5)` produce? Write them out. For Program B, trace `n = 472` and count how many
times the loop body runs compared with how many digits 472 has.

## Hint 2

Program B is wrong in two independent ways. One shows up for almost every input (it is always one short).
The other shows up only for numbers like 10, 100 and 1000. Trace `n = 10` with `while n > 10`. Does the loop run?

## Hint 3

Fix A with `range(a, b + 1)`. For B, ask: how many times can you divide a d-digit number by 10 before it has one digit?
That is `d - 1`. So either start `count` at 1 and loop `while n >= 10`, or rewrite the whole loop and then
re-check `n = 0`, which is the input most rewrites forget.
