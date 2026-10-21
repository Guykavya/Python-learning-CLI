## Hint 1

A `while` loop checks its condition, runs the whole body, then checks again. When the body changes
`i` before printing, which value gets printed: the old one or the new one?

## Hint 2

The loop stops only when the condition is **false**. So after the loop, `i` is the first value
that failed the check. For `i < 3` that is 3; what is it for `i <= 3`?

## Hint 3

Loop B: check `1 <= 3` true, `i` becomes 2, print `B 2`. Check `2 <= 3` true, `i` becomes 3, print.
Keep going until the check is false, then print the ending line.
