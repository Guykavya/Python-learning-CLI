# Problem plan: dsa.11 Heaps and priority queues (30 problems)

Rules and format: see [dsa.07-problem-plan.md](dsa.07-problem-plan.md). Ids `dsa.11.p001`…`p030`. Function style (`from solution import f`).
**Mix:** 9 drill, 10 applied, 9 deep, 2 challenge. Kinds: 24 code (incl. fix p016 and build p030), 4 trace, 2 explain.
**assessment:** explain = p008, trace = p005, fix = p016, build = p030.
Tests for heap classes compare with `heapq`/`sorted` on random operation sequences (fixed seed). Ties: tests use unique priorities unless the problem is about ties.

## Conventions (pin these in every statement that needs them)
- **0-based array layout** exactly as the chapter: `parent(i) = (i-1)//2`, `left(i) = 2i+1`, `right(i) = 2i+2`. `parent` is only asked for `i >= 1` (`parent(0)` is -1 with `//` but 0 with `int()`: do not test it).
- **Textbook pop** (chapter section 3): last item goes to the root, then `sift_down` with the SMALLER child. `heapq.heappop` uses a different route (sink to a leaf, then sift up), so its intermediate arrays can differ. Trace problems get their expected lines from the chapter's algorithm, printed by the code that is in `problem.md`, never from `heapq`.
- Signatures: `sift_up(a, i)` and `sift_down(a, i, n)` (only `a[:n]` counts), both in place. `MinHeap.pop()` and `peek()` on an empty heap raise `IndexError`.
- From-scratch problems (p003, p004, p006, p009, p030) are checked by AST: the solution must not import `heapq` and must not call `sorted` or `.sort`. Otherwise they are one line long.
- Course supports Python 3.11: tests and references must not use `heapq.heappush_max` / `heappop_max` / `heapify_max` (3.14 only). A max-heap is made by negation (hints say so).
- Tests count work, not seconds, where they can: a wrapper class `Counted` whose `__lt__` counts comparisons. Where a time limit is needed, run the learner's code in a subprocess with a timeout (as dsa.09 p018 did). No absolute-time asserts in-process.
- Explain problems are self-rated against `answer.md` (a checklist of terms); nothing is machine-graded.

## A. The array layout, push and pop (Ch. 2–3)
| # | Title | Tier | Kind | Idea / tests |
|---|---|---|---|---|
| 1 | Indices in the array layout | drill | code | `parent(i)`, `left(i)`, `right(i)`; also `children(i, n)` that drops indices `>= n` |
| 2 | Is this array a min-heap? | drill | code | empty, 1 item, equal items, a heap that is valid except for one leaf |
| 3 | Sift up | drill | code | in place; check the heap property afterwards and that the multiset is unchanged |
| 4 | Sift down | drill | code | in place with the `n` limit (items at index `>= n` must not move) |
| 5 | Trace a pop | drill | trace | `⚠ HAND-TRACE` array after each swap during the chapter's `pop` on a 7-item heap (the code is in `problem.md`; expected lines come from running it, then check by hand) |
| 6 | MinHeap class | applied | code | `push/pop/peek/__len__`, `MinHeap(items)` builds bottom-up; differential test vs `heapq` on 2,000 random ops (fixed seed); build from a list must use at most `2n` comparisons (`Counted`), while `n` pushes use many more; AST ban |

## B. Building a heap, heap sort (Ch. 4–6)
| # | Title | Tier | Kind | Idea / tests |
|---|---|---|---|---|
| 7 | Trace heapify | applied | trace | `⚠ HAND-TRACE` array after each sift-down in bottom-up heapify of `[9,4,7,1,6,2,8]` (4 swaps; final `[1,4,2,9,6,7,8]`, checked by hand and by running) |
| 8 | Why heapify is O(n) | deep | explain | `answer.md` checklist: "most nodes are near the bottom", "a node's work is its height, not log n", "sum of heights", compare with n pushes |
| 9 | Heap sort | applied | code | in place on the same list object, `heap_sort(a, reverse=False)`; duplicates; empty; AST ban |

## C. `heapq` and top-K (Ch. 5, 7)
| # | Title | Tier | Kind | Idea / tests |
|---|---|---|---|---|
| 10 | Max-heap with heapq | drill | code | negation; ints and floats; do not mutate the input |
| 11 | Heap of tuples | drill | code | `(priority, counter, item)`; items that cannot be compared must still work (test uses dicts) |
| 12 | K largest elements | drill | code | min-heap of size k, result descending; `k` greater than `n`, `k = 0`; `Counted` items: at most `4n` comparisons (a full sort needs about `n log n`); AST ban on `sorted`, `.sort`, `nlargest`, `nsmallest` |
| 13 | K-th largest in a stream | applied | code | class `KthLargest(k, nums)` with `add(val)`; **returns `None` while fewer than k numbers have been seen**; initial list shorter than k |
| 14 | K most frequent words | applied | code | tie → alphabetical order; result ordered by (count desc, word asc) |
| 15 | K closest points to the origin | applied | code | compare squared distances, no sqrt; result ordered by (distance, x, y) |
| 16 | Fix the top-k | applied | code | `assessment = "fix"`; the starter keeps a size-k heap but of the wrong kind (a negated heap keeps the k SMALLEST) and crashes for `k = 0`; each failing test names the cause. Not a time-limit fix: a size-n heap with k pops is still `O(n + k log n)` |

## D. Two heaps (Ch. 8)
| # | Title | Tier | Kind | Idea / tests |
|---|---|---|---|---|
| 17 | Running median | deep | code | stream class `add`/`median`; compare with `statistics.median` on random streams, odd and even counts |
| 18 | Trace the two heaps | deep | trace | `⚠ HAND-TRACE` the chapter's `MedianFinder.add` (push to low, move top to high, rebalance) on 6 numbers; print the SORTED contents of both heaps and the median after each add (heap-internal order is not asked) |
| 19 | Sliding window median | challenge | code | two heaps with lazy deletion; compare with brute force on random inputs; even k returns `(a+b)/2`; one big case for efficiency in a subprocess. The chapter shows lazy deletion (section 11) and two heaps (section 8) but not the combination: statement and hints walk through it |

## E. Merging (Ch. 9)
| # | Title | Tier | Kind | Idea / tests |
|---|---|---|---|---|
| 20 | Merge k sorted lists with a heap | applied | code | list of lists in, one sorted list out; empty lists inside; duplicates; compare with `sorted(chain)`. (The lazy generator version is "another way" in `solution.md`, not graded) |
| 21 | K-th smallest in a sorted matrix | deep | code | rows and columns sorted; compare with sorting the flattened matrix; one 500×500 case in a subprocess |
| 22 | K smallest pair sums | deep | code | two sorted lists, k pairs with the smallest sums, lazy exploration; two inputs of 10**5 numbers with k = 100 in a subprocess (the full product has 10**10 pairs); ties: compare the sums only |

## F. Greedy with a heap (Ch. 10)
| # | Title | Tier | Kind | Idea / tests |
|---|---|---|---|---|
| 23 | Connect the sticks | drill | code | minimal total cost; one stick = 0; empty = 0 |
| 24 | Meeting rooms II | applied | code | rooms needed; touching intervals (end == start) do not overlap |
| 25 | Reorganise a string | deep | code | return any valid; the test validates (same letters, no equal neighbours); impossible → `""` |
| 26 | Task scheduler with cooldown | challenge | code | least time units with a cooldown `n` between equal tasks, idle slots count; brute force (search over states) on tiny inputs. Not taught in the chapter: statement and hints explain the greedy |
| 27 | Shortest job first | applied | trace | `⚠ HAND-TRACE` the chapter's `sjf_average_wait` with a print per scheduling decision; 5 jobs, one idle gap, one tie on duration (ties: duration, then arrival, then input index) |

## G. Updates and removals (Ch. 11)
| # | Title | Tier | Kind | Idea / tests |
|---|---|---|---|---|
| 28 | Why not change an item inside the heap? | deep | explain | demonstrate on a small heap that editing a priority in place breaks the invariant; `answer.md` checklist: "the item is not moved", "parent/child order breaks", "pop returns a wrong item", lazy deletion or sift after the edit |
| 29 | Priority queue with updates (lazy deletion) | deep | code | built on `heapq`: `add(task, priority)` (also changes), `remove(task)`, `pop()` (best priority; equal priorities leave in the order they were last added), `__len__`, `stored()` = entries in the heap including stale ones; random ops vs a dict model; after 10**5 changes of 5 tasks `stored()` must stay `<= 4 * len + 8` (rebuild when stale entries exceed half, chapter "The cost of laziness") |
| 30 | Build an indexed priority queue | deep | code | `assessment = "build"`; hand-written indexed heap (a position dictionary): `push/update/remove/pop_min/peek`, `__len__`, `stored()` that ALWAYS equals `len()` (no stale entries); ops vs a dict+`min` model; AST ban on `heapq`. The chapter only names the indexed heap, so the hints teach it |

## Counts
Tiers 9 drill / 10 applied / 9 deep / 2 challenge. Traces: p005, p007, p018, p027 (4). Explain: p008, p028 (2). Fix: p016. Build: p030. Everything else is code (24 incl. fix and build). The old closing paragraph wanted 7 traces and 4 explains, which did not match the table, and said p2 and p19 could become explains (they are code); it was replaced.

## Changes against the first draft (made 2026-11-16)
1. Order follows the chapter: the heapify trace and the "why O(n)" explain now come after the MinHeap class (old p5/p7/p8 became p8/p5/p7); the explain on in-place edits (old p29) now comes BEFORE the lazy-deletion queue (p28 / p29). Assessment ids changed: explain p008, trace p005.
2. p016 was "a size-n heap that passes only small tests, time limit on 10**5": not a bug a time limit can show (heapify plus k pops is also fast). Now a wrong-direction heap plus the `k = 0` crash.
3. p029 and p030 overlapped (both "priority queue with updates"): now lazy deletion on `heapq` against a hand-written indexed heap, told apart by `stored()`.
4. p006 also tests the O(n) build (comparison count), the only place where heapify is coded.
5. p012 "counter forbids full sort" is now a concrete comparison-count wrapper plus an AST ban; p022 "counter on pushes" (not observable from outside) became a subprocess time limit on huge inputs; p020 "generator bonus" removed (it cannot be tested as a bonus).
6. Pinned: 0-based layout, textbook pop (not `heapq`'s), `None` from `KthLargest.add` before k numbers, output orders for p014/p015, tie rules for p027/p029, sorted-content printing for p018, no 3.14-only `heapq` functions.
7. Premium LeetCode problems removed from the real-site list.

## Real-site problems (`external.toml`)
Free LeetCode only, slugs written from memory and unverified: `kth-largest-element-in-an-array`, `kth-largest-element-in-a-stream`, `top-k-frequent-elements`, `top-k-frequent-words`, `k-closest-points-to-origin`, `find-median-from-data-stream`, `sliding-window-median`, `merge-k-sorted-lists`, `kth-smallest-element-in-a-sorted-matrix`, `find-k-pairs-with-smallest-sums`, `last-stone-weight`, `meeting-rooms-iii`, `reorganize-string`, `task-scheduler`, `ipo`, `smallest-range-covering-elements-from-k-lists`, `furthest-building-you-can-reach`, `minimum-number-of-refueling-stops`. Dropped because they are LeetCode Premium: `meeting-rooms-ii`, `minimum-cost-to-connect-sticks` (the module's own p023 and p024 cover them). CSES: 1164 Room Allocation and 1076 Sliding Window Median (ids from memory, unverified); no Codeforces (none verified). The chapter teaches the smallest range (section 9) but the plan has no own problem for it: it is on the real-site list.
