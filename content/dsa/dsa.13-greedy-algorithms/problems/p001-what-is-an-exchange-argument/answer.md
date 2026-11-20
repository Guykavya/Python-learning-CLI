## Model answer

**1. Two properties.** A greedy algorithm is correct when (a) the **greedy-choice property** holds: some optimal answer contains the greedy choice, and (b) **optimal substructure** holds: after the choice, the rest of an optimal answer is optimal for the smaller problem that is left. The exchange argument proves (a).

**2. Why `end(g) <= end(f)`.** `g` is the event with the earliest end time among **all** events. `f` is one of those events. So `g` cannot end later than `f`.

**3. The swap.** Let `h` be the second event of `O`. Because `O` is valid, `start(h) >= end(f)`, and with question 2, `start(h) >= end(f) >= end(g)`. So `g` ends before `h` (or exactly when `h` starts, which is allowed) and, for the same reason, before every later event of `O`. Removing `f` and adding `g` gives a valid schedule `O'` with the **same number** of events, so `O'` is no worse; since `O` was optimal, `O'` is optimal too.

**4. What it proves.** There **exists** an optimal schedule that contains `g`. It does not say `O` was wrong: `O` may be just as good. Several optimal answers can exist; we only need one of them to agree with greedy's first choice.

**5. Repeat.** After taking `g`, the events left to consider are those that start at or after `end(g)`. That is the same problem (activity selection), only smaller. The same swap shows greedy's next choice is safe there too. By induction on the number of events, every choice is safe, so the whole greedy schedule has the optimal size. Each swap makes `O` look more like greedy's answer, until they are equal.

**6. Shortest first breaks.** On `[(0, 5), (4, 7), (6, 10)]` the shortest event is `(4, 7)` and the optimal schedule is `(0, 5), (6, 10)`. Swapping `(4, 7)` in for `(0, 5)` gives `(4, 7), (6, 10)`, which **overlaps** (6 < 7). The step "the result is still valid" fails, because a short event can still end **late**. Only "ends earliest" guarantees `end(g) <= end(f)`, which is what made the swap legal.

**Checklist: your answer should mention**
- [ ] the two properties: greedy choice and optimal substructure; the exchange proves the greedy choice
- [ ] start from **any** optimal answer `O`, not from greedy's answer
- [ ] `end(g) <= end(f)` because `g` ends first of all events
- [ ] the swapped schedule is valid: `start(h) >= end(f) >= end(g)` (touching is fine)
- [ ] it has the same size, so it is still optimal ("no worse")
- [ ] conclusion: **some** optimal answer contains `g` (not "every" one)
- [ ] what is left is the same problem, so induction / repeating finishes the proof
- [ ] for "shortest first" the swap creates an overlap, so the validity step breaks
