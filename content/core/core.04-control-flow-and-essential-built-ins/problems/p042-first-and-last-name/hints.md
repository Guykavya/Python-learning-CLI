## Hint 1

Without a key, `"zoya" > "Bhavesh"` but `"Zoya" < "bhavesh"`. Capitals come first in character
order. How do you compare names as if they were all small letters?

## Hint 2

`key=str.lower` compares the lower-case versions but returns the original names.

## Hint 3

`key=len` finds the longest. Ties already go to the first.
