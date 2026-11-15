# Problem plan: dsa.17 Competitive programming in Python (20 problems)

Rules and format: see [dsa.07-problem-plan.md](dsa.07-problem-plan.md). Ids `dsa.17.p001`…`p020`.
This module teaches contest habits, so problems are **script style** (stdin → stdout) with a `run()` helper in the tests, unlike the function-style modules. Time limits are real: the runner measures wall time, and each slow variant must fail with a message naming the cause (slow `input()`, `+=` on strings, recursion). Starter files must never read an input that a test makes huge in a way that could exhaust memory (use small defaults).
**Mix:** 7 drill, 8 applied, 4 deep, 1 challenge. Kinds: 15 code, 3 trace, 2 explain. **assessment:** explain = p003, trace = p009, fix = p012, build = p020.

| # | Title | Tier | Kind | Idea / tests |
|---|---|---|---|---|
| 1 | Read the constraints | drill | code | given n and a time limit, print the largest complexity class allowed (table in the statement); 10 cases |
| 2 | Sum of numbers with `sys.stdin` | drill | code | 2·10**5 numbers; `input()` version fails the time limit (message) |
| 3 | Why is `input()` slow? | drill | explain | graded by terms ("flush", "buffer", "readline", "per call") |
| 4 | Fast output | drill | code | 2·10**5 lines; one `print` per line fails; `"\n".join` passes |
| 5 | Multiple test cases | applied | code | `t` cases; trap: reading one number per line vs a whole line; empty lines |
| 6 | Read until end of input | drill | code | no count given; trailing spaces |
| 7 | Parse a grid | applied | code | `n m` then n strings; 1000x1000 |
| 8 | Iterative DFS on a long chain | applied | code | 2·10**5 nodes; recursive version fails with RecursionError message |
| 9 | Trace the template | applied | trace | `⚠ HAND-TRACE` the output of a given `main()` for a tiny input, including the print order of buffered output |
| 10 | Modular arithmetic template | applied | code | `pow(a, b, m)`, inverse, factorials mod p; vs big-integer reference |
| 11 | nCr mod p with precomputed factorials | applied | code | 10**5 queries |
| 12 | Fix the TLE | applied | code | `assessment = "fix"`; given a correct but slow solution (string `+=`, `list.pop(0)`, `input()`), change data structures only |
| 13 | Count the operations | drill | trace | `⚠ HAND-TRACE` estimate: for 3 given loops decide AC or TLE at 10**8 simple ops/s; expected labels |
| 14 | Stress test harness | deep | code | write `stress(brute, fast, gen, n)`; the test plants a bug in `fast` and checks your harness finds a failing input and prints it |
| 15 | Generator for random trees | deep | code | valid connected acyclic graph; seeds reproducible |
| 16 | Minimise a failing input | deep | code | shrink a failing case by removing elements while it still fails |
| 17 | Reading a verdict | drill | trace | `⚠ HAND-TRACE` for 6 verdict descriptions (WA on test 2, TLE on test 17, RE, MLE…) choose the likely cause; expected labels |
| 18 | Contest plan and upsolve | applied | explain | write a 5-line plan for a 2-hour contest and what to upsolve; graded by required items (read all problems first, skip rule, time boxes) |
| 19 | A full contest problem set | challenge | code | three small problems A, B, C in one file, solved within a total time limit |
| 20 | Build your contest template | deep | code | `assessment = "build"`; `template.py` with fast IO, `solve()` per test case, helpers; the test runs it on four earlier problems |

## Counts
Traces: 9, 13, 17 explicit; make p1 and p10 "predict the result" variants for 5. Explain: 3, 18 plus p2 as a written variant for 3. One assessment of each kind.

## Real-site problems (`external.toml`)
Codeforces: pick 10 Div. 3 problems A–C (ids must be verified when writing; from memory 1520A, 1352A, 1367A as easy examples), CSES 1068 (Weird Algorithm), 1083 (Missing Number), 1069 (Repetitions), 1094 (Increasing Array), 1070, 1071, 1072 for fast-IO practice; LeetCode `sum-of-two-integers` not relevant. Verify every id.
