# Problem plan: dsa.14 Dynamic programming (80 problems)

Rules and format: see [dsa.07-problem-plan.md](dsa.07-problem-plan.md). Ids `dsa.14.p001`…`p080`. Recommended: write this module in 4 sessions of 20 problems (A–B, C–D, E–F, G–H), on **Opus/high** because of the many hand-traced tables.
**Mix:** 21 drill, 32 applied, 20 deep, 7 challenge. Kinds: 70 code, 6 trace, 4 explain. **assessment:** explain = p010, trace = p024, fix = p050, build = p080.
Every DP problem's test compares the learner's answer with a **brute-force or recursive reference** on small random inputs, then runs a big input (n = 10**3 to 10**5) under a time limit, so a plain recursion without memo fails with the message "exponential: add a memo". Reconstruction problems are **validated**, not compared. Memory-reduction problems state the allowed memory (rolling arrays) in the statement; the test only checks time and result.

## A. Memo, tabulation, the recipe (Ch. 1–4)
| # | Title | Tier | Kind | Idea / tests |
|---|---|---|---|---|
| 1 | Fibonacci three ways | drill | code | naive, memo, table; `fib(5000)` big int; naive only up to 25 |
| 2 | Count the calls | drill | trace | `⚠ HAND-TRACE` number of calls for `fib(6)` with and without memo (25 vs 11) |
| 3 | Climbing stairs | drill | code | 1 or 2 steps; n up to 10**5 mod 10**9+7 |
| 4 | Climbing stairs with a set of steps | applied | code | steps given as list |
| 5 | Min cost climbing stairs | drill | code | |
| 6 | Tribonacci with rolling variables | drill | code | O(1) memory |
| 7 | State, transition, base case | drill | trace | `⚠ HAND-TRACE` fill the table of `ways(n)` for n=0..8, steps `{1,3,4}` |
| 8 | From memo to table | applied | code | rewrite given top-down code bottom-up; same answers on random inputs |
| 9 | Python recursion limit and DP | applied | code | n=10**4 top-down fails; solution uses a table or `lru_cache` with iteration |
| 10 | Why does memoisation work? | drill | explain | graded by terms ("overlapping", "same state", "repeated") |

## B. 1-D DP and coins (Ch. 5–7)
| # | Title | Tier | Kind | Idea / tests |
|---|---|---|---|---|
| 11 | House robber | drill | code | |
| 12 | House robber II (circle) | applied | code | |
| 13 | Maximum subarray (Kadane) | drill | code | all negative |
| 14 | Maximum product subarray | applied | code | zeros and negatives |
| 15 | Decode ways | applied | code | `"06"`, `"226"` |
| 16 | Word break | applied | code | set of words; 10**3 length |
| 17 | Coin change: fewest coins | drill | code | `-1`; amount 0; 10**4 |
| 18 | Coin change II: number of ways | applied | code | order does not matter; loop order trap (message) |
| 19 | Perfect squares | applied | code | |
| 20 | Combination sum IV (ordered ways) | deep | code | contrasts with p18 |
| 21 | Jump game as DP | applied | code | vs greedy |
| 22 | Longest valid chain of pairs | deep | code | |
| 23 | Paint houses | applied | code | 3 colours, no equal neighbours |
| 24 | Trace coin change | drill | trace | `⚠ HAND-TRACE` table for coins `[1,3,4]`, amount 6 |

## C. Grid DP, reconstruction (Ch. 8–9)
| # | Title | Tier | Kind | Idea / tests |
|---|---|---|---|---|
| 25 | Unique paths | drill | code | 1x1; large grid uses table; compare with `comb` |
| 26 | Unique paths with obstacles | applied | code | start/end blocked |
| 27 | Minimum path sum | drill | code | |
| 28 | Triangle | applied | code | bottom-up |
| 29 | Maximal square | deep | code | |
| 30 | Cherry pickup (two walkers) | challenge | code | |
| 31 | Dungeon game | deep | code | backwards DP |
| 32 | Minimum path with the path itself | applied | code | reconstruction validated: cost of returned path equals the answer |
| 33 | Coin change with the coins used | applied | code | validated: sums to amount and uses the minimum count |
| 34 | Longest path in a matrix (memo DFS) | deep | code | strictly increasing; memo |
| 35 | Trace grid DP | applied | trace | `⚠ HAND-TRACE` filled table for a 4x4 grid with two obstacles |

## D. Knapsack family (Ch. 10–12)
| # | Title | Tier | Kind | Idea / tests |
|---|---|---|---|---|
| 36 | 0/1 knapsack | drill | code | 2-D table then 1-D (backwards loop trap message) |
| 37 | 0/1 knapsack: which items | applied | code | validated reconstruction |
| 38 | Unbounded knapsack | drill | code | forwards loop |
| 39 | Rod cutting | drill | code | |
| 40 | Subset sum | drill | code | bitset trick as bonus test with 10**4 target |
| 41 | Partition equal subset sum | applied | code | |
| 42 | Target sum (+/-) | applied | code | transform to subset sum |
| 43 | Last stone weight II | deep | code | |
| 44 | Ones and zeroes (2-D knapsack) | deep | code | |
| 45 | Count subsets with sum | applied | code | zeros in the input |
| 46 | Minimum subset difference | applied | code | |
| 47 | Loop direction: 0/1 vs unbounded | applied | explain | explain why one goes backwards; graded by terms ("reuse", "same item twice", "backwards") |
| 48 | Trace 0/1 knapsack | applied | trace | `⚠ HAND-TRACE` the 1-D array after each item |
| 49 | Bounded knapsack with counts | deep | code | binary splitting |
| 50 | Fix the knapsack | applied | code | `assessment = "fix"`; given a 1-D version looping forwards, so items are reused |

## E. LIS, LCS, edit distance, palindromes (Ch. 13–16)
| # | Title | Tier | Kind | Idea / tests |
|---|---|---|---|---|
| 51 | LIS length O(n²) | drill | code | |
| 52 | LIS length O(n log n) | deep | code | 10**5; vs O(n²) |
| 53 | Count LIS | challenge | code | |
| 54 | Russian doll envelopes | challenge | code | sort trap on equal widths |
| 55 | LCS length | drill | code | |
| 56 | LCS string itself | applied | code | validated subsequence of both and of the right length |
| 57 | Edit distance | drill | code | empty strings; vs recursion |
| 58 | Edit distance operations | applied | code | validated sequence of edits |
| 59 | Longest palindromic subsequence | applied | code | |
| 60 | Longest palindromic substring | applied | code | expand around centre vs DP |
| 61 | Count palindromic substrings | applied | code | |
| 62 | Shortest common supersequence | deep | code | validated |
| 63 | Distinct subsequences | deep | code | |
| 64 | Interleaving string | deep | code | |
| 65 | Wildcard matching | challenge | code | `?` `*` |
| 66 | Regular expression matching | challenge | code | `.` `*`; vs `re.fullmatch` on a safe generator |
| 67 | Trace edit distance | drill | trace | `⚠ HAND-TRACE` the full table for `"kitten"` → `"sitting"` |
| 68 | Why is LIS O(n log n)? | deep | explain | tails array argument; graded by terms |

## F. Interval, tree, bitmask, digit DP (Ch. 17–20)
| # | Title | Tier | Kind | Idea / tests |
|---|---|---|---|---|
| 69 | Matrix chain multiplication | deep | code | |
| 70 | Burst balloons | challenge | code | brute-force on ≤ 8 balloons |
| 71 | Minimum score triangulation | deep | code | |
| 72 | Stone game (interval) | applied | code | |
| 73 | House robber III (tree) | applied | code | return pair per node |
| 74 | Tree: maximum independent set size | deep | code | |
| 75 | Binary tree cameras | challenge | code | three states |
| 76 | Traveling salesman (bitmask) | deep | code | n ≤ 12; vs permutations for n ≤ 7 |
| 77 | Partition to k equal sum subsets (bitmask) | deep | code | |
| 78 | Count numbers ≤ N with digit property | deep | code | digit DP; vs brute force up to 10**5 |
| 79 | DP, greedy or backtracking? | applied | explain | classify 8 statements, justify two |
| 80 | Build a DP debugger | deep | code | `assessment = "build"`; wrapper that records `(state → value)`, counts calls and detects missing base cases; tests use fib, coin change and a deliberately broken recursion |

## Counts
Tiers about 27/26/19/8 (adjust p29, p52, p60 if the totals are off). Traces: 2, 7, 24, 35, 48, 67 explicit; turn p1, p13, p25, p57, p76 into "fill the table by hand" variants for 12. Explain: 10, 47, 68, 79 plus p9 and p20 as written variants for 6. One assessment of each kind.

## Real-site problems (`external.toml`)
LeetCode `climbing-stairs`, `min-cost-climbing-stairs`, `house-robber`, `house-robber-ii`, `maximum-subarray`, `maximum-product-subarray`, `decode-ways`, `word-break`, `coin-change`, `coin-change-ii`, `perfect-squares`, `combination-sum-iv`, `unique-paths`, `unique-paths-ii`, `minimum-path-sum`, `triangle`, `maximal-square`, `dungeon-game`, `cherry-pickup`, `partition-equal-subset-sum`, `target-sum`, `last-stone-weight-ii`, `ones-and-zeroes`, `longest-increasing-subsequence`, `russian-doll-envelopes`, `longest-common-subsequence`, `edit-distance`, `longest-palindromic-subsequence`, `longest-palindromic-substring`, `palindromic-substrings`, `shortest-common-supersequence`, `distinct-subsequences`, `interleaving-string`, `wildcard-matching`, `regular-expression-matching`, `burst-balloons`, `house-robber-iii`, `binary-tree-cameras`, `partition-to-k-equal-sum-subsets`, `number-of-digit-one`; CSES 1633 (Dice Combinations), 1634, 1635, 1636, 1637, 1638, 1639, 1158, 1097, 1746 to verify. Ids unverified.
