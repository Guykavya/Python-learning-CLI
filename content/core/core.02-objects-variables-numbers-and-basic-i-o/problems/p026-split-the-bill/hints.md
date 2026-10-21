## Hint 1

Run the starter with `4.35` and `1` person. Why does it lose a paisa? What is `4.35 * 100` as a float?

## Hint 2

`Decimal("4.35") * 100` is exactly `435.00`, so `int()` of it is exactly 435.
Then `divmod(paise, people)` gives the share and the leftover.

## Hint 3

To print a whole number of paise as rupees without floats: rupees are `share // 100`,
the remaining paise are `share % 100`, padded to two digits with `:02d`.
