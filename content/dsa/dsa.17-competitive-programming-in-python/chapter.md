# dsa.17 Competitive programming in Python

## 1. What a programming contest is

A programming contest is a timed exam where the questions are programs. You get a set of problems. Each problem says what the input looks like, what output is wanted, and how large the input can be. You write a program, submit it to a **judge** (a server), and the judge runs it on many hidden tests. You get a **verdict** back: accepted, or one of several kinds of failure.

Nothing in this module teaches a new algorithm. Dsa.01 to dsa.16 gave you the algorithms. This module teaches the **craft around them**:

- how to read a statement and know, before writing any code, how fast your solution must be;
- how to read input and write output quickly, because in Python the input can cost more than the algorithm;
- how to survive deep recursion;
- how to choose between CPython and PyPy and what each one is bad at;
- how to test your solution against a brute force before the judge sees it;
- how to spend two hours of contest time, and how to learn from a contest afterwards.

The outcome of the module is practical: you will take part in a live contest and then **upsolve** it (solve the problems you could not solve during the contest, afterwards, with the editorial allowed).

### The shape of every contest

Whatever the website, a contest has the same parts.

1. **A clock.** Usually 2 to 3 hours. Sometimes 90 minutes. Problems are available from the first second.
2. **A problem set**, usually sorted from easy to hard. On Codeforces they are labelled A, B, C, and so on.
3. **A judge** that compiles or runs your code with a **time limit** (often 1 to 3 seconds per test) and a **memory limit** (often 256 MB).
4. **Hidden tests.** You see only the examples in the statement. The hidden tests include the largest allowed inputs and nasty corner cases.
5. **A scoreboard** that ranks everyone.

### The main platforms

| Platform | Typical format | Scoring | Notes |
|---|---|---|---|
| **Codeforces** | 2 hours, 5 to 8 problems, "Div. 2", "Div. 3", "Div. 4", "Educational" | Points per problem that drop with time; wrong submissions cost penalty | Has **hacking** and a public rating. The main target of this module |
| **ICPC style** | 5 hours, teams of 3, one computer per team | Number of problems solved, ties broken by total penalty time | Each wrong submission adds 20 minutes. Used at university contests |
| **AtCoder** | 100 minutes, 6 to 8 problems, "ABC", "ARC", "AGC" | Fixed points per problem, penalty only for wrong submissions | Very clean statements, no hacking, strong mathematical flavour |
| **CodeChef** | "Starters" (2 to 3 hours) and longer "Long Challenges" | Points per problem, partial scoring in some | Strong in India, many contests, some with subtasks |
| **LeetCode** | Weekly and biweekly, 90 minutes, 4 problems | Points per problem, time penalty | Function style (you write a function, no input parsing). Not the topic of this module's IO sections |
| **HackerRank, HackerEarth, CSES** | Practice sets and occasional contests | Mostly accepted or not | CSES is a fixed problem set, very good for training |

Codeforces divisions are defined by rating. Div. 1 is for strong participants, Div. 2 for the broad middle, Div. 3 and Div. 4 are easier contests (Div. 4 has the simplest problems of all), and Educational rounds are close to Div. 2 in difficulty with a teaching focus. For a first contest, a **Div. 3 or Div. 4** is the friendliest choice. Check the schedule on the site; the format changes over the years, so treat this table as a guide, not as rules.

### Two ways to be judged on a problem

- **Accepted/rejected on all tests (Codeforces, AtCoder, ICPC).** One failing hidden test means no credit.
- **Partial scoring (CodeChef, some others).** The statement lists **subtasks** with smaller limits. A slow solution can still earn points on small subtasks. That is a good place to practise: you can submit a brute force and get something.

### What "Python" means in a contest

Most contest judges accept both **CPython** (the normal `python3`) and **PyPy** (a different Python with a just-in-time compiler). On Codeforces you pick the language per submission, for example "Python 3" or "PyPy 3". Section 9 is about this choice. Until then, we write code that is correct on both, and we use CPython to test it on your machine.

Python is not the fastest contest language and everyone knows it. Problem setters choose time limits for C++. Python can still solve a large share of problems, up to roughly Codeforces rating 1800 to 2000 with care, and the rest of the module is about making that care systematic.

### Conventions in this chapter

- `n` is the size of the main input, `t` the number of test cases, `q` the number of queries.
- "Simple operation" means one arithmetic step, comparison, or list read/write.
- Timings printed in this chapter are **machine-specific**: your numbers will differ, but the *ratios* between two methods should look similar. Everything else (outputs, counts) is exact.
- All code was run with CPython 3.14. Nothing here needs a newer feature than dsa.01 to dsa.16 gave you, except the small standard-library modules named in each section (`sys`, `io`, `time`, `threading`, `random`, `subprocess`).

## 2. Reading the constraints: how fast must I be?

This is the single most useful skill in a contest. Before you think about the solution, look at the **constraints** and ask: *how many steps may my program take?*

### The rule of 10^8

A judge allows about 1 to 2 seconds. A fast language does about `10^8` to `10^9` simple operations per second. So we plan for **about `10^8` simple operations** in the worst case. This number is approximate. It is the right order of magnitude, and it lets you rule out ideas quickly.

Python (CPython) is much slower. Plan for roughly `10^7` simple operations per second in CPython, and a few times to a few tens of times more in PyPy for plain loops. We measure this on your own machine in the next section, so you do not need to trust any figure.

### The table: n against the intended algorithm

If the statement says `n <= N`, the intended solution probably has the complexity in this table.

| Largest `n` | Intended complexity | Typical algorithms |
|---|---|---|
| up to 10 | `O(n!)` | Try all permutations, brute force |
| up to 20 to 25 | `O(2^n)` or `O(2^n * n)` | Subsets, bitmask DP, meet in the middle at 40 |
| up to 100 | `O(n^3)` or `O(n^4)` | Floyd-Warshall, 3-nested-loop DP |
| up to 500 | `O(n^3)` | Floyd-Warshall, matrix-chain DP |
| up to 5,000 | `O(n^2)` | Quadratic DP (LCS, knapsack), all pairs |
| up to 10^5 | `O(n log n)` | Sorting, heaps, segment tree, binary search, Dijkstra |
| up to 10^6 | `O(n)` or `O(n log n)` with a tiny constant | Prefix sums, two pointers, sieve, BFS |
| up to 10^7 and up | `O(n)` with very small constant, or `O(log n)`, or `O(1)` | Math formula, sieve, closed form |
| up to 10^18 | `O(log n)` or `O(sqrt n)` at 10^12 | Binary search on answer, fast power, number theory |

Why does this table work? Because setters choose `n` so that the **intended** solution barely fits the time limit and the **slower, natural** solution does not. A statement with `n <= 2 * 10^5` is telling you "a quadratic solution is wrong". A statement with `n <= 20` is telling you "exponential is fine".

### Let us compute it

Instead of memorising, compute. The program below prints, for several `n`, how many operations common growth rates need. A value above `10^8` is marked as too slow for one second in a fast language.

```python
import math

LIMIT = 10**8
rows = [10, 20, 100, 500, 5000, 10**5, 10**6]
print("%8s %12s %12s %12s %12s" % ("n", "n log n", "n^2", "n^3", "2^n"))
for n in rows:
    nlogn = int(n * math.log2(n))
    cells = [nlogn, n**2, n**3, 2**n]
    shown = []
    for c in cells:
        if c > 10**15:
            shown.append("huge")
        elif c > LIMIT:
            shown.append("%.0e!" % c)
        else:
            shown.append(str(c))
    print("%8d %12s %12s %12s %12s" % (n, *shown))
```
```text
       n      n log n          n^2          n^3          2^n
      10           33          100         1000         1024
      20           86          400         8000      1048576
     100          664        10000      1000000         huge
     500         4482       250000       1e+08!         huge
    5000        61438     25000000       1e+11!         huge
  100000      1660964       1e+10!       1e+15!         huge
 1000000     19931568       1e+12!         huge         huge
```

Entries ending in `!` are over `10^8`. Read the table down the columns: `n^2` dies between `5000` and `10^5`; `n log n` survives until `10^6` and beyond; `2^n` dies at `n` around 27.

### Step by step: reading a statement

Suppose a statement says:

> You are given an array of `n` integers (`1 <= n <= 2 * 10^5`, `1 <= a_i <= 10^9`) and `q` queries (`1 <= q <= 2 * 10^5`). Each query asks for the sum of a range.

Check list:

1. `n` and `q` are both `2 * 10^5`. A loop over the range per query is `n * q = 4 * 10^10`. Too slow. Target: `O((n + q) log n)` or better.
2. `a_i` up to `10^9`, and up to `2 * 10^5` of them: the sum can reach `2 * 10^14`. In Python this is fine (integers do not overflow). In C++ you would need 64-bit; remember that if you read editorials.
3. A range sum with no updates is **prefix sums** (dsa.03): `O(n)` build, `O(1)` per query.

You reached the algorithm from the constraints alone. This is the habit.

### Other things the constraints tell you

- **Sum of `n` over all test cases is bounded** (for example "the sum of `n` over all test cases does not exceed `2 * 10^5`"). Then you may spend `O(n log n)` per test, but you must not do `O(max n)` setup per test (for example allocating a 10^5-size array for each of 10^4 tests).
- **Small `a_i` (up to 100 or 1000)** often means counting arrays or DP over values.
- **Time limit larger than 2 seconds** means the setter expects something heavier, or wants to be kind to slow languages.
- **Memory limit 256 MB.** A Python list of `10^7` ints is about 80 MB for pointers plus the int objects themselves. Big lists of small ints share cached objects only up to 256, so beware (section 10).
- **Answer modulo `10^9 + 7` or `998244353`.** The true answer is huge. Use the modular templates of section 11.

### Try it

For each statement fragment, name the largest complexity you can afford.

1. `n <= 18`, find the best subset.
2. `n <= 3000`, find the longest common subsequence of two strings of length `n`.
3. `n <= 10^6`, count pairs `(i, j)` with `a[i] + a[j] == k`.
4. `n <= 10^18`, find the smallest `x` such that `f(x) >= n`, where `f` is increasing and cheap.

<details><summary>Answer</summary>

1. `n = 18`: `2^18 = 262,144` subsets, times `n` for the work per subset is about `4.7 * 10^6`. Exponential is fine.
2. `n = 3000`: `n^2 = 9 * 10^6` DP cells. Quadratic is fine (in CPython it is already about a second, see section 10).
3. `n = 10^6`: `O(n)` with a dictionary or `O(n log n)` with sorting and two pointers. Not `O(n^2)` (that is `10^12`).
4. `n = 10^18`: `O(log n)`, which is about 60 steps of binary search on the answer (dsa.06, section 9).

</details>

## 3. Measuring instead of guessing: a timing harness

Online judges tell you "time limit exceeded" and nothing else. Offline you can do better. This section gives a small tool that you will use for the rest of the chapter.

### Why `time.perf_counter`

`time.perf_counter()` returns a clock with the highest resolution available, in seconds, as a float. It is meant for measuring short durations. (Do not use `time.time()` for this: it can jump when the system clock is adjusted.)

### Why repeat and take the minimum

One measurement is noisy: the operating system may pause your program for another process. The **fastest** of several runs is the one least disturbed by noise, so it is the best estimate of the true cost. That is what the standard library's `timeit` does too.

```python
import time

def bench(fn, repeat=5):
    """Return the best (minimum) time in seconds over `repeat` runs of fn()."""
    best = float("inf")
    for _ in range(repeat):
        start = time.perf_counter()
        fn()
        elapsed = time.perf_counter() - start
        if elapsed < best:
            best = elapsed
    return best

def loop_million():
    total = 0
    for i in range(10**6):
        total += i
    return total

best = bench(loop_million)
print("one million loop passes took %.3f s (machine-specific)" % best)
print("so this machine does about %.0f million simple loop passes per second" % (1 / best))
```
```text
one million loop passes took 0.035 s (machine-specific)
so this machine does about 29 million simple loop passes per second
```

The second line is the number you should remember about **your** machine and **your** interpreter. A pass of `total += i` is about three simple operations (add, store, next item). Use it to convert "this loop runs `10^7` times" into seconds.

### A harness that compares two functions

When you wonder "which of these two is faster?", do not argue. Measure. This helper runs several candidates and prints them as ratios of the fastest.

```python
import time

def bench(fn, repeat=5):
    best = float("inf")
    for _ in range(repeat):
        start = time.perf_counter()
        fn()
        best = min(best, time.perf_counter() - start)
    return best

def compare(**candidates):
    results = {name: bench(fn) for name, fn in candidates.items()}
    fastest = min(results.values())
    for name, t in sorted(results.items(), key=lambda kv: kv[1]):
        print("%-12s %8.4f s   x%.2f" % (name, t, t / fastest))

N = 10**6

def with_loop():
    out = []
    for i in range(N):
        out.append(i * 2)
    return out

def with_comprehension():
    return [i * 2 for i in range(N)]

compare(loop=with_loop, comprehension=with_comprehension)
```
```text
comprehension   0.0553 s   x1.00
loop           0.0588 s   x1.06
```

The times are machine-specific. On older CPython versions the comprehension wins clearly, because `append` is not looked up and called each time; on recent versions (we ran 3.14) the two are close. This is exactly why you measure instead of trusting advice: the gap depends on the interpreter version.

### Make a worst-case input, not a random one

A judge's hidden tests contain **worst cases**. Your own tests must too. For each solution, build the largest input the statement allows, and time that. For sorted-input traps, the worst case may be an already sorted list, or all equal values, or a path-shaped graph.

```python
import random

def worst_inputs(n):
    rng = random.Random(7)
    return {
        "random": [rng.randint(1, 10**9) for _ in range(n)],
        "sorted": list(range(1, n + 1)),
        "reversed": list(range(n, 0, -1)),
        "all equal": [5] * n,
    }

for name, arr in worst_inputs(8).items():
    print("%-10s %s" % (name, arr))
```
```text
random     [347712783, 161973070, 423938500, 698935573, 51847157, 77777869, 881836554, 575398923]
sorted     [1, 2, 3, 4, 5, 6, 7, 8]
reversed   [8, 7, 6, 5, 4, 3, 2, 1]
all equal  [5, 5, 5, 5, 5, 5, 5, 5]
```

(`random.Random(7)` fixes the seed, so the "random" array is the same on every run.)

### A rough speed table for your machine

The next program measures four basic workloads and prints how many "units per second" your interpreter manages. Run it once on CPython (and later on PyPy, if you install it) and write the numbers in your notebook. They replace folklore with facts.

```python
import time

def bench(fn, repeat=3):
    best = float("inf")
    for _ in range(repeat):
        s = time.perf_counter()
        fn()
        best = min(best, time.perf_counter() - s)
    return best

def plain_loop():
    t = 0
    for i in range(10**6):
        t += i

def list_index():
    a = [1] * 1000
    t = 0
    for _ in range(1000):
        for j in range(1000):
            t += a[j]

def dict_ops():
    d = {}
    for i in range(10**6 // 4):
        d[i] = i
    t = 0
    for i in range(10**6 // 4):
        t += d[i]

def function_calls():
    def f(x):
        return x + 1
    t = 0
    for i in range(10**6 // 2):
        t = f(t)

for name, fn, units in [
    ("plain loop", plain_loop, 10**6),
    ("list index", list_index, 10**6),
    ("dict ops", dict_ops, 2 * 10**6 // 4),
    ("function call", function_calls, 10**6 // 2),
]:
    t = bench(fn)
    print("%-14s %6.0f thousand units per second (machine-specific)" % (name, units / t / 1000))
```
```text
plain loop      27791 thousand units per second (machine-specific)
list index      33242 thousand units per second (machine-specific)
dict ops        13567 thousand units per second (machine-specific)
function call   21112 thousand units per second (machine-specific)
```

Typical lesson: a function call costs several times more than a plain loop pass. That explains why recursive solutions are slower than iterative ones in CPython.

### Counting operations instead of time

Sometimes you want a number that does not depend on the machine. Count operations inside your algorithm with a counter, like dsa.16 did. For example, this counts comparisons in a nested loop and shows why `n = 5000` is borderline.

```python
def pair_count(n):
    ops = 0
    for i in range(n):
        for j in range(i + 1, n):
            ops += 1
    return ops

for n in [10, 100, 1000, 3000]:
    print(n, pair_count(n))
print("formula n*(n-1)/2 for n = 5000:", 5000 * 4999 // 2)
```
```text
10 45
100 4950
1000 499500
3000 4498500
formula n*(n-1)/2 for n = 5000: 12497500
```

Twelve and a half million pairs for `n = 5000`. In CPython that is a second or more; in PyPy it is a small fraction of a second. This is the sort of reasoning that decides *which interpreter to submit to*.

## 4. Fast input

### Why input is slow

Reading `10^6` numbers with `input()` is a classic reason for "time limit exceeded", even when the algorithm is perfect. Two things make `input()` slow:

1. It does extra work: it checks whether the terminal is interactive, handles a prompt, and strips the newline.
2. You call it once per line, and each call has a fixed overhead.

The fix has two parts: use `sys.stdin`, which is the raw input stream, and read **many bytes at once** so the fixed overhead is paid once.

### The first example: `input()`

You know this already. The first line holds `n`, the second holds `n` numbers.

```text
5
3 1 4 1 5
```
```python
n = int(input())
a = list(map(int, input().split()))
print(n, sum(a))
```
```text
5 14
```

(The block above the code shows what we gave on standard input. The block below it is the real output.) This is fine for small inputs. Let us find out what happens on a large one.

### Measuring the three styles

The test below builds an input with `200,000` lines of one number each, then reads it in three ways. To measure only the reading, we replace `sys.stdin` with an in-memory text stream `io.StringIO`, which behaves like a file of text. (A real judge uses a real pipe or file, which is faster or about equal; the *ratios* are what matter.)

```python
import io, sys, time

N = 200000
data = "\n".join(str(i) for i in range(N)) + "\n"

def read_with_input():
    sys.stdin = io.StringIO(data)
    total = 0
    for _ in range(N):
        total += int(input())
    return total

def read_with_readline():
    sys.stdin = io.StringIO(data)
    rl = sys.stdin.readline
    total = 0
    for _ in range(N):
        total += int(rl())
    return total

def read_all_split():
    sys.stdin = io.StringIO(data)
    nums = sys.stdin.read().split()
    total = 0
    for x in nums:
        total += int(x)
    return total

def read_all_map():
    sys.stdin = io.StringIO(data)
    return sum(map(int, sys.stdin.read().split()))

answers = set()
for name, fn in [("input()", read_with_input), ("readline", read_with_readline),
                 ("read().split()", read_all_split), ("read+map", read_all_map)]:
    best = float("inf")
    for _ in range(3):
        s = time.perf_counter()
        r = fn()
        best = min(best, time.perf_counter() - s)
    answers.add(r)
    print("%-15s %.4f s (machine-specific)" % (name, best))
print("all four give the same sum:", len(answers) == 1, answers)
```
```text
input()         0.1324 s (machine-specific)
readline        0.0262 s (machine-specific)
read().split()  0.0262 s (machine-specific)
read+map        0.0208 s (machine-specific)
all four give the same sum: True {19999900000}
```

Your timings will differ. The usual order is `input()` slowest, then `readline`, then the two `read().split()` forms. With a real file or pipe, the gap between `input()` and `sys.stdin.readline` is larger than here, because the real `input()` also touches the terminal machinery.

### The four standard patterns

Learn these four. Everything else is a variation.

**Pattern A: one line at a time with `sys.stdin.readline`.**

```python
import sys
input = sys.stdin.readline   # shadow the built-in name with the fast one

n = int(input())
a = list(map(int, input().split()))
```

`sys.stdin.readline` does **not** strip the trailing newline, so `input()` now returns `"5\n"`. `int("5\n")` still works, because `int` ignores surrounding white space. But for **strings** you must strip yourself: `s = input().strip()`.

**Pattern B: read everything, split into tokens.**

```python
import sys
data = sys.stdin.read().split()   # list of all tokens, as strings
n = int(data[0])
a = list(map(int, data[1:1 + n]))
```

This ignores the line structure completely. It is the fastest and the shortest, but you must track your position yourself.

**Pattern C: an iterator over tokens.**

```python
import sys
it = iter(sys.stdin.read().split())
n = int(next(it))
a = [int(next(it)) for _ in range(n)]
```

This keeps Pattern B's speed and removes the index bookkeeping. `next(it)` hands out the next token and remembers where it stopped. It is the style most competitive programmers settle on.

**Pattern D: read bytes, not text.**

```python
import sys
data = sys.stdin.buffer.read().split()   # tokens are bytes: b"12"
n = int(data[0])                         # int() accepts bytes
a = list(map(int, data[1:1 + n]))
```

`sys.stdin.buffer` skips the step of decoding bytes to text. `int(b"12")` works directly. It is the fastest on large inputs. The price: tokens are `bytes`, so words are `b"abc"`, not `"abc"`. Decode (`tok.decode()`) when you need a real string.

### Running the patterns on a real input

We now run all four on the same small input and check they agree. Each pattern reads a count `n` and then `n` numbers.

```text
4
10 20 30 40
```
```python
import io, sys

raw = "4\n10 20 30 40\n"

def a_readline():
    sys.stdin = io.StringIO(raw)
    input = sys.stdin.readline
    n = int(input())
    return list(map(int, input().split()))

def b_read_split():
    sys.stdin = io.StringIO(raw)
    data = sys.stdin.read().split()
    n = int(data[0])
    return list(map(int, data[1:1 + n]))

def c_iterator():
    sys.stdin = io.StringIO(raw)
    it = iter(sys.stdin.read().split())
    n = int(next(it))
    return [int(next(it)) for _ in range(n)]

def d_bytes():
    sys.stdin = io.TextIOWrapper(io.BytesIO(raw.encode()))
    data = sys.stdin.buffer.read().split()
    n = int(data[0])
    return list(map(int, data[1:1 + n]))

for f in (a_readline, b_read_split, c_iterator, d_bytes):
    print(f.__name__, f())
```
```text
a_readline [10, 20, 30, 40]
b_read_split [10, 20, 30, 40]
c_iterator [10, 20, 30, 40]
d_bytes [10, 20, 30, 40]
```

All four print the same list. (We wrap the string in `io.StringIO` or `io.TextIOWrapper` only to imitate a real standard input inside one script.)

### Which pattern when?

| Situation | Best pattern |
|---|---|
| Line structure matters (grid of strings, a sentence per line) | A |
| Many numbers, simple structure, fastest wanted | D or C |
| Mixed words and numbers, you want to avoid index bookkeeping | C |
| Tiny inputs (under about `10^4` numbers) | anything; correctness first |

In a contest, pick one template and use it for every problem. Familiarity prevents bugs.

### Reading a grid

A grid is a set of lines of characters. Pattern A is natural here, because every line is one row:

```text
3 4
#..#
.##.
....
```
```python
import sys
input = sys.stdin.readline

h, w = map(int, input().split())
grid = [input().strip() for _ in range(h)]
hashes = sum(row.count("#") for row in grid)
print(h, w, hashes)
print(grid[1][1], grid[1][0])
```
```text
3 4 4
# .
```

`strip()` removes the newline (and any trailing spaces). Forgetting it leaves `"#..#\n"` in each row, and `len(row)` becomes `w + 1`. That is a classic bug.

### Reading pairs, edges and queries

For `m` lines of two numbers each (edges of a graph), combine Pattern C with a comprehension.

```text
4 3
1 2
2 3
3 4
```
```python
import sys
it = iter(sys.stdin.read().split())
n = int(next(it)); m = int(next(it))
adj = [[] for _ in range(n + 1)]
for _ in range(m):
    u = int(next(it)); v = int(next(it))
    adj[u].append(v)
    adj[v].append(u)
print(adj[1:])
```
```text
[[2], [1, 3], [2, 4], [3]]
```

Compare with dsa.12, section 2, where graphs were stored this way. The only new thing is how the numbers arrive.

### Reading when the number of lines is unknown (EOF)

Some problems (rare, mostly older ones) end the input with end-of-file instead of a count. Then loop until the stream is empty.

```text
3 4
10 20
7 7
```
```python
import sys

for line in sys.stdin:           # iterating a file gives one line at a time
    parts = line.split()
    if not parts:                # skip blank lines
        continue
    a, b = int(parts[0]), int(parts[1])
    print(a + b)
```
```text
7
30
14
```

`for line in sys.stdin` stops at end of file by itself. With `readline`, the equivalent is `while True: line = sys.stdin.readline(); if not line: break` (an empty string, with no newline at all, means end of file; a blank line is `"\n"`).

## 5. Fast output

### Why many `print` calls are slow

Every `print(x)` converts `x` to text, writes it to a buffer, and may flush. For `2 * 10^5` lines, those calls add up. The fix is again to do the work **once**: build a list of strings, join with a newline, and write it in one call.

### Measuring

```python
import io, sys, time

N = 200000
values = list(range(N))

def print_each():
    sys.stdout = io.StringIO()
    for v in values:
        print(v)

def join_then_print():
    sys.stdout = io.StringIO()
    print("\n".join(map(str, values)))

def collect_then_write():
    sys.stdout = io.StringIO()
    out = []
    for v in values:
        out.append(str(v))
    sys.stdout.write("\n".join(out) + "\n")

real = sys.__stdout__
results = []
for name, fn in [("print each", print_each), ("join+print", join_then_print),
                 ("list+write", collect_then_write)]:
    best = float("inf")
    for _ in range(3):
        s = time.perf_counter()
        fn()
        best = min(best, time.perf_counter() - s)
    results.append((name, best))
sys.stdout = real
for name, best in results:
    print("%-11s %.4f s (machine-specific)" % (name, best))
```
```text
print each  0.0405 s (machine-specific)
join+print  0.0200 s (machine-specific)
list+write  0.0240 s (machine-specific)
```

(We send the output to an `io.StringIO` while timing, then restore the real one to print the results.) The `print`-each version is slowest. The gap against a real terminal or pipe is bigger, since a real stream has extra flushing cost.

### The standard output patterns

```python
import sys

# Pattern 1: collect lines, print once at the end.
out = []
for i in range(3):
    out.append(str(i * i))
print("\n".join(out))

# Pattern 2: same with sys.stdout.write (no automatic newline!).
sys.stdout.write("\n".join(out) + "\n")

# Pattern 3: numbers on one line, separated by spaces.
print(*[1, 2, 3])          # unpacking: prints 1 2 3
print(" ".join(map(str, [1, 2, 3])))
```
```text
0
1
4
0
1
4
1 2 3
1 2 3
```

Three notes.

- `"\n".join(...)` puts newlines **between** items. There is no newline after the last one, which is why Pattern 2 adds `+ "\n"`.
- `join` needs **strings**. `"\n".join([1, 2])` raises `TypeError`. Use `map(str, ...)` or `str(x)` when you append.
- `print(*list)` is fine for one short line. For a list of `10^5` items, `" ".join(map(str, list))` is faster than unpacking.

### Output format traps

Judges compare your output to the expected output. Most ignore **trailing spaces and trailing newlines** at the end, and compare tokens. But:

- Some judges (ICPC-style, older systems) are strict: an extra space can mean "presentation error" or "wrong answer".
- Printing `1.0` when `1` is expected is wrong. Division `/` returns a float; use `//` for integer division.
- For real-number answers, the statement says the allowed error ("absolute or relative error at most `10^-6`"). Print with enough digits: `print("%.10f" % x)`.
- `True` and `False` print with capital letters. If the statement wants `YES`/`NO` or `Yes`/`No`, copy the exact spelling.

```python
x = 7 / 2
y = 7 // 2
print(x, y)
print("%.10f" % (1 / 3))
print("YES" if y == 3 else "NO")
print(True)
```
```text
3.5 3
0.3333333333
YES
True
```

### Many answers on one line versus one per line

Read the statement: "print `n` integers separated by spaces" is one line; "print the answer for each test case on a separate line" is one line per test. A very common beginner failure is to print each test's answer separated by spaces when lines were required (or the other way round). Tokens-comparing judges accept either, but do not count on it.

### `sys.stdout.write` and `print` differ in one more way

`print` converts any object with `str()`. `sys.stdout.write` accepts **only strings** and returns the number of characters written.

```python
import sys

n = sys.stdout.write("abc\n")
print(n)
try:
    sys.stdout.write(5)
except TypeError as e:
    print("TypeError:", e)
```
```text
abc
4
TypeError: write() argument must be str, not int
```

## 6. Multiple test cases and the common input traps

### The multi-test format

Most modern contests have a first line `t`, the number of test cases, and then `t` independent tests. The shape of your program is always:

```python
def solve():
    ...read one test, return the answer string...

t = int(next(it))
out = []
for _ in range(t):
    out.append(solve())
print("\n".join(out))
```

Here is a complete example. Each test is a line with `n` followed by `n` numbers; the answer is the maximum.

```text
3
3 5 1 9
1 7
4 2 2 2 2
```
```python
import sys

def main():
    it = iter(sys.stdin.read().split())
    t = int(next(it))
    out = []
    for _ in range(t):
        n = int(next(it))
        a = [int(next(it)) for _ in range(n)]
        out.append(str(max(a)))
    print("\n".join(out))

main()
```
```text
9
7
2
```

Why a `main()` function? Variables inside a function are **local variables**, and local variable access is faster than global access in CPython. Section 10 measures it. Put all your code in functions.

### Trap 1: state that leaks between tests

If you use a global list or dictionary across tests, you must reset it for each test. A frequent bug is a global counter that keeps growing.

```python
seen = set()           # BUG: global, never cleared

def solve_bad(a):
    for x in a:
        if x in seen:
            return "duplicate"
        seen.add(x)
    return "unique"

def solve_good(a):
    seen = set()       # fresh set for every test
    for x in a:
        if x in seen:
            return "duplicate"
        seen.add(x)
    return "unique"

tests = [[1, 2, 3], [3, 5, 6]]
print([solve_bad(a) for a in tests])
print([solve_good(a) for a in tests])
```
```text
['unique', 'duplicate']
['unique', 'unique']
```

The two tests are independent and neither has a repeated value, yet the buggy version calls the second one a duplicate: `seen` still holds `3` from the first test. The fix is the fresh `seen = set()` inside the function.

### Trap 2: allocating big arrays per test

If `t` can be `10^4` and you write `dp = [0] * (10**5 + 1)` inside `solve`, you do `10^9` work. Allocate according to the **current** test's `n`, or allocate once outside and reset only the part you used. The statement hint is "the sum of `n` over all test cases is at most ...".

```python
import time

def per_test_big(t):
    for _ in range(t):
        dp = [0] * (10**5 + 1)

def per_test_small(t, n):
    for _ in range(t):
        dp = [0] * (n + 1)

s = time.perf_counter(); per_test_big(2000); a = time.perf_counter() - s
s = time.perf_counter(); per_test_small(2000, 10); b = time.perf_counter() - s
print("big array each test : %.3f s" % a)
print("array sized to n    : %.5f s" % b)
print("ratio is large (machine-specific numbers)")
```
```text
big array each test : 0.217 s
array sized to n    : 0.00019 s
ratio is large (machine-specific numbers)
```

### Trap 3: trailing spaces and blank lines in the input

Judges are usually careful, but your **own** test files may have an extra blank line at the end. Token-based reading (Patterns B, C and D) is immune to that. Line-based reading is not: `input().split()` on an empty line gives an empty list, and then `int(...)` or indexing fails.

```python
line = "\n"
print(line.split())
try:
    print(int(line.split()[0]))
except IndexError as e:
    print("IndexError:", e)
```
```text
[]
IndexError: list index out of range
```

### Trap 4: `bytes` instead of `str`

With Pattern D, `data[i]` is `b"hello"`, not `"hello"`. Comparisons with a string literal quietly fail, and indexing returns an integer.

```python
tok = b"abc"
print(tok == "abc")
print(tok[0])
print(tok.decode() == "abc")
print(tok == b"abc")
```
```text
False
97
True
True
```

`b"abc" == "abc"` is `False` (Python does not raise an error; it just says they differ). `b"abc"[0]` is the number `97`, not a character. Use Pattern D for numbers, and `decode()` for words.

### Trap 5: `int(input())` on a line with two numbers

If the first line is `3 4` and you call `int(input())`, you get `ValueError: invalid literal for int()`. Read the statement's input section to see how many numbers each line has.

### Trap 6: shadowing `input` or `max` and then using the built-in

Writing `input = sys.stdin.readline` is a deliberate shadow. But writing `max = 0` or `sum = 0` as variable names, and then calling `max(...)`, raises `TypeError: 'int' object is not callable`.

```python
total = 0
for x in [3, 1, 2]:
    total += x
print(total)

sum = 10
try:
    print(sum([1, 2, 3]))
except TypeError as e:
    print("TypeError:", e)
```
```text
6
TypeError: 'int' object is not callable
```

### Trap 7: Windows line endings

If an input file has `\r\n` line endings, `readline` returns `"5\r\n"`. `int("5\r\n")` works, but `s == "abc"` on a string read with `.rstrip("\n")` fails because of the leftover `\r`. `.strip()` removes both. Use `.strip()` always, never `.rstrip("\n")`.

## 7. Interactive problems

### What "interactive" means

In an interactive problem, your program does not get all input at once. It **talks** to the judge program: you print a question, the judge prints an answer, you print the next question, and so on, until you print the final answer. A typical story: "I have a hidden number between 1 and `10^9`. You may ask 30 questions of the form `? x` and I answer whether my number is greater than `x`. Then print `! answer`."

This is binary search (dsa.06) where the predicate is an *interaction*.

### The one rule: flush

Output is **buffered**: Python holds your text in memory and sends it in bigger chunks. In a normal problem that is good. In an interactive problem it is a disaster: you printed `? 500` but the judge never received it, so it never answers, and both programs wait forever. The judge reports "idleness limit exceeded" or "time limit exceeded".

The cure is to **flush** after every question:

```python
print("? 500", flush=True)
```

`flush=True` forces Python to send the buffer immediately. Equivalent: `sys.stdout.write(...)` then `sys.stdout.flush()`.

### Input rules in interactive problems

- **Do not read all of stdin at once.** `sys.stdin.read()` waits for end of file, which only comes when the judge closes the pipe, i.e. never. Use `input()` or `sys.stdin.readline()` to read one line at a time.
- Read exactly the lines the protocol says. If the judge says "-1" for an invalid query, you must stop at once and exit; continuing leads to a wrong-answer verdict or a hung program.

### A complete example, with a local judge

We cannot call a real judge offline, so we build a tiny one. The following script writes the solution to a file, writes a judge, connects them with pipes using `subprocess`, and counts the questions.

First, the solution. It guesses a number in `[1, 1000]`, asking `? x`; the judge replies `<` if the hidden number is smaller than `x`, `>=` otherwise.

```python
import os, subprocess, sys, tempfile, textwrap

solution = textwrap.dedent('''
    import sys
    lo, hi = 1, 1000                 # hidden number is in [lo, hi]
    while lo < hi:
        mid = (lo + hi + 1) // 2     # upper middle, so the loop always progresses
        print("?", mid, flush=True)
        reply = sys.stdin.readline().strip()
        if reply == ">=":
            lo = mid
        else:
            hi = mid - 1
    print("!", lo, flush=True)
''')

def run_interaction(secret):
    with tempfile.TemporaryDirectory() as d:
        path = os.path.join(d, "sol.py")
        with open(path, "w") as f:
            f.write(solution)
        proc = subprocess.Popen([sys.executable, "-I", path], stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, text=True)
        questions = 0
        while True:
            line = proc.stdout.readline().split()
            if line[0] == "!":
                proc.stdin.close()
                proc.wait()
                return int(line[1]), questions
            questions += 1
            x = int(line[1])
            proc.stdin.write((">=" if secret >= x else "<") + "\n")
            proc.stdin.flush()               # the judge must flush too

for secret in [1, 2, 500, 999, 1000]:
    answer, q = run_interaction(secret)
    print("secret", secret, "-> answer", answer, "in", q, "questions")
```
```text
secret 1 -> answer 1 in 9 questions
secret 2 -> answer 2 in 10 questions
secret 500 -> answer 500 in 10 questions
secret 999 -> answer 999 in 10 questions
secret 1000 -> answer 1000 in 10 questions
```

Look at the numbers of questions: about `log2(1000) = 10` each. A wrong update (`lo = mid + 1` with the lower middle) would loop forever or lose the answer, exactly the off-by-one traps of dsa.06, section 4.

Now try something instructive: remove `flush=True` from the solution's question and run it. The program hangs, because the judge never sees the question. Do this only with a timeout in your own tests; here it is deliberately not run.

### Protocol checklist for interactive problems

1. Read the statement: how many queries are allowed? (Exceeding it is "wrong answer".)
2. Always `flush=True` on every line you send, including the final answer.
3. Read replies with `readline`, not `read()`.
4. If the judge may send an error code (like `-1`), check for it first and `exit()`.
5. Never print debugging text to **stdout**: the judge parses it. Print debug lines to `sys.stderr`, which judges ignore.

```python
import sys
print("debug: this goes to stderr", file=sys.stderr)
print("this goes to stdout")
```
```text
this goes to stdout
debug: this goes to stderr
```

In the output above, both lines appear because our tool shows both streams. A real judge would read only the second.

## 8. Recursion limits and iterative DFS

### The recursion limit

Python protects itself from runaway recursion. Every function call in progress takes space on the **call stack**. If recursion goes too deep, a C-level crash would follow, so Python raises `RecursionError` once the depth passes a limit. In CPython the limit is **1000** by default. You can read it with `sys.getrecursionlimit()`.

```python
import sys
print(sys.getrecursionlimit())

def depth(n):
    return 0 if n == 0 else 1 + depth(n - 1)

print(depth(500))
try:
    print(depth(5000))
except RecursionError as e:
    print("RecursionError:", e)
```
```text
1000
500
RecursionError: maximum recursion depth exceeded
```

Contest inputs are cruel here. A tree with `2 * 10^5` nodes that is shaped like a path (a "chain") needs a DFS of depth `2 * 10^5`. A recursive DFS dies at depth about 1000. The setters include a path-shaped test on purpose.

### Way 1: raise the limit

```python
import sys
sys.setrecursionlimit(10**6)
```

This only changes Python's *polite* limit. The real constraint is the memory of the C stack. Each Python call (in older CPython versions) uses C stack space, and the main thread has a small stack, commonly 8 MB on Linux. A deep enough recursion then crashes the whole interpreter with a segmentation fault, with no error message. Modern CPython (3.12 and later) keeps pure-Python calls off the C stack, so the crash is rarer, but you cannot rely on it being the judge's version.

Memory is the other cost: each frame holds locals. A depth of `10^6` can take hundreds of MB.

### Way 2: run in a thread with a big stack

The `threading` module lets you start a new thread and choose its stack size before it starts. The main thread's stack cannot be changed, but a new thread's can.

```python
import sys, threading

def dfs_sum(n):
    # A recursive function with depth n: sum of 1..n by recursion.
    return 0 if n == 0 else n + dfs_sum(n - 1)

def main():
    print(dfs_sum(100000))

sys.setrecursionlimit(10**6)
threading.stack_size(128 * 1024 * 1024)      # 128 MB, request before creating the thread
t = threading.Thread(target=main)
t.start()
t.join()
```
```text
5000050000
```

This is the standard "contest recipe" for recursion in CPython. Order matters: set the recursion limit, set the stack size, create the thread, start it, wait for it with `join`. Everything your program does goes inside `main`.

Costs and warnings:

- The stack size is virtual memory that the OS reserves. A judge with a strict memory limit may count it. Do not ask for more than you need; 64 MB or 128 MB is usually enough for depth `2 * 10^5`.
- A bug inside `main` raises an exception in the thread; make sure the exit code is non-zero (the traceback prints) so you notice.
- Recursion is **slow** in CPython because each call costs far more than a loop pass (section 3). Even with the thread trick, converting to iteration is faster.
- On PyPy the recursion limit has its own rules (section 9).

### Way 3: convert to an iterative DFS

This is the robust answer, and the one that also runs faster. You already met iterative DFS with an explicit stack in dsa.12, section 4. Here we turn it into a template for the most common tree tasks.

**Why it works.** A recursive DFS uses the call stack to remember "where was I in this node's neighbour list". We keep our own stack, a plain Python list, which has no depth limit except RAM.

#### Template 1: visiting order (preorder) with parents

```python
def dfs_order(adj, root):
    """Return (order, parent). order lists nodes in the order they are first visited."""
    n = len(adj)
    parent = [-1] * n
    order = []
    stack = [root]
    parent[root] = root                  # mark the root as seen
    while stack:
        u = stack.pop()
        order.append(u)
        for v in adj[u]:
            if parent[v] == -1:          # not visited yet
                parent[v] = u
                stack.append(v)
    return order, parent

#        0
#       / \
#      1   2
#     / \   \
#    3   4   5
adj = [[1, 2], [0, 3, 4], [0, 5], [1], [1], [2]]
order, parent = dfs_order(adj, 0)
print("order :", order)
print("parent:", parent)
```
```text
order : [0, 2, 5, 1, 4, 3]
parent: [0, 0, 0, 1, 1, 2]
```

Complexity: `O(n + m)` time (each node and edge once), `O(n)` extra space.

Note the order: `0, 2, 5, 1, 4, 3`. The stack is last-in-first-out, so the last pushed neighbour is explored first. The visit order differs from the recursive order `0, 1, 3, 4, 2, 5`, but it is still a valid DFS preorder (every node comes after its parent). For most tasks only the parent relationships matter.

#### Template 2: processing children before parents (subtree sizes)

Many tree problems need results computed **bottom-up**: the size of each subtree, the height, the sum of values. In recursion, the answer for a node is computed after its children return. The iterative trick: get a visiting order in which parents come first, then process it **in reverse**. In reverse, every node is processed after all its descendants.

```python
def dfs_order(adj, root):
    parent = [-1] * len(adj)
    parent[root] = root
    order = []
    stack = [root]
    while stack:
        u = stack.pop()
        order.append(u)
        for v in adj[u]:
            if parent[v] == -1:
                parent[v] = u
                stack.append(v)
    return order, parent

def subtree_sizes(adj, root):
    order, parent = dfs_order(adj, root)
    size = [1] * len(adj)
    for u in reversed(order):            # children before parents
        if u != root:
            size[parent[u]] += size[u]
    return size

adj = [[1, 2], [0, 3, 4], [0, 5], [1], [1], [2]]
print(subtree_sizes(adj, 0))
```
```text
[6, 3, 2, 1, 1, 1]
```

Check by hand: node 1 has children 3 and 4, so its subtree has `1 + 1 + 1 = 3` nodes; node 2 has child 5, so size 2; the root has `1 + 3 + 2 = 6`. The output matches.

This "order, then reversed order" pattern solves a huge family of problems: subtree sums, tree DP (maximum independent set on a tree), heights, diameters, counting leaves. Whenever you would write `result[u] = combine(result[child] for child in children)`, write the reversed loop.

#### Template 3: the chain stress test

The point of all this is that it survives a chain of 200,000 nodes. We build the worst case and run it. The recursive version fails; the iterative version finishes.

```python
import sys

n = 200000
adj = [[] for _ in range(n)]
for i in range(n - 1):
    adj[i].append(i + 1)
    adj[i + 1].append(i)

def dfs_order(adj, root):
    parent = [-1] * len(adj)
    parent[root] = root
    order = []
    stack = [root]
    while stack:
        u = stack.pop()
        order.append(u)
        for v in adj[u]:
            if parent[v] == -1:
                parent[v] = u
                stack.append(v)
    return order, parent

def height_recursive(u, p):
    best = 0
    for v in adj[u]:
        if v != p:
            best = max(best, 1 + height_recursive(v, u))
    return best

try:
    height_recursive(0, -1)
except RecursionError:
    print("recursive version: RecursionError at the default limit")

order, parent = dfs_order(adj, 0)
height = [0] * n
for u in reversed(order):
    if u != 0:
        p = parent[u]
        if height[u] + 1 > height[p]:
            height[p] = height[u] + 1
print("iterative version: height of the chain =", height[0])
```
```text
recursive version: RecursionError at the default limit
iterative version: height of the chain = 199999
```

The height of a chain of 200,000 nodes (199,999 edges) is `199999`. The iterative version used a few MB.

#### Template 4: DFS that needs "enter" and "exit" events

Sometimes you must do something both when you **enter** a node and when you **leave** it: assign entry/exit times (to ask "is `v` in the subtree of `u`?"), or undo a change after finishing a subtree. Push each node twice: once to enter, once (marked) to exit.

```python
def euler_times(adj, root):
    n = len(adj)
    tin = [0] * n
    tout = [0] * n
    seen = [False] * n
    timer = 0
    stack = [root]            # positive u = enter, ~u (negative) = exit
    seen[root] = True
    while stack:
        u = stack.pop()
        if u >= 0:
            tin[u] = timer
            timer += 1
            stack.append(~u)              # schedule the exit before the children
            for v in adj[u]:
                if not seen[v]:
                    seen[v] = True
                    stack.append(v)
        else:
            tout[~u] = timer
    return tin, tout

adj = [[1, 2], [0, 3, 4], [0, 5], [1], [1], [2]]
tin, tout = euler_times(adj, 0)
print("tin :", tin)
print("tout:", tout)

def is_ancestor(u, v):
    return tin[u] <= tin[v] < tout[u]

print("is 1 an ancestor of 4?", is_ancestor(1, 4))
print("is 1 an ancestor of 5?", is_ancestor(1, 5))
```
```text
tin : [0, 3, 1, 5, 4, 2]
tout: [6, 6, 3, 6, 5, 3]
is 1 an ancestor of 4? True
is 1 an ancestor of 5? False
```

`~u` is the bitwise NOT: for `u >= 0` it equals `-u - 1`, which is always negative, and `~~u == u`. It is a compact way to carry a flag inside the integer. The exit event is pushed *before* the children, so (stack order) it is popped *after* all of them. Subtree of `u` is exactly the interval `[tin[u], tout[u])`.

#### When recursion is truly needed

Backtracking with complex state (dsa.07), where each level has a loop that resumes after the recursive call returns, can still be written with an explicit stack of "(state, next choice index)" pairs, but it is clumsy. Options in order of preference: (1) bound the depth (a depth of `n <= 20` needs no tricks), (2) the thread recipe, (3) a manual stack. Plain DFS on a tree or graph almost always converts cleanly.

### Try it

1. Change `dfs_order` to visit neighbours in the order they appear in the list (so the iterative order equals the recursive one for the sample). *Hint: push neighbours in reverse.*
2. Write `tree_depths(adj, root)` returning each node's distance from the root, iteratively.

<details><summary>Answer</summary>

1. Iterate `for v in reversed(adj[u])`. The last pushed is popped first, so the first neighbour is explored first.

```python
def dfs_order_same(adj, root):
    parent = [-1] * len(adj)
    parent[root] = root
    order = []
    stack = [root]
    while stack:
        u = stack.pop()
        order.append(u)
        for v in reversed(adj[u]):
            if parent[v] == -1:
                parent[v] = u
                stack.append(v)
    return order

adj = [[1, 2], [0, 3, 4], [0, 5], [1], [1], [2]]
print(dfs_order_same(adj, 0))
```
```text
[0, 1, 3, 4, 2, 5]
```

Caveat: marking a node as visited when it is **pushed** (as we do) can give an order that differs from true recursive DFS on graphs with cycles. For trees it matches.

2. Use the visiting order, where a parent always comes before its children:

```python
def tree_depths(adj, root):
    depth = [-1] * len(adj)
    depth[root] = 0
    stack = [root]
    while stack:
        u = stack.pop()
        for v in adj[u]:
            if depth[v] == -1:
                depth[v] = depth[u] + 1
                stack.append(v)
    return depth

adj = [[1, 2], [0, 3, 4], [0, 5], [1], [1], [2]]
print(tree_depths(adj, 0))
```
```text
[0, 1, 1, 2, 2, 2]
```

</details>

## 9. PyPy versus CPython

### What PyPy is

**CPython** is the interpreter you have been using: the reference implementation, written in C. It executes bytecode instruction by instruction.

**PyPy** is another implementation of Python with a **just-in-time (JIT) compiler**. It watches your program run, finds loops that run many times ("hot" loops), and translates them to machine code on the fly. For plain numeric loops, this can make PyPy many times faster than CPython. It implements the Python language, so ordinary programs give the same answers.

On Codeforces and several other judges you choose "PyPy 3" (or similar) when you submit. This is the biggest single performance decision you make in Python.

### Is PyPy installed here?

You can check with the standard library. This tells you whether to try the experiments of this section.

```python
import shutil, sys, platform

print("running on:", platform.python_implementation(), sys.version.split()[0])
print("pypy3 on PATH:", shutil.which("pypy3") is not None)
```
```text
running on: CPython 3.14.4
pypy3 on PATH: False
```

If `pypy3` is not on your PATH, you can still follow this section. The qualitative statements (what PyPy is good and bad at) hold on every machine; we give **no** PyPy timing numbers here, because we only publish numbers we measured. If you install PyPy (from your package manager or `pypy.org`), run the benchmark file in section 3 with `pypy3` instead of `python3` and record the ratios yourself. This is a worthwhile exercise.

### What PyPy is very good at

- Tight loops over integers and lists: `for i in range(n): total += a[i]`.
- Simple arithmetic, comparisons, list indexing, list `append`.
- Plain functions called many times (the JIT can inline them).
- Dynamic programming with nested loops over lists. A `10^7`-step DP that takes many seconds in CPython is commonly feasible in PyPy.

The JIT needs a short **warm-up**: the first thousand or so passes of a loop run in the slow interpreter while PyPy gathers information. That makes tiny programs slightly slower on PyPy than on CPython. It only matters for programs that run for a few milliseconds.

### What PyPy is bad at, or different about

| Topic | CPython | PyPy |
|---|---|---|
| Plain loops and arithmetic | slow | usually much faster |
| Built-in C-implemented functions (`sorted`, `sum`, `str.join`, `list.sort`, big `int` math) | fast, written in C | fast too, but their advantage over loops is smaller; some are not faster than on CPython |
| Very large integers (hundreds of digits) | optimised in C | similar or slower |
| Memory use | lower | typically higher for the same program (the JIT and its data structures use extra memory) |
| Recursion | limit 1000, raise with `setrecursionlimit`, stack-size threading trick | `setrecursionlimit` has effect, but deep recursion uses a lot of memory; the thread trick works differently or may not be needed. Prefer iterative code |
| `numpy` and other C extension modules | available if installed | usually **not available** on judges |
| String concatenation in a loop (`s += c`) | has an in-place optimisation that is not guaranteed | can be quadratic: **do not rely on it**; use `"".join` |
| `sys.stdin.read` and `print` | fast | fast; but reading with many tiny `input()` calls is slow in both |
| Very first-time execution of rarely run code | no warm-up | warm-up cost |

Two points deserve more explanation.

**Memory.** A CPython list of integers stores pointers to int objects, and small ints (-5 to 256) are shared. PyPy stores lists of plain integers in a compact form when it can. In practice you cannot predict this; the lesson is: *measure memory too*, and keep arrays you do not need out of the program. With a 256 MB limit, a Python program that builds a `10^7`-element list of lists will fail in either interpreter.

**String building.** `s += "x"` in a loop is `O(n)` per step in the worst case, because strings are immutable and a new string may be built each time. CPython sometimes performs the append in place and hides the problem, so the code seems fine locally and then hits quadratic time on a judge running PyPy. Always append to a list and `join` once:

```python
parts = []
for i in range(5):
    parts.append(str(i))
print("".join(parts))
```
```text
01234
```

### How to choose

A simple decision procedure for a Codeforces submission:

1. **Default to PyPy** for problems whose time comes from your own loops: DP, simulation, sieve, nested loops, graph search with explicit stacks and queues.
2. **Use CPython** when the problem leans heavily on a library that needs C extensions (rare on judges), on huge integers (big-number factorial, Fibonacci of a million digits), on deep recursion with the thread trick, or when your measurements show it is faster.
3. If you get *time limit exceeded* on one, **try the other**, as a cheap first experiment, before redesigning the algorithm. Then still check the complexity table: a `10^10` algorithm is too slow in both.
4. If you get *memory limit exceeded* on PyPy, try CPython or reduce the memory (use `array` or bytes, section 10).

### Same code, both interpreters

Write your solution so that it is correct on both. That means: no reliance on `s += c` speed, no reliance on CPython's recursion limit semantics, and no `numpy`. Write one template and check it with whichever interpreter you have.

### Measure with your own harness

The timing harness of section 3 works on PyPy unchanged. The ratio between CPython and PyPy depends on the program, so never trust a rule like "PyPy is 10 times faster": run your own loops. Keep one results table in your notebook:

| Workload | CPython time | PyPy time |
|---|---|---|
| 10^6 plain loop passes | (measure) | (measure) |
| sort 10^6 random ints | (measure) | (measure) |
| 5000x5000 DP | (measure) | (measure) |
| dictionary with 10^6 keys | (measure) | (measure) |

### Common PyPy surprises

- **Different behaviour of dictionary iteration order is not a surprise**: both keep insertion order, as of Python 3.7. Do not depend on set order though (sets of strings can differ between runs for any interpreter).
- **A program passes locally on CPython but gets "runtime error" on PyPy** is usually deep recursion or memory.
- **`int` from a very long string** works the same in both, but CPython 3.11 and later limit int/str conversion to 4300 digits by default (`ValueError`). If a problem prints or parses a 10^5-digit number, set `sys.set_int_max_str_digits(0)`. Check what your judge's version supports before relying on this.

## 10. Micro-optimisations that matter

The first rule is: **a better algorithm beats any micro-optimisation**. Do these only after the complexity is right and a timing test says you are close to the limit. The second rule is: **measure**; every trick below is accompanied by a measurement.

We reuse the `bench`/`compare` helper from section 3. To keep each example self-contained, it is repeated in compact form.

### 1. Local variables are faster than globals

Inside a function, a local variable is stored in a fixed slot. A global is looked up by name in a dictionary every time. In a hot loop the difference is real.

```python
import time

def bench(fn, repeat=3):
    best = float("inf")
    for _ in range(repeat):
        s = time.perf_counter(); fn(); best = min(best, time.perf_counter() - s)
    return best

total = 0
def global_loop():
    global total
    total = 0
    for i in range(10**6):
        total += i

def local_loop():
    total = 0
    for i in range(10**6):
        total += i

g, l = bench(global_loop), bench(local_loop)
print("global %.3f s, local %.3f s, ratio %.2f (machine-specific)" % (g, l, g / l))
```
```text
global 0.052 s, local 0.036 s, ratio 1.47 (machine-specific)
```

Rule: put all code inside `def main()` and call it. Top-level code uses globals.

### 2. Cache method lookups: `append = out.append`

`out.append(x)` looks up `append` on `out` each time. Binding it once saves that work.

```python
import time

def bench(fn, repeat=3):
    best = float("inf")
    for _ in range(repeat):
        s = time.perf_counter(); fn(); best = min(best, time.perf_counter() - s)
    return best

def lookup_each():
    out = []
    for i in range(10**6):
        out.append(i)

def lookup_once():
    out = []
    push = out.append
    for i in range(10**6):
        push(i)

a, b = bench(lookup_each), bench(lookup_once)
print("method each time %.3f s, cached %.3f s, ratio %.2f (machine-specific)" % (a, b, a / b))
```
```text
method each time 0.046 s, cached 0.049 s, ratio 0.93 (machine-specific)
```

The gain is small, and on recent CPython versions (our run used 3.14, whose interpreter already speeds up repeated method calls) it can vanish into noise. On older versions it often gave a few percent. Treat it as optional. A shorter name is still handy for `heappush`, `heappop` and `bisect_left`: write `from heapq import heappush, heappop` at the top and call them directly, which also saves typing in a contest.

### 3. List comprehensions and built-ins beat hand loops

A comprehension runs its loop with less bytecode per item. `sum`, `max`, `min`, `sorted`, `any`, `all`, `map` run their loops in C.

```python
import time

def bench(fn, repeat=3):
    best = float("inf")
    for _ in range(repeat):
        s = time.perf_counter(); fn(); best = min(best, time.perf_counter() - s)
    return best

a = list(range(10**6))

def manual_max():
    m = a[0]
    for x in a:
        if x > m:
            m = x
    return m

def builtin_max():
    return max(a)

def manual_sum():
    t = 0
    for x in a:
        t += x
    return t

x, y = bench(manual_max), bench(builtin_max)
z, w = bench(manual_sum), bench(lambda: sum(a))
print("max: loop %.4f s, builtin %.4f s, ratio %.1f" % (x, y, x / y))
print("sum: loop %.4f s, builtin %.4f s, ratio %.1f" % (z, w, z / w))
```
```text
max: loop 0.0195 s, builtin 0.0114 s, ratio 1.7
sum: loop 0.0293 s, builtin 0.0062 s, ratio 4.7
```

(Machine-specific timings.) On CPython the built-ins are several times faster. On PyPy the gap is smaller, since the JIT already compiles the hand loop. The advice "use built-ins" never hurts on either.

### 4. List versus dictionary versus set

- A list of size `n` indexed by a small integer is faster and smaller than a dictionary with integer keys. Use a list when keys are `0..n-1`.
- Dictionary or set when keys are sparse (large, strings, tuples). Membership `x in some_set` is `O(1)`; `x in some_list` is `O(n)`.

```python
import time

def bench(fn, repeat=3):
    best = float("inf")
    for _ in range(repeat):
        s = time.perf_counter(); fn(); best = min(best, time.perf_counter() - s)
    return best

N = 10**5
lst = list(range(N))
st = set(lst)
queries = list(range(0, N * 2, 20))

def list_member():
    return sum(1 for q in queries[:2000] if q in lst)

def set_member():
    return sum(1 for q in queries[:2000] if q in st)

assert list_member() == set_member()
a, b = bench(list_member), bench(set_member)
print("list membership %.4f s, set membership %.6f s, ratio %.0f (machine-specific)" % (a, b, a / b))
```
```text
list membership 0.2097 s, set membership 0.000099 s, ratio 2109 (machine-specific)
```

(2000 membership tests only; the list version already takes a visible fraction of a second, and the ratio explodes with bigger sizes.)

### 5. Avoid tuples and small objects in the hottest loop

Creating a tuple `(a, b)` for each step allocates memory. In Dijkstra-like code, `heappush(h, (d, v))` is needed; but in a tight DP loop, prefer two parallel lists or a single encoded integer.

An integer encoding trick: store the pair `(d, v)` as one integer `d * N + v`, where `v < N`. Comparing and heap-ordering integers is faster than comparing tuples, and the pair is recovered with `divmod`.

```python
import heapq, time

def bench(fn, repeat=3):
    best = float("inf")
    for _ in range(repeat):
        s = time.perf_counter(); fn(); best = min(best, time.perf_counter() - s)
    return best

N = 10**6
items = [(i * 7919) % 100003 for i in range(10**5)]

def heap_tuples():
    h = []
    for i, d in enumerate(items):
        heapq.heappush(h, (d, i))
    out = 0
    while h:
        d, i = heapq.heappop(h)
        out += i
    return out

def heap_encoded():
    h = []
    for i, d in enumerate(items):
        heapq.heappush(h, d * N + i)
    out = 0
    while h:
        d, i = divmod(heapq.heappop(h), N)
        out += i
    return out

assert heap_tuples() == heap_encoded()
a, b = bench(heap_tuples), bench(heap_encoded)
print("tuples %.3f s, encoded ints %.3f s, ratio %.2f (machine-specific)" % (a, b, a / b))
```
```text
tuples 0.187 s, encoded ints 0.098 s, ratio 1.91 (machine-specific)
```

The `assert` is important: always check that an optimised version gives the same answer as the plain one. Only encode when the number stays below about `2^63` (no problem in Python, but beyond that integers become "big" and slower).

### 6. Bit tricks

| Task | Expression |
|---|---|
| Is `x` even? | `x & 1 == 0` (careful with precedence; write `(x & 1) == 0`) |
| Multiply / divide by 2 | `x << 1`, `x >> 1` |
| Is `x` a power of two (`x > 0`)? | `x & (x - 1) == 0` |
| Lowest set bit | `x & -x` |
| Number of set bits | `x.bit_count()` (3.10+) or `bin(x).count("1")` |
| Bit length | `x.bit_length()` |
| Test bit `i` | `(x >> i) & 1` |
| Set / clear / flip bit `i` | `x | (1 << i)`, `x & ~(1 << i)`, `x ^ (1 << i)` |

```python
x = 40
print("binary:", bin(x))
print("lowest set bit:", x & -x)
print("bit count:", x.bit_count(), " bit length:", x.bit_length())
print("power of two?", (x & (x - 1)) == 0, (64 & 63) == 0)

# iterate over all subsets of a 4-element set with bitmasks
n = 4
print(sum(1 for mask in range(1 << n)))
print([i for i in range(n) if (0b1010 >> i) & 1])
```
```text
binary: 0b101000
lowest set bit: 8
bit count: 2  bit length: 6
power of two? False True
16
[1, 3]
```

Python's `x // 2` on a non-negative int equals `x >> 1`, but the shift is not always faster in CPython; the gain is small. Bit **tricks as algorithms** (bitmask DP, subset enumeration, the Fenwick lowbit from dsa.16) matter more than bit shifts as micro-optimisation.

### 7. `divmod`, `math.isqrt`, and integer-only arithmetic

- `divmod(a, b)` gives quotient and remainder in one call. Useful for flattening a 2D index: `r, c = divmod(idx, width)`.
- `math.isqrt(n)` is the **exact** integer square root. `int(n ** 0.5)` can be off by one for large `n` because floats have 53 bits of precision.
- Prefer `//` to `int(a / b)`. The float division loses precision above `2^53`.

```python
import math

n = 10**18
print("isqrt exact :", math.isqrt(n))
big = 10**30 + 7
print("float root  :", int(big ** 0.5), "  isqrt:", math.isqrt(big))
print("isqrt^2 <= n < (isqrt+1)^2:", math.isqrt(big) ** 2 <= big < (math.isqrt(big) + 1) ** 2)

print(divmod(17, 5), divmod(-17, 5))
r, c = divmod(23, 6)
print("cell", r, c)

a, b = 10**17 + 3, 7
print(a // b, int(a / b))
```
```text
isqrt exact : 1000000000
float root  : 1000000000000000   isqrt: 1000000000000000
isqrt^2 <= n < (isqrt+1)^2: True
(3, 2) (-4, 3)
cell 3 5
14285714285714286 14285714285714286
```

Look at the last line: `a // b` is exact; `int(a / b)` goes through a float and can differ in the low digits. When it matters, always use `//`.

(Notice `divmod(-17, 5)` is `(-4, 3)`: Python's `%` result has the sign of the divisor, so the remainder is never negative for a positive modulus. In C++ the result would be `-2`. Remember this when you read editorials written for C++.)

### 8. Standard-library tools worth knowing

| Module / function | Use | Complexity |
|---|---|---|
| `heapq.heappush/heappop` | priority queue (min-heap) | `O(log n)` |
| `heapq.heapify(list)` | build a heap in place | `O(n)` |
| `bisect.bisect_left/right`, `insort` | binary search in a sorted list | `O(log n)`; `insort` is `O(n)` because of shifting |
| `collections.deque` | queue with `O(1)` at both ends; BFS | `O(1)` |
| `collections.Counter` | frequency table | `O(n)` |
| `itertools.accumulate` | prefix sums | `O(n)` |
| `itertools.permutations/combinations/product` | brute force enumeration | output size |
| `functools.lru_cache` | memoised recursion (but beware recursion depth) | per call |
| `math.gcd`, `math.lcm`, `math.comb`, `math.factorial`, `math.isqrt` | number theory | varies |

```python
from itertools import accumulate, combinations
from collections import deque, Counter
from bisect import bisect_left, bisect_right
import heapq, math

a = [3, 1, 4, 1, 5, 9, 2, 6]
print(list(accumulate(a)))                     # prefix sums
print(Counter(a).most_common(2))
print(list(combinations([1, 2, 3], 2)))
s = sorted(a)
print(s, bisect_left(s, 4), bisect_right(s, 4))
h = a[:]
heapq.heapify(h)
print([heapq.heappop(h) for _ in range(3)])
q = deque([1, 2, 3]); q.appendleft(0); print(q.popleft(), q.pop(), list(q))
print(math.gcd(12, 18), math.lcm(4, 6), math.comb(5, 2), math.factorial(5))
```
```text
[3, 4, 8, 9, 14, 23, 25, 31]
[(1, 2), (3, 1)]
[(1, 2), (1, 3), (2, 3)]
[1, 1, 2, 3, 4, 5, 6, 9] 4 5
[1, 1, 2]
0 3 [1, 2]
6 12 10 120
```

Python's `deque` has no `O(1)` access in the middle. A list's `pop(0)` is `O(n)`: **never use a list as a queue** for BFS with many items. This one mistake turns `O(n)` into `O(n^2)`.

```python
import time
from collections import deque

def bench(fn, repeat=3):
    best = float("inf")
    for _ in range(repeat):
        s = time.perf_counter(); fn(); best = min(best, time.perf_counter() - s)
    return best

N = 60000

def list_queue():
    q = list(range(N))
    while q:
        q.pop(0)

def deque_queue():
    q = deque(range(N))
    while q:
        q.popleft()

a, b = bench(list_queue), bench(deque_queue)
print("list.pop(0) %.4f s, deque.popleft %.4f s, ratio %.0f (machine-specific)" % (a, b, a / b))
```
```text
list.pop(0) 0.4162 s, deque.popleft 0.0032 s, ratio 130 (machine-specific)
```

### 9. Precompute once, outside the test loop

If every test needs factorials, primes, or a table, compute it **once** for the maximum size before reading the tests. We do this in the next section for factorials.

### 10. Integers versus floats

Float arithmetic is not slower than integer arithmetic for single operations, but a float has 53 bits of precision. Use floats only when the problem is about real numbers. Never use `/` where `//` is meant. For comparing real numbers, compare with a small tolerance, never with `==`.

```python
print(0.1 + 0.2 == 0.3)
print(abs((0.1 + 0.2) - 0.3) < 1e-9)
print(2**53 + 1, float(2**53 + 1) == float(2**53))
```
```text
False
True
9007199254740993 True
```

### 11. Memory: avoid big structures you do not need

A list of `10^7` ints uses about 80 MB for pointers on a 64-bit machine, plus the int objects. A 2D list of size `5000 x 5000` is 25 million cells, around 200 MB just for the pointers. Options:

- Keep **two rows** of a DP instead of the whole table.
- Use `bytearray` for flags (one byte per entry; a `bytearray(10**7)` is 10 MB), as in the sieve below.
- Use the `array` module (`array("i", ...)`) for compact numbers.

```python
import sys
from array import array

n = 10**5
as_list = [0] * n
as_bytes = bytearray(n)
as_array = array("i", [0]) * n
print("list of pointers  :", sys.getsizeof(as_list), "bytes")
print("bytearray         :", sys.getsizeof(as_bytes), "bytes")
print("array('i') (4 B)  :", sys.getsizeof(as_array), "bytes")
```
```text
list of pointers  : 800056 bytes
bytearray         : 100057 bytes
array('i') (4 B)  : 400080 bytes
```

(Exact sizes can differ slightly between Python versions and platforms.) The list is 8 times bigger than the bytearray per entry, before counting any int objects other than the shared zero.

## 11. Modular arithmetic and number-theory templates

### Why "modulo 10^9 + 7"

Many counting problems have answers far too large to print, so the statement says "print the answer modulo `1_000_000_007`" (written `10^9 + 7`) or modulo `998244353`. Both are **prime** numbers around `10^9`. Prime moduli give us division (through inverses), and numbers below `10^9` multiply to less than `10^18`, which fits a 64-bit integer in other languages. In Python the size is no problem, but the **modular rules** still matter.

### The rules

For `+`, `-`, `*`, you can reduce at any step:

- `(a + b) % M == ((a % M) + (b % M)) % M`
- `(a * b) % M == ((a % M) * (b % M)) % M`

Python's `%` returns a result in `[0, M)` even for negative operands, so `(a - b) % M` is safe (in C++ you must add `M`).

**Division does not work like that.** `(a / b) % M` is not `(a % M) / (b % M)`. To divide, multiply by the **modular inverse** of `b`, defined by `b * inv(b) % M == 1`.

### Fast power

Computing `a ** e % M` by first computing `a ** e` would build a number with millions of digits. Python's three-argument `pow(a, e, M)` reduces at every step, in `O(log e)` multiplications. This is the same square-and-multiply idea as dsa.01's fast-exponent exercise.

```python
import time

M = 10**9 + 7
print(pow(2, 10, M))
print(pow(2, 10**18, M))        # instant

# what it replaces
def slow_pow(a, e, m):
    r = 1
    for _ in range(e):
        r = r * a % m
    return r

print(slow_pow(3, 10**5, M) == pow(3, 10**5, M))

# own square-and-multiply, to see the idea
def mod_pow(a, e, m):
    r = 1
    a %= m
    while e:
        if e & 1:
            r = r * a % m
        a = a * a % m
        e >>= 1
    return r

print(mod_pow(2, 10**18, M) == pow(2, 10**18, M))
```
```text
1024
719476260
True
True
```

Complexity: `O(log e)`.

### Modular inverse

For a prime `M`, Fermat's little theorem says `b^(M-1) ≡ 1`, so `b^(M-2)` is the inverse: `inv = pow(b, M - 2, M)`. Python 3.8+ also accepts a negative exponent: `pow(b, -1, M)`, which works for any `M` coprime to `b` (using the extended Euclid algorithm).

```python
M = 10**9 + 7
b = 123456
inv1 = pow(b, M - 2, M)
inv2 = pow(b, -1, M)
print(inv1 == inv2, b * inv1 % M)

# divide 10**12 by 6 modulo M
a = 10**12
print(a * pow(6, -1, M) % M)
print((a // 6) % M)
print(a % 6)
```
```text
True 1
333332169
666665504
4
```

Careful with the last two lines: `a % 6` is `4`, so `a` is **not** divisible by 6, and the integer quotient `a // 6` (third line) is not the modular quotient (second line). The two numbers differ. The modular "division" gives a number such that multiplied by 6 returns `a` modulo `M`. Check:

```python
M = 10**9 + 7
a = 10**12
q = a * pow(6, -1, M) % M
print(q * 6 % M == a % M)
```
```text
True
```

### nCr modulo a prime with factorials

Counting combinations `C(n, r)` many times: precompute factorials and inverse factorials once, then each query is two multiplications.

`C(n, r) = n! / (r! * (n - r)!)`, so `C(n, r) = fact[n] * inv_fact[r] * inv_fact[n - r] mod M`. The inverse factorials are computed from the **top** to avoid `N` calls to `pow`: compute `inv_fact[N]` with one `pow`, then `inv_fact[i - 1] = inv_fact[i] * i`.

```python
import math

M = 10**9 + 7
N = 10**6

fact = [1] * (N + 1)
for i in range(1, N + 1):
    fact[i] = fact[i - 1] * i % M

inv_fact = [1] * (N + 1)
inv_fact[N] = pow(fact[N], M - 2, M)
for i in range(N, 0, -1):
    inv_fact[i - 1] = inv_fact[i] * i % M

def nCr(n, r):
    if r < 0 or r > n:
        return 0
    return fact[n] * inv_fact[r] % M * inv_fact[n - r] % M

print(nCr(5, 2), nCr(10, 0), nCr(10, 11))
print(nCr(1000, 500) == math.comb(1000, 500) % M)
print(nCr(10**6, 3) == math.comb(10**6, 3) % M)
```
```text
10 1 0
True
True
```

Complexity: `O(N)` precomputation, `O(1)` per query. Notes:

- The precomputation covers `N` as large as the largest `n` in any test. Pick `N` from the statement's constraint.
- `r > n` returns `0` (guard needed, or the index goes wrong).
- Modulo must be **prime and larger than `N`**. With a composite modulus, factorial inverses may not exist.
- `math.comb(n, r) % M` is exact but slow for huge `n`; the table is for many queries.

### Sieve of Eratosthenes

All primes up to `N` in `O(N log log N)`. Use a `bytearray`, and slice assignment for the inner loop to run in C.

```python
def sieve(n):
    is_prime = bytearray([1]) * (n + 1)
    is_prime[0:2] = b"\x00\x00"
    for i in range(2, int(n ** 0.5) + 1):
        if is_prime[i]:
            is_prime[i * i::i] = bytearray(len(range(i * i, n + 1, i)))
    return is_prime

n = 50
p = sieve(n)
print([i for i in range(n + 1) if p[i]])
print(sum(sieve(10**6)))             # number of primes below 10**6
```
```text
[2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
78498
```

`78498` primes below one million is a famous number; if your sieve prints something else, there is a bug. The slice `is_prime[i*i::i]` is every `i`-th entry from `i*i`; assigning zeros of the same length removes them all in one C-level operation. `len(range(i*i, n+1, i))` computes the slice length without building the list.

#### Smallest prime factor sieve: factorise fast

For many factorisation queries, store the **smallest prime factor** for every number, then divide repeatedly.

```python
def spf_sieve(n):
    spf = list(range(n + 1))
    for i in range(2, int(n ** 0.5) + 1):
        if spf[i] == i:                       # i is prime
            for j in range(i * i, n + 1, i):
                if spf[j] == j:
                    spf[j] = i
    return spf

def factorise(x, spf):
    out = []
    while x > 1:
        p = spf[x]
        cnt = 0
        while x % p == 0:
            x //= p
            cnt += 1
        out.append((p, cnt))
    return out

spf = spf_sieve(1000)
print(factorise(360, spf))
print(factorise(997, spf))
print(factorise(1000, spf))
```
```text
[(2, 3), (3, 2), (5, 1)]
[(997, 1)]
[(2, 3), (5, 3)]
```

### GCD, LCM, and trial division

`math.gcd(a, b)` runs in `O(log min(a, b))`. `math.lcm(a, b)` exists (3.9+). For one number up to about `10^12`, trial division up to its square root (`10^6` steps) is enough.

```python
import math

def is_prime(n):
    if n < 2:
        return False
    if n % 2 == 0:
        return n == 2
    i = 3
    while i * i <= n:
        if n % i == 0:
            return False
        i += 2
    return True

print([x for x in range(30) if is_prime(x)])
print(is_prime(10**9 + 7), is_prime(10**9 + 9), is_prime(10**9 + 8))
print(math.gcd(10**18, 6 * 10**17), math.lcm(12, 18))
```
```text
[2, 3, 5, 7, 11, 13, 17, 19, 23, 29]
True True False
200000000000000000 36
```

Complexity of `is_prime`: `O(sqrt n)`. For `n` near `10^9` that is about 16,000 steps; for `10^18` it would be `5 * 10^8`: too slow, and the intended solution would use Miller-Rabin (not covered here).

### Try it

1. Compute `5^(10^9) mod (10^9 + 7)` with `pow`.
2. What is `C(10, 3) mod 7`? Why is the factorial method not valid here?

<details><summary>Answer</summary>

```python
M = 10**9 + 7
print(pow(5, 10**9, M))

import math
print(math.comb(10, 3) % 7)
```
```text
142848001
1
```

`C(10,3) = 120`, and `120 % 7 = 1`. The factorial-and-inverse method needs a prime modulus bigger than `n`: here `7 < 10`, and `10!` contains the factor 7, so `10!` is `0` modulo 7 and has no inverse structure we can use.

</details>

## 12. A template file

### Why have a template

At the start of a contest, every second counts and every typo hurts. Competitors keep a **template**: a file they copy for each problem with the boilerplate already written. You should too.

### A good template does four things

1. Sets up fast input (Pattern C or D).
2. Puts the solution inside functions (local variables).
3. Reads test cases in a loop and collects the output.
4. Leaves a clear place where the problem-specific code goes.

Here is a template. Save it as `template.py` in your own folder.

```python
import sys
from collections import deque, Counter
from heapq import heappush, heappop
from bisect import bisect_left, bisect_right
from itertools import accumulate
from math import gcd, isqrt, inf

def solve(it):
    n = int(next(it))
    a = [int(next(it)) for _ in range(n)]
    # ---- problem-specific code goes here ----
    return str(sum(a))

def main():
    it = iter(sys.stdin.read().split())
    t = int(next(it))
    out = []
    for _ in range(t):
        out.append(solve(it))
    sys.stdout.write("\n".join(out) + "\n")

main()
```

Test it: it should give the sum for each test.

```text
2
3 1 2 3
2 10 20
```
```python
import sys
from math import gcd

def solve(it):
    n = int(next(it))
    a = [int(next(it)) for _ in range(n)]
    return str(sum(a))

def main():
    it = iter(sys.stdin.read().split())
    t = int(next(it))
    out = []
    for _ in range(t):
        out.append(solve(it))
    sys.stdout.write("\n".join(out) + "\n")

main()
```
```text
6
30
```

(The imports in the block you will paste are listed at the top; the run above shortened them so the example is minimal. Unused imports cost nothing.)

### Variants to keep

- **Single test case** (no `t`): drop the loop.
- **Query problems:** read `n`, array, `q`, then `q` queries inside `solve`.
- **Graph problem:** a helper to read `n`, `m`, and build `adj`.
- **Interactive:** `input = sys.stdin.readline` and `flush=True` (section 7).
- **Recursive solution:** the thread recipe (section 8) wrapped around `main`.

```python
import sys, threading

def main():
    ...

sys.setrecursionlimit(10**6)
threading.stack_size(128 * 1024 * 1024)
threading.Thread(target=main).start()
```

### Local setup

Keep a folder per contest and a file per problem: `A.py`, `B.py`, and files `A.in`, `A.out`. Run with `python3 A.py < A.in`. A tiny shell loop, or the Python script in the next section, compares the output to the expected one. With the `./learn` system you can also record your attempt, but contests use your own files.

### Do not copy-paste code you do not understand

A library is useful only if you can reconstruct it. The capstone of this track is exactly this: your own algorithms library, with tests and benchmarks. Add each tested piece (modular nCr, DSU from dsa.12, Fenwick from dsa.16) to it **after** you have used it in a problem.

## 13. Stress testing: finding the failing input yourself

### Why

On a judge you see only a verdict, such as "wrong answer on test 7", and often not even the input. Offline you can do far better: if you have a slow solution that you *trust* (a **brute force**), you can generate thousands of small random inputs, run both, and stop at the first difference. That difference is a tiny failing input you can trace by hand.

### The three pieces

1. **The solution** you want to test (`fast`).
2. **A brute force** (`brute`): obviously correct, as slow as you like, for small inputs.
3. **A generator** (`gen`): produces random small inputs, with a **fixed seed** for repeatability.

The loop: generate, run both, compare, stop on the first mismatch.

### A worked example

The problem: given a list of integers (which may be negative), find the maximum sum of a non-empty contiguous subarray. A tempting fast solution is Kadane's algorithm initialised with the wrong value:

```python
import random

def fast(a):
    best = 0                     # BUG: should start at the first element
    cur = 0
    for x in a:
        cur = max(x, cur + x)
        best = max(best, cur)
    return best

def brute(a):
    n = len(a)
    return max(sum(a[i:j]) for i in range(n) for j in range(i + 1, n + 1))

def gen(rng):
    n = rng.randint(1, 5)
    return [rng.randint(-5, 5) for _ in range(n)]

rng = random.Random(2024)
for trial in range(1, 1001):
    a = gen(rng)
    if fast(a) != brute(a):
        print("mismatch after", trial, "trials")
        print("input :", a)
        print("fast  :", fast(a))
        print("brute :", brute(a))
        break
else:
    print("no mismatch in 1000 trials")
```
```text
mismatch after 11 trials
input : [-2, -2, -5, -2]
fast  : 0
brute : -2
```

The failing input is tiny: all numbers negative, so the true answer is negative but the buggy `best = 0` claims the empty subarray (sum 0). With the input in front of you, the bug is obvious. This is the power of the method. Fix: `best = a[0]`, `cur = a[0]`, loop from `a[1:]`... or `best = -inf`. Let us check the fixed version in the same loop.

```python
import random

def fast(a):
    best = cur = a[0]
    for x in a[1:]:
        cur = max(x, cur + x)
        best = max(best, cur)
    return best

def brute(a):
    n = len(a)
    return max(sum(a[i:j]) for i in range(n) for j in range(i + 1, n + 1))

rng = random.Random(2024)
bad = 0
for trial in range(3000):
    n = rng.randint(1, 8)
    a = [rng.randint(-10, 10) for _ in range(n)]
    if fast(a) != brute(a):
        bad += 1
print("mismatches in 3000 trials:", bad)
```
```text
mismatches in 3000 trials: 0
```

### Why small inputs

Small inputs find bugs faster and make the failing case readable. Most bugs show up on inputs with `n <= 6` and values in `[-5, 5]` or `[0, 3]`. Small value ranges force **duplicates**, which large random values hide.

### Stress testing as a reusable function

Package it, so for every problem you only write `fast`, `brute`, and `gen`.

```python
import random

def stress(fast, brute, gen, trials=1000, seed=1):
    rng = random.Random(seed)
    for t in range(trials):
        case = gen(rng)
        a = fast(*case)
        b = brute(*case)
        if a != b:
            return case, a, b
    return None

# Example: count pairs i<j with a[i]+a[j]==k, two-pointer on sorted vs brute
def fast(a, k):
    s = sorted(a)
    i, j = 0, len(s) - 1
    cnt = 0
    while i < j:
        t = s[i] + s[j]
        if t == k:
            cnt += 1          # BUG: duplicates are not counted properly
            i += 1
            j -= 1
        elif t < k:
            i += 1
        else:
            j -= 1
    return cnt

def brute(a, k):
    n = len(a)
    return sum(1 for i in range(n) for j in range(i + 1, n) if a[i] + a[j] == k)

def gen(rng):
    n = rng.randint(2, 6)
    return [rng.randint(0, 3) for _ in range(n)], rng.randint(0, 6)

res = stress(fast, brute, gen)
if res:
    case, a, b = res
    print("failing case:", case)
    print("fast says", a, "but brute says", b)
```
```text
failing case: ([3, 0, 3, 2, 1], 4)
fast says 1 but brute says 2
```

In the failing case the value `3` appears twice and each copy pairs with the `1`, so the true count is 2. The two-pointer loop counts one pair, then moves both pointers and loses the second. Counting pairs among duplicates needs a count-based formula, not a single increment. The tiny failing case lets you see it in seconds.

### Finding the bug: shrink the input

If a failing case is not small enough, **shrink** it: try removing elements one at a time and keep any smaller list that still fails. Here is a tiny shrinker.

```python
def shrink(a, still_fails):
    """Remove elements one at a time while the failure persists."""
    changed = True
    while changed:
        changed = False
        for i in range(len(a)):
            smaller = a[:i] + a[i + 1:]
            if smaller and still_fails(smaller):
                a = smaller
                changed = True
                break
    return a

def fast(a):
    best = 0
    cur = 0
    for x in a:
        cur = max(x, cur + x)
        best = max(best, cur)
    return best

def brute(a):
    n = len(a)
    return max(sum(a[i:j]) for i in range(n) for j in range(i + 1, n + 1))

big = [-3, -7, -2, -1, -5, -9, -4]
print("fails on big:", fast(big) != brute(big))
small = shrink(big, lambda x: fast(x) != brute(x))
print("shrunk to :", small)
```
```text
fails on big: True
shrunk to : [-4]
```

### Timing stress: a generator for the worst case

Wrong answers are one failure. Slowness is the other. For the time limit, run `fast` on the **largest** input and time it with the harness of section 3. Generator ideas for large worst cases:

- random values (average),
- all values equal,
- already sorted, reverse sorted,
- a chain graph, a star graph, a complete graph,
- alternating patterns (`1, 0, 1, 0, ...`),
- maximum values (`10^9`) and minimum values,
- `n = 1`, `n = 2` (smallest cases for off-by-one).

### The same idea as shell scripts

If you keep solutions as separate files, a tiny loop does the job:

```text
for i in $(seq 1 500); do
    python3 gen.py $i > in.txt
    python3 fast.py < in.txt > out_fast.txt
    python3 brute.py < in.txt > out_brute.txt
    cmp -s out_fast.txt out_brute.txt || { echo "DIFF on seed $i"; break; }
done
```

Here `gen.py` takes the seed as `sys.argv[1]` and calls `random.seed(...)`. The in-process version above is faster (no process start per test), which matters when you run 10,000 trials.

## 14. Verdicts and debugging

### The verdicts

| Verdict | Meaning | Most likely causes |
|---|---|---|
| **AC** Accepted | All tests passed | Done |
| **WA** Wrong answer on test k | Output differs | Logic error; corner case; off-by-one; wrong output format; integer division vs float; uninitialised state between tests |
| **TLE** Time limit exceeded | Too slow (or infinite loop, or interactive without flush) | Wrong complexity; Python overhead; slow input; try PyPy; recursion |
| **MLE** Memory limit exceeded | Used too much memory | Huge arrays; storing all of a DP table; PyPy overhead; deep recursion; lists of lists |
| **RE** Runtime error | Crash | `IndexError`; `RecursionError`; `ValueError` from parsing; division by zero; reading past the input; stack overflow |
| **ILE** Idleness limit exceeded | No output for too long | Interactive problem, missing flush |
| **PE** Presentation error | Output format is wrong | Extra or missing whitespace (strict judges) |
| **CE** Compilation error | Syntax error | Typo; a feature not available in the judge's Python version |

### A debugging order

1. **Re-read the statement.** Most WA verdicts on early tests are misreadings. Check the units, the 0-/1-indexing, "at least" versus "at most", inclusive versus exclusive ranges.
2. **Run the samples.** If a sample fails, that is a bug, not a corner case.
3. **Check the output format** (section 5).
4. **Think about corner cases:** `n = 1`, all equal, already sorted, negative numbers, zero, maximum values, empty answer.
5. **Stress test** against a brute force (section 13).
6. **Look at the failing test number.** Test 1 is a sample. Small test numbers are small cases (a logic or format bug). A failure at the first big test is often overflow (not in Python), TLE, or a hidden structure the examples did not show.
7. **Use asserts** for invariants you believe: `assert 0 <= i < n`. A crash with a message beats a silent wrong answer.
8. **Print to stderr**, never stdout, in a program that you submit.

### Debugging by hand-tracing

Pick the smallest input that fails. Write the variables on paper and step. This is the habit from the earlier modules; here it pays directly, because the failing case from the stress test is only 3 or 4 numbers long.

### The causes by verdict, deeper

**WA** (wrong answer):
- Integer vs float division.
- A global variable kept from the previous test case (section 6).
- Reading fewer or more numbers than the format says.
- Assuming the input is sorted, distinct, or non-empty without being told.
- Modulo forgotten or applied too late (large numbers fine in Python, but the output must be reduced).
- Off-by-one in ranges (half-open versus closed).
- A greedy that works on the sample but is not correct. Stress test.

**TLE** (time limit exceeded):
- The complexity is higher than the table allows (section 2).
- A hidden quadratic: `list.pop(0)`, `x in list`, `s += c`, `list.insert(0, x)`, slicing in a loop (`a[i:]` copies), `sum(a[i:j])` inside a loop.
- Slow input (`input()` ten million times).
- Using CPython when PyPy would do (or vice versa).
- Recursion through a decorated function (`lru_cache`) on a big state space.

Hidden quadratics deserve one demonstration. This looks like a linear loop and is not:

```python
import time

def bench(fn, repeat=3):
    best = float("inf")
    for _ in range(repeat):
        s = time.perf_counter(); fn(); best = min(best, time.perf_counter() - s)
    return best

N = 20000
a = list(range(N))

def slicing_sum():
    t = 0
    for i in range(N):
        t += sum(a[i:i + 50])          # copies and sums 50 items: fine, constant
    return t

def suffix_sum():
    t = 0
    for i in range(N):
        t += sum(a[i:]) % 7            # copies and sums n - i items: quadratic
    return t

print("window of 50   : %.3f s" % bench(slicing_sum))
print("suffix each time: %.3f s (machine-specific)" % bench(suffix_sum, 1))
```
```text
window of 50   : 0.010 s
suffix each time: 1.412 s (machine-specific)
```

The first is `O(N * 50)`; the second is `O(N^2 / 2)`, about 200 million element visits. The second one took far longer. In a real contest this single line gives TLE on the largest test and passes all small tests, which is how quadratics hide.

**RE** (runtime error):
- `IndexError`: a loop one step too far, or a list too small (`adj = [[]] * n` with `n` instead of `n + 1` for 1-indexed nodes).
- `ValueError`: parsing a line with the wrong number of parts; parsing a line with a trailing `\r`.
- `RecursionError` or a crash: deep recursion (section 8).
- `ZeroDivisionError`: modulus or divisor zero.
- `KeyError`: missing dictionary key; use `.get(key, default)` or `defaultdict`.

A classic RE: `[[]] * n` creates **one** inner list repeated `n` times (all aliases). Every `adj[u].append(v)` appends to the same list. This is also a WA/TLE source.

```python
n = 3
bad = [[]] * n
bad[0].append(1)
print(bad)

good = [[] for _ in range(n)]
good[0].append(1)
print(good)
```
```text
[[1], [1], [1]]
[[1], [], []]
```

**MLE** (memory limit exceeded):
- A table of `n * m` that could be two rows.
- Storing all prefixes or all strings; `sorted` makes a copy while `.sort()` does not.
- `list(range(10**8))`; use `range` directly (it is lazy).
- Building a large `set` of tuples when integers (encoded) would do.

```python
import sys
r = range(10**9)
print(sys.getsizeof(r), "bytes for range(10**9)")
print(sum(1 for _ in range(10)), "iterating lazily needs no list")
```
```text
48 bytes for range(10**9)
10 iterating lazily needs no list
```

## 15. Contest strategy

### Before the contest

- **Register** and read the rules. Know the scoring and the time. Codeforces contests typically allow rated participation after you register; practice rounds and virtual contests are unrated.
- **Set up your template** and a test folder. Make sure your Python and PyPy versions are chosen and that submission settings are right.
- **Rest.** A clear head beats an extra hour of last-minute reading.
- **Have water and snacks.** Two hours is a long time.

### The first minutes: read the whole set

Spend the first 5 to 10 minutes **reading** problems A, B, C (and a quick look at D). The goal is to find the easiest. Problem order is a hint, not a guarantee: sometimes B is easier than A for you, and often there are more solves on a problem than its position suggests. The **scoreboard** shows how many people solved each problem. A problem solved by thousands is easy.

### Time per problem

A reasonable allocation for a two-hour Div. 2 round (a guide, not a rule):

| Problem | Target time | If you are stuck |
|---|---|---|
| A | under 10 minutes | Check you read the statement right; test the samples |
| B | under 20 minutes | Brute force on small cases; find the pattern |
| C | 30 to 40 minutes | Move on after about 30 minutes without an idea |
| D and higher | the rest | Think about partial ideas; stress test later |

If you have no idea after **15 minutes** of honest thought, read the next problem. Return later with a fresher mind.

### The cost of a wrong submission

On Codeforces each rejected submission on a problem adds a penalty (the exact amount depends on the contest format; the rules are printed on each contest page). The lesson is the same everywhere: **do not submit blindly.**

Before each submit:

1. Run all the samples.
2. Run two or three small cases of your own, including `n = 1`.
3. Build one **maximum** input and check the time.
4. Re-read the output format.

### Reading a statement properly

Do it in this order:

1. The **last paragraph** (input/output constraints) first, to know the complexity target.
2. The story, but only until you see the task.
3. The samples, and run them in your head.
4. The **note** section, which explains a sample. It is often the clearest statement of the task.

Underline every number you will need: the limits, the modulus, the indexing base.

### Skipping and switching

- A problem with a **long** statement and an unfamiliar topic is rarely worth the time in the first half of the contest.
- A problem solved by many people is cheaper than the one solved by few. Use the scoreboard.
- Do not get stuck on one problem with an "almost right" answer for more than 15 minutes of debugging. Try the stress test; if it fails to find anything, move on and return.

### Hacking and uphacking (Codeforces)

In Codeforces rounds with hacks, after you submit a problem and it passes the samples you can **lock** it, which allows you to look at other participants' solutions and try to *hack* them: submit a test that makes their code give a wrong answer or time out. A successful hack gains points; a failed one loses some. For a beginner: do not hack in your first contests. Focus on solving. Later, reading the solutions of others is excellent practice. Hacking also reminds you that your own solution is judged by **systematic tests** after the contest ("system tests"); something that passed pretests can fail later. This is why section 13 matters.

### Pretests and system tests

Codeforces first judges your submission on a **small set of pretests**. Passing means "pretests passed", not accepted. After the contest, system tests run all tests (including hacks). Solutions that were "accepted on pretests" can fail on system tests for TLE or an edge case. Always self-test beyond the samples.

### Keep notes during the contest

Write on paper: which problems you read, the idea for each, time of each submission. After the contest this is data for your upsolve.

### Psychology

- Do not look at the scoreboard too much. Others' speed is not your speed.
- If a problem is solved much sooner than you expect, you may be overlooking a trap. Reread.
- A rating drop is part of learning. People get stronger by playing a lot of rounds.

### Choosing your first live contest

Pick a **Div. 3** or **Div. 4**, or an Educational round. On AtCoder an **ABC** (Beginner Contest) is the friendliest. Before it, do a **virtual contest** (a past contest replayed with a timer): it has the same pressure and no rating risk. Do two or three virtual contests, then your first live one.

## 16. Upsolving

### What upsolving is

**Upsolving** means solving, after the contest, the problems you did not solve during it. It is where most of the learning happens, more than in the contest itself. In the contest you are rushed. Afterwards you can think, read the editorial, and fix the gap.

### A routine for each contest

Within 24 hours:

1. **Write what happened.** For each problem: solved / not solved / why. Note the time you submitted, number of wrong tries, and the verdict of each.
2. **Retry the one you nearly solved** for 30 to 60 minutes **without** the editorial.
3. **Read the editorial** for the problems you could not do. Read slowly. Ask: what was the key observation? What would have led me to it?
4. **Re-implement from scratch** without looking at the editorial's code. If you only read, you learn little. Submit it as a practice submission and get AC.
5. **Look at the fastest accepted solutions** (Codeforces lets you open other participants' submissions). Compare how they read input, how short they are, what tricks they use.
6. **Extract the lesson** in one sentence and store it with the problem: "sort then two pointers when sum of pairs", "binary search on the answer when monotone".
7. **Add to a problem log**: id, topic, rating, status, date, lesson, and whether you needed the editorial.

### The problem log

Keep a plain text or CSV file. Here is a tiny Python reader for it, which lists what to revisit.

```python
import csv, io

log_text = """id,topic,rating,status,lesson
1900A,greedy,800,solved,count blocks of dots
1900B,math,1000,solved,parity of sums
1900C,dfs,1200,editorial,iterative dfs on tree
1900D,binary search,1500,unsolved,monotone predicate
"""

rows = list(csv.DictReader(io.StringIO(log_text)))
to_review = [r for r in rows if r["status"] != "solved"]
for r in to_review:
    print(r["id"], r["topic"], r["rating"], r["status"])
print("topics to revise:", sorted({r["topic"] for r in to_review}))
```
```text
1900C dfs 1200 editorial
1900D binary search 1500 unsolved
topics to revise: ['binary search', 'dfs']
```

(The ids above are made-up examples to show the format. Use the real ids from your contest.)

### Weak-spot analysis

After 5 to 10 contests, count the topics in your "editorial" and "unsolved" rows. The topic that appears most is your next study target: go back to the matching dsa module, redo its problems, then solve 10 contest problems of that topic with rating a little below your limit.

### Upsolve a bit above your level

A good practice problem is one you can almost solve: rated 100 to 300 points **above** your current rating. Below that you learn little; far above you learn only from the editorial.

## 17. Rating progression: a plan by stage

Codeforces ratings (and similar ones) measure your standing. Colours: below 1200 is "newbie" (gray), then "pupil" (green) from 1200, "specialist" (cyan) from 1400, "expert" (blue) from 1600, then candidate master, master, and up. Other platforms have different scales; the stages below use approximate Codeforces numbers.

The numbers and names are a guide to *what to practise*, not a promise of speed. Progress depends on hours of deliberate practice and varies a lot.

### Stage 0: no rating yet to 800

Goal: solve problems A and sometimes B reliably.

- Skills: basic loops, strings, arrays, sorting, simple math, brute force.
- Practice: 5 to 10 problems of rating 800 per week; all of dsa.01 to dsa.03.
- Contest: Div. 4 and Div. 3, virtual first.
- Habit: always run the samples, always use fast input.

### Stage 1: 800 to 1200

Goal: solve A and B quickly, and C sometimes.

- Skills: two pointers, prefix sums, binary search (dsa.06), greedy basics, number theory basics (gcd, primes), simple recursion.
- Practice: problems rated 800 to 1200, grouped by tag.
- Habit: start stress testing.

### Stage 2: 1200 to 1600

Goal: solve A, B, C reliably; D in good rounds.

- Skills: DP basics (dsa.14), graphs with BFS and DFS (dsa.12), DSU, sorting-based tricks, modular arithmetic (section 11), bit manipulation, constructive problems.
- Practice: problems rated 1200 to 1600. Upsolve every contest.
- Habit: iterative DFS and PyPy-ready code.

### Stage 3: 1600 to 1900

Goal: solve C and D reliably; E sometimes.

- Skills: Dijkstra, segment tree and Fenwick tree (dsa.16), trees (LCA, rerooting), advanced DP (bitmask, digit DP), number theory (sieve, combinatorics modulo prime), strings (hashing, Z, KMP; dsa.15).
- Python note: at this level, some problems are too slow in Python even with PyPy. Learn when to choose a different problem rather than fight the constraint.

### Stage 4: above 1900

At this level, the heavy techniques (flows, heavy-light decomposition, FFT, suffix structures) are a stretch in Python because of constant factors. Many strong competitors switch to C++ at this point. Both are valid choices. A Python-only path is still possible but narrower.

### Weekly plan (example)

| Day | Activity |
|---|---|
| Mon, Tue | 3 new problems in one topic, rating just above comfort |
| Wed | Revisit failed problems from last week |
| Thu | Virtual contest (shorter form, 90 minutes) or a topic lesson |
| Fri | Upsolve |
| Sat | Live contest (when there is one) |
| Sun | Review the log; rest |

Adjust to your timetable. Frequency matters more than long single sessions.

## 18. Practice resources

All of these are free. They need internet; to work offline, download the problem statements you want, or use the problems in this module's folder when they arrive.

| Resource | What it is good for |
|---|---|
| **Codeforces** (codeforces.com) | Live contests, a huge archive filterable by rating and tag, editorials, virtual contests, the "Problemset" page |
| **AtCoder** (atcoder.jp) | Clean problems; ABC archive; the "AtCoder Problems" site tracks progress by difficulty |
| **CSES Problem Set** (cses.fi/problemset) | 300 classic problems in a sensible order: sorting, DP, graphs, trees, range queries |
| **CodeChef** | Regular contests, practice by difficulty, many contests in the Indian time zone |
| **LeetCode** | Interview-style practice, weekly contests; function format |
| **USACO Guide** (usaco.guide) | Free topic-by-topic lessons with problem lists |
| **cp-algorithms.com** | Algorithm articles with code and proofs |
| **Codeforces EDU** | Short courses with practice (binary search, segment tree, etc.) |
| **Competitive Programmer's Handbook** (Antti Laaksonen) | A free book covering the basics to advanced topics |
| **kenkoooo's AtCoder Problems** | Filters problems by difficulty and tracks which you solved |

Use the site features: filter Codeforces by tag and rating, sort by number of solvers, hide tags until after you solve to avoid being hinted. The first read of an editorial should be only the hint, not the full solution.

### Working offline

You asked for a self-contained learning system. Offline, you can still:

- Solve the problems and the stress-test exercises of this module (they arrive as a set of 20 later).
- Re-implement the templates of this chapter and time them with the harness.
- Download a few statements (copy as text) before travelling; run your solution with your own sample files.
- Ask: "could I write this from memory?" about each template.

## 19. Common traps, collected

1. **Using `input()` for large inputs.** Use `sys.stdin.readline` or `sys.stdin.buffer.read().split()`.
2. **Forgetting `strip()`** on lines read by `readline`: a trailing `\n` stays in strings and grids.
3. **Many `print` calls.** Collect and `"\n".join(...)`.
4. **Joining non-strings.** `"\n".join([1, 2])` raises `TypeError`; use `map(str, ...)`.
5. **State not reset between test cases.** Create sets, lists and counters inside the per-test function.
6. **Allocating a maximum-size array per test.** Size arrays by `n` or allocate once.
7. **Recursion on a long chain.** Default limit 1000 fails. Convert to iterative DFS or use the thread recipe.
8. **Raising the recursion limit alone.** Without a larger stack it can crash the interpreter.
9. **Interactive problem without `flush=True`.** The judge never sees your question.
10. **Debug output on stdout.** It corrupts the answer; use `sys.stderr`.
11. **`list.pop(0)` and `x in list`** in a loop. Use `deque` and `set`.
12. **`s += c` in a loop.** Append to a list and `join`.
13. **`[[]] * n`** creates aliased inner lists. Use a comprehension.
14. **Integer division by `/`.** Use `//`; floats lose precision above `2^53`.
15. **`int(n ** 0.5)`** for large `n`. Use `math.isqrt`.
16. **Modulus mistakes.** Negative values are fine in Python's `%`, but forgetting the final `% M` before printing is a WA. Division needs a modular inverse, not `/`.
17. **No guard in `nCr`** for `r > n`.
18. **Confusing 0-indexed and 1-indexed** nodes; size `n + 1` for 1-indexed graphs.
19. **Reading the wrong number of tokens** with the iterator style: print debug counts to stderr while testing.
20. **Trusting a CPython timing for PyPy** (and the reverse). Measure on the interpreter you submit with.
21. **Trusting the samples.** They are minimal. Add `n = 1`, all equal, maximum value, and a worst-case size test.
22. **Submitting without a plan for the largest input.** Estimate operations first (section 2).
23. **Not looking at the editorial after the contest.** The contest is the exam; upsolving is the lesson.
24. **Comparing floats with `==`.** Use a tolerance.
25. **Stopping practice after a bad round.** Rating is noisy. The log of solved problems is the signal.

## 20. Summary

- **A contest** is a timed set of problems judged by hidden tests with verdicts WA, TLE, MLE, RE. Platforms differ in scoring, but the craft is shared.
- **Read the constraints first.** About `10^8` simple operations per second in a fast language; plan for less in Python. `n <= 10^5` means `O(n log n)`, `n <= 5000` allows `O(n^2)`, `n <= 20` allows `O(2^n)`.
- **Measure.** `time.perf_counter` with the best-of-several harness. Build worst-case inputs. Record speed numbers for your own machine, and for PyPy if you install it.
- **Fast input:** `sys.stdin.readline` for line structure; `sys.stdin.read().split()` with an iterator, or `sys.stdin.buffer.read().split()`, for numbers. Mind `strip()` and `bytes`.
- **Fast output:** collect strings, one `"\n".join`, one `print` or `write`. Match the format exactly.
- **Multi-test:** one `solve` per test, reset state, never allocate the maximum per test.
- **Interactive:** `flush=True`, read line by line, debug to stderr.
- **Recursion:** default limit 1000. Prefer iterative DFS (order, then reversed order for bottom-up; enter/exit events for intervals). The thread plus `setrecursionlimit` recipe is the fallback.
- **PyPy vs CPython:** PyPy is usually much faster on plain loops, may use more memory, handles deep recursion differently, and lacks C extension modules. Write code that is correct on both, and try the other when you get TLE.
- **Micro-optimisations:** functions with local variables, built-ins over hand loops, `deque` not list queues, sets for membership, integer encoding for heap pairs, `math.isqrt`, `//`. Measure each one; some tips depend on the Python version.
- **Math templates:** `pow(a, e, M)`, `pow(b, -1, M)` for inverses, factorial tables for `nCr`, bytearray sieve, smallest-prime-factor sieve.
- **Stress test** every non-trivial solution: fast, brute, generator, fixed seed, shrink the failing case.
- **Strategy:** read all early problems, solve the easiest first, test before submitting, skip after about 15 minutes without an idea, do not hack at first, remember pretests are not system tests.
- **Upsolve** within a day: retry, read the editorial, reimplement, log the lesson. Review the log for weak topics and train them.
- **Rating** grows with steady practice at the edge of your ability, virtual contests, and live contests. Python carries you far; know its limits.

### Learning outcomes checklist

You should now be able to:

- [ ] Estimate, from the constraints, the complexity a problem needs.
- [ ] Write a fast-input, fast-output template and use it for multi-test and interactive problems.
- [ ] Convert a recursive DFS to an iterative one for subtree sizes, depths, and entry/exit times.
- [ ] Decide between CPython and PyPy, and explain what PyPy does badly.
- [ ] Use modular arithmetic templates and a sieve.
- [ ] Stress test a solution with a brute force and a random generator.
- [ ] Diagnose WA, TLE, MLE and RE from the symptoms.
- [ ] Join a live contest, manage your time, and upsolve it with a log.

### Further reading

- Antti Laaksonen, *Competitive Programmer's Handbook* (free PDF).
- The CSES Problem Set and the cp-algorithms.com articles named in section 18.
- The Python documentation for `sys`, `heapq`, `bisect`, `collections`, `itertools`, `math`, `threading`.

