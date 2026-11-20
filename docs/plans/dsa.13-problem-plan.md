# Problem plan: dsa.13 Greedy algorithms (35 problems)

Rules and format: see [dsa.07-problem-plan.md](dsa.07-problem-plan.md). Function style (`from solution import f`).
Ids `dsa.13.p001`…`p035`, folder `pNNN-slug`. **Order follows the chapter** (`Ch.` = chapter section).
**Mix:** 13 drill, 12 applied, 8 deep, 2 challenge. Kinds: 30 code, 3 trace, 2 explain.
**assessment:** explain = p001, trace = p003, fix = p018, build = p035.

**Greedy tests:** whenever a problem has a brute force (subsets, permutations, DP, BFS), the test compares the
learner's answer with it on many small seeded random inputs (`random.Random(seed)`), plus fixed edge cases.
"Find the counterexample" problems (p004, p015) run the learner's input through the wrong greedy and through
an optimal solver inside the test and check that they differ. Explain problems are self-rated against `answer.md`
(a checklist of the points a good answer makes), not graded by a test.

**Pinned rules (from the chapter, so tests and chapter agree):**
- Intervals are `(start, end)` pairs with `start <= end`, given as lists or tuples, unsorted unless stated.
- Activity selection, meeting rooms I, non-overlapping intervals: **touching intervals do not overlap** (`end == next start` is fine).
- Merge intervals: **touching intervals merge** (`[1,3]` and `[3,5]` become `[1,5]`).
- Arrows (balloons are closed intervals): touching balloons **share** one arrow.
- Platforms / rooms: use the chapter's rule in Ch. 6 for an arrival at the same time as a departure; state it in `problem.md`.
- Huffman (p031, p032): use the chapter's `heapq` implementation and tie-break from Ch. 13 exactly.

## A. What makes a greedy choice safe (Ch. 2–4)

| # | Title | Tier | Kind | Idea / tests |
|---|---|---|---|---|
| 1 | What is an exchange argument? | drill | explain | `assessment = "explain"`; explain it for activity selection; checklist: optimal solution O, swap its first choice for greedy's, "no worse", repeat on the rest |
| 2 | Activity selection | drill | code | earliest finish; return the count; touching OK; vs brute force over subsets (n ≤ 10) |
| 3 | Trace activity selection | drill | trace | `assessment = "trace"`; `⚠ HAND-TRACE` 8 intervals: sorted order, then for each step chosen/skipped and the last finish time |
| 4 | Wrong greedy rules for scheduling | applied | code | return one input where "earliest start" fails and one where "shortest first" fails; test checks each with brute force |

## B. Interval variants (Ch. 5–6)

| # | Title | Tier | Kind | Idea / tests |
|---|---|---|---|---|
| 5 | Non-overlapping intervals | applied | code | minimum removals; vs brute force |
| 6 | Minimum arrows to burst balloons | applied | code | closed intervals; vs brute force |
| 7 | Merge intervals | drill | code | touching merge; unsorted input; one interval; empty list |
| 8 | Insert interval | applied | code | sorted, non-overlapping input; new one before, after, inside, covering all |
| 9 | Meeting rooms I | drill | code | can one person attend all; touching OK |
| 10 | Assign meetings to rooms | applied | code | return a room number for each meeting (in input order); test checks no clash in a room and room count = max depth (vs brute force count) |
| 11 | Platforms needed | applied | code | two sorted arrays sweep; chapter's same-time rule; vs O(n²) count |

## C. Knapsack and coins (Ch. 7–9)

| # | Title | Tier | Kind | Idea / tests |
|---|---|---|---|---|
| 12 | Fractional knapsack | drill | code | sort by value/weight; float compare with `math.isclose`; capacity 0; zero-value items |
| 13 | Why 0/1 knapsack breaks greedy | drill | explain | self-rated; model answer gives a concrete instance and why the exchange argument breaks |
| 14 | Make change with the fewest coins (US coins) | drill | code | `[25,10,5,1]`; amounts 0..200 vs DP |
| 15 | When greedy change fails | drill | code | return an amount where greedy ≠ optimal for `[1,3,4]`; test checks with DP |
| 16 | Is this coin system canonical? | deep | code | check up to the chapter's bound; `[1,5,10]` true, `[1,3,4]` false; vs full DP check |

## D. Scheduling (Ch. 10)

| # | Title | Tier | Kind | Idea / tests |
|---|---|---|---|---|
| 17 | Minimum waiting time | drill | code | shortest first; vs permutations (n ≤ 7) |
| 18 | Fix the shortest-job-first scheduler | applied | code | `assessment = "fix"`; given code sorts jobs but never accumulates the wait time (and one more small bug); starter fails, fixed passes |
| 19 | Job sequencing with deadlines | applied | code | max profit, unit-time jobs; heap or slots; vs brute force |
| 20 | Minimise maximum lateness | deep | code | earliest deadline first; vs permutations |

## E. Greedy on arrays (Ch. 11)

| # | Title | Tier | Kind | Idea / tests |
|---|---|---|---|---|
| 21 | Assign cookies | drill | code | sort both; vs brute force matching |
| 22 | Jump game | drill | code | furthest reach; zeros; one element |
| 23 | Jump game II | applied | code | minimum jumps; vs BFS |
| 24 | Gas station | applied | code | unique start or `-1`; vs brute force |
| 25 | Best time to buy and sell stock II | drill | code | sum of rises; vs DP |
| 26 | Candy distribution | deep | code | two passes; vs brute force (small n, small values); hints teach the two passes (not in the chapter) |
| 27 | Partition labels | applied | code | last occurrence; hints teach it (not in the chapter) |

## F. Numbers and strings (Ch. 12)

| # | Title | Tier | Kind | Idea / tests |
|---|---|---|---|---|
| 28 | Largest number from an array | deep | code | compare `a+b` vs `b+a`; all zeros gives `"0"`; vs permutations |
| 29 | Remove k digits | deep | code | smallest result; no leading zeros; empty gives `"0"`; vs brute force |
| 30 | Queue reconstruction by height | deep | code | tallest first, insert at k; vs permutations check; hints teach it |

## G. Huffman (Ch. 13)

| # | Title | Tier | Kind | Idea / tests |
|---|---|---|---|---|
| 31 | Trace Huffman coding | applied | trace | `⚠ HAND-TRACE` heap merges in order and the final code table for given frequencies, using the chapter's code and tie-break |
| 32 | Huffman code lengths | deep | code | total bits (tie-independent); one symbol; vs reference and a brute-force optimal tree for ≤ 6 symbols |

## H. Harder problems and checking greedy (Ch. 14–16)

| # | Title | Tier | Kind | Idea / tests |
|---|---|---|---|---|
| 33 | Task scheduler (greedy count) | challenge | code | formula vs simulation; hints teach the formula |
| 34 | Minimum cost to connect sticks | challenge | trace | `⚠ HAND-TRACE` given code: merges and total cost for `[2,4,3,6]` smallest-first, then the same with largest-first, ending with both totals |
| 35 | Build a greedy checker | deep | code | `assessment = "build"`; `first_counterexample(greedy, brute, instances)` returns the first instance where they differ, else `None`; plus a random-instance stress helper (Ch. 15); tests use 3 problems, one where greedy is correct |

## Real-site problems (`external.toml`)

Already used in earlier modules, so **not** repeated here: merge-intervals, insert-interval, non-overlapping-intervals,
minimum-number-of-arrows-to-burst-balloons, largest-number, meeting-rooms(-ii) (Premium), task-scheduler, remove-k-digits;
CSES 1629, 1630, 1076.
Use (free LeetCode): assign-cookies, jump-game, jump-game-ii, gas-station, best-time-to-buy-and-sell-stock-ii, candy,
partition-labels, queue-reconstruction-by-height, lemonade-change, maximum-units-on-a-truck, boats-to-save-people,
two-city-scheduling, hand-of-straights, valid-parenthesis-string, wiggle-subsequence. CSES (ids from memory, unverified):
1074 Stick Lengths, 1090 Ferris Wheel, 1631 Reading Books, 1632 Movie Festival II.
