# dsa.01 Complexity analysis

## Why this chapter exists

In dsa.00 you learned to produce a correct program. This chapter is about the second question every
problem asks, usually silently: **will it finish in time?**

A program that gives the right answer after three hours is, for most purposes, a wrong program. Online judges
stop your code after one or two seconds. A website that takes ten seconds to answer loses its users. And the
difference between a fast program and a hopeless one is almost never "a faster computer" or "cleverer typing". It
is the *shape* of the algorithm: how the amount of work grows when the input grows.

Complexity analysis is the skill of predicting that growth **before running the code**, with a pencil. By the end
of this chapter you should be able to look at any program you write and say, in one line, "this is O(n log n)
time and O(n) space, so for n = 200000 it will take about a tenth of a second". You should also be able to read
a problem's constraints and know, before you start designing, which complexity you need.

This is the most reused idea in the whole DSA track. Every later module (hashing, sorting, trees, graphs, dynamic
programming) is, in the end, a collection of ways to move from a slow complexity to a fast one.

You need nothing new from Python except two small tools for measuring: `import time` and `time.perf_counter()`,
which returns a number of seconds from a very precise clock. Subtract two readings to get how long the code in
between took.

## A first experiment: how running time grows

Let us start with facts, not theory. This program times three jobs for lists of 1,000 up to 1,000,000 random
numbers: one loop over the list, sorting it, and a loop inside a loop.

```python
import random
import time

for n in [1_000, 10_000, 100_000, 1_000_000]:
    numbers = [random.randint(1, 10**9) for _ in range(n)]

    start = time.perf_counter()
    total = 0
    for x in numbers:                # one pass: about n steps
        total += x
    one_loop = time.perf_counter() - start

    start = time.perf_counter()
    sorted(numbers)                  # sorting: about n log n steps
    sorting = time.perf_counter() - start

    two_loops = "-"
    if n <= 10_000:                  # bigger n would take minutes or hours
        start = time.perf_counter()
        pairs = 0
        for i in range(n):           # a loop inside a loop: n * n steps
            for j in range(n):
                pairs += 1
        two_loops = f"{time.perf_counter() - start:.3f}"

    print(f"n={n:>9,}  one loop {one_loop:.5f}s  sort {sorting:.5f}s  two loops {two_loops}")
```

(`1_000` is just `1000`; Python lets you put underscores in numbers to make them readable.)

On the machine this course was written on, it printed:

```text
n=    1,000  one loop 0.00009s  sort 0.00017s  two loops 0.071
n=   10,000  one loop 0.00167s  sort 0.00288s  two loops 6.656
n=  100,000  one loop 0.00870s  sort 0.02895s  two loops -
n=1,000,000  one loop 0.07600s  sort 0.35319s  two loops -
```

Your numbers will differ (a faster or slower computer, other programs running), but the **pattern** will not.
Put it in a table, with the missing values estimated from the pattern:

| n | one loop | sort | loop inside a loop |
|---|---|---|---|
| 1,000 | 0.0001 s | 0.0002 s | 0.07 s |
| 10,000 | 0.0017 s | 0.003 s | 6.7 s |
| 100,000 | 0.009 s | 0.03 s | about 11 minutes (estimated) |
| 1,000,000 | 0.08 s | 0.35 s | about 18 hours (estimated) |

Look at what happens each time `n` grows ten times:

- The single loop takes about **10 times** longer. Its work is proportional to `n`.
- The sort takes a little more than 10 times longer (about 12 times). Its work is proportional to `n log n`.
- The double loop takes about **100 times** longer. Its work is proportional to `n * n`.

That last row is the whole reason this chapter exists. At `n = 1000` all three are instant, and you cannot tell
a good algorithm from a bad one by trying it. At `n = 1,000,000` the double loop needs most of a day while the
others need a fraction of a second. No amount of faster hardware closes that gap: a computer 10 times faster
turns 18 hours into 2 hours.

The estimates come from the growth rule, not from guessing: 6.7 seconds at `n = 10^4`, times 100 for each
further factor of 10, gives 670 seconds at `10^5` and 67,000 seconds (about 18.6 hours) at `10^6`.

## Counting operations

Timing needs a computer and gives a different number every run. Counting needs only a pencil and gives the same
answer every time. So we analyse algorithms by **counting steps**.

A **step** (or basic operation) is anything that takes a fixed amount of time, not depending on the input size:
an addition, a comparison, an assignment, indexing a list `a[i]`, reading a dict entry, calling `len` on a list.
We do not care exactly how long one step takes; we care how **many** steps there are as a function of the input
size, which we call `n`.

### Counting a single loop

```python
total = 0
for x in a:          # a has n elements
    total += x
print(total)
```

The body runs `n` times. Each pass is a few steps (fetch `x`, add, store). Before and after, a constant number of
steps. So the total is something like `3n + 2` steps. The exact numbers 3 and 2 depend on what you count as a step,
and they do not matter much, as you will see.

For `range`, the number of values is the key quantity:

| loop | number of passes |
|---|---|
| `for i in range(n)` | `n` |
| `for i in range(a, b)` | `b - a` (if `b > a`, else 0) |
| `for i in range(a, b + 1)` | `b - a + 1` |
| `for i in range(0, n, k)` | `ceil(n / k)`, which is `(n + k - 1) // k` |

### Counting nested loops

```python
count = 0
for i in range(n):
    for j in range(n):
        count += 1
```

For each of the `n` values of `i`, the inner loop runs `n` times: `n * n = n^2` passes in total.

When the inner loop depends on the outer variable, add up the inner counts row by row:

```python
count = 0
for i in range(n):
    for j in range(i + 1, n):
        count += 1
```

For `i = 0` the inner loop runs `n - 1` times, for `i = 1` it runs `n - 2` times, ..., for `i = n - 1` it runs 0
times. The total is `(n - 1) + (n - 2) + ... + 1 + 0`. You met this sum in dsa.00:

```text
1 + 2 + ... + m = m (m + 1) / 2
```

With `m = n - 1`, the total is `n (n - 1) / 2`. For `n = 4`: `4 * 3 / 2 = 6`. Check by listing:
(0,1) (0,2) (0,3) (1,2) (1,3) (2,3). Six pairs. This loop visits every **pair** of positions once, and the
number of pairs from `n` things is `n (n - 1) / 2`, about `n^2 / 2`.

### Counting a halving loop

```python
steps = 0
while n > 1:
    n = n // 2
    steps += 1
```

Start with `n = 1000`: 500, 250, 125, 62, 31, 15, 7, 3, 1. Nine halvings. The number of times you can halve `n`
before reaching 1 is the **logarithm base 2** of `n`, written `log2 n` (rounded down). It is the answer to
"2 to what power gives n?". Some values worth remembering:

| n | log2 n (about) |
|---|---|
| 1,000 | 10 |
| 1,000,000 | 20 |
| 10^9 | 30 |
| 10^18 | 60 |

Logarithms grow incredibly slowly. A loop that halves its range is almost free even for gigantic `n`. A loop that
**doubles** a variable from 1 up to `n` takes the same number of steps, also about `log2 n`.

<details><summary>Try it: how many times does <code>count += 1</code> run, for n = 10?</summary>

```python
count = 0
for i in range(n):
    for j in range(i):
        count += 1
for k in range(n):
    count += 1
```

The first part runs `0 + 1 + ... + 9 = 45` times. The second part runs 10 times. Total 55.
In general: `n (n - 1) / 2 + n = n (n + 1) / 2`.
</details>

## Big-O, Big-Theta and Big-Omega

Exact counts like `3n + 2` or `n (n - 1) / 2` are more detail than we need. When `n` is large, the term that grows
fastest swamps everything else, and the constant in front of it depends on the machine and on what we chose to
call a step. So we keep only the **growth rate**. Three notations do this.

### In plain words

- **Big-O, `O(g(n))`, is an upper bound:** "for large `n`, this grows **no faster than** `g(n)`, up to a constant
  factor". Saying a program is O(n^2) promises that doubling `n` will at worst roughly quadruple the time.
- **Big-Omega, `Ω(g(n))`, is a lower bound:** "for large `n`, this grows **at least as fast as** `g(n)`, up to a
  constant factor".
- **Big-Theta, `Θ(g(n))`, is a tight bound:** both at once. "This grows **exactly like** `g(n)`, up to constant
  factors."

In everyday programming talk, people say "O" when they mean "Θ". When someone says "this loop is O(n)", they
usually mean it really takes about `n` steps, not just "at most". This course does the same in informal places,
but you should know the difference: an O(n) algorithm is also, technically, O(n^2) (a true but useless upper
bound), while it is not Θ(n^2).

### Formally

Let `f(n)` be the number of steps. Then:

- `f(n)` is `O(g(n))` if there are positive constants `c` and `n0` such that `f(n) <= c * g(n)` for every
  `n >= n0`.
- `f(n)` is `Ω(g(n))` if there are positive constants `c` and `n0` such that `f(n) >= c * g(n)` for every
  `n >= n0`.
- `f(n)` is `Θ(g(n))` if it is both `O(g(n))` and `Ω(g(n))`.

The constant `c` is what lets us ignore constant factors. The threshold `n0` is what lets us ignore small inputs,
where anything can happen.

**Example.** Show that `f(n) = 3n + 2` is `Θ(n)`.

- Upper bound: for `n >= 1`, `2 <= 2n`, so `3n + 2 <= 3n + 2n = 5n`. Take `c = 5`, `n0 = 1`. So it is O(n).
- Lower bound: `3n + 2 >= 3n >= 1 * n` for every `n >= 1`. Take `c = 1`, `n0 = 1`. So it is Ω(n).
- Both hold, so it is Θ(n).

**Example.** Show that `n (n - 1) / 2` is `Θ(n^2)`.

- Upper: `n (n - 1) / 2 <= n * n / 2 = 0.5 n^2`. Take `c = 0.5`.
- Lower: for `n >= 2`, `n - 1 >= n / 2`, so `n (n - 1) / 2 >= n * (n/2) / 2 = 0.25 n^2`. Take `c = 0.25`, `n0 = 2`.

<details><summary>Try it: is <code>100n</code> in O(n^2)? Is <code>n^2</code> in O(100n)?</summary>

`100n <= 100 * n^2` for all `n >= 1`, so yes, `100n` is O(n^2) (a loose upper bound, but true).

`n^2 <= c * 100n` would need `n <= 100c` for every large `n`, which fails as soon as `n > 100c`, whatever constant
you pick. So `n^2` is **not** O(100n), which is the same as O(n). No constant can make a quadratic stay under a
linear function forever.
</details>

## Dropping constants and lower-order terms

Two rules follow from the definition, and you will use them constantly:

1. **Drop constant factors.** `5n`, `n / 2` and `100n` are all Θ(n). `0.5 n^2` is Θ(n^2).
2. **Keep only the fastest-growing term.** `n^2 + 1000n + 10^6` is Θ(n^2), because for large `n` the `n^2` term is
   bigger than the others combined. (At `n = 10^6`, `n^2 = 10^12` while `1000n = 10^9`, a thousandth of it.)

The order of growth, from slowest to fastest, of the terms you meet most:

```text
1  <  log n  <  sqrt(n)  <  n  <  n log n  <  n^2  <  n^3  <  2^n  <  n!
```

Also: the base of a logarithm does not matter in Big-O. `log2 n` and `log10 n` differ only by a constant factor
(`log2 n` is about `3.32 * log10 n`), so we just write O(log n).

### When constants still matter

Big-O is a statement about **growth**, not about speed at a particular size. Constants matter in three situations:

- **Same Big-O, different constants.** `sum(a)` and a Python `for` loop that adds the numbers are both O(n), but
  on this machine `sum` was about 10 times faster for a million numbers (0.014 s against 0.13 s), because `sum`
  runs in compiled C code while every pass of a Python loop goes through the interpreter. When two solutions have
  the same Big-O, the one with smaller constants wins, and you find out which by measuring.
- **Small inputs.** For `n = 5`, an O(n^2) method with a tiny constant can beat an O(n log n) method with a big
  one. Python's own sort uses a simple O(n^2) method (insertion sort) on short runs of data for exactly this reason.
- **Near the time limit.** If your O(n) solution takes 1.5 seconds and the limit is 1 second, you need a smaller
  constant, not a better Big-O.

What constants can **never** do is rescue a worse growth rate at large `n`. The table at the start shows it: the
double loop needs 10^8 steps at `n = 10^4` and took 6.7 s, while sorting a million numbers (about 2 * 10^7
comparisons) took 0.35 s. At `n = 10^6` their step counts differ by a factor of about 50,000. **Choose by Big-O
first; use constants to choose between solutions of the same Big-O.**

## The common complexity classes

These seven classes cover almost everything you will write.

- **O(1), constant.** The work does not depend on `n`: indexing `a[i]`, `len(a)`, a dict lookup (on average), a
  formula like `n * (n - 1) // 2`.
- **O(log n), logarithmic.** The problem size is cut by a constant factor each step: halving loops, binary search
  in a sorted list, counting the digits of `n`.
- **O(n), linear.** A constant amount of work per element: one pass, `sum`, `max`, `x in list`, building a set.
- **O(n log n), linearithmic.** Sorting (`sorted`, `list.sort`), and divide-and-conquer methods like merge sort.
  "Sort first, then do one pass" is the most common O(n log n) solution shape.
- **O(n^2), quadratic.** All pairs: a loop inside a loop over the same data. Also hidden versions, like
  `x in list` inside a loop.
- **O(2^n), exponential.** Trying every subset of `n` things, or recursion that calls itself twice on a problem only
  one smaller (the naive recursive Fibonacci).
- **O(n!), factorial.** Trying every order (permutation) of `n` things.

How the number of steps grows (values rounded):

| n | log2 n | n | n log2 n | n^2 | 2^n | n! |
|---|---|---|---|---|---|---|
| 10 | 3.3 | 10 | 33 | 100 | 1,024 | 3.6 * 10^6 |
| 20 | 4.3 | 20 | 86 | 400 | 1.05 * 10^6 | 2.4 * 10^18 |
| 100 | 6.6 | 100 | 664 | 10^4 | 1.3 * 10^30 | 9.3 * 10^157 |
| 1,000 | 10 | 1,000 | about 10^4 | 10^6 | far too many | far too many |
| 10^5 | 17 | 10^5 | 1.7 * 10^6 | 10^10 | far too many | far too many |
| 10^6 | 20 | 10^6 | 2 * 10^7 | 10^12 | far too many | far too many |

Read it with the rule of thumb from dsa.00 (plain Python does about 10^7 simple steps per second; the measurement
at the start gave about 1.3 * 10^7 for the single loop and 1.5 * 10^7 for the double loop). Then:

- 10^4 steps is instant, 10^7 is about a second, 10^10 is about 15 minutes to an hour, 10^12 is days.
- O(2^n) is fine for `n = 20` (a million) and absurd for `n = 100` (10^30 steps would outlast the universe).
- O(n!) is fine for `n = 10` and hopeless beyond about 12.

## Analysing code

Here are the rules, all of which follow from counting.

**Rule 1: simple statements are O(1).** Assignments, arithmetic on ordinary-sized numbers, comparisons, indexing,
`append` (amortised, see below), dict and set operations (on average).

**Rule 2: a loop costs (number of passes) times (cost of one pass).** If the cost of a pass changes from pass to
pass, add them up instead of multiplying.

**Rule 3: sequential blocks add.** Two loops one after the other, of `n` and `m` passes: O(n + m). Then keep only
the biggest term. A loop of `n` followed by a double loop of `n^2` is O(n + n^2) = O(n^2).

**Rule 4: nested blocks multiply.** A loop of `n` passes containing a loop of `m` passes: O(n * m).

**Rule 5: a loop that multiplies or divides its variable by a constant runs O(log n) times.**

**Rule 6: look inside every operation.** `x in some_list`, `max(a)`, `a.count(x)`, `a.index(x)`, `a[i:j]`,
`a.insert(0, x)`, `a.pop(0)`, `s1 + s2`, `sorted(a)` are single lines that are not single steps. Their costs are
in the Python section below. Most "mysteriously slow" programs have one of these inside a loop.

### Worked example 1: sequential versus nested

```python
n = 8
ops = 0
for i in range(n):          # n
    ops += 1
for j in range(n):          # + n
    ops += 1
print(ops)                  # 16: sequential, O(n)

ops = 0
for i in range(n):          # n times ...
    for j in range(n):      # ... n each
        ops += 1
print(ops)                  # 64: nested, O(n^2)
```

### Worked example 2: a nested loop that is not quadratic

```python
n = 8
ops = 0
size = n
while size > 0:
    for j in range(size):
        ops += 1
    size = size // 2
print(ops)                  # 8 + 4 + 2 + 1 = 15
```

A loop inside a loop, but the inner lengths are `n, n/2, n/4, ...`. Their sum is less than `2n`
(each term is half the previous one, so together they never reach twice the first). This is O(n). The lesson:
**never judge complexity by indentation. Add up what really runs.**

### Worked example 3: a loop with halving inside a loop

```python
n = 1000
ops = 0
for i in range(n):
    k = 1
    while k < n:
        k = k * 2
        ops += 1
print(ops)                  # 1000 * 10 = 10000
```

The inner loop doubles `k` up to `n`, about `log2 n` passes, and does not depend on `i`. Total `n log n`:
O(n log n).

### Worked example 4: a hidden loop

```python
a = list(range(10000))
b = list(range(5000, 15000))
common = 0
for x in a:
    if x in b:              # scans b: up to len(b) comparisons
        common += 1
print(common)               # 5000
```

The loop runs `n = len(a)` times and each `x in b` scans up to `m = len(b)` elements: O(n * m). With
`b = set(b)` before the loop, each check is O(1) on average and the total is O(n + m).

<details><summary>Try it: give the Big-O of each snippet (a has n elements).</summary>

```python
# (1)
for i in range(n):
    for j in range(10):
        print(i, j)

# (2)
i = 1
while i < n:
    i = i * 3

# (3)
for i in range(n):
    print(a[:i])
```

(1) O(n): the inner loop has a fixed length of 10.
(2) O(log n): `i` triples each time, so about `log3 n` passes, and the base does not matter.
(3) O(n^2): `a[:i]` copies `i` elements (and printing them costs as much again), so the total is
`0 + 1 + ... + (n - 1)`, about `n^2 / 2`.
</details>

## Space complexity

Memory is a cost too. **Space complexity** counts how much memory an algorithm needs as a function of `n`. In this
course it means **extra** (auxiliary) space: memory the algorithm creates, not counting the input.

- A few variables, whatever their values: O(1).
- A new list, set or dict with one entry per input element: O(n).
- A table of `n` rows and `n` columns: O(n^2). At `n = 10^4` that is 10^8 entries, about 800 MB just for the
  references in the lists. Many solutions that are fast enough in time fail because of this.
- Recursion: every call that is still waiting for a result keeps its own variables. A recursion that goes `n`
  levels deep uses O(n) space, even if it creates no lists (more on this below).

Watch out for **copies**. `b = a` does not copy (both names refer to the same list, as you learned in core.05), but
`a[1:]`, `a[:]`, `list(a)`, `sorted(a)` and `a + b` all create new lists. Slicing inside a loop costs time as well
as memory.

There is often a trade between time and space. The set-based duplicate check uses O(n) extra space and O(n) time;
the sort-based one can use O(1) extra space (sorting the list in place with `a.sort()`) and O(n log n) time.
Usually memory is cheaper than time, so we accept O(n) extra space for a faster algorithm, but not O(n^2) space at
`n = 10^5`.

<details><summary>Try it: what is the extra space of this code?</summary>

```python
best = 0
current = 0
for x in a:
    current = max(0, current + x)
    best = max(best, current)
```

O(1): two variables, no matter how long `a` is. The time is O(n).
</details>

## Amortised analysis: why append is fast

A Python list stores references to its items in one block of memory. The block has room for a certain number of
items, its **capacity**, which is often more than the current length. Appending to a list with spare room just
writes into the next slot: O(1). But when the block is full, Python must reserve a bigger block and **copy every
item** across. That one append costs O(n).

So is `append` O(1) or O(n)? Let us count the total cost of many appends, using the simplest growth rule:
**double the capacity when full**, starting from capacity 1.

| append number | full before it? | items copied | capacity after | total copies so far |
|---|---|---|---|---|
| 1 | no | 0 | 1 | 0 |
| 2 | yes | 1 | 2 | 1 |
| 3 | yes | 2 | 4 | 3 |
| 4 | no | 0 | 4 | 3 |
| 5 | yes | 4 | 8 | 7 |
| 6, 7, 8 | no | 0 | 8 | 7 |
| 9 | yes | 8 | 16 | 15 |
| 10 to 16 | no | 0 | 16 | 15 |
| 17 | yes | 16 | 32 | 31 |

After `n` appends the copies add up to `1 + 2 + 4 + ... + 2^k`, where `2^k` is the largest power of two below `n`.
That sum equals `2^(k+1) - 1`, which is less than `2n`. Adding the `n` writes of the new items themselves, the
whole sequence of `n` appends costs less than `3n` steps: **O(n) in total, so O(1) per append on average**.

This is called **amortised O(1)**. "Amortised" means the cost is averaged over a whole sequence of operations, and
the bound is guaranteed for *any* sequence, not just on typical inputs. The rare expensive appends are paid for by
the many cheap ones that follow them: after a growth that copied `m` items, there are about `m` cheap appends
before the next growth.

Two things are essential for this to work:

- **Growth must be proportional to the current size.** If the list grew by a fixed 10 slots each time, it would
  copy 10, 20, 30, ... items, adding up to about `n^2 / 20`: O(n^2) in total.
- **Amortised is not "every time".** A single append can still take O(n) time. For a batch program, only the
  total matters. For a game that must draw a frame every 16 milliseconds, one huge copy could cause a stutter.

You can watch CPython's real list grow. `sys.getsizeof` reports how many bytes a list's block takes; when it jumps,
the capacity changed:

```python
import sys

a = []
last = sys.getsizeof(a)
for i in range(70):
    a.append(i)
    size = sys.getsizeof(a)
    if size != last:
        print("length", len(a), "bytes", size)
        last = size
```

On this machine (64-bit Python 3.14) it printed:

```text
length 1 bytes 88
length 5 bytes 120
length 9 bytes 184
length 17 bytes 248
length 25 bytes 312
length 33 bytes 376
length 41 bytes 472
length 53 bytes 568
length 65 bytes 664
```

Each item reference takes 8 bytes, and an empty list takes 56, so the capacities were 4, 8, 16, 24, 32, 40, 52, 64,
76. CPython grows by about one eighth of the current size plus a little, not by doubling. Growth by a fixed
**fraction** still gives a geometric sum, so the conclusion is the same: amortised O(1).

Compare `a.insert(0, x)`: to make room at the front, every existing item must shift one place. The `i`-th insert
shifts `i` items, so `n` inserts cost `n (n - 1) / 2`: O(n^2). Measured here: 100,000 appends took 0.008 s;
100,000 inserts at the front took 1.38 s. When `n` went from 10,000 to 100,000, append's time grew 10 times and
insert's grew about 90 times.

<details><summary>Try it: a dynamic array starts with capacity 1 and triples when full. How many copies do 28 appends cause?</summary>

It grows before appends 2 (copy 1, capacity 3), 4 (copy 3, capacity 9) and 10 (copy 9, capacity 27), and
before append 28 (copy 27, capacity 81). Total `1 + 3 + 9 + 27 = 40` copies for 28 appends. Still less than
`2n`: a geometric sum is always dominated by its last term.
</details>

## Best, average and worst case

The same code can be fast on one input and slow on another **of the same size**. Linear search:

```python
pos = -1
for i in range(len(a)):
    if a[i] == target:
        pos = i
        break
```

- **Best case:** the target is at position 0. One comparison: O(1).
- **Worst case:** the target is last or missing. `n` comparisons: O(n).
- **Average case:** if the target is present and equally likely to be anywhere, about `n / 2` comparisons: O(n).
  An average always depends on an assumption about the inputs.

Unless told otherwise, **analyse the worst case**. A judge's test data, or one unlucky real user, will hit it.
Small, friendly examples in a problem statement tell you nothing about speed; one test at the maximum size in the
worst shape decides whether you pass.

Two accepted exceptions:

- **Hashing.** Dict and set operations are O(1) on average and O(n) in a pathological worst case (when many keys
  collide). With ordinary data the worst case does not happen, so we quote O(1).
- **Amortised bounds** like `append`. They are guarantees for the total over any sequence, so they are safe to use.

Some algorithms have very different best and worst cases. Insertion sort (move each element left until it is in
place) does `n - 1` comparisons on an already sorted list (O(n)) but `n (n - 1) / 2` swaps on a reversed one (O(n^2)).

## Analysing recursion

You will write functions in core.06 and recursion soon after. You can already read them, and you need to analyse
them, so here is the minimum. In

```python
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

print(fib(10))       # 55
```

`def fib(n):` defines a named piece of code that receives a number `n`. `fib(10)` runs it with `n = 10`. `return`
sends a value back to whoever asked. Inside, `fib` asks for `fib(n - 1)` and `fib(n - 2)`: it **calls itself** on
smaller inputs, which is recursion. The `if n < 2` part is the **base case** that stops it.

### Recursion trees

To count the work of a recursive function, draw a **recursion tree**: a box for each call, with its child calls
underneath. For `fib(4)`:

```text
                      fib(4)
                 /              \
            fib(3)              fib(2)
           /      \            /      \
       fib(2)    fib(1)    fib(1)    fib(0)
      /      \
  fib(1)    fib(0)
```

Nine boxes: nine calls. Each call does O(1) work of its own (a comparison and an addition), so the time is
proportional to the number of boxes. And the tree is wasteful: `fib(2)` is computed twice, and in `fib(10)` it is
computed 34 times. The number of calls `C(n)` satisfies `C(n) = 1 + C(n - 1) + C(n - 2)`, which grows about 1.6
times for each step of `n`: `fib(10)` makes 177 calls, `fib(30)` makes about 2.7 million, `fib(40)` about 330
million. That is exponential, O(1.62^n), often loosely written O(2^n). A loop that keeps the last two values
does the same job in O(n).

### Recurrence relations

A **recurrence** describes the running time of a recursive function in terms of its running time on smaller
inputs. Write `T(n)` for the time on input size `n`:

- `T(n) = T(n - 1) + T(n - 2) + O(1)` for `fib`.
- `T(n) = T(n / 2) + O(1)` for binary search: one recursive look at half the list, plus a comparison.
- `T(n) = 2 T(n / 2) + O(n)` for merge sort: sort two halves, then merge them in linear time.
- `T(n) = T(n - 1) + O(1)` for a recursive sum that adds the first element to the sum of the rest (passing an
  index, not a slice).

To **solve** a recurrence, draw its tree and add up the work **level by level**. Merge sort, for `n = 8`:

| level | calls | size of each | work per call | work on the level |
|---|---|---|---|---|
| 0 | 1 | 8 | 8 | 8 |
| 1 | 2 | 4 | 4 | 8 |
| 2 | 4 | 2 | 2 | 8 |
| 3 | 8 | 1 | 1 | 8 |

Every level does `n` work in total, and halving from `n` down to 1 gives `log2 n + 1` levels. Total
`n (log2 n + 1)`: O(n log n). This is the most important recurrence in the course.

Binary search has one call per level and O(1) work per call over `log2 n` levels: O(log n). The recursive sum has
one call per level, `n` levels, O(1) work each: O(n), and also **O(n) space**, because all `n` calls are waiting
at the same time. Python allows only about 1000 nested calls by default (`sys.getrecursionlimit()` returns 1000),
so that recursive sum crashes with `RecursionError` for a list of a few thousand items, while a loop handles
millions.

### The master theorem, practical form

For recurrences of the shape

```text
T(n) = a T(n / b) + n^d
```

where `a >= 1` calls are made on pieces of size `n / b` (with `b > 1`) and each call does `n^d` work of its own,
compare `a` with `b^d`:

| case | meaning | answer |
|---|---|---|
| `a < b^d` | the work shrinks down the tree; the top level dominates | O(n^d) |
| `a = b^d` | every level does the same work | O(n^d log n) |
| `a > b^d` | the work grows down the tree; the leaves dominate | O(n^(log_b a)) |

Examples:

| recurrence | a, b, d | compare | answer | typical algorithm |
|---|---|---|---|---|
| `T(n) = T(n/2) + 1` | 1, 2, 0 | `1 = 2^0` | O(log n) | binary search |
| `T(n) = 2T(n/2) + n` | 2, 2, 1 | `2 = 2^1` | O(n log n) | merge sort |
| `T(n) = 2T(n/2) + 1` | 2, 2, 0 | `2 > 1` | O(n^(log2 2)) = O(n) | visiting every node of a balanced tree |
| `T(n) = T(n/2) + n` | 1, 2, 1 | `1 < 2` | O(n) | work `n + n/2 + n/4 + ...` |
| `T(n) = 4T(n/2) + n` | 4, 2, 1 | `4 > 2` | O(n^2) | a poor split into four halves |

The theorem only covers problems that shrink by a **factor**. For subtract-by-one recurrences, expand them directly:

- `T(n) = T(n - 1) + 1` gives `n` levels of 1: O(n).
- `T(n) = T(n - 1) + n` gives `n + (n - 1) + ... + 1`: O(n^2). (A recursive function that slices off the first
  element, `rest = a[1:]`, is this: each slice costs O(n).)
- `T(n) = 2 T(n - 1) + 1` gives `1 + 2 + 4 + ... + 2^(n - 1)`: O(2^n).

<details><summary>Try it: solve T(n) = 3 T(n/3) + n and T(n) = 8 T(n/2) + n^2.</summary>

First: `a = 3, b = 3, d = 1`, `3 = 3^1`: O(n log n). (Three thirds, linear work per level, `log3 n` levels.)

Second: `a = 8, b = 2, d = 2`, `8 > 2^2 = 4`: O(n^(log2 8)) = O(n^3).
</details>

## Python-specific costs

Big-O analysis needs the cost of each built-in operation. These are the ones you use daily (from the Python wiki's
"TimeComplexity" page; `n` is the size of the collection, `k` the size of the slice or of the other argument):

| operation | cost |
|---|---|
| `len(a)`, `a[i]`, `a[i] = x` | O(1) |
| `a.append(x)` | amortised O(1) |
| `a.pop()` (from the end) | O(1) |
| `a.pop(0)`, `a.insert(0, x)`, `a.pop(i)`, `a.insert(i, x)` | O(n) |
| `x in a`, `a.index(x)`, `a.count(x)`, `a.remove(x)` | O(n) |
| `min(a)`, `max(a)`, `sum(a)` | O(n) |
| `a[i:j]` (slice) | O(k), it copies `k = j - i` items |
| `a + b`, `a.copy()`, `list(a)` | O(n + k) / O(n) |
| `a.sort()`, `sorted(a)` | O(n log n) |
| `x in s`, `s.add(x)`, `s.remove(x)` (set) | O(1) on average |
| `d[k]`, `d[k] = v`, `k in d`, `del d[k]` (dict) | O(1) on average |
| `set(a)`, `dict.fromkeys(a)` | O(n) |
| `s1 + s2` (strings) | O(len(s1) + len(s2)), it builds a new string |
| `"".join(parts)` | O(total length) |

### List versus set membership

The single most common performance bug is `x in some_list` inside a loop. Measured on this machine, looking up a
value that is **not** present:

```python
import time

for n in [1_000, 10_000, 100_000, 1_000_000]:
    as_list = list(range(n))
    as_set = set(as_list)
    missing = -1                     # not present: the list must look at everything
    start = time.perf_counter()
    for _ in range(1000):
        missing in as_list
    t_list = (time.perf_counter() - start) / 1000
    start = time.perf_counter()
    for _ in range(1000):
        missing in as_set
    t_set = (time.perf_counter() - start) / 1000
    print(f"n={n:>9,}  list {t_list*1e6:10.2f} us   set {t_set*1e6:.3f} us")
```

```text
n=    1,000  list       5.61 us   set 0.074 us
n=   10,000  list      49.58 us   set 0.066 us
n=  100,000  list     555.61 us   set 0.066 us
n=1,000,000  list    6282.62 us   set 0.076 us
```

("us" means microseconds, millionths of a second.) The list grows tenfold with the size: O(n). The set does not
change at all: O(1). A set (and a dict) uses **hashing**: Python computes a number from the value (its hash),
uses it to pick a slot in a table, and checks only that slot. It never looks at the other elements. For 100,000
lookups in a 100,000-element collection, that is roughly 55 seconds against 0.007 seconds.

The price: a set uses more memory than a list, has no order and no positions, and can only hold hashable values
(numbers, strings, tuples of those; not lists).

### Building strings in a loop

```python
import time

for n in [10_000, 100_000, 1_000_000]:
    start = time.perf_counter()
    text = ""
    for i in range(n):
        text = text + "x"
    t_plus = time.perf_counter() - start

    start = time.perf_counter()
    parts = []
    for i in range(n):
        parts.append("x")
    text = "".join(parts)
    t_join = time.perf_counter() - start
    print(f"n={n:>9,}  text = text + x: {t_plus:.4f}s   join: {t_join:.4f}s")
```

Strings cannot be changed in place, so `text + "x"` builds a brand new string and copies all the old characters
into it. Over `n` steps that is `1 + 2 + ... + n` copies: O(n^2). Measured here:

| n | `text = text + "x"` | append to a list, then `"".join` |
|---|---|---|
| 10,000 | 0.003 s | 0.001 s |
| 100,000 | 0.32 s | 0.009 s |
| 1,000,000 | 36 to 95 s (two runs) | 0.09 s |

The quadratic growth only shows at large sizes: at 10,000 the difference is invisible, which is exactly why this
bug survives testing on small inputs. (CPython sometimes manages to extend a string in place when nothing else
refers to it, which can hide the problem in one program and not in another. Do not rely on it.) The safe habit:
collect pieces in a list and `"".join` them once at the end. This also applies to output: building one big string
and printing it once is faster than many separate `print` calls.

### Slicing copies

`a[1:]` is not a "view" of the list; it is a new list with `n - 1` items copied in. Measured here, `a[1:]` on a
million-item list took about 0.012 s. Harmless once; disastrous inside a loop of a million passes. When you need
"the rest of the list", keep an index instead of slicing.

### Sorting

`sorted` and `list.sort` are O(n log n) comparisons in the worst case, and very fast in practice (implemented in C,
and quicker still on data that is already partly sorted). Sorting a million random integers took 0.35 s here.
"Sort, then scan once" is a standard way to turn an O(n^2) pairs problem into O(n log n): after sorting, equal
values are neighbours, and the two closest values are neighbours.

### Dicts

A dict is a hash table from keys to values, so lookups, inserts, updates, deletes and `k in d` are O(1) on
average. That makes it the tool for "count how many times each value occurs" and "remember where I saw this
value" in one pass. Iterating over a dict is O(n), and `len(d)` is O(1).

## Three ways to make code faster

Most speed-ups in this module (and many in the whole track) are one of these:

1. **Hoist work out of the loop.** If something gives the same result on every pass, compute it once before the
   loop. `if a[i] == max(a)` inside a loop is O(n^2); `best = max(a)` before it makes the loop O(n).
2. **Use the right structure.** Replace a scan by a lookup: a set for "have I seen this?", a dict for "how many?"
   or "where?". Replace `pop(0)` from a list by a `for` loop (or later, a `deque`).
3. **Precompute, or count instead of simulate.** Pay once for something that answers many later questions
   (running totals answer any range-sum question with one subtraction), or find a formula for what a loop
   counts (the pairs loop runs `n (n - 1) / 2` times; no need to run it).

The trace-and-count skills of this chapter are how you find which line to change: list each line inside the main
loop with its cost and how often it runs. The slow line is the one whose cost grows with `n`.

## Using constraints to choose an approach

This is where analysis pays off before you write anything. A problem's constraints tell you the largest input,
and the time limit tells you the budget. Combine them with the rule of thumb:

- A compiled language like C++ does roughly **10^8** simple operations per second.
- **Python is slower, roughly 10^7** simple operations per second (between a few million and a few tens of
  millions, depending on the operation; built-ins written in C are much faster per element).

Put the largest `n` into your complexity, and see whether the result fits in about 10^7 per second of time limit.
The table below, for a time limit of about one second in Python, is worth memorising:

| largest n | acceptable complexity | typical approach |
|---|---|---|
| n <= 10 to 11 | O(n!) | try every order (permutations) |
| n <= 20 to 25 | O(2^n), O(2^n * n) | try every subset |
| n <= 100 to 300 | O(n^3) | three nested loops |
| n <= 2,000 to 5,000 | O(n^2) | all pairs, a double loop |
| n <= 10^5 to 10^6 | O(n log n) or O(n) | sort then scan, hashing, one pass, two pointers |
| n <= 10^7 | O(n), with a small constant | one simple pass, built-ins where possible |
| n up to 10^12 | O(sqrt n) | loop up to the square root |
| n up to 10^18 | O(log n) or O(1) | halving, binary search, a formula |

The borders are fuzzy: a tight O(n^2) loop at `n = 3000` (9 * 10^6 steps) is about a second in Python; at
`n = 10^4` (10^8) it is about ten seconds and fails. In C++ that same `n = 10^4` would pass. When you are near a
border, prefer the safer complexity.

### Worked example

> Given `n <= 2 * 10^5` integers, print how many pairs of positions hold equal values.

1. Constraints: `n = 2 * 10^5`. All pairs means `n^2 / 2 = 2 * 10^10` steps: about half an hour. Too slow.
2. Target: O(n log n) or O(n), at most a few million steps.
3. Idea at that complexity: count each value's occurrences in a dict (one pass, O(n)). A value that occurs `c`
   times forms `c (c - 1) / 2` pairs. Add them up.
4. Check the answer's size: if all values are equal, the answer is about 2 * 10^10, bigger than `n`. So the
   pairs must be counted by formula, not listed. (Python's integers are unlimited, so no overflow worries.)

Notice that the constraint did half the design work: it ruled out the obvious idea and told us the shape of the
right one before we had to be clever.

### Constraints are hints

Problem setters choose limits on purpose. `n <= 20` almost always means "exponential is intended". `n <= 10^18`
means "do not loop to n". `n <= 5000` means "O(n^2) is allowed, don't over-think it". Read the constraints
**first**, before the story.

<details><summary>Try it: n <= 10^5, and q <= 10^5 questions "is x in the list?". Does "loop over the list for each question" pass?</summary>

`n * q = 10^10` comparisons in the worst case: no (about 15 minutes in Python). Build a set once (O(n)), then
answer each question in O(1): O(n + q), about 2 * 10^5 steps. Or sort once and use binary search,
O((n + q) log n).
</details>

## Measuring your own code

Analysis predicts; measurement confirms. A simple and very effective experiment is the **doubling test**: time
your program at `n`, `2n` and `4n`, and look at the ratio between consecutive times.

```python
import time

for n in [1000, 2000, 4000]:
    start = time.perf_counter()
    count = 0
    for i in range(n):
        for j in range(i + 1, n):
            count += 1
    print(n, round(time.perf_counter() - start, 3))
```

On this machine it printed about `1000 0.03`, `2000 0.13`, `4000 0.52`: each doubling of `n` multiplied the time by
about 4, which is what O(n^2) predicts. The ratios to expect when `n` doubles:

| complexity | time ratio when n doubles |
|---|---|
| O(n) | about 2 |
| O(n log n) | a little more than 2 |
| O(n^2) | about 4 |
| O(n^3) | about 8 |
| O(2^n) | the time squares (it does not just multiply) |

Some practical advice for timing:

- Use `time.perf_counter()`, not `time.time()`; it is designed for measuring short intervals.
- Run several times and take the smallest time; other programs on the computer add noise.
- Time with large inputs. At small `n`, start-up costs and noise hide the growth.
- Generate large test inputs with a small script (as the tests in this module do) instead of typing them.

## Summary

- Complexity analysis predicts how running time and memory grow with the input size `n`, using counting rather than
  timing. Growth, not raw speed, decides whether a program finishes: at `n = 10^6`, an O(n^2) loop needs hours
  where an O(n) loop needs a tenth of a second.
- Count how many times the innermost line runs. Single loops give sums of `range` lengths; dependent nested loops
  give sums like `n (n - 1) / 2`; halving or doubling gives about `log2 n`.
- Big-O is an upper bound, Big-Omega a lower bound, Big-Theta a tight bound, each up to a constant factor and for
  large enough `n`. Drop constants and lower-order terms.
- The classes in order: O(1) < O(log n) < O(n) < O(n log n) < O(n^2) < O(2^n) < O(n!).
- Sequential code adds, nested code multiplies, and every built-in has its own cost: `x in list`, `max`, slicing,
  `pop(0)`, `insert(0, x)` and string `+` are hidden O(n) loops.
- Space complexity counts extra memory, including copies and the recursion stack.
- `append` is amortised O(1): with proportional growth, the copies total less than `2n` over `n` appends.
- Analyse the worst case, except for hashing (average O(1)) and amortised bounds.
- Recursion: draw the tree, add the work per level. The master theorem solves `T(n) = a T(n/b) + n^d` by comparing
  `a` with `b^d`. Subtract-by-one recurrences are expanded directly.
- Python does roughly 10^7 simple operations per second. Read the constraints first and use the table to choose
  the target complexity before designing.
- To speed up code: hoist repeated work out of loops, use sets and dicts instead of scans, precompute or use a
  formula instead of simulating.

## Learning outcomes checklist

Tick these honestly. Each should be true without looking anything up.

- [ ] I can count exactly how many times a line runs in single, nested, dependent and halving loops, and turn the
  count into a formula.
- [ ] I can define Big-O, Big-Omega and Big-Theta in plain words and with `c` and `n0`, and prove a simple bound.
- [ ] I can state the time and space complexity of any solution I write, in one line, with a reason.
- [ ] I know the costs of common list, set, dict and string operations and spot hidden O(n) operations inside loops.
- [ ] I can explain why `append` is amortised O(1) with a cost table, and why `insert(0, x)` in a loop is O(n^2).
- [ ] I can give best, average and worst cases for a simple algorithm, and I know which one to use.
- [ ] I can draw a recursion tree, write a recurrence, and solve common ones with the master theorem or by expansion.
- [ ] Given constraints, I can say which complexity is needed and whether an O(n^2) idea will pass in Python.
- [ ] I can verify a complexity claim with a doubling experiment using `time.perf_counter`.

## Further reading

- Python wiki, "TimeComplexity": the cost of every list, deque, set and dict operation in CPython:
  https://wiki.python.org/moin/TimeComplexity
- Python documentation, `time.perf_counter`: https://docs.python.org/3/library/time.html#time.perf_counter
- Python documentation, `timeit`, a module for careful timing of small snippets:
  https://docs.python.org/3/library/timeit.html
- "Competitive Programmer's Handbook" by Antti Laaksonen, chapter 2 "Time complexity" (including the table of input
  sizes and complexities): https://cses.fi/book/book.pdf
- Big-O cheat sheet of common data structures and sorting algorithms: https://www.bigocheatsheet.com/
- Thomas H. Cormen, Charles E. Leiserson, Ronald L. Rivest and Clifford Stein, *Introduction to Algorithms*
  (MIT Press). Chapter 3 defines the notations formally and chapter 4 covers recurrences and the master theorem.
  Look for it in your college library.
- The CPython source for list growth, with a comment explaining the over-allocation rule:
  https://github.com/python/cpython/blob/main/Objects/listobject.c
