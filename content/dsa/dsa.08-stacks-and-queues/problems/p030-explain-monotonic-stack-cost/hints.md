## Hint 1

Do not count loops; count stack operations. How many times is each index pushed? Once it is popped, can it ever come back?

## Hint 2

Every turn of the `while` loop pops exactly one index. If at most `n` indices are ever pushed, how many pops can there be in the whole run? Now add the `n` turns of the `for` loop.
