## Hint 1

How many bytes does UTF-8 use for plain ASCII letters? For `é`? For `₹`? Add them up for the whole string.

## Hint 2

`len(text)` counts characters: 7. For bytes: `caf` is 3, `é` is 2, the space is 1, `₹` is 3, `5` is 1, total 10. `data[:5]` shows bytes: printable ASCII bytes appear as letters, others as `\x..` escapes. `é` in UTF-8 is `c3 a9`; in Latin-1 it is the single byte `e9`.
