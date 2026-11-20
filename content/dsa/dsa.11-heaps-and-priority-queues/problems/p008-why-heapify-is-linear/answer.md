## Model answer

**1. The perfect heap of 15 items.** Level by level: 1 node at the root (height 3), 2 nodes of height 2, 4 nodes of height 1 and 8 leaves of height 0. A `sift_down` from a node can make at most as many swaps as the node's height, because the item can sink at most to the bottom. So the most that `heapify` can do is `8*0 + 4*1 + 2*2 + 1*3 = 11` swaps.

**2. Pushing in the worst order.** A push pays the **depth** of the new node, because the item may climb up to the root. The depths are: 8 leaves at depth 3, 4 nodes at depth 2, 2 at depth 1 and the root at depth 0. The total is `8*3 + 4*2 + 2*1 + 0 = 34` swaps, three times more than the 11 of heapify. For 1,023 items the numbers are 1,013 against 8,194.

**3. Why the height.** `sift_down` only moves **down** from its start node, and every swap goes one level lower. The longest way down from a node is its height, so one call costs at most `height` swaps (and two comparisons per swap). It never goes back up, so `log2(n)` is only the cost for the root.

**4. Adding it up.** About `n/2` nodes are leaves and cost nothing. About `n/4` nodes have height 1 and cost at most 1, `n/8` nodes have height 2 and cost at most 2, and so on up to the root. The total is at most `n/4*1 + n/8*2 + n/16*3 + ...`, which can be written as `n * (1/4 + 2/8 + 3/16 + ...)`; the bracket adds up to 1, so the total is at most `n`. The few nodes that are expensive (high up) are balanced by the many nodes that are cheap (low down): each halving of the number of nodes only adds 1 to the cost per node, and a number that halves each time beats a cost that grows by 1.

**5. Why pushes are different.** A push pays the **depth**, not the height, and most nodes are **deep**: half of them are leaves at the largest depth, `log2(n)`. So the sum of the depths is about `n log n`, while the sum of the heights is below `n`. It is the same tree, counted from the other end.

**6. The friend.** Not wrong, only not precise. `n/2` calls, each at most `log n`, really is a correct **upper bound**: `O(n log n)` is true for heapify. But it is not **tight**: it counts the cost of the root for every call. The careful count shows that the real total is at most `n`, which is a smaller bound that is also true, so `O(n)` is the tight bound. It is also a lower bound: every item must be looked at at least once, so `heapify` is `Theta(n)`.

**7. Heap sort.** No. Building the heap is `O(n)`, but then heap sort does `n - 1` pops, and each pop sinks an item from the root, which costs up to `log n`. This part is `O(n log n)` and it dominates. (Measured in the chapter: for 100,000 random numbers `heapify` used 188,081 comparisons and 100,000 pushes used 228,401; on descending data 199,978 against 1,468,946.)

**Checklist: your answer should mention**
- [ ] the counts 8, 4, 2, 1 for heights 0, 1, 2, 3 and the total of 11
- [ ] the pushes in the worst case cost 34 (depths), more than heapify's 11
- [ ] `sift_down` costs at most the **height** of its start node: it only moves down
- [ ] most nodes are near the bottom: `n/2` have height 0, `n/4` height 1, `n/8` height 2 ...
- [ ] the sum `n/4*1 + n/8*2 + ...` stays below `n` (cheap nodes are many, expensive nodes are few)
- [ ] a push pays the **depth**, and most nodes have a large depth: `n log n`
- [ ] `O(n log n)` for heapify is a correct but loose upper bound; `O(n)` is the tight one
- [ ] heap sort is still `O(n log n)` because of the `n` pops
