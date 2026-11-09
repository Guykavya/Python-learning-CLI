# dsa.14 Dynamic programming

## 1. Recursion with a notebook

In dsa.07 you met the Fibonacci recursion and saw that its call tree repeats itself again and again. Here is the problem in its rawest form. Count how many calls `fib(25)` makes.

```python
calls = 0

def fib(n):
    global calls
    calls += 1
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

print(fib(25))
print("calls:", calls)
```
```text
75025
calls: 242785
```

The answer, 75025, needs 242785 calls. There are only 26 different questions (`fib(0)` to `fib(25)`). The program is asking the same questions again and again and forgetting the answers each time. `fib(23)` alone is computed by `fib(25)` once, and by `fib(24)` once more, and so on, many separate times.

Now give the function a **notebook**: a dictionary where it writes each answer the first time it computes one, and looks there before doing any work.

```python
calls = 0
notebook = {}

def fib(n):
    global calls
    calls += 1
    if n in notebook:
        return notebook[n]
    if n < 2:
        result = n
    else:
        result = fib(n - 1) + fib(n - 2)
    notebook[n] = result
    return result

print(fib(25))
print("calls:", calls)
```
```text
75025
calls: 49
```

Same answer, 49 calls instead of 242785. That small change is **dynamic programming** (DP). The name is old and unhelpful; here is what it really means.

> **Dynamic programming = solve each different sub-problem once, remember the answer, and build bigger answers from smaller ones.**

DP is not a data structure and not one algorithm. It is a **way of designing algorithms** for problems that have two properties.

1. **Overlapping sub-problems.** The same smaller question is asked many times by different paths. (If every sub-problem is new, there is nothing to remember. That is the situation in backtracking, dsa.07.)
2. **Optimal substructure.** The answer to a big question can be built from the answers to smaller questions. (The best way to reach step 10 is made from the best ways to reach earlier steps.)

When both hold, a problem that looks exponential often collapses to a polynomial one. Subset-style brute force `O(2^n)` becomes `O(n * W)`. Trying all ways to cut a string becomes `O(n^2)`.

### What you can do after this module

1. **Write the three parts of a DP before any code**: the state, the transition and the base case.
2. **Write the same DP top-down (memoisation) and bottom-up (tabulation)**, and convert one into the other.
3. **Shrink the memory** of a DP with rolling variables and rolling arrays, and know when that is not possible.
4. **Solve 1D problems**: climbing stairs, house robber, maximum subarray, decode ways.
5. **Solve counting and optimising coin problems**, and see why the loop order changes the meaning.
6. **Solve grid problems**: minimum path sum, unique paths with obstacles, maximal square.
7. **Solve knapsack variants**: 0/1, unbounded, subset sum, partition, target sum.
8. **Solve sequence problems**: longest increasing subsequence (`O(n^2)` and `O(n log n)`), longest common subsequence, edit distance.
9. **Solve palindrome problems** and **interval DP**: matrix chain, burst balloons.
10. **Do DP on trees, over subsets (bitmasks) and over digits.**
11. **Rebuild the actual answer**, not only its value, with parent pointers or by walking the table backwards.
12. **Recognise DP**, choose between DP, greedy and backtracking, and debug a wrong table.

### What this module reuses

- **Recursion, base cases and the call tree** are in dsa.07, sections 2 to 4. `functools.cache` was introduced at the end of section 4 there, and the coin-ways comparison is in section 17.
- **Greedy versus DP** was started in dsa.13, sections 8 and 9 (0/1 knapsack and coin change break greedy). This chapter gives the fix.
- **Binary search with `bisect`** is in dsa.06, section 7. The `O(n log n)` increasing subsequence uses it.
- **Tree recursion that returns a value for the parent** is in dsa.10, sections 3 and 7. Tree DP is the same pattern with a pair of values.
- **Topological order** is in dsa.12, section 7. Every DP is secretly a walk over a DAG (a graph with no cycles) of states: an edge goes from a smaller sub-problem to a bigger one that needs it, and filling a table in a valid order is a topological sort.

## 2. The recipe: state, transition, base case

Every DP in this chapter, from Fibonacci to travelling salesman, is designed with the same three questions. Answer them **on paper, in words**, before you write any code. Most wrong DP code comes from skipping this.

1. **State.** What is the smallest set of numbers that completely describes one sub-problem? Name the function: `f(i)`, `f(i, j)`, `f(i, remaining)`, `f(mask, last)`. Then say in one English sentence what `f(...)` *means*.
2. **Transition.** How is `f(state)` computed from the answers of smaller states? This is a formula, or a `min`/`max`/`sum` over a few choices.
3. **Base case.** Which states are so small that the answer is known directly? Without these the recursion never stops, and a table has nothing to start from.

And two extra questions that people forget:

4. **Where is the final answer?** It is often `f(n)`, but may be `max(f(i) for all i)` (longest increasing subsequence), or a corner of a table.
5. **In what order do I fill the states?** Every state must be computed *after* all the states it depends on.

### A worked example: climbing stairs

You climb a staircase of `n` steps. Each move is 1 or 2 steps. In how many different ways can you reach the top?

- **State.** `f(i)` = the number of ways to stand on step `i`. (The sentence matters. "ways to *reach* step `i`", starting from the ground.)
- **Transition.** The last move into step `i` came from step `i - 1` (a 1-step) or from step `i - 2` (a 2-step). Those two groups of ways are different and cover everything, so `f(i) = f(i-1) + f(i-2)`.
- **Base case.** `f(0) = 1`: there is exactly one way to be on the ground (do nothing). `f(1) = 1`.
- **Answer.** `f(n)`.
- **Order.** `i` increasing, because `f(i)` needs smaller indices.

Do you see that it is the Fibonacci recurrence with different starting numbers? Many problems in this chapter are "the same recurrence in disguise". Code, written straight from the recipe:

```python
def climb(n):
    f = [0] * (n + 1)
    f[0] = 1                      # base case
    if n >= 1:
        f[1] = 1                  # base case
    for i in range(2, n + 1):     # order: small to large
        f[i] = f[i - 1] + f[i - 2]   # transition
    return f[n]                   # answer

print([climb(n) for n in range(0, 9)])
```
```text
[1, 1, 2, 3, 5, 8, 13, 21, 34]
```

Hand check for `n = 4`. `f[0]=1, f[1]=1`, `f[2]=1+1=2` (ways: 1+1, 2), `f[3]=2+1=3` (1+1+1, 1+2, 2+1), `f[4]=3+2=5`. The list above agrees: the fifth entry (n = 4) is 5.

### The state is the whole art

Choosing the state is 80% of a DP problem. A good state has two properties.

- **It is sufficient**: knowing the state is enough to decide the future. Nothing about *how* you got there can matter. (This is called the Markov property. For stairs: it does not matter which steps you used before; only your current step matters.)
- **It is small**: the number of different states times the work per state gives the running time. If the state is "the whole path so far", the number of states is exponential and DP gives nothing.

A very useful formula:

> **Time = (number of states) x (work per transition). Space = (number of states stored).**

For `f(i, j)` with `i` up to `n` and `j` up to `m`, and a transition that looks at 3 neighbours: `n * m * 3`, which is `O(n * m)`.

### Try it 1

A frog is on stone 0 and wants to reach stone `n`. In one jump it can go forward 1, 2 or 3 stones. Write the state, transition, base case and answer in words. Then write the code and print the number of ways for `n = 0..7`.

<details><summary>Answer</summary>

State: `f(i)` = number of ways to land on stone `i`. Transition: `f(i) = f(i-1) + f(i-2) + f(i-3)`, using only terms with a non-negative index. Base: `f(0) = 1`. Answer `f(n)`. Order: increasing `i`.

```python
def frog(n):
    f = [0] * (n + 1)
    f[0] = 1
    for i in range(1, n + 1):
        for step in (1, 2, 3):
            if i - step >= 0:
                f[i] += f[i - step]
    return f[n]

print([frog(n) for n in range(8)])
```
```text
[1, 1, 2, 4, 7, 13, 24, 44]
```

The guard `i - step >= 0` is the base-case logic in disguise: stones before stone 0 do not exist, so they contribute nothing. Time `O(n)`, space `O(n)`.
</details>

## 3. Top-down: memoisation

The notebook in section 1 is **memoisation**: write the plain recursion first, then add a cache. This is called **top-down** because you start from the big question and recurse down to small ones.

The beauty is that you only need the recursion, which you learned in dsa.07, plus one extra step. Python offers two ways to do it.

### `functools.cache`

```python
import functools

@functools.cache
def ways(n):
    if n <= 1:
        return 1
    return ways(n - 1) + ways(n - 2)

print(ways(10), ways(100))
print(ways.cache_info())
```
```text
89 573147844013817084101
CacheInfo(hits=99, misses=101, maxsize=None, currsize=101)
```

`cache_info()` shows `hits` (answers found in the notebook), `misses` (answers computed) and `currsize` (how many are stored). The 101 misses are the 101 distinct states `0..100`. `functools.lru_cache(maxsize=None)` is the older spelling of the same thing. Plain `functools.cache` is enough for us.

The arguments of a cached function become the **dictionary key**, so they must be **hashable**: numbers, strings, tuples, yes; lists and dicts, no.

```python
import functools

@functools.cache
def total(values):
    return sum(values)

try:
    total([1, 2, 3])
except TypeError as e:
    print("TypeError:", e)

print(total((1, 2, 3)))
```
```text
TypeError: unhashable type: 'list'
6
```

The cure is to pass tuples, or better: **pass indices**. Instead of `f(remaining_list)` write `f(i)` where `i` says "the part of the list from `i` onward". A DP state should be a few small numbers.

### A dictionary you manage yourself

Sometimes you want control: to clear the cache between tests, to count entries, or to store parent pointers. Then keep your own `memo` dictionary. The usual pattern puts the dictionary in an outer function so each call starts clean:

```python
def count_paths(rows, cols):
    memo = {}

    def go(r, c):                       # ways to get from (0,0) to (r,c) moving right/down
        if r == 0 or c == 0:
            return 1
        if (r, c) not in memo:
            memo[(r, c)] = go(r - 1, c) + go(r, c - 1)
        return memo[(r, c)]

    return go(rows - 1, cols - 1)

print(count_paths(3, 3), count_paths(3, 7), count_paths(18, 18))
```
```text
6 28 2333606220
```

Note `if (r, c) not in memo` then `return memo[(r, c)]`. Do **not** write `if memo.get(key):` to test for presence. A stored answer of `0` is falsy, and you would recompute it every time (correct but slow, a silent trap). Test with `in`, or compare to `None` only if `None` can never be a real answer.

### Memoisation, step by step on a tiny case

Take `count_paths(3, 3)`: a 3 by 3 grid, so we want `go(2, 2)`. Write `G(r,c)` for `go(r,c)`. The calls happen in this order (indented by depth). A repeated call that finds its answer in the notebook is marked `(cached)`.

```text
G(2,2)
  G(1,2)
    G(0,2) = 1        base
    G(1,1)
      G(0,1) = 1      base
      G(1,0) = 1      base
      G(1,1) = 2      stored
    G(1,2) = 3        stored
  G(2,1)
    G(1,1) = 2        (cached)
    G(2,0) = 1        base
    G(2,1) = 3        stored
  G(2,2) = 6          stored
```

`G(1,1)` is asked twice but computed once. In a bigger grid, the number of repeats grows enormously; with the notebook the work stays proportional to the number of cells. The answer 6 is the first number printed above.

### The traps of memoisation

**Trap 1: a mutable default argument as the notebook.** It looks neat, and it works, but the dictionary is created once and survives between calls, even calls with *different inputs*.

```python
def count_ways(coins, amount, memo={}):          # BAD: shared by all calls
    if amount == 0:
        return 1
    if amount < 0 or not coins:
        return 0
    key = (len(coins), amount)
    if key not in memo:
        memo[key] = (count_ways(coins, amount - coins[-1], memo)
                     + count_ways(coins[:-1], amount, memo))
    return memo[key]

print(count_ways([1, 2], 4))
print(count_ways([1, 5], 4))        # different coins, same lengths and amount
```
```text
3
3
```

The second answer should be 1 (only `1+1+1+1`), but the key `(len(coins), amount)` collides with the first call and the stale answer 3 comes back. There are two bugs here: the **shared default dictionary**, and a **key that does not identify the state** (the length of the coin list is not the same as the coin list). The first is a pure Python trap you know from core modules; the second is a DP trap. A memo key must contain **everything the answer depends on**, and nothing that it does not.

**Trap 2: the recursion limit.** Python allows about 1000 nested calls. A DP over `n = 5000` stairs recurses 5000 deep and crashes, even though the algorithm is fine.

```python
import functools, sys

@functools.cache
def ways(n):
    if n <= 1:
        return 1
    return ways(n - 1) + ways(n - 2)

print("limit:", sys.getrecursionlimit())
try:
    ways(5000)
except RecursionError:
    print("RecursionError for n = 5000")
```
```text
limit: 1000
RecursionError for n = 5000
```

Cures, in order of preference: (1) convert to a table (next section), which has no recursion at all; (2) warm the cache from the bottom: call `ways(500)`, `ways(1000)`, ... in increasing order so each call recurses only 500 deep; (3) `sys.setrecursionlimit(10000)`, which works for moderate depth but a very deep recursion can crash the interpreter itself. Competitive programmers on long inputs nearly always use the table.

**Trap 3: a cache that outlives the data.** A global `@cache` function that reads a global list (not as an argument) gives stale answers when the list changes. The cache only knows its arguments. If the answer depends on `coins` or `grid`, either pass them as hashable arguments, or define the cached function *inside* the outer function (a closure), so a new cache is made for each call, as `count_paths` did above.

**Trap 4: wrong or missing state.** If the function takes `(i, j, k)` but the answer really depends on a fourth thing, you get wrong answers that look random. And if you add something that the answer does *not* depend on (like the full path so far), you destroy the sharing and the speed. Good habit: for every parameter ask "does the answer change if only this changes?"

### Try it 2

What does this print? Count the calls to the inner function body, not the cache hits.

```python
import functools
body_runs = 0

@functools.cache
def f(i, j):
    global body_runs
    body_runs += 1
    if i == 0 or j == 0:
        return 1
    return f(i - 1, j) + f(i, j - 1)

print(f(3, 3), body_runs)
```

<details><summary>Answer</summary>

```text
20 15
```

The states are all pairs `(i, j)` with `0 <= i, j <= 3`: 16 pairs, but `(0, 0)` is never asked for (the cells `(0, j)` and `(i, 0)` are base cases, so nobody recurses into it), so the body runs 15 times. The value 20 is the number of paths in a 4 by 4 lattice (`C(6, 3)`). Remember: **number of body runs = number of distinct states reached.**
</details>

## 4. Bottom-up: tabulation

Top-down starts from the question and recurses. **Bottom-up** starts from the smallest sub-problems and fills a **table** towards the answer. No recursion, so no recursion limit and no call overhead. The price is that **you** must choose the order.

### The conversion recipe

You have a memoised function. To turn it into a table:

1. **The memo becomes an array** (or a 2D array) indexed by the state. Its size is the range of each state variable (+1 for the zero index).
2. **The base cases become the first assignments** into the array.
3. **The recursive calls become array reads.** `f(i-1)` becomes `table[i-1]`.
4. **Choose loops so every read has been written.** If `f(i)` calls `f(i-1)` and `f(i-2)`, loop `i` upward. If `f(i)` calls `f(i+1)`, loop `i` downward. For `f(i, j)` calling `f(i-1, j)` and `f(i, j-1)`, two nested increasing loops work.
5. **The answer** is the entry the original call asked for.

An example: the grid-path counter from section 3.

```python
import functools

@functools.cache
def top_down(r, c):
    if r == 0 or c == 0:
        return 1
    return top_down(r - 1, c) + top_down(r, c - 1)

def bottom_up(rows, cols):
    table = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if r == 0 or c == 0:
                table[r][c] = 1                                   # base case
            else:
                table[r][c] = table[r - 1][c] + table[r][c - 1]  # transition
    return table

t = bottom_up(4, 5)
for row in t:
    print(row)
print(top_down(3, 4), t[3][4])
```
```text
[1, 1, 1, 1, 1]
[1, 2, 3, 4, 5]
[1, 3, 6, 10, 15]
[1, 4, 10, 20, 35]
35 35
```

Look at the table. Every cell is the sum of the cell above and the cell to the left, the Pascal's-triangle pattern. The recursion `top_down(3, 4)` and the table corner `t[3][4]` agree.

### Top-down or bottom-up?

| | Top-down (memoisation) | Bottom-up (tabulation) |
|---|---|---|
| Code | Recursion you already wrote, plus `@cache` | Loops and an array |
| Computes | Only the states that are actually needed | Every state in the table |
| Order | Automatic | You must choose it |
| Recursion limit | Yes, depth up to the longest chain of states | No |
| Speed | Slower constant (calls, hashing) | Faster constant |
| Memory trick (rolling array) | Not possible | Often possible |
| Best when | The state space is sparse or awkward (bitmask, digit, interval) | The state space is a dense, regular grid |

A sensible workflow: **first write the top-down version** (it is the closest to your thinking and is easy to get right), test it on small inputs, and then convert to a table if you need speed, depth or less memory. Keep the memoised version as a slow-but-sure checker to test the table against, in the style of a brute-force oracle.

### Iteration order: the classic bug

If the loops run in the wrong order, the table reads cells that are still zero (never written), and the answer is silently wrong.

```python
def broken(n):
    f = [0] * (n + 1)
    f[0] = f[1] = 1
    for i in range(n, 1, -1):          # BUG: counting downwards
        f[i] = f[i - 1] + f[i - 2]
    return f[n]

def fixed(n):
    f = [0] * (n + 1)
    f[0] = f[1] = 1
    for i in range(2, n + 1):
        f[i] = f[i - 1] + f[i - 2]
    return f[n]

print(broken(6), fixed(6))
```
```text
0 13
```

`broken` reads `f[5]` and `f[4]` before they are filled. Rule: **draw the dependency arrows; fill in an order that follows them.** When the arrows point left/up, loop forwards; when they point right/down, loop backwards. For `f(i, j)` depending on `f(i+1, j)` and `f(i, j+1)`, both loops run downward.

### Table size and the "+1"

Tables for lengths need `n + 1` entries: index 0 means "empty prefix" (nothing used yet). With strings of length `n` and `m`, the table is `(n+1) x (m+1)`. Forgetting the `+1` is the most common index error in DP. A related trap: build 2D tables with a comprehension.

```python
bad = [[0] * 3] * 2             # BUG: both rows are the same list
bad[0][1] = 7
good = [[0] * 3 for _ in range(2)]
good[0][1] = 7
print(bad)
print(good)
```
```text
[[0, 7, 0], [0, 7, 0]]
[[0, 7, 0], [0, 0, 0]]
```

`[row] * k` copies the *reference*, so all rows are one list. You met this in the core track. In DP it makes every row change together and gives wrong totals.

### Try it 3

Convert this memoised function into a table and print `f(10)` from both.

```python
import functools

@functools.cache
def f(i):
    if i == 0:
        return 2
    if i == 1:
        return 3
    return 2 * f(i - 1) - f(i - 2) + 1
```

<details><summary>Answer</summary>

```python
import functools

@functools.cache
def f(i):
    if i == 0:
        return 2
    if i == 1:
        return 3
    return 2 * f(i - 1) - f(i - 2) + 1

def table_f(n):
    t = [0] * (n + 1)
    t[0] = 2
    if n >= 1:
        t[1] = 3
    for i in range(2, n + 1):
        t[i] = 2 * t[i - 1] - t[i - 2] + 1
    return t[n]

print(f(10), table_f(10))
```
```text
57 57
```

Steps: memo to array; the two base cases first (guard `n >= 1` so `n = 0` does not index out of range); recursive calls to reads; loop upward because the dependencies are smaller indices.
</details>

## 5. One-dimensional DP

The simplest tables have one index: `f(i)` for `i = 0..n`, with `i` meaning "the first `i` things" or "position `i`". We go through five classics. For each one, look first at the **sentence that defines the state**; the rest follows.

### Minimum cost climbing stairs

`cost[i]` is the price of stepping **from** stair `i`. You may start on stair 0 or stair 1, you move 1 or 2 stairs at a time, and the top is just beyond the last stair (index `n`). Find the cheapest way to the top.

- State: `f(i)` = the cheapest cost to arrive at stair `i` (not yet paying `cost[i]`).
- Transition: you came from `i - 1` (paying `cost[i-1]`) or from `i - 2` (paying `cost[i-2]`). So `f(i) = min(f(i-1) + cost[i-1], f(i-2) + cost[i-2])`.
- Base: `f(0) = f(1) = 0` (you may start on either, for free).
- Answer: `f(n)`.

```python
def min_cost_climb(cost):
    n = len(cost)
    f = [0] * (n + 1)
    for i in range(2, n + 1):
        f[i] = min(f[i - 1] + cost[i - 1], f[i - 2] + cost[i - 2])
    return f[n], f

best, table = min_cost_climb([10, 15, 20])
print(best, table)
best, table = min_cost_climb([1, 100, 1, 1, 1, 100, 1, 1, 100, 1])
print(best, table)
```
```text
15 [0, 0, 10, 15]
6 [0, 0, 1, 2, 2, 3, 3, 4, 4, 5, 6]
```

Trace the first: `cost = [10, 15, 20]`, `n = 3`. `f[0] = f[1] = 0`. `f[2] = min(0 + 15, 0 + 10) = 10`. `f[3] = min(f[2] + cost[2], f[1] + cost[1]) = min(10 + 20, 0 + 15) = 15`. The cheapest way: start at stair 1, pay 15, jump 2 to the top. Time `O(n)`, space `O(n)`.

### House robber

Houses in a row hold `nums[i]` money. You cannot rob two **adjacent** houses. Maximise the money.

Think about the last house. Either you skip it (the best is whatever you made from the earlier houses), or you rob it (then you could not have robbed the one before it).

- State: `f(i)` = the best total using only the first `i` houses.
- Transition: `f(i) = max(f(i-1), f(i-2) + nums[i-1])`. Skip house `i`, or rob it and add to the best of the first `i - 2`.
- Base: `f(0) = 0`, `f(1) = nums[0]`.
- Answer: `f(n)`.

```python
def rob(nums):
    n = len(nums)
    f = [0] * (n + 1)
    if n >= 1:
        f[1] = nums[0]
    for i in range(2, n + 1):
        f[i] = max(f[i - 1], f[i - 2] + nums[i - 1])
    return f[n], f

print(rob([2, 7, 9, 3, 1]))
print(rob([1, 2, 3, 1]))
print(rob([]))
```
```text
(12, [0, 2, 7, 11, 11, 12])
(4, [0, 1, 2, 4, 4])
(0, [0])
```

Hand trace of `[2, 7, 9, 3, 1]`:

| i | house `nums[i-1]` | skip = `f[i-1]` | rob = `f[i-2] + house` | `f[i]` |
|---|---|---|---|---|
| 0 | | | | 0 |
| 1 | 2 | | | 2 |
| 2 | 7 | 2 | 0 + 7 = 7 | 7 |
| 3 | 9 | 7 | 2 + 9 = 11 | 11 |
| 4 | 3 | 11 | 7 + 3 = 10 | 11 |
| 5 | 1 | 11 | 11 + 1 = 12 | 12 |

The answer 12 comes from houses with 2, 9 and 1. Notice that the greedy idea "always rob the richest house" (7 first) would give 7 + 3 = 10 or worse. Greedy fails here and DP does not. Time `O(n)`.

### Maximum subarray (Kadane's algorithm is a DP)

Find the contiguous block with the largest sum. A trap in thinking: if the state is "best sum in the first `i` items", the transition is not clear (does the best block touch item `i`?). Change the state so that it is.

- State: `f(i)` = the best sum of a block that **ends exactly at index `i`**.
- Transition: the block is either just `nums[i]` alone, or it extends the best block ending at `i - 1`: `f(i) = max(nums[i], f(i-1) + nums[i])`.
- Base: `f(0) = nums[0]`.
- Answer: `max(f(i))` over **all** `i`, because the best block may end anywhere.

```python
def max_subarray(nums):
    f = [0] * len(nums)
    f[0] = nums[0]
    for i in range(1, len(nums)):
        f[i] = max(nums[i], f[i - 1] + nums[i])
    return max(f), f

print(max_subarray([-2, 1, -3, 4, -1, 2, 1, -5, 4]))
print(max_subarray([-3, -1, -2]))
```
```text
(6, [-2, 1, -2, 4, 3, 5, 6, 1, 5])
(-1, [-3, -1, -2])
```

Trace the first: `f` = -2; then max(1, -2+1) = 1; max(-3, 1-3) = -2; max(4, -2+4) = 4; max(-1, 4-1) = 3; max(2, 3+2) = 5; max(1, 5+1) = 6; max(-5, 6-5) = 1; max(4, 1+4) = 5. The maximum of the list is 6 (block `[4, -1, 2, 1]`). With all negatives the answer is the least negative single item, -1; this is why the base is `nums[0]` and not 0.

This lesson is general: **if the natural state "best among the first `i`" has no transition, add the extra condition "and item `i` is used/ends here"**, then take a max over all `i` at the end. You will see it again in the longest increasing subsequence.

### Decode ways

A message of digits is decoded with `1 -> A`, `2 -> B`, ..., `26 -> Z`. Count the ways to decode `s`. For example `"226"` can be `2 2 6`, `22 6` or `2 26`: three ways.

- State: `f(i)` = the number of ways to decode the first `i` characters.
- Transition: the last piece is one digit `s[i-1]` (valid if it is not `'0'`) giving `f(i-1)` ways; or two digits `s[i-2:i]` (valid if between 10 and 26) giving `f(i-2)` ways. Add the valid parts.
- Base: `f(0) = 1` (the empty string has one decoding: do nothing).

```python
def decode_ways(s):
    n = len(s)
    f = [0] * (n + 1)
    f[0] = 1
    for i in range(1, n + 1):
        if s[i - 1] != "0":
            f[i] += f[i - 1]
        if i >= 2 and 10 <= int(s[i - 2:i]) <= 26:
            f[i] += f[i - 2]
    return f[n]

for s in ["226", "12", "06", "10", "2101", "1111"]:
    print(s, decode_ways(s))
```
```text
226 3
12 2
06 0
10 1
2101 1
1111 5
```

Check `"226"` by hand: `f[0]=1`. `i=1`: digit '2' valid, `f[1]=1`. `i=2`: digit '2' valid adds `f[1]=1`; "22" valid adds `f[0]=1`, so `f[2]=2`. `i=3`: digit '6' adds `f[2]=2`; "26" valid adds `f[1]=1`, so `f[3]=3`. The zero cases are the traps: `"06"` has no decoding (a leading zero is invalid, and "06" is not between 10 and 26) and `"10"` has one (only "10" as J).

### Word break

Can the string `s` be split into words from a dictionary? State: `f(i)` = True if the first `i` characters can be split. Transition: `f(i)` is True if there is a cut `j < i` with `f(j)` True and `s[j:i]` a word. Base: `f(0) = True`.

```python
def word_break(s, words):
    words = set(words)
    f = [False] * (len(s) + 1)
    f[0] = True
    for i in range(1, len(s) + 1):
        for j in range(i):
            if f[j] and s[j:i] in words:
                f[i] = True
                break
    return f[len(s)]

print(word_break("leetcode", ["leet", "code"]))
print(word_break("catsandog", ["cats", "dog", "sand", "and", "cat"]))
print(word_break("applepenapple", ["apple", "pen"]))
```
```text
True
False
True
```

Two nested loops give `O(n^2)` states-times-transitions (plus the cost of slicing and hashing a substring, so `O(n^3)` in the worst case for long words; limit `j` to the longest word length to cut this). Notice the new shape: the transition loops over **all earlier cut points**, not just `i - 1` and `i - 2`. DP transitions can look back arbitrarily far.

### Try it 4

What does `rob([5, 1, 1, 5])` return, and what is the table? Hand-fill it first.

<details><summary>Answer</summary>

```python
def rob(nums):
    n = len(nums)
    f = [0] * (n + 1)
    if n >= 1:
        f[1] = nums[0]
    for i in range(2, n + 1):
        f[i] = max(f[i - 1], f[i - 2] + nums[i - 1])
    return f

print(rob([5, 1, 1, 5]))
```
```text
[0, 5, 5, 6, 10]
```

`f[1]=5`; `f[2]=max(5, 0+1)=5`; `f[3]=max(5, 5+1)=6`; `f[4]=max(6, 5+5)=10`. The best is the two 5s at both ends. A greedy "take the first, then take the best allowed" would also find this one, but it fails on `[2, 7, 9, 3, 1]`.
</details>

## 6. Saving memory: rolling variables and rolling arrays

Look at the house robber again. To compute `f[i]` we read only `f[i-1]` and `f[i-2]`. The cells before that are never read again. Why keep them?

### Rolling variables

```python
def rob_small(nums):
    prev2, prev1 = 0, 0          # f(i-2), f(i-1)
    for money in nums:
        prev2, prev1 = prev1, max(prev1, prev2 + money)
    return prev1

print(rob_small([2, 7, 9, 3, 1]), rob_small([5, 1, 1, 5]), rob_small([]))
```
```text
12 10 0
```

Here `prev1` holds `f(i-1)` and `prev2` holds `f(i-2)`. The tuple assignment updates both at once, using the old values on the right side. Memory goes from `O(n)` to `O(1)`; time is unchanged.

**The rule:** if `f(i)` depends only on the last `k` cells, keep `k` variables (or a window of size `k`). The same trick turns climbing stairs, Fibonacci and Kadane into constant-memory loops.

You lose something, though. A table lets you **reconstruct** the answer (section 9) and lets you **inspect** values while debugging. When you only need the final number, roll. When you need the choices, keep the table. A good habit is: write the full table first, make it pass the tests, *then* shrink it.

### Rolling arrays for 2D tables

In a 2D table `f[i][j]`, where each row depends only on the previous row, you need two rows (or even just one). Take the path-count grid.

```python
def paths_full(rows, cols):
    f = [[1] * cols for _ in range(rows)]
    for r in range(1, rows):
        for c in range(1, cols):
            f[r][c] = f[r - 1][c] + f[r][c - 1]
    return f[rows - 1][cols - 1]

def paths_two_rows(rows, cols):
    prev = [1] * cols
    for r in range(1, rows):
        cur = [1] * cols
        for c in range(1, cols):
            cur[c] = prev[c] + cur[c - 1]
        prev = cur
    return prev[cols - 1]

def paths_one_row(rows, cols):
    row = [1] * cols
    for r in range(1, rows):
        for c in range(1, cols):
            row[c] = row[c] + row[c - 1]     # row[c] is still last row's value (above)
    return row[cols - 1]

print(paths_full(5, 6), paths_two_rows(5, 6), paths_one_row(5, 6))
```
```text
126 126 126
```

The one-row version is the tricky one. Before the update, `row[c]` holds the cell **above** (from the previous row). `row[c-1]` has just been updated, so it is the cell to the **left** (in the current row). The in-place update works *because* of the left-to-right order. If you looped `c` downward, `row[c-1]` would still hold the old row and the answer would be wrong.

Memory: `O(rows * cols)` becomes `O(cols)`. Pick the shorter side as the row length when you can.

### The window of a "look-back" DP

If a transition looks back at most `k` rows, keep `k` rows, using a small list or `i % k` indexing. In the LCS and edit distance problems (sections 14 and 15) `k = 1`, so two rows suffice.

### Try it 5

Rewrite `climb(n)` (section 2) with two variables. Print `climb(1)`, `climb(2)`, `climb(30)`.

<details><summary>Answer</summary>

```python
def climb(n):
    a, b = 1, 1                  # f(0), f(1)
    for _ in range(n - 1):
        a, b = b, a + b
    return b

print(climb(1), climb(2), climb(30))
```
```text
1 2 1346269
```

For `n = 1` the loop runs `range(0)`, zero times, and returns `b = 1`. For `n = 0` this version would also return 1, which happens to be correct. Always test the smallest inputs after you shrink a table.
</details>

## 7. Coin change

Coin change comes in two flavours that look alike and need different loops. You saw in dsa.13 that greedy works only for some coin systems. DP works for **all**.

### Fewest coins

Given coin values `coins` (unlimited supply of each) and a target `amount`, find the fewest coins that add up to exactly `amount`, or report -1.

- State: `f(a)` = the fewest coins needed to make amount `a`.
- Transition: the last coin is some `c`. Then the rest is `a - c`, which needs `f(a - c)` coins. Try every coin: `f(a) = 1 + min(f(a - c))` over coins `c <= a`.
- Base: `f(0) = 0`. Unreachable amounts are `infinity`.
- Answer: `f(amount)`, or -1 if still infinite.

```python
INF = float("inf")

def coin_min(coins, amount):
    f = [INF] * (amount + 1)
    f[0] = 0
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and f[a - c] + 1 < f[a]:
                f[a] = f[a - c] + 1
    return (f[amount] if f[amount] != INF else -1), f

best, table = coin_min([1, 2, 5], 11)
print(best)
print(table)
print(coin_min([1, 3, 4], 6)[0], "<- greedy would say 3")
print(coin_min([2], 3)[0])
```
```text
3
[0, 1, 1, 2, 2, 1, 2, 2, 3, 3, 2, 3]
2 <- greedy would say 3
-1
```

Fill the table by hand for coins `[1, 2, 5]`:

| a | 0 | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 11 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| f(a) | 0 | 1 | 1 | 2 | 2 | 1 | 2 | 2 | 3 | 3 | 2 | 3 |

For `a = 7`: options are `f(6)+1 = 3`, `f(5)+1 = 2`, `f(2)+1 = 2`. Best 2 (a 5 and a 2). For `a = 11`: `f(10)+1 = 3`, `f(9)+1 = 4`, `f(6)+1 = 3`. Best 3 (5 + 5 + 1).

Time `O(amount * len(coins))`, space `O(amount)`. Compare with brute force, which would try all sequences of coins and is exponential.

The reason infinity is used (and not -1 or 0) is arithmetic: `INF + 1` is still `INF`, and `INF` never wins a `min`. If you used `-1` for "impossible" you would have to special-case it in every transition. A very large integer such as `10**9` also works, but must be bigger than any real answer.

### Counting the ways (combinations)

Now count the number of **combinations** of coins that make `amount`. `[1, 1, 2]` and `[2, 1, 1]` are the same combination. For coins `[1, 2, 3]` and amount 4 the combinations are `1+1+1+1`, `1+1+2`, `2+2`, `1+3`: four of them.

The state must forbid counting different orders as different. The trick is to **process the coins one at a time in the outer loop**. When coin `c` is being processed, `f[a]` counts combinations using only the coins processed so far.

```python
def coin_ways(coins, amount):
    f = [0] * (amount + 1)
    f[0] = 1                       # one way to make 0: take nothing
    for c in coins:                # outer loop: coins
        for a in range(c, amount + 1):
            f[a] += f[a - c]
        print("after coin", c, ":", f)
    return f[amount]

print(coin_ways([1, 2, 3], 4))
```
```text
after coin 1 : [1, 1, 1, 1, 1]
after coin 2 : [1, 1, 2, 2, 3]
after coin 3 : [1, 1, 2, 3, 4]
4
```

Read the lines. After coin 1, there is exactly one way to make each amount (all ones). After coin 2, `f[a] += f[a-2]`: for `a = 4`, the new `f[4]` is the old value 1 (ones only) plus `f[2] = 2`, the ways to make 2 from `{1, 2}` (`1+1`, `2`), each followed by a final coin 2 (`1+1+2`, `2+2`). Total 3. After coin 3, `f[3]` becomes 3 (`1+1+1`, `1+2`, `3`) and `f[4]` becomes 3 + `f[1]` = 4.

Because coins are processed in a fixed order, a combination is only ever built in one order (all 1s, then 2s, then 3s), so each combination is counted once.

### Counting the ways (sequences, order matters)

Swap the loops: for each amount, try every coin as the **last** coin. Then `1+2` and `2+1` are different sequences.

```python
def coin_sequences(coins, amount):
    f = [0] * (amount + 1)
    f[0] = 1
    for a in range(1, amount + 1):      # outer loop: amounts
        for c in coins:
            if c <= a:
                f[a] += f[a - c]
    return f[amount]

print(coin_sequences([1, 2, 3], 4))
```
```text
7
```

Seven sequences: `1111, 112, 121, 211, 22, 13, 31`. The only difference from `coin_ways` is **which loop is outside**. This is the best example in the whole course of how the loop order *is* the meaning of the DP:

| Outer loop | Inner loop | What `f[amount]` counts |
|---|---|---|
| coins | amounts | combinations (order ignored) |
| amounts | coins | sequences (order matters) |

This is also the "stairs with steps from a set" problem: climbing with steps `{1, 2, 3}` is `coin_sequences` with those steps.

### The relation to dsa.07

In dsa.07 you wrote `ways(coins, i, remaining)` with a cache: the state was (index of the coin, amount left). That is the same DP as `coin_ways`, with the coin loop and the amount loop turned into recursion. The tabulation removed the index `i` by reusing one array across coins, which is a space optimisation (section 6) in action: the 2D table `g[i][a]` ("combinations using the first `i` coins") only needs the previous row.

### Try it 6

Count the combinations making 10 from `[2, 5, 3, 6]` and the sequences making 10 from the same coins. Which one is bigger and why?

<details><summary>Answer</summary>

```python
def coin_ways(coins, amount):
    f = [0] * (amount + 1)
    f[0] = 1
    for c in coins:
        for a in range(c, amount + 1):
            f[a] += f[a - c]
    return f[amount]

def coin_sequences(coins, amount):
    f = [0] * (amount + 1)
    f[0] = 1
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a:
                f[a] += f[a - c]
    return f[amount]

print(coin_ways([2, 5, 3, 6], 10), coin_sequences([2, 5, 3, 6], 10))
```
```text
5 17
```

Sequences are at least as many as combinations, because each combination with different coin values can be arranged in several orders. They are equal only when every combination has just one arrangement.
</details>

## 8. Grid DP

In a grid problem the state is a cell `(r, c)`, and the transition looks at neighbours already visited. Moving only right and down means `f(r, c)` depends on `f(r-1, c)` and `f(r, c-1)`: loop rows downward, columns rightward.

### Minimum path sum

Each cell has a cost. Move right or down from the top-left to the bottom-right and minimise the total cost.

- State: `f(r, c)` = the cheapest cost of a path from `(0,0)` to `(r,c)`, including the cost of cell `(r,c)`.
- Transition: `f(r,c) = grid[r][c] + min(f(r-1,c), f(r,c-1))`, using only neighbours that exist.
- Base: `f(0,0) = grid[0][0]`. The first row and column have only one way in.

```python
def min_path_sum(grid):
    rows, cols = len(grid), len(grid[0])
    f = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if r == 0 and c == 0:
                f[r][c] = grid[r][c]
            elif r == 0:
                f[r][c] = f[r][c - 1] + grid[r][c]
            elif c == 0:
                f[r][c] = f[r - 1][c] + grid[r][c]
            else:
                f[r][c] = grid[r][c] + min(f[r - 1][c], f[r][c - 1])
    return f

g = [[1, 3, 1],
     [1, 5, 1],
     [4, 2, 1]]
for row in min_path_sum(g):
    print(row)
```
```text
[1, 4, 5]
[2, 7, 6]
[6, 8, 7]
```

Trace by hand. Row 0 is a running sum: 1, 4, 5. Column 0 is a running sum: 1, 2, 6. Cell (1,1): `5 + min(4, 2) = 7`. Cell (1,2): `1 + min(f[0][2]=5, f[1][1]=7) = 6`. Cell (2,1): `2 + min(f[1][1]=7, f[2][0]=6) = 8`. Cell (2,2): `1 + min(f[1][2]=6, f[2][1]=8) = 7`. The answer is 7: the path `1 -> 3 -> 1 -> 1 -> 1`.

Time `O(rows * cols)`, space `O(rows * cols)` (or `O(cols)` rolling).

A cleaner way to handle the edges: use an infinity border so every cell can use the same formula.

```python
INF = float("inf")

def min_path_sum2(grid):
    rows, cols = len(grid), len(grid[0])
    f = [[INF] * (cols + 1) for _ in range(rows + 1)]     # one extra row and column of INF
    f[0][1] = 0                                           # makes cell (0,0) cost 0 + grid
    for r in range(rows):
        for c in range(cols):
            f[r + 1][c + 1] = grid[r][c] + min(f[r][c + 1], f[r + 1][c])
    return f[rows][cols]

print(min_path_sum2([[1, 3, 1], [1, 5, 1], [4, 2, 1]]))
print(min_path_sum2([[1, 2, 3]]))
```
```text
7
6
```

The sentinel border (a "guard") removes three `if` branches. The line `f[0][1] = 0` seeds the start. Many people prefer the explicit `if` version because the base cases are visible; choose one and be consistent.

### Unique paths with obstacles

The grid has `1` for an obstacle, `0` for open. Count right/down paths from the top-left to the bottom-right avoiding obstacles.

- State: `f(r, c)` = the number of paths to `(r, c)`.
- Transition: if the cell is an obstacle, `f = 0`. Otherwise `f(r,c) = f(r-1,c) + f(r,c-1)`.
- Base: `f(0,0) = 1` unless blocked.

```python
def paths_with_obstacles(grid):
    rows, cols = len(grid), len(grid[0])
    f = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1:
                f[r][c] = 0
            elif r == 0 and c == 0:
                f[r][c] = 1
            else:
                up = f[r - 1][c] if r > 0 else 0
                left = f[r][c - 1] if c > 0 else 0
                f[r][c] = up + left
    return f

g = [[0, 0, 0],
     [0, 1, 0],
     [0, 0, 0]]
for row in paths_with_obstacles(g):
    print(row)
print(paths_with_obstacles([[1, 0]])[0][1], paths_with_obstacles([[0, 1]])[0][1])
```
```text
[1, 1, 1]
[1, 0, 1]
[1, 1, 2]
0 0
```

The centre cell is blocked so it gets 0. The two paths go around it. If the start is blocked, everything after it is 0 (the first `elif` is never reached for the start cell, so the table stays all zero). A blocked cell *resets* its count to 0, which also kills the paths that would have flowed through it into later cells.

### Maximal square

A grid of `0` and `1`. Find the area of the largest square made only of 1s. This is a 2D DP with a surprising transition.

- State: `f(r, c)` = the side of the largest all-ones square whose **bottom-right corner** is `(r, c)`.
- Transition: if the cell is `0`, `f = 0`. Otherwise `f(r,c) = 1 + min(f(r-1,c), f(r,c-1), f(r-1,c-1))`.
- Answer: the largest `f` value, squared.

Why `min` of three neighbours? A square of side `k` ending here needs squares of side `k-1` ending at the cell above, to the left, and diagonally. The smallest of these three limits how big the square can grow.

```python
def maximal_square(matrix):
    rows, cols = len(matrix), len(matrix[0])
    f = [[0] * cols for _ in range(rows)]
    best = 0
    for r in range(rows):
        for c in range(cols):
            if matrix[r][c] == 1:
                if r == 0 or c == 0:
                    f[r][c] = 1
                else:
                    f[r][c] = 1 + min(f[r - 1][c], f[r][c - 1], f[r - 1][c - 1])
                best = max(best, f[r][c])
    return best * best, f

m = [[1, 0, 1, 0, 0],
     [1, 0, 1, 1, 1],
     [1, 1, 1, 1, 1],
     [1, 0, 0, 1, 0]]
area, f = maximal_square(m)
print(area)
for row in f:
    print(row)
```
```text
4
[1, 0, 1, 0, 0]
[1, 0, 1, 1, 1]
[1, 1, 1, 2, 2]
[1, 0, 0, 1, 0]
```

The largest value in the table is 2 (at row 2, columns 3 and 4), so the area is 4. Check `f[2][3]`: the cell is 1; the cell above `f[1][3]` is 1, the cell to the left `f[2][2]` is 1 and the diagonal `f[1][2]` is 1; so `1 + min(1, 1, 1) = 2`. Check `f[2][4]`: above is 1, left `f[2][3]` is 2, diagonal `f[1][3]` is 1; so `1 + min(1, 2, 1) = 2`. The `1` in column 0 can never grow because a square needs a left neighbour. Time and space `O(rows * cols)`; keeping the previous row and the left value (and the saved diagonal) gives `O(cols)`.

### The aliasing trap, again

When you roll rows, `prev = cur` makes both names point to the **same** list. That is harmless if the next round builds a fresh `cur`, and harmful if it does not. It matters most when the transition reads the **diagonal** cell `prev[c-1]`, because the diagonal is exactly the value an in-place update overwrites. Take a grid where you may also move diagonally (so `f(r,c) = f(r-1,c) + f(r,c-1) + f(r-1,c-1)`).

```python
def diag_paths_right(rows, cols):
    prev = [1] * cols
    for r in range(1, rows):
        cur = [1] * cols                      # a fresh list every round
        for c in range(1, cols):
            cur[c] = prev[c] + cur[c - 1] + prev[c - 1]
        prev = cur
    return prev[-1]

def diag_paths_aliased(rows, cols):
    prev = [1] * cols
    cur = prev                                # BUG: same list, not a copy
    for r in range(1, rows):
        for c in range(1, cols):
            cur[c] = prev[c] + cur[c - 1] + prev[c - 1]
    return prev[-1]

print(diag_paths_right(3, 3), diag_paths_aliased(3, 3))
```
```text
13 17
```

The correct answer for a 3 by 3 grid is 13. In the aliased version `prev[c-1]` has already been overwritten by the current row, so it is not the diagonal any more. Cures: create a new list each round, use `prev = cur[:]` or `prev, cur = cur, [1] * cols`, or save the diagonal in a variable before you overwrite it.

### Try it 7

For the grid below, how many paths exist from the top-left to the bottom-right (right/down only), with `1` as an obstacle?

```python
g = [[0, 0, 0, 0],
     [0, 1, 0, 0],
     [0, 0, 0, 1],
     [1, 0, 0, 0]]
```

<details><summary>Answer</summary>

```python
def count_paths_obs(grid):
    rows, cols = len(grid), len(grid[0])
    row = [0] * cols
    row[0] = 1 if grid[0][0] == 0 else 0
    for r in range(rows):
        for c in range(cols):
            if grid[r][c] == 1:
                row[c] = 0
            elif c > 0:
                row[c] += row[c - 1]
    return row[-1]

g = [[0, 0, 0, 0],
     [0, 1, 0, 0],
     [0, 0, 0, 1],
     [1, 0, 0, 0]]
print(count_paths_obs(g))
```
```text
3
```

This is the one-row rolling version. For each row, `row[c]` before the update is the count from above; adding `row[c-1]` adds the count from the left. A blocked cell is set to 0 in place. Hand check, row by row: row 0 gives `[1,1,1,1]`; row 1 gives `[1,0,1,2]`; row 2 gives `[1,1,2,0]`; row 3 gives `[0,1,3,3]`.
</details>

## 9. Getting the answer back: reconstruction

So far the code returned a **number**: the minimum, the maximum, the count. Real problems often ask for the **solution itself**: *which* coins, *which* path, *which* houses. There are two standard ways, and both depend on keeping the full table.

### Method 1: parent pointers (store the choice)

Next to `f[a]`, store `choice[a]`: which option achieved the best value. After the table is full, follow the choices backwards from the answer to the base case.

```python
INF = float("inf")

def coins_used(coins, amount):
    f = [INF] * (amount + 1)
    last = [None] * (amount + 1)         # last[a] = the coin used last to make a
    f[0] = 0
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a and f[a - c] + 1 < f[a]:
                f[a] = f[a - c] + 1
                last[a] = c
    if f[amount] == INF:
        return None
    used = []
    a = amount
    while a > 0:
        used.append(last[a])
        a -= last[a]                     # step back to the sub-problem
    return used

print(coins_used([1, 2, 5], 11))
print(coins_used([1, 3, 4], 6))
print(coins_used([2], 3))
```
```text
[1, 5, 5]
[3, 3]
None
```

The backwards walk is `O(answer length)`. It is exactly the path in the "DAG of states" from `amount` back to `0`. A common bug is to update `last[a]` outside the `if` (so it stores the *last coin tried*, not the *best coin*).

### Method 2: re-derive the choice from the table

You may not want to store extra memory. Since `f[a] = 1 + f[a - c]` for the best coin, you can find `c` afterwards by asking "which coin satisfies this equation?". It is the same work as the forward pass, only for one chain.

```python
def coins_used_rederive(coins, amount):
    INF = float("inf")
    f = [INF] * (amount + 1)
    f[0] = 0
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a:
                f[a] = min(f[a], f[a - c] + 1)
    if f[amount] == INF:
        return None
    used, a = [], amount
    while a > 0:
        for c in coins:
            if c <= a and f[a - c] + 1 == f[a]:   # this coin achieves the optimum
                used.append(c)
                a -= c
                break
    return used

print(coins_used_rederive([1, 2, 5], 11))
```
```text
[1, 5, 5]
```

The two methods can give different valid answers when several optimal solutions exist (here they happen to agree: 5 + 5 + 1). Tests for such problems should check the *validity and the length*, not one exact list. Keep that in mind when you write problems: if multiple answers are legal, test the properties.

### Reconstructing a path in a grid

For the minimum path sum, walk back from the bottom-right: at each cell, move to whichever of up/left has the smaller `f`, until the start.

```python
def min_path_with_route(grid):
    rows, cols = len(grid), len(grid[0])
    f = [[0] * cols for _ in range(rows)]
    for r in range(rows):
        for c in range(cols):
            best_prev = 0
            if r > 0 and c > 0:
                best_prev = min(f[r - 1][c], f[r][c - 1])
            elif r > 0:
                best_prev = f[r - 1][c]
            elif c > 0:
                best_prev = f[r][c - 1]
            f[r][c] = grid[r][c] + best_prev
    # walk back
    r, c = rows - 1, cols - 1
    route = [(r, c)]
    while (r, c) != (0, 0):
        if r == 0:
            c -= 1
        elif c == 0:
            r -= 1
        elif f[r - 1][c] <= f[r][c - 1]:
            r -= 1
        else:
            c -= 1
        route.append((r, c))
    route.reverse()
    return f[-1][-1], route

total, route = min_path_with_route([[1, 3, 1], [1, 5, 1], [4, 2, 1]])
print(total)
print(route)
```
```text
7
[(0, 0), (0, 1), (0, 2), (1, 2), (2, 2)]
```

The route goes right along the top row, then down the right column: `(0,0) -> (0,1) -> (0,2) -> (1,2) -> (2,2)`, with cost 1+3+1+1+1 = 7. When two predecessors tie, the `<=` picks "up"; the other choice gives a different but equally cheap path. Whenever a table has ties, there are several optimal answers.

### The same idea in memoised form

In top-down code, a dictionary `choice[state]` records the decision when the state is first solved. The rebuild loop then follows `choice` from the starting state. Memoisation + choices is how you find the words in word break, or the cuts in palindrome partitioning (section 16).

### Try it 8

Return the actual houses (0-based indices) robbed by the house robber for `[2, 7, 9, 3, 1]`.

<details><summary>Answer</summary>

```python
def rob_houses(nums):
    n = len(nums)
    f = [0] * (n + 1)
    if n >= 1:
        f[1] = nums[0]
    for i in range(2, n + 1):
        f[i] = max(f[i - 1], f[i - 2] + nums[i - 1])
    houses = []
    i = n
    while i >= 1:
        if i >= 2 and f[i] == f[i - 1]:
            i -= 1                       # house i-1 was skipped
        else:
            houses.append(i - 1)         # house i-1 was robbed
            i -= 2
    houses.reverse()
    return f[n], houses

print(rob_houses([2, 7, 9, 3, 1]))
```
```text
(12, [0, 2, 4])
```

Walk back from `i = 5`: `f[5]=12` differs from `f[4]=11`, so house 4 was robbed; jump to `i = 3`. `f[3]=11` differs from `f[2]=7`, so house 2 was robbed; jump to `i = 1`. At `i = 1` the first house is robbed; house 0. Money 2 + 9 + 1 = 12.
</details>

## 10. The 0/1 knapsack

You have a bag that holds weight `W`. There are `n` items, item `i` weighs `wt[i]` and is worth `val[i]`. Each item is taken **at most once**. Maximise the total value. In dsa.13 you saw that the greedy "best value per weight" rule fails here. DP does not.

Think about the last item. Either it stays out (the problem becomes: the first `i - 1` items, same bag), or it goes in (the problem becomes: the first `i - 1` items, a bag that is smaller by its weight, plus its value).

- State: `f(i, w)` = the best value using only the first `i` items with a bag of capacity `w`.
- Transition: `f(i, w) = max( f(i-1, w), f(i-1, w - wt[i-1]) + val[i-1] )`, the second option only if `wt[i-1] <= w`.
- Base: `f(0, w) = 0` for all `w` (no items, no value). `f(i, 0) = 0`.
- Answer: `f(n, W)`.

```python
def knapsack_table(wt, val, W):
    n = len(wt)
    f = [[0] * (W + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for w in range(W + 1):
            f[i][w] = f[i - 1][w]                                  # leave item i-1
            if wt[i - 1] <= w:
                f[i][w] = max(f[i][w], f[i - 1][w - wt[i - 1]] + val[i - 1])   # take it
    return f

wt = [1, 3, 4, 5]
val = [1, 4, 5, 7]
f = knapsack_table(wt, val, 7)
print("w =       ", list(range(8)))
for i, row in enumerate(f):
    print("items", i, "  ", row)
print("answer:", f[4][7])
```
```text
w =        [0, 1, 2, 3, 4, 5, 6, 7]
items 0    [0, 0, 0, 0, 0, 0, 0, 0]
items 1    [0, 1, 1, 1, 1, 1, 1, 1]
items 2    [0, 1, 1, 4, 5, 5, 5, 5]
items 3    [0, 1, 1, 4, 5, 6, 6, 9]
items 4    [0, 1, 1, 4, 5, 7, 8, 9]
answer: 9
```

Read the table row by row. Row 0 is all zeros. Row 1 allows only item 0 (weight 1, value 1): from `w = 1` onwards the best is 1. Row 2 adds item 1 (weight 3, value 4): `f[2][3] = max(f[1][3] = 1, f[1][0] + 4 = 4) = 4` and `f[2][4] = max(1, f[1][1] + 4 = 5) = 5`. Row 3 adds item 2 (weight 4, value 5): `f[3][7] = max(f[2][7] = 5, f[2][3] + 5 = 9) = 9`. Row 4 adds item 3 (weight 5, value 7): `f[4][7] = max(f[3][7] = 9, f[3][2] + 7 = 1 + 7 = 8) = 9`. The best is 9: items 1 and 2 (weights 3 + 4, values 4 + 5).

Time `O(n * W)`, space `O(n * W)`. This is called **pseudo-polynomial**: the running time depends on the *number* `W`, not on how many digits `W` has. If `W` is `10^12` this table is impossible, even though the input is short. Knapsack is NP-hard; the DP is fast only when `W` is moderate.

### Which items were taken?

Walk back from `f[n][W]`. If `f[i][w] == f[i-1][w]`, item `i - 1` was left out. Otherwise it was taken: record it and reduce `w` by its weight.

```python
def knapsack_items(wt, val, W):
    f = knapsack_table(wt, val, W)
    items, w = [], W
    for i in range(len(wt), 0, -1):
        if f[i][w] != f[i - 1][w]:        # value changed, so item i-1 was taken
            items.append(i - 1)
            w -= wt[i - 1]
    items.reverse()
    return f[len(wt)][W], items

print(knapsack_items([1, 3, 4, 5], [1, 4, 5, 7], 7))
```
```text
(9, [1, 2])
```

### The one-dimensional version, and the loop direction

Row `i` depends only on row `i - 1`, so one array is enough: `g[w]` = best value for capacity `w` using the items processed so far. The update is `g[w] = max(g[w], g[w - wt] + val)`. But **the direction of the inner loop is vital**. In the 2D version, `f[i-1][w - wt]` is the *old* row. In the 1D array, `g[w - wt]` must also still be old (not yet updated for this item). Cells with a smaller index are updated *later* if we go downwards, so:

> **For 0/1 knapsack, loop the capacity from high to low.**

```python
def knapsack_1d(wt, val, W):
    g = [0] * (W + 1)
    for i in range(len(wt)):
        for w in range(W, wt[i] - 1, -1):          # downwards
            g[w] = max(g[w], g[w - wt[i]] + val[i])
    return g[W]

def knapsack_wrong_direction(wt, val, W):
    g = [0] * (W + 1)
    for i in range(len(wt)):
        for w in range(wt[i], W + 1):              # BUG: upwards
            g[w] = max(g[w], g[w - wt[i]] + val[i])
    return g[W]

print(knapsack_1d([1, 3, 4, 5], [1, 4, 5, 7], 7))
print(knapsack_wrong_direction([1, 3, 4, 5], [1, 4, 5, 7], 7))
print(knapsack_1d([2], [10], 7), knapsack_wrong_direction([2], [10], 7))
```
```text
9
9
10 30
```

The upward loop is wrong because `g[w - wt]` has *already been updated for the same item*, so the item may be used again and again. With one item of weight 2 and value 10 and a bag of 7, the wrong version takes it three times (30). So the upward loop silently solves a different problem: the **unbounded** knapsack of the next section. One loop direction turns "each item once" into "each item many times".

### Try it 9

Fill the 1D array by hand for `wt = [2, 3]`, `val = [3, 4]`, `W = 5`. Show `g` after each item.

<details><summary>Answer</summary>

```python
wt, val, W = [2, 3], [3, 4], 5
g = [0] * (W + 1)
for i in range(len(wt)):
    for w in range(W, wt[i] - 1, -1):
        g[w] = max(g[w], g[w - wt[i]] + val[i])
    print("after item", i, g)
```
```text
after item 0 [0, 0, 3, 3, 3, 3]
after item 1 [0, 0, 3, 4, 4, 7]
```

After item 0 (weight 2, value 3): every capacity from 2 gets 3. After item 1 (weight 3, value 4): `g[5] = max(3, g[2] + 4) = 7`, `g[4] = max(3, g[1] + 4) = 4`, `g[3] = max(3, g[0] + 4) = 4`. Capacity 5 holds both items, value 7.
</details>

## 11. The unbounded knapsack

Now each item type can be used any number of times. This is the same as coin change with values. The transition is `f(w) = max over items of f(w - wt[i]) + val[i]`, and the table is one-dimensional.

```python
def unbounded(wt, val, W):
    g = [0] * (W + 1)
    for w in range(1, W + 1):
        for i in range(len(wt)):
            if wt[i] <= w:
                g[w] = max(g[w], g[w - wt[i]] + val[i])
    return g[W]

print(unbounded([2, 3], [10, 14], 7))
print(unbounded([5], [1], 4))
```
```text
34
0
```

For capacity 7 with items (2, 10) and (3, 14): two of the first plus one of the second is weight 7, value 34. The second line shows a bag where nothing fits: 0.

There are two correct loop orders here, because the *order of use* is not counted (we want a maximum, not a count). Items outside and capacity inside (upward) also works:

```python
def unbounded2(wt, val, W):
    g = [0] * (W + 1)
    for i in range(len(wt)):
        for w in range(wt[i], W + 1):            # upwards: item may repeat
            g[w] = max(g[w], g[w - wt[i]] + val[i])
    return g[W]

print(unbounded2([2, 3], [10, 14], 7))
```
```text
34
```

Compare with section 10: the only difference between 0/1 and unbounded is the **direction of the capacity loop** (down for 0/1, up for unbounded). Learn this pair as one fact:

| Items | Capacity loop | Why |
|---|---|---|
| each at most once | high to low | `g[w - wt]` must be the old value |
| unlimited | low to high | `g[w - wt]` may already include this item |

### Rod cutting

A rod of length `n` can be cut into integer pieces. A piece of length `k` sells for `price[k-1]`. Maximise the total. This is an unbounded knapsack where the item lengths are `1..n`.

```python
def rod_cut(price, n):
    f = [0] * (n + 1)
    for length in range(1, n + 1):
        for k in range(1, length + 1):
            f[length] = max(f[length], price[k - 1] + f[length - k])
    return f[n]

prices = [1, 5, 8, 9, 10, 17, 17, 20]
print([rod_cut(prices, n) for n in range(1, 9)])
```
```text
[1, 5, 8, 10, 13, 17, 18, 22]
```

For length 4 the best is two pieces of length 2 (5 + 5 = 10), better than a whole rod of length 4 (price 9). For length 8 the best is 22: pieces of length 2 and 6 (5 + 17), which beats the whole rod (price 20). The first piece `k` of the cut is tried for every `k`, and the rest of the rod is the sub-problem `f[length - k]`.

### Try it 10

Use `unbounded` to find the maximum value for capacity 12 with items `(weight, value)` = `(4, 7)` and `(5, 9)`. Compare with the 0/1 version on the same input.

<details><summary>Answer</summary>

```python
def unbounded(wt, val, W):
    g = [0] * (W + 1)
    for w in range(1, W + 1):
        for i in range(len(wt)):
            if wt[i] <= w:
                g[w] = max(g[w], g[w - wt[i]] + val[i])
    return g[W]

def zero_one(wt, val, W):
    g = [0] * (W + 1)
    for i in range(len(wt)):
        for w in range(W, wt[i] - 1, -1):
            g[w] = max(g[w], g[w - wt[i]] + val[i])
    return g[W]

wt, val = [4, 5], [7, 9]
print(unbounded(wt, val, 12), zero_one(wt, val, 12))
```
```text
21 16
```

With reuse allowed you can take the weight-4 item three times (weight 12, value 21). Without reuse you have only one of each, so the best is both items (weight 9, value 16). Reuse can never make the answer smaller, so the unbounded value is always at least the 0/1 value.
</details>

## 12. Subset sum and its relatives

Many problems are 0/1 knapsack in disguise, where the "value" is a yes/no or a count.

### Subset sum

Is there a subset of `nums` with sum exactly `target`?

- State: `f(s)` = True if some subset of the items processed so far sums to `s`.
- Transition: processing item `x`: `f(s) = f(s) or f(s - x)`.
- Base: `f(0) = True` (the empty subset).
- Loop `s` downwards (each item once).

```python
def subset_sum(nums, target):
    f = [False] * (target + 1)
    f[0] = True
    for x in nums:
        for s in range(target, x - 1, -1):
            if f[s - x]:
                f[s] = True
    return f[target]

print(subset_sum([3, 34, 4, 12, 5, 2], 9))
print(subset_sum([3, 34, 4, 12, 5, 2], 30))
print(subset_sum([], 0), subset_sum([], 1))
```
```text
True
False
True False
```

Time `O(n * target)`, space `O(target)`. This is where Python offers a pleasant trick: store the whole boolean array as the bits of one integer. Bit `s` is 1 if sum `s` is reachable. Adding an item `x` is `bits |= bits << x`.

```python
def subset_sum_bits(nums, target):
    bits = 1                       # only sum 0 is reachable
    for x in nums:
        bits |= bits << x          # every reachable s also makes s + x
    return (bits >> target) & 1 == 1

print(subset_sum_bits([3, 34, 4, 12, 5, 2], 9), subset_sum_bits([3, 34, 4, 12, 5, 2], 30))
```
```text
True False
```

Same answers, and for large inputs it runs far faster because the shifting happens inside the big-integer arithmetic, not in a Python loop. It only works for non-negative values.

### Partition equal subset sum

Can `nums` be split into two groups with equal sums? If the total `S` is odd, no. Otherwise it is subset sum with target `S / 2`.

```python
def can_partition(nums):
    total = sum(nums)
    if total % 2:
        return False
    return subset_sum(nums, total // 2)

print(can_partition([1, 5, 11, 5]), can_partition([1, 2, 3, 5]), can_partition([2, 2]))
```
```text
True False True
```

`[1, 5, 11, 5]` splits as `[11]` and `[1, 5, 5]`. The reduction is the whole idea: *recognise the knapsack inside the story.*

### Counting subsets with a given sum

Count how many subsets sum to `target`. Same array, but `f[s]` holds a count and the update is `+=`.

```python
def count_subsets(nums, target):
    f = [0] * (target + 1)
    f[0] = 1
    for x in nums:
        for s in range(target, x - 1, -1):
            f[s] += f[s - x]
    return f[target]

print(count_subsets([1, 2, 3, 3], 6))
print(count_subsets([0, 0, 1], 1))
```
```text
3
4
```

The first answer is 3: `{1, 2, 3}` using the first 3, `{1, 2, 3}` using the second 3, and `{3, 3}`. Items with value 0 double the count: in the second call `{1}`, `{0, 1}`, `{0', 1}` and `{0, 0', 1}` are four subsets, and the output is 4. Counting subsets counts *positions*, not distinct values.

### Target sum (assign + or -)

Put a `+` or `-` before each number so the expression equals `target`. Count the ways. Let `P` be the sum of numbers marked `+` and `N` the sum of those marked `-`. Then `P - N = target` and `P + N = S` (the total), so `P = (S + target) / 2`. The question becomes: **count the subsets with sum `P`**.

```python
def target_sum(nums, target):
    total = sum(nums)
    if abs(target) > total or (total + target) % 2:
        return 0
    return count_subsets(nums, (total + target) // 2)

print(target_sum([1, 1, 1, 1, 1], 3))
print(target_sum([1], 2), target_sum([1, 2], 0))
```
```text
5
0 0
```

For five ones and target 3: `P = (5 + 3) / 2 = 4`; choose which four of the five are `+`: 5 ways. The guards matter: if the total plus target is odd, or the target is out of reach, the answer is 0. Without the guards, `P` could be fractional or negative and the array code would crash or give nonsense.

### Try it 11

Which weights can a balance scale measure if you may put the given weights only on one pan? For `[1, 3, 5]`, list all measurable totals from 0 to 9 using subset sum.

<details><summary>Answer</summary>

```python
def reachable_sums(nums, limit):
    f = [False] * (limit + 1)
    f[0] = True
    for x in nums:
        for s in range(limit, x - 1, -1):
            if f[s - x]:
                f[s] = True
    return [s for s in range(limit + 1) if f[s]]

print(reachable_sums([1, 3, 5], 9))
```
```text
[0, 1, 3, 4, 5, 6, 8, 9]
```

The subsets of `{1, 3, 5}` give sums 0, 1, 3, 4, 5, 6, 8, 9. Sums 2 and 7 are not reachable. The same array answers "which totals are possible?" for every target at once.
</details>

## 13. Longest increasing subsequence (LIS)

A **subsequence** keeps the order but may skip items. Find the length of the longest strictly increasing subsequence of `nums`. For `[10, 9, 2, 5, 3, 7, 101, 18]` it is 4, for example `2, 3, 7, 18`.

### The `O(n^2)` DP

The natural state "LIS of the first `i` items" has no transition (the same issue as maximum subarray). Fix the end point.

- State: `f(i)` = the length of the longest increasing subsequence that **ends at index `i`** (with `nums[i]` as its last item).
- Transition: `f(i) = 1 + max(f(j))` over all `j < i` with `nums[j] < nums[i]`. If there is no such `j`, `f(i) = 1`.
- Base: every `f(i) >= 1` (the item alone).
- Answer: `max(f)` over all `i`.

```python
def lis_n2(nums):
    n = len(nums)
    if n == 0:
        return 0, []
    f = [1] * n
    for i in range(n):
        for j in range(i):
            if nums[j] < nums[i]:
                f[i] = max(f[i], f[j] + 1)
    return max(f), f

nums = [10, 9, 2, 5, 3, 7, 101, 18]
best, f = lis_n2(nums)
print(nums)
print(f)
print(best)
```
```text
[10, 9, 2, 5, 3, 7, 101, 18]
[1, 1, 1, 2, 2, 3, 4, 4]
4
```

Trace: `10` alone: 1. `9`: nothing smaller before it: 1. `2`: 1. `5`: `2 < 5` so `f = 1 + 1 = 2`. `3`: `2 < 3` gives 2. `7`: smaller items before it are 2 (f=1), 5 (f=2), 3 (f=2), so `1 + 2 = 3`. `101`: all smaller; the best is `f[5] = 3` giving 4. `18`: also 4. The maximum is 4.

Time `O(n^2)`, space `O(n)`.

### Rebuilding the subsequence

Store `parent[i]`, the `j` that gave the best `f[i]`. Start from the index with the largest `f`, then follow parents.

```python
def lis_with_path(nums):
    n = len(nums)
    if n == 0:
        return []
    f = [1] * n
    parent = [-1] * n
    for i in range(n):
        for j in range(i):
            if nums[j] < nums[i] and f[j] + 1 > f[i]:
                f[i] = f[j] + 1
                parent[i] = j
    end = max(range(n), key=lambda i: f[i])
    path = []
    while end != -1:
        path.append(nums[end])
        end = parent[end]
    return path[::-1]

print(lis_with_path([10, 9, 2, 5, 3, 7, 101, 18]))
print(lis_with_path([0, 1, 0, 3, 2, 3]))
print(lis_with_path([7, 7, 7]))
```
```text
[2, 5, 7, 101]
[0, 1, 2, 3]
[7]
```

The first answer shows one of several valid longest subsequences (ties are broken by `>`: the first best parent wins). The last answer: with a strict `<`, equal numbers do not extend each other, so the longest strictly increasing subsequence of `[7, 7, 7]` has length 1. For a **non-decreasing** subsequence, change the test to `<=`.

### The `O(n log n)` method with `bisect`

Here is a different state, a clever one. Keep a list `tails` where `tails[k]` is the **smallest possible last value** of an increasing subsequence of length `k + 1` found so far. Why smallest? A subsequence that ends with a smaller number is easier to extend later, so we never need to remember a worse one.

Two facts make this work. First, `tails` is always sorted (increasing). Second, for each new number `x`:

- If `x` is larger than everything in `tails`, it extends the longest subsequence: **append**.
- Otherwise find the first position `k` with `tails[k] >= x` (`bisect_left`) and **replace** `tails[k]` with `x`. We now have an increasing subsequence of length `k + 1` ending in a smaller value.

The length of `tails` at the end is the LIS length. (The list itself is *not* an actual subsequence. Only its length is meaningful.)

```python
from bisect import bisect_left

def lis_fast(nums):
    tails = []
    for x in nums:
        k = bisect_left(tails, x)
        if k == len(tails):
            tails.append(x)
        else:
            tails[k] = x
        print("x =", x, " tails =", tails)
    return len(tails)

print(lis_fast([10, 9, 2, 5, 3, 7, 101, 18]))
```
```text
x = 10  tails = [10]
x = 9  tails = [9]
x = 2  tails = [2]
x = 5  tails = [2, 5]
x = 3  tails = [2, 3]
x = 7  tails = [2, 3, 7]
x = 101  tails = [2, 3, 7, 101]
x = 18  tails = [2, 3, 7, 18]
4
```

Follow the lines. `10`: tails `[10]`. `9` replaces 10 (a length-1 subsequence ending in 9 is better than one ending in 10). `2` replaces 9. `5` is larger than everything: append, `[2, 5]`. `3` replaces 5 (length 2 now ends at 3). `7` appends: `[2, 3, 7]`. `101` appends. `18` replaces 101. Final length 4.

`bisect_left` (first position with `tails[k] >= x`) is correct for **strictly** increasing, since an equal number replaces rather than extends. For non-decreasing, use `bisect_right`. Time `O(n log n)`, space `O(n)`.

```python
from bisect import bisect_left, bisect_right

def lis_len(nums, strict=True):
    tails = []
    find = bisect_left if strict else bisect_right
    for x in nums:
        k = find(tails, x)
        if k == len(tails):
            tails.append(x)
        else:
            tails[k] = x
    return len(tails)

data = [2, 2, 3, 3, 1]
print(lis_len(data, strict=True), lis_len(data, strict=False))
```
```text
2 4
```

### Variations that reuse LIS

- **Longest non-decreasing subsequence**: `<=` or `bisect_right`.
- **Longest decreasing subsequence**: negate the numbers, or reverse the comparison.
- **Minimum deletions to make an array sorted**: `n - LIS`.
- **Envelopes that nest** (sort by width ascending and height descending, then LIS on heights).
- **Longest bitonic subsequence**: LIS ending at `i` plus LDS starting at `i`, minus 1.

### Try it 12

What is `tails` after processing `[4, 10, 4, 3, 8, 9]`? What is the LIS length? Predict, then run.

<details><summary>Answer</summary>

```python
from bisect import bisect_left
tails = []
for x in [4, 10, 4, 3, 8, 9]:
    k = bisect_left(tails, x)
    if k == len(tails):
        tails.append(x)
    else:
        tails[k] = x
print(tails, len(tails))
```
```text
[3, 8, 9] 3
```

`4` gives `[4]`; `10` appends; the second `4` replaces the first `4` (position 0, since `bisect_left` finds the first element `>= 4`); `3` replaces `4`; `8` replaces `10`; `9` appends. Length 3 (for example `4, 8, 9`). Here the final `tails` happens to be a real subsequence, but it need not be: for `[2, 5, 3, 1]` the list ends as `[1, 3]`, and `1` comes after `3` in the input. Only the length is guaranteed.
</details>

## 14. Longest common subsequence (LCS)

Two strings `a` and `b`. Find the length of the longest sequence of characters that appears in both **in order** (not necessarily next to each other). For `"abcde"` and `"ace"` it is 3 (`"ace"`). This is the heart of the `diff` tool.

- State: `f(i, j)` = the LCS length of the prefixes `a[:i]` and `b[:j]`.
- Transition. Look at the last characters `a[i-1]` and `b[j-1]`.
  - If they are **equal**, they can be matched: `f(i, j) = f(i-1, j-1) + 1`.
  - If different, at least one of them is not used: `f(i, j) = max(f(i-1, j), f(i, j-1))` (drop the last character of `a`, or of `b`).
- Base: `f(0, j) = f(i, 0) = 0` (an empty string has nothing in common).
- Answer: `f(len(a), len(b))`. Table size `(len(a)+1) x (len(b)+1)`.

```python
def lcs_table(a, b):
    n, m = len(a), len(b)
    f = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                f[i][j] = f[i - 1][j - 1] + 1
            else:
                f[i][j] = max(f[i - 1][j], f[i][j - 1])
    return f

a, b = "abcde", "ace"
f = lcs_table(a, b)
print("     ", "  ".join(" " + ch for ch in " " + b))
for i, row in enumerate(f):
    print(("  " + a[i - 1]) if i else "   ", row)
print("LCS length:", f[len(a)][len(b)])
```
```text
           a   c   e
    [0, 0, 0, 0]
  a [0, 1, 1, 1]
  b [0, 1, 1, 1]
  c [0, 1, 2, 2]
  d [0, 1, 2, 2]
  e [0, 1, 2, 3]
LCS length: 3
```

Read the table (rows are prefixes of `"abcde"`, columns prefixes of `"ace"`). Row `a`: matching 'a' with 'a' gives `f[1][1] = f[0][0] + 1 = 1`, and the rest of the row copies it (`max` of the left). Row `b`: no matches, values carry down: 1, 1, 1. Row `c`: 'c' matches column `c`: `f[3][2] = f[2][1] + 1 = 2`. Row `d`: carries 2. Row `e`: 'e' matches column `e`: `f[5][3] = f[4][2] + 1 = 3`.

Why is it right to match equal last characters immediately? If both strings end in the same character, there is always an optimal common subsequence that uses both (exchange argument: if it used neither, appending the match makes it longer; if it used one, re-point it to the other equal character). Time `O(n * m)`, space `O(n * m)`.

### Rebuilding the LCS string

Walk backwards from `f[n][m]`: if the characters are equal, that character is in the answer: move diagonally. Otherwise move toward the larger neighbour.

```python
def lcs_string(a, b):
    f = lcs_table(a, b)
    i, j = len(a), len(b)
    out = []
    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1]:
            out.append(a[i - 1])
            i -= 1
            j -= 1
        elif f[i - 1][j] >= f[i][j - 1]:
            i -= 1
        else:
            j -= 1
    return "".join(reversed(out))

print(lcs_string("abcde", "ace"))
print(lcs_string("AGGTAB", "GXTXAYB"))
print(repr(lcs_string("abc", "xyz")))
```
```text
ace
GTAB
''
```

### Two rows are enough

Row `i` reads only row `i - 1` and the cell to its left, so keep two rows. We lose the table, so no reconstruction, but the length is still available in `O(min(n, m))` memory if you roll along the shorter string.

```python
def lcs_length(a, b):
    if len(b) > len(a):
        a, b = b, a                      # make b the shorter string
    prev = [0] * (len(b) + 1)
    for ch in a:
        cur = [0] * (len(b) + 1)
        for j in range(1, len(b) + 1):
            if ch == b[j - 1]:
                cur[j] = prev[j - 1] + 1
            else:
                cur[j] = max(prev[j], cur[j - 1])
        prev = cur
    return prev[-1]

print(lcs_length("abcde", "ace"), lcs_length("AGGTAB", "GXTXAYB"), lcs_length("", "abc"))
```
```text
3 4 0
```

### The longest common substring: a small change

A **substring** must be contiguous. Now a mismatch **resets** the count to 0 (the run is broken), and the answer is the **maximum anywhere** in the table, not the corner.

```python
def longest_common_substring(a, b):
    f = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    best = 0
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                f[i][j] = f[i - 1][j - 1] + 1
                best = max(best, f[i][j])
            # else: stays 0, the run is broken
    return best

print(longest_common_substring("abcdxyz", "xyzabcd"))
print(longest_common_substring("abcde", "ace"))
```
```text
4
1
```

The state changed its meaning: `f[i][j]` is now "the longest common suffix of `a[:i]` and `b[:j]`", the common block that ends exactly here. That is the "ends at `i`" trick again (as in Kadane and LIS).

### Try it 13

What is the LCS length of `"ABCBDAB"` and `"BDCABA"`? Compute the table with code, then use `lcs_string` to see one answer.

<details><summary>Answer</summary>

```python
a, b = "ABCBDAB", "BDCABA"
f = lcs_table(a, b)
print(f[len(a)][len(b)], lcs_string(a, b))
```
```text
4 BCBA
```

The length is 4. There are several longest common subsequences (`BCBA`, `BDAB`, `BCAB`), and which one you get depends on how you break ties when walking back. The length is unique; the string is not, so test it by checking that it is a subsequence of both inputs and has the right length.
</details>

## 15. Edit distance

The **edit distance** (Levenshtein distance) between two strings is the fewest operations that turn one into the other, where an operation is: **insert** a character, **delete** a character, or **replace** one character. Spell checkers use it. `"kitten"` to `"sitting"` takes 3: replace k by s, replace e by i, insert g.

- State: `f(i, j)` = the edit distance between `a[:i]` and `b[:j]`.
- Transition. Look at the last characters:
  - Equal: no cost, `f(i, j) = f(i-1, j-1)`.
  - Different: take the cheapest of three, plus 1:
    - replace: `f(i-1, j-1)`
    - delete from `a`: `f(i-1, j)`
    - insert into `a` (match the last of `b`): `f(i, j-1)`
- Base: `f(i, 0) = i` (delete all `i` characters), `f(0, j) = j` (insert `j` characters).
- Answer: `f(len(a), len(b))`.

```python
def edit_table(a, b):
    n, m = len(a), len(b)
    f = [[0] * (m + 1) for _ in range(n + 1)]
    for i in range(n + 1):
        f[i][0] = i
    for j in range(m + 1):
        f[0][j] = j
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            if a[i - 1] == b[j - 1]:
                f[i][j] = f[i - 1][j - 1]
            else:
                f[i][j] = 1 + min(f[i - 1][j - 1], f[i - 1][j], f[i][j - 1])
    return f

f = edit_table("horse", "ros")
print("      ", "   ".join(" " + ch for ch in "ros"))
for i, row in enumerate(f):
    print(("  " + "horse"[i - 1]) if i else "   ", row)
print("distance:", f[5][3])
```
```text
        r    o    s
    [0, 1, 2, 3]
  h [1, 1, 2, 3]
  o [2, 2, 1, 2]
  r [3, 2, 2, 2]
  s [4, 3, 3, 2]
  e [5, 4, 4, 3]
distance: 3
```

Trace a few cells for `"horse"` and `"ros"`. The first row and column are the base cases `0 1 2 3` and `0 1 2 3 4 5`. Cell `f[1][1]`: 'h' vs 'r' differ, so `1 + min(f[0][0]=0, f[0][1]=1, f[1][0]=1) = 1`. Cell `f[2][1]`: 'o' vs 'r' differ, `1 + min(f[1][0]=1, f[1][1]=1, f[2][0]=2) = 2`. Cell `f[2][2]`: 'o' = 'o', so copy the diagonal `f[1][1] = 1`. The corner is 3 (horse -> rorse -> rose -> ros).

Time `O(n * m)`, space `O(n * m)`, or `O(min(n, m))` with two rows.

### Why the three moves are right

Think of aligning the strings. At the end of the alignment, either the two last characters are matched together (equal or replaced), or the last character of `a` is deleted, or the last character of `b` was inserted. These are all the possibilities, so the `min` over them is complete. The `+ 1` is the cost of that operation. The equal case needs no `min` because matching equal characters is never worse (the same exchange idea as in LCS).

### Reading the operations back

Walk from the corner. At `(i, j)`, find which neighbour produced the value, and record the operation.

```python
def edit_script(a, b):
    f = edit_table(a, b)
    i, j = len(a), len(b)
    ops = []
    while i > 0 or j > 0:
        if i > 0 and j > 0 and a[i - 1] == b[j - 1] and f[i][j] == f[i - 1][j - 1]:
            i, j = i - 1, j - 1                                   # match: no operation
        elif i > 0 and j > 0 and f[i][j] == f[i - 1][j - 1] + 1:
            ops.append(f"replace {a[i-1]!r} with {b[j-1]!r}")
            i, j = i - 1, j - 1
        elif i > 0 and f[i][j] == f[i - 1][j] + 1:
            ops.append(f"delete {a[i-1]!r}")
            i -= 1
        else:
            ops.append(f"insert {b[j-1]!r}")
            j -= 1
    return list(reversed(ops))

for step in edit_script("horse", "ros"):
    print(step)
print(len(edit_script("kitten", "sitting")), edit_script("", "ab"))
```
```text
replace 'h' with 'r'
delete 'r'
delete 'e'
3 ["insert 'a'", "insert 'b'"]
```

Careful with the order of the `elif` tests: the "match" test must come first and must check `a[i-1] == b[j-1]`, otherwise a replace of two *equal* characters would be counted as a cost-1 operation.

### Rolling arrays

```python
def edit_distance(a, b):
    prev = list(range(len(b) + 1))                 # row 0: f[0][j] = j
    for i in range(1, len(a) + 1):
        cur = [i] + [0] * len(b)                   # f[i][0] = i
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                cur[j] = prev[j - 1]
            else:
                cur[j] = 1 + min(prev[j - 1], prev[j], cur[j - 1])
        prev = cur
    return prev[-1]

print(edit_distance("kitten", "sitting"), edit_distance("", ""), edit_distance("abc", "abc"), edit_distance("intention", "execution"))
```
```text
3 0 0 5
```

### Related problems

- **Delete operation for two strings** (only deletions): `len(a) + len(b) - 2 * LCS(a, b)`.
- **Shortest common supersequence**: `len(a) + len(b) - LCS(a, b)`.
- **Distinct subsequences** (count how many times `b` appears as a subsequence of `a`): `f(i, j) = f(i-1, j) + (f(i-1, j-1) if a[i-1] == b[j-1])`.
- **Wildcard and regex matching**: `f(i, j)` = does `s[:i]` match `p[:j]`; `*` adds extra transitions.

### Try it 14

Use the formulas above to compute, with `lcs_length`, the number of deletions needed to make `"sea"` and `"eat"` the same string.

<details><summary>Answer</summary>

```python
a, b = "sea", "eat"
common = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
for i in range(1, len(a) + 1):
    for j in range(1, len(b) + 1):
        if a[i - 1] == b[j - 1]:
            common[i][j] = common[i - 1][j - 1] + 1
        else:
            common[i][j] = max(common[i - 1][j], common[i][j - 1])
lcs = common[len(a)][len(b)]
print(len(a) + len(b) - 2 * lcs)
```
```text
2
```

The LCS is `"ea"` (length 2); delete 's' from the first and 't' from the second: 2 deletions. If replacement were allowed (edit distance), it would be 2 as well here.
</details>

## 16. Palindromes

A palindrome reads the same backwards. Three common problems; all three show a different technique.

### Longest palindromic substring

The substring must be contiguous. Idea 1 (DP): `is_pal(i, j)` is True when `s[i] == s[j]` and the inside `is_pal(i+1, j-1)` is True (or the inside is empty or one letter). This state has a clear order: shorter substrings first.

```python
def longest_pal_dp(s):
    n = len(s)
    if n == 0:
        return ""
    is_pal = [[False] * n for _ in range(n)]
    start, best = 0, 1
    for i in range(n):
        is_pal[i][i] = True                       # length 1
    for length in range(2, n + 1):                # shorter substrings first
        for i in range(n - length + 1):
            j = i + length - 1
            if s[i] == s[j] and (length == 2 or is_pal[i + 1][j - 1]):
                is_pal[i][j] = True
                if length > best:
                    start, best = i, length
    return s[start:start + best]

print(longest_pal_dp("babad"), longest_pal_dp("cbbd"), longest_pal_dp("a"), repr(longest_pal_dp("")))
```
```text
bab bb a ''
```

This is the first table that is **filled by length**, not by row and column. Whenever `f(i, j)` depends on `f(i+1, j-1)`, a row-by-row order does not work directly, so loop over the length of the substring. We use this pattern again in interval DP.

Idea 2: **expand around the centre**. Every palindrome has a centre (a letter or a gap between two letters). Expand outward while the ends match. No table at all, and the memory is `O(1)`.

```python
def longest_pal_expand(s):
    best = ""
    for centre in range(len(s)):
        for lo, hi in ((centre, centre), (centre, centre + 1)):    # odd, even length
            while lo >= 0 and hi < len(s) and s[lo] == s[hi]:
                lo -= 1
                hi += 1
            if hi - lo - 1 > len(best):
                best = s[lo + 1:hi]
    return best

print(longest_pal_expand("babad"), longest_pal_expand("cbbd"), longest_pal_expand("forgeeksskeegfor"))
```
```text
bab bb geeksskeeg
```

Both are `O(n^2)` time. Expansion is simpler and uses less memory; the DP version is the template for the harder problems (counting all palindromic substrings, or the cuts below). This is also a good example of DP not always being the best tool: the "expand" method is a one-line idea.

### Minimum cuts to split into palindromes

Cut `s` into pieces, each a palindrome. Fewest cuts?

- State: `cuts(i)` = the fewest cuts for the first `i` characters.
- Transition: the last piece is `s[j:i]`. If it is a palindrome, `cuts(i) = min(cuts(j) + 1)`.
- Base: `cuts(0) = -1` (so a single palindromic piece costs `-1 + 1 = 0` cuts).
- We need a fast palindrome test, so we first fill the `is_pal` table.

```python
def min_cuts(s):
    n = len(s)
    is_pal = [[False] * n for _ in range(n)]
    for i in range(n - 1, -1, -1):                 # i downwards: needs row i+1
        for j in range(i, n):
            if s[i] == s[j] and (j - i < 2 or is_pal[i + 1][j - 1]):
                is_pal[i][j] = True
    cuts = [0] * (n + 1)
    cuts[0] = -1
    for i in range(1, n + 1):
        cuts[i] = i - 1                              # worst case: cut between every letter
        for j in range(i):
            if is_pal[j][i - 1]:
                cuts[i] = min(cuts[i], cuts[j] + 1)
    return cuts[n]

print(min_cuts("aab"), min_cuts("a"), min_cuts("ab"), min_cuts("racecar"), min_cuts("abacdc"))
```
```text
1 0 1 0 1
```

For `"aab"`: `"aa" | "b"` is one cut. This table `is_pal` is filled with `i` going **downwards** and `j` upwards, because `is_pal[i][j]` needs `is_pal[i+1][j-1]`, from the row below. That is another way (besides filling by length) to order such a table.

Time `O(n^2)`, space `O(n^2)` for `is_pal`.

### Trap: the base case `cuts(0) = -1`

A very frequent bug is to use `cuts(0) = 0`. Then a whole-string palindrome like `"racecar"` costs 1 cut instead of 0. The `-1` is intentional: it cancels the `+ 1` that counts the piece, so "k pieces" costs "k - 1 cuts".

### Try it 15

Count all palindromic substrings of `"aaa"` (substrings at different positions count separately). Use the expand idea.

<details><summary>Answer</summary>

```python
def count_palindromes(s):
    total = 0
    for centre in range(len(s)):
        for lo, hi in ((centre, centre), (centre, centre + 1)):
            while lo >= 0 and hi < len(s) and s[lo] == s[hi]:
                total += 1
                lo -= 1
                hi += 1
    return total

print(count_palindromes("aaa"), count_palindromes("abc"))
```
```text
6 3
```

Each successful expansion step is one palindrome: `"a"` three times, `"aa"` twice and `"aaa"` once, 6 in total. For `"abc"`, only the three single letters.
</details>

## 17. Interval DP

Some problems ask about a **range** `[i, j]` of a sequence, and the best way to handle the range is to **split it** at some point `k` and combine the answers of the two parts. The state is a pair `(i, j)`, and the order of filling is **by the length of the range**: short ranges first.

The skeleton looks like this:

```text
for length in 2..n:
    for i in 0..n-length:
        j = i + length - 1
        f[i][j] = best over k in [i, j) of  combine(f[i][k], f[k+1][j], cost(i, k, j))
```

There are `O(n^2)` states and `O(n)` choices of `k` each, so interval DP is typically `O(n^3)` time and `O(n^2)` space. It is only practical for `n` up to a few hundred.

### Longest palindromic subsequence

A subsequence (not contiguous) that is a palindrome. For `"bbbab"` the answer is 4 (`"bbbb"`).

- State: `f(i, j)` = the longest palindromic subsequence inside `s[i..j]`.
- Transition: if `s[i] == s[j]`, these two ends frame a palindrome: `f(i, j) = f(i+1, j-1) + 2`. Otherwise drop one end: `f(i, j) = max(f(i+1, j), f(i, j-1))`.
- Base: `f(i, i) = 1`; an empty range (when `i > j`) is 0.

```python
def lps(s):
    n = len(s)
    if n == 0:
        return 0
    f = [[0] * n for _ in range(n)]
    for i in range(n):
        f[i][i] = 1
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            if s[i] == s[j]:
                f[i][j] = (f[i + 1][j - 1] if length > 2 else 0) + 2
            else:
                f[i][j] = max(f[i + 1][j], f[i][j - 1])
    return f[0][n - 1]

print(lps("bbbab"), lps("cbbd"), lps("a"), lps(""))
```
```text
4 2 1 0
```

(There is a shortcut: the longest palindromic subsequence of `s` equals `LCS(s, reversed(s))`. Try it with `lcs_length` from section 14: same numbers.) The `length > 2` guard handles `length == 2`, where the inside is empty (0).

### Matrix chain multiplication

You must multiply matrices `A1 A2 ... An`. Matrix multiplication is associative, so the *result* does not depend on the bracketing, but the *cost* does. Multiplying a `p x q` matrix by a `q x r` matrix costs `p * q * r` scalar multiplications. Find the cheapest bracketing.

The dimensions are given as a list `dims` of length `n + 1`: matrix `i` is `dims[i] x dims[i+1]`.

- State: `f(i, j)` = the cheapest cost of multiplying matrices `i..j`.
- Transition: choose the last split `k`: multiply `i..k` and `k+1..j` separately, then multiply the two results (sizes `dims[i] x dims[k+1]` and `dims[k+1] x dims[j+1]`): cost `dims[i] * dims[k+1] * dims[j+1]`.
  `f(i, j) = min over k in [i, j) of f(i, k) + f(k+1, j) + dims[i] * dims[k+1] * dims[j+1]`.
- Base: `f(i, i) = 0` (a single matrix needs no multiplication).

```python
def matrix_chain(dims):
    n = len(dims) - 1                       # number of matrices
    f = [[0] * n for _ in range(n)]
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            f[i][j] = min(f[i][k] + f[k + 1][j] + dims[i] * dims[k + 1] * dims[j + 1]
                          for k in range(i, j))
    return f[0][n - 1], f

best, f = matrix_chain([10, 30, 5, 60])
print(best)
print(f)
print(matrix_chain([40, 20, 30, 10, 30])[0])
```
```text
4500
[[0, 1500, 4500], [0, 0, 9000], [0, 0, 0]]
26000
```

For dimensions `[10, 30, 5, 60]` the matrices are `10x30`, `30x5` and `5x60`. Bracketing `(A1 A2) A3`: `10*30*5 + 10*5*60 = 1500 + 3000 = 4500`. Bracketing `A1 (A2 A3)`: `30*5*60 + 10*30*60 = 9000 + 18000 = 27000`. The table entry `f[0][2] = 4500` takes the first. The min over `k` tried both splits.

### Burst balloons

Balloons with numbers `nums`. Bursting balloon `i` earns `left * nums[i] * right`, where `left` and `right` are its current neighbours (the edge counts as 1). Burst them all in the best order to maximise the coins.

If you pick the *first* balloon to burst, the remaining balloons become neighbours across the gap: the two sides stop being independent. The key insight: **choose the last balloon to burst** in a range. When `k` is the last balloon of the range `(i, j)`, its neighbours are the fixed boundaries `i` and `j`, and the left and right parts are independent.

- Pad the array with 1 on both ends: `a = [1] + nums + [1]`.
- State: `f(i, j)` = the best coins from bursting all balloons **strictly between** `i` and `j`.
- Transition: `f(i, j) = max over k in (i, j) of f(i, k) + f(k, j) + a[i] * a[k] * a[j]`.
- Base: `f(i, i+1) = 0` (nothing between).
- Answer: `f(0, len(a) - 1)`.

```python
def burst_balloons(nums):
    a = [1] + nums + [1]
    n = len(a)
    f = [[0] * n for _ in range(n)]
    for gap in range(2, n):                    # distance between i and j
        for i in range(n - gap):
            j = i + gap
            f[i][j] = max(f[i][k] + f[k][j] + a[i] * a[k] * a[j]
                          for k in range(i + 1, j))
    return f[0][n - 1]

print(burst_balloons([3, 1, 5, 8]), burst_balloons([1, 5]), burst_balloons([7]), burst_balloons([]))
```
```text
167 10 7 0
```

For `[3, 1, 5, 8]` the best is 167. One optimal order: burst 1 (3*1*5 = 15), then 5 (3*5*8 = 120), then 3 (1*3*8 = 24), then 8 (1*8*1 = 8): 15 + 120 + 24 + 8 = 167. For `[]` the loop never runs and `f[0][1]` is 0.

Changing the question "which is first?" into "which is **last**?" is the most important trick in interval DP. It is also what makes the two sides independent.

### Order of evaluation, again

In all three, `f(i, j)` needs smaller ranges inside it. If you loop `i` from 0 and `j` from `i`, the cells `f(i, k)` are ready (same row, smaller `j`), but `f(k+1, j)` (a *later* row) is not. Three ways to fix the order: loop by **length** (as above), or loop `i` downwards and `j` upwards, or write it top-down with `@cache` and let recursion find the order. For interval DP, top-down is often the least error-prone.

```python
import functools

def burst_balloons_topdown(nums):
    a = [1] + nums + [1]

    @functools.cache
    def best(i, j):
        if j - i < 2:
            return 0
        return max(best(i, k) + best(k, j) + a[i] * a[k] * a[j]
                   for k in range(i + 1, j))

    return best(0, len(a) - 1)

print(burst_balloons_topdown([3, 1, 5, 8]))
```
```text
167
```

### Try it 16

What is the cheapest cost for `dims = [5, 10, 3, 12, 5]` (four matrices)? Predict the best bracketing before you run.

<details><summary>Answer</summary>

```python
def matrix_chain(dims):
    n = len(dims) - 1
    f = [[0] * n for _ in range(n)]
    for length in range(2, n + 1):
        for i in range(n - length + 1):
            j = i + length - 1
            f[i][j] = min(f[i][k] + f[k + 1][j] + dims[i] * dims[k + 1] * dims[j + 1]
                          for k in range(i, j))
    return f[0][n - 1]

print(matrix_chain([5, 10, 3, 12, 5]))
```
```text
405
```

The matrices are `5x10`, `10x3`, `3x12`, `12x5`. The bracketing `(A1 A2)(A3 A4)` costs `5*10*3 = 150`, plus `3*12*5 = 180`, plus multiplying the two results (`5x3` times `3x5`) `5*3*5 = 75`: total 405. The code tries every split and confirms that 405 is the minimum.
</details>

## 18. DP on trees

In dsa.10 you wrote tree functions that **return a value to the parent**. Tree DP is exactly that, where the returned value is a small bundle of answers: the answer for this subtree under each possible "mode" of the root.

The state is `(node, mode)`. The transition combines the children's bundles. The order is a post-order walk: children before parent. There is no cycle, so no memo is needed when each node is visited once.

The two helpers below build trees from the level-order lists used on LeetCode (`None` means no child).

```python
from collections import deque

class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right

def build_tree(values):
    if not values or values[0] is None:
        return None
    root = TreeNode(values[0])
    queue = deque([root])
    i = 1
    while queue and i < len(values):
        node = queue.popleft()
        if i < len(values) and values[i] is not None:
            node.left = TreeNode(values[i])
            queue.append(node.left)
        i += 1
        if i < len(values) and values[i] is not None:
            node.right = TreeNode(values[i])
            queue.append(node.right)
        i += 1
    return root

t = build_tree([3, 2, 3, None, 3, None, 1])
print(t.val, t.left.val, t.right.val, t.left.right.val, t.right.right.val)
```
```text
3 2 3 3 1
```

### House robber III

The houses form a binary tree. If you rob a house, you cannot rob its parent or its children (directly linked houses). Maximise the money.

The earlier linear version used `f(i)` with a single value. Here a node needs **two** answers, because the parent's choice depends on whether the child was robbed.

- State: `rob(node)` = best total in the subtree of `node` **if `node` is robbed**; `skip(node)` = best total in that subtree **if `node` is not robbed**. The function returns the pair.
- Transition:
  - `rob(node) = node.val + skip(left) + skip(right)` (children must be skipped).
  - `skip(node) = max(rob(left), skip(left)) + max(rob(right), skip(right))` (children are free).
- Base: a missing child gives `(0, 0)`.
- Answer: `max(rob(root), skip(root))`.

```python
def rob_tree(root):
    def go(node):
        if node is None:
            return 0, 0                          # (rob, skip)
        lrob, lskip = go(node.left)
        rrob, rskip = go(node.right)
        rob = node.val + lskip + rskip
        skip = max(lrob, lskip) + max(rrob, rskip)
        return rob, skip

    return max(go(root))

print(rob_tree(build_tree([3, 2, 3, None, 3, None, 1])))
print(rob_tree(build_tree([3, 4, 5, 1, 3, None, 1])))
print(rob_tree(None), rob_tree(build_tree([5])))
```
```text
7
9
0 5
```

For the first tree (root 3, children 2 and 3, grandchildren 3 under the left child and 1 under the right child) the best is 7: rob the root 3 and the two grandchildren 3 and 1. The second tree gives 9: rob the two children of the root, 4 and 5, which are not adjacent to each other. Time `O(n)`: each node is visited once and does `O(1)` work. Space `O(h)` for the recursion (the height).

Why the pair? The simpler recursion "rob this node or not, recursing to children and grandchildren" without memoisation recomputes subtrees (the grandchild appears under two different paths), and is exponential. Returning both answers from each call is the DP: it computes each state `(node, mode)` exactly once.

### The memoised version, for comparison

If you prefer to think "rob this node or not" with grandchildren, memoise on the **node object** (nodes are hashable by identity).

```python
import functools

def rob_tree_memo(root):
    @functools.cache
    def best(node):
        if node is None:
            return 0
        take = node.val
        if node.left:
            take += best(node.left.left) + best(node.left.right)
        if node.right:
            take += best(node.right.left) + best(node.right.right)
        leave = best(node.left) + best(node.right)
        return max(take, leave)

    return best(root)

print(rob_tree_memo(build_tree([3, 2, 3, None, 3, None, 1])))
```
```text
7
```

Here `best(node)` means the best for the subtree of `node` with no restriction. Same answer, different state definition. Both are correct; the pair version is more efficient (no hashing) and is the standard.

### Diameter and max path sum: the same pattern

In dsa.10 section 7 the diameter function returned the **height** to its parent but recorded the best answer in a shared variable. That is tree DP with state `height(node)` and answer `max over nodes (left + right)`. The **maximum path sum** problem is the same with sums, ignoring negative branches:

```python
def max_path_sum(root):
    best = [float("-inf")]

    def down(node):                      # best path going down from node, ending at a leaf side
        if node is None:
            return 0
        left = max(down(node.left), 0)   # a negative branch is never worth taking
        right = max(down(node.right), 0)
        best[0] = max(best[0], node.val + left + right)    # path bending at this node
        return node.val + max(left, right)                 # what the parent may use

    down(root)
    return best[0]

print(max_path_sum(build_tree([1, 2, 3])))
print(max_path_sum(build_tree([-10, 9, 20, None, None, 15, 7])))
print(max_path_sum(build_tree([-3])))
```
```text
6
42
-3
```

The pattern: the function **returns what the parent can use** (a path that goes down in one direction only) and **records what can be the final answer** (a path that bends here and uses both sides). When you see "the answer may bend at any node", think of this.

### Independent set and general trees

For a tree given as an adjacency list, root it anywhere and do the same with a list of children. The classic is the **maximum independent set** (the house robber III on a general tree): `take(v) = 1 + sum(skip(child))`, `skip(v) = sum(max(take(child), skip(child)))`.

```python
def max_independent_set(n, edges):
    adj = [[] for _ in range(n)]
    for a, b in edges:
        adj[a].append(b)
        adj[b].append(a)

    def go(v, parent):
        take, skip = 1, 0
        for w in adj[v]:
            if w != parent:
                t, s = go(w, v)
                take += s
                skip += max(t, s)
        return take, skip

    return max(go(0, -1))

# a path 0-1-2-3-4 and a star around node 2
print(max_independent_set(5, [(0, 1), (1, 2), (2, 3), (3, 4)]))
print(max_independent_set(5, [(2, 0), (2, 1), (2, 3), (2, 4)]))
```
```text
3
4
```

On the path of five nodes, pick nodes 0, 2, 4: three. In the star, pick the four leaves: four. For a very deep tree (a chain of 100000 nodes) this recursion hits the recursion limit; convert it to an iterative post-order (dsa.10 section 5) or use an explicit stack.

### Try it 17

Compute `rob_tree` by hand for the tree with values `[2, 1, 3, None, 4]` (root 2; left child 1 with right child 4; right child 3). Fill in the pairs `(rob, skip)` for each node, then check by running.

<details><summary>Answer</summary>

Leaves: node 4 gives `(4, 0)`; node 3 gives `(3, 0)`. Node 1 has only a right child 4: `rob = 1 + skip(4) = 1`, `skip = max(4, 0) = 4`, so `(1, 4)`. Root 2: `rob = 2 + skip(1) + skip(3) = 2 + 4 + 0 = 6`; `skip = max(1, 4) + max(3, 0) = 4 + 3 = 7`. The answer is `max(6, 7) = 7`.

```python
print(rob_tree(build_tree([2, 1, 3, None, 4])))
```
```text
7
```

The best is to rob 4 and 3, which are not adjacent (4's parent is 1, not 3).
</details>

## 19. Bitmask DP

Sometimes the state must remember **which items out of a small set have been used**. A set of `n` items is a subset, and there are `2^n` subsets. If `n` is at most about 20, we can afford to number them: a subset is an integer whose bit `i` is 1 when item `i` is in the set. This turns "a subset" into an array index.

Quick facts about masks (bit operations from the core track):

- Empty set: `0`. All `n` items: `(1 << n) - 1`.
- Is item `i` in `mask`? `mask >> i & 1` (or `mask & (1 << i)`).
- Add item `i`: `mask | (1 << i)`.
- Remove item `i`: `mask & ~(1 << i)`.
- How many items: `mask.bit_count()`.

The key property for ordering: **adding a bit makes the number bigger**. So looping `mask` from 0 upwards visits every subset after all its subsets.

### The travelling salesman problem (TSP)

There are `n` cities and a distance matrix. Start at city 0, visit every city exactly once, and return to city 0. Find the shortest tour. Brute force tries `(n-1)!` orders. DP with a mask does it in `O(2^n * n^2)`, which for `n = 20` is about 400 million: heavy but possible in a compiled language; in Python it is fine up to about `n = 15`.

- State: `f(mask, last)` = the shortest path that starts at city 0, visits exactly the cities in `mask`, and currently stands at city `last` (which is in `mask`).
- Transition: the previous city was `prev` in `mask` without `last`: `f(mask, last) = min over prev of f(mask without last, prev) + dist[prev][last]`.
- Base: `f({0}, 0) = 0`, that is `f[1][0] = 0`.
- Answer: `min over last of f(full, last) + dist[last][0]`.

```python
def tsp(dist):
    n = len(dist)
    INF = float("inf")
    full = (1 << n) - 1
    f = [[INF] * n for _ in range(1 << n)]
    f[1][0] = 0                                    # only city 0 visited, standing there
    for mask in range(1 << n):
        if not mask & 1:                           # every valid mask contains city 0
            continue
        for last in range(n):
            if f[mask][last] == INF:
                continue
            for nxt in range(n):
                if mask >> nxt & 1:                # already visited
                    continue
                new_mask = mask | (1 << nxt)
                cost = f[mask][last] + dist[last][nxt]
                if cost < f[new_mask][nxt]:
                    f[new_mask][nxt] = cost
    return min(f[full][last] + dist[last][0] for last in range(1, n)) if n > 1 else 0

dist = [[0, 10, 15, 20],
        [10, 0, 35, 25],
        [15, 35, 0, 30],
        [20, 25, 30, 0]]
print(tsp(dist))
```
```text
80
```

This version "pushes" forward: from a known `f[mask][last]` it improves the states reachable by adding one more city. That is a valid way to organise a DP (the earlier ones "pulled" from smaller states). Either way you only need each state finalised before it is used, which the increasing `mask` loop guarantees.

The best tour is `0 -> 1 -> 3 -> 2 -> 0` with length `10 + 25 + 30 + 15 = 80`. Always cross-check a bitmask DP with a brute force on tiny inputs:

```python
from itertools import permutations

def tsp_brute(dist):
    n = len(dist)
    best = float("inf")
    for order in permutations(range(1, n)):
        route = (0,) + order + (0,)
        best = min(best, sum(dist[a][b] for a, b in zip(route, route[1:])))
    return best

print(tsp_brute(dist), tsp(dist) == tsp_brute(dist))
```
```text
80 True
```

Memory: a table of `2^n * n` entries. For `n = 20` that is 20 million numbers, too much for Python lists. The DP is for small `n` only.

### Assigning tasks: matching with a mask

Another classic: `n` workers and `n` tasks, `cost[w][t]`. Assign each worker one task, each task to one worker, minimising the total. The mask records the tasks already taken. Worker number is implied by how many bits are set: `bit_count(mask)` workers are done.

- State: `f(mask)` = the cheapest cost of assigning workers `0..k-1` to the tasks in `mask`, where `k = mask.bit_count()`.
- Transition: worker `k` takes some free task `t`: `f(mask | 1<<t) = min(f(mask) + cost[k][t])`.

```python
def assign(cost):
    n = len(cost)
    INF = float("inf")
    f = [INF] * (1 << n)
    f[0] = 0
    for mask in range(1 << n):
        if f[mask] == INF:
            continue
        worker = mask.bit_count()                 # the next worker to place
        if worker == n:
            continue
        for task in range(n):
            if not mask >> task & 1:
                new_mask = mask | (1 << task)
                f[new_mask] = min(f[new_mask], f[mask] + cost[worker][task])
    return f[(1 << n) - 1]

print(assign([[9, 2, 7], [6, 4, 3], [5, 8, 1]]))
```
```text
9
```

Here the state needs just the mask (a number up to `2^n`), because "which worker is next" is a function of the mask. Always look for such **redundant information**: any parameter that can be computed from the others should not be in the state. That is how a state shrinks from `(mask, worker)` to `(mask)`.

Time `O(2^n * n)`. The best assignment costs 9: worker 0 takes task 1 (cost 2), worker 1 takes task 0 (cost 6), worker 2 takes task 2 (cost 1). The other promising assignment, worker 1 on task 2 (cost 3) and worker 2 on task 0 (cost 5), gives `2 + 3 + 5 = 10`, which is worse.

### Try it 18

Count the subsets of `{1, 2, 3, 4, 5}` (as masks over indices) with sum exactly 8 by looping over all masks. Why is this not DP, and when would a mask DP be needed instead?

<details><summary>Answer</summary>

```python
nums = [1, 2, 3, 4, 5]
count = 0
for mask in range(1 << len(nums)):
    total = sum(nums[i] for i in range(len(nums)) if mask >> i & 1)
    if total == 8:
        count += 1
print(count)
```
```text
3
```

The subsets are `{3,5}`, `{1,2,5}` and `{1,3,4}`. This loop just enumerates all masks; nothing is stored or reused, so it is brute force `O(2^n * n)`. A mask becomes a DP *state* when two different histories reach the same mask with a different cost, and we keep only the better one, as in TSP.
</details>

## 20. Digit DP

How many integers from 1 to `N` have some property of their digits? When `N` is `10^18` you cannot test every number. Digit DP builds the numbers **digit by digit** from the most significant side, and counts the possibilities with a memoised function. The number of states is tiny: the digits are only 0 to 9, and a number has at most 19 of them.

The state has these ingredients.

- `pos`: which digit position we are filling (0 is the leftmost).
- `tight`: **are we still equal to the prefix of `N`?** If yes, the next digit cannot exceed `N`'s digit at this position; if no, we have already gone below `N` and any digit 0 to 9 is allowed.
- Whatever the property needs to remember: the previous digit, the digit sum so far, whether we have seen a 7, and so on.
- Sometimes `started`: whether we have placed a non-zero digit yet, to handle leading zeros.

### Count numbers with no digit 7

How many integers in `[0, N]` contain no digit `7`?

```python
import functools

def count_no_seven(N):
    digits = list(map(int, str(N)))

    @functools.cache
    def go(pos, tight):
        if pos == len(digits):
            return 1                                  # a complete valid number
        limit = digits[pos] if tight else 9
        total = 0
        for d in range(limit + 1):
            if d == 7:
                continue
            total += go(pos + 1, tight and d == limit)
        return total

    return go(0, True)

def brute_no_seven(N):
    return sum(1 for x in range(N + 1) if "7" not in str(x))

for N in (0, 6, 7, 70, 99, 1234):
    print(N, count_no_seven(N), brute_no_seven(N))
print(count_no_seven(10**18))
```
```text
0 1 1
6 7 7
7 7 7
70 63 63
99 81 81
1234 923 923
150094635296999122
```

The brute force and the DP agree. The DP then handles `10^18` instantly, where brute force would never finish. The count of states is `len(digits) * 2`, the work per state is at most 10.

How `tight` works: at the root we are tight (we have not gone below `N` yet). When we place a digit equal to `limit` and we were tight, we stay tight. Placing a smaller digit makes the rest **free**: `tight` becomes False, and the remaining positions can take any digit, so `go(pos + 1, False)` counts the same thing for every such prefix, which is exactly where memoisation helps.

### Leading zeros and the `started` flag

If the property involves adjacent digits, the leading zeros (we write numbers as fixed-length digit strings) would count as real digits. Count the numbers in `[1, N]` in which **no two adjacent digits are equal**. For `N = 100` the number `11` is bad and `10` is good, but the fixed-length string `"00"` or `"05"` must not count `00` as a repeated digit. So add `started`: until we place a non-zero digit, zeros are "not part of the number yet".

```python
import functools

def count_no_adjacent_equal(N):
    digits = list(map(int, str(N)))

    @functools.cache
    def go(pos, prev, tight, started):
        if pos == len(digits):
            return 1 if started else 0               # the number 0 is excluded
        limit = digits[pos] if tight else 9
        total = 0
        for d in range(limit + 1):
            now_tight = tight and d == limit
            if not started and d == 0:
                total += go(pos + 1, -1, now_tight, False)       # still in leading zeros
            elif started and d == prev:
                continue                                          # adjacent equal digits
            else:
                total += go(pos + 1, d, now_tight, True)
        return total

    return go(0, -1, True, False)

def brute(N):
    def ok(x):
        s = str(x)
        return all(a != b for a, b in zip(s, s[1:]))
    return sum(1 for x in range(1, N + 1) if ok(x))

for N in (9, 10, 11, 100, 1000, 54321):
    print(N, count_no_adjacent_equal(N), brute(N))
```
```text
9 9 9
10 10 10
11 10 10
100 90 90
1000 819 819
54321 36803 36803
```

State count: `pos` (up to 19) times `prev` (11 values including "none") times `tight` times `started`: a few hundred states for `10^18`. The values `prev = -1` mean "no previous digit yet".

### Range queries: `count(hi) - count(lo - 1)`

Digit DP almost always counts "from 0 to N". To count in a range `[lo, hi]`, subtract: `count(hi) - count(lo - 1)`. Be careful when `lo = 0`.

```python
lo, hi = 50, 100
print(count_no_adjacent_equal(hi) - count_no_adjacent_equal(lo - 1), brute(hi) - brute(lo - 1))
```
```text
45 45
```

### Try it 19

Count the integers in `[0, N]` whose digit sum equals 10, for `N = 1000`. The state needs the digit sum so far. Write the digit DP, then compare with brute force.

<details><summary>Answer</summary>

```python
import functools

def count_digit_sum(N, target):
    digits = list(map(int, str(N)))

    @functools.cache
    def go(pos, remaining, tight):
        if remaining < 0:
            return 0
        if pos == len(digits):
            return 1 if remaining == 0 else 0
        limit = digits[pos] if tight else 9
        return sum(go(pos + 1, remaining - d, tight and d == limit)
                   for d in range(limit + 1))

    return go(0, target, True)

print(count_digit_sum(1000, 10), sum(1 for x in range(1001) if sum(map(int, str(x))) == 10))
```
```text
63 63
```

Here the state `remaining` counts down from the target; the guard `remaining < 0` prunes. Leading zeros do not matter, since adding zeros does not change a sum.
</details>

## 21. How to recognise DP and design the state

You rarely see the words "dynamic programming" in a problem statement. You see clues.

### Clues in the statement

| Phrase | Typical DP |
|---|---|
| "minimum / maximum cost / length / number of ..." | optimisation over choices |
| "how many ways to ..." (with a large count, often modulo `10^9 + 7`) | counting DP |
| "is it possible to ..." (yes/no) | boolean DP (subset sum, word break) |
| "longest / shortest ... subsequence" | LIS, LCS family |
| "split into pieces", "bracket", "cut" | interval DP, or 1D with a back-look |
| "each item at most once", "capacity" | knapsack |
| "grid, moving right/down" | grid DP |
| "all permutations of up to 15-20 items" | bitmask DP |
| "count numbers up to `10^18`" | digit DP |
| "tree where each node chooses" | tree DP |

### The questions that find the state

Ask these in order, on paper.

1. **What decision am I making at each step?** (Take or skip an item; the next coin; where to cut; which city next.)
2. **What do I need to know about the past to make the future decision, and nothing more?** That is the state. If you pick "the whole history", the state space is exponential; find what the future truly depends on.
3. **Can I state the meaning of `f(...)` in one sentence?** If not, you have not defined it yet.
4. **How many states are there? What is the work per state?** Multiply. Is it fast enough for the limits (`10^7` simple operations is fine in Python)?
5. **What are the base cases, and where is the answer?**

### Common shapes of state

| Shape | Meaning of the state | Examples |
|---|---|---|
| `f(i)` | prefix of length `i`, or position `i` | stairs, robber, decode ways, word break |
| `f(i)` ending at `i` | a structure that **ends exactly at** `i` | Kadane, LIS |
| `f(i, w)` | first `i` items with `w` budget | knapsack, subset sum |
| `f(i, j)` over two sequences | prefixes of `a` and `b` | LCS, edit distance |
| `f(i, j)` over a range | substring `[i, j]` | palindromes, matrix chain, balloons |
| `f(r, c)` | grid cell | path sums, unique paths, maximal square |
| `f(node, mode)` | subtree plus a choice at the node | tree robber, independent set |
| `f(mask, last)` | set of used items, plus the last one | TSP, assignment |
| `f(pos, tight, ...)` | digit position, tightness, summary | digit DP |

### The most useful trick: "ends at" and "exactly"

When the natural state ("best among the first `i`") has no transition, change it to "best structure that **ends at `i`**" (or **uses** item `i`, or **is at** `i`). Then take the max over all `i` at the end. You have seen this three times (Kadane, LIS, longest common substring); expect it again.

### The decision checklist

Use this list before you code, and again when your answer is wrong.

```text
[ ] The state is defined in ONE English sentence.
[ ] The transition covers EVERY way to arrive at the state (no missing option).
[ ] Each way is counted ONCE (no double counting) when counting.
[ ] Base cases are written for the smallest states, including empty input.
[ ] The loops fill states AFTER the states they depend on.
[ ] The answer is read from the right place (corner? max over all? )
[ ] The table size has the +1 for the empty prefix.
[ ] Time = states x work per state fits the limits.
[ ] Tested against a brute force on tiny inputs.
```

### Try it 20

Name the state, the transition and the base case for this problem, without coding: *"A thief walks along a street of `n` houses; each house `i` has `cost[i]` to paint in red, green or blue; adjacent houses must differ in colour; minimise the total."*

<details><summary>Answer</summary>

State: `f(i, c)` = the cheapest cost to paint houses `0..i` with house `i` painted colour `c`. Transition: `f(i, c) = cost[i][c] + min(f(i-1, c'))` over colours `c' != c`. Base: `f(0, c) = cost[0][c]`. Answer: `min(f(n-1, c))` over the three colours. States `3n`, work 2 each: `O(n)`. The colour of the previous house must be in the state because the rule depends on it (the "what do I need to know about the past" question); without it you cannot check the adjacency rule.

```python
def paint_houses(cost):
    if not cost:
        return 0
    prev = cost[0][:]
    for row in cost[1:]:
        prev = [row[c] + min(prev[o] for o in range(3) if o != c) for c in range(3)]
    return min(prev)

print(paint_houses([[17, 2, 17], [16, 16, 5], [14, 3, 19]]))
```
```text
10
```
</details>

## 22. DP, greedy or backtracking?

You now have three tools for optimisation and counting problems. The choice is a matter of what the problem allows.

| | Backtracking (dsa.07) | Greedy (dsa.13) | Dynamic programming |
|---|---|---|---|
| Idea | Try all choices, undo | Make the locally best choice, never undo | Try all choices, reuse repeated sub-problems |
| Needs | Nothing | A proof that the greedy choice is safe | Overlapping sub-problems, optimal substructure |
| Typical cost | Exponential | `O(n log n)` | Polynomial in the number of states |
| Output | Can list all solutions | One optimal answer | A value; the solution via reconstruction |
| Fails when | The input is large | The greedy choice is wrong | The state space is too big |

### The same problem, three ways

Count how many ways to make 12 using the coins `[1, 5, 10]`, order ignored.

- **Backtracking** enumerates each combination. It also lists them, which DP cannot do directly. Cost grows with the answer.
- **Greedy** has no meaning here: there is no single "best".
- **DP** counts them with one array in `O(12 * 3)`.

```python
def ways_backtrack(coins, amount, start=0):
    if amount == 0:
        return 1
    count = 0
    for i in range(start, len(coins)):
        if coins[i] <= amount:
            count += ways_backtrack(coins, amount - coins[i], i)
    return count

def ways_dp(coins, amount):
    f = [1] + [0] * amount
    for c in coins:
        for a in range(c, amount + 1):
            f[a] += f[a - c]
    return f[amount]

print(ways_backtrack([1, 5, 10], 12), ways_dp([1, 5, 10], 12))
print(ways_backtrack([1, 5, 10, 25, 50], 300), ways_dp([1, 5, 10, 25, 50], 300))
```
```text
4 4
9590 9590
```

Both agree; backtracking visits every combination one at a time (9590 of them for the second call, plus all the partial ones), DP only fills 300 cells per coin.

### When greedy is enough and when it is not

Take "fewest coins". With coins `[1, 5, 10, 25]` greedy works. With `[1, 3, 4]` it does not. Test a greedy rule against the DP: the DP is the **reference answer** for any greedy idea on small inputs.

```python
INF = float("inf")

def greedy_coins(coins, amount):
    count = 0
    for c in sorted(coins, reverse=True):
        count += amount // c
        amount %= c
    return count if amount == 0 else None

def dp_coins(coins, amount):
    f = [0] + [INF] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a:
                f[a] = min(f[a], f[a - c] + 1)
    return None if f[amount] == INF else f[amount]

for coins in ([1, 5, 10, 25], [1, 3, 4], [1, 5, 6]):
    bad = [a for a in range(1, 30) if greedy_coins(coins, a) != dp_coins(coins, a)]
    print(coins, "greedy wrong for", bad[:6])
```
```text
[1, 5, 10, 25] greedy wrong for []
[1, 3, 4] greedy wrong for [6, 10, 14, 18, 22, 26]
[1, 5, 6] greedy wrong for [10, 15, 16, 20, 21, 22]
```

This is a tiny testing method you will use all the time: when you cannot prove a greedy rule, run it against DP (or brute force) on every small input and look for the first difference.

### Questions that decide between them

1. Can I list the choices, and does one choice clearly dominate the others? Try to prove it. Greedy, if provable.
2. Do different choice sequences lead to the same state, and is the state small? DP.
3. Is the state "the whole history", or must I output every solution (all permutations, all subsets)? Backtracking.
4. Is `n` tiny (at most 20) and the structure subset-like? Bitmask DP or backtracking with pruning.

## 23. Debugging a DP

A wrong DP usually has one of a small list of causes. Work through them with the tools below.

### 1. Print the table

For small inputs, print the entire table and verify a few cells by hand. Wrong values often appear in the first row or column (base case) or at the boundary. The tables in this chapter are exactly the kind of output you should be able to produce on demand.

### 2. Compare with brute force on random small inputs

Write the slow, obviously correct version (recursion without memo, or `itertools` enumeration) and compare on many tiny random inputs. The first mismatch is a minimal counterexample. Here is the pattern, testing coin change.

```python
import random
from itertools import product

INF = float("inf")

def coin_min(coins, amount):
    f = [0] + [INF] * amount
    for a in range(1, amount + 1):
        for c in coins:
            if c <= a:
                f[a] = min(f[a], f[a - c] + 1)
    return f[amount]

def coin_brute(coins, amount):
    best = INF
    limit = amount // min(coins) + 1
    for counts in product(range(limit + 1), repeat=len(coins)):
        if sum(n * c for n, c in zip(counts, coins)) == amount:
            best = min(best, sum(counts))
    return best

random.seed(1)
mismatches = 0
for _ in range(200):
    coins = random.sample(range(1, 8), random.randint(1, 3))
    amount = random.randint(0, 15)
    if coin_min(coins, amount) != coin_brute(coins, amount):
        mismatches += 1
print("mismatches:", mismatches)
```
```text
mismatches: 0
```

Zero mismatches in 200 random cases gives good confidence. A DP bug almost always shows up on a tiny input.

### 3. The usual suspects

| Symptom | Likely cause |
|---|---|
| Answer is 0 or too small | Base case missing; table never initialised to the right value (`0` vs `INF`) |
| `IndexError` | Forgot the `+1` in the table size; looked at `i - 1` when `i = 0` |
| Answer off by exactly one | Wrong base value (`cuts(0) = 0` instead of `-1`), or counted items vs gaps |
| Counts too large | Double counting: the loop order gives sequences when combinations were asked |
| Knapsack uses an item twice | The 1D capacity loop goes upwards (0/1) |
| Right on small tests, wrong on big | Hidden state missing, or a greedy shortcut in the transition |
| `RecursionError` | Top-down on a long chain; convert to a table |
| Every row identical | `[[0] * m] * n` aliasing |
| Stale answers between tests | Global or default-argument memo |
| `INF` leaking into answers | Adding to `INF` and comparing to a number later; check for `INF` before use |
| Too slow | Number of states larger than needed; extra parameters in the state |

### 4. Check the invariants

Each table has rules you can assert while debugging: values never negative, `f` non-decreasing in `w` for knapsack, `f[i][j] <= min(i, j)` for LCS, edit distance at least `abs(len(a) - len(b))`. An `assert` at the end of each row will catch a bug at the first row where it appears.

```python
def lcs_checked(a, b):
    f = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            if a[i - 1] == b[j - 1]:
                f[i][j] = f[i - 1][j - 1] + 1
            else:
                f[i][j] = max(f[i - 1][j], f[i][j - 1])
            assert f[i][j] <= min(i, j), f"LCS of {a[:i]!r}, {b[:j]!r} cannot exceed the shorter prefix"
            assert f[i][j] >= f[i - 1][j], "LCS must not shrink when a prefix grows"
    return f[-1][-1]

print(lcs_checked("AGGTAB", "GXTXAYB"))
```
```text
4
```

## 24. Common traps, collected

1. **No written state.** Coding without a one-sentence meaning of `f(...)`. Write the sentence first.
2. **Wrong or missing base case.** `f(0)`, empty strings, empty input, a single item. Test the smallest inputs.
3. **Missing `+1` in table size** for "the first `i` items", so index 0 means empty.
4. **Wrong iteration order**: reading cells not yet written. Draw the dependency arrows.
5. **`[[0] * m] * n`**: all rows are one list. Use `[[0] * m for _ in range(n)]`.
6. **`prev = cur` aliasing** when rolling rows, especially with a diagonal dependency.
7. **Mutable default argument as the memo** (`def f(x, memo={})`), or a global cache that survives between test cases.
8. **A memo key that misses a variable** the answer depends on, or includes one that it does not.
9. **Unhashable arguments** to `@cache` (lists, dicts). Pass tuples or indices.
10. **`lru_cache` or recursion on a deep chain**: `RecursionError` at about 1000. Use a table, or fill from the bottom.
11. **Testing presence with `if memo.get(k):`**: a stored `0` or empty value looks missing. Use `in`.
12. **0/1 knapsack with an upward capacity loop**: reuses items. Unbounded needs the upward loop.
13. **Combinations vs sequences**: the coin loop must be outside for combinations, inside for sequences.
14. **`INF` mistakes**: using `0` or `-1` as "impossible" so that the `min`/`max` picks it by accident. Use `float("inf")` and convert at the end.
15. **Answer in the wrong place**: the corner of the table, or `max` over all cells (LIS, Kadane, longest common substring).
16. **Reconstruction updates the choice outside the `if`**, so it records the last option tried and not the best.
17. **LIS with `tails` taken as the subsequence.** It only has the right length, not the right items.
18. **Forgetting the guards** in target sum (odd total, target out of range) and in decode ways (the digit `0`).
19. **Interval DP looping `i` upward and `j` upward** so that `f[k+1][j]` is not ready. Loop by length.
20. **Using DP where greedy or a formula is enough** (or the reverse). Check small cases against both.
21. **Optimising memory too early.** A rolling array loses the table, and with it reconstruction and easy debugging. Make it correct first.
22. **Pseudo-polynomial surprise.** Knapsack is `O(n * W)`; if `W` is `10^12`, the table cannot exist.

## 25. Summary

- **Dynamic programming** is recursion with a notebook: solve every different sub-problem once and reuse it. It needs **overlapping sub-problems** and **optimal substructure**.
- Design on paper first: **state** (one sentence), **transition**, **base case**, **where the answer is**, **order of filling**. Time = states x work per state.
- **Top-down** (`functools.cache`) is the recursion plus a cache: quick to write, only computes what is needed, but limited by the recursion depth. **Bottom-up** (a table) has no recursion, is faster, and allows memory tricks. Convert: memo to array, base cases first, recursive calls to reads, loops in dependency order.
- **Space optimisation**: if a row depends only on the previous one, keep one or two rows (rolling array); `O(1)` memory for a look-back of two. Costs: you lose reconstruction. Be careful with in-place loop direction and aliasing.
- **1D DP**: stairs, robber, Kadane (state "ends at `i`"), decode ways, word break.
- **Coin change**: min coins (`INF`), count combinations (coins outside), count sequences (amounts outside).
- **Grid DP**: min path sum, obstacles, maximal square. Rolling rows give `O(cols)` memory.
- **Knapsack**: 0/1 (capacity downwards), unbounded (upwards), subset sum, partition, count subsets, target sum (`P = (S + target) / 2`). Pseudo-polynomial time.
- **Sequences**: LIS in `O(n^2)` (state "ends at `i`") and `O(n log n)` (`tails` with `bisect_left`), LCS (match diagonally, else max), edit distance (insert, delete, replace).
- **Palindromes**: expand around the centre; palindromic subsequence via interval DP or LCS with the reverse; minimum cuts with `is_pal` and base `-1`.
- **Interval DP**: fill by length; try the **last** operation (burst balloons) or last split (matrix chain). `O(n^3)`.
- **Tree DP**: return a bundle (rob, skip) from each node; post-order.
- **Bitmask DP**: subset as an integer, `O(2^n * n^2)` for TSP, small `n` only. **Digit DP**: `(pos, tight, summary)`, count up to `N` as `go(0, True)`, with `started` for leading zeros.
- **Reconstruction**: store a parent or choice, or re-derive it, then walk backwards from the answer.
- **Choosing**: provable local choice, greedy; repeated states, DP; listing all solutions or a huge state, backtracking. Test a greedy rule against DP and a DP against brute force.

### Checklist

- [ ] I write the state in one sentence, then the transition, base case and answer location, before coding.
- [ ] I can turn a memoised function into a table and a table into rolling rows.
- [ ] I can explain why 0/1 knapsack loops downwards and why coin-combinations put the coins outside.
- [ ] I can write LIS (both ways), LCS and edit distance from memory, and rebuild the answer.
- [ ] I know the order of filling for interval DP and the "last operation" trick.
- [ ] I can write a small tree DP, a TSP bitmask DP and a digit DP with `tight`.
- [ ] I can test a DP against brute force and a greedy rule against DP.
