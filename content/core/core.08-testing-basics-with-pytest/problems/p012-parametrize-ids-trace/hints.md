## Hint 1

Handle the plain tests first. Write all the rows of `test_add` with their ids (`1-2-3`, ...) and decide pass or fail by arithmetic. Is `-1 + 1 == 0`?

## Hint 2

`test_palindrome`: which word is not the same backwards? `test_positive`: with `ids`, the text in brackets is the id you gave, not the number.

## Hint 3

`test_pair` has 2 x 2 = 4 combinations. The id reads `[y-x]` because the bottom decorator (`y`) comes first. Which combination makes `str(x) + y` equal `"2b"`?
