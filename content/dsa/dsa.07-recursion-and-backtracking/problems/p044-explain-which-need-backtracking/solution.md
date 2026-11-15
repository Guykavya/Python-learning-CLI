## Approach

Use the table of clues from chapter section 17: what is asked (all answers, a count, an optimum, a yes/no), and how large the input is. Backtracking fits when all answers must be produced or when a small puzzle must be searched; dynamic programming when states repeat; greedy when a local choice is provably safe; a loop when one pass suffices.

## Model answer

See `answer.md`: **1 B, 2 D, 3 L, 4 G, 5 B, 6 D, 7 B, 8 L**.

## What to check

- Your two justifications use the words **state**, **repeated** and the input **size**.
- You did not label problem 2 as B: a 1,000-step staircase has an astronomically large number of paths to walk, but only 1,000 states.
- For problem 4 you know why greedy works here and that it fails for other coin systems (for example 1, 3, 4 with amount 6: greedy gives 4 + 1 + 1, the best is 3 + 3).
