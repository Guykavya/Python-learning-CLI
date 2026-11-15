# Problem plan: dsa.08 Stacks and queues (40 problems)

Rules, format and the meaning of `⚠ HAND-TRACE`: see [dsa.07-problem-plan.md](dsa.07-problem-plan.md) and [free-tier-authoring.md](../guides/free-tier-authoring.md). Ids `dsa.08.p001`…`p040`.
**Mix:** 12 drill, 15 applied, 8 deep, 5 challenge. Kinds: 34 code, 4 trace, 2 explain. **assessment:** explain = p007, trace = p015, fix = p021, build = p040.
Tests for design problems (min stack, queue from stacks) compare against a plain list/deque model on random operation sequences (fixed seed).

| # | Title | Tier | Kind | Idea / what the tests check |
|---|---|---|---|---|
| 1 | Reverse a string with a stack | drill | code | list as stack; empty, 1 char, unicode |
| 2 | Stack class with safe `pop` | drill | code | `Stack` with `push/pop/peek/is_empty`; pop on empty raises `IndexError` with message |
| 3 | Queue with deque | drill | code | `Queue` class; FIFO order; `popleft` O(1) check via 10**5 operations within a time limit |
| 4 | Last k values average | drill | code | `deque(maxlen=k)`; fewer than k values |
| 5 | Palindrome check from both ends | drill | code | deque, pop both ends; even/odd length |
| 6 | Trace a stack | drill | trace | `⚠ HAND-TRACE` stack contents after each of 8 push/pop ops, expected as list of snapshots |
| 7 | Why not `list.pop(0)` for a queue? | drill | explain | explain cost; graded by terms ("shift", "O(n)", "deque") |
| 8 | Valid brackets | drill | code | `()[]{}`; empty string True; `"(]"`, `"(("`, `")("`; message names the case |
| 9 | Position of the first bracket error | applied | code | return index or -1; `"(()"` reports unclosed index; `⚠ HAND-TRACE` the expected indices |
| 10 | Longest valid parentheses | deep | code | `")()())"` → 4; stack of indices; brute-force comparison on random strings |
| 11 | Minimum brackets to add | applied | code | counter or stack; both directions of imbalance |
| 12 | Evaluate postfix | drill | code | `["2","1","+","3","*"]` → 9; division truncates toward zero; negative numbers |
| 13 | Infix to postfix (shunting-yard) | deep | code | `+ - * / ( )` with precedence; compare evaluated result with `eval` on random expressions (safe generator) |
| 14 | Basic calculator with parentheses | challenge | code | `"2-(5-6)"`, spaces, unary minus; compare with `eval` on generated cases |
| 15 | Trace shunting-yard | applied | trace | `⚠ HAND-TRACE` output queue and operator stack after each token of `3+4*2/(1-5)` |
| 16 | Simplify a Unix path | applied | code | `/a/./b/../../c/` → `/c`; root edge cases `/../` |
| 17 | Decode a nested string | applied | code | `3[a2[c]]` → `accaccacc`; multi-digit counts |
| 18 | Remove adjacent duplicates | drill | code | `"abbaca"` → `ca`; empty result |
| 19 | Backspace string compare | applied | code | `#` as backspace; O(1) space variant bonus test on long inputs |
| 20 | Min stack | applied | code | `push/pop/top/get_min` O(1); random operation test against a list model |
| 21 | Fix the broken min stack | applied | code | `assessment = "fix"`; given a min stack that forgets the old minimum after a pop of equal values |
| 22 | Queue from two stacks | applied | code | amortised O(1); random ops vs deque model |
| 23 | Stack from one queue | applied | code | only `deque` append/popleft allowed (test wraps the deque and counts forbidden calls) |
| 24 | Undo and redo | applied | code | editor with `type`, `undo`, `redo`; typing after undo clears redo; `⚠ HAND-TRACE` one scripted session |
| 25 | Trace next greater element | drill | trace | `⚠ HAND-TRACE` stack contents and answer array while processing `[2,1,2,4,3]` |
| 26 | Next greater element | drill | code | return `-1` when none; equal values are not "greater"; brute-force compare |
| 27 | Next greater element II (circular) | applied | code | loop twice; `[1,2,1]` → `[2,-1,2]` |
| 28 | Daily temperatures | applied | code | distance to the next warmer day; 10**5 values within the time limit |
| 29 | Stock span | applied | code | span = days back not higher; stream class `next(price)`; trace example given in the statement |
| 30 | Why is the monotonic stack O(n)? | deep | explain | argument "each index pushed and popped once"; graded by terms |
| 31 | Trace the sliding window deque | deep | trace | `⚠ HAND-TRACE` deque (indices) after each step for `[1,3,-1,-3,5,3,6,7]`, k=3 |
| 32 | Sliding window maximum | deep | code | `O(n)`; k=1, k=n, decreasing and increasing input; time limit |
| 33 | Remove k digits | deep | code | smallest number; leading zeros stripped; result `"0"` for empty |
| 34 | Largest rectangle in a histogram | deep | code | brute-force compare on random small inputs; 10**5 bars in time |
| 35 | Trapping rain water | deep | code | stack or two-pointer; known examples; flat and V shapes |
| 36 | Sum of subarray minimums | challenge | code | contribution technique; mod 10**9+7; brute-force compare |
| 37 | Maximal rectangle of 1s | challenge | code | rows as histograms; `⚠ HAND-TRACE` one 4x5 example |
| 38 | Shortest path in a grid with BFS | applied | code | 4 directions, `-1` if blocked; mark visited on enqueue (message about duplicates) |
| 39 | Rotting oranges (multi-source BFS) | challenge | code | minutes until all rot or `-1`; empty grid |
| 40 | Build a bounded task scheduler | challenge | code | `assessment = "build"`; round robin with quantum and a ready queue; tests print the exact finish order; `⚠ HAND-TRACE` |

## Counts

Trace: 6, 9?, 15, 24?, 25, 31 are the hand-traced ones; to reach 10 traces turn p9, p16, p29 and p37 into pure trace questions if the author prefers. Explain: 7, 30 plus p23, p35 and p4 as short written-reason variants if exactly 5 is wanted. Exact numbers matter less than: one `assessment` of each kind, and every test hand-checked.

## Real-site problems (`external.toml`)
LeetCode `valid-parentheses`, `min-stack`, `implement-queue-using-stacks`, `implement-stack-using-queues`, `daily-temperatures`, `next-greater-element-i`, `next-greater-element-ii`, `online-stock-span`, `largest-rectangle-in-histogram`, `maximal-rectangle`, `trapping-rain-water`, `sliding-window-maximum`, `remove-k-digits`, `decode-string`, `simplify-path`, `basic-calculator`, `evaluate-reverse-polish-notation`, `longest-valid-parentheses`, `rotting-oranges`, `shortest-path-in-binary-matrix`; CSES 1073 is in dsa.06 already; Codeforces to be chosen and verified. Ids unverified.
