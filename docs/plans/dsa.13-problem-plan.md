# Problem plan: dsa.13 Greedy algorithms (35 problems)

Rules and format: see [dsa.07-problem-plan.md](dsa.07-problem-plan.md). Ids `dsa.13.p001`…`p035`.
**Mix:** 13 drill, 12 applied, 8 deep, 2 challenge. Kinds: 30 code, 3 trace, 2 explain. **assessment:** explain = p006, trace = p011, fix = p019, build = p035.
Greedy tests: whenever a problem has a brute force (subsets, permutations, DP), the test compares the greedy answer with it on small random inputs. Several problems are "find the counterexample": the test runs the learner's input through greedy and through the optimal solver and checks they differ.

| # | Title | Tier | Kind | Idea / tests |
|---|---|---|---|---|
| 1 | Make change with the fewest coins (US coins) | drill | code | `[25,10,5,1]`; amounts 0..200 vs DP |
| 2 | When greedy change fails | drill | code | return an amount where greedy ≠ optimal for `[1,3,4]`; test checks with DP |
| 3 | Is this coin system canonical? | deep | code | brute check up to a bound; `[1,5,10]` true, `[1,3,4]` false |
| 4 | Fractional knapsack | drill | code | sort by value/weight; float compare |
| 5 | Why 0/1 knapsack breaks greedy | drill | explain | the answer includes a concrete instance; graded by running it |
| 6 | What is an exchange argument? | drill | explain | graded by terms ("swap", "no worse", "first choice") |
| 7 | Activity selection | drill | code | sort by finish time; touching intervals compatible; vs brute force |
| 8 | Wrong greedy rules for scheduling | applied | code | find inputs where "earliest start" and "shortest" fail; test validates by brute force |
| 9 | Minimum number of rooms | applied | code | |
| 10 | Non-overlapping intervals | applied | code | minimum removals |
| 11 | Trace activity selection | drill | trace | `⚠ HAND-TRACE` sorted list, chosen set, and last-finish after each step for 8 intervals |
| 12 | Merge intervals | drill | code | touching merge; unsorted input; one interval |
| 13 | Insert interval | applied | code | |
| 14 | Minimum arrows to burst balloons | applied | code | |
| 15 | Meeting rooms I | drill | code | |
| 16 | Platforms needed | applied | code | two sorted arrays sweep |
| 17 | Job sequencing with deadlines | applied | code | heap; vs brute force |
| 18 | Minimise maximum lateness | deep | code | earliest deadline first; vs permutations |
| 19 | Fix the shortest-job-first scheduler | applied | code | `assessment = "fix"`; given code that sorts jobs but never accumulates the wait time |
| 20 | Minimum waiting time | drill | code | |
| 21 | Jump game | drill | code | furthest reach |
| 22 | Jump game II | applied | code | minimum jumps; vs BFS |
| 23 | Gas station | applied | code | unique start; `-1`; vs brute force |
| 24 | Best time to buy and sell stock II | drill | code | sum of rises |
| 25 | Assign cookies | drill | code | sort both |
| 26 | Candy distribution | deep | code | two passes; vs brute force |
| 27 | Partition labels | applied | code | last occurrence |
| 28 | Largest number from an array | deep | code | custom comparison `a+b` vs `b+a`; leading zeros |
| 29 | Remove k digits (greedy view) | deep | code | smallest result; compare with brute force |
| 30 | Queue reconstruction by height | deep | code | |
| 31 | Trace Huffman coding | applied | trace | `⚠ HAND-TRACE` heap merges and the final code table for given frequencies |
| 32 | Huffman code lengths | deep | code | total bits; tie-independent total compared with a reference |
| 33 | Task scheduler (greedy count) | challenge | code | formula vs simulation |
| 34 | Minimum cost to connect sticks (greedy proof) | challenge | trace | `⚠ HAND-TRACE` merges and total cost for `[2,4,3,6]`, then a counterexample for "merge largest first" |
| 35 | Build a greedy checker | deep | code | `assessment = "build"`; function `is_greedy_safe(problem, instances)` that finds the first instance where greedy ≠ brute force; tests use 3 problems, one of them correct |

## Counts
Traces: 11, 31, 34 explicit; to reach 8 turn p9, p12, p21, p24, p27 into "write the result by hand" variants. Explain: 5, 6 plus p3, p8, p22 as written variants for 5. One assessment of each kind.

## Real-site problems (`external.toml`)
LeetCode `assign-cookies`, `jump-game`, `jump-game-ii`, `gas-station`, `best-time-to-buy-and-sell-stock-ii`, `candy`, `partition-labels`, `largest-number`, `queue-reconstruction-by-height`, `non-overlapping-intervals`, `merge-intervals`, `insert-interval`, `minimum-number-of-arrows-to-burst-balloons`, `meeting-rooms`, `meeting-rooms-ii`, `task-scheduler`, `lemonade-change`, `maximum-units-on-a-truck`; CSES 1629 (Movie Festival, already in dsa.05, skip), 1630 (Tasks and Deadlines), 1632, 1076, 1074 to verify. Ids unverified.
