## Hint 1

Which of these numbers can be written exactly as a sum of powers of two (1/2, 1/4, 1/8, ...)?
Those are stored exactly; the others are approximations.

## Hint 2

A float has 53 bits of precision, about 15 to 17 significant decimal digits. Above 2**53, not every
whole number can be stored. Python prints the shortest text that reads back to the same float.

## Hint 3

Floats that overflow become `inf`. `nan` ("not a number") is never equal to anything, not even itself.
