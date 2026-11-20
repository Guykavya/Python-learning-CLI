## Model answer

**The eight choices.**

1. **Greedy**, largest coin first. `[1, 5, 10, 25]` is a canonical coin system: greedy is always optimal (chapter section 22 checks every amount below 30 against the DP and finds no difference). DP also works but needs a table of 10**6 cells for no gain.
2. **DP**, fewest coins `f[a] = 1 + min(f[a - c])`. Greedy fails: for 6 it takes 4 + 1 + 1 (three coins), the best is 3 + 3 (two).
3. **Backtracking.** Every solution must be printed, so every solution must be built; place one queen per row and undo on a conflict.
4. **Greedy**, earliest end time first (dsa.13). Proved safe by the exchange argument; `O(n log n)`. A DP over sorted meetings also works but is more work.
5. **DP**, the 0/1 knapsack table, `O(n * W)` = 10**6 steps. Greedy by value per weight fails for whole items.
6. **Greedy** by value per weight, taking a fraction of the last item that does not fit. With fractions allowed, the exchange argument works.
7. **DP**, the LCS table, `O(n * m)` = 10**6 cells. There is no safe local choice, and backtracking over subsequences is `2**1000`.
8. **Backtracking** to print the subsets: the output itself can be huge, and each one must be built. For the **count** with 300 numbers: **DP** (count subsets, `f[s] += f[s - x]`, loop `s` downwards), because counting needs no list.

**Full justification, task 2 (DP).** Greedy takes the largest coin that fits, and for `[1, 3, 4]` with amount 6 that is 4, after which only 1 + 1 fits: three coins, but 3 + 3 uses two. So no local rule is safe here. The state is the amount still to pay, `f[a]` = the fewest coins for `a`; the last coin is some `c`, so `f[a] = 1 + min(f[a - c])`. Sub-problems repeat because many different coin sequences leave the same remaining amount (pay 4 then 1, or 1 then 4: both leave `a - 5`). There are only 10**4 + 1 states, each with 3 choices.

**Full justification, task 6 (greedy).** The rule is: sort the items by value per kilogram, take them in that order, and when the next item does not fit, take the fraction that fills the bag. It is safe by an exchange argument: if an optimal bag holds some weight of a worse-ratio item while a better-ratio item is not fully taken, swapping that weight for the better item never lowers the value. Fractions make that swap always possible, which is exactly what breaks for task 5 (whole items cannot be swapped by weight). DP would be wrong-shaped here: the capacity is not split into whole units, and the greedy answer is already optimal in `O(n log n)`.

**Checklist: your answer should mention**
- [ ] task 1: greedy works for these coins (a canonical system), and you did not just say "greedy is faster"
- [ ] task 2: a **counterexample** to greedy (6 = 3 + 3) and the DP state "amount left"
- [ ] task 3 and task 8 (print every subset): **backtracking**, because every solution must be **listed**
- [ ] task 4: greedy by **earliest end time**, with an exchange-argument reason
- [ ] task 5 vs task 6: whole items need **DP**; fractions make **greedy** by value per weight safe
- [ ] task 7: DP, because there is no safe local choice and sub-problems (prefix pairs) **repeat**
- [ ] task 8, twin: **counting** with DP, not listing; and each number used once (downward loop)
- [ ] the two full justifications name the state (DP), the rule and why it is safe (greedy), or why the whole history is needed (backtracking)
