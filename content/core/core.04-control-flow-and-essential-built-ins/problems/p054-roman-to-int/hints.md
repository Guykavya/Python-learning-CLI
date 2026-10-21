## Hint 1

Each symbol's value depends only on itself and the symbol **after** it. How can a loop see
each symbol together with the next one?

## Hint 2

`zip(text, text[1:] + " ")` pairs each symbol with the next one; the extra space gives the
last symbol a partner. A `match` (or a chain of `if`s) turns a symbol into its value; give the
space value 0.

## Hint 3

For each pair: if the value is smaller than the next value, subtract it, otherwise add it.
Validate first: `all(ch in "IVXLCDM" for ch in text)` and `text` not empty.
