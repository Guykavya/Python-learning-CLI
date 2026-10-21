## Hint 1

What is `1234 % 10`? What is `1234 // 10`? Repeat that by hand until nothing is left.

## Hint 2

Loop while the number is greater than 0: add the last digit to a total, then drop the last digit.

## Hint 3

Negative numbers break the loop condition and `%` behaves differently for them. What does `abs()` do?
