## Hint 1

Build the index once: for each document number and each lowercase word,
`index.setdefault(word, set()).add(number)`.

## Hint 2

`and` is the intersection of the words' sets, `or` the union, `not` a difference. Use
`index.get(word, set())` for unknown words.

## Hint 3

Start an `and` result with the first word's set (a copy!) and intersect with the rest, using
`&=` on the copy, never on the index's own set.
