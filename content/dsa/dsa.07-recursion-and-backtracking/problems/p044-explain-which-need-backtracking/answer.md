## Answer key

1: **B** - "list every" placement, with rules (rows, columns, forbidden squares): generate with pruning.
2: **D** - a count where the state (the current step) repeats: `ways(n) = ways(n-1) + ways(n-2)`.
3: **L** - one pass, keep the maximum.
4: **G** - for the euro coin system, always taking the largest coin that fits is optimal.
5: **B** - a puzzle with rules where every partial fill must be checked (constraint search).
6: **D** - counting with a state `(index, remaining sum)`: 100 x 2,500 states, while `2^100` subsets is far too many to walk.
7: **B** - "generate every" string; the prune `closed < opened` is the whole rule (Catalan numbers).
8: **L** - one pass comparing each character with the next.

## Sample justifications

**Problem 7 (B).** The task asks to output every answer, so the work is at least the number of answers (14 for `n = 4`), and no two partial strings lead to the same future that we could reuse. Backtracking with the prune builds only valid prefixes; the input is tiny.

**Problem 6 (D).** The same **state** "I am at number `i` and still need `s`" is reached by many different choices, so the recursion tree has **repeated** sub-trees; remembering each state's count gives about 100 x 2,500 = 250,000 states. Plain backtracking would walk up to `2^100` branches, which is hopeless for an input of size 100.

Checklist: your answer should mention
- [ ] the labels **1 B, 2 D, 3 L, 4 G, 5 B, 6 D, 7 B, 8 L**
- [ ] "list / generate **every**" points to backtracking
- [ ] "**count**" plus a **repeated state** points to dynamic programming
- [ ] the **size** of the input (`2^100` versus 250,000 states; `n = 100,000` needs a loop)
- [ ] greedy is safe for problem 4 only because of this particular coin system
