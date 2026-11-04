## Hint 1

For `p = 2` the walk is `4, 6, 8, ..., 50`. All of them are still marked prime at that moment, so they are all listed.
There are 24 of them. Write them with commas, as a Python list.

## Hint 2

For `p = 3` the walk starts at 9: `9, 12, 15, ..., 48`. Remove the numbers that 2 already crossed (the even ones). What
is left are the odd multiples of 3 from 9.

## Hint 3

At which `p` does `p * p > 50` first become true? That is where the loop breaks. Then count the numbers still marked
prime: the primes up to 50 are 2, 3, 5, 7, 11, ... Count them, and give the largest.
