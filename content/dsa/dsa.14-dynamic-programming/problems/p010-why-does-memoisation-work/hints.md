## Hint 1

Count the calls of `fib(6)` per argument. `C(n)` was the total; now you want "how many times is `fib(k)` called". The counts for `k = 5, 4, 3, 2, 1` are themselves Fibonacci numbers: 1, 2, 3, 5, 8. How many different arguments are there in total?

## Hint 2

For question 3, ask: what happens the **second** time a state is asked, with and without the notebook? Then use the formula "time = states x work per transition" from chapter section 2.

## Hint 3

For question 4, write down the arguments of a few calls of `perms((), (1, 2, 3))`. Can two calls ever have the same `(chosen, remaining)`? A cache only saves time when the same arguments come back. For question 5, re-read the last paragraph of chapter section 3, trap 1: there are two bugs, name both.
