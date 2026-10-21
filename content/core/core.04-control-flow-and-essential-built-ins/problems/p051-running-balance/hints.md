## Hint 1

You need a loop that can stop for two different reasons: the `end` line, or a declined
withdrawal. Which loop shape lets you leave from the middle?

## Hint 2

Check the shape with `len(line) >= 2 and line[0] in "+-" and line[1:].isdigit()`. Short-circuit
keeps `line[0]` safe on an empty line.

## Hint 3

Count `K` only for valid lines. For a decline, print, then `break` before changing the balance.
