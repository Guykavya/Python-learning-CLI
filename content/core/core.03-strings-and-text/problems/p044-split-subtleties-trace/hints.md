## Hint 1

There are two different splitting rules. With a separator, every separator makes a cut and empty pieces are kept. With no argument, runs of whitespace count as one and the ends are ignored.

## Hint 2

With a separator, an empty string still has one (empty) field. With no argument, an empty string has no words.

## Hint 3

`maxsplit` limits the number of cuts; `rsplit` makes them from the right. `splitlines` understands `\r\n` and does not produce an empty last piece.
