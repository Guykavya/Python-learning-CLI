# dsa.07 Recursion and backtracking

## 1. Thinking in smaller copies of the same problem

Open a folder on your computer. Inside are files and more folders. To count every file, you do not need a special plan for "folders inside folders inside folders". You need one rule: *count the files here, then do the same job for every folder
here*. The job inside a sub-folder is the same job, just on a smaller piece of the world. That is **recursion**: a function that solves a problem by calling itself on a smaller version of the same problem.

There is a second idea in this module, built on the first. Sometimes the question is not "compute one answer" but "try all the possibilities and keep the ones that work": all the ways to pick teammates, all the ways to place eight queens so that
none attack each other, all the ways to fill a Sudoku board. The possibilities form a *tree* of choices, and a recursive function walks that tree. If you take a wrong turn, you walk back one step and try something else. That walking back is
**backtracking**.

Why is this module so important?

1. Many problems you cannot solve with a loop have a short, clear recursive solution. Trees, graphs, parsing, "all arrangements of ...", "can we reach ...?" are all recursion at heart.
2. Dynamic programming (a later module) is "recursion plus a notebook". If you cannot write the recursion, you cannot write the dynamic programme.
3. Interviewers love it, because it shows whether you can think in states and choices.

### What you can do after this module

1. **Write a correct recursive function** with a base case, a smaller subproblem, and a clear idea of what the call returns.
2. **Draw the recursion tree of a function** and use it to count calls, find the depth, and estimate the running time.
3. **Write the backtracking template** (choose, explore, un-choose) and use it to generate subsets, combinations, permutations, partitions, and parenthesis strings.
4. **Solve board problems** (N-Queens, Sudoku, word search) and explain why each state is stored and undone the way it is.
5. **Speed up a search with pruning**: cut a branch as soon as you know it cannot lead to an answer, and measure how much work you saved.
6. **Avoid the classic traps**: a missing base case, a shared list that changes behind your back, and a forgotten "undo".

### A first look

Here is the smallest useful recursive function. It counts down and then says "go".

```python
def countdown(n):
    if n == 0:
        print("go!")
        return
    print(n)
    countdown(n - 1)

countdown(3)
```
```text
3
2
1
go!
```

Read it as a sentence: "To count down from `n`: if `n` is zero, say go. Otherwise print `n`, then count down from `n - 1`." The function calls itself, but with a *smaller* number. Eventually the number reaches 0 and the calls stop.

**Predict the output 1.** What does this print? Look at the order of the two lines inside the function.

```python
def show(n):
    if n == 0:
        return
    show(n - 1)
    print(n)

show(3)
```

<details><summary>Answer</summary>

```text
1
2
3
```

The `print` is *after* the recursive call. So the function first goes all the way down to `show(0)`, which returns, and only then does each waiting call print its own `n` while coming back up: 1, then 2, then 3. Moving one line before or after
the recursive call changes the order completely. Keep that in mind: it is the basis of many tricks in this module.

</details>

## 2. The anatomy of a recursive function

Every correct recursive function has the same three parts. If you can name them for your function, the function is almost certainly right. If you cannot, it is almost certainly wrong.

1. **Base case.** The input is so small that you can answer without calling yourself. (`n == 0`, an empty list, a leaf of a tree.)
2. **Recursive case.** Break the input into a smaller piece, call yourself on it, and combine the result with what is left.
3. **Progress.** Each recursive call must move *closer* to the base case. If it does not, the calls never stop.

A good habit is to ask three questions before you write a line of code:

- What is the smallest input, and what is its answer? (the base case)
- If I magically had the answer for a slightly smaller input, how would I get the answer for mine? (the recursive case)
- What "gets smaller" each time? (progress)

The second question is the secret. You are allowed to *trust* the recursive call. You do not trace it in your head to the bottom; you assume it works for smaller inputs (that is the idea of **induction** from your maths class) and you only check
that your own step is right.

### Example: factorial

`n! = n * (n-1) * ... * 1`, and `0! = 1`. Notice that `n! = n * (n-1)!`. That is the recursive case. And `0! = 1` is the base case.

```python
def factorial(n):
    if n == 0:                 # base case
        return 1
    return n * factorial(n - 1)   # smaller problem, then combine

for n in range(6):
    print(n, factorial(n))
```
```text
0 1
1 1
2 2
3 6
4 24
5 120
```

Trust the call: if `factorial(n - 1)` is right, then `n * factorial(n - 1)` is right. And `factorial(0)` is right by definition. By induction, all of them are right.

### Example: the sum of a list

Recursion on a list: the smaller problem is "the list without its first element".

```python
def total(nums):
    if not nums:               # base case: empty list
        return 0
    return nums[0] + total(nums[1:])

print(total([]))
print(total([5]))
print(total([3, 1, 4, 1, 5]))
```
```text
0
5
14
```

This is a nice teaching example, but a bad real-life one: `nums[1:]` copies the rest of the list every call, so the work is `n + (n-1) + ... = O(n^2)`. The fix is to pass an *index* that moves right, and never copy:

```python
def total_from(nums, i=0):
    if i == len(nums):         # base case: no elements left
        return 0
    return nums[i] + total_from(nums, i + 1)

print(total_from([3, 1, 4, 1, 5]))
```
```text
14
```

Now each call does `O(1)` work, so the whole function is `O(n)`. Remember this habit: **recurse on an index (or two indexes), not on a slice.** Almost every backtracking function in this chapter passes a `start` index for this reason.

### Several base cases and several recursive calls

A function may have more than one base case and more than one recursive call. The Fibonacci numbers show both: `fib(0) = 0`, `fib(1) = 1` (two base cases), and `fib(n) = fib(n-1) + fib(n-2)` (two calls).

```python
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

print([fib(i) for i in range(10)])
```
```text
[0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
```

### What happens without a base case or without progress

```python
import sys

def broken(n):
    return broken(n + 1)      # no base case, and no progress

try:
    broken(0)
except RecursionError as e:
    print("RecursionError:", str(e)[:40])

print("limit is", sys.getrecursionlimit())
```
```text
RecursionError: maximum recursion depth exceeded
limit is 1000
```

Python protects itself. Each call uses some memory (a *stack frame*), and when the depth passes the limit (usually 1000) it raises `RecursionError`. The limit is a safety net, not a design tool. A correct recursive function that needs more than about
1000 levels should be written with a loop or an explicit stack (section 15).

> Machine note: the default limit is 1000 on standard CPython, but it can differ in other implementations or if a program changed it.

**Try it 1.** Write `power(base, n)` for `n >= 0` using `power(base, n) = base * power(base, n - 1)`. What are the base case and the progress? What happens for `n = -1`?

<details><summary>Answer</summary>

```python
def power(base, n):
    if n == 0:
        return 1
    return base * power(base, n - 1)

print(power(2, 10))
print(power(5, 0))
```
```text
1024
1
```

Base case: `n == 0`, answer 1. Progress: `n` goes down by one. For `n = -1` the value goes -1, -2, -3, ... and never reaches 0, so you get a `RecursionError`. The lesson: the base case must be *reachable* from every input you accept. Either
check the input (`if n < 0: raise ValueError`) or document that it must be `>= 0`.

</details>

## 3. The call stack: where the waiting calls live

When `factorial(3)` calls `factorial(2)`, the first call is not finished. It is *waiting* for the answer. Python keeps a list of the waiting calls, the **call stack**. The newest call is on top. When a call returns, it is removed from the top and the
call below it can continue. (Remember stacks from your data structure lessons: last in, first out.)

Let us watch it happen. The helper below prints a line when a call starts and when it ends, with indentation that shows the depth.

```python
def factorial(n, depth=0):
    pad = "  " * depth
    print(f"{pad}factorial({n}) starts")
    if n == 0:
        print(f"{pad}  base case -> 1")
        return 1
    result = n * factorial(n - 1, depth + 1)
    print(f"{pad}factorial({n}) returns {result}")
    return result

factorial(3)
```
```text
factorial(3) starts
  factorial(2) starts
    factorial(1) starts
      factorial(0) starts
        base case -> 1
    factorial(1) returns 1
  factorial(2) returns 2
factorial(3) returns 6
```

Read it from the top. The calls go *down* (each deeper line is a new call on top of the stack), and the "returns" lines come back *up* in the reverse order. This "down, then up" shape is the heartbeat of every recursive function.

### A decorator that shows the stack for any function

You learned decorators in core.11. Here is a small one that you can reuse to debug any recursive function in this module.

```python
import functools

def trace(func):
    depth = 0
    @functools.wraps(func)
    def wrapper(*args):
        nonlocal depth
        pad = "| " * depth
        print(f"{pad}{func.__name__}{args}")
        depth += 1
        try:
            result = func(*args)
        finally:
            depth -= 1
        print(f"{pad}-> {result}")
        return result
    return wrapper

@trace
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

fib(3)
```
```text
fib(3,)
| fib(2,)
| | fib(1,)
| | -> 1
| | fib(0,)
| | -> 0
| -> 1
| fib(1,)
| -> 1
-> 2
```

Notice that `fib(1)` is called twice, and `fib(2)` appears more than once as we go to bigger numbers. That repeated work is the cost of naive recursion, and the next section turns it into a picture.

### Stack depth and memory

Each waiting call holds its own variables. The stack depth is the maximum number of calls waiting at the same time. For `factorial(n)` the depth is `n + 1`. For a function that splits the problem in half each time the depth is about `log2(n)`.
We will call this the **depth** of the recursion, and it matters for two reasons: memory use (`O(depth)` extra space) and the recursion limit.

```python
import sys

def depth_of_sum(n):
    # How deep does the stack get when we recurse n levels?
    if n == 0:
        return 0
    return 1 + depth_of_sum(n - 1)

print(depth_of_sum(500))
try:
    print(depth_of_sum(5000))
except RecursionError:
    print("too deep for the default limit")
```
```text
500
too deep for the default limit
```

**Predict the output 2.** What is printed, and how many calls are waiting at the same time at the deepest point?

```python
def f(n):
    if n == 0:
        return "x"
    return f(n - 1) + str(n)

print(f(4))
```

<details><summary>Answer</summary>

```text
x1234
```

`f(4) = f(3) + "4"`, `f(3) = f(2) + "3"`, and so on until `f(0) = "x"`. The string grows as the calls return: `x`, `x1`, `x12`, `x123`, `x1234`. At the deepest point 5 calls wait (`f(4)` down to `f(0)`).

</details>

## 4. Recursion trees

A **recursion tree** is a drawing of all the calls made by one top-level call. Each call is a node. If call A makes calls B and C, then B and C are the children of A. The first call is the root. The calls that make no more calls (base
cases) are the leaves.

This picture is the most useful tool in the module. With it you can see:

- the **depth** (the longest path from the root to a leaf = the maximum stack depth),
- the **number of calls** (the number of nodes),
- the **work per call**, and so the **total cost** = (number of nodes) x (work per node).

### Drawing the tree for `fib(4)`

Let us make the computer draw it. The function prints each call with a branch character, so the tree reads from top to bottom.

```python
def draw(n, prefix="", connector=""):
    print(prefix + connector + f"fib({n})")
    if n < 2:
        return
    if connector == "":
        child_prefix = ""
    elif connector == "└── ":
        child_prefix = prefix + "    "
    else:
        child_prefix = prefix + "│   "
    draw(n - 1, child_prefix, "├── ")
    draw(n - 2, child_prefix, "└── ")

draw(4)
```
```text
fib(4)
├── fib(3)
│   ├── fib(2)
│   │   ├── fib(1)
│   │   └── fib(0)
│   └── fib(1)
└── fib(2)
    ├── fib(1)
    └── fib(0)
```

Count the nodes: 9 calls for `fib(4)`. The leaves are the calls that return right away (`fib(1)` and `fib(0)`). Look at the repeated pieces: `fib(2)` appears twice, with its whole sub-tree. That is wasted work, because the answer to `fib(2)` is
always the same.

### Counting the calls

Let `calls(n)` be the number of calls made by `fib(n)`. One call for the node itself, plus the calls of its two children: `calls(n) = 1 + calls(n-1) + calls(n-2)`, with `calls(0) = calls(1) = 1`. Let us count by really running the function.

```python
calls = 0

def fib(n):
    global calls
    calls += 1
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

for n in (5, 10, 15, 20, 25):
    calls = 0
    value = fib(n)
    print(f"fib({n:>2}) = {value:>6}   calls = {calls:>6}")
```
```text
fib( 5) =      5   calls =     15
fib(10) =     55   calls =    177
fib(15) =    610   calls =   1973
fib(20) =   6765   calls =  21891
fib(25) =  75025   calls = 242785
```

The number of calls grows by a factor of about 1.6 for every step of `n`. That is **exponential growth**: `fib(30)` needs 2,692,537 calls, and `fib(50)` needs more than 40 billion. A tree that doubles (or nearly doubles) at every level
is the normal size of a brute-force search, and the reason why we need pruning (section 9) and memoisation.

### The shape tells you the cost

| Shape of the recursion tree | Example | Number of nodes | Depth |
|---|---|---|---|
| A single chain (one call per level) | `factorial(n)`, `total(nums)` | `n` | `n` |
| A chain that halves the input | binary search, `power` by squaring | `log n` | `log n` |
| A binary tree, depth `n`, nothing is shared | subsets of `n` items | `2^n` | `n` |
| A tree with a "wide" fan-out | permutations of `n` items | about `n!` | `n` |
| A binary tree of depth `log n` | merge sort | `n` | `log n` |

**The cost formula.** Total cost = (number of nodes) x (work done inside one node, not counting the recursive calls). Merge sort has `2n` nodes, but the node at the top merges `n` items and the ones lower down merge fewer. Adding it up level by level
gives `n` work per level and `log n` levels, so `O(n log n)`. Always count *per level* when the work per node changes.

### Memoisation: cutting the repeated sub-trees

If the same sub-problem appears many times, remember the answer after the first time. Python gives you this in one line: `functools.cache`.

```python
import functools

calls = 0

@functools.cache
def fib(n):
    global calls
    calls += 1
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

print(fib(50))
print("calls:", calls)
```
```text
12586269025
calls: 51
```

Only 51 real calls (one per value of `n`), instead of tens of billions. The tree collapsed into a chain, because each repeated sub-tree is computed only once. This is the whole idea of **dynamic programming**, and it is the topic of a later module.
In *this* module the trees do **not** have repeated sub-trees (each branch is a different partial answer), so we cannot memoise them. We make them smaller with pruning instead.

**Try it 2.** Draw by hand the recursion tree of `countdown_sum(3)`, where `countdown_sum(n) = n + countdown_sum(n-1)` and `countdown_sum(0) = 0`. How many nodes? What is the depth?

<details><summary>Answer</summary>

The tree is a chain: `countdown_sum(3) -> (2) -> (1) -> (0)`. It has 4 nodes and depth 4 (counting nodes) or 3 (counting edges). A function that makes **one** recursive call per level always has a chain-shaped tree with `n + 1` nodes.
We usually say "depth `n`" and "`O(n)` time, `O(n)` space".

```python
def countdown_sum(n):
    if n == 0:
        return 0
    return n + countdown_sum(n - 1)

print(countdown_sum(3))
```
```text
6
```

</details>

### Two ways to use a recursive call

Be careful to notice *how* a function uses the result of its children, because it changes how you read the tree.

1. **Combine the returned values** (`return a + b`): the answer flows from the leaves up to the root. Examples: `factorial`, `fib`, `total`.
2. **Do the work on the way down, return nothing useful**: you walk the tree and *do* something at the nodes (print, collect, count). Backtracking functions usually work like this: they collect answers in a list instead of returning them.

Both styles appear in this module. When you read a recursive function, first decide which style it is.

## 5. Backtracking: choose, explore, un-choose

Imagine a maze. At every junction you pick a corridor and walk on. If you reach a dead end, you do not give up: you walk back to the last junction and try the next corridor. You remember which corridors you have not tried yet.
That is backtracking. In code, "the maze" is a **tree of partial solutions**, and "walking back" is the return of a recursive call.

Three words describe each junction:

1. **Choose** one of the options and add it to the partial solution.
2. **Explore**: recurse to build the rest of the solution.
3. **Un-choose**: remove the option again, so the partial solution is exactly as it was before. Then try the next option.

The "un-choose" step is what makes backtracking different from plain recursion. It restores the state, so every sibling branch starts from the same starting point.

### The template

```text
def backtrack(path, ...):
    if path is a complete answer:
        record a COPY of path
        return                      # (or continue, if longer answers are also valid)
    for option in options_at_this_point:
        if option is not allowed:
            continue                # prune
        add option to path          # choose
        backtrack(path, ...)        # explore
        remove option from path     # un-choose
```

Almost every problem in this module is this template with three questions answered:

- **What is a complete answer?** (path has length `n`, the remaining target is 0, the board is full.)
- **What are the options at this point?** (the unused items, the next candidates, the free columns.)
- **What is not allowed?** (the same item twice, a queen under attack, a sum above the target.)

### The simplest example: all binary strings of length n

At each of the `n` positions you choose `0` or `1`. The tree has `2^n` leaves, and every leaf is one string.

```python
def binary_strings(n):
    result = []
    path = []

    def go():
        if len(path) == n:
            result.append("".join(path))
            return
        for ch in "01":
            path.append(ch)      # choose
            go()                 # explore
            path.pop()           # un-choose

    go()
    return result

print(binary_strings(3))
print(len(binary_strings(10)))
```
```text
['000', '001', '010', '011', '100', '101', '110', '111']
1024
```

Watch the walk for `n = 2`. The helper prints each choose and un-choose, so you can see the path grow and shrink.

```python
def walk(n):
    path = []

    def go(depth):
        pad = "  " * depth
        if len(path) == n:
            print(f"{pad}answer: {''.join(path)}")
            return
        for ch in "01":
            print(f"{pad}choose {ch}   path={''.join(path) + ch}")
            path.append(ch)
            go(depth + 1)
            path.pop()
            print(f"{pad}undo {ch}     path={''.join(path)}")

    go(0)

walk(2)
```
```text
choose 0   path=0
  choose 0   path=00
    answer: 00
  undo 0     path=0
  choose 1   path=01
    answer: 01
  undo 1     path=0
undo 0     path=
choose 1   path=1
  choose 0   path=10
    answer: 10
  undo 0     path=1
  choose 1   path=11
    answer: 11
  undo 1     path=1
undo 1     path=
```

Look at what happens after `answer: 00`. The `undo 0` line puts the path back to `0`, and then the loop picks the next option `1`, giving `01`. After both options at depth 1 are done, the path goes back to the empty string and the first level
tries its second option. The path is a **stack** that mirrors the call stack.

### The trap: appending the path itself

This is the number one backtracking bug. `result.append(path)` stores a *reference* to the list, not a copy. Later `path.pop()` changes that very list, so every stored "answer" changes too.

```python
def broken(n):
    result = []
    path = []

    def go():
        if len(path) == n:
            result.append(path)        # BUG: no copy
            return
        for ch in "01":
            path.append(ch)
            go()
            path.pop()

    go()
    return result

print(broken(2))
```
```text
[[], [], [], []]
```

The result holds four references to the same list, and that list is empty at the end because every `pop` has run. The fix is to store a copy: `path[:]` or `list(path)`.

### The other style: pass a new value down (no un-choose)

If the partial solution is an *immutable* value (a string, a tuple, a number), you do not need to undo anything. Each call gets a new value, and the old one is untouched. This can be simpler, but each step copies the value.

```python
def binary_strings_v2(n):
    result = []

    def go(prefix):
        if len(prefix) == n:
            result.append(prefix)
            return
        go(prefix + "0")
        go(prefix + "1")

    go("")
    return result

print(binary_strings_v2(3) == [s for s in ["000","001","010","011","100","101","110","111"]])
```
```text
True
```

Which style is better? With a list and `append`/`pop` the work per step is `O(1)`, and copying happens only for the answers. With a new string the work per step is `O(length)`. For small outputs it does not matter; for large searches the list style is
faster. We use the list style (the "real" backtracking) in most of this chapter.

**Predict the output 3.** What is printed? (Careful: where is the copy made?)

```python
result = []
path = []

def go(i):
    if i == 3:
        result.append(path[:])
        return
    path.append(i)
    go(i + 1)
    path.pop()
    go(i + 1)

go(0)
print(result)
```

<details><summary>Answer</summary>

```text
[[0, 1, 2], [0, 1], [0, 2], [0], [1, 2], [1], [2], []]
```

At each index, the function first takes `i` (include) and goes down, then removes `i` and goes down again without it (exclude). So all answers that contain 0 come first. The result has `2^3 = 8` lists: the 8 subsets of
`{0, 1, 2}`. This is the *include or exclude* view of subsets, which we meet again in the next section.

</details>

## 6. Subsets

The **power set** of a collection is the set of all its subsets, including the empty set and the whole collection. A collection of `n` items has `2^n` subsets: for each item you decide "in" or "out", independently.

### View 1: include or exclude

Decide about each item in turn. Depth is `n`; the leaves are the subsets.

```python
def subsets_include_exclude(nums):
    result = []
    path = []

    def go(i):
        if i == len(nums):
            result.append(path[:])
            return
        path.append(nums[i])     # include nums[i]
        go(i + 1)
        path.pop()
        go(i + 1)                # exclude nums[i]

    go(0)
    return result

for s in subsets_include_exclude([1, 2, 3]):
    print(s)
```
```text
[1, 2, 3]
[1, 2]
[1, 3]
[1]
[2, 3]
[2]
[3]
[]
```

### View 2: choose the next item from the rest

Here every node of the tree is itself a subset (we record the path at *every* call), and a loop chooses the next item from the ones to the right of the last choice. The `start` index makes sure you never go back, so `[2, 1]` is not produced
as well as `[1, 2]`.

```python
def subsets(nums):
    result = []
    path = []

    def go(start):
        result.append(path[:])               # every node is an answer
        for i in range(start, len(nums)):
            path.append(nums[i])
            go(i + 1)
            path.pop()

    go(0)
    return result

print(subsets([1, 2, 3]))
```
```text
[[], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3]]
```

This second view is the one to remember. It becomes **combinations** (section 7) when you only record paths of the right length, and **partitions** when the loop picks "how long is the next piece".

The tree for `[1, 2, 3]` (each node is the path at that call):

```text
[]
├── [1]
│   ├── [1,2]
│   │   └── [1,2,3]
│   └── [1,3]
├── [2]
│   └── [2,3]
└── [3]
```

There are 8 nodes, and 8 subsets. Time `O(n * 2^n)`: there are `2^n` nodes, and copying a path costs up to `n`. Space `O(n)` for the recursion plus the output.

### View 3: bit masks (no recursion)

A subset of `n` items matches a number from `0` to `2^n - 1`: bit `i` of the number says "item `i` is in". This is short, fast, and good when `n` is up to about 20.

```python
def subsets_mask(nums):
    n = len(nums)
    return [[nums[i] for i in range(n) if (mask >> i) & 1] for mask in range(1 << n)]

print(subsets_mask([1, 2, 3]))
```
```text
[[], [1], [2], [1, 2], [3], [1, 3], [2, 3], [1, 2, 3]]
```

Compare the three. They produce the same eight subsets in different orders. Use the one that fits the problem: the mask when you need "all subsets of a small set" quickly, the recursive form when you need to **prune** (stop early) or
when the choices depend on earlier choices.

### Counting, without generating

If a question only asks *how many*, do not build the lists.

```python
print([2 ** n for n in range(0, 11)])
print(2 ** 20, 2 ** 30)
```
```text
[1, 2, 4, 8, 16, 32, 64, 128, 256, 512, 1024]
1048576 1073741824
```

Twenty items give a million subsets: fine. Thirty items give a billion: too many to list in Python. Remember these numbers; they tell you when brute force is possible.

### Subsets with duplicates

What if the input has repeated values, such as `[1, 2, 2]`? If you do nothing, you get duplicate subsets, because the two `2`s are different positions but the same value.

```python
def subsets_naive(nums):
    result, path = [], []
    def go(start):
        result.append(path[:])
        for i in range(start, len(nums)):
            path.append(nums[i]); go(i + 1); path.pop()
    go(0)
    return result

print(subsets_naive([1, 2, 2]))
```
```text
[[], [1], [1, 2], [1, 2, 2], [1, 2], [2], [2, 2], [2]]
```

`[2]` appears twice and `[1, 2]` appears twice. The fix has two steps: **sort the input** (so equal values sit next to each other), then **skip a value if it equals the previous one at the same level of the loop**.

```python
def subsets_unique(nums):
    nums = sorted(nums)
    result, path = [], []

    def go(start):
        result.append(path[:])
        for i in range(start, len(nums)):
            if i > start and nums[i] == nums[i - 1]:
                continue                       # same value already tried here
            path.append(nums[i])
            go(i + 1)
            path.pop()

    go(0)
    return result

print(subsets_unique([2, 1, 2]))
```
```text
[[], [1], [1, 2], [1, 2, 2], [2], [2, 2]]
```

Why `i > start`, and not `i > 0`? The test only skips a value that was *already tried as the choice at this same level*. Inside the call, `start` is the first position of this level. The choice at `i == start` is the first at this level, so it is
always allowed even when `nums[i] == nums[i - 1]` (the previous `2` was chosen at a higher level, and we want `[2, 2]`). Using `i > 0` would wrongly remove `[2, 2]`.

```python
def subsets_wrong_skip(nums):
    nums = sorted(nums)
    result, path = [], []
    def go(start):
        result.append(path[:])
        for i in range(start, len(nums)):
            if i > 0 and nums[i] == nums[i - 1]:
                continue
            path.append(nums[i]); go(i + 1); path.pop()
    go(0)
    return result

print(subsets_wrong_skip([1, 2, 2]))
```
```text
[[], [1], [1, 2], [2]]
```

`[2, 2]` and `[1, 2, 2]` are missing. This is a classic bug, and a classic test case. The rule to remember: **"skip a duplicate of the sibling before you, never a duplicate of your parent."**

**Try it 3.** Write `subsets_of_size(nums, k)` that returns only the subsets of size `k`. Test it on `[1, 2, 3, 4]`, `k = 2`.

<details><summary>Answer</summary>

```python
def subsets_of_size(nums, k):
    result, path = [], []

    def go(start):
        if len(path) == k:
            result.append(path[:])
            return
        for i in range(start, len(nums)):
            path.append(nums[i])
            go(i + 1)
            path.pop()

    go(0)
    return result

print(subsets_of_size([1, 2, 3, 4], 2))
```
```text
[[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]
```

The only change from `subsets` is when we record: only when the path has the right length, and then we `return` (no need to go deeper). This is exactly the combination generator of the next section.

</details>

## 7. Combinations

A **combination** is a choice of `k` items out of `n`, where the order does not matter: `{1, 3}` and `{3, 1}` are the same. The number of them is "n choose k" = `n! / (k! (n-k)!)`.

```python
def combine(n, k):
    """All k-element combinations of 1..n, in increasing order."""
    result, path = [], []

    def go(start):
        if len(path) == k:
            result.append(path[:])
            return
        for x in range(start, n + 1):
            path.append(x)
            go(x + 1)
            path.pop()

    go(1)
    return result

print(combine(4, 2))
print(len(combine(10, 3)), len(combine(20, 10)))
```
```text
[[1, 2], [1, 3], [1, 4], [2, 3], [2, 4], [3, 4]]
120 184756
```

Because each next choice is bigger than the last (`go(x + 1)`), every combination is generated once in sorted order. There is no check for duplicates and no "used" array.

### Pruning the tail

Suppose `n = 10`, `k = 3`, and the path is `[9]`. We need two more numbers bigger than 9, but only `10` is left. This branch is **doomed**, but the code above still visits it. We can stop the loop earlier: with `need = k - len(path)` slots still
to fill, the first slot can be at most `n - need + 1`.

```python
def combine_counted(n, k, prune):
    nodes = 0
    found = 0
    path = []

    def go(start):
        nonlocal nodes, found
        nodes += 1
        if len(path) == k:
            found += 1
            return
        need = k - len(path)
        last = n - need + 1 if prune else n
        for x in range(start, last + 1):
            path.append(x)
            go(x + 1)
            path.pop()

    go(1)
    return found, nodes

for n, k in ((10, 3), (20, 5), (25, 10)):
    f1, plain = combine_counted(n, k, False)
    f2, pruned = combine_counted(n, k, True)
    print(f"n={n:>2} k={k:>2}  answers={f1:>8}  nodes plain={plain:>8}  nodes pruned={pruned:>8}")
```
```text
n=10 k= 3  answers=     120  nodes plain=     176  nodes pruned=     165
n=20 k= 5  answers=   15504  nodes plain=   21700  nodes pruned=   20349
n=25 k=10  answers= 3268760  nodes plain= 7119516  nodes pruned= 5311735
```

Both versions find the same answers. The pruned one visits fewer nodes because it never walks into a doomed branch. The saving is small when `k` is small (176 against 165 nodes) and bigger when `k` is large (about a quarter fewer nodes in the last line).
Pruning cannot make the *number of answers* smaller, only the time wasted on dead ends. Remember this picture: **pruning saves the dead branches, not the answers.**

### Combination sum: reuse allowed

Given positive numbers `candidates` and a `target`, find all combinations that add up to `target`. Each candidate may be used any number of times. For example `[2, 3, 6, 7]` and target `7` gives `[2, 2, 3]` and `[7]`.

Think of each step as "pick the next candidate". After you pick `candidates[i]`, you may pick the same one again, so the next call starts at `i` (not `i + 1`). To keep each combination in sorted order (no repeated sets like `[2,3,2]`), you never go back to an earlier index.

```python
def combination_sum(candidates, target):
    candidates = sorted(candidates)
    result, path = [], []

    def go(start, remaining):
        if remaining == 0:
            result.append(path[:])
            return
        for i in range(start, len(candidates)):
            c = candidates[i]
            if c > remaining:
                break                  # prune: sorted, so all later ones are too big
            path.append(c)
            go(i, remaining - c)       # i, not i + 1: the same number may be reused
            path.pop()

    go(0, target)
    return result

print(combination_sum([2, 3, 6, 7], 7))
print(combination_sum([2, 3, 5], 8))
print(combination_sum([4, 6], 3))
```
```text
[[2, 2, 3], [7]]
[[2, 2, 2, 2], [2, 3, 3], [3, 5]]
[]
```

Three things to notice. First, the base case is `remaining == 0`. We never need a case for "remaining below 0" because the `break` stops us from ever subtracting too much. Second, sorting the candidates makes the `break` valid (the rest are even
bigger). Third, the depth is at most `target / min(candidates)`, which is why positive numbers matter: with a zero or a negative candidate the recursion would never end.

### Combination sum II: each number once, with duplicates in the input

Now the input may contain repeated numbers (`[10, 1, 2, 7, 6, 1, 5]`), and each *position* may be used at most once. Combine two ideas: `go(i + 1, ...)` for "once" and the "skip a duplicate sibling" rule from section 6.

```python
def combination_sum2(candidates, target):
    candidates = sorted(candidates)
    result, path = [], []

    def go(start, remaining):
        if remaining == 0:
            result.append(path[:])
            return
        for i in range(start, len(candidates)):
            c = candidates[i]
            if c > remaining:
                break
            if i > start and c == candidates[i - 1]:
                continue                   # duplicate sibling
            path.append(c)
            go(i + 1, remaining - c)       # i + 1: each position once
            path.pop()

    go(0, target)
    return result

print(combination_sum2([10, 1, 2, 7, 6, 1, 5], 8))
```
```text
[[1, 1, 6], [1, 2, 5], [1, 7], [2, 6]]
```

`[1, 1, 6]` is present (two different positions with the value 1), but `[1, 7]` appears only once even though there are two `1`s. Compare with the standard library to check yourself:

```python
import itertools

def combine(n, k):
    result, path = [], []
    def go(start):
        if len(path) == k:
            result.append(path[:]); return
        for x in range(start, n + 1):
            path.append(x); go(x + 1); path.pop()
    go(1)
    return result

mine = combine(6, 3)
std = [list(c) for c in itertools.combinations(range(1, 7), 3)]
print(mine == std)
```
```text
True
```

`itertools.combinations` gives the same list in the same order. In real code, use it. In an interview, or when you need pruning, write the recursion yourself.

## 8. Permutations

A **permutation** is an arrangement: the order matters. The 6 permutations of `[1, 2, 3]` are 123, 132, 213, 231, 312, 321. For `n` distinct items there are `n! = n * (n-1) * ... * 1` of them: `n` choices for the first place,
`n - 1` for the second, and so on.

Now we cannot use a `start` index (any unused item may go next), so we remember which items are already in the path with a `used` list.

```python
def permutations(nums):
    result, path = [], []
    used = [False] * len(nums)

    def go():
        if len(path) == len(nums):
            result.append(path[:])
            return
        for i in range(len(nums)):
            if used[i]:
                continue
            used[i] = True            # choose
            path.append(nums[i])
            go()                      # explore
            path.pop()                # un-choose
            used[i] = False

    go()
    return result

for p in permutations([1, 2, 3]):
    print(p)
```
```text
[1, 2, 3]
[1, 3, 2]
[2, 1, 3]
[2, 3, 1]
[3, 1, 2]
[3, 2, 1]
```

The state has two parts now, the `path` and the `used` flags, and **both** must be undone. Forgetting `used[i] = False` is a typical bug: the items stay "used" and later branches find nothing to pick.

### How fast does it grow?

```python
import math

for n in range(1, 13):
    print(f"{n:>2}! = {math.factorial(n):>12,}")
```
```text
 1! =            1
 2! =            2
 3! =            6
 4! =           24
 5! =          120
 6! =          720
 7! =        5,040
 8! =       40,320
 9! =      362,880
10! =    3,628,800
11! =   39,916,800
12! =  479,001,600
```

Ten items give 3.6 million permutations: fine. Twelve give 479 million: too slow in Python. Twenty give more than `2 * 10^18`: impossible. If a problem says `n <= 8` or `n <= 10`, it is hinting at permutations. If it says `n <= 20`, think of subsets (`2^20`), not permutations.

### The swap method: no `used` array

Another way: fix the first position, try each item there by swapping it in, then permute the rest. After the recursive call, swap back.

```python
def permutations_swap(nums):
    nums = list(nums)
    result = []

    def go(i):
        if i == len(nums):
            result.append(nums[:])
            return
        for j in range(i, len(nums)):
            nums[i], nums[j] = nums[j], nums[i]    # choose nums[j] for position i
            go(i + 1)
            nums[i], nums[j] = nums[j], nums[i]    # un-choose: swap back

    go(0)
    return result

print(permutations_swap([1, 2, 3]))
```
```text
[[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 2, 1], [3, 1, 2]]
```

The same six permutations, but in a different order (the order depends on the swaps). This version needs no extra memory for flags, but the output order is not sorted. If the problem wants lexicographic order, use the `used` version on sorted input.

### Permutations with duplicates

For `[1, 1, 2]` there are only 3 different arrangements (112, 121, 211), not 6. Again: sort, then skip a value that equals the previous one, **but only when the previous equal value is not currently in the path**.

```python
def permutations_unique(nums):
    nums = sorted(nums)
    result, path = [], []
    used = [False] * len(nums)

    def go():
        if len(path) == len(nums):
            result.append(path[:])
            return
        for i in range(len(nums)):
            if used[i]:
                continue
            if i > 0 and nums[i] == nums[i - 1] and not used[i - 1]:
                continue                  # same value, and the twin is free: skip
            used[i] = True
            path.append(nums[i])
            go()
            path.pop()
            used[i] = False

    go()
    return result

print(permutations_unique([1, 1, 2]))
print(len(permutations_unique([1, 1, 2, 2, 3])))
```
```text
[[1, 1, 2], [1, 2, 1], [2, 1, 1]]
30
```

Why `not used[i - 1]`? If the twin `nums[i - 1]` is *free* (not in the path), then choosing `nums[i]` now means we skip the twin and use the second copy first. That is the same arrangement we get when we pick the twin first,
so we skip it. If the twin is already in the path (used), then we are building a different position and `nums[i]` is the second copy: allowed. The effect: equal values are always taken in the left-to-right order, so each arrangement appears once.

You can count the answer with a formula: `n! / (a! * b! * ...)`, where `a`, `b` are the counts of each repeated value. For `[1, 1, 2, 2, 3]` that is `120 / (2 * 2) = 30`.

### Permutations of size k

Sometimes you need only `k` of the `n` items in order ("how many 3-digit codes from 5 distinct digits?"). Stop when the path has length `k`. There are `n! / (n - k)!` of them.

```python
def k_permutations(nums, k):
    result, path = [], []
    used = [False] * len(nums)

    def go():
        if len(path) == k:
            result.append(path[:])
            return
        for i in range(len(nums)):
            if not used[i]:
                used[i] = True; path.append(nums[i])
                go()
                path.pop(); used[i] = False

    go()
    return result

print(len(k_permutations([1, 2, 3, 4, 5], 3)))
print(k_permutations([1, 2, 3], 2))
```
```text
60
[[1, 2], [1, 3], [2, 1], [2, 3], [3, 1], [3, 2]]
```

**Predict the output 4.** The code below uses a `used` list but forgets one line. What does it print?

```python
def broken_permutations(nums):
    result, path = [], []
    used = [False] * len(nums)

    def go():
        if len(path) == len(nums):
            result.append(path[:])
            return
        for i in range(len(nums)):
            if used[i]:
                continue
            used[i] = True
            path.append(nums[i])
            go()
            path.pop()           # forgot: used[i] = False

    go()
    return result

print(broken_permutations([1, 2, 3]))
```

<details><summary>Answer</summary>

```text
[[1, 2, 3]]
```

Only one permutation, `[1, 2, 3]`. After the first full path is found, the loop goes back up, but the items stay marked as used. Every later branch finds no free item, so it never reaches full length and records nothing. When the state has several parts,
write the "undo" lines right under the "do" lines so you cannot forget a pair.

</details>

**Try it 4.** Use `itertools.permutations` to check that `permutations_swap` and `permutations` produce the same *set* of arrangements for `[1, 2, 3, 4]`. Why compare sorted lists, not the lists directly?

<details><summary>Answer</summary>

```python
import itertools

def permutations_swap(nums):
    nums = list(nums)
    result = []
    def go(i):
        if i == len(nums):
            result.append(nums[:]); return
        for j in range(i, len(nums)):
            nums[i], nums[j] = nums[j], nums[i]
            go(i + 1)
            nums[i], nums[j] = nums[j], nums[i]
    go(0)
    return result

mine = permutations_swap([1, 2, 3, 4])
std = [list(p) for p in itertools.permutations([1, 2, 3, 4])]
print(mine == std)
print(sorted(mine) == sorted(std))
```
```text
False
True
```

The swap method creates the arrangements in a different order, so a direct comparison is `False`. Both lists hold the same 24 arrangements, so the sorted comparison is `True`. When the order of the output is not part of the problem, compare after sorting.

</details>

## 9. Pruning: cutting branches early

A backtracking search without pruning is just brute force: it builds *every* possible path and checks it at the end. Pruning means **checking as early as possible** and abandoning a branch the moment you know it cannot lead to a valid answer. The earlier you cut,
the more of the tree disappears with it: cutting a branch at depth 2 removes everything below it, which may be millions of nodes.

There are four common kinds of pruning:

1. **Constraint check (feasibility).** The partial solution already breaks a rule. (Two queens attack each other; the sum is already above the target; a digit appears twice in a row.)
2. **Bound check.** Even the best possible completion cannot reach the goal. (The numbers left add up to less than we still need; we need 5 more items but only 3 positions remain.)
3. **Order and `break`.** If the candidates are sorted and one is too big, all later ones are too big as well: stop the loop, do not just skip one.
4. **Duplicates and symmetry.** Skip branches that would produce an answer you already have (section 6), or that is a mirror of one you already explored (section 11).

The golden rule: **a prune must never remove a real answer.** A wrong prune is worse than no prune, because the program becomes fast and wrong. Always compare the pruned version with a slow, obviously-correct version on small inputs.

### An experiment: count the subsets with a given sum

We have the numbers 1 to 18 (all positive) and want to count the subsets that add up to 40. Version A decides include/exclude for each number and checks the sum only at the end. Version B stops as soon as it can:

- if the sum so far **equals** the target, the answer is complete: every number we have not decided yet must be left out (adding any positive number would overshoot), so that is exactly one subset;
- if the sum is already **above** the target, stop (feasibility);
- if the sum plus **all** the numbers still undecided is **below** the target, stop (bound).

```python
def count_plain(nums, target):
    nodes = 0

    def go(i, total):
        nonlocal nodes
        nodes += 1
        if i == len(nums):
            return 1 if total == target else 0
        return go(i + 1, total + nums[i]) + go(i + 1, total)

    return go(0, 0), nodes


def count_pruned(nums, target):
    nodes = 0
    # suffix[i] = sum of nums[i:], the most we can still add
    suffix = [0] * (len(nums) + 1)
    for i in range(len(nums) - 1, -1, -1):
        suffix[i] = suffix[i + 1] + nums[i]

    def go(i, total):
        nonlocal nodes
        nodes += 1
        if total == target:
            return 1                         # the rest must all be left out
        if i == len(nums) or total > target:
            return 0                         # feasibility
        if total + suffix[i] < target:
            return 0                         # bound: even taking everything is not enough
        return go(i + 1, total + nums[i]) + go(i + 1, total)

    return go(0, 0), nodes


nums = list(range(1, 19))
print("plain :", count_plain(nums, 40))
print("pruned:", count_pruned(nums, 40))
```
```text
plain : (670, 524287)
pruned: (670, 50821)
```

Each line shows `(number of subsets, number of calls)`. The two versions find the **same number of subsets**, but the pruned one needs far fewer calls. That is the whole point.

Now the check that matters most. Compare both with the obviously-correct brute force on many small inputs. If you ever change a prune, run a check like this before you trust it.

```python
from itertools import combinations

def brute(nums, target):
    return sum(1 for k in range(len(nums) + 1)
                 for c in combinations(nums, k) if sum(c) == target)

ok = True
for n in range(1, 11):
    nums = list(range(1, n + 1))
    for target in range(0, sum(nums) + 3):
        a = brute(nums, target)
        if count_plain(nums, target)[0] != a or count_pruned(nums, target)[0] != a:
            ok = False
            print("MISMATCH", n, target)
print("all agree:", ok)
```
```text
all agree: True
```

The target `0` is a good test: the empty subset sums to 0, so the answer is 1. (It works because `total == target` is checked before anything else.) Remember: **the prune is an optimisation, never a change of the answer.**

### Pruning by sorting

If the candidates are sorted, one failure lets you stop the whole loop. You have already seen this in `combination_sum`: `if c > remaining: break`. Compare it with `continue`, which would also be correct but would keep checking larger values one by one.

```python
def count_nodes_sum(cands, target, use_break):
    cands = sorted(cands)
    nodes = 0

    def go(start, remaining):
        nonlocal nodes
        nodes += 1
        if remaining == 0:
            return
        for i in range(start, len(cands)):
            if cands[i] > remaining:
                if use_break:
                    break
                continue
            go(i, remaining - cands[i])

    go(0, target)
    return nodes

cands = [2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37, 41, 43, 47]
print("with break   :", count_nodes_sum(cands, 40, True))
print("with continue:", count_nodes_sum(cands, 40, False))
```
```text
with break   : 2699
with continue: 2699
```

The number of recursive calls is the same, since the extra values were never entered. The saving is in the *loop work* inside each call, not in the calls. This is a small gain, but it costs nothing. The big gains come from stopping recursive calls.

### The order of the choices matters

Pruning works best when failures come early. Two ideas:

- **Try the most constrained choice first.** In Sudoku, fill the cell with the fewest possible digits first (section 12).
- **Try the likely-to-succeed choice first** if you only need *one* answer (stop at the first success).

### Stop at the first answer

Sometimes the question is "is there any solution?" or "give me one solution". Then the recursive function should *return a signal* (`True`/`False`), and every caller should stop as soon as one call says `True`.

```python
def has_subset_sum(nums, target):
    def go(i, remaining):
        if remaining == 0:
            return True
        if i == len(nums) or remaining < 0:
            return False
        # take nums[i], or skip it; `or` stops at the first True
        return go(i + 1, remaining - nums[i]) or go(i + 1, remaining)

    return go(0, target)

print(has_subset_sum([3, 34, 4, 12, 5, 2], 9))
print(has_subset_sum([3, 34, 4, 12, 5, 2], 30))
```
```text
True
False
```

The pattern is `if go(...): return True` inside a loop, or `go(...) or go(...)` for two choices. The "undo" still happens if you return `False`, but when you return `True` you often do not care any more: the answer is already complete. If you need to **keep** the state
of the winning path (for example the board), do not undo it after a success (section 12 shows this).

**Predict the output 5.** How many times is `go` called?

```python
calls = 0

def go(i, remaining, nums):
    global calls
    calls += 1
    if remaining == 0:
        return True
    if i == len(nums) or remaining < 0:
        return False
    return go(i + 1, remaining - nums[i], nums) or go(i + 1, remaining, nums)

print(go(0, 5, [2, 3, 4]))
print(calls)
```

<details><summary>Answer</summary>

```text
True
3
```

Follow the first branches: `go(0,5)` takes 2 -> `go(1,3)` takes 3 -> `go(2,0)`, which is `True` at once. That is three calls. The `or` operators stop immediately, so nothing else runs. The answer is found with 3 calls, a tiny part of the full tree. This is the benefit of early exit.

</details>

## 10. Backtracking on a grid: word search

Many puzzles live on a grid: a maze, a board of letters, an island map. A grid search is backtracking where the "choices" are the four (or eight) neighbouring cells. The new difficulty is the **visited** state: a path must not use the same cell twice.

### Word search

Given a grid of letters and a word, decide if the word can be spelled by walking from cell to neighbouring cell (up, down, left, right), using no cell twice.

```text
A B C E
S F C S
A D E E
```

"ABCCED" can be spelled: A at (0,0), B at (0,1), C at (0,2), the second C at (1,2) just below it, E at (2,2), and D at (2,1). "ABCB" cannot: after A, B, C there is no second B next to the C.

The search starts from every cell, and at each step tries the four neighbours that match the next letter. To mark a cell as used, replace its letter by `"#"` while we are inside it, and put the letter back when we leave.

```python
def exist(board, word):
    rows, cols = len(board), len(board[0])

    def go(r, c, k):
        if k == len(word):
            return True                                  # every letter matched
        if not (0 <= r < rows and 0 <= c < cols) or board[r][c] != word[k]:
            return False                                 # off the grid, or wrong letter
        saved = board[r][c]
        board[r][c] = "#"                                # choose: mark used
        found = (go(r + 1, c, k + 1) or go(r - 1, c, k + 1) or
                 go(r, c + 1, k + 1) or go(r, c - 1, k + 1))
        board[r][c] = saved                              # un-choose: restore
        return found

    return any(go(r, c, 0) for r in range(rows) for c in range(cols))

board = [list("ABCE"), list("SFCS"), list("ADEE")]
for word in ("ABCCED", "SEE", "ABCB"):
    print(word, exist(board, word))
print(board)
```
```text
ABCCED True
SEE True
ABCB False
[['A', 'B', 'C', 'E'], ['S', 'F', 'C', 'S'], ['A', 'D', 'E', 'E']]
```

The last line proves that the board is back to its original state: the `"#"` marks were all removed. This is the same "choose, explore, un-choose", with the grid cell as the thing that is changed and restored.

Why mark with `"#"` instead of a separate `visited` set? It saves memory and is fast. But you must be sure that `"#"` is not a legal letter, and you must restore it. A separate `visited` set (add before, remove after) is equally correct and easier to read when the grid holds numbers.

### What happens if you forget to restore

```python
def exist_broken(board, word):
    rows, cols = len(board), len(board[0])

    def go(r, c, k):
        if k == len(word):
            return True
        if not (0 <= r < rows and 0 <= c < cols) or board[r][c] != word[k]:
            return False
        board[r][c] = "#"                                # marked ...
        return (go(r + 1, c, k + 1) or go(r - 1, c, k + 1) or
                go(r, c + 1, k + 1) or go(r, c - 1, k + 1))   # ... and never restored

    return any(go(r, c, 0) for r in range(rows) for c in range(cols))

for word in ("ABCCED", "SEE", "ABCB"):
    board = [list("ABCE"), list("SFCS"), list("ADEE")]    # fresh board for each word
    print(word, exist_broken(board, word))
```
```text
ABCCED True
SEE True
ABCB False
```

Compare with the correct version: `"SEE"` should be `True` but the broken version gives `False`. The reason: the first attempt starts at an `S`, marks cells, fails, and the marks stay. The next start finds a board full of `#` and cannot succeed. A missing
"un-choose" does not crash. It silently gives wrong answers, which is why it is the hardest backtracking bug to find.

### Pruning in word search

Two cheap prunes make this practical for big boards:

1. **Letter-count check.** If the word needs three `E`s but the board has only two, return `False` immediately, before any search.
2. **Search from the rarer end.** If the last letter of the word is rarer on the board than the first, reverse the word. Fewer starting cells means fewer searches.

```python
from collections import Counter

def exist_pruned(board, word):
    rows, cols = len(board), len(board[0])
    have = Counter(ch for row in board for ch in row)
    need = Counter(word)
    if any(need[ch] > have[ch] for ch in need):
        return False                                   # prune: not enough letters at all
    if have[word[0]] > have[word[-1]]:
        word = word[::-1]                              # start from the rarer end

    def go(r, c, k):
        if k == len(word):
            return True
        if not (0 <= r < rows and 0 <= c < cols) or board[r][c] != word[k]:
            return False
        saved = board[r][c]
        board[r][c] = "#"
        found = (go(r + 1, c, k + 1) or go(r - 1, c, k + 1) or
                 go(r, c + 1, k + 1) or go(r, c - 1, k + 1))
        board[r][c] = saved
        return found

    return any(go(r, c, 0) for r in range(rows) for c in range(cols))

board = [list("ABCE"), list("SFCS"), list("ADEE")]
print(exist_pruned(board, "ABCCED"), exist_pruned(board, "EEEEE"), exist_pruned(board, "SEE"))
```
```text
True False True
```

### Counting paths in a grid

Backtracking on a grid can also count. How many ways can you walk from the top-left cell to the bottom-right cell of an `n x n` grid, moving up, down, left or right, never visiting a cell twice? (These are called self-avoiding walks.)

```python
def count_paths(n):
    visited = [[False] * n for _ in range(n)]

    def go(r, c):
        if r == n - 1 and c == n - 1:
            return 1
        visited[r][c] = True
        total = 0
        for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nr, nc = r + dr, c + dc
            if 0 <= nr < n and 0 <= nc < n and not visited[nr][nc]:
                total += go(nr, nc)
        visited[r][c] = False
        return total

    return go(0, 0)

for n in range(1, 6):
    print(n, count_paths(n))
```
```text
1 1
2 2
3 12
4 184
5 8512
```

There is no formula for this one, and the numbers grow very fast (n = 6 has more than a million, and n = 7 more than 500 million). A search that *must* look at every path has no shortcut. When there is a shortcut (for example, only right and down moves, where the answer is a binomial
number or can be found by dynamic programming), use it. Compare: if you may only go right or down, there are `C(2(n-1), n-1)` paths: 2 for `n = 2`, 6 for `n = 3`, 20 for `n = 4`.

**Try it 5.** In `exist`, we check `k == len(word)` *before* the bounds check. Why does the order matter? What happens with the word `""` (the empty word)?

<details><summary>Answer</summary>

When all the letters are matched (`k == len(word)`), the call is *after* the last letter's cell, and the coordinates `(r, c)` may be off the grid (the neighbour of a cell on the edge). If we checked the grid first, we would return `False` for a successful match. So the "done" test must come first.

For the empty word, `go(0, 0, 0)` immediately has `k == len(word) == 0`, so the answer is `True` on any non-empty board: the empty word can be "spelled" without using any cell.

```python
def exist(board, word):
    rows, cols = len(board), len(board[0])
    def go(r, c, k):
        if k == len(word):
            return True
        if not (0 <= r < rows and 0 <= c < cols) or board[r][c] != word[k]:
            return False
        saved = board[r][c]; board[r][c] = "#"
        found = (go(r+1, c, k+1) or go(r-1, c, k+1) or go(r, c+1, k+1) or go(r, c-1, k+1))
        board[r][c] = saved
        return found
    return any(go(r, c, 0) for r in range(rows) for c in range(cols))

print(exist([list("AB")], ""), exist([list("AB")], "BA"), exist([list("AB")], "ABA"))
```
```text
True True False
```

</details>

## 11. N-Queens

Place `n` queens on an `n x n` chessboard so that no two queens attack each other. A queen attacks along its row, its column, and both diagonals. The puzzle is the textbook example of backtracking with strong pruning.

### Thinking before coding

Eight queens on 64 squares: the number of ways to pick 8 squares at random is huge.

```python
import math
print(math.comb(64, 8))
print(8 ** 8)
```
```text
4426165368
16777216
```

Over four billion ways to pick 8 squares. But we can think a little first. Two queens in the same row attack each other, so every row has **exactly one** queen. Instead of "choose 8 squares", the question becomes "for each row, choose a column", which is `8^8` = 16.7 million
placements. And we can do better: place a queen row by row, and stop as soon as a new queen is attacked. This is "choose, explore, un-choose", where the choice is the **column** of the next row.

### Checking attacks fast: columns and diagonals

How do you know quickly that a square `(r, c)` is safe? You track three things:

- **columns used**: the set of `c` values;
- **diagonals** `\`: all squares on one such diagonal share the same `r - c`;
- **anti-diagonals** `/`: all squares on one such diagonal share the same `r + c`.

Each check is a set lookup, `O(1)`.

```text
r+c (anti-diagonal)        r-c (diagonal)
 0 1 2 3                    0 -1 -2 -3
 1 2 3 4                    1  0 -1 -2
 2 3 4 5                    2  1  0 -1
 3 4 5 6                    3  2  1  0
```

```python
def solve_queens(n):
    solutions = []
    cols_of = []                  # cols_of[r] = column of the queen in row r
    cols, diag, anti = set(), set(), set()

    def go(r):
        if r == n:
            solutions.append(cols_of[:])
            return
        for c in range(n):
            if c in cols or (r - c) in diag or (r + c) in anti:
                continue                                  # prune: this square is attacked
            cols_of.append(c); cols.add(c); diag.add(r - c); anti.add(r + c)      # choose
            go(r + 1)                                                              # explore
            cols_of.pop(); cols.remove(c); diag.remove(r - c); anti.remove(r + c)  # un-choose

    go(0)
    return solutions

for n in range(1, 9):
    print(n, len(solve_queens(n)))
```
```text
1 1
2 0
3 0
4 2
5 10
6 4
7 40
8 92
```

The counts for `n = 1 ... 8` are 1, 0, 0, 2, 10, 4, 40, 92. Two things to notice. For `n = 2` and `n = 3` there is no solution at all (the function returns an empty list, which is a valid answer). And the sequence is not smooth: `n = 6` has fewer solutions than `n = 5`.

### Seeing a solution

```python
def show(solution):
    n = len(solution)
    for c in solution:
        print(" ".join("Q" if j == c else "." for j in range(n)))

sols = solve_queens(6)
print(sols[0])
show(sols[0])
```
```text
[1, 3, 5, 0, 2, 4]
. Q . . . .
. . . Q . .
. . . . . Q
Q . . . . .
. . Q . . .
. . . . Q .
```

Check by eye: no two `Q` in a row (by construction), none in a column, and no two on the same diagonal.

### How much did pruning save?

Count the nodes of the search: calls to `go`. Compare with the "no pruning" version that places a queen in every row and checks only at the end (`n^n` leaves).

```python
def count_nodes(n):
    nodes = 0
    cols, diag, anti = set(), set(), set()

    def go(r):
        nonlocal nodes
        nodes += 1
        if r == n:
            return
        for c in range(n):
            if c in cols or (r - c) in diag or (r + c) in anti:
                continue
            cols.add(c); diag.add(r - c); anti.add(r + c)
            go(r + 1)
            cols.remove(c); diag.remove(r - c); anti.remove(r + c)

    go(0)
    return nodes

for n in (4, 6, 8):
    print(f"n={n}: pruned nodes = {count_nodes(n):>5}, without pruning about {n ** n:>10,} leaves")
```
```text
n=4: pruned nodes =    17, without pruning about        256 leaves
n=6: pruned nodes =   153, without pruning about     46,656 leaves
n=8: pruned nodes =  2057, without pruning about 16,777,216 leaves
```

For 8 queens, about two thousand calls instead of sixteen million leaves. This is what pruning looks like in practice: the tree is still exponential in theory, but a huge part of it never exists.

**Predict the output 6.** How many solutions does `solve_queens(4)` return, and what are they?

<details><summary>Answer</summary>

```python
def solve_queens(n):
    solutions, cols_of = [], []
    cols, diag, anti = set(), set(), set()
    def go(r):
        if r == n:
            solutions.append(cols_of[:]); return
        for c in range(n):
            if c in cols or (r - c) in diag or (r + c) in anti:
                continue
            cols_of.append(c); cols.add(c); diag.add(r - c); anti.add(r + c)
            go(r + 1)
            cols_of.pop(); cols.remove(c); diag.remove(r - c); anti.remove(r + c)
    go(0)
    return solutions

print(solve_queens(4))
```
```text
[[1, 3, 0, 2], [2, 0, 3, 1]]
```

Two solutions, and they are mirror images of each other (reflect the board left to right). Each list is "column of the queen in row 0, row 1, row 2, row 3".

</details>

### A faster way: bit masks

With three integers instead of three sets, each check is one operation on bits. Bit `c` of `cols` says "column `c` is used". For the diagonals, the used bits shift by one position every time we move to the next row.

```python
def count_queens_bits(n):
    full = (1 << n) - 1

    def go(cols, d1, d2):
        if cols == full:
            return 1
        total = 0
        free = full & ~(cols | d1 | d2)         # squares in this row that are not attacked
        while free:
            bit = free & -free                  # lowest free square
            free ^= bit                         # remove it from the list
            total += go(cols | bit, ((d1 | bit) << 1) & full, (d2 | bit) >> 1)
        return total

    return go(0, 0, 0)

print([count_queens_bits(n) for n in range(1, 10)])
```
```text
[1, 0, 0, 2, 10, 4, 40, 92, 352]
```

The same counts, only much faster in practice. You do not need this version in an exam, but it is a good tool for competitions where `n` is 12 to 15. The key facts: `x & -x` isolates the lowest set bit, `x ^= bit` clears it, and shifting `d1` left and `d2` right moves the "attack lines" one row down.

### Using symmetry

Mirror a solution left to right and you get another solution. So, for the first queen, we can search only the left half of the columns and double the count (for odd `n`, the middle column counts once). This halves the work. It is a *symmetry prune*, and a good example of how
knowing the structure of the problem beats clever code.

## 12. Sudoku

A Sudoku board has 9 rows, 9 columns and nine 3x3 boxes. The rule: each row, each column and each box contains the digits 1 to 9 exactly once. Some cells are given, the others are empty (we use `0`). Fill the board.

This is backtracking with *choices that depend on the board*: for an empty cell, the options are the digits that are not already used in the cell's row, column, or box.

### The state: three families of sets

```text
box number = (r // 3) * 3 + (c // 3)

boxes:   0 1 2
         3 4 5
         6 7 8
```

For each row, column and box we keep the set of digits already used. A digit `d` is allowed at `(r, c)` if `d` is in none of the three sets.

### A first solver

We keep a list of the empty cells. At each call we take the first empty cell, try each allowed digit, and recurse on the rest. If the recursion fails, we remove the digit again (un-choose). If it succeeds we **do not** undo anything: we want to
keep the filled board.

```python
class Giveup(Exception):
    pass

def solve_sudoku(grid, smart=False, limit=10**9):
    """Solve in place. Return (solved, calls). `smart` = pick the most constrained cell."""
    rows = [set() for _ in range(9)]
    cols = [set() for _ in range(9)]
    boxes = [set() for _ in range(9)]
    empties = []
    for r in range(9):
        for c in range(9):
            d = grid[r][c]
            if d:
                rows[r].add(d); cols[c].add(d); boxes[(r // 3) * 3 + c // 3].add(d)
            else:
                empties.append((r, c))
    calls = 0

    def options(r, c):
        used = rows[r] | cols[c] | boxes[(r // 3) * 3 + c // 3]
        return [d for d in range(1, 10) if d not in used]

    def go(todo):
        nonlocal calls
        calls += 1
        if calls > limit:
            raise Giveup
        if not todo:
            return True
        if smart:
            cell = min(todo, key=lambda rc: len(options(*rc)))
        else:
            cell = todo[0]
        r, c = cell
        b = (r // 3) * 3 + c // 3
        rest = [e for e in todo if e != cell]
        for d in options(r, c):
            grid[r][c] = d
            rows[r].add(d); cols[c].add(d); boxes[b].add(d)           # choose
            if go(rest):
                return True                                           # keep the board
            grid[r][c] = 0
            rows[r].remove(d); cols[c].remove(d); boxes[b].remove(d)  # un-choose
        return False

    try:
        return go(empties), calls
    except Giveup:
        return None, calls


def parse(text):
    return [[int(ch) for ch in text[r * 9:(r + 1) * 9]] for r in range(9)]

def show(grid):
    for r, row in enumerate(grid):
        if r % 3 == 0 and r:
            print("------+-------+------")
        groups = [" ".join(str(d or ".") for d in row[i:i + 3]) for i in (0, 3, 6)]
        print(" | ".join(groups))

easy = ("530070000600195000098000060800060003400803001"
        "700020006060000280000419005000080079")
grid = parse(easy)
solved, calls = solve_sudoku(grid)
print(solved, calls)
show(grid)
```
```text
True 4209
5 3 4 | 6 7 8 | 9 1 2
6 7 2 | 1 9 5 | 3 4 8
1 9 8 | 3 4 2 | 5 6 7
------+-------+------
8 5 9 | 7 6 1 | 4 2 3
4 2 6 | 8 5 3 | 7 9 1
7 1 3 | 9 2 4 | 8 5 6
------+-------+------
9 6 1 | 5 3 7 | 2 8 4
2 8 7 | 4 1 9 | 6 3 5
3 4 5 | 2 8 6 | 1 7 9
```

The first line is `True` and the number of calls, then the finished board (`show` is only a print helper). Every row, column and box holds the digits 1 to 9 once; you can check a few by eye.

### Why "pick the most constrained cell" is so much better

The first solver takes the cells in reading order. If the first cell has 5 options and only one of them works, the search may spend a long time inside a doomed branch before it reaches the cell that would show the mistake. The *smart* order asks first: "which empty cell has the fewest
options right now?" A cell with exactly one option is forced. A cell with zero options means the current branch is dead, and we find out **immediately**. This idea (called the "minimum remaining values" rule) makes the tree extremely narrow.

```python
hard = ("800000000003600000070090200050007000000045700"
        "000100030001000068008500010090000400")

for name, puzzle in (("easy", easy), ("hard", hard)):
    for smart in (False, True):
        grid = parse(puzzle)
        solved, calls = solve_sudoku(grid, smart=smart, limit=300_000)
        label = "smart (fewest options)" if smart else "plain (reading order)"
        result = "solved" if solved else "GAVE UP"
        print(f"{name:5} {label:24} {result:8} calls={calls}")
```
```text
easy  plain (reading order)    solved   calls=4209
easy  smart (fewest options)   solved   calls=52
hard  plain (reading order)    solved   calls=49559
hard  smart (fewest options)   solved   calls=10102
```

Read the last column. On the easy puzzle the smart order needs about 80 times fewer calls (52 against 4,209). On the "hard" puzzle (famous for being hard for humans) it is still about five times fewer (10,102 against 49,559). The lesson is the same as in N-Queens: the *order of the decisions* can matter more than any micro-optimisation of the code.

**Try it 6.** Without running the code, say what `options(r, c)` returns for a cell where the row contains `{1, 2, 3}`, the column `{3, 4}` and the box `{5, 6, 7}`. How many options?

<details><summary>Answer</summary>

The used digits are the union `{1, 2, 3, 4, 5, 6, 7}`. So the options are `[8, 9]`: two options.

```python
used = {1, 2, 3} | {3, 4} | {5, 6, 7}
print([d for d in range(1, 10) if d not in used])
```
```text
[8, 9]
```

Note that `3` appears in both the row and the column set: the union counts it once. If the union has all 9 digits, `options` is empty, and the branch is dead.

</details>

## 13. More classics, one idea each

You now own the template. This section shows how the same three questions (what is complete, what are the options, what is not allowed) produce three well-known problems.

### Generate parentheses

Produce all strings of `n` pairs of well-formed parentheses, such as `((()))`, `(()())`, `()()()`. A string is well formed if every prefix has at least as many `(` as `)`, and the totals are equal.

- Options at each step: add `(` or add `)`.
- Not allowed: more than `n` open brackets, or a `)` when no `(` is waiting to be closed (`closed >= opened`).
- Complete: length `2n`.

Notice that the prune is the *whole* rule. We never build an invalid prefix, so no check is needed at the end.

```python
def generate_parentheses(n):
    result, path = [], []

    def go(opened, closed):
        if len(path) == 2 * n:
            result.append("".join(path))
            return
        if opened < n:
            path.append("(")
            go(opened + 1, closed)
            path.pop()
        if closed < opened:
            path.append(")")
            go(opened, closed + 1)
            path.pop()

    go(0, 0)
    return result

print(generate_parentheses(3))
print([len(generate_parentheses(n)) for n in range(1, 8)])
```
```text
['((()))', '(()())', '(())()', '()(())', '()()()']
[1, 2, 5, 14, 42, 132, 429]
```

The counts 1, 2, 5, 14, 42, 132, 429 are the **Catalan numbers**. They appear in many places: binary trees with `n` nodes, ways to triangulate a polygon, and valid bracket strings. Without the prune you would visit `2^(2n)` strings and keep very few of them.

### Letter combinations of a phone number

On an old phone keypad, `2` is `abc`, `3` is `def`, and so on. Given the digits `"23"`, list all the letter strings they could mean. At each digit the options are the letters of that digit; nothing is forbidden; the answer is complete when every digit has a letter.

```python
PHONE = {"2": "abc", "3": "def", "4": "ghi", "5": "jkl",
         "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"}

def letter_combinations(digits):
    if not digits:
        return []
    result, path = [], []

    def go(i):
        if i == len(digits):
            result.append("".join(path))
            return
        for ch in PHONE[digits[i]]:
            path.append(ch)
            go(i + 1)
            path.pop()

    go(0)
    return result

print(letter_combinations("23"))
print(len(letter_combinations("2345")), 3 * 3 * 3 * 3)
```
```text
['ad', 'ae', 'af', 'bd', 'be', 'bf', 'cd', 'ce', 'cf']
81 81
```

The number of answers is the product of the sizes of the choices. This is the same job as `itertools.product`, written by hand so that you can add rules to it later (for example "only words found in a dictionary").

### Palindrome partitioning

Cut a string into pieces so that every piece is a palindrome. For `"aab"`: `["a", "a", "b"]` and `["aa", "b"]`. This is the *"how long is the next piece"* view of subsets: the loop chooses the end of the next piece, and a piece is allowed only if it is a palindrome.

```python
def palindrome_partitions(s):
    result, path = [], []

    def go(start):
        if start == len(s):
            result.append(path[:])
            return
        for end in range(start + 1, len(s) + 1):
            piece = s[start:end]
            if piece == piece[::-1]:           # prune: only palindromic pieces
                path.append(piece)
                go(end)
                path.pop()

    go(0)
    return result

print(palindrome_partitions("aab"))
print([len(palindrome_partitions("a" * n)) for n in range(1, 9)])
```
```text
[['a', 'a', 'b'], ['aa', 'b']]
[1, 2, 4, 8, 16, 32, 64, 128]
```

For a string of `n` equal letters every cut is allowed, and there are `n - 1` places where you may cut or not, so the count is `2^(n-1)`: 1, 2, 4, 8, ... The prune matters in other strings, where most pieces are not palindromes and whole branches vanish.

**Predict the output 7.** What does this print?

```python
def go(i, path, out):
    if i == 3:
        out.append("".join(path))
        return
    for ch in ("x", "y"):
        if ch == "y" and path and path[-1] == "y":
            continue
        path.append(ch)
        go(i + 1, path, out)
        path.pop()

out = []
go(0, [], out)
print(out)
```

<details><summary>Answer</summary>

```text
['xxx', 'xxy', 'xyx', 'yxx', 'yxy']
```

This builds strings of length 3 over `x` and `y` in which no two `y`s are next to each other. The rule `ch == "y" and path[-1] == "y"` is a prune: the branch `yy...` is never created. Without it you would get all 8 strings; with it, 5. (Counting
such strings gives the Fibonacci numbers: 2, 3, 5, 8, ...)

</details>

## 14. How expensive is backtracking?

Backtracking is exponential in the worst case. You must be able to say *how* exponential, so you can tell before you press "run" whether a program will finish.

### Counting nodes

Total cost = (number of nodes in the tree) x (work per node). Let us measure the node counts for the three basic generators, by counting the calls.

```python
import math

def nodes_subsets(n):
    count = 0
    def go(start):
        nonlocal count
        count += 1
        for i in range(start, n):
            go(i + 1)
    go(0)
    return count

def nodes_permutations(n):
    count = 0
    used = [False] * n
    def go(depth):
        nonlocal count
        count += 1
        for i in range(n):
            if not used[i]:
                used[i] = True
                go(depth + 1)
                used[i] = False
    go(0)
    return count

for n in range(1, 9):
    exact = sum(math.factorial(n) // math.factorial(n - k) for k in range(n + 1))
    print(f"n={n}  subsets nodes={nodes_subsets(n):>4} (2^n={2 ** n:>4})   "
          f"permutation nodes={nodes_permutations(n):>6} (formula={exact:>6})")
```
```text
n=1  subsets nodes=   2 (2^n=   2)   permutation nodes=     2 (formula=     2)
n=2  subsets nodes=   4 (2^n=   4)   permutation nodes=     5 (formula=     5)
n=3  subsets nodes=   8 (2^n=   8)   permutation nodes=    16 (formula=    16)
n=4  subsets nodes=  16 (2^n=  16)   permutation nodes=    65 (formula=    65)
n=5  subsets nodes=  32 (2^n=  32)   permutation nodes=   326 (formula=   326)
n=6  subsets nodes=  64 (2^n=  64)   permutation nodes=  1957 (formula=  1957)
n=7  subsets nodes= 128 (2^n= 128)   permutation nodes= 13700 (formula= 13700)
n=8  subsets nodes= 256 (2^n= 256)   permutation nodes=109601 (formula=109601)
```

Subsets have exactly `2^n` nodes. Permutations have `n!/(n-0)! + n!/(n-1)! + ... + n!/0!` nodes, which is about `e * n!` (2.72 times the number of leaves). The last level holds most of the nodes, so we say "about `n!`".

### The rule of thumb

The cost of a backtracking solution is about (number of **answers or leaves**) x (cost to copy or check one answer), plus the dead branches you did not prune. For the basic generators:

| Problem | Number of answers | Typical time | Reasonable `n` in Python |
|---|---|---|---|
| Subsets | `2^n` | `O(n * 2^n)` | up to about 20 |
| Combinations `C(n, k)` | `n! / (k! (n-k)!)` | `O(k * C(n, k))` | depends on `k`; check `C(n, k)` first |
| Permutations | `n!` | `O(n * n!)` | up to about 9 or 10 |
| N-Queens (count) | 92 for `n = 8` | much less than `n!` thanks to pruning | up to about 10 or 11 with sets, 14 with bit masks |
| Sudoku | one answer | depends on the order of the cells | a normal puzzle is instant |
| Parentheses | Catalan(`n`) | `O(n * Catalan(n))` | up to about 12 |

> Machine note: Python runs very roughly a few million simple operations per second. So a search of ten million nodes takes seconds, and a search of a billion nodes takes many minutes. Use these numbers to decide *before* you run; the exact speed depends on your computer.

### Space

The depth of the recursion is the number of decisions, usually `n`. So the extra space is `O(n)` (the call stack, the path, the `used` flags). If you **store** all the answers, the space is the size of the output, which can be huge. If the problem only needs a count or the first answer, do not
store the rest.

**Try it 7.** A problem says: "n <= 12. List every ordering of the n tasks." Is this feasible? And "n <= 25, list every subset of the tasks whose total time is at most T"?

<details><summary>Answer</summary>

```python
import math
print(math.factorial(12))
print(2 ** 25)
```
```text
479001600
33554432
```

`12!` is 479 million orderings: far too many to list in Python, so either the problem intends a different approach (a counting formula, dynamic programming over subsets) or the real limit is smaller. `2^25` is about 33 million subsets: heavy but possible in a few seconds
only with strong pruning (stop as soon as the total time passes T). Always compute the size of the output first.

</details>

## 15. Recursion without recursion: explicit stacks and generators

### Why avoid deep recursion?

Python's recursion limit (usually 1000) protects the machine, but it also means that a recursive function over a long list or a deep tree can crash even when the algorithm is correct. There are two cures: raise the limit with `sys.setrecursionlimit` (risky: a very deep
recursion can crash the whole interpreter), or use your own stack.

### An explicit stack

Every recursion can be turned into a loop with a `list` used as a stack. Each stack entry carries the state that the call would have held. Because every entry carries its own copy of the state, there is nothing to "undo".

```python
def subsets_iterative(nums):
    result = []
    stack = [(0, [])]                         # (start, path)
    while stack:
        start, path = stack.pop()
        result.append(path)
        for i in range(len(nums) - 1, start - 1, -1):
            stack.append((i + 1, path + [nums[i]]))
    return result

def subsets_recursive(nums):
    result, path = [], []
    def go(start):
        result.append(path[:])
        for i in range(start, len(nums)):
            path.append(nums[i]); go(i + 1); path.pop()
    go(0)
    return result

print(subsets_iterative([1, 2, 3]))
print(subsets_iterative([1, 2, 3]) == subsets_recursive([1, 2, 3]))
```
```text
[[], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3]]
True
```

We push the children in *reverse* order, so that the first child is popped first, and the output order equals the recursive one. The cost: `path + [nums[i]]` copies the path, so each push is `O(n)`, where the recursive version does `O(1)` work with
`append`/`pop`. The iterative form is the right tool when the depth is too big; for backtracking, which is usually shallow, the recursive form is simpler and faster.

A simple loop is even better when the recursion is a chain (one call per level), like `factorial` or `total`:

```python
def factorial_loop(n):
    result = 1
    for k in range(2, n + 1):
        result *= k
    return result

print(factorial_loop(10))
print(factorial_loop(3000).bit_length(), "bits")      # a 3000-deep recursion would have crashed
```
```text
3628800
30332 bits
```

### Generators: recursion that hands out answers one at a time

You learned generators in core.10. A recursive generator is perfect for backtracking, because the caller can take only as many answers as it wants, and the rest are never computed. `yield from` passes the answers of the inner call outwards.

```python
import itertools

def permutations_gen(items):
    path, used = [], [False] * len(items)

    def go():
        if len(path) == len(items):
            yield path[:]
            return
        for i in range(len(items)):
            if not used[i]:
                used[i] = True
                path.append(items[i])
                yield from go()
                path.pop()
                used[i] = False

    yield from go()

# 12 items have 479,001,600 permutations. We only take the first 3.
first3 = list(itertools.islice(permutations_gen(range(1, 13)), 3))
print(first3)
```
```text
[[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12], [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 11], [1, 2, 3, 4, 5, 6, 7, 8, 9, 11, 10, 12]]
```

The result appeared at once, although a list of all arrangements would not fit in memory. This is the right shape for "find one solution", "find the first `k`", or "keep going until a test passes".

Another use: **search for the first valid answer and stop**, with `next(...)`:

```python
def first_with_sum(items, target):
    for p in permutations_gen(items):
        if p[0] + p[1] == target:
            return p
    return None

print(first_with_sum(range(1, 9), 15))
```
```text
[7, 8, 1, 2, 3, 4, 5, 6]
```

Because the generator is lazy, the loop stops as soon as it finds the first match, and the rest of the tree is not visited. One thing to watch: the generator yields `path[:]`, a *copy*. If it yielded `path` itself, the consumer would see the list change while it was holding it.

## 16. Debugging recursive code

Recursive bugs feel hard because the failure happens deep in a tree you cannot see. Use a method:

1. **Shrink the input** until the bug is visible on 2 or 3 items. A bug that exists at size 20 almost always exists at size 3.
2. **Draw the tree** for that small input, and compare with what the program does. The `@trace` decorator from section 3 prints the calls.
3. **Check the base case first.** Is it correct for the smallest inputs? Does every path of the recursion reach a base case?
4. **Compare with a slow, obviously-correct version** (a brute force, `itertools`, or a hand-written list of answers). Compare the *set* of answers, then the count.
5. **Print the state at entry and exit** of the function (path, used, remaining). In backtracking, the state at exit should equal the state at entry. If it does not, you forgot an un-choose.

### The state-check trick

This wrapper asserts that a function leaves a shared structure as it found it. It is useful in tests for any backtracking function that uses a shared `path`.

```python
def check_restored(path_list, func):
    before = list(path_list)
    func()
    assert path_list == before, f"state not restored: {before} -> {path_list}"

path = []
def go_good(n):
    if n == 0:
        return
    path.append(n)
    go_good(n - 1)
    path.pop()

def go_bad(n):
    if n == 0:
        return
    path.append(n)
    go_bad(n - 1)          # forgot path.pop()

check_restored(path, lambda: go_good(3))
print("good: restored")
try:
    check_restored(path, lambda: go_bad(3))
except AssertionError as e:
    print("bad:", e)
```
```text
good: restored
bad: state not restored: [] -> [3, 2, 1]
```

### A table of classic bugs

| Symptom | Likely cause | Fix |
|---|---|---|
| `RecursionError` | no base case, or no progress toward it | check the base case and that the argument gets smaller |
| Every stored answer is the same (or empty) | `result.append(path)` without a copy | `result.append(path[:])` |
| Answers have wrong content, board stays changed | a missing "un-choose" | write the undo line right below the do line |
| Function returns `None` instead of a value | the result of the recursive call is ignored | `return go(...)` or use the value |
| Results grow between calls | a mutable default argument, such as `def f(x, acc=[])` | use `None` and create the list inside |
| Duplicate answers | duplicates in input and no skip rule | sort, then skip equal siblings |
| Answers missing | a wrong prune, or `i > 0` instead of `i > start` | compare with a brute force |
| Too slow | no pruning, or the checks happen too late | check rules as early as possible |

Two of these deserve a demonstration.

```python
def can_make(nums, target, i=0):
    if target == 0:
        return True
    if i == len(nums):
        return False
    can_make(nums, target - nums[i], i + 1)       # the answer is thrown away!
    return can_make(nums, target, i + 1)

print(can_make([2, 3], 5))       # 2 + 3 = 5, so this should be True


def collect(x, acc=[]):                           # one list, shared by every call
    acc.append(x)
    return acc

print(collect(1), collect(2))
```
```text
False
[1, 2] [1, 2]
```

The first line should be `True`, but it is `False`: the "take" branch is computed and then forgotten. The second line shows two calls that should have returned `[1]` and `[2]`; both show `[1, 2]`, because the default list is created once, when the function is defined, and every call shares it.

**Try it 8.** `result.append(path)` stores the same list object each time. Show it in three lines of code, and show how to check whether two names refer to the same list.

<details><summary>Answer</summary>

```python
path = [1]
result = [path, path[:]]
path.append(2)
print(result)
print(result[0] is path, result[1] is path)
```
```text
[[1, 2], [1]]
True False
```

`result[0]` is `path` itself, so it changed when `path` changed. `result[1]` is a copy, so it kept `[1]`. The `is` operator asks "same object?" while `==` asks "same content?". When you see answers that all look identical in a backtracking result, think of `is`.

</details>

## 17. Recognising a backtracking problem

How do you know that a problem wants backtracking, and not a loop, a greedy method or dynamic programming?

| Clue in the problem | Likely tool |
|---|---|
| "all", "list every", "generate all" | backtracking |
| "count the ways", and the state repeats (same index and same remaining value reached many ways) | dynamic programming (memoised recursion) |
| "does there exist ...", small `n` (up to about 20-25) | backtracking, or bit masks |
| "best", "minimum", "maximum" and a local choice that is always safe | greedy |
| Search on a grid or in a maze, "is there a path" | backtracking / DFS |
| A puzzle with rules (Sudoku, N-Queens, crossword) | backtracking with pruning |
| `n` up to 10^5 and an answer is expected quickly | not backtracking: look for sorting, hashing, greedy or DP |

The **size of `n` is the strongest clue**. If `n <= 10` or `n <= 20`, the intended solution is probably exponential. If `n` is 10^5, it is not.

### Backtracking or dynamic programming?

Both are recursion. The difference is in what the sub-problems look like.

- In pure backtracking every path to a node is **different**, and the node's future depends on the whole path. Subsets, permutations and N-Queens are of this kind: nothing is repeated, so there is nothing to remember.
- In dynamic programming, many different paths lead to the **same state** (for example, "I am at coin number 3 and need 12 more"), and the future depends only on the state. Then the recursion tree has repeated sub-trees and you can store the answer once.

Here is the same problem solved both ways: how many ways to make 40 with the coins 1, 2, 5, 10 (each coin type used any number of times; the order of coins does not matter)?

```python
import functools

calls_plain = 0
def ways_plain(coins, i, remaining):
    global calls_plain
    calls_plain += 1
    if remaining == 0:
        return 1
    if remaining < 0 or i == len(coins):
        return 0
    return ways_plain(coins, i, remaining - coins[i]) + ways_plain(coins, i + 1, remaining)

calls_cached = 0
@functools.cache
def ways_cached(coins, i, remaining):
    global calls_cached
    calls_cached += 1
    if remaining == 0:
        return 1
    if remaining < 0 or i == len(coins):
        return 0
    return ways_cached(coins, i, remaining - coins[i]) + ways_cached(coins, i + 1, remaining)

coins = (1, 2, 5, 10)
print(ways_plain(coins, 0, 40), "calls:", calls_plain)
print(ways_cached(coins, 0, 40), "calls:", calls_cached)
```
```text
195 calls: 8133
195 calls: 218
```

Same answer, far fewer calls with the cache, because the state `(i, remaining)` repeats. Now compare with permutations of 4 items: the state "path so far" never repeats, so a cache would give no help and would only waste memory. **Ask: do different paths arrive at the same state?** If yes, think dynamic
programming (the next modules). If no, backtracking with pruning is the tool.

## 18. Common traps, collected

1. **No copy of the path.** `result.append(path)` stores a reference. Use `path[:]`.
2. **A missing un-choose.** Every `append` needs a `pop`, every `add` a `remove`, every `used[i] = True` a `used[i] = False`. Write them as a pair.
3. **Un-choosing after success when you meant to keep the state.** If you return `True` to keep a filled board, do not undo it. Undo only on failure.
4. **Forgetting `return` after recording an answer.** The function continues into the loop and adds more items to a complete path.
5. **`i > 0` instead of `i > start`** in the duplicate skip, which removes valid answers such as `[2, 2]`.
6. **Skipping the sort** before the duplicate rule. The rule only works when equal values are neighbours.
7. **`go(i + 1)` against `go(i)`** in combination problems. `i + 1` means "each item once"; `i` means "an item may be reused". Mixing them changes the problem.
8. **A loop `range` that is off by one**, in particular with the pruned upper bound of combinations (`n - need + 1`). Test small cases by hand.
9. **A prune that removes a real answer.** Test against a brute force.
10. **A mutable default argument** (`acc=[]`) shared by all calls.
11. **A base case that cannot be reached**, for example when the argument can be negative.
12. **Building the full list when you need a count or the first answer.** Use a counter, an early `return True`, or a generator.
13. **Recursion that is too deep.** Switch to a loop or an explicit stack, or reconsider the algorithm.

## 19. Summary

- **Recursion** solves a problem with the same problem on a smaller input. Every recursive function needs a base case, a recursive case, and progress. Trust the recursive call (induction); check only your own step.
- The **call stack** holds the waiting calls. Its maximum size is the recursion depth, and Python limits it (usually 1000).
- A **recursion tree** shows calls as nodes. Depth = stack size. Number of nodes x work per node = total cost. A chain has `n` nodes; a halving chain has `log n`; branching trees are exponential.
- Repeated sub-trees (like `fib`) can be cut by **memoisation**. Trees without repeats (subsets, permutations) need **pruning**.
- **Backtracking** = choose, explore, un-choose, on a tree of partial solutions. Answer three questions: what is complete, what are the options, what is forbidden.
- Always store a **copy** of the path, and always **undo** every part of the state.
- **Subsets** `2^n`: include/exclude, or the loop with a `start` index. **Combinations**: a `start` index and a length check. **Permutations**: a `used` array (or swaps). **Duplicates**: sort, then skip an equal *sibling*.
- **Pruning** = feasibility checks, bounds, `break` on sorted input, symmetry and duplicate skipping. A prune must never lose an answer: check against a brute force. The *order* of decisions (most constrained first) can matter more than the code.
- **Grid problems** mark a cell while you are inside it, and restore it when you leave. **N-Queens** uses sets for columns and two diagonals (`r - c`, `r + c`). **Sudoku** uses sets for rows, columns and boxes, and picks the cell with the fewest options.
- Estimate the size first: `2^n`, `n!`, `C(n, k)`, Catalan numbers. Python handles about 20 items for subsets and 9 or 10 for permutations.
- Use **generators** for "the first few" or "find one"; use an **explicit stack** when the depth is too big; use **dynamic programming** when the same state is reached by different paths.

### Self-check

- [ ] I can name the base case, the recursive case and the progress of any recursive function I write.
- [ ] I can draw a recursion tree, count its nodes, and give its depth.
- [ ] I can write the backtracking template from memory and explain choose, explore, un-choose.
- [ ] I copy the path before storing it, and I can explain why.
- [ ] I can generate subsets, combinations, and permutations, with and without duplicates.
- [ ] I can write an N-Queens solver and explain the sets for diagonals.
- [ ] I can write a grid search that marks and restores cells.
- [ ] I can add a prune and prove (or test) that it never loses an answer.
- [ ] I can estimate whether a backtracking solution is fast enough for the given `n`.
- [ ] I know when the problem is really dynamic programming.

### How to practise

Work through the problems of this module in the order of the chapter: first small recursions (sum, power, reverse, palindrome check), then the three generators (subsets, combinations, permutations), then the duplicates variants, then combination sum and its relatives, then
the grid and board problems (word search, N-Queens, Sudoku), and last the harder pruning problems. For every problem, **draw the recursion tree of a tiny input before you code**. When your program is wrong, compare its answers with `itertools` or a brute force on `n <= 5`.
The site problems for this module (LeetCode, CSES, Codeforces) will be listed for you in the module's external list.

### Further reading

- Donald Knuth, *The Art of Computer Programming*, volume 4 (fascicles 2, 3 and 5): generating all tuples, permutations, combinations, and backtracking, including the "dancing links" method for exact cover (Sudoku-like puzzles).
- Steven Skiena, *The Algorithm Design Manual*, the chapter on combinatorial search and heuristic methods.
- Peter Norvig, "Solving Every Sudoku Puzzle": a short essay on constraint propagation plus backtracking.
- The Python documentation of the `itertools` module (`product`, `permutations`, `combinations`, `combinations_with_replacement`) and of `functools.cache`.
- The CSES Problem Set, section "Introductory Problems", for chess and grid backtracking.

Next module: **dsa.08 Stacks and queues**.
