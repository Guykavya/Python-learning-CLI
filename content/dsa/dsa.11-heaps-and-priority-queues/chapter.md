# dsa.11 Heaps and priority queues

## 1. "Give me the smallest one, again and again"

In a hospital emergency room, patients do not wait in the order they arrive. The nurse always calls the **most urgent** one next. A new patient with a broken arm can wait; a new patient who has stopped breathing goes first. The waiting room is not a queue (first come, first served) and not a stack (last in, first out). It is a **priority queue**: every item has a priority, and the item that comes out is always the one with the **best priority**.

A priority queue has just three jobs:

1. **push** an item with its priority,
2. **pop** the item with the best priority (the smallest number, or the largest, depending on the problem),
3. **peek** at the best item without removing it.

Many problems are secretly this: "the next task to run", "the nearest unvisited city" (Dijkstra, in the graphs module), "the K largest scores", "the median of a stream of numbers", "merge K sorted files". Whenever you catch yourself writing *"find the minimum, remove it, then find the minimum again"* in a loop, you need a heap.

### Why not a plain list?

Compare the obvious choices for a priority queue holding `n` items:

| Structure | push | pop the smallest | peek |
|---|---|---|---|
| Unsorted list | `O(1)` | `O(n)` (scan for the minimum) | `O(n)` |
| Sorted list | `O(n)` (shift to insert in place) | `O(1)` from the end, or `O(n)` from the front | `O(1)` |
| Balanced search tree (dsa.10) | `O(log n)` | `O(log n)` | `O(log n)` |
| **Binary heap** | `O(log n)` | `O(log n)` | **`O(1)`** |

A balanced tree is as fast but heavy to build and keep balanced. The **binary heap** gets the same `O(log n)` with a much simpler structure: **a plain list** and two tiny loops. That simplicity is why almost every standard library offers a heap and not a tree for priority queues.

### What you can do after this module

1. **Explain the heap property and the array layout**, and write push, pop and `heapify` from scratch.
2. **Use Python's `heapq`**: min-heaps, max-heaps by negation, tuples as priorities, and the tie-breaker trap.
3. **Solve top-K problems** in `O(n log k)`: the K largest, the K most frequent, the K closest points.
4. **Keep a running median** with two heaps.
5. **Merge K sorted lists** or streams, and explore "smallest pairs" lazily.
6. **Schedule and simulate** with a heap, and handle updates and removals with **lazy deletion**.
7. **Recognise when a heap is the right tool**, and when it is not.

### A first look

Python's `heapq` module turns a plain list into a heap.

```python
import heapq

tasks = []
heapq.heappush(tasks, (3, "write report"))
heapq.heappush(tasks, (1, "fix the bug"))
heapq.heappush(tasks, (2, "reply to mail"))
print(tasks[0])                       # peek: the smallest priority number
while tasks:
    print(heapq.heappop(tasks))
```
```text
(1, 'fix the bug')
(1, 'fix the bug')
(2, 'reply to mail')
(3, 'write report')
```

The tasks come out in order of their number, whatever order we pushed them in. Priority `1` is "most urgent" here: `heapq` always gives the **smallest** item first.

## 2. What a heap is

A **binary heap** is a binary tree (dsa.10) with two rules.

1. **Shape rule:** it is a **complete** tree. Every level is full except possibly the last, and the last level is filled from the left. (No gaps.)
2. **Order rule (the heap property):** every node is **less than or equal to** its children. This is a **min-heap**. (For a **max-heap**, every node is greater than or equal to its children.)

```text
            1
          /   \
         3     2        Each parent is <= its children.
        / \   / \       1 <= 3, 1 <= 2, 3 <= 7, 3 <= 4, 2 <= 5, 2 <= 6.
       7   4 5   6
```

Two consequences:

- **The smallest item is always at the root.** Every other item has a chain of smaller-or-equal items above it, ending at the root. So peeking is `O(1)`.
- **A heap is NOT sorted.** Look at the tree: `3` is on the left, `2` on the right; `7` and `4` are below `3`. There is no left-to-right order. The heap guarantees only parent versus child, never left versus right or one level versus the next. This weak promise is exactly what makes it cheap to maintain.

### The array layout

Because the tree is complete, we need no node objects and no pointers. We store the nodes level by level in a list, as you saw in dsa.10:

```text
index:   0   1   2   3   4   5   6
value: [ 1,  3,  2,  7,  4,  5,  6 ]

children of i : 2*i + 1  and  2*i + 2
parent of i   : (i - 1) // 2
```

Check with the picture: the children of index `1` (value `3`) are at `3` and `4` (values `7` and `4`) ✓; the parent of index `5` (value `5`) is `(5 - 1) // 2 = 2` (value `2`) ✓.

```python
import heapq
import random

def parent(i):
    return (i - 1) // 2

def left(i):
    return 2 * i + 1

def right(i):
    return 2 * i + 2

def is_min_heap(a):
    """True if every item is >= its parent."""
    return all(a[parent(i)] <= a[i] for i in range(1, len(a)))

samples = {
    "the heap in the picture": [1, 3, 2, 7, 4, 5, 6],
    "a sorted list": [1, 2, 3, 4, 5, 6, 7],
    "a reversed list": [7, 6, 5, 4, 3, 2, 1],
    "one child too small": [1, 5, 2, 3, 4, 6, 7],
}
for name, a in samples.items():
    print(f"{name:26} {a} -> {is_min_heap(a)}")
```
```text
the heap in the picture    [1, 3, 2, 7, 4, 5, 6] -> True
a sorted list              [1, 2, 3, 4, 5, 6, 7] -> True
a reversed list            [7, 6, 5, 4, 3, 2, 1] -> False
one child too small        [1, 5, 2, 3, 4, 6, 7] -> False
```

Notice two things. A **sorted list is always a valid min-heap** (each item is at least as big as the one before it, so also as big as its parent). But a valid heap is **not** necessarily sorted (the first one). And `[1, 5, 2, 3, 4, 6, 7]` fails: index `3` (value `3`) has its parent at index `1` (value `5`), and `5 > 3`.

Why is the complete shape so useful? A complete tree with `n` nodes has height `floor(log2(n)) + 1`, so every path from the root to a leaf is short: about `log2 n` steps. A million items need a height of 20. And a complete tree has no gaps, so the list has no holes.

### Heap or binary search tree?

| | Binary search tree | Heap |
|---|---|---|
| Rule | left subtree < node < right subtree | parent <= children |
| Inorder traversal | sorted | not meaningful |
| Find any value | `O(log n)` if balanced | `O(n)` (no left/right rule to guide you) |
| Find the minimum | `O(log n)` | `O(1)` |
| Find the maximum | `O(log n)` | `O(n)` (it is among the leaves) |
| Memory | node objects with pointers | one flat list |

A heap is **specialised**: it answers "what is the smallest?" extremely well and almost nothing else. If you need to search for arbitrary values, or iterate in sorted order, use a tree or a sorted list. If you only repeatedly need the best item, the heap is simpler and faster.

A **max-heap** mirrors everything: the largest is at the root. Python's `heapq` provides only the min-heap; we get a max-heap by storing negative numbers (section 5).

## 3. Push and pop

Both operations must keep the two rules. The shape rule is kept by touching only the **end** of the list. The order rule is repaired by moving one item along a single root-to-leaf path: **sifting**.

### Push: add at the end, sift up

1. Append the new item at the end of the list. (This keeps the tree complete: it is the next free place in the last level.)
2. The new item may be smaller than its parent, so the order rule may be broken. While the item is smaller than its parent, **swap** them. The item *moves up*.

It stops when the item is not smaller than its parent, or when it reaches the root. At most `log n` swaps.

### Pop: take the root, move the last item up, sift down

1. The smallest is the root, `a[0]`; remember it to return.
2. Removing the root leaves a hole at the top. The only way to keep the shape is to take the **last** item of the list and put it into the root.
3. That item is probably too big for the root, so the order rule may be broken. While it is bigger than one of its children, **swap it with the smaller child**. It *moves down*. (We use the **smaller** child, so that the new parent is not bigger than the other child.)

It stops when the item is not bigger than its children, or when it becomes a leaf. At most `log n` swaps.

```python
def sift_up(a, i):
    """Move a[i] up until it is not smaller than its parent."""
    while i > 0:
        p = parent(i)
        if a[i] < a[p]:
            a[i], a[p] = a[p], a[i]
            i = p
        else:
            break

def sift_down(a, i, n):
    """Move a[i] down until it is not bigger than its children (only a[:n] counts)."""
    while True:
        smallest = i
        l, r = left(i), right(i)
        if l < n and a[l] < a[smallest]:
            smallest = l
        if r < n and a[r] < a[smallest]:
            smallest = r
        if smallest == i:
            break                              # both children are bigger: done
        a[i], a[smallest] = a[smallest], a[i]
        i = smallest

def push(a, x):
    a.append(x)
    sift_up(a, len(a) - 1)

def pop(a):
    top = a[0]
    last = a.pop()                             # raises IndexError on an empty list
    if a:
        a[0] = last
        sift_down(a, 0, len(a))
    return top

heap = []
for x in (5, 3, 8, 1, 9, 2):
    push(heap, x)
    print(f"push {x}: {heap}")
print("pop ->", pop(heap), heap)
print("pop ->", pop(heap), heap)
```
```text
push 5: [5]
push 3: [3, 5]
push 8: [3, 5, 8]
push 1: [1, 3, 8, 5]
push 9: [1, 3, 8, 5, 9]
push 2: [1, 3, 2, 5, 9, 8]
pop -> 1 [2, 3, 8, 5, 9]
pop -> 2 [3, 5, 8, 9]
```

Follow the first lines. After `5, 3`: pushing `3` appends it after `5`; `3 < 5` so they swap: `[3, 5]`. Pushing `8` appends it as the right child of `3`: `8 >= 3`, so it stays. Pushing `1` appends it at index 3, whose parent is index 1 (value `5`): swap; its new parent is index 0 (value `3`): swap again; it is the root. That is the "bubbling up" that gives `sift_up` its name.

### Watch a pop in detail

```python
def pop_traced(a):
    print("start        ", a)
    top = a[0]
    last = a.pop()
    print(f"remove root {top}, move last item {last} to the root")
    if a:
        a[0] = last
        i, n = 0, len(a)
        print("             ", a)
        while True:
            smallest = i
            l, r = left(i), right(i)
            if l < n and a[l] < a[smallest]:
                smallest = l
            if r < n and a[r] < a[smallest]:
                smallest = r
            if smallest == i:
                break
            print(f"swap {a[i]} with the smaller child {a[smallest]}")
            a[i], a[smallest] = a[smallest], a[i]
            i = smallest
            print("             ", a)
    return top

h = [1, 3, 2, 7, 4, 5, 6]
print("returned", pop_traced(h))
print("is a heap:", is_min_heap(h))
```
```text
start         [1, 3, 2, 7, 4, 5, 6]
remove root 1, move last item 6 to the root
              [6, 3, 2, 7, 4, 5]
swap 6 with the smaller child 2
              [2, 3, 6, 7, 4, 5]
swap 6 with the smaller child 5
              [2, 3, 5, 7, 4, 6]
returned 1
is a heap: True
```

The last item `6` came to the root, and then it sank twice. First it swapped with `2`, the smaller of its two children (`3` and `2`). Then it swapped with `5`, the only child of its new position. After that it was a leaf, so it stopped. The remaining list is again a valid heap, although not sorted. We always choose the **smaller** child: if we swapped with the bigger one (`3`), the smaller child (`2`) would end up below a bigger parent and break the rule.

### A `MinHeap` class

Wrapping the functions in a class gives a clean interface.

```python
class MinHeap:
    def __init__(self):
        self._data = []

    def push(self, x):
        self._data.append(x)
        sift_up(self._data, len(self._data) - 1)

    def pop(self):
        if not self._data:
            raise IndexError("pop from an empty heap")
        top = self._data[0]
        last = self._data.pop()
        if self._data:
            self._data[0] = last
            sift_down(self._data, 0, len(self._data))
        return top

    def peek(self):
        if not self._data:
            raise IndexError("peek at an empty heap")
        return self._data[0]

    def __len__(self):
        return len(self._data)

    def __repr__(self):
        return f"MinHeap({self._data})"

h = MinHeap()
for x in (4, 1, 7, 3):
    h.push(x)
print(h, h.peek(), len(h))
print([h.pop() for _ in range(len(h))])
```
```text
MinHeap([1, 3, 7, 4]) 1 4
[1, 3, 4, 7]
```

### Is it right? A differential test

Compare with `heapq`. One subtlety: two **different** valid heaps can hold the same items (the heap is not unique), and `heapq` uses a slightly different pop method, so the internal lists may differ. What must be identical is the **sequence of values popped**, and after every step our list must satisfy the heap property.

```python
import heapq
import random

rng = random.Random(11)
ok = True
mine, model = MinHeap(), []
for _ in range(4000):
    if model and rng.random() < 0.45:
        ok &= mine.pop() == heapq.heappop(model)
    else:
        x = rng.randint(0, 50)                 # many equal values
        mine.push(x)
        heapq.heappush(model, x)
    ok &= is_min_heap(mine._data) and len(mine) == len(model)
    ok &= (mine.peek() == model[0]) if model else True
print("4000 random push/pop steps: same values as heapq, always a valid heap:", bool(ok))
```
```text
4000 random push/pop steps: same values as heapq, always a valid heap: True
```

**Predict the output 1.** Push `4, 2, 6, 1` into an empty min-heap one by one. What is the list at the end?

<details><summary>Answer</summary>

```python
h = []
for x in (4, 2, 6, 1):
    push(h, x)
print(h)
```
```text
[1, 2, 6, 4]
```

`[4]`; push `2`: it goes after `4`, `2 < 4`, swap: `[2, 4]`; push `6`: appended at index 2 (parent index 0, value `2`), stays: `[2, 4, 6]`; push `1`: appended at index 3, whose parent is index 1 (value `4`): swap; then its parent is index 0 (value `2`): swap. Result `[1, 2, 6, 4]`.

</details>

**Try it 1.** Write `replace_top(a, x)` that removes the smallest item and inserts `x` **in one sift** (no separate pop and push), returning the old smallest. What is the cost, and when is it useful?

<details><summary>Answer</summary>

```python
def replace_top(a, x):
    top = a[0]
    a[0] = x                         # put the new item into the root ...
    sift_down(a, 0, len(a))          # ... and let it sink to its place
    return top

h = []
for v in (5, 3, 8, 1, 9):
    push(h, v)
print(h)
print(replace_top(h, 7), h, is_min_heap(h))
```
```text
[1, 3, 8, 5, 9]
1 [3, 5, 8, 7, 9] True
```

One `sift_down`: `O(log n)`, and the list size does not change, so there is no append or removal of the last element. This is exactly what `heapq.heapreplace` does. It is useful whenever the heap must stay at a fixed size, as in the top-K algorithm of section 7. Note the difference from "push then pop": `replace_top` removes the **old** smallest even if `x` is smaller. (The related `heappushpop` pushes first and pops second, so it may return `x` itself.)

</details>

## 4. Building a heap: `heapify` and why it costs only `O(n)`

You have `n` items in a list and you want a heap. The obvious way is to push them one by one: `n` pushes of `O(log n)` each, so `O(n log n)`. There is a smarter way that takes `O(n)`.

### Bottom-up heapify

Look at the array. Half of the items (the second half of the list) are **leaves**: they have no children, so each of them is already a valid one-item heap. Go through the other items **from the last parent back to the root**, and call `sift_down` on each. By the time you reach an item, both subtrees below it are already heaps, so a single `sift_down` makes the whole subtree a heap.

The index of the last parent is `n // 2 - 1` (the parent of the last item).

```python
def heapify(a):
    n = len(a)
    for i in range(n // 2 - 1, -1, -1):      # from the last parent up to the root
        sift_down(a, i, n)

a = [9, 5, 8, 2, 7, 1, 6, 3]
heapify(a)
print(a, is_min_heap(a))
b = list(range(10, 0, -1))
heapify(b)
print(b, is_min_heap(b))
```
```text
[1, 2, 6, 3, 7, 8, 9, 5] True
[1, 2, 4, 3, 6, 5, 8, 10, 7, 9] True
```

### Why `O(n)` and not `O(n log n)`?

A `sift_down` from a node costs at most the **height of that node**, not `log n`. Most nodes are near the bottom, where the height is tiny:

- about `n / 2` nodes are leaves (height 0, no work),
- about `n / 4` nodes have height 1 (at most 1 swap),
- about `n / 8` nodes have height 2 (at most 2 swaps), and so on,
- only the root has height `log n`.

The total is `n/4 * 1 + n/8 * 2 + n/16 * 3 + ...`, and this series adds up to at most `n`. The expensive nodes are few; the cheap nodes are many.

Let us count it. We wrap numbers in a class that counts every `<` comparison, then run both methods on the same data. Two kinds of data: random, and the worst case for pushing one by one (descending numbers: each new item is the smallest so far, so it rises all the way to the root).

```python
class Counted:
    comparisons = 0
    def __init__(self, v):
        self.v = v
    def __lt__(self, other):
        Counted.comparisons += 1
        return self.v < other.v

def work_push(values):
    Counted.comparisons = 0
    a = []
    for v in values:
        push(a, Counted(v))
    return Counted.comparisons

def work_heapify(values):
    Counted.comparisons = 0
    a = [Counted(v) for v in values]
    heapify(a)
    return Counted.comparisons
```

```python
rng = random.Random(3)
print(f"{'n':>7} {'data':>11} {'n pushes':>10} {'heapify':>9}")
for n in (1000, 10000, 100000):
    random_data = [rng.random() for _ in range(n)]
    descending = list(range(n, 0, -1))
    for name, data in (("random", random_data), ("descending", descending)):
        print(f"{n:>7} {name:>11} {work_push(data):>10} {work_heapify(data):>9}")
```
```text
      n        data   n pushes   heapify
   1000      random       2238      1875
   1000  descending       7987      1982
  10000      random      22772     18832
  10000  descending     113631     19982
 100000      random     228401    188081
 100000  descending    1468946    199978
```

Read the table. `heapify` always uses fewer than `2n` comparisons: roughly proportional to `n`, whatever the data. Repeated `push` is also cheap on **random** data (a random item rarely climbs far), but on **descending** data every new item climbs to the root, and the work grows like `n log n`. So `heapify` is never worse, and sometimes much better.

This is also why `heapq.heapify(list)` is the right way to turn an existing list into a heap, and why "push everything, then pop everything" for sorting costs `O(n log n)` mainly because of the pops.

**Predict the output 2.** After `heapify([4, 10, 3, 5, 1])`, what is the list? (Work from the last parent.)

<details><summary>Answer</summary>

```python
a = [4, 10, 3, 5, 1]
heapify(a)
print(a)
```
```text
[1, 4, 3, 5, 10]
```

There are 5 items, so the last parent is at index `5 // 2 - 1 = 1` (value `10`). Its children are `5` and `1`: swap with the smaller, `1`: `[4, 1, 3, 5, 10]`. Next the root `4`: its children are `1` and `3`; the smaller is `1`, swap: `[1, 4, 3, 5, 10]`; then `4` at index 1 has children `5` and `10`, both larger: stop. The result is a valid heap whose root is the minimum, `1`.

</details>

**Try it 2.** Why does the loop in `heapify` go **backwards** (from the last parent to the root)? What would go wrong if it went forwards from the root?

<details><summary>Answer</summary>

`sift_down(a, i, n)` assumes that the subtrees below `a[i]` are already heaps; it only repairs `a[i]` itself. Going backwards guarantees this: when we reach index `i`, all the indices after it (its descendants) have already been processed. Going forwards, we would fix the root first while its children's subtrees are still arbitrary; the root would sink into a subtree that is not a heap yet, and the later fixes could leave a smaller item below a bigger one higher up.

```python
def heapify_forward(a):
    n = len(a)
    for i in range(n // 2):                 # root first: wrong
        sift_down(a, i, n)

a = [9, 8, 7, 6, 5, 4, 3, 2, 1]
heapify_forward(a)
print(a, is_min_heap(a))
```
```text
[7, 5, 3, 1, 8, 4, 9, 2, 6] False
```

</details>

## 5. Python's `heapq`

In real programs you do not write your own heap; you use the standard library's `heapq`. It is fast (written in C) and it works on an ordinary `list`. There is no `Heap` class: **a heap is just a list that obeys the heap property**, and the functions of `heapq` keep it that way.

| Function | What it does | Cost |
|---|---|---|
| `heapq.heapify(lst)` | turn a list into a min-heap, in place | `O(n)` |
| `heapq.heappush(heap, x)` | add `x` | `O(log n)` |
| `heapq.heappop(heap)` | remove and return the smallest | `O(log n)` |
| `heap[0]` | peek at the smallest (no function needed) | `O(1)` |
| `heapq.heappushpop(heap, x)` | push `x`, then pop the smallest (faster than the two calls) | `O(log n)` |
| `heapq.heapreplace(heap, x)` | pop the smallest, then push `x` | `O(log n)` |
| `heapq.nsmallest(k, iterable, key=None)` | the `k` smallest items, in order | `O(n log k)` |
| `heapq.nlargest(k, iterable, key=None)` | the `k` largest items, in order | `O(n log k)` |
| `heapq.merge(*sorted_iterables, key=None)` | merge sorted inputs lazily | `O(log k)` per item |

```python
import heapq

heap = [9, 4, 7, 1, 8, 2]
heapq.heapify(heap)
print(heap, heap[0])                       # a valid heap: NOT sorted
heapq.heappush(heap, 0)
print(heap)
print([heapq.heappop(heap) for _ in range(len(heap))])
```
```text
[1, 4, 2, 9, 8, 7] 1
[0, 4, 1, 9, 8, 7, 2]
[0, 1, 2, 4, 7, 8, 9]
```

The list after `heapify` is `[1, 4, 2, 9, 8, 7]`: the smallest is first, but the rest is in heap order, not sorted order. The only thing you may rely on is `heap[0]`. To get sorted output you must **pop** items one by one (or call `sorted`). Printing a heap and expecting sorted values is a very common surprise.

An empty heap raises `IndexError` for both `heap[0]` and `heappop`. Check `if heap:` first.

### `heappushpop` against `heapreplace`

These two look alike and differ in the order of the steps. `heappushpop(h, x)` pushes `x` **first** and pops afterwards, so if `x` is smaller than everything, it comes straight back. `heapreplace(h, x)` pops **first**, so it always returns the old smallest and always inserts `x`, even if `x` is smaller.

```python
h1 = [2, 3, 5]
print(heapq.heappushpop(h1, 1), h1)      # pushed 1, popped 1: the heap is unchanged

h2 = [2, 3, 5]
print(heapq.heapreplace(h2, 1), h2)      # popped 2, pushed 1: the heap changed
```
```text
1 [2, 3, 5]
2 [1, 3, 5]
```

### A max-heap: negate the numbers

`heapq` has only a min-heap. To get the **largest** first, store the **negatives**: the smallest negative number is the largest original number. Negate again when you take items out.

```python
nums = [5, 1, 8, 3]
max_heap = [-x for x in nums]
heapq.heapify(max_heap)
print(-max_heap[0])                       # peek: the largest
print([-heapq.heappop(max_heap) for _ in range(len(nums))])
```
```text
8
[8, 5, 3, 1]
```

The classic bug is forgetting one of the two minus signs: on push or on pop. For objects that cannot be negated (strings, or tuples), use a small wrapper whose `<` is reversed:

```python
class Reversed:
    """Makes the heap treat a larger value as 'smaller'."""
    def __init__(self, value):
        self.value = value
    def __lt__(self, other):
        return other.value < self.value

h = [Reversed(w) for w in ("pear", "apple", "mango", "fig")]
heapq.heapify(h)
print([heapq.heappop(h).value for _ in range(4)])
```
```text
['pear', 'mango', 'fig', 'apple']
```

Newer versions of Python (3.14 and later) add max-heap functions to the module: `heapq.heapify_max`, `heappush_max`, `heappop_max`, `heapreplace_max` and `heappushpop_max`. Code that must also run on older versions should keep using negation.

```python
print(hasattr(heapq, "heappush_max"))
```
```text
True
```

> Version note: the line above prints `True` on Python 3.14 and later, and `False` on older versions. This course uses negation, which works everywhere.

### Tuples as priorities, and the tie-breaker trap

A heap compares items with `<`. Python compares tuples **element by element**: first the first elements, and only if they are equal, the second ones. So `(priority, task)` works as a priority queue. But if two priorities are **equal**, Python compares the tasks, and if the tasks cannot be compared, the push fails.

```python
queue = []
heapq.heappush(queue, (1, {"name": "backup"}))
try:
    heapq.heappush(queue, (1, {"name": "email"}))
except TypeError as e:
    print("TypeError:", e)
```
```text
TypeError: '<' not supported between instances of 'dict' and 'dict'
```

The fix is to put a **tie-breaker** between the priority and the item: a counter that increases with every push. Two entries can then never be equal in the first two places, and the item is never compared. As a bonus, equal priorities come out in the order they went in (first in, first out).

```python
import itertools

counter = itertools.count()
queue = []
for priority, task in ((2, {"name": "backup"}), (1, {"name": "email"}), (2, {"name": "report"}), (1, {"name": "call"})):
    heapq.heappush(queue, (priority, next(counter), task))
while queue:
    priority, _, task = heapq.heappop(queue)
    print(priority, task["name"])
```
```text
1 email
1 call
2 backup
2 report
```

Inside the same priority, the output keeps the pushing order: `email` before `call`, `backup` before `report`.

### Do not change items inside the heap

The heap property is a promise about the whole list. If you change an item through its index, you can break the promise, and `heappop` will then return a wrong answer without any error.

```python
h = [1, 3, 2]
heapq.heapify(h)
h[0] = 10                                 # bypasses the heap functions
print(h, "valid heap:", is_min_heap(h))
print("heappop gives", heapq.heappop(h), "but the smallest item was 2")
```
```text
[10, 3, 2] valid heap: False
heappop gives 10 but the smallest item was 2
```

To change the smallest item, use `heapreplace`. To change any other item, you have two safe choices: rebuild with `heapify` (`O(n)`), or use the "lazy deletion" technique of section 11.

### `nsmallest`, `nlargest` and `merge`

```python
data = [5, 1, 9, 3, 7, 8, 2]
print(heapq.nlargest(3, data), heapq.nsmallest(3, data))
people = [("Asha", 31), ("Ben", 25), ("Chitra", 40), ("Dev", 19)]
print(heapq.nsmallest(2, people, key=lambda p: p[1]))
print(list(heapq.merge([1, 4, 9], [2, 3, 10], [0, 5])))
```
```text
[9, 8, 7] [1, 2, 3]
[('Dev', 19), ('Ben', 25)]
[0, 1, 2, 3, 4, 5, 9, 10]
```

`nsmallest` and `nlargest` accept a `key=` function. The documentation gives a rule of thumb about speed: for `k = 1` use `min` / `max`; for a `k` close to `n`, `sorted(data)[:k]` is faster; in between, `nlargest` / `nsmallest` win. `merge` takes inputs that are **already sorted** and returns a lazy iterator.

**Predict the output 3.** What do the three prints show?

```python
h = [4, 1, 7, 3]
heapq.heapify(h)
print(h[0])
print(heapq.heapreplace(h, 0))
print(heapq.heappushpop(h, 9), sorted(h))
```

<details><summary>Answer</summary>

```text
1
1
0 [3, 4, 7, 9]
```

After `heapify`, the smallest is `1`. `heapreplace(h, 0)` pops the old smallest (`1`) and pushes `0`. Now `heappushpop(h, 9)`: pushes `9` and pops the smallest, which is `0`. The heap holds `3, 4, 7, 9`.

</details>

**Try it 3.** Use `heapq` to sort `["pear", "fig", "apple", "kiwi"]` by length, ties in alphabetical order, without calling `sorted`. Which entries do you push?

<details><summary>Answer</summary>

```python
words = ["pear", "fig", "apple", "kiwi"]
h = [(len(w), w) for w in words]            # tuples compare length first, then the word
heapq.heapify(h)
print([heapq.heappop(h)[1] for _ in range(len(h))])
```
```text
['fig', 'kiwi', 'pear', 'apple']
```

The tuple `(len(w), w)` does the work: the length decides, and when the lengths are equal (`pear` and `kiwi`), the word decides. No tie-breaker counter is needed here, because the words themselves can be compared.

</details>

## 6. Heap sort

If you can always remove the smallest item in `O(log n)`, you can sort: put everything in a heap, then pop everything.

```python
def heap_sort_simple(items):
    h = list(items)
    heapq.heapify(h)                                   # O(n)
    return [heapq.heappop(h) for _ in range(len(h))]    # n pops of O(log n)

print(heap_sort_simple([5, 2, 9, 1, 5, 6]))
```
```text
[1, 2, 5, 5, 6, 9]
```

Time `O(n log n)`, and it needs `O(n)` extra space for the heap.

### In-place heap sort

The classic heap sort needs **no extra space**. Use a **max-heap** inside the array itself:

1. Build a max-heap from the array (bottom-up, as in section 4, but with the larger child).
2. The largest item is at index 0. **Swap it with the last item** of the heap part; now the largest is in its final place at the end. Shrink the heap by one, and `sift_down` the new root.
3. Repeat until the heap has one item.

The sorted part grows from the right and the heap part shrinks on the left, in the same array.

```python
def sift_down_max(a, i, n):
    while True:
        largest = i
        l, r = 2 * i + 1, 2 * i + 2
        if l < n and a[largest] < a[l]:
            largest = l
        if r < n and a[largest] < a[r]:
            largest = r
        if largest == i:
            break
        a[i], a[largest] = a[largest], a[i]
        i = largest

def heap_sort(a):
    n = len(a)
    for i in range(n // 2 - 1, -1, -1):        # phase 1: build a max-heap
        sift_down_max(a, i, n)
    for end in range(n - 1, 0, -1):            # phase 2: move the maximum to the end
        a[0], a[end] = a[end], a[0]
        sift_down_max(a, 0, end)               # the heap is now a[:end]
    return a

a = [4, 10, 3, 5, 1]
print(heap_sort(a))
```
```text
[1, 3, 4, 5, 10]
```

Watch the two phases on a small list:

```python
def heap_sort_traced(a):
    n = len(a)
    for i in range(n // 2 - 1, -1, -1):
        sift_down_max(a, i, n)
    print("max-heap built :", a)
    for end in range(n - 1, 0, -1):
        a[0], a[end] = a[end], a[0]
        sift_down_max(a, 0, end)
        print(f"after moving   : {a[:end]} | {a[end:]}")
    return a

heap_sort_traced([4, 10, 3, 5, 1])
```
```text
max-heap built : [10, 5, 3, 4, 1]
after moving   : [5, 4, 3, 1] | [10]
after moving   : [4, 1, 3] | [5, 10]
after moving   : [3, 1] | [4, 5, 10]
after moving   : [1] | [3, 4, 5, 10]
```

The bar `|` separates the heap (left) from the sorted tail (right). Each line moves the current maximum behind the bar.

### Check it

```python
rng = random.Random(5)
ok = True
for _ in range(500):
    data = [rng.randint(-5, 9) for _ in range(rng.randint(0, 15))]
    ok &= heap_sort(data[:]) == sorted(data)
    ok &= heap_sort_simple(data) == sorted(data)
print("500 random lists (many duplicates): both heap sorts agree with sorted():", bool(ok))
```
```text
500 random lists (many duplicates): both heap sorts agree with sorted(): True
```

### Heap sort is not stable

A **stable** sort keeps equal items in their original order (dsa.05). The swaps of heap sort jump over many items, so equal items can change places.

```python
class Item:
    def __init__(self, key, label):
        self.key, self.label = key, label
    def __lt__(self, other):                     # compare by key only
        return self.key < other.key
    def __repr__(self):
        return f"{self.key}{self.label}"

items = [Item(2, "a"), Item(1, "b"), Item(2, "c"), Item(1, "d"), Item(2, "e")]
print("heap sort   :", heap_sort(items[:]))
print("stable sort :", sorted(items))
```
```text
heap sort   : [1b, 1d, 2c, 2e, 2a]
stable sort : [1b, 1d, 2a, 2c, 2e]
```

Look at the labels of the items with the same key: `sorted` keeps them in the original order (`a, c, e` and `b, d`); heap sort does not.

| Sort | Time (worst) | Extra space | Stable |
|---|---|---|---|
| Heap sort | `O(n log n)` | `O(1)` in place | no |
| Merge sort | `O(n log n)` | `O(n)` | yes |
| Quick sort | `O(n^2)` (rare) | `O(log n)` | no |
| Python's `sorted` (Timsort) | `O(n log n)` | `O(n)` | yes |

Heap sort is the only one here that guarantees `O(n log n)` **and** `O(1)` extra space. In practice it is slower than quicksort or Timsort (it jumps around memory, which is bad for the CPU cache), so it is rarely your first choice. It is used as the "safety net" of **introsort**, the sort of C++'s `std::sort`: it starts as a quicksort and switches to heap sort when the recursion gets too deep.

## 7. Top-K problems

A very common task: from a large collection (or a stream that never ends), find the **K largest** (or smallest) items. Sorting everything costs `O(n log n)` and needs all the data in memory. A heap does it in `O(n log k)` with `O(k)` memory.

### The K largest: a min-heap of size K

This is the idea people find backwards, so read it slowly. To keep the **K largest** items seen so far, keep a **min-heap** of exactly `K` items. Why a *min*-heap? Its root is the **smallest of the K kept items**, which is exactly the one that must leave if a better candidate arrives.

For each new item `x`:

- if the heap has fewer than `K` items, push `x`;
- otherwise, if `x` is larger than the root `heap[0]` (the weakest of the K), replace the root with `x` (one `heapreplace`);
- otherwise, ignore `x`.

At the end, the heap holds the K largest items.

```python
def top_k_largest(nums, k):
    if k <= 0:
        return []                              # without this guard, heap[0] would fail on an empty heap
    heap = []
    for x in nums:
        if len(heap) < k:
            heapq.heappush(heap, x)
        elif x > heap[0]:
            heapq.heapreplace(heap, x)         # the weakest of the K leaves
    return sorted(heap, reverse=True)

print(top_k_largest([3, 1, 5, 12, 2, 11, 7], 3))
print(top_k_largest([4, 4, 4], 2), top_k_largest([1, 2], 5), top_k_largest([1, 2], 0))
```
```text
[12, 11, 7]
[4, 4] [2, 1] []
```

Note the first two lines: for `k = 0` the heap would stay empty, and the test `x > heap[0]` would raise `IndexError`. Always decide what the function does for `k = 0` and for `k` larger than the number of items (here the answer is simply all the items).

For the K **smallest**, mirror everything: a **max-heap** of size K (store negatives), replace the root when `x` is smaller. The same trick works for objects: push a tuple `(key, item)`.

### Why it is fast

Each item costs one comparison with `heap[0]`, `O(1)`. Only items that beat the current weakest cause a `heapreplace` of `O(log k)`. In random data, most items lose. We can count:

```python
import math

def count_replacements(nums, k):
    heap, replaced = [], 0
    for x in nums:
        if len(heap) < k:
            heapq.heappush(heap, x)
        elif x > heap[0]:
            heapq.heapreplace(heap, x)
            replaced += 1
    return replaced

rng = random.Random(9)
k = 10
for n in (1000, 10000, 100000):
    data = [rng.random() for _ in range(n)]
    print(f"n={n:>6}, k={k}: {count_replacements(data, k):>3} replacements; "
          f"estimate k*ln(n/k) = {round(k * math.log(n / k))}")
```
```text
n=  1000, k=10:  43 replacements; estimate k*ln(n/k) = 46
n= 10000, k=10:  66 replacements; estimate k*ln(n/k) = 69
n=100000, k=10:  90 replacements; estimate k*ln(n/k) = 92
```

In a random order, the number of replacements is about `k * ln(n / k)`: it grows only like the *logarithm* of `n`. A hundred thousand items cause only about a hundred expensive operations. (In the worst case, an increasing input, every item causes a replacement: `O(n log k)`.)

### Compare the approaches

| Method | Time | Space | Notes |
|---|---|---|---|
| Sort everything, take `k` | `O(n log n)` | `O(n)` | simplest to write |
| Heap of size `k` | `O(n log k)` | `O(k)` | works on a **stream**; best when `k` is small |
| `heapq.nlargest(k, data)` | `O(n log k)` | `O(k)` | the heap method, ready made |
| Quickselect | `O(n)` average | `O(1)` or `O(n)` | finds the k-th, not sorted; needs all data in memory |

### The K-th largest element in a stream

Keep the same min-heap of size `K`. After each new number, `heap[0]` is the K-th largest so far.

```python
class KthLargest:
    def __init__(self, k, nums):
        self.k = k
        self.heap = []
        for x in nums:
            self.add(x)

    def add(self, val):
        if len(self.heap) < self.k:
            heapq.heappush(self.heap, val)
        elif val > self.heap[0]:
            heapq.heapreplace(self.heap, val)
        return self.heap[0] if len(self.heap) == self.k else None   # None: fewer than k numbers yet

stream = KthLargest(3, [4, 5, 8, 2])
print([stream.add(v) for v in (3, 5, 10, 9, 4)])
print(KthLargest(3, [1]).add(2))
```
```text
[4, 5, 5, 8, 8]
None
```

Follow the first calls. After `4, 5, 8, 2` the heap keeps `4, 5, 8` (the `2` is too small), so the 3rd largest is `4`. Adding `3` changes nothing (`3` is smaller than `4`): the answer is still `4`. Adding `5` replaces `4`: the kept numbers are `5, 5, 8`, so the answer is `5`. Adding `10` replaces a `5`: the kept numbers are `5, 8, 10`, and the answer is again `5`. Adding `9` replaces `5`: the kept numbers are `8, 9, 10`, and the answer is `8`. Adding `4` changes nothing, so the answer stays `8`. The class returns `None` while it has fewer than `k` numbers, because then the K-th largest does not exist.

### The K most frequent words

Count with a dictionary (`Counter`, dsa.04), then pick the K best counts. We want the highest counts first and, for equal counts, alphabetical order. The sort key `(-count, word)` expresses it, and `nsmallest` with that key does the rest.

```python
from collections import Counter

def top_k_frequent(words, k):
    counts = Counter(words)
    best = heapq.nsmallest(k, counts.items(), key=lambda kv: (-kv[1], kv[0]))
    return [word for word, _ in best]

print(top_k_frequent(["i", "love", "leetcode", "i", "love", "coding"], 2))
print(top_k_frequent(["the", "day", "is", "sunny", "the", "the", "the", "sunny", "is", "is"], 4))
```
```text
['i', 'love']
['the', 'is', 'sunny', 'day']
```

Time `O(n + m log k)`, where `m` is the number of distinct words. A negative count turns "the biggest count" into "the smallest key", the same negation trick as the max-heap.

### The K closest points to the origin

The distance of a point `(x, y)` from the origin is `sqrt(x^2 + y^2)`. Comparing the **squared** distances gives the same order and avoids the square root and its rounding. We want the K *smallest* distances, so we use a **max-heap** of size K (negated squared distances).

```python
def k_closest(points, k):
    if k <= 0:
        return []
    heap = []                                       # entries: (-squared distance, x, y)
    for x, y in points:
        d = x * x + y * y
        if len(heap) < k:
            heapq.heappush(heap, (-d, x, y))
        elif -d > heap[0][0]:                       # closer than the farthest kept point
            heapq.heapreplace(heap, (-d, x, y))
    return [(x, y) for _, x, y in heap]

pts = [(3, 3), (5, -1), (-2, 4), (0, 1), (-1, -1)]
print(sorted(k_closest(pts, 2)))
```
```text
[(-1, -1), (0, 1)]
```

The two closest are `(0, 1)` with distance squared 1 and `(-1, -1)` with 2. The heap root is the **farthest** of the kept points, the one to throw away first, so the test is "is the new point closer than that?" A point never needs to be compared with all the others.

### Check the three against a sort

```python
rng = random.Random(15)
ok = True
for _ in range(500):
    data = [rng.randint(-20, 20) for _ in range(rng.randint(0, 25))]
    k = rng.randint(0, 8)
    ok &= top_k_largest(data, k) == sorted(data, reverse=True)[:k]
    pts = [(rng.randint(-6, 6), rng.randint(-6, 6)) for _ in range(rng.randint(0, 15))]
    mine = sorted(x * x + y * y for x, y in k_closest(pts, k))
    expected = sorted(x * x + y * y for x, y in pts)[:k]
    ok &= mine == expected                           # compare the distances: tied points may differ
    stream = KthLargest(k, []) if k else None
    if stream:
        seq = [stream.add(v) for v in data]
        ok &= all(seq[i] == (sorted(data[:i + 1], reverse=True)[k - 1] if i + 1 >= k else None)
                  for i in range(len(data)))
print("500 random inputs: top-K, k-closest and the K-th largest stream agree with sorting:", bool(ok))
```
```text
500 random inputs: top-K, k-closest and the K-th largest stream agree with sorting: True
```

We compare the **distances** for the closest points: two points can be equally far, and then more than one answer is correct. A test that compares the points themselves would reject a correct solution.

**Try it 4.** To find the K **smallest** numbers with `heapq` functions only (no negation), which of `nsmallest`, `nlargest` and `heappush` would you use? And if you must write the loop yourself, what heap and what comparison do you use?

<details><summary>Answer</summary>

`heapq.nsmallest(k, data)` does it directly. By hand, use a **max-heap** of size `k` (store `-x`): push while the size is below `k`; afterwards, if `x` is smaller than the current largest kept item (`-heap[0]`), replace the root.

```python
def top_k_smallest(nums, k):
    heap = []                                   # negated values: the root is the LARGEST kept
    for x in nums:
        if len(heap) < k:
            heapq.heappush(heap, -x)
        elif x < -heap[0]:
            heapq.heapreplace(heap, -x)
    return sorted(-v for v in heap)

print(top_k_smallest([3, 1, 5, 12, 2, 11, 7], 3), heapq.nsmallest(3, [3, 1, 5, 12, 2, 11, 7]))
```
```text
[1, 2, 3] [1, 2, 3]
```

The rule to remember: for the K *largest*, keep a *min*-heap; for the K *smallest*, keep a *max*-heap. The heap keeps the K candidates and puts the weakest one at the root, ready to be replaced.

</details>

## 8. Two heaps: the running median

The **median** of a collection is its middle value when sorted (for an even count, the average of the two middle values). Problem: numbers arrive one at a time, and after each one you must report the median.

Re-sorting each time costs `O(n log n)` per step. Keeping a sorted list and inserting costs `O(n)` per step. With **two heaps** each step costs `O(log n)`, and reading the median costs `O(1)`.

### The idea

Split the numbers into a **lower half** and an **upper half**:

- the lower half lives in a **max-heap** (its root is the largest of the small numbers),
- the upper half lives in a **min-heap** (its root is the smallest of the big numbers).

The two roots sit right next to the middle of the sorted order. If we keep the halves balanced, the median is made of those two roots.

```text
 lower half (max-heap)      upper half (min-heap)
   1  2  3  [4]          |     [5]  6  8  9
           top = 4              top = 5
                  median = (4 + 5) / 2
```

The invariants (the rules that must hold after every step):

1. every number in the lower half is `<=` every number in the upper half,
2. the sizes differ by at most one; we keep the **lower half the larger** one: `len(low) == len(high)` or `len(low) == len(high) + 1`.

Then: if the sizes are equal, the median is the average of the two tops; otherwise it is the top of the lower half.

### Adding a number

A neat way to keep both invariants in three lines:

1. push the new number into the **lower** half;
2. move the largest of the lower half to the **upper** half (this guarantees invariant 1: no number in the lower half is bigger than any number in the upper half);
3. if the upper half became bigger than the lower half, move its smallest back to the lower half (this restores the sizes).

```python
class MedianFinder:
    def __init__(self):
        self.low = []                              # max-heap (stored as negatives)
        self.high = []                             # min-heap

    def add(self, x):
        heapq.heappush(self.low, -x)
        heapq.heappush(self.high, -heapq.heappop(self.low))      # the largest of low goes up
        if len(self.high) > len(self.low):
            heapq.heappush(self.low, -heapq.heappop(self.high))  # rebalance: smallest of high comes back

    def median(self):
        if len(self.low) > len(self.high):
            return -self.low[0]
        return (-self.low[0] + self.high[0]) / 2

mf = MedianFinder()
for x in (5, 2, 8, 1, 9, 3):
    mf.add(x)
    print(f"add {x}: lower {sorted(-v for v in mf.low)}  upper {sorted(mf.high)}  median {mf.median()}")
```
```text
add 5: lower [5]  upper []  median 5
add 2: lower [2]  upper [5]  median 3.5
add 8: lower [2, 5]  upper [8]  median 5
add 1: lower [1, 2]  upper [5, 8]  median 3.5
add 9: lower [1, 2, 5]  upper [8, 9]  median 5
add 3: lower [1, 2, 3]  upper [5, 8, 9]  median 4.0
```

Check the invariants on the printed lines: the biggest number on the left of the bar is never larger than the smallest on the right, and the left side is never smaller than the right side. After `5, 2, 8, 1, 9, 3` the sorted list is `1, 2, 3, 5, 8, 9`, and the median is `(3 + 5) / 2 = 4.0`.

### Cost

`add` does at most three heap operations: `O(log n)`. `median` just reads the roots: `O(1)`. The memory is `O(n)`: every number is stored once.

### Check it

Compare with `statistics.median`, which sorts the data on every call, after every single `add`.

```python
import statistics

rng = random.Random(27)
ok = True
for _ in range(300):
    mf, seen = MedianFinder(), []
    for _ in range(rng.randint(1, 25)):
        x = rng.randint(-10, 10)
        mf.add(x)
        seen.append(x)
        ok &= mf.median() == statistics.median(seen)
        ok &= len(mf.low) in (len(mf.high), len(mf.high) + 1)
        ok &= not mf.low or not mf.high or -mf.low[0] <= mf.high[0]
print("300 random streams: the median is right after every number, and the invariants hold:", bool(ok))
```
```text
300 random streams: the median is right after every number, and the invariants hold: True
```

The test also checks the two invariants after each step, so a wrong rebalancing would be caught even if it did not change the median yet.

### The same pattern elsewhere

The idea "a max-heap for the small half, a min-heap for the big half" gives the middle (or any fixed percentile) of a stream. It appears in **sliding-window median** (the window changes at both ends, so numbers must be removed; see the lazy deletion of section 11), in **scheduling** problems that always take the best of two groups, and in the "IPO" problem (pick the most profitable project that you can afford).

**Predict the output 4.** After adding `7, 1, 3` in this order, what are the contents of `low` and `high` (as sorted lists) and the median?

<details><summary>Answer</summary>

```python
mf = MedianFinder()
for x in (7, 1, 3):
    mf.add(x)
print(sorted(-v for v in mf.low), sorted(mf.high), mf.median())
```
```text
[1, 3] [7] 3
```

The sorted data is `1, 3, 7`. The lower half is `[1, 3]` (the larger half, because the count is odd), the upper half is `[7]`, and the median is the top of the lower half: `3`.

</details>

**Try it 5.** Use a single max-heap of size `k` to report the **k-th smallest** number of a stream after every number. Why is one heap enough here, while the median needed two?

<details><summary>Answer</summary>

```python
def kth_smallest_stream(stream, k):
    heap = []                                    # negated: root = the largest of the k smallest
    answers = []
    for x in stream:
        if len(heap) < k:
            heapq.heappush(heap, -x)
        elif x < -heap[0]:
            heapq.heapreplace(heap, -x)
        answers.append(-heap[0] if len(heap) == k else None)
    return answers

print(kth_smallest_stream([5, 2, 8, 1, 9, 3], 2))
```
```text
[None, 5, 5, 2, 2, 2]
```

The k-th smallest of a stream needs only the `k` smallest numbers; everything larger can be forgotten, because it can never be the k-th smallest again (numbers are only added). The median is the middle, and the middle moves in both directions as numbers arrive, so both halves must be remembered.

</details>

## 9. Merging K sorted sequences

You met this in dsa.09 (merge `k` sorted linked lists). Here is the general form, for lists, files and streams.

**Problem:** there are `k` sorted sequences with `N` items in total. Produce one sorted sequence.

**Idea:** the smallest item overall is the smallest of the `k` *front* items. Keep a min-heap with the front item of each sequence. Pop the smallest, output it, and push the next item of the same sequence. The heap never holds more than `k` items, so each step costs `O(log k)`, and the whole merge costs `O(N log k)`.

Each heap entry is a tuple `(value, which sequence, position in it)`. The sequence number also acts as a tie-breaker, so equal values never make Python compare anything else, and equal values come out in sequence order (a stable merge).

```python
def merge_k_sorted(lists):
    heap = [(lst[0], i, 0) for i, lst in enumerate(lists) if lst]
    heapq.heapify(heap)
    out = []
    while heap:
        value, i, j = heap[0]                    # the smallest front item
        out.append(value)
        if j + 1 < len(lists[i]):
            heapq.heapreplace(heap, (lists[i][j + 1], i, j + 1))   # swap in the next item of the same list
        else:
            heapq.heappop(heap)                  # that list is finished
    return out

print(merge_k_sorted([[1, 4, 9], [2, 3, 10], [], [0, 5]]))
rng = random.Random(21)
ok = True
for _ in range(400):
    lists = [sorted(rng.randint(0, 20) for _ in range(rng.randint(0, 6))) for _ in range(rng.randint(0, 6))]
    expected = sorted(v for lst in lists for v in lst)
    ok &= merge_k_sorted(lists) == expected == list(heapq.merge(*lists))
print("400 random inputs: our merge, heapq.merge and sorted() agree:", bool(ok))
```
```text
[0, 1, 2, 3, 4, 5, 9, 10]
400 random inputs: our merge, heapq.merge and sorted() agree: True
```

`heapq.merge` is the same algorithm as a lazy generator. Because it produces one item at a time, it can merge **huge** inputs that do not fit in memory: that is how an **external sort** works.

### External sort in miniature

To sort a file larger than memory: read it in chunks that fit, sort each chunk, write the sorted **runs** to disk, then merge all the runs with a heap. Memory use is one chunk while sorting, and `k` items while merging.

```python
rng = random.Random(1)
data = [rng.randint(0, 10**6) for _ in range(1000)]
chunk = 100
runs = [sorted(data[i:i + chunk]) for i in range(0, len(data), chunk)]   # each run fits in memory
merged = list(heapq.merge(*runs))
print(len(runs), "runs;", "sorted correctly:", merged == sorted(data))
```
```text
10 runs; sorted correctly: True
```

### The k-th smallest in a sorted matrix

A matrix has sorted rows and sorted columns. Find the k-th smallest value without flattening it. This is a merge of `n` sorted rows, stopped after `k` steps. Start with the first item of each of the first `min(n, k)` rows (rows beyond the `k`-th cannot contribute, because their first item is already bigger than `k` smaller values).

```python
rng = random.Random(101)
def kth_smallest_matrix(matrix, k):
    heap = [(matrix[r][0], r, 0) for r in range(min(len(matrix), k))]
    heapq.heapify(heap)
    for _ in range(k - 1):
        value, r, c = heapq.heappop(heap)
        if c + 1 < len(matrix[r]):
            heapq.heappush(heap, (matrix[r][c + 1], r, c + 1))
    return heap[0][0]

print(kth_smallest_matrix([[1, 5, 9], [10, 11, 13], [12, 13, 15]], 8))
ok = True
for _ in range(300):
    a = sorted(rng.randint(0, 9) for _ in range(rng.randint(1, 5)))
    b = sorted(rng.randint(0, 9) for _ in range(rng.randint(1, 5)))
    matrix = [[x + y for y in b] for x in a]            # rows and columns are both sorted
    flat = sorted(v for row in matrix for v in row)
    k = rng.randint(1, len(flat))
    ok &= kth_smallest_matrix(matrix, k) == flat[k - 1]
print("300 random sorted matrices agree with flatten-and-sort:", bool(ok))
```
```text
13
300 random sorted matrices agree with flatten-and-sort: True
```

The cost is `O(k log k)` (the heap has at most `k` items), instead of building all `n * m` values.

### The K smallest pair sums: explore lazily

Two sorted lists `a` and `b`. Among all pairs `(x, y)` with `x` from `a` and `y` from `b`, list the `k` pairs with the smallest sums. There are `len(a) * len(b)` pairs; we want only `k` of them.

View the pairs as a grid: rows are items of `a`, columns are items of `b`. The sums increase along each row and each column. So, starting at the corner, the next smallest pair is always next to one already chosen. Keep a heap of candidates: start with `(a[i], b[0])` for the first rows, and every time you take `(a[i], b[j])`, add its right neighbour `(a[i], b[j+1])`.

```python
rng = random.Random(102)
def k_smallest_pairs(a, b, k):
    if not a or not b or k <= 0:
        return []
    heap = [(a[i] + b[0], i, 0) for i in range(min(k, len(a)))]
    heapq.heapify(heap)
    out = []
    while heap and len(out) < k:
        _, i, j = heapq.heappop(heap)
        out.append((a[i], b[j]))
        if j + 1 < len(b):
            heapq.heappush(heap, (a[i] + b[j + 1], i, j + 1))
    return out

print(k_smallest_pairs([1, 7, 11], [2, 4, 6], 3))
print(k_smallest_pairs([1, 1, 2], [1, 2, 3], 4))
ok = True
for _ in range(400):
    a = sorted(rng.randint(0, 8) for _ in range(rng.randint(0, 5)))
    b = sorted(rng.randint(0, 8) for _ in range(rng.randint(0, 5)))
    k = rng.randint(0, 12)
    mine = [x + y for x, y in k_smallest_pairs(a, b, k)]
    expected = sorted(x + y for x in a for y in b)[:k]
    ok &= mine == expected
print("400 random inputs: the sums match the brute force:", bool(ok))
```
```text
[(1, 2), (1, 4), (1, 6)]
[(1, 1), (1, 1), (1, 2), (1, 2)]
400 random inputs: the sums match the brute force: True
```

We compare the **sums** and not the pairs, because several pairs can have the same sum and a correct answer may pick any of them. The lesson: a heap lets you explore a huge space **in order**, generating only the part you need.

### The smallest range covering all lists

Given `k` sorted lists, find the smallest interval `[x, y]` that contains at least one number from every list. Keep one pointer in each list, a min-heap of the current items and the current maximum. The interval `[heap minimum, current maximum]` covers every list. To try a smaller interval, the minimum has to go: advance its list by one item and update the maximum. Stop when some list is exhausted.

```python
rng = random.Random(103)
def smallest_range(lists):
    heap = [(lst[0], i, 0) for i, lst in enumerate(lists)]
    heapq.heapify(heap)
    current_max = max(lst[0] for lst in lists)
    best = (heap[0][0], current_max)
    while True:
        value, i, j = heap[0]
        if current_max - value < best[1] - best[0]:
            best = (value, current_max)
        if j + 1 == len(lists[i]):
            break                                  # list i has no next item: we cannot cover it any more
        nxt = lists[i][j + 1]
        heapq.heapreplace(heap, (nxt, i, j + 1))
        current_max = max(current_max, nxt)
    return list(best)

def smallest_range_brute(lists):
    values = sorted({v for lst in lists for v in lst})
    candidates = []
    for lo in values:
        for hi in values:
            if hi >= lo and all(any(lo <= v <= hi for v in lst) for lst in lists):
                candidates.append((hi - lo, lo, hi))
    _, lo, hi = min(candidates)
    return [lo, hi]

print(smallest_range([[4, 10, 15, 24, 26], [0, 9, 12, 20], [5, 18, 22, 30]]))
ok = True
for _ in range(300):
    lists = [sorted(rng.sample(range(25), rng.randint(1, 5))) for _ in range(rng.randint(1, 4))]
    ok &= smallest_range(lists) == smallest_range_brute(lists)
print("300 random inputs match the brute force:", bool(ok))
```
```text
[20, 24]
300 random inputs match the brute force: True
```

**Predict the output 5.** What does `merge_k_sorted([[3, 6], [1, 8], [2]])` print, and how many items can the heap hold at most?

<details><summary>Answer</summary>

```python
print(merge_k_sorted([[3, 6], [1, 8], [2]]))
```
```text
[1, 2, 3, 6, 8]
```

The result is `[1, 2, 3, 6, 8]`. The heap starts with the three front items `3, 1, 2` and never holds more than one item per list, that is, at most `k = 3`. That is why the merge needs only `O(k)` memory besides the output.

</details>

## 10. Greedy algorithms with a heap

A **greedy** algorithm builds its answer by always taking the best-looking choice right now. The hard part is finding "the best choice right now" quickly, again and again. That is a heap's job. Here are the classics.

### Connect the sticks (and Huffman coding)

You have sticks of given lengths. Joining two sticks of lengths `a` and `b` costs `a + b` and gives one stick of length `a + b`. Join them all into one stick at the smallest total cost.

Greedy rule: always join the **two shortest** sticks. (A stick that is joined early is paid for again in every later join that contains it, so the long sticks should be joined as late as possible.)

```python
def connect_sticks(sticks):
    heap = list(sticks)
    heapq.heapify(heap)
    cost = 0
    while len(heap) > 1:
        a = heapq.heappop(heap)
        b = heapq.heappop(heap)
        cost += a + b
        heapq.heappush(heap, a + b)
    return cost

print(connect_sticks([2, 4, 3]), connect_sticks([1, 8, 3, 5]), connect_sticks([5]))
```
```text
14 30 0
```

This is exactly **Huffman coding**, the idea behind file compression. Letters that occur often get short bit codes, and rare letters get long ones. Treat the letter frequencies as stick lengths; each join creates an inner node of a tree, and the two sticks become its two children. Reading the left branches as `0` and the right branches as `1` gives the codes.

```python
from collections import Counter

def huffman_codes(text):
    freq = Counter(text)
    if len(freq) == 1:
        return {next(iter(freq)): "0"}
    # entries: (frequency, tie-breaker, tree); a tree is a letter or a pair (left, right)
    heap = [(f, i, ch) for i, (ch, f) in enumerate(sorted(freq.items()))]
    heapq.heapify(heap)
    counter = len(heap)
    while len(heap) > 1:
        f1, _, t1 = heapq.heappop(heap)
        f2, _, t2 = heapq.heappop(heap)
        heapq.heappush(heap, (f1 + f2, counter, (t1, t2)))
        counter += 1
    codes = {}
    def walk(tree, prefix):
        if isinstance(tree, str):
            codes[tree] = prefix
        else:
            walk(tree[0], prefix + "0")
            walk(tree[1], prefix + "1")
    walk(heap[0][2], "")
    return codes

text = "abracadabra"
codes = huffman_codes(text)
print(codes)
bits = sum(len(codes[ch]) for ch in text)
print("Huffman bits:", bits, "| fixed 3-bit codes:", 3 * len(text))
print("same as connect_sticks on the frequencies:", connect_sticks(Counter(text).values()) == bits)
```
```text
{'a': '0', 'c': '100', 'd': '101', 'b': '110', 'r': '111'}
Huffman bits: 23 | fixed 3-bit codes: 33
same as connect_sticks on the frequencies: True
```

The most frequent letter `a` gets the shortest code. The total number of bits equals the cost of joining the sticks, which is no accident: each join cost counts the letters below it once for every level they are deeper in the tree. The tie-breaker counter in the heap entries prevents Python from comparing trees.

A Huffman code is **prefix-free**: no code is the start of another, so a bit string can be decoded without separators. Check it, and decode:

```python
rng = random.Random(104)
def is_prefix_free(codes):
    values = list(codes.values())
    return not any(a != b and b.startswith(a) for a in values for b in values)

def decode(bits, codes):
    inverse = {code: ch for ch, code in codes.items()}
    out, current = [], ""
    for bit in bits:
        current += bit
        if current in inverse:
            out.append(inverse[current])
            current = ""
    return "".join(out)

encoded = "".join(codes[ch] for ch in text)
print(is_prefix_free(codes), decode(encoded, codes) == text)
ok = True
for _ in range(200):
    t = "".join(rng.choice("abcdef") for _ in range(rng.randint(2, 30)))
    c = huffman_codes(t)
    enc = "".join(c[ch] for ch in t)
    ok &= is_prefix_free(c) and decode(enc, c) == t
    if len(set(t)) > 1:
        ok &= len(enc) == connect_sticks(Counter(t).values())
print("200 random texts: prefix-free, decodes back, and the length equals the stick cost:", bool(ok))
```
```text
True True
200 random texts: prefix-free, decodes back, and the length equals the stick cost: True
```

### How many meeting rooms?

Given meetings as `(start, end)` times (a meeting that ends at 10 and one that starts at 10 do not overlap), find the smallest number of rooms.

Sort the meetings by start time. Keep a min-heap of the **end times of the rooms in use**. For a new meeting:

- if the room that frees up first (`heap[0]`) is free by the new start, **reuse** that room (replace its end time);
- otherwise **open a new room** (push the end time).

The answer is the size of the heap.

```python
rng = random.Random(105)
def min_rooms(intervals):
    ends = []
    for start, end in sorted(intervals):
        if ends and ends[0] <= start:
            heapq.heapreplace(ends, end)           # reuse the room that frees up first
        else:
            heapq.heappush(ends, end)              # every room is busy: open a new one
    return len(ends)

def min_rooms_sweep(intervals):
    events = sorted([(s, 1) for s, e in intervals] + [(e, -1) for s, e in intervals])   # at equal times, -1 (end) comes first
    rooms = best = 0
    for _, delta in events:
        rooms += delta
        best = max(best, rooms)
    return best

print(min_rooms([(0, 30), (5, 10), (15, 20)]), min_rooms([(7, 10), (2, 4)]), min_rooms([(1, 5), (5, 9)]), min_rooms([]))
ok = True
for _ in range(500):
    meetings = []
    for _ in range(rng.randint(0, 10)):
        s = rng.randint(0, 20)
        meetings.append((s, s + rng.randint(1, 6)))
    ok &= min_rooms(meetings) == min_rooms_sweep(meetings)
print("500 random schedules: the heap method equals the sweep-line method:", bool(ok))
```
```text
2 1 1 0
500 random schedules: the heap method equals the sweep-line method: True
```

The second solution is a different algorithm (count the meetings that are running at the same time, by scanning the start and end events in order). Two independent solutions that agree on many random inputs give real confidence.

### Reorganise a string so that no two neighbours are equal

Rearrange the letters of a string so that no two equal letters are adjacent, or report that it is impossible. Greedy: at each step place the letter with the **largest remaining count** that is not the one we just placed. A max-heap on the counts gives that letter. The letter we just used waits one round (it is kept out of the heap), and then returns with its count reduced.

```python
rng = random.Random(106)
from collections import Counter

def reorganize(s):
    heap = [(-count, ch) for ch, count in Counter(s).items()]
    heapq.heapify(heap)
    out = []
    held = (0, "")                                   # the letter placed last, not yet back in the heap
    while heap:
        count, ch = heapq.heappop(heap)
        out.append(ch)
        if held[0] < 0:
            heapq.heappush(heap, held)               # the previous letter may be used again
        held = (count + 1, ch)                       # one copy used (counts are negative)
    return "".join(out) if len(out) == len(s) else ""

print(reorganize("aab"), repr(reorganize("aaab")), reorganize("aabbcc"))
ok = True
for _ in range(500):
    s = "".join(rng.choice("abc") for _ in range(rng.randint(0, 9)))
    result = reorganize(s)
    possible = not s or max(Counter(s).values()) <= (len(s) + 1) // 2
    if possible:
        ok &= (sorted(result) == sorted(s)) and all(x != y for x, y in zip(result, result[1:]))
    else:
        ok &= result == ""
print("500 random strings: results are valid, and impossible exactly when one letter exceeds half:", bool(ok))
```
```text
aba '' abcabc
500 random strings: results are valid, and impossible exactly when one letter exceeds half: True
```

A string can be reorganised exactly when the most frequent letter appears at most `(n + 1) // 2` times, which is the condition the test uses as ground truth.

### Shortest job first

A computer has jobs, each with an arrival time and a duration. When the processor becomes free, it runs the available job with the **shortest duration**. This minimises the average waiting time. A min-heap on the duration picks that job. Jobs arrive while others run, so we push every job that has arrived by the current time.

```python
rng = random.Random(107)
def sjf_average_wait(jobs):
    """jobs: list of (arrival, duration). Returns the average waiting time."""
    jobs = sorted(jobs)
    heap, i, time, total_wait = [], 0, 0, 0
    for _ in range(len(jobs)):
        if not heap and time < jobs[i][0]:
            time = jobs[i][0]                       # idle until the next job arrives
        while i < len(jobs) and jobs[i][0] <= time:
            heapq.heappush(heap, (jobs[i][1], jobs[i][0]))
            i += 1
        duration, arrival = heapq.heappop(heap)
        total_wait += time - arrival
        time += duration
    return total_wait / len(jobs) if jobs else 0.0

def sjf_scan(jobs):
    pending, time, total_wait, n = sorted(jobs), 0, 0, len(jobs)
    while pending:
        ready = [j for j in pending if j[0] <= time]
        if not ready:
            time = min(j[0] for j in pending)
            continue
        job = min(ready, key=lambda j: (j[1], j[0]))     # shortest duration, then earliest arrival
        pending.remove(job)
        total_wait += time - job[0]
        time += job[1]
    return total_wait / n if n else 0.0

print(sjf_average_wait([(0, 7), (2, 4), (4, 1), (5, 4)]))
ok = True
for _ in range(500):
    jobs = [(rng.randint(0, 15), rng.randint(1, 6)) for _ in range(rng.randint(0, 8))]
    ok &= sjf_average_wait(jobs) == sjf_scan(jobs)
print("500 random job lists: the heap scheduler equals the scan-the-list scheduler:", bool(ok))
```
```text
4.0
500 random job lists: the heap scheduler equals the scan-the-list scheduler: True
```

The scan version costs `O(n)` per decision, `O(n^2)` in total; the heap version `O(n log n)`. They make the same choices, which the test confirms.

### A preview of Dijkstra's algorithm

The graphs module teaches **Dijkstra's algorithm** for the shortest paths from one place to all others on a map with positive road lengths. Its core is a heap: always expand the city that is **closest to the start** among those not finished. Heap entries are `(distance, city)`.

One detail needs care. When we find a shorter way to a city that is already in the heap, we cannot easily change its entry. We simply push a **new** entry with the better distance. The old, worse entry stays in the heap as a *stale* entry; when it is popped later, we notice that it is outdated (`d > dist[u]`) and skip it. This is **lazy deletion**, the topic of the next section.

```python
def dijkstra(graph, source):
    dist = {source: 0}
    heap = [(0, source)]
    while heap:
        d, u = heapq.heappop(heap)
        if d > dist[u]:
            continue                                  # a stale entry: a shorter way was found later
        for v, weight in graph[u]:
            new_dist = d + weight
            if new_dist < dist.get(v, float("inf")):
                dist[v] = new_dist
                heapq.heappush(heap, (new_dist, v))   # do not remove the old entry; just push the better one
    return dist

graph = {
    "A": [("B", 4), ("C", 1)],
    "B": [("D", 1)],
    "C": [("B", 2), ("D", 5)],
    "D": [],
    "E": [("A", 1)],
}
print(dijkstra(graph, "A"))
```
```text
{'A': 0, 'B': 3, 'C': 1, 'D': 4}
```

The shortest way to `B` is `A -> C -> B` (cost 3) and not the direct road (cost 4); to `D` it is `A -> C -> B -> D` (cost 4). `E` is not reachable from `A`, so it does not appear. A brute force for checking: **Bellman-Ford**, which just relaxes every edge `n - 1` times.

```python
rng = random.Random(108)
def bellman_ford(graph, source):
    dist = {source: 0}
    for _ in range(len(graph) - 1):
        for u in graph:
            if u in dist:
                for v, weight in graph[u]:
                    if dist[u] + weight < dist.get(v, float("inf")):
                        dist[v] = dist[u] + weight
    return dist

ok = True
for _ in range(300):
    n = rng.randint(1, 8)
    graph = {u: [] for u in range(n)}
    for _ in range(rng.randint(0, 16)):
        graph[rng.randrange(n)].append((rng.randrange(n), rng.randint(1, 9)))
    ok &= dijkstra(graph, 0) == bellman_ford(graph, 0)
print("300 random weighted graphs: Dijkstra with a heap equals Bellman-Ford:", bool(ok))
```
```text
300 random weighted graphs: Dijkstra with a heap equals Bellman-Ford: True
```

**Try it 6.** In `min_rooms`, what changes if a meeting that ends at 10 and one that starts at 10 **do** overlap? Which character changes in the code?

<details><summary>Answer</summary>

In `ends[0] <= start`, the `<=` becomes `<`. A room that frees up at exactly the new start time is then not available.

```python
def min_rooms_strict(intervals):
    ends = []
    for start, end in sorted(intervals):
        if ends and ends[0] < start:               # strict: ending at 10 and starting at 10 clash
            heapq.heapreplace(ends, end)
        else:
            heapq.heappush(ends, end)
    return len(ends)

print(min_rooms([(1, 5), (5, 9)]), min_rooms_strict([(1, 5), (5, 9)]))
```
```text
1 2
```

Always read the statement for what happens at the boundary. This one-character choice is the typical off-by-one of interval problems.

</details>

## 11. Updates and removals: lazy deletion

A heap only supports "remove the smallest". Removing an arbitrary item, or changing an item's priority, would need to find the item in the list (`O(n)`) and then repair the heap. For many programs there is a better way: **do not remove it now; mark it as removed, and throw it away when it reaches the top.** This is **lazy deletion**.

### Priority queue with changes (the standard recipe)

We want these operations:

- `add(task, priority)`: add a new task, or **change** the priority of an existing one,
- `remove(task)`: cancel a task,
- `pop()`: return the task with the best priority.

The recipe, which also appears in the `heapq` documentation:

- keep the heap entries as lists `[priority, count, task]`, where `count` is a unique, increasing number (the tie-breaker, and first-in-first-out for equal priorities);
- keep a dictionary `task -> entry`, to find the entry of a task in `O(1)`;
- to change or remove a task, **mark its entry** as removed (replace the task by a special marker) and, for a change, push a new entry;
- `pop` skips entries that carry the marker.

```python
import itertools

class UpdatablePQ:
    REMOVED = object()                               # marks a deleted entry

    def __init__(self):
        self.heap = []
        self.entries = {}                            # task -> its live entry
        self.counter = itertools.count()

    def add(self, task, priority=0):
        if task in self.entries:
            self.remove(task)                        # a change = remove the old entry + add a new one
        entry = [priority, next(self.counter), task]
        self.entries[task] = entry
        heapq.heappush(self.heap, entry)

    def remove(self, task):
        entry = self.entries.pop(task)               # KeyError if the task is not there
        entry[-1] = self.REMOVED                     # mark it; it stays in the heap

    def pop(self):
        while self.heap:
            priority, _, task = heapq.heappop(self.heap)
            if task is not self.REMOVED:
                del self.entries[task]
                return task
        raise KeyError("pop from an empty priority queue")

    def __len__(self):
        return len(self.entries)

pq = UpdatablePQ()
pq.add("write", 3)
pq.add("test", 2)
pq.add("deploy", 1)
pq.add("write", 0)                                   # raise the priority of "write"
pq.remove("test")
print(len(pq), len(pq.heap))
print(pq.pop(), pq.pop(), len(pq))
```
```text
2 4
write deploy 0
```

Look at the numbers on the first line: the queue has 2 live tasks, but the heap list still holds 4 entries (the old "write" and the removed "test" are still there as stale entries). They disappear only when they reach the top and `pop` throws them away.

The heap property is safe because the comparison never looks at the task: the entries are compared by `priority`, then by the unique `count`, so they never reach the third place. Changing the third field to the marker does not move the entry.

### Check it against a dictionary

The model is a plain dictionary `task -> (priority, count)`, and `pop` takes the entry with the smallest `(priority, count)` by scanning the dictionary.

```python
rng = random.Random(33)
ok = True
for _ in range(300):
    pq, model, count = UpdatablePQ(), {}, 0
    for _ in range(rng.randint(1, 40)):
        op = rng.choice(["add", "add", "remove", "pop"])
        task = rng.randint(0, 5)
        if op == "add":
            priority = rng.randint(0, 4)
            pq.add(task, priority)
            model[task] = (priority, count)
            count += 1
        elif op == "remove" and task in model:
            pq.remove(task)
            del model[task]
        elif op == "pop" and model:
            expected = min(model, key=lambda t: model[t])
            ok &= pq.pop() == expected
            del model[expected]
        ok &= len(pq) == len(model)
print("300 random sequences: the lazy-deletion queue always agrees with the dictionary model:", bool(ok))
```
```text
300 random sequences: the lazy-deletion queue always agrees with the dictionary model: True
```

### The cost of laziness

Stale entries stay in the heap until they reach the top, so the heap can grow bigger than the number of live items. Each entry is still removed only once, so the total time is fine: each `add` and each `pop` of an entry costs `O(log n)`, where `n` is the heap size including the stale ones. If many changes happen, you can **rebuild** the heap from the live entries when the stale ones exceed half of it (`O(n)` for `heapify`). The more complex alternative is an **indexed heap**, which stores the position of every item so that it can be moved at once; it is faster in theory and harder to write.

### Sliding window maximum with a heap

In dsa.08 you solved this with a monotonic deque in `O(n)`. With a heap and lazy deletion, you can do it in `O(n log n)` without any clever invariant. Push `(-value, index)` for every number. The maximum of the window is the top, **unless** its index has left the window; then pop it (it is stale) and look again.

```python
rng = random.Random(109)
def sliding_max_heap(nums, k):
    heap, out = [], []
    for i, x in enumerate(nums):
        heapq.heappush(heap, (-x, i))
        if i >= k - 1:
            while heap[0][1] <= i - k:               # the top is outside the window: stale
                heapq.heappop(heap)
            out.append(-heap[0][0])
    return out

print(sliding_max_heap([1, 3, -1, -3, 5, 3, 6, 7], 3))
ok = True
for _ in range(400):
    nums = [rng.randint(-5, 5) for _ in range(rng.randint(1, 15))]
    k = rng.randint(1, len(nums))
    ok &= sliding_max_heap(nums, k) == [max(nums[i:i + k]) for i in range(len(nums) - k + 1)]
print("400 random inputs agree with the brute force:", bool(ok))
```
```text
[3, 3, 5, 5, 6, 7]
400 random inputs agree with the brute force: True
```

We never remove an old entry from the middle of the heap. We only look at the top, and if it is outdated we pop it. Stale entries deep in the heap cost nothing until they surface. The deque solution is faster (`O(n)`), but the heap solution generalises: it works whenever "the best item in a window" needs a heap, for example with a complicated comparison.

**Predict the output 6.** What does this print?

```python
pq = UpdatablePQ()
pq.add("a", 5)
pq.add("b", 5)
pq.add("a", 1)
print(pq.pop(), pq.pop(), len(pq), len(pq.heap))
```

<details><summary>Answer</summary>

```text
a b 0 0
```

`a` was added with priority 5, then re-added with priority 1 (the first entry became stale). The best is the new `a` (priority 1), then `b` (priority 5). Popping `b` also surfaces the stale entry of `a`: it sits in the heap with priority 5 and a count *smaller* than `b`'s count, so it comes out of the heap *before* `b`, is recognised as removed and thrown away. At the end the queue is empty (`0` live tasks) and the heap list is empty too.

</details>

**Try it 7.** You change the priority of a task with `pq.add(task, new_priority)` many thousands of times. Which operation do you add to keep the heap list from growing without limit?

<details><summary>Answer</summary>

A **rebuild** (compaction): when the heap list is more than about twice the number of live tasks, make a new list of the live entries and call `heapify`.

```python
def compact(pq):
    pq.heap = [entry for entry in pq.entries.values()]
    heapq.heapify(pq.heap)

pq = UpdatablePQ()
for round_ in range(1000):
    pq.add("job", round_)                         # the same task, 1000 times
print(len(pq), len(pq.heap))
if len(pq.heap) > 2 * len(pq):
    compact(pq)
print(len(pq), len(pq.heap), pq.pop())
```
```text
1 1000
1 1 job
```

After 1000 updates there is one live task and 1000 entries. A compaction costs `O(live)` and brings the heap back to 1. Done only when the heap has doubled, the cost per operation stays `O(log n)` on average.

</details>

## 12. Which structure for which problem?

| Clue in the problem | Tool |
|---|---|
| "the smallest / largest item, repeatedly", while items are added | **heap** |
| "top K", "K largest / smallest / closest / most frequent" | heap of size `K` (or `nlargest` / `nsmallest`) |
| "K-th largest" in a stream | min-heap of size `K` |
| "running median", "median of a stream" | two heaps |
| "merge K sorted ...", "smallest pairs / sums" | heap of fronts, lazy exploration |
| "always process the cheapest / earliest / most urgent next" | greedy with a heap |
| shortest path with positive weights | Dijkstra (heap) |
| "the largest in each window" | monotonic deque (dsa.08), or heap with lazy deletion |
| sort everything once | `sorted` (a heap is not needed) |
| search for an arbitrary value, ordered iteration, delete any item | balanced tree, or a sorted list with `bisect` |
| first come, first served | queue (`deque`) |
| lookup by key | `dict` |

Two questions help:

1. **Do I need the order of everything, or only the next best item?** For everything, sort once. For only the next best item as the data changes, use a heap. A heap that is filled once and emptied once is just a slower sort.
2. **How big is K compared with N?** If `K` is tiny, a heap of size `K` is excellent. If `K` is close to `N`, sorting is simpler and as fast.

## 13. Common traps, collected

1. **Expecting a heap to be sorted.** Only `heap[0]` is meaningful. Pop items, or use `sorted`, to get the order.
2. **A max-heap with a wrong sign.** Negate on **push** and negate again on **pop** and **peek**. A forgotten minus sign gives the smallest instead of the largest.
3. **Comparing items that cannot be compared.** Equal priorities make Python compare the next tuple element; use `(priority, counter, item)`.
4. **Changing an item inside the heap** (`heap[i] = ...`, or mutating an object that is in the heap). The heap property can break silently. Use `heapreplace`, lazy deletion, or `heapify` again.
5. **`heap[0]` or `heappop` on an empty heap.** Check `if heap:` first, and decide what to return when `k = 0` or when there are fewer than `k` items.
6. **The wrong heap direction in top-K.** The K *largest* need a *min*-heap of size `K` (so that the weakest candidate is at the root). The K *smallest* need a *max*-heap.
7. **Pushing one by one when `heapify` is enough.** Building from an existing list is `O(n)` with `heapify`, against `O(n log n)` for repeated pushes in the worst case.
8. **Confusing `heappushpop` with `heapreplace`.** The first pushes then pops (the new item may come straight back); the second pops then pushes.
9. **Using a heap when you need a sorted result.** A heap is a partial order. For a full sort use `sorted`.
10. **Off-by-one in the index formulas** of a hand-written heap: children `2i + 1`, `2i + 2`, parent `(i - 1) // 2`; and the last parent is `n // 2 - 1`. Stop `sift_down` when the child index is `>= n`.
11. **Forgetting that equal priorities come out in no particular order**, unless you add a counter. If order among equals matters, say so with the tie-breaker.
12. **Forgetting stale entries** after lazy deletion: the size of the heap list is not the number of live items. Keep a separate count.
13. **Using `nlargest(1, ...)` where `max` is enough**, or `nlargest(k, ...)` with `k` close to `n`, where `sorted` is simpler.
14. **Comparing points by the true distance** with square roots and floating-point error. Compare squared distances.

## 14. Summary

- A **priority queue** gives the item with the best priority. A **binary heap** is the standard way: a **complete** binary tree, stored in a plain list, in which every parent is `<=` its children (min-heap). The smallest item is always `heap[0]`. A heap is **not sorted**.
- Index formulas: children of `i` at `2i + 1` and `2i + 2`; parent at `(i - 1) // 2`. The height is about `log2 n`.
- **Push:** append at the end, `sift_up`. **Pop:** take the root, move the last item to the root, `sift_down` using the **smaller** child. Both cost `O(log n)`. Peek costs `O(1)`.
- **`heapify`** turns a list into a heap in `O(n)`: call `sift_down` from the last parent (`n // 2 - 1`) back to the root. Most nodes are near the bottom and need almost no work.
- **`heapq`** works on a plain list: `heappush`, `heappop`, `heapify`, `heappushpop`, `heapreplace`, `nsmallest`, `nlargest`, `merge`. A max-heap is made by **negating** values. Use `(priority, counter, item)` to avoid comparing items. Never edit items inside the heap.
- **Heap sort** is `O(n log n)` with `O(1)` extra space in place, but not stable.
- **Top-K:** a min-heap of size `K` for the K largest (replace the root when a better item comes): `O(n log K)` time, `O(K)` space, works on streams. Mirror it for the K smallest. The K-th largest is `heap[0]`.
- **Two heaps** (a max-heap for the lower half, a min-heap for the upper half) give the running median: `O(log n)` per number, `O(1)` for the median.
- **Merge K sorted** inputs with a heap of their fronts: `O(N log K)`. The same "explore in order with a heap" idea gives the K smallest pair sums and the K-th smallest in a sorted matrix.
- **Greedy with a heap:** connect sticks / Huffman coding, meeting rooms, reorganise a string, shortest job first, and Dijkstra's shortest paths.
- **Lazy deletion** handles removals and priority changes: mark an entry as removed (or push a better entry) and discard stale entries when they reach the top.

### Self-check

- [ ] I can state the heap property and the shape rule, and say why the array layout works.
- [ ] I can write `sift_up`, `sift_down`, `push`, `pop` and `heapify` from memory.
- [ ] I can explain why `heapify` is `O(n)` and not `O(n log n)`.
- [ ] I can use `heapq` for a max-heap, for tuples with a tie-breaker, and for `nlargest` / `nsmallest` / `merge`.
- [ ] I can solve the K largest, K-th largest in a stream, K most frequent and K closest points, and I know which heap each needs.
- [ ] I can write the two-heap median, and state its two invariants.
- [ ] I can merge K sorted lists with a heap, and explain why the heap never holds more than K items.
- [ ] I can solve meeting rooms, connect the sticks and one more greedy problem with a heap.
- [ ] I can explain lazy deletion and use it in a priority queue with updates.
- [ ] I can decide between a heap, `sorted`, `bisect`, a `deque` and a dictionary.

### How to practise

Do the problems in the order of the chapter: the structure first (index formulas, validity checks, the sift operations traced by hand), then your own heap and `heapq`, then top-K, then the two-heap median, then merging, then the greedy problems, and last the priority queue with updates. **For every problem, say aloud what the heap contains and what its root means** ("the weakest of the K I keep", "the room that frees up first"). Test a heap solution against a sort or a brute force on small random inputs, as in this chapter; always include empty inputs, `k = 0`, `k` larger than the data, and many equal values. The site problems for this module (LeetCode, CSES, Codeforces) will be listed for you in the module's external list.

### Further reading

- Thomas Cormen, Charles Leiserson, Ronald Rivest and Clifford Stein, *Introduction to Algorithms*, the chapter on heapsort and priority queues (including the proof that building a heap takes linear time).
- Robert Sedgewick and Kevin Wayne, *Algorithms*, section 2.4 ("Priority Queues"), including the indexed priority queue.
- Donald Knuth, *The Art of Computer Programming*, volume 3, section 5.2.3 ("Sorting by Selection"), for heapsort.
- The Python documentation of the `heapq` module, in particular the sections "Priority Queue Implementation Notes" and "Theory" (François Pinard's explanation of why heaps work).
- David Huffman, "A Method for the Construction of Minimum-Redundancy Codes" (1952), the original Huffman coding paper.

Next module: **dsa.12 Graphs**.
