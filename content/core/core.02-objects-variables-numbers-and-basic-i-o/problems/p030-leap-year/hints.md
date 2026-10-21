## Hint 1

Why is 1900 not a leap year but 2000 is? Which of the three rules decides each one?

## Hint 2

"Divisible by 4 but not by 100" is one part. "Divisible by 400" is the other. A year is a leap
year if either part is true.

## Hint 3

`(year % 4 == 0 and year % 100 != 0) or year % 400 == 0`
