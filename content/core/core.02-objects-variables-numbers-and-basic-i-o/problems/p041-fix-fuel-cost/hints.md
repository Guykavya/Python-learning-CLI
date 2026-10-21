## Hint 1

Run the starter with the example input. What crashes or looks wrong first? Fix one bug, run again, repeat.

## Hint 2

Check every line against the specification: the type each input becomes, the formula, how
the Decimal is built, the rounding rule, and the `print` separator.

## Hint 3

The five bugs: `int()` on a decimal distance; `float` for mileage and price (and `Decimal(float(...))`);
`*` instead of `/`; `round()` instead of `quantize(CENT, rounding=ROUND_HALF_UP)`; `sep=""` removing the space.
