# dsa.05 Sorting

## 1. Why sorting matters

Almost every program that works with data sorts it at some point. Phone books, leaderboards, search results, bank statements, the "Sort by price"
button on a shop: all of them sort. But sorting matters in this course for a deeper reason. **Sorting is the cheapest way to turn a messy problem into an easy one.**

Once data is in order, a lot of questions become a single walk from left to right:

- Are there duplicates? Equal values are now **neighbours**.
- What is the smallest gap between two numbers? The closest pair is now a pair of neighbours.
- Which meetings overlap? Meetings sorted by start can only clash with the one just before.
- What is the median? It is the middle element.
- Does a pair add up to a target? Two pointers walk in from both ends (you saw this in dsa.03).

Sorting costs `O(n log n)`. The walk afterwards costs `O(n)`. So "sort, then walk" is `O(n log n)` in total, and that beats the `O(n^2)` of comparing every pair.
This is called the **sort-first trick**, and by the end of this module you will have used it many times, especially on intervals.

### A first example: duplicates

Without sorting, finding whether any value occurs twice means comparing every pair:

```python
def has_duplicate_slow(a):
    for i in range(len(a)):
        for j in range(i + 1, len(a)):
            if a[i] == a[j]:
                return True
    return False


print(has_duplicate_slow([4, 9, 2, 7, 9]))
print(has_duplicate_slow([4, 9, 2, 7, 1]))
```
```text
True
False
```

For 200,000 numbers that is about `2 * 10^10` comparisons, far too slow. Now sort first:

```python
def has_duplicate_fast(a):
    b = sorted(a)
    for i in range(1, len(b)):
        if b[i] == b[i - 1]:
            return True
    return False


print(has_duplicate_fast([4, 9, 2, 7, 9]))
print(has_duplicate_fast([4, 9, 2, 7, 1]))
```
```text
True
False
```

After `sorted`, the two 9s sit next to each other, so one pass over neighbours is enough. (In dsa.04 you did this with a set in `O(n)`. Both ideas are good tools: the set needs hashing,
the sort needs only an order, and the sort also gives you the *sorted data* for free.)

### The learning outcomes of this module

1. **Implement merge sort and quick sort from memory.** You will write both, trace them by hand, and know where each one is slow.
2. **Solve interval problems by sorting first.** Merge intervals, insert an interval, meeting rooms, arrows and balloons all follow the same pattern.

Along the way you will meet the simple sorts (bubble, selection, insertion), the "clever" ones (heap sort), and the sorts that do not compare at all (counting and radix sort).

### Why "n log n"?

You will see `O(n log n)` again and again. Here is a rough picture of where it comes from. Halve a list of `n` items over and over: you reach single items after `log2(n)` halvings
(for `n = 1,000,000` that is only about 20). If every level of halving costs `n` work in total, the whole job costs `n * log2(n)`. For a million items:

```python
import math

n = 1_000_000
print("n * n       =", n * n)
print("n * log2(n) =", round(n * math.log2(n)))
print("ratio       =", round(n * n / (n * math.log2(n))))
```
```text
n * n       = 1000000000000
n * log2(n) = 19931569
ratio       = 50172
```

So an `O(n log n)` sort is about 50,000 times less work than an `O(n^2)` sort on a million items. That is the difference between a fraction of a second and many hours.

### The lower bound: why not faster?

Can a comparison-based sort be faster than `n log n`? No, and there is a short argument. A list of `n` different values can be in `n!` (n factorial) different orders. A correct sort must
produce the right result for every one of them. Each comparison ("is `a < b`?") has only two answers, so after `k` comparisons the algorithm can tell apart at most `2^k` situations.
To separate `n!` situations you need `2^k >= n!`, so `k >= log2(n!)`, which grows like `n log2 n`.

```python
import math

for n in (4, 8, 16, 100):
    needed = math.ceil(math.log2(math.factorial(n)))
    print(n, "items need at least", needed, "comparisons; n*log2(n) =", round(n * math.log2(n)))
```
```text
4 items need at least 5 comparisons; n*log2(n) = 8
8 items need at least 16 comparisons; n*log2(n) = 24
16 items need at least 45 comparisons; n*log2(n) = 64
100 items need at least 525 comparisons; n*log2(n) = 664
```

For 4 items there are 24 orders, and 4 comparisons give only 16 answers, so you need at least 5. The numbers show that `log2(n!)` and `n log2 n` stay in the same neighbourhood.
This bound is only about sorts that **compare**. Counting sort and radix sort (sections 12 and 13) do something else, and can run in `O(n)` when the keys are small integers.

**Predict the output 1.** How many comparisons are needed at least to sort 3 different values? Compute `ceil(log2(3!))`.

<details><summary>Answer</summary>

`3! = 6` orders. `2^2 = 4 < 6 <= 8 = 2^3`, so at least 3 comparisons. (You can check this by running `math.ceil(math.log2(math.factorial(3)))`, which gives `3`.)
</details>

## 2. Sorting in Python: `sorted`, `list.sort`, `key` and `reverse`

Before you write any sort by hand, know the tool you will use in real programs. Python has two ways to sort:

- `sorted(iterable)` returns a **new list** and leaves the original alone. It accepts any iterable (list, tuple, string, dict keys, a set).
- `list.sort()` sorts a list **in place** and returns `None`.

```python
a = [5, 2, 9, 1]
b = sorted(a)
print(a)
print(b)
r = a.sort()
print(r)
print(a)
print(sorted("banana"))
print(sorted({3: "c", 1: "a", 2: "b"}))
print(sorted((3, 1, 2)))
```
```text
[5, 2, 9, 1]
[1, 2, 5, 9]
None
[1, 2, 5, 9]
['a', 'a', 'a', 'b', 'n', 'n']
[1, 2, 3]
[1, 2, 3]
```

The classic mistake is `a = a.sort()`: `sort` returns `None`, so `a` becomes `None`. Python does this on purpose: a method that changes an object returns `None`, so that you do not confuse it with a copy.

### Descending order and `reverse`

```python
nums = [3, 1, 4, 1, 5, 9, 2, 6]
print(sorted(nums))
print(sorted(nums, reverse=True))
print(nums[::-1])
```
```text
[1, 1, 2, 3, 4, 5, 6, 9]
[9, 6, 5, 4, 3, 2, 1, 1]
[6, 2, 9, 5, 1, 4, 1, 3]
```

`nums[::-1]` is **not** a sort. It only reverses the existing order. Use `reverse=True`.

### The `key` function

`key=` is a function that Python calls **once per element** to get a value to compare. The elements themselves are not changed; only the order is.

```python
words = ["banana", "kiwi", "fig", "cherry", "apple"]
print(sorted(words))
print(sorted(words, key=len))
print(sorted(words, key=lambda w: w[-1]))
print(sorted(words, key=str.upper))
print(sorted([-3, 2, -1, 4], key=abs))
```
```text
['apple', 'banana', 'cherry', 'fig', 'kiwi']
['fig', 'kiwi', 'apple', 'banana', 'cherry']
['banana', 'apple', 'fig', 'kiwi', 'cherry']
['apple', 'banana', 'cherry', 'fig', 'kiwi']
[-1, 2, -3, 4]
```

Read `key=len` as "compare the words by their length". A **key tuple** sorts by several things at once: Python compares tuples element by element, looking at the second element only when the first ones are equal.

```python
students = [("zoe", 90), ("ann", 85), ("bob", 90), ("cy", 70)]
print(sorted(students, key=lambda s: (-s[1], s[0])))
```
```text
[('bob', 90), ('zoe', 90), ('ann', 85), ('cy', 70)]
```

The minus sign on the score turns "highest first" into "smallest first", and the name breaks ties alphabetically. (The minus trick works for numbers only. Section 15 shows the tools for strings.)

### Stability

Python's sort is **stable**: elements whose keys are equal keep the order they had in the input. Check it:

```python
people = [("ann", 30), ("bob", 25), ("cy", 30), ("dee", 25)]
print(sorted(people, key=lambda p: p[1]))
```
```text
[('bob', 25), ('dee', 25), ('ann', 30), ('cy', 30)]
```

`bob` came before `dee` in the input and both are 25, so `bob` stays first. The same holds for `ann` and `cy`. Stability is invisible for plain numbers (two 5s look the same) but it matters for records.
Section 14 explains why it is useful and how to build multi-key sorts from it.

### `reverse=True` keeps ties in input order

A common surprise: `reverse=True` does **not** reverse the tie order. Python sorts so that the result equals "sort descending, equal elements in original order".

```python
people = [("ann", 30), ("bob", 25), ("cy", 30), ("dee", 25)]
print(sorted(people, key=lambda p: p[1], reverse=True))
print(sorted(people, key=lambda p: p[1])[::-1])
```
```text
[('ann', 30), ('cy', 30), ('bob', 25), ('dee', 25)]
[('cy', 30), ('ann', 30), ('dee', 25), ('bob', 25)]
```

The first line keeps `ann` before `cy`. The second line reverses everything, ties included. They differ, and only the first is a stable descending sort.

### Timsort in one paragraph

Python's sort is called **Timsort**. It looks for already ordered stretches (**runs**) in the data, extends short runs with insertion sort, and merges runs like merge sort. It is stable, `O(n log n)` in the worst case,
and `O(n)` when the data is already sorted or nearly so. You never have to implement it, but you will implement the ideas it is built from: insertion sort (section 6) and merging (section 8).

```python
import random

def count_with_key(n, data):
    calls = [0]
    def key(x):
        calls[0] += 1
        return x
    sorted(data, key=key)
    return calls[0]

rng = random.Random(1)
data = [rng.randint(0, 1000) for _ in range(1000)]
print("key calls for 1000 items:", count_with_key(1000, data))
```
```text
key calls for 1000 items: 1000
```

The key function is called exactly once per element (1000 times), not once per comparison. That is why `key=` is fast, and why it is better than a comparator (section 15).

### What does sorting cost?

`sorted` and `.sort()` cost `O(n log n)` time. `sorted` needs `O(n)` extra memory for the new list; `.sort()` needs `O(n)` in the worst case internally (Timsort's merge buffer) but never builds a second copy of the list.

**Try it 1.** What does this print?

```python
a = [3, 1, 2]
b = a.sort()
print(b, a)
c = sorted(a, reverse=True)
print(c, a)
```

<details><summary>Answer</summary>

```python
a = [3, 1, 2]
b = a.sort()
print(b, a)
c = sorted(a, reverse=True)
print(c, a)
```
```text
None [1, 2, 3]
[3, 2, 1] [1, 2, 3]
```

`a.sort()` sorts in place and returns `None`. `sorted(a, reverse=True)` returns a new list and leaves `a` (already sorted ascending) untouched.
</details>

**Try it 2.** Sort these words by length, longest first, and among equal lengths keep the input order. Which call does it?

```python
words = ["pear", "fig", "apple", "kiwi"]
```

<details><summary>Answer</summary>

```python
words = ["pear", "fig", "apple", "kiwi"]
print(sorted(words, key=len, reverse=True))
```
```text
['apple', 'pear', 'kiwi', 'fig']
```

`reverse=True` with a stable sort keeps `pear` before `kiwi` (equal length, input order). A key of `-len(w)` would also work.
</details>

## 3. How to test and measure a sort you wrote

When you write a sort by hand you need two tools: a way to **check** it and a way to **count** what it does. Python's own `sorted` is the perfect reference to check against.

### Random testing against `sorted`

```python
import random

def my_sort(a):
    a = list(a)
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key
    return a


rng = random.Random(7)
for trial in range(1000):
    n = rng.randint(0, 12)
    data = [rng.randint(-5, 5) for _ in range(n)]
    assert my_sort(data) == sorted(data), data
print("1000 random tests passed")
```
```text
1000 random tests passed
```

Three habits make this test strong: use **small lists** (bugs show up on tiny inputs, and failures are easy to read), use **small value ranges** (so that duplicates are common), and
include **length 0 and 1**. Also keep a short list of special inputs that break many sorts:

```python
def my_sort(a):
    a = list(a)
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            j -= 1
        a[j + 1] = key
    return a


special = [[], [1], [2, 1], [1, 1], [1, 2, 3], [3, 2, 1], [5, 5, 5, 5], [2, 1, 2, 1]]
for data in special:
    assert my_sort(data) == sorted(data), data
print("special cases passed:", len(special))
```
```text
special cases passed: 8
```

Empty, one element, two elements, already sorted, reversed, all equal and many duplicates: these seven shapes catch most mistakes. The tests of this module's problems use the same shapes.

### Counting comparisons

To compare algorithms honestly count **operations** instead of seconds (seconds depend on your machine). A small wrapper counts comparisons:

```python
class Counted:
    count = 0
    def __init__(self, v):
        self.v = v
    def __lt__(self, other):
        Counted.count += 1
        return self.v < other.v

def comparisons(sort_function, data):
    Counted.count = 0
    sort_function([Counted(x) for x in data])
    return Counted.count

print(comparisons(sorted, list(range(1000))))
print(comparisons(sorted, list(range(1000, 0, -1))))
import random
rng = random.Random(3)
shuffled = list(range(1000))
rng.shuffle(shuffled)
print(comparisons(sorted, shuffled))
```
```text
999
999
8663
```

`sorted` on already sorted data makes only 999 comparisons (one per neighbour pair): that is Timsort noticing a single long run. On reversed data it also takes 999, because Timsort detects a strictly descending run and flips it.
On shuffled data it needs about 8,700, close to `n log2 n = 9,966`. The class `Counted` only defines `<` because `sorted` only ever uses `<`.

### Sorted-ness checks

Use this helper in your own tests:

```python
def is_sorted(a):
    return all(a[i] <= a[i + 1] for i in range(len(a) - 1))

print(is_sorted([1, 2, 2, 3]), is_sorted([1, 3, 2]), is_sorted([]))
```
```text
True False True
```

Note that a correct sort must also keep **the same elements**. A function that returns `[0] * len(a)` passes `is_sorted`. Compare against `sorted(data)` as above, or compare `sorted(result) == sorted(data)` too.

## 4. Bubble sort

### The idea

Bubble sort walks along the list and compares **neighbours**. If a pair is in the wrong order (`a[i] > a[i + 1]`) it swaps them. After one walk (a **pass**), the largest value has "bubbled" to the end,
like a bubble rising in a drink. Repeat until a pass makes no swap.

### Why it works

After pass 1 the largest value sits in the last place. Why? Whenever the walk meets the current largest value, it keeps swapping it to the right until it meets a larger one or the end.
After pass 2 the second largest is in the second to last place, and so on. After `n - 1` passes everything is in place.

### Code with a trace

```python
a = [5, 1, 4, 2, 8]
for p in range(len(a) - 1):
    for i in range(len(a) - 1 - p):
        if a[i] > a[i + 1]:
            a[i], a[i + 1] = a[i + 1], a[i]
    print("after pass", p + 1, a)
```
```text
after pass 1 [1, 4, 2, 5, 8]
after pass 2 [1, 2, 4, 5, 8]
after pass 3 [1, 2, 4, 5, 8]
after pass 4 [1, 2, 4, 5, 8]
```

The inner loop shortens by one each pass, because the last `p` places are already final. Trace pass 1 by hand: `5 1` swap, `5 4` swap, `5 2` swap, `5 8` no swap: the 5 travelled right as far as the 8.

### The early exit

Pass 2 above already produced a sorted list; passes 3 and 4 do nothing. Add a flag:

```python
def bubble_sort(a):
    a = list(a)
    passes = 0
    while True:
        passes += 1
        swapped = False
        for i in range(len(a) - 1):
            if a[i] > a[i + 1]:
                a[i], a[i + 1] = a[i + 1], a[i]
                swapped = True
        if not swapped:
            return a, passes


print(bubble_sort([5, 1, 4, 2, 8]))
print(bubble_sort([1, 2, 3, 4, 5]))
print(bubble_sort([5, 4, 3, 2, 1]))
print(bubble_sort([2, 3, 4, 5, 1]))
print(bubble_sort([5, 1, 2, 3, 4]))
```
```text
([1, 2, 4, 5, 8], 3)
([1, 2, 3, 4, 5], 1)
([1, 2, 3, 4, 5], 5)
([1, 2, 3, 4, 5], 5)
([1, 2, 3, 4, 5], 2)
```

Notice the last two lists. `[2, 3, 4, 5, 1]` needs 5 passes because the 1 can move only **one place left per pass**, but `[5, 1, 2, 3, 4]` needs just 2: the large 5 jumps right in a single pass.
Bubble sort is fast at moving large values right and slow at moving small values left (the "turtles").

### Cost

- Comparisons: about `n^2 / 2` (fewer with the early exit on friendly data).
- Swaps: exactly the number of **inversions** (each swap fixes one pair that was out of order).
- Time: `O(n^2)` worst and average, `O(n)` best (already sorted, with the early exit).
- Memory: `O(1)`, in place. Stable (swap only when strictly greater).

### When is bubble sort OK?

Almost never in real code. Its use is teaching: it is the easiest sort to write, and its pass structure shows what "sorting by local swaps" does. If you must sort a handful of elements without a library, insertion sort is simpler and faster.

**Try it 3.** How many swaps does bubble sort make on `[3, 2, 1]`?

<details><summary>Answer</summary>

```python
a = [3, 2, 1]
swaps = 0
for p in range(len(a) - 1):
    for i in range(len(a) - 1 - p):
        if a[i] > a[i + 1]:
            a[i], a[i + 1] = a[i + 1], a[i]
            swaps += 1
print(a, swaps)
```
```text
[1, 2, 3] 3
```

Three swaps: the list has 3 inversions, (3,2), (3,1), (2,1), and each swap fixes one.
</details>

## 5. Selection sort

### The idea

Selection sort keeps a **sorted prefix** at the left and an **unsorted rest** at the right. In every round it **selects** the smallest value in the unsorted rest and swaps it to the front of the rest.

```python
a = [64, 25, 12, 22, 11]
for i in range(len(a) - 1):
    m = i
    for j in range(i + 1, len(a)):
        if a[j] < a[m]:
            m = j
    a[i], a[m] = a[m], a[i]
    print("round", i, "min at", m, a)
```
```text
round 0 min at 4 [11, 25, 12, 22, 64]
round 1 min at 2 [11, 12, 25, 22, 64]
round 2 min at 3 [11, 12, 22, 25, 64]
round 3 min at 3 [11, 12, 22, 25, 64]
```

Read the first round: the minimum of the whole list is 11 at index 4; it is swapped with 64. Now `[11, ...]` is final. The second round looks only at `a[1:]`.

### Cost

- Comparisons: always `n(n-1)/2`, **even if the list is already sorted**. Selection sort cannot notice order.
- Swaps: at most `n - 1`. That is the fewest of the three simple sorts.
- Time: `O(n^2)` in every case. Memory `O(1)`.
- **Not stable.** A swap can jump a value over an equal one:

```python
data = [("a", 2), ("b", 2), ("c", 1)]
for i in range(len(data) - 1):
    m = i
    for j in range(i + 1, len(data)):
        if data[j][1] < data[m][1]:
            m = j
    data[i], data[m] = data[m], data[i]
print(data)
```
```text
[('c', 1), ('b', 2), ('a', 2)]
```

Input order of the two records with key 2 was `a`, `b`. Output order is `b`, `a`: the first swap moved `("a", 2)` to the back, behind `("b", 2)`. Compare with Python's stable result `[('c', 1), ('a', 2), ('b', 2)]`.

### When is selection sort OK?

When **writing is expensive** and reading is cheap (the memory of some devices wears out with writes), because it writes at most `n - 1` times. For ordinary programs prefer insertion sort or the library.

## 6. Insertion sort

### The idea

Insertion sort is how most people sort playing cards in their hand. The left part of the list is already sorted. Take the next card (**key**), slide it left past every larger card, and drop it into the gap.

```python
a = [4, 3, 2, 10, 12, 1]
for i in range(1, len(a)):
    key = a[i]
    j = i - 1
    while j >= 0 and a[j] > key:
        a[j + 1] = a[j]
        j -= 1
    a[j + 1] = key
    print("inserted", key, "->", a)
```
```text
inserted 3 -> [3, 4, 2, 10, 12, 1]
inserted 2 -> [2, 3, 4, 10, 12, 1]
inserted 10 -> [2, 3, 4, 10, 12, 1]
inserted 12 -> [2, 3, 4, 10, 12, 1]
inserted 1 -> [1, 2, 3, 4, 10, 12]
```

Trace `i = 5`, key 1: the 12, 10, 4, 3, 2 each shift one place right, and 1 drops into index 0. The shift is one assignment, not a three-step swap, so insertion sort writes less than bubble sort.

### Why check `j >= 0` first?

In `while j >= 0 and a[j] > key`, Python evaluates `j >= 0` first and stops if it is false. If you swap the two tests, then at `j = -1` Python reads `a[-1]`, the **last** element, and quietly gives wrong answers without an error.

### Cost: it depends on inversions

Every shift removes exactly one inversion, so the time is `O(n + I)` where `I` is the number of inversions.

```python
def insertion_shifts(a):
    a = list(a)
    shifts = 0
    for i in range(1, len(a)):
        key = a[i]
        j = i - 1
        while j >= 0 and a[j] > key:
            a[j + 1] = a[j]
            shifts += 1
            j -= 1
        a[j + 1] = key
    return shifts

n = 100
print("sorted   :", insertion_shifts(list(range(n))))
print("reversed :", insertion_shifts(list(range(n, 0, -1))))
nearly = list(range(n))
nearly[10], nearly[11] = nearly[11], nearly[10]
nearly[50], nearly[51] = nearly[51], nearly[50]
print("2 swapped:", insertion_shifts(nearly))
import random
rng = random.Random(5)
shuffled = list(range(n))
rng.shuffle(shuffled)
print("random   :", insertion_shifts(shuffled), "(about n*n/4 = 2475)")
```
```text
sorted   : 0
reversed : 4950
2 swapped: 2
random   : 2482 (about n*n/4 = 2475)
```

Sorted data: 0 shifts. Two neighbouring pairs swapped: only 2 shifts. Reversed: `n(n-1)/2 = 4950`. Random: about half of that.

### Properties and when it is OK

- Stable (`>` is strict), in place, `O(1)` memory.
- Best case `O(n)`, worst and average `O(n^2)`.
- **Great for small lists** (up to roughly 16 to 50 items) and for **nearly sorted** data. Real library sorts (Timsort, and the sorts in many C libraries) use insertion sort on small pieces because it has almost no overhead.
- **Online**: it can sort items as they arrive, keeping the prefix sorted.

**Try it 4.** For `[2, 1, 3, 5, 4]` how many shifts does insertion sort do? Count inversions first.

<details><summary>Answer</summary>

```python
a = [2, 1, 3, 5, 4]
inv = sum(1 for i in range(len(a)) for j in range(i + 1, len(a)) if a[i] > a[j])
print("inversions:", inv)
```
```text
inversions: 2
```

The inversions are (2,1) and (5,4), so insertion sort makes exactly 2 shifts.
</details>

## 7. Comparing the three simple sorts

| | Bubble | Selection | Insertion |
|---|---|---|---|
| Best case | `O(n)` (with early exit) | `O(n^2)` | `O(n)` |
| Worst / average | `O(n^2)` | `O(n^2)` | `O(n^2)` |
| Writes | many swaps (= inversions) | at most `n - 1` | shifts (= inversions) |
| Stable | yes | no | yes |
| In place | yes | yes | yes |
| Good for | teaching | few writes | small or nearly sorted data |

Let us count comparisons for the three on the same data to see the differences:

```python
def bubble(a):
    a = list(a); cmp = 0
    while True:
        swapped = False
        for i in range(len(a) - 1):
            cmp += 1
            if a[i] > a[i + 1]:
                a[i], a[i + 1] = a[i + 1], a[i]; swapped = True
        if not swapped:
            return cmp

def selection(a):
    a = list(a); cmp = 0
    for i in range(len(a) - 1):
        m = i
        for j in range(i + 1, len(a)):
            cmp += 1
            if a[j] < a[m]:
                m = j
        a[i], a[m] = a[m], a[i]
    return cmp

def insertion(a):
    a = list(a); cmp = 0
    for i in range(1, len(a)):
        key = a[i]; j = i - 1
        while j >= 0:
            cmp += 1
            if a[j] > key:
                a[j + 1] = a[j]; j -= 1
            else:
                break
        a[j + 1] = key
    return cmp

import random
rng = random.Random(11)
n = 200
shapes = {
    "sorted": list(range(n)),
    "reversed": list(range(n, 0, -1)),
    "random": rng.sample(range(n), n),
}
for name, data in shapes.items():
    print(f"{name:9} bubble {bubble(data):6} selection {selection(data):6} insertion {insertion(data):6}")
```
```text
sorted    bubble    199 selection  19900 insertion    199
reversed  bubble  39800 selection  19900 insertion  19900
random    bubble  38606 selection  19900 insertion  10364
```

On sorted data insertion and bubble both need about `n` comparisons while selection still needs `n(n-1)/2 = 19900`. On reversed data all three are quadratic. All three are far from the `n log2 n = 1529` of the next sorts, so you should leave this section with one rule:
**use these only for tiny lists, nearly sorted lists, or to learn.**

Everything from here needs one new idea: **divide and conquer**. Instead of fixing one element per pass, split the problem into smaller problems of the same kind.

## 8. Merge sort

### The idea

Merge sort has three steps:

1. **Divide** the list into two halves.
2. **Conquer**: sort each half (by calling merge sort again).
3. **Combine**: **merge** the two sorted halves into one sorted list.

A list of 0 or 1 elements is already sorted: that is the **base case** that stops the recursion.

All the real work is in the merge, so first understand merging alone.

### The merge step

Two sorted lists, two pointers. Compare the front elements, take the smaller, advance that pointer. When one list runs out, copy the rest of the other.

```python
def merge(left, right):
    out = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    out.extend(left[i:])
    out.extend(right[j:])
    return out


print(merge([1, 4, 7], [2, 4, 9, 10]))
print(merge([], [3]))
print(merge([5, 6], [1, 2]))
```
```text
[1, 2, 4, 4, 7, 9, 10]
[3]
[1, 2, 5, 6]
```

Why is the merge correct? The smallest value of the combined data must be one of the two front elements (each list is sorted, so nothing in a list is smaller than its front). So taking the smaller front is always safe.
Why is it fast? Each loop round moves one element into `out`, so a merge of sizes `n` and `m` makes at most `n + m` steps. Also notice `<=`: on a tie we take from the **left** list, which keeps the sort **stable**.

### The full sort

```python
def merge_sort(a):
    if len(a) <= 1:
        return a
    mid = len(a) // 2
    left = merge_sort(a[:mid])
    right = merge_sort(a[mid:])
    return merge(left, right)


def merge(left, right):
    out = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
    out.extend(left[i:])
    out.extend(right[j:])
    return out


print(merge_sort([38, 27, 43, 3, 9, 82, 10]))
print(merge_sort([]))
print(merge_sort([5]))
print(merge_sort([2, 2, 1, 1]))
```
```text
[3, 9, 10, 27, 38, 43, 82]
[]
[5]
[1, 1, 2, 2]
```

### A trace of the recursion

The best way to understand recursion is to print it. This version prints what each call receives and returns, indented by depth:

```python
def merge(left, right):
    out = []
    i = j = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            out.append(left[i]); i += 1
        else:
            out.append(right[j]); j += 1
    return out + left[i:] + right[j:]


def merge_sort(a, depth=0):
    pad = "  " * depth
    print(pad + "sort", a)
    if len(a) <= 1:
        return a
    mid = len(a) // 2
    left = merge_sort(a[:mid], depth + 1)
    right = merge_sort(a[mid:], depth + 1)
    result = merge(left, right)
    print(pad + "merge", left, right, "->", result)
    return result


merge_sort([5, 2, 4, 7, 1, 3])
```
```text
sort [5, 2, 4, 7, 1, 3]
  sort [5, 2, 4]
    sort [5]
    sort [2, 4]
      sort [2]
      sort [4]
    merge [2] [4] -> [2, 4]
  merge [5] [2, 4] -> [2, 4, 5]
  sort [7, 1, 3]
    sort [7]
    sort [1, 3]
      sort [1]
      sort [3]
    merge [1] [3] -> [1, 3]
  merge [7] [1, 3] -> [1, 3, 7]
merge [2, 4, 5] [1, 3, 7] -> [1, 2, 3, 4, 5, 7]
```

Read it as a tree. The list is cut in halves down to single elements (the "sort" lines getting more indented). Then the "merge" lines go back up: each merges two sorted lists into a longer sorted one.
The total number of merge **levels** is `log2(n)`; every level touches all `n` elements once.

### Cost

- Time: `O(n log n)` **always**, because the halves are always equal. There is no bad input.
- Extra memory: `O(n)` for the merge output (the recursion stack is only `O(log n)` deep).
- Stable if the merge takes the left element on ties.
- Works well on data that must be read sequentially (linked lists, files on disk), because merging only needs to walk forward.

```python
import math

def merge_sort_counting(a, stats):
    if len(a) <= 1:
        return a
    mid = len(a) // 2
    left = merge_sort_counting(a[:mid], stats)
    right = merge_sort_counting(a[mid:], stats)
    out = []
    i = j = 0
    while i < len(left) and j < len(right):
        stats[0] += 1
        if left[i] <= right[j]:
            out.append(left[i]); i += 1
        else:
            out.append(right[j]); j += 1
    return out + left[i:] + right[j:]

import random
rng = random.Random(2)
for n in (1000, 2000, 4000):
    stats = [0]
    merge_sort_counting([rng.random() for _ in range(n)], stats)
    print(n, "items:", stats[0], "comparisons; n*log2(n) =", round(n * math.log2(n)))
```
```text
1000 items: 8718 comparisons; n*log2(n) = 9966
2000 items: 19434 comparisons; n*log2(n) = 21932
4000 items: 42852 comparisons; n*log2(n) = 47863
```

Doubling `n` slightly more than doubles the comparisons: the `n log n` growth. For `n = 4000` we make about 43,000 comparisons, versus 8,000,000 for a quadratic sort.

### A note on slicing and memory

`a[:mid]` and `a[mid:]` copy. That is `O(n)` per call, which fits inside the `O(n)` budget of the merge, so the total stays `O(n log n)`. A more careful version sorts index ranges `lo..hi` with one shared buffer.
A **bottom-up** merge sort uses no recursion: merge runs of length 1, then 2, 4, 8, ... until one run is left.

```python
def merge_sort_bottom_up(a):
    a = list(a)
    n = len(a)
    width = 1
    while width < n:
        out = []
        for lo in range(0, n, 2 * width):
            left = a[lo:lo + width]
            right = a[lo + width:lo + 2 * width]
            i = j = 0
            while i < len(left) and j < len(right):
                if left[i] <= right[j]:
                    out.append(left[i]); i += 1
                else:
                    out.append(right[j]); j += 1
            out.extend(left[i:])
            out.extend(right[j:])
        a = out
        width *= 2
    return a


print(merge_sort_bottom_up([38, 27, 43, 3, 9, 82, 10]))
print(merge_sort_bottom_up([3, 3, 1]))
```
```text
[3, 9, 10, 27, 38, 43, 82]
[1, 3, 3]
```

### Common merge sort mistakes

- Base case `len(a) == 0` only: a list of one element splits into `[]` and itself, forever: `RecursionError`.
- Forgetting the leftovers after the `while` loop.
- `<` instead of `<=` in the merge: still sorted, but no longer stable.
- Splitting with `a[mid + 1:]`: one element disappears.
- Merging with `pop(0)`: each pop is `O(n)`, so the merge becomes quadratic.

**Try it 5.** What does `merge([2, 2], [2])` return if you track which list each `2` came from (call the lists `L` and `R`)? Which comes first?

<details><summary>Answer</summary>

```python
left = [("L", 2), ("L", 2)]
right = [("R", 2)]
out = []
i = j = 0
while i < len(left) and j < len(right):
    if left[i][1] <= right[j][1]:
        out.append(left[i]); i += 1
    else:
        out.append(right[j]); j += 1
out.extend(left[i:])
out.extend(right[j:])
print(out)
```
```text
[('L', 2), ('L', 2), ('R', 2)]
```

With `<=` both `L` elements are taken first, then the `R`. With `<` the `R` would jump ahead.
</details>

## 9. Counting inversions with merge sort

### The question

An **inversion** is a pair `i < j` with `a[i] > a[j]`. The number of inversions measures how far a list is from sorted: 0 means sorted, `n(n-1)/2` means reversed.
It is also exactly the number of swaps bubble sort makes and the number of shifts of insertion sort. Counting by two loops is `O(n^2)`. Merge sort does it in `O(n log n)`.

### The idea

Count inversions in three groups: pairs inside the left half, pairs inside the right half, and **cross pairs** (one element in each half). Recursion gives the first two groups.
The cross pairs are counted **during the merge**: when you take `right[j]` because it is smaller than `left[i]`, then `right[j]` is smaller than `left[i]` **and** all later elements of `left` (they are all `>= left[i]`, because `left` is sorted).
So it forms `len(left) - i` inversions.

```python
def sort_count(a):
    if len(a) <= 1:
        return a, 0
    mid = len(a) // 2
    left, x = sort_count(a[:mid])
    right, y = sort_count(a[mid:])
    out = []
    i = j = 0
    cross = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            out.append(left[i])
            i += 1
        else:
            out.append(right[j])
            j += 1
            cross += len(left) - i
    out.extend(left[i:])
    out.extend(right[j:])
    return out, x + y + cross


print(sort_count([2, 4, 1, 3, 5]))
print(sort_count([5, 4, 3, 2, 1]))
print(sort_count([1, 2, 3]))
print(sort_count([2, 2, 1]))
```
```text
([1, 2, 3, 4, 5], 3)
([1, 2, 3, 4, 5], 10)
([1, 2, 3], 0)
([1, 2, 2], 2)
```

Check `[2, 4, 1, 3, 5]` by hand: the inversions are (2,1), (4,1), (4,3), so 3. The merge of `[2, 4]` and `[1, 3, 5]` takes 1 first (2 and 4 are both greater: +2), then takes 2, then 3 while 4 waits (+1), so the cross count is 3, and the halves have none.
Note `[2, 2, 1]` gives 2, not 3: equal values are **not** inversions, which is why the merge uses `<=`.

### A variation: the reverse pairs

The same trick counts other relations between a left and a right element as long as the condition is **monotone** (it moves in one direction when you move along a sorted half). For "count pairs with `a[i] > 2 * a[j]`" do the counting in a separate loop **before** merging, with a pointer that only moves forward. Problem p038 is exactly this.

**Try it 6.** What is the inversion count of `[3, 1, 2]`?

<details><summary>Answer</summary>

```python
def sort_count(a):
    if len(a) <= 1:
        return a, 0
    mid = len(a) // 2
    left, x = sort_count(a[:mid])
    right, y = sort_count(a[mid:])
    out = []
    i = j = 0
    cross = 0
    while i < len(left) and j < len(right):
        if left[i] <= right[j]:
            out.append(left[i]); i += 1
        else:
            out.append(right[j]); j += 1
            cross += len(left) - i
    return out + left[i:] + right[j:], x + y + cross

print(sort_count([3, 1, 2])[1])
```
```text
2
```

The inversions are (3,1) and (3,2).
</details>

## 10. Quick sort

### The idea

Quick sort also divides and conquers, but it puts the work on the **divide** side:

1. Pick a **pivot** value.
2. **Partition**: rearrange the list so that everything smaller than the pivot is on its left and everything larger is on its right. The pivot is now in its **final place**.
3. Sort the left part and the right part by calling quick sort again. There is nothing to combine.

Compare with merge sort: merge sort splits trivially and merges cleverly; quick sort splits cleverly and combines trivially.

### The simplest version (and why it is not the real one)

```python
def quick_simple(a):
    if len(a) <= 1:
        return a
    pivot = a[0]
    smaller = [x for x in a[1:] if x < pivot]
    larger = [x for x in a[1:] if x >= pivot]
    return quick_simple(smaller) + [pivot] + quick_simple(larger)


print(quick_simple([6, 3, 8, 1, 5, 9, 2]))
print(quick_simple([4, 4, 1, 4]))
```
```text
[1, 2, 3, 5, 6, 8, 9]
[1, 4, 4, 4]
```

This builds new lists, so it uses `O(n)` extra memory per level. The real quick sort rearranges **in place** with swaps. There are two classic ways to partition.

### Lomuto partition

Lomuto's scheme takes the **last element** as the pivot and keeps an index `i` that marks where the "smaller than pivot" zone ends. Scan `j` from left to right; whenever `a[j] < pivot`, swap it into position `i` and move `i` one step right. At the end swap the pivot into `a[i]`.

```python
def partition(a, lo, hi):
    pivot = a[hi]
    i = lo
    for j in range(lo, hi):
        if a[j] < pivot:
            a[i], a[j] = a[j], a[i]
            i += 1
        print("j =", j, "i =", i, a)
    a[i], a[hi] = a[hi], a[i]
    return i


a = [7, 2, 9, 4, 3, 8, 5]
p = partition(a, 0, len(a) - 1)
print("pivot index", p, a)
```
```text
j = 0 i = 0 [7, 2, 9, 4, 3, 8, 5]
j = 1 i = 1 [2, 7, 9, 4, 3, 8, 5]
j = 2 i = 1 [2, 7, 9, 4, 3, 8, 5]
j = 3 i = 2 [2, 4, 9, 7, 3, 8, 5]
j = 4 i = 3 [2, 4, 3, 7, 9, 8, 5]
j = 5 i = 3 [2, 4, 3, 7, 9, 8, 5]
pivot index 3 [2, 4, 3, 5, 9, 8, 7]
```

Invariant (a fact that stays true during the loop): `a[lo:i]` is all `< pivot`, `a[i:j]` is all `>= pivot`. When the loop ends `a[i:hi]` holds the larger-or-equal values, so swapping the pivot into `a[i]` puts it exactly between the two zones.

The full sort:

```python
def quick_sort(a, lo=0, hi=None):
    if hi is None:
        hi = len(a) - 1
    if lo >= hi:
        return
    pivot = a[hi]
    i = lo
    for j in range(lo, hi):
        if a[j] < pivot:
            a[i], a[j] = a[j], a[i]
            i += 1
    a[i], a[hi] = a[hi], a[i]
    quick_sort(a, lo, i - 1)
    quick_sort(a, i + 1, hi)


data = [6, 3, 8, 1, 5, 9, 2]
quick_sort(data)
print(data)
data = [3, 3, 3, 1]
quick_sort(data)
print(data)
```
```text
[1, 2, 3, 5, 6, 8, 9]
[1, 3, 3, 3]
```

### Hoare partition

Hoare's original scheme uses **two pointers that walk toward each other**. Take the pivot (here the middle value). Move `i` right until `a[i] >= pivot`, move `j` left until `a[j] <= pivot`, and if `i < j` swap them. Stop when the pointers cross.
It does about **three times fewer swaps** than Lomuto on average and handles many equal values well (both pointers stop on equals, so the split stays balanced).

```python
def hoare_partition(a, lo, hi):
    pivot = a[(lo + hi) // 2]
    i = lo - 1
    j = hi + 1
    while True:
        i += 1
        while a[i] < pivot:
            i += 1
        j -= 1
        while a[j] > pivot:
            j -= 1
        if i >= j:
            return j
        a[i], a[j] = a[j], a[i]


def quick_sort_hoare(a, lo, hi):
    if lo < hi:
        p = hoare_partition(a, lo, hi)
        quick_sort_hoare(a, lo, p)
        quick_sort_hoare(a, p + 1, hi)


data = [7, 2, 9, 4, 3, 8, 5]
quick_sort_hoare(data, 0, len(data) - 1)
print(data)
data = [4, 4, 4, 4]
quick_sort_hoare(data, 0, len(data) - 1)
print(data)
```
```text
[2, 3, 4, 5, 7, 8, 9]
[4, 4, 4, 4]
```

Two details make Hoare's version delicate and are the usual source of bugs: the returned index `j` is **not** necessarily the pivot's final position (so you recurse on `lo..j` and `j+1..hi`, not `j-1` and `j+1`), and the pivot must be chosen so that the recursion makes progress (the middle element works; the last element can loop forever with this exact code).
Lomuto is easier to get right, which is why this module's problems use it for tracing.

### The worst case

Quick sort is fast only if the pivot splits the list **reasonably evenly**. If the pivot is always the smallest or largest value, one side is empty, the other has `n - 1` elements, and the work is `n + (n-1) + (n-2) + ... = O(n^2)`. With "last element as pivot" the input that does this is simply **an already sorted list** (or a reversed one). That is the cruellest case, because sorted data is so common.

```python
def lomuto_comparisons(a):
    a = list(a)
    count = 0
    stack = [(0, len(a) - 1)]
    max_depth = 0
    # iterative, so that the test itself does not hit the recursion limit
    while stack:
        lo, hi = stack.pop()
        if lo >= hi:
            continue
        pivot = a[hi]
        i = lo
        for j in range(lo, hi):
            count += 1
            if a[j] < pivot:
                a[i], a[j] = a[j], a[i]
                i += 1
        a[i], a[hi] = a[hi], a[i]
        stack.append((lo, i - 1))
        stack.append((i + 1, hi))
    return count


import random
n = 500
rng = random.Random(8)
print("sorted  :", lomuto_comparisons(range(n)))
print("reversed:", lomuto_comparisons(range(n, 0, -1)))
print("random  :", lomuto_comparisons(rng.sample(range(n), n)))
```
```text
sorted  : 124750
reversed: 124750
random  : 4868
```

On sorted input the count is `n(n-1)/2 = 124,750`, the quadratic worst case, while random data needs only a few thousand. In Python the sorted case is worse than slow: the recursion is `n` levels deep and **crashes with `RecursionError`** around depth 1000.

```python
def quick_sort(a, lo, hi):
    if lo >= hi:
        return
    pivot = a[hi]
    i = lo
    for j in range(lo, hi):
        if a[j] < pivot:
            a[i], a[j] = a[j], a[i]
            i += 1
    a[i], a[hi] = a[hi], a[i]
    quick_sort(a, lo, i - 1)
    quick_sort(a, i + 1, hi)

try:
    data = list(range(3000))
    quick_sort(data, 0, len(data) - 1)
except RecursionError:
    print("RecursionError on 3000 sorted numbers")
```
```text
RecursionError on 3000 sorted numbers
```

### Choosing the pivot

The fix is to choose the pivot so that no fixed input is bad:

- **Random pivot**: pick `a[random.randint(lo, hi)]`. Then no input is always bad; the expected running time is `O(n log n)` for every input, and the recursion depth is `O(log n)` with very high probability.
- **Median of three**: use the median of the first, middle and last elements. It fixes sorted and reversed input and is cheap, but clever adversarial inputs still exist.
- **Swap the chosen pivot to the end** and then use Lomuto, which expects the pivot at `hi`.

```python
import random

def quick_sort(a, lo, hi, rng):
    if lo >= hi:
        return
    k = rng.randint(lo, hi)
    a[k], a[hi] = a[hi], a[k]
    pivot = a[hi]
    i = lo
    for j in range(lo, hi):
        if a[j] < pivot:
            a[i], a[j] = a[j], a[i]
            i += 1
    a[i], a[hi] = a[hi], a[i]
    quick_sort(a, lo, i - 1, rng)
    quick_sort(a, i + 1, hi, rng)


rng = random.Random(1)
for data in (list(range(3000)), list(range(3000, 0, -1)), [rng.randint(0, 9) for _ in range(3000)]):
    expected = sorted(data)
    quick_sort(data, 0, len(data) - 1, rng)
    print(data == expected)
```
```text
True
True
True
```

All three lines print `True`: sorted and reversed input no longer hurt. The third input has only ten different values; it works here, but it still has a weakness, described next.

### Many equal values: three-way partition

Lomuto and the simple version put all values equal to the pivot on the same side, and only the pivot itself is finished. If the list has few distinct values (3000 numbers drawn from 0..9), each partition finishes only one element out of about 300 equal ones, so the work grows toward `n^2 / 10`. For an **all-equal** list every partition puts all `n - 1` other elements on one side: `O(n^2)` again. The cure is a **three-way partition** into `< pivot`, `== pivot`, `> pivot`, then recursing only on the outer two parts.

```python
import random

def quick3(a):
    if len(a) <= 1:
        return a
    pivot = a[random.randrange(len(a))]
    less = [x for x in a if x < pivot]
    equal = [x for x in a if x == pivot]
    greater = [x for x in a if x > pivot]
    return quick3(less) + equal + quick3(greater)


random.seed(4)
print(quick3([5, 1, 5, 3, 5, 2, 1]))
big = [7] * 200000
print(len(quick3(big)), "all-equal elements sorted in one step")
```
```text
[1, 1, 2, 3, 5, 5, 5]
200000 all-equal elements sorted in one step
```

In the all-equal list the `equal` part holds everything; nothing is recursed into. More equal values make the sort **faster**, down to `O(n)` when there are only a few distinct values.
The in-place version of this idea is the **Dutch national flag** partition with three pointers `lt`, `i`, `gt`:

```python
def dutch_flag(a, pivot):
    lt, i, gt = 0, 0, len(a) - 1
    while i <= gt:
        if a[i] < pivot:
            a[lt], a[i] = a[i], a[lt]
            lt += 1
            i += 1
        elif a[i] > pivot:
            a[i], a[gt] = a[gt], a[i]
            gt -= 1
        else:
            i += 1
    return lt, gt


data = [3, 6, 1, 6, 2, 9, 6, 4]
lt, gt = dutch_flag(data, 6)
print(data, "less ends before", lt, "greater starts after", gt)
```
```text
[3, 1, 2, 4, 6, 6, 6, 9] less ends before 4 greater starts after 6
```

When `a[i] > pivot` the element swapped in from the right is **not examined yet**, so `i` does not advance. This is the classic bug in problem p017.

### Quickselect: the k-th smallest without sorting everything

Suppose you need only the `k`-th smallest value (the median, say). After a partition the pivot is in its final index `p`. If `p == k` you are done; if `k < p` the answer is in the left part; otherwise in the right part. **You recurse into only one side**, so the expected work is `n + n/2 + n/4 + ... = O(n)`.

```python
import random

def quickselect(a, k):
    """k-th smallest (0-based) of a. Expected O(n)."""
    a = list(a)
    lo, hi = 0, len(a) - 1
    while True:
        if lo == hi:
            return a[lo]
        r = random.randint(lo, hi)
        a[r], a[hi] = a[hi], a[r]
        pivot = a[hi]
        i = lo
        for j in range(lo, hi):
            if a[j] < pivot:
                a[i], a[j] = a[j], a[i]
                i += 1
        a[i], a[hi] = a[hi], a[i]
        if k == i:
            return a[i]
        if k < i:
            hi = i - 1
        else:
            lo = i + 1


random.seed(9)
data = [7, 10, 4, 3, 20, 15]
print([quickselect(data, k) for k in range(6)])
print(sorted(data))
```
```text
[3, 4, 7, 10, 15, 20]
[3, 4, 7, 10, 15, 20]
```

The worst case is still `O(n^2)` (with an unlucky pivot every time), but with a random pivot it is vanishingly unlikely. Quickselect answers "k-th largest element" (LeetCode 215) and "median" questions in linear time.

### Cost summary

| | Time (average) | Time (worst) | Memory | Stable |
|---|---|---|---|---|
| Quick sort (random pivot) | `O(n log n)` | `O(n^2)` (extremely unlikely) | `O(log n)` stack | no |
| Quick sort, last pivot | `O(n log n)` on random data | `O(n^2)` on sorted data | `O(n)` stack worst | no |
| Three-way quick sort | `O(n log n)`, `O(n)` few distinct | `O(n^2)` unlikely | `O(log n)` | no |

To keep the stack small: after partitioning, recurse into the **smaller** part and loop on the larger one. Then the stack depth is at most `log2(n)`.

### Quick sort bugs to watch

- Pivot always first or last: sorted input becomes quadratic and crashes with `RecursionError`.
- Two-way partition with many duplicates: quadratic.
- Forgetting the base case `lo >= hi`, or recursing on `i` instead of `i - 1`/`i + 1` (the pivot is final, do not include it again).
- Lomuto with the pivot not at `hi`: swap the chosen pivot to `hi` first.

**Try it 7.** After one Lomuto partition (pivot = last element) of `[4, 1, 3, 2]`, what is the list and the pivot index?

<details><summary>Answer</summary>

```python
a = [4, 1, 3, 2]
pivot = a[-1]
i = 0
for j in range(len(a) - 1):
    if a[j] < pivot:
        a[i], a[j] = a[j], a[i]
        i += 1
a[i], a[-1] = a[-1], a[i]
print(a, i)
```
```text
[1, 2, 3, 4] 1
```

Pivot 2: only `1` is smaller; it is swapped to index 0; then the pivot swaps with `a[1]` (the 4).
</details>

## 11. Heap sort

### The heap idea

A **max-heap** is a list viewed as a tree: the children of index `i` are `2i + 1` and `2i + 2`, the parent of `i` is `(i - 1) // 2`, and **every parent is at least as large as its children**. So the largest value is at index 0, always.

```text
list:   [9, 4, 5, 1, 3, 2]

tree:         9
            /   \
           4     5
          / \   /
         1   3 2
```

The tree is only a way of thinking: the data stays in a flat list, and there are no pointers. Index arithmetic does the work.

### Sift down

The basic repair operation is **sift down**: if `a[i]` is smaller than one of its children, swap it with the **larger** child and continue from that child, until the heap rule holds.

```python
def sift_down(a, i, size):
    while True:
        left = 2 * i + 1
        right = 2 * i + 2
        big = i
        if left < size and a[left] > a[big]:
            big = left
        if right < size and a[right] > a[big]:
            big = right
        if big == i:
            return
        a[i], a[big] = a[big], a[i]
        i = big


a = [1, 9, 5, 4, 3, 2]
sift_down(a, 0, len(a))
print(a)
```
```text
[9, 4, 5, 1, 3, 2]
```

The root `1` fell: it swapped with 9 (the larger of its children 9 and 5), then with 4 (the larger of its new children 4 and 3), and then reached index 3, which has no children inside the list. The printed result satisfies `9 >= 4, 5` and `4 >= 1, 3`.

### Build a heap in `O(n)`

To make a heap out of any list, sift down every non-leaf node, **from the last parent back to the root**. The last parent is at index `n // 2 - 1`; everything after it is a leaf and already a valid one-element heap.

```python
def build_max_heap(a):
    n = len(a)
    for i in range(n // 2 - 1, -1, -1):
        sift_down(a, i, n)


def sift_down(a, i, size):
    while True:
        left = 2 * i + 1
        right = 2 * i + 2
        big = i
        if left < size and a[left] > a[big]:
            big = left
        if right < size and a[right] > a[big]:
            big = right
        if big == i:
            return
        a[i], a[big] = a[big], a[i]
        i = big


a = [3, 9, 2, 1, 4, 5]
build_max_heap(a)
print(a)
```
```text
[9, 4, 5, 1, 3, 2]
```

Building takes only `O(n)` (not `O(n log n)`): most nodes are near the bottom and sift down only a step or two. Half the nodes are leaves and do nothing; a quarter sift at most one level; and so on. The sum of `n/4 * 1 + n/8 * 2 + n/16 * 3 + ...` is at most `n`.

### The sort

1. Build a max-heap.
2. Swap `a[0]` (the maximum) with the last element of the heap region. The maximum is now in its final place; shrink the heap region by one.
3. Sift down the new root inside the smaller heap. Repeat.

```python
def heap_sort(a):
    n = len(a)
    for i in range(n // 2 - 1, -1, -1):
        sift_down(a, i, n)
    for end in range(n - 1, 0, -1):
        a[0], a[end] = a[end], a[0]
        sift_down(a, 0, end)


def sift_down(a, i, size):
    while True:
        left = 2 * i + 1
        right = 2 * i + 2
        big = i
        if left < size and a[left] > a[big]:
            big = left
        if right < size and a[right] > a[big]:
            big = right
        if big == i:
            return
        a[i], a[big] = a[big], a[i]
        i = big


data = [3, 9, 2, 1, 4, 5, 9]
heap_sort(data)
print(data)
empty = []
heap_sort(empty)
print(empty)
```
```text
[1, 2, 3, 4, 5, 9, 9]
[]
```

### Cost

- Time: `O(n log n)` in the worst case, always (`n` extractions, each sift-down at most `log2 n` levels).
- Memory: `O(1)`, fully in place. This is the only sort here with both a worst-case `n log n` guarantee and constant extra space.
- Not stable. In practice slower than quick sort because it jumps around memory (poor cache use).

### `heapq` in two sentences

Python's `heapq` module provides a **min-heap** on a list: `heapq.heapify(a)` builds it in `O(n)`, `heapq.heappush(a, x)` and `heapq.heappop(a)` cost `O(log n)`, and `a[0]` is the smallest. It is the tool for "k smallest", "next event", and "merge k sorted lists".

```python
import heapq

a = [5, 3, 8, 1, 9, 2]
heapq.heapify(a)
print(a[0])
print([heapq.heappop(a) for _ in range(len(a))])
print(heapq.nlargest(2, [5, 3, 8, 1, 9, 2]))
```
```text
1
[1, 2, 3, 5, 8, 9]
[9, 8]
```

For the "largest first" order store negated numbers. In this module the problems ban `heapq` when you must write the sort by hand (problem p025), and allow it nowhere else because you do not need it.

**Try it 8.** In the list `[9, 4, 5, 1, 3, 2]` which indices are the children of index 1, and who is the parent of index 5?

<details><summary>Answer</summary>

```python
a = [9, 4, 5, 1, 3, 2]
i = 1
print("children of 1:", 2 * i + 1, 2 * i + 2, "values", a[2 * i + 1], a[2 * i + 2])
print("parent of 5:", (5 - 1) // 2, "value", a[(5 - 1) // 2])
```
```text
children of 1: 3 4 values 1 3
parent of 5: 2 value 5
```
</details>

## 12. Counting sort

### Sorting without comparing

All the sorts so far compare two elements. By the lower bound of section 1 that costs at least `n log n`. But if the values are **small integers** we can do something else: use the value as an **index**.

Suppose all values are between `0` and `k`. Make a table `count` of `k + 1` counters. One pass counts how often each value occurs. A second pass writes the values out: `count[0]` zeros, then `count[1]` ones, and so on.

```python
def counting_sort(a, k):
    count = [0] * (k + 1)
    for x in a:
        count[x] += 1
    out = []
    for v in range(k + 1):
        out.extend([v] * count[v])
    return out


data = [3, 1, 5, 1, 0, 3, 3, 2]
print(counting_sort(data, 5))
print(counting_sort([], 3))
```
```text
[0, 1, 1, 2, 3, 3, 3, 5]
[]
```

Time `O(n + k)`, memory `O(n + k)`. When `k` is about `n` or smaller, this is linear time. When `k` is huge (values up to `10^18`) the table cannot exist, and counting sort is useless.

### The stable version for records

The version above rebuilds numbers from counts, which loses the identity of the records. To sort **records** by an integer key and stay **stable**, turn the counts into **start positions** (prefix sums), then place each record at the next free slot of its key, in input order:

```python
def counting_sort_records(records, k):
    count = [0] * k
    for name, key in records:
        count[key] += 1
    start = [0] * k
    total = 0
    for key in range(k):
        start[key] = total
        total += count[key]
    out = [None] * len(records)
    for name, key in records:
        out[start[key]] = (name, key)
        start[key] += 1
    return out


records = [("ann", 2), ("bob", 0), ("cy", 2), ("dee", 1), ("eli", 0), ("fay", 2)]
print(counting_sort_records(records, 3))
```
```text
[('bob', 0), ('eli', 0), ('dee', 1), ('ann', 2), ('cy', 2), ('fay', 2)]
```

Equal keys keep their input order: `ann, cy, fay` for key 2. This stable placement is what radix sort needs. The textbook form fills `out` **from the back** using end positions; the result is the same, as long as you process the records in the opposite direction as you decrement.

### When to use it

- Marks 0..100, ages 0..120, letters (26 or 256 values), digits, small ids.
- As the inner step of radix sort.
- **Not** when `k` is much larger than `n`: sorting 10 numbers below `10^9` with a table of a billion cells is absurd.

**Try it 9.** What are `count` and `start` for keys `[1, 0, 1, 2, 0]` with `k = 3`?

<details><summary>Answer</summary>

```python
keys = [1, 0, 1, 2, 0]
k = 3
count = [0] * k
for key in keys:
    count[key] += 1
start = [0] * k
total = 0
for key in range(k):
    start[key] = total
    total += count[key]
print(count, start)
```
```text
[2, 2, 1] [0, 2, 4]
```

Key 0 starts at slot 0 and has 2 records, key 1 starts at 2 and has 2, key 2 starts at 4.
</details>

## 13. Radix sort

### The idea

What if the numbers are too large for a counting table, like values up to `10^9`? Sort by **one digit at a time**. **LSD radix sort** (least significant digit first) does one **stable** counting/bucket pass for the ones digit, then for the tens digit, then hundreds, ... After the last pass the list is sorted.

Why does it work? Consider two numbers. The last pass compares their top digit; if different, that decides, which is right. If the top digits are equal, the stable pass leaves them in the order of the **previous** passes, which already ordered them correctly by the lower digits. By induction the final order is right.

### Code

```python
def radix_sort(a):
    a = list(a)
    if not a:
        return a
    exp = 1
    biggest = max(a)
    while biggest // exp > 0:
        buckets = [[] for _ in range(10)]
        for x in a:
            buckets[(x // exp) % 10].append(x)
        a = [x for bucket in buckets for x in bucket]
        print("exp", exp, a)
        exp *= 10
    return a


print(radix_sort([170, 45, 75, 90, 802, 24, 2, 66]))
```
```text
exp 1 [170, 90, 802, 2, 24, 45, 75, 66]
exp 10 [802, 2, 24, 45, 66, 170, 75, 90]
exp 100 [2, 24, 45, 66, 75, 90, 170, 802]
[2, 24, 45, 66, 75, 90, 170, 802]
```

Trace the second pass: the tens digits of `[170, 90, 802, 2, 24, 45, 75, 66]` are 7, 9, 0, 0, 2, 4, 7, 6. The buckets, read from 0 to 9, give `[802, 2, 24, 45, 66, 170, 75, 90]`. Notice that `802` is still before `2` because they tied on the tens digit and kept their previous order (this is why the pass **must be stable**).

### Why stability is essential

If the bucket pass were unstable, ties in the current digit could be reordered, destroying the work of earlier digits:

```python
a = [21, 11, 12]
# pass 1: sort by ones digit, stable
a = [x for d in range(10) for x in a if x % 10 == d]
print(a)
# pass 2: sort by tens digit, but break ties in reverse (unstable)
a = [x for d in range(10) for x in reversed([y for y in a if y // 10 % 10 == d])]
print(a)
```
```text
[21, 11, 12]
[12, 11, 21]
```

After pass 1 the order is `[21, 11, 12]` (ones digits 1, 1, 2). In pass 2, 21 has tens digit 2 and 11 and 12 have tens digit 1; the unstable tie-break reverses `[11, 12]` to `[12, 11]`, so the final list `[12, 11, 21]` is wrong. A stable pass gives `[11, 12, 21]`.

### Cost

For numbers with `d` digits in base `b` the cost is `O(d * (n + b))`. With 32-bit integers and base 256, `d = 4` passes: effectively `O(n)`. Radix sort is a good choice for large lists of fixed-size integers or strings of equal length. It is not a general replacement for comparison sorts because it needs a digit structure.

A larger base means fewer passes but more buckets. A common choice is base 256 or `2^16`, using shifts and masks: `(x >> shift) & 255`.

```python
def radix_sort_256(a):
    a = list(a)
    for shift in (0, 8, 16, 24):
        buckets = [[] for _ in range(256)]
        for x in a:
            buckets[(x >> shift) & 255].append(x)
        a = [x for bucket in buckets for x in bucket]
    return a


import random
rng = random.Random(6)
data = [rng.randint(0, 2**32 - 1) for _ in range(10000)]
print(radix_sort_256(data) == sorted(data))
```
```text
True
```

**Try it 10.** How many passes does LSD radix sort (base 10) make on `[9, 100, 25]`?

<details><summary>Answer</summary>

```python
a = [9, 100, 25]
passes = 0
exp = 1
while max(a) // exp > 0:
    passes += 1
    exp *= 10
print(passes)
```
```text
3
```

The largest value 100 has three digits, so there are three passes (ones, tens, hundreds).
</details>

## 14. Stability in depth

### What stable means, again

A sort is **stable** if elements with **equal keys** keep their input order. For plain numbers it makes no difference, but for **records** (tuples, objects, rows) you can tell equal-key elements apart, and then it matters.

| Stable | Not stable |
|---|---|
| merge sort (with `<=`), insertion sort, bubble sort, counting sort (placed in order), Timsort (`sorted`, `.sort`) | selection sort, heap sort, usual quick sort |

### Why you want it: sorting by several columns

Imagine a table of `(city, name)` rows, and you want it ordered by city, and by name inside each city. Because the sort is stable you can do it in **two passes, least important key first**:

```python
rows = [("pune", "dee"), ("agra", "bob"), ("pune", "ann"), ("agra", "cy"), ("goa", "eli")]
by_name = sorted(rows, key=lambda r: r[1])
by_city = sorted(by_name, key=lambda r: r[0])
print(by_name)
print(by_city)
print(by_city == sorted(rows))
```
```text
[('pune', 'ann'), ('agra', 'bob'), ('agra', 'cy'), ('pune', 'dee'), ('goa', 'eli')]
[('agra', 'bob'), ('agra', 'cy'), ('goa', 'eli'), ('pune', 'ann'), ('pune', 'dee')]
True
```

The second sort only changes the order when the cities differ; for equal cities it keeps the name order from the first pass. The **last** sort has the **highest priority**. This is the same as sorting once with the key `(city, name)`, which is what `sorted(rows)` does for tuples.

### A demonstration with an unstable sort

```python
def selection_sort_records(a):
    a = list(a)
    for i in range(len(a) - 1):
        m = i
        for j in range(i + 1, len(a)):
            if a[j][1] < a[m][1]:
                m = j
        a[i], a[m] = a[m], a[i]
    return a


records = [("a", 3), ("b", 3), ("c", 1), ("d", 2), ("e", 2)]
print(selection_sort_records(records))
print(sorted(records, key=lambda r: r[1]))
```
```text
[('c', 1), ('d', 2), ('e', 2), ('b', 3), ('a', 3)]
[('c', 1), ('d', 2), ('e', 2), ('a', 3), ('b', 3)]
```

Both are sorted by the number, but selection sort changed `a, b` to `b, a` (the swap that brought `c` to the front threw `a` behind `b`) and `d, e` stayed. A stable sort gives `c, d, e, a, b`.

### Making an unstable sort stable

Attach the **original index** to each element and compare `(key, index)`. Equal keys are then ordered by input position:

```python
def selection_sort(a):
    a = list(a)
    for i in range(len(a) - 1):
        m = i
        for j in range(i + 1, len(a)):
            if a[j] < a[m]:
                m = j
        a[i], a[m] = a[m], a[i]
    return a


records = [("a", 3), ("b", 3), ("c", 1), ("d", 2), ("e", 2)]
decorated = [(key, i, name) for i, (name, key) in enumerate(records)]
result = selection_sort(decorated)
print([name for key, i, name in result])
```
```text
['c', 'd', 'e', 'a', 'b']
```

(This is the *decorate-sort-undecorate* idea: sort tuples `(key, original_index, payload)` and drop the extras afterwards. Any sort, stable or not, then gives the stable order because no two decorated tuples compare equal.)

### Reverse and stability

As seen in section 2, `reverse=True` keeps equal elements in input order. If you want a descending stable sort by a **number** you can also negate the key; for **strings** use `reverse=True` on a single pass.

```python
rows = [("ann", 90), ("bob", 85), ("cy", 90), ("dee", 85)]
print(sorted(rows, key=lambda r: r[1], reverse=True))
print(sorted(rows, key=lambda r: -r[1]))
print(sorted(rows, key=lambda r: r[1])[::-1])
```
```text
[('ann', 90), ('cy', 90), ('bob', 85), ('dee', 85)]
[('ann', 90), ('cy', 90), ('bob', 85), ('dee', 85)]
[('cy', 90), ('ann', 90), ('dee', 85), ('bob', 85)]
```

The first two lines are the same stable descending order; the third reverses the ties as well.

### Multi-key with mixed directions

Sort by `score` descending and `name` ascending. With a key tuple and a negated number it is one pass. If the name must go **descending** and the score ascending, negating a string is impossible, so use two passes:

```python
rows = [("ann", 90), ("bob", 85), ("cy", 90), ("dee", 85)]
step1 = sorted(rows, key=lambda r: r[0], reverse=True)
step2 = sorted(step1, key=lambda r: r[1])
print(step2)
```
```text
[('dee', 85), ('bob', 85), ('cy', 90), ('ann', 90)]
```

Score ascending, names descending inside each score. Problem p035 traces this.

**Try it 11.** `sorted(["bb", "a", "cc", "d"], key=len, reverse=True)`: what is the order of `bb` and `cc`, and of `a` and `d`?

<details><summary>Answer</summary>

```python
print(sorted(["bb", "a", "cc", "d"], key=len, reverse=True))
```
```text
['bb', 'cc', 'a', 'd']
```

Equal lengths keep input order, even with `reverse=True`.
</details>

## 15. Custom comparators and key design

### Key first, comparator last

In Python 3, `sorted(data, key=f)` is the normal tool. A **comparator** is a function `cmp(a, b)` returning a negative number if `a` goes first, zero if equal, and a positive number if `b` goes first. Use `functools.cmp_to_key` to turn one into a key:

```python
from functools import cmp_to_key

def by_length_then_alpha(a, b):
    if len(a) != len(b):
        return len(a) - len(b)
    if a < b:
        return -1
    if a > b:
        return 1
    return 0


words = ["pear", "fig", "apple", "kiwi", "date", "plum"]
print(sorted(words, key=cmp_to_key(by_length_then_alpha)))
print(sorted(words, key=lambda w: (len(w), w)))
```
```text
['fig', 'date', 'kiwi', 'pear', 'plum', 'apple']
['fig', 'date', 'kiwi', 'pear', 'plum', 'apple']
```

Both lines are equal; the key version is shorter and faster because the key is computed once per element instead of the function being called on every comparison. Prefer `key`, and reach for a comparator only when the order is defined by **pairs**.

### When you need a comparator: the largest number

Arrange `[3, 30, 34, 5, 9]` so that the joined digits form the largest number. Two natural attempts, a numeric sort and an alphabetical sort of the strings, both fail:

```python
from functools import cmp_to_key

nums = [3, 30, 34, 5, 9]
numeric = "".join(map(str, sorted(nums, reverse=True)))
text = "".join(sorted(map(str, nums), reverse=True))


def cmp(x, y):
    if x + y > y + x:
        return -1
    if x + y < y + x:
        return 1
    return 0


smart = "".join(sorted(map(str, nums), key=cmp_to_key(cmp)))
print(numeric)
print(text)
print(smart)
```
```text
3430953
9534303
9534330
```

The numeric attempt puts `34` and `30` before `9`. The alphabetical attempt puts `30` before `3` (the string `'30'` is longer, so it sorts after `'3'`, and reversed it comes first), but the best order puts `3` before `30` because `"330" > "303"`. The rule "`x` first if `x + y > y + x`" compares **pairs of strings**, which no simple key expresses directly. (A key does exist: repeat each string until it is long enough, `s * 10`, and sort descending. It works because the order of the repeated fractions matches.)

### The comparator contract

A valid comparator must behave like a real ordering:

1. **Antisymmetric**: `cmp(a, b)` and `cmp(b, a)` have opposite signs, and `cmp(a, a) == 0`.
2. **Transitive**: if `a` before `b` and `b` before `c`, then `a` before `c`.
3. **Equality is transitive**: if `a ~ b` and `b ~ c` then `a ~ c`.

If a comparator breaks these (rock-paper-scissors is the classic example), the sort does **not** raise an error. It just returns some order that depends on the algorithm and the input. These bugs are quiet and hard to find.

```python
from functools import cmp_to_key

beats = {("rock", "scissors"), ("scissors", "paper"), ("paper", "rock")}

def rps(a, b):
    if a == b:
        return 0
    return -1 if (a, b) in beats else 1


items = ["rock", "paper", "scissors"]
print(sorted(items, key=cmp_to_key(rps)))
print(sorted(items[::-1], key=cmp_to_key(rps)))
print(sorted(["paper", "scissors", "rock"], key=cmp_to_key(rps)))
```
```text
['scissors', 'paper', 'rock']
['scissors', 'paper', 'rock']
['rock', 'scissors', 'paper']
```

Three different input orders give three different "sorted" answers: there is no consistent order. A cycle means no sorting exists.

### Subtraction is a risky comparator

`return a - b` works for small integers, but it is fragile: with floats a tiny difference like `1e-20` is positive and fine, yet in languages with fixed-size integers `a - b` can overflow, and with huge Python ints it is just slow. The safe all-purpose form is:

```python
def cmp_numbers(a, b):
    return (a > b) - (a < b)

print(cmp_numbers(3, 5), cmp_numbers(5, 5), cmp_numbers(7, 5))
```
```text
-1 0 1
```

Booleans are `0` or `1`, so `(a > b) - (a < b)` is `-1`, `0` or `1`.

### Key design tricks

- **Several keys**: return a tuple, `key=lambda r: (r.age, r.name)`.
- **Descending number**: negate it, `key=lambda r: (-r.score, r.name)`.
- **Case-insensitive**: `key=str.lower` (or `str.casefold`).
- **Sort by a computed value**: `key=lambda p: p[0] ** 2 + p[1] ** 2` (distance from the origin).
- **Sort indices, not values**: `sorted(range(len(a)), key=lambda i: a[i])` gives the **argsort**: the positions that would sort `a`.
- **Missing values last**: `key=lambda x: (x is None, x)` puts `None` after the numbers (all `False` come before `True`, and `None` is never compared with a number).

```python
a = [30, 10, 20]
order = sorted(range(len(a)), key=lambda i: a[i])
print(order)
print([a[i] for i in order])
print(sorted([3, None, 1, 2, None], key=lambda x: (x is None, x if x is not None else 0)))
points = [(3, 4), (1, 1), (0, 2), (-2, 0)]
print(sorted(points, key=lambda p: p[0] ** 2 + p[1] ** 2))
```
```text
[1, 2, 0]
[10, 20, 30]
[1, 2, 3, None, None]
[(1, 1), (0, 2), (-2, 0), (3, 4)]
```

### Sorting without `<` between different types

Python refuses to compare incompatible types in a sort:

```python
try:
    sorted([3, "a", 1])
except TypeError as e:
    print("TypeError:", e)
```
```text
TypeError: '<' not supported between instances of 'str' and 'int'
```

Make sure every key compares with every other key. Convert, or add a type marker to a tuple key.

**Try it 12.** What does `sorted(["Bob", "alice", "Cy"], key=str.lower)` return? And without the key?

<details><summary>Answer</summary>

```python
print(sorted(["Bob", "alice", "Cy"], key=str.lower))
print(sorted(["Bob", "alice", "Cy"]))
```
```text
['alice', 'Bob', 'Cy']
['Bob', 'Cy', 'alice']
```

Uppercase letters come before lowercase in code point order, so the plain sort puts `alice` last.
</details>

## 16. Interval problems: sort first, then sweep

### What is an interval problem?

An **interval** is a range `[start, end]` on a line (times, positions, ids). Typical questions: which intervals overlap, merge them, how many are active at once, what is free?
Almost all of them are solved by one idea: **sort the intervals by start** (or by end), then walk through them once while remembering one or two numbers.

### First decision: are the ends included?

Before you write any code decide how **touching** intervals behave. Compare `[1, 2]` and `[2, 3]`:

- **Closed** intervals `[l, r]` include both ends. They share the point 2, so they **overlap** and merge into `[1, 3]`.
- **Half-open** intervals `[l, r)` exclude the end. A meeting from 1 to 2 and another from 2 to 3 do not overlap.

Always read the statement for this rule. It changes `<` to `<=` in one place, and a wrong choice fails exactly the edge cases the tests check. In this module every problem states the rule explicitly.

### Merge overlapping intervals

Sort by start. Keep the current merged block `[cl, cr]`. For the next interval `(l, r)`: if `l <= cr` they overlap (closed intervals), so extend the block with `cr = max(cr, r)`. Otherwise output the block and start a new one.

```python
def merge_intervals(intervals):
    intervals = sorted(intervals)
    out = []
    cl, cr = intervals[0]
    for l, r in intervals[1:]:
        if l <= cr:
            cr = max(cr, r)
        else:
            out.append((cl, cr))
            cl, cr = l, r
    out.append((cl, cr))
    return out


print(merge_intervals([(1, 3), (8, 10), (2, 6), (15, 18)]))
print(merge_intervals([(1, 2), (2, 3)]))
print(merge_intervals([(1, 10), (2, 3), (4, 5)]))
```
```text
[(1, 6), (8, 10), (15, 18)]
[(1, 3)]
[(1, 10)]
```

Why sort by start? After sorting, an interval can only overlap the **block just before it**: if it does not reach the current block, no later interval can reach back either (later starts are even further right).
Why `max`? The third example: after `[1, 10]` comes `[2, 3]`, which is nested; setting `cr = 3` would shrink the block. This single line is the most common bug.

Cost: `O(n log n)` for the sort, `O(n)` for the walk.

### Insert an interval into a sorted list

If the list is already sorted and non-overlapping, no sort is needed: three phases over one index. (1) Copy intervals that end **before** the new one starts. (2) Absorb all intervals that overlap it, growing the new interval. (3) Copy the rest. `O(n)`.

```python
def insert_interval(intervals, new):
    a, b = new
    out = []
    i = 0
    n = len(intervals)
    while i < n and intervals[i][1] < a:
        out.append(intervals[i])
        i += 1
    while i < n and intervals[i][0] <= b:
        a = min(a, intervals[i][0])
        b = max(b, intervals[i][1])
        i += 1
    out.append((a, b))
    while i < n:
        out.append(intervals[i])
        i += 1
    return out


print(insert_interval([(1, 2), (3, 5), (6, 7), (8, 10), (12, 16)], (4, 8)))
print(insert_interval([], (5, 7)))
print(insert_interval([(1, 5)], (6, 8)))
```
```text
[(1, 2), (3, 10), (12, 16)]
[(5, 7)]
[(1, 5), (6, 8)]
```

### Overlap check: can one person attend every meeting?

Meetings are half-open here. Sort by start; two meetings clash exactly when a meeting starts **before** the previous one ends.

```python
def can_attend(meetings):
    meetings = sorted(meetings)
    for i in range(1, len(meetings)):
        if meetings[i][0] < meetings[i - 1][1]:
            return False
    return True


print(can_attend([(0, 30), (5, 10), (15, 20)]))
print(can_attend([(7, 10), (2, 4), (4, 7)]))
```
```text
False
True
```

Why is comparing only neighbours enough? Suppose two meetings `i < j` clash, so `start[j] < end[i]`. Sorted by start we have `start[i + 1] <= start[j] < end[i]`, so meeting `i` clashes with its neighbour `i + 1` too: if any pair clashes, some neighbouring pair clashes. And if no neighbouring pair clashes, no pair does.

### Meeting rooms: how many at once?

The minimum number of rooms equals the largest number of meetings running at the same moment. Think of events: `+1` at every start, `-1` at every end. Sort starts and ends **separately** and sweep:

```python
def min_rooms(meetings):
    starts = sorted(s for s, e in meetings)
    ends = sorted(e for s, e in meetings)
    j = 0
    best = 0
    for i, s in enumerate(starts):
        while ends[j] <= s:
            j += 1
        best = max(best, i + 1 - j)
    return best


print(min_rooms([(0, 30), (5, 10), (15, 20)]))
print(min_rooms([(7, 10), (2, 4), (4, 7)]))
print(min_rooms([(1, 5), (1, 5), (1, 5)]))
```
```text
2
1
3
```

At start number `i` (0-based) exactly `i + 1` meetings have started; `j` of them have already ended (`ends[j] <= s`), so `i + 1 - j` are running. Using `<=` here is the half-open rule: a meeting that ends at `s` frees its room.
(You can drop the pairing of start with end because the *count* of running meetings only needs the two multisets.)

### Minimum arrows (balloons) and activity selection

**Balloons**: closed intervals `[xs, xe]`; one arrow at `x` bursts all balloons with `xs <= x <= xe`. Fewest arrows? **Greedy by right end**: the first balloon to end must be hit by some arrow; shooting at its right end gets the most extra balloons. Sort by `xe`; shoot when the next balloon starts after the last arrow.

```python
def min_arrows(balloons):
    arrows = 0
    last = float("-inf")
    for xs, xe in sorted(balloons, key=lambda b: b[1]):
        if xs > last:
            arrows += 1
            last = xe
    return arrows


print(min_arrows([(10, 16), (2, 8), (1, 6), (7, 12)]))
print(min_arrows([(1, 2), (2, 3)]))
```
```text
2
1
```

**Fewest intervals to remove so that the rest do not overlap**: same sort, same loop, but the "arrow" is an interval you **keep**. Keep the interval that ends first, skip every interval that starts before it ends; the answer is `n - kept`. This is the classical **activity selection** problem, and the proof is an *exchange argument*: if an optimal answer keeps another first interval, replacing it by the earliest-ending one never makes things worse.

```python
def min_removals(intervals):
    kept = 0
    last_end = float("-inf")
    for l, r in sorted(intervals, key=lambda x: x[1]):
        if l >= last_end:
            kept += 1
            last_end = r
    return len(intervals) - kept


print(min_removals([(1, 2), (2, 3), (3, 4), (1, 3)]))
```
```text
1
```

### Gaps and free time

The longest free stretch of a day: sort by start, keep the **furthest end so far**, and take the maximum of `start - furthest_end`. Do not forget the gap before the first meeting and after the last.

```python
def longest_gap(T, meetings):
    busy_until = 0
    best = 0
    for l, r in sorted(meetings):
        best = max(best, l - busy_until)
        busy_until = max(busy_until, r)
    return max(best, T - busy_until)


print(longest_gap(20, [(2, 5), (4, 9), (12, 14)]))
print(longest_gap(10, [(0, 10)]))
```
```text
6
0
```

### Which sort key?

| Question | Sort by | Keep while sweeping |
|---|---|---|
| Merge overlapping intervals | start | current block end (max) |
| Can one person attend all? | start | previous end |
| How many rooms? | starts and ends separately | running count |
| Fewest arrows, fewest removals | **end** | last arrow / last kept end |
| Free time, gaps | start | furthest end so far |
| Insert into sorted list | already sorted | three phases |

A good habit: write the answer for `[1, 2], [2, 3]` (touching), for a nested interval and for an empty input **before** you code.

**Try it 13.** Merge `[(1, 4), (4, 5)]` as closed intervals, and then decide whether two half-open meetings `(1, 4)` and `(4, 5)` clash.

<details><summary>Answer</summary>

```python
def merge_intervals(intervals):
    intervals = sorted(intervals)
    out = []
    cl, cr = intervals[0]
    for l, r in intervals[1:]:
        if l <= cr:
            cr = max(cr, r)
        else:
            out.append((cl, cr)); cl, cr = l, r
    out.append((cl, cr))
    return out

print(merge_intervals([(1, 4), (4, 5)]))
print("clash:", 4 < 4)
```
```text
[(1, 5)]
clash: False
```

Closed intervals sharing the point 4 merge into `[1, 5]`. For half-open meetings the second starts at 4, which is **not before** the end 4, so they do not clash.
</details>

## 17. Which tool? A decision guide

| Situation | Use |
|---|---|
| Normal program, anything sortable | `sorted` / `list.sort()` with `key=` |
| Need stable multi-key order | tuple key, or several stable passes |
| Tiny list (under about 20) or nearly sorted | insertion sort |
| Must write a sort, want guaranteed `O(n log n)`, stability | merge sort |
| Must write a sort, in place, fast on average | quick sort with random pivot (three-way if duplicates) |
| Guaranteed `O(n log n)` and `O(1)` memory | heap sort |
| Keys are small integers (range about `n`) | counting sort |
| Large fixed-width integers or equal-length strings | radix sort |
| Only the `k`-th element, or the top `k` | quickselect or `heapq.nlargest` |
| Few writes allowed | selection sort |
| Count inversions or "pairs across halves" | merge sort with counting |
| Intervals | sort by start (merge, gaps, overlap) or by end (greedy selection) |

Three questions to ask: **Is the data in memory? Are the keys small integers? Is stability required?** Most answers follow.

## 18. Common traps

1. `a = a.sort()`: `sort` returns `None`.
2. Sorting strings that hold numbers: `"10" < "9"`. Convert to `int` first.
3. `reverse=True` is not `[::-1]`: ties differ.
4. Negating a string key. Use two passes or `reverse=True`.
5. Merge sort: base case `len(a) == 0` only; forgetting leftovers; `<` instead of `<=`; `a[mid + 1:]`.
6. Quick sort: last-element pivot on sorted data (quadratic, `RecursionError`); two-way partition on many equal values; not swapping the chosen pivot to `hi` before Lomuto.
7. Insertion sort: testing `a[j] > key` before `j >= 0`.
8. Dutch flag: advancing `i` after swapping with the right end.
9. Counting sort: table of size `k` instead of `k + 1`; using it when `k` is gigantic.
10. Radix sort: unstable bucket pass; iterating from the most significant digit.
11. Comparators: returning `True/False`; non-transitive rules; `a - b` on floats.
12. Intervals: forgetting `max` when merging; `<` versus `<=` at touching ends; not sorting first; forgetting the last block; array of size `10^9`.
13. Using `pop(0)` or `insert(0, x)` inside a sort: each is `O(n)`.
14. Comparing keys of different types: `TypeError`.
15. Assuming "sorted input" is a harmless test: it is the worst case for naive quick sort.

## 19. Summary

- Sorting is the cheapest way to make a hard problem easy: **sort, then sweep**.
- Comparison sorts cannot beat `n log2 n` (there are `n!` orders; each comparison halves what you know at most).
- Python: `sorted` and `.sort()`, `key=`, `reverse=`, stable Timsort. `.sort()` returns `None`.
- Bubble, selection, insertion: `O(n^2)`; insertion is the one to keep (small or nearly sorted data, `O(n + inversions)`); selection writes least; none is for big data.
- **Merge sort**: split, sort halves, merge with two pointers. `O(n log n)` always, `O(n)` memory, stable. Counting inversions rides on the merge.
- **Quick sort**: partition around a pivot (Lomuto or Hoare), recurse on both sides. Fast on average, in place, not stable. Use a **random** pivot and a **three-way** partition. Quickselect finds the k-th element in expected `O(n)`.
- **Heap sort**: build a max-heap in `O(n)`, then extract the maximum `n - 1` times. `O(n log n)`, `O(1)` memory, not stable.
- **Counting sort** and **radix sort** avoid comparisons: `O(n + k)` and `O(d(n + b))`, for small integer keys; radix needs a **stable** pass per digit.
- **Stability** keeps equal keys in input order; it makes multi-key sorting from several passes possible (least important key first).
- **Comparators** (`cmp_to_key`) must be antisymmetric and transitive. Prefer key tuples.
- **Intervals**: decide whether touching counts; sort by start to merge and find gaps; sort by end for greedy selection; sort starts and ends separately for "how many at once".

## 20. How this chapter maps to the problems

| Section | Problems |
|---|---|
| 1-2 Why sorting, Python sorting | p001, p002, p009, p012 |
| 4 Bubble | p003, p014 |
| 5 Selection | p004 |
| 6 Insertion, 7 comparison | p005, p006, p007 |
| 8 Merge sort | p008, p010, p015, p030, p039 |
| 9 Inversions | p016, p038 |
| 10 Quick sort | p013, p017, p023, p024, p037 |
| 11 Heap sort | p022, p025 |
| 12 Counting sort | p026, p027 |
| 13 Radix sort | p028, p029 |
| 14 Stability | p011, p035 |
| 15 Comparators and keys | p021, p034, p039 |
| 16 Intervals | p018, p019, p020, p031, p032, p033, p040 |
| 1 Lower bound | p036 |

Assessment problems: **explain** p036 (and p007, p011, p024, p034), **trace** p023, **fix** p030, **build** p039.

## 21. Learning outcomes checklist

- [ ] I can write merge sort from memory, with a correct base case and a stable merge.
- [ ] I can write quick sort from memory with a Lomuto partition, and explain why a random pivot and a three-way split are needed.
- [ ] I can trace bubble, selection and insertion sort by hand and count swaps, shifts and passes.
- [ ] I can build a heap with sift-down and use it to sort.
- [ ] I can explain why counting sort and radix sort are not bound by `n log n` and when they cannot be used.
- [ ] I know which sorts are stable and why stability matters for multi-key sorting.
- [ ] I can sort with `key=` (tuples, negation) and know when a comparator is needed and what makes it valid.
- [ ] I can count inversions with merge sort.
- [ ] I decide the touching rule for intervals first, then solve merge, insert, overlap, rooms, arrows, and gaps by sorting first.
- [ ] I can find the k-th element with quickselect.

## 22. Further reading

- Python docs: *Sorting HOW TO* (key functions, stability, `cmp_to_key`) and the `heapq` module page.
- Tim Peters' notes on Timsort (`listsort.txt` in the CPython source).
- Cormen, Leiserson, Rivest, Stein: *Introduction to Algorithms*, chapters on heapsort, quicksort, and sorting in linear time.
- Sedgewick and Wayne: *Algorithms*, chapter 2 (three-way quicksort, stability).
- Skiena: *The Algorithm Design Manual*, the sorting chapter and the war stories.
- Practice sets: the problems in `external.toml` (LeetCode intervals and sorting lists, CSES *Sorting and Searching*).
