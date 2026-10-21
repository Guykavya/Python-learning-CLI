## Hint 1

The checks have an order, and you report only the first failure. Which statement picks the
first true condition?

## Hint 2

`all(ch in "ABCDEFGHIJKLMNOPQRSTUVWXYZ" for ch in code[:2])` checks the letters.

## Hint 3

Check the length first, so that `code[2]` can never crash on a short code.
`all(ch in "0123456789" for ch in code[3:])` checks the digits.
