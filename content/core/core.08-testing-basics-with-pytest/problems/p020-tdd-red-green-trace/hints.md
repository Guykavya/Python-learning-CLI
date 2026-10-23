## Hint 1

Take the tests one at a time and run each in your head against version 1. A stub that returns 0: which tests happen to expect 0?

## Hint 2

Version 3 starts with `best = 0`. Which tests have only numbers smaller than 0? What does version 2 do on `[1, 2, 9]`? What does neither version 2 nor 3 do for `[]`?

## Hint 3

Count failures for each version. Version 4 should be green: do all five tests pass? (If you got 5 passed, you are right.)
