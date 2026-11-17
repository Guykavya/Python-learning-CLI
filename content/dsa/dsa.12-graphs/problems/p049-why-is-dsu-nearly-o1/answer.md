## Model answer

**1. No tricks.** `union(i, i + 1)` hangs the root of `i`'s group under `i + 1`, and the root of the growing group is always its right end. After all unions the parents form a single chain `0 -> 1 -> 2 -> ... -> n-1`: element 0 is at depth `n - 1` (99,999 in the chapter's run). Every `find(0)` walks the whole chain, so `n` such calls cost about `n^2` steps: 10 billion for `n = 100,000`.

**2. The doubling argument.** An element's depth grows only when the root of its group is hung under another root. Union by size does that only to the **smaller** group (on a tie, either one). If the smaller group has `s` elements and the other has at least `s`, the merged group has at least `2s`. So every time an element moves one level deeper, its group at least doubles. A group can double at most `log2(n)` times before it contains all `n` elements, so no element is ever deeper than `log2(n)`, and `find` walks at most `log2(n)` steps: `O(log n)` per operation even **without** compression.

**3. A worked example.** Unite `(0,1), (2,3), (4,5), (6,7)`: four trees of height 1. Unite `(0,2), (4,6)`: two trees of 4 with height 2. Unite `(0,4)`: one tree of 8 with height 3. With the chapter's tie rule (the root of `y` goes under the root of `x`) the final parents are `1 -> 0`, `3 -> 2 -> 0`, `5 -> 4 -> 0`, `7 -> 6 -> 4 -> 0`: element 7 is 3 steps from the root. Height 4 would need some element to be moved down 4 times, so its group would have reached at least `2**4 = 16` elements, more than 8. Impossible.

**4. Path compression.** `find(x)` first walks up to the root, then walks the same path again and makes every element on it point **straight at the root**. The next `find` on any of those elements takes one step. A long path is paid for once and then disappears.

**5. Amortised.** "Amortised `O(1)`" means the **total** cost of `m` operations is `O(m)` (times α), so the **average** per operation is constant. A single `find` can still walk several steps (up to `log2 n` with union by size), but such a walk flattens the path, so expensive operations are rare and pay for the cheap ones that follow. It is a promise about sequences, not about every single call.

**6. The α.** α is the inverse of the Ackermann function, which grows faster than any tower of exponents. Its inverse therefore grows unimaginably slowly: α(n) is at most 4 for every `n` up to a number with far more digits than there are atoms in the universe. For any input that fits in a computer it is a small constant, so the cost is practically `O(1)` per operation. (With only **one** of the two tricks, the bound is `O(log n)`.)

**7. The price.** Each element only knows its parent, and only the roots carry information about a group. Splitting a group would require knowing which elements belong to which half, but the tree shape (after compression) no longer records the history of the unions, and there are no pointers downwards. Listing a group's members would mean checking every element's root, `O(n)`. Use Union-Find when edges only **arrive** and you ask "same group?" or "how many groups?" between arrivals; use BFS/DFS when the graph is fixed and you need paths, distances, or the members of a component, or when edges are removed.

**Checklist: your answer should mention**
- [ ] without tricks a line of unions builds a chain of depth `n - 1`, and `n` finds cost about `n^2`
- [ ] with union by size an element gets deeper only when its group at least doubles
- [ ] therefore every depth is at most `log2(n)`, and `find` is `O(log n)` even without compression
- [ ] an example of height 3 on 8 elements (pairs, then fours, then eight) and why 4 is impossible
- [ ] path compression points every element on the walked path straight at the root
- [ ] amortised = total cost over a sequence divided by its length; one call can still be slow
- [ ] α is the inverse Ackermann function, at most 4 for any realistic `n`: practically constant
- [ ] Union-Find can only merge, not split, and cannot list members quickly; BFS for fixed graphs, paths or deletions
