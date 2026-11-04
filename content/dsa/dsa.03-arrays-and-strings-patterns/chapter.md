# dsa.03 Arrays and strings patterns

## 1. Why patterns, and how to recognise them

Most array and string problems can be solved by a "try everything" program: two nested loops that look at every
pair `(i, j)`, or every subarray `a[i..j]`. That program is easy to write and usually correct. It is also usually
too slow. With `n = 200,000` there are about `2 * 10^10` pairs, and Python does roughly `10^7` simple steps per
second, so the brute force would run for more than half an hour. The judge gives you one or two seconds.

The good news: the fast solutions are not a thousand different clever tricks. Almost all of them are one of six
**patterns**, each a small, reusable shape of code:

1. **Prefix sums**: precompute running totals once, then answer every "sum of `a[l..r]`" in `O(1)`.
2. **Difference arrays**: the reverse of prefix sums. Apply many "add `v` to `a[l..r]`" updates in `O(1)` each,
   then read the final array once.
3. **Two pointers**: two indices that only ever move in one direction each, for sorted data, in-place rewriting,
   and merging.
4. **Sliding window**: a contiguous block `a[l..r]` that slides right, adding one element on the right and removing
   one on the left, instead of being recomputed from scratch.
5. **Kadane's algorithm**: the best subarray sum ending at each index, carried forward in one pass.
6. **Matrix traversal**: walking a grid in a planned order (row by row, spiral, diagonals, neighbours, a robot
   with a direction), with careful bounds.

Each one turns an `O(n^2)` (or worse) scan into `O(n)` or `O(n + q)`. The work of this chapter is to understand
**why** each pattern is correct, so you can trust it, and to learn the **signals** that tell you which one a
problem wants.

### Signal 1: the constraints

Before reading the story of a problem, read its limits. In Python, a safe rule of thumb (from dsa.01):

| Largest `n` | What fits in about one second | Typical pattern |
|---|---|---|
| `n <= 20` | `2^n` subsets | brute force over subsets |
| `n <= 500` | `n^3` | three nested loops, 2D Kadane on a 100 x 100 grid |
| `n <= 5,000` | `n^2` | all pairs, all subarrays |
| `n <= 2 * 10^5` or `10^6` | `n` or `n log n` | prefix sums, two pointers, sliding window, Kadane, sorting |

So when you see `n <= 2 * 10^5`, the double loop over all subarrays is **ruled out before you start**. You know you
need one pass (or a sort plus one pass). That alone narrows the choice to the patterns in this chapter.

### Signal 2: the wording

| Words in the statement | Think of |
|---|---|
| "sum of elements from index `l` to `r`", many queries | prefix sums |
| "add `v` to every element from `l` to `r`", many updates, then print | difference array |
| "number of subarrays whose sum is `k`" (negatives allowed) | prefix sums + dictionary |
| "sorted array", "pair", "triplet", "closest to target" | two pointers from both ends |
| "in place", "without extra memory", "remove", "move to the end" | slow/fast pointers |
| "every window of size `k`" | fixed sliding window |
| "longest / shortest substring or subarray such that ..." | variable sliding window |
| "maximum subarray sum", "best profit" | Kadane |
| "maximum of every window" | monotonic deque |
| "grid", "matrix", "neighbours", "rotate", "spiral" | matrix traversal |

One word deserves special attention: **contiguous**. A *subarray* or *substring* is a contiguous block
`a[l], a[l+1], ..., a[r]`. A *subsequence* may skip elements. Every pattern in this chapter is about contiguous
blocks (or pairs). If the problem says "subsequence", it is usually a different module (dynamic programming).

**Try it 1: contiguous or not?**

For `a = [3, 1, 4, 1, 5]`, which of these are subarrays? (a) `[1, 4, 1]` (b) `[3, 4, 5]` (c) `[5]`
(d) `[]` (e) `[4, 1, 5]` (f) `[1, 5]` taken as `a[1], a[4]`.

<details><summary>Answer</summary>

(a) yes, `a[1..3]`. (b) no, it skips elements: it is a subsequence. (c) yes, a single element is a subarray of
length 1. (d) an empty subarray exists mathematically, but most problems say "non-empty" (always check; it matters
for Kadane in section 9). (e) yes, `a[2..4]`. (f) no: the values `1, 5` *do* appear next to each other as
`a[3..4]`, but `a[1], a[4]` are not neighbours, so that choice of positions is a subsequence.
</details>

### How many subarrays are there?

An array of length `n` has `n * (n + 1) / 2` non-empty subarrays: choose a start `l` (n ways), and an end
`r >= l`. Let us count them by brute force and compare with the formula:

```python
def count_subarrays(n):
    return sum(1 for l in range(n) for r in range(l, n))

for n in [1, 2, 3, 10, 1000]:
    print(n, count_subarrays(n), n * (n + 1) // 2)
```
```text
1 1 1
2 3 3
3 6 6
10 55 55
1000 500500 500500
```

For `n = 200,000` the formula gives about `2 * 10^10`. Any program that **visits** every subarray is too slow,
even if it does only `O(1)` work per subarray. A brute force that also **re-sums** each subarray does `O(n)` work
per subarray, `O(n^3)` total, and is slow even for `n = 1,000`.

The patterns below avoid visiting every subarray. Prefix sums answer a question about one subarray in `O(1)`
without looping over it. A sliding window visits only `O(n)` windows and proves the others cannot be the answer.
Kadane remembers, for each end `r`, only the single best start.

### Reading the input

The problems in this module are scripts: they read standard input and print lines. With up to `2 * 10^5` numbers,
calling `input()` in a loop is fine, but the safest habit is to read everything at once:

```python
import sys

def main():
    data = sys.stdin.read().split()
    n = int(data[0])
    a = [int(x) for x in data[1:1 + n]]
    print(n, a, sum(a))

main()
```
```text
5 [3, 1, 4, 1, 5] 14
```

Note what `split()` does with an empty array: for the input `0` followed by an empty line, `data` is `['0']`, and
`data[1:1]` is an empty list, so `a = []` without any special case. The same code handles `n = 0`.

For a grid, the usual input is `r c` on the first line and then `r` lines. A row of characters like `"..#."` is one
word for `split()`; turn it into a list with `list(word)` if you need to change cells, because strings are **immutable**.

### Strings are arrays too

Every pattern here works on strings: `s[i]` is a character, `len(s)` is the length, `s[l:r+1]` is the substring
`s[l..r]`. Two Python facts to keep in mind:

- **Slicing copies.** `s[l:r]` and `a[l:r]` build a new object of length `r - l`, so they cost `O(r - l)`, not
  `O(1)`. A loop that slices a window of size `k` at every step is `O(n * k)`, which is the brute force in
  disguise. Inside a loop, keep indices and running values; slice only at the end to print the answer.
- **`s += ch` in a loop** may copy the whole string each time. Collect characters in a list and `"".join` at the end.

## 2. Prefix sums

### The problem: many range-sum questions

You have an array of `n` numbers and `q` questions, each "what is `a[l] + a[l+1] + ... + a[r]`?". The direct answer
loops from `l` to `r` for each question: up to `n` steps per question, `q * n` in total. With `n = q = 2 * 10^5`
that is `4 * 10^10` steps. Hopeless.

The observation that saves us: all those questions share work. The sum of `a[2..7]` and the sum of `a[2..8]` differ
by one element. If we knew the running total up to every position, any range would be **a difference of two
running totals**.

### The definition

Define the **prefix sum array** `P` of length `n + 1`:

- `P[0] = 0` (the sum of the first zero elements),
- `P[i] = a[0] + a[1] + ... + a[i-1]` (the sum of the first `i` elements).

Then, for any `0 <= l <= r < n`:

```text
sum(a[l..r]) = P[r + 1] - P[l]
```

Why? `P[r + 1]` is the sum of `a[0..r]`. `P[l]` is the sum of `a[0..l-1]`. Subtracting removes exactly the part
before `l`, leaving `a[l..r]`. Picture it for `l = 2, r = 4`:

```text
index:      0   1   2   3   4   5
a:          3   1   4   1   5   9
P[5]:      [3 + 1 + 4 + 1 + 5]          = 14
P[2]:      [3 + 1]                      =  4
P[5]-P[2]:         [4 + 1 + 5]          = 10
```

The extra `0` at the front is not decoration. It makes the formula work for `l = 0` (then `P[l] = P[0] = 0`)
without an `if`. This is the most common prefix-sum bug: building `P` of length `n` with `P[i] = a[0..i]`, and
then needing a special case for ranges that start at `0`.

### Building it

One pass, each entry is the previous one plus one element:

```python
a = [3, 1, 4, 1, 5, 9, 2, 6]
P = [0] * (len(a) + 1)
for i in range(len(a)):
    P[i + 1] = P[i] + a[i]
print("a =", a)
print("P =", P)

def range_sum(l, r):          # 0-based, inclusive
    return P[r + 1] - P[l]

for l, r in [(0, 0), (2, 4), (0, 7), (5, 5), (3, 6)]:
    print(f"sum a[{l}..{r}] = {range_sum(l, r)}  check {sum(a[l:r + 1])}")
```
```text
a = [3, 1, 4, 1, 5, 9, 2, 6]
P = [0, 3, 4, 8, 9, 14, 23, 25, 31]
sum a[0..0] = 3  check 3
sum a[2..4] = 10  check 10
sum a[0..7] = 31  check 31
sum a[5..5] = 9  check 9
sum a[3..6] = 17  check 17
```

The standard library has the same thing: `list(itertools.accumulate(a, initial=0))` builds exactly this `P`.
Without `initial=0` you get the running totals *without* the leading zero (length `n`). In this chapter we write the
loop, because it makes the indices visible.

### 1-based queries

Many problem statements number positions from 1: "query `l r` means `a_l + ... + a_r`, with `1 <= l <= r <= n`".
Our `P` is perfect for that, because `P[i]` is "the sum of the first `i` elements":

```text
sum of positions l..r (1-based) = P[r] - P[l - 1]
```

No `+1` and no conversion. The two formulas, side by side:

| Indexing of the query | Formula |
|---|---|
| 0-based `l..r` | `P[r + 1] - P[l]` |
| 1-based `l..r` | `P[r] - P[l - 1]` |

Mixing these two up is the second most common prefix-sum bug. Before writing the formula, check it on the
smallest case: a one-element range must give that one element.

**Try it 2: predict the output**

```python
a = [5, -2, 7, 0, 3]
P = [0]
for x in a:
    P.append(P[-1] + x)
print(P)
print(P[3] - P[1])
print(P[5] - P[0])
print(P[4] - P[4])
```

Which 1-based range does `P[3] - P[1]` answer? Which 0-based range?

<details><summary>Answer</summary>

```text
[0, 5, 3, 10, 10, 13]
5
13
0
```

`P = [0, 5, 3, 10, 10, 13]`. `P[3] - P[1] = 10 - 5 = 5`: 1-based positions `2..3` (`-2 + 7`), which is 0-based
`1..2`. `P[5] - P[0]` is the whole array. `P[4] - P[4] = 0` is the **empty** range: equal indices in a difference
of prefix sums mean "no elements", which is not the same as "one element".
</details>

### Why this is a big win: counting steps

We count additions instead of measuring time, so the result is the same on every machine:

```python
def steps_recompute(n, q):
    # each query loops over up to n elements
    return q * n

def steps_prefix(n, q):
    # n additions to build P, then 1 subtraction per query
    return n + q

for n, q in [(10, 10), (1000, 1000), (200000, 200000)]:
    r, p = steps_recompute(n, q), steps_prefix(n, q)
    print(f"n={n:>6} q={q:>6}  recompute={r:>12}  prefix={p:>7}  ratio={r // p}")
```
```text
n=    10 q=    10  recompute=         100  prefix=     20  ratio=5
n=  1000 q=  1000  recompute=     1000000  prefix=   2000  ratio=500
n=200000 q=200000  recompute= 40000000000  prefix= 400000  ratio=100000
```

The ratio is `n * q / (n + q)`, about `n / 2` when `q = n`. For `n = 2 * 10^5` the prefix version does 100,000 times
less work. The price: one extra list of `n + 1` integers, `O(n)` memory. That is the classic trade: **spend memory
once to save time on every query.** It pays off as soon as there is more than about one query, and it only works
because the array **does not change** between queries. If the values are updated between queries, you need a
different structure (a Fenwick tree or segment tree, later in the course).

### Worked example: equilibrium index

*Find the first index `i` such that the sum of elements to its left equals the sum to its right
(the element itself is in neither side). Print `-1` if there is none.*

Brute force: for each `i`, sum both sides: `O(n^2)`. With a running left sum and the total, the right sum is
`total - left - a[i]`, so one pass suffices:

```python
def equilibrium(a):
    total = sum(a)
    left = 0
    for i, x in enumerate(a):
        right = total - left - x
        if left == right:
            return i
        left += x
    return -1

print(equilibrium([1, 7, 3, 6, 5, 6]))
print(equilibrium([1, 2, 3]))
print(equilibrium([2, 1, -1]))
print(equilibrium([5]))
print(equilibrium([]))
```
```text
3
-1
0
0
-1
```

Check the cases. `[1, 7, 3, 6, 5, 6]`: at `i = 3`, left `1 + 7 + 3 = 11`, right `5 + 6 = 11`. `[2, 1, -1]`: at `i = 0`
the left side is empty (sum `0`) and the right is `1 + (-1) = 0`, so the answer is `0`. A single element has two empty
sides, so `[5]` gives `0`. Note the order inside the loop: compute `right` and compare **before** adding `x` to `left`.
Adding first is an off-by-one that puts `a[i]` on the left.

This is still the prefix-sum idea: `left` is `P[i]`, and `total - left - x` is `P[n] - P[i + 1]`. We just never
stored the whole array `P`, because we only needed each value once, in order.

### Worked example: product of the array except self

*For each `i`, output the product of all elements except `a[i]`. Do not use division (there may be zeros).*

Division would be `total_product // a[i]`, which breaks when `a[i] = 0`. Instead, use the prefix idea with
products: `left[i]` = product of `a[0..i-1]`, `right[i]` = product of `a[i+1..n-1]`, and the answer is
`left[i] * right[i]`. The "empty product" is `1`, just as the empty sum is `0`.

```python
def product_except_self(a):
    n = len(a)
    ans = [1] * n
    run = 1
    for i in range(n):            # ans[i] = product of a[0..i-1]
        ans[i] = run
        run *= a[i]
    run = 1
    for i in range(n - 1, -1, -1):  # multiply by product of a[i+1..n-1]
        ans[i] *= run
        run *= a[i]
    return ans

print(product_except_self([1, 2, 3, 4]))
print(product_except_self([2, 0, 5]))
print(product_except_self([0, 0, 3]))
print(product_except_self([-1, 4]))
```
```text
[24, 12, 8, 6]
[0, 10, 0]
[0, 0, 0]
[4, -1]
```

Trace `[1, 2, 3, 4]`. The first loop stores the left products `[1, 1, 2, 6]`. The second loop walks from the right
with `run = 1, 4, 12, 24` and multiplies: `ans[3] = 6 * 1 = 6`, `ans[2] = 2 * 4 = 8`, `ans[1] = 1 * 12 = 12`,
`ans[0] = 1 * 24 = 24`. Same rule as before: **store, then update** the running value, so `a[i]` is never included
in its own answer.

### 2D prefix sums

Now the questions are about rectangles in a grid: "what is the sum of the cells in rows `r1..r2` and columns
`c1..c2`?". Define `P` with one extra row and one extra column of zeros:

```text
P[i][j] = sum of all cells grid[x][y] with x < i and y < j
        = the sum of the top-left i x j block
```

**Building** `P` uses inclusion and exclusion. The block ending at `(i, j)` is the block above it, plus the block to
its left, minus their overlap (counted twice), plus the new cell:

```text
P[i+1][j+1] = P[i][j+1] + P[i+1][j] - P[i][j] + grid[i][j]
```

**Querying** the rectangle with corners `(r1, c1)` and `(r2, c2)` (0-based, inclusive) is the same idea in reverse:
take the big top-left block, remove the strip above, remove the strip to the left, and add back the corner that was
removed twice:

```text
sum = P[r2+1][c2+1] - P[r1][c2+1] - P[r2+1][c1] + P[r1][c1]
```

```text
        c1      c2
    +---+-------+
    | D |   B   |        P[r2+1][c2+1] = A + B + C + D
 r1 +---+-------+        P[r1][c2+1]   = B + D
    | C |   A   |        P[r2+1][c1]   = C + D
 r2 +---+-------+        P[r1][c1]     = D
                         A = big - (B+D) - (C+D) + D
```

```python
grid = [
    [1, 2, 3, 4],
    [5, 6, 7, 8],
    [9, 10, 11, 12],
]
R, C = len(grid), len(grid[0])
P = [[0] * (C + 1) for _ in range(R + 1)]
for i in range(R):
    for j in range(C):
        P[i + 1][j + 1] = P[i][j + 1] + P[i + 1][j] - P[i][j] + grid[i][j]
for row in P:
    print(row)

def rect(r1, c1, r2, c2):
    return P[r2 + 1][c2 + 1] - P[r1][c2 + 1] - P[r2 + 1][c1] + P[r1][c1]

def brute(r1, c1, r2, c2):
    return sum(grid[i][j] for i in range(r1, r2 + 1) for j in range(c1, c2 + 1))

for q in [(1, 1, 2, 2), (0, 0, 2, 3), (2, 3, 2, 3), (0, 1, 1, 2)]:
    print(q, rect(*q), brute(*q))
```
```text
[0, 0, 0, 0, 0]
[0, 1, 3, 6, 10]
[0, 6, 14, 24, 36]
[0, 15, 33, 54, 78]
(1, 1, 2, 2) 34 34
(0, 0, 2, 3) 78 78
(2, 3, 2, 3) 12 12
(0, 1, 1, 2) 18 18
```

Check one query by hand: rows `1..2`, columns `1..2` are the cells `6, 7, 10, 11`, total `34`. From `P`:
`P[3][3] - P[1][3] - P[3][1] + P[1][1] = 54 - 6 - 15 + 1 = 34`. Matches.

Building costs `O(R * C)`, each query `O(1)`. The same inclusion-exclusion shape appears in every 2D prefix problem,
so learn the picture rather than the formula: **big block, minus top strip, minus left strip, plus the corner.**

**Try it 3: find the bug**

This builder gives wrong values for some cells. Which line is wrong and what does it compute instead?

```python
grid = [[1, 1], [1, 1]]
P = [[0] * 3 for _ in range(3)]
for i in range(2):
    for j in range(2):
        P[i + 1][j + 1] = P[i][j + 1] + P[i + 1][j] + grid[i][j]
print(P[2][2])
```

<details><summary>Answer</summary>

```text
5
```

The building line forgets `- P[i][j]`. The overlap (the block above-left) is counted twice, so the total of four
ones comes out as `5` instead of `4`. In bigger grids the error grows quickly. Always write all four terms.
</details>

**Try it 4: by hand**

Write `P` for `a = [2, 4, 6, 8]`, then answer the 1-based query `2 4` and the 0-based query `0 0`.

<details><summary>Answer</summary>

`P = [0, 2, 6, 12, 20]`. 1-based `2..4`: `P[4] - P[1] = 20 - 2 = 18` (`4 + 6 + 8`). 0-based `0..0`:
`P[1] - P[0] = 2`.
</details>

## 3. Prefix sums with a dictionary

### Turning "a subarray with sum k" into "two prefix sums"

The question changes: not "what is the sum of this range?" but "**how many** subarrays have sum exactly `k`?".
The array may contain negative numbers.

Start from the formula. The subarray `a[l..r]` has sum `P[r + 1] - P[l]`. So

```text
sum(a[l..r]) == k   <=>   P[l] == P[r + 1] - k
```

Read it from the point of view of the **right end**. We walk through the array once, keeping the current prefix
sum `cur` (which is `P[r + 1]` after reading `a[r]`). The number of good subarrays that **end at `r`** is the number
of earlier prefix sums equal to `cur - k`. If we keep a dictionary `seen` that counts how many times each prefix sum
value has appeared so far, the answer for this `r` is `seen.get(cur - k, 0)`. One dictionary lookup per element:
`O(n)` total instead of `O(n^2)` pairs.

```python
def count_sum_k(a, k):
    seen = {0: 1}          # the empty prefix P[0] = 0 has been seen once
    cur = 0
    count = 0
    for x in a:
        cur += x
        count += seen.get(cur - k, 0)
        seen[cur] = seen.get(cur, 0) + 1
    return count

for a, k in [([1, 1, 1], 2), ([1, 2, 3], 3), ([1, -1, 0], 0), ([3, 4, 7, 2, -3, 1, 4, 2], 7), ([], 0)]:
    print(a, k, count_sum_k(a, k))
```
```text
[1, 1, 1] 2 2
[1, 2, 3] 3 2
[1, -1, 0] 0 3
[3, 4, 7, 2, -3, 1, 4, 2] 7 4
[] 0 0
```

Three details make or break this code.

1. **`seen = {0: 1}` before the loop.** This is the empty prefix `P[0]`. Without it, subarrays that start at index
   `0` are never counted. In `[1, 2, 3]` with `k = 3`, the subarray `[1, 2]` needs `cur - k = 3 - 3 = 0` to have been
   seen.
2. **Look up first, then insert.** If you insert `cur` before looking up `cur - k`, then for `k = 0` every position
   matches itself, and you count empty subarrays.
3. **It works with negative numbers and zeros.** Nothing in the argument needs the values to be positive. This is
   exactly why we use it when a sliding window fails (section 7).

### Hand trace

Trace `a = [3, 4, 7, 2, -3, 1, 4, 2]`, `k = 7`. The table shows `cur`, the value we look up (`cur - 7`), how many
times it was seen, and the dictionary after inserting `cur`:

```python
a, k = [3, 4, 7, 2, -3, 1, 4, 2], 7
seen = {0: 1}
cur = count = 0
print(f"{'x':>3} {'cur':>4} {'need':>5} {'found':>5} {'count':>5}  seen")
for x in a:
    cur += x
    found = seen.get(cur - k, 0)
    count += found
    seen[cur] = seen.get(cur, 0) + 1
    print(f"{x:>3} {cur:>4} {cur - k:>5} {found:>5} {count:>5}  {seen}")
```
```text
  x  cur  need found count  seen
  3    3    -4     0     0  {0: 1, 3: 1}
  4    7     0     1     1  {0: 1, 3: 1, 7: 1}
  7   14     7     1     2  {0: 1, 3: 1, 7: 1, 14: 1}
  2   16     9     0     2  {0: 1, 3: 1, 7: 1, 14: 1, 16: 1}
 -3   13     6     0     2  {0: 1, 3: 1, 7: 1, 14: 1, 16: 1, 13: 1}
  1   14     7     1     3  {0: 1, 3: 1, 7: 1, 14: 2, 16: 1, 13: 1}
  4   18    11     0     3  {0: 1, 3: 1, 7: 1, 14: 2, 16: 1, 13: 1, 18: 1}
  2   20    13     1     4  {0: 1, 3: 1, 7: 1, 14: 2, 16: 1, 13: 1, 18: 1, 20: 1}
```

The four subarrays are `[3, 4]`, `[7]`, `[7, 2, -3, 1]` and `[1, 4, 2]`. Find each one in the table: for example, at
the last step `cur = 20`, we need `13`, which was seen once (after `7, 2, -3`, that is `P[5] = 13`), so the subarray
starts at index `5`: `a[5..7] = [1, 4, 2]`. Notice how `cur = 14` appears both after the `7` and after the `1`, so
the dictionary stores the count `2` for it: later, if we needed `14`, both earlier positions would count.

### Longest subarray with sum k: store the first index

Now the question is "what is the **length of the longest** subarray with sum `k`?". The same equation holds, but
instead of counting the earlier positions with `P[l] == cur - k`, we want the **earliest** one, because the
earliest start gives the longest subarray ending here.

So the dictionary maps a prefix-sum value to the **first index** where it appeared, and we never overwrite an entry.
The empty prefix sits at index `-1` (before the array starts), so that a subarray starting at `0` has length
`r - (-1) = r + 1`.

```python
def longest_sum_k(a, k):
    first = {0: -1}
    cur = 0
    best = 0
    for r, x in enumerate(a):
        cur += x
        if cur - k in first:
            best = max(best, r - first[cur - k])
        if cur not in first:          # keep only the FIRST index
            first[cur] = r
    return best

for a, k in [([1, -1, 5, -2, 3], 3), ([-2, -1, 2, 1], 1), ([1, 2, 3], 7), ([0, 0, 0], 0), ([2, -2, 2, -2], 0)]:
    print(a, k, longest_sum_k(a, k))
```
```text
[1, -1, 5, -2, 3] 3 4
[-2, -1, 2, 1] 1 2
[1, 2, 3] 7 0
[0, 0, 0] 0 3
[2, -2, 2, -2] 0 4
```

The tempting bug is writing `first[cur] = r` unconditionally. Then the dictionary remembers the **last** index of each
prefix sum, and the subarrays you find are the shortest ones, not the longest. For `[0, 0, 0]` with `k = 0`, the
correct answer is `3` (the whole array). With overwriting, every lookup finds the previous index, and the answer is `1`.

**Try it 5: count vs longest**

For `a = [1, -1, 1, -1]` and `k = 0`: how many subarrays have sum `0`? What is the longest one? Write the
prefix sums first.

<details><summary>Answer</summary>

Prefix sums (with the leading `0`): `0, 1, 0, 1, 0`. Equal pairs of prefix sums are zero-sum subarrays. The value
`0` appears 3 times (3 choose 2 = 3 pairs) and the value `1` appears 2 times (1 pair), so there are **4** subarrays:
`[1, -1]` twice, `[-1, 1]`, and the whole array. The longest is the whole array, length **4**, from the first `0`
(index `-1`) to the last (index `3`). Running `count_sum_k` and `longest_sum_k` from above on it prints:

```text
4 4
```
</details>

### Subarrays with sum divisible by k

*Count subarrays whose sum is divisible by `k`.* Now the condition is `(P[r + 1] - P[l]) % k == 0`, which is the same
as `P[r + 1] % k == P[l] % k`. Two prefix sums with the **same remainder** bound a good subarray. So we count prefix
sums by their remainder, and each new prefix pairs with every earlier one that has the same remainder.

Negative numbers raise the question: what is `-3 % 5`? In Python it is `2`, always in `0 .. k-1` for positive `k`
(you met this in dsa.02). That is exactly what we need: the prefix sums `-3` and `2` differ by `5`, so they must land
in the same bucket, and in Python they do. In C++ or Java, `-3 % 5` is `-3`, and the code needs the extra fix
`((x % k) + k) % k`. In Python, writing that fix is harmless but unnecessary.

```python
def count_divisible(a, k):
    seen = {0: 1}
    cur = 0
    count = 0
    for x in a:
        cur = (cur + x) % k
        count += seen.get(cur, 0)
        seen[cur] = seen.get(cur, 0) + 1
    return count

print(-3 % 5, 7 % 5, (-8) % 5)
for a, k in [([4, 5, 0, -2, -3, 1], 5), ([5], 9), ([-1, 2, 9], 2), ([-5, -5], 5)]:
    print(a, k, count_divisible(a, k))
```
```text
4 4
2 2 2
[4, 5, 0, -2, -3, 1] 5 7
[5] 9 0
[-1, 2, 9] 2 2
[-5, -5] 5 3
```

Keeping `cur` reduced (`cur = (cur + x) % k`) is fine because remainders of sums only depend on remainders. It also
keeps the dictionary small: at most `k` keys.

**Try it 6: why did C++ programmers get this wrong?**

In C++ the remainder has the sign of the dividend, so `-1 % 2` is `-1` there.
For `a = [-1, 2, 9]` and `k = 2`, the prefix sums are `0, -1, 1, 10`. Group them by Python remainder and by
C++ remainder. How many pairs does each grouping give, and which is right?

<details><summary>Answer</summary>

Python remainders: `0, 1, 1, 0`. Two zeros (1 pair) and two ones (1 pair): **2** subarrays, `[-1, 2, 9]` (sum `10`)
and `[2]` (sum `2`). That matches what `count_divisible` printed above.

C++ remainders: `0, -1, 1, 0`. Now `-1` and `1` land in different buckets, so the pair for `[2]` (prefix sums `-1`
and `1`, difference `2`) is missed: only **1** subarray. Python's `%` is right here without a fix; in C++ you must
add `k` and reduce again.
</details>

## 4. Difference arrays

### The problem: many range updates, one final read

You start with an array (often all zeros) and receive `q` updates, each "add `v` to every element from `l` to `r`".
After all updates, print the array. The direct way loops from `l` to `r` per update: `O(q * n)` again.

Here is the trick, as a story. A bus drives along stops `0..n-1`. Each group of `v` passengers boards at stop `l` and
gets off after stop `r`. To know how many passengers are on board at each stop, you do not need to walk every group
along its route. You just write `+v` at the boarding stop and `-v` at the stop after the last one, and then walk the
route once, keeping a running total. That running total is the load at each stop.

### The definition

Make an array `D` of length `n + 1` (one extra slot, so `r + 1` never goes out of range). For each update `(l, r, v)`:

```text
D[l]     += v
D[r + 1] -= v
```

Then take the prefix sum of `D`: `a[i] = D[0] + D[1] + ... + D[i]`.

### Why it works

Look at one update `(l, r, v)` and one position `i`. The running total at `i` includes `D[0..i]`.

- If `i < l`, neither `+v` (at `l`) nor `-v` (at `r + 1`) is inside `D[0..i]`. Contribution `0`.
- If `l <= i <= r`, the `+v` is inside and the `-v` is not. Contribution `v`.
- If `i > r`, both are inside and cancel. Contribution `0`.

So each update adds exactly `v` to the positions `l..r` and nothing elsewhere. Several updates just add up, because
each one contributes independently. That is the whole proof. Difference arrays and prefix sums are inverse
operations: the prefix sum of the difference array is the array.

```python
def apply_updates(n, updates):
    D = [0] * (n + 1)
    for l, r, v in updates:          # 0-based, inclusive
        D[l] += v
        D[r + 1] -= v
    print("D =", D)
    a = [0] * n
    run = 0
    for i in range(n):
        run += D[i]
        a[i] = run
    return a

ups = [(1, 3, 5), (0, 1, 2), (2, 4, -1), (4, 4, 10)]
print(apply_updates(5, ups))
```
```text
D = [2, 5, -3, 0, 5, -9]
[2, 7, 4, 4, 9]
```

Trace it, one update at a time:

- `(1, 3, 5)`: `D[1] += 5`, `D[4] -= 5`.
- `(0, 1, 2)`: `D[0] += 2`, `D[2] -= 2`.
- `(2, 4, -1)`: `D[2] -= 1`, `D[5] += 1`.
- `(4, 4, 10)`: `D[4] += 10`, `D[5] -= 10`.

So `D[0] = 2`, `D[1] = 5`, `D[2] = -2 - 1 = -3`, `D[3] = 0`, `D[4] = -5 + 10 = 5`, `D[5] = 1 - 10 = -9`, exactly the
printed `D`. The running sum of `D[0..4]` is `2, 7, 4, 4, 9`. Each update cost `O(1)`; the final pass is
`O(n)`. Total `O(n + q)`.

If the array does not start at zero, either add the initial values in the final pass (`a[i] = initial[i] + run`), or
build `D` from the initial array: `D[0] = a[0]` and `D[i] = a[i] - a[i - 1]`. That second form explains the name: `D`
stores the **differences** between neighbours, and a range add changes only two differences (the one entering the
range and the one leaving it).

### 1-based updates

With `1 <= l <= r <= n`, allocate `D` of length `n + 2` and use `D[l] += v`, `D[r + 1] -= v`, then read positions
`1..n`. Or convert to 0-based once when reading (`l -= 1; r -= 1`). Pick one and stick to it; mixing them is the
classic bug. The `n + 1` (or `n + 2`) size is not optional: when `r` is the last position, `r + 1` is one past the
end.

**Try it 7: predict D and the final array**

`n = 6`, all zeros, updates (0-based): `(0, 5, 1)`, `(2, 3, 4)`, `(5, 5, -1)`. Write `D` (length 7), then the final
array.

<details><summary>Answer</summary>

Running the updates and the prefix pass prints `D`, then the array:

```text
[1, 0, 4, 0, -4, -1, 0]
[1, 1, 5, 5, 1, 0]
```

`(0, 5, 1)`: `D[0] += 1`, `D[6] -= 1`. `(2, 3, 4)`: `D[2] += 4`, `D[4] -= 4`. `(5, 5, -1)`: `D[5] -= 1`, `D[6] += 1`.
`D[6]` ends at `0`, and it is never read anyway. Running sum: `1, 1, 5, 5, 1, 0`.
</details>

### 2D difference arrays

For "add `v` to every cell of the rectangle `(r1, c1)..(r2, c2)`", mark four corners in a `(R + 1) x (C + 1)` table:

```text
D[r1][c1]         += v        start of the rectangle
D[r1][c2 + 1]     -= v        stop it on the right
D[r2 + 1][c1]     -= v        stop it below
D[r2 + 1][c2 + 1] += v        the two stops overlap here, add back once
```

Then take the 2D prefix sum of `D` (the same four-term formula as section 2). Why it works is the 1D argument twice:
a 2D prefix sum is a prefix sum along each row followed by a prefix sum down each column. The four corners are
"`+v` at `c1`, `-v` at `c2 + 1`" in row `r1`, and the same pattern negated in row `r2 + 1`, which cancels the
effect for rows below `r2`.

```python
R, C = 4, 5
updates = [(0, 0, 1, 2, 3), (1, 1, 3, 3, 1), (2, 4, 3, 4, 7)]   # r1, c1, r2, c2, v
D = [[0] * (C + 1) for _ in range(R + 1)]
for r1, c1, r2, c2, v in updates:
    D[r1][c1] += v
    D[r1][c2 + 1] -= v
    D[r2 + 1][c1] -= v
    D[r2 + 1][c2 + 1] += v

grid = [[0] * C for _ in range(R)]
for i in range(R):
    for j in range(C):
        up = grid[i - 1][j] if i > 0 else 0
        left = grid[i][j - 1] if j > 0 else 0
        diag = grid[i - 1][j - 1] if i > 0 and j > 0 else 0
        grid[i][j] = D[i][j] + up + left - diag
for row in grid:
    print(row)
```
```text
[1, 0, 4, 0, -4, -1, 0]
[1, 1, 5, 5, 1, 0]
[3, 3, 3, 0, 0]
[3, 4, 4, 1, 0]
[0, 1, 1, 1, 7]
[0, 1, 1, 1, 7]
```

Check by eye: the `3` block covers rows `0..1`, columns `0..2`; the `1` block covers rows `1..3`, columns `1..3`
and overlaps it at `(1, 1)` and `(1, 2)`, which show `4`; the `7` block is the right column of rows `2..3`.

Each rectangle update is `O(1)` and the final pass is `O(R * C)`, instead of `O(R * C)` per update.

**Try it 8: which corner did they forget?**

A student's grid comes out right inside the rectangle, but every cell **below and to the right** of the rectangle
shows `-v`. Which of the four lines is missing?

<details><summary>Answer</summary>

The last one, `D[r2 + 1][c2 + 1] += v`. Cells below and to the right of the rectangle receive `+v` (start), `-v`
(stop right) and `-v` (stop below) from the prefix sum, which leaves `-v`. The fourth corner adds `+v` back so the
total is `0` there.
</details>

## 5. Two pointers

"Two pointers" means two indices into the same array (or one into each of two arrays) that move according to a rule,
and **never move backwards**. Because each pointer moves at most `n` times, the whole scan is `O(n)`, even though it
seems to consider pairs. There are three shapes:

1. **Opposite ends**: `i` starts at the left, `j` at the right, and they move towards each other. Used on sorted data,
   for palindromes, for reversing.
2. **Same direction, slow and fast**: `fast` reads every element, `slow` marks where the next kept element is written.
   Used to filter or compact an array in place.
3. **One pointer per array**: merging two sorted lists.

### Opposite ends: a pair with a given sum in a sorted array

*`a` is sorted in non-decreasing order. Find two positions `i < j` with `a[i] + a[j] == target`.*

Brute force checks all `n(n-1)/2` pairs. The two-pointer rule: start with `i = 0` and `j = n - 1`. If
`a[i] + a[j]` is too small, the only way to get a bigger sum is to move `i` right; if it is too big, the only way
down is to move `j` left; if it is equal, stop.

```python
def pair_sum_sorted(a, target, show=False):
    i, j = 0, len(a) - 1
    while i < j:
        s = a[i] + a[j]
        if show:
            move = "found" if s == target else ("i += 1" if s < target else "j -= 1")
            print(f"  i={i} j={j} a[i]={a[i]:>2} a[j]={a[j]:>2} sum={s:>2}  {move}")
        if s == target:
            return i, j
        if s < target:
            i += 1
        else:
            j -= 1
    return None

a = [1, 2, 4, 7, 11, 15]
print(pair_sum_sorted(a, 15, show=True))
print(pair_sum_sorted(a, 26), pair_sum_sorted(a, 100), pair_sum_sorted([3, 3], 6), pair_sum_sorted([5], 10))
```
```text
  i=0 j=5 a[i]= 1 a[j]=15 sum=16  j -= 1
  i=0 j=4 a[i]= 1 a[j]=11 sum=12  i += 1
  i=1 j=4 a[i]= 2 a[j]=11 sum=13  i += 1
  i=2 j=4 a[i]= 4 a[j]=11 sum=15  found
(2, 4)
(4, 5) None (0, 1) None
```

Hand check the trace: `1 + 15 = 16 > 15`, so `j` moves to `11`. `1 + 11 = 12 < 15`, so `i` moves to `2`.
`2 + 11 = 13 < 15`, `i` moves to `4`. `4 + 11 = 15`: found at `(2, 4)`. Four steps instead of fifteen pairs.

When there are several valid pairs, this rule returns **one particular** pair (the first one it meets), not
necessarily the pair with the smallest `i` among all pairs. Problems that print "the pair" must say which one they
mean; in this module the problems say "the pair found by the standard two-pointer rule", which is exactly the code
above.

### Why it never skips the answer

This is the part to understand, not memorise. Suppose a valid pair `(p, q)` with `p < q` exists. We show the
pointers can never jump past it.

At every step, `i <= p` and `j >= q` hold (the answer is still "inside" the window `i..j`). At the start this is
true. Now suppose it is true and we are about to move a pointer.

- If `i == p` and `j > q`: the sum is `a[p] + a[j] >= a[p] + a[q] = target` because `a[j] >= a[q]` (sorted). So the
  sum is not less than the target, the rule never moves `i`, and `i` stays at `p`. Either the sum equals the target
  (found, maybe a different pair, which is fine) or `j` moves left, still `>= q`.
- If `j == q` and `i < p`: by the mirror argument the sum is `<= target`, so `j` is never moved; `i` moves right, still
  `<= p`.
- If `i < p` and `j > q`: whichever pointer moves, it moves by one, so it cannot pass `p` or `q` in this step.

So the window keeps containing `(p, q)`, and it shrinks by one each step. It cannot shrink forever, so the loop
stops with "found" at the latest when `i == p` and `j == q`.

Another way to say it: each move **eliminates** a whole row or column of the pair table. When `a[i] + a[j] < target`,
`a[i]` plus **any** remaining partner `a[i+1..j]` is at most `a[i] + a[j]`, still too small. So `a[i]` cannot be in
any answer, and we discard it. That is why one step can safely throw away up to `n` pairs at once.

The argument uses "sorted" at every step. On unsorted data the rule is simply wrong. For unsorted data, use a
dictionary of values seen so far (dsa.04, hashing), or sort first and remember the original positions.

**Try it 9: trace the pointers**

`a = [-3, -1, 0, 2, 4, 6]`, `target = 3`. List each `(i, j, sum, move)` until the rule stops. Then do the same for
`target = 20`.

<details><summary>Answer</summary>

Each line is `i j sum move`, with `--` between the two targets:

```text
0 5 3 found
--
0 5 3 i += 1
1 5 5 i += 1
2 5 6 i += 1
3 5 8 i += 1
4 5 10 i += 1
no pair
```

For `target = 3`: `-3 + 6 = 3` is found at once. For `20`, every sum is too small, so `i` walks right until it meets
`j`: five steps, then "no pair". The loop condition `i < j` (not `i <= j`) stops us from pairing an element with itself.
</details>

### Reversing and palindromes

Reversing in place is the simplest opposite-ends loop: swap `a[i]` and `a[j]`, then `i += 1` and `j -= 1`, while
`i < j`. With odd length the middle element meets itself and stays; with even length the pointers cross. Python's
`a.reverse()` does the same job; the point of the loop is the shape, which you will reuse for palindromes.

A palindrome check that **ignores** non-alphanumeric characters and case adds one idea: each pointer **skips** the
characters that do not count before comparing. Skipping is done with inner `while` loops that also keep `i < j`:

```python
def is_palindrome(s):
    i, j = 0, len(s) - 1
    while i < j:
        while i < j and not s[i].isalnum():
            i += 1
        while i < j and not s[j].isalnum():
            j -= 1
        if s[i].lower() != s[j].lower():
            return False
        i += 1
        j -= 1
    return True

for s in ["A man, a plan, a canal: Panama", "race a car", " ", ".,", "0P", "No 'x' in Nixon"]:
    print(repr(s), is_palindrome(s))
```
```text
0 5 3 found
--
0 5 3 i += 1
1 5 5 i += 1
2 5 6 i += 1
3 5 8 i += 1
4 5 10 i += 1
no pair
'A man, a plan, a canal: Panama' True
'race a car' False
' ' True
'.,' True
'0P' False
"No 'x' in Nixon" True
```

`"0P"` is a trap for people who compare `s[i].lower()` with `s[j].lower()` after checking only `isalpha`: digits
count as alphanumeric. A string with **no** letters or digits at all (`" "`, `".,"`) is a palindrome: the empty
string reads the same both ways. Forgetting `i < j` in the skipping loops sends a pointer off the end of the string.

### Slow and fast pointers: compacting in place

*Remove duplicates from a **sorted** array in place. Return `k`, the number of distinct values, with them in
`a[0..k-1]`.*

`fast` reads every element. `slow` is the length of the "kept" part. Because the array is sorted, a value is new
exactly when it differs from the last kept value `a[slow - 1]`:

```python
def dedupe_sorted(a):
    if not a:
        return 0
    slow = 1
    for fast in range(1, len(a)):
        if a[fast] != a[slow - 1]:
            a[slow] = a[fast]
            slow += 1
    return slow

for a in [[1, 1, 2], [0, 0, 1, 1, 1, 2, 2, 3, 3, 4], [5], [], [2, 2, 2]]:
    k = dedupe_sorted(a)
    print(k, a[:k], "  whole list now:", a)
```
```text
2 [1, 2]   whole list now: [1, 2, 2]
5 [0, 1, 2, 3, 4]   whole list now: [0, 1, 2, 3, 4, 2, 2, 3, 3, 4]
1 [5]   whole list now: [5]
0 []   whole list now: []
1 [2]   whole list now: [2, 2, 2]
```

The elements after position `k - 1` are leftovers; the problem only promises the first `k`. The invariant, true
after each step: `a[0..slow-1]` holds the distinct values among `a[0..fast]`, in order. `fast` only moves forward and
`slow <= fast`, so writing `a[slow]` never destroys a value we still need to read.

The same shape solves "move all zeros to the end, keep the order of the others": copy every non-zero to `a[slow]`,
then fill `a[slow:]` with zeros. `[0, 1, 0, 3, 12]` becomes `[1, 3, 12, 0, 0]`.

### Merging two sorted lists

*Given sorted lists `a` and `b`, produce one sorted list.* One pointer per list; at each step take the smaller front
element. When one list runs out, copy the rest of the other.

```python
def merge(a, b):
    i = j = 0
    out = []
    while i < len(a) and j < len(b):
        if a[i] <= b[j]:          # <= keeps equal elements from a first (stable)
            out.append(a[i])
            i += 1
        else:
            out.append(b[j])
            j += 1
    out.extend(a[i:])             # at most one of these two adds anything
    out.extend(b[j:])
    return out

print(merge([1, 3, 5, 7], [2, 3, 6]))
print(merge([], [1, 2]))
print(merge([4, 4], [4]))
print(merge([10, 20], [1, 2, 3]))
```
```text
[1, 2, 3, 3, 5, 6, 7]
[1, 2]
[4, 4, 4]
[1, 2, 3, 10, 20]
```

Each step appends one element and moves one pointer, so the cost is `O(len(a) + len(b))`. Calling `sorted(a + b)`
works too but is `O((n + m) log(n + m))` and ignores the fact that the inputs are already sorted. The most common
bug is forgetting the two `extend` lines, which loses the tail of the longer list (`[10, 20]` above would vanish).

### Three numbers that sum to zero

*Find all **unique** triplets `[x, y, z]` from the array with `x + y + z == 0`.*

Brute force is `O(n^3)`. The two-pointer version:

1. Sort the array.
2. Fix the first element `a[i]`. The other two must sum to `-a[i]`: that is pair-sum on the sorted part
   `a[i+1..n-1]`, done with two pointers `l` and `r` in `O(n)`.
3. Total `O(n^2)`.

The hard part is **uniqueness**. With `[-1, -1, 0, 1]` the triplet `[-1, 0, 1]` can be built from either `-1`. Two
skipping rules remove duplicates without a set:

- **Skip equal first elements**: if `i > 0` and `a[i] == a[i - 1]`, every triplet starting with this value was
  already found, so `continue`.
- **After finding a triplet**, move `l` past all copies of `a[l]` and `r` past all copies of `a[r]`. Otherwise the
  next step finds the same values again.

```python
def three_sum(nums, show=False):
    a = sorted(nums)
    n = len(a)
    out = []
    for i in range(n - 2):
        if i > 0 and a[i] == a[i - 1]:
            if show:
                print(f"i={i} a[i]={a[i]}: same as previous first element, skip")
            continue
        l, r = i + 1, n - 1
        while l < r:
            s = a[i] + a[l] + a[r]
            if s < 0:
                action = "l += 1"
            elif s > 0:
                action = "r -= 1"
            else:
                action = "record, skip duplicates"
            if show:
                print(f"i={i} l={l} r={r} sum={s:>2}  {action}")
            if s < 0:
                l += 1
            elif s > 0:
                r -= 1
            else:
                out.append([a[i], a[l], a[r]])
                while l < r and a[l] == a[l + 1]:
                    l += 1
                while l < r and a[r] == a[r - 1]:
                    r -= 1
                l += 1
                r -= 1
    return out

print(sorted([-1, 0, 1, 2, -1, -4]))
print(three_sum([-1, 0, 1, 2, -1, -4], show=True))
```
```text
[-4, -1, -1, 0, 1, 2]
i=0 l=1 r=5 sum=-3  l += 1
i=0 l=2 r=5 sum=-3  l += 1
i=0 l=3 r=5 sum=-2  l += 1
i=0 l=4 r=5 sum=-1  l += 1
i=1 l=2 r=5 sum= 0  record, skip duplicates
i=1 l=3 r=4 sum= 0  record, skip duplicates
i=2 a[i]=-1: same as previous first element, skip
i=3 l=4 r=5 sum= 3  r -= 1
[[-1, -1, 2], [-1, 0, 1]]
```

Hand-check the trace. Sorted: `[-4, -1, -1, 0, 1, 2]`. With `i = 0` (`-4`), the best possible sum is
`-4 + 1 + 2 = -1 < 0`, so `l` walks right until it meets `r`. With `i = 1` (`-1`): `-1 + -1 + 2 = 0` is recorded
(`[-1, -1, 2]`); no duplicates beside `l = 2` or `r = 5`, so both move once to `l = 3, r = 4`: `-1 + 0 + 1 = 0` is
recorded. `i = 2` has the same value `-1` as `i = 1` and is skipped: without that rule we would record `[-1, 0, 1]` a
second time. `i = 3` (`0`): `0 + 1 + 2 = 3 > 0`, `r` moves, the pointers meet.

Two small speed-ups that are safe because the array is sorted: if `a[i] > 0`, stop (three positives cannot sum to
`0`); the outer loop only needs `i <= n - 3`.

**Try it 10: duplicates**

What does `three_sum([0, 0, 0, 0])` return? And `three_sum([-2, 0, 0, 2, 2])`? Predict first, using the two
skipping rules.

<details><summary>Answer</summary>

Running the `three_sum` above (without the trace) prints:

```text
[[0, 0, 0]]
[[-2, 0, 2]]
```

`[0, 0, 0]` is recorded once at `i = 0`; then `l` skips over the zeros and the pointers cross; `i = 1` is skipped as a
duplicate first element. For `[-2, 0, 0, 2, 2]`, `[-2, 0, 2]` is recorded once: after recording, `l` skips the second
`0`, `r` skips the second `2`, and the pointers cross.
</details>

### Dutch national flag: three groups in one pass

*The array holds only `0`, `1` and `2`. Sort it in place in one pass, without counting.*

Keep three pointers and an **invariant** (a fact that is true before every step):

```text
a[0 .. low-1]     are all 0
a[low .. mid-1]   are all 1
a[mid .. high]    not looked at yet
a[high+1 .. n-1]  are all 2
```

Look at `a[mid]`:

- `0`: swap it with `a[low]` (which is a `1`, or `mid == low`), then `low += 1`, `mid += 1`.
- `1`: already in the right zone, `mid += 1`.
- `2`: swap it with `a[high]`, then `high -= 1`. **Do not move `mid`**: the value that came from `high` has not been
  looked at yet.

The loop runs while `mid <= high` (unknown zone not empty).

```python
def dutch_flag(a, show=False):
    low, mid, high = 0, 0, len(a) - 1
    while mid <= high:
        x = a[mid]
        if x == 0:
            a[low], a[mid] = a[mid], a[low]
            low += 1
            mid += 1
        elif x == 1:
            mid += 1
        else:
            a[mid], a[high] = a[high], a[mid]
            high -= 1
        if show:
            print(f"saw {x}: {a}  low={low} mid={mid} high={high}")
    return a

dutch_flag([2, 0, 2, 1, 1, 0], show=True)
print(dutch_flag([2, 2, 0]), dutch_flag([1]), dutch_flag([]))
```
```text
[[0, 0, 0]]
[[-2, 0, 2]]
saw 2: [0, 0, 2, 1, 1, 2]  low=0 mid=0 high=4
saw 0: [0, 0, 2, 1, 1, 2]  low=1 mid=1 high=4
saw 0: [0, 0, 2, 1, 1, 2]  low=2 mid=2 high=4
saw 2: [0, 0, 1, 1, 2, 2]  low=2 mid=2 high=3
saw 1: [0, 0, 1, 1, 2, 2]  low=2 mid=3 high=3
saw 1: [0, 0, 1, 1, 2, 2]  low=2 mid=4 high=3
[0, 2, 2] [1] []
```

Hand-check the first three steps. Start `[2, 0, 2, 1, 1, 0]`, `low = mid = 0`, `high = 5`. `a[0] = 2`: swap with
`a[5] = 0`, giving `[0, 0, 2, 1, 1, 2]`, `high = 4`, `mid` stays `0`. Now `a[0] = 0`: swap with itself,
`low = mid = 1`. `a[1] = 0`: same, `low = mid = 2`. `a[2] = 2`: swap with `a[4] = 1`, `high = 3`. And so on.

Why not advance `mid` after swapping a `2`? Look at the first step: the `0` that arrived from the end would be
skipped, and a `0` would be left in the middle. And why *is* it safe to advance `mid` after swapping a `0`? Because
the value that comes back from `low` is a `1` that `mid` has already passed (or `low == mid` and it is the same cell),
so there is nothing new to look at.

**Try it 11: predict the steps**

Run `dutch_flag([1, 2, 0], show=True)` in your head. How many steps does it take, and which step changes nothing?

<details><summary>Answer</summary>

```text
saw 1: [1, 2, 0]  low=0 mid=1 high=2
saw 2: [1, 0, 2]  low=0 mid=1 high=1
saw 0: [0, 1, 2]  low=1 mid=2 high=1
```

Step 1 sees `1` and only moves `mid` (the array does not change). Step 2 sees `2` and swaps it with `a[2] = 0`; `mid`
stays at `1`. Step 3 looks at that `0`, swaps it with `a[low] = a[0] = 1`. Now `mid = 2 > high = 1`: done in 3 steps.
</details>

### Container with most water

*Heights `h[0..n-1]` are vertical lines. Choose two lines `i < j`; together with the x-axis they hold
`min(h[i], h[j]) * (j - i)` water. Find the maximum.*

Start with the widest container (`i = 0`, `j = n - 1`). To find something better, the width will shrink, so the
height must grow. Which pointer should move? **The shorter one.** Here is why: suppose `h[i] <= h[j]`. Every
container that uses line `i` with some `j' < j` has width smaller than `j - i` and height at most `h[i]` (the
minimum cannot exceed `h[i]`). So all those containers are **no better** than the current one. Line `i` has given its
best; discard it with `i += 1`. Moving the taller line instead could skip the optimum.

```python
def max_area(h):
    i, j = 0, len(h) - 1
    best = 0
    while i < j:
        best = max(best, min(h[i], h[j]) * (j - i))
        if h[i] <= h[j]:
            i += 1
        else:
            j -= 1
    return best

for h in [[1, 8, 6, 2, 5, 4, 8, 3, 7], [1, 1], [4, 3, 2, 1, 4], [1, 2, 1], [2, 3, 10, 5, 7, 8, 9]]:
    print(h, max_area(h))
```
```text
saw 1: [1, 2, 0]  low=0 mid=1 high=2
saw 2: [1, 0, 2]  low=0 mid=1 high=1
saw 0: [0, 1, 2]  low=1 mid=2 high=1
[1, 8, 6, 2, 5, 4, 8, 3, 7] 49
[1, 1] 1
[4, 3, 2, 1, 4] 16
[1, 2, 1] 2
[2, 3, 10, 5, 7, 8, 9] 36
```

It is the same "eliminate a whole row of the pair table" argument as for pair-sum. The tie `h[i] == h[j]` can move
either pointer: both lines have given their best with the current partner.

### Trapping rain water

*Bars of heights `h[0..n-1]`, width 1 each. How much rain water is held between them?*

Think about one position `i`. Water above it rises to the level of the **lower** of the two highest walls around it:
the highest bar on its left (including itself) and the highest bar on its right (including itself). So

```text
water[i] = min(left_max[i], right_max[i]) - h[i]
```

That formula alone gives an `O(n)` solution with two extra arrays: a prefix maximum from the left and a suffix
maximum from the right, exactly the prefix idea with `max` instead of `+`.

For `h = [0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1]` the three arrays are (computed by two loops, one from each end):

```text
h          0  1  0  2  1  0  1  3  2  1  2  1
left_max   0  1  1  2  2  2  2  3  3  3  3  3
right_max  3  3  3  3  3  3  3  3  2  2  2  1
water      0  0  1  0  1  2  1  0  0  1  0  0      total 6
```

Check `i = 5` (height `0`): the highest bar to its left is `2`, to its right `3`; water `min(2, 3) - 0 = 2`.

The two-pointer version drops the arrays. Keep `left_max` and `right_max` as running values while `i` moves right and
`j` moves left. If `left_max <= right_max`, then for position `i` the true right maximum is **at least** `right_max`
(there may be even taller bars further in), so the minimum of the two sides is exactly `left_max`, already known. So
we can settle position `i` now. The mirror case settles `j`.

```python
def trap(h):
    i, j = 0, len(h) - 1
    left_max = right_max = 0
    total = 0
    while i <= j:
        if left_max <= right_max:
            left_max = max(left_max, h[i])
            total += left_max - h[i]
            i += 1
        else:
            right_max = max(right_max, h[j])
            total += right_max - h[j]
            j -= 1
    return total

for h in [[0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1], [4, 2, 0, 3, 2, 5], [3, 2, 1], [], [5], [2, 0, 2]]:
    print(h, trap(h))
```
```text
[0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1] 6
[4, 2, 0, 3, 2, 5] 9
[3, 2, 1] 0
[] 0
[5] 0
[2, 0, 2] 2
```

A strictly falling or strictly rising array holds no water: there is no wall on one side. The trap here is
`max(h[:i])` inside a loop, which recomputes the maximum every time: `O(n^2)` again.

**Try it 12: which two-pointer shape?**

Name the shape (opposite ends, slow/fast, or one pointer per array) for each task:
(a) Is `"Was it a car or a cat I saw"` a palindrome ignoring spaces and case?
(b) Remove every negative number from a list in place, keeping order.
(c) Given two sorted lists of student ids, print the ids that appear in both.
(d) In a sorted array, count pairs with sum less than `t`.

<details><summary>Answer</summary>

(a) Opposite ends, with skipping. (b) Slow/fast: copy each non-negative to `a[slow]`. (c) One pointer per list, like
merge: if the fronts are equal, print and advance both; otherwise advance the smaller one. (d) Opposite ends: if
`a[i] + a[j] < t`, then `a[i]` pairs with **every** element in `a[i+1..j]`, so add `j - i` to the count and move `i`
right; otherwise move `j` left. One step counts many pairs at once, the same elimination idea as pair-sum.
</details>

## 6. Sliding window: fixed size

### The idea

*Find the maximum sum of any `k` consecutive elements.*

The brute force sums each of the `n - k + 1` windows from scratch: `O(n * k)`. But two neighbouring windows share
`k - 1` elements. Going from `a[l..l+k-1]` to `a[l+1..l+k]`, one element **leaves** on the left and one **enters** on
the right. So the new sum is the old sum minus the leaving element plus the entering one: `O(1)` per move, `O(n)` in
total.

```python
def max_window_sum(a, k, show=False):
    s = sum(a[:k])              # the first window, computed once
    best = s
    if show:
        print(f"  start  window={a[0:k]} sum={s} best={best}")
    for r in range(k, len(a)):
        add, remove = a[r], a[r - k]   # a[r] enters, a[r - k] leaves
        s += add - remove
        best = max(best, s)
        if show:
            print(f"  r={r}    window={a[r - k + 1:r + 1]} add={add} remove={remove} sum={s} best={best}")
    return best

print(max_window_sum([2, 1, 5, 1, 3, 2], 3, show=True))
print(max_window_sum([-1, -2, -3], 2))
print(max_window_sum([4], 1))
```
```text
  start  window=[2, 1, 5] sum=8 best=8
  r=3    window=[1, 5, 1] add=1 remove=2 sum=7 best=8
  r=4    window=[5, 1, 3] add=3 remove=1 sum=9 best=9
  r=5    window=[1, 3, 2] add=2 remove=5 sum=6 best=9
9
-3
4
```

(The slices in the `print` lines are only for display; the algorithm itself never slices after the first window.)
Check each step by hand: `8 + 1 - 2 = 7`, `7 + 3 - 1 = 9`, `9 + 2 - 5 = 6`. The best window is `[5, 1, 3]`.

Notice `best` starts as the first window's sum, not `0`: with all negative numbers (second call) the answer is
negative. Starting from `0` would print a sum that no window has.

The index arithmetic is the only hard part. When the new element is `a[r]`, the window is `a[r-k+1..r]`, and the
element that just left is `a[r - k]`. Check with the first move: `r = k`, the leaving element is `a[0]`. If `k > n`
there is no window at all; decide what the problem wants for that case before writing the loop.

### Counting windows that pass a test

*Count windows of size `k` whose average is at least `t`.* Average `>= t` means `sum / k >= t`. Comparing floats
invites rounding trouble, and the multiplication form is exact for integers:

```text
sum / k >= t     <=>     sum >= t * k          (k > 0)
```

```python
def windows_avg_at_least(a, k, t):
    s = sum(a[:k])
    count = 1 if s >= t * k else 0
    for r in range(k, len(a)):
        s += a[r] - a[r - k]
        if s >= t * k:
            count += 1
    return count

print(windows_avg_at_least([2, 2, 2, 2, 5, 5, 5, 8], 3, 4))
print(windows_avg_at_least([1, 1, 1], 3, 1))
```
```text
3
1
```

The first window must be tested **before** the loop. Forgetting it is the classic fixed-window off-by-one: you check
`n - k` windows instead of `n - k + 1`.

### Windows that hold counts: anagrams

*Count the windows of `text` that are anagrams of `pattern`* (the same letters with the same multiplicities, in
any order). The window size is fixed at `len(pattern)`. We need more than a sum: we need **how many of each
character** the window holds, so the window state is a dictionary of counts.

Sliding means: increase the count of the entering character, decrease the count of the leaving one. One rule
matters a lot: **when a count drops to zero, delete the key.** Otherwise the dictionaries `{"a": 1, "b": 0}` and
`{"a": 1}` describe the same window but compare as different.

```python
def count_anagram_windows(text, pattern):
    k = len(pattern)
    if k > len(text):
        return 0
    need = {}
    for ch in pattern:
        need[ch] = need.get(ch, 0) + 1
    win = {}
    for ch in text[:k]:
        win[ch] = win.get(ch, 0) + 1
    count = 1 if win == need else 0
    for r in range(k, len(text)):
        add, remove = text[r], text[r - k]
        win[add] = win.get(add, 0) + 1
        win[remove] -= 1
        if win[remove] == 0:
            del win[remove]
        if win == need:
            count += 1
    return count

print(count_anagram_windows("cbaebabacd", "abc"))
print(count_anagram_windows("abab", "ab"))
print(count_anagram_windows("aaaa", "aa"))
print(count_anagram_windows("ab", "abc"))
```
```text
2
3
3
0
```

In `"cbaebabacd"` the anagram windows start at `0` (`"cba"`) and `6` (`"bac"`). In `"abab"` with `"ab"`, all three
windows `"ab"`, `"ba"`, `"ab"` count.

Comparing two dictionaries costs `O(number of keys)`, at most the alphabet size (26 for lowercase letters), so the
whole scan is `O(26 n)`, which is `O(n)`. A faster variant keeps a single number `matches` (how many letters have
exactly the needed count) and updates it in `O(1)` per move; it is worth knowing but not needed here. `collections.Counter`
works the same way, and since Python 3.10, `Counter` equality also ignores zero counts. With a plain `dict`, you must
delete them yourself.

**Try it 13: the zero-count bug**

```python
win = {"a": 1, "b": 1}
need = {"a": 1, "c": 1}
win["b"] -= 1
win["c"] = win.get("c", 0) + 1
print(win == need, win)
if win["b"] == 0:
    del win["b"]
print(win == need, win)
```

<details><summary>Answer</summary>

```text
False {'a': 1, 'b': 0, 'c': 1}
True {'a': 1, 'c': 1}
```

The window now holds exactly one `a` and one `c`, the same as `need`, but the leftover key `"b": 0` makes the first
comparison `False`. After deleting it, they compare equal. An anagram counter that forgets the `del` simply never
counts any window after the first time a letter leaves.
</details>

### Circular windows

*A circular array of `0`s and `1`s: what is the minimum number of swaps to bring all the `1`s together?*

If there are `m` ones in total, they must end up in some block of `m` consecutive positions (going around the end
is allowed). A block that already contains `c` ones needs exactly `m - c` swaps (each swap brings one `1` in and one
`0` out). So we want the window of size `m` with the **most** ones: a fixed window again. The circular part: let
the right end run from `0` to `n + m - 2` and read `a[r % n]`, so windows that wrap around are included.

```python
def min_swaps_circular(a):
    n = len(a)
    m = sum(a)
    if m == 0 or m == n:
        return 0
    ones = sum(a[:m])
    best = ones
    for r in range(m, n + m - 1):
        ones += a[r % n] - a[(r - m) % n]
        best = max(best, ones)
    return m - best

print(min_swaps_circular([0, 1, 0, 1, 1, 0, 0]))
print(min_swaps_circular([1, 0, 0, 1, 0, 1]))     # 1s at both ends wrap together
print(min_swaps_circular([1, 1, 0, 0, 1]))
print(min_swaps_circular([0, 0, 0]))
```
```text
1
1
0
0
```

In `[1, 1, 0, 0, 1]` the three ones are already together if you go around the end (positions `4, 0, 1`), so the
answer is `0`. A non-circular window would say `1`.

### Taking cards from both ends

*From a row of cards, take exactly `k` cards, each time from the left end or the right end. Maximise the total.*

It looks like a choice at every step. Turn it around: whatever you take, the cards you **leave** are a contiguous
block of `n - k` cards in the middle. Maximising what you take is the same as minimising the block you leave. So:
answer = `total - (minimum sum of a window of size n - k)`.

```python
def max_cards(cards, k):
    n = len(cards)
    w = n - k
    total = sum(cards)
    if w == 0:
        return total
    s = sum(cards[:w])
    low = s
    for r in range(w, n):
        s += cards[r] - cards[r - w]
        low = min(low, s)
    return total - low

print(max_cards([1, 2, 3, 4, 5, 6, 1], 3))
print(max_cards([2, 2, 2], 2))
print(max_cards([9, 7, 7, 9, 7, 7, 9], 7))
print(max_cards([1, 1000, 1], 1))
```
```text
12
4
55
1
```

For the first case, leave the window `[1, 2, 3, 4]` (sum `10`) and take `5 + 6 + 1 = 12` from the right. This
"look at the complement" trick turns many end-choosing problems into a plain window.

## 7. Sliding window: variable size

### When the window size is not given

Many problems ask for the **longest** or **shortest** contiguous block with some property: "the longest substring
without repeated characters", "the shortest subarray with sum at least `s`". The window grows and shrinks. The two
ends `l` and `r` both only move right, so the total work is `O(n)`: `r` moves `n` times, `l` moves at most `n` times.

The template:

```text
l = 0
for r in range(n):
    add a[r] to the window state
    while the window is invalid:        # WHILE, not if
        remove a[l] from the state
        l += 1
    the window a[l..r] is valid: update the answer with r - l + 1
```

When does this work? When the property is **monotone**: if a window is valid, every smaller window inside it is valid
too (for "longest" problems), or every bigger window containing it stays valid (for "shortest" problems). Then
moving `l` right can only help an invalid window become valid, and we never need to move `l` back. Section 7 ends
with the case where this fails: negative numbers in sum problems.

### Longest substring without repeating characters

The window is valid when no character appears twice. Adding `s[r]` may create one repeat; we shrink from the left
until that character's count is back to `1`.

```python
def longest_unique(s, show=False):
    count = {}
    l = 0
    best = 0
    for r, ch in enumerate(s):
        count[ch] = count.get(ch, 0) + 1
        while count[ch] > 1:
            count[s[l]] -= 1
            l += 1
        best = max(best, r - l + 1)
        if show:
            print(f"r={r} add {ch!r}  l={l}  window={s[l:r + 1]!r:<8} best={best}")
    return best

print(longest_unique("abcabcbb", show=True))
```
```text
r=0 add 'a'  l=0  window='a'      best=1
r=1 add 'b'  l=0  window='ab'     best=2
r=2 add 'c'  l=0  window='abc'    best=3
r=3 add 'a'  l=1  window='bca'    best=3
r=4 add 'b'  l=2  window='cab'    best=3
r=5 add 'c'  l=3  window='abc'    best=3
r=6 add 'b'  l=5  window='cb'     best=3
r=7 add 'b'  l=7  window='b'      best=3
3
```

Hand-check one shrink. At `r = 3` the window was `"abc"` and we add `"a"`: the count of `a` is `2`. We remove `s[0] = "a"`,
`l` becomes `1`, the count is `1`, the loop stops: the window is `"bca"`, length 3. At `r = 6` we add `"b"` to `"abc"`
(`l = 3`): we remove `a` (`l = 4`), then `b` (`l = 5`), and the window is `"cb"`. At `r = 7` we add another `b` and the
window shrinks to just `"b"`. The answer is `3`.

Here **`while` is essential**. At `r = 6` the shrink needed two steps; with `if`, `l` would move once and the window
`"bcb"` (with a repeat) would be measured as valid.

```python
for s in ["bbbbb", "pwwkew", "", "a", "abba", "dvdf"]:
    print(repr(s), longest_unique(s))
```
```text
'bbbbb' 1
'pwwkew' 3
'' 0
'a' 1
'abba' 2
'dvdf' 3
```

A faster-to-write variant stores the **last index** of each character and jumps `l` directly past it:
`l = max(l, last[ch] + 1)`. The `max` matters: in `"abba"`, when the second `a` arrives, the last `a` is at index `0`,
but `l` is already `2`; without `max`, `l` would jump **back** to `1`.

**Try it 14: trace the variable window**

Trace `longest_unique("abba", show=True)`: for each `r`, give `l`, the window, and `best`.

<details><summary>Answer</summary>

```text
r=0 add 'a'  l=0  window='a'      best=1
r=1 add 'b'  l=0  window='ab'     best=2
r=2 add 'b'  l=2  window='b'      best=2
r=3 add 'a'  l=2  window='ba'     best=2
```

At `r = 2` the second `b` forces two removals (`a`, then `b`), so `l = 2`. At `r = 3` the window `"ba"` has no repeat:
the earlier `a` was already removed (its count went to `0`), so nothing shrinks.
</details>

### Shortest subarray with sum at least s (positive numbers)

For "shortest" problems the roles flip: we **record the answer inside the shrinking loop**, while the window is
still valid, and keep shrinking to see if a shorter one is also valid.

```python
def shortest_sum_at_least(a, s):
    l = 0
    total = 0
    best = len(a) + 1               # "infinity": longer than any real window
    for r, x in enumerate(a):
        total += x
        while total >= s:           # valid: record, then try to shrink
            best = min(best, r - l + 1)
            total -= a[l]
            l += 1
    return best if best <= len(a) else 0

print(shortest_sum_at_least([2, 3, 1, 2, 4, 3], 7))
print(shortest_sum_at_least([1, 4, 4], 4))
print(shortest_sum_at_least([1, 1, 1, 1], 11))
print(shortest_sum_at_least([5, 1, 3, 5, 10, 7, 4, 9, 2, 8], 15))
```
```text
r=0 add 'a'  l=0  window='a'      best=1
r=1 add 'b'  l=0  window='ab'     best=2
r=2 add 'b'  l=2  window='b'      best=2
r=3 add 'a'  l=2  window='ba'     best=2
2
1
0
2
```

This depends on **all numbers being positive**: growing the window always increases the sum and shrinking always
decreases it. Keep that in mind; it breaks below.

### At most k distinct characters (and the three classic bugs)

*Find the longest substring with at most `k` distinct characters.* The state is a dictionary of counts; the number of
distinct characters is `len(count)`, which is only correct if keys with count `0` are **deleted**.

```python
def longest_at_most_k_distinct(s, k):
    count = {}
    l = 0
    best = 0
    for r, ch in enumerate(s):
        count[ch] = count.get(ch, 0) + 1
        while len(count) > k:
            left = s[l]
            count[left] -= 1
            if count[left] == 0:
                del count[left]
            l += 1
        best = max(best, r - l + 1)
    return best

for s, k in [("eceba", 2), ("aa", 1), ("abaccc", 2), ("abcabc", 0), ("aabbccdd", 3)]:
    print(repr(s), k, longest_at_most_k_distinct(s, k))
```
```text
'eceba' 2 3
'aa' 1 2
'abaccc' 2 4
'abcabc' 0 0
'aabbccdd' 3 6
```

Three bugs appear again and again in this code. To see their effect clearly, we use the **counting** version of the
same loop, which you will meet properly a few pages on: after shrinking, the subarrays ending at `r` that satisfy the
rule are the ones starting at `l, l+1, ..., r`, which is `r - l + 1` of them. For `"abaccc"` and `k = 2`, the correct
count of substrings with at most 2 distinct letters is `15`:

```python
def count_at_most(s, k, bug=None):
    count = {}
    l = 0
    total = 0
    for r, ch in enumerate(s):
        count[ch] = count.get(ch, 0) + 1
        if bug == "if":
            if len(count) > k:          # shrinks only one step
                count[s[l]] -= 1
                if count[s[l]] == 0:
                    del count[s[l]]
                l += 1
        else:
            while len(count) > k:
                count[s[l]] -= 1
                if bug != "no-del" and count[s[l]] == 0:
                    del count[s[l]]
                l += 1
                if l > r:
                    break               # stop the runaway loop for the demo
        total += (r - l) if bug == "off-by-one" else (r - l + 1)
    return total

s = "abaccc"
brute = sum(1 for l in range(len(s)) for r in range(l, len(s)) if len(set(s[l:r + 1])) <= 2)
print("correct", count_at_most(s, 2), "brute", brute)
for bug in ["if", "no-del", "off-by-one"]:
    print(bug, count_at_most(s, 2, bug))
```
```text
correct 15 brute 15
if 16
no-del 6
off-by-one 9
```

- **`if` instead of `while`**: one removal may not be enough. At `r = 3` (`"abac"`), removing one `a` leaves
  `"bac"`, which still has three letters, yet its 3 starts are counted. The total is too big.
- **Not deleting zero counts**: `len(count)` never goes down, so once a third letter appears, the window shrinks to
  nothing (we added a `break` so the demo stops). The total is too small.
- **`r - l` instead of `r - l + 1`**: the window `a[l..r]` has `r - l + 1` elements. Check with `l == r`: one element.

A curious fact about the `if` bug: in the "longest" version of the problem it still prints the **right length**.
With `if`, the window never gets shorter (when it is invalid, `l` and `r` both move by one, so it slides at
constant length), and it only grows when the grown window is valid. So the maximum length is correct, but the
window itself may be invalid, and anything else you compute from it (a count, the substring, its position) is wrong.
For example, on `"aabcd"` with `k = 2` the `if` version still reports length `3` (the true answer is `"aab"`), but
at the end its window is `"bcd"`, with three distinct letters.

Write `while`. It is always correct, and it costs nothing extra: `l` still moves at most `n` times in total.

### Longest run of ones with at most k flips

*In an array of `0`s and `1`s you may flip at most `k` zeros to ones. What is the longest run of ones you can get?*
Rephrase: the longest window that contains **at most `k` zeros**. Same template, and the state is just a counter.

```python
def longest_ones(a, k):
    zeros = 0
    l = 0
    best = 0
    for r, x in enumerate(a):
        if x == 0:
            zeros += 1
        while zeros > k:
            if a[l] == 0:
                zeros -= 1
            l += 1
        best = max(best, r - l + 1)
    return best

print(longest_ones([1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 0], 2))
print(longest_ones([0, 0, 1, 1, 0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0, 1, 1, 1, 1], 3))
print(longest_ones([0, 0, 0], 0))
print(longest_ones([0, 0, 0], 5))
```
```text
6
10
0
3
```

The rephrasing step is the real skill. "Flip at most `k`" sounds like a choice of which zeros to flip; "a window with at
most `k` zeros" is a condition you can check by counting.

### Exactly k: the at-most trick

*Count the subarrays with **exactly** `k` distinct values.* "Exactly" is **not** monotone: a window with exactly `k`
distinct values can grow into one with `k + 1`, and shrink into one with `k - 1`. The template does not apply directly.

"At most `k`" **is** monotone. And

```text
exactly(k) = atMost(k) - atMost(k - 1)
```

because the subarrays with at most `k` distinct values are those with exactly `k` plus those with at most `k - 1`.

How do we **count** (not measure) the subarrays with at most `k` distinct values? For each `r`, after shrinking, every
start from `l` to `r` gives a valid subarray ending at `r` (shorter windows inside a valid one are valid). That is
`r - l + 1` subarrays. Add them up:

```python
def at_most(a, k):
    if k < 0:
        return 0
    count = {}
    l = 0
    total = 0
    for r, x in enumerate(a):
        count[x] = count.get(x, 0) + 1
        while len(count) > k:
            count[a[l]] -= 1
            if count[a[l]] == 0:
                del count[a[l]]
            l += 1
        total += r - l + 1
    return total

def exactly(a, k):
    return at_most(a, k) - at_most(a, k - 1)

def brute(a, k):
    n = len(a)
    return sum(1 for l in range(n) for r in range(l, n) if len(set(a[l:r + 1])) == k)

for a, k in [([1, 2, 1, 2, 3], 2), ([1, 2, 1, 3, 4], 3), ([1, 1, 1], 1), ([1, 2], 3)]:
    print(a, k, at_most(a, k), at_most(a, k - 1), exactly(a, k), brute(a, k))
```
```text
[1, 2, 1, 2, 3] 2 12 5 7 7
[1, 2, 1, 3, 4] 3 13 10 3 3
[1, 1, 1] 1 6 0 6 6
[1, 2] 3 3 3 0 0
```

For `[1, 2, 1, 2, 3]` and `k = 2`: 12 subarrays have at most 2 distinct values, 5 have at most 1 (the single
elements), so `7` have exactly 2. The same trick counts "subarrays with exactly `k` odd numbers", "binary subarrays with
sum exactly `s`" (non-negative values), and more.

### Minimum window substring

*Given strings `s` and `t`, find the shortest substring of `s` that contains every character of `t`, with
multiplicity (if `t` has two `a`s, the window needs two `a`s).*

It is a "shortest" problem, so: grow `r` until the window is valid, then shrink `l` while it stays valid, recording
the answer each time. To test "valid" in `O(1)`, keep a number `missing`: how many characters of `t` (counting
multiplicity) the window still lacks. Adding a character that is still needed decreases `missing`; removing one that
drops below the need increases it.

```python
def min_window(s, t):
    need = {}
    for ch in t:
        need[ch] = need.get(ch, 0) + 1
    missing = len(t)
    have = {}
    l = 0
    best_len, best_l = len(s) + 1, 0
    for r, ch in enumerate(s):
        have[ch] = have.get(ch, 0) + 1
        if have[ch] <= need.get(ch, 0):
            missing -= 1
        while missing == 0:
            if r - l + 1 < best_len:      # strictly shorter: keeps the earliest on ties
                best_len, best_l = r - l + 1, l
            left = s[l]
            have[left] -= 1
            if have[left] < need.get(left, 0):
                missing += 1
            l += 1
    return s[best_l:best_l + best_len] if best_len <= len(s) else ""

print(repr(min_window("ADOBECODEBANC", "ABC")))
print(repr(min_window("a", "a")))
print(repr(min_window("a", "aa")))
print(repr(min_window("aaflslflsldkalskaaa", "aaa")))
print(repr(min_window("abcab", "ab")))
```
```text
'BANC'
'a'
''
'aaa'
'ab'
```

The tie rule comes from `<` (strictly shorter): the first window of the best length is kept, so the answer is the
**earliest** one. With `<=` you would get the **last** one (`"ab"` at index `3` instead of index `0` in the final
example, which looks the same but starts elsewhere). Problems that print positions must pin this rule.

### Why negative numbers break the window

Take "shortest subarray with sum at least `s`" and allow negatives: `a = [2, -1, 2]`, `s = 3`. The only answer is the
whole array (sum `3`). Run the positive-only window code:

```python
# shortest_sum_at_least is the positive-only window code from above
print(shortest_sum_at_least([2, -1, 2], 3))
print(shortest_sum_at_least([84, -37, 32, 40, 95], 167))
```
```text
3
5
```

The first answer happens to be right, but the second is wrong: the correct answer is `3` (`[32, 40, 95]`, sum `167`),
and the window code reports `5`. When it reached the end with the whole array (sum `214`), it shrank by removing `84`, getting
`130 < 167`, and stopped. It never tried removing `-37` as well, which would have **increased** the sum back to `167`.

The window logic relies on two facts that are only true for non-negative numbers:

1. Adding an element never makes the sum smaller (so a too-small window can only be fixed by growing).
2. Removing an element never makes the sum bigger (so once a window is too small, shrinking further cannot help).

With negatives both fail, and the window can stop too early or too late. What to use instead:

- Counting or longest subarrays with sum **exactly** `k`: **prefix sums + dictionary** (section 3).
- Shortest subarray with sum **at least** `k`: **prefix sums + monotonic deque** (section 8).
- Maximum subarray sum: **Kadane** (section 9).

**Try it 15: does the window work here?**

For each task, say whether the plain variable window is correct, and if not, what to use: (a) longest subarray with
sum at most `s`, all values positive; (b) number of subarrays with sum exactly `k`, values may be negative;
(c) longest substring with at most two distinct letters; (d) longest subarray with sum exactly `k`, values positive.

<details><summary>Answer</summary>

(a) Yes: with positive values, "sum `<= s`" is monotone (sub-windows of a valid window are valid). (b) No: use prefix
sums with a counting dictionary. (c) Yes: counts dictionary, shrink while more than two keys. (d) Yes, with positive
values: grow, shrink while the sum is above `k`, check for equality. The prefix-plus-first-index method also works and is
the one to use if zeros or negatives may appear.
</details>

## 8. The monotonic deque

### Maximum of every window

*For each window of size `k`, print its maximum.* A running sum worked because "minus the leaving element" undoes
"plus". There is no "minus" for `max`: when the maximum leaves the window, what is the new maximum? Rescanning the
window costs `O(k)` per step.

Key observation: if `a[j] >= a[i]` and `j > i`, then `a[i]` can **never** again be the maximum of any window that
contains `a[j]`, and every future window that contains `a[i]` also contains `a[j]` (because `a[j]` leaves later). So
`a[i]` is useless from the moment `a[j]` arrives. Throw it away.

What remains, if we always throw away useless elements, is a list of indices whose values are **strictly
decreasing** from front to back. The front is the maximum of the current window. We store it in a
`collections.deque`, which can add and remove at both ends in `O(1)`:

- New index `r`: pop from the **back** every index whose value is `<= a[r]` (they became useless), then append `r`.
- Pop from the **front** if that index has left the window (`front <= r - k`).
- Once the first window is complete (`r >= k - 1`), the front holds the answer.

```python
from collections import deque

def window_max(a, k, show=False):
    dq = deque()            # indices, values strictly decreasing
    out = []
    for r, x in enumerate(a):
        while dq and a[dq[-1]] <= x:
            dq.pop()
        dq.append(r)
        if dq[0] <= r - k:
            dq.popleft()
        if r >= k - 1:
            out.append(a[dq[0]])
        if show:
            print(f"r={r} x={x:>2}  deque idx={list(dq)} values={[a[i] for i in dq]}"
                  + (f"  max={a[dq[0]]}" if r >= k - 1 else ""))
    return out

print(window_max([1, 3, -1, -3, 5, 3, 6, 7], 3, show=True))
```
```text
r=0 x= 1  deque idx=[0] values=[1]
r=1 x= 3  deque idx=[1] values=[3]
r=2 x=-1  deque idx=[1, 2] values=[3, -1]  max=3
r=3 x=-3  deque idx=[1, 2, 3] values=[3, -1, -3]  max=3
r=4 x= 5  deque idx=[4] values=[5]  max=5
r=5 x= 3  deque idx=[4, 5] values=[5, 3]  max=5
r=6 x= 6  deque idx=[6] values=[6]  max=6
r=7 x= 7  deque idx=[7] values=[7]  max=7
[3, 3, 5, 5, 6, 7]
```

Hand-check three steps. At `r = 1` (`3`), the `1` at index `0` is popped from the back because `1 <= 3`. At `r = 3`
(`-3`), nothing is popped (`-1 > -3`), the deque holds values `3, -1, -3`, and the front index `1` is still inside
the window `1..3`, so the maximum is `3`. At `r = 4` (`5`), all three are popped from the back (each `<= 5`); the
deque holds only index `4`. The front check would have removed index `1` anyway, since the window is now `2..4`.

Why `O(n)`? Every index is appended once and popped at most once (from one end or the other). The `while` loop can
run many times in one step, but its **total** over the whole scan is at most `n`. This "amortised" argument is the same
one that makes the variable window `O(n)`.

**Try it 16: sliding minimum**

What must change to get the **minimum** of each window? Predict the output for `[4, 2, 12, 3, 8, 1]` with `k = 2`.

<details><summary>Answer</summary>

Flip the comparison: pop from the back while `a[dq[-1]] >= x`, so the deque is increasing and the front is the minimum.

```text
[2, 2, 3, 3, 1]
```

The windows are `[4, 2]`, `[2, 12]`, `[12, 3]`, `[3, 8]`, `[8, 1]`.
</details>

### Shortest subarray with sum at least k, negatives allowed

We saw the plain window fail on `[84, -37, 32, 40, 95]` with `k = 167`. The fix combines prefix sums and a monotonic
deque. With prefix sums `P`, a subarray `a[i..j-1]` has sum `P[j] - P[i]`. For each end `j`, we want the **largest**
`i < j` with `P[i] <= P[j] - k` (largest `i` = shortest subarray).

Two observations keep the deque small, both about candidate starts `i`:

1. **Front**: if `P[j] - P[dq[0]] >= k`, we have an answer `j - dq[0]`. Any later end `j' > j` using the same start
   gives a longer subarray, so this start will never be better: pop it from the front, and check the next one.
2. **Back**: before adding `j` as a future start, pop every `i` from the back with `P[i] >= P[j]`. A later start with a
   **smaller or equal** prefix sum is better in both ways (shorter and a larger sum), so those `i` are useless.

The deque then holds indices with **increasing** prefix sums.

```python
from collections import deque

def shortest_at_least_k(a, k):
    n = len(a)
    P = [0] * (n + 1)
    for i in range(n):
        P[i + 1] = P[i] + a[i]
    best = n + 1
    dq = deque()
    for j in range(n + 1):
        while dq and P[j] - P[dq[0]] >= k:
            best = min(best, j - dq.popleft())
        while dq and P[dq[-1]] >= P[j]:
            dq.pop()
        dq.append(j)
    return best if best <= n else -1

for a, k in [([84, -37, 32, 40, 95], 167), ([2, -1, 2], 3), ([1, 2], 4), ([1], 1), ([-28, 81, -20, 28, -29], 89)]:
    print(a, k, shortest_at_least_k(a, k))
```
```text
[2, 2, 3, 3, 1]
[84, -37, 32, 40, 95] 167 3
[2, -1, 2] 3 3
[1, 2] 4 -1
[1] 1 1
[-28, 81, -20, 28, -29] 89 3
```

The first case now gives `3`, which the plain window got wrong. Note that this loop runs over the `n + 1` prefix sums, not over the `n` elements, and that `j = 0` (the empty prefix)
goes into the deque first, just as `seen = {0: 1}` did in section 3.

## 9. Kadane's algorithm

### The maximum subarray problem

*Find the largest sum of a non-empty contiguous subarray.* For `[-2, 1, -3, 4, -1, 2, 1, -5, 4]` the answer is `6`,
from `[4, -1, 2, 1]`.

Prefix sums give an `O(n^2)` solution (try every pair), and a sliding window does not apply (the values are negative
as well as positive). Kadane's algorithm does it in one pass with two numbers.

### Why it works: the best subarray ending here

Ask a smaller question for each index `i`: **what is the best sum of a subarray that ends exactly at `i`?** Call it
`cur[i]`. Such a subarray either

- is just `[a[i]]`, or
- is some subarray ending at `i - 1`, extended by `a[i]`. The best of those is `cur[i - 1] + a[i]`.

So `cur[i] = max(a[i], cur[i - 1] + a[i])`. In words: **if the best sum ending just before `i` is negative, throw it
away and start fresh at `i`; otherwise extend it.** A negative prefix can only drag down whatever comes after it.

Every subarray ends somewhere, so the overall answer is the maximum of `cur[i]` over all `i`. We only ever need the
previous `cur`, so two variables are enough:

```python
def kadane(a):
    cur = best = a[0]
    for x in a[1:]:
        cur = max(x, cur + x)
        best = max(best, cur)
    return best

for a in [[-2, 1, -3, 4, -1, 2, 1, -5, 4], [1], [5, 4, -1, 7, 8], [-3, -1, -2], [0, -1, 0]]:
    print(a, kadane(a))
```
```text
[-2, 1, -3, 4, -1, 2, 1, -5, 4] 6
[1] 1
[5, 4, -1, 7, 8] 23
[-3, -1, -2] -1
[0, -1, 0] 0
```

(`a[1:]` makes a copy; that is `O(n)` once, which is fine. You can also loop over `range(1, len(a))`.)

This "best answer **ending at** each position, built from the previous one" is your first taste of dynamic
programming. The whole trick is choosing a question whose answer for `i` depends only on the answer for `i - 1`.

### The all-negative trap

Look at `[-3, -1, -2]`: the answer is `-1`, a single element. A very common version of Kadane starts with
`cur = best = 0` and resets `cur` to `0` when it goes negative:

```python
def kadane_zero(a):
    cur = best = 0
    for x in a:
        cur = max(0, cur + x)
        best = max(best, cur)
    return best

print(kadane_zero([-2, 1, -3, 4, -1, 2, 1, -5, 4]))
print(kadane_zero([-3, -1, -2]))
```
```text
6
0
```

It returns `0` for an all-negative array: the sum of the **empty** subarray. That version is correct only if the
problem allows an empty subarray (some do: "you may choose to buy nothing"). When the statement says "at least one
element" or "non-empty", start from `a[0]` as in `kadane` above. Always test an all-negative input.

### Trace

```python
a = [-2, 1, -3, 4, -1, 2, 1, -5, 4]
cur = best = a[0]
print(f"x={a[0]:>2}  cur={cur:>2}  best={best:>2}  (start)")
for x in a[1:]:
    action = "extend" if cur + x >= x else "restart"
    cur = max(x, cur + x)
    best = max(best, cur)
    print(f"x={x:>2}  cur={cur:>2}  best={best:>2}  {action}")
```
```text
x=-2  cur=-2  best=-2  (start)
x= 1  cur= 1  best= 1  restart
x=-3  cur=-2  best= 1  extend
x= 4  cur= 4  best= 4  restart
x=-1  cur= 3  best= 4  extend
x= 2  cur= 5  best= 5  extend
x= 1  cur= 6  best= 6  extend
x=-5  cur= 1  best= 6  extend
x= 4  cur= 5  best= 6  extend
```

Hand-check: at `x = 1`, the previous `cur = -2` is negative, so restart: `cur = 1`. At `x = -3`: `1 - 3 = -2` beats
`-3`, so extend. At `x = 4`: `-2 + 4 = 2 < 4`, restart. Then `3, 5, 6` by extending, and `best` stops at `6`. At
`x = -5`, `cur` drops to `1` but stays positive, so the last `4` extends it to `5`, not enough to beat `6`.

**Try it 17: trace Kadane**

Trace `[3, -4, 5, -1, 2, -6, 1]`: give `cur` and `best` after each element, and the final answer.

<details><summary>Answer</summary>

Each line is `x cur best`:

```text
3 3 3
-4 -1 3
5 5 5
-1 4 5
2 6 6
-6 0 6
1 1 6
```

The best subarray is `[5, -1, 2]` with sum `6`. At `x = 5` the running `cur = -1` is thrown away (restart); at
`x = 1` the `cur = 0` is not negative, so extending and restarting give the same `1`.
</details>

### Reporting the subarray: indices and tie rules

Problems often want the positions `l` and `r` too. Track where the current run started:

- When we **restart** at `i`, the start becomes `i`.
- When `cur` improves `best`, record `(start, i)`.

The interesting part is **ties**, and a problem that prints positions must say which subarray it wants when several
have the same maximum sum. Two choices decide the answer:

1. **Extend or restart when `cur` is exactly `0`?** Extending keeps the earlier start (a longer subarray with the same
   sum). Restarting gives a later start.
2. **Update `best` on `>` or on `>=`?** `>` keeps the first subarray found (the earliest end); `>=` keeps the last one.

The rule "**restart only when `cur < 0`**, update only when `cur > best`" gives the subarray with the **earliest start,
and among those the shortest** (the earliest end). Here is the code, checked against a brute force that applies that
rule literally:

```python
def kadane_bounds(a):
    cur = best = a[0]
    start = 0
    best_l = best_r = 0
    for i in range(1, len(a)):
        if cur < 0:              # restart only on a strictly negative run
            cur = a[i]
            start = i
        else:
            cur += a[i]
        if cur > best:           # strictly better: keep the first one found
            best = cur
            best_l, best_r = start, i
    return best, best_l + 1, best_r + 1     # 1-based positions

def brute_bounds(a):
    n = len(a)
    found = []
    for l in range(n):
        s = 0
        for r in range(l, n):
            s += a[r]
            found.append((-s, l, r))        # max sum, then smallest l, then smallest r
    s, l, r = min(found)
    return -s, l + 1, r + 1

tests = [[-2, 1, -3, 4, -1, 2, 1, -5, 4], [2, -2, 3], [1, -1, 1], [0, 0, 5], [5, 0, 0], [-1, -1], [3, -3, 3, -3, 3]]
for a in tests:
    print(a, kadane_bounds(a), brute_bounds(a))
```
```text
3 3 3
-4 -1 3
5 5 5
-1 4 5
2 6 6
-6 0 6
1 1 6
[-2, 1, -3, 4, -1, 2, 1, -5, 4] (6, 4, 7) (6, 4, 7)
[2, -2, 3] (3, 1, 3) (3, 1, 3)
[1, -1, 1] (1, 1, 1) (1, 1, 1)
[0, 0, 5] (5, 1, 3) (5, 1, 3)
[5, 0, 0] (5, 1, 1) (5, 1, 1)
[-1, -1] (-1, 1, 1) (-1, 1, 1)
[3, -3, 3, -3, 3] (3, 1, 1) (3, 1, 1)
```

Read the tie cases. `[2, -2, 3]`: both `[2, -2, 3]` (positions 1..3) and `[3]` (3..3) sum to `3`; the earliest start
wins. `[1, -1, 1]`: `[1]` at 1..1 and `[1, -1, 1]` at 1..3 tie; same start, so the shorter wins. `[5, 0, 0]`: the zeros
do not change the sum, and `>` refuses to extend the answer over them.

Now the other rule, "restart when `cur <= 0`, update on `>=`". The function `kadane_bounds_late` is the same code
with only those two comparisons changed (`if cur <= 0:` and `if cur >= best:`):

```python
for a in [[2, -2, 3], [1, -1, 1], [0, 0, 5], [5, 0, 0]]:
    print(a, kadane_bounds_late(a))
```
```text
[2, -2, 3] (3, 3, 3)
[1, -1, 1] (1, 3, 3)
[0, 0, 5] (5, 3, 3)
[5, 0, 0] (5, 1, 3)
```

Same sums, different positions. Neither rule is "right"; the **problem statement** decides. When a problem pins a
tie rule, test your code against a brute force like `brute_bounds` on many small random arrays (with lots of zeros and
small values, where ties are common). That is how the rule above was checked:

```python
import random
# kadane_bounds and brute_bounds as defined above

random.seed(3)
ok = True
for _ in range(3000):
    a = [random.randint(-3, 3) for _ in range(random.randint(1, 8))]
    if kadane_bounds(a) != brute_bounds(a):
        ok = False
        print("differs on", a)
        break
print("all 3000 random tests agree:", ok)
```
```text
all 3000 random tests agree: True
```

### Best time to buy and sell (one transaction)

*Prices `p[0..n-1]`; buy on one day and sell on a later day. Maximum profit, or `0` if no profit is possible.*

For each selling day `j`, the best buying day is the cheapest day **before** it. Keep the running minimum:

```python
def max_profit(p):
    lowest = None
    best = 0
    for price in p:
        if lowest is not None:
            best = max(best, price - lowest)
        if lowest is None or price < lowest:
            lowest = price
    return best

print(max_profit([7, 1, 5, 3, 6, 4]))
print(max_profit([7, 6, 4, 3, 1]))
print(max_profit([2]))
print(max_profit([]))
```
```text
5
0
0
0
```

This is Kadane in disguise: the profit of buying on day `i` and selling on day `j` is the sum of the daily changes
`p[i+1] - p[i], ..., p[j] - p[j-1]`. So the answer is the maximum subarray sum of the **differences**, with the empty
subarray allowed (profit `0`). Order matters inside the loop: compute the profit **before** updating `lowest`, or you
would allow buying and selling on the same day (harmless here, but a real bug in variants).

### Circular arrays

*The array is circular: the last element is followed by the first. Find the maximum subarray sum.*

A circular subarray either does **not** wrap around (a normal subarray: plain Kadane) or **does** wrap, taking a
suffix and a prefix. A wrapping subarray leaves out a block in the middle, so its sum is `total - (that middle
block)`. The best wrapping subarray leaves out the **minimum** subarray. So:

```text
answer = max(max_subarray(a), total - min_subarray(a))
```

with one trap. If every element is negative, the minimum subarray is the whole array and `total - min` is `0`: the
sum of the **empty** subarray, which is not allowed. In that case the answer is plain Kadane (the largest element).

```python
def max_circular(a):
    total = sum(a)
    cur_max = best_max = a[0]
    cur_min = best_min = a[0]
    for x in a[1:]:
        cur_max = max(x, cur_max + x)
        best_max = max(best_max, cur_max)
        cur_min = min(x, cur_min + x)
        best_min = min(best_min, cur_min)
    if best_max < 0:                 # all negative: wrapping would mean "take nothing"
        return best_max
    return max(best_max, total - best_min)

for a in [[1, -2, 3, -2], [5, -3, 5], [-3, -2, -3], [3, -1, 2, -1], [-2, 4, -5, 4, -5, 9, 4]]:
    print(a, max_circular(a))
```
```text
[1, -2, 3, -2] 3
[5, -3, 5] 10
[-3, -2, -3] -2
[3, -1, 2, -1] 4
[-2, 4, -5, 4, -5, 9, 4] 15
```

`[5, -3, 5]` wraps: `5 + 5 = 10`, leaving out the `-3`. `[-3, -2, -3]` hits the trap: without the `best_max < 0` check
the code would return `0`.

### 2D: the maximum sum rectangle

*In an `R x C` grid of integers (some negative), find the sub-rectangle with the largest sum.*

Brute force over all rectangles is `O(R^2 C^2)` rectangles, each summed in `O(1)` with a 2D prefix table: too slow for
`R = C = 100` in Python (about `2.5 * 10^7` rectangles, each with several list lookups). The standard trick reduces 2D to 1D:

1. Fix a **top row** `top` and a **bottom row** `bottom`.
2. Squash the rows `top..bottom` into one array: `col[j]` = sum of column `j` over those rows.
3. A rectangle between these two rows is a contiguous range of columns, and its sum is a subarray sum of `col`.
   Run Kadane on `col`.

When `bottom` moves down by one, `col` gains one row: add `grid[bottom][j]` to each `col[j]`. No recomputation.
Total: `O(R^2)` pairs of rows times `O(C)` for Kadane, so `O(R^2 * C)`: `10^6` steps for a 100 x 100 grid.

```python
def kadane(a):
    cur = best = a[0]
    for x in a[1:]:
        cur = max(x, cur + x)
        best = max(best, cur)
    return best

def max_rectangle(grid):
    R, C = len(grid), len(grid[0])
    best = grid[0][0]
    for top in range(R):
        col = [0] * C
        for bottom in range(top, R):
            for j in range(C):
                col[j] += grid[bottom][j]
            best = max(best, kadane(col))
    return best

g = [
    [1, 2, -1, -4, -20],
    [-8, -3, 4, 2, 1],
    [3, 8, 10, 1, 3],
    [-4, -1, 1, 7, -6],
]
print(max_rectangle(g))
print(max_rectangle([[-5, -2], [-3, -9]]))
```
```text
29
-2
```

The best rectangle in `g` is rows `1..3`, columns `1..3` (`-3 + 4 + 2 + 8 + 10 + 1 - 1 + 1 + 7 = 29`). Notice `best`
starts at a real cell, so the all-negative grid correctly gives `-2`. If the grid is wider than it is tall, fix
pairs of the **shorter** dimension: `O(min^2 * max)`.

## 10. Matrix traversal and manipulation

### Grids in Python

A grid (matrix) with `R` rows and `C` columns is a list of `R` row lists, each of length `C`. `grid[i][j]` is the cell
in **row `i`, column `j`**: the first index picks the row (up and down), the second picks the column (left and right).
Two habits prevent most grid bugs:

- Name the sizes `R` and `C` (or `rows` and `cols`), never `n` for both. A 3 x 4 grid has `R = 3` rows and `C = 4`
  columns; `len(grid)` is `R` and `len(grid[0])` is `C`.
- Use `i` (or `r`) only for rows and `j` (or `c`) only for columns, everywhere.

Creating a grid has one famous trap:

```python
bad = [[0] * 3] * 2           # two references to ONE row
good = [[0] * 3 for _ in range(2)]
bad[0][0] = 7
good[0][0] = 7
print(bad)
print(good)
print(bad[0] is bad[1], good[0] is good[1])
```
```text
[[7, 0, 0], [7, 0, 0]]
[[7, 0, 0], [0, 0, 0]]
True False
```

`[[0] * 3] * 2` copies the **reference** to the same inner list, so changing one row changes "both". Always build rows
with a comprehension. (Copying a grid has the same issue: `grid[:]` copies only the outer list; use
`[row[:] for row in grid]`.)

To print a grid, join each row: `print(" ".join(str(x) for x in row))`. Column `j` is `[grid[i][j] for i in range(R)]`.

### Transpose

The transpose swaps rows and columns: `T[j][i] = grid[i][j]`. A 3 x 4 grid becomes 4 x 3, so for a non-square grid
you **must** build a new grid; there is no room to do it in place.

```python
grid = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]
R, C = len(grid), len(grid[0])
T = [[0] * R for _ in range(C)]       # C rows, R columns
for i in range(R):
    for j in range(C):
        T[j][i] = grid[i][j]
for row in T:
    print(row)
print([list(col) for col in zip(*grid)] == T)
```
```text
[1, 5, 9]
[2, 6, 10]
[3, 7, 11]
[4, 8, 12]
True
```

`zip(*grid)` passes each row as a separate argument to `zip`, which then yields the first elements of every row,
then the second elements, and so on: the columns. It gives tuples, hence `list(col)`.

For a **square** grid, the transpose can be done in place by swapping across the main diagonal. Only swap the
upper triangle (`j > i`); looping over every pair would swap each pair twice and undo the work:

```python
g = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
n = len(g)
for i in range(n):
    for j in range(i + 1, n):
        g[i][j], g[j][i] = g[j][i], g[i][j]
print(g)
```
```text
[[1, 4, 7], [2, 5, 8], [3, 6, 9]]
```

### Spiral order with shrinking bounds

*Print the cells of an `R x C` grid in spiral order: along the top row left to right, down the right column, along
the bottom row right to left, up the left column, then the next ring inwards.*

Keep four bounds for the part not yet visited: `top`, `bottom` (rows) and `left`, `right` (columns). Each side you walk
**uses up** that row or column, so you move its bound inwards:

1. Top row, columns `left..right`; then `top += 1`.
2. Right column, rows `top..bottom`; then `right -= 1`.
3. If rows remain (`top <= bottom`): bottom row, columns `right..left` backwards; then `bottom -= 1`.
4. If columns remain (`left <= right`): left column, rows `bottom..top` upwards; then `left += 1`.

The two checks in steps 3 and 4 matter for grids that are not square: after steps 1 and 2 the remaining part may be
empty, and walking the bottom row again would print cells twice.

Hand-trace on the 3 x 4 grid (the code follows):

```text
 1  2  3  4        ring 1: top=0 bottom=2 left=0 right=3
 5  6  7  8          top row     1 2 3 4     -> top = 1
 9 10 11 12          right col   8 12        -> right = 2
                     bottom row  11 10 9     -> bottom = 1   (top 1 <= bottom 2, so walk it)
                     left col    5           -> left = 1     (rows bottom..top = 1..1)
                   ring 2: top=1 bottom=1 left=1 right=2
                     top row     6 7         -> top = 2
                     right col   rows 2..1: nothing  -> right = 1
                     bottom row  skipped: top 2 > bottom 1
                     left col    1 <= 1, rows bottom..top = 1..2 backwards: nothing -> left = 2
                   loop ends: top 2 > bottom 1
```

Result `1 2 3 4 8 12 11 10 9 5 6 7`, all 12 cells once. The code, run on that grid and on the edge cases where most
bugs live:

```python
def spiral(grid):
    out = []
    if not grid:
        return out
    top, bottom = 0, len(grid) - 1
    left, right = 0, len(grid[0]) - 1
    while top <= bottom and left <= right:
        for j in range(left, right + 1):
            out.append(grid[top][j])
        top += 1
        for i in range(top, bottom + 1):
            out.append(grid[i][right])
        right -= 1
        if top <= bottom:
            for j in range(right, left - 1, -1):
                out.append(grid[bottom][j])
            bottom -= 1
        if left <= right:
            for i in range(bottom, top - 1, -1):
                out.append(grid[i][left])
            left += 1
    return out

print(spiral([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]]))
print(spiral([[1, 2, 3]]))                 # one row
print(spiral([[1], [2], [3]]))             # one column
print(spiral([[1, 2], [3, 4]]))
print(spiral([[1, 2, 3], [4, 5, 6], [7, 8, 9]]))
print(spiral([[1, 2], [3, 4], [5, 6]]))
print(spiral([[7]]))
```
```text
[1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7]
[1, 2, 3]
[1, 2, 3]
[1, 2, 4, 3]
[1, 2, 3, 6, 9, 8, 7, 4, 5]
[1, 2, 4, 6, 5, 3]
[7]
```

For one row: the top row is walked, `top` becomes `1 > bottom = 0`, so the right column loop is empty and the bottom row
is skipped; the left column check `left 0 <= right 1` passes, but the rows `bottom..top` = `0..1` backwards is
`range(0, 0, -1)`, empty. Without the `top <= bottom` check, the one-row grid would print `1 2 3 2 1`.

**Try it 18: trace the bounds**

For the 4 x 3 grid `[[1, 2, 3], [4, 5, 6], [7, 8, 9], [10, 11, 12]]`, list the bounds at the start of each ring and
the spiral order.

<details><summary>Answer</summary>

The run, printing the bounds at the start of each ring:

```text
ring: top=0 bottom=3 left=0 right=2
ring: top=1 bottom=2 left=1 right=1
[1, 2, 3, 6, 9, 12, 11, 10, 7, 4, 5, 8]
```

Ring 1 takes the outer ten cells: `1 2 3`, then `6 9 12`, then `11 10`, then `7 4`. Ring 2 has `top = 1`,
`bottom = 2` and `left = right = 1`: a single column holding `5` and `8`. Its "top row" is just `5` (then `top = 2`),
its "right column" is rows `2..2`, which is `8` (then `right = 0`). The bottom-row step still runs because
`top 2 <= bottom 2`, but its column range `right..left` = `0..1` backwards is empty; it only sets `bottom = 1`. The
left-column step is skipped (`left 1 > right 0`), and the loop ends.
</details>

### Rotating a square grid by 90 degrees, in place

*Rotate an `n x n` grid 90 degrees clockwise, without a second grid.*

First, where does each cell go? In a clockwise rotation, the **top row becomes the right column**. Cell `(i, j)` moves
to `(j, n - 1 - i)`. Check with a corner of a 3 x 3 grid: `(0, 0)` goes to `(0, 2)`, the top-right corner. Correct.

**Method 1: transpose, then reverse each row.** The transpose sends `(i, j)` to `(j, i)`; reversing a row sends column
`i` to column `n - 1 - i`. Together: `(i, j) -> (j, n - 1 - i)`, the rotation.

```python
def rotate_transpose(g):
    n = len(g)
    for i in range(n):
        for j in range(i + 1, n):
            g[i][j], g[j][i] = g[j][i], g[i][j]
    for row in g:
        row.reverse()

g = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
rotate_transpose(g)
for row in g:
    print(row)
```
```text
ring: top=0 bottom=3 left=0 right=2
ring: top=1 bottom=2 left=1 right=1
[1, 2, 3, 6, 9, 12, 11, 10, 7, 4, 5, 8]
[7, 4, 1]
[8, 5, 2]
[9, 6, 3]
```

The first column `1 4 7`, read from the bottom up (`7 4 1`), is now the first row. That is a quick way to check any
clockwise rotation. For **counterclockwise**, transpose and then reverse each **column** (equivalently, reverse the
order of the rows).

**Method 2: rotate layer by layer with 4-way swaps.** Look at the outer ring. Each cell on the top edge moves to the
right edge, which moves to the bottom edge, which moves to the left edge, which moves to the top. So four cells trade
places in a cycle, and we can do it with one temporary variable:

```text
top    = g[first][i]                     (save the top cell)
g[first][i]       = g[last - k][first]   left   -> top
g[last - k][first] = g[last][last - k]   bottom -> left
g[last][last - k]  = g[i][last]          right  -> bottom
g[i][last]        = top                  top    -> right
```

where `first` and `last` are the ring's first and last index, `i` walks along the ring from `first` to `last - 1`,
and `k = i - first` is the offset. Here is every swap on a 4 x 4 grid:

```python
def rotate_layers(g, show=False):
    n = len(g)
    for layer in range(n // 2):
        first, last = layer, n - 1 - layer
        for i in range(first, last):
            k = i - first
            top = g[first][i]
            g[first][i] = g[last - k][first]
            g[last - k][first] = g[last][last - k]
            g[last][last - k] = g[i][last]
            g[i][last] = top
            if show:
                print(f"layer {layer}, i={i}: cells ({first},{i}) ({i},{last}) "
                      f"({last},{last - k}) ({last - k},{first})")
                for row in g:
                    print("   ", " ".join(f"{x:>2}" for x in row))
    return g

g = [[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12], [13, 14, 15, 16]]
rotate_layers(g, show=True)
```
```text
layer 0, i=0: cells (0,0) (0,3) (3,3) (3,0)
    13  2  3  1
     5  6  7  8
     9 10 11 12
    16 14 15  4
layer 0, i=1: cells (0,1) (1,3) (3,2) (2,0)
    13  9  3  1
     5  6  7  2
    15 10 11 12
    16 14  8  4
layer 0, i=2: cells (0,2) (2,3) (3,1) (1,0)
    13  9  5  1
    14  6  7  2
    15 10 11  3
    16 12  8  4
layer 1, i=1: cells (1,1) (1,2) (2,2) (2,1)
    13  9  5  1
    14 10  6  2
    15 11  7  3
    16 12  8  4
```

Hand-check the first swap (`layer 0`, `i = 0`, `k = 0`). The four corners `(0,0)=1`, `(0,3)=4`, `(3,3)=16`, `(3,0)=13`
trade places: `13` (left, bottom corner) goes to the top-left, `16` goes to the bottom-left, `4` goes to the bottom-right,
`1` goes to the top-right. The first printed grid has `13 _ _ 1` on top and `16 _ _ 4` at the bottom. Correct. The
second swap moves `2, 8, 15, 9`; the third moves `3, 12, 14, 5`. Then layer 1 is the inner 2 x 2 ring: one swap of
`6, 7, 11, 10`. The final grid has `13 9 5 1` as its first row: the first column read upwards.

The inner loop runs `i` from `first` to `last - 1`, **not** to `last`: the last cell of each edge is the first cell of
the next edge, already moved by the corner swap. Running to `last` would rotate the corners twice. An `n x n` grid has
`n // 2` layers; for odd `n` the centre cell stays put.

**Try it 19: rotate twice**

What does rotating `[[1, 2], [3, 4]]` clockwise twice give? What simpler operation is a 180-degree rotation?

<details><summary>Answer</summary>

Rotating with `rotate_transpose` twice, then building the 180-degree turn directly:

```text
[[3, 1], [4, 2]]
[[4, 3], [2, 1]]
[[4, 3], [2, 1]]
```

A 180-degree rotation reverses the order of the rows **and** reverses each row: cell `(i, j)` goes to
`(n-1-i, n-1-j)`.
</details>

### Diagonal zigzag

*Visit an `R x C` grid along its anti-diagonals, alternating direction, as in this order for a 3 x 3 grid:*

```text
1  2  3
4  5  6        order: 1, 2, 4, 7, 5, 3, 6, 8, 9
7  8  9
```

All cells on one anti-diagonal have the same `d = i + j`, from `0` to `R + C - 2`. The rule used in the classic
version of this problem (and in this module): on an **even** `d` you walk **up and to the right** (row decreasing),
on an **odd** `d` you walk **down and to the left** (row increasing). The first diagonal (`d = 0`) is just `(0, 0)`;
`d = 1` goes down from `(0, 1)` to `(1, 0)`; `d = 2` goes up from `(2, 0)` to `(0, 2)`.

The simplest correct code collects each diagonal in one fixed direction (row increasing) and reverses it when `d` is
even. The valid rows on diagonal `d` are those with `0 <= i < R` and `0 <= d - i < C`:

```python
def zigzag(grid):
    R, C = len(grid), len(grid[0])
    out = []
    for d in range(R + C - 1):
        cells = []
        for i in range(max(0, d - C + 1), min(R - 1, d) + 1):   # rows increasing
            cells.append(grid[i][d - i])
        if d % 2 == 0:
            cells.reverse()                                     # even d: walk upwards
        out.extend(cells)
    return out

print(zigzag([[1, 2, 3], [4, 5, 6], [7, 8, 9]]))
print(zigzag([[1, 2, 3, 4], [5, 6, 7, 8]]))
print(zigzag([[1], [2], [3]]))
print(zigzag([[1, 2, 3]]))
```
```text
[[3, 1], [4, 2]]
[[4, 3], [2, 1]]
[[4, 3], [2, 1]]
[1, 2, 4, 7, 5, 3, 6, 8, 9]
[1, 2, 5, 6, 3, 4, 7, 8]
[1, 2, 3]
[1, 2, 3]
```

Hand-trace the 2 x 4 grid (`R = 2`, `C = 4`, so `d` runs `0..4`):

```text
1 2 3 4      d=0: rows 0..0 -> (0,0)=1                     even, reversed: 1
5 6 7 8      d=1: rows 0..1 -> (0,1)=2, (1,0)=5            odd:  2 5
             d=2: rows 0..1 -> (0,2)=3, (1,1)=6            even: 6 3
             d=3: rows 0..1 -> (0,3)=4, (1,2)=7            odd:  4 7
             d=4: rows 1..1 -> (1,3)=8                     even: 8
```

giving `1 2 5 6 3 4 7 8`, the printed result. The row range is where bugs hide: `max(0, d - C + 1)` keeps the column
`d - i` at most `C - 1`, and `min(R - 1, d)` keeps both the row and the column in range.

### Searching a sorted matrix: the staircase

*Every row is sorted left to right, and every column is sorted top to bottom. Is `target` in the grid?*

Start at the **top-right** corner. Its value is the largest in its row and the smallest in its column, so one
comparison always eliminates a whole row or a whole column:

- value `== target`: found.
- value `> target`: everything below in this column is even bigger, so the column is useless: move **left**.
- value `< target`: everything to the left in this row is even smaller, so the row is useless: move **down**.

At most `R + C` steps, instead of `R * C`. It is the pair-sum elimination argument again, in two dimensions.

```python
def staircase(grid, target, show=False):
    R, C = len(grid), len(grid[0])
    i, j = 0, C - 1
    while i < R and j >= 0:
        v = grid[i][j]
        if show:
            print(f"  at ({i},{j}) value {v}")
        if v == target:
            return True
        if v > target:
            j -= 1
        else:
            i += 1
    return False

g = [
    [1, 4, 7, 11, 15],
    [2, 5, 8, 12, 19],
    [3, 6, 9, 16, 22],
    [10, 13, 14, 17, 24],
    [18, 21, 23, 26, 30],
]
print("search 5")
print(staircase(g, 5, show=True))
print("search 20:", staircase(g, 20))
```
```text
search 5
  at (0,4) value 15
  at (0,3) value 11
  at (0,2) value 7
  at (0,1) value 4
  at (1,1) value 5
True
search 20: False
```

Search `5`: `15 > 5` left, `11 > 5` left, `7 > 5` left, `4 < 5` down, `5` found. Search `20` (try it by hand): the
path goes `15, 19, 22, 16, 17, 26, 23, 21, 18` and then falls off the bottom edge, at most `R + C` cells. Starting at the
**top-left** would not work: `1` is the smallest in both its row and its column, so "bigger than target" would not
tell you which way to go. The bottom-left corner works too, by symmetry.

### Set matrix zeroes: mark first, change later

*If a cell is `0`, set its whole row and whole column to `0`.* "Original zeros only": a zero that **you** wrote must
not spread further.

The trap is changing the grid while scanning it: the new zeros look like original zeros, and soon the whole grid is
zero. Separate the two phases. First record which rows and which columns contain an original zero; then zero them.

```python
def set_zeroes(g):
    R, C = len(g), len(g[0])
    zero_rows, zero_cols = set(), set()
    for i in range(R):
        for j in range(C):
            if g[i][j] == 0:
                zero_rows.add(i)
                zero_cols.add(j)
    for i in range(R):
        for j in range(C):
            if i in zero_rows or j in zero_cols:
                g[i][j] = 0
    return g

def set_zeroes_wrong(g):
    R, C = len(g), len(g[0])
    for i in range(R):
        for j in range(C):
            if g[i][j] == 0:
                for x in range(C):
                    g[i][x] = 0
                for y in range(R):
                    g[y][j] = 0
    return g

print(set_zeroes([[1, 1, 1], [1, 0, 1], [1, 1, 1]]))
print(set_zeroes([[0, 1, 2, 0], [3, 4, 5, 2], [1, 3, 1, 5]]))
print(set_zeroes_wrong([[0, 1, 2, 0], [3, 4, 5, 2], [1, 3, 1, 5]]))
```
```text
[[1, 0, 1], [0, 0, 0], [1, 0, 1]]
[[0, 0, 0, 0], [0, 4, 5, 0], [0, 3, 1, 0]]
[[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
```

The wrong version zeroes row 0 when it meets `(0, 0)`, then meets those new zeros at `(0, 1)` and `(0, 2)` and spreads
them down their columns. The extra memory of the right version is `O(R + C)`. (There is a known trick that stores the
markers in the first row and column to get `O(1)` extra memory; it is fiddly and not needed in this module.)

### Neighbours and bounds checks

Many grid problems look at the neighbours of a cell. Write the moves once as **offset lists** instead of eight
hand-written `if` blocks:

```text
DIRS4 = [(-1, 0), (1, 0), (0, -1), (0, 1)]                 up, down, left, right
DIRS8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

for di, dj in DIRS8:
    ni, nj = i + di, j + dj
    if 0 <= ni < R and 0 <= nj < C:      the bounds check
        ... use grid[ni][nj] ...
```

A corner cell has 3 of its 8 neighbours inside the grid, an edge cell 5, an inner cell 8.

Never skip the bounds check, and **never rely on negative indexes**: in Python, `grid[-1][j]` does not raise an error,
it silently reads the **last** row. A missing check at the top edge gives wrong answers without any crash, which is the
worst kind of bug. Write the check as the chained comparison `0 <= ni < R`.

### Game of Life: one generation

*Each cell is alive (`1`) or dead (`0`). In the next generation: a live cell with 2 or 3 live neighbours stays
alive; a dead cell with exactly 3 live neighbours becomes alive; every other cell is dead. Cells outside the grid
are dead.*

All cells change **at the same time**: the new state of every cell depends only on the **old** grid. So compute the
next generation into a **new** grid (updating in place would let already-updated cells influence their neighbours).

```python
DIRS8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

def live_neighbours(g, i, j):
    R, C = len(g), len(g[0])
    count = 0
    for di, dj in DIRS8:
        ni, nj = i + di, j + dj
        if 0 <= ni < R and 0 <= nj < C and g[ni][nj] == 1:
            count += 1
    return count

def step(g):
    R, C = len(g), len(g[0])
    new = [[0] * C for _ in range(R)]
    for i in range(R):
        for j in range(C):
            n = live_neighbours(g, i, j)
            if g[i][j] == 1 and n in (2, 3):
                new[i][j] = 1
            elif g[i][j] == 0 and n == 3:
                new[i][j] = 1
    return new

def show(g):
    for row in g:
        print(" ".join(".#"[x] for x in row))

blinker = [
    [0, 0, 0, 0, 0],
    [0, 0, 1, 0, 0],
    [0, 0, 1, 0, 0],
    [0, 0, 1, 0, 0],
    [0, 0, 0, 0, 0],
]
print("neighbour counts:")
for i in range(5):
    print(" ".join(str(live_neighbours(blinker, i, j)) for j in range(5)))
print("generation 0:")
show(blinker)
g1 = step(blinker)
print("generation 1:")
show(g1)
print("generation 2 equals generation 0:", step(g1) == blinker)
```
```text
neighbour counts:
0 1 1 1 0
0 2 1 2 0
0 3 2 3 0
0 2 1 2 0
0 1 1 1 0
generation 0:
. . . . .
. . # . .
. . # . .
. . # . .
. . . . .
generation 1:
. . . . .
. . . . .
. # # # .
. . . . .
. . . . .
generation 2 equals generation 0: True
```

Hand-check the counts. The centre `(2, 2)` touches `(1, 2)` and `(3, 2)`: 2 neighbours, so it survives. The ends
`(1, 2)` and `(3, 2)` touch only the centre: 1 neighbour each, so they die. The cells `(2, 1)` and `(2, 3)`, beside
the centre, touch all three live cells: they are born. The result is a horizontal bar, and one more step turns it back:
a "blinker" with period 2.

Edge cells are where bounds bugs show up. Here is the most common one: checking only `ni < R and nj < C` and
forgetting the `>= 0` half. Python does not crash on `grid[-1]`, it reads the last row, so the grid silently "wraps
around". If the last row and column happen to be empty, the answer is still right, which is why the bug survives
casual testing. Put live cells in the last row and it shows at once:

```python
DIRS8 = [(-1, -1), (-1, 0), (-1, 1), (0, -1), (0, 1), (1, -1), (1, 0), (1, 1)]

def count(g, i, j, check_low):
    R, C = len(g), len(g[0])
    n = 0
    for di, dj in DIRS8:
        ni, nj = i + di, j + dj
        if ni < R and nj < C and (not check_low or (ni >= 0 and nj >= 0)):
            n += g[ni][nj]
    return n

g = [
    [0, 0, 0],
    [0, 0, 0],
    [1, 1, 0],
]
print("neighbours of (0,0) with full check:", count(g, 0, 0, True))
print("neighbours of (0,0) without >= 0  :", count(g, 0, 0, False))
```
```text
neighbours of (0,0) with full check: 0
neighbours of (0,0) without >= 0  : 2
```

With the bug, `(0, 0)` "sees" the two live cells of the bottom row through row `-1`. Always check both ends.

### Direction vectors and turning: a robot walk

*A robot stands on a grid of open cells `.` and walls `#`, facing North. Commands: `F` (move forward one cell),
`L` (turn left 90 degrees), `R` (turn right 90 degrees). A move into a wall or off the grid is skipped. Report where
it ends, which way it faces, and how many distinct cells it visited.*

Store the four directions **in clockwise order**, as row and column offsets:

```text
index:  0      1      2      3
name:   N      E      S      W
(dr,dc) (-1,0) (0,1)  (1,0)  (0,-1)
```

North is "row minus one" because row `0` is at the top. With clockwise order, turning is arithmetic modulo 4:

- turn right: `d = (d + 1) % 4`
- turn left: `d = (d + 3) % 4` (the same as `(d - 1) % 4` in Python, since `%` is never negative)

```python
DR = [-1, 0, 1, 0]
DC = [0, 1, 0, -1]
NAMES = "NESW"

def walk(grid, r, c, commands):
    R, C = len(grid), len(grid[0])
    d = 0                                   # facing North
    visited = {(r, c)}
    for cmd in commands:
        if cmd == "L":
            d = (d + 3) % 4
        elif cmd == "R":
            d = (d + 1) % 4
        else:
            nr, nc = r + DR[d], c + DC[d]
            if 0 <= nr < R and 0 <= nc < C and grid[nr][nc] != "#":
                r, c = nr, nc
                visited.add((r, c))
            # otherwise the move is blocked: skip it, change nothing
    return r, c, NAMES[d], len(visited)

grid = [
    "....",
    ".#..",
    "....",
]
print(walk(grid, 2, 0, "FFFRFRFLFRF"))
```
```text
(1, 2, 'S', 6)
```

Hand-trace it (row `0` at the top; the wall is at `(1, 1)`):

```text
    col 0 1 2 3
row 0   . . . .
row 1   . # . .
row 2   S . . .        S = start (2,0), facing N

F  N: (2,0) -> (1,0)   open                    visited 2
F  N: (1,0) -> (0,0)   open                    visited 3
F  N: (0,0) -> (-1,0)  off the grid: skipped
R  facing E
F  E: (0,0) -> (0,1)   open                    visited 4
R  facing S
F  S: (0,1) -> (1,1)   wall: skipped
L  facing E
F  E: (0,1) -> (0,2)   open                    visited 5
R  facing S
F  S: (0,2) -> (1,2)   open                    visited 6
```

It ends at `(1, 2)` facing South, having visited 6 distinct cells, which matches the printed `(1, 2, 'S', 6)`. Two
details from the trace: a skipped move (off the grid or into the wall) does not change the position or the direction, and the start cell counts as
visited. Count **distinct** cells with a set, because a robot that walks back and forth visits some cells twice.

**Try it 20: turning arithmetic**

Starting facing North (`d = 0`), what is the facing after `R R R`? After `L`? After `L L L L L`? After `R L L`?

<details><summary>Answer</summary>

```python
NAMES = "NESW"
for cmds in ["RRR", "L", "LLLLL", "RLL"]:
    d = 0
    for c in cmds:
        d = (d + 1) % 4 if c == "R" else (d + 3) % 4
    print(cmds, NAMES[d])
```
```text
RRR W
L W
LLLLL W
RLL W
```

Three rights are one left (West). Five lefts are one left (four lefts are a full circle). `R L L` is one net left.
Using `(d - 1) % 4` for a left turn gives the same results in Python, but in C++ or Java `-1 % 4` is `-1`, so `+3` is
the portable habit.
</details>

## 11. Which pattern? A decision guide

When a new problem arrives, ask these questions in order. The first "yes" usually names the pattern.

1. **Is it a grid?** Matrix traversal (section 10): decide the visiting order (rows, spiral, diagonals, neighbours,
   a walker with a direction), write the bounds check once, and decide whether you need a new grid (simultaneous
   updates) or can work in place.
2. **Many range-sum questions on an array that does not change?** Prefix sums (section 2); for rectangles, 2D prefix
   sums.
3. **Many range updates, then one read?** Difference array (section 4).
4. **Count (or find the longest) subarrays with sum exactly `k`, or divisible by `k`, with negatives allowed?** Prefix
   sums + dictionary (section 3): count map for "how many", first-index map for "longest".
5. **The data is sorted (or you may sort it) and you look for a pair or triplet with a target sum?** Two pointers from
   both ends (section 5). Sorting first costs `O(n log n)`, which is fine at `n <= 2 * 10^5`.
6. **Rewrite or filter an array in place?** Slow and fast pointers. **Combine two sorted lists?** One pointer each.
7. **Every window of a given size `k`?** Fixed sliding window (section 6); a counts dictionary if the window holds
   characters; the maximum of each window needs a monotonic deque (section 8).
8. **Longest or shortest contiguous block with a condition that stays true when you shrink the block (or grow it)?**
   Variable sliding window (section 7). Check that the values are non-negative if the condition is about sums.
   "Exactly `k`" is `atMost(k) - atMost(k - 1)`.
9. **Maximum (or minimum) subarray sum?** Kadane (section 9); circular: also the minimum; 2D: fix two rows.
10. **Choosing from the ends?** Look at the complement: what remains is a window in the middle.

And always: **read the constraints first.** `n <= 2 * 10^5` means one pass. If you catch yourself writing two nested
loops over the array, ask which of the questions above you skipped.

Here are short scenarios with the reasoning spelled out.

| Scenario | Pattern | Why |
|---|---|---|
| Daily temperatures for a year; 10^5 questions "average from day `l` to day `r`" | prefix sums | static array, many range sums |
| 10^5 bookings "seats `l..r` reserved by `v` people", print the load on each seat | difference array | many range adds, one read |
| Longest stretch of days whose total rainfall is exactly 100 mm; rainfall `>= 0` | variable window (or prefix + first index) | non-negative values keep the window monotone |
| The same with profit/loss values (can be negative) | prefix sums + first-index map | negatives break the window |
| Shortest stretch with total profit at least `k`, losses allowed | prefix sums + monotonic deque | "at least" + negatives |
| Two prices in a sorted list that sum to a budget | two pointers from both ends | sorted pair |
| The best single stretch of profit | Kadane | maximum subarray |
| Highest temperature in every 7-day window | monotonic deque | window maximum |
| A cleaning robot on a floor map with obstacles | grid walk with direction vectors | turning and bounds |

**Try it 21: name the pattern**

(a) Given a string, find the length of the longest substring that contains at most two vowels. (b) Given an
`n x n` image, flip it upside down, then mirror it left to right. (c) Given an array with negative numbers, count
subarrays whose sum is a multiple of 7. (d) Given heights of bars, the total water trapped after rain.

<details><summary>Answer</summary>

(a) Variable window: the state is "number of vowels in the window", shrink while it exceeds 2; the condition is
monotone. (b) Matrix manipulation: reversing the row order and then each row is a 180-degree rotation (`(i, j)` goes
to `(n-1-i, n-1-j)`); two pointer swaps per row or column, in place. (c) Prefix sums with a remainder count
dictionary, using Python's `%` (always in `0..6`). (d) Two pointers from both ends with running maxima (or prefix and
suffix maximum arrays).
</details>

## 12. Common traps

1. **Prefix array without the leading zero**, then a special case for `l = 0`. Use `P` of length `n + 1`, `P[0] = 0`.
2. **Mixing 0-based and 1-based formulas**: `P[r + 1] - P[l]` (0-based) vs `P[r] - P[l - 1]` (1-based). Test a range
   of length one.
3. **Forgetting `seen = {0: 1}`** (or `first = {0: -1}`) in prefix + dictionary: subarrays starting at index `0` are lost.
4. **Inserting before looking up** in prefix + dictionary: with `k = 0` you count empty subarrays.
5. **Overwriting the first index** when you want the longest subarray: store a prefix value only the first time.
6. **Difference array of size `n`**: `D[r + 1]` falls off the end when `r = n - 1`. Use `n + 1`. In 2D, write all
   four corners.
7. **2D prefix building without `- P[i][j]`**: the overlap is counted twice.
8. **Two pointers on unsorted data**: the elimination argument needs sorted order.
9. **`i <= j` instead of `i < j`** in pair-sum: an element is paired with itself.
10. **Three-sum duplicates**: skip equal first elements, and after a match move both pointers past equal values.
11. **Dutch flag**: advancing `mid` after swapping with `high` skips an unchecked value.
12. **Merge without copying the tails**: the rest of the longer list is lost.
13. **Fixed window: forgetting the first window** (counting `n - k` windows instead of `n - k + 1`), or using
    `a[r - k + 1]` as the leaving element instead of `a[r - k]`.
14. **Starting `best` at `0`** for maximum window sums or Kadane: wrong when every value is negative.
15. **Shrinking with `if` instead of `while`**: the window can stay invalid. Counts and windows come out wrong even
    when the maximum length happens to be right.
16. **Not deleting zero counts**: `len(count)` and dictionary equality become wrong.
17. **Window length `r - l`** instead of `r - l + 1`.
18. **Sliding window with negative numbers**: the window is not monotone. Use prefix sums + dictionary or a deque.
19. **Exactly-k counted directly** with one window: use `atMost(k) - atMost(k - 1)`.
20. **Slicing inside the loop** (`sum(a[l:r])`, `max(a[l:r])`, `s[l:r] == t`): `O(k)` per step, the brute force in disguise.
21. **Kadane tie rules**: restart on `cur < 0` or `cur <= 0`, update on `>` or `>=`; the problem decides which
    subarray to report. Check against a brute force.
22. **Circular Kadane when all values are negative**: `total - min` is the empty subarray. Return the plain maximum.
23. **`[[0] * C] * R`**: one row shared `R` times. Use a comprehension. Copy grids with `[row[:] for row in g]`.
24. **Swapping `R` and `C`**, or `grid[x][y]` with `x` as the column. Rows first, always.
25. **Negative indexes in neighbour checks**: `grid[-1]` is the last row, not an error. Check `0 <= ni < R and 0 <= nj < C`.
26. **Updating Game of Life in place**: the new state must come only from the old grid. Build a new grid.
27. **Spiral without the inner checks**: one-row or one-column remainders are printed twice.
28. **In-place rotation running `i` to `last`** instead of `last - 1`: corners are rotated twice.
29. **Set zeroes on the fly**: written zeros spread. Mark rows and columns first.
30. **Turning left with `(d - 1) % 4`** is fine in Python but not in C++/Java; `(d + 3) % 4` works everywhere.

## 13. Summary

- Read the constraints first: `n <= 2 * 10^5` rules out visiting all `n^2 / 2` subarrays.
- **Prefix sums**: `P[0] = 0`, `P[i + 1] = P[i] + a[i]`; `sum(a[l..r]) = P[r + 1] - P[l]`. `O(n)` to build, `O(1)` per
  query, `O(n)` memory. 2D: big block minus top strip minus left strip plus corner.
- **Prefix + dictionary**: a subarray `l..r` has sum `k` when `P[l] = P[r + 1] - k`. Count map (start `{0: 1}`) for
  counting, first-index map (start `{0: -1}`) for the longest, remainders for divisibility. Works with negatives.
- **Difference array**: `D[l] += v`, `D[r + 1] -= v`, then prefix-sum `D`. Each update `O(1)`. 2D: four corners.
- **Two pointers**: opposite ends on sorted data (each step eliminates a whole row of pairs), slow/fast to compact
  in place, one pointer per list to merge. Three-sum is sort + fixed first element + pair-sum, with duplicate skipping.
  Dutch flag keeps three zones with an invariant. Container and rain water move the shorter side.
- **Fixed window**: add the entering element, remove the leaving one; test the first window too; counts dictionary
  with zero-count deletion for characters; circular windows with `% n`; "take from the ends" is a middle window.
- **Variable window**: grow `r`, shrink `l` **while** invalid, then update the answer (longest), or update inside the
  shrinking loop (shortest). `O(n)` because `l` and `r` only move right. Needs a monotone condition; sums need
  non-negative values. `exactly(k) = atMost(k) - atMost(k - 1)`.
- **Monotonic deque**: keep indices whose values are decreasing; the front is the window maximum; `O(n)` amortised.
  With prefix sums and an increasing deque it solves "shortest subarray with sum at least `k`" with negatives.
- **Kadane**: `cur = max(x, cur + x)`, `best = max(best, cur)`, start from `a[0]`. Tie rules decide reported positions.
  Circular: `max(best, total - min)` unless all negative. 2D: fix top and bottom rows, Kadane on column sums.
- **Grids**: `grid[row][col]`, sizes `R` and `C`; transpose builds a `C x R` grid; spiral with four shrinking bounds;
  rotate clockwise by transpose + reverse rows or by 4-way layer swaps; diagonals share `i + j`; staircase search
  from the top-right; mark before zeroing; neighbours from offset lists with a full bounds check; directions in
  clockwise order and turning with `% 4`.

## 14. How this chapter maps to the problems

| Problems | Topic | Section |
|---|---|---|
| 1 (prefix sum array), 2 (range sum queries), 3 (trace prefix sums), 20 (explain prefix vs recompute) | 1D prefix sums | 2 |
| 22 (equilibrium index), 40 (product except self) | running sums and products from both sides | 2 |
| 23 (grid prefix sum queries) | 2D prefix sums | 2 |
| 21 (subarray sum equals k), 52 (longest subarray sum k), 54 (subarrays divisible by k) | prefix sums + dictionary | 3 |
| 4 (range add), 24 (grid difference array), 49 (explain difference array) | difference arrays | 4 |
| 5 (reverse in place), 6 (palindrome), 7 (pair sum sorted), 10 (trace pointer moves), 41 (explain correctness) | two pointers from both ends | 5 |
| 8 (merge two sorted), 9 (dedupe sorted in place) | one pointer per list, slow/fast | 5 |
| 25 (three sum), 43 (trace three-sum pointers), 38 (Dutch flag), 26 (container), 45 (trapping rain water) | two pointers, harder | 5 |
| 11 (max sum window), 12 (windows above average), 13 (trace sliding window), 29 (anagram windows) | fixed window | 6 |
| 57 (cards from the ends), 58 (min swaps, circular) | fixed window: complement and circular | 6 |
| 27 (longest unique substring), 31 (trace variable window), 28 (shortest sum at least), 30 (max ones with k flips) | variable window | 7 |
| 42 (fix sliding window bugs), 44 (exactly k distinct), 48 (minimum window substring), 39 (explain negatives) | variable window, harder | 7 |
| 53 (sliding window maximum), 55 (shortest subarray with negatives) | monotonic deque | 8 |
| 14 (max subarray), 15 (trace Kadane), 46 (subarray with bounds), 33 (buy and sell), 32 (circular), 47 (max rectangle) | Kadane | 9 |
| 16 (transpose), 17 (spiral), 18 (trace spiral), 19 (rotate), 37 (trace rotation layers), 35 (diagonal zigzag) | grid orders | 10 |
| 36 (staircase search), 34 (set matrix zeroes) | grid search and marking | 10 |
| 50 (game of life), 51 (trace game of life), 56 (robot walk) | neighbours and directions | 10 |
| 59 (explain: choose the pattern), 60 (build: sensor log analyser) | everything | 11 |

Habits that win points in this module: write the brute force first and keep it as a checker; test the edge cases
every pattern has (empty array, one element, all negative, all equal, window size equal to `n`, one-row and
one-column grids); and pin the tie rule before writing code that reports positions.

## 15. Learning outcomes checklist

By the end of this module you should be able to:

- [ ] Look at the constraints and the wording and name the pattern before writing code.
- [ ] Build 1D and 2D prefix sums and answer 0-based and 1-based range queries without off-by-one errors.
- [ ] Count subarrays with sum `k`, find the longest one, and count subarrays divisible by `k`, with negative values.
- [ ] Apply many range updates with a difference array, in 1D and 2D, and explain why it works.
- [ ] Use two pointers on sorted data and explain why they never skip the answer; write three-sum without duplicates.
- [ ] Compact an array in place with slow/fast pointers, merge two sorted lists, and sort 0/1/2 in one pass.
- [ ] Write fixed and variable sliding windows with `while` shrinking and zero-count deletion, and count "exactly k".
- [ ] Explain why negative numbers break the window, and use a prefix dictionary or a monotonic deque instead.
- [ ] Write Kadane with positions and a stated tie rule, the circular version, and the 2D version.
- [ ] Traverse and transform grids: transpose, spiral, rotation, diagonals, staircase search, set zeroes, Game of Life, and a robot walk with direction vectors.

## 16. Further reading

- Python docs: `collections.deque`, `collections.Counter`, `itertools.accumulate`, `zip`.
- cp-algorithms.com: "Minimum stack / Minimum queue" (the idea behind the monotonic deque).
- CSES Problem Set, "Sorting and Searching" and "Range Queries"; LeetCode's array, two-pointer and sliding-window
  problems. Practise the problems listed in `external.toml`.
