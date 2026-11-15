1. The list is **sorted**, so when `candidates[i] > remaining` **all later** candidates are at least as big and are also too big; none of them can fit, so `break` skips them all at once and is still correct.
2. Without sorting, a big candidate can come before a small one that would fit: with `[5, 2]` and target 2, the loop sees 5 > 2 and breaks, so the answer `[2]` is lost.
3. Sorting with `break` gives the same answers and the same recursive calls as `continue` without sorting (the call is skipped in both cases); it only saves the loop iterations over the remaining too-big candidates, which matters when there are many of them.

Checklist: your answer should mention
- [ ] the list is **sorted**, so **all later** candidates are too big as well
- [ ] **break** leaves the loop, `continue` only skips one candidate
- [ ] an example where `break` without sorting loses an answer
- [ ] pruning does not change the answers; here it saves loop iterations (the calls are already skipped by the check)
