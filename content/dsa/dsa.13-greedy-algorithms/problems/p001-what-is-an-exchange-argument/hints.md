## Hint 1

Re-read the template in chapter section 3, "Tool 1": take any optimal answer `O`, find the first place where it differs from greedy, swap in greedy's choice, show that the result is **valid** and **no worse**, repeat. Your answer for questions 2 to 5 is that template filled in with events and end times.

## Hint 2

For question 3, look at the **second** event of `O`, call it `h`. It starts at or after `end(f)` (that is why `f` and `h` fit together). And `end(g) <= end(f)`. Put the two facts in one line: `start(h) >= end(f) >= end(g)`. What does that say about `g` and `h`? The number of events did not change, so the size is the same.

## Hint 3

For question 6: greedy picks `(4, 7)`. The optimal schedule is `(0, 5), (6, 10)`. Try to swap `(4, 7)` in for `(0, 5)`: does `(4, 7)` fit next to `(6, 10)`? The step "the result is still valid" fails, and that is exactly the step the earliest-finish rule makes safe.
