# Chapter 5: Built-in collections

Up to now, almost every name in your programs has referred to one value: one number, one string, one bool. Real programs work with many values at once. A class has sixty students. A shop has hundreds of products. A phone has a contact list. You need a way to keep many values together, look them up quickly, and change them safely.

Python gives you four main built-in **collections** for this: the **list**, the **tuple**, the **dict** and the **set**. They are built into the language, so you can use them without importing anything. They are also extremely fast, because they are written in C inside the Python interpreter.

This chapter does more than list their methods. For each collection you will learn how it is stored in memory, what each operation costs, and which mistakes catch almost every beginner. The biggest of those mistakes is **aliasing**: two names that refer to the same list, so a change through one name shows up through the other. Once you understand aliasing, a whole family of confusing bugs becomes easy to explain.

A note on how examples are shown. A block of code is followed by the exact output it produces when run as a script with Python 3.14. When an example ends in an error, the traceback is shown with the file name shortened to `example.py`. Answer every "Predict the output" question on paper before you open the answer. Being wrong on paper is how the mental model gets fixed.

## Table of contents

1. [The four collections at a glance](#1-the-four-collections-at-a-glance)
2. [Lists: creating, indexing and looping](#2-lists-creating-indexing-and-looping)
3. [List methods](#3-list-methods)
4. [Slicing, slice assignment and del](#4-slicing-slice-assignment-and-del)
5. [Nested lists](#5-nested-lists)
6. [Under the hood: how a list is stored](#6-under-the-hood-how-a-list-is-stored)
7. [Aliasing, shallow copies and deep copies](#7-aliasing-shallow-copies-and-deep-copies)
8. [The [[0] * 3] * 3 trap](#8-the-0--3--3-trap)
9. [Tuples, packing and unpacking](#9-tuples-packing-and-unpacking)
10. [namedtuple](#10-namedtuple)
11. [Dicts](#11-dicts)
12. [Dict views, merging, and changing a dict while looping](#12-dict-views-merging-and-changing-a-dict-while-looping)
13. [Under the hood: hashing](#13-under-the-hood-hashing)
14. [Hashability: what can be a key](#14-hashability-what-can-be-a-key)
15. [Sets and frozensets](#15-sets-and-frozensets)
16. [Comprehensions](#16-comprehensions)
17. [Sorting](#17-sorting)
18. [Big-O of collection operations and choosing a structure](#18-big-o-of-collection-operations-and-choosing-a-structure)
19. [Summary](#summary)
20. [Learning outcomes](#learning-outcomes)
21. [Module project](#module-project)
22. [Further reading](#further-reading)

---

## 1. The four collections at a glance

Before the details, here is the whole map. Keep coming back to this table.

| Collection | Example | Ordered? | Can change? | Duplicates? | Look up by |
|---|---|---|---|---|---|
| list | `[3, 1, 3]` | yes | yes (mutable) | allowed | position (index) |
| tuple | `(3, 1, 3)` | yes | no (immutable) | allowed | position (index) |
| dict | `{"a": 1, "b": 2}` | yes, insertion order | yes | keys unique | key |
| set | `{3, 1}` | no | yes | no | membership only |

A few words in that table need care.

- **Ordered** means the collection remembers the order you put things in, and you can ask for "the first one" or "the third one". A set does not remember order at all.
- **Mutable** means the object itself can be changed after it is created: items added, removed or replaced. Recall from core.02 that a name is a label on an object. With a mutable object, the object can change while all its labels stay put.
- **Look up by** is the question you ask the collection. A list answers "what is at position 4?". A dict answers "what is stored under the key `'priya'`?". A set answers only "is this in here?".

Choosing the right collection is mostly about choosing the right question. We come back to this in the last section.

`len()`, `in` and `for` loops work on every collection, which is why you can often swap one collection for another with few changes.

---

## 2. Lists: creating, indexing and looping

A **list** is an ordered, changeable sequence of values. You write it with square brackets and commas.

```python
marks = [72, 85, 64, 90]
names = ["Asha", "Ravi", "Meena"]
mixed = [1, "two", 3.0, True, None]
empty = []
print(marks)
print(names)
print(mixed)
print(empty, len(empty))
```

Output:

```text
[72, 85, 64, 90]
['Asha', 'Ravi', 'Meena']
[1, 'two', 3.0, True, None]
[] 0
```

A list can hold values of different types, as `mixed` shows. In practice most lists hold one kind of thing, because that is what makes them easy to loop over.

### Other ways to build a list

`list()` turns any *iterable* (anything a `for` loop can walk over) into a list. You already know several iterables: strings, `range` objects and the result of `str.split()`.

```python
print(list("hello"))
print(list(range(5)))
print(list(range(10, 0, -3)))
print("10 20 30".split())
print([int(x) for x in "10 20 30".split()])
```

Output:

```text
['h', 'e', 'l', 'l', 'o']
[0, 1, 2, 3, 4]
[10, 7, 4, 1]
['10', '20', '30']
[10, 20, 30]
```

The last line is a **list comprehension**. It builds a new list by running an expression for each item. Section 16 covers comprehensions fully. For now, read it as "the list of `int(x)` for each `x` in the split words". It is the standard way to read a line of numbers:

```python
nums = [int(x) for x in input().split()]
```

### Indexing

Each item has a position called its **index**. The first item is at index `0`. Negative indexes count from the end: `-1` is the last item.

```
index:      0     1     2     3
         +-----+-----+-----+-----+
marks -> | 72  | 85  | 64  | 90  |
         +-----+-----+-----+-----+
index:     -4    -3    -2    -1
```

```python
marks = [72, 85, 64, 90]
print(marks[0], marks[1], marks[-1], marks[-2])
marks[1] = 88
print(marks)
print(marks[4])
```

Output:

```text
72 85 90 64
[72, 88, 64, 90]
Traceback (most recent call last):
  File "example.py", line 5, in <module>
    print(marks[4])
          ~~~~~^^^
IndexError: list index out of range
```

Two things happened. First, `marks[1] = 88` **replaced** an item. You cannot do that with a string, because strings are immutable. Second, reading past the end raised `IndexError`. A list of length 4 has valid indexes `0` to `3` and `-4` to `-1`, nothing else.

### Looping

You loop over a list exactly as you loop over a string: `for name in names:`, or `for i, name in enumerate(names, start=1):` when you also need positions. `"Ravi" in names` tests membership.

### Predict the output

```python
x = [5, 10, 15, 20]
x[-1] = x[0] + x[1]
print(x)
print(x[len(x) - 1] == x[-1])
print(len(x[1:]))
```

<details><summary>Answer</summary>

```text
[5, 10, 15, 15]
True
3
```

`x[-1]` is the last slot. It gets `5 + 10 = 15`. `x[len(x) - 1]` is the long way of writing `x[-1]`. `x[1:]` is a slice holding everything after the first item, so its length is 3.

</details>

### Common misconceptions

- "The last item is `x[len(x)]`." No, that is one past the end. The last item is `x[len(x) - 1]`, or simply `x[-1]`.
- "A list stores the values inside it." It stores **references** to objects, as section 6 explains. This one fact explains most surprises in this chapter.

---

## 3. List methods

A list has methods for changing it in place. Here are the ones you will use every day.

| Method | What it does | Returns |
|---|---|---|
| `a.append(x)` | adds `x` at the end | `None` |
| `a.extend(items)` | adds every item from an iterable at the end | `None` |
| `a.insert(i, x)` | puts `x` before position `i` | `None` |
| `a.remove(x)` | removes the **first** item equal to `x`, error if none | `None` |
| `a.pop()` | removes and returns the last item | the item |
| `a.pop(i)` | removes and returns the item at `i` | the item |
| `a.index(x)` | position of the first item equal to `x`, error if none | an int |
| `a.count(x)` | how many items equal `x` | an int |
| `a.sort()` | sorts in place | `None` |
| `a.reverse()` | reverses in place | `None` |
| `a.clear()` | removes everything | `None` |
| `a.copy()` | a new list with the same items | a new list |

```python
a = [3, 1, 4]
a.append(1)
print(a)
a.extend([5, 9])
print(a)
a.insert(0, 100)
print(a)
a.remove(1)
print(a)
last = a.pop()
print(last, a)
first = a.pop(0)
print(first, a)
print(a.index(4), a.count(1))
a.sort()
print(a)
a.reverse()
print(a)
```

Output:

```text
[3, 1, 4, 1]
[3, 1, 4, 1, 5, 9]
[100, 3, 1, 4, 1, 5, 9]
[100, 3, 4, 1, 5, 9]
9 [100, 3, 4, 1, 5]
100 [3, 4, 1, 5]
1 1
[1, 3, 4, 5]
[5, 4, 3, 1]
```

Notice that `remove(1)` removed only the **first** `1`. To remove every copy, build a new list without them (section 16 shows the neat way).

### Methods that change a list return None

This is the most common list mistake of all. Methods like `append`, `sort` and `reverse` change the list **and return `None`**. They do not hand back the list.

```python
nums = [3, 1, 2]
result = nums.sort()
print(result)
print(nums)
nums = nums.append(4)
print(nums)
```

Output:

```text
None
[1, 2, 3]
None
```

The line `nums = nums.append(4)` appended `4` to the list, then took the `None` that `append` returned and stuck the label `nums` onto it. The list is now lost. The rule is simple: a method that changes a list in place returns `None`, so never assign its result.

### append versus extend

`append` adds **one** item, whatever it is. `extend` adds **each** item of an iterable.

```python
a = [1, 2]
a.append([3, 4])
print(a, len(a))
b = [1, 2]
b.extend([3, 4])
print(b, len(b))
c = [1, 2]
c.extend("hi")
print(c)
```

Output:

```text
[1, 2, [3, 4]] 3
[1, 2, 3, 4] 4
[1, 2, 'h', 'i']
```

`extend("hi")` added two items, `'h'` and `'i'`, because a string is an iterable of characters.

### + makes a new list, += changes the old one

`a + b` builds a **new** list. `a += b` changes `a` **in place**, like `a.extend(b)`. The difference is invisible until a second name refers to the same list.

```python
a = [1, 2]
b = a
a = a + [3]
print(a, b)
c = [1, 2]
d = c
c += [3]
print(c, d)
```

Output:

```text
[1, 2, 3] [1, 2]
[1, 2, 3] [1, 2, 3]
```

With `a = a + [3]`, a new list was made and only the label `a` moved to it. `b` still sees the old list. With `c += [3]`, the one shared list was extended, so `d` sees the change too. Remember this: for lists, `+=` is a mutation, not a rebinding. For ints and strings `+=` must rebind, because those objects cannot change.

`*` repeats a list: `[0] * 4` is `[0, 0, 0, 0]`. Keep that in mind for section 8.

### Edge cases

```python
a = [1, 2, 3]
print(a.pop(-2), a)
a.insert(100, "end")
print(a)
a.insert(-100, "start")
print(a)
a.remove(99)
```

Output:

```text
2 [1, 3]
[1, 3, 'end']
['start', 1, 3, 'end']
Traceback (most recent call last):
  File "example.py", line 7, in <module>
    a.remove(99)
    ~~~~~~~~^^^^
ValueError: list.remove(x): x not in list
```

`insert` never fails: a position past the end just appends, and one before the start puts the item first. `remove` and `index` raise `ValueError` when the value is missing, and `pop` on an empty list raises `IndexError`. When you are not sure the value exists, check first with `if x in a:`.

### Predict the output

```python
a = [1, 2, 3]
b = a.append(4)
print(a, b)
a.extend([5])
a.append([6])
print(len(a), a[-1])
print(a.pop(), a.count(5))
```

<details><summary>Answer</summary>

```text
[1, 2, 3, 4] None
6 [6]
[6] 1
```

`append` changes `a` and returns `None`, so `b` is `None`. After `extend([5])` the list has five items, and `append([6])` adds one more item, the list `[6]`, giving length 6. `pop()` removes and returns that last item.

</details>

### Common misconceptions

- "`a.sort()` gives me a sorted list." It gives `None`. Use `sorted(a)` when you want a new sorted list (section 17).
- "`remove(x)` removes every `x`." Only the first.
- "`a + b` and `a += b` are the same." The first makes a new list; the second changes `a` in place.

---

## 4. Slicing, slice assignment and del

You met slicing with strings in core.03. Lists slice the same way: `a[start:stop:step]` gives the items from `start` up to but **not including** `stop`, moving by `step`. Missing parts take sensible defaults.

```python
a = [10, 20, 30, 40, 50, 60]
print(a[1:4])
print(a[:3])
print(a[3:])
print(a[-2:])
print(a[::2])
print(a[1::2])
print(a[::-1])
print(a[4:100])
print(a[5:2])
```

Output:

```text
[20, 30, 40]
[10, 20, 30]
[40, 50, 60]
[50, 60]
[10, 30, 50]
[20, 40, 60]
[60, 50, 40, 30, 20, 10]
[50, 60]
[]
```

Slices never raise `IndexError`. A slice that runs past the end is simply cut short, and a slice whose start is after its stop is just empty.

A slice of a list is a **new list**. That is why `a[:]`, the slice of everything, is a common way to copy a list. Section 7 explains exactly what kind of copy it is.

### Slice assignment

Here lists can do something strings cannot. You can assign **to** a slice. The slice on the left is cut out and replaced by the items of the iterable on the right. The two sides do not need the same length, so the list can grow or shrink.

```python
a = [0, 1, 2, 3, 4, 5]
a[1:3] = ["x", "y"]
print(a)
a[1:3] = ["only one"]
print(a)
a[1:2] = [7, 8, 9]
print(a)
a[2:2] = ["inserted"]
print(a)
a[:0] = ["front"]
print(a)
a[len(a):] = ["back"]
print(a)
a[:] = []
print(a)
```

Output:

```text
[0, 'x', 'y', 3, 4, 5]
[0, 'only one', 3, 4, 5]
[0, 7, 8, 9, 3, 4, 5]
[0, 7, 'inserted', 8, 9, 3, 4, 5]
['front', 0, 7, 'inserted', 8, 9, 3, 4, 5]
['front', 0, 7, 'inserted', 8, 9, 3, 4, 5, 'back']
[]
```

Read each line as "remove this stretch, put these items in its place":

- `a[1:3] = ["only one"]` removed two items and put one back, so the list shrank.
- `a[2:2] = [...]` is an empty stretch, so nothing was removed. This is an insert.
- `a[:] = []` replaced everything with nothing. Unlike `a = []`, it empties **the same list object**, so every other name for the list sees it empty too.

There is one restriction. When the slice has a step other than 1 (an *extended slice*), the right side must have exactly as many items as the slice selects, because there is no sensible way to grow a "every second item" pattern.

```python
a = [0, 1, 2, 3, 4, 5]
a[::2] = ["a", "b", "c"]
print(a)
a[::2] = [1, 2]
```

Output:

```text
['a', 1, 'b', 3, 'c', 5]
Traceback (most recent call last):
  File "example.py", line 4, in <module>
    a[::2] = [1, 2]
    ~^^^^^
ValueError: attempt to assign sequence of size 2 to extended slice of size 3
```

### Deleting with del

`del` removes by index or by slice. It is a statement, not a method, and it returns nothing.

```python
a = [0, 1, 2, 3, 4, 5, 6, 7]
del a[0]
print(a)
del a[-1]
print(a)
del a[1:3]
print(a)
del a[::2]
print(a)
```

Output:

```text
[1, 2, 3, 4, 5, 6, 7]
[1, 2, 3, 4, 5, 6]
[1, 4, 5, 6]
[4, 6]
```

`del a[1:3]` means the same as `a[1:3] = []`. `del a` with no index would remove the **name** `a`, not the list; the list lives on if another name still refers to it.

### Predict the output

```python
a = [1, 2, 3, 4, 5]
a[1:4] = a[1:4][::-1]
print(a)
a[-1:] = [50, 60]
print(a)
del a[::3]
print(a)
```

<details><summary>Answer</summary>

```text
[1, 4, 3, 2, 5]
[1, 4, 3, 2, 50, 60]
[4, 3, 50, 60]
```

`a[1:4]` is `[2, 3, 4]`, reversed to `[4, 3, 2]` and put back in the same stretch. `a[-1:]` is the stretch holding the last item; replacing it with two items grows the list. `del a[::3]` removes indexes 0 and 3 of `[1, 4, 3, 2, 50, 60]`, which are `1` and `2`.

</details>

### Common misconceptions

- "`a[1:3] = x` puts `x` into the list as one item." It puts in the **items of** `x`. Write `a[1:3] = [x]` to put in one item.
- "`a = []` and `a[:] = []` are the same." The first moves the label; the second empties the object everyone shares.

---

## 5. Nested lists

A list can hold anything, including other lists. A list of lists is the natural way to store a table or a grid. Each inner list is one **row**.

```python
grid = [
    [1, 2, 3],
    [4, 5, 6],
]
print(grid[0])
print(grid[1][2])
grid[0][1] = 20
print(grid)
print(len(grid), len(grid[0]))
for row in grid:
    for value in row:
        print(value, end=" ")
    print()
```

Output:

```text
[1, 2, 3]
6
[[1, 20, 3], [4, 5, 6]]
2 3
1 20 3 
4 5 6 
```

Read `grid[1][2]` from left to right. `grid[1]` is the second row, `[4, 5, 6]`. Then `[2]` picks the third item of that row. The first index chooses the row, the second chooses the column.

### Printing a grid nicely

`" ".join(...)` needs strings, so convert numbers first:

```python
grid = [[1, 2, 3], [4, 5, 6]]
for row in grid:
    print(" ".join(str(v) for v in row))
```

Output:

```text
1 2 3
4 5 6
```

### Reading a grid from input

A common pattern is: read the number of rows, then read each row as a line of numbers.

```python
rows = int(input())
grid = []
for _ in range(rows):
    grid.append([int(x) for x in input().split()])
```

The name `_` is a convention for "a loop variable I do not use".

Building each row with its own `append` gives each row its own list object. That detail matters a lot in section 8.

### Common misconceptions

- "`grid[1, 2]` gets row 1, column 2." In Python that is indexing with a tuple, and a list rejects it with `TypeError`. Write `grid[1][2]`.
- "A nested list holds copies of the rows." It holds references to them, as the next section shows.

---

## 6. Under the hood: how a list is stored

To understand aliasing and the cost of list operations, you need a picture of what a list really is in memory.

### A list is an array of references

In CPython (the standard Python), a list object holds two main things:

1. a count of how many items it has, and
2. a pointer to a block of memory holding a row of **references**, one per item.

A reference is the memory address of an object. The list does **not** contain the objects themselves. The numbers, strings and inner lists live elsewhere in memory; the list only holds arrows to them.

```
names = ["Asha", "Ravi", "Asha"]

 names                                    objects in memory
   |
   v
 +------------------+
 | list object      |
 | size: 3          |
 | items: ----------+--> +---+---+---+
 +------------------+    | o | o | o |
                         +-|-+-|-+-|-+
                           |   |   |
                           |   |   +--------+
                           v   v            |
                     "Asha"   "Ravi"  <-----+   (may be the same "Asha" object,
                                                  or another equal one)
```

Because every slot is a reference of the same size, the list can jump straight to slot `i` by arithmetic: start address plus `i` times the size of one reference. That is why `a[i]` takes the same short time whether the list has 10 items or 10 million. We say indexing is **O(1)**, "constant time".

### Big-O in one paragraph

**Big-O notation** describes how the work grows as the input grows. O(1) means the work does not depend on the size n. O(n) means the work grows in proportion to n: double the list, double the time. O(n²) means doubling n makes it four times slower. Big-O ignores constant factors and small details. It answers one question: "if my data gets 1,000 times bigger, how much slower will this be?" A whole DSA module covers this properly; here we need only the basic idea.

### Growth and amortised append

The block of references has a fixed size. So what happens when you `append` and the block is full? CPython allocates a **bigger** block, copies all the references across, and frees the old block. Copying n references costs O(n). If that happened on every append, building a list of n items would cost O(n²).

CPython avoids this by **over-allocating**. When it grows the block, it adds spare room, roughly an extra eighth of the current size plus a little. The next several appends just fill spare slots, which is O(1) each. Only occasionally does a full copy happen.

You can watch this with `sys.getsizeof`, which reports the bytes used by the list object and its block of references (not the items they point to):

```python
import sys
a = []
last = sys.getsizeof(a)
print(0, last)
for i in range(1, 30):
    a.append(i)
    size = sys.getsizeof(a)
    if size != last:
        print(len(a), size)
        last = size
```

Output:

```text
0 56
1 88
5 120
9 184
17 248
25 312
```

The size jumps only at certain lengths. Between jumps, appends are cheap. Adding up the occasional big copies and spreading their cost over all the appends gives a constant amount of work per append on average. This is called **amortised O(1)**. "Amortised" means "averaged over a long run of operations", the way a yearly fee is spread across twelve months.

### Why insert(0) and pop(0) are slow

The references sit side by side in order. To put a new item at the front, every existing reference must shift one slot to the right to make room. For a list of n items that is n moves, so `insert(0, x)` is O(n). `pop(0)` and `del a[0]` must shift everything left, also O(n). `append` and `pop()` at the **end** move nothing, which is why they are fast.

On a list of 50,000 items, inserting every item at the front instead of appending takes around a hundred times longer, and the gap widens as n grows, because each insert costs more than the last. If you truly need fast adding and removing at both ends, Python has `collections.deque`, covered in core.17.

### Why `in` on a list is slow

`x in a` has no shortcut. The list does not know where `x` might be, so it compares `x` with each item from the start until it finds a match or runs out. That is O(n). One membership test is fine. A membership test **inside a loop** over n items is O(n²), and that is where programs become painfully slow.

On the machine used to write this chapter, 20,000 membership tests against a 20,000-item list took about 1.8 seconds. The same tests against a set took about 0.004 seconds.

A set answers `in` in O(1) on average, using hashing (section 13). With 20,000 items the set is hundreds of times faster. With a million items, the list version would take hours.

### Common misconceptions

- "`append` is O(1) every time." It is O(1) **on average**. A single append that triggers a resize costs O(n), but such appends are rare.
- "Removing from the front is cheap because it is only one item." Shifting all the others is not.

---

## 7. Aliasing, shallow copies and deep copies

### Aliasing

Two names that refer to the same object are called **aliases**. With immutable objects, aliasing is harmless, because nothing can change. With a list, a change made through one name is visible through every alias, because there is only one list.

```python
original = [1, 2, 3]
alias = original
alias.append(4)
print(original)
print(alias is original)
```

Output:

```text
[1, 2, 3, 4]
True
```

`alias = original` copied nothing. It stuck a second label on the same list. This is the rule from core.02, now with real consequences: **assignment never copies**.

Aliasing is not a bug in itself. It is often exactly what you want, for example when a nested list holds a reference to a row and you change the row through it. It becomes a bug when you **think** you have two independent lists but you really have one.

### Making a copy

There are four everyday ways to copy a list. All four make a **new outer list**:

```python
import copy
a = [1, 2, 3]
b = a.copy()
c = list(a)
d = a[:]
e = copy.copy(a)
b.append("b")
print(a)
print(b, c, d, e)
print(a is b, a is c, a is d, a is e)
```

Output:

```text
[1, 2, 3]
[1, 2, 3, 'b'] [1, 2, 3] [1, 2, 3] [1, 2, 3]
False False False False
```

Each copy is a different list object (`is` gives `False`), so appending to `b` did not affect `a`.

### Shallow copies share the inner objects

All four of those copies are **shallow**. A shallow copy makes a new outer list and copies the **references** from the old one. The new list points to the very same item objects. With numbers and strings that does not matter, because those objects can never change. With **nested lists**, it matters a lot.

```python
grid = [[1, 2], [3, 4]]
copy_of_grid = grid.copy()
copy_of_grid.append([5, 6])
copy_of_grid[0][0] = 99
print(grid)
print(copy_of_grid)
print(grid[0] is copy_of_grid[0])
```

Output:

```text
[[99, 2], [3, 4]]
[[99, 2], [3, 4], [5, 6]]
True
```

Appending a new row to the copy did not affect `grid`, because the outer lists are different. But changing `copy_of_grid[0][0]` **did** affect `grid`, because both outer lists point to the same inner row. Here is the memory picture after the copy:

```
 grid ---------> [ o , o ]            (outer list 1)
                   |   |
                   v   v
                [1,2] [3,4]           (the inner rows, shared)
                   ^   ^
                   |   |
 copy_of_grid -> [ o , o ]            (outer list 2)
```

There are two outer lists, but only one of each row.

### Deep copies

`copy.deepcopy` copies the outer list **and**, recursively, everything mutable inside it. The result shares nothing changeable with the original.

```python
import copy
grid = [[1, 2], [3, 4]]
deep = copy.deepcopy(grid)
deep[0][0] = 99
print(grid)
print(deep)
print(grid[0] is deep[0])
```

Output:

```text
[[1, 2], [3, 4]]
[[99, 2], [3, 4]]
False
```

For a list of lists of numbers, you can also make a deep copy by hand by copying each row:

```python
grid = [[1, 2], [3, 4]]
by_hand = [row[:] for row in grid]
by_hand[1][1] = 0
print(grid, by_hand)
```

Output:

```text
[[1, 2], [3, 4]] [[1, 2], [3, 0]]
```

That works only one level down. If the rows themselves contained lists, you would need to go deeper, which is what `deepcopy` does for you.

### Under the hood

- `copy.deepcopy` keeps a memo (a dict) of objects it has already copied. If the same inner list appears twice in the original, the copy also has one list appearing twice, not two separate lists. This also lets it copy structures that contain themselves without looping forever.
- Immutable objects such as ints, strings and tuples of immutables are not copied by `deepcopy`; it simply reuses them, since sharing an object that cannot change is always safe.
- `deepcopy` is much slower than a shallow copy because it visits every object. Use it when you need it, not by habit.

### Mutating a list while looping over it

A related bug is changing a list while a `for` loop is walking over it. The loop keeps an internal position counter. If you remove an item, everything after it shifts left, and the loop skips the item that slid into the current position.

```python
nums = [1, 2, 2, 3, 2, 4]
for n in nums:
    if n == 2:
        nums.remove(n)
print(nums)
```

Output:

```text
[1, 3, 2, 4]
```

One `2` survived. Trace it: the loop is at position 1 (the first `2`) and removes it. The second `2` slides into position 1. The loop moves on to position 2, which is now `3`. The second `2` was never looked at.

The fix is to **build a new list** with only the items you want to keep, or to loop over a copy:

```python
nums = [1, 2, 2, 3, 2, 4]
kept = [n for n in nums if n != 2]
print(kept)
nums2 = [1, 2, 2, 3, 2, 4]
for n in nums2[:]:
    if n == 2:
        nums2.remove(n)
print(nums2)
```

Output:

```text
[1, 3, 4]
[1, 3, 4]
```

The comprehension is better: it is O(n), while each `remove` is O(n) by itself, making the second version O(n²).

### Predict the output

```python
a = [[0], [0]]
b = a[:]
c = a
b[0] = [7]
c[1].append(8)
print(a)
print(b)
print(a is c, a[1] is b[1])
```

<details><summary>Answer</summary>

```text
[[0], [0, 8]]
[[7], [0, 8]]
True True
```

`b` is a shallow copy, so `b[0] = [7]` replaces a slot in `b` only. `c` is an alias of `a`. `c[1].append(8)` mutates the inner list `a[1]`, which `b[1]` also refers to, so the `8` shows in both `a` and `b`.

</details>

### Common misconceptions

- "`b = a` makes a copy." It makes an alias.
- "`a.copy()` copies everything." It copies one level. Inner lists are shared.
- "Replacing an item in a shallow copy changes the original." Replacing (`b[0] = ...`) does not; **mutating** a shared inner object (`b[0].append(...)`) does.

---

## 8. The [[0] * 3] * 3 trap

This bug is so common it gets its own section. You want a 3 by 3 grid of zeros. This looks right:

```python
grid = [[0] * 3] * 3
print(grid)
grid[0][0] = 1
print(grid)
```

Output:

```text
[[0, 0, 0], [0, 0, 0], [0, 0, 0]]
[[1, 0, 0], [1, 0, 0], [1, 0, 0]]
```

You changed one cell, and a whole column changed. Why?

### What * does with a list

`[0] * 3` is fine. It makes a new list with three references to the int `0`. Since ints cannot change, sharing `0` is harmless. When you later write `row[0] = 1`, you **replace** a reference in that row; you do not change the `0` object.

The outer `* 3` does the same thing one level up. It makes a list with three references to **the same row object**. It does not copy the row. Here is the memory diagram:

```
                 +-----+-----+-----+
 grid  -------> |  o  |  o  |  o  |      outer list: 3 references
                 +--|--+--|--+--|--+
                    |     |     |
                    +-----+-----+
                          |
                          v
                 +-----+-----+-----+
                 |  o  |  o  |  o  |      ONE inner list
                 +--|--+--|--+--|--+
                    |     |     |
                    +-----+-----+
                          |
                          v
                        int 0
```

`grid[0]`, `grid[1]` and `grid[2]` are three names for one list. `grid[0][0] = 1` changes slot 0 of that one list, and you see the change "in every row" because all rows are the same row.

You can prove it with `is`:

```python
grid = [[0] * 3] * 3
print(grid[0] is grid[1], grid[1] is grid[2])
good = [[0] * 3 for _ in range(3)]
print(good[0] is good[1])
```

Output:

```text
True True
False
```

### The fix

Make a **new** row for each position. A comprehension runs its expression once per item, so `[0] * 3` is evaluated three separate times, giving three separate lists:

```python
grid = [[0] * 3 for _ in range(3)]
grid[0][0] = 1
print(grid)
```

Output:

```text
[[1, 0, 0], [0, 0, 0], [0, 0, 0]]
```

The memory picture is now:

```
 grid -------> [ o , o , o ]
                 |   |   |
                 v   v   v
             [0,0,0] [0,0,0] [0,0,0]     three separate rows
```

### Why the inner * 3 is safe but the outer one is not

Both use `*`, and both copy references. The difference is what the references point to.

- The inner list repeats references to `0`, an **immutable** int. You can only replace those references, never change the `0`. So sharing causes no trouble.
- The outer list repeats references to a **mutable** list. `grid[0][0] = 1` does not replace `grid[0]`; it reaches into the shared row and changes it.

The general rule: `[x] * n` is safe when `x` is immutable, and a trap when `x` is mutable. The same trap appears with `[[]] * 3` (three references to one empty list) and `[{}] * 3`.

```python
buckets = [[]] * 3
buckets[0].append("a")
print(buckets)
```

Output:

```text
[['a'], ['a'], ['a']]
```

### Predict the output

```python
rows = [[0] * 2] * 2
rows[0] = [5, 5]
rows[1][0] = 9
print(rows)
```

<details><summary>Answer</summary>

```text
[[5, 5], [9, 0]]
```

Tricky. At first both slots point to one row. `rows[0] = [5, 5]` **replaces** slot 0 with a brand new list, so now the two slots point to different lists. `rows[1][0] = 9` changes only the old row, which is now only in slot 1.

</details>

### Common misconceptions

- "`*` copies the list." It repeats references. Nothing inside is copied.
- "Only `[[0] * 3] * 3` has this problem." Any `[mutable] * n` has it, including `[[]] * n`.

---

## 9. Tuples, packing and unpacking

A **tuple** is an ordered sequence like a list, but **immutable**: once made, it cannot be changed. You write it with commas, usually inside round brackets.

```python
point = (3, 4)
person = ("Asha", 19, "Pune")
print(point[0], person[-1], len(person))
print(person[1:])
print(point + (5,), point * 2)
print(point.count(3), person.index(19))
point[0] = 10
```

Output:

```text
3 Pune 3
(19, 'Pune')
(3, 4, 5) (3, 4, 3, 4)
1 1
Traceback (most recent call last):
  File "example.py", line 7, in <module>
    point[0] = 10
    ~~~~~^^^
TypeError: 'tuple' object does not support item assignment
```

Tuples support everything that reads: indexing, slicing, `len`, `in`, looping, `count` and `index`. They have no `append`, `remove` or item assignment.

### The comma makes the tuple

The brackets are only for grouping. It is the **comma** that makes a tuple. This gives the most famous tuple surprise: a single value in brackets is not a tuple.

```python
a = (5)
b = (5,)
c = 5,
d = ()
print(type(a), type(b), type(c), type(d))
print(b, len(b), len(d))
```

Output:

```text
<class 'int'> <class 'tuple'> <class 'tuple'> <class 'tuple'>
(5,) 1 0
```

`(5)` is just the number 5 in brackets, like `(2 + 3)`. A **one-item tuple** needs a trailing comma: `(5,)`. The empty tuple `()` is the one case written without a comma.

### Packing and unpacking

Writing several values separated by commas **packs** them into a tuple. Putting several names on the left of `=` **unpacks** a sequence into those names.

```python
t = 1, 2, 3
print(t)
x, y, z = t
print(x, y, z)
name, age = ["Ravi", 20]
print(name, age)
first, second = "hi"
print(first, second)
```

Output:

```text
(1, 2, 3)
1 2 3
Ravi 20
h i
```

Unpacking works with any iterable, not only tuples. The number of names must match the number of items exactly:

```python
a, b = (1, 2, 3)
```

Output:

```text
Traceback (most recent call last):
  File "example.py", line 1, in <module>
    a, b = (1, 2, 3)
    ^^^^
ValueError: too many values to unpack (expected 2, got 3)
```

### Swapping

Packing and unpacking together give Python its neat swap:

```python
a, b = 1, 2
a, b = b, a
print(a, b)
```

Output:

```text
2 1
```

How does this work without a temporary variable? The right side `b, a` is **evaluated first**, building the tuple `(2, 1)`. Only then are the names on the left bound, in order. The old values were safely captured in the tuple before any name moved.

### Star unpacking

A name with a `*` in front collects "all the rest" into a **list**. There can be at most one starred name.

```python
first, *rest = [10, 20, 30, 40]
print(first, rest)
*start, last = [10, 20, 30, 40]
print(start, last)
head, *middle, tail = "abcde"
print(head, middle, tail)
a, *b = [1]
print(a, b)
```

Output:

```text
10 [20, 30, 40]
[10, 20, 30] 40
a ['b', 'c', 'd'] e
1 []
```

The starred name always gets a list, even when it collects nothing (`b` is `[]`).

### Unpacking in for loops

`enumerate` and `zip` produce tuples, which is why `for i, x in enumerate(a)` works. In the same way, `for name, mark in pairs:` unpacks each pair of a list of pairs.

### Tuples containing lists

A tuple's slots cannot be changed. But if a slot refers to a mutable object, **that object** can still change.

```python
t = (1, [2, 3])
t[1].append(4)
print(t)
t[1] = [9]
```

Output:

```text
(1, [2, 3, 4])
Traceback (most recent call last):
  File "example.py", line 4, in <module>
    t[1] = [9]
    ~^^^
TypeError: 'tuple' object does not support item assignment
```

The tuple still holds the same two references. The list it refers to has grown. "Immutable" means the references cannot change, not that everything reachable from the tuple is frozen. This matters for hashing in section 14.

### When to use a tuple

Use a tuple for a fixed group of related values where the position gives the meaning, like a point `(x, y)`, and whenever you need a dict key or set member (section 14). Use a list for a varying number of similar items.

### Predict the output

```python
a, *b, c = range(5)
print(a, b, c)
x = 1,
y = (1)
print(x == y, len(x))
p, q = q, p = 3, 4
print(p, q)
```

<details><summary>Answer</summary>

```text
0 [1, 2, 3] 4
False 1
4 3
```

`range(5)` unpacks as `0, [1, 2, 3], 4`. `x` is the tuple `(1,)` and `y` is the int `1`, which are not equal. The last line is a chained assignment: the tuple `(3, 4)` is assigned first to `p, q` (giving `p = 3`, `q = 4`), then to `q, p` (giving `q = 3`, `p = 4`).

</details>

### Common misconceptions

- "Brackets make a tuple." The comma does. `(5)` is an int.
- "A tuple can never change in any way." Its references cannot; a list inside it can.
- "`*rest` gives a tuple." It gives a list.

---

## 10. namedtuple

A plain tuple uses positions for meaning. `person[1]` is the age only because you remember that it is. A **namedtuple** gives each position a name, so you can write `person.age`. It is still a real tuple underneath.

`namedtuple` lives in the `collections` module. The rest of that module comes in core.17; this one tool belongs here because it is simply a better tuple.

```python
from collections import namedtuple

Point = namedtuple("Point", ["x", "y"])
p = Point(3, 4)
print(p)
print(p.x, p.y)
print(p[0], p[1])
x, y = p
print(x + y)
q = Point(y=10, x=1)
print(q)
print(isinstance(p, tuple), p == (3, 4))
```

Output:

```text
Point(x=3, y=4)
3 4
3 4
7
Point(x=1, y=10)
True True
```

The call `namedtuple("Point", ["x", "y"])` creates a new **type**, and you name it `Point`. The first argument is the name used when printing. You then make points by calling `Point(...)`, by position or by field name.

Because a namedtuple is a tuple, it is immutable. To get a changed version, use `_replace`, which returns a **new** namedtuple. The underscore is there only to keep the method name from clashing with your field names.

```python
from collections import namedtuple
Student = namedtuple("Student", "name marks city")
s = Student("Meena", 88, "Nagpur")
s2 = s._replace(marks=91)
print(s)
print(s2)
print(s._fields)
print(s._asdict())
s.marks = 95
```

Output:

```text
Student(name='Meena', marks=88, city='Nagpur')
Student(name='Meena', marks=91, city='Nagpur')
('name', 'marks', 'city')
{'name': 'Meena', 'marks': 88, 'city': 'Nagpur'}
Traceback (most recent call last):
  File "example.py", line 9, in <module>
    s.marks = 95
    ^^^^^^^
AttributeError: can't set attribute
```

The field names can be given as a list or as one string separated by spaces. `_fields` lists them, and `_asdict()` turns the namedtuple into a dict.

### When to use namedtuple

Use it for small, fixed records: points, colours, a row from a file. It costs no more memory than a plain tuple, because the field names are stored once on the type. Records you can change come later, with classes.

### Common misconceptions

- "`p.x = 5` will update the point." Namedtuples are immutable; use `p = p._replace(x=5)`.
- "A namedtuple is a dict." It is a tuple with named positions. Use `_asdict()` if you need a dict.

---

## 11. Dicts

A **dict** (dictionary) maps **keys** to **values**. You look things up by key instead of by position. Think of a phone's contact list: you search by name, and you get the number.

```python
phone = {"Asha": "98200", "Ravi": "98111"}
print(phone["Asha"])
phone["Meena"] = "99000"
phone["Asha"] = "90000"
print(phone)
print(len(phone), "Ravi" in phone, "98111" in phone)
del phone["Ravi"]
print(phone)
print(phone["Kiran"])
```

Output:

```text
98200
{'Asha': '90000', 'Ravi': '98111', 'Meena': '99000'}
3 True False
{'Asha': '90000', 'Meena': '99000'}
Traceback (most recent call last):
  File "example.py", line 9, in <module>
    print(phone["Kiran"])
          ~~~~~^^^^^^^^^
KeyError: 'Kiran'
```

Look at what each line did:

- `phone["Meena"] = ...` **added** a new key, because `"Meena"` was not there.
- `phone["Asha"] = ...` **replaced** the value, because the key already existed. Keys are unique; there can never be two `"Asha"` entries.
- `in` checks **keys**, not values. `"98111" in phone` is `False` even though it is a value.
- Reading a missing key raises `KeyError`.

### Creating dicts

```python
a = {}
b = dict(name="Asha", age=19)
c = dict([("x", 1), ("y", 2)])
d = dict(zip(["p", "q"], [10, 20]))
e = dict.fromkeys(["a", "b", "c"], 0)
print(a, b, c, d, e, sep="\n")
```

Output:

```text
{}
{'name': 'Asha', 'age': 19}
{'x': 1, 'y': 2}
{'p': 10, 'q': 20}
{'a': 0, 'b': 0, 'c': 0}
```

`{}` is an **empty dict**, not an empty set. `dict()` accepts keyword arguments or a sequence of pairs, which makes `dict(zip(keys, values))` a handy way to pair up two lists.

### Insertion order

Since Python 3.7, a dict **remembers the order** in which keys were first added. Looping and printing follow that order. Replacing the value of an existing key does not move it. Deleting a key and adding it again puts it at the end.

```python
d = {"b": 1, "a": 2}
d["c"] = 3
d["b"] = 10
print(d)
del d["b"]
d["b"] = 20
print(d)
```

Output:

```text
{'b': 10, 'a': 2, 'c': 3}
{'a': 2, 'c': 3, 'b': 20}
```

Two dicts are equal when they have the same key-value pairs; order does not matter for `==`.

### Safe reading: get

`d.get(key)` returns the value, or `None` if the key is missing. `d.get(key, default)` returns `default` instead. It never raises `KeyError`.

```python
stock = {"pen": 10, "ink": 0}
print(stock.get("pen"), stock.get("pad"), stock.get("pad", 0))
print(stock.get("ink", 99))
```

Output:

```text
10 None 0
0
```

`stock.get("ink", 99)` gives `0`, not `99`. The default is used only when the key is **missing**, not when the value is falsy.

### Counting with get

The most common dict pattern is counting. `counts.get(word, 0) + 1` reads the current count (0 if new) and adds one.

```python
words = "the cat and the hat and the bat".split()
counts = {}
for w in words:
    counts[w] = counts.get(w, 0) + 1
print(counts)
```

Output:

```text
{'the': 3, 'cat': 1, 'and': 2, 'hat': 1, 'bat': 1}
```

### Grouping with setdefault

`d.setdefault(key, default)` returns `d[key]` if the key exists. If not, it first stores `default` under the key and then returns it. That makes grouping into lists a one-liner per item:

```python
words = ["apple", "bat", "avocado", "cherry", "banana"]
groups = {}
for w in words:
    groups.setdefault(w[0], []).append(w)
print(groups)
```

Output:

```text
{'a': ['apple', 'avocado'], 'b': ['bat', 'banana'], 'c': ['cherry']}
```

For a new first letter, `setdefault` stores a fresh empty list and returns it, and `append` adds to it. For a letter already seen, it returns the existing list. Either way the word goes into the right list. The `[]` is evaluated every time, even when not needed, but making an empty list is cheap.

### pop, popitem, update, clear

```python
d = {"a": 1, "b": 2, "c": 3}
print(d.pop("a"))
print(d.pop("zzz", "missing"))
print(d.popitem())
print(d)
d.update({"b": 20, "e": 5})
d.update(f=6)
print(d)
d.clear()
print(d)
```

Output:

```text
1
missing
('c', 3)
{'b': 2}
{'b': 20, 'e': 5, 'f': 6}
{}
```

- `pop(key)` removes the key and returns its value. With a second argument it returns that instead of raising `KeyError` when the key is missing.
- `popitem()` removes and returns the **last added** pair as a tuple.
- `update(other)` copies every pair from `other` in, overwriting existing keys.

### Looping over a dict

Looping over a dict gives its **keys**. Use `.items()` to get key-value pairs, and unpack them.

```python
marks = {"Asha": 82, "Ravi": 75, "Meena": 91}
for name in marks:
    print(name, marks[name])
for name, mark in marks.items():
    print(f"{name}: {mark}")
print(sum(marks.values()), max(marks))
```

Output:

```text
Asha 82
Ravi 75
Meena 91
Asha: 82
Ravi: 75
Meena: 91
248 Ravi
```

`max(marks)` is the largest **key** in alphabetical order, because a dict behaves like its keys. To get the name with the highest mark, you need a key function (section 17): `max(marks, key=marks.get)`.

### Common misconceptions

- "`in` checks values." It checks keys. Use `x in d.values()` for values, and know that it is O(n).
- "`d.get(k, default)` gives the default when the value is 0." Only when the key is absent.
- "Dicts are unordered." They were before Python 3.7. Now insertion order is guaranteed.

---

## 12. Dict views, merging, and changing a dict while looping

### Views are live

`d.keys()`, `d.values()` and `d.items()` do not return lists. They return **view objects**: windows onto the dict. A view does not copy anything, and it always shows the dict's **current** contents.

```python
d = {"a": 1, "b": 2}
keys = d.keys()
items = d.items()
print(keys)
d["c"] = 3
print(keys)
print(items)
print(len(keys), "c" in keys)
frozen = list(d.keys())
d["z"] = 26
print(keys)
print(frozen)
```

Output:

```text
dict_keys(['a', 'b'])
dict_keys(['a', 'b', 'c'])
dict_items([('a', 1), ('b', 2), ('c', 3)])
3 True
dict_keys(['a', 'b', 'c', 'z'])
['a', 'b', 'c']
```

The view `keys` was created when the dict had two keys, yet after adding `"c"` it shows three. `list(d.keys())` makes a real list snapshot, which does not follow later changes.

Key views also support set operations, because keys are unique:

```python
a = {"x": 1, "y": 2}
b = {"y": 5, "z": 6}
print(sorted(a.keys() & b.keys()))
print(sorted(a.keys() - b.keys()))
```

Output:

```text
['y']
['x']
```

### Merging dicts with the pipe operator

Since Python 3.9, `a | b` makes a **new** dict containing the pairs of both. When a key is in both, the value from the **right** side wins. `a |= b` updates `a` in place, like `a.update(b)`.

```python
defaults = {"theme": "light", "size": 12}
user = {"size": 14, "lang": "hi"}
settings = defaults | user
print(settings)
print(defaults)
defaults |= {"theme": "dark"}
print(defaults)
```

Output:

```text
{'theme': 'light', 'size': 14, 'lang': 'hi'}
{'theme': 'light', 'size': 12}
{'theme': 'dark', 'size': 12}
```

The "right side wins" rule makes merging defaults with user choices natural: put the defaults on the left.

### Changing a dict while looping over it

Adding or removing keys while looping over a dict raises an error. Python detects that the size changed and refuses to go on, since the loop's position would no longer make sense.

```python
stock = {"pen": 0, "ink": 5, "pad": 0}
for item in stock:
    if stock[item] == 0:
        del stock[item]
```

Output:

```text
Traceback (most recent call last):
  File "example.py", line 2, in <module>
    for item in stock:
                ^^^^^
RuntimeError: dictionary changed size during iteration
```

The fix is the same as for lists: loop over a **snapshot** of the keys, or build a new dict.

```python
stock = {"pen": 0, "ink": 5, "pad": 0}
for item in list(stock):
    if stock[item] == 0:
        del stock[item]
print(stock)
stock2 = {"pen": 0, "ink": 5, "pad": 0}
in_stock = {k: v for k, v in stock2.items() if v > 0}
print(in_stock)
```

Output:

```text
{'ink': 5}
{'ink': 5}
```

Changing the **value** of an existing key during a loop is allowed, because it does not change the dict's size or shape: `for k in d: d[k] += 1` is fine.

### Predict the output

```python
d = {"x": 1}
v = d.values()
d["y"] = 2
d["x"] = 10
print(list(v))
e = d | {"x": 0}
print(d["x"], e["x"], list(e))
```

<details><summary>Answer</summary>

```text
[10, 2]
10 0 ['x', 'y']
```

The view `v` shows current values, in key order: `x` (now 10), then `y`. In `d | {"x": 0}`, the right side wins for `x`, but `x` keeps its original position because it was first inserted from `d`. `d` itself is unchanged by the pipe operator.

</details>

---

## 13. Under the hood: hashing

How can a dict find `phone["Meena"]` among a million entries without checking them one by one? The answer is **hashing**.

### The hash function

`hash(x)` turns a value into an integer, called its **hash**. Equal values always give equal hashes. Different values usually give different hashes, though not always.

```python
print(hash(42), hash(42.0), hash(True), hash(1))
print(hash((1, 2)) == hash((1, 2)))
print(hash("abc") == hash("abc"))
```

Output:

```text
42 42 1 1
True
True
```

Small ints hash to themselves. `42.0 == 42`, so they must hash the same, and they do. String hashes are not shown here on purpose: Python mixes a random value into string hashes each time it starts (a security feature called *hash randomisation*), so `hash("abc")` gives a different number in each run, though always the same number within one run.

### The hash table

A dict stores its entries in a **hash table**, a block of slots. To store a key:

1. Compute `hash(key)`.
2. Use that number to choose a slot, roughly `hash % number_of_slots`.
3. Put the key, its hash and the value in that slot.

To look a key up, Python repeats steps 1 and 2 and goes **straight** to that slot. No scanning. That is why lookup, insert and delete are **O(1) on average**.

```
 key "Meena" --hash--> 7395...41 --% 8--> slot 1

  slot:   0       1                  2      3     ...    7
       +-----+---------------------+-----+-----+-     -+-----+
       |     | "Meena" -> "99000"  |     | ... |       |     |
       +-----+---------------------+-----+-----+-     -+-----+
```

### Collisions

Two different keys can land in the same slot. This is a **collision**. CPython handles it by trying other slots in a fixed pattern until it finds the key or an empty slot. When it finds a slot with a matching hash, it also checks the keys with `==`, because equal hashes do not prove equal keys. Collisions cost a little extra time. With a good hash function they are rare, so the average stays O(1).

To keep collisions rare, the table is never allowed to get too full. When it passes about two thirds full, CPython builds a bigger table and re-inserts everything. Like list growth, this occasional O(n) step averages out to O(1) per insert.

### Sets use the same idea

A set is a hash table holding keys with no values. So `x in some_set` is also O(1) on average. That is the speed difference you measured in section 6.

---

## 14. Hashability: what can be a key

A dict key and a set member must be **hashable**. An object is hashable when:

1. it has a hash value that **never changes** during its lifetime, and
2. objects that are equal (`==`) have the same hash.

In practice:

| Type | Hashable? | Why |
|---|---|---|
| int, float, bool, str, None | yes | immutable |
| tuple | yes, if every item is hashable | immutable, and its hash is built from its items |
| frozenset | yes | immutable set |
| list | no | mutable |
| dict | no | mutable |
| set | no | mutable |

```python
ok = {1: "int", "a": "str", (1, 2): "tuple", None: "none", frozenset({1}): "frozenset"}
print(len(ok))
bad = {[1, 2]: "list"}
```

Output:

```text
5
Traceback (most recent call last):
  File "example.py", line 3, in <module>
    bad = {[1, 2]: "list"}
          ^^^^^^^^^^^^^^^^
TypeError: cannot use 'list' as a dict key (unhashable type: 'list')
```

### Why a list cannot be a key

Imagine Python allowed it. You store a value under the key `[1, 2]`. Python computes the hash of `[1, 2]` and puts the entry in, say, slot 5. Then you append to that same list, so the key is now `[1, 2, 3]`. Its hash would be different. Now:

- Looking up `[1, 2, 3]` computes the new hash, goes to some other slot, and finds nothing.
- Looking up `[1, 2]` goes to slot 5, finds the entry, but the stored key is now `[1, 2, 3]`, which is not equal to `[1, 2]`. No match.

The entry is still in the dict but can never be found. The table is silently broken. Python prevents this by refusing to hash mutable built-in types at all. `hash([1, 2])` raises `TypeError`.

### Why a tuple of ints can be a key

A tuple cannot change, and ints cannot change, so the hash of `(1, 2)` is the same forever. It is perfectly safe as a key. Tuples are the standard way to use a **compound key**, like a grid position:

```python
board = {}
board[(0, 0)] = "X"
board[(1, 2)] = "O"
print(board[(1, 2)], (2, 2) in board)
print(board.get((5, 5), "."))
```

Output:

```text
O False
.
```

The brackets are optional in a subscript: `board[1, 2]` means the same as `board[(1, 2)]`.

### A tuple containing a list is not hashable

A tuple is hashable only if everything in it is hashable. If it holds a list, that list could change, so the tuple's hash could change.

```python
t = (1, [2, 3])
print(hash(t))
```

Output:

```text
Traceback (most recent call last):
  File "example.py", line 2, in <module>
    print(hash(t))
          ~~~~^^^
TypeError: unhashable type: 'list'
```

### Equal keys are the same key

Since `1 == 1.0 == True` and their hashes are equal, a dict treats them as **one** key. The first key object stays; the value is replaced.

```python
d = {1: "int"}
d[1.0] = "float"
d[True] = "bool"
print(d)
```

Output:

```text
{1: 'bool'}
```

You will rarely meet this in real code, but it shows exactly how lookup works: hash first, then `==`.

### Predict the output

```python
s = {(1, 2), (2, 1), (1, 2)}
print(len(s))
d = {}
d[frozenset([1, 2])] = "pair"
print(d[frozenset([2, 1])])
key = ("a", (1, 2))
d[key] = "nested"
print(len(d))
```

<details><summary>Answer</summary>

```text
2
pair
2
```

`(1, 2)` and `(2, 1)` are different tuples (order matters), and the duplicate `(1, 2)` is dropped, so the set has 2 items. Frozensets ignore order, so `frozenset([2, 1])` equals `frozenset([1, 2])` and finds the same entry. A tuple holding a string and a tuple of ints is fully hashable, so the dict now has 2 keys.

</details>

### Common misconceptions

- "Tuples are always hashable." Only if all their items are.
- "Lists can't be keys because Python can't compute a hash for them." It could; it refuses, because the hash would go stale when the list changed.

---

## 15. Sets and frozensets

A **set** is an unordered collection of **unique**, hashable items. It answers one question very fast: "is this in here?". It also does set algebra from mathematics.

```python
s = {3, 1, 4, 1, 5, 9, 2, 6, 5}
print(s)
print(len(s), 4 in s, 7 in s)
empty = set()
print(type({}), type(empty))
print(set("banana") == {"a", "b", "n"})
```

Output:

```text
{1, 2, 3, 4, 5, 6, 9}
7 True False
<class 'dict'> <class 'set'>
True
```

Duplicates vanished. The printed order happens to be sorted here because small ints hash to themselves, but **never rely on set order**. Sets of strings come out in a different order on different runs. When you print a set's items for people to read, use `sorted(s)`.

To make an empty set you must write `set()`, because `{}` is an empty dict.

### Changing a set

```python
s = {1, 2}
s.add(3)
s.add(2)
print(sorted(s))
s.update([4, 5])
print(sorted(s))
s.remove(5)
s.discard(99)
print(sorted(s))
s.remove(99)
```

Output:

```text
[1, 2, 3]
[1, 2, 3, 4, 5]
[1, 2, 3, 4]
Traceback (most recent call last):
  File "example.py", line 10, in <module>
    s.remove(99)
    ~~~~~~~~^^^^
KeyError: 99
```

`remove` raises `KeyError` for a missing item; `discard` silently does nothing. Use `discard` when "already gone" is fine. `pop()` removes and returns an arbitrary item. A set has no indexing: `s[0]` is a `TypeError`, since there is no "first" item.

### Set algebra

| Operation | Operator | Method | Meaning |
|---|---|---|---|
| union | the pipe operator, `a` pipe `b` | `a.union(b)` | in either |
| intersection | `a & b` | `a.intersection(b)` | in both |
| difference | `a - b` | `a.difference(b)` | in `a` but not `b` |
| symmetric difference | `a ^ b` | `a.symmetric_difference(b)` | in exactly one |
| subset | `a <= b` | `a.issubset(b)` | every item of `a` is in `b` |
| superset | `a >= b` | `a.issuperset(b)` | every item of `b` is in `a` |
| disjoint | none | `a.isdisjoint(b)` | no items in common |

```python
python_club = {"Asha", "Ravi", "Meena", "Kiran"}
chess_club = {"Ravi", "Kiran", "John"}
print(sorted(python_club | chess_club))
print(sorted(python_club & chess_club))
print(sorted(python_club - chess_club))
print(sorted(python_club ^ chess_club))
print({"Ravi"} <= chess_club, python_club.isdisjoint({"Zoe"}))
print({1, 2} < {1, 2}, {1, 2} <= {1, 2})
```

Output:

```text
['Asha', 'John', 'Kiran', 'Meena', 'Ravi']
['Kiran', 'Ravi']
['Asha', 'Meena']
['Asha', 'John', 'Meena']
True True
False True
```

The operators need both sides to be sets. The methods accept any iterable, so `s.union([1, 2])` works but `s | [1, 2]` does not. In-place versions exist too: `a |= b`, `a &= b`, `a -= b`, `a ^= b`.

`<` is a **proper** subset: a subset that is not equal. That is why `{1, 2} < {1, 2}` is `False`.

### Removing duplicates

`set(items)` removes duplicates in one O(n) step, but the order is lost. To keep the **first-seen order**, use `dict.fromkeys`, since dict keys are unique and keep insertion order. Or use a set to remember what you have seen, with a list for the result.

```python
names = ["Ravi", "Asha", "Ravi", "Meena", "Asha"]
print(len(set(names)))
print(list(dict.fromkeys(names)))
seen = set()
unique = []
for n in names:
    if n not in seen:
        seen.add(n)
        unique.append(n)
print(unique)
```

Output:

```text
3
['Ravi', 'Asha', 'Meena']
['Ravi', 'Asha', 'Meena']
```

Both order-keeping versions are O(n). The version that checks `if n not in unique` on the **list** gives the same answer but is O(n²), because each `in` scans the list.

### frozenset

A **frozenset** is an immutable set. It supports all the reading operations and the algebra, but not `add` or `remove`. Because it cannot change, it is hashable, so it can be a dict key or live inside another set. Use it when order does not matter in a key, such as "the pair Asha and Ravi" being the same as "the pair Ravi and Asha".

```python
pair1 = frozenset(["Asha", "Ravi"])
pair2 = frozenset(["Ravi", "Asha"])
meetings = {pair1: 1}
meetings[pair2] = meetings.get(pair2, 0) + 1
print(len(meetings), meetings[pair1])
groups = {frozenset({1, 2}), frozenset({2, 1}), frozenset({3})}
print(len(groups))
```

Output:

```text
1 2
2
```

### Under the hood

A set is a hash table of keys with no values, so `add`, `remove`, `discard` and `in` are O(1) on average. Union and intersection must visit items: `a | b` is O(len(a) + len(b)), and `a & b` loops over the **smaller** set and checks membership in the larger one, so it is O(min(len(a), len(b))).

### Common misconceptions

- "`{}` is an empty set." It is an empty dict. Use `set()`.
- "Sets keep the order I added things." They do not. Sort before showing them.
- "A set can hold lists." Set members must be hashable. Use tuples or frozensets.

---

## 16. Comprehensions

A **comprehension** builds a collection from another iterable in one expression. It replaces a common loop shape:

```python
squares = []
for x in range(6):
    squares.append(x * x)
print(squares)
print([x * x for x in range(6)])
```

Output:

```text
[0, 1, 4, 9, 16, 25]
[0, 1, 4, 9, 16, 25]
```

Read the comprehension as English: "the list of `x * x`, for each `x` in `range(6)`". The expression comes first, then the `for` clause.

### Filtering with if

An `if` at the **end** keeps only the items for which the condition is true.

```python
nums = [5, -2, 8, 0, -7, 3]
print([n for n in nums if n > 0])
print([n * 10 for n in nums if n % 2 == 0])
words = ["Apple", "bat", "Cat", "dog"]
print([w.lower() for w in words if w[0].isupper()])
```

Output:

```text
[5, 8, 3]
[-20, 80, 0]
['apple', 'cat']
```

### Choosing a value with if-else

A conditional expression `a if condition else b` in the **expression part** chooses a value for **every** item. Nothing is filtered out.

```python
nums = [5, -2, 8, 0, -7]
print(["pos" if n > 0 else "not pos" for n in nums])
print([n if n >= 0 else 0 for n in nums])
```

Output:

```text
['pos', 'not pos', 'pos', 'not pos', 'not pos']
[5, 0, 8, 0, 0]
```

The position tells you which one it is:

- `[x for x in data if cond]`: `if` at the end, **filters**. No `else` allowed.
- `[a if cond else b for x in data]`: `if-else` at the front, **transforms**. The `else` is required.

### Dict and set comprehensions

Curly brackets with a `key: value` expression make a dict. Curly brackets with a single expression make a set.

```python
words = ["apple", "kiwi", "banana", "fig"]
lengths = {w: len(w) for w in words}
print(lengths)
first_letters = {w[0] for w in "the quick brown fox the".split()}
print(sorted(first_letters))
prices = {"pen": 10, "ink": 45, "pad": 30}
print({k: v for k, v in prices.items() if v >= 30})
print({v: k for k, v in prices.items()})
```

Output:

```text
{'apple': 5, 'kiwi': 4, 'banana': 6, 'fig': 3}
['b', 'f', 'q', 't']
{'ink': 45, 'pad': 30}
{10: 'pen', 45: 'ink', 30: 'pad'}
```

The last one inverts a dict. If two keys had the same value, the later one would win, because a dict keeps only one entry per key.

Round brackets do **not** make a "tuple comprehension". `(x * x for x in data)` is a *generator expression*, a lazy sequence covered in core.12. If you want a tuple, write `tuple(x * x for x in data)`. You have already used generator expressions without knowing it, inside calls like `sum(x * x for x in data)`.

### Nested comprehensions and reading order

A comprehension can have several `for` clauses. They run in the **same order as nested loops written top to bottom**. The leftmost `for` is the outer loop.

```python
pairs = [(r, c) for r in range(2) for c in range(3)]
print(pairs)
same = []
for r in range(2):
    for c in range(3):
        same.append((r, c))
print(same == pairs)
```

Output:

```text
[(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (1, 2)]
True
```

So to flatten a list of lists, the outer loop picks a row and the inner loop picks a value from that row:

```python
grid = [[1, 2, 3], [4, 5, 6]]
flat = [v for row in grid for v in row]
print(flat)
```

Output:

```text
[1, 2, 3, 4, 5, 6]
```

The trick for reading it: cover the expression at the front, and read the `for` clauses as if they were indented loops.

A comprehension **inside** the expression of another builds nested lists. Here the **inner** comprehension is the one that runs first for each outer item:

```python
table = [[r * c for c in range(1, 4)] for r in range(1, 4)]
print(table)
grid = [[1, 2, 3], [4, 5, 6]]
transposed = [[row[i] for row in grid] for i in range(3)]
print(transposed)
```

Output:

```text
[[1, 2, 3], [2, 4, 6], [3, 6, 9]]
[[1, 4], [2, 5], [3, 6]]
```

Compare the two shapes:

- `[v for row in grid for v in row]`: two `for` clauses, **one** flat list.
- `[[... for ...] for ...]`: a comprehension inside a comprehension, a **list of lists**.

### Under the hood

- A comprehension runs in its own small scope. Its loop variable does not leak: after `[x for x in range(3)]`, the name `x` from the comprehension is not visible outside. (A plain `for` loop variable does stay defined after the loop.)
- A list comprehension is usually a little faster than the same `append` loop, because it avoids looking up `.append` on every turn.

### When not to use one

Use a comprehension to **build** a collection, not to run something for its side effect: `[print(x) for x in data]` builds a useless list of `None`s. If it needs several conditions and loops, a plain loop reads better.

### Predict the output

```python
data = [1, 2, 3, 4]
print([x * y for x in data if x % 2 for y in data if y > x])
print({x % 3 for x in data})
print({x: x % 2 == 0 for x in data})
```

<details><summary>Answer</summary>

```text
[2, 3, 4, 12]
{0, 1, 2}
{1: False, 2: True, 3: False, 4: True}
```

Reading the first as nested loops: for each odd `x` (1 and 3), for each `y` greater than `x`. That gives `1*2, 1*3, 1*4, 3*4`. The set comprehension collects remainders, and duplicates disappear. The dict maps each number to whether it is even.

</details>

### Common misconceptions

- "`[x for x in a if c else d]` is valid." No. An `else` belongs only in the expression at the front.
- "In `[v for row in grid for v in row]`, the `for v` loop is the outer one." The leftmost `for` is the outer loop.
- "`(x for x in a)` is a tuple." It is a generator.

---

## 17. Sorting

### sort versus sorted

There are two ways to sort:

- `a.sort()` is a **list method**. It sorts the list **in place** and returns `None`.
- `sorted(iterable)` is a **built-in function**. It accepts any iterable, builds a **new** list, and leaves the original alone.

```python
a = [3, 1, 2]
b = sorted(a)
print(a, b)
a.sort()
print(a)
print(sorted("banana"))
print(sorted({"b": 1, "a": 2}))
print(sorted((3, 1, 2), reverse=True))
```

Output:

```text
[3, 1, 2] [1, 2, 3]
[1, 2, 3]
['a', 'a', 'a', 'b', 'n', 'n']
['a', 'b']
[3, 2, 1]
```

`sorted` works on strings, tuples, dicts (giving sorted keys) and sets, and always returns a list. Both accept `reverse=True` for descending order.

Python can only sort values it can compare with `<`. Mixing numbers and strings fails:

```python
print(sorted([3, "a", 1]))
```

Output:

```text
Traceback (most recent call last):
  File "example.py", line 1, in <module>
    print(sorted([3, "a", 1]))
          ~~~~~~^^^^^^^^^^^^^
TypeError: '<' not supported between instances of 'str' and 'int'
```

### How strings sort

Strings compare by character codes, so all uppercase letters come before all lowercase letters, and `"10"` comes before `"9"` because `"1"` comes before `"9"`.

```python
print(sorted(["banana", "Apple", "cherry"]))
print(sorted(["10", "9", "100"]))
```

Output:

```text
['Apple', 'banana', 'cherry']
['10', '100', '9']
```

### The key argument

`key=` takes a **function**. Python calls it once on each item and sorts by the results, instead of by the items themselves. The items themselves are not changed. You can pass any function that takes one argument, including built-ins and methods:

```python
words = ["banana", "Apple", "fig", "cherry"]
print(sorted(words, key=str.lower))
print(sorted(words, key=len))
print(sorted(["10", "9", "100"], key=int))
print(sorted([-5, 3, -1, 4], key=abs))
```

Output:

```text
['Apple', 'banana', 'cherry', 'fig']
['fig', 'Apple', 'banana', 'cherry']
['9', '10', '100']
[-1, 3, 4, -5]
```

Notice: we wrote `key=len`, **not** `key=len()`. We hand Python the function itself, and Python calls it for us. `str.lower` is the `lower` method taken from the `str` type, so `str.lower("Apple")` gives `"apple"`.

A neat built-in key is a dict's `get` method. `sorted(d, key=d.get)` sorts the **keys** by their **values**:

```python
marks = {"Asha": 82, "Ravi": 75, "Meena": 91}
print(sorted(marks, key=marks.get))
print(max(marks, key=marks.get))
```

Output:

```text
['Ravi', 'Asha', 'Meena']
Meena
```

`min` and `max` accept `key` too.

### Stability

Python's sort is **stable**: when two items have equal keys, they keep their original relative order. In `sorted(words, key=len)` above, `"banana"` and `"cherry"` both have length 6, and `"banana"` stays before `"cherry"` because it came first in the input.

Stability is what makes **multi-key sorting by sorting twice** work. To sort by department, and within a department by name: sort by the **secondary** key first, then by the **primary** key. The second sort keeps the name order inside each department.

```python
staff = [("Ravi", "IT"), ("Asha", "HR"), ("Meena", "IT"), ("John", "HR")]
by_name = sorted(staff)
by_dept = sorted(by_name, key=lambda person: person[1])
print(by_dept)
```

Output:

```text
[('Asha', 'HR'), ('John', 'HR'), ('Meena', 'IT'), ('Ravi', 'IT')]
```

That `lambda` is a preview of core.06. `lambda person: person[1]` is a tiny unnamed function that takes one item and returns its second part. You will learn it properly soon. Until then, there is another way that needs no new syntax.

### Tuple keys: decorate, sort, undecorate

Tuples compare item by item, left to right. So if you build tuples with the **most important** key first, a plain sort orders by that key, and breaks ties with the next one. For a key that should go **descending**, use its negative (for numbers).

```python
scores = {"Asha": 82, "Ravi": 91, "Meena": 82, "John": 75}
ranked = sorted((-score, name) for name, score in scores.items())
print(ranked)
for neg, name in ranked:
    print(name, -neg)
```

Output:

```text
[(-91, 'Ravi'), (-82, 'Asha'), (-82, 'Meena'), (-75, 'John')]
Ravi 91
Asha 82
Meena 82
John 75
```

This sorts by score, high to low, and alphabetically among equal scores. The pattern has a name: **decorate** each item with its sort key, **sort**, then **undecorate** by taking the parts you need. It works with no `key` function at all.

### Under the hood

Python's sort is **Timsort**, a merge sort that takes advantage of already-sorted runs in the data. It is O(n log n) in general and close to O(n) on nearly sorted data. The `key` function is called once per item, not once per comparison.

### Predict the output

```python
words = ["bb", "a", "ccc", "dd", "e"]
print(sorted(words, key=len))
print(sorted(words, key=len, reverse=True))
words.sort()
print(words.sort())
print(sorted(words)[::-1] == sorted(words, reverse=True))
```

<details><summary>Answer</summary>

```text
['a', 'e', 'bb', 'dd', 'ccc']
['ccc', 'bb', 'dd', 'a', 'e']
None
True
```

Equal lengths keep input order: `"bb"` before `"dd"` and `"a"` before `"e"`. With `reverse=True`, Python still keeps equal items in their original order (it does not just reverse the stable result), so `"bb"` stays before `"dd"`. `words.sort()` returns `None`. The last comparison is `True` here because no two words are equal.

</details>

### Common misconceptions

- "`key=len()`". Pass the function, do not call it.
- "`reverse=True` is the same as reversing the result." Not quite: equal items keep their original order with `reverse=True`.
- "`sorted(d)` sorts the dict." It returns a sorted list of keys. The dict is unchanged.

---

## 18. Big-O of collection operations and choosing a structure

Here are the costs of common operations, for collections of n items. "Average" assumes a good hash spread, which is what you get in practice.

| Operation | list | tuple | dict | set |
|---|---|---|---|---|
| `len(x)` | O(1) | O(1) | O(1) | O(1) |
| index `x[i]` | O(1) | O(1) | not available | not available |
| lookup by key `d[k]` | not available | not available | O(1) average | not available |
| `item in x` | O(n) | O(n) | O(1) average (keys) | O(1) average |
| add at end: `append` | O(1) amortised | not allowed | O(1) average | O(1) average (`add`) |
| `pop()` from end | O(1) | not allowed | `popitem()` O(1) | O(1) |
| `insert(0, x)`, `pop(0)` | O(n) | not allowed | not available | not available |
| remove by value | O(n) | not allowed | `del d[k]` O(1) average | O(1) average |
| slice `x[a:b]` | O(b - a) | O(b - a) | not available | not available |
| copy | O(n) | O(n) | O(n) | O(n) |
| sort | O(n log n) | sorted() O(n log n) | sorted() O(n log n) | sorted() O(n log n) |
| loop over all items | O(n) | O(n) | O(n) | O(n) |

Two lines in that table cause most slow programs:

1. `item in a_list` inside a loop. Each test is O(n), so the loop is O(n²). Switch to a set or a dict.
2. `insert(0, ...)` or `pop(0)` on a long list inside a loop. Again O(n²). Append at the end and reverse once, or use `collections.deque` (core.17).

### Choosing a structure

Ask what questions your program will ask most.

| You need to... | Use |
|---|---|
| keep items in order, add at the end, access by position | list |
| store a fixed record, or use a compound key | tuple (or namedtuple) |
| look up a value by a name or id | dict |
| count things or group things | dict (counts or lists as values) |
| test membership quickly, remove duplicates | set |
| compare two groups: common, missing, extra | set algebra |
| use a group of items as a key where order does not matter | frozenset |

Some examples, with reasons:

- **A contact book.** You look people up by name: a dict from name to phone. To list contacts alphabetically, sort the keys when printing.
- **"Have I seen this username before?"** across 100,000 sign-ups: a set. A list would make each check scan everything.
- **The moves of a game, in order, with undo.** A list used as a stack: `append` to do, `pop()` to undo. Both O(1).
- **A chessboard.** Either an 8 by 8 list of lists, or a dict from `(row, col)` tuples to pieces. The dict is better when most squares are empty, because it stores only the occupied ones.
- **Students who took both exams.** A set intersection.

### Space matters too

A set or dict uses more memory than a list of the same items, because its hash table keeps empty slots to stay fast. On this machine, `sys.getsizeof` reports about 8 KB for a list of 1,000 ints, 33 KB for a set of them and 37 KB for a dict. Choose a hash-based structure when you need fast lookups, not by habit.

### Common misconceptions

- "O(1) is always faster than O(n)." For tiny n, a list scan can beat building a set. Big-O tells you about growth, not about small cases.
- "Lists are slow." Lists are the fastest structure for what they are good at: ordered data accessed by position or at the end.

---

## Summary

- **Lists** are ordered, mutable arrays of references. Indexing and `append` are O(1) (append amortised); `insert(0)`, `pop(0)` and `in` are O(n). Methods that change a list return `None`. `a + b` makes a new list; `a += b` changes `a` in place.
- Slices make new lists and never raise `IndexError`. Slice assignment can grow or shrink a list; `del a[i:j]` deletes a stretch.
- **Assignment never copies.** `copy()`, `list()`, `[:]` and `copy.copy` are shallow (inner objects shared); `copy.deepcopy` copies every mutable level. `[[0] * 3] * 3` repeats one row; build grids with a comprehension.
- Never add or remove items while looping over the same list or dict.
- **Tuples** are immutable; the comma makes them; `(5,)` has one item. Unpacking, `*rest` (a list) and `a, b = b, a`. **namedtuple** names the positions.
- **Dicts** map unique hashable keys to values with O(1) average lookup, in insertion order. Use `get`, `setdefault`, `pop`, `update` and the pipe operator (right side wins). Views are live.
- **Hashable** means a hash that never changes and agrees with `==`. Lists, dicts and sets are not hashable; tuples are if their items are.
- **Sets** give O(1) average membership and set algebra; `set()` is empty; `frozenset` is hashable. `dict.fromkeys` removes duplicates keeping order.
- **Comprehensions**: an `if` at the end filters; `a if c else b` at the front transforms; `for` clauses read left to right as outer to inner.
- **Sorting**: `sort()` in place returns `None`; `sorted()` returns a new list. `key=` takes a function; the sort is stable, so sort twice or sort tuples like `(-score, name)`.
- Choose a structure by the operations you need most and their cost.

## Learning outcomes

After this chapter you should be able to:

- [ ] Use every common list method, slicing, slice assignment and `del`, knowing which methods return `None`.
- [ ] Draw how a list stores references, and explain amortised O(1) append and O(n) `insert(0)` and `in`.
- [ ] Tell an alias from a shallow copy from a deep copy, and predict what a change through each affects.
- [ ] Explain and fix the `[[0] * 3] * 3` bug with a memory diagram.
- [ ] Use tuples, one-item tuples, packing, star unpacking, swapping and namedtuple.
- [ ] Use dicts for lookup, counting and grouping, and explain that their views are live.
- [ ] Explain why a list cannot be a dict key but a tuple of ints can.
- [ ] Use sets, frozensets and set algebra, and remove duplicates with or without keeping order.
- [ ] Write and read list, dict, set and nested comprehensions.
- [ ] Sort with `key`, `reverse`, stability and tuple keys.
- [ ] Pick the right collection for a task and justify it by its operations' cost.

## Module project

The project for this module is an **in-memory contact book and inventory manager** driven by typed commands. A contact book maps names to phone numbers (a dict), supports adding, updating, deleting and searching, and lists contacts in sorted order. An inventory manager tracks quantities per item, refuses to sell more than is in stock, and reports low-stock items sorted by quantity and name. Both read commands one line at a time with `input()` until a `quit` command, use `split()` to break each command into parts, and use `match`/`case` or `if`/`elif` to choose what to do. Be ready to explain why you chose each collection and what each command costs. Problem p059 in this module is the assessed version of the contact book.

## Further reading

All links are to the official Python documentation.

- Data structures tutorial (lists, tuples, sets, dicts, comprehensions): https://docs.python.org/3/tutorial/datastructures.html
- Sequence types (list, tuple, range): https://docs.python.org/3/library/stdtypes.html#sequence-types-list-tuple-range
- Mutable sequence operations: https://docs.python.org/3/library/stdtypes.html#mutable-sequence-types
- Mapping types (dict) and view objects: https://docs.python.org/3/library/stdtypes.html#mapping-types-dict
- Set types (set, frozenset): https://docs.python.org/3/library/stdtypes.html#set-types-set-frozenset
- The copy module (shallow and deep copy): https://docs.python.org/3/library/copy.html
- collections.namedtuple: https://docs.python.org/3/library/collections.html#collections.namedtuple
- Sorting techniques: https://docs.python.org/3/howto/sorting.html
- hash(): https://docs.python.org/3/library/functions.html#hash
- Glossary entry for "hashable": https://docs.python.org/3/glossary.html#term-hashable
- Programming FAQ, "Why did changing list y also change list x?": https://docs.python.org/3/faq/programming.html#why-did-changing-list-y-also-change-list-x
- Programming FAQ, "How do I create a multidimensional list?": https://docs.python.org/3/faq/programming.html#how-do-i-create-a-multidimensional-list
- Design FAQ, "Why must dictionary keys be immutable?": https://docs.python.org/3/faq/design.html#why-must-dictionary-keys-be-immutable
