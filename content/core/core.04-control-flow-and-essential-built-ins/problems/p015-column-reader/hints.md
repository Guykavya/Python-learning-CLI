## Hint 1

Which positions are in column 0? Column 1? Write them out for width 3 and a 7-character message.

## Hint 2

Column `c` holds positions `c`, `c + width`, `c + 2 * width`, ... up to the end. That is a
`range` with a step.

## Hint 3

```
for c in range(width):
    for pos in range(c, len(message), width):
        result += message[pos]
```
