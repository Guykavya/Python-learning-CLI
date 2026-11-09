# dsa.16 Advanced data structures

## 1. Why range queries with updates need new tools

Many programs keep a list of numbers and keep asking questions about **a stretch** of it.

- *What is the total of the sales from day 10 to day 250?*
- *What was the lowest temperature between hour 5 and hour 90?*
- *A shop changes one price. What is the new total of the shelf from slot 30 to slot 70?*
- *Add 5 points to every player ranked 100 to 400, then ask for the best score among ranks 200 to 300.*

The first two are **range queries**. The last two add **updates**: the data changes between the questions. A data structure that handles both, fast, is what this module is about.

### What we already know: prefix sums

In dsa.03 (arrays and strings patterns), section 2, you learned prefix sums. Build `pre` once, and the sum of any stretch is one subtraction.

```python
def build_prefix(a):
    pre = [0] * (len(a) + 1)
    for i, x in enumerate(a):
        pre[i + 1] = pre[i] + x
    return pre

a = [5, 3, 8, 6, 2, 7, 4, 1]
pre = build_prefix(a)
print(pre)
print("sum of a[2:7] =", pre[7] - pre[2])
```
```text
[0, 5, 8, 16, 22, 24, 31, 35, 36]
sum of a[2:7] = 27
```

That is `O(n)` to build and `O(1)` per query. For a list that never changes, nothing beats it.

### Where prefix sums break: updates

Now one price changes: `a[3]` becomes `100`. Every prefix sum from `pre[4]` onwards contained the old value, so every one of them is wrong.

```python
a[3] = 100
print("stale pre :", pre)
print("true sums :", build_prefix(a))
```
```text
stale pre : [0, 5, 8, 16, 22, 24, 31, 35, 36]
true sums : [0, 5, 8, 16, 116, 118, 125, 129, 130]
```

To repair the table we must touch every entry from the changed position to the end. That is `O(n)` work for **one** changed number. If there are as many updates as queries, we have lost: each update costs `O(n)`.

### The three simple strategies, and what they cost

Let us count the work. For a list of `n` numbers we compare three ways to answer "sum of `a[l:r]`" and to "set `a[i] = v`".

| Strategy | Update | Query |
|---|---|---|
| Plain list, add up the stretch | `O(1)` | `O(n)` |
| Prefix sums, rebuild after an update | `O(n)` | `O(1)` |
| **A tree over the ranges** (this module) | `O(log n)` | `O(log n)` |

The tree wins because it balances the two costs. Neither side is free, but both are small. With `n = 10^5`, `log2(n)` is about 17. Instead of 100,000 steps per operation we do about 17.

We can see this with a counter. Below, 1,000 random operations (half updates, half queries) run on 1,000 numbers. We count how many array cells each strategy touches. (`random.Random(1)` is a random generator with a fixed seed, so the numbers are the same on every run.)

```python
import random

def count_work(n, ops, seed):
    rng = random.Random(seed)
    plain = 0      # cells touched by "plain list"
    prefix = 0     # cells touched by "prefix sums with rebuild"
    for _ in range(ops):
        if rng.random() < 0.5:
            i = rng.randrange(n)
            plain += 1               # a[i] = v: one cell
            prefix += n - i          # pre[i+1:] must be repaired
        else:
            l = rng.randrange(n)
            r = rng.randrange(l, n) + 1
            plain += r - l           # add up the stretch
            prefix += 2              # pre[r] - pre[l]
    return plain, prefix

plain, prefix = count_work(1000, 1000, 1)
print("plain list     :", plain)
print("prefix + rebuild:", prefix)
print("log2(1000) * 1000 =", 10 * 1000, "(about what a tree needs)")
```
```text
plain list     : 123924
prefix + rebuild: 247597
log2(1000) * 1000 = 10000 (about what a tree needs)
```

Both simple strategies touch over a hundred thousand cells (the prefix version more than a quarter of a million). The tree needs about ten thousand. The gap grows with `n`: at `n = 10^6` it is the difference between a program that finishes and one that does not.

### What you can do after this module

1. **Build a segment tree** recursively and iteratively, for sum, min, max and gcd, with point update and range query.
2. **Write your own node type** (for example "maximum subarray sum of this range") and merge two nodes correctly.
3. **Use lazy propagation** to add a number to a whole range, or assign a number to a whole range, in `O(log n)`.
4. **Write a Fenwick tree** (binary indexed tree) with the lowbit trick, and extend it to range updates, range sums, inversions and the k-th element.
5. **Build a sparse table** for `O(1)` range-minimum queries on static data, and explain why it fails for sums.
6. **Use square-root decomposition** and **Mo's algorithm** when a tree does not fit the question.
7. **Choose** between all of them by asking: do the values change? Is the operation a sum or a min? Can I read all queries first?

### What this module reuses

- **Prefix sums and difference arrays** are in dsa.03, sections 2 and 4. The Fenwick tree is a clever prefix-sum table that can be updated.
- **Trees, recursion on nodes** are in dsa.10 (trees), sections 1 to 4. A segment tree is a binary tree built over an array.
- **Recursion** is in dsa.07 (recursion and backtracking), sections 1 to 3. Every recursive method here splits a range in two halves.
- **Sorting and `bisect`** are in dsa.05 and dsa.06. Coordinate compression uses `sorted`; one example uses `bisect`.
- **Dynamic programming** (dsa.14) and **graphs** (dsa.12) are the prerequisites of this module. They give you the habit of reasoning about overlapping sub-problems and about "what do I store at each node?".

### Conventions in this chapter

- Arrays are 0-indexed. A range is **half-open**: `[l, r)` means positions `l, l+1, ..., r-1`, and has length `r - l`. This matches `a[l:r]` in Python. The *empty* range is `l == r`.
- `n` is the number of elements, `q` the number of queries.
- A **combine** (or **merge**) function joins the answers of two neighbouring ranges. For sums it is `+`, for minimum it is `min`.
- An **identity** is the value that changes nothing when combined: `0` for sum, `+infinity` for min, `-infinity` for max, `0` for gcd.
- Every class below has a `brute` twin in the tests: a slow, obviously correct loop. We compare the two on random data, because a data structure that is *almost* right is the worst kind of bug.

## 2. The segment tree idea

### Ranges as a tree

The sum of a stretch is the sum of two smaller stretches. And each of those is the sum of two still smaller stretches. Keep splitting in halves until a piece is one element. That is a binary tree where:

- the **root** stands for the whole array `[0, n)`;
- every **node** stands for a range `[lo, hi)` and stores the answer for that range (here: the sum);
- the **children** of `[lo, hi)` are `[lo, mid)` and `[mid, hi)` where `mid = (lo + hi) // 2`;
- the **leaves** are single elements.

Take `a = [5, 3, 8, 6, 2, 7, 4, 1]`. Each node stores the sum of its range.

```text
                       [0,8)=36
                 /                  \
          [0,4)=22                [4,8)=14
          /      \                /      \
     [0,2)=8   [2,4)=14      [4,6)=9   [6,8)=5
      /   \     /   \         /   \     /   \
     5     3   8     6       2     7   4     1
```

Check some nodes: `5+3 = 8`, `8+6 = 14`, `8+14 = 22`, `2+7 = 9`, `4+1 = 5`, `9+5 = 14`, `22+14 = 36`. The root holds the sum of everything.

### Why this makes queries fast

Suppose we want the sum of `a[2:7]`, which is `8 + 6 + 2 + 7 + 4 = 27`. We do not add five numbers. We look for the **fewest nodes whose ranges exactly cover `[2, 7)`**:

- `[2,4)` = 14 (a whole node)
- `[4,6)` = 9 (a whole node)
- `[6,7)` = 4 (the leaf for `a[6]`)

`14 + 9 + 4 = 27`. Three nodes instead of five elements. For a long range the saving is huge: any range of any length is covered by at most about `2 * log2(n)` nodes, as we will prove in section 4.

### Why this makes updates fast

When `a[3]` changes from `6` to `100`, which nodes hold a stale sum? Only those whose range **contains position 3**: the leaf, `[2,4)`, `[0,4)` and `[0,8)`. That is one node per level: `log2(n) + 1` nodes. Fix the leaf, then recompute each ancestor from its two children, going up.

```text
                       [0,8)=130   <- recomputed
                 /                  \
          [0,4)=116               [4,8)=14
          /      \                /      \
     [0,2)=8   [2,4)=108 <- recomputed    ...
      /   \     /   \
     5     3   8     100 <- changed
```

Everything outside that single path stays correct. That is the whole trick: **a query touches a few "big" nodes, an update touches one path**.

### Storing the tree in a list

We do not need node objects with pointers. A binary tree can live in a flat list, using the heap numbering you may know from dsa.11:

- the root is node `1`;
- the children of node `i` are `2*i` and `2*i + 1`;
- the parent of node `i` is `i // 2`.

For our array this gives

```text
node 1  = [0,8)
node 2  = [0,4)     node 3  = [4,8)
node 4  = [0,2)     node 5  = [2,4)     node 6  = [4,6)    node 7  = [6,8)
node 8..15 = the eight leaves, a[0] .. a[7]
```

The list `t` has `t[i]` = the answer for node `i`. Position `0` of the list is unused. That keeps the arithmetic `2*i` and `2*i+1` clean.

## 3. The recursive segment tree

### Build, query, update

Each method works on **one node** and needs to know which range that node covers, so we pass `node, lo, hi` down the recursion. This is the same "what does one call return?" thinking you practised in dsa.10, section 3.

```python
class SegTree:
    """Sum segment tree. Half-open ranges [l, r). 0-indexed."""

    def __init__(self, a):
        self.n = len(a)
        self.t = [0] * (4 * self.n)       # why 4n? see section 4
        if self.n > 0:
            self._build(1, 0, self.n, a)

    def _build(self, node, lo, hi, a):
        if hi - lo == 1:                  # a leaf: one element
            self.t[node] = a[lo]
            return
        mid = (lo + hi) // 2
        self._build(2 * node, lo, mid, a)
        self._build(2 * node + 1, mid, hi, a)
        self.t[node] = self.t[2 * node] + self.t[2 * node + 1]

    def query(self, l, r):
        """Sum of a[l:r]."""
        return self._query(1, 0, self.n, l, r)

    def _query(self, node, lo, hi, l, r):
        if r <= lo or hi <= l:            # no overlap: contributes nothing
            return 0
        if l <= lo and hi <= r:           # node range fully inside the query
            return self.t[node]
        mid = (lo + hi) // 2              # partial overlap: ask both children
        return (self._query(2 * node, lo, mid, l, r)
                + self._query(2 * node + 1, mid, hi, l, r))

    def update(self, i, v):
        """Set a[i] = v."""
        self._update(1, 0, self.n, i, v)

    def _update(self, node, lo, hi, i, v):
        if hi - lo == 1:
            self.t[node] = v
            return
        mid = (lo + hi) // 2
        if i < mid:
            self._update(2 * node, lo, mid, i, v)
        else:
            self._update(2 * node + 1, mid, hi, i, v)
        self.t[node] = self.t[2 * node] + self.t[2 * node + 1]   # fix on the way back up

a = [5, 3, 8, 6, 2, 7, 4, 1]
st = SegTree(a)
print(st.t[1:16])
print(st.query(2, 7), st.query(0, 8), st.query(3, 4), st.query(5, 5))
st.update(3, 100)
print(st.t[1:16])
print(st.query(2, 7), st.query(0, 4))
```
```text
[36, 22, 14, 8, 14, 9, 5, 5, 3, 8, 6, 2, 7, 4, 1]
27 36 6 0
[130, 116, 14, 8, 108, 9, 5, 5, 3, 8, 100, 2, 7, 4, 1]
121 116
```

The first list is `t[1]` to `t[15]`: the root `36`, then `22, 14`, then `8, 14, 9, 5`, then the eight leaves. After the update, only `t[1]`, `t[2]`, `t[5]` and `t[11]` (the leaf of `a[3]`) changed.

Read `_query`; it has three cases, and they are the heart of every segment tree:

1. **No overlap.** The node's range and the query do not touch (`r <= lo` or `hi <= l`). Return the identity (`0` for sum).
2. **Total overlap.** The node's range lies inside the query. Return the stored value. Do **not** go deeper.
3. **Partial overlap.** The node sticks out of the query. Ask both children and combine.

With half-open ranges the "no overlap" test is exactly `r <= lo or hi <= l`. Use `<=` and not `<`: the range `[4,6)` and the query `[2,4)` share no element even though `4` appears in both.

### Hand trace: which nodes does a query visit?

Let us print the visits for `query(2, 7)`. We use an indented trace so that the shape of the recursion is visible.

```python
def trace_query(t, node, lo, hi, l, r, depth=0):
    pad = "  " * depth
    if r <= lo or hi <= l:
        print(f"{pad}node {node} [{lo},{hi}): outside, skip")
        return 0
    if l <= lo and hi <= r:
        print(f"{pad}node {node} [{lo},{hi}): inside, take {t[node]}")
        return t[node]
    print(f"{pad}node {node} [{lo},{hi}): partial, split")
    mid = (lo + hi) // 2
    left = trace_query(t, 2 * node, lo, mid, l, r, depth + 1)
    right = trace_query(t, 2 * node + 1, mid, hi, l, r, depth + 1)
    return left + right

fresh = SegTree([5, 3, 8, 6, 2, 7, 4, 1])
print("answer:", trace_query(fresh.t, 1, 0, 8, 2, 7))
```
```text
node 1 [0,8): partial, split
  node 2 [0,4): partial, split
    node 4 [0,2): outside, skip
    node 5 [2,4): inside, take 14
  node 3 [4,8): partial, split
    node 6 [4,6): inside, take 9
    node 7 [6,8): partial, split
      node 14 [6,7): inside, take 4
      node 15 [7,8): outside, skip
answer: 27
```

Count the "inside" lines: they are the nodes that actually contribute. The "partial" lines are the path along the two edges of the query (the left edge at position 2 and the right edge at position 7). Everything else is cut off immediately, either as "outside" or as "inside".

### Predict the output

What does this print? Trace by hand first. (Hint: the nodes that cover `[1, 3)` are single leaves and not big nodes.)

```python
fresh = SegTree([5, 3, 8, 6, 2, 7, 4, 1])
trace_query(fresh.t, 1, 0, 8, 1, 3)
```

<details><summary>Answer</summary>

```text
node 1 [0,8): partial, split
  node 2 [0,4): partial, split
    node 4 [0,2): partial, split
      node 8 [0,1): outside, skip
      node 9 [1,2): inside, take 3
    node 5 [2,4): partial, split
      node 10 [2,3): inside, take 8
      node 11 [3,4): outside, skip
  node 3 [4,8): outside, skip
```

The query `[1, 3)` is `a[1]` and `a[2]`. They sit in different halves of `[0,4)` and in different children of it: `a[1]` is in `[0,2)`, `a[2]` is in `[2,4)`. Neither `[0,2)` nor `[2,4)` is inside the query, so both split, and we end with two leaves (`3` and `8`). The answer would be `11`. A range that straddles a split point at a high level can force many "partial" nodes.

</details>

### Edge cases for the recursive tree

```python
one = SegTree([42])
print(one.query(0, 1), one.query(0, 0))
one.update(0, 7)
print(one.query(0, 1))
empty = SegTree([])
print(empty.n, empty.t)
```
```text
42 0
7
0 []
```

- A single element is a tree of one leaf; node `1` is the root and the leaf at once.
- The empty range `query(l, l)` returns the identity `0`. The recursion may split a few times, but every leaf `[x, x+1)` satisfies `r <= x` or `x + 1 <= l`, so each leaf reports "outside" and contributes nothing.
- An empty array has `n = 0`; we skip `_build` (otherwise `hi - lo == 1` would never be true and the recursion would run forever).

## 4. How fast is it, and why `4n`?

### A query touches at most about four nodes per level

Take any level of the tree. Claim: **at most two nodes at that level are "partial"**, the rest are "outside" or "inside". Why? A partial node contains at least one query boundary (position `l` or `r`) strictly inside it. There are only two boundaries, and nodes on one level do not overlap, so at most two nodes per level are partial. Each partial node has two children, so at most four nodes are *visited* per level, and the tree has about `log2(n) + 1` levels. So a query visits `O(log n)` nodes.

Let us measure it. For `n = 100` we try **every** possible range and record the maximum number of visited nodes.

```python
def count_visits(node, lo, hi, l, r):
    if r <= lo or hi <= l:
        return 1
    if l <= lo and hi <= r:
        return 1
    mid = (lo + hi) // 2
    return 1 + count_visits(2 * node, lo, mid, l, r) + count_visits(2 * node + 1, mid, hi, l, r)

n = 100
worst = 0
for l in range(n):
    for r in range(l, n + 1):
        worst = max(worst, count_visits(1, 0, n, l, r))

levels = n.bit_length() + 1
print("n =", n, " worst visits =", worst, " 4 * levels =", 4 * levels)
```
```text
n = 100  worst visits = 27  4 * levels = 32
```

The worst case stays under the bound `4 * levels`. An update is simpler: one node per level, exactly one root-to-leaf path, `O(log n)`.

| Operation | Time | Space |
|---|---|---|
| build | `O(n)` (every node is created once, and there are fewer than `2n` of them) | |
| point update | `O(log n)` | |
| range query | `O(log n)` | |
| the structure | | `O(n)` (a list of `4n`) |

### Why do we allocate `4 * n`?

The tree over `n` elements has exactly `2n - 1` nodes (n leaves and n-1 internal nodes). But with heap numbering a node's index is **not** the number of nodes before it; when `n` is not a power of two, the tree is lopsided and some indices are skipped. The largest index used can be close to `4n`. Let us measure the biggest index that `_build` touches for every `n` from 1 to 2,000.

```python
def max_index(node, lo, hi):
    if hi - lo == 1:
        return node
    mid = (lo + hi) // 2
    return max(max_index(2 * node, lo, mid), max_index(2 * node + 1, mid, hi))

worst_ratio, worst_n = 0, 0
for n in range(1, 2001):
    top = max_index(1, 0, n)
    assert top < 4 * n, "index reached 4n"
    if top / n > worst_ratio:
        worst_ratio, worst_n = top / n, n
print("largest index / n:", round(worst_ratio, 3), "at n =", worst_n)
print("n = 5 uses up to node", max_index(1, 0, 5), "of", 4 * 5)
print("n = 8 uses up to node", max_index(1, 0, 8), "of", 4 * 8)
```
```text
largest index / n: 3.995 at n = 1025
n = 5 uses up to node 15 of 20
n = 8 uses up to node 15 of 32
```

So the biggest index stays below `4n`, and `4n` is the standard safe size. Allocating exactly `2n` crashes with `IndexError` for many `n` in this layout. The iterative tree of section 6 avoids the waste with a different numbering and uses exactly `2n`.

### A brute-force check

Never trust a data structure until it has survived random operations against a slow, plainly correct version.

```python
def check_sum_tree(trials, seed):
    rng = random.Random(seed)
    for _ in range(trials):
        n = rng.randint(1, 30)
        a = [rng.randint(-50, 50) for _ in range(n)]
        st = SegTree(a)
        for _ in range(60):
            if rng.random() < 0.4:
                i = rng.randrange(n)
                v = rng.randint(-50, 50)
                a[i] = v
                st.update(i, v)
            else:
                l = rng.randint(0, n)
                r = rng.randint(l, n)
                assert st.query(l, r) == sum(a[l:r]), f"wrong sum for [{l},{r}) on {a}"
    return "ok"

print(check_sum_tree(300, 2))
```
```text
ok
```

## 5. Other operations: min, max, gcd

### What the tree needs from the operation

Nothing in the tree was specific to sums. The tree only needs two things:

1. a **combine** function that joins the answers of two neighbouring ranges, and
2. an **identity** value for "nothing here", returned by the "no overlap" case.

The combine must be **associative**: `combine(combine(x, y), z) == combine(x, combine(y, z))`. That is what lets us group a range into any set of blocks. Sum, min, max, gcd, bitwise AND/OR/XOR, product (mod something) and string concatenation are all associative.

| Operation | combine | identity |
|---|---|---|
| sum | `x + y` | `0` |
| minimum | `min(x, y)` | `+infinity` |
| maximum | `max(x, y)` | `-infinity` |
| gcd | `math.gcd(x, y)` | `0` (because `gcd(0, x) = x`) |
| xor | `x ^ y` | `0` |
| product | `x * y % M` | `1` |

Here is the generic version. It passes the two functions in.

```python
import math

class SegTreeG:
    """Generic recursive segment tree. Point update, range query on [l, r)."""

    def __init__(self, a, combine, identity):
        self.n = len(a)
        self.f = combine
        self.e = identity
        self.t = [identity] * (4 * self.n)
        if self.n > 0:
            self._build(1, 0, self.n, a)

    def _build(self, node, lo, hi, a):
        if hi - lo == 1:
            self.t[node] = a[lo]
            return
        mid = (lo + hi) // 2
        self._build(2 * node, lo, mid, a)
        self._build(2 * node + 1, mid, hi, a)
        self.t[node] = self.f(self.t[2 * node], self.t[2 * node + 1])

    def query(self, l, r):
        return self._query(1, 0, self.n, l, r)

    def _query(self, node, lo, hi, l, r):
        if r <= lo or hi <= l:
            return self.e
        if l <= lo and hi <= r:
            return self.t[node]
        mid = (lo + hi) // 2
        return self.f(self._query(2 * node, lo, mid, l, r),
                      self._query(2 * node + 1, mid, hi, l, r))

    def update(self, i, v):
        self._update(1, 0, self.n, i, v)

    def _update(self, node, lo, hi, i, v):
        if hi - lo == 1:
            self.t[node] = v
            return
        mid = (lo + hi) // 2
        if i < mid:
            self._update(2 * node, lo, mid, i, v)
        else:
            self._update(2 * node + 1, mid, hi, i, v)
        self.t[node] = self.f(self.t[2 * node], self.t[2 * node + 1])

INF = float("inf")
a = [5, 3, 8, 6, 2, 7, 4, 1]
mn = SegTreeG(a, min, INF)
mx = SegTreeG(a, max, -INF)
gc = SegTreeG([12, 18, 30, 8, 20, 45], math.gcd, 0)
print(mn.query(0, 4), mn.query(4, 8), mn.query(2, 7))
print(mx.query(0, 4), mx.query(4, 8), mx.query(2, 7))
print(gc.query(0, 3), gc.query(2, 5), gc.query(3, 4), gc.query(5, 5))
mn.update(5, -9)
print(mn.query(2, 7), mn.query(0, 2))
```
```text
3 1 2
8 7 8
6 2 8 0
-9 3
```

Look at the last number of the gcd line: the empty range `[5, 5)` returned `0`, the identity. For minimum, an empty range would return `inf`. Decide what your problem wants for an empty range before you run it.

### Why the identity matters

Suppose we used `0` as the identity for **minimum** by mistake. Every "no overlap" branch would return `0` and the minimum of any partial query would become `0`.

```python
broken = SegTreeG([5, 3, 8, 6], min, 0)
print(broken.query(1, 3), "<- should be 3")
```
```text
0 <- should be 3
```

The identity must be a value that never wins. For min that is the largest possible value; for max the smallest; for gcd it is `0`; for sum `0`.

### A brute-force check for all four operations

```python
def check_generic(seed):
    rng = random.Random(seed)
    ops = [("min", min, INF, lambda xs: min(xs)),
           ("max", max, -INF, lambda xs: max(xs)),
           ("gcd", math.gcd, 0, lambda xs: math.gcd(*xs)),
           ("sum", lambda x, y: x + y, 0, lambda xs: sum(xs))]
    for name, f, e, brute in ops:
        for _ in range(150):
            n = rng.randint(1, 25)
            a = [rng.randint(1, 60) for _ in range(n)]
            tree = SegTreeG(a, f, e)
            for _ in range(40):
                if rng.random() < 0.4:
                    i, v = rng.randrange(n), rng.randint(1, 60)
                    a[i] = v
                    tree.update(i, v)
                else:
                    l = rng.randint(0, n - 1)
                    r = rng.randint(l + 1, n)
                    assert tree.query(l, r) == brute(a[l:r]), f"{name} wrong on [{l},{r}) of {a}"
    return "ok"

print(check_generic(3))
```
```text
ok
```

(`math.gcd(*xs)` unpacks the list into separate arguments. `gcd` of several numbers is the gcd of the gcds, which is exactly what the tree computes.)

### Try it

A "range update with set" is **not** a point update, so we cannot do it yet. But we can already do this: given `a`, answer *"how many elements in `a[l:r]` are even?"* with updates. What should the leaf store, and what is `combine`?

<details><summary>Answer</summary>

A leaf stores `1` if its value is even and `0` otherwise. `combine` is `+`, identity `0`. So the tree is the sum tree over the 0/1 array. Update `a[i]`: recompute the 0/1 flag and call `update(i, flag)`. **Any "count of things with a property" question becomes a sum over 0/1 flags.** We use this idea again with Fenwick trees.

</details>

## 6. The iterative (bottom-up) segment tree

### The idea: leaves at the end of the list

The recursive tree is easy to read, but each query makes about `4 log n` Python function calls, and a function call in Python is slow. There is a famous shorter version that has **no recursion and no `lo, hi` bookkeeping**:

- Use a list `t` of size `2n`.
- Put the `n` elements in the **second half**: `t[n + i] = a[i]`.
- Fill the first half from the end down to 1: `t[i] = combine(t[2*i], t[2*i + 1])`.

Node `i` has the children `2i` and `2i+1`, exactly as before; the difference is only that we do not insist the root is `[0, n)` split at midpoints. For `n = 8` (a power of two) the picture is the same tree as before:

```text
index:      1
          /   \
        2       3
       / \     / \
      4   5   6   7
     /\  /\  /\  /\
    8 9 10 11 12 13 14 15      <- leaves: t[8 + i] = a[i]

values:  a = [5, 3, 8, 6, 2, 7, 4, 1]
         t[8..15] = 5 3 8 6 2 7 4 1
         t[4..7]  = 8 14 9 5
         t[2..3]  = 22 14
         t[1]     = 36
```

The size is exactly `2n`, not `4n`.

### Point update: walk up

```text
update(i, v):   i += n;  t[i] = v;  while i > 1: i //= 2; t[i] = combine(t[2i], t[2i+1])
```

### Range query: walk up from both edges at once

This is the clever part. We keep two pointers `l` and `r` on the leaf level, for the half-open range `[l + n, r + n)`. At each level:

- If `l` is a **right child** (odd), then node `l` belongs to the answer, because its parent would also include the element to the left of the range. Take `t[l]` and step `l += 1`.
- If `r` is odd, then `r - 1` is a left child that belongs to the answer (half-open: `r` itself is excluded). Step `r -= 1`, take `t[r]`.
- Move both to their parents: `l //= 2`, `r //= 2`.
- Stop when `l >= r`.

The "take" order matters when the operation is not commutative (for example string concatenation or the max-subarray node in section 7): pieces taken on the left side go to the left accumulator `resl`, pieces on the right go to `resr`, and we join them at the end.

```python
class IterSeg:
    """Bottom-up segment tree. Size exactly 2n. Works for any n and any associative combine."""

    def __init__(self, a, combine, identity):
        self.n = n = len(a)
        self.f = combine
        self.e = identity
        self.t = [identity] * n + list(a)        # t[n + i] = a[i]
        for i in range(n - 1, 0, -1):
            self.t[i] = combine(self.t[2 * i], self.t[2 * i + 1])

    def update(self, i, v):
        t, f = self.t, self.f
        i += self.n
        t[i] = v
        while i > 1:
            i //= 2
            t[i] = f(t[2 * i], t[2 * i + 1])

    def query(self, l, r):
        """combine of a[l:r], in order."""
        t, f = self.t, self.f
        resl, resr = self.e, self.e
        l += self.n
        r += self.n
        while l < r:
            if l % 2 == 1:            # l is a right child: take it, move right
                resl = f(resl, t[l])
                l += 1
            if r % 2 == 1:            # r is a right child: r-1 is a left child to take
                r -= 1
                resr = f(t[r], resr)
            l //= 2
            r //= 2
        return f(resl, resr)

it = IterSeg([5, 3, 8, 6, 2, 7, 4, 1], lambda x, y: x + y, 0)
print(it.t[1:])
print(it.query(2, 7), it.query(0, 8), it.query(3, 4), it.query(6, 6))
it.update(3, 100)
print(it.query(2, 7), it.query(0, 4))
```
```text
[36, 22, 14, 8, 14, 9, 5, 5, 3, 8, 6, 2, 7, 4, 1]
27 36 6 0
121 116
```

The answers match the recursive tree: `27`, `36`, `6`, `0`, then `121`, `116`.

### Hand trace of `query(2, 7)`

We print `l`, `r` and what is taken at each level. `n = 8`, so `l` starts at `10` and `r` at `15`.

```python
def trace_iter_query(tree, l, r):
    n = tree.n
    l += n
    r += n
    print(f"start l={l} r={r}")
    level = 0
    while l < r:
        taken = []
        if l % 2 == 1:
            taken.append(f"left takes t[{l}]={tree.t[l]}")
            l += 1
        if r % 2 == 1:
            r -= 1
            taken.append(f"right takes t[{r}]={tree.t[r]}")
        l //= 2
        r //= 2
        print(f"level {level}: {', '.join(taken) or 'nothing'}; now l={l} r={r}")
        level += 1

trace_iter_query(IterSeg([5, 3, 8, 6, 2, 7, 4, 1], lambda x, y: x + y, 0), 2, 7)
```
```text
start l=10 r=15
level 0: right takes t[14]=4; now l=5 r=7
level 1: left takes t[5]=14, right takes t[6]=9; now l=3 r=3
```

At level 0, `r = 15` is odd, so the right edge takes `t[14]` (which is `a[6] = 4`, the leaf for position 6). At level 1 the left edge takes `t[5]` (the node for `[2,4)`, value 14) and the right edge takes `t[6]` (the node for `[4,6)`, value 9). Total `14 + 9 + 4 = 27`. These are exactly the three nodes the recursive version picked. The two methods are the same algorithm; the iterative one just finds the nodes from the bottom.

### It also works when `n` is not a power of two

For `n = 5` the tree is not a perfect picture: some internal nodes join pieces that are not neighbours in the array (for example node 1 may join the end and the start). That does not matter. The query loop never uses a node that crosses the border incorrectly, because it only takes nodes fully inside `[l, r)`. We test it with the **non-commutative** operation "string concatenation": any ordering mistake shows up as scrambled letters.

```python
def concat(x, y):
    return x + y

letters = list("segmenttree")
tc = IterSeg(letters, concat, "")
print(len(letters), tc.query(0, 11), tc.query(2, 7), tc.query(3, 3) == "")

def check_iter(seed):
    rng = random.Random(seed)
    for _ in range(300):
        n = rng.randint(1, 40)               # includes many non-powers of two
        s = [rng.choice("abcdef") for _ in range(n)]
        tree = IterSeg(s, concat, "")
        nums = [rng.randint(-20, 20) for _ in range(n)]
        sums = IterSeg(nums, lambda x, y: x + y, 0)
        for _ in range(40):
            if rng.random() < 0.3:
                i = rng.randrange(n)
                s[i], nums[i] = rng.choice("abcdef"), rng.randint(-20, 20)
                tree.update(i, s[i])
                sums.update(i, nums[i])
            else:
                l = rng.randint(0, n)
                r = rng.randint(l, n)
                assert tree.query(l, r) == "".join(s[l:r]), f"order broken on [{l},{r}) of {s}"
                assert sums.query(l, r) == sum(nums[l:r]), f"sum broken on [{l},{r})"
    return "ok"

print(check_iter(4))
```
```text
11 segmenttree gment True
ok
```

### Recursive or iterative?

| | Recursive (section 3) | Iterative (section 6) |
|---|---|---|
| Size | `4n` | `2n` |
| Code | longer, passes `node, lo, hi` | shorter |
| Speed in Python | slower (many calls) | faster (a loop) |
| Lazy propagation (range updates) | natural | harder; usually recursive |
| "Descend to the first position where ..." | natural | possible but fiddly |

Use the iterative tree for **point update + range query**. Use the recursive tree when you need lazy propagation or a descent. The next sections do both.

## 7. Custom nodes: the tree stores whatever you can merge

### The principle

So far a node stored one number. A node can store a **small record**, as long as you can answer: *given the records of two neighbouring ranges, what is the record of the joined range?* That function is the `combine`.

Think of it as designing a tiny summary of a range that is just rich enough to be merged.

### Example 1: maximum subarray sum on a range

In dsa.03, section 9, Kadane's algorithm found the best subarray of one list. Now the question is: *what is the largest sum of a non-empty contiguous piece inside `a[l:r]`?* with updates. Kadane runs in `O(r - l)`. A tree needs `O(log n)`.

What must a node remember? The best subarray of the joined range is one of three things: the best inside the left part, the best inside the right part, or one that **crosses the middle** (a suffix of the left part glued to a prefix of the right part). To compute a crossing one, each node must remember its best prefix and best suffix. And to compute the new best prefix we need the total of the left part. So the record is four numbers:

```text
node = (total, best_prefix, best_suffix, best)
total        sum of the whole range
best_prefix  largest sum of a prefix a[lo:k] (non-empty)
best_suffix  largest sum of a suffix a[k:hi] (non-empty)
best         largest sum of any non-empty piece
```

Merging `x` (left) and `y` (right):

```text
total        = x.total + y.total
best_prefix  = max(x.best_prefix, x.total + y.best_prefix)
best_suffix  = max(y.best_suffix, y.total + x.best_suffix)
best         = max(x.best, y.best, x.best_suffix + y.best_prefix)
```

The prefix of the joined range either stays inside `x`, or takes all of `x` and continues into `y`. The best crossing piece joins the best suffix of `x` with the best prefix of `y`. A leaf holding `v` is `(v, v, v, v)`: the piece must be non-empty, so even for a negative `v` the best is `v`, not `0`.

The identity is `(0, -inf, -inf, -inf)`: it has total `0` and no valid non-empty pieces.

```python
NEG = float("-inf")

def merge_best(x, y):
    return (x[0] + y[0],
            max(x[1], x[0] + y[1]),
            max(y[2], y[0] + x[2]),
            max(x[3], y[3], x[2] + y[1]))

EMPTY = (0, NEG, NEG, NEG)

def leaf(v):
    return (v, v, v, v)

vals = [2, -5, 4, -1, 3, -6, 5]
mst = IterSeg([leaf(v) for v in vals], merge_best, EMPTY)
print(mst.query(0, 7))
print(mst.query(0, 2), mst.query(2, 5), mst.query(5, 7))
print("best in [0,7):", mst.query(0, 7)[3], " best in [2,5):", mst.query(2, 5)[3])
mst.update(1, leaf(10))
print("after a[1] = 10, best in [0,7):", mst.query(0, 7)[3])
```
```text
(2, 3, 5, 6)
(-3, 2, -3, 2) (6, 6, 6, 6) (-1, -1, 5, 5)
best in [0,7): 6  best in [2,5): 6
after a[1] = 10, best in [0,7): 18
```

Check `[2, 5)`: the values are `4, -1, 3`. The best piece is the whole thing, `4 - 1 + 3 = 6`. The record `(6, 6, 6, 6)` says total 6, best prefix 6, best suffix 6, best 6. Look at `[0, 2)` = `2, -5`: total `-3`, best prefix `2` (just the `2`), best suffix `-5`, best `2`.

Because merging is **not commutative** (left and right play different roles), the iterative tree's `resl` / `resr` split from section 6 is exactly what keeps this correct. Now the brute-force check:

```python
def brute_best(xs):
    best = xs[0]
    for i in range(len(xs)):
        s = 0
        for j in range(i, len(xs)):
            s += xs[j]
            best = max(best, s)
    return best

def check_best(seed):
    rng = random.Random(seed)
    for _ in range(200):
        n = rng.randint(1, 20)
        v = [rng.randint(-9, 9) for _ in range(n)]
        tree = IterSeg([leaf(x) for x in v], merge_best, EMPTY)
        for _ in range(30):
            if rng.random() < 0.4:
                i, x = rng.randrange(n), rng.randint(-9, 9)
                v[i] = x
                tree.update(i, leaf(x))
            else:
                l = rng.randint(0, n - 1)
                r = rng.randint(l + 1, n)
                assert tree.query(l, r)[3] == brute_best(v[l:r]), f"wrong best on [{l},{r}) of {v}"
    return "ok"

print(check_best(5))
```
```text
ok
```

### Example 2: counting zeros, and finding the k-th zero

Here the record is a single number, but we add a new kind of operation: **descent**. Let every leaf be `1` if `a[i] == 0` and `0` otherwise; the node stores the number of zeros in its range. Then *"where is the k-th zero?"* is a walk from the root: if the left child has at least `k` zeros, go left; otherwise subtract the left count from `k` and go right.

We make the size a power of two so that the leaf index minus the size is the position.

```python
class ZeroCounter:
    def __init__(self, a):
        self.size = 1
        while self.size < len(a):
            self.size *= 2
        self.t = [0] * (2 * self.size)
        for i, x in enumerate(a):
            self.t[self.size + i] = 1 if x == 0 else 0
        for i in range(self.size - 1, 0, -1):
            self.t[i] = self.t[2 * i] + self.t[2 * i + 1]

    def set(self, i, x):
        i += self.size
        self.t[i] = 1 if x == 0 else 0
        while i > 1:
            i //= 2
            self.t[i] = self.t[2 * i] + self.t[2 * i + 1]

    def total(self):
        return self.t[1]

    def kth_zero(self, k):
        """Position of the k-th zero (k = 1 is the first), or -1 if there are fewer than k."""
        if k < 1 or k > self.t[1]:
            return -1
        node = 1
        while node < self.size:            # until we reach a leaf
            if self.t[2 * node] >= k:      # enough zeros on the left
                node = 2 * node
            else:                          # skip the left zeros, go right
                k -= self.t[2 * node]
                node = 2 * node + 1
        return node - self.size

zc = ZeroCounter([3, 0, 5, 0, 0, 7, 0, 2, 0])
print(zc.total(), [zc.kth_zero(k) for k in range(1, 7)])
zc.set(2, 0)
zc.set(3, 9)
print(zc.total(), [zc.kth_zero(k) for k in range(1, 7)], zc.kth_zero(0))
```
```text
5 [1, 3, 4, 6, 8, -1]
5 [1, 2, 4, 6, 8, -1] -1
```

The zeros of `[3,0,5,0,0,7,0,2,0]` are at positions 1, 3, 4, 6, 8. After `set(2, 0)` and `set(3, 9)` they are at 1, 2, 4, 6, 8. The descent costs `O(log n)`: one step per level, no recursion. We will see the same descent on a Fenwick tree in section 13.

### Designing a node: a checklist

1. What question do I need to answer for a range?
2. What smaller facts about each half are needed to answer it for the joined range?
3. Write `combine(left, right)`. Does it depend on the order? If yes, mark it non-commutative.
4. Write the identity so that `combine(identity, x) == x == combine(x, identity)`. Test it.
5. Write the brute force and compare on random data.

Other classic nodes: *(min, count of the min)* to count how many times the minimum appears; *(gcd, count of elements equal to the gcd)*; *(sum, sum of squares)* for variance; a 2x2 matrix for a linear recurrence; the *longest run of equal values* record (prefix run, suffix run, best, length).

### Try it

For the "minimum and how many times it occurs" node, write `combine` for `(m, c)` pairs.

<details><summary>Answer</summary>

```python
def merge_min_count(x, y):
    if x[0] < y[0]:
        return x
    if y[0] < x[0]:
        return y
    return (x[0], x[1] + y[1])      # equal minimums: add the counts
```

A leaf with value `v` is `(v, 1)`. The identity is `(inf, 0)`. The order of `x` and `y` does not matter here, so this combine is commutative.

</details>

## 8. Lazy propagation: range updates

### The new problem

The tree so far changes **one** element at a time. What about *"add 10 to every element of `a[l:r]`"*? With a point update per element it costs `(r - l) * log n`, as slow as the plain list. We want `O(log n)` for the whole range.

Look at what a **query** does: it covers `[l, r)` with a few big nodes. An **update** can do the same! Cover `[l, r)` with the same few nodes, and update only those nodes. A node whose whole range gets `+10` simply has its stored sum increased by `10 * (hi - lo)`. But its children now hold stale numbers.

### The lazy idea

> Do the work for a node now, and leave a **note** for its children. Deliver the note later, only if somebody needs to look inside.

That note is the **lazy tag** `lz[node]`: "every element under me still owes `+lz`; my own sum is already correct, my children's sums are not". Three rules:

1. **Apply** a value `v` to a node: `s[node] += v * (hi - lo)` and `lz[node] += v`.
2. **Push down** (deliver the note) just before we descend to the children: apply `lz[node]` to both children, then clear it.
3. After the children return, **recompute** `s[node]` from them (as in the point update).

The rule that decides correctness: **push down before you look into or change a node's children.** Both `add` and `query` must push, because a query that descends reads the children.

```python
class LazySeg:
    """Range add, range sum. Half-open [l, r)."""

    def __init__(self, a):
        self.n = len(a)
        self.s = [0] * (4 * self.n)     # s[node]  = true sum of the node's range
        self.lz = [0] * (4 * self.n)    # lz[node] = pending +value for the children
        if self.n > 0:
            self._build(1, 0, self.n, a)

    def _build(self, node, lo, hi, a):
        if hi - lo == 1:
            self.s[node] = a[lo]
            return
        mid = (lo + hi) // 2
        self._build(2 * node, lo, mid, a)
        self._build(2 * node + 1, mid, hi, a)
        self.s[node] = self.s[2 * node] + self.s[2 * node + 1]

    def _apply(self, node, lo, hi, v):
        self.s[node] += v * (hi - lo)
        self.lz[node] += v

    def _push(self, node, lo, hi):
        if self.lz[node] != 0:
            mid = (lo + hi) // 2
            self._apply(2 * node, lo, mid, self.lz[node])
            self._apply(2 * node + 1, mid, hi, self.lz[node])
            self.lz[node] = 0

    def add(self, l, r, v):
        self._add(1, 0, self.n, l, r, v)

    def _add(self, node, lo, hi, l, r, v):
        if r <= lo or hi <= l:
            return
        if l <= lo and hi <= r:
            self._apply(node, lo, hi, v)        # stop here and leave a note
            return
        self._push(node, lo, hi)                # deliver the note before descending
        mid = (lo + hi) // 2
        self._add(2 * node, lo, mid, l, r, v)
        self._add(2 * node + 1, mid, hi, l, r, v)
        self.s[node] = self.s[2 * node] + self.s[2 * node + 1]

    def query(self, l, r):
        return self._query(1, 0, self.n, l, r)

    def _query(self, node, lo, hi, l, r):
        if r <= lo or hi <= l:
            return 0
        if l <= lo and hi <= r:
            return self.s[node]
        self._push(node, lo, hi)                # a query that descends must push too
        mid = (lo + hi) // 2
        return self._query(2 * node, lo, mid, l, r) + self._query(2 * node + 1, mid, hi, l, r)

lazy = LazySeg([5, 3, 8, 6, 2, 7, 4, 1])
print(lazy.query(0, 8), lazy.query(2, 7))
lazy.add(1, 6, 10)             # positions 1..5 get +10
print(lazy.query(0, 8), lazy.query(2, 7), lazy.query(0, 1), lazy.query(5, 6))
lazy.add(0, 8, -1)             # the whole array gets -1
print(lazy.query(0, 8), lazy.query(3, 4))
```
```text
36 27
86 67 5 17
78 15
```

Check by hand: before, the total is `36`. Adding `10` to five positions raises it by `50` (86), and `-1` to eight positions lowers it by 8 (78). The single value `a[3]` was `6`, got `+10` and `-1`, so it is `15`.

### A trace you can follow on four elements

Let us watch the arrays `s` and `lz` for `a = [2, 4, 6, 8]` (nodes 1 to 7: `1 = [0,4)`, `2 = [0,2)`, `3 = [2,4)`, `4..7` are the leaves).

```python
def dump(tree, title):
    print(title)
    print("  node :", " ".join(f"{i:>3}" for i in range(1, 8)))
    print("  s    :", " ".join(f"{tree.s[i]:>3}" for i in range(1, 8)))
    print("  lz   :", " ".join(f"{tree.lz[i]:>3}" for i in range(1, 8)))

tr = LazySeg([2, 4, 6, 8])
dump(tr, "start")
tr.add(1, 4, 10)
dump(tr, "after add(1, 4, +10)")
print("query(2, 3) =", tr.query(2, 3))
dump(tr, "after query(2, 3)")
```
```text
start
  node :   1   2   3   4   5   6   7
  s    :  20   6  14   2   4   6   8
  lz   :   0   0   0   0   0   0   0
after add(1, 4, +10)
  node :   1   2   3   4   5   6   7
  s    :  50  16  34   2  14   6   8
  lz   :   0   0  10   0  10   0   0
query(2, 3) = 16
after query(2, 3)
  node :   1   2   3   4   5   6   7
  s    :  50  16  34   2  14  16  18
  lz   :   0   0   0   0  10  10  10
```

Follow the first update. The range `[1, 4)` is covered by the leaf `[1,2)` (node 5) and by the whole node `[2,4)` (node 3). Node 3 got `s = 14 + 10 * 2 = 34` and `lz = 10`; its leaves (nodes 6 and 7) still say `6` and `8`: **stale on purpose**. Now `query(2, 3)` wants node 6. To reach it, it descends through node 3, which pushes the note: nodes 6 and 7 become `16` and `18`, and `lz[3]` returns to `0`. The two leaves received the note only when someone needed them.

(Leaves also collect a `lz` value, as node 5 shows. It is never used, because a leaf has no children. That is harmless; some implementations skip it.)

### What happens if you forget to push?

Let us break the class on purpose, to see the failure.

```python
class NoPush(LazySeg):
    def _push(self, node, lo, hi):
        pass                                   # forgot to deliver notes

good = LazySeg([2, 4, 6, 8])
bad = NoPush([2, 4, 6, 8])
for tree in (good, bad):
    tree.add(0, 4, 10)       # note sits on the root
    tree.add(1, 2, 5)        # needs to go inside; should push first
print("good:", [good.query(i, i + 1) for i in range(4)])
print("bad :", [bad.query(i, i + 1) for i in range(4)])
```
```text
good: [12, 19, 16, 18]
bad : [2, 9, 6, 8]
```

The `bad` tree reports `[2, 9, 6, 8]` instead of the true `[12, 19, 16, 18]`: the notes were never delivered, so every `+10` below the root is lost. A missing push does not crash. It quietly gives wrong numbers, and only for some ranges, so a small hand test can pass. That is why we always compare with a brute force.

### Brute-force check

```python
def check_lazy(seed):
    rng = random.Random(seed)
    for _ in range(300):
        n = rng.randint(1, 25)
        a = [rng.randint(-20, 20) for _ in range(n)]
        tree = LazySeg(a)
        for _ in range(50):
            l = rng.randint(0, n - 1)
            r = rng.randint(l + 1, n)
            if rng.random() < 0.5:
                v = rng.randint(-9, 9)
                tree.add(l, r, v)
                for i in range(l, r):
                    a[i] += v
            else:
                assert tree.query(l, r) == sum(a[l:r]), f"wrong sum [{l},{r}) of {a}"
    return "ok"

print(check_lazy(6))
```
```text
ok
```

### Cost

Both operations visit `O(log n)` nodes, like the plain tree: the same "at most two partial nodes per level" argument holds, and `_push` is `O(1)`. Space is `O(n)` (two lists of `4n`). The structure is exactly twice as large as before, plus a few more lines of code.

### Predict the output

```python
t = LazySeg([1, 1, 1, 1])
t.add(0, 4, 2)
t.add(0, 2, 3)
t.add(1, 3, 100)
print([t.query(i, i + 1) for i in range(4)])
print(t.query(0, 4))
```

<details><summary>Answer</summary>

```text
[6, 106, 103, 3]
218
```

Every element starts at `1`. The three updates add: `+2` to all, `+3` to positions 0 and 1, `+100` to positions 1 and 2. So `a[0] = 1+2+3 = 6`, `a[1] = 1+2+3+100 = 106`, `a[2] = 1+2+100 = 103`, `a[3] = 1+2 = 3`. The total is `6 + 106 + 103 + 3 = 218`. The tree gets this without ever touching all four leaves in one update.

</details>

## 9. Lazy propagation with other tags

### What the tag must be able to do

For "add and sum" the tag was a number and we could add tags together. In general, a lazy tree needs four things:

1. A **node value** (the answer for the range) and a **tag** (the pending change).
2. `apply(tag, node)`: how the tag changes the node's value. For add + sum: `value += tag * length`. For add + min: `value += tag` (no length factor).
3. **Composition** of tags: if a node already has a tag and gets a new one, what is the single tag that means "first the old, then the new"?
4. A **no-tag** marker.

The composition rule is where errors hide. Three cases follow.

### Range add, range min

Now `apply` does not multiply by the length. If every element in the range gets `+v`, the minimum gets `+v`.

```python
class LazyMinAdd:
    """Range add, range minimum. Half-open [l, r)."""

    def __init__(self, a):
        self.n = len(a)
        self.mn = [INF] * (4 * self.n)
        self.lz = [0] * (4 * self.n)
        if self.n > 0:
            self._build(1, 0, self.n, a)

    def _build(self, node, lo, hi, a):
        if hi - lo == 1:
            self.mn[node] = a[lo]
            return
        mid = (lo + hi) // 2
        self._build(2 * node, lo, mid, a)
        self._build(2 * node + 1, mid, hi, a)
        self.mn[node] = min(self.mn[2 * node], self.mn[2 * node + 1])

    def _apply(self, node, v):
        self.mn[node] += v          # the minimum moves by v; no length factor
        self.lz[node] += v

    def _push(self, node):
        if self.lz[node] != 0:
            self._apply(2 * node, self.lz[node])
            self._apply(2 * node + 1, self.lz[node])
            self.lz[node] = 0

    def add(self, l, r, v):
        self._add(1, 0, self.n, l, r, v)

    def _add(self, node, lo, hi, l, r, v):
        if r <= lo or hi <= l:
            return
        if l <= lo and hi <= r:
            self._apply(node, v)
            return
        self._push(node)
        mid = (lo + hi) // 2
        self._add(2 * node, lo, mid, l, r, v)
        self._add(2 * node + 1, mid, hi, l, r, v)
        self.mn[node] = min(self.mn[2 * node], self.mn[2 * node + 1])

    def query(self, l, r):
        return self._query(1, 0, self.n, l, r)

    def _query(self, node, lo, hi, l, r):
        if r <= lo or hi <= l:
            return INF
        if l <= lo and hi <= r:
            return self.mn[node]
        self._push(node)
        mid = (lo + hi) // 2
        return min(self._query(2 * node, lo, mid, l, r), self._query(2 * node + 1, mid, hi, l, r))

lm = LazyMinAdd([5, 3, 8, 6, 2, 7, 4, 1])
print(lm.query(0, 8), lm.query(0, 4))
lm.add(4, 8, 10)
print(lm.query(0, 8), lm.query(4, 8))
lm.add(0, 4, -4)
print(lm.query(0, 8), lm.query(0, 4), lm.query(2, 3))
```
```text
1 3
3 11
-1 -1 4
```

### Range assign, range sum: a tag that is not a number

Now an update says *"set every element of `a[l:r]` to `v`"*. The tag is the value `v`, and "no tag" must be told apart from every legal value. This is the first trap.

**Do not use `0` as "no tag"**: `0` is a perfectly good value to assign. Use `None`.

```python
class LazyAssign:
    """Range assign, range sum. Half-open [l, r)."""

    def __init__(self, a):
        self.n = len(a)
        self.s = [0] * (4 * self.n)
        self.tag = [None] * (4 * self.n)       # None means "no pending assignment"
        if self.n > 0:
            self._build(1, 0, self.n, a)

    def _build(self, node, lo, hi, a):
        if hi - lo == 1:
            self.s[node] = a[lo]
            return
        mid = (lo + hi) // 2
        self._build(2 * node, lo, mid, a)
        self._build(2 * node + 1, mid, hi, a)
        self.s[node] = self.s[2 * node] + self.s[2 * node + 1]

    def _apply(self, node, lo, hi, v):
        self.s[node] = v * (hi - lo)           # assignment REPLACES the sum
        self.tag[node] = v                     # and replaces any older pending tag

    def _push(self, node, lo, hi):
        if self.tag[node] is not None:         # "is not None", never "if self.tag[node]:"
            mid = (lo + hi) // 2
            self._apply(2 * node, lo, mid, self.tag[node])
            self._apply(2 * node + 1, mid, hi, self.tag[node])
            self.tag[node] = None

    def assign(self, l, r, v):
        self._assign(1, 0, self.n, l, r, v)

    def _assign(self, node, lo, hi, l, r, v):
        if r <= lo or hi <= l:
            return
        if l <= lo and hi <= r:
            self._apply(node, lo, hi, v)
            return
        self._push(node, lo, hi)
        mid = (lo + hi) // 2
        self._assign(2 * node, lo, mid, l, r, v)
        self._assign(2 * node + 1, mid, hi, l, r, v)
        self.s[node] = self.s[2 * node] + self.s[2 * node + 1]

    def query(self, l, r):
        return self._query(1, 0, self.n, l, r)

    def _query(self, node, lo, hi, l, r):
        if r <= lo or hi <= l:
            return 0
        if l <= lo and hi <= r:
            return self.s[node]
        self._push(node, lo, hi)
        mid = (lo + hi) // 2
        return self._query(2 * node, lo, mid, l, r) + self._query(2 * node + 1, mid, hi, l, r)

la = LazyAssign([5, 3, 8, 6, 2, 7, 4, 1])
la.assign(2, 6, 9)
print(la.query(0, 8), la.query(2, 6), la.query(1, 3))
la.assign(0, 8, 0)                  # assigning ZERO is a real update
print(la.query(0, 8))
la.assign(3, 5, 4)
print(la.query(0, 8), la.query(4, 5))
```
```text
49 36 12
0
8 4
```

The composition rule here is the simplest possible: **the newer assignment replaces the older**. `_apply` overwrites both `s` and the tag. If you had used `if self.tag[node]:` in `_push`, the assignment of `0` would be forgotten and the second print would show the old sum.

### Add and assign together

Real problems often have both: *"add `v` to a range"*, *"assign `v` to a range"*, and *"sum of a range"*. Now the tag has two parts and the order of operations matters. Think of a node's tag as **"first assign `x` (or nothing), then add `d`"**.

Compose with a new operation:

- **New assign `y`**: it wipes everything before it. The tag becomes `(assign y, add 0)`.
- **New add `e`**: if the tag already has an assignment `x`, the result is `(assign x + e, add 0)`, because assigning `x` then adding `e` is the same as assigning `x + e`. If there is no assignment, just `add d + e`.

So we never keep both an assignment and a non-zero add: the state is either "assign x" or "add d".

```python
class LazyMix:
    """Range assign, range add, range sum. Half-open [l, r)."""

    def __init__(self, a):
        self.n = len(a)
        self.s = [0] * (4 * self.n)
        self.setv = [None] * (4 * self.n)    # pending assignment, or None
        self.addv = [0] * (4 * self.n)       # pending add (only used when setv is None)
        if self.n > 0:
            self._build(1, 0, self.n, a)

    def _build(self, node, lo, hi, a):
        if hi - lo == 1:
            self.s[node] = a[lo]
            return
        mid = (lo + hi) // 2
        self._build(2 * node, lo, mid, a)
        self._build(2 * node + 1, mid, hi, a)
        self.s[node] = self.s[2 * node] + self.s[2 * node + 1]

    def _apply_set(self, node, lo, hi, y):
        self.s[node] = y * (hi - lo)
        self.setv[node] = y
        self.addv[node] = 0

    def _apply_add(self, node, lo, hi, e):
        self.s[node] += e * (hi - lo)
        if self.setv[node] is not None:
            self.setv[node] += e            # assign x, then add e == assign x + e
        else:
            self.addv[node] += e

    def _push(self, node, lo, hi):
        mid = (lo + hi) // 2
        if self.setv[node] is not None:
            self._apply_set(2 * node, lo, mid, self.setv[node])
            self._apply_set(2 * node + 1, mid, hi, self.setv[node])
            self.setv[node] = None
        elif self.addv[node] != 0:
            self._apply_add(2 * node, lo, mid, self.addv[node])
            self._apply_add(2 * node + 1, mid, hi, self.addv[node])
            self.addv[node] = 0

    def update(self, l, r, kind, v):
        """kind is 'set' or 'add'."""
        self._update(1, 0, self.n, l, r, kind, v)

    def _update(self, node, lo, hi, l, r, kind, v):
        if r <= lo or hi <= l:
            return
        if l <= lo and hi <= r:
            if kind == "set":
                self._apply_set(node, lo, hi, v)
            else:
                self._apply_add(node, lo, hi, v)
            return
        self._push(node, lo, hi)
        mid = (lo + hi) // 2
        self._update(2 * node, lo, mid, l, r, kind, v)
        self._update(2 * node + 1, mid, hi, l, r, kind, v)
        self.s[node] = self.s[2 * node] + self.s[2 * node + 1]

    def query(self, l, r):
        return self._query(1, 0, self.n, l, r)

    def _query(self, node, lo, hi, l, r):
        if r <= lo or hi <= l:
            return 0
        if l <= lo and hi <= r:
            return self.s[node]
        self._push(node, lo, hi)
        mid = (lo + hi) // 2
        return self._query(2 * node, lo, mid, l, r) + self._query(2 * node + 1, mid, hi, l, r)

def check_lazy_all(seed):
    rng = random.Random(seed)
    for _ in range(300):
        n = rng.randint(1, 20)
        a = [rng.randint(-9, 9) for _ in range(n)]
        t_min, t_asg, t_mix = LazyMinAdd(a), LazyAssign(a), LazyMix(a)
        b_min, b_asg, b_mix = a[:], a[:], a[:]
        for _ in range(40):
            l = rng.randint(0, n - 1)
            r = rng.randint(l + 1, n)
            v = rng.randint(-9, 9)
            kind = rng.choice(["q", "add", "set"])
            if kind == "add":
                t_min.add(l, r, v)
                t_mix.update(l, r, "add", v)
                for i in range(l, r):
                    b_min[i] += v
                    b_mix[i] += v
            elif kind == "set":
                t_asg.assign(l, r, v)
                t_mix.update(l, r, "set", v)
                for i in range(l, r):
                    b_asg[i] = v
                    b_mix[i] = v
            else:
                assert t_min.query(l, r) == min(b_min[l:r]), "add+min wrong"
                assert t_asg.query(l, r) == sum(b_asg[l:r]), "assign+sum wrong"
                assert t_mix.query(l, r) == sum(b_mix[l:r]), "mix wrong: tag composition"
    return "ok"

print(check_lazy_all(7))
mixed = LazyMix([1, 2, 3, 4])
mixed.update(0, 4, "set", 5)
mixed.update(1, 3, "add", 10)
mixed.update(0, 2, "set", 0)
mixed.update(2, 4, "add", 1)
print([mixed.query(i, i + 1) for i in range(4)], mixed.query(0, 4))
```
```text
ok
[0, 0, 16, 6] 22
```

Trace the last four lines by hand: start `[1,2,3,4]`; set all to 5 gives `[5,5,5,5]`; add 10 to positions 1 and 2 gives `[5,15,15,5]`; set positions 0,1 to 0 gives `[0,0,15,5]`; add 1 to positions 2 and 3 gives `[0,0,16,6]`, total `22`.

### The recipe for any lazy tree

```text
node value  : the answer for the range, ALREADY including this node's pending tag
tag         : what the children still owe
apply(node, tag)   : update value, then combine tag into node's pending tag
push(node)         : apply(child, tag) for both children; clear tag
update walk  : partial overlap -> push, recurse, recompute value from children
query walk   : partial overlap -> push, recurse, combine
```

If the value of a range is not a simple function of the tag and the length (for example "number of increasing pairs"), lazy propagation may not be possible. A requirement is that the tag can be applied to a node **without looking at its children**.

### Try it

What breaks if `_push` for `LazyMix` handled the `addv` branch first and the `setv` branch second (both with `if`, not `if ... elif`)?

<details><summary>Answer</summary>

By design the state is *either* an assignment *or* an add, so with the invariant kept it would not break. But if some code path left both non-zero, the order matters: "assign then add" and "add then assign" give different results. For example, add 3 and then assign 7 gives 7; assign 7 and then add 3 gives 10. Keeping the invariant (an assign wipes the add, an add merges into the assign) is what makes one tag enough.

</details>

## 10. The Fenwick tree (binary indexed tree)

### Why another structure?

A segment tree is flexible, but for the most common job, **point update and prefix or range sum**, it is heavy: `2n` or `4n` cells, recursion or a long loop, and lots of code. In 1994 Peter Fenwick showed a trick that does the same job with **one list of `n + 1` numbers, two three-line loops** and a very small constant. It is called the **Fenwick tree** or **binary indexed tree** (BIT).

Its limit: it answers **prefix** questions for operations that can be *undone* (sum, xor, counts). A range sum is `prefix(r) - prefix(l)`, which needs subtraction. It cannot do range minimum with updates. That price buys speed and brevity.

### The key: the lowest set bit

Write an index in binary. The **lowbit** of `i` is the value of its lowest `1` bit.

| `i` | binary | lowbit(i) |
|---|---|---|
| 12 | `1100` | 4 |
| 10 | `1010` | 2 |
| 7 | `0111` | 1 |
| 8 | `1000` | 8 |

In Python, `i & -i` gives it. Why? In two's complement, `-i` is "flip all the bits of `i`, then add 1". Flipping turns the trailing zeros into ones; adding 1 carries through them and lands exactly on the lowest set bit; bits above it stay flipped. So `i` and `-i` agree only at the lowest set bit, and `&` keeps only that. (Bit tricks are in dsa.02.)

```python
for i in (12, 10, 7, 8, 1, 6):
    print(f"i={i:>2}  {i:>04b}  -i (8 bits)={(-i) & 0xFF:08b}  i & -i = {i & -i}")
```
```text
i=12  1100  -i (8 bits)=11110100  i & -i = 4
i=10  1010  -i (8 bits)=11110110  i & -i = 2
i= 7  0111  -i (8 bits)=11111001  i & -i = 1
i= 8  1000  -i (8 bits)=11111000  i & -i = 8
i= 1  0001  -i (8 bits)=11111111  i & -i = 1
i= 6  0110  -i (8 bits)=11111010  i & -i = 2
```

### What each cell stores

Use **1-indexed positions** `1..n`. Cell `t[i]` stores the sum of the **`lowbit(i)` elements that end at position `i`**: that is the range `(i - lowbit(i), i]`.

- `t[1]` covers 1 element, `a1`.
- `t[2]` covers 2 elements, `a1..a2`.
- `t[3]` covers 1 element, `a3`. `t[4]` covers 4, `a1..a4`.
- `t[6]` (`110`, lowbit 2) covers 2 elements, `a5..a6`.
- `t[8]` covers 8 elements.

Here is the picture, drawn by code for `n = 16` (each bar is the range one cell covers):

```python
def fenwick_picture(n):
    width = 4
    print("pos   " + "".join(f"{i:<{width}}" for i in range(1, n + 1)))
    for i in sorted(range(1, n + 1), key=lambda x: (-(x & -x), x)):
        lo = i - (i & -i)                 # cell covers positions lo+1 .. i
        bar = "[" + "-" * (width * (i & -i) - 3) + "]" if (i & -i) > 1 else "[]"
        print(f"t[{i:>2}] " + " " * (width * lo) + bar)

fenwick_picture(16)
```
```text
pos   1   2   3   4   5   6   7   8   9   10  11  12  13  14  15  16  
t[16] [-------------------------------------------------------------]
t[ 8] [-----------------------------]
t[ 4] [-------------]
t[12]                                 [-------------]
t[ 2] [-----]
t[ 6]                 [-----]
t[10]                                 [-----]
t[14]                                                 [-----]
t[ 1] []
t[ 3]         []
t[ 5]                 []
t[ 7]                         []
t[ 9]                                 []
t[11]                                         []
t[13]                                                 []
t[15]                                                         []
```

Read it as stacked bars. The long bar `t[16]` covers everything. `t[8]` covers 1 to 8, `t[12]` covers 9 to 12, `t[14]` covers 13 and 14, and the odd cells cover only themselves. Two facts to notice:

1. The bars are **nested or disjoint**, never partly overlapping: the structure is a hidden tree.
2. A prefix `1..13` can be tiled by **a few bars laid end to end**: `t[8]` (1-8), then `t[12]` (9-12), then `t[13]` (13). That is the query.

### Prefix query: drop the lowest bit

To get `a1 + ... + a13`, start at 13 (`1101`), take `t[13]`, which covers just position 13. We still need 1..12. Remove the lowest bit: `13 - 1 = 12` (`1100`). Take `t[12]` (covers 9..12). Remove the lowest bit: `12 - 4 = 8` (`1000`). Take `t[8]` (covers 1..8). Remove the lowest bit: 0. Stop.

```text
prefix(i):  total = 0
            while i > 0:
                total += t[i]
                i -= i & -i          # remove the lowest set bit
```

The number of steps is the number of `1` bits in `i`, at most `log2(n) + 1`.

### Point update: add the lowbit

When `a_i` changes by `v`, which cells contain position `i`? `t[i]` itself, then the next bar that is long enough to also cover it: `i + lowbit(i)`. And then `i + lowbit(i)` of that, and so on, until we pass `n`.

```text
add(i, v):  while i <= n:
                t[i] += v
                i += i & -i          # jump to the next bar that covers i
```

Update of position 5 (`101`): `5 -> 6 (110) -> 8 (1000) -> 16`. The cells `t[5]`, `t[6]`, `t[8]`, `t[16]` all contain position 5, and no others do.

### The class

We keep the user interface **0-indexed and half-open**, so that it matches the rest of this chapter, and hide the 1-indexing inside. The method `prefix(r)` is "the sum of the first `r` elements", which is `a[0:r]`, and `r` doubles as the 1-indexed position of the last included element.

```python
class Fenwick:
    """Point add, prefix sum. Public interface 0-indexed, half-open."""

    def __init__(self, n, a=None):
        self.n = n
        self.t = [0] * (n + 1)              # t[0] is never used
        if a is not None:                   # O(n) build, see below
            for i in range(1, n + 1):
                self.t[i] += a[i - 1]
                j = i + (i & -i)
                if j <= n:
                    self.t[j] += self.t[i]

    def add(self, i, v):
        """a[i] += v"""
        i += 1                              # to 1-indexed
        while i <= self.n:
            self.t[i] += v
            i += i & -i

    def prefix(self, r):
        """Sum of a[0:r]."""
        total = 0
        while r > 0:
            total += self.t[r]
            r -= r & -r
        return total

    def range_sum(self, l, r):
        """Sum of a[l:r]."""
        return self.prefix(r) - self.prefix(l)

    def get(self, i):
        return self.range_sum(i, i + 1)

    def set(self, i, v):
        self.add(i, v - self.get(i))

a = [5, 3, 8, 6, 2, 7, 4, 1]
fw = Fenwick(8, a)
print(fw.t[1:])
print(fw.prefix(8), fw.prefix(4), fw.range_sum(2, 7), fw.range_sum(3, 3))
fw.add(3, 94)                    # a[3] = 6 + 94 = 100
print(fw.t[1:])
print(fw.range_sum(2, 7), fw.get(3))
fw.set(3, 1)
print(fw.range_sum(0, 8), fw.get(3))
```
```text
[5, 8, 8, 22, 2, 9, 4, 36]
36 22 27 0
[5, 8, 8, 116, 2, 9, 4, 130]
121 100
31 1
```

Check `t` against the bars: `t[1]=5`, `t[2]=5+3=8`, `t[3]=8`, `t[4]=5+3+8+6=22`, `t[5]=2`, `t[6]=2+7=9`, `t[7]=4`, `t[8]=36`. After `add(3, 94)` the cells `t[4]` and `t[8]` changed, because position 3 (0-indexed) is position 4 (1-indexed), and `4 -> 8` is the path.

### Watching the jumps in binary

```python
def query_path(r):
    path = []
    while r > 0:
        path.append(r)
        r -= r & -r
    return path

def update_path(i, n):
    path = []
    i += 1
    while i <= n:
        path.append(i)
        i += i & -i
    return path

for r in (13, 7, 8):
    print(f"prefix({r}) reads", [f"{p}={p:b}" for p in query_path(r)])
for i in (4, 0, 9):
    print(f"add({i}) on n=16 writes", [f"{p}={p:b}" for p in update_path(i, 16)])
```
```text
prefix(13) reads ['13=1101', '12=1100', '8=1000']
prefix(7) reads ['7=111', '6=110', '4=100']
prefix(8) reads ['8=1000']
add(4) on n=16 writes ['5=101', '6=110', '8=1000', '16=10000']
add(0) on n=16 writes ['1=1', '2=10', '4=100', '8=1000', '16=10000']
add(9) on n=16 writes ['10=1010', '12=1100', '16=10000']
```

Every query step *clears* a bit. Every update step *carries* into a higher bit. Because a number has at most `log2(n) + 1` bits, both loops are short.

### Predict the output

```python
print(update_path(2, 10))
print(query_path(10))
```

<details><summary>Answer</summary>

```text
[3, 4, 8]
[10, 8]
```

`add(2)` means 1-indexed position 3 (`11`). Then `3 + 1 = 4`, `4 + 4 = 8`, `8 + 8 = 16 > 10`: the path is `[3, 4, 8]`. For `prefix(10)`: 10 is `1010`; clear the lowest bit to get `8`; clear again to get 0. The path is `[10, 8]`.

</details>

### The linear-time build

Calling `add` for each element costs `O(n log n)`. The constructor above does it in `O(n)`: copy each element into its cell, and then push the finished cell `i` into its **parent** `i + lowbit(i)` once. Each cell is pushed exactly once, so the work is `n` steps. We check it against building with `add`.

```python
rng = random.Random(8)
data = [rng.randint(-9, 9) for _ in range(37)]
fast = Fenwick(len(data), data)
slow = Fenwick(len(data))
for i, x in enumerate(data):
    slow.add(i, x)
print(fast.t == slow.t)
```
```text
True
```

### The 0-index trap

Fenwick trees are **1-indexed** by nature. With index `0`, `0 & -0 == 0`, so `i += i & -i` never moves and the update loop never ends. Look at what happens (we stop the loop by hand after five steps):

```python
i, steps = 0, 0
while i <= 8 and steps < 5:
    i += i & -i
    steps += 1
print("i =", i, "after", steps, "steps (stuck at 0)")
```
```text
i = 0 after 5 steps (stuck at 0)
```

That is why our class adds `1` to the user's index before the loop. If you write a raw Fenwick tree in a contest, store the array from index `1`.

### Brute-force check

```python
def check_fenwick(seed):
    rng = random.Random(seed)
    for _ in range(300):
        n = rng.randint(1, 40)
        a = [rng.randint(-20, 20) for _ in range(n)]
        fw = Fenwick(n, a)
        for _ in range(50):
            if rng.random() < 0.4:
                i, v = rng.randrange(n), rng.randint(-9, 9)
                a[i] += v
                fw.add(i, v)
            else:
                l = rng.randint(0, n)
                r = rng.randint(l, n)
                assert fw.range_sum(l, r) == sum(a[l:r]), f"wrong sum on [{l},{r}) of {a}"
    return "ok"

print(check_fenwick(9))
```
```text
ok
```

### Costs, and the limit of a Fenwick tree

| Operation | Time | Space |
|---|---|---|
| build from a list | `O(n)` | `O(n)` |
| point add | `O(log n)` | |
| prefix sum / range sum | `O(log n)` | |

A Fenwick tree stores `n + 1` numbers: half or a quarter of the segment tree. It works for any operation that has an **inverse**: sum, xor, count. Prefix *minimum* works too if values only ever move one way (a value may only decrease), because a minimum cannot be subtracted. For range minimum with arbitrary updates, use a segment tree.

## 11. Range updates with a Fenwick tree

### Range add, point query: the difference array

In dsa.03, section 4, a **difference array** `d` turned "add `v` to `a[l:r]`" into two changes: `d[l] += v` and `d[r] -= v`. The element `a[i]` is then the prefix sum of `d` up to `i`. A prefix sum with point updates is exactly what a Fenwick tree does.

So: keep a Fenwick tree over `d`. Range add is two point adds. A point query is one prefix sum.

```python
class RangeAddPointQuery:
    def __init__(self, a):
        self.base = list(a)
        self.fw = Fenwick(len(a))        # holds the difference array d, starting at zero

    def add(self, l, r, v):
        self.fw.add(l, v)
        if r < self.fw.n:
            self.fw.add(r, -v)

    def get(self, i):
        return self.base[i] + self.fw.prefix(i + 1)

rp = RangeAddPointQuery([5, 3, 8, 6, 2, 7, 4, 1])
rp.add(2, 6, 10)
rp.add(0, 8, -1)
rp.add(4, 5, 100)
print([rp.get(i) for i in range(8)])
```
```text
[4, 2, 17, 15, 111, 16, 3, 0]
```

By hand: start `[5,3,8,6,2,7,4,1]`; `+10` on positions 2 to 5 gives `[5,3,18,16,12,17,4,1]`; `-1` everywhere gives `[4,2,17,15,11,16,3,0]`; `+100` at position 4 gives `[4,2,17,15,111,16,3,0]`. The code says the same.

(`if r < n` skips the `-v` at position `n`: no element lives there, and our `add` would ignore it anyway. The guard just makes the intention clear.)

### Range add, range sum: two Fenwick trees

Now we want both range add and range **sum**. The sum of the first `p` elements, using the difference array `d`, is

```text
prefix(p) = sum over i<p of a[i]
          = sum over i<p of (d[0] + d[1] + ... + d[i])
          = sum over j<p of d[j] * (p - j)        <- d[j] is counted for each i from j to p-1
          = p * (sum of d[j], j<p)  -  (sum of j * d[j], j<p)
```

So we need two prefix sums over `d`: one of `d[j]`, one of `j * d[j]`. Keep **two Fenwick trees**, `b1` over `d[j]` and `b2` over `j * d[j]`. A range add of `v` on `[l, r)` does `d[l] += v` and `d[r] -= v`, so:

- `b1.add(l, v)`, `b1.add(r, -v)`
- `b2.add(l, v * l)`, `b2.add(r, -v * r)`

And `prefix(p) = base_prefix[p] + p * b1.prefix(p) - b2.prefix(p)`, where `base_prefix` is the plain prefix sums of the original array. A range sum is `prefix(r) - prefix(l)`.

```python
class RangeAddRangeSum:
    def __init__(self, a):
        n = len(a)
        self.n = n
        self.base = [0] * (n + 1)
        for i, x in enumerate(a):
            self.base[i + 1] = self.base[i] + x
        self.b1 = Fenwick(n)
        self.b2 = Fenwick(n)

    def add(self, l, r, v):
        self.b1.add(l, v)
        self.b2.add(l, v * l)
        if r < self.n:
            self.b1.add(r, -v)
            self.b2.add(r, -v * r)

    def prefix(self, p):
        return self.base[p] + p * self.b1.prefix(p) - self.b2.prefix(p)

    def range_sum(self, l, r):
        return self.prefix(r) - self.prefix(l)

rr = RangeAddRangeSum([5, 3, 8, 6, 2, 7, 4, 1])
print(rr.range_sum(0, 8), rr.range_sum(2, 7))
rr.add(2, 6, 10)
print(rr.range_sum(0, 8), rr.range_sum(2, 7), rr.range_sum(0, 2))
rr.add(0, 8, -1)
print(rr.range_sum(0, 8), rr.range_sum(3, 5))

def check_rr(seed):
    rng = random.Random(seed)
    for _ in range(300):
        n = rng.randint(1, 30)
        a = [rng.randint(-20, 20) for _ in range(n)]
        tree = RangeAddRangeSum(a)
        for _ in range(40):
            l = rng.randint(0, n - 1)
            r = rng.randint(l + 1, n)
            if rng.random() < 0.5:
                v = rng.randint(-9, 9)
                tree.add(l, r, v)
                for i in range(l, r):
                    a[i] += v
            else:
                assert tree.range_sum(l, r) == sum(a[l:r]), f"wrong on [{l},{r}) of {a}"
    return "ok"

print(check_rr(10))
```
```text
36 27
76 67 8
68 26
ok
```

This gives range add and range sum in `O(log n)` with two small lists and no lazy tags. It cannot do range assignment or range min; for those use the lazy segment tree.

### Which one for range updates?

| Need | Use |
|---|---|
| add on a range, read single values | one Fenwick over the differences |
| add on a range, sum of a range | two Fenwick trees |
| assign on a range, or min/max with range add | lazy segment tree |

## 12. Counting inversions with a Fenwick tree

### The problem

An **inversion** is a pair `i < j` with `a[i] > a[j]`. It measures how far a list is from sorted: a sorted list has 0 inversions, a reversed list of length `n` has `n(n-1)/2`. Merge sort counts them in `O(n log n)` (dsa.05, section 9). A Fenwick tree gives a second way, and the same method answers the harder variants (*"for each element, how many smaller ones are to its right?"*).

### The idea

Scan left to right. When we reach `x`, the earlier elements are already stored. The inversions that end at `x` are the earlier elements **strictly greater than** `x`. If the Fenwick tree keeps a **count of how many earlier elements have each value**, then

```text
earlier elements > x   =   (number of elements seen so far)  -  (earlier elements <= x)
                       =   seen  -  prefix(rank of x, inclusive)
```

After counting, record `x` with `add(rank, 1)`.

### Coordinate compression

The values may be huge (up to 10^9) or negative, so we cannot make a tree with one cell per value. We only care about the **order** of values, so replace each value by its **rank** among the distinct values: `0` for the smallest, `1` for the next, and so on.

```python
a = [40, 10, 30, 10, 20]
ranks = {v: i for i, v in enumerate(sorted(set(a)))}
print(ranks)
print([ranks[x] for x in a])
```
```text
{10: 0, 20: 1, 30: 2, 40: 3}
[3, 0, 2, 0, 1]
```

`sorted(set(a))` removes duplicates and sorts; the dictionary maps each value to its position. Equal values get equal ranks, which is what we want: equal elements are not inversions.

```python
def count_inversions(a):
    ranks = {v: i for i, v in enumerate(sorted(set(a)))}
    bit = Fenwick(len(ranks))
    inversions = 0
    for seen, x in enumerate(a):           # 'seen' = how many elements came before x
        k = ranks[x]
        inversions += seen - bit.prefix(k + 1)     # earlier elements with rank > k
        bit.add(k, 1)
    return inversions

def trace_inversions(a):
    ranks = {v: i for i, v in enumerate(sorted(set(a)))}
    bit = Fenwick(len(ranks))
    total = 0
    for seen, x in enumerate(a):
        k = ranks[x]
        le = bit.prefix(k + 1)
        total += seen - le
        print(f"x={x:>2} rank={k} seen={seen} earlier<=x: {le}  new inversions: {seen - le}  total: {total}")
        bit.add(k, 1)

trace_inversions([40, 10, 30, 10, 20])
print(count_inversions([1, 2, 3, 4]), count_inversions([4, 3, 2, 1]), count_inversions([2, 2, 2]), count_inversions([]))
```
```text
x=40 rank=3 seen=0 earlier<=x: 0  new inversions: 0  total: 0
x=10 rank=0 seen=1 earlier<=x: 0  new inversions: 1  total: 1
x=30 rank=2 seen=2 earlier<=x: 1  new inversions: 1  total: 2
x=10 rank=0 seen=3 earlier<=x: 1  new inversions: 2  total: 4
x=20 rank=1 seen=4 earlier<=x: 2  new inversions: 2  total: 6
0 6 0 0
```

Read the trace. When `x = 30` arrives, two elements have been seen (`40`, `10`); only `10` is `<= 30`, so `2 - 1 = 1` inversion: the pair `(40, 30)`. The second `10` arrives after `40`, `10`, `30`. Only the `40` and the `30` are greater, so it adds 2 inversions; the earlier `10` is equal, and equal elements do not count. The final `20` adds 2 more (`40` and `30`), for a total of 6.

### The brute-force check

```python
def brute_inversions(a):
    return sum(1 for i in range(len(a)) for j in range(i + 1, len(a)) if a[i] > a[j])

def check_inv(seed):
    rng = random.Random(seed)
    for _ in range(500):
        n = rng.randint(0, 25)
        a = [rng.randint(-5, 5) for _ in range(n)]    # many duplicates on purpose
        assert count_inversions(a) == brute_inversions(a), f"wrong inversions for {a}"
    return "ok"

print(check_inv(11))
```
```text
ok
```

### Variants

- **Count smaller elements to the right of each element**: scan from the right; before adding `x`, `bit.prefix(rank)` (strictly smaller) is the answer for `x`.
- **Count pairs with `a[i] > 2 * a[j]`**: compress all values and all doubled values together, and query before adding.
- **Longest increasing subsequence in `O(n log n)`** with a "best length ending at rank `r`" tree. Here the tree needs *prefix maximum*, which is allowed because the values only increase (see the limit in section 10).

Time `O(n log n)` (a sort for compression, then `n` queries and updates). Space `O(n)`.

## 13. The k-th element: descending the Fenwick tree

### The problem

We keep a **multiset** of integers in a range `0..m-1` with insertions and deletions, and we ask: *what is the k-th smallest element now?* (The median is the case `k = (count + 1) / 2`.) Store the **count of each value** in a Fenwick tree. The k-th smallest is the first value `v` for which `prefix(v + 1) >= k`.

A binary search on `v` with a `prefix` call each time costs `O(log^2 n)`. We can do better by exploiting the shape of the tree: the cells `t[p]` for `p = 2^j` are known lengths, so we can walk through the bits from high to low and decide each bit in `O(1)`.

### The descent

```text
pos = 0
for pw in powers of two, from the largest <= n down to 1:
    if pos + pw <= n and t[pos + pw] < k:   # the whole block pos+1 .. pos+pw has fewer than k items
        pos += pw                            # skip it
        k   -= t[pos]
answer (1-indexed) = pos + 1
```

At each step `t[pos + pw]` covers exactly `pw` positions, `pos + 1 .. pos + pw`, because `pos` is a multiple of `2 * pw` (its lower bits are zero): the lowbit of `pos + pw` is `pw`. So the cell holds the count of the next block. If that block holds fewer than `k` items, the k-th item is beyond it. When the loop ends, `pos` is the **largest position whose prefix count is less than `k`**, so the k-th item is at the next position, `pos + 1` in 1-indexing, which is `pos` in 0-indexing.

```python
class FenwickKth(Fenwick):
    def kth(self, k):
        """Smallest 0-indexed position v with prefix(v + 1) >= k. -1 if fewer than k items."""
        if k < 1 or k > self.prefix(self.n):
            return -1
        pos = 0
        pw = 1 << (self.n.bit_length() - 1)      # largest power of two <= n
        while pw:
            nxt = pos + pw
            if nxt <= self.n and self.t[nxt] < k:
                pos = nxt
                k -= self.t[nxt]
            pw >>= 1
        return pos

bag = FenwickKth(10)                 # values 0..9
for v in (7, 3, 3, 9, 1, 3, 7):
    bag.add(v, 1)
print([bag.kth(k) for k in range(1, 8)], bag.kth(8), bag.kth(0))
bag.add(3, -2)                       # remove two copies of 3
print([bag.kth(k) for k in range(1, 6)])
```
```text
[1, 3, 3, 3, 7, 7, 9] -1 -1
[1, 3, 7, 7, 9]
```

The multiset `{1, 3, 3, 3, 7, 7, 9}` sorted is `1,3,3,3,7,7,9`, so the k-th for `k = 1..7` is exactly what the first line shows. After removing two `3`s the multiset is `{1, 3, 7, 7, 9}`.

### A step-by-step descent

Let us watch the loop for `k = 5` on the first multiset.

```python
def trace_kth(tree, k):
    pos, pw = 0, 1 << (tree.n.bit_length() - 1)
    print(f"looking for k={k}")
    while pw:
        nxt = pos + pw
        if nxt <= tree.n and tree.t[nxt] < k:
            print(f"  pw={pw}: t[{nxt}]={tree.t[nxt]} < {k}: skip, pos={nxt}, k -> {k - tree.t[nxt]}")
            pos, k = nxt, k - tree.t[nxt]
        else:
            shown = tree.t[nxt] if nxt <= tree.n else "out of range"
            print(f"  pw={pw}: t[{nxt}] = {shown}: stay at pos={pos}")
        pw >>= 1
    print(f"  answer: position {pos}")

bag2 = FenwickKth(10)
for v in (7, 3, 3, 9, 1, 3, 7):
    bag2.add(v, 1)
trace_kth(bag2, 5)
```
```text
looking for k=5
  pw=8: t[8] = 6: stay at pos=0
  pw=4: t[4]=4 < 5: skip, pos=4, k -> 1
  pw=2: t[6]=0 < 1: skip, pos=6, k -> 1
  pw=1: t[7]=0 < 1: skip, pos=7, k -> 1
  answer: position 7
```

The fifth smallest of `1,3,3,3,7,7,9` is `7`, found in four steps, one per bit: no `prefix` calls, no binary search on top.

### Brute-force check

```python
def check_kth(seed):
    rng = random.Random(seed)
    for _ in range(300):
        m = rng.randint(1, 30)
        tree = FenwickKth(m)
        items = []
        for _ in range(40):
            if items and rng.random() < 0.3:
                v = rng.choice(items)
                items.remove(v)
                tree.add(v, -1)
            else:
                v = rng.randrange(m)
                items.append(v)
                tree.add(v, 1)
            ordered = sorted(items)
            for k in range(0, len(items) + 2):
                want = ordered[k - 1] if 1 <= k <= len(items) else -1
                assert tree.kth(k) == want, f"kth({k}) wrong for {ordered}"
    return "ok"

print(check_kth(12))
```
```text
ok
```

The same idea is "binary lifting on a Fenwick tree": find the largest `pos` whose prefix satisfies a monotone condition. It works for any condition that is monotone in the prefix, so long as the values are non-negative.

## 14. A two-dimensional Fenwick tree (briefly)

For a grid with point updates and **rectangle sums**, nest one Fenwick loop inside another. The cell `t[i][j]` covers the rectangle of `lowbit(i)` rows and `lowbit(j)` columns that end at `(i, j)`.

```python
class Fenwick2D:
    """Point add, rectangle sum. 0-indexed, half-open rectangles."""

    def __init__(self, rows, cols):
        self.R, self.C = rows, cols
        self.t = [[0] * (cols + 1) for _ in range(rows + 1)]

    def add(self, r, c, v):
        i = r + 1
        while i <= self.R:
            j = c + 1
            while j <= self.C:
                self.t[i][j] += v
                j += j & -j
            i += i & -i

    def prefix(self, r, c):
        """Sum of the rectangle rows [0, r), columns [0, c)."""
        total = 0
        i = r
        while i > 0:
            j = c
            while j > 0:
                total += self.t[i][j]
                j -= j & -j
            i -= i & -i
        return total

    def rect(self, r1, c1, r2, c2):
        """Sum of rows [r1, r2), columns [c1, c2): inclusion-exclusion on four prefixes."""
        return (self.prefix(r2, c2) - self.prefix(r1, c2)
                - self.prefix(r2, c1) + self.prefix(r1, c1))

grid = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]
f2 = Fenwick2D(3, 4)
for r in range(3):
    for c in range(4):
        f2.add(r, c, grid[r][c])
print(f2.prefix(3, 4), f2.rect(1, 1, 3, 3), f2.rect(0, 0, 1, 4))
f2.add(1, 2, 100)
print(f2.rect(1, 1, 3, 3), f2.rect(1, 2, 2, 3))

def check_2d(seed):
    rng = random.Random(seed)
    for _ in range(100):
        R, C = rng.randint(1, 8), rng.randint(1, 8)
        g = [[rng.randint(-9, 9) for _ in range(C)] for _ in range(R)]
        f = Fenwick2D(R, C)
        for r in range(R):
            for c in range(C):
                f.add(r, c, g[r][c])
        for _ in range(30):
            r, c, v = rng.randrange(R), rng.randrange(C), rng.randint(-9, 9)
            g[r][c] += v
            f.add(r, c, v)
            r1, r2 = sorted((rng.randint(0, R), rng.randint(0, R)))
            c1, c2 = sorted((rng.randint(0, C), rng.randint(0, C)))
            want = sum(g[i][j] for i in range(r1, r2) for j in range(c1, c2))
            assert f.rect(r1, c1, r2, c2) == want, f"rect [{r1},{r2}) x [{c1},{c2}) wrong"
    return "ok"

print(check_2d(13))
```
```text
78 34 10
134 107
ok
```

The rectangle `rows 1..2, columns 1..2` of the grid holds `6, 7, 10, 11`, total `34`. The prefix answer is the same inclusion-exclusion you know from the 2D prefix sums in dsa.03, section 2.

| | Time | Space |
|---|---|---|
| point add | `O(log R * log C)` | |
| rectangle sum | `O(4 * log R * log C)` | |
| the structure | | `O(R * C)` |

For huge sparse grids (many points, few cells) one compresses coordinates offline or uses a different structure; that is outside this module.

## 15. The sparse table: O(1) queries on data that never changes

### A different trade

Everything so far pays `O(log n)` per query to allow updates. If the array is **static** (it never changes), we can precompute more and answer in `O(1)`. The **sparse table** does this for operations like minimum and maximum.

### The idea: blocks whose length is a power of two

Precompute, for every start `i` and every power of two `2^k`, the answer for the block `a[i : i + 2^k]`.

```text
table[0][i] = a[i]                                   (blocks of length 1)
table[k][i] = f(table[k-1][i], table[k-1][i + 2^(k-1)])    (two halves of length 2^(k-1))
```

There are about `log2(n)` rows, each of up to `n` entries, so building costs `O(n log n)` time and space.

### The query: two blocks that overlap

For `[l, r)` of length `len = r - l`, let `k` be the largest integer with `2^k <= len`. Then two blocks of length `2^k` cover the range: one starting at `l`, one **ending** at `r`, that is starting at `r - 2^k`. They may overlap in the middle, and together they cover everything.

```text
        l                       r
        |<------ len --------->|
        [==== 2^k ====]
                  [==== 2^k ====]
                  ^ starts at r - 2^k
```

For minimum, overlap is harmless: taking the minimum of a value twice changes nothing. That property is called **idempotent**: `f(x, x) == x`. Minimum, maximum, gcd, bitwise AND and OR are idempotent.

Finding `k` quickly: precompute `lg[len] = floor(log2(len))` once (`lg[i] = lg[i // 2] + 1`).

```python
class SparseTable:
    """Static array, idempotent combine, O(1) query on [l, r) with r > l."""

    def __init__(self, a, f=min):
        n = len(a)
        self.f = f
        self.lg = [0] * (n + 2)
        for i in range(2, n + 2):
            self.lg[i] = self.lg[i // 2] + 1
        self.table = [list(a)]
        k = 1
        while (1 << k) <= n:
            prev, half = self.table[-1], 1 << (k - 1)
            self.table.append([f(prev[i], prev[i + half]) for i in range(n - (1 << k) + 1)])
            k += 1

    def query(self, l, r):
        k = self.lg[r - l]
        row = self.table[k]
        return self.f(row[l], row[r - (1 << k)])

a = [5, 3, 8, 6, 2, 7, 4, 1]
sp = SparseTable(a)
for k, row in enumerate(sp.table):
    print(f"k={k} (blocks of {1 << k}):", row)
print(sp.query(1, 7), sp.query(0, 8), sp.query(4, 5), sp.query(2, 4))
```
```text
k=0 (blocks of 1): [5, 3, 8, 6, 2, 7, 4, 1]
k=1 (blocks of 2): [3, 3, 6, 2, 2, 4, 1]
k=2 (blocks of 4): [3, 2, 2, 2, 1]
k=3 (blocks of 8): [1]
2 1 2 6
```

Trace `query(1, 7)`. The length is 6, so `k = 2` (blocks of 4). The first block is `a[1:5] = 3, 8, 6, 2` with minimum `2` (that is `table[2][1]`). The second block starts at `7 - 4 = 3`: `a[3:7] = 6, 2, 7, 4` with minimum `2` (`table[2][3]`). Their overlap is positions 3 and 4. The answer is `min(2, 2) = 2`.

### Why a sparse table fails for sums

Do the same for sums on the same range. The two blocks have sums `19` and `19`, and `19 + 19 = 38`, but the true sum of `a[1:7]` is `3 + 8 + 6 + 2 + 7 + 4 = 30`. The overlap `6 + 2 = 8` was counted twice.

```python
sums = SparseTable(a, lambda x, y: x + y)
print("two overlapping blocks:", sums.query(1, 7), " true sum:", sum(a[1:7]))
```
```text
two overlapping blocks: 38  true sum: 30
```

The fix for **non-idempotent** operations is to use blocks that do not overlap: split the length into powers of two (its binary digits), which costs `O(log n)` per query. For sums you would use prefix sums instead, which is `O(1)` with an `O(n)` table.

```python
def query_disjoint(sp, l, r, identity):
    """Works for any associative f (sum, xor, concatenation). O(log n) per query."""
    result = identity
    for k in range(sp.lg[r - l], -1, -1):
        if l + (1 << k) <= r:
            result = sp.f(result, sp.table[k][l])
            l += 1 << k
    return result

letters = SparseTable(list("sparsetable"), lambda x, y: x + y)
print(query_disjoint(sums, 1, 7, 0), query_disjoint(letters, 2, 9, ""))
```
```text
30 arsetab
```

### Checking against brute force

```python
def check_sparse(seed):
    rng = random.Random(seed)
    for _ in range(200):
        n = rng.randint(1, 40)
        a = [rng.randint(1, 100) for _ in range(n)]
        smin, smax, sgcd = SparseTable(a, min), SparseTable(a, max), SparseTable(a, math.gcd)
        ssum = SparseTable(a, lambda x, y: x + y)
        for l in range(n):
            for r in range(l + 1, n + 1):
                assert smin.query(l, r) == min(a[l:r]), "min wrong"
                assert smax.query(l, r) == max(a[l:r]), "max wrong"
                assert sgcd.query(l, r) == math.gcd(*a[l:r]), "gcd wrong"
                assert query_disjoint(ssum, l, r, 0) == sum(a[l:r]), "disjoint sum wrong"
    return "ok"

print(check_sparse(14))
```
```text
ok
```

### Costs and when to use it

| | Time | Space |
|---|---|---|
| build | `O(n log n)` | `O(n log n)` |
| query (idempotent) | `O(1)` | |
| query (any associative, disjoint blocks) | `O(log n)` | |
| point update | none (rebuild, `O(n log n)`) | |

For `n = 10^6`, the table has about 20 rows of up to a million entries: 20 million Python objects, which is hundreds of megabytes. Sparse tables in Python are comfortable up to a few times `10^5`. They are the standard tool for static **range minimum query (RMQ)**, and for the **lowest common ancestor** (dsa.10, section 10), by reducing LCA to an RMQ on an Euler tour.

## 16. Square-root decomposition and Mo's algorithm

### Blocks of size sqrt(n)

Cut the array into blocks of size `B = floor(sqrt(n))`. For each block, keep its sum.

- **Point update**: change the element and its block's sum. `O(1)`.
- **Range query** `[l, r)`: add single elements at the two ends (at most `B` each), plus the sums of the whole blocks in the middle (at most `n / B`). That is about `3 * sqrt(n)` cells.

```text
 n = 16, B = 4

 index:   0 1 2 3 | 4 5 6 7 | 8 9 10 11 | 12 13 14 15
 block:      0    |    1    |     2      |      3
 query [2, 14):  2 3 | block 1 | block 2 | 12 13
                 ^ scan        whole blocks     scan ^
```

```python
class SqrtSum:
    def __init__(self, a):
        self.a = list(a)
        self.n = len(a)
        self.B = max(1, math.isqrt(self.n))
        nb = (self.n + self.B - 1) // self.B
        self.blocks = [sum(self.a[b * self.B:(b + 1) * self.B]) for b in range(nb)]

    def update(self, i, v):
        self.blocks[i // self.B] += v - self.a[i]
        self.a[i] = v

    def query(self, l, r):
        """Return (sum, number of cells looked at)."""
        a, blocks, B = self.a, self.blocks, self.B
        total = touched = 0
        while l < r and l % B != 0:           # left partial block, one by one
            total += a[l]
            l += 1
            touched += 1
        while l + B <= r:                     # whole blocks
            total += blocks[l // B]
            l += B
            touched += 1
        while l < r:                          # right partial block
            total += a[l]
            l += 1
            touched += 1
        return total, touched

data = list(range(1, 101))                    # n = 100, B = 10
sq = SqrtSum(data)
print(sq.B, sq.query(0, 100), sq.query(7, 93), sq.query(3, 5))
sq.update(50, 0)
print(sq.query(7, 93))
print("check, sum of sq.a[7:93] =", sum(sq.a[7:93]))
```
```text
10 (5050, 10) (4343, 14) (9, 2)
(4292, 14)
check, sum of sq.a[7:93] = 4292
```

The query `[7, 93)` looked at `3 + 8 + 3 = 14` cells (three single elements at the left, eight whole blocks, three at the right) rather than 86.

The big advantage of sqrt decomposition is that **each block can keep any structure you like**, even ones a segment tree cannot merge. A famous case: *"count the elements `>= x` in `a[l:r]`, with updates"*. Keep every block as a **sorted list**; whole blocks answer with `bisect`.

```python
import bisect

class SqrtCountAtLeast:
    def __init__(self, a):
        self.a = list(a)
        n = len(a)
        self.B = max(1, math.isqrt(n))
        self.blocks = [sorted(a[i:i + self.B]) for i in range(0, n, self.B)]

    def update(self, i, v):
        block = self.blocks[i // self.B]
        del block[bisect.bisect_left(block, self.a[i])]     # remove one copy of the old value
        bisect.insort(block, v)                             # insert the new value in order
        self.a[i] = v

    def query(self, l, r, x):
        """How many of a[l:r] are >= x."""
        B, count = self.B, 0
        while l < r and l % B != 0:
            count += self.a[l] >= x
            l += 1
        while l + B <= r:
            block = self.blocks[l // B]
            count += len(block) - bisect.bisect_left(block, x)
            l += B
        while l < r:
            count += self.a[l] >= x
            l += 1
        return count

def check_sqrt(seed):
    rng = random.Random(seed)
    for _ in range(100):
        n = rng.randint(1, 60)
        a = [rng.randint(0, 20) for _ in range(n)]
        s1, s2 = SqrtSum(a), SqrtCountAtLeast(a)
        for _ in range(40):
            if rng.random() < 0.4:
                i, v = rng.randrange(n), rng.randint(0, 20)
                a[i] = v
                s1.update(i, v)
                s2.update(i, v)
            else:
                l = rng.randint(0, n)
                r = rng.randint(l, n)
                x = rng.randint(0, 21)
                assert s1.query(l, r)[0] == sum(a[l:r]), "block sum wrong"
                assert s2.query(l, r, x) == sum(1 for y in a[l:r] if y >= x), "count wrong"
    return "ok"

print(check_sqrt(15))
```
```text
ok
```

(`count += self.a[l] >= x` adds `True` or `False`, i.e. 1 or 0.)

| | Time | Space |
|---|---|---|
| build | `O(n)` (sum) or `O(n log B)` (sorted blocks) | `O(n)` |
| point update | `O(1)` (sum) or `O(B)` (sorted blocks) | |
| range query | `O(sqrt(n))` (sum) or `O(sqrt(n) log n)` (count) | |

`sqrt(n)` is bigger than `log n`: for `n = 10^6`, `sqrt(n) = 1000` against `log n = 20`. Choose sqrt decomposition when a block can store something no tree can merge, or when it is simply the easiest correct code.

### Mo's algorithm: sort the queries and slide a window

**Mo's algorithm** answers many range queries **offline** on a static array. Keep a window `[curL, curR)` and the answer for it. To go to the next query, move the window edges one step at a time, adding or removing one element per step. If the queries are processed in a clever order, the total number of steps is small.

The order: split positions into blocks of size `B ~ sqrt(n)`; sort queries by `(l // B, r)`. Within one block of `l`, the right edge moves forward only (at most `n` in total per block) and the left edge moves less than `B` per query. The total is about `O((n + q) * sqrt(n))` steps. (A common refinement alternates the direction of `r` in odd blocks; we use it below.)

The use: a question where **adding or removing one element is easy** but a segment tree cannot merge two halves, such as *"how many distinct values are in `a[l:r]`?"*.

```python
def mo_distinct(a, queries):
    """queries: list of (l, r), half-open, l <= r. Returns (answers, number of single-step moves)."""
    n = len(a)
    B = max(1, math.isqrt(n))
    order = sorted(range(len(queries)),
                   key=lambda i: (queries[i][0] // B,
                                  queries[i][1] if (queries[i][0] // B) % 2 == 0 else -queries[i][1]))
    count = {}
    distinct = 0
    cur_l = cur_r = 0                       # current window a[cur_l:cur_r], empty at first
    answers = [0] * len(queries)
    moves = 0
    for qi in order:
        l, r = queries[qi]
        while cur_l > l:                    # grow first ...
            cur_l -= 1
            count[a[cur_l]] = count.get(a[cur_l], 0) + 1
            distinct += count[a[cur_l]] == 1
            moves += 1
        while cur_r < r:
            count[a[cur_r]] = count.get(a[cur_r], 0) + 1
            distinct += count[a[cur_r]] == 1
            cur_r += 1
            moves += 1
        while cur_l < l:                    # ... then shrink, so the window never goes negative
            count[a[cur_l]] -= 1
            distinct -= count[a[cur_l]] == 0
            cur_l += 1
            moves += 1
        while cur_r > r:
            cur_r -= 1
            count[a[cur_r]] -= 1
            distinct -= count[a[cur_r]] == 0
            moves += 1
        answers[qi] = distinct
    return answers, moves

rng = random.Random(16)
arr = [rng.randint(1, 30) for _ in range(2000)]
qs = []
for _ in range(2000):
    l = rng.randint(0, 1999)
    qs.append((l, rng.randint(l, 2000)))
answers, moves = mo_distinct(arr, qs)
brute = [len(set(arr[l:r])) for l, r in qs]
print(answers == brute)
print("Mo moves:", moves, " naive element visits:", sum(r - l for l, r in qs))
```
```text
True
Mo moves: 76005  naive element visits: 984555
```

The answers match, and the window moved far fewer steps than adding up every query from scratch. Even for this small example (`n = 2000`) the window moved about thirteen times fewer steps; the gain grows with `n`.

Notice that `distinct += count[x] == 1` uses a boolean as 0 or 1. The order of operations matters: **grow before you shrink**. If the right edge shrinks first while `cur_l > cur_r`, counts go negative.

Time `O((n + q) sqrt(n))`, space `O(n + q)`. No updates are allowed: the array is static. (There are variants with updates, outside this chapter.)

## 17. Offline and online queries

### Two ways questions arrive

- **Online**: each query must be answered before the next one is known. Often the next query depends on the previous answer ("forced online"), or the data stream is live.
- **Offline**: you may read **all queries first**, then answer them in any order you like.

Offline is a gift. You can sort the queries, reorder them, or process them in one sweep. Many hard problems become easy.

### Example: distinct values in a range, offline, with a Fenwick tree

We solved it with Mo's algorithm. Here is a better way in `O(n log n)` with a Fenwick tree. Sort the queries by their right end. Sweep `i` from left to right. Keep a Fenwick tree that has a `1` at the **last occurrence** so far of each value, and `0` elsewhere. When a value appears again, remove the old `1` and put a new `1` at the new position. At the time we stand at `i`, the number of distinct values in `a[l : i+1]` is the number of `1`s in positions `l..i`: each distinct value contributes exactly one `1`, the one at its last occurrence, and that one is at or beyond `l` exactly when the value occurs in the window.

```python
def distinct_offline(a, queries):
    """queries: list of (l, r) with l < r, half-open. Returns the number of distinct values in each."""
    by_right = {}
    for idx, (l, r) in enumerate(queries):
        by_right.setdefault(r, []).append((l, idx))
    bit = Fenwick(len(a))
    last = {}
    answers = [0] * len(queries)
    for i, x in enumerate(a):
        if x in last:
            bit.add(last[x], -1)           # the old last occurrence no longer counts
        bit.add(i, 1)
        last[x] = i
        for l, idx in by_right.get(i + 1, []):      # queries whose range ends right after i
            answers[idx] = bit.range_sum(l, i + 1)
    return answers

small = [4, 7, 4, 4, 9, 7]
print(distinct_offline(small, [(0, 6), (0, 3), (2, 5), (1, 2), (3, 6)]))
good_qs = [(l, r) for l, r in qs if l < r]
print(distinct_offline(arr, good_qs) == [len(set(arr[l:r])) for l, r in good_qs])
```
```text
[3, 2, 2, 1, 3]
True
```

The first list is easy to check: `[4,7,4,4,9,7]` has 3 distinct values in total; `[0,3)` is `4,7,4` which has 2; `[2,5)` is `4,4,9` with 2; `[1,2)` is `7` with 1; `[3,6)` is `4,9,7` with 3.

### What offline allows

| Technique | Idea |
|---|---|
| Sort by right end + Fenwick | one sweep, state keeps "last occurrence" style info |
| Mo's algorithm | reorder queries so a sliding window moves little |
| Sort values, insert one by one | answer "how many elements `<= x` in `[l, r)`" by inserting elements in value order |
| Coordinate compression | read all values first to know the set of values |

If the problem says "the next query is encoded using the previous answer", it is forced online and none of these apply; you need a structure that answers any query at any time, like the segment tree.

### Try it

You must answer 200,000 queries "minimum of `a[l:r]`" on an array that never changes. Online or offline does not matter. Which structure, and why?

<details><summary>Answer</summary>

The array is static and the operation is minimum, which is idempotent: a **sparse table** with `O(1)` queries and `O(n log n)` build. A segment tree also works, with `O(log n)` per query. The sparse table is faster per query if memory allows; the segment tree needs less memory.

</details>

## 18. Which structure when?

### The table

`n` is the array length, `B = sqrt(n)`, `q` is the number of queries.

| Structure | Build | Point update | Range query | Range update | Space | Typical use |
|---|---|---|---|---|---|---|
| Plain loop | `O(1)` | `O(1)` | `O(n)` | `O(n)` | `O(n)` | tiny `n`, few queries |
| Prefix sums | `O(n)` | `O(n)` | `O(1)` | `O(n)` | `O(n)` | static sums |
| Difference array | `O(n)` | | | `O(1)`, read at the end | `O(n)` | many range adds, read once |
| Fenwick tree | `O(n)` | `O(log n)` | `O(log n)` prefix/range sum | with 2 trees, `O(log n)` | `O(n)` | counts, sums, inversions, k-th |
| Segment tree (iterative) | `O(n)` | `O(log n)` | `O(log n)` any associative op | no | `O(2n)` | min, max, gcd, custom nodes |
| Segment tree (recursive) | `O(n)` | `O(log n)` | `O(log n)` | no | `O(4n)` | same, easier to extend |
| Lazy segment tree | `O(n)` | `O(log n)` | `O(log n)` | `O(log n)` add or assign | `O(8n)` | range update + range query |
| Sparse table | `O(n log n)` | none (rebuild) | `O(1)` idempotent | none | `O(n log n)` | static min/max/gcd |
| Sqrt decomposition | `O(n)` | `O(1)` to `O(B)` | `O(B)` to `O(B log n)` | `O(B)` | `O(n)` | odd per-block structures |
| Mo's algorithm | | static | `O((n + q) B)` total | no | `O(n + q)` | offline, easy add/remove |

### Questions to ask, in order

1. **Does the data change?** No: prefix sums (sum) or sparse table (min, max, gcd). Yes: continue.
2. **What is the operation?** If it is a sum, count or xor (has an inverse): a **Fenwick tree** is shortest and fastest. If it is min, max, gcd or a custom record: a **segment tree**.
3. **What kind of update?** Point: plain tree. Range add + sum: two Fenwick trees or a lazy tree. Range assign, or range add + min: **lazy segment tree**.
4. **Can I read the queries first?** Then try an offline sweep with a Fenwick tree, or Mo's algorithm.
5. **Is the data small enough that a simple `O(sqrt(n))` loop is fine?** Then sqrt decomposition is often the least error-prone.

### Practice: pick the structure

For each problem name the structure and the key idea. Cover the answers and decide first.

1. An array of 10^5 stock prices; 10^5 queries "highest price from day `l` to day `r`"; prices never change.
2. A leaderboard where scores change by point updates, and queries ask "how many players have score `< x`?" Scores up to 10^9.
3. Orders arrive; a query asks the total of orders from slot `l` to `r`; an order edits one slot.
4. "Add `v` to every cell from `l` to `r`", then "what is the minimum cell from `l` to `r`?", 10^5 operations.
5. Count pairs `(i, j)` with `i < j` and `a[i] > a[j]` in an array of 10^6 numbers.
6. 10^5 offline queries "how many distinct numbers in `a[l:r]`", array never changes.

<details><summary>Answer</summary>

1. **Sparse table** (static, max is idempotent), `O(1)` per query. A segment tree also works.
2. **Fenwick tree over compressed scores** (read all scores that may ever appear, rank them), then `prefix(rank of x)`. The tree stores counts per score.
3. **Fenwick tree** (point update, range sum), or an iterative segment tree.
4. **Lazy segment tree** with range add and range min (section 9). A Fenwick tree cannot do min.
5. **Fenwick tree with coordinate compression** (section 12) or merge sort. In Python, merge sort with lists may be faster at `10^6`; both are `O(n log n)`.
6. **Offline Fenwick sweep** by right end (section 17) or Mo's algorithm; the sweep is `O(n log n)`.

</details>

## 19. Python performance notes

### Where the time goes

A segment tree query in C++ takes microseconds. In Python the same `O(log n)` is dominated by **interpreter overhead**: every function call, every attribute lookup (`self.t`), every addition costs tens of nanoseconds. Over `10^5` or `10^6` operations that matters. The ideas below are about doing less interpretive work per operation.

### 1. Prefer the iterative tree and a Fenwick tree

The recursive tree makes a function call per visited node. Let us count: for `n = 100,000` and 2,000 random ranges, how many nodes does the recursive query visit, and how many loop passes does the iterative query make?

```python
def iter_loops(n, l, r):
    l += n
    r += n
    loops = 0
    while l < r:
        l = (l + 1) // 2 if l % 2 == 1 else l // 2
        r //= 2
        loops += 1
    return loops

rng = random.Random(17)
N = 100000
rec_total = it_total = 0
for _ in range(2000):
    l = rng.randint(0, N - 1)
    r = rng.randint(l + 1, N)
    rec_total += count_visits(1, 0, N, l, r)
    it_total += iter_loops(N, l, r)
print("recursive: average calls per query   :", round(rec_total / 2000, 1))
print("iterative: average loop passes per query:", round(it_total / 2000, 1))
```
```text
recursive: average calls per query   : 58.3
iterative: average loop passes per query: 13.6
```

The recursive query makes several times more steps, and each one is a full function call, which costs far more than a loop pass. In practice the iterative query is noticeably faster in CPython: the loop avoids the call overhead. (`iter_loops` reproduces the pointer movement of `IterSeg.query` without the combining, so that we count only the steps.)

### 2. The recursion limit is not your problem here

Python stops recursion at about 1,000 levels by default. A segment tree is balanced, so its recursion depth is about `log2(n)`:

```python
def depth(n):
    return 1 if n <= 1 else 1 + depth((n + 1) // 2)

print(depth(10**5), depth(10**6), depth(10**9))
```
```text
18 21 31
```

Even for a billion elements the depth is about 31. No `sys.setrecursionlimit` is needed. The recursion limit hurts with **unbalanced** recursions, such as a tree built over a long chain, or a "dynamic" segment tree grown by inserting in order into a linked structure. The segment tree is not one of them.

### 3. Other habits that pay off

- **Use flat lists, not node objects.** A list `t` indexed by `node` is much lighter than one Python object per node. A million objects with `__dict__` cost hundreds of megabytes.
- **Bind attributes to local names** inside hot loops: `t, f = self.t, self.f`, as `IterSeg.query` does. A local lookup is faster than `self.t` each time.
- **Avoid passing a combine function** for sum and min in contest code; write `t[i] = t[2*i] + t[2*i+1]` directly. The function-call overhead for each merge is large.
- **Build in `O(n)`**, not with `n` updates. Both the iterative tree and the Fenwick tree have a linear build (sections 6 and 10).
- **Read input in one go**, with `sys.stdin.read().split()`, if you have 10^5 or more numbers.
- **Know your sizes.** A sparse table for `n = 10^6` is too big; use a segment tree. A 2D Fenwick tree of `3000 x 3000` has 9 million cells, about 70 MB in lists: that is the practical limit.
- **Test against brute force** every time. These structures fail quietly.

### 4. When Python is simply too slow

If a problem needs `10^6` operations with a lazy segment tree, plain Python will likely time out: that is around 10^8 interpreter steps. Options: use the Fenwick-based version if the problem allows it; reduce the constant by using the iterative approach; or move the heavy part to NumPy or another language. In this course, correctness and understanding come first; the same code ports to C++ or Java almost line by line.

## 20. Common traps, collected

1. **1-indexing in the Fenwick tree.** Index 0 loops forever in `add`, and `prefix` of 0 is the empty sum. Store from 1, or hide the shift inside the class.
2. **Half-open versus closed.** Decide once. With `[l, r)`, the empty range is `l == r`, the length is `r - l`, "no overlap" is `r <= lo or hi <= l`, and "inside" is `l <= lo and hi <= r`. A mixed `<` / `<=` returns a node twice or never.
3. **Tree size.** Recursive segment tree: `4 * n`, not `2 * n`. Iterative: exactly `2 * n`.
4. **The wrong identity.** `0` for min returns zeros for partial queries. Use `inf` for min, `-inf` for max, `0` for gcd and sum.
5. **Forgetting to recompute after the children return.** In update and range-add, set `s[node]` from the children afterwards, or the parent stays stale.
6. **Forgetting to push down before descending.** In both the update and the query. A missing push gives wrong answers silently, for some ranges only.
7. **Pushing in the wrong order.** Push **before** you recurse into the children, and recompute **after** they return. Applying a tag to a node and also pushing it to its children in the same step counts it twice.
8. **`0` as the "no tag" marker for assignment.** Assigning `0` looks the same as no tag. Use `None` and test `is not None`.
9. **Lazy tags that do not compose.** Add then assign is not assign then add. Write the composition rule before the code (section 9), and keep the invariant (either assign or add, not both).
10. **Leaf length in `apply`.** For sum with range add the node's sum grows by `v * (hi - lo)`, not `v`. For min it grows by `v`.
11. **A non-commutative combine in the iterative tree.** Keep `resl` and `resr` separate; combining into a single accumulator scrambles the order.
12. **Fenwick tree for range minimum.** It needs an inverse. It works for prefix minimum only when values only decrease.
13. **A sparse table with a non-idempotent operation.** Overlapping blocks double count. Use idempotent operations or disjoint blocks.
14. **Skipping coordinate compression.** A Fenwick tree with a cell per value needs the maximum value as its size.
15. **Counting equal values as inversions.** Use `seen - prefix(rank + 1)` (strictly greater), not `seen - prefix(rank)`.
16. **Mo's algorithm: shrinking before growing.** Counts go negative and the answer is garbage.
17. **Recursion for point-only trees in tight loops.** Not wrong, but slow. Choose the iterative tree unless you need lazy propagation or a descent.
18. **Building the tree with `n` updates.** It works, but costs `O(n log n)` where `O(n)` is possible.
19. **Not testing the empty range and the single element.** `query(l, l)` must give the identity; `n = 1` must not crash.
20. **Trusting a hand-sized test.** Compare against a brute-force loop on a few hundred random small cases, with duplicates and negative numbers.

## 21. Summary

- **Prefix sums** answer range sums in `O(1)` but break on updates: one change costs `O(n)`. A plain loop has the opposite trade. The structures in this module give `O(log n)` for both.
- A **segment tree** stores the answer for every range of a halving of the array. A **query** covers `[l, r)` with `O(log n)` whole nodes (three cases: no overlap, inside, partial); an **update** fixes one root-to-leaf path. Allocate `4n` for the recursive form, `2n` for the iterative form.
- It works with any **associative combine** and its **identity**: sum, min, max, gcd, xor, and custom records such as `(total, best_prefix, best_suffix, best)` for the maximum subarray sum. For non-commutative merges keep left and right accumulators apart.
- The **iterative** (bottom-up) tree puts leaves at `n..2n-1` and walks up from both ends: shorter and faster in Python. A **descent** from the root finds the k-th item (for example the k-th zero).
- **Lazy propagation** allows range updates in `O(log n)`: apply the change to the covering nodes, leave a **tag** for the children, **push down before descending**, recompute after. Tags must compose: add + add sums, assign replaces, add after assign merges into the assign. Use `None` as "no assignment".
- The **Fenwick tree** stores, in `t[i]`, the sum of the `lowbit(i)` elements ending at `i`. Query: `i -= i & -i`. Update: `i += i & -i`. It needs 1-indexing, `O(n)` memory, `O(log n)` per operation, and an operation with an inverse.
- Fenwick extensions: **range add + point query** (tree over differences), **range add + range sum** (two trees, `prefix(p) = p * B1(p) - B2(p)`), **inversions** (coordinate compression, count strictly greater), **k-th element** (binary descent over powers of two), **2D** (nested loops, `O(log R log C)`).
- The **sparse table** answers idempotent queries (min, max, gcd) on static data in `O(1)` after an `O(n log n)` build, using two overlapping power-of-two blocks. It fails for sums because the overlap is counted twice; use disjoint blocks (`O(log n)`) or prefix sums.
- **Square-root decomposition** splits the array into blocks of size `sqrt(n)`, each holding a summary (a sum, or a sorted list): `O(sqrt n)` per query. **Mo's algorithm** answers offline range queries by sorting them by block and sliding a window, in `O((n + q) sqrt n)`.
- **Offline** queries allow sweeps and reordering (Fenwick by right end, Mo's); **online** (forced) queries need a structure that answers anything at any time.
- In Python: prefer flat lists, iterative trees, local variable binding, a linear build, and always verify against brute force. The recursion limit is not a concern for balanced trees (depth about `log2 n`).

### Learning outcomes checklist

- [ ] I can explain why prefix sums fail with updates and what the cost of each simple strategy is.
- [ ] I can write a recursive segment tree with build, point update and range query, and say why it needs `4n` cells.
- [ ] I can trace which nodes a query visits and which nodes an update changes.
- [ ] I can write the generic version with a combine and an identity, for sum, min, max and gcd.
- [ ] I can write the iterative bottom-up tree, and keep left and right accumulators for non-commutative merges.
- [ ] I can design a custom node, such as the maximum subarray record, and test it against brute force.
- [ ] I can write a lazy segment tree for range add + sum, range assign + sum and range add + min, and explain when to push.
- [ ] I can write a Fenwick tree from memory and explain `i & -i`, the query path and the update path.
- [ ] I can do range add + point query, and range add + range sum with two Fenwick trees.
- [ ] I can count inversions with a Fenwick tree and coordinate compression.
- [ ] I can find the k-th element by descending a Fenwick tree or a segment tree.
- [ ] I can build a sparse table, answer `O(1)` range-minimum queries, and say why it fails for sums.
- [ ] I can use square-root decomposition and explain Mo's algorithm in a few sentences.
- [ ] I can say, for a given problem, whether it is online or offline and pick a structure from the table in section 18.
