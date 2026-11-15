# Problem plan: dsa.07 Recursion and backtracking (45 problems)

Use with [docs/guides/free-tier-authoring.md](../guides/free-tier-authoring.md) and the format of dsa.06 (`problem.toml`, `problem.md`, `hints.md`, `solution.md`, `mistakes.md`, `test_solution.py`).
Function style (`from solution import f`). Ids `dsa.07.p001` … `p045`, folder `pNNN-slug`.

**Mix:** 14 drill, 14 applied, 12 deep, 5 challenge. Kinds: 30 code, 10 trace, 5 explain.
**One each of `assessment`:** explain = p008, trace = p013, fix = p027, build = p045.
**Tests:** compare answers as sorted lists (or sets of tuples) unless order is the point. **⚠ HAND-TRACE** marks tests with step-by-step expected output; trace them by hand before shipping (core.04.p058 lesson).
**Order inside the plan follows the chapter sections 1–17.** `Ch.` = chapter section.

## A. Recursion basics (Ch. 1–3)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | Sum of a list, recursively | drill | code | `total(xs)`; empty list = 0; tests with 1, 2, 1000 items (stay under the limit) |
| 2 | Power by repeated halving | drill | explain | explain why the simple `power(x, n)` crashes for n=10**6 and why halving fixes it; graded by terms ("recursion limit", "depth", "log") |
| 3 | Reverse a string | drill | code | no slicing `[::-1]`; empty, 1 char, palindrome, unicode char |
| 4 | Count down, then up | drill | trace | `⚠ HAND-TRACE` print order of a function that prints before and after the recursive call; ask for the exact printed lines |
| 5 | Is it a palindrome? | drill | code | two-ends recursion; ignore nothing (plain string); odd and even length |
| 6 | Flatten a nested list | deep | code | `flatten([1,[2,[3]],4])`; empty inner lists; depth 50 |
| 7 | Greatest common divisor | drill | code | Euclid recursively; (a,0), (0,b), equal numbers, coprime |
| 8 | Why does this recursion never stop? | drill | explain | four short snippets; name the missing base case or the step that does not shrink; graded by multiple-choice keywords |

## B. Call stack and recursion trees (Ch. 3–4)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 9 | Draw the call stack | drill | trace | `⚠ HAND-TRACE` maximum stack depth and total calls of `f(n)=f(n-1)+f(n-2)` for n=5 |
| 10 | Count the calls | applied | trace | `⚠ HAND-TRACE` how many calls `fib(5)` makes without a memo (15) and the call order; no code to write |
| 11 | Fibonacci with a memo dictionary | applied | code | `fib(300)` must finish fast; message about re-computed subproblems |
| 12 | Depth of a nested structure | deep | code | max depth of nested lists; empty list = 1; flat list |
| 13 | Trace the recursion tree of subsets | applied | trace | `⚠ HAND-TRACE` order in which `subsets([1,2,3])` visits the nodes (preorder list given as expected output) |
| 14 | Tower of Hanoi moves | deep | code | return list of `(from,to)` moves; n=1,2,3,4; length `2**n-1`; check each move legal by replaying |

## C. Backtracking template and subsets (Ch. 5–6)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 15 | All subsets | drill | code | `subsets(nums)` distinct input; count `2**n`; includes `[]` |
| 16 | Subsets with duplicates | applied | trace | `⚠ HAND-TRACE` which branches the skip rule cuts when generating subsets of `[1,2,2]`; give the visited nodes |
| 17 | Subset sum: does one exist? | applied | code | bool, early exit; negative numbers allowed; target 0 → True |
| 18 | Count subsets with a given sum | applied | code | return count; n=20 within a time limit |
| 19 | Binary strings of length n | drill | code | generate in lexicographic order; n=0 → `[""]` |

## D. Combinations and permutations (Ch. 7–8)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 20 | Combinations n choose k | drill | trace | `⚠ HAND-TRACE` the order of `combine(4, 2)` results and which start index each recursion level used |
| 21 | Combination sum (reuse allowed) | applied | code | candidates distinct; target 7, `[2,3,6,7]`; no repeated multisets |
| 22 | Combination sum II (use once) | deep | code | candidates with duplicates; result has no duplicate lists |
| 23 | All permutations | drill | code | `permute(nums)`; n=0, 1, 4 → 24; sorted comparison |
| 24 | Permutations with duplicates | deep | explain | explain why sorting plus the skip rule removes duplicate permutations; graded by terms ("sorted", "used", "previous") |
| 25 | Next permutation order by hand | deep | trace | `⚠ HAND-TRACE` the 6 permutations of `[1,2,3]` in the order the swap-based code produces them (differs from the used-array order) |
| 26 | k-th permutation (no full generation) | challenge | code | n=9, k=200000 must be instant; factorial number system; test with brute force on small n |

## E. Pruning (Ch. 9)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 27 | Fix the slow combination sum | applied | code | `assessment = "fix"`; given a version with no pruning that times out on `target=500`; add sort + `break`; test checks count of recursive calls via a counter passed in |
| 28 | Count the pruned calls | applied | trace | `⚠ HAND-TRACE` number of nodes visited for subset-sum on `[3,5,8]`, target 8, with and without the `remaining < 0` check |
| 29 | Partition into k equal subsets | challenge | code | `[4,3,2,3,5,2,1], k=4` → True; prune: sort descending, skip equal buckets |
| 30 | Why does sorting help here? | applied | explain | explain in 3 sentences, graded by required terms ("sorted", "break", "all later") |

## F. Grid backtracking: word search (Ch. 10)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 31 | Word search | deep | code | LeetCode-style; board must be unchanged after the call (message: "you forgot to un-mark") |
| 32 | Number of paths in a grid with obstacles | applied | code | 4 directions, no revisit; 3x3 open grid has 12 paths corner to corner; `⚠ HAND-TRACE` that count |
| 33 | Flood fill count of islands (recursive) | deep | code | recursive DFS; also a test of a 1x1 and of a 150x1 strip using an iterative fallback |
| 34 | Longest path in a small grid | challenge | code | max steps visiting each cell once, start anywhere; grids up to 4x4 |

## G. N-Queens and Sudoku (Ch. 11–12)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 35 | Count N-Queens solutions | applied | code | n=1..8 → 1,0,0,2,10,4,40,92; sets for columns and both diagonals |
| 36 | N-Queens boards | deep | code | return boards as list of strings; each board validated by the test, not compared to a fixed list |
| 37 | Is this queen placement safe? | drill | trace | `⚠ HAND-TRACE` for a 6x6 partial placement, which column indices are free for the next row |
| 38 | Sudoku: validate a board | drill | code | complete or partial; each row, column, box check; message names which unit failed |
| 39 | Sudoku solver | challenge | code | one easy and one medium puzzle; solved board must satisfy `validate`; unsolvable puzzle returns `None` |

## H. More classics (Ch. 13)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 40 | Generate parentheses | applied | trace | `⚠ HAND-TRACE` the order in which `generate_parentheses(3)` produces its 5 strings, and the `(open, close)` counts at each step |
| 41 | Letter combinations of a phone number | applied | code | `"23"` → 9 strings; empty string → `[]` |
| 42 | Palindrome partitioning | deep | code | `"aab"` → `[["a","a","b"],["aa","b"]]`; sorted compare |

## I. Cost, explicit stacks and judgement (Ch. 14–17)

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 43 | Subsets as a generator | deep | code | `iter_subsets` must be lazy: test takes `next()` 3 times on `range(40)` in under a second (starter must not `list()` the input) |
| 44 | Which problems need backtracking? | deep | explain | classify 8 short problem statements (backtracking, DP, greedy, plain loop) and justify one; graded by the label dictionary + keywords |
| 45 | Backtracking template by hand | challenge | code | `assessment = "build"`; write a generic `backtrack(choices, is_valid, is_done)` and use it for subsets and permutations; tests run it on 3 different problems |

## Counts check

Tiers 14 drill / 14 applied / 12 deep / 5 challenge. Kinds: 10 trace (4, 9, 10, 13, 16, 20, 25, 28, 37, 40), 5 explain (2, 8, 24, 30, 44), 30 code.
p2 and p24 are explain, and p10, p16, p20, p40 are trace: when writing them, keep the code-style title only if you add a small function the learner must call; otherwise make them pure questions with a printed answer file.
Rules that matter more than the numbers: exactly one `assessment` of each kind, and every item above has a hand-checked test.

## Real-site problems (`external.toml`)

Not yet written for dsa.07 (the module has `external: true`). Suggested ids, to be verified when written:
LeetCode `subsets`, `subsets-ii`, `permutations`, `permutations-ii`, `combinations`, `combination-sum`, `combination-sum-ii`, `generate-parentheses`, `letter-combinations-of-a-phone-number`, `palindrome-partitioning`, `word-search`, `n-queens`, `n-queens-ii`, `sudoku-solver`, `partition-to-k-equal-sum-subsets`; CSES 1624 (Chessboard and Queens), 1623 (Apple Division), 1622 (Creating Strings).
