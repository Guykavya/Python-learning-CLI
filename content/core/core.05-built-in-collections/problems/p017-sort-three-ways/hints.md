## Hint 1

`sorted(words)` returns a new list. Pass `key=` to sort by something computed from each word.

## Hint 2

`key=str.lower` and `key=len`. Pass the function itself, without brackets.

## Hint 3

`sorted(words, key=len, reverse=True)` keeps tied words in input order. Reversing the result of
`sorted(words, key=len)` does **not**: it flips the ties too.
