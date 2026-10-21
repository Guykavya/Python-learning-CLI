## Hint 1

Try writing 1/3 as a decimal number exactly. What goes wrong? Now think about which base computers use.

## Hint 2

Run `print(f"{0.1:.20f}")` in the REPL and look at the digits.

## Hint 3

Look up `math.isclose` and the `decimal` module. Why must `Decimal` be created from a string, not a float?
