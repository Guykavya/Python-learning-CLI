# Chapter 10: Iterators and generators

You have written hundreds of `for` loops by now. You loop over lists, strings, dicts, `range(...)`, `enumerate(...)` and `zip(...)`, and it all just works. This chapter opens the box and shows you **how** it works. That sounds like a small thing, but it changes the way you write programs.

Here is the problem that makes it matter. Suppose a web server writes one line to a log for every request. A busy server writes millions of lines a day. You want to answer one question: "how many requests failed today?" The obvious way is:

1. read all the lines into a list,
2. loop over the list and count the failures.

Step 1 needs memory for **every line at once**. If the log is 20 GB and your laptop has 8 GB of RAM, the program dies before it counts anything. But think about step 2 for a moment: to count, you only ever look at **one line at a time**. You never need line 1 and line 900,000 together. So why hold them all?

Python's answer is the **iterator**: an object that hands you items one by one, on request, and forgets them when you move on. And the easiest way to make your own iterators is a **generator**: a function that uses `yield` instead of `return` and can pause in the middle. With these two tools you can process data much larger than your memory, and you can build programs as **pipelines** of small steps (clean the lines, parse them, filter them, count them) where each item flows through all steps before the next item is even read.

So this chapter, like the others, has two halves:

1. **The mechanics**: `iter()`, `next()`, `StopIteration`, iterables and iterators, generator functions, `yield`, generator expressions, `yield from`, `send`/`throw`/`close`, and the `itertools` module.
2. **The judgement**: when laziness helps and when a plain list is better, why an iterator can be used only once, and the traps that come from that.

Along the way you will answer these questions:

- What does a `for` loop really do, step by step?
- What is the difference between an **iterable** (like a list) and an **iterator** (like what `iter(list)` gives you)?
- Why does the second loop over `map(...)` or over a generator print nothing at all?
- What happens inside a function when it reaches `yield`, and when does its code actually run?
- Why is `(x * x for x in data)` tiny in memory while `[x * x for x in data]` is huge?
- How do you build a data pipeline from small generators, and why is it better than one big loop?
- What do `chain`, `islice`, `groupby`, `product`, `combinations`, `accumulate`, `pairwise`, `tee` and their friends do, and when should you reach for each?
- Why must you sort before `groupby`, and why do its groups suddenly become empty?

A note on how examples are shown. Every block of code is followed by the exact output produced by really running it with **Python 3.14**. Tracebacks show the folder path as `/home/you/project`. Some outputs contain a **memory address**, like `<generator object countdown at 0x71daf8d46bc0>`. The hex number after `at` is different on your machine and on every run; only the words before it matter. Sizes from `sys.getsizeof` are from a 64-bit computer and may differ by a few bytes on yours. Answer every "Predict the output" question on paper before you open the answer.

What this chapter leaves out on purpose: real files (`open`, `with`) come in core.12, so our "files" here are lists of strings. Classes come in core.14. We need a tiny class in section 4 to show the machinery, but you will not be asked to write classes. Asynchronous generators (`async`) come much later.

## Table of contents

1. [Why iteration matters: the memory story](#1-why-iteration-matters-the-memory-story)
2. [What a `for` loop really does](#2-what-a-for-loop-really-does)
3. [Iterable vs iterator, and "consumed once"](#3-iterable-vs-iterator-and-consumed-once)
4. [Peek under the hood: the protocol in a class](#4-peek-under-the-hood-the-protocol-in-a-class)
5. [Generator functions and `yield`](#5-generator-functions-and-yield)
6. [Generator expressions and lazy evaluation](#6-generator-expressions-and-lazy-evaluation)
7. [Infinite sequences](#7-infinite-sequences)
8. [Pipelines: chaining generators](#8-pipelines-chaining-generators)
9. [`yield from`: handing over to another iterable](#9-yield-from-handing-over-to-another-iterable)
10. [`send`, `throw` and `close`](#10-send-throw-and-close)
11. [itertools 1: infinite iterators](#11-itertools-1-infinite-iterators)
12. [itertools 2: slicing, joining and stopping](#12-itertools-2-slicing-joining-and-stopping)
13. [itertools 3: running totals, pairs and batches](#13-itertools-3-running-totals-pairs-and-batches)
14. [`groupby` in depth](#14-groupby-in-depth)
15. [itertools 4: combinatorics](#15-itertools-4-combinatorics)
16. [`tee`, and sharing one iterator](#16-tee-and-sharing-one-iterator)
17. [Useful patterns](#17-useful-patterns)
18. [Project: a lazy log-file pipeline](#18-project-a-lazy-log-file-pipeline)
19. [Common traps](#19-common-traps)
20. [Summary](#20-summary)

## 1. Why iteration matters: the memory story

### 1.1 Two ways to add up a million squares

Here are two ways to compute the sum of the squares of the numbers from 0 to 999,999. The only difference is the brackets.

```python
import sys

squares_list = [n * n for n in range(1_000_000)]
squares_lazy = (n * n for n in range(1_000_000))

print("list:", sys.getsizeof(squares_list), "bytes")
print("lazy:", sys.getsizeof(squares_lazy), "bytes")
print(sum(squares_list) == sum(squares_lazy))
```

`sys.getsizeof(x)` tells you how many bytes the object `x` itself takes in memory. (`sys` is a standard module, just like `math`; `import sys` is all you need.)

```text
$ python mem1.py
list: 8448728 bytes
lazy: 208 bytes
True
```

Both give the same sum. But the list holds a million numbers at once: over 8 MB just for the list's slots, and the number objects themselves come on top of that. The version with round brackets is a **generator expression**. It holds **no numbers at all**. It holds only a recipe ("take the next `n` from the range, square it") and a bookmark ("where am I in the range?"). That costs 208 bytes, and it would still cost 208 bytes for a billion numbers.

### 1.2 Eager and lazy

These two words appear in the whole chapter, so let us fix them now.

- **Eager**: do all the work now, keep all the results. A list comprehension is eager: the moment the line runs, all one million squares are computed and stored.
- **Lazy**: do the work only when somebody asks for the next result, and do not keep old results. A generator expression is lazy: it computes square number 7 only when `sum` asks for it, and then forgets it.

Think of a restaurant. An eager kitchen cooks all 200 dishes on the menu in the morning and puts them on tables, "just in case". A lazy kitchen cooks a dish when a customer orders it. The lazy kitchen needs one stove and one plate at a time, not 200 tables.

### 1.3 A measurement on a "big log"

Let us make a fake log of two million lines and count the error lines, once eagerly and once lazily. The details of the lazy version (`yield`) come in section 5; for now just look at the result.

```python
# lazy version
def fake_big_log(n):
    for i in range(n):
        level = "ERROR" if i % 1000 == 0 else "INFO"
        yield f"line {i} {level} something happened"


errors = sum(1 for line in fake_big_log(2_000_000) if " ERROR " in line)
print("errors:", errors)
```

```python
# eager version
def fake_big_log_list(n):
    lines = []
    for i in range(n):
        level = "ERROR" if i % 1000 == 0 else "INFO"
        lines.append(f"line {i} {level} something happened")
    return lines


errors = len([line for line in fake_big_log_list(2_000_000) if " ERROR " in line])
print("errors:", errors)
```

Both print `errors: 2000`. The peak memory used by the whole Python process, measured on Linux with `/usr/bin/time -f "%M KB"`, was (your numbers will differ, the ratio is what matters):

```text
lazy  version: max memory 9328 KB     (about 9 MB)
eager version: max memory 181660 KB   (about 180 MB)
```

The lazy version used about the same memory as an empty Python program. Make the log 100 times bigger and the eager version needs 18 GB and crashes on most laptops. The lazy version still needs about 9 MB. **That is the first outcome of this module: process data larger than memory, by never holding all of it at once.**

### 1.4 What you need to learn to do this

To write the lazy version yourself you need to understand:

1. the **iteration protocol**: the small agreement (`iter`, `next`, `StopIteration`) that every `for` loop uses (sections 2 to 4);
2. **generators**: the easy way to write your own lazy sources and steps (sections 5 to 10);
3. **itertools**: a box of ready-made lazy tools, so you do not write the common ones by hand (sections 11 to 16).

## 2. What a `for` loop really does

### 2.1 `iter()` and `next()`

Two built-in functions do all the work behind a `for` loop:

- `iter(x)` asks the object `x`: "give me something that can hand out your items one by one". That something is called an **iterator**.
- `next(it)` asks the iterator `it`: "give me the next item".

Let us call them by hand on a list.

```python
colours = ["red", "green", "blue"]
it = iter(colours)
print(it)
print(next(it))
print(next(it))
print(next(it))
print(next(it))
```

```text
$ python iter1.py
<list_iterator object at 0x769f2758c610>
red
green
blue
Traceback (most recent call last):
  File "/home/you/project/iter1.py", line 7, in <module>
    print(next(it))
          ~~~~^^^^
StopIteration
```

(The address `0x769f...` is different on your machine.)

Read it line by line:

- `iter(colours)` returned a `list_iterator`. It is a separate, small object. It does not copy the list. It keeps a reference to the list and a **position**, starting at 0.
- Each `next(it)` returns the item at the current position and moves the position forward by one.
- After `"blue"` there is nothing left. The fourth `next(it)` does not return `None` and does not return an empty string. It **raises an exception** called `StopIteration`. That is the iterator's way of saying "I am finished".

Why an exception, and not a special value like `None`? Because `None` could be a real item. A list like `[1, None, 3]` must be able to hand out `None` without the loop stopping early. An exception is a signal that can never be confused with an item.

### 2.2 The `for` loop, rewritten by hand

Now you can see what this loop does:

```python
for colour in colours:
    print(colour.upper())
```

Python runs it almost exactly like this:

```python
colours = ["red", "green", "blue"]

it = iter(colours)
while True:
    try:
        colour = next(it)
    except StopIteration:
        break
    print(colour.upper())
```

```text
$ python iter2.py
RED
GREEN
BLUE
```

So a `for` loop is three steps:

1. call `iter()` **once**, on the thing after `in`;
2. call `next()` again and again, putting each item into the loop variable and running the body;
3. when `next()` raises `StopIteration`, catch it quietly and leave the loop.

You never see `StopIteration` in a normal `for` loop because the loop catches it for you. This is the whole **iteration protocol**. Everything else in this chapter is built on these three steps.

### 2.3 Everything you loop over has an iterator

Every kind of collection gives its own kind of iterator:

```python
print(type(iter([1, 2])))
print(type(iter("hi")))
print(type(iter({"a": 1})))
print(type(iter({1, 2})))
print(type(iter((1, 2))))
print(type(iter(range(3))))
```

```text
$ python iter3.py
<class 'list_iterator'>
<class 'str_ascii_iterator'>
<class 'dict_keyiterator'>
<class 'set_iterator'>
<class 'tuple_iterator'>
<class 'range_iterator'>
```

Notice `dict_keyiterator`: looping over a dict gives its **keys**. That is why `for name in marks:` gives names, and you need `.items()` to get pairs.

If an object has no way to give an iterator, `iter()` fails. This is the error you get from `for x in 5:`:

```python
print(iter(5))
```

```text
$ python iter4.py
Traceback (most recent call last):
  File "/home/you/project/iter4.py", line 1, in <module>
    print(iter(5))
          ~~~~^^^
TypeError: 'int' object is not iterable
```

You have probably seen `'int' object is not iterable` before. Now you know exactly what it means: "I tried `iter()` on an int, and ints cannot give an iterator".

### 2.4 `next()` with a default

`next(it, default)` returns `default` instead of raising `StopIteration` when the iterator is finished. This is very handy when you want "the next item, or some fallback".

```python
word = "hey"
it = iter(word)
print(next(it, "done"))
print(next(it, "done"))
print(next(it, "done"))
print(next(it, "done"))
print(next(it, "done"))
```

```text
$ python iter5.py
h
e
y
done
done
```

Notice that a finished iterator **stays** finished. Asking again just gives the default again.

### 2.5 Try it: the loop by hand

Without running it, rewrite this loop as a `while True` loop with `iter`, `next` and `try/except StopIteration`:

```python
total = 0
for n in [4, 7, 1]:
    total += n
print(total)
```

<details><summary>Answer</summary>

```python
total = 0
it = iter([4, 7, 1])
while True:
    try:
        n = next(it)
    except StopIteration:
        break
    total += n
print(total)
```

It prints `12`. The `iter()` call happens once, before the loop. Only the `next(it)` call is inside the `try`: if you put `total += n` inside the `try` too, a real error in the body would be mixed up with the end-of-loop signal.

</details>

## 3. Iterable vs iterator, and "consumed once"

### 3.1 Two words, two jobs

These two words look alike, and many people mix them up. They are different jobs.

- An **iterable** is anything you can loop over: anything that `iter()` accepts. Lists, strings, tuples, dicts, sets, ranges are iterables. An iterable is like a **book**.
- An **iterator** is the object that actually walks through the items: it has a **position**, and `next()` moves it forward. An iterator is like a **bookmark** in that book.

A book can have many bookmarks at once, each at a different page. Moving one bookmark does not move the others. And a bookmark can only move forward: there is no "go back" for an iterator.

Every iterator is also an iterable: `iter()` on an iterator gives back **the same iterator** (the bookmark itself). Look:

```python
numbers = [1, 2, 3]
it = iter(numbers)

print(iter(numbers) is numbers)
print(iter(it) is it)
print(iter(numbers) is iter(numbers))
```

```text
$ python once5.py
False
True
False
```

- `iter(numbers) is numbers` is `False`: a list is not its own iterator; it makes a **new** bookmark each time.
- `iter(it) is it` is `True`: an iterator returns **itself**.
- `iter(numbers) is iter(numbers)` is `False`: two calls, two separate bookmarks.

That gives a quick test you can use any time: **if `iter(x) is x`, then `x` is an iterator** (one-use, has a position). If not, `x` is an iterable that makes fresh iterators.

### 3.2 Consumed once

Here is the consequence that surprises almost everyone. Loop twice over a list, then twice over an iterator:

```python
numbers = [1, 2, 3]

print("list, loop 1:", [n for n in numbers])
print("list, loop 2:", [n for n in numbers])

it = iter(numbers)
print("iterator, loop 1:", [n for n in it])
print("iterator, loop 2:", [n for n in it])
```

```text
$ python once1.py
list, loop 1: [1, 2, 3]
list, loop 2: [1, 2, 3]
iterator, loop 1: [1, 2, 3]
iterator, loop 2: []
```

Now use what you know about the `for` loop to explain it:

- For the list, each loop calls `iter(numbers)`, which makes a **new** bookmark at page 0. Both loops see everything.
- For the iterator, each loop calls `iter(it)`, which returns **the same** bookmark. The first loop moved it to the end. The second loop starts at the end, gets `StopIteration` at once, and runs zero times. No error, just nothing.

This is what "an iterator can be consumed only once" means, and it is the second outcome of this module. **An iterator is a position, not a collection.** Once the position is at the end, there is nothing to rewind. To go through the data again you need a new iterator from the original iterable (or you need to have saved the items in a list).

### 3.3 Many built-ins return iterators

`map`, `filter`, `zip`, `enumerate` and `reversed` all return **iterators**, not lists. So they are consumed once too.

```python
names = ["asha", "ravi", "meena"]
upper = map(str.upper, names)

print(list(upper))
print(list(upper))
```

```text
$ python once2.py
['ASHA', 'RAVI', 'MEENA']
[]
```

Here is the same bug, in a form you could easily write:

```python
scores = [40, 75, 90, 30, 85]
passed = filter(lambda s: s >= 50, scores)

print("count:", len(list(passed)))
for s in passed:
    print("passed:", s)
print("loop finished")
```

```text
$ python once3.py
count: 3
loop finished
```

The count is right, but not one score is printed. `list(passed)` used up the filter iterator to count it. The loop got an empty iterator. There is no error message to warn you. The fix is to make a list **once** and use the list twice:

```python
passed = [s for s in scores if s >= 50]   # a list: can be used many times
```

Compare with `range`, which is **not** an iterator. It is a lazy *sequence*: it computes its numbers from `start`, `stop` and `step`, so it can make as many fresh iterators as you like, and it supports `len`, indexing and `in`:

```python
r = range(3)
print(list(r), list(r))
print(len(r), r[1], 2 in r)

z = zip("ab", [1, 2])
print(list(z), list(z))

e = enumerate("ab")
print(next(e))
print(list(e))
```

```text
$ python once6.py
[0, 1, 2] [0, 1, 2]
3 1 True
[('a', 1), ('b', 2)] []
(0, 'a')
[(1, 'b')]
```

The `zip` object was empty the second time. The `enumerate` object, after one `next`, had only one pair left.

### 3.4 Even `in` consumes

The `in` operator on an iterator has to walk forward to find the item. It stops when it finds it, and everything it walked past is gone.

```python
it = iter([10, 20, 30, 40])
print(20 in it)
print(list(it))
```

```text
$ python once4.py
True
[30, 40]
```

`10` and `20` were used up by the search. Only `30` and `40` are left.

### 3.5 Iterators have no length

An iterator does not know how many items are left. It only knows how to get the next one. So `len()` does not work:

```python
it = iter([1, 2, 3])
print(len(it))
```

```text
$ python once7.py
Traceback (most recent call last):
  File "/home/you/project/once7.py", line 2, in <module>
    print(len(it))
          ~~~^^^^
TypeError: object of type 'list_iterator' has no len()
```

Indexing (`it[0]`) and slicing (`it[1:3]`) fail too. If you need those, make a list. (For slicing an iterator lazily, `itertools.islice` exists; see section 12.)

### 3.6 The good side of "one position": resuming

The shared position is not only a trap. It is also a feature. Because the bookmark stays where you left it, you can **stop and continue later**:

```python
it = iter([1, 2, 3, 4, 5])
for n in it:
    print("outer", n)
    if n == 2:
        break
print("rest:", list(it))
```

```text
$ python once8.py
outer 1
outer 2
rest: [3, 4, 5]
```

And you can call `next(it)` **inside** a loop over `it` to take an extra item. Here each loop step eats two items:

```python
it = iter([1, 2, 3, 4, 5, 6])
for a in it:
    b = next(it)
    print(a, b)
```

```text
$ python once9.py
1 2
3 4
5 6
```

(With an odd number of items the last `next(it)` would raise `StopIteration` inside the loop body, which is *not* caught by the `for`. You would use `next(it, None)` there.)

### 3.7 Predict the output

```python
nums = iter([1, 2, 3, 4, 5, 6])
print(3 in nums)
print(sum(nums))
print(list(nums))
```

<details><summary>Answer</summary>

```text
True
15
[]
```

`3 in nums` walks past `1`, `2` and `3`. `sum` gets what is left: `4 + 5 + 6 = 15`, and uses it up. `list` gets an empty iterator.

</details>

### 3.8 Predict the output

```python
pairs = zip([1, 2, 3], "abc")
first = next(pairs)
print(first)
print(dict(pairs))
```

<details><summary>Answer</summary>

```text
(1, 'a')
{2: 'b', 3: 'c'}
```

`zip` returns an iterator of pairs. `next` takes the first pair, so `dict` only receives the remaining two.

</details>

## 4. Peek under the hood: the protocol in a class

This section is a **peek**, not a lesson in classes. Classes come properly in core.14, and you will not be asked to write one in this module. But seeing a hand-made iterator once makes everything later obvious, so read it like a diagram.

### 4.1 Just enough about classes

A **class** is a way to make your own kind of object that keeps some data together with the functions that work on it. Three facts are enough here:

- `class Countdown:` starts the definition. Functions written inside it are called **methods**.
- `Countdown(3)` creates a new object. Python then calls the method `__init__` to set it up.
- Every method gets the object itself as its first parameter, by convention called `self`. `self.current = start` stores a value **inside** the object, so it survives between method calls.

Methods with double underscores on both sides (`__init__`, `__iter__`, `__next__`) are **special methods**: Python calls them for you at certain moments. `iter(x)` calls `x.__iter__()`. `next(x)` calls `x.__next__()`. That is the whole link between the protocol and objects.

### 4.2 A countdown iterator

```python
class Countdown:
    def __init__(self, start):
        self.current = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        value = self.current
        self.current = self.current - 1
        return value


c = Countdown(3)
print(next(c))
for n in c:
    print("loop:", n)
print(list(c))
```

```text
$ python cls1.py
3
loop: 2
loop: 1
[]
```

Match each part to the protocol:

- `__next__` is "give me the next item". It returns the current number and moves the state down by one. When nothing is left, it **raises `StopIteration` itself**. That is all a `for` loop needs.
- `__iter__` returns `self`. That makes the object its own iterator, exactly like `iter(it) is it` in section 3.1.
- Because it is an iterator, it is **consumed once**: `next(c)` took the `3`, the loop took the rest, and `list(c)` found nothing.

### 4.3 Splitting the book from the bookmark

A list is reusable because `list.__iter__` returns a **new** bookmark every time. We can copy that design with two classes: one "book" that remembers the starting number, and one "bookmark" that does the counting.

```python
class CountdownIterator:
    def __init__(self, start):
        self.current = start

    def __iter__(self):
        return self

    def __next__(self):
        if self.current <= 0:
            raise StopIteration
        value = self.current
        self.current = self.current - 1
        return value


class Countdown:
    def __init__(self, start):
        self.start = start

    def __iter__(self):
        return CountdownIterator(self.start)


c = Countdown(3)
print(list(c))
print(list(c))
print(iter(c) is c)
```

```text
$ python cls2.py
[3, 2, 1]
[3, 2, 1]
False
```

Now `Countdown` is an **iterable** (reusable, like a list) and `CountdownIterator` is the **iterator** (one-use, has a position). This is precisely the difference between a book and a bookmark, written in code.

### 4.4 Why you will rarely write this

Look at how much code it took to say "count down from `start` to 1": two classes, four methods, manual state in `self.current`, a manual `raise StopIteration`. The next section does the same job in **four lines** with a generator, and the generator writes all of this machinery for you. That is why, in real Python code, hand-written iterator classes are rare and generators are everywhere.

## 5. Generator functions and `yield`

### 5.1 The countdown again, in four lines

```python
def countdown(n):
    while n > 0:
        yield n
        n = n - 1


print(countdown(3))
for x in countdown(3):
    print("loop:", x)
print(list(countdown(5)))
```

```text
$ python gen1.py
<generator object countdown at 0x71daf8d46bc0>
loop: 3
loop: 2
loop: 1
[5, 4, 3, 2, 1]
```

(The address after `at` differs on your machine.)

A function that contains the word `yield` anywhere in its body is a **generator function**. It behaves very differently from a normal function:

- **Calling it does not run the body.** `countdown(3)` runs none of the code inside. It only creates and returns a **generator object**: you can see it in the first line of output.
- **A generator object is an iterator.** It has `__iter__` (returning itself) and `__next__`, so it works with `next()`, `for`, `list()`, `sum()` and everything else that takes an iterable.
- **Each `next()` runs the body until the next `yield`.** `yield n` hands `n` out as the next item and **pauses** the function right there, with all its local variables kept.
- **When the body ends, the generator raises `StopIteration` for you.** You never write `raise StopIteration` in a generator.

Compare this with the `Countdown` class from section 4. The state (`self.current`) is now just the local variable `n`. The position is "which line the function is paused at". Python builds the iterator machinery for you.

### 5.2 Watching a generator pause

Prints inside the generator show exactly when its code runs.

```python
def talker():
    print("  [start]")
    yield "A"
    print("  [between A and B]")
    yield "B"
    print("  [after B, about to finish]")


g = talker()
print("created the generator")
print("got", next(g))
print("got", next(g))
print("asking for a third value...")
print("got", next(g))
```

```text
$ python gen2.py
created the generator
  [start]
got A
  [between A and B]
got B
asking for a third value...
  [after B, about to finish]
Traceback (most recent call last):
  File "/home/you/project/gen2.py", line 14, in <module>
    print("got", next(g))
                 ~~~~^^^
StopIteration
```

Follow the timeline carefully, because this is the heart of the chapter:

1. `g = talker()` printed **nothing** from inside. The body has not started.
2. The first `next(g)` starts the body. It prints `[start]`, reaches `yield "A"`, hands out `"A"` and **freezes**.
3. The second `next(g)` **resumes** from just after `yield "A"`. It prints `[between A and B]`, reaches `yield "B"`, freezes again.
4. The third `next(g)` resumes after `yield "B"`, prints the last line and falls off the end of the function. There is no more `yield`, so the generator raises `StopIteration`.

A good picture: a normal function is a phone call. You call, it talks until it is done, then hangs up (`return`). A generator is a **pause button on a video**. Each `next()` presses play; each `yield` presses pause and shows you one frame. The video remembers where it was.

In a `for` loop the final `StopIteration` is caught for you:

```python
for value in talker():
    print("got", value)
print("done")
```

```text
$ python gen3.py
  [start]
got A
  [between A and B]
got B
  [after B, about to finish]
done
```

Look at the order: the prints from inside the generator and the prints from the loop body **take turns**. The generator does not run ahead. It produces one item, the loop body uses it, and only then does the generator continue. This taking-turns is what makes generators lazy.

### 5.3 Predict the output

```python
def gen():
    print("A")
    yield 1
    print("B")
    yield 2
    print("C")


g = gen()
print("start")
x = next(g)
print("x =", x)
for y in g:
    print("y =", y)
```

<details><summary>Answer</summary>

```text
start
A
x = 1
B
y = 2
C
```

`gen()` prints nothing, so `start` comes first. `next(g)` runs up to the first `yield` (printing `A`). The `for` loop continues the **same** generator from where it paused: it prints `B`, gets `2`, then on the next round prints `C` and finishes. The loop does not restart the generator, because `iter(g) is g`.

</details>

### 5.4 Local variables survive the pause

Because the function is paused, not finished, its local variables keep their values between items. That makes "running" calculations easy:

```python
def running_total(numbers):
    total = 0
    for n in numbers:
        total = total + n
        yield total


print(list(running_total([5, 3, 10, 2])))
```

```text
$ python gen4.py
[5, 8, 18, 20]
```

`total` keeps growing between the yields. With a normal function you would have to build and return a whole list. Here the caller can stop after the first two totals and the rest are never computed.

### 5.5 `return` inside a generator

`return` in a generator means "stop now". It ends the generator just like falling off the end does. This generator yields the first long word and stops:

```python
def first_word_longer_than(words, size):
    for w in words:
        if len(w) > size:
            yield w
            return
    yield "(none)"


print(list(first_word_longer_than(["to", "be", "honest"], 3)))
print(list(first_word_longer_than(["to", "be"], 3)))
```

```text
$ python gen5.py
['honest']
['(none)']
```

A generator can also `return` a value. That value is **not** yielded. It is attached to the `StopIteration` exception, in its `.value` attribute, and a `for` loop or `list()` throws it away:

```python
def numbers():
    yield 1
    yield 2
    return "finished"


g = numbers()
print(next(g))
print(next(g))
try:
    next(g)
except StopIteration as e:
    print("stopped, value =", e.value)
print(list(numbers()))
```

```text
$ python gen6.py
1
2
stopped, value = finished
[1, 2]
```

You will see one real use of a returned value with `yield from` in section 9. Most generators never return a value.

### 5.6 A generator is consumed once; calling the function again makes a fresh one

A generator object is an iterator, so all of section 3 applies to it:

```python
def evens(limit):
    for n in range(0, limit, 2):
        yield n


g = evens(7)
print(list(g))
print(list(g))
print(list(evens(7)))
print(iter(g) is g)
```

```text
$ python gen7.py
[0, 2, 4, 6]
[]
[0, 2, 4, 6]
True
```

The generator **function** `evens` is like the "book": every call `evens(7)` makes a new, independent generator object. The generator **object** `g` is a "bookmark". So the rule is simple: **if you need the data again, call the function again** (or save the items in a list the first time).

Two generators from the same function do not affect each other:

```python
def letters():
    yield "a"
    yield "b"


g1 = letters()
g2 = letters()
print(next(g1), next(g1))
print(next(g2))
```

```text
$ python gen13.py
a b
a
```

### 5.7 The word `yield` changes the whole function

Python decides "is this a generator function?" by looking at the source code, **before** running anything. A `yield` anywhere in the body, even on a line that can never run, makes the whole function a generator function:

```python
def maybe():
    if False:
        yield 1


print(maybe())
print(list(maybe()))


def plain():
    return 1


print(plain())
```

```text
$ python gen8.py
<generator object maybe at 0x79babbf46b00>
[]
1
```

This matters when you add a `yield` to an existing function while debugging: suddenly calling the function does nothing at all, because it just builds a generator that nobody runs.

### 5.8 Errors appear late

Because the body runs only on `next()`, an error inside the generator also appears only on `next()`, not when you call the function:

```python
def parse_numbers(texts):
    for t in texts:
        yield int(t)


g = parse_numbers(["10", "20", "oops", "40"])
print("generator created, no error yet")
print(next(g))
print(next(g))
print(next(g))
```

```text
$ python gen9.py
generator created, no error yet
10
20
Traceback (most recent call last):
  File "/home/you/project/gen9.py", line 10, in <module>
    print(next(g))
          ~~~~^^^
  File "/home/you/project/gen9.py", line 3, in parse_numbers
    yield int(t)
          ~~~^^^
ValueError: invalid literal for int() with base 10: 'oops'
```

The traceback shows two places: the `next(g)` that asked, and the line inside the generator that failed. Read both.

And if an exception escapes from a generator, **the generator is finished for good**. You cannot "skip the bad item and continue" from outside:

```python
def parse_numbers(texts):
    for t in texts:
        yield int(t)


g = parse_numbers(["10", "oops", "30"])
print(next(g))
try:
    next(g)
except ValueError as e:
    print("error:", e)
print(next(g, "generator is finished"))
```

```text
$ python gen10.py
10
error: invalid literal for int() with base 10: 'oops'
generator is finished
```

`"30"` is never produced. If you want to skip bad items, put the `try/except` **inside** the generator, around the risky line. You will do exactly that in the project (section 18).

### 5.9 Type hints for generators

From core.09 you know how to annotate functions. For a generator function, annotate what **calling it returns**, which is an iterator. The simplest honest hint is `Iterator[X]`, where `X` is the type of each yielded item. Import it from `collections.abc`:

```python
from collections.abc import Iterator, Generator


def countdown(n: int) -> Iterator[int]:
    while n > 0:
        yield n
        n -= 1


def numbers() -> Generator[int, None, str]:
    yield 1
    yield 2
    return "finished"


print(list(countdown(3)))
print(list(numbers()))
```

```text
$ python gen11.py
[3, 2, 1]
[1, 2]
```

```text
$ python -m mypy gen11.py
Success: no issues found in 1 source file
```

- `Iterator[int]`: "this yields ints". Use it for almost every generator.
- `Generator[int, None, str]`: the full form. The three slots are: the type **yielded**, the type you can **send** in (section 10; `None` if you never send), and the type **returned**. Use it only when you send values or return a value.
- For parameters, the matching hint is `Iterable[X]`: "anything I can loop over". A function that only loops over its input should accept `Iterable[str]`, not `list[str]`, so callers can pass a list, a tuple or a generator.

### 5.10 Generator vs normal function: a summary table

| | normal function | generator function |
|---|---|---|
| contains | `return` | at least one `yield` |
| calling it | runs the body to the end | runs **nothing**, returns a generator object |
| gives back | one value | many values, one per `next()` |
| between values | no "between": it is finished | **paused**, local variables kept |
| when it ends | `return` / end of body | `return` / end of body raises `StopIteration` |
| reuse | call again | call again (each generator object is one-use) |

## 6. Generator expressions and lazy evaluation

### 6.1 Round brackets instead of square brackets

You know list comprehensions from core.05. Replace the square brackets with round ones and you get a **generator expression**: the same syntax, but lazy.

```python
nums = [1, 2, 3, 4]
as_list = [n * 10 for n in nums]
as_gen = (n * 10 for n in nums)
print(as_list)
print(as_gen)
print(list(as_gen))
print(sum(n * n for n in nums))
print(max(len(w) for w in ["a", "abc", "ab"]))
print(",".join(str(n) for n in nums))
```

```text
$ python gx1.py
[10, 20, 30, 40]
<generator object <genexpr> at 0x7c3db60b64d0>
[10, 20, 30, 40]
30
3
1,2,3,4
```

(The address differs on your machine.)

A generator expression is a short way to write a small generator function. These two are the same thing:

```python
squares = (n * n for n in nums if n % 2 == 0)

def _squares(nums):
    for n in nums:
        if n % 2 == 0:
            yield n * n
squares = _squares(nums)
```

When a generator expression is the **only** argument of a function call, you can drop its own brackets: `sum(n * n for n in nums)` instead of `sum((n * n for n in nums))`. If there are other arguments, the brackets are needed:

```python
print(sum(x for x in range(5)))
print(sum((x for x in range(5)), 100))
```

```text
$ python gx5.py
10
110
```

### 6.2 When does the work happen?

A list comprehension does all its work on the line where it is written. A generator expression does its work later, one item at a time, when somebody asks.

```python
def square(n):
    print("  squaring", n)
    return n * n


print("list comprehension:")
squares = [square(n) for n in range(3)]
print("built:", squares)

print("generator expression:")
lazy = (square(n) for n in range(3))
print("built:", lazy is not None)
for s in lazy:
    print("used", s)
```

```text
$ python gx2.py
list comprehension:
  squaring 0
  squaring 1
  squaring 2
built: [0, 1, 4]
generator expression:
built: True
  squaring 0
used 0
  squaring 1
used 1
  squaring 2
used 4
```

The list version squares everything first, then you use it. The generator version squares **one** number, you use it, then it squares the next one. Same taking-turns as in section 5.2.

### 6.3 Memory does not grow with the data

```python
import sys

for size in [10, 1_000, 100_000]:
    as_list = [n for n in range(size)]
    as_gen = (n for n in range(size))
    print(size, sys.getsizeof(as_list), sys.getsizeof(as_gen))
```

```text
$ python gx3.py
10 184 200
1000 8856 200
100000 800984 200
```

(Exact sizes depend on your Python version and computer; these are from 64-bit Python 3.14.)

The list grows with the data: about 8 bytes per item for its slots alone. The generator expression is always the same size, because it stores no items. For 10 items the list is actually smaller. Laziness only pays off when the data is large, or when you might stop early.

### 6.4 Stopping early: `any`, `all`, `next`

Laziness has a second benefit besides memory: **work you never ask for is never done**. `any()` stops as soon as it finds a `True`. With a generator expression, the remaining items are never even computed:

```python
def is_big(n):
    print("  checking", n)
    return n > 100


values = [5, 500, 7, 9000, 3]
print(any(is_big(v) for v in values))
print("---")
print(any([is_big(v) for v in values]))
```

```text
$ python gx4.py
  checking 5
  checking 500
True
---
  checking 5
  checking 500
  checking 7
  checking 9000
  checking 3
True
```

With the square brackets, the list comprehension checks all five values **before** `any` even starts. If `is_big` were slow (a network call, a big calculation), the difference would be huge. `all()` works the same way: it stops at the first `False`.

### 6.5 What a generator expression cannot do

A generator expression is an iterator, so it has all the limits from section 3: one pass only, no `len`, no indexing, no slicing, no sorting in place.

```python
words = ["pear", "fig", "apple"]
lengths = (len(w) for w in words)
print(len(lengths))
```

```text
$ python gx6.py
Traceback (most recent call last):
  File "/home/you/project/gx6.py", line 3, in <module>
    print(len(lengths))
          ~~~^^^^^^^^^
TypeError: object of type 'generator' has no len()
```

### 6.6 When does it read the input?

A generator expression reads its source **when it runs**, not when it is written. So if the source list changes before you consume the generator, you see the change:

```python
nums = [1, 2, 3]
doubled = (n * 2 for n in nums)
nums.append(4)
print(list(doubled))

nums = [1, 2, 3]
doubled = (n * 2 for n in nums)
nums = [100, 200]
print(list(doubled))
```

```text
$ python gx7.py
[2, 4, 6, 8]
[2, 4, 6]
```

Two different results, and both make sense once you know one detail: the **first** `for ... in nums` part is evaluated immediately, when the generator expression is created. So the generator grabs a reference to the list object that `nums` names **at that moment**. Appending to that same list (first case) is visible. Making the name `nums` point to a new list (second case, rebinding, from core.06) is not: the generator still holds the old list. Everything else in the expression runs lazily.

The safe habit: build a generator and consume it soon after, without changing its source in between.

### 6.7 List or generator? A decision guide

Use a **list** (comprehension) when:

- you need the data more than once, or need `len`, indexing, slicing or sorting;
- the data is small and you want to print or inspect it while debugging;
- you return the result from a function and callers expect a list.

Use a **generator** (expression or function) when:

- the data is large or endless;
- you pass it straight into something that loops once: `sum`, `max`, `min`, `any`, `all`, `"".join`, `sorted`, `dict(...)`, `set(...)`, a `for` loop;
- you might stop early;
- it is one stage of a pipeline (section 8).

A simple rule of thumb: if the only thing you do with the list is loop over it once, it did not need to be a list.

### 6.8 Predict the output

```python
squares = (n * n for n in range(4))
total = sum(squares)
biggest = max(squares, default=-1)
print(total, biggest)
```

<details><summary>Answer</summary>

```text
14 -1
```

`sum` used the generator up (`0 + 1 + 4 + 9 = 14`). `max` got an empty iterator. Without `default=-1`, `max` would raise `ValueError: max() iterable argument is empty`. If you need both values, use a list, or a list comprehension, instead.

</details>

## 7. Infinite sequences

### 7.1 A generator that never ends

A list must have an end: it has to fit in memory. A generator does not. Because it produces items only on request, it can **describe** an endless sequence and let the caller decide when to stop.

```python
def naturals():
    n = 1
    while True:
        yield n
        n += 1


nums = naturals()
print(next(nums), next(nums), next(nums))

for n in naturals():
    if n * n > 50:
        print("first square above 50 comes from", n)
        break
```

```text
$ python inf1.py
1 2 3
first square above 50 comes from 8
```

`while True` without a `break` would be an infinite loop in a normal function. Inside a generator it is fine and common: the `yield` pauses it after each item. The **consumer** owns the stop condition: here the `break` in the `for` loop.

Why is this useful? Because the question "how many do I need?" often has no answer in advance. "The first Fibonacci number above 1000": you do not know how many to compute until you find it. With an infinite generator you separate **producing** the sequence from **deciding when to stop**.

```python
def fibonacci():
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b


def take(n, iterable):
    result = []
    for item in iterable:
        if len(result) == n:
            break
        result.append(item)
    return result


print(take(10, fibonacci()))
for f in fibonacci():
    if f > 1000:
        print("first Fibonacci number above 1000:", f)
        break
```

```text
$ python inf2.py
[0, 1, 1, 2, 3, 5, 8, 13, 21, 34]
first Fibonacci number above 1000: 1597
```

### 7.2 Danger: never ask for "all" of an infinite iterator

`list(naturals())`, `sum(fibonacci())`, `max(...)`, `sorted(...)`, `len(list(...))`, or a `for` loop with no `break`: all of these try to reach the end. An infinite iterator has no end. The program runs forever, eating memory until the operating system kills it (or your laptop freezes). We do not show the output, for that reason.

Before you pass an iterator to something that consumes everything, ask: **is this iterator finite?** If not, put something in between that stops: a `break`, `takewhile` or `islice` (section 12), or `zip` with a finite partner.

### 7.3 A careful `take`

The `take` above has a subtle problem. Look at what happens to an iterator after `take`:

```python
def take(n, iterable):
    result = []
    for item in iterable:
        if len(result) == n:
            break
        result.append(item)
    return result


def take_bad(n, iterable):
    result = []
    for item in iterable:
        result.append(item)
        if len(result) == n:
            break
    return result


it = iter([1, 2, 3, 4, 5])
print(take(2, it), list(it))
it = iter([1, 2, 3, 4, 5])
print(take_bad(2, it), list(it))
print(take_bad(0, [1, 2, 3]))
```

```text
$ python inf3.py
[1, 2] [4, 5]
[1, 2] [3, 4, 5]
[1, 2, 3]
```

- `take` returns the right list, but it **ate the `3`**. To discover that it had enough, it pulled one more item from the iterator, then threw it away. On a list you never notice. On a shared iterator, the item is lost.
- `take_bad` leaves the rest intact, but it is wrong for `n = 0`: it appends before checking, so it returns all three items.

A version that is right in both cases asks for exactly `n` items with `next()` and nothing more:

```python
def take(n, iterable):
    it = iter(iterable)
    result = []
    for _ in range(n):
        try:
            result.append(next(it))
        except StopIteration:
            break
    return result


it = iter([1, 2, 3, 4, 5])
print(take(2, it), list(it))
print(take(10, "abc"))
```

```text
$ python inf4.py
[1, 2] [3, 4, 5]
['a', 'b', 'c']
```

Notice `it = iter(iterable)` at the start: it makes the function work with any iterable (a string, a list), not only with iterators. And if `iterable` is already an iterator, `iter()` returns it unchanged, so the caller's position is shared, as we want. In section 12 you will meet `itertools.islice`, which does this job for you; it never takes more than it needs.

## 8. Pipelines: chaining generators

### 8.1 The problem with one big loop

Here is a small web-app log. We want the users who had errors.

```python
LOG = [
    "2026-10-01 09:00:01 INFO  user=asha action=login",
    "",
    "2026-10-01 09:00:05 ERROR user=ravi action=upload size=2048",
    "# comment line",
    "2026-10-01 09:01:10 WARN  user=asha action=upload size=99999",
    "2026-10-01 09:02:00 ERROR user=asha action=delete",
    "   ",
    "2026-10-01 09:03:30 INFO  user=meena action=logout",
]

# Version 1: one big loop that does everything
error_users = []
for line in LOG:
    line = line.strip()
    if line and not line.startswith("#"):
        parts = line.split()
        level = parts[2]
        if level == "ERROR":
            for field in parts[3:]:
                if field.startswith("user="):
                    error_users.append(field[5:])
print(error_users)
```

```text
$ python pipe1.py
['ravi', 'asha']
```

It works. But it is four levels deep, and it mixes four different jobs in one block: **cleaning** lines, **parsing** them, **filtering** by level, and **extracting** a field. To answer a second question ("which uploads were slow?") you would copy the whole block and change the middle. To test the parsing alone, you cannot: it is buried inside.

### 8.2 One job per generator

A **pipeline** splits the work into stages. Each stage is a generator that takes an iterable in and yields items out. Then you connect them like pipes: the output of one is the input of the next.

```python
def clean(lines):
    for line in lines:
        line = line.strip()
        if line and not line.startswith("#"):
            yield line


def parse(lines):
    for line in lines:
        date, time, level, *rest = line.split()
        fields = {}
        for pair in rest:
            key, value = pair.split("=", 1)
            fields[key] = value
        yield {"time": time, "level": level, **fields}


def only_level(records, level):
    for r in records:
        if r["level"] == level:
            yield r


lines = clean(LOG)
records = parse(lines)
errors = only_level(records, "ERROR")
print(errors)
for r in errors:
    print(r["time"], r["user"], r["action"])
```

(Same `LOG` as above.)

```text
$ python pipe2.py
<generator object only_level at 0x74669231c200>
09:00:05 ravi upload
09:02:00 asha delete
```

`date, time, level, *rest = line.split()` is star unpacking from core.05: the first three words go into names, the rest into a list. `{..., **fields}` merges the `fields` dict into a new dict.

Now each stage is small, has one job and a clear name. You can test `parse` with three lines of input. You can reuse `clean` and `parse` for any question and only change the last stage.

### 8.3 The order of work: one item flows all the way through

When the three lines `lines = clean(LOG)`, `records = parse(lines)`, `errors = only_level(...)` run, **nothing is processed**. Each call just builds a paused generator wrapped around the previous one. Work starts when the `for` loop asks the **last** stage for an item. Prints make the flow visible:

```python
def source(items):
    for x in items:
        print(f"source  -> {x}")
        yield x


def double(xs):
    for x in xs:
        print(f"double  -> {x * 2}")
        yield x * 2


def keep_big(xs):
    for x in xs:
        if x > 4:
            print(f"keep    -> {x}")
            yield x


pipeline = keep_big(double(source([1, 2, 3, 4])))
print("pipeline built, nothing has run yet")
for value in pipeline:
    print(f"RESULT  {value}")
```

```text
$ python pipe3.py
pipeline built, nothing has run yet
source  -> 1
double  -> 2
source  -> 2
double  -> 4
source  -> 3
double  -> 6
keep    -> 6
RESULT  6
source  -> 4
double  -> 8
keep    -> 8
RESULT  8
```

Read the output like a conveyor belt in a factory:

1. The `for` loop asks `keep_big` for an item.
2. `keep_big` needs input, so it asks `double`, which asks `source`.
3. `source` produces `1`; `double` turns it into `2`; `keep_big` rejects it (not `> 4`) and asks for another.
4. The same happens with `2` → `4`, rejected.
5. `3` → `6` passes all the way and reaches the loop body: `RESULT 6`.

At any moment **only one item is in the pipeline**. There is no list of "all doubled values" anywhere. That is why a pipeline over a 20 GB log needs only a few MB: the memory cost is one item per stage, not one item per line.

### 8.4 Short pipelines with generator expressions

For simple stages you do not need a whole function. Generator expressions chain the same way:

```python
LOG = [
    "09:00 GET /home 200 12",
    "09:01 GET /cart 500 340",
    "09:01 POST /login 200 45",
    "09:02 GET /cart 500 290",
    "09:03 GET /home 200 9",
]

rows = (line.split() for line in LOG)
codes = (int(r[3]) for r in rows)
errors = sum(1 for c in codes if c >= 500)
print("server errors:", errors)

rows = (line.split() for line in LOG)
slow = [r[2] for r in rows if int(r[4]) > 100]
print("slow pages:", slow)
```

```text
$ python pipe5.py
server errors: 2
slow pages: ['/cart', '/cart']
```

`sum(1 for c in codes if c >= 500)` is the standard way to **count** items in an iterator that match a condition, without building a list.

Notice that `rows` had to be built a second time for the second question. The first `rows` was used up by the first pipeline. When the source is a list (like `LOG`), building the pipeline again is cheap. When the source is a one-time stream (a network connection, a real file being read), you either answer all questions in **one** pass, or you read it again.

### 8.5 Why this is better than nested loops

- **Memory**: one item at a time, so the input can be bigger than RAM.
- **Speed to first result**: the first result comes out before the last input line is read. If you stop early (`break`, `islice`), the rest is never read.
- **Readability**: each stage has one job and a name. The final pipeline reads like a sentence: "only errors, from parsed records, from cleaned lines".
- **Testing**: each stage is a small function you can test with a short list (core.08).
- **Reuse**: new questions reuse the same stages and add one more at the end.

The third outcome of this module is "build a pipeline with itertools instead of nested loops". You now have the pipeline idea. Sections 11 to 16 give you the ready-made stages from `itertools`.

## 9. `yield from`: handing over to another iterable

### 9.1 The repetitive loop

Often a generator wants to yield every item of some other iterable. You can write a loop:

```python
def inner():
    yield 1
    yield 2


def outer_loop():
    yield "start"
    for x in inner():
        yield x
    yield "end"


def outer_from():
    yield "start"
    yield from inner()
    yield "end"


print(list(outer_loop()))
print(list(outer_from()))
```

```text
$ python yf1.py
['start', 1, 2, 'end']
['start', 1, 2, 'end']
```

`yield from X` means "yield every item of `X`, one by one, then continue here". `X` can be any iterable: a list, a string, a range, another generator. For simple use it is exactly the same as the two-line `for` loop, just shorter and clearer about intent: "hand over to this one for a while".

### 9.2 Flattening

The most common use: flattening a list of lists into one stream.

```python
def flatten_once(rows):
    for row in rows:
        yield from row


print(list(flatten_once([[1, 2], [3], [], [4, 5]])))
print(list(flatten_once(["ab", "cd"])))
```

```text
$ python yf2.py
[1, 2, 3, 4, 5]
['a', 'b', 'c', 'd']
```

Empty inner lists simply yield nothing. Strings are iterables too, so they flatten into their characters. (`itertools.chain.from_iterable` does the same job, section 12.)

### 9.3 Recursion with `yield from`

`yield from` shines with **recursive** generators (recursion was in core.06). To flatten lists nested to any depth: if an item is a list, hand over to a recursive call on it; otherwise yield the item.

```python
def flatten(items):
    for item in items:
        if isinstance(item, list):
            yield from flatten(item)
        else:
            yield item


data = [1, [2, [3, 4], 5], [[6]], 7]
print(list(flatten(data)))
```

```text
$ python yf3.py
[1, 2, 3, 4, 5, 6, 7]
```

Without `yield from`, the line `flatten(item)` alone would only **create** a generator and throw it away. A very common mistake is to write just `flatten(item)` inside the loop and wonder where the nested items went. A recursive generator must `yield from` its recursive call.

The same idea walks a tree. Here a folder is a pair `(name, list_of_children)`:

```python
def walk(tree, depth=0):
    name, children = tree
    yield "  " * depth + name
    for child in children:
        yield from walk(child, depth + 1)


folders = ("home", [
    ("kavya", [("notes", []), ("code", [("python", [])])]),
    ("guest", []),
])
for line in walk(folders):
    print(line)
```

```text
$ python yf5.py
home
  kavya
    notes
    code
      python
  guest
```

Each call yields its own name, then hands over to one recursive call per child. The `depth` parameter grows by one at each level, which gives the indentation.

### 9.4 `yield from` gives back the return value

There is one thing `yield from` does that the plain loop cannot. The **value** of the expression `yield from sub()` is whatever `sub` returned (the `StopIteration.value` from section 5.5):

```python
def read_header():
    yield "header line 1"
    yield "header line 2"
    return 2


def document():
    count = yield from read_header()
    yield f"(the header had {count} lines)"
    yield "body"


for line in document():
    print(line)
```

```text
$ python yf4.py
header line 1
header line 2
(the header had 2 lines)
body
```

The sub-generator yields its items out to the caller **and** reports a result back to the generator that delegated to it. You will not need this often; it is mostly used to build bigger generators from smaller ones in libraries. (`yield from` also forwards `send` and `throw` from section 10 into the sub-generator, which is why it exists as special syntax.)

### 9.5 Predict the output

```python
def a():
    yield 1
    yield 2
    return 3


def b():
    result = yield from a()
    yield result * 10


print(list(b()))
```

<details><summary>Answer</summary>

```text
[1, 2, 30]
```

`b` passes on `1` and `2` from `a`. When `a` finishes, its return value `3` lands in `result`, and `b` yields `30`. The `3` itself is never yielded.

</details>

## 10. `send`, `throw` and `close`

An honest note first: **you will rarely use `send` and `throw` in everyday code.** They turn a generator into a two-way channel (a *coroutine*), which was important in older Python for asynchronous programs. Modern code uses `async`/`await` for that. But you will meet them in interviews and in library code, and `close` with `try/finally` is genuinely useful. So here is a short, clear tour.

### 10.1 `yield` is also an expression

Until now `yield value` has been a statement that hands a value **out**. It can also bring a value **in**. Write `received = yield`, and the generator pauses; when the caller calls `g.send(something)`, the generator resumes and `received` becomes `something`.

```python
def echo():
    print("  started")
    while True:
        received = yield
        print("  got:", received)


g = echo()
next(g)
g.send("hello")
g.send(42)
```

```text
$ python send1.py
  started
  got: hello
  got: 42
```

Why the `next(g)` first? A new generator is paused **before its first line**, not at a `yield`. There is no `yield` waiting to receive a value yet. `next(g)` runs it to the first `yield`; this is called **priming** the generator. Only then can `send` deliver a value. If you forget:

```python
def averager():
    total = 0
    count = 0
    average = None
    while True:
        value = yield average
        total += value
        count += 1
        average = total / count


avg = averager()
avg.send(10)
```

```text
$ python send3.py
Traceback (most recent call last):
  File "/home/you/project/send3.py", line 13, in <module>
    avg.send(10)
    ~~~~~~~~^^^^
TypeError: can't send non-None value to a just-started generator
```

### 10.2 Two-way: a running average

`value = yield average` does both directions on one line: it hands `average` **out**, pauses, and when resumed takes the sent value **in**. `send` returns the next yielded value.

```python
avg = averager()
print(next(avg))
print(avg.send(10))
print(avg.send(20))
print(avg.send(60))
```

```text
$ python send2.py
None
10.0
15.0
30.0
```

Step by step:

1. `next(avg)` primes it: runs to `yield average` with `average = None`, so it prints `None`.
2. `avg.send(10)`: `value` becomes `10`; total 10, count 1, average 10.0; loop back to `yield average`, which hands out `10.0`. That is what `send` returns.
3. `send(20)`: total 30, count 2, average `15.0`.
4. `send(60)`: total 90, count 3, average `30.0`.

The generator keeps private state (total, count) between calls, which is the attraction. But note that a simple closure from core.06 could do the same job, and most readers would find the closure easier. That is the main reason `send` is rare.

`next(g)` is exactly the same as `g.send(None)`: the paused `yield` expression then evaluates to `None`. So in `echo` from 10.1, calling `next(g)` instead of `g.send(...)` would print `got: None`.

### 10.3 `throw`: raise an exception at the paused `yield`

`g.throw(exc)` resumes the generator, but instead of continuing normally, the exception `exc` is raised **at the line where it is paused**. If the generator catches it, it can recover and continue; `throw` then returns the next yielded value.

```python
def worker():
    n = 0
    while True:
        try:
            yield n
            n += 1
        except ValueError as e:
            print("  worker handled:", e)
            n = 0


w = worker()
print(next(w))
print(next(w))
print(next(w))
print(w.throw(ValueError("start again")))
print(next(w))
```

```text
$ python throw1.py
0
1
2
  worker handled: start again
0
1
```

If the generator does not catch it, the exception comes back out of `throw` to the caller, and the generator is finished:

```python
def numbers():
    yield 1
    yield 2


g = numbers()
print(next(g))
g.throw(KeyError("boom"))
```

```text
$ python throw2.py
1
Traceback (most recent call last):
  File "/home/you/project/throw2.py", line 8, in <module>
    g.throw(KeyError("boom"))
    ~~~~~~~^^^^^^^^^^^^^^^^^^
  File "/home/you/project/throw2.py", line 2, in numbers
    yield 1
KeyError: 'boom'
```

The traceback points at `yield 1`: that is where the generator was paused when the exception was thrown in.

### 10.4 `close` and clean-up with `try/finally`

`g.close()` tells a generator "you will not be asked for anything else, stop now". Python raises a special exception, `GeneratorExit`, at the paused `yield`. You normally do not catch it. Instead you use `try/finally` (core.07), so clean-up code runs however the generator ends.

```python
def reader(lines):
    print("  open the resource")
    try:
        for line in lines:
            yield line
    finally:
        print("  clean up the resource")


r = reader(["a", "b", "c", "d"])
print(next(r))
print(next(r))
r.close()
print("closed")
print(next(r, "nothing more"))
```

```text
$ python close1.py
  open the resource
a
b
  clean up the resource
closed
nothing more
```

After `close()`, the generator is finished: `next` gives the default.

Why care? Later (core.12) generators will read real files, and a file should be closed when you stop reading, even if you stop after two lines. The `finally` block is the place for that. You often do not even call `close` yourself:

```python
for line in reader(["a", "b", "c", "d"]):
    print(line)
    if line == "b":
        break
print("after the loop")
```

```text
$ python close2.py
  open the resource
a
b
  clean up the resource
after the loop
```

After the `break`, nothing refers to the generator any more. Python (CPython, the normal Python) deletes it at once, and deleting an unfinished generator calls `close()` on it, which runs the `finally`. Do not rely on the exact moment in other Python versions; when timing matters, call `close()` yourself.

If you do catch `GeneratorExit` to log something, **re-raise it**. A generator that keeps yielding after `GeneratorExit` makes Python raise `RuntimeError: generator ignored GeneratorExit`.

```python
def tracked():
    try:
        yield 1
        yield 2
    except GeneratorExit:
        print("  GeneratorExit arrived")
        raise


g = tracked()
print(next(g))
g.close()
print("closed cleanly")
```

```text
$ python close4.py
1
  GeneratorExit arrived
closed cleanly
```

### 10.5 The three methods in one table

| method | resumes the generator with... | returns |
|---|---|---|
| `next(g)` / `g.send(None)` | `yield` expression = `None` | next yielded value |
| `g.send(v)` | `yield` expression = `v` | next yielded value |
| `g.throw(exc)` | `exc` raised at the `yield` | next yielded value (if caught) |
| `g.close()` | `GeneratorExit` raised at the `yield` | `None`; generator is finished |

## 11. itertools 1: infinite iterators

The `itertools` module is a standard toolbox of fast, lazy iterator building blocks. Everything in it returns an **iterator**: lazy, and consumed once. Import what you need:

```python
from itertools import count, cycle, repeat, islice
```

We group the tools in three families: **infinite** (this section), **terminating** (sections 12 to 14), and **combinatoric** (section 15). Since infinite iterators must never be passed to `list()` alone, we use `islice(it, n)` to take the first `n` items. (`islice` is explained fully in 12.1; for now read it as "the first n".)

### 11.1 `count`, `cycle`, `repeat`

```python
from itertools import count, cycle, repeat, islice

print(list(islice(count(), 5)))
print(list(islice(count(10), 3)))
print(list(islice(count(1, 0.5), 4)))
print(list(islice(count(100, -10), 4)))

print(list(islice(cycle("AB"), 5)))
print(list(islice(cycle([1, 2, 3]), 7)))

print(list(repeat("hi", 3)))
print(list(islice(repeat(0), 4)))
print(list(map(pow, [2, 3, 4], repeat(2))))
```

```text
$ python it_inf.py
[0, 1, 2, 3, 4]
[10, 11, 12]
[1, 1.5, 2.0, 2.5]
[100, 90, 80, 70]
['A', 'B', 'A', 'B', 'A']
[1, 2, 3, 1, 2, 3, 1]
['hi', 'hi', 'hi']
[0, 0, 0, 0]
[4, 9, 16]
```

- `count(start=0, step=1)`: `start, start+step, start+2*step, ...` forever. Like `range` with no end, and it allows float steps.
- `cycle(iterable)`: repeats the items of the iterable forever. (It saves a copy of the items as it goes the first time, so it can repeat them even if the input was a one-time iterator.)
- `repeat(x)`: `x` forever. `repeat(x, n)`: `x` exactly `n` times, so that one is finite.

`repeat` looks useless alone, but it is handy as a "constant column" for `map` or `zip`: `map(pow, [2, 3, 4], repeat(2))` squares each number.

### 11.2 Infinite iterators with `zip`

`zip` stops at its **shortest** input. So zipping an infinite iterator with a finite list is safe, and a neat way to attach numbers or labels:

```python
from itertools import count

names = ["asha", "ravi", "meena"]
for number, name in zip(count(101), names):
    print(number, name)
```

```text
$ python it_count2.py
101 asha
102 ravi
103 meena
```

(For numbering from a start value, `enumerate(names, start=101)` does the same. `count` is more flexible: steps, floats, and you can share one counter between several loops.)

`cycle` is perfect for "take turns":

```python
from itertools import cycle

players = cycle(["Asha", "Ravi"])
moves = ["e4", "e5", "Nf3", "Nc6", "Bb5"]
for move in moves:
    print(next(players), "plays", move)
```

```text
$ python it_cycle2.py
Asha plays e4
Ravi plays e5
Asha plays Nf3
Ravi plays Nc6
Asha plays Bb5
```

## 12. itertools 2: slicing, joining and stopping

### 12.1 `islice`: slicing any iterator

You cannot write `gen[2:5]`, because iterators have no indexes. `islice(iterable, stop)` or `islice(iterable, start, stop, step)` does the same thing lazily, by walking forward and skipping:

```python
from itertools import islice

letters = "abcdefghij"
print(list(islice(letters, 3)))
print(list(islice(letters, 2, 5)))
print(list(islice(letters, 0, None, 3)))
print(list(islice(letters, 8, 100)))

it = iter(range(10))
print(list(islice(it, 3)))
print(list(islice(it, 3)))
print(list(it))
```

```text
$ python it_islice.py
['a', 'b', 'c']
['c', 'd', 'e']
['a', 'd', 'g', 'j']
['i', 'j']
[0, 1, 2]
[3, 4, 5]
[6, 7, 8, 9]
```

The arguments mean the same as in normal slicing: `islice(x, 2, 5)` is like `x[2:5]`; `None` means "no limit". Asking for more than exists is fine (`islice(letters, 8, 100)`). On a shared iterator, `islice` takes exactly what it needs and leaves the rest: three calls on `it` gave three neat pieces, with nothing lost. This is the careful `take` from section 7.3, built in.

Two differences from normal slicing:

- **No negative numbers.** "The last 3 items" needs to know where the end is, and an iterator does not know until it gets there.

```python
from itertools import islice

print(list(islice("abc", -1)))
```

```text
$ python it_islice_err.py
Traceback (most recent call last):
  File "/home/you/project/it_islice_err.py", line 3, in <module>
    print(list(islice("abc", -1)))
               ~~~~~~^^^^^^^^^^^
ValueError: Stop argument for islice() must be None or an integer: 0 <= x <= sys.maxsize.
```

- **Skipping is not free.** `islice(it, 1_000_000, None)` must call `next` a million times to get there. A list can jump straight to an index; an iterator cannot.

### 12.2 `chain`: one stream from many

`chain(a, b, c)` yields everything from `a`, then everything from `b`, then from `c`. No list is built.

```python
from itertools import chain

a = [1, 2]
b = (3, 4)
c = "xy"
print(list(chain(a, b, c)))

groups = [["asha", "ravi"], ["meena"], [], ["dev", "zoya"]]
print(list(chain.from_iterable(groups)))
print(list(chain(*groups)))
```

```text
$ python it_chain.py
[1, 2, 3, 4, 'x', 'y']
['asha', 'ravi', 'meena', 'dev', 'zoya']
['asha', 'ravi', 'meena', 'dev', 'zoya']
```

- `chain(a, b, c)`: when you have the iterables as separate arguments.
- `chain.from_iterable(groups)`: when you have **one** iterable **of** iterables. It is the same as `flatten_once` from section 9.2.
- `chain(*groups)` gives the same result, but `*groups` unpacks all groups into arguments **first**. If `groups` is a huge or endless generator, that never finishes. `from_iterable` is lazy all the way, so prefer it.

Compare with `a + b`: list `+` builds a new list (memory, and both must be lists). `chain` works across types and builds nothing.

### 12.3 `takewhile` and `dropwhile`: stop or start at a condition

```python
from itertools import takewhile, dropwhile

nums = [2, 4, 6, 7, 8, 10]
print(list(takewhile(lambda n: n % 2 == 0, nums)))
print(list(dropwhile(lambda n: n % 2 == 0, nums)))
print(list(filter(lambda n: n % 2 == 0, nums)))

lines = ["# config", "# version 2", "name=app", "# not a header", "port=80"]
body = dropwhile(lambda line: line.startswith("#"), lines)
print(list(body))
```

```text
$ python it_takedrop.py
[2, 4, 6]
[7, 8, 10]
[2, 4, 6, 8, 10]
['name=app', '# not a header', 'port=80']
```

- `takewhile(pred, it)`: yields items while `pred(item)` is true, and **stops for good** at the first false one.
- `dropwhile(pred, it)`: skips items while `pred(item)` is true; from the first false one onwards it yields **everything**, without testing again.
- `filter(pred, it)` is different: it tests **every** item and never stops early. Compare the three outputs above: `8` and `10` are even, but `takewhile` never reaches them.

`dropwhile` is perfect for "skip the header": the comment line `# not a header` in the middle is kept, because after the first non-comment, `dropwhile` stops checking.

`takewhile` is the safe way to cut an **infinite** iterator at a condition: `takewhile(lambda f: f < 1000, fibonacci())` is finite.

One trap: to know it must stop, `takewhile` has to **read** the first failing item. That item is then gone from a shared iterator (like `take` in section 7.3):

```python
from itertools import takewhile

it = iter([1, 2, 3, 10, 4, 5])
small = list(takewhile(lambda n: n < 5, it))
print(small)
print(list(it))
```

```text
$ python it_takewhile_trap.py
[1, 2, 3]
[4, 5]
```

The `10` was read, tested, and lost.

### 12.4 `zip_longest`, and `zip(strict=True)`

`zip` stops at the shortest input, silently dropping the extra items. Sometimes that hides a bug. Two tools help:

```python
from itertools import zip_longest

names = ["asha", "ravi", "meena"]
marks = [80, 65]
print(list(zip(names, marks)))
print(list(zip_longest(names, marks)))
print(list(zip_longest(names, marks, fillvalue=0)))
print(list(zip(names, marks, strict=False)))
```

```text
$ python it_zipl.py
[('asha', 80), ('ravi', 65)]
[('asha', 80), ('ravi', 65), ('meena', None)]
[('asha', 80), ('ravi', 65), ('meena', 0)]
[('asha', 80), ('ravi', 65)]
```

- `zip_longest` goes to the **longest** input and fills the gaps with `fillvalue` (default `None`).
- `zip(..., strict=True)` (a built-in option, not from itertools) raises an error when the lengths differ. Use it when different lengths would mean a bug:

```python
names = ["asha", "ravi", "meena"]
marks = [80, 65]
print(list(zip(names, marks, strict=True)))
```

```text
$ python it_zipstrict.py
Traceback (most recent call last):
  File "/home/you/project/it_zipstrict.py", line 3, in <module>
    print(list(zip(names, marks, strict=True)))
          ~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ValueError: zip() argument 2 is shorter than argument 1
```

Never use `zip_longest` with an infinite iterator: it goes to the longest, which is forever.

### 12.5 `compress`, `filterfalse`, `starmap`

Three smaller tools, each the "other half" of something you know.

`compress(data, selectors)` keeps the items of `data` whose matching selector is truthy. It is a filter driven by a second sequence instead of a function:

```python
from itertools import compress

names = ["asha", "ravi", "meena", "dev"]
present = [1, 0, 1, 1]
print(list(compress(names, present)))

marks = [80, 35, 60, 20]
print(list(compress(names, (m >= 40 for m in marks))))
```

```text
$ python it_compress.py
['asha', 'meena', 'dev']
['asha', 'meena']
```

`filterfalse(pred, it)` is the opposite of `filter`: it keeps the items where `pred` is **false**. With `None` as the predicate, `filter` keeps truthy items and `filterfalse` keeps falsy ones.

```python
from itertools import filterfalse

nums = range(10)
print(list(filter(lambda n: n % 3 == 0, nums)))
print(list(filterfalse(lambda n: n % 3 == 0, nums)))
words = ["ok", "", "yes", "", "no"]
print(list(filter(None, words)))
print(list(filterfalse(None, words)))
```

```text
$ python it_filterfalse.py
[0, 3, 6, 9]
[1, 2, 4, 5, 7, 8]
['ok', 'yes', 'no']
['', '']
```

`starmap(func, pairs)` is `map` for data that is already grouped into tuples. `map(f, xs, ys)` takes the arguments from parallel iterables; `starmap(f, rows)` unpacks each row with `*`, calling `f(*row)`:

```python
from itertools import starmap

pairs = [(2, 5), (3, 2), (10, 3)]
print(list(starmap(pow, pairs)))
print(list(map(pow, [2, 3, 10], [5, 2, 3])))

rects = [(3, 4), (5, 5), (2, 9)]
print(list(starmap(lambda w, h: w * h, rects)))
```

```text
$ python it_starmap.py
[32, 9, 1000]
[32, 9, 1000]
[12, 25, 18]
```

### 12.6 Predict the output

```python
from itertools import islice, count, chain, accumulate

print(list(islice(count(5, 5), 4)))
print(list(chain("ab", range(2))))
print(list(accumulate([1, 2, 3, 4])))
print(list(islice("python", 1, None, 2)))
```

(`accumulate` is in the next section; guess from its name: a running total.)

<details><summary>Answer</summary>

```text
[5, 10, 15, 20]
['a', 'b', 0, 1]
[1, 3, 6, 10]
['y', 'h', 'n']
```

`count(5, 5)` counts in fives from 5. `chain` mixes a string and a range. `accumulate` gives running totals. `islice("python", 1, None, 2)` is like `"python"[1::2]`.

</details>

## 13. itertools 3: running totals, pairs and batches

### 13.1 `accumulate`: running results

`accumulate(it)` yields running totals: the first item, then first + second, and so on. It is the `running_total` generator from section 5.4, built in. With a second argument you choose the combining function instead of `+`.

```python
from itertools import accumulate

sales = [5, 3, 10, 2]
print(list(accumulate(sales)))
print(list(accumulate(sales, initial=100)))
print(list(accumulate(sales, max)))
print(list(accumulate(sales, lambda a, b: a * b)))
print(list(accumulate([3, 1, 4, 1, 5], min)))
balance = list(accumulate([+500, -200, -400, +100], initial=1000))
print(balance)
```

```text
$ python it_accum.py
[5, 8, 18, 20]
[100, 105, 108, 118, 120]
[5, 5, 10, 10]
[5, 15, 150, 300]
[3, 1, 1, 1, 1]
[1000, 1500, 1300, 900, 1000]
```

- With `max`: "the biggest so far" at each step. With `min`: "the smallest so far".
- With a two-argument `lambda`: any running combination (here a running product).
- `initial=100` puts a starting value in front, so the output is **one item longer** than the input. The bank balance example uses it: start with 1000, then apply each transaction, and you get the balance after every step.

`accumulate` replaces a very common loop pattern ("keep a running value and append it to a list").

### 13.2 `pairwise`: neighbours

`pairwise(it)` yields each item together with the next one: `(a, b), (b, c), (c, d), ...`. It is the clean answer to the old index loop `for i in range(len(x) - 1): x[i], x[i + 1]`.

```python
from itertools import pairwise

print(list(pairwise([1, 4, 9, 16])))
print(list(pairwise("abc")))
print(list(pairwise([7])))

temps = [21, 23, 22, 25, 25, 19]
changes = [b - a for a, b in pairwise(temps)]
print(changes)
print(all(a <= b for a, b in pairwise([1, 2, 2, 5])))
```

```text
$ python it_pairwise.py
[(1, 4), (4, 9), (9, 16)]
[('a', 'b'), ('b', 'c')]
[]
[2, -1, 3, 0, -6]
True
```

- `n` items give `n - 1` pairs. One item gives no pairs, and no error.
- Day-to-day changes are `b - a` for each pair.
- "Is it sorted?" is `all(a <= b for a, b in pairwise(xs))`, and it stops at the first pair out of order.

Unlike the index loop, `pairwise` works on **any** iterable, including generators that have no indexes.

### 13.3 `batched`: fixed-size chunks

`batched(it, n)` (Python 3.12 and newer) cuts a stream into tuples of `n` items. The last batch may be shorter.

```python
from itertools import batched

print(list(batched("abcdefg", 3)))
print(list(batched(range(10), 4)))

ids = range(1, 8)
for batch in batched(ids, 3):
    print("saving batch", batch)
```

```text
$ python it_batched.py
[('a', 'b', 'c'), ('d', 'e', 'f'), ('g',)]
[(0, 1, 2, 3), (4, 5, 6, 7), (8, 9)]
saving batch (1, 2, 3)
saving batch (4, 5, 6)
saving batch (7,)
```

Batching is everywhere in real programs: save 1000 rows to a database at a time, send 50 emails per request, process a big file in pieces. With `strict=True` (Python 3.13+), a short last batch is an error instead:

```python
from itertools import batched

print(list(batched("abcdefg", 3, strict=True)))
```

```text
$ python it_batched_strict.py
Traceback (most recent call last):
  File "/home/you/project/it_batched_strict.py", line 3, in <module>
    print(list(batched("abcdefg", 3, strict=True)))
          ~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ValueError: batched(): incomplete batch
```

Section 17.2 shows how to write batching yourself, which is a classic exercise (and the way to do it on older Python).

## 14. `groupby` in depth

`groupby` is the most useful tool in `itertools`, and the one with the most traps. It gets its own section.

### 14.1 What it does: runs of equal items

`groupby(it)` walks through the items and yields one pair `(key, group)` for each **run** of equal, **neighbouring** items. `group` is itself an iterator over the items of that run.

```python
from itertools import groupby

for key, group in groupby("aaabccdaa"):
    print(key, list(group))
```

```text
$ python gb1.py
a ['a', 'a', 'a']
b ['b']
c ['c', 'c']
d ['d']
a ['a', 'a']
```

Look at the last line: `a` appears **twice** as a key. `groupby` does **not** collect all the `a`s in the string. It only groups items that are next to each other. When the item changes, a new group starts. This is very different from SQL's `GROUP BY` or from building a dict of lists, and it is the first trap.

Why does it work like this? Because it is lazy. To collect all the `a`s, it would have to read the whole input before yielding anything, and keep it all in memory. Grouping only neighbours needs to look at one item at a time.

### 14.2 Grouping by a key function

With `key=`, items are grouped by `key(item)` instead of the item itself, just like `sorted(..., key=...)` from core.05. The yielded key is the key value; the group contains the original items.

```python
from itertools import groupby

words = ["apple", "avocado", "banana", "blueberry", "cherry", "apricot"]
for letter, group in groupby(words, key=lambda w: w[0]):
    print(letter, list(group))
```

```text
$ python gb2.py
a ['apple', 'avocado']
b ['banana', 'blueberry']
c ['cherry']
a ['apricot']
```

Again two `a` groups, because `apricot` is not next to the other `a` words.

### 14.3 Rule 1: sort by the same key first

If you want **one group per key**, sort the data by the **same key** first. Sorting puts equal keys next to each other, and then neighbour-grouping is complete grouping.

```python
from itertools import groupby

words = ["apple", "avocado", "banana", "blueberry", "cherry", "apricot"]
first_letter = lambda w: w[0]
for letter, group in groupby(sorted(words, key=first_letter), key=first_letter):
    print(letter, list(group))
```

```text
$ python gb3.py
a ['apple', 'avocado', 'apricot']
b ['banana', 'blueberry']
c ['cherry']
```

Use the same key function in both places. Sorting by one thing and grouping by another gives broken groups. A neat way to make sure: store the key function in a variable, as above. (Python style guides usually prefer `def` to assigning a lambda to a name; here the variable is just to show the same function is used twice.)

Two notes:

- Sorting reads all the data into a list, so it is no longer lazy. That is the price of complete grouping. When the data is **already** in order (a log sorted by time, grouped by date), you can skip the sort and stay lazy. You will use that in the project.
- If you only need counts or lists per key and the data is not sorted, a plain dict (`counts[key] = counts.get(key, 0) + 1`) is often simpler than sort + `groupby`.

### 14.4 Rule 2: use each group before moving on

This is the trap that catches even experienced programmers. Collect the groups in a dict, use them afterwards:

```python
from itertools import groupby

words = ["apple", "avocado", "banana", "blueberry", "cherry"]
groups = {}
for letter, group in groupby(words, key=lambda w: w[0]):
    groups[letter] = group

for letter, group in groups.items():
    print(letter, list(group))
```

```text
$ python gb4.py
a []
b []
c []
```

Every group is empty. Why? `groupby` has only **one** iterator over the input. Each `group` is not a list; it is a small window that reads **from that shared iterator**. When the outer loop asks for the next key, `groupby` must move the shared iterator past the current group to find where the next key starts. The old group's window is then pointing at data that has already gone by, so the old group is **invalidated** and yields nothing.

The fix: turn each group into a list **inside** the loop, while it is still current.

```python
from itertools import groupby

words = ["apple", "avocado", "banana", "blueberry", "cherry"]
groups = {}
for letter, group in groupby(words, key=lambda w: w[0]):
    groups[letter] = list(group)

print(groups)
```

```text
$ python gb5.py
{'a': ['apple', 'avocado'], 'b': ['banana', 'blueberry'], 'c': ['cherry']}
```

Here is the same trap in its smallest form, with `next` instead of a loop:

```python
from itertools import groupby

g = groupby("aabbb")
key1, group1 = next(g)
key2, group2 = next(g)
print(key1, list(group1))
print(key2, list(group2))
```

```text
$ python gb7.py
a []
b ['b', 'b', 'b']
```

Asking for the second group moved past the first one. `group1` is dead.

### 14.5 Classic uses

Many "consecutive" problems become one line with `groupby`:

```python
from itertools import groupby

def run_length(text):
    return "".join(f"{ch}{len(list(g))}" for ch, g in groupby(text))


print(run_length("aaabccdddd"))

readings = [0, 0, 1, 1, 1, 0, 1, 1, 0, 0, 0]
longest_on = max(len(list(g)) for k, g in groupby(readings) if k == 1)
print("longest run of 1s:", longest_on)

lines = ["ERROR a", "ERROR b", "INFO c", "ERROR d"]
for level, group in groupby(lines, key=lambda s: s.split()[0]):
    print(level, sum(1 for _ in group))
```

```text
$ python gb6.py
a3b1c2d4
longest run of 1s: 3
ERROR 2
INFO 1
ERROR 1
```

- **Run-length encoding**: each run becomes "character + length".
- **Longest streak**: the longest run of 1s (a sensor that was "on" longest, the longest winning streak).
- **Bursts**: how many errors came in a row before something else happened.

`len(list(g))` and `sum(1 for _ in g)` both count a group. The second one does not build a list, which matters only for very long groups. Each one uses the group **immediately**, so Rule 2 is respected.

### 14.6 Predict the output

```python
from itertools import groupby

data = [1, 1, 2, 2, 2, 1, 3, 3]
print([(k, len(list(g))) for k, g in groupby(data)])
print([(k, len(list(g))) for k, g in groupby(sorted(data))])
```

<details><summary>Answer</summary>

```text
[(1, 2), (2, 3), (1, 1), (3, 2)]
[(1, 3), (2, 3), (3, 2)]
```

Unsorted, the lone `1` in the middle forms its own run. After sorting, all three `1`s are neighbours. Each group is used (by `len(list(g))`) before the comprehension asks for the next one, so nothing is lost.

</details>

## 15. itertools 4: combinatorics

The last family answers "in how many ways can I pick or arrange things?" and, more usefully, **lists** those ways lazily. They replace nested loops whose depth depends on the data.

### 15.1 The four tools

```python
from itertools import product, permutations, combinations, combinations_with_replacement

print(list(product("AB", [1, 2])))
print(list(product([0, 1], repeat=3)))
print(list(permutations("ABC")))
print(list(permutations("ABC", 2)))
print(list(combinations("ABCD", 2)))
print(list(combinations_with_replacement("AB", 2)))
```

```text
$ python comb1.py
[('A', 1), ('A', 2), ('B', 1), ('B', 2)]
[(0, 0, 0), (0, 0, 1), (0, 1, 0), (0, 1, 1), (1, 0, 0), (1, 0, 1), (1, 1, 0), (1, 1, 1)]
[('A', 'B', 'C'), ('A', 'C', 'B'), ('B', 'A', 'C'), ('B', 'C', 'A'), ('C', 'A', 'B'), ('C', 'B', 'A')]
[('A', 'B'), ('A', 'C'), ('B', 'A'), ('B', 'C'), ('C', 'A'), ('C', 'B')]
[('A', 'B'), ('A', 'C'), ('A', 'D'), ('B', 'C'), ('B', 'D'), ('C', 'D')]
[('A', 'A'), ('A', 'B'), ('B', 'B')]
```

| tool | picks | order matters? | same item twice? | example question |
|---|---|---|---|---|
| `product(a, b, ...)` | one from **each** input | yes | yes (separate inputs) | every size with every colour |
| `product(a, repeat=k)` | `k` from the same input | yes | yes | every 4-digit PIN |
| `permutations(a, k)` | `k` different positions | **yes** | no | gold, silver, bronze winners |
| `combinations(a, k)` | `k` different positions | **no** | no | a team of 2 from 4 people |
| `combinations_with_replacement(a, k)` | `k` | no | yes | 2 scoops from 2 flavours |

The output is always in a predictable order, based on the **positions** of the input items: `combinations("ABCD", 2)` starts with `A` paired with everything after it, then `B` with everything after it, and so on. That is why `('B', 'A')` never appears in `combinations`: it is the same team as `('A', 'B')`.

### 15.2 `product` replaces nested loops

`product(sizes, colours)` is exactly two nested `for` loops, flattened into one:

```python
from itertools import product

sizes = ["S", "M"]
colours = ["red", "blue"]

for size in sizes:
    for colour in colours:
        print(size, colour)
print("---")
for size, colour in product(sizes, colours):
    print(size, colour)
```

```text
$ python comb2.py
S red
S blue
M red
M blue
---
S red
S blue
M red
M blue
```

The rightmost input changes fastest, like the inner loop (or like the last digit of a counter). Two benefits over nested loops:

1. **The depth can depend on data.** `product([0, 1], repeat=n)` gives all `n`-bit patterns for any `n`. With loops you would need `n` nested `for`s, and you cannot write a variable number of nested loops.
2. **`break` leaves everything.** With nested loops, `break` leaves only the inner loop:

```python
for i in range(3):
    for j in range(3):
        if i == 1 and j == 1:
            print("found at", (i, j))
            break
    print("finished row", i)
```

```text
$ python comb7.py
finished row 0
found at (1, 1)
finished row 1
finished row 2
```

```python
from itertools import product

for i, j in product(range(3), range(3)):
    if i == 1 and j == 1:
        print("found the centre at", (i, j))
        break
```

```text
$ python comb6.py
found the centre at (1, 1)
```

With `product` there is only one loop, so one `break` really stops the search.

### 15.3 A real use: choosing items for a budget

You have item prices and a budget of exactly 100. Which pairs add up to 100? Which groups of any size?

```python
from itertools import combinations

prices = [30, 70, 45, 25, 55]
budget = 100
for a, b in combinations(prices, 2):
    if a + b == budget:
        print(a, "+", b)

for size in range(1, len(prices) + 1):
    for combo in combinations(prices, size):
        if sum(combo) == budget:
            print("exactly 100:", combo)
```

```text
$ python comb4.py
30 + 70
45 + 55
exactly 100: (30, 70)
exactly 100: (45, 55)
exactly 100: (30, 45, 25)
```

`combinations(prices, 2)` never pairs an item with itself and never gives the same pair twice, so you do not need the usual `for i ... for j in range(i + 1, ...)` index trick.

### 15.4 These grow very fast

The number of results explodes as the input grows. The `math` module has functions that **count** without listing: `math.perm(n, k)` for permutations, `math.comb(n, k)` for combinations, `math.factorial(n)` for `n!`.

```python
from itertools import product, permutations, combinations
import math

print(len(list(product(range(10), repeat=4))), 10 ** 4)
print(len(list(permutations(range(5), 3))), math.perm(5, 3))
print(len(list(combinations(range(5), 3))), math.comb(5, 3))
print(math.factorial(10), math.factorial(20))
```

```text
$ python comb3.py
10000 10000
60 60
10 10
3628800 2432902008176640000
```

All permutations of 20 items: about 2.4 billion billion. Because these tools are lazy, **creating** `permutations(range(20))` is instant and costs nothing. Calling `list()` on it would never finish. Loop over them and `break` as soon as you find what you need, or check the count with `math` first. When the count is huge, trying every possibility (brute force) is the wrong approach; the DSA modules teach smarter ones.

### 15.5 Duplicates in, duplicates out

These tools work on **positions**, not values. If the input has equal values, you get equal-looking results:

```python
from itertools import permutations

print(list(permutations([1, 1, 2])))
print(sorted(set(permutations([1, 1, 2]))))
```

```text
$ python comb5.py
[(1, 1, 2), (1, 2, 1), (1, 1, 2), (1, 2, 1), (2, 1, 1), (2, 1, 1)]
[(1, 1, 2), (1, 2, 1), (2, 1, 1)]
```

If you want distinct arrangements, put the results in a `set` (fine for small inputs).

### 15.6 Predict the output

```python
from itertools import combinations, permutations, product

print(len(list(combinations(range(6), 2))))
print(len(list(permutations(range(6), 2))))
print(len(list(product(range(6), repeat=2))))
```

<details><summary>Answer</summary>

```text
15
30
36
```

Pairs from 6 items: `6 * 5 = 30` ordered pairs without repeats (permutations). Each unordered pair appears twice in that, so combinations give `30 / 2 = 15`. `product` also allows `(0, 0)`, `(1, 1)` and so on: `6 * 6 = 36`.

</details>

## 16. `tee`, and sharing one iterator

### 16.1 The problem: two passes over a one-pass iterator

```python
def readings():
    yield 5
    yield 9
    yield 2


r = readings()
smallest = min(r)
largest = max(r)
print(smallest, largest)
```

```text
$ python tee3.py
Traceback (most recent call last):
  File "/home/you/project/tee3.py", line 9, in <module>
    largest = max(r)
ValueError: max() iterable argument is empty
```

`min` used up `r`; `max` got nothing. You already know the cause (section 3.2). There are several ways out.

### 16.2 The ways out

```python
from itertools import tee


def readings():
    yield 5
    yield 9
    yield 2


one, two = tee(readings())
print(min(one), max(two))

values = list(readings())
print(min(values), max(values))
```

```text
$ python tee4.py
2 9
2 9
```

1. **`tee(it)`** splits one iterator into two (or `tee(it, n)` for `n`) **independent** iterators. Each sees all the items.
2. **Make a list** once and use it twice. Simple and clear.
3. **Call the generator function again** (`readings()` twice). Only possible when you have the function, and the source can be read again.
4. (A fourth, best for big data: do **both jobs in one pass**: a single loop that tracks the smallest and largest at the same time.)

### 16.3 How `tee` works, and its cost

`tee` is not magic. It cannot rewind the original. Behind the scenes it reads from the original once and keeps a **buffer** of the items that one copy has seen and the other has not yet. That means:

- If both copies move forward at roughly the same speed (like `pairwise`: one copy is one step ahead), the buffer stays tiny. This is what `tee` is good for.
- If one copy is consumed **completely** before the other starts (like `min(one)` then `max(two)` above), the buffer holds **every item**. Then `tee` uses as much memory as a list, and is slower. In that case just use `list()`.

So the rule from the Python docs is: **if one copy will be used up before the other starts, use a list instead of `tee`.**

### 16.4 Do not touch the original after `tee`

After `tee`, use only the copies. If you advance the original iterator yourself, the copies miss those items, because `tee` never saw them:

```python
from itertools import tee

numbers = iter([10, 20, 30, 40])
first, second = tee(numbers)
print(next(numbers))
print(list(first))
print(list(second))
```

```text
$ python tee2.py
10
[20, 30, 40]
[20, 30, 40]
```

The `10` was taken straight from the original, behind `tee`'s back, so neither copy has it. Treat the original as handed over: forget its name after calling `tee`.

## 17. Useful patterns

This section collects small iterator patterns you will use again and again, in the problems and in real code.

### 17.1 `iter(callable, sentinel)`: loop until a special value

`iter()` has a second form that most people never learn. `iter(func, sentinel)` makes an iterator that calls `func()` (with no arguments) again and again, yields each result, and **stops when the result equals `sentinel`**. The sentinel itself is not yielded.

The classic use: read input lines until an empty one.

```python
names = []
for line in iter(input, ""):
    names.append(line.strip().title())
print(names)
```

```text
$ printf "asha\nravi kumar\n\nignored\n" | python pat_input.py
['Asha', 'Ravi Kumar']
```

(`printf ... |` feeds those lines to the program as if typed. The empty line stops the loop, so `ignored` is never read.)

Compare with the `while True` version you would write otherwise:

```python
names = []
while True:
    line = input()
    if line == "":
        break
    names.append(line.strip().title())
```

Same job, more lines. The `iter` form says the stopping rule in one place.

Any function with no arguments works. Here a command source stops at `"quit"`:

```python
commands = iter(["add 5", "add 7", "quit", "add 100"])


def read_command():
    return next(commands)


for cmd in iter(read_command, "quit"):
    print("running:", cmd)
print("stopped at the sentinel")
```

```text
$ python pat_sent1.py
running: add 5
running: add 7
stopped at the sentinel
```

The other classic use is reading fixed-size **chunks** until the data runs out. Real files come in core.12. Until then, `io.StringIO` gives a fake text file in memory: `stream.read(4)` returns the next 4 characters, and `""` when nothing is left.

```python
import io

stream = io.StringIO("abcdefghij")
for chunk in iter(lambda: stream.read(4), ""):
    print(repr(chunk))
```

```text
$ python pat_sent2.py
'abcd'
'efgh'
'ij'
```

`stream.read` needs an argument, but `iter` calls its function with **none**, so we wrap the call in a `lambda` that takes no arguments. This exact line, with a real file, is how programs read huge files in pieces.

### 17.2 Chunking by hand, and a nasty bug

Before `batched` existed, everyone wrote this generator. It is still a great exercise:

```python
def chunks(items, size):
    batch = []
    for item in items:
        batch.append(item)
        if len(batch) == size:
            yield batch
            batch = []
    if batch:
        yield batch


print(list(chunks(range(1, 8), 3)))
print(list(chunks([], 3)))
print(list(chunks("abcdef", 2)))
```

```text
$ python pat_chunk.py
[[1, 2, 3], [4, 5, 6], [7]]
[]
[['a', 'b'], ['c', 'd'], ['e', 'f']]
```

Two details matter: the final `if batch:` yields the short last chunk (and yields nothing for empty input); and after yielding, `batch = []` makes a **new** list. Look what happens with `batch.clear()` instead:

```python
def chunks_bad(items, size):
    batch = []
    for item in items:
        batch.append(item)
        if len(batch) == size:
            yield batch
            batch.clear()
    if batch:
        yield batch


print(list(chunks_bad(range(1, 8), 3)))
```

```text
$ python pat_chunk2.py
[[7], [7], [7]]
```

All three chunks are the same list object (aliasing, from core.05). The caller received a reference to `batch`, then the generator cleared and refilled that same list. By the time `list()` prints, all three references show its final state. **Never yield a mutable object and then keep changing it.** Yield a new object each time (or a tuple, which cannot change).

### 17.3 Sliding window

A window of size `n` moving one step at a time: for `[1, 2, 3, 4, 5]` and `n = 3`, the windows are `(1, 2, 3), (2, 3, 4), (3, 4, 5)`. `pairwise` is the special case `n = 2`. A lazy version for any `n`:

```python
from itertools import islice


def windows(items, size):
    it = iter(items)
    window = tuple(islice(it, size))
    if len(window) == size:
        yield window
    for item in it:
        window = window[1:] + (item,)
        yield window


print(list(windows([1, 2, 3, 4, 5], 3)))
print(list(windows("ab", 3)))
temps = [20, 22, 27, 25, 24, 30]
print([round(sum(w) / 3, 1) for w in windows(temps, 3)])
```

```text
$ python pat_window.py
[(1, 2, 3), (2, 3, 4), (3, 4, 5)]
[]
[23.0, 24.7, 25.3, 26.3]
```

How it works: `islice` fills the first window. Then for each new item, drop the oldest (`window[1:]`) and add the new one at the end. Because the window is a tuple, every yielded window is a **new** object, so the aliasing bug from 17.2 cannot happen. The last line is a **moving average**, used for smoothing noisy data such as temperatures or stock prices.

(For large windows, building a new tuple each step costs `O(n)`. A later module introduces `collections.deque`, which does this more efficiently.)

### 17.4 The first match, or a default

"Find the first item that matches" is `next()` on a generator expression, with a default for "none found":

```python
scores = [35, 48, 72, 91, 55]
first_pass = next((s for s in scores if s >= 50), None)
print(first_pass)
first_hundred = next((s for s in scores if s == 100), None)
print(first_hundred)
```

```text
$ python pat_first.py
72
None
```

It stops at the first match, like `any`, but gives you the item, not just `True`. Here the generator expression needs its own brackets, because `next` has a second argument.

### 17.5 Peeking at the first item

Sometimes you need to look at the first item before deciding what to do, for example to detect empty input. An iterator has no `len`, but `next(it, None)` tells you:

```python
def describe(iterable):
    it = iter(iterable)
    first = next(it, None)
    if first is None:
        return "empty"
    rest = sum(1 for _ in it)
    return f"starts with {first!r}, then {rest} more"


print(describe([]))
print(describe(x * x for x in range(5)))
print(describe("hello"))
```

```text
$ python pat_peek.py
empty
starts with 0, then 4 more
starts with 'h', then 4 more
```

The first item has been taken from the iterator, so you must use it yourself (here `first`) and continue with `it` for the rest. If you need to pass the whole stream on, put the first item back in front: `chain([first], it)`. (If `None` could be a real item, use a different default to compare against.)

### 17.6 Lazy de-duplication

A `set` remembers what has been seen; the generator yields each item the first time only, **keeping the original order**:

```python
def unique(items):
    seen = set()
    for item in items:
        if item not in seen:
            seen.add(item)
            yield item


print(list(unique([3, 1, 3, 2, 1, 4])))
print("".join(unique("mississippi")))
```

```text
$ python pat_dedupe.py
[3, 1, 2, 4]
misp
```

`set(items)` would also remove duplicates, but it loses the order and is not lazy. Note the memory: the `seen` set grows with the number of **distinct** items, not with the total length.

### 17.7 Built-ins that return iterators, and those that return lists

Know which is which, because the iterators are consumed once:

| returns an iterator (lazy, one pass) | returns a new list or other value (eager) |
|---|---|
| `iter`, `map`, `filter`, `zip`, `enumerate`, `reversed` | `sorted` (always a list) |
| generator functions and expressions | `list`, `tuple`, `set`, `dict` |
| everything in `itertools` | `sum`, `min`, `max`, `any`, `all`, `len` (a value) |
| `dict.items()`/`.keys()`/`.values()` are *views*: reusable, not iterators | `str.join` (a string) |

`range` and the dict views are reusable lazy objects, not iterators: you can loop over them many times.

## 18. Project: a lazy log-file pipeline

Time to put the whole chapter together. You will build a small log analyser as a pipeline of generators and `itertools` tools. It must work on a 14-line sample **and** on a million-line stream, without changing the code, and without the memory growing with the size of the log.

Real files come in core.12. Here the log is a **list of strings** (for the sample) or a **generator of strings** (for the big test). Our functions accept any `Iterable[str]`, so when you learn files, you will pass a file object in exactly the same place: a file is also an iterable of lines.

### 18.1 The data

Each good line has a date, a time, a level, and `key=value` fields. Real logs are messy, so ours has comments, blank lines and one garbage line.

```python
LOG = [
    "# app log, version 3",
    "2026-10-01 09:00:01 INFO  user=asha  action=login   ms=12",
    "2026-10-01 09:00:05 ERROR user=ravi  action=upload  ms=2048",
    "",
    "2026-10-01 09:01:10 WARN  user=asha  action=upload  ms=950",
    "2026-10-01 09:02:00 ERROR user=asha  action=delete  ms=31",
    "2026-10-01 09:02:07 ERROR user=meena action=upload  ms=1500",
    "this line is garbage",
    "2026-10-02 10:15:00 INFO  user=ravi  action=login   ms=15",
    "2026-10-02 10:16:42 INFO  user=ravi  action=search  ms=220",
    "2026-10-02 10:20:00 ERROR user=ravi  action=search  ms=3100",
    "   ",
    "2026-10-03 08:00:00 INFO  user=meena action=login   ms=9",
    "2026-10-03 08:05:30 WARN  user=meena action=export  ms=780",
]
```

`ms` is how many milliseconds the request took. We want to answer:

1. How many lines of each level?
2. How many errors per day?
3. The first few slow requests.
4. Which users had errors, and how many?
5. Did errors come in bursts (two in a row)?

Plan the stages before writing code:

```text
lines  ->  clean_lines  ->  parse  ->  (filter / group / count)  ->  answer
 str          str           dict
```

### 18.2 Stage 1: clean the lines

```python
def clean_lines(lines):
    for line in lines:
        line = line.strip()
        if line and not line.startswith("#"):
            yield line


for line in clean_lines(LOG):
    print(line)
```

```text
$ python proj1.py
2026-10-01 09:00:01 INFO  user=asha  action=login   ms=12
2026-10-01 09:00:05 ERROR user=ravi  action=upload  ms=2048
2026-10-01 09:01:10 WARN  user=asha  action=upload  ms=950
2026-10-01 09:02:00 ERROR user=asha  action=delete  ms=31
2026-10-01 09:02:07 ERROR user=meena action=upload  ms=1500
this line is garbage
2026-10-02 10:15:00 INFO  user=ravi  action=login   ms=15
2026-10-02 10:16:42 INFO  user=ravi  action=search  ms=220
2026-10-02 10:20:00 ERROR user=ravi  action=search  ms=3100
2026-10-03 08:00:00 INFO  user=meena action=login   ms=9
2026-10-03 08:05:30 WARN  user=meena action=export  ms=780
```

The comment and the blank lines are gone. The garbage line is still here: it is not blank, so cleaning cannot know it is bad. Recognising bad lines is the parser's job.

### 18.3 Stage 2: parse, and keep the bad lines aside

We split the work: `parse_line` turns **one** line into a dict (a normal function, easy to test), and `parse` is the generator stage that calls it for every line. Bad lines must not crash the whole run (remember section 5.8: an exception escaping a generator ends it for good). So the `try/except` goes **inside** the generator, and bad lines are collected in a list the caller provides.

```python
def parse_line(line):
    date, time, level, *pairs = line.split()
    record = {"date": date, "time": time, "level": level}
    for pair in pairs:
        key, value = pair.split("=", 1)
        record[key] = value
    record["ms"] = int(record["ms"])
    return record


def parse(lines, bad):
    for line in lines:
        try:
            yield parse_line(line)
        except (ValueError, KeyError):
            bad.append(line)


bad = []
records = parse(clean_lines(LOG), bad)
first = next(records)
print(first)
print("bad lines so far:", bad)
rest = list(records)
print(len(rest), "more records")
print("bad lines:", bad)
```

```text
$ python proj2.py
{'date': '2026-10-01', 'time': '09:00:01', 'level': 'INFO', 'user': 'asha', 'action': 'login', 'ms': 12}
bad lines so far: []
9 more records
bad lines: ['this line is garbage']
```

Which exceptions can `parse_line` raise? Following core.07, we catch exactly those and nothing more. Testing three bad lines shows them:

```text
"2026-10-01 09:00 INFO user=asha"   ->  KeyError 'ms'            (no ms field)
"2026-10-01 09:00 INFO ms=abc"      ->  ValueError invalid literal for int() with base 10: 'abc'
"only two"                          ->  ValueError not enough values to unpack (expected at least 3, got 2)
```

(`"this line is garbage"` fails with a `ValueError` too: the word `garbage` has no `=` to split on.)

Look at `bad lines so far: []` in the output. After the first record, the garbage line has **not been reached yet**, because the pipeline is lazy. The `bad` list is complete only after the stream has been fully consumed. Keep that in mind: never read `bad` before you have finished with the records.

A small helper builds the whole front of the pipeline, so we do not repeat it:

```python
def records_from(lines, bad):
    return parse(clean_lines(lines), bad)
```

### 18.4 Stage 3: filters and the first questions

From here on, the file starts with the imports it needs: `from itertools import accumulate, groupby, islice, pairwise`.

```python
def with_level(records, level):
    return (r for r in records if r["level"] == level)


def slower_than(records, ms):
    for r in records:
        if r["ms"] > ms:
            yield r


bad = []
errors = with_level(records_from(LOG, bad), "ERROR")
for r in errors:
    print(r["date"], r["time"], r["user"], r["action"])

print("--- slow requests (over 1000 ms)")
for r in slower_than(records_from(LOG, []), 1000):
    print(r["user"], r["action"], r["ms"])

print("--- first two warnings or errors")
problems = (r for r in records_from(LOG, []) if r["level"] in ("WARN", "ERROR"))
for r in islice(problems, 2):
    print(r["time"], r["level"], r["user"])
```

```text
$ python proj3.py
2026-10-01 09:00:05 ravi upload
2026-10-01 09:02:00 asha delete
2026-10-01 09:02:07 meena upload
2026-10-02 10:20:00 ravi search
--- slow requests (over 1000 ms)
ravi upload 2048
meena upload 1500
ravi search 3100
--- first two warnings or errors
09:00:05 ERROR ravi
09:01:10 WARN asha
```

`with_level` is a normal function that **returns** a generator expression. From the outside, that is the same as a generator function: calling it gives an iterator. Use whichever reads better.

`islice(problems, 2)` stops the whole pipeline after two matches. The rest of the log is never cleaned or parsed. On a 20 GB log, that is the difference between a millisecond and ten minutes.

Each question builds a **new** pipeline with `records_from(LOG, ...)`. That is fine because `LOG` is a list and can be read many times. Section 18.7 shows what goes wrong when it is not.

### 18.5 Counting and grouping

Counting per level uses a dict, because the levels are mixed together. Errors per day use `groupby` **without sorting**, because the log is already in time order, so all lines of one day are neighbours. That keeps it lazy.

```python
counts = {}
for r in records_from(LOG, []):
    level = r["level"]
    counts[level] = counts.get(level, 0) + 1
print(counts)

print("--- per day")
for date, day in groupby(records_from(LOG, []), key=lambda r: r["date"]):
    day_records = list(day)
    errors = sum(1 for r in day_records if r["level"] == "ERROR")
    print(date, len(day_records), "records,", errors, "errors")
```

```text
$ python proj4.py
{'INFO': 4, 'ERROR': 4, 'WARN': 2}
--- per day
2026-10-01 5 records, 3 errors
2026-10-02 3 records, 1 errors
2026-10-03 2 records, 0 errors
```

We wrote `day_records = list(day)` because we use the group **twice** (`len` and the error count). A group is an iterator, so it would be empty the second time. A list of one day's records is fine; it is one day, not the whole log.

"Errors per user" is different: the users are **not** in order in the log. So we **sort** by user first, then group (Rule 1 from section 14.3). Sorting needs all error records in memory, but only the errors, which are few.

```python
errors = with_level(records_from(LOG, []), "ERROR")
by_user = sorted(errors, key=lambda r: r["user"])
for user, group in groupby(by_user, key=lambda r: r["user"]):
    print(user, sum(1 for _ in group))
```

```text
asha 1
meena 1
ravi 2
```

### 18.6 Running counts and bursts

`accumulate` gives a running count of errors, line by line. `pairwise` looks at neighbouring records to find two errors in a row.

```python
print("--- running count of errors")
flags = (1 if r["level"] == "ERROR" else 0 for r in records_from(LOG, []))
print(list(accumulate(flags)))

print("--- two errors in a row")
pairs = pairwise(records_from(LOG, []))
for a, b in pairs:
    if a["level"] == "ERROR" and b["level"] == "ERROR":
        print(a["time"], "and", b["time"])
```

```text
--- running count of errors
[0, 1, 1, 2, 3, 3, 3, 4, 4, 4]
--- two errors in a row
09:02:00 and 09:02:07
```

Check it by hand against the records: INFO (0), ERROR (1), WARN (1), ERROR (2), ERROR (3), INFO, INFO (3, 3), ERROR (4), INFO, WARN (4, 4). Ten records, ten running counts. The only two neighbouring errors are at 09:02:00 and 09:02:07. (The ERROR at 09:00:05 is followed by a WARN, so it is not a burst.)

Notice there are **no nested loops and no index arithmetic** anywhere. Each question is "a source, some stages, and a consumer".

### 18.7 The one-pass trap, on a real stream

Now let us put the questions in one `report` function and run it on a big **generated** log, as if it were a stream from a server. `fake_log` produces lines in the same format, lazily:

```python
def fake_log(days, per_day):
    for d in range(1, days + 1):
        for i in range(per_day):
            level = "ERROR" if i % 997 == 0 else "INFO"
            ms = (i * 37) % 4000
            yield f"2026-11-{d:02d} 12:00:00 {level} user=u{i % 50} action=view ms={ms}"


def count_levels(records):
    counts = {}
    for r in records:
        level = str(r["level"])
        counts[level] = counts.get(level, 0) + 1
    return counts


def report(lines):
    bad = []
    print("levels:", count_levels(records_from(lines, bad)))
    print("bad lines:", bad)

    print("errors per day:")
    for date, day in groupby(records_from(lines, []), key=lambda r: r["date"]):
        errors = sum(1 for r in day if r["level"] == "ERROR")
        print(" ", date, errors)

    print("first 3 slow requests:")
    for r in islice(slower_than(records_from(lines, []), 500), 3):
        print(" ", r["time"], r["user"], r["action"], r["ms"])

    print("errors in a row:")
    for a, b in pairwise(records_from(lines, [])):
        if a["level"] == b["level"] == "ERROR":
            print(" ", a["time"], "->", b["time"])
```

On the list it works:

```text
$ python logpipe.py      # report(LOG)
levels: {'INFO': 4, 'ERROR': 4, 'WARN': 2}
bad lines: ['this line is garbage']
errors per day:
  2026-10-01 3
  2026-10-02 1
  2026-10-03 0
first 3 slow requests:
  09:00:05 ravi upload 2048
  09:01:10 asha upload 950
  09:02:07 meena upload 1500
errors in a row:
  09:02:00 -> 09:02:07
```

On the stream, three of the four answers are **empty**, with no error:

```text
$ python logpipe.py      # report(fake_log(3, 1000))
levels: {'ERROR': 6, 'INFO': 2994}
bad lines: []
errors per day:
first 3 slow requests:
errors in a row:
```

You can explain this now. `report` builds four pipelines from `lines`. When `lines` is a list, each `records_from(lines, ...)` gets a fresh iterator. When `lines` is a generator, all four pipelines share **one** iterator. The first question (`count_levels`) consumed it completely; the other three got an exhausted iterator. This is "consumed once" again, and it is the most common real bug with generators: a function that silently works on lists and silently fails on streams.

Three honest fixes:

1. Make `lines` a list first: `report(list(fake_log(...)))`. Correct, but the whole log is in memory again, which defeats the purpose.
2. Read the source again for each question (for a file: open it again). Correct and lazy, but four passes over the data.
3. Answer **all** the questions in **one pass**. Lazy and fastest. This is what real log tools do.

### 18.8 One pass over a big stream

Here is a one-pass daily summary: for each day, the number of records, errors, and very slow requests (over 3000 ms). Everything happens inside a single `groupby` over a single pipeline.

```python
def daily_summary(lines):
    bad = []
    records = records_from(lines, bad)
    for date, day in groupby(records, key=lambda r: r["date"]):
        total = errors = slow = 0
        for r in day:
            total += 1
            if r["level"] == "ERROR":
                errors += 1
            if r["ms"] > 3000:
                slow += 1
        print(date, total, "records,", errors, "errors,", slow, "slow")
    print("bad lines:", len(bad))


daily_summary(fake_log(5, 200_000))
```

```text
$ python logpipe.py      # daily_summary(fake_log(5, 200_000))
2026-11-01 200000 records, 201 errors, 49950 slow
2026-11-02 200000 records, 201 errors, 49950 slow
2026-11-03 200000 records, 201 errors, 49950 slow
2026-11-04 200000 records, 201 errors, 49950 slow
2026-11-05 200000 records, 201 errors, 49950 slow
bad lines: 0
```

One million lines. On my machine it took about 1.3 seconds, and the **peak memory of the whole process was about 10 MB** (measured with `/usr/bin/time`; your numbers will differ). Change `fake_log(5, 200_000)` to `fake_log(500, 200_000)`, a hundred million lines, and it takes longer, but the memory stays the same. That is the first outcome of this module, achieved.

Note that `bad` is printed **after** the loop, when the stream is finished (section 18.3).

### 18.9 The finished program, with type hints

Finally, add the type hints from core.09. Two new details:

- `Record = dict[str, str | int]` gives a **name** to a type that we use many times. It is just a variable holding a type; mypy understands it. A record's values are strings, except `ms`, which is an int.
- Because a value can be `str | int`, mypy will not let us write `r["ms"] > ms` directly: comparing a `str` with an `int` would crash. We narrow it with `isinstance` (core.09).

Here is the top of the finished `logpipe.py`, with the stages that changed:

```python
from collections.abc import Iterable, Iterator
from itertools import groupby, islice, pairwise

LOG = [ ... ]          # the 14 lines from section 18.1

Record = dict[str, str | int]


def clean_lines(lines: Iterable[str]) -> Iterator[str]:
    for line in lines:
        line = line.strip()
        if line and not line.startswith("#"):
            yield line


def parse_line(line: str) -> Record:
    date, time, level, *pairs = line.split()
    record: Record = {"date": date, "time": time, "level": level}
    for pair in pairs:
        key, value = pair.split("=", 1)
        record[key] = value
    record["ms"] = int(record["ms"])
    return record


def parse(lines: Iterable[str], bad: list[str]) -> Iterator[Record]:
    for line in lines:
        try:
            yield parse_line(line)
        except (ValueError, KeyError):
            bad.append(line)


def slower_than(records: Iterable[Record], ms: int) -> Iterator[Record]:
    for r in records:
        duration = r["ms"]
        if isinstance(duration, int) and duration > ms:
            yield r
```

The other functions get their hints in the same way:

```python
def with_level(records: Iterable[Record], level: str) -> Iterator[Record]: ...
def records_from(lines: Iterable[str], bad: list[str]) -> Iterator[Record]: ...
def count_levels(records: Iterable[Record]) -> dict[str, int]: ...
def report(lines: Iterable[str]) -> None: ...
def fake_log(days: int, per_day: int) -> Iterator[str]: ...
def daily_summary(lines: Iterable[str]) -> None: ...
```

Inside them, write `counts: dict[str, int] = {}` and `bad: list[str] = []` for the empty collections, and in `daily_summary` narrow `r["ms"]` with `isinstance` exactly as in `slower_than`. Then the file ends with:

```python
report(LOG)
print("---")
daily_summary(fake_log(5, 200_000))
```

Running it prints exactly the output of sections 18.7 (the `report(LOG)` part) and 18.8, separated by `---`. Hints never change what a program does. And mypy agrees with all of it:

```text
$ python -m mypy --strict logpipe.py
Success: no issues found in 1 source file
```

Every stage takes an `Iterable` and returns an `Iterator`. That one choice is what makes the stages plug into each other, and into lists, generators, and (in core.12) files.

### 18.10 Extend it yourself

Try these on your own copy. Each one is a single new stage or consumer.

1. A stage `for_user(records, name)` and the question "what did `ravi` do, in order?".
2. The slowest request per day (hint: `max(day, key=...)` inside the `groupby` loop).
3. Add "longest burst of errors" to `daily_summary` using `groupby` on the level inside each day. Careful: you cannot loop over `day` twice.
4. Change `report` so it answers all four questions in **one** pass, and check that `report(fake_log(3, 1000))` now prints all four answers.
5. Write pytest tests (core.08) for `parse_line`: a good line, a line without `ms`, a line with `ms=abc`.

## 19. Common traps

1. **Looping twice over an iterator.** The second loop silently does nothing. This includes `map`, `filter`, `zip`, `enumerate`, `reversed`, generators, generator expressions and everything from `itertools`. Make a list if you need two passes, or call the generator function again.
2. **A function that works on lists but fails on generators.** Any function that loops over its argument twice (`sum(values)` then `len(list(values))`, or several pipelines from one source) breaks on a stream. Test your functions with a generator as input, not only with a list.
3. **Checking with `len(list(it))` and then using `it`.** Counting consumed it.
4. **`x in iterator` consumes** everything up to and including the match.
5. **Expecting `len`, indexing or slicing on an iterator.** Use `list(...)`, or `islice` for slicing.
6. **Printing a generator and seeing `<generator object ...>`.** You printed the bookmark, not the data. Use `list(g)` (for small data) or `print(*g)`.
7. **Forgetting that calling a generator function runs nothing.** Code before the first `yield`, including input checks, runs only at the first `next()`. To check arguments early, do it in a normal function that returns the generator.
8. **Adding `yield` to a normal function** turns the whole function into a generator. Its `return value` no longer returns that value to the caller.
9. **Calling a recursive generator without `yield from`.** `flatten(item)` alone creates a generator and throws it away. Write `yield from flatten(item)`.
10. **Calling `next()` inside a generator without a default.** If the inner iterator is empty, its `StopIteration` escapes, and Python turns it into `RuntimeError: generator raised StopIteration`. Use `next(it, default)` or `try/except StopIteration` inside the generator.
11. **Passing an infinite iterator to something that wants the end**: `list`, `sum`, `max`, `sorted`, `zip_longest`, `chain(*...)`, or a `for` with no `break`. The program never stops. Cut it first with `islice`, `takewhile`, `break` or `zip`.
12. **Losing an item to `takewhile` or to a home-made `take`.** To decide to stop, they must read one item past the end of what they return.
13. **`groupby` on unsorted data.** It groups **neighbours** only. Sort by the same key first, unless the data is already in that order.
14. **Keeping `groupby` groups for later.** Groups die when `groupby` moves on. Convert each group to a list inside the loop.
15. **Using the original iterator after `tee`.** Items you take from it are missing from the copies. And if one copy runs far ahead, `tee` stores everything; use a list then.
16. **Yielding a mutable object and then changing it** (`batch.clear()`). The caller's references all change too. Yield a new object each time.
17. **Changing a dict or list while looping over it.** A dict raises `RuntimeError: dictionary changed size during iteration`. Loop over a copy (`for k in list(d):`) or build a new dict.
18. **Changing a generator expression's source before consuming it.** The generator reads the data when it runs, not when it is written.
19. **`send` to a new generator.** It must be primed with `next(g)` first.
20. **Swallowing `GeneratorExit`.** If you catch it, re-raise it. Use `try/finally` for clean-up instead.
21. **Using a generator when a list is simpler.** For small data that you need several times, a list is clearer and avoids all the one-pass traps. Laziness is a tool, not a rule.

Trap 17 in action, since you have not seen it yet in this chapter:

```python
marks = {"asha": 80, "ravi": 30, "meena": 25}
for name in marks:
    if marks[name] < 40:
        del marks[name]
```

```text
$ python trap_mutate.py
Traceback (most recent call last):
  File "/home/you/project/trap_mutate.py", line 2, in <module>
    for name in marks:
                ^^^^^
RuntimeError: dictionary changed size during iteration
```

The dict's iterator keeps a position inside the dict. Deleting a key moves the other keys around, so the position would no longer make sense, and Python stops you. Looping over `list(marks)` (a separate copy of the keys) is safe:

```python
marks = {"asha": 80, "ravi": 30, "meena": 25}
for name in list(marks):
    if marks[name] < 40:
        del marks[name]
print(marks)
```

```text
$ python trap_mutate2.py
{'asha': 80}
```

And trap 10, the one that looks the strangest:

```python
def firsts(lists):
    for lst in lists:
        it = iter(lst)
        yield next(it)


print(list(firsts([[1, 2], [3], [], [4]])))
```

```text
$ python trap_stopiter.py
Traceback (most recent call last):
  File "/home/you/project/trap_stopiter.py", line 4, in firsts
    yield next(it)
          ~~~~^^^^
StopIteration

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/home/you/project/trap_stopiter.py", line 7, in <module>
    print(list(firsts([[1, 2], [3], [], [4]])))
          ~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
RuntimeError: generator raised StopIteration
```

The empty list `[]` made `next(it)` raise `StopIteration` inside the generator. If Python let it out, the `list()` call would think the **generator** had finished normally and would quietly return `[1, 3]`, hiding the bug, and dropping `4`. So Python converts it to a `RuntimeError` instead. The fix is to handle the empty case inside the generator:

```python
def firsts(lists):
    for lst in lists:
        it = iter(lst)
        try:
            yield next(it)
        except StopIteration:
            continue


print(list(firsts([[1, 2], [3], [], [4]])))
```

```text
$ python trap_stopiter2.py
[1, 3, 4]
```

And trap 7, with its fix:

```python
def check_positive(values):
    if not values:
        raise ValueError("values must not be empty")
    for v in values:
        yield v > 0


result = check_positive([])
print("no error yet!")
print(list(result))
```

```text
$ python trap_lazyerr.py
no error yet!
Traceback (most recent call last):
  File "/home/you/project/trap_lazyerr.py", line 10, in <module>
    print(list(result))
          ~~~~^^^^^^^^
  File "/home/you/project/trap_lazyerr.py", line 3, in check_positive
    raise ValueError("values must not be empty")
ValueError: values must not be empty
```

The check ran only when `list` started the generator: far from the line with the mistake. Split it: a normal function checks the arguments **now**, then returns the generator.

```python
def check_positive(values):
    if not values:
        raise ValueError("values must not be empty")
    return _check(values)


def _check(values):
    for v in values:
        yield v > 0


try:
    result = check_positive([])
except ValueError as e:
    print("caught at once:", e)
print(list(check_positive([3, -1])))
```

```text
$ python trap_lazyerr2.py
caught at once: values must not be empty
[True, False]
```

## 20. Summary

- **The iteration protocol**: `iter(x)` gets an iterator; `next(it)` gets the next item; `StopIteration` means "finished". A `for` loop is exactly `iter` once, then `next` until `StopIteration`. `next(it, default)` returns `default` instead of raising.
- An **iterable** can make iterators (a book: list, str, dict, set, range). An **iterator** is a position that only moves forward (a bookmark). `iter(it) is it` is true only for iterators.
- **An iterator can be consumed only once** because it is a position, not a collection. Second loops, `in`, `len(list(...))` and shared pipelines all fall into this. Make a list, or create a fresh iterator.
- Under the hood, an iterator is any object with `__iter__` (returning itself) and `__next__` (returning the next item or raising `StopIteration`). Generators write this for you.
- A **generator function** contains `yield`. Calling it runs nothing and returns a generator object. Each `next()` runs to the next `yield` and **pauses**, keeping local variables. `return` (or the end) finishes it. Errors appear at `next()`, and an escaping exception ends the generator.
- A **generator expression** `(f(x) for x in xs if ...)` is a lazy list comprehension: constant small memory, work done on demand, stops early with `any`/`all`/`next`/`islice`. Use a list when you need several passes, `len`, indexing or sorting.
- Generators can be **infinite**; the consumer decides when to stop. Never pass an infinite iterator to `list`, `sum`, `max` or `sorted`.
- A **pipeline** is a chain of generator stages (`source -> clean -> parse -> filter -> consume`). One item flows through at a time, so memory stays flat and the input can be larger than RAM.
- `yield from it` yields every item of `it`; it is how recursive generators work, and it passes back the sub-generator's return value.
- `send(v)` puts a value into a paused `yield` (prime with `next` first), `throw(exc)` raises an exception there, `close()` raises `GeneratorExit` there. Use `try/finally` for clean-up. `send` and `throw` are rare in everyday code.
- **itertools**, all lazy:
  - infinite: `count`, `cycle`, `repeat`;
  - cutting and joining: `islice`, `takewhile`, `dropwhile`, `chain`, `chain.from_iterable`, `zip_longest`;
  - filtering and mapping: `compress`, `filterfalse`, `starmap`;
  - running and neighbours: `accumulate`, `pairwise`, `batched`;
  - grouping: `groupby` groups **neighbours**: sort by the same key first, and use each group before moving on;
  - combinatorics: `product` (replaces nested loops), `permutations`, `combinations`, `combinations_with_replacement`; they grow explosively, so count with `math.comb`/`math.perm` first;
  - `tee` splits one iterator into several; do not touch the original, and prefer a list if one copy runs far ahead.
- Patterns: `iter(func, sentinel)`, chunking, sliding windows, `next((x for x in xs if ...), None)`, peeking with `next(it, None)`, order-keeping de-duplication.

When you can explain why the second loop over a generator prints nothing, rewrite a nested loop as a pipeline of generators and `itertools`, and process a million-line stream in a few megabytes, you have met the outcomes of this module. The problems that follow practise each part, from tracing a `for` loop by hand to building your own pipeline stages.

### What comes next

In **core.11, Decorators and functional tools**, functions that take functions and return functions become the main topic. You will meet `functools`, a sister module of `itertools`, with more ready-made tools for working with functions. In **core.12**, real files arrive: a file object is an iterator of lines, so every pipeline from this chapter will work on real log files by changing one argument.
