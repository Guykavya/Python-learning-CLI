## Hint 1

Each method checks **every** character. One failing character makes the whole answer `False`.

## Hint 2

The empty string is `False` for these methods. A space is not a letter. A minus sign and a dot are not digits.

## Hint 3

`isupper()` ignores characters that have no case (digits, spaces) as long as at least one letter exists. `²` is a digit but not a decimal digit.
