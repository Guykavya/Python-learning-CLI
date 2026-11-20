## Hint 1

Read the diff as if you had to maintain the code. What does it do with **money**? What happened to the old name `apply_discount`? What changed in `tests/`? And what is only taste?

## Hint 2

Label each comment by weight: what must be fixed before merge (`blocking`), what you would do but is optional (`suggestion`), what is a tiny style preference (`nit`).

## Hint 3

Four comments that cover it: (1) the float arithmetic for money (`0.1 + 0.2` problems; round, or use `Decimal`/cents) and no validation of `percent`; (2) the function was **renamed**: other code that imports `apply_discount` breaks (keep the old name as an alias, or rename in a separate PR); (3) no tests; (4) a style nit (`d` is a poor name; spaces around `*`).
