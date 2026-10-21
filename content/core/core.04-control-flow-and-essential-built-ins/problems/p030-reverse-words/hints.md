## Hint 1

`reversed(words)` walks the list of words from the end. `reversed(word)` walks the characters
of one word from the end.

## Hint 2

`reversed()` gives an iterator, not a string. Build the result with a loop and `+=`, or with
`"".join(...)`.

## Hint 3

For line 2 you need a loop over the words, and inside it a loop (or a `join`) over
`reversed(word)`.
