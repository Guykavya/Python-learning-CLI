# Problem plan: dsa.11 Heaps and priority queues (30 problems)

Rules and format: see [dsa.07-problem-plan.md](dsa.07-problem-plan.md). Ids `dsa.11.p001`…`p030`.
**Mix:** 9 drill, 10 applied, 9 deep, 2 challenge. Kinds: 24 code, 4 trace, 2 explain. **assessment:** explain = p005, trace = p007, fix = p016, build = p030.
Tests for heap classes compare with `heapq`/`sorted` on random operation sequences (fixed seed). Ties: tests use unique priorities unless the problem is about ties.

| # | Title | Tier | Kind | Idea / tests |
|---|---|---|---|---|
| 1 | Indices in the array layout | drill | code | `parent(i)`, `left(i)`, `right(i)` |
| 2 | Is this array a min-heap? | drill | code | empty, 1 item, equal items |
| 3 | Sift up | drill | code | in-place function; check the heap property afterwards |
| 4 | Sift down | drill | code | |
| 5 | Why heapify is O(n) | deep | explain | graded by terms ("most nodes are near the bottom", "height") |
| 6 | MinHeap class | applied | code | `push/pop/peek/__len__`; differential test vs `heapq` on 2,000 random ops |
| 7 | Trace a pop | drill | trace | `⚠ HAND-TRACE` array after each swap during `pop` on a 7-item heap |
| 8 | Trace heapify | applied | trace | `⚠ HAND-TRACE` array after each sift-down in bottom-up heapify of `[9,4,7,1,6,2,8]` |
| 9 | Heap sort | applied | code | in place, descending and ascending; duplicates; empty |
| 10 | Max-heap with heapq | drill | code | negation; works for ints and for floats |
| 11 | Heap of tuples | drill | code | `(priority, counter, item)`; items that cannot be compared must still work (test uses dicts) |
| 12 | K largest elements | drill | code | min-heap of size k; k > n; counter forbids full sort |
| 13 | K-th largest in a stream | applied | code | class `add(val)`; initial list shorter than k |
| 14 | K most frequent words | applied | code | tie → alphabetical order |
| 15 | K closest points to the origin | applied | code | compare squared distances; no sqrt |
| 16 | Fix the top-k with a max-heap | applied | code | `assessment = "fix"`; given a version that builds an n-size heap and passes only small tests; time-limit test on 10**5 |
| 17 | Running median | deep | code | two heaps; stream class `add`/`median`; compare with `statistics.median` |
| 18 | Trace the two heaps | deep | trace | `⚠ HAND-TRACE` both heaps and the median after each of 6 numbers |
| 19 | Sliding window median | challenge | code | lazy deletion; compare with brute force |
| 20 | Merge k sorted lists with a heap | applied | code | generator version bonus: lazy `merge` |
| 21 | K-th smallest in a sorted matrix | deep | code | |
| 22 | K smallest pair sums | deep | code | lazy exploration; counter on pushes |
| 23 | Connect the sticks | drill | code | minimal cost; one stick = 0 |
| 24 | Meeting rooms II | applied | code | rooms needed; touching intervals do not overlap |
| 25 | Reorganise a string | deep | code | return any valid; validator in test; impossible → `""` |
| 26 | Task scheduler with cooldown | challenge | code | brute-force on tiny inputs |
| 27 | Shortest job first | applied | trace | `⚠ HAND-TRACE` finish order and average wait for 5 jobs |
| 28 | Priority queue with updates | deep | code | lazy deletion; random ops vs dict model |
| 29 | Why not change an item inside the heap? | deep | explain | demonstrate breaking the invariant; graded by terms |
| 30 | Build an indexed priority queue | deep | code | `assessment = "build"`; `push/update/remove/pop_min`; ops vs dict+`min` model |

## Counts
Traces 7, 8, 18, 27 are explicit; turn p6's printed state, p13, p17 into pure trace questions to reach 7. Explain 5, 29 plus p2 and p19 as written variants for 4. Keep one assessment of each kind.

## Real-site problems (`external.toml`)
LeetCode `kth-largest-element-in-an-array`, `kth-largest-element-in-a-stream`, `top-k-frequent-elements`, `top-k-frequent-words`, `k-closest-points-to-origin`, `find-median-from-data-stream`, `sliding-window-median`, `merge-k-sorted-lists`, `kth-smallest-element-in-a-sorted-matrix`, `find-k-pairs-with-smallest-sums`, `last-stone-weight`, `meeting-rooms-ii`, `reorganize-string`, `task-scheduler`, `ipo`, `smallest-range-covering-elements-from-k-lists`, `minimum-cost-to-connect-sticks`; CSES 1074/1075 not heap; verify Codeforces choices. Ids unverified.
