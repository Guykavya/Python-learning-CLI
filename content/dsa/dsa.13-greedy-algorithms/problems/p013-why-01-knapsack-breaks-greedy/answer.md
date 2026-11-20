## Model answer

**1. An instance.** Capacity 8. Items `A = (11, 5)`, `B = (8, 4)`, `C = (8, 4)`. Densities: A is 2.2, B and C are 2.0. Greedy by density takes A (weight 5, room 3 left); B and C each weigh 4 and no longer fit. Greedy's total is **11**. The best bag is B + C: weight 8, total **16**.

**2. The empty space.** Greedy leaves 3 of the 8 kilograms empty. The best bag uses all 8. In 0/1 knapsack every kilogram left empty is value lost, and greedy cannot fill the gap because no remaining item is small enough. In the fractional version greedy would fill those 3 kilograms with `3/4` of B (worth 6), reaching 17, which beats both 0/1 answers.

**3. Why the proof breaks.** The fractional exchange removes **a little** (`d` kilograms, any amount) of a thinner item and adds the same weight of a denser one; the weight stays equal and the value cannot fall. In 0/1 knapsack "a little" is illegal: items are indivisible lumps. Swapping whole items changes the total weight: replacing B (weight 4) by A (weight 5) in the best bag B + C gives weight 9 > 8, which does not fit. The step "the result is still valid" fails, so the greedy-choice property is not proved, and indeed it is false.

**4. Other keys do not fix it.** Highest value first fails on capacity 10 with `(10, 10)`, `(6, 5)`, `(6, 5)`: it takes the 10 and stops, while the two smaller items give 12. Lightest first fails on capacity 5 with `(1, 1)` and `(100, 5)`: it takes the worthless light item and the 100 no longer fits. No single sort key can work, because the best set depends on how weights **combine** to fill the bag, which a one-item-at-a-time rule never looks at.

**5. What to use.** For an exact answer use **dynamic programming** (a later module), which considers both "take" and "skip" for every item and every capacity, `O(n * W)`; for tiny `n`, brute force over all `2^n` subsets. The quick approximation: take the better of "density greedy" and "the single most valuable item that fits". It is guaranteed to reach **at least half** of the optimum, but not the optimum.

**Checklist: your answer should mention**
- [ ] a concrete instance with capacity and items, greedy's total and the best total (greedy strictly worse)
- [ ] greedy's densest item leaves space that no remaining item fits, and that space is the loss
- [ ] the fractional proof needs "any amount" / "a little"; whole items make that step illegal
- [ ] swapping whole items changes the weight, so the swapped bag may not fit
- [ ] other keys (value first, lightest first) also fail, with an instance or a reason
- [ ] the exact method: dynamic programming (or brute force for small `n`)
- [ ] the approximation: better of density greedy and the best single item, at least half the optimum
