# dsa.06 Binary search

## 1. Why halving works

Imagine a dictionary with a million words. You want the word "mango". You do not start at the first page and read every word. You open the book in the middle, see "lemon", know that "mango" comes later, and
throw away the whole first half in one move. Then you open the middle of the rest, and so on. After about 20 openings you are at the word. That is **binary search**, and it is the most important
"clever" idea in this course: *use order to throw away half of the possibilities with one question*.

The rule is simple, and it hides a lot of detail. Almost everybody understands binary search; almost nobody writes it bug-free on the first try. (A famous study found that most professional programmers' first versions had bugs, and the version in a big
standard library carried a hidden bug for years.) This module is about writing it with **control**: you will know why every `+ 1` and every `<=` is there.

### What you can do after this module

1. **Write a bug-free binary search with a clear loop invariant.** You will pick one template and use it for finding a value, the first and last copy of a value, an insertion point, and more.
2. **Spot a monotonic condition and binary search on the answer.** Many problems have no sorted list at all, only a question like "is speed `k` enough?" whose answer flips once from No to Yes.

### The cost of halving

Each question cuts the candidates in half. After `k` questions at most `n / 2^k` candidates remain. You are done when `n / 2^k < 1`, so `k` is about `log2(n)`. Let us see how small that number is.

```python
import math

for n in (10, 1_000, 1_000_000, 1_000_000_000, 10**18):
    print(f"{n:>22}  about {math.ceil(math.log2(n)):>2} halvings")
```
```text
                    10  about  4 halvings
                  1000  about 10 halvings
               1000000  about 20 halvings
            1000000000  about 30 halvings
   1000000000000000000  about 60 halvings
```

A million items need 20 halvings. A billion need 30. Even `10^18` (more than the number of grains of sand on Earth) needs only 60. This is why a program that does 60 steps can answer a question
that a loop could never answer: a loop of `10^18` steps would run for thousands of years.

Compare it with a linear scan for a list of a million sorted numbers and a thousand queries:

```python
n = 1_000_000
q = 1_000
linear_steps = n * q
binary_steps = 20 * q
print("linear scan :", linear_steps, "comparisons")
print("binary search:", binary_steps, "comparisons")
print("ratio        :", linear_steps // binary_steps)
```
```text
linear scan : 1000000000 comparisons
binary search: 20000 comparisons
ratio        : 50000
```

The binary search does 50,000 times less work. (The exact ratio is "about", since the real number of steps is between 19 and 20.)

### The price: the data must be ordered

Halving works because **one comparison tells you about many elements at once**. If `a[mid] < x` and the list is sorted, then everything before `mid` is also smaller than `x`, so none of them is the target.
Take away the order and this reasoning collapses:

```python
a = [5, 1, 4, 2, 3]          # NOT sorted
x = 3

lo, hi = 0, len(a) - 1
while lo <= hi:
    mid = (lo + hi) // 2
    print("lo", lo, "hi", hi, "mid", mid, "a[mid]", a[mid])
    if a[mid] == x:
        print("found")
        break
    elif a[mid] < x:
        lo = mid + 1
    else:
        hi = mid - 1
else:
    print("not found, although 3 is in the list!")
```
```text
lo 0 hi 4 mid 2 a[mid] 4
lo 0 hi 1 mid 0 a[mid] 5
not found, although 3 is in the list!
```

The 3 sits at the end, but the search looked at `a[2] = 4`, concluded "go left", and never came back. Binary search on unsorted data gives **wrong answers**, not just slow ones.

Later in this chapter we will see that "sorted" is really a special case of something more general: a **monotonic condition** (a yes/no question whose answers look like `No No No Yes Yes Yes`).
For now keep the simple picture: sorted data in, halving out.

### When is it worth it?

Sorting costs `O(n log n)`. A single search in an unsorted list costs only `O(n)`, so for **one** query a linear scan is cheaper than "sort, then binary search". For `q` queries on the same data, sorting once and
searching `q` times costs `O(n log n + q log n)`, which is much less than `O(q n)` when `q` is more than a few. If your data arrives sorted (timestamps, ids, a sorted file) binary search is free.

**Predict the output 1.** A sorted list has 1,000,000 elements. You search for a value that is not in the list, using binary search. About how many elements do you look at?

<details><summary>Answer</summary>

About 20 (more exactly, at most `floor(log2(1000000)) + 1 = 20`). Failing to find the value costs the same as finding it in the worst case: the range simply shrinks until it is empty.

```python
import math
print(math.floor(math.log2(1_000_000)) + 1)
```
```text
20
```
</details>

## 2. Classic binary search and the loop invariant

Let us write the search once, slowly, and learn why it works. The problem: a sorted list `a` of distinct numbers and a target `x`. Return the index of `x`, or `-1`.

### The idea in one picture

Keep a window `a[lo..hi]` (both ends included) that **might still contain the target**. At the start the window is the whole list. At every step look at the middle element and compare:

- `a[mid] == x`: found.
- `a[mid] < x`: `x` can only be to the right. Everything up to and including `mid` is useless. New window: `mid + 1 .. hi`.
- `a[mid] > x`: `x` can only be to the left. New window: `lo .. mid - 1`.

When the window is empty (`lo > hi`), the target is not there.

```python
def binary_search(a, x):
    lo, hi = 0, len(a) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if a[mid] == x:
            return mid
        elif a[mid] < x:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


a = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
print(binary_search(a, 23))
print(binary_search(a, 2))
print(binary_search(a, 91))
print(binary_search(a, 40))
print(binary_search([], 7))
```
```text
5
0
9
-1
-1
```

### The loop invariant: the sentence that makes it correct

A **loop invariant** is a sentence that is true before the loop starts, stays true after every step, and, when the loop ends, tells you the result. For this search the invariant is:

> **If `x` is in the list, then its index is inside `lo..hi`.**

Check the three duties of an invariant:

1. **Before the loop.** `lo = 0`, `hi = n - 1`: the window is the whole list, so the sentence is true.
2. **Each step keeps it true.** If `a[mid] < x`, the list is sorted, so every index `<= mid` holds a value `<= a[mid] < x`: none of them is `x`. Moving `lo` to `mid + 1` throws away only impossible indices.
   The case `a[mid] > x` is the mirror image.
3. **At the end.** The loop stops when `lo > hi`, i.e. the window is empty. By the invariant, "`x` is in the list" would put its index in an empty window, which is impossible. So `x` is not in the list: return `-1`.

If you ever feel unsure about a `+ 1`, ask: *"does my update keep the invariant? does it make the window strictly smaller?"* Those two questions find every off-by-one bug.

### Watching the window shrink

Let us print the window at each step. The list has 16 elements, so we expect at most 5 probes.

```python
a = list(range(0, 32, 2))     # 0, 2, 4, ..., 30  (16 elements)
x = 22
lo, hi = 0, len(a) - 1
step = 0
while lo <= hi:
    mid = (lo + hi) // 2
    step += 1
    print(f"step {step}: window a[{lo}..{hi}] has {hi - lo + 1} elements, mid = {mid}, a[mid] = {a[mid]}")
    if a[mid] == x:
        print("found at", mid)
        break
    elif a[mid] < x:
        lo = mid + 1
    else:
        hi = mid - 1
```
```text
step 1: window a[0..15] has 16 elements, mid = 7, a[mid] = 14
step 2: window a[8..15] has 8 elements, mid = 11, a[mid] = 22
found at 11
```

The window had 16, then 8, then 4... elements. Each step costs one comparison and halves the window (the middle element is removed from the window, and the rest is split in two).

### How many probes at most?

If the window has `m` elements, one step leaves at most `m // 2` elements (the larger side, when `m` is even, has `m / 2` elements, and when `m` is odd both sides have `(m - 1) / 2`).
So the number of probes is at most the number of times you can do `m = m // 2` before reaching 0, plus the last one: that is `floor(log2(n)) + 1`.

```python
def probes_worst_case(n):
    count = 0
    while n > 0:
        n //= 2
        count += 1
    return count


for n in (1, 2, 3, 7, 8, 10, 1000, 1_000_000):
    print(n, "->", probes_worst_case(n))
```
```text
1 -> 1
2 -> 2
3 -> 2
7 -> 3
8 -> 4
10 -> 4
1000 -> 10
1000000 -> 20
```

This is `n.bit_length()` in Python: the number of binary digits of `n`. Binary search is called "binary" for a reason: the number of steps is the number of bits.

### Why `mid = (lo + hi) // 2`?

Any value between `lo` and `hi` would keep the invariant, but the middle gives the best worst case. In languages with fixed-size integers (C, Java) the sum `lo + hi` can **overflow** when both are near the
largest integer, and the safe form is `lo + (hi - lo) // 2`. In Python integers never overflow, so `(lo + hi) // 2` is fine. Still, you will see the safe form in other people's code, and it gives the same number.

```python
lo, hi = 2**62, 2**62 + 10
print((lo + hi) // 2)
print(lo + (hi - lo) // 2)
```
```text
4611686018427387909
4611686018427387909
```

**Predict the output 2.** In the list `[1, 3, 5, 7, 9, 11, 13]` we search for 11 with the closed template. Which indices are probed, in order?

<details><summary>Answer</summary>

```python
a = [1, 3, 5, 7, 9, 11, 13]
lo, hi = 0, 6
while lo <= hi:
    mid = (lo + hi) // 2
    print(mid, a[mid])
    if a[mid] == 11:
        break
    elif a[mid] < 11:
        lo = mid + 1
    else:
        hi = mid - 1
```
```text
3 7
5 11
```

The probes are index 3 (value 7, too small), then 5 (value 11: found). Two probes.
</details>

### Binary search is also a "yes/no" game

Look at the search again, but ignore equality. Define the question `Q(i)`: "is `a[i] >= x`?" On a sorted list the answers look like `No No No Yes Yes Yes`. Finding `x` means finding the place where the answers flip.
This view is the key to the second half of the module: when you can phrase *any* problem as "find where a No/Yes sequence flips", binary search applies, even if there is no list at all.

## 3. Three template styles, and why you should pick one

There are three popular ways to write the loop. They are all correct, and they differ in what the window means. Mixing parts of them is the number one source of bugs.

### Template A: closed window `[lo, hi]`

This is the one you just saw.

```text
lo, hi = 0, n - 1
while lo <= hi:
    mid = (lo + hi) // 2
    if (found at mid): return mid
    elif (go right):   lo = mid + 1
    else:              hi = mid - 1
return -1                       # not found
```

- The window is **closed**: both `lo` and `hi` are candidates.
- The loop runs while the window is not empty: `lo <= hi`.
- Both updates exclude `mid`: `mid + 1` and `mid - 1`.
- At the end `lo = hi + 1`, and the window is empty.

Use it when you want to *stop at a hit*: "find x".

### Template B: half-open window `[lo, hi)`

Here `hi` is **not** a candidate. It means "one past the last candidate".

```text
lo, hi = 0, n
while lo < hi:
    mid = (lo + hi) // 2
    if (mid is too small, go right): lo = mid + 1
    else:                            hi = mid
return lo                       # the first index where the answer is "not too small"
```

- The window is `lo, lo + 1, ..., hi - 1` and has `hi - lo` elements. It is empty when `lo == hi`.
- `hi = mid` keeps `mid` out of the window, because `hi` is exclusive. That is why there is no `- 1` here.
- `hi` can start at `n`: the value `n` means "no element qualifies". The loop never reads `a[n]` because `mid < hi`.
- At the end `lo == hi`, and it is **the first index where the condition is True** (or `n`).

Use it for "find the first position where something becomes True": lower bound, upper bound, insertion point, first bad version. This template is the favourite of this module.

### Template C: closed window with shrinking (`lo < hi`, `hi = mid`)

```text
lo, hi = 0, n - 1
while lo < hi:
    mid = (lo + hi) // 2
    if (mid is too small): lo = mid + 1
    else:                  hi = mid
return lo                       # exactly one candidate remains; check it if "not found" is possible
```

- The window is closed `[lo, hi]` but the loop stops at **one** remaining element, not at an empty window.
- It assumes the answer **exists** in the window. For "the minimum of a rotated array" or "the peak of a mountain" that is guaranteed. For "find x" you must test `a[lo] == x` after the loop.

Use it when the problem guarantees an answer. The loop body is identical to template B; only the initial `hi` differs (`n - 1` against `n`).

### The three side by side

All three run on the same list and the same target, so you can see how they behave.

```python
def template_a(a, x):
    lo, hi = 0, len(a) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if a[mid] == x:
            return mid
        elif a[mid] < x:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


def template_b(a, x):
    lo, hi = 0, len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return lo if lo < len(a) and a[lo] == x else -1


def template_c(a, x):
    lo, hi = 0, len(a) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return lo if a[lo] == x else -1


a = [2, 5, 8, 12, 16, 23, 38, 56, 72, 91]
for x in (2, 23, 91, 40, 1, 100):
    print(x, template_a(a, x), template_b(a, x), template_c(a, x))
```
```text
2 0 0 0
23 5 5 5
91 9 9 9
40 -1 -1 -1
1 -1 -1 -1
100 -1 -1 -1
```

All three agree on every query. They differ in **how** they get there (which probes, what the window means), not in what they return.

### Why pick one and stick to it

Each template is a package: *initial value of `hi`*, *loop condition*, *update rules*, *final meaning of `lo`*. The pieces only work together. Take the "half-open" update `hi = mid` and combine it with the closed condition
`lo <= hi`: the loop never ends when `lo == hi`, because `hi = mid` does not change anything. Take the closed update `hi = mid - 1` with the half-open start `hi = n`: you may skip an answer.

The recommendation of this module: **write template B for every "first position where..." problem, and template A when you want to stop on a hit**. For the rest of the chapter, when you see `lo, hi = 0, n` and `while lo < hi`, that is template B.
Whichever you choose, say its invariant to yourself *before* you write the loop. The chapter's section 4 shows what happens when you do not.

**Try it 1.** Write template B for "first index with `a[i] >= x`" and run it on `a = [1, 3, 3, 5]` for `x = 3`, `x = 4`, `x = 6`. What do you get?

<details><summary>Answer</summary>

```python
def lower_bound(a, x):
    lo, hi = 0, len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return lo


a = [1, 3, 3, 5]
print(lower_bound(a, 3), lower_bound(a, 4), lower_bound(a, 6))
```
```text
1 3 4
```

3 first occurs at index 1; 4 would be inserted at index 3 (before the 5); 6 is larger than everything, so the answer is 4 (the length).
</details>

## 4. Off-by-one traps

Binary search bugs have a small number of causes. Learn them as a list, and test every loop you write against it.

### Trap 1: `lo = mid` with the rounding-down `mid`

If you write `lo = mid` (without `+ 1`), the window might not shrink. Take `lo = 3`, `hi = 4`. Then `mid = (3 + 4) // 2 = 3`, and `lo = mid` leaves `lo = 3`. The loop repeats the same state forever.

The experiment below caps the loop at 5 steps so that it ends.

```python
a = [1, 3, 5, 7]
x = 7
lo, hi = 0, len(a) - 1
steps = 0
while lo < hi and steps < 5:
    mid = (lo + hi) // 2
    steps += 1
    if a[mid] < x:
        lo = mid          # BUG: should be mid + 1
    else:
        hi = mid
    print("step", steps, "lo", lo, "mid", mid, "hi", hi)
```
```text
step 1 lo 1 mid 1 hi 3
step 2 lo 2 mid 2 hi 3
step 3 lo 2 mid 2 hi 3
step 4 lo 2 mid 2 hi 3
step 5 lo 2 mid 2 hi 3
```

From step 2 on the state is `lo = 2, hi = 3`, and it never changes. Two cures:

1. Use `lo = mid + 1` (the usual one): the window strictly shrinks, because `mid` is thrown away.
2. If you must keep `mid` in the window on the left side (`lo = mid`), round the middle **up**: `mid = (lo + hi + 1) // 2`, and use `hi = mid - 1` on the other side. This is the template for "last position where the condition is True"; we will need it in section 10.

**The shrink check.** For every branch of your loop ask: *is the new window strictly smaller than the old one?* If one branch can leave `lo` and `hi` unchanged, you have an infinite loop.

### Trap 2: `<=` against `<`

The condition `lo <= hi` belongs to the closed window, `lo < hi` to the half-open or shrinking one. Use the wrong one and you get one of two bugs:

- Template A with `<`: the loop stops when `lo == hi`, and **one candidate is never tested**.

```python
def broken_closed(a, x):
    lo, hi = 0, len(a) - 1
    while lo < hi:                  # BUG: should be <=
        mid = (lo + hi) // 2
        if a[mid] == x:
            return mid
        elif a[mid] < x:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


a = [1, 3, 5, 7, 9]
print([broken_closed(a, x) for x in a])
```
```text
[0, -1, 2, 3, -1]
```

Five values, five expected indices `0 1 2 3 4`. Some are `-1`: the loop ended with `lo == hi` pointing at the answer and never looked at it.

- Template B with `<=`: when `lo == hi`, `mid = lo`, and `hi = mid` changes nothing: infinite loop.

### Trap 3: the wrong initial `hi`

For the half-open template `hi` must be `n`. If you write `hi = n - 1`, the answer `n` ("everything is smaller") becomes impossible.

```python
def lower_bound_wrong(a, x):
    lo, hi = 0, len(a) - 1          # BUG: should be len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return lo


a = [1, 3, 5]
print(lower_bound_wrong(a, 4))
print(lower_bound_wrong(a, 9))
```
```text
2
2
```

For `x = 9` the correct answer is 3 (the length), but we got 2. Pointing at the last element is wrong, since `a[2] = 5 < 9`. The bug only shows up for queries bigger than everything, a classic **edge case** that simple tests miss.

### Trap 4: stopping at a hit when you need the first (or last) one

With duplicates the classic search returns *some* index holding `x`, not necessarily the first.

Here is the experiment.

```python
def classic(a, x):
    lo, hi = 0, len(a) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if a[mid] == x:
            return mid
        elif a[mid] < x:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


a = [1, 2, 2, 2, 2, 2, 3]
print(classic(a, 2))
```
```text
3
```

It returned index 3, the middle copy. The first 2 is at index 1. For the first occurrence you must **keep searching to the left** after a hit. Template B does that for free (section 5).

### Trap 5: mixing up the predicate direction

When you search for the *first True* you move `hi = mid` on True and `lo = mid + 1` on False. When you search for the *last True* it is the other way round, with the rounded-up middle. Write the predicate shape
(`F F F T T T` or `T T T F F F`) on paper first.

### Trap 6: reading outside the list

`a[mid + 1]` and `a[mid - 1]` can be out of range. In Python `a[-1]` does not crash; it silently reads the **last** element. A search that reads `a[mid - 1]` with `mid = 0` will compare against the wrong value and give a wrong answer with no error.

```python
a = [4, 6, 9]
mid = 0
print(a[mid - 1])
```
```text
9
```

### Trap 7: not testing the edges

Before you trust a binary search, run it on these inputs: empty list (if allowed), one element, two elements, the first element, the last element, a value smaller than all, a value larger than all, a value between two elements, and a list full of equal values.
The tests in this module's problems do exactly that.

### A debugging helper

When a search misbehaves, print the window at the top of the loop. Seeing `lo`, `mid`, `hi` for a tiny list shows the bug in seconds.

```python
def trace_search(a, x):
    lo, hi = 0, len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        print(f"  window [{lo}, {hi})  mid = {mid}  a[mid] = {a[mid]}")
        if a[mid] < x:
            lo = mid + 1
        else:
            hi = mid
    return lo


print("answer", trace_search([10, 20, 30, 40, 50], 35))
```
```text
  window [0, 5)  mid = 2  a[mid] = 30
  window [3, 5)  mid = 4  a[mid] = 50
  window [3, 4)  mid = 3  a[mid] = 40
answer 3
```

**Predict the output 3.** With the half-open template, `a = [10, 20, 30, 40, 50]`, what does `trace_search(a, 10)` print for `lo`, `mid`, `hi` in the first line?

<details><summary>Answer</summary>

`lo = 0`, `hi = 5`, so `mid = 2` and `a[mid] = 30`. Run it:

```python
a = [10, 20, 30, 40, 50]
lo, hi = 0, len(a)
print(lo, hi, (lo + hi) // 2, a[(lo + hi) // 2])
```
```text
0 5 2 30
```
</details>


## 5. Lower bound and upper bound

Finding "the index of `x`" is a weak question when the list has duplicates or when `x` is missing. Two better questions have clean answers for **every** `x`:

- **`lower_bound(x)`**: the first index `i` with `a[i] >= x` (or `n` if there is none).
- **`upper_bound(x)`**: the first index `i` with `a[i] > x` (or `n` if there is none).

Look at `a = [1, 2, 2, 2, 5, 7, 7, 9]`.

```text
index:    0  1  2  3  4  5  6  7
value:    1  2  2  2  5  7  7  9

x = 2:  lower_bound = 1 (first 2)        upper_bound = 4 (first value > 2)
x = 3:  lower_bound = 4                  upper_bound = 4         (3 is missing: both bounds agree)
x = 0:  lower_bound = 0                  upper_bound = 0
x = 9:  lower_bound = 7                  upper_bound = 8 = n
```

Three facts to remember:

1. `lower_bound(x)` is the **number of elements smaller than `x`**.
2. `upper_bound(x)` is the **number of elements `<= x`**.
3. The elements equal to `x` occupy exactly `a[lower_bound(x) : upper_bound(x)]`. If `x` is missing, that slice is empty.

### The predicate view

For `lower_bound(x)` the question at index `i` is "is `a[i] >= x`?" For `upper_bound(x)` it is "is `a[i] > x`?" Both look like `False ... False True ... True` on a sorted list. We want the **first True**, and that is
exactly what template B finds.

```text
a        = 1  2  2  2  5  7  7  9
a[i]>=2  = F  T  T  T  T  T  T  T     -> first True at 1   (lower_bound(2))
a[i]>2   = F  F  F  F  T  T  T  T     -> first True at 4   (upper_bound(2))
```

### The code

Both functions are the same loop. Only one comparison differs.

```python
def lower_bound(a, x):
    lo, hi = 0, len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < x:          # a[mid] is too small: go right
            lo = mid + 1
        else:                   # a[mid] >= x: could be the answer, keep it
            hi = mid
    return lo


def upper_bound(a, x):
    lo, hi = 0, len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] <= x:         # a[mid] is not greater than x: go right
            lo = mid + 1
        else:
            hi = mid
    return lo


a = [1, 2, 2, 2, 5, 7, 7, 9]
for x in (0, 1, 2, 3, 7, 9, 10):
    print(x, lower_bound(a, x), upper_bound(a, x))
```
```text
0 0 0
1 0 1
2 1 4
3 4 4
7 5 7
9 7 8
10 8 8
```

### The invariant of template B

For `lower_bound`:

> Every index before `lo` holds a value `< x`. Every index from `hi` on holds a value `>= x`.

At the start `lo = 0` and `hi = n`: both parts are empty, so the sentence is true. If `a[mid] < x`, then (sorted) everything up to `mid` is `< x`, so moving `lo` to `mid + 1` keeps the first half of the sentence.
Otherwise `a[mid] >= x`, so everything from `mid` on is `>= x`, and `hi = mid` keeps the second half. At the end `lo == hi`: all before are `< x`, all from there on are `>= x`, so `lo` is the **first** index with `a[i] >= x`.
Everything follows from the invariant; you never have to think about equal elements separately. That is why this template is a good default.

### Why `hi = mid` and not `mid - 1`

Because in template B the element at `hi` is *not* in the window: it is the boundary. When `a[mid] >= x`, `mid` itself may be the first True, and we want it to remain a possible answer. Setting `hi = mid` makes `mid` the new
(excluded) boundary, which means "the answer is `mid` or earlier". If you wrote `hi = mid - 1` you would exclude `mid` from the answer.

### The relationship between the two

For integers there is a neat link:

```text
upper_bound(x) == lower_bound(x + 1)
```

because "first element `> x`" is "first element `>= x + 1`" when all values are whole numbers. This trick does **not** work for floats or strings, so prefer the direct code.

```python
a = [1, 2, 2, 2, 5, 7, 7, 9]
print(all(upper_bound(a, x) == lower_bound(a, x + 1) for x in range(-2, 12)))
```
```text
True
```

**Predict the output 4.** For `a = [10, 20, 20, 30]`, what are `lower_bound` and `upper_bound` for `x = 20` and for `x = 25`?

<details><summary>Answer</summary>

```python
a = [10, 20, 20, 30]
print(lower_bound(a, 20), upper_bound(a, 20))
print(lower_bound(a, 25), upper_bound(a, 25))
```
```text
1 3
3 3
```

For 20: block of two 20s at indices 1 and 2, so (1, 3). For 25: missing, so both are 3 (the 30 is at index 3).
</details>

## 6. First and last occurrence, count, insertion point

With the two bounds in hand, many small tasks become one-liners.

### Count of `x`

The number of copies is the length of the block:

```python
def count(a, x):
    return upper_bound(a, x) - lower_bound(a, x)


a = [1, 2, 2, 2, 5, 7, 7, 9]
print(count(a, 2), count(a, 7), count(a, 3), count(a, 9))
```
```text
3 2 0 1
```

A million queries on a sorted list of ten million numbers is now fast: `2 * 24` steps per query. (`list.count` would scan the whole list every time.)

### First and last occurrence

First: `lower_bound(x)` if the value there is `x`. Last: `upper_bound(x) - 1`.

```python
def first_last(a, x):
    i = lower_bound(a, x)
    if i == len(a) or a[i] != x:
        return -1, -1
    return i, upper_bound(a, x) - 1


a = [1, 2, 2, 2, 5, 7, 7, 9]
print(first_last(a, 2))
print(first_last(a, 7))
print(first_last(a, 5))
print(first_last(a, 3))
print(first_last(a, 100))
```
```text
(1, 3)
(5, 6)
(4, 4)
(-1, -1)
(-1, -1)
```

Note the guard `i == len(a) or a[i] != x`. Order matters: the first part protects the second from an index error, because Python evaluates `or` from the left and stops at the first True.

### The insertion point

`lower_bound(x)` is the index where `x` can be inserted to keep the list sorted, **before** the equal elements. `upper_bound(x)` is the insertion point **after** the equal elements.
For numbers it does not matter which you choose, because equal numbers look identical. For records it can: with a "stable" insertion you want the new record **after** its equals (the upper bound), so records inserted
earlier stay first.

```python
a = [10, 20, 20, 30]
for x in (5, 20, 25, 99):
    print(x, "insert before equals at", lower_bound(a, x), "| after equals at", upper_bound(a, x))
```
```text
5 insert before equals at 0 | after equals at 0
20 insert before equals at 1 | after equals at 3
25 insert before equals at 3 | after equals at 3
99 insert before equals at 4 | after equals at 4
```

### Floor and ceiling

- **Ceiling** of `x`: the smallest element `>= x` is `a[lower_bound(x)]` (if the index is `< n`).
- **Floor** of `x`: the largest element `<= x` is `a[upper_bound(x) - 1]` (if `upper_bound(x) > 0`).

```python
def floor_ceiling(a, x):
    j = upper_bound(a, x)
    i = lower_bound(a, x)
    fl = a[j - 1] if j > 0 else None
    ce = a[i] if i < len(a) else None
    return fl, ce


a = [10, 20, 20, 30, 50]
for x in (5, 10, 25, 50, 60):
    print(x, floor_ceiling(a, x))
```
```text
5 (None, 10)
10 (10, 10)
25 (20, 30)
50 (50, 50)
60 (50, None)
```

Be careful with `a[j - 1]` when `j == 0`: Python would silently give the **last** element. The explicit check `j > 0` prevents that (trap 6 of section 4).

### Number of elements in a range

How many elements lie in `[lo_v, hi_v]` (both included)? `upper_bound(hi_v) - lower_bound(lo_v)`. This is a fast range count query on sorted data.

```python
a = [1, 2, 2, 2, 5, 7, 7, 9]
print(upper_bound(a, 7) - lower_bound(a, 2))
print(upper_bound(a, 4) - lower_bound(a, 3))
```
```text
6
0
```

The first query counts the elements with values from 2 to 7: all but the 1 and the 9, so 6. The second counts values in `[3, 4]`: none.

### "Is x present?"

`i = lower_bound(a, x)` and then `i < len(a) and a[i] == x`. This is the same test as in `template_b` of section 3. It works for duplicates and missing values alike, and it is the only version you need to remember.

### Binary search on a sorted list of records

When the list holds tuples, strings or objects, binary search needs only the **comparison**. To search a list of `(name, age)` sorted by age, compare `a[mid][1]` with the target age. The searching logic does not change.

```python
people = [("Ravi", 19), ("Meena", 21), ("Asha", 21), ("Tom", 25), ("Lily", 30)]


def first_age_at_least(people, age):
    lo, hi = 0, len(people)
    while lo < hi:
        mid = (lo + hi) // 2
        if people[mid][1] < age:
            lo = mid + 1
        else:
            hi = mid
    return lo


i = first_age_at_least(people, 21)
print(i, people[i])
i = first_age_at_least(people, 22)
print(i, people[i])
print(first_age_at_least(people, 99))
```
```text
1 ('Meena', 21)
3 ('Tom', 25)
5
```

**Try it 2.** Using only `lower_bound` and `upper_bound`, count how many numbers in `[4, 8, 8, 8, 15, 16, 23, 42]` are strictly between 8 and 23 (both excluded).

<details><summary>Answer</summary>

Strictly greater than 8: starts at `upper_bound(8)`. Strictly less than 23: ends before `lower_bound(23)`.

```python
a = [4, 8, 8, 8, 15, 16, 23, 42]
print(lower_bound(a, 23) - upper_bound(a, 8))
```
```text
2
```

The numbers are 15 and 16.
</details>

## 7. The `bisect` module

Python already has these functions in the standard library, written in C and very fast. You should know them well, for real programs. In this course you also write them by hand, because the exercise is the point, and because on the
exams and in interviews you will be asked to.

| Function | Meaning | Our name |
|---|---|---|
| `bisect_left(a, x)` | first index with `a[i] >= x` | `lower_bound` |
| `bisect_right(a, x)` (also `bisect`) | first index with `a[i] > x` | `upper_bound` |
| `insort_left(a, x)` | insert `x` before equal elements | |
| `insort_right(a, x)` (also `insort`) | insert `x` after equal elements | |

```python
from bisect import bisect_left, bisect_right, insort

a = [1, 2, 2, 2, 5, 7, 7, 9]
print(bisect_left(a, 2), bisect_right(a, 2))
print(bisect_left(a, 6), bisect_right(a, 6))
insort(a, 6)
print(a)
insort(a, 2)
print(a)
```
```text
1 4
5 5
[1, 2, 2, 2, 5, 6, 7, 7, 9]
[1, 2, 2, 2, 2, 5, 6, 7, 7, 9]
```

### Check against our version

```python
from bisect import bisect_left, bisect_right
import random

rng = random.Random(1)
ok = True
for _ in range(2000):
    n = rng.randint(0, 12)
    a = sorted(rng.randint(0, 9) for _ in range(n))
    x = rng.randint(-1, 10)
    if lower_bound(a, x) != bisect_left(a, x) or upper_bound(a, x) != bisect_right(a, x):
        ok = False
print("our versions agree with bisect:", ok)
```
```text
our versions agree with bisect: True
```

This is a very good habit: **test your hand-written search against `bisect` on thousands of small random lists.** The random test finds edge-case bugs that you would never think of.

### The optional arguments: `lo`, `hi` and `key`

- `bisect_left(a, x, lo, hi)` searches only the slice `a[lo:hi]` (the answer is still a position in the whole list).
- Since Python 3.10, `key=f` applies `f` to each **list element** before comparing. The searched value `x` is *not* transformed. It must already be in "key units".

```python
from bisect import bisect_left, bisect_right

words = ["fig", "kiwi", "apple", "banana", "cherry"]      # sorted by length
print(bisect_left(words, 5, key=len))
print(bisect_right(words, 6, key=len))
print(bisect_left([10, 20, 20, 20, 30], 20, 2, 4))
```
```text
2
5
2
```

The list `words` is sorted by `len` (3, 4, 5, 6, 6). The first word with length `>= 5` is at index 2; the first word with length `> 6` would be at index 5 (past the end).

### `insort` is not magic

`insort(a, x)` finds the position in `O(log n)` and then **inserts** with `list.insert`, which shifts all later elements: `O(n)`. For a few thousand inserts that is fine; for hundreds of thousands of inserts into a big list, consider
a different structure (a heap, a balanced tree, or a "sorted container" library).

```python
from bisect import insort

a = []
for x in [5, 1, 4, 1, 3]:
    insort(a, x)
    print(a)
```
```text
[5]
[1, 5]
[1, 4, 5]
[1, 1, 4, 5]
[1, 1, 3, 4, 5]
```

### Hand-writing it with a key (a template)

```python
def bisect_left_key(a, x, key=lambda v: v):
    lo, hi = 0, len(a)
    while lo < hi:
        mid = (lo + hi) // 2
        if key(a[mid]) < x:
            lo = mid + 1
        else:
            hi = mid
    return lo


words = ["fig", "kiwi", "apple", "banana", "cherry"]
print(bisect_left_key(words, 5, key=len))
print(bisect_left_key(words, 4, key=len))
```
```text
2
1
```

### A real use: grading by thresholds

A classic use of `bisect` is turning a score into a letter without a ladder of `if` statements.

```python
from bisect import bisect_right

breakpoints = [60, 70, 80, 90]
letters = "FDCBA"


def grade(score):
    return letters[bisect_right(breakpoints, score)]


print([grade(s) for s in (59, 60, 69, 70, 85, 90, 100)])
```
```text
['F', 'D', 'D', 'C', 'B', 'A', 'A']
```

`bisect_right` is used because a score equal to a breakpoint (60) already belongs to the **next** grade.

**Predict the output 5.** What does `bisect_right([1, 3, 3, 5], 3)` return, and what does `bisect_left([1, 3, 3, 5], 3)` return?

<details><summary>Answer</summary>

```python
from bisect import bisect_left, bisect_right
print(bisect_right([1, 3, 3, 5], 3), bisect_left([1, 3, 3, 5], 3))
```
```text
3 1
```

`bisect_right` is the upper bound (3), `bisect_left` the lower bound (1).
</details>

## 8. Searching on floats, and fixed iteration counts

Binary search is not only for lists. Suppose you want the number `x` such that `x * x = 10`. You know that `x` is between 3 and 4. The condition `x * x >= 10` flips from False to True at the answer.
That works with real numbers too, but there is a big difference: **there is no "next" number**. Between 3.1 and 3.2 there are infinitely many reals. So the integer rule `lo = mid + 1` does not apply.

### Bisection on real numbers

```python
lo, hi = 3.0, 4.0
for step in range(1, 9):
    mid = (lo + hi) / 2
    if mid * mid >= 10:
        hi = mid
    else:
        lo = mid
    print(step, lo, hi)
print("estimate", (lo + hi) / 2)
print("true     ", 10 ** 0.5)
```
```text
1 3.0 3.5
2 3.0 3.25
3 3.125 3.25
4 3.125 3.1875
5 3.15625 3.1875
6 3.15625 3.171875
7 3.15625 3.1640625
8 3.16015625 3.1640625
estimate 3.162109375
true      3.1622776601683795
```

Rules for reals:

- Use `/ 2` for the midpoint, not `// 2`.
- Both updates are `lo = mid` and `hi = mid` (no `+ 1`, no `- 1`).
- The width halves each step: after `k` steps it is `width / 2^k`.

### Why not `while hi - lo > eps`?

It looks natural, and it is dangerous. Floats have a limited precision: near `10^5` the gap between two neighbouring floats is about `1.5 * 10^-11`. If you ask for `eps = 10^-15`, then
`hi - lo` can never get below the gap and the loop **never ends**.

```python
import math

for x in (1.0, 1000.0, 1e5, 1e10):
    print(x, "gap to the next float:", math.ulp(x))
```
```text
1.0 gap to the next float: 2.220446049250313e-16
1000.0 gap to the next float: 1.1368683772161603e-13
100000.0 gap to the next float: 1.4551915228366852e-11
10000000000.0 gap to the next float: 1.9073486328125e-06
```

The safest method is a **fixed number of iterations**: 100 halvings reduce any interval of width up to `10^10` to about `10^10 / 2^100 = 10^-20`, far below the float precision, and the loop always ends.

```python
def solve(c):
    """Find x >= 0 with x**3 + x == c, by 100 halvings."""
    lo, hi = 0.0, 100000.0
    for _ in range(100):
        mid = (lo + hi) / 2
        if mid ** 3 + mid >= c:
            hi = mid
        else:
            lo = mid
    return (lo + hi) / 2


for c in (0, 2, 10, 10**15):
    x = solve(c)
    print(c, f"{x:.6f}", f"check: {x ** 3 + x:.3f}")
```
```text
0 0.000000 check: 0.000
2 1.000000 check: 2.000
10 2.000000 check: 10.000
1000000000000000 99999.999997 check: 999999999999999.500
```

### How many iterations are enough?

For an interval of width `W` and a wanted accuracy `e`, you need `k` with `W / 2^k <= e`, i.e. `k >= log2(W / e)`.

```python
import math

W, e = 100000.0, 1e-6
print(math.ceil(math.log2(W / e)))
```
```text
37
```

About 37 halvings give an accuracy of `10^-6` for the interval of width `10^5`. In practice people use 60 to 100 so they never think about it.

### Printing the result

Use a format: `f"{x:.6f}"`. `print(x)` may show 17 digits, or the form `1e-05`. Judges usually accept an absolute or relative error (often `10^-6`), so print enough digits.

### Floats are an approximation: do not use `==`

A float search finds a number *close to* the answer. Never test `mid * mid == 10`; compare with `>=` or `<` as the predicate and let the interval shrink.

### Use integers when you can

If the true answer is a whole number (a speed, a capacity, a day), search **integers**, as in section 9. Integer searches are exact. If the answer needs a fraction (like `1.414...`), bisect on floats with a fixed number of steps.
A third way for "the largest `x` such that `f(x) <= c`" with whole-number `x` is to search with integers directly (section 10, square root).

**Predict the output 6.** After exactly 3 halvings of `[1.0, 2.0]` looking for `sqrt(2)` (move `hi` when `mid * mid >= 2`), what are `lo` and `hi`?

<details><summary>Answer</summary>

```python
lo, hi = 1.0, 2.0
for _ in range(3):
    mid = (lo + hi) / 2
    if mid * mid >= 2:
        hi = mid
    else:
        lo = mid
print(lo, hi)
```
```text
1.375 1.5
```

Step 1: mid 1.5 (too big, `hi = 1.5`). Step 2: mid 1.25 (too small, `lo = 1.25`). Step 3: mid 1.375 (too small, `lo = 1.375`). The width is `1 / 2^3 = 0.125`.
</details>


## 9. Binary search on the answer

Until now we searched a *list*. The big leap of this module: **you can binary search without any list**, whenever the answer is a number and a yes/no question about candidate answers flips only once.

### The story: the smallest speed

Koko has 4 piles of bananas: `[3, 6, 7, 11]`. She has `h = 8` hours. She eats at speed `k` bananas per hour (one pile at a time; a pile of 7 at speed 4 takes 2 hours, because the second hour only has 3 bananas left).
What is the smallest `k` that lets her finish in 8 hours?

Try a few speeds by hand:

```python
piles = [3, 6, 7, 11]


def hours_needed(k):
    return sum((p + k - 1) // k for p in piles)


for k in range(1, 13):
    print(k, hours_needed(k), "OK" if hours_needed(k) <= 8 else "too slow")
```
```text
1 27 too slow
2 15 too slow
3 10 too slow
4 8 OK
5 8 OK
6 6 OK
7 5 OK
8 5 OK
9 5 OK
10 5 OK
11 4 OK
12 4 OK
```

Look at the third column: `too slow` for speeds 1, 2, 3 and `OK` from 4 on. The speed that works is *monotone*: if speed 4 is enough, speed 5 is enough too (a faster Koko never needs more hours).
So the table is a `No No No Yes Yes Yes ...` sequence and the answer is the first Yes. That is exactly "find the first True", which template B solves in `log` steps. The list we search is the *virtual* list `1, 2, 3, ...` of candidate speeds. It is never built.

### The recipe

1. **Choose the answer variable** `x` (speed, capacity, day, distance...).
2. **Write the predicate** `feasible(x)`: "does `x` work?" It must be monotone: all `False` first and then all `True` (or the reverse).
3. **Find a range** `[lo, hi]` that surely contains the answer: a value that is too small (or the smallest possible) and one that surely works.
4. **Binary search** with the half-open template for the first True.
5. **Cost:** `O(log(range) * cost of feasible)`.

```python
def first_true(lo, hi, feasible):
    """Smallest x in [lo, hi] with feasible(x) True. Assumes feasible(hi) is True."""
    while lo < hi:
        mid = (lo + hi) // 2
        if feasible(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo


piles = [3, 6, 7, 11]
h = 8
print(first_true(1, max(piles), lambda k: sum((p + k - 1) // k for p in piles) <= h))
```
```text
4
```

This `first_true` is the whole technique. Everything else in the chapter is "choose `lo`, `hi`, and write `feasible`".

### Why the range matters: `hi` must be feasible

`first_true(lo, hi, f)` returns `hi` if no smaller value works. It silently returns `hi` even when `hi` itself is **not** feasible. So pick `hi` with care, and do not forget to check the "impossible" case separately (e.g. print `-1`).
For Koko, `hi = max(piles)` is safe: at that speed every pile takes one hour, and `h >= n` is guaranteed.

### Why linear search over the answer is hopeless

If the piles are as large as `10^9`, the answer can be around `10^9`. Trying every speed from 1 costs `10^9` checks of the whole list. Binary search needs about `30` checks:

```python
import math

print("range of speeds: 10^9, checks needed:", math.ceil(math.log2(10**9)))
```
```text
range of speeds: 10^9, checks needed: 30
```

### The last True version

Sometimes the predicate is `True True True False False` and you want the **last True** (the largest feasible value). Examples: "largest minimum distance", "largest `x` with `x * x <= n`".
You can flip the predicate (`not feasible`) and take the first False minus one, or use the template with a rounded-up middle:

```python
def last_true(lo, hi, feasible):
    """Largest x in [lo, hi] with feasible(x) True. Assumes feasible(lo) is True."""
    while lo < hi:
        mid = (lo + hi + 1) // 2      # round UP, because lo = mid keeps mid
        if feasible(mid):
            lo = mid
        else:
            hi = mid - 1
    return lo


print(last_true(0, 100, lambda x: x * x <= 50))
```
```text
7
```

With `mid = (lo + hi) // 2` and `lo = mid`, the loop gets stuck when `hi == lo + 1` (trap 1). Rounding up gives `mid = hi`, so `lo = hi` or `hi = hi - 1`: the window shrinks. **Whenever you write `lo = mid`, round mid up.**
Every other combination in this module uses `hi = mid` or `lo = mid + 1` with the normal rounding.

### Min of max and max of min

Two phrases signal this technique:

- "Minimise the largest ..." (largest load, largest sum, maximum time): the predicate "can we keep the maximum `<= x`?" is False then True. First True.
- "Maximise the smallest ..." (smallest distance, minimum gap): the predicate "can we keep the minimum `>= x`?" is True then False. Last True.

**Predict the output 7.** With `piles = [3, 6, 7, 11]` and `h = 8`, `first_true(1, 11, ...)` probes some speeds. Which speeds does it test, in order?

<details><summary>Answer</summary>

```python
piles = [3, 6, 7, 11]
h = 8
lo, hi = 1, 11
while lo < hi:
    mid = (lo + hi) // 2
    ok = sum((p + mid - 1) // mid for p in piles) <= h
    print("lo", lo, "hi", hi, "mid", mid, ok)
    if ok:
        hi = mid
    else:
        lo = mid + 1
print(lo)
```
```text
lo 1 hi 11 mid 6 True
lo 1 hi 6 mid 3 False
lo 4 hi 6 mid 5 True
lo 4 hi 5 mid 4 True
4
```

Four checks instead of eleven.
</details>

## 10. Classic "answer search" problems

Here are six problems you will meet again and again. Each has the same skeleton; only `feasible` changes.

### 10.1 Integer square root

`floor(sqrt(n))`: the largest `r` with `r * r <= n`. The predicate `r * r <= n` is `True ... True False ... False`: last True.
Equivalently, find the first `r` with `r * r > n` and subtract 1. For `n` up to `10^18`, a float `n ** 0.5` is **not safe**: floats have 53 bits of precision, but `10^18` needs 60.

```python
import math


def isqrt(n):
    lo, hi = 0, n + 1            # first r with r*r > n
    while lo < hi:
        mid = (lo + hi) // 2
        if mid * mid > n:
            hi = mid
        else:
            lo = mid + 1
    return lo - 1


for n in (0, 1, 2, 15, 16, 17, 10**18):
    print(n, isqrt(n), math.isqrt(n))
n = 10**18 - 1
print(int(n ** 0.5), isqrt(n))
```
```text
0 0 0
1 1 1
2 1 1
15 3 3
16 4 4
17 4 4
1000000000000000000 1000000000 1000000000
1000000000 999999999
```

The last line shows the float trap: `int((10**18 - 1) ** 0.5)` is `1000000000`, but the true floor is `999999999`.

### 10.2 Koko eating bananas

(You saw it.) `feasible(k) = sum(ceil(p / k)) <= h`; range `[1, max(piles)]`; first True.

### 10.3 Capacity to ship packages in D days

Packages with weights `w` must ship **in order**. A ship of capacity `C` carries consecutive packages each day. What is the smallest `C` so that everything ships in at most `D` days?

`feasible(C)`: count days greedily (fill a day until the next package does not fit). Range: `lo = max(w)` (the heaviest package must fit), `hi = sum(w)` (everything in one day).

```python
def days_needed(w, cap):
    days, load = 1, 0
    for x in w:
        if load + x > cap:
            days += 1
            load = 0
        load += x
    return days


def min_capacity(w, d):
    return first_true(max(w), sum(w), lambda c: days_needed(w, c) <= d)


w = [3, 2, 2, 4, 1, 4]
print(min_capacity(w, 3))
print(min_capacity([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 5))
for c in (5, 6):
    print("capacity", c, "needs", days_needed(w, c), "days")
```
```text
6
15
capacity 5 needs 4 days
capacity 6 needs 3 days
```

Why is the greedy count right? Filling each day as much as possible never hurts: any other plan that ends a day earlier can be changed to move the cut later without increasing the number of days (an "exchange argument").

### 10.4 Split array largest sum

Cut a list into `m` contiguous pieces so that the **largest piece sum** is as small as possible. This is *the same problem* as shipping: pieces are days, the largest sum is the capacity. The check is identical, `pieces(S) <= m`.

```python
def split_cost(a, m):
    return first_true(max(a), sum(a), lambda s: days_needed(a, s) <= m)


print(split_cost([7, 2, 5, 10, 8], 2))
```
```text
18
```

This shows the power of recognising structure: two stories, one code. (A dynamic programming solution for this problem takes `O(m n^2)`. Binary search on the answer takes `O(n log(sum))`.)

### 10.5 Aggressive cows (maximise the minimum)

`c` cows go into `n` stalls at given positions; maximise the smallest distance between two cows. Predicate: `can_place(d)` = "can I place `c` cows with every pair at least `d` apart?" It is `True ... True False ... False`: **last True**.
Greedy check: sort, first cow at the first stall, next cow at the first stall at least `d` away from the last cow.

```python
def can_place(stalls, c, d):
    placed, last = 1, stalls[0]
    for s in stalls:
        if s - last >= d:
            placed += 1
            last = s
    return placed >= c


def aggressive_cows(stalls, c):
    stalls = sorted(stalls)
    return last_true(1, (stalls[-1] - stalls[0]) // (c - 1), lambda d: can_place(stalls, c, d))


print(aggressive_cows([1, 2, 8, 4, 9], 3))
print(aggressive_cows([1, 2, 4, 8, 9], 2))
print(aggressive_cows([1, 2, 4, 8, 9], 5))
```
```text
3
8
1
```

The upper limit `(max - min) // (c - 1)` is the biggest distance that could possibly fit: `c` cows have `c - 1` gaps that together cannot be longer than the whole line.

### 10.6 Kth smallest in a sorted matrix

The matrix has sorted rows and sorted columns. The k-th smallest value cannot be found by index. Instead search the **value** `v`: `count_le(v)` = how many entries are `<= v`. It is non-decreasing in `v`.
The answer is the first `v` with `count_le(v) >= k`. The count uses a staircase walk from the bottom-left corner in `O(n)`.

```python
def count_le(m, v):
    n = len(m)
    r, c, cnt = n - 1, 0, 0
    while r >= 0 and c < n:
        if m[r][c] <= v:
            cnt += r + 1      # the whole column above (and including) row r
            c += 1
        else:
            r -= 1
    return cnt


def kth_smallest(m, k):
    lo, hi = m[0][0], m[-1][-1]
    return first_true(lo, hi, lambda v: count_le(m, v) >= k)


m = [[1, 5, 9], [10, 11, 13], [12, 13, 15]]
print([kth_smallest(m, k) for k in range(1, 10)])
```
```text
[1, 5, 9, 10, 11, 12, 13, 13, 15]
```

The first `v` with `count_le(v) >= k` is always a value that **exists** in the matrix: at the previous integer the count was `< k`, so `v` itself must add at least one element.
The search is over values (a range of integers), not positions. That is the "binary search on the answer" idea again.

### 10.7 Minimum days for bouquets

`bloom[i]` is the day flower `i` blooms. A bouquet needs `k` adjacent bloomed flowers. Smallest day with `m` bouquets? Predicate "at least `m` bouquets on day `d`" is monotone in `d` (more flowers bloom). Range `[min(bloom), max(bloom)]`; print `-1` first if `m * k > n`.

```python
def bouquets(bloom, k, day):
    run = count = 0
    for b in bloom:
        if b <= day:
            run += 1
            if run == k:
                count += 1
                run = 0
        else:
            run = 0
    return count


def min_days(bloom, m, k):
    if m * k > len(bloom):
        return -1
    return first_true(min(bloom), max(bloom), lambda d: bouquets(bloom, k, d) >= m)


print(min_days([1, 10, 3, 10, 2], 3, 1))
print(min_days([1, 10, 3, 10, 2], 3, 2))
print(min_days([1, 10, 3, 10, 2], 1, 2))
```
```text
3
-1
10
```

### 10.8 Machines (Factory Machines)

`n` machines, machine `i` makes one product in `k[i]` seconds. The least time to make `t` products: `feasible(T) = sum(T // k[i]) >= t`; range `[1, min(k) * t]`. The answer can reach `10^18`, so no loop over times could work, but 60 checks are enough.

```python
def factory(k, t):
    return first_true(1, min(k) * t, lambda T: sum(T // x for x in k) >= t)


print(factory([3, 2, 5], 7))
print(factory([10**9], 10**9))
```
```text
8
1000000000000000000
```

## 11. Recognising monotonicity

All of section 10 hangs on one property. Learn to test it quickly.

### The test

A predicate `ok(x)` is **monotone** if, once it flips, it never flips back. Concretely: if `ok(a)` is True and `a < b`, then `ok(b)` is True (the "increasing" kind),
or the mirror image. A quick check: *"if `x` works, does a bigger (or smaller) `x` always work too?"*

| Predicate | Monotone? | Why |
|---|---|---|
| Speed `k` finishes within `h` hours | yes (more is better) | faster never needs more time |
| Capacity `C` ships in `D` days | yes | more capacity never needs more days |
| `x * x >= n` | yes | squares grow |
| Distance `d` can be kept between `c` cows | yes (smaller is easier) | smaller gap is always possible if a bigger gap is |
| `x` is prime | **no** | `2` yes, `4` no, `5` yes |
| Sum of digits of `x` is at least 10 | **no** | `19` yes, `20` no |
| `x` is even | **no** | alternates |

### Questions to ask yourself

1. **What is the answer variable `x`, and is it a whole number?** Sometimes you can *choose* the variable: "the time", "the day", "the capacity", "the number of items taken".
2. **If `x` is feasible, what happens to `x + 1`?** If the problem asks for a minimum, `x + 1` should still be feasible. If it asks for a maximum, `x - 1` should still be feasible.
3. **Can I check one `x` fast?** The cost of one check multiplies with the number of steps. A check that costs `O(n)` and 60 steps is `60 n`, fine.
4. **What are the two ends of the range?** One end where the answer is certainly False (or `lo` itself is the minimum possible), one end where it is certainly True.

### Common shapes

| Words in the problem | Likely predicate | Answer shape |
|---|---|---|
| "minimum possible maximum" | "can we keep every group below `x`?" | first True |
| "maximum possible minimum" | "can we keep every gap at least `x`?" | last True |
| "smallest `x` such that ..." | "does `x` satisfy ...?" | first True |
| "largest `x` such that ..." | "does `x` satisfy ...?" | last True |
| "minimum time / speed / capacity" | "is `x` enough?" | first True |
| "the `k`-th smallest" | "are at least `k` values `<= x`?" | first True |

### A guard: test the monotonicity by brute force

When you are not sure, write the predicate and print it for a range of small values. If the output is `FFFFTTTT`, you are fine; if it flips twice, stop.

```python
def pattern(f, values):
    return "".join("T" if f(x) else "F" for x in values)


print(pattern(lambda x: x * x >= 50, range(1, 15)))
print(pattern(lambda x: sum(int(c) for c in str(x)) >= 10, range(1, 30)))
print(pattern(lambda x: all(x % d for d in range(2, x)) and x > 1, range(1, 20)))
```
```text
FFFFFFFTTTTTTT
FFFFFFFFFFFFFFFFFFTFFFFFFFFTT
FTTFTFTFFFTFTFFFTFT
```

The first is `FFFFFFFTTTTTTT`: monotone. The second flips several times (19 is True, 20 False), and the third is the primes: neither is monotone. Do not binary search those.

### Monotone in the data, not the index

Another important case: the list itself is not sorted, but a *derived* function is. For example, prefix sums of non-negative numbers are non-decreasing, even if the numbers are not sorted. Then "the first index where the prefix sum reaches `s`" is a binary search over indices.

```python
from itertools import accumulate

a = [4, 0, 7, 3, 0, 5]
prefix = list(accumulate(a))
print(prefix)
print(bisect_left(prefix, 11))
```
```text
[4, 4, 11, 14, 14, 19]
2
```

The prefix sums `[4, 4, 11, 14, 14, 19]` are sorted; the first index where the sum is at least 11 is 2.

**Predict the output 8.** Is the predicate "`x` is a multiple of 3 or `x >= 10`" monotone on `x = 1 .. 14`? Print its pattern.

<details><summary>Answer</summary>

```python
print(pattern(lambda x: x % 3 == 0 or x >= 10, range(1, 15)))
```
```text
FFTFFTFFTTTTTT
```

The pattern is `FFTFFTFFTTTTTT`: the True at 3, 6, 9 comes before a False at 4, 5, 7, 8. Not monotone, so binary search on it would be wrong.
</details>

## 12. Rotated sorted arrays

A sorted array is **rotated** if you cut it at some point and swap the two parts: `[2, 5, 8, 12, 16, 23]` rotated by 3 is `[12, 16, 23, 2, 5, 8]`. It is no longer sorted, yet it still has structure: **two sorted runs** with one "drop" in between.
A binary search can still halve the work: at each step **one of the two halves is sorted**.

```text
index:   0   1   2   3   4   5   6   7
value:   6   7   9  15  19   2   3   4
         |_____sorted_____| |__sorted__|
```

### 12.1 Find the minimum (distinct values)

The minimum is the element right after the drop. Compare `a[mid]` with the **last element** `a[hi]`:

- `a[mid] > a[hi]`: the drop is to the right of `mid` (the minimum is in `mid + 1 .. hi`). `lo = mid + 1`.
- `a[mid] < a[hi]`: `mid .. hi` is sorted, so the minimum is at `mid` or to its left. `hi = mid`.

The predicate "`a[i] <= a[last]`" is `False ... False True ... True`: the minimum is the **first True**. Template C, with the guaranteed answer.

```python
def find_min(a):
    lo, hi = 0, len(a) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] > a[hi]:
            lo = mid + 1
        else:
            hi = mid
    return lo


for a in ([6, 7, 9, 15, 19, 2, 3, 4], [2, 3, 4, 6, 7], [4, 2], [5], [3, 4, 5, 1, 2]):
    i = find_min(a)
    print(a, "-> index", i, "value", a[i])
```
```text
[6, 7, 9, 15, 19, 2, 3, 4] -> index 5 value 2
[2, 3, 4, 6, 7] -> index 0 value 2
[4, 2] -> index 1 value 2
[5] -> index 0 value 5
[3, 4, 5, 1, 2] -> index 3 value 1
```

### Why compare with `a[hi]` and not `a[lo]`?

Compare `[1, 2, 3, 4, 5]` (not rotated) and `[3, 4, 5, 1, 2]` (rotated). In both, `a[mid]` (the 3 and the 5) is `>= a[lo]`. The answer to "`a[mid] >= a[lo]`" is the same, but the minimum is on the
left in the first case and on the right in the second. Comparing with `a[hi]` gives different answers (3 `< 5` against 5 `> 2`), so it tells them apart.

### 12.2 Search for a value

At every step find the sorted half, then check whether the target lies in it.

- If `a[lo] <= a[mid]`, the left half `lo..mid` is sorted. If `a[lo] <= x < a[mid]` go left, otherwise go right.
- Otherwise the right half `mid..hi` is sorted. If `a[mid] < x <= a[hi]` go right, otherwise go left.

```python
def search_rotated(a, x):
    lo, hi = 0, len(a) - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        if a[mid] == x:
            return mid
        if a[lo] <= a[mid]:                    # left half is sorted
            if a[lo] <= x < a[mid]:
                hi = mid - 1
            else:
                lo = mid + 1
        else:                                  # right half is sorted
            if a[mid] < x <= a[hi]:
                lo = mid + 1
            else:
                hi = mid - 1
    return -1


a = [6, 7, 9, 15, 19, 2, 3, 4]
print([search_rotated(a, x) for x in (6, 19, 2, 4, 3, 8, 100)])
```
```text
[0, 4, 5, 7, 6, -1, -1]
```

Notice `a[lo] <= a[mid]` with **`<=`**. When the window has one or two elements, `lo == mid`, and the left "half" is a single element; it is sorted. Writing `<` would send the search into the other branch with wrong assumptions.

### Another way: find the rotation, then search a virtual array

Find the minimum index `k`. Then the array is the sorted array `a[k], a[k+1], ..., a[n-1], a[0], ..., a[k-1]`. Element `j` of this virtual sorted array is `a[(j + k) % n]`. Run an ordinary binary search on `j`.

```python
def search_rotated_2(a, x):
    n = len(a)
    k = find_min(a)
    lo, hi = 0, n - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        v = a[(mid + k) % n]
        if v == x:
            return (mid + k) % n
        elif v < x:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


print([search_rotated_2(a, x) for x in (6, 19, 2, 4, 3, 8, 100)])
```
```text
[0, 4, 5, 7, 6, -1, -1]
```

Both versions give the same answers. The second is easier to reason about, because the search loop is the plain classic one; only the indexing is "virtual".

### 12.3 Duplicates: the caveat

With equal values the comparison with `a[hi]` is sometimes **inconclusive**. Take `[3, 3, 3, 1, 3]` and `[3, 1, 3, 3, 3]`. For both, `lo = 0`, `hi = 4`, `mid = 2`, and `a[lo] = a[mid] = a[hi] = 3`.
The minimum is right of `mid` in the first array and left of it in the second. When `a[mid] == a[hi]`, you cannot decide the side.

The safe move: **drop `a[hi]`** (`hi -= 1`). It is safe because a copy of that value stays at `mid`, so the minimum value is not lost.

```python
def find_min_dups(a):
    lo, hi = 0, len(a) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] > a[hi]:
            lo = mid + 1
        elif a[mid] < a[hi]:
            hi = mid
        else:
            hi -= 1
    return a[lo]


for a in ([3, 3, 3, 1, 3], [3, 1, 3, 3, 3], [1, 1, 1, 0, 1], [2, 2, 2], [10, 1, 10, 10, 10]):
    print(a, "->", find_min_dups(a))
```
```text
[3, 3, 3, 1, 3] -> 1
[3, 1, 3, 3, 3] -> 1
[1, 1, 1, 0, 1] -> 0
[2, 2, 2] -> 2
[10, 1, 10, 10, 10] -> 1
```

The price: the worst case is `O(n)`. In `[1, 1, 1, 1, 0, 1, 1]` each step removes only one element. No algorithm can do better in general, because the lone `0` could hide in any position and every position must be examined.
In typical data (few repeats) it is still about `log n`.

### What about searching with duplicates?

The same issue: when `a[lo] == a[mid] == a[hi]` you do not know which half is sorted. The fix is `lo += 1` and `hi -= 1` (after checking that those elements are not the target). Again worst case `O(n)`.

**Predict the output 9.** What does `find_min([4, 5, 6, 7, 0, 1, 2])` return (index)?

<details><summary>Answer</summary>

```python
print(find_min([4, 5, 6, 7, 0, 1, 2]))
```
```text
4
```

The drop is between 7 and 0; the minimum 0 is at index 4.
</details>

**Try it 3.** Trace `search_rotated(a, 3)` for `a = [6, 7, 9, 15, 19, 2, 3, 4]` and print the `lo`, `mid`, `hi` of each step. How many probes?

<details><summary>Answer</summary>

```python
a = [6, 7, 9, 15, 19, 2, 3, 4]
x = 3
lo, hi = 0, len(a) - 1
while lo <= hi:
    mid = (lo + hi) // 2
    print("lo", lo, "mid", mid, "hi", hi, "a[mid]", a[mid])
    if a[mid] == x:
        break
    if a[lo] <= a[mid]:
        if a[lo] <= x < a[mid]:
            hi = mid - 1
        else:
            lo = mid + 1
    else:
        if a[mid] < x <= a[hi]:
            lo = mid + 1
        else:
            hi = mid - 1
```
```text
lo 0 mid 3 hi 7 a[mid] 15
lo 4 mid 5 hi 7 a[mid] 2
lo 6 mid 6 hi 7 a[mid] 3
```

Three probes.
</details>


## 13. Unknown size: doubling (exponential search)

Sometimes you cannot see the whole array, only ask "what is at index `i`?" and you do not know how long it is: a stream, a huge file, an infinite sorted sequence, or an API that returns a special value past the end.
Binary search needs two ends, and you only have the left one. The trick is to **find the right end by doubling**.

### The idea

Probe indices `1, 2, 4, 8, 16, ...` until you reach a value that is `>= target` (or past the end). Now you know the target, if present, lies between the last two probes, so run a normal binary search there.

```text
index probed:   1   2   4   8   16   32
value:         ... smaller ... smaller  >= target
                                       ^ stop here, search between 16 and 32
```

### Why it is fast

Suppose the target sits at position `p`. Doubling stops after `log2(p)` steps, because `2^k >= p` when `k = ceil(log2 p)`. The window `[2^(k-1), 2^k]` has about `p` elements, so the binary search needs about `log2(p)` more steps.
Total: `2 log2(p)` probes. It does not depend on the (unknown) length `n`. This is called **exponential search** or **galloping**.

### A runnable model

We will pretend the array is a function `f(i)` that is increasing and always defined (an "infinite" sequence), and look for the first `i` with `f(i) >= target`.

```python
def f(i):
    return i * i + 3 * i


def first_index_at_least(target):
    probes = 0
    bound = 1
    while f(bound) < target:
        probes += 1
        bound *= 2
    lo, hi = bound // 2, bound
    while lo < hi:
        mid = (lo + hi) // 2
        probes += 1
        if f(mid) >= target:
            hi = mid
        else:
            lo = mid + 1
    return lo, probes


for target in (1, 100, 10**6, 10**18, 10**30):
    i, p = first_index_at_least(target)
    print(f"target 10^{len(str(target)) - 1:<2} first index {i:>14} probes {p}")
```
```text
target 10^0  first index              1 probes 1
target 10^2  first index              9 probes 8
target 10^6  first index            999 probes 19
target 10^18 first index      999999999 probes 59
target 10^30 first index 999999999999999 probes 99
```

Even for a target of `10^30` the search needs about 100 probes: the answer `i` is near `10^15`, so `2 * log2(10^15) = 100`. A linear walk would need `10^15` steps.

### An array that ends: the sentinel trick

A common API (LeetCode's "search in a sorted array of unknown size") returns a huge number for indices past the end. That number is larger than any target, so the doubling loop stops when it sees it, and the binary search treats those indices as "too large".

```python
class Reader:
    """A sorted list that pretends not to know its own length."""

    def __init__(self, data):
        self._data = data
        self.probes = 0

    def get(self, i):
        self.probes += 1
        return self._data[i] if i < len(self._data) else 2**31 - 1


def search_unknown(reader, target):
    hi = 1
    while reader.get(hi) < target:
        hi *= 2
    lo = hi // 2
    while lo <= hi:
        mid = (lo + hi) // 2
        v = reader.get(mid)
        if v == target:
            return mid
        elif v < target:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


data = list(range(0, 3000, 3))              # 1000 elements, hidden from the search
r = Reader(data)
print(search_unknown(r, 999), "probes:", r.probes)
r = Reader(data)
print(search_unknown(r, 1000), "probes:", r.probes)
r = Reader(data)
print(search_unknown(r, 99999), "probes:", r.probes)
```
```text
333 probes: 17
-1 probes: 18
-1 probes: 20
```

### Traps

- **Doubling from 0:** `0 * 2 = 0` forever. Start at 1.
- **Forgetting that the first probe may already pass the end:** the sentinel must stop the loop, not crash it.
- **Using a fixed big `hi`** like `10^9`: it works, but costs 30 probes even for a tiny array, and many judges limit the probe count.
- **When growth is expensive,** a factor of 2 is the best compromise: at most twice the optimal number of probes. Larger factors make the second phase longer.

### Where this pattern shows up

Besides sorted arrays of unknown size: finding the right range for "binary search on the answer" when you have no obvious upper bound (double `hi` until `feasible(hi)` is True); and `galloping` in the merge step of Python's own sort.
If you do not know how large the answer can be, doubling gives a safe `hi` in `log` steps.

```python
def smallest_power_of_two_square_above(n):
    hi = 1
    while hi * hi < n:
        hi *= 2
    return hi


print(smallest_power_of_two_square_above(10**18))
```
```text
1073741824
```

## 14. Peak elements and mountain arrays

A **mountain array** rises strictly to a peak and then falls strictly: `[1, 3, 8, 12, 9, 5, 2]`. It is not sorted, but the *slope* is monotone: the predicate "`a[i] > a[i + 1]`" (is the next step downhill?) reads `False False False True True True`.
The peak is the **first True**.

```text
index:        0   1   2   3   4   5   6
value:        1   3   8  12   9   5   2
a[i] > a[i+1]: F   F   F   T   T   T   (index 6 has no right neighbour)
```

### The code

Use template C: the answer always exists, so the loop stops at one element.

```python
def peak_index(a):
    lo, hi = 0, len(a) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < a[mid + 1]:      # still climbing: the peak is to the right
            lo = mid + 1
        else:                        # going down (or at the top): the peak is mid or to the left
            hi = mid
    return lo


a = [1, 3, 8, 12, 9, 5, 2]
print(peak_index(a), a[peak_index(a)])
print(peak_index([0, 10, 5, 2]))
print(peak_index([3, 5, 3, 2, 0]))
```
```text
3 12
1
1
```

`mid + 1` is safe: the loop runs only when `mid < hi`, so `mid + 1 <= hi <= n - 1`. And `hi = mid` (not `mid - 1`) because `mid` may be the peak itself.

### Any peak in an array that is not a mountain

The classic "find a peak element" problem gives an array where neighbours are different, and a **peak** is an element bigger than both neighbours (the ends count as `-infinity` outside). There may be several peaks, and you must return **any** of them.
The same loop works! If `a[mid] < a[mid + 1]`, walking right must climb at least until... a peak (either the values keep rising to the end, where the last element is a peak, or they turn down at some point, creating a peak). So there is a peak on the right. Otherwise there is one at `mid` or on the left.

```python
def find_any_peak(a):
    lo, hi = 0, len(a) - 1
    while lo < hi:
        mid = (lo + hi) // 2
        if a[mid] < a[mid + 1]:
            lo = mid + 1
        else:
            hi = mid
    return lo


a = [1, 2, 1, 3, 5, 6, 4]               # peaks at index 1 (value 2) and 5 (value 6)
i = find_any_peak(a)
print(i, a[i])
neighbours_ok = (i == 0 or a[i - 1] < a[i]) and (i == len(a) - 1 or a[i + 1] < a[i])
print("is a peak:", neighbours_ok)
```
```text
5 6
is a peak: True
```

The invariant here is not "the peak is the only candidate", but "**a peak exists in `[lo, hi]`**". Each step keeps a half in which a peak is guaranteed. This is a different kind of reasoning from "look for a number", and that is fine: binary search is about *keeping a promise* about the window.

### Mountains with duplicates or plateaus

If equal neighbours are allowed, a plateau can hide the slope direction (`[1, 2, 2, 2, 1]`), and, like in the rotated case, the worst case becomes `O(n)`. This module's peak problems have strict slopes.

### Bitonic search

To find a value in a mountain: find the peak, then binary search the rising part (ascending) and the falling part (descending, so reverse the comparison). Three binary searches, total `O(log n)`.

```python
def search_mountain(a, x):
    p = peak_index(a)
    lo, hi = 0, p
    while lo <= hi:                          # ascending part
        mid = (lo + hi) // 2
        if a[mid] == x:
            return mid
        elif a[mid] < x:
            lo = mid + 1
        else:
            hi = mid - 1
    lo, hi = p + 1, len(a) - 1
    while lo <= hi:                          # descending part: comparison reversed
        mid = (lo + hi) // 2
        if a[mid] == x:
            return mid
        elif a[mid] > x:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1


a = [1, 3, 8, 12, 9, 5, 2]
print([search_mountain(a, x) for x in (1, 12, 9, 2, 4, 100)])
```
```text
[0, 3, 4, 6, -1, -1]
```

**Predict the output 10.** For `a = [2, 4, 7, 6, 5, 1]`, what is `peak_index(a)`?

<details><summary>Answer</summary>

```python
print(peak_index([2, 4, 7, 6, 5, 1]))
```
```text
2
```

The peak value 7 is at index 2.
</details>

## 15. Searching a 2D matrix

### Case 1: the matrix is one long sorted list

If each row is sorted and every row starts after the previous one ended, then reading the rows in order gives one sorted list of `R * C` numbers. You do not need to build that list. Use the **virtual index**:

```text
virtual index i  ->  row = i // C,  col = i % C
```

where `C` is the number of **columns**. Then run a classic search on `i` in `[0, R*C - 1]`.

```python
def search_matrix(m, x):
    R, C = len(m), len(m[0])
    lo, hi = 0, R * C - 1
    while lo <= hi:
        mid = (lo + hi) // 2
        v = m[mid // C][mid % C]
        if v == x:
            return mid // C, mid % C
        elif v < x:
            lo = mid + 1
        else:
            hi = mid - 1
    return -1, -1


m = [[1, 3, 5, 7],
     [10, 11, 16, 20],
     [23, 30, 34, 60]]
print([search_matrix(m, x) for x in (3, 13, 60, 1, 23)])
```
```text
[(0, 1), (-1, -1), (2, 3), (0, 0), (2, 0)]
```

A common slip is to divide by `R` instead of `C`. Check with a non-square matrix (3 rows, 4 columns): `i = 5` is row `5 // 4 = 1`, column `5 % 4 = 1`, value 11.

### Case 2: sorted rows and sorted columns (but not one long list)

Here a row may start with a value smaller than the end of the previous row. Binary search on the index fails. Two good methods:

- **Staircase walk** from the top-right corner: if the value is too big, go left; if too small, go down. At most `R + C` steps. It is not a binary search, but it is the right tool.
- For the **k-th smallest**, binary search on the *value* and count with the staircase walk (section 10.6).

```python
def staircase(m, x):
    r, c = 0, len(m[0]) - 1
    while r < len(m) and c >= 0:
        if m[r][c] == x:
            return r, c
        elif m[r][c] > x:
            c -= 1
        else:
            r += 1
    return -1, -1


m = [[1, 4, 7, 11],
     [2, 5, 8, 12],
     [3, 6, 9, 16],
     [10, 13, 14, 17]]
print([staircase(m, x) for x in (5, 16, 15, 1, 17)])
```
```text
[(1, 1), (2, 3), (-1, -1), (0, 0), (3, 3)]
```

### Two searches instead of one

Alternative for case 1: first binary search the **row** (the last row whose first element is `<= x`), then binary search inside it. It is two small loops with the same complexity. The virtual index is shorter to write.

**Try it 4.** In a 3 x 4 matrix, which `(row, col)` has virtual index 10?

<details><summary>Answer</summary>

```python
print(10 // 4, 10 % 4)
```
```text
2 2
```

Row 2, column 2. (Rows hold 4 numbers: indices 8 to 11 are row 2, and 10 is the third of them.)
</details>

## 16. Binary search with a custom predicate function

The most flexible form separates **what to test** from **how to search**. You write a function `ok(i)` that returns True or False, and the search finds the boundary. This is what `first_true` in section 9 does.

### Example: first bad version

A product has versions `1..n`. Version `B` and every later one is bad. You may call `is_bad(v)`. Find `B` with few calls.

```python
calls = []


def is_bad_factory(B):
    def is_bad(v):
        calls.append(v)
        return v >= B
    return is_bad


def first_bad(n, is_bad):
    lo, hi = 1, n
    while lo < hi:
        mid = (lo + hi) // 2
        if is_bad(mid):
            hi = mid
        else:
            lo = mid + 1
    return lo


is_bad = is_bad_factory(137)
print(first_bad(1000, is_bad))
print(calls)
print(len(calls), "calls for 1000 versions")
```
```text
137
[500, 250, 125, 188, 157, 141, 133, 137, 135, 136]
10 calls for 1000 versions
```

Note that the search **never asks about the same version twice**, and when `lo == hi` it stops without a final confirmation call.

### Interactive programs and `flush`

Some contest problems are *interactive*: your program talks to a judge by printing questions and reading answers. In that setting the judge hides the data and counts your questions.
The rules are the same as above, with two practical points:

- **Flush after every question:** `print("? 5", flush=True)`. Without `flush=True` Python may keep the text in a buffer, the judge never sees it, and both programs wait forever.
- **Print nothing else** while the conversation runs; debug text confuses the judge. Use `sys.stderr` for debugging.

A program for first bad version reads `n`, then loops: print `? mid`, read the answer, update. Several problems of this module use exactly this protocol so that **the number of questions is checked**, which proves you really halve the range.

```python
import sys

n = 5
B = 4                                  # hidden from the "student" code below


def ask(v):
    # In a real interactive problem you would do: print("?", v, flush=True); return int(input())
    print("?", v)
    return 1 if v >= B else 0


lo, hi = 1, n
while lo < hi:
    mid = (lo + hi) // 2
    if ask(mid) == 1:
        hi = mid
    else:
        lo = mid + 1
print("!", lo)
```
```text
? 3
? 4
! 4
```

### A predicate can hide a whole algorithm

`feasible(x)` can be as complex as you like: a greedy scan (shipping), a counting walk (matrix), a simulation, even another binary search (counting elements `<= x` in several sorted arrays).
The outer search only needs one fact: the predicate is monotone. Keep the two parts separate, test `feasible` alone on small cases with a brute force, and the search part is the same few lines every time.

### Binary search over several sorted arrays: k-th of two arrays

Given two sorted arrays and `k`, find the k-th smallest of the union. Binary search on the **value** with two counts:

```python
def kth_two_arrays(a, b, k):
    lo, hi = min(a[0], b[0]), max(a[-1], b[-1])
    return first_true(lo, hi, lambda v: bisect_right(a, v) + bisect_right(b, v) >= k)


print([kth_two_arrays([1, 3, 5], [2, 4, 6], k) for k in range(1, 7)])
print(kth_two_arrays([1, 1, 1], [1, 1], 4))
```
```text
[1, 2, 3, 4, 5, 6]
1
```

When the arrays are huge and hidden, as in the challenge problem, binary search on the **partition** (how many elements of the `k` smallest come from `a`) uses far fewer probes: `O(log min(n, m))` instead of `O(log(range) * log n)`.

## 17. Decision guide

When you meet a new problem, walk through these questions.

1. **Is there a sorted (or monotone-valued) sequence?** Search for a value, a bound, an insertion point: sections 2 to 7.
   - Need *any* position of `x`? Template A.
   - Need the first or last, or the position for a missing `x`, or a count? Template B with a lower or upper bound.
2. **Is the answer a number whose "is `x` enough?" question flips once?** Binary search on the answer: sections 9 and 10. Write `feasible(x)`; check it is monotone; choose `lo` and `hi`.
   - "Smallest `x` such that ok(x)": first True.
   - "Largest `x` such that ok(x)": last True (round the middle up when you write `lo = mid`).
3. **Is the sequence sorted but rotated, or a mountain?** Find which half is "normal": sections 12 and 14.
4. **Is the length unknown?** Double to find `hi`: section 13.
5. **Is the answer a real number?** Fixed number of halvings, `lo = mid`, `hi = mid`: section 8.
6. **Is it a matrix?** Whole matrix sorted as one list: virtual index. Rows and columns sorted separately: staircase, or search the value and count with a staircase.
7. **None of the above:** maybe a hash set, two pointers, or sorting is the better tool. Binary search is not magic: it needs a monotone structure.

### Cost summary

| Task | Time |
|---|---|
| Find, lower bound, upper bound in a sorted list | `O(log n)` per query |
| Binary search on the answer with check cost `C` and range `R` | `O(C log R)` |
| Rotated array (distinct) | `O(log n)` |
| Rotated array (duplicates) | `O(n)` worst, `O(log n)` typical |
| Unknown size, target at position `p` | `O(log p)` |
| Insert into a sorted list | `O(log n)` to find, `O(n)` to shift |

### Which template for which job

| Job | Template | Final result |
|---|---|---|
| Is `x` in the list? Where? | A (closed, `<=`) | the index or -1 |
| First index with `a[i] >= x` | B (half-open) | `lo` |
| First index with `a[i] > x` | B | `lo` |
| Last index with `a[i] <= x` | B, then `lo - 1` | `lo - 1` |
| First True of a predicate | B | `lo` |
| Last True of a predicate | B flipped, or round-up mid | `lo` |
| An answer is guaranteed (min of rotated, peak) | C (shrink) | `lo` |

## 18. Common traps, collected

1. **Unsorted input.** The #1 cause of "my binary search is wrong". Sort first, or check that the monotone property really holds.
2. **Infinite loop** with `lo = mid` and a rounded-down `mid`. Check that every branch shrinks the window.
3. **`<=` against `<`** in the loop condition: closed window uses `<=`, half-open and shrink use `<`.
4. **Wrong initial `hi`**: `n` for half-open, `n - 1` for closed. `hi = n - 1` with half-open loses the answer `n`.
5. **Returning the wrong thing:** index against value; first True against last True; `lo` against `lo - 1`.
6. **Out of range reads**: `a[mid + 1]`, `a[lo]` after the loop (when `lo == n`), and the silent negative index `a[-1]`.
7. **Duplicates:** a classic search returns an arbitrary copy. Use the bounds for the first or last copy.
8. **A non-monotone predicate.** Test it with the pattern helper. Binary search on a predicate that flips twice returns garbage without any error.
9. **A bad range for the answer search:** `lo` too big (skipping the answer) or `hi` not feasible (returned silently). Include the extremes in your tests.
10. **Integer against float:** `//` for ints, `/` for floats; `+ 1` only for integers; fixed iteration count for floats.
11. **Overflow:** not in Python. (In C++ or Java, `lo + hi` and products like `mid * mid` can overflow; use `long long` or `lo + (hi - lo) / 2`.)
12. **Forgetting to flush** in interactive problems.
13. **Costly check inside a loop of queries:** if the check is `O(n)` and there are `q` queries, the total is `q * n * log(R)`. Think about whether the check can be made faster (prefix sums, sorting once).
14. **Searching a list that changes:** after inserts and deletes the list must remain sorted (use `insort` or your own insertion).
15. **Testing only the happy path.** Always run the edge list: empty, one element, two elements, ends, outside, duplicates.

### A small test harness you can reuse

The best protection is a **brute force check**: compare your search with a slow, obviously correct version on thousands of tiny random cases.

```python
import random
from bisect import bisect_left


def brute_lower(a, x):
    for i, v in enumerate(a):
        if v >= x:
            return i
    return len(a)


rng = random.Random(0)
bad = 0
for _ in range(5000):
    a = sorted(rng.randint(0, 6) for _ in range(rng.randint(0, 8)))
    x = rng.randint(-1, 7)
    if lower_bound(a, x) != brute_lower(a, x):
        bad += 1
print("mismatches:", bad)
```
```text
mismatches: 0
```

Zero mismatches on 5000 tiny random lists: a strong sign that the loop is right, including the edges (empty list, all equal, `x` outside the range).

## 19. Summary

- Binary search halves the candidates with one comparison. It needs **order**, or more generally a **monotone predicate**. Cost: `O(log n)`, about 20 steps for a million and 60 for `10^18`.
- State the **loop invariant** before writing the loop. For the closed window: "if the target exists, it is in `[lo, hi]`". For the half-open window: "everything before `lo` is False, everything from `hi` on is True".
- Choose **one template**. Closed `[lo, hi]` with `<=` and `mid +- 1` to stop at a hit; half-open `[lo, hi)` with `<`, `lo = mid + 1`, `hi = mid` for "first True"; shrink for guaranteed answers.
- Every branch must **shrink the window**. If you write `lo = mid`, round the middle up.
- **Lower bound** = first `a[i] >= x` (count of smaller elements). **Upper bound** = first `a[i] > x` (count of elements `<= x`). First, last, count, insertion point, floor and ceiling all come from these two. `bisect_left` and `bisect_right` are the library versions; `key=` needs Python 3.10.
- **Binary search on the answer:** choose the answer variable, write a monotone `feasible(x)`, bound the range, search for the first or last True. Minimise-the-maximum is first True; maximise-the-minimum is last True.
- **Rotated arrays:** one half is always sorted. Compare `a[mid]` with `a[hi]` for the minimum. Duplicates force `hi -= 1` and `O(n)` worst case.
- **Unknown size:** double until you pass the target, then search the last interval.
- **Peaks:** compare `a[mid]` with `a[mid + 1]`; keep the side where a peak must exist.
- **Floats:** fixed number of halvings, `lo = mid`, `hi = mid`.
- Test with edge cases and against `bisect` or a brute force.

### Learning outcomes checklist

Tick each item only if you could do it on paper without looking at the chapter.

- [ ] I can explain why binary search needs about `log2(n)` steps and why the data must be sorted (or monotone).
- [ ] I can write the closed template and state its loop invariant and the three duties of an invariant.
- [ ] I can write the half-open template and say what `lo` means when the loop ends.
- [ ] I know why `lo = mid` needs a rounded-up `mid`, and can spot an infinite loop by checking that each branch shrinks the window.
- [ ] I can write `lower_bound` and `upper_bound` and use them for first and last occurrence, count, insertion point, floor and ceiling.
- [ ] I can use `bisect_left`, `bisect_right`, `insort`, and `key=`, and I know their cost.
- [ ] I can bisect on real numbers with a fixed iteration count.
- [ ] I can recognise a monotone predicate and write `feasible(x)` for shipping, bananas, cows and similar problems.
- [ ] I choose the right range for the answer and know when the answer is a first True or a last True.
- [ ] I can search a rotated array, find its minimum, and explain the duplicate caveat.
- [ ] I can search an array of unknown size by doubling.
- [ ] I can find a peak, and search a matrix with a virtual index.

### Mapping to the problems

| Section | Problems |
|---|---|
| 1. Why halving works | p010 (explain: why halving is so fast) |
| 2. Classic search and invariant | p001, p002 (trace), p003 (trace: closed against half-open) |
| 3. Templates | p003, p034 (explain: three templates) |
| 4. Off-by-one traps | p030 (fix a broken lower bound), p035 (trace: a loop that never ends) |
| 5. Lower and upper bound | p004, p005 (trace), p006 |
| 6. First, last, count, insertion point | p007, p008, p011, p037 (build a sorted multiset) |
| 7. The `bisect` module | p009 (trace), p023 (time-based store) |
| 8. Floats | p038, p039 (trace) |
| 9-10. Binary search on the answer | p012, p013, p016, p017, p018 (trace), p019, p020, p026, p027, p031 |
| 11. Monotonicity | p025 (explain) |
| 12. Rotated arrays | p014, p015, p024 (trace), p028, p040 (explain) |
| 13. Unknown size | p029, p033 (trace) |
| 14. Peaks | p022, p032 (trace) |
| 15. Matrix | p021 |
| 16. Custom predicates | p013, p036 (kth of two sorted arrays) |

The assessment problems: **trace** p002, **fix** p030, **explain** p034, **build** p037.

### Further reading

- Jon Bentley, *Programming Pearls*, column 4 ("Writing Correct Programs"): the classic binary search derived with an invariant, and the story of how few programmers get it right.
- Joshua Bloch, "Nearly All Binary Searches and Mergesorts are Broken" (Google Research blog, 2006): the overflow bug in `(lo + hi) / 2`.
- The Python documentation of the `bisect` module, including the "Searching Sorted Lists" recipes.
- Knuth, *The Art of Computer Programming*, volume 3, section 6.2.1 ("Searching an ordered table").
- The "binary search" tutorials on the usaco.guide and cp-algorithms.com sites: many examples of search on the answer.
- Practice: the LeetCode, CSES and Codeforces problems in this module's `external.toml`, in the order of the chapter.

Next module: **dsa.07 Recursion and backtracking**.
