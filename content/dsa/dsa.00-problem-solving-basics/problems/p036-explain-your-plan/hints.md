## Hint 1

Which digit sums are divisible by 7? Not only 7. What is the largest digit sum a number up to 10^6 can have
(think of 999999)? Which multiples of 7 are below that?

## Hint 2

For `n = 70`, go through the numbers with digit sum 7 (7, 16, 25, ...) and then look for digit sum 14.
Is there any number below 70 whose digits add up to 14? (Try 59.)

## Hint 3

The plan has two loops: an outer loop over every `x` from 1 to `n`, and an inner loop that takes
`x % 10` and `x // 10` to add up the digits of a copy of `x`. Count the steps as
"number of values times digits per value".
