# Problem plan: dsa.16 Advanced data structures (30 problems)

Rules and format: see [dsa.07-problem-plan.md](dsa.07-problem-plan.md). Ids `dsa.16.p001`…`p030`.
**Mix:** 8 drill, 10 applied, 8 deep, 4 challenge. Kinds: 23 code, 5 trace, 2 explain. **assessment:** explain = p007, trace = p009, fix = p017, build = p030.
Every structure is tested against a **naive array** (`sum(a[l:r+1])`, `min(...)`, a list updated in place) on random operation sequences (fixed seed, 2,000 ops on n = 50), then a time test with n = 10**5 and 10**5 operations that makes an O(n) query fail with "too slow: each query must be O(log n)". Index convention (0-based, inclusive ranges) is stated in every statement.

| # | Title | Tier | Kind | Idea / tests |
|---|---|---|---|---|
| 1 | Prefix sums and why they stop working ✅ | drill | code | static queries; then a test with updates shows the O(n) cost (counter) |
| 2 | Segment tree: build and query sum ✅ | drill | code | recursive; n not a power of two; n=1 |
| 3 | Segment tree: point update ✅ | drill | code | random ops vs naive |
| 4 | Segment tree for min ✅ | applied | code | `inf` identity element |
| 5 | Segment tree for gcd ✅ | applied | code | identity 0 |
| 6 | Iterative (bottom-up) segment tree ✅ | deep | code | non-commutative merge test (string concatenation) to catch left/right order bugs |
| 7 | Why 4n nodes? ✅ | drill | explain | graded by terms ("height", "power of two", "2n") |
| 8 | Custom node: max subarray sum in a range ✅ | deep | code | node stores `(sum, best, prefix, suffix)` |
| 9 | Trace a range query ✅ | drill | trace | `⚠ HAND-TRACE` nodes visited for `query(2, 6)` on n = 8, and which are fully inside |
| 10 | Lazy propagation: range add, range sum ✅ | challenge | code | random ops vs naive |
| 11 | Lazy: range assign, range sum ✅ | challenge | code | tag order trap |
| 12 | Count of numbers in a range (merge sort tree or offline) ✅ | deep | code | |
| 13 | Fenwick tree: update and prefix sum ✅ | drill | code | 1-based internal indexing hidden behind 0-based API |
| 14 | Fenwick: range sum ✅ | drill | code | `prefix(r) - prefix(l-1)` |
| 15 | Fenwick: range update, point query ✅ | applied | code | difference array on a Fenwick |
| 16 | Trace the Fenwick update path ✅ | drill | trace | `⚠ HAND-TRACE` indices touched by `update(5)` and `prefix(13)` for n = 16 |
| 17 | Fix the Fenwick index bug ✅ | applied | code | `assessment = "fix"`; given `i += i & i` / index 0 loops forever |
| 18 | Count inversions ✅ | applied | code | coordinate compression; vs O(n²) |
| 19 | Count smaller numbers after self ✅ | applied | code | |
| 20 | K-th smallest with a Fenwick tree ✅ | deep | code | binary descent |
| 21 | Range sum with range update (two Fenwicks) ✅ | challenge | code | |
| 22 | Fenwick 2-D ✅ | deep | code | n x m grid; vs naive |
| 23 | Sparse table: range minimum ✅ | applied | code | O(1) query (counter); `log` table |
| 24 | Sparse table: why overlap is fine ✅ | applied | explain | min is idempotent, sum is not; graded by terms |
| 25 | Trace the sparse table ✅ | applied | trace | `⚠ HAND-TRACE` table rows for `[5,2,4,7,6,3,1,8]` |
| 26 | Square-root decomposition ✅ | applied | code | block size; range sum with updates |
| 27 | Mo's algorithm ✅ | challenge | code | distinct count in range; offline; vs naive |
| 28 | Trace Mo's order ✅ | deep | trace | `⚠ HAND-TRACE` query order and pointer moves for 5 queries |
| 29 | Which structure when? ✅ | deep | trace | `⚠ HAND-TRACE` choose per scenario (8 given) with expected labels, e.g. static range min → sparse table |
| 30 | Build a range-query library ✅ | deep | code | `assessment = "build"`; `FenwickTree`, `SegmentTree(merge, identity)`, `SparseTable` with a common test harness |

## Counts
Written 2026-11-19 as the table says: 8/10/8/4, 23 code, 5 traces (p009, p016, p025, p028, p029), 2 explain (p007, p024). The older idea of extra trace/explain variants was dropped. Ranges are half-open `[l, r)` in every problem, following the chapter (not the inclusive ranges this plan's header mentions). One assessment of each kind.

## Real-site problems (`external.toml`)
LeetCode `range-sum-query-mutable`, `range-sum-query-immutable`, `count-of-smaller-numbers-after-self`, `reverse-pairs`, `count-of-range-sum`, `the-skyline-problem`, `range-module`, `falling-squares`; CSES 1646 (Static Range Sum), 1647 (Static Range Minimum), 1648 (Dynamic Range Sum), 1649 (Dynamic Range Minimum), 1651 (Range Update Queries), 1652, 1190 (Subarray Sum Queries), 1143; Codeforces 380C, 339D to verify. Ids unverified.
