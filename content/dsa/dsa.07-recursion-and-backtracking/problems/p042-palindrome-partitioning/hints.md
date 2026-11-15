## Hint 1

`go(start)` cuts `s[start:]`. If `start == len(s)` the current list of pieces is a complete answer.

## Hint 2

Loop `end` from `start + 1` to `len(s)`. The piece is `s[start:end]`. Only if it is a palindrome: append it, recurse with `go(end)`, pop it.

## Hint 3

A palindrome test: `piece == piece[::-1]`.
