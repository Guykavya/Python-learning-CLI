# Chapter 22: Pythonic design and patterns

By now you can write Python that works. You know loops, classes, decorators, generators, the data model, typing, testing and concurrency. This chapter is about a different skill: writing Python that is **good**. Code that another person (or you, in six months) can read in one pass, change without fear, and test without a ceremony.

That skill is mostly **judgment**, not syntax. Nothing in this chapter adds a new keyword. Instead it teaches you to look at working code and ask: is this easy to read? Is it easy to change? What will break if I touch it? Is this design solving a real problem, or only looking professional?

Because it is judgment, the chapter is built **problem first**. For every idiom, principle and pattern you will see the same path:

1. the **pain**: real code that works but hurts;
2. the **naive fix**, and why it only moves the pain;
3. the **idea** (the idiom, principle or pattern) in its general form;
4. the **short Pythonic version**, because Python often needs ten lines where other languages need a hundred;
5. **when not to use it**, because every idea here is a tool, and a tool used on the wrong job makes things worse.

The chapter has four learning outcomes:

1. **Write idiomatic Python**: use iteration tools, unpacking, `None` checks, EAFP, comprehensions, context managers and the standard library the way Python programmers expect, and name the common smells.
2. **Apply SOLID with Python's tools**: split responsibilities, extend by registering instead of editing, keep subclasses honest, depend on small Protocols, and inject collaborators.
3. **Use the classic patterns when they pay**: strategy, factory, observer, adapter, command, null object. Know the one-line Python shortcut for each, and know when a plain function is enough.
4. **Change code safely**: pin behavior with characterization tests, refactor in small steps, keep tests green, and stop when the code is good enough.

**A note on how examples are shown.** Every block that has output was really run, with **Python 3.14** on Linux. File paths are shown as `/home/you/...`. Nothing here depends on the machine, except where the text says so. Some examples show only the key lines of a longer program; their output comes from running the full program. Everything uses only features from core.01 to core.21 (for example dataclasses from core.15, `Protocol` from core.16, `pytest` from core.19).

## Table of contents

[1. What "Pythonic" means](#1-what-pythonic-means) · [2. Pythonic idioms](#2-pythonic-idioms) · [3. Anti-patterns and code smells](#3-anti-patterns-and-code-smells) · [4. Data with a shape](#4-data-with-a-shape) · [5. Functions first](#5-functions-first) · [6. SOLID in Python](#6-solid-in-python) · [7. Design patterns, problem first](#7-design-patterns-problem-first) · [8. Dependency injection without frameworks](#8-dependency-injection-without-frameworks) · [9. Clean code](#9-clean-code) · [10. Refactoring safely](#10-refactoring-safely) · [11. Worked refactor: a legacy script becomes a clean module](#11-worked-refactor-a-legacy-script-becomes-a-clean-module) · [12. Over-engineering: pattern or ceremony?](#12-over-engineering-pattern-or-ceremony) · [13. Common traps](#13-common-traps) · [14. Summary](#14-summary)

## 1. What "Pythonic" means

### 1.1 Code is read more than it is written

You write a line of code once. After that it is read many times: by a teammate who reviews it, by a tester who wonders why it fails, by you when a bug report arrives next month. Every design rule in this chapter comes back to one fact: **the reader's time is the cost that matters most.** A clever trick saves you ten seconds today and costs every later reader a minute.

"Pythonic" is the word the Python community uses for code that respects this. It does not mean "short" and it does not mean "uses advanced features". It means: *code that does the obvious thing in the way Python programmers expect to see it.*

Look at the same task written twice. Both programs print the same result.

```python
names = ["Asha", "Ben", "Chen"]
scores = [90, 72, 85]

i = 0
while i < len(names):
    print(str(i + 1) + ". " + names[i] + " scored " + str(scores[i]))
    i = i + 1
```

```python
names = ["Asha", "Ben", "Chen"]
scores = [90, 72, 85]

for rank, (name, score) in enumerate(zip(names, scores), start=1):
    print(f"{rank}. {name} scored {score}")
```

Both output:

```text
1. Asha scored 90
2. Ben scored 72
3. Chen scored 85
```

The second version has no counter to forget to increment, no index to get wrong, no `str()` conversions, and it says what it means: "go through names and scores together, numbering from 1". The first one makes you read the loop machinery to find the intent.

### 1.2 The Zen of Python

Python ships with a tiny poem about its own design. Run `import this` and you get 19 lines. These are the ones that matter most for this chapter:

```text
Explicit is better than implicit.
Flat is better than nested.
Readability counts.
Errors should never pass silently.
If the implementation is hard to explain, it's a bad idea.
```

Read them as design advice:

- **Explicit is better than implicit**: a function that takes `now` as a parameter is clearer than one that secretly calls the clock (section 8).
- **Flat is better than nested**: early returns beat five levels of `if` (section 9).
- **Errors should never pass silently**: a bare `except: pass` breaks this rule (section 3).
- **If the implementation is hard to explain, it's a bad idea**: a good test for any "clever" design.

### 1.3 Idiom versus cleverness

An **idiom** is a way of writing something that everyone in the community recognizes. `for item in items:` is an idiom. `x = x or default` is an idiom. When you see an idiom you do not read it, you *recognize* it, like a word.

**Cleverness** is code that is short because it is hard to read. A rule of thumb: an idiom gets *easier* to read as you learn Python. Cleverness stays hard for everyone.

```python
# clever: what does this do?
result = [x for x in (y for y in data if y) if x % 2][::-1][:3]
```

Names are free documentation: two lines and two named values (`odd_numbers`, `last_three_odd`) beat one line nobody can decode, and you can print each while debugging.

### 1.4 Pythonic is not a religion

Pythonic does not always mean shorter: a 12-line loop with an early `break` can beat a one-line comprehension that does extra work. Idioms are defaults, not laws. Know the idiom, and break it on purpose, not by accident.

#### Try it 1.1

Which version would you rather review? Say why in one sentence.

```python
# A
def f(l):
    r = []
    for i in range(len(l)):
        if l[i] % 2 == 0:
            r.append(l[i] * l[i])
    return r

# B
def squares_of_evens(numbers):
    return [n * n for n in numbers if n % 2 == 0]
```

<details><summary>Answer</summary>

B. The function name says what it does, the parameter is `numbers` (not `l`, which looks like `1`), there is no index to get wrong, and the whole job is one line that reads almost like English: "n times n for each n in numbers if n is even". Version A does the same work but the reader must decode `f`, `l`, `r`, `i` and the index arithmetic first.

</details>

## 2. Pythonic idioms

These are the idioms you will meet in almost every real Python file. For each, you see the pain first.

### 2.1 Iterate over things, not over positions

**The pain.** People who learned C or Java first write loops over indexes. It works, but it adds a variable (`i`) that can be off by one, and it hides what you really want.

```python
names = ["Asha", "Ben", "Chen"]
scores = [90, 72, 85]

for i in range(len(names)):
    print(i + 1, names[i], scores[i])
```

**The idea.** Python's `for` loop walks over the items directly. When you need more than the item, ask a helper for it:

Use `for x in items` for the item only; `enumerate(items, start=1)` for the item and its position; `zip(xs, ys)` for several sequences together; `reversed(items)` for backwards; `sorted(items)` for sorted order without changing the list.

```python
for rank, (name, score) in enumerate(zip(names, scores), start=1):
    print(rank, name, score)
```

```text
1 Asha 90
2 Ben 72
3 Chen 85
```

Two details worth knowing, both shown by running:

```python
print(list(zip([1, 2, 3], "ab")))
print(list(enumerate("ab", start=10)))
```
```text
[(1, 'a'), (2, 'b')]
[(10, 'a'), (11, 'b')]
```

`zip` stops at the **shortest** input and silently drops the rest. That is often fine, but if the lengths should match and a mismatch means a bug, use `zip(xs, ys, strict=True)` (Python 3.10+), which raises `ValueError` instead.

**The same idea for "loop with a flag" and "loop with an accumulator".** Two loops appear everywhere in beginner code:

```python
scores = [90, 72, 85]

found = False
for s in scores:
    if s < 75:
        found = True
        break

total = 0
for s in scores:
    total += s
```

Python has one-word answers for both:

```python
found = any(s < 75 for s in scores)
total = sum(scores)
print(found, total)
```
```text
True 247
```

`any`, `all`, `sum`, `min`, `max`, `sorted`, `len` and `enumerate` are the built-in "verbs" of iteration. Learn them well; they replace most hand-written accumulator loops.

**When not to.** If the loop body does several different things (prints, writes a file, updates three variables), keep it as a loop. `any`/`sum` are for *one* clear question.

#### Try it 2.1

What do these print?

```python
print(list(zip(["a", "b", "c"], [1, 2])))
for i, ch in enumerate("hi", start=5):
    print(i, ch)
print(all([]), any([]))
```

<details><summary>Answer</summary>

```text
[('a', 1), ('b', 2)]
5 h
6 i
True False
```

`zip` stops at the shorter list, so `'c'` is dropped. `enumerate(..., start=5)` counts from 5. `all([])` is `True` ("no element breaks the rule") and `any([])` is `False` ("no element satisfies it"); both follow from "an empty collection has no counterexample and no example".

</details>

### 2.2 Unpacking

**The pain.** Reaching into sequences by number makes the reader remember what `row[2]` means.

```python
row = ("Asha", 30, "Pune")
print(row[0] + " is " + str(row[1]) + " and lives in " + row[2])
```

**The idea.** Give every piece a name at the moment you take it apart.

```python
name, age, city = row
print(f"{name} is {age} and lives in {city}")

first, *rest = [10, 20, 30, 40]
head, *middle, last = [10, 20, 30, 40]
print(first, rest)
print(head, middle, last)

a, b = 1, 2
a, b = b, a          # swap, no temporary variable
print(a, b)

(x, y), label = (3, 4), "point"      # nested unpacking
print(x, y, label)
```
```text
Asha is 30 and lives in Pune
10 [20, 30, 40]
10 [20, 30] 40
2 1
3 4 point
```

The starred name always gets a **list**, even when it is empty. Unpacking also merges dictionaries: `{**defaults, **user}` or `defaults | user` (Python 3.9+) gives the merged dict, and later keys win.

**When not to.** Unpacking a 9-item tuple into 9 names is a sign the data wants a name for itself (a dataclass or `NamedTuple`, section 4).

### 2.3 Truthiness and `None`

**The pain.** Python lets you write `if not x`. Beginners learn "empty means False" and then use it for everything, including values where `0` or `""` is a perfectly good answer.

```python
def describe(count):
    if not count:
        return "nothing"
    return f"{count} items"

print(describe(0), describe(None), describe([]))
```
```text
nothing nothing nothing
```

All three calls print `nothing`. But "0 items" and "no information" are not the same thing. If `count` is `0` because the shelf was counted and is empty, you just threw that fact away.

**The idea.** Use truthiness when you really mean "is there something here?". Use `is None` when you mean "was a value supplied?".

```python
def describe(count):
    if count is None:
        return "unknown"
    return f"{count} items"

print(describe(0), describe(None))
```
```text
0 items unknown
```

The falsy values are `None`, `False`, `0`, `0.0`, `""`, `[]`, `{}`, `set()`, `()` and `range(0)`. Everything else is truthy, including `[0]` and `" "`.

```python
print(bool([]), bool(""), bool(0), bool(0.0), bool(None), bool([0]), bool(" "))
```
```text
False False False False False True True
```

Two companion rules:

- **Compare to `None` with `is`, never `==`.** `None` is a singleton, so `is` is exact and fast. `==` calls `__eq__`, and a class can lie in it:

```python
class Weird:
    def __eq__(self, other):
        return True

print(Weird() == None, Weird() is None)
```
```text
True False
```

- **Do not compare to `True`/`False`.** Write `if ready:`, not `if ready == True:`.

The `or` default idiom has the same trap: `name or "friend"` is fine when an empty name should also become "friend", but `port or 8080` turns a legal `port = 0` into `8080`. When `0` or `""` is a real value, write `8080 if port is None else port`.

#### Try it 2.2

What does each line print?

```python
def label(n):
    return "zero" if not n else "some"

print(label(0), label(None), label([]), label(0.0), label("0"))
print(None == None, [] == None, [] is None)
```

<details><summary>Answer</summary>

```text
zero zero zero zero some
True False False
```

`0`, `None`, `[]` and `0.0` are falsy, but `"0"` is a non-empty string, so it is truthy. An empty list is not `None`: it is a real list that happens to be empty.

</details>

### 2.4 EAFP versus LBYL

**The pain.** Two ways to deal with something that might fail.

- **LBYL**, "look before you leap": check first, then act.
- **EAFP**, "easier to ask forgiveness than permission": act, and handle the failure.

```python
import os

def read_lbyl(path):
    if os.path.exists(path):
        with open(path) as f:
            return f.read()
    return ""
```

This is **racy**: between the `exists` check and the `open`, another process can delete the file. The only reliable test of "can I open this?" is opening it.

**The idea.** Do the thing, and catch the *specific* error you expect.

```python
def read_eafp(path):
    try:
        with open(path) as f:
            return f.read()
    except FileNotFoundError:
        return ""
```

The same shape applies to dictionaries:

```python
settings = {"theme": "dark"}

# LBYL: two lookups
if "theme" in settings:
    print(settings["theme"])

# EAFP: one lookup, handle the miss
try:
    print(settings["font"])
except KeyError:
    print("default font")

# even better when a default is enough
print(settings.get("font", "mono"))
```
```text
dark
default font
mono
```

For counting and grouping, `dict` has helpers so you need neither:

```python
counts = {}
for w in "a b a c a".split():
    counts[w] = counts.get(w, 0) + 1
print(counts)

groups = {}
for w in ["apple", "avocado", "banana"]:
    groups.setdefault(w[0], []).append(w)
print(groups)
```
```text
{'a': 3, 'b': 1, 'c': 1}
{'a': ['apple', 'avocado'], 'b': ['banana']}
```

(Section 2.7 shows `Counter` and `defaultdict`, which do both even better.)

**When not to.** EAFP is not "wrap everything in try". Keep the `try` body **small**, and catch the **specific** exception. This function hides every bug:

```python
def total(rows):
    try:
        return sum(int(r) for r in rows)
    except Exception:
        return 0

print(total(["1", "2"]), total(["1", "x"]))
```
```text
3 0
```

`["1", "x"]` is bad input, but the caller just gets `0` and thinks the total is zero. Catch `ValueError` only if you know what to do about it, and let everything else crash loudly. Use LBYL when failure is **expensive or irreversible** (check before you send an email or delete a record) and when the check is cheap and not racy (`if not items:` before `items[0]`).

#### Try it 2.3

`parse_age("x")` should return `None` for bad input. Which version is better, and what does the other one hide?

```python
def parse_age_a(text):
    try:
        return int(text)
    except Exception:
        return None

def parse_age_b(text):
    try:
        return int(text)
    except ValueError:
        return None
```

<details><summary>Answer</summary>

B. `int("x")` raises `ValueError`, which is exactly the "bad input" case. Version A also catches `TypeError` (for `parse_age(None)`, which is a programming mistake, not bad user input), and it would swallow a typo such as a `NameError` inside the `try` too. With B, `parse_age(None)` raises `TypeError` right away and tells you the *caller* is wrong. Catch the error you can recover from, nothing more.

</details>

### 2.5 Comprehensions and generator expressions

**The pain.** Building a list with `append` in a loop is five lines for a one-line idea.

```python
squares = []
for n in range(6):
    if n % 2 == 0:
        squares.append(n * n)
```

**The idea.** A comprehension says "a list of *this* for each *that* where *condition*":

```python
squares = [n * n for n in range(6) if n % 2 == 0]
print(squares)
words = ["aa", "b", "cc"]
print({w: len(w) for w in words}, {len(w) for w in words})
```
```text
[0, 4, 16]
{'aa': 2, 'b': 1, 'cc': 2} {1, 2}
```

Round brackets give a **generator expression**: it makes the items **one at a time, on demand**, and builds no list. This matters when you only need part of the data:

```python
class Counting:
    def __init__(self, n):
        self.n = n
        self.pulled = 0
    def __iter__(self):
        for i in range(self.n):
            self.pulled += 1
            yield i

c = Counting(1000)
print(any(x > 2 for x in c), c.pulled)       # generator: stops early

c = Counting(1000)
print(any([x > 2 for x in c]), c.pulled)     # list: builds all 1000 first
```
```text
True 4
True 1000
```

The generator version looked at 4 items (0, 1, 2, 3) and stopped. The list version made all 1000 first. For `sum`, `min`, `max`, `any`, `all`, `",".join(...)` pass a generator expression with no extra brackets.

**When not to.** Three situations where a plain loop is better:

1. **Side effects.** `[log.append(n) for n in range(3)]` builds a throwaway list of `None`s just to call `append`. Use a `for` loop.
2. **Early exit with work in the body.** If you need `break`, a comprehension cannot do it.
3. **Too many clauses.** One `for` and one `if` is easy. Three `for` clauses in one line is a puzzle:

```python
hard = [(x, y, z) for x in range(3) for y in range(3) for z in range(3) if x < y < z]
print(hard)
```
```text
[(0, 1, 2)]
```

You can understand it, but it took you a moment. A rule that works: **at most two `for` clauses, or one `for` plus one `if`; otherwise write a loop or a helper function.**

### 2.6 Context managers for cleanup

**The pain.** Anything you must undo (close a file, release a lock, restore a setting) is easy to forget when an error happens halfway.

```python
class Settings:
    debug = False

Settings.debug = True
run_the_risky_part()          # if this raises, debug stays True forever
Settings.debug = False
```

`try/finally` fixes it, but you write the same four lines at every use. The `with` statement (core.15) moves the cleanup into one place. If no ready-made context manager exists, write one in six lines with `contextlib.contextmanager`:

```python
from contextlib import contextmanager

class Settings:
    debug = False

@contextmanager
def temp_setting(obj, name, value):
    old = getattr(obj, name)
    setattr(obj, name, value)
    try:
        yield obj
    finally:
        setattr(obj, name, old)

with temp_setting(Settings, "debug", True):
    print("inside:", Settings.debug)
print("after:", Settings.debug)

try:
    with temp_setting(Settings, "debug", True):
        raise RuntimeError("boom")
except RuntimeError:
    print("restored:", Settings.debug)
```
```text
inside: True
after: False
restored: False
```

The `finally` runs even when the body raises. Every "do X, then always undo X" pair is a context manager waiting to be written: open/close, acquire/release, start/stop a timer, change directory and change back, begin/commit a transaction.

**When not to.** Do not write a context manager for a one-off cleanup that appears once. A plain `try/finally` there is clearer.

### 2.7 Stdlib first

**The pain.** Hand-written helpers for common jobs are longer, slower and have more bugs than the standard library versions, which are tested by millions of programs.

```python
from collections import Counter, defaultdict, deque
from itertools import groupby, chain
from functools import cache

text = "the cat and the hat and the bat"
print(Counter(text.split()).most_common(2))

by_letter = defaultdict(list)
for w in ["apple", "avocado", "banana"]:
    by_letter[w[0]].append(w)
print(dict(by_letter))

q = deque([1, 2, 3], maxlen=3)
q.append(4)
print(q)
print(q.popleft())

data = sorted(["bb", "a", "cc", "d"], key=len)
print([(k, list(v)) for k, v in groupby(data, key=len)])
print(list(chain([1, 2], (3,), "ab")))

@cache
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)

print(fib(80))
print(fib.cache_info())
```
```text
[('the', 3), ('and', 2)]
{'a': ['apple', 'avocado'], 'b': ['banana']}
deque([2, 3, 4], maxlen=3)
2
[(1, ['a', 'd']), (2, ['bb', 'cc'])]
[1, 2, 3, 'a', 'b']
23416728348467685
CacheInfo(hits=78, misses=81, maxsize=None, currsize=81)
```

Quick map: `Counter` replaces a `get(w, 0) + 1` loop; `defaultdict(list)` replaces `if k not in d`; `deque.popleft()` replaces `list.pop(0)` (slow: every item shifts); `groupby` groups equal neighbours; `chain` flattens; `functools.cache` replaces a hand-made dict of past results.

`groupby` has a classic trap: it only groups **adjacent** equal keys. That is why the example sorts by `len` first.

**When not to.** Do not import a module for a trivial case. `sum(x for x in xs)` is just `sum(xs)`, and you do not need `Counter` to count one thing.

#### Try it 2.4

What does this print? Trace it by hand first, then check.

```python
x = [[0] * 2] * 2
x[0][0] = 1
print(x)
print(1 < 2 < 3, 1 < 3 < 2, 3 > 2 == 2)
a, b = 1, 2
a, b = b, a + b
print(a, b)
d = {"k": 1}
def expensive():
    print("expensive called")
    return 0
print(d.get("k", expensive()))
print("" or "default", 0 or None, [] and 1)
```

<details><summary>Answer</summary>

```text
[[1, 0], [1, 0]]
True False True
2 3
expensive called
1
default None []
```

- `[[0] * 2] * 2` repeats **the same inner list twice**, so changing `x[0][0]` also changes `x[1][0]`. Build a grid with a comprehension: `[[0] * 2 for _ in range(2)]`.
- Chained comparisons: `1 < 2 < 3` means `1 < 2 and 2 < 3`. `3 > 2 == 2` means `3 > 2 and 2 == 2`, which is true.
- `a, b = b, a + b`: the whole right side is calculated first (`2` and `1 + 2 = 3`), then assigned. So `a=2, b=3`.
- `d.get("k", expensive())` calls `expensive()` **before** `get` runs, because arguments are evaluated first, even though `"k"` is found.
- `"" or "default"` gives `"default"`; `0 or None` gives `None` (the last operand); `[] and 1` stops at the first falsy value and gives `[]`.

</details>

## 3. Anti-patterns and code smells

A **code smell** is a pattern in code that is not a bug yet, but often leads to one. An **anti-pattern** is a common "solution" that causes more problems than it solves. You cannot design well until you can *smell* trouble. This section is a field guide to the eight smells you will meet most.

### 3.1 The mutable default argument

**The pain.** A default value is created **once**, when `def` runs, not each time the function is called.

```python
def add_tag(tag, tags=[]):
    tags.append(tag)
    return tags

print(add_tag("a"))
print(add_tag("b"))
print(add_tag.__defaults__)
```
```text
['a']
['a', 'b']
(['a', 'b'],)
```

The second call was supposed to return `['b']`. It returned `['a', 'b']` because both calls share the same list, which lives inside the function object (`__defaults__` shows it). This bug is silent, depends on call history, and shows up far from its cause.

**The naive fix** is "just do not call it twice", which is not a fix. **The real fix** is the `None` sentinel:

```python
def add_tag(tag, tags=None):
    if tags is None:
        tags = []
    tags.append(tag)
    return tags

print(add_tag("a"), add_tag("b"))
```
```text
['a'] ['b']
```

The same trap exists for `{}`, `set()`, and any other mutable object, including `datetime.now()` evaluated as a default (it is frozen at definition time). Immutable defaults (`0`, `""`, `None`, `()`) are safe.

### 3.2 The bare `except`

**The pain.** `except:` with no class catches **everything**, including your own typos and Ctrl+C.

```python
def average(xs):
    try:
        return sum(xs) / len(xs)
    except:
        return 0

print(average([1, 2, 3]))
print(average([]))
print(average(None))
```
```text
2.0
0
0
```

`average([])` has a real, expected failure (division by zero). `average(None)` is a bug in the *caller*, but it also quietly returns `0`. A typo inside the `try` would be swallowed the same way. Zen: *errors should never pass silently*.

**The fix.** Catch the specific exception you know how to handle, and only around the line that can raise it:

```python
def average(xs):
    try:
        return sum(xs) / len(xs)
    except ZeroDivisionError:
        return 0.0

try:
    average(None)
except TypeError as e:
    print("TypeError:", e)
```
```text
TypeError: 'NoneType' object is not iterable
```

Now the empty-list case is handled on purpose and the caller bug is loud. If you must catch widely (a top-level loop that should not die), catch `Exception` (not bare), and **log** it with the traceback (core.17).

### 3.3 The god function

**The pain.** One function that reads input, validates, calculates and prints. Here is a small one:

```python
def process(text):
    lines = text.strip().splitlines()
    total = 0
    for line in lines:
        name, qty, price = line.split(",")
        qty = int(qty)
        price = float(price)
        if qty <= 0:
            print("bad qty", name)
            continue
        total += qty * price
    print("TOTAL", total)

process("pen,2,1.5\nbook,0,9\ncup,1,4")
```
```text
bad qty book
TOTAL 7.0
```

It works. Now try to *test* the pricing rule: you must capture printed text. Try to *reuse* the parsing for a web page: it prints, so you cannot. Try to change the format of a line: you touch the same function that does the maths. A function that does four jobs has four reasons to change. Section 6.2 (single responsibility) and section 11 show how to split it.

**How to smell it.** The function is longer than a screen; its name needs "and" (`parse_and_print`); you cannot describe it without "then"; variables at the top are used only at the bottom.

### 3.4 Stringly typed code

**The pain.** Using plain strings (or numbers) for things that have a fixed set of values, so that typos are not errors.

```python
def speed(kind):
    if kind == "car":
        return 100
    elif kind == "bike":
        return 25
    elif kind == "walk":
        return 5

print(speed("bike"), speed("bkie"))
```
```text
25 None
```

`"bkie"` is a typo. Python does not mind: no branch matches, the function falls off the end and returns `None`, which will blow up somewhere else, later.

**The fix.** Give the closed set of values a type, an `Enum` (core.15), so an unknown name is an immediate error:

```python
from enum import Enum

class Mode(Enum):
    CAR = 100
    BIKE = 25
    WALK = 5

Mode["BKIE"]          # KeyError: 'BKIE'  (an immediate, loud error)
```

Editors also auto-complete `Mode.` and type checkers (core.16) catch `Mode.BKIE` before the program runs. The same smell appears as dictionaries with magic keys (`user["nmae"]`); section 4 shows the cure.

### 3.5 The `isinstance` / type-string chain

**The pain.** A function that asks "what are you?" and branches. Each new kind forces you to **edit** that function, and to remember every other function that has the same chain.

```python
class Circle:
    def __init__(self, r): self.r = r
class Rect:
    def __init__(self, w, h): self.w, self.h = w, h
class Tri:
    def __init__(self, b, h): self.b, self.h = b, h

def area(shape):
    if isinstance(shape, Circle):
        return 3 * shape.r ** 2
    elif isinstance(shape, Rect):
        return shape.w * shape.h

print(area(Rect(2, 3)), area(Tri(2, 3)))
```
```text
6 None
```

`Tri` was added but nobody updated `area`, so it quietly returns `None` again. Two cures appear later: a **method on the class** (`shape.area()`, polymorphism), and a **registry** when you cannot touch the classes (section 6.2).

Related: `type(x) == list` rejects subclasses (`MyList()` fails the test, `isinstance` accepts it). Use `isinstance` when you truly must check, but first ask whether you need to check at all: duck typing (core.14) says to call the method and let it fail if it is missing.

### 3.6 Flag arguments

A boolean parameter that switches the function between two jobs (`render("hi", True)`) is unreadable at the call site, since `True` means nothing there. Write two functions with honest names (`render_html`, `render_text`), pass the behavior as a function (section 5), or at least make the flag keyword-only: `def render(text, *, html=False)`.

### 3.7 Premature abstraction

The opposite of copy-paste: someone sees two similar pieces and builds a framework (`DataProcessor(reader, parser, validator, writer)`) for imagined future cases, for a script that reads one CSV. When the second real case arrives, it never fits. A useful guide is the **rule of three**: copy once, tolerate the second repeat, abstract at the third, when you know what really varies.

### 3.8 Copy-paste code

**The pain.** The first fix for "I need this again" is to paste and edit.

```python
def price_book(item):
    fine = max(item.days - 14, 0) * 0.25
    return min(fine, 10)

def price_dvd(item):
    fine = max(item.days - 3, 0) * 1.0
    return min(fine, 20)
```

Two copies of the same shape: "days past a grace period, times a rate, capped at a maximum". Fix a bug in one and the other keeps it. The cure is to find *what differs* (grace, rate, cap) and make those the parameters: one function, three arguments, or one function and a table of settings (section 11 does exactly this).

Premature abstraction and copy-paste are **opposites**, and good judgment lives between them: do not abstract one example; do abstract the third.

A smell is a question, not a verdict: each one above has a legitimate use. Look closer, ask what will change here and what could go wrong, then decide.

#### Try it 3.1

What does this print? Then fix the function.

```python
def f(a, b=[]):
    b.append(a)
    return b

print(f(1), f(2), f(3, []))
```

<details><summary>Answer</summary>

```text
[1, 2] [1, 2] [3]
```

`f(1)` and `f(2)` both return the **same** default list object, so when `print` finally shows them, that list already holds `1` and `2`. `f(3, [])` was given its own fresh list. Fix: `def f(a, b=None):` then `if b is None: b = []`.

</details>

#### Try it 3.2

What does `average([])` return here, and why is that a problem for the caller?

```python
def average(xs):
    try:
        return sum(xs) / len(xs)
    except Exception:
        return 0
```

<details><summary>Answer</summary>

It returns `0`. The caller cannot tell "the average of the data is zero" from "there was no data" or even "I passed the wrong type of object" (`average(None)` also returns `0`). The failure is converted into a plausible value. Better: catch `ZeroDivisionError` only, and decide on purpose what an empty list means (return `0.0`, return `None`, or raise `ValueError("no data")`).

</details>

#### Try it 3.3

Predict the output, then say which line is the surprise.

```python
print(type(True) == bool, isinstance(True, int), type(True) == int)
```

<details><summary>Answer</summary>

```text
True True False
```

`bool` is a subclass of `int`, so `isinstance(True, int)` is `True`, but `type(True) == int` is `False`. An exact `type(x) == ...` check ignores subclasses; `isinstance` respects them.

</details>

## 4. Data with a shape

### 4.1 The pain: dictionaries and tuples as records

A record is a group of named values: a user, a point, an order. The first tool most people reach for is a `dict` or a `tuple`.

```python
user = {"name": "Asha", "age": 30}
print(user["nmae"] if "nmae" in user else "typo goes unnoticed")
```
```text
typo goes unnoticed
```

A dictionary accepts any key at any time: typos, missing keys, extra keys. A tuple `("Asha", 30)` is worse: nothing says which item is the age. The structure exists only in the programmer's head.

### 4.2 The tools

Python gives you five tools for "data with a shape". They answer different questions:

| Tool | Choose it when | Mutable? | Checked at runtime? |
|---|---|---|---|
| `dict` | keys are not known in advance (a word count, a lookup table) | yes | no |
| `NamedTuple` | a small, fixed, **immutable** record that must also behave like a tuple (unpacking, indexing, returned from functions) | no | field count only |
| `@dataclass` | a record with behavior, defaults, validation, ordering; the default choice | your choice (`frozen=True`) | only what you write |
| `Enum` | a **closed set of named choices** | no | yes (bad name raises) |
| `TypedDict` | JSON-like dicts whose keys are known, for **type checkers** only | yes | **no, at runtime it is a plain `dict`** |
| `Protocol` | "anything with these methods" (behavior, not data) | n/a | only with `runtime_checkable` |

### 4.3 `@dataclass`: the default choice

```python
from dataclasses import dataclass, field, replace

@dataclass(frozen=True, order=True)
class User:
    name: str
    age: int = 0
    tags: tuple = ()

    def __post_init__(self):
        if self.age < 0:
            raise ValueError("age must be >= 0")

u = User("Asha", 30)
print(u)
print(u == User("Asha", 30), hash(u) == hash(User("Asha", 30)))
print(replace(u, age=31))
try:
    u.age = 5
except Exception as e:
    print(type(e).__name__)
try:
    User("x", -1)
except ValueError as e:
    print(e)
print(sorted([User("b", 2), User("a", 9)]))
```
```text
User(name='Asha', age=30, tags=())
True True
User(name='Asha', age=31, tags=())
FrozenInstanceError
age must be >= 0
[User(name='a', age=9, tags=()), User(name='b', age=2, tags=())]
```

Read what you got for free: a readable `repr`, equality by value, a hash (because of `frozen=True`), ordering (because of `order=True`, compared field by field: here by `name` first), and a clear error on assignment. `replace` makes a changed **copy**, the Pythonic way to "update" an immutable record. `__post_init__` is where a record checks its own rules once, at creation, so an invalid `User` can never exist.

For a mutable default such as a list, never write `items: list = []` (dataclass refuses it, because of section 3.1). Write `items: list = field(default_factory=list)`, so each new object gets its own fresh list.

### 4.4 `NamedTuple`

When you want something light that *is* a tuple (it unpacks, it can be a dict key, it is immutable) but with names:

```python
from typing import NamedTuple

class Point(NamedTuple):
    x: int
    y: int

p = Point(1, 2)
x, y = p
print(p, x, y, p[0], p._replace(x=5))
```
```text
Point(x=1, y=2) 1 2 1 Point(x=5, y=2)
```

Pick `NamedTuple` for tiny, always-immutable values returned from functions (`divmod`-like results, coordinates). Pick `@dataclass` as soon as you want methods with real logic, validation, defaults you will change, or ordering control.

### 4.5 `Enum`

```python
from enum import Enum

class Status(Enum):
    ACTIVE = "active"
    CLOSED = "closed"

print(Status("active"), Status.ACTIVE.value, [s.name for s in Status])
try:
    Status("actve")
except ValueError as e:
    print(e)
```
```text
Status.ACTIVE active ['ACTIVE', 'CLOSED']
'actve' is not a valid Status
```

An `Enum` turns "a string that must be one of three" into a real type, and gives you free iteration over all choices. Use it at the **boundary**: convert the raw string from a file or user into the enum once (`Status(raw)`), and from there on pass the enum.

### 4.6 `TypedDict` and `Protocol` in one place

```python
from typing import TypedDict

class Row(TypedDict):
    id: int
    name: str

r: Row = {"id": 1, "name": "a"}
print(type(r))
```
```text
<class 'dict'>
```

`TypedDict` is a promise for the **type checker**: at runtime `r` is an ordinary `dict`, nothing is checked. Use it for data that is a dict already (decoded JSON) when you cannot or do not want to convert it. If you create the data yourself, a dataclass is almost always better, since it checks and carries methods.

`Protocol` (core.16) describes **behavior**: "anything with a `read()` method". It is the typing tool for duck typing and shows up in section 6.4.

#### Try it 4.1

You are writing `parse_log_line(line)`, which returns a timestamp (string), a level (one of INFO, WARN, ERROR) and a message. Which tool would you choose for the return value and for the level, and why?

<details><summary>Answer</summary>

Return a small record: a `NamedTuple` if it is only unpacked by the caller (`when, level, message = parse_log_line(line)`), or a frozen `@dataclass` if you also want defaults, validation (reject unknown levels in `__post_init__`) or methods. The level is a closed set, so an `Enum` (`Level.WARN`): a misspelled level then fails at parse time, not three modules later. Not a plain `dict`: the keys are fixed, so a dict would only add typo risk.

</details>

## 5. Functions first

### 5.1 The pain: classes for everything

Many programmers who come from Java write a class for every idea, even when there is one method and no state.

```python
class Greeter:
    def __init__(self, greeting):
        self.greeting = greeting

    def greet(self, name):
        return f"{self.greeting}, {name}"

print(Greeter("Hi").greet("Asha"))
```
```text
Hi, Asha
```

A class with `__init__` and one other method is usually a **function with remembered settings**. Python has simpler ways to say that. They all rest on one fact: **functions are objects**. You can store them in variables, put them in lists and dicts, pass them to other functions, and return them.

### 5.2 Closures: a function that remembers

```python
def make_multiplier(n):
    def multiply(x):
        return x * n
    return multiply

double = make_multiplier(2)
print(double(21), double.__closure__[0].cell_contents)
```
```text
42 2
```

`multiply` still sees `n` after `make_multiplier` has returned. The value is kept in the function's `__closure__`. That is "state without a class".

A famous trap: closures remember the **variable**, not its value at that moment.

```python
fs = [lambda: i for i in range(3)]
print([f() for f in fs])

fs = [lambda i=i: i for i in range(3)]
print([f() for f in fs])
```
```text
[2, 2, 2]
[0, 1, 2]
```

All three lambdas share one `i`, and by the time they run, `i` is `2`. Binding the current value as a **default argument** (`i=i`), or using `functools.partial`, freezes it.

### 5.3 `functools.partial`

`partial` pre-fills some arguments of an existing function and gives back a new one:

```python
from functools import partial

power = partial(pow, exp=2)
print(power(5), list(map(partial(pow, 2), [1, 2, 3])))
hi = partial("{}, {}".format, "Hi")
print(hi("Asha"))
```
```text
25 [2, 4, 8]
Hi, Asha
```

`Greeter("Hi").greet` and `partial(greet, "Hi")` do the same job; the second needs no class.

### 5.4 Callable objects, and the key-function idiom

When a function needs to **keep changing state** between calls, an object with `__call__` (core.15) is the honest tool:

```python
class Counter:
    def __init__(self):
        self.n = 0
    def __call__(self):
        self.n += 1
        return self.n

c = Counter()
c()
print(c())
```
```text
2
```

Functions as arguments are everywhere in Python's own library: `sorted(words, key=len)`, `max(words, key=len)`, `map`, `filter`, `functools.reduce`, `threading.Thread(target=...)`. `operator.itemgetter` and `attrgetter` are ready-made key functions, so `sorted(rows, key=itemgetter("age", "name"))` needs no `lambda`.

### 5.5 When *is* a class the right tool?

Use a **function** when there is input and output and nothing to remember. Use a **closure or `partial`** when you need to remember a couple of settings. Use a **class** when:

- there is **state that changes** and several functions share it (an account, a connection with a buffer);
- several **operations belong together** on the same data;
- you **hold a resource** and must release it (`__enter__`/`__exit__`);
- you need to plug into the data model (`__len__`, `__iter__`, `__eq__`).

A good smell test: if your class has `__init__` and exactly one public method, ask whether a function or a `partial` is enough. If it has several methods that all read and write the same `self.something`, it is a real class.

#### Try it 5.1

What does this print, and how do you change the second line so it prints `[0, 1, 2]`?

```python
callbacks = []
for i in range(3):
    callbacks.append(lambda: i)
print([cb() for cb in callbacks])
```

<details><summary>Answer</summary>

```text
[2, 2, 2]
```

Every lambda looks up the same variable `i` when called, after the loop ended with `i = 2`. Fix: `callbacks.append(lambda i=i: i)` (bind the current value as a default), or `callbacks.append(partial(identity, i))` with `identity = lambda x: x`.

</details>

## 6. SOLID in Python

### 6.1 What SOLID is, and why it exists

SOLID is five design principles collected by Robert C. Martin. They were written for languages like Java and C++, but the *problems* they address exist in every language: code that is hard to change because everything depends on everything.

| Letter | Principle | One-line version |
|---|---|---|
| **S** | Single responsibility | a unit has **one reason to change** |
| **O** | Open/closed | add new behavior by **adding** code, not by editing working code |
| **L** | Liskov substitution | a subclass must work wherever its base class works |
| **I** | Interface segregation | depend on **small** interfaces, only what you use |
| **D** | Dependency inversion | depend on **abstractions** (behavior you pass in), not on concrete things you create |

Python needs less machinery for these than Java does: duck typing replaces many interfaces, first-class functions replace many classes, and `Protocol` gives you typed interfaces without inheritance. But the principles themselves still pay. We take them one at a time, problem first.

### 6.2 S: single responsibility

**The pain.** Recall the god function from section 3.3. Four reasons to change are tangled together: the input format, the validation rules, the pricing rule, and the output format. A change to any one risks breaking another, and you cannot test one without the rest.

**The naive fix**: add comments (`# parse`, `# validate`) inside the same function. That labels the problem but does not separate it.

**The idea.** Split by *reason to change*. A good split has **pure functions** (input in, value out, no printing, no files, no clock) in the core, and the messy world (printing, reading) at the edge:

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Line:
    name: str
    qty: int
    price: float

def parse_order(text):
    lines = []
    for raw in text.strip().splitlines():
        name, qty, price = raw.split(",")
        lines.append(Line(name, int(qty), float(price)))
    return lines

def validate_order(lines):
    return [f"bad qty {ln.name}" for ln in lines if ln.qty <= 0]

def price_order(lines):
    return sum(ln.qty * ln.price for ln in lines if ln.qty > 0)

def process_order(text):
    lines = parse_order(text)
    problems = validate_order(lines)
    total = price_order(lines)
    return "\n".join(problems + [f"TOTAL {total}"])

text = "pen,2,1.5\nbook,0,9\ncup,1,4"
print(process_order(text))
print(price_order(parse_order("a,1,2.5")))
```
```text
bad qty book
TOTAL 7.0
2.5
```

The output is identical to the god function, but now: `price_order` can be tested with plain values; if the input becomes JSON, only `parse_order` changes; `process_order` *returns* a string instead of printing, so the caller decides where it goes (screen, file, web response).

**How to find the reasons.** Ask "who would ask me to change this?": the accountant (pricing), the data team (input format) and the designer (output) are three responsibilities.

**When not to.** Do not split a 6-line function into six 1-line functions with names like `step_one`. Single responsibility is about *reasons to change*, not about counting lines. A cohesive 30-line function that reads like a recipe may be fine.

### 6.3 O: open/closed with a registry

**The pain.** You add a new shape, a new export format, a new discount. Every time you must open the same function and add another `elif`, and re-test every old branch.

```python
def area(kind, *args):
    if kind == "circle":
        return 3.14159 * args[0] ** 2
    elif kind == "square":
        return args[0] ** 2
    # next week "rect", then "triangle": edit here again
```

**The naive fix**: a bigger `elif` chain. That is the problem, not a solution.

**The idea.** Code should be **open for extension, closed for modification**: new behavior arrives as *new* code, and the old function never changes. The simplest Python form is a **registry**: a dictionary from a name to a function, filled by a decorator.

```python
import math

SHAPES = {}

def register(name):
    def deco(fn):
        SHAPES[name] = fn
        return fn
    return deco

@register("circle")
def circle(r):
    return math.pi * r * r

@register("square")
def square(s):
    return s * s

def area(kind, *args):
    try:
        fn = SHAPES[kind]
    except KeyError:
        raise ValueError(f"unknown shape {kind!r}; known: {sorted(SHAPES)}") from None
    return fn(*args)

print(round(area("circle", 1), 3), area("square", 3))

@register("rect")            # a NEW shape, written later, anywhere
def rect(w, h):
    return w * h

print(area("rect", 2, 5))
try:
    area("hexagon", 1)
except ValueError as e:
    print(e)
```
```text
3.142 9
10
unknown shape 'hexagon'; known: ['circle', 'rect', 'square']
```

`area` was never edited when `rect` appeared; the new shape could live in another file, even another package. The error message lists the known names, which turns a typo into an instant fix. (`from None` hides the confusing `KeyError` chain, core.12.)

The **object-oriented form** is polymorphism: give every shape class an `area()` method and call `shape.area()`. No registry is needed because the object knows how to do the work. Use methods when you own the classes; use a registry when the choice comes from **data** (a string from a config file or the command line).

**When not to.** Two cases are not worth a registry. If the choice has two stable branches that will never grow, an `if` is clearer. And do not use the registry just to *look* extensible, as section 12 explains.

### 6.4 L: Liskov substitution

**The pain.** A subclass "is-a" its parent in the real world, but the code that works with the parent breaks when it receives the child.

```python
class Rectangle:
    def __init__(self, w, h):
        self._w, self._h = w, h
    @property
    def w(self): return self._w
    @w.setter
    def w(self, v): self._w = v
    @property
    def h(self): return self._h
    @h.setter
    def h(self, v): self._h = v
    def area(self): return self._w * self._h

class Square(Rectangle):             # a square IS a rectangle, in geometry
    def __init__(self, s):
        super().__init__(s, s)
    @Rectangle.w.setter
    def w(self, v): self._w = self._h = v
    @Rectangle.h.setter
    def h(self, v): self._w = self._h = v

def stretch(rect):
    rect.w = 5
    rect.h = 2
    return rect.area()

print(stretch(Rectangle(1, 1)), stretch(Square(1)))
```
```text
10 4
```

`stretch` is written for rectangles: "set width 5, height 2, area is 10". Handed a `Square`, setting `h = 2` also changes `w`, and the area is 4. The subclass broke a **promise** the base class made implicitly: the two sides change independently.

A second, very common form of the same violation is a subclass that is stricter than its parent:

A second, very common form is a subclass that is **stricter** than its parent. `Stack.push(x)` always succeeds; `LimitedStack(Stack)` overrides `push` to raise `OverflowError("full")` after two items. A function `fill(s)` that pushes three items works for `Stack` (it returns `3`) and fails with `OverflowError full` for `LimitedStack`. Code written against the parent is broken by a legal-looking subclass.

**The principle.** If `B` is a subclass of `A`, then anywhere the code expects an `A`, it must be able to use a `B` **without knowing** and without surprise. In practice a subclass may:

- accept **more** (looser inputs) but not less;
- promise **more** (stronger outputs) but not less;
- raise **no new kinds of exception** the base class did not say it could raise;
- keep the base class's **invariants** (the things always true).

**The fix.** Do not force the "is-a". Options: use **composition** (a `Square` *has* a size and offers `area()`, without inheriting settable `w` and `h`); make both classes **immutable** so there are no setters to contradict; or make the base class *honest* (`Stack` has a documented `push` that may raise `OverflowError`, so `fill` must handle it). The test question: **"If I replace the parent with the child in the callers, which call breaks?"**

**When not to worry.** Liskov is about code that is **written against the base class**. If nobody uses the base class polymorphically, the hierarchy is only code sharing, and composition may be the better tool anyway.

### 6.5 I: interface segregation and small Protocols

**The pain.** A big interface forces every implementer to stub out things it cannot do.

```python
class ReadOnlyStore(Storage):          # Storage: an ABC with read, write, delete
    def read(self): return "x"
    def write(self, t): raise NotImplementedError("read-only")
    def delete(self): raise NotImplementedError("read-only")
```

The read-only class is forced to *claim* abilities it does not have. A function that takes a `Storage` cannot know whether `delete` is real. (That is also a Liskov violation: a trap waiting for a caller.)

**The naive fix**: leave the stubs and write "do not call this" in a comment.

**The idea.** Define **small** interfaces, each describing one ability, and make each function depend only on the ability it uses. In Python, `typing.Protocol` (core.16) does it with no inheritance at all:

```python
from typing import Protocol, runtime_checkable

@runtime_checkable
class Reader(Protocol):
    def read(self) -> str: ...

@runtime_checkable
class Writer(Protocol):
    def write(self, text: str) -> None: ...

class StringBox:
    def __init__(self, s=""): self.s = s
    def read(self): return self.s
    def write(self, text): self.s = text

class ReadOnly:
    def read(self): return "fixed"

def shout(src: Reader) -> str:        # needs only reading
    return src.read().upper()

print(shout(StringBox("hi")), shout(ReadOnly()))
print(isinstance(ReadOnly(), Reader), isinstance(ReadOnly(), Writer), isinstance(StringBox(), Writer))
```
```text
HI FIXED
True False True
```

`shout` accepts anything that can read, and a type checker rejects a class that cannot. `ReadOnly` never pretends to write. `runtime_checkable` lets `isinstance` look for the *methods* (it checks they exist, not their signatures).

**Why it helps testing.** To test `shout` you need only a fake with a `read` method, not a full storage implementation.

**When not to.** One class with five related methods, used as a whole by all its callers, does not need to be split into five Protocols. Segregate when different callers use different slices.

### 6.6 D: dependency inversion

**The pain.** A function that creates or reaches for its own collaborators (the clock, a random generator, a database, a file) cannot be tested or reused without the real thing.

```python
import datetime

def is_expired(token):
    return datetime.datetime.now() > token["expires"]
```

To test this you would need to wait for real time to pass. The function is welded to the system clock.

**The idea.** **High-level logic should not depend on low-level details. Both should depend on an abstraction**, and the details should be *handed in*. In Python the abstraction is often just "a callable" or "an object with this method", and "handing in" is a parameter with a sensible default:

```python
import datetime
import random

def is_expired(token, now=None):
    now = now or datetime.datetime.now()
    return now > token["expires"]

tok = {"expires": datetime.datetime(2020, 1, 1)}
print(is_expired(tok, now=datetime.datetime(2019, 12, 31)))
print(is_expired(tok, now=datetime.datetime(2021, 1, 1)))

def pick(options, rng=random):
    return rng.choice(options)

class FakeRng:
    def choice(self, seq):
        return seq[0]

print(pick(["a", "b"], FakeRng()))
print(pick(["a", "b", "c"], random.Random(7)))
```
```text
False
True
a
b
```

Normal callers still write `is_expired(token)` and get the real clock. A test passes any `now` it likes. `pick` takes anything with a `choice` method: the real `random` module, a seeded `random.Random(7)` (always the same answer), or a fake. Section 8 builds this idea up to whole applications.

**When not to.** Do not inject things that never change and are cheap and pure (`math.sqrt`). Inject what is **slow, random, global, or has side effects**: time, randomness, network, files, databases, email.

#### Try it 6.1

Which principle does each complaint point to?

1. "To add a new payment type I must edit `pay()` and three other functions."
2. "`ReadOnlyList` inherits from `MyList` but raises `TypeError` in `append`."
3. "I cannot test `report()` without a real database."
4. "`handle_request` parses the URL, checks the password, formats the HTML and writes the log."

<details><summary>Answer</summary>

1. **O** (open/closed): replace the chain with a registry or give each payment type a method.
2. **L** (Liskov): code that appends to a `MyList` breaks for the subclass; use composition or a separate read-only type.
3. **D** (dependency inversion): pass the database (or a `Reader`/repository object) into `report`.
4. **S** (single responsibility): four reasons to change; split into parse, authenticate, render, log.

</details>

## 7. Design patterns, problem first

A **design pattern** is a named, reusable solution to a problem that keeps coming back. The famous catalog (the "Gang of Four" book) has 23 patterns, written in 1994 for C++ and Smalltalk. Many of them exist to work around missing language features. In Python, with first-class functions, modules and duck typing, several shrink to one line.

We take five patterns that you will use, each as: **pain, naive code, pattern, Pythonic shortcut, when not to**. Then three short notes.

### 7.1 Strategy: swap the rule, keep the process

**The pain.** The same process (checkout) with a rule that varies (the discount). The first version picks the rule by name inside the function.

```python
def checkout(items, discount="none"):
    total = sum(items)
    if discount == "ten_percent":
        return total * 0.9
    elif discount == "flat5":
        return max(total - 5, 0)
    elif discount == "none":
        return total
    raise ValueError(discount)

print(checkout([20, 30], "ten_percent"))
```
```text
45.0
```

Every new discount edits `checkout` (open/closed again), and `checkout` knows about all discount rules (single responsibility again).

**The pattern.** **Strategy**: define a family of interchangeable algorithms and let the caller choose. In the classic version each algorithm is a class with the same method. In Python, a strategy is just **a function**: the "interface" is its signature `(total) -> new_total`.

```python
def percent_off(p):
    return lambda total: total * (1 - p / 100)

def flat_off(n):
    return lambda total: max(total - n, 0)

def no_discount(total):
    return total

def checkout(items, strategy=no_discount):
    return strategy(sum(items))

print(checkout([20, 30], percent_off(10)))
print(checkout([20, 30], flat_off(60)))
print(checkout([20, 30]))
print(checkout([20, 30], lambda t: t - 1))
```
```text
45.0
0
50
49
```

`percent_off(10)` is a **function factory**: it returns the strategy (a closure, section 5.2). `checkout` never changes when a new rule appears; the last line shows a one-off rule written inline with `lambda`, no class at all. Python's own `sorted(key=...)` is the strategy pattern.

**When not to.** Use a class-based strategy only if the strategy needs **several methods** or **its own state and configuration** that callers inspect. A strategy class with one method named `execute` is a function in disguise.

### 7.2 Factory: one place that knows how to build things

**The pain.** Code scattered everywhere decides which class to create.

```python
if fmt == "json":
    exp = JsonExporter()
elif fmt == "csv":
    exp = CsvExporter()
# ... same chain pasted in three other modules
```

**The pattern.** A **factory** is the *one* place that turns a description ("json") into an object. Combine it with the registry from section 6.3 and it also follows open/closed:

```python
import json

EXPORTERS = {}

def exporter(fmt):
    def deco(cls):
        EXPORTERS[fmt] = cls
        return cls
    return deco

@exporter("json")
class JsonExporter:
    def export(self, rows):
        return json.dumps(rows)

@exporter("csv")
class CsvExporter:
    def export(self, rows):
        return "\n".join(",".join(map(str, r.values())) for r in rows)

def create_exporter(fmt):
    try:
        return EXPORTERS[fmt]()
    except KeyError:
        known = ", ".join(sorted(EXPORTERS))
        raise ValueError(f"unknown format {fmt!r}, known: {known}") from None

rows = [{"a": 1, "b": 2}]
print(create_exporter("json").export(rows))
print(create_exporter("csv").export(rows))
try:
    create_exporter("xml")
except ValueError as e:
    print(e)
```
```text
[{"a": 1, "b": 2}]
1,2
unknown format 'xml', known: csv, json
```

**The Pythonic shortcut: classes are objects.** In Python, `JsonExporter` itself is a callable that builds an instance, so `EXPORTERS["json"]()` already *is* a factory, no `AbstractFactory` hierarchy needed. The other Pythonic factory is the **alternative constructor**: a `@classmethod` that builds an object from another representation:

```python
class Money:
    def __init__(self, cents):
        self.cents = cents

    @classmethod
    def from_string(cls, text):
        whole, _, frac = text.lstrip("$").partition(".")
        return cls(int(whole) * 100 + int((frac + "00")[:2]))

    def __repr__(self):
        return f"{type(self).__name__}({self.cents})"

class Euro(Money):
    pass

print(Money.from_string("$3.5"), Euro.from_string("12.07"))
```
```text
Money(350) Euro(1207)
```

Because the method uses `cls(...)` and not `Money(...)`, a subclass gets *its own type* back. That is why alternative constructors are `@classmethod`, not `@staticmethod` (compare `dict.fromkeys`, `datetime.fromisoformat`).

**When not to.** If only one class ever exists, call it directly. A factory is for the moment where *the caller should not know* which concrete class it gets.

### 7.3 Observer: tell whoever is interested

**The pain.** An event happens (a user signs up) and many unrelated things must react: send mail, update stats, write a log. The naive version makes the signup code know every reaction.

The naive version is one `signup` function that saves the user, then sends the email, then updates the stats, then writes the log, each as a direct call:

```text
saved asha
email asha
stats asha
log asha
```

Add "notify sales" and you edit `signup`. Remove the mailer in tests and you edit `signup`. The core knows about the shell.

**The pattern.** **Observer** (also publish/subscribe): the publisher keeps a list of subscribers and calls them, without knowing who they are. A complete event bus in Python is about 15 lines:

```python
class EventBus:
    def __init__(self):
        self._handlers = {}

    def subscribe(self, event, fn):
        self._handlers.setdefault(event, []).append(fn)
        def unsubscribe():
            self._handlers[event].remove(fn)
        return unsubscribe

    def publish(self, event, **data):
        errors = []
        for fn in list(self._handlers.get(event, [])):
            try:
                fn(**data)
            except Exception as exc:
                errors.append(exc)
        return errors

bus = EventBus()

def log(**d):
    print("log", d)

def mail(**d):
    raise RuntimeError("smtp down")

def stats(**d):
    print("stats", d["user"])

bus.subscribe("signup", log)
bus.subscribe("signup", mail)
off = bus.subscribe("signup", stats)

print(bus.publish("signup", user="asha"))
off()
print(bus.publish("signup", user="ben"))
```
```text
log {'user': 'asha'}
stats asha
[RuntimeError('smtp down')]
log {'user': 'ben'}
[RuntimeError('smtp down')]
```

Four design choices are worth noticing, because each guards against a real bug:

1. **Handlers are plain functions**: no `Observer` base class (a callable *is* the interface).
2. **`list(...)` copies** the handler list before looping, so a handler that unsubscribes during `publish` does not corrupt the loop.
3. **One failing handler does not stop the rest**: `mail` raised, yet `stats` still ran. The errors are collected and returned, not hidden.
4. **`subscribe` returns an `unsubscribe` function**, a closure that remembers `event` and `fn`, so callers never need to hold the bus and the names.

**When not to.** Observers make the flow of control **invisible**: reading `signup` no longer tells you what happens. Debugging "who changed this?" gets harder. For two or three fixed reactions that always happen, just call them. Use events when the set of listeners really varies or comes from plugins.

### 7.4 Adapter: make an old thing fit a new shape

**The pain.** You have code that expects one interface, and a library (or a legacy class you may not edit) that offers another.

```python
class LegacySensor:
    def read_fahrenheit_string(self):
        return "72.5F"

def monitor(sensor):                 # wants sensor.celsius() -> float
    c = sensor.celsius()
    return "hot" if c > 30 else f"ok {c}"
```

**The naive fix**: edit `LegacySensor` (maybe it belongs to another team, or a vendor library), or rewrite `monitor` to know about Fahrenheit strings (now it knows about *every* sensor kind).

**The pattern.** An **adapter** wraps the old object and presents the new interface. It translates, and does nothing else.

```python
class FahrenheitAdapter:
    def __init__(self, legacy):
        self._legacy = legacy

    def celsius(self):
        text = self._legacy.read_fahrenheit_string().rstrip("F")
        return round((float(text) - 32) * 5 / 9, 2)

print(monitor(FahrenheitAdapter(LegacySensor())))
```
```text
ok 22.5
```

`monitor` is unchanged, and `LegacySensor` is unchanged. And often the shortest adapter is **no adapter**: change `monitor` to accept a **function** (`monitor(read_celsius)`), so that anything callable can be plugged in with a one-line `lambda`.

**When not to.** If you own both sides, change one of them instead of adding a translation layer. Adapters are for code you cannot or should not edit: third-party libraries, legacy modules, another team's service.

### 7.5 Command: an action as an object

**The pain.** You need to **record, delay, repeat or undo** actions, but your code performs them directly (`editor.text += "x"`), so after the call nothing remains that you could undo.

**The pattern.** **Command**: turn each action into an object that knows how to `do()` and `undo()` itself. A `History` runs commands and keeps them on two stacks:

```python
class Editor:
    def __init__(self):
        self.text = ""

class Insert:
    def __init__(self, ed, s):
        self.ed, self.s = ed, s
    def do(self):
        self.ed.text += self.s
    def undo(self):
        self.ed.text = self.ed.text[:-len(self.s)]

class History:
    def __init__(self):
        self.done, self.undone = [], []

    def run(self, cmd):
        cmd.do()
        self.done.append(cmd)
        self.undone.clear()          # a new action ends the redo chain

    def undo(self):
        if not self.done:
            return False
        cmd = self.done.pop()
        cmd.undo()
        self.undone.append(cmd)
        return True

    def redo(self):
        if not self.undone:
            return False
        cmd = self.undone.pop()
        cmd.do()
        self.done.append(cmd)
        return True

ed, h = Editor(), History()
h.run(Insert(ed, "Hello"))
h.run(Insert(ed, " world"))
print(repr(ed.text))
h.undo()
print(repr(ed.text))
h.redo()
print(repr(ed.text))
h.undo()
h.run(Insert(ed, "!"))
print(repr(ed.text), h.redo())
h.undo()
h.undo()
print(repr(ed.text), h.undo())
```
```text
'Hello world'
'Hello'
'Hello world'
'Hello!' False
'' False
```

Walk through the 4th line: after `h.undo()` the text was `'Hello'` and `" world"` sat on the `undone` stack. Running a **new** command (`"!"`) clears `undone`, so `redo()` returns `False`: you cannot "redo" an action from a timeline that no longer exists. The last line: both inserts are undone, the text is empty, and a third `undo()` has nothing to do and returns `False` instead of raising.

**The Pythonic shortcut.** If you do **not** need undo, a command is just a **function stored in a list**:

```python
queue = []
queue.append(lambda: print("job 1"))
queue.append(lambda: print("job 2"))
for job in queue:
    job()
```
```text
job 1
job 2
```

`functools.partial(send_mail, to, text)` packages a call with its arguments for later. A command **class** earns its place only when each action needs more than "run": undo, a name for logging, saving to disk, or combining many into one **macro** (its `do` runs a list of commands, its `undo` runs their `undo` in **reverse** order).

### 7.6 Three short notes

**Singleton: use a module.** The pattern says "exactly one instance of a class". In Python, a module is imported once and then shared, so a module-level object *is* a singleton, with no machinery (`settings = {...}` in `config.py`, then `from config import settings` everywhere gives every importer the same object).

The `__new__`-based singleton class is almost never needed (see section 12). Remember the cost: any shared global object is **hidden shared state** (section 8.4). Prefer passing the object in.

**Template method: a skeleton with holes.** A base class fixes the steps (`render` calls `header`, `body`, a footer) and subclasses fill in one or two. Often passing the varying steps as **functions** (strategy again) is simpler: `render(header, body)`. Prefer functions unless several steps vary together and inheritance already fits.

**Null object: do nothing on purpose.** Optional collaborators lead to `if logger is not None:` before every use. Instead, provide a collaborator that does nothing:

```python
class NullLogger:
    def info(self, msg):
        pass

class PrintLogger:
    def info(self, msg):
        print("INFO", msg)

def work(n, logger=NullLogger()):
    logger.info(f"working on {n}")
    return n * 2

print(work(3))
print(work(3, PrintLogger()))
```
```text
6
INFO working on 3
6
```

`work` has no `None` checks and does not care whether anyone listens. The standard library does the same: `logging.NullHandler`, `contextlib.nullcontext`, `io.StringIO` as a throwaway file. A `NullLogger()` default is safe to share here because it has no state; a null object that *remembers* things would be the mutable-default trap of section 3.1.

#### Try it 7.1

After this code runs, what is `bus.publish("x")` going to return, and which lines print?

```python
bus = EventBus()                 # the class from section 7.3
def a(**d): print("a")
def b(**d): raise ValueError("bad")
def c(**d): print("c")
bus.subscribe("x", a)
off = bus.subscribe("x", b)
bus.subscribe("x", c)
off()
print(bus.publish("x"))
```

<details><summary>Answer</summary>

```text
a
c
[]
```

`off()` removed `b` before publishing, so no error occurs and the returned list is empty. Handlers run in the order they subscribed (`a`, then `c`). If you remove the `off()` line, `b` still runs between them, and the result is `[ValueError('bad')]` while `c` still prints.

</details>

#### Try it 7.2

Using the `Editor`, `Insert` and `History` from section 7.5, what is `ed.text` at the end?

```python
ed, h = Editor(), History()
h.run(Insert(ed, "ab"))
h.run(Insert(ed, "cd"))
h.undo()
h.redo()
h.undo()
h.run(Insert(ed, "X"))
h.redo()
```

<details><summary>Answer</summary>

`'abX'`. After the two runs the text is `'abcd'`; `undo` makes it `'ab'`; `redo` makes it `'abcd'`; `undo` makes it `'ab'` again. Running `Insert("X")` gives `'abX'` and clears the redo stack, so the last `redo()` finds nothing and returns `False`; the text stays `'abX'`.

</details>

#### Try it 7.3

You call `create_exporter("xml")` from section 7.2 after registering a new `"xml"` exporter in another file that was **never imported** by your program. What happens, and what does this teach about registries?

<details><summary>Answer</summary>

You get `ValueError: unknown format 'xml', known: csv, json`. The `@exporter("xml")` decorator only runs when its module is **imported**. A registry is filled by import side effects, so you must make sure the plugin modules are imported (explicitly, or by a function that scans a package with `importlib`). The helpful error message, which lists the known names, is what lets you find this bug in seconds.

</details>

## 8. Dependency injection without frameworks

### 8.1 The pain: code that builds its own world

Java and C# have large "dependency injection frameworks". In Python you almost never need one, because the idea underneath is tiny: **do not create your collaborators inside; receive them from outside.**

Look at a signup service that builds everything it needs inside `__init__` (`self.mailer = SmtpMailer("smtp.example.com")`, a real database) and calls `datetime.datetime.now()` inside `signup`.

To test `signup` you would send a real email and depend on the real time. To reuse the service with a different mailer you must edit the class. The service is **welded** to its environment.

### 8.2 Three ways to hand things in

**1. Parameters.** For one-off collaborators, pass them to the function, as with `now` and `rng` in section 6.6; a default keeps the common call short.

**2. Constructor injection.** For a class, take the collaborators in `__init__` and store them. The class now says in its signature **what it needs**:

```python
class SignupService:
    def __init__(self, repo, mailer, clock):
        self.repo, self.mailer, self.clock = repo, mailer, clock
    # signup() uses self.repo, self.mailer, self.clock (full code in 8.3)
```

Nothing in the class names a concrete mailer or knows what a clock is: `clock` is "any function that returns a time", `mailer` is "anything with `send(to, text)`", `repo` is "anything that supports `repo[key] = value`". These are tiny, implicit interfaces, exactly the Protocols of section 6.5.

**3. Default arguments for the real thing.** In a public function, a default of the real implementation (`rng=random`, `opener=open`) means normal callers do nothing special and tests substitute fakes.

### 8.3 The composition root: wire everything in one place

If every class receives its parts from outside, *somebody* must create the real parts and connect them. That place is the **composition root**: usually `main()` or a function like `build_app(config)`. It is the only place that knows which concrete classes exist.

```python
import datetime

class Mailer:
    def send(self, to, text):
        print("REAL MAIL", to)

class FakeMailer:
    def __init__(self):
        self.sent = []
    def send(self, to, text):
        self.sent.append((to, text))

class SignupService:
    def __init__(self, repo, mailer, clock):
        self.repo, self.mailer, self.clock = repo, mailer, clock
    def signup(self, email):
        self.repo[email] = self.clock()
        self.mailer.send(email, "welcome")
        return "ok"

def build_app(env):
    if env == "test":
        return SignupService({}, FakeMailer(), lambda: "2025-01-01")
    return SignupService({}, Mailer(), datetime.datetime.now)

svc = build_app("test")
print(svc.signup("a@x.com"), svc.mailer.sent, svc.repo)
```
```text
ok [('a@x.com', 'welcome')] {'a@x.com': '2025-01-01'}
```

A test can now say, with no patching: the signup stored the email with *this exact time*, and sent *exactly this one message*. That is the "best seam" you saw in core.19, section 7. This is also why `unittest.mock.patch` is a last resort: it reaches into modules to replace things that should have been parameters.

The rule of thumb for layering: **the core never imports the shell.** Business functions take plain values and collaborators; only `main`/`build_app` imports `smtplib`, opens files and reads `sys.argv`.

### 8.4 Why globals hurt

The opposite of injection is **global state**: a module-level variable that functions read and change.

```python
_counter = 0

def next_id():
    global _counter
    _counter += 1
    return _counter

print(next_id(), next_id())
```
```text
1 2
```

It works, until: a test calls `next_id()` and the result depends on every earlier test (test order changes the outcome); two threads call it at once (the race condition of core.21); you need two independent counters (impossible). Keep the state **inside an object or a closure** (`make_ids(start=0)` returns a `next` function with its own `nonlocal n`), and each test makes its own counter. A module-level **constant** (`MAX_RETRIES = 3`) is fine; a module-level **mutable thing that functions change** is the problem.

### 8.5 When not to inject

- **Pure, cheap, deterministic helpers** (`math.sqrt`, `str.upper`) need no injection.
- **Do not build a framework** (a "container" that wires classes by name) for a program you can wire in 20 lines in `main`.
- **Do not inject for the sake of it.** If a class takes eleven collaborators, the cure is not a container; it is that the class has too many responsibilities (section 6.2).

#### Try it 8.1

Rewrite this function so a test can check it without waiting and without a real random number, and say what the test passes in.

```python
import random
def pick_greeting(names):
    return "hello " + random.choice(names)
```

<details><summary>Answer</summary>

```python
import random

def pick_greeting(names, rng=random):
    return "hello " + rng.choice(names)
```

A test passes a fake with a `choice` method, or a seeded generator `random.Random(7)`, and checks the exact result. Callers who do not care still write `pick_greeting(names)`. The default `rng=random` is safe as a default because the `random` module is not mutated by the function.

</details>

## 9. Clean code

"Clean code" is not a style guide; it is the habit of writing code so that **the next change is cheap**. The advice is a list of small things that, together, remove most of the confusion from code.

### 9.1 Names

A name is the cheapest documentation you will ever write. Good names say **what** and avoid **how**.

```python
def do_stuff(d, f, x):          # what stuff? what are d, f, x?
    ...

def total_price(prices, tax_rate):
    return sum(prices) * (1 + tax_rate)

print(total_price([10, 20], 0.2))
```
```text
36.0
```

Practical rules: name by **meaning**, not type (`users`, not `user_list`); functions are **verbs** (`parse_order`), values and classes are **nouns**; booleans read as questions (`is_valid`, not `flag`); a name's length should match its scope (`i` in a 3-line loop is fine, a module-level `d` is not). If you cannot name it, you probably do not understand it yet, or it does two things.

### 9.2 Small functions, one level of abstraction

A function should do **one thing at one level of abstraction**. A loop that sums amounts, a format string and a call that emails the boss do not belong in the same function: the loop and format string are details, "send the report" is the idea. Extract `total_amount(rows)` and `report_body(total)`, and `send_report` reads like a sentence.

**Flat beats nested.** Deep `if` nesting forces the reader to hold five conditions in mind. Use **guard clauses** (early returns) to handle the odd cases first and leave the main path unindented:

```python
def classify(age, member, coupon):
    if age is not None:
        if age >= 0:
            if member:
                if coupon:
                    return "gold+coupon"
                else:
                    return "gold"
            else:
                return "guest"
        else:
            return "invalid"
    else:
        return "invalid"

def classify2(age, member, coupon):
    if age is None or age < 0:
        return "invalid"
    if not member:
        return "guest"
    return "gold+coupon" if coupon else "gold"

cases = [(None, 1, 1), (-1, 1, 1), (5, 0, 0), (5, 1, 0), (5, 1, 1)]
print([classify(*c) for c in cases] == [classify2(*c) for c in cases])
print([classify2(*c) for c in cases])
```
```text
True
['invalid', 'invalid', 'guest', 'gold', 'gold+coupon']
```

The two functions agree on every case we tried, but the second reads top to bottom with at most one level of indentation. A rough guide for limits: **functions under about 20 lines, nesting at most 3 deep, at most 4 parameters.** These are alarms, not laws.

### 9.3 Side effects and surprises

A function with **no side effects** (it only computes and returns) is easy to test and reason about. A function that *also* changes its argument, a global, a file or the screen is full of surprises:

```python
def apply_discount(order):
    order["total"] = order["total"] * 0.9      # changes the caller's dict!

o = {"total": 100}
apply_discount(o)
apply_discount(o)
print(o)
```
```text
{'total': 81.0}
```

The caller called it twice and got 19% off, not 10%. The function's name says nothing about changing `o`. The pure version returns a **new** value:

```python
def with_discount(order):
    return {**order, "total": order["total"] * 0.9}

o = {"total": 100}
print(with_discount(o), o)
```
```text
{'total': 90.0} {'total': 100}
```

The original is untouched, so calling twice is harmless and the caller sees the change because it asks for it (`order = with_discount(order)`). Rule: **either a function computes and returns, or it changes something and returns nothing (or says so in its name, `save_`, `update_`, `send_`). Avoid doing both.** Python's own `list.sort()` (changes, returns `None`) versus `sorted()` (returns a new list) follows this rule.

### 9.4 Comments

A comment that repeats the code is noise, and worse, it goes out of date:

```python
# loop through d
for i in d:
    ...
```

Write comments for **why**, never for what: the business rule, the workaround, the unexpected constraint ("the warehouse API returns ounces for orders before 2019").

If you feel a comment is needed to explain *what* a block does, extract that block into a function whose name is the comment.

### 9.5 Errors

- **Raise exceptions; do not return error codes or `None`.** A function that returns `None` for "not found" forces every caller to remember a check, and forgetting it produces a distant `AttributeError`:

```python
def find_user(users, name):
    for u in users:
        if u == name:
            return u
    return None

print(find_user(["a"], "b").upper() if find_user(["a"], "b") else "none")

class UserNotFound(LookupError):
    pass

def find_user2(users, name):
    if name in users:
        return name
    raise UserNotFound(name)

try:
    find_user2(["a"], "b")
except LookupError as e:
    print(type(e).__name__, e)
```
```text
none
UserNotFound b
```

A custom exception inheriting from a built-in (`LookupError`) lets callers catch it narrowly or broadly.

- **Do not return mixed types** (an `int` on success, a `str` such as `"bad"` on failure): `parse("x") + 1` then fails far away with a `TypeError`. Always return an `int` and raise on bad input, or always return `int | None` and say so in the type hint.

- **Fail early, with a useful message.** Check arguments at the top (`if rate < 0: raise ValueError(f"rate must be >= 0, got {rate}")`), not after three steps of work.

### 9.6 The cost of abstraction

Every function, class and layer you add is something the next reader must open, read and understand. An abstraction **pays** when it removes more complexity than it adds. A one-line wrapper around a one-line call adds a name to learn and a jump to follow. Before extracting, ask: does the new name tell me something I could not see before? Before adding a layer, ask: what would change if I did not?

#### Try it 9.1

Why is the second call a surprise for the caller? What does it print?

```python
def apply_discount(order):
    order["total"] = order["total"] * 0.9

o = {"total": 100}
apply_discount(o)
apply_discount(o)
print(o)
```

<details><summary>Answer</summary>

`{'total': 81.0}`. The function **mutates the caller's dict**, so each call stacks another 10% off. The fix is a pure function that returns a new dict, `return {**order, "total": order["total"] * 0.9}`; calling it twice with the same input then gives the same result.

</details>

## 10. Refactoring safely

### 10.1 What refactoring is

**Refactoring** means changing the *structure* of code **without changing its behavior**. That second half is the whole point. If behavior changes, it is not a refactor; it is a rewrite or a bug fix, and it should be done separately, in its own step.

The danger is that "I cleaned it up" and "I accidentally changed it" look the same until a customer finds out. Here is a refactor that looks harmless. The original:

```python
def shipping_old(weight):
    if weight > 10:
        return 20
    elif weight > 5:
        return 10
    else:
        return 5
```

"Let me make this table-driven":

```python
RATES = [(10, 20), (5, 10), (0, 5)]

def shipping_new(weight):
    for limit, cost in RATES:
        if weight >= limit:
            return cost
```

Compare them on the boundary values:

```python
for w in [0, 5, 7, 10, 11]:
    print(w, shipping_old(w), shipping_new(w))
```
```text
0 5 5
5 5 10
7 10 10
10 10 20
11 20 20
```

At `w = 5` and `w = 10` the new function charges more. The old code used `>` ("over 10"), the new table used `>=`. A reviewer reading the diff would likely miss it. A **test** would not.

### 10.2 Step zero: characterization tests

If there are no tests, or the tests do not cover the code you are about to touch, **write tests first**, but with a twist. You do not yet know what the code is *supposed* to do; you only know what it *does*. A **characterization test** (also called a golden test or approval test) records the current behavior, whatever it is, and pins it down.

Recipe:

1. Pick **inputs** that cover: a typical case, the empty case, the single case, each branch, **boundaries** (the exact values at `>` / `>=`), and bad input.
2. **Run the existing code** and record its output.
3. Write a test that asserts exactly that output.
4. Only now change the code, run the tests after **each small step**.

```python
def legacy_label(n):
    if n % 15 == 0: return "fizzbuzz"
    if n % 3 == 0: return "fizz"
    if n % 5 == 0: return "buzz"
    return str(n)

inputs = [0, 1, 3, 5, 15, -3, 30]
golden = {n: legacy_label(n) for n in inputs}
print(golden)
```
```text
{0: 'fizzbuzz', 1: '1', 3: 'fizz', 5: 'buzz', 15: 'fizzbuzz', -3: 'fizz', 30: 'fizzbuzz'}
```

Paste that dictionary into a test (`assert label(n) == expected` for each pair) and you have a safety net. Notice the values for `0` and `-3`: perhaps nobody *intended* them, but callers may depend on them. You decide *separately* whether to change them. If a characterization test records a result you believe is a bug, **write the bug into the test with a comment**, refactor, and fix the bug as a separate commit.

Tests for an old script that reads input and prints can be **end to end**: run the program with `subprocess`, feed it text, compare its output. Section 11 does exactly that.

### 10.3 A catalog of smell-to-move

Most refactorings are one of a handful of moves. Learn these and you can handle most code:

| Smell | Move | Example |
|---|---|---|
| a block with a comment saying what it does | **Extract function** (the comment becomes the name) | `# compute total` becomes `total = total_amount(rows)` |
| a tiny function whose body is as clear as its name | **Inline function** | replace `is_even(n)` by `n % 2 == 0` if used once |
| a vague name | **Rename** (variable, function, parameter) | `d` becomes `days_late` |
| an `if/elif` chain choosing by a key | **Replace conditional with a table** (dict) or registry | section 6.3 |
| an `if/elif` chain choosing by type | **Replace conditional with polymorphism** | `shape.area()` |
| several values always passed around together | **Introduce a data class** | `title, days, kind` becomes `Loan` |
| magic numbers (`0.25`, `14`) | **Name the constant** or move to a table | `GRACE_DAYS = 14` |
| a function that does I/O and calculation | **Separate pure core from I/O shell** | section 6.2 |
| a hard-coded collaborator (clock, file) | **Inject it** | section 8 |
| nested `if` | **Guard clauses** / early return | section 9.2 |
| copy-paste | **Parameterize** the difference | section 3.8 |

### 10.4 When to stop

Refactoring has no natural end, which is why you need a stopping rule. Stop when:

- the code **does what you need to change next** without a fight (the real goal: your next change is easy);
- the remaining ugliness is in code **nobody touches** (working legacy code that never changes is not costing you anything);
- a further step would add an abstraction **without removing a real problem**;
- you are refactoring to avoid starting the actual task.

A practical rule from the field: *make the change easy (warning: this may be hard), then make the easy change.* Refactor only as much as the next change needs, and leave the area a little cleaner than you found it.

#### Try it 10.1

The table-driven `shipping_new` charged more at `w = 5`. Fix `RATES` and the comparison so the behavior matches `shipping_old` exactly, and name the boundary test values that would have caught the bug.

<details><summary>Answer</summary>

Keep the table, but use `>` in the loop: `if weight > limit: return cost`. The table `[(10, 20), (5, 10)]` plus a final fallback `5` then matches (the `(0, 5)` row is replaced by a fallback, or kept as `(-1, 5)` or `float("-inf")`, because `0 > 0` is false). The boundary values `5` and `10` (and `0`) catch the bug; the values 7 and 11 pass both versions and prove nothing. Always test the value **at** each boundary, one below and one above.

</details>

## 11. Worked refactor: a legacy script becomes a clean module

This section puts everything together. We take a real-looking messy script, pin its behavior with tests, and clean it in four small steps. **The tests are green at every step.** The module project (problem `core.22.p030`) asks you to do the same job on a *different* script (an inventory report), so here we use a library-fines script. The moves are the same; the details are yours to find.

### 11.1 The legacy script

A librarian's helper. It reads commands from the keyboard: `add <title> <days_late> <kind>`, `report`, `quit`. A book has 14 days of grace, then costs 0.25 per day, capped at 10.00; a DVD has 3 days of grace, then 1.00 per day, capped at 20.00.

```python
# /home/you/library/fines.py  (legacy version)
data = []


def go():
    while True:
        line = input()
        if line == "quit":
            break
        parts = line.split()
        if parts[0] == "add":
            data.append([parts[1], int(parts[2]), parts[3]])
            print("added " + parts[1])
        elif parts[0] == "report":
            t = 0
            for d in data:
                if d[2] == "book":
                    f = (d[1] - 14) * 0.25
                    if f < 0:
                        f = 0
                    if f > 10:
                        f = 10
                    print(d[0] + ": " + "%.2f" % f)
                    t = t + f
                elif d[2] == "dvd":
                    f = (d[1] - 3) * 1.0
                    if f < 0:
                        f = 0
                    if f > 20:
                        f = 20
                    print(d[0] + ": " + "%.2f" % f)
                    t = t + f
                else:
                    print("unknown kind " + d[2])
            print("total: " + "%.2f" % t)
        else:
            print("unknown command " + parts[0])


go()
```

Run it with some input:

```text
$ printf 'add Dune 20 book\nadd Film 6 dvd\nadd Map 9 atlas\nreport\nquit\n' | python fines.py
added Dune
added Film
added Map
Dune: 1.50
Film: 3.00
unknown kind atlas
total: 4.50
```

It works. Count the smells from section 3: a module-level mutable `data` (section 8.4); everything in one function, mixing input, parsing, rules, arithmetic and printing (3.3, 6.2); a record stored as a list where `d[1]` means "days late" (section 4); stringly typed kinds (3.4); copy-pasted blocks for book and DVD (3.8); `input` and `print` welded in, so nothing can be tested without a subprocess (6.6); the mystery names `t`, `f`, `d` (9.1).

### 11.2 Step 0: write characterization tests, run them on the legacy code

Because the script reads standard input and prints, the first tests are end to end: run it as a program, feed it text, compare the output lines. This test file will stay **unchanged** for the whole refactor, which is exactly what makes it a safety net.

```python
# test_fines.py
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent


def run(*lines):
    result = subprocess.run(
        [sys.executable, str(HERE / "fines.py")],
        input="\n".join(lines) + "\nquit\n",
        capture_output=True,
        text=True,
        timeout=20,
    )
    return result.stdout.splitlines()


def test_add_prints_title():
    assert run("add Dune 20 book") == ["added Dune"]


def test_book_fine_after_grace():
    assert run("add Dune 20 book", "report")[-2:] == ["Dune: 1.50", "total: 1.50"]


def test_book_fine_is_capped():
    assert run("add Old 400 book", "report")[-2] == "Old: 10.00"


# ... and four more: grace boundary, DVD rules, unknown kind, empty report.
```

The eight tests cover each command, each rule, **both caps**, **the grace boundary** (a book at 10 days: inside grace), an unknown kind, an unknown command and the empty case. Every expected value came from *running the legacy script*, not from what we think it should do. Run them against the untouched legacy code:

```text
$ python -m pytest -q
........                                                                 [100%]
8 passed in 0.51s
```

(The time is machine-specific.) Green. Now we may touch the code.

**What the tests do not pin.** Look: nothing tests an empty line, or `add Dune` with missing arguments. The legacy script crashes in those cases (`IndexError`). We decide that those crashes are **not** behavior worth keeping: we know about the gap, and we will not promise anything about them. Good characterization is deliberate about what it covers.

### 11.3 Step 1: create a seam (inject `read` and `write`)

Smallest possible change: put the loop in a function that takes its input and output as parameters, and make `data` local. The body is untouched. Only `input()` becomes `read()`, `print` becomes `write`, and the entry point is guarded:

```python
def main(read=input, write=print):
    data = []
    while True:
        line = read()
        if line == "quit":
            break
        parts = line.split()
        if parts[0] == "add":
            data.append([parts[1], int(parts[2]), parts[3]])
            write("added " + parts[1])
        elif parts[0] == "report":
            ...                                   # same body, print -> write
        else:
            write("unknown command " + parts[0])


if __name__ == "__main__":
    main()
```

```text
$ python -m pytest -q
........                                                                 [100%]
8 passed in 0.52s
```

Green. We gained three things at once: the global `data` is gone (no state survives between runs), the module can be imported without running, and the program now has a **seam**: tests can call `main` with fakes, no subprocess needed.

This is dependency injection (section 8) in its smallest form.

### 11.4 Step 2: name the data, make the rule a table

Two moves from the catalog: **introduce a data class** and **replace copy-paste with a parameterized table**. The two blocks for book and DVD differ only in three numbers: grace days, rate, cap.

```python
from dataclasses import dataclass


@dataclass(frozen=True)
class Loan:
    title: str
    days_late: int
    kind: str


RULES = {
    "book": (14, 0.25, 10.0),   # grace days, rate per day, cap
    "dvd": (3, 1.0, 20.0),
}


def fine_for(loan):
    grace, rate, cap = RULES[loan.kind]
    return min(max(loan.days_late - grace, 0) * rate, cap)
```

And in `main`, `data.append([parts[1], int(parts[2]), parts[3]])` becomes `loans.append(Loan(parts[1], int(parts[2]), parts[3]))`, and the two long branches in `report` become:

```python
            for loan in loans:
                if loan.kind in RULES:
                    fine = fine_for(loan)
                    write(f"{loan.title}: {fine:.2f}")
                    total += fine
                else:
                    write("unknown kind " + loan.kind)
```

Check the maths by hand before trusting the tests: the old code did `f = (days - grace) * rate`, then forced `f` to be at least 0, then at most `cap`. `max(x, 0)` then `min(..., cap)` is the same order of clamping. A subtle point: in the old code the subtraction happened *before* clamping, `(days - grace) * rate`; in the new code `max(days - grace, 0) * rate`. They are equal because `rate` is positive, so clamping before or after multiplying gives the same value. (If a rate could be negative, this would **not** be a safe step. Always ask what an "equivalent" change relies on.)

```text
$ python -m pytest -q
........                                                                 [100%]
8 passed in 0.83s
```

Green. The two copy-pasted blocks are now one function plus a table. Adding a "magazine" kind is a one-line change to `RULES`, and `fine_for` is a **pure function** you can test with plain numbers.

### 11.5 Step 3: separate the pure core from the I/O shell

`main` still does two jobs: it reads commands (the shell), and it builds the report text (the core). Extract the second as a function that takes the loans and returns a **list of lines**, no `write` inside:

```python
def build_report(loans):
    """Pure: loans in, list of output lines out."""
    lines = []
    total = 0
    for loan in loans:
        if loan.kind in RULES:
            fine = fine_for(loan)
            lines.append(f"{loan.title}: {fine:.2f}")
            total += fine
        else:
            lines.append(f"unknown kind {loan.kind}")
    lines.append(f"total: {total:.2f}")
    return lines
```

In `main`, the `report` branch becomes:

```python
        elif parts[0] == "report":
            for line in build_report(loans):
                write(line)
```

```text
$ python -m pytest -q
........                                                                 [100%]
8 passed in 0.84s
```

Green. Now the report can be tested **without any fake reader or writer**:

```python
from fines import build_report
print(build_report([]))
```
```text
['total: 0.00']
```

### 11.6 Step 4: replace the command chain with a registry

The `if/elif` over command names is the open/closed smell from section 6.3. Each command becomes a small function with the same signature (`(loans, args) -> list of lines to write`), and a dictionary maps names to them. The loop reads like what it does:

```python
def cmd_add(loans, args):
    title, days, kind = args
    loans.append(Loan(title, int(days), kind))
    return [f"added {title}"]


def cmd_report(loans, args):
    return build_report(loans)


COMMANDS = {"add": cmd_add, "report": cmd_report}


def main(read=input, write=print):
    loans = []
    while (line := read()) != "quit":
        name, *args = line.split()
        handler = COMMANDS.get(name)
        if handler is None:
            write(f"unknown command {name}")
            continue
        for out in handler(loans, args):
            write(out)


if __name__ == "__main__":
    main()
```

```text
$ python -m pytest -q
........                                                                 [100%]
8 passed in 0.84s
```

Green again. `main` is 9 lines, nesting two deep, and is the only function that touches `read` and `write`. A new command is a function plus one dictionary entry; `main` never changes.

Notice two small Pythonic choices in the final loop: the walrus operator `:=` (core.02) reads and tests in one place, and `name, *args = line.split()` unpacks "the first word, then the rest" (section 2.2).

One honest change: on an **empty line** the legacy code crashed with `IndexError`, and the new code crashes with `ValueError` (the unpacking has nothing to unpack). Both crash; neither is pinned by a test. If a caller depended on the *type* of that crash, we would have broken it, which is why we looked at what the tests do and do not cover in step 0.

### 11.7 What changed, and what did not

The behavior (8 tests, unchanged test file) is the same. The global mutable `data` is gone. The longest function went from about 36 lines, 5 levels deep, to 13 lines, 2 levels deep. Two copy-pasted rule blocks became one table. Everything is testable without a subprocess (`fine_for`, `build_report`, `main(read, write)`), a new kind of item is one line in `RULES`, and a new command is one function plus one entry.

Each step was one idea: **seam, data and table, pure core, registry.** None needed a framework, a base class or a pattern *name*. The registry is O of SOLID, `read`/`write` is D, the pure functions are S, and `Loan` is section 4, but we got there by following the pain, not a checklist.

**What we left alone on purpose.** `add` does not validate its arguments and nothing handles `EOFError` if the input ends without `quit`. Each is a real problem, but each is a **behavior change**, so each belongs in its own later change, with its own test written first.

### 11.8 The module project: the inventory report (p030)

Problem `core.22.p030` is this same exercise at a larger size, with a different legacy program: an **inventory report** script. It is a single file with global lists, `input()` and `print()` calls everywhere, a hard-coded file path, an `if/elif` chain of commands and no function shorter than 30 lines.

You deliver a clean `solution.py` that has:

- a pure core, `build_report(records, today)`, which takes the date as a parameter and returns lines (no clock, no printing);
- a `Record` dataclass instead of lists and dicts;
- a command registry instead of the `if/elif` chain;
- `main(argv, read=..., write=..., today=...)` as the **only** place that touches I/O.

The tests are a golden table for eight command scripts, fakes in place of `input`/`print`/files, and structure checks (no function longer than 20 lines, no module-level mutable state, a dataclass, a registry, I/O only in `main`). Work like this section: **run the legacy script on your own inputs first, write the golden table, make the seam, then take one small step at a time with tests after each.**

#### Try it 11.1

In step 2 we turned "`(days - grace) * rate`, then clamp to `[0, cap]`" into `max(days - grace, 0) * rate`. Suppose a rule used a **negative** rate of `-0.5`, with `days = 5` and `grace = 14`, and the old clamping code (`if f < 0: f = 0`, `if f > cap: f = cap`). Do the two versions agree?

<details><summary>Answer</summary>

No. Old: `(5 - 14) * -0.5 = 4.5`, no clamp applies, result `4.5`. New: `max(-9, 0) * -0.5 = -0.0`. The step was safe only **because `rate > 0`**. A refactor preserves behavior only under the assumptions it makes, so when an assumption matters, write it down in a comment or a test.

</details>

## 12. Over-engineering: pattern or ceremony?

### 12.1 The other failure

Everything so far warned about messy code. There is an opposite failure that is just as expensive and, in a way, harder to see because it *looks* professional: **over-engineering**, designs with more structure than the problem needs. Here is a greeting service written as if it were a banking system:

```python
from abc import ABC, abstractmethod

class GreetingStrategy(ABC):
    @abstractmethod
    def greet(self, name): ...

class FriendlyGreetingStrategy(GreetingStrategy):
    def greet(self, name):
        return f"Hello, {name}!"

class GreetingStrategyFactory:
    def create(self):
        return FriendlyGreetingStrategy()

class GreetingService:
    def __init__(self, factory):
        self.strategy = factory.create()
    def run(self, name):
        return self.strategy.greet(name)

print(GreetingService(GreetingStrategyFactory()).run("Asha"))
```
```text
Hello, Asha!
```

Five classes, one abstract base, one factory, for this:

```python
def greet(name):
    return f"Hello, {name}!"

print(greet("Asha"))
```
```text
Hello, Asha!
```

Same output. The first version has 5 names to learn, 4 places to look, and zero extra capability. Every design pattern in this chapter is a **solution to a problem you have**. If you cannot point at the pain it removes *today*, it is ceremony.

### 12.2 Signs of ceremony

- **One implementation behind an interface**: an ABC with a single subclass nobody plans to add to.
- **A class with a single method and no state**, called `Manager`, `Handler` or `Service`. It is a function.
- **Layers that only forward**, each calling the next with no logic of its own.
- **A "plugin system" with no second plugin**, or **configuration for things that never vary**.
- **A Singleton class** (a `__new__` that returns the same instance). A module-level object does the same for free (section 7.6), and the class version only hides shared mutable state (section 8.4).

### 12.3 The three questions

Before adding structure, ask:

1. **What problem does this solve right now?** Name a concrete, current pain (a bug, a repeated change, a test that cannot be written), not "it might be useful".
2. **What is the simplest thing that could work?** If a function does it, write the function.
3. **What would change if I did not do this?** If the answer is "nothing", do not do it.

And the **rule of three** for abstraction: the first time you write something, just write it; the second time, notice the repeat and tolerate it; the third time, you know what varies, so extract. "You Aren't Gonna Need It" (YAGNI) says the same: do not build for requirements you imagine.

### 12.4 When the heavier design IS worth it

This is not an argument against structure. Heavier designs pay off when the pain is real:

- **An interface with several real implementations** (real mailer, SMTP-test mailer, in-memory fake): a `Protocol` or a base class earns its place, because callers truly vary.
- **A plugin system** when third parties add behavior you cannot predict (`pytest` plugins, a command-line tool that discovers add-ons).
- **A Command class with undo** when users must undo, logged actions must be replayed, or work must be queued and saved.
- **Layers** when they *do* something, such as a repository that hides which of two real databases is used.
- **Dependency injection** at the boundaries that make tests possible.

The test is always the same: *is there a variation that actually exists (or is certain to arrive soon) that this structure lets me handle cheaply?*

#### Try it 12.1

A teammate proposes this for "formatting a price" in a program that always uses dollars:

```python
class PriceFormatterStrategy(ABC): ...
class DollarFormatter(PriceFormatterStrategy): ...
class PriceFormatterFactory: ...
```

Write the three questions as a reply, and say what you would write instead. Then say what news would change your answer.

<details><summary>Answer</summary>

1. *What problem does this solve right now?* None: there is one currency, and no bug or repeated change is waiting.
2. *Simplest thing?* `def format_price(amount): return f"${amount:,.2f}"`: one function, one place to change.
3. *What if we do not?* Nothing changes today.

What would change my answer: a real requirement for a **second** currency (the company is entering another country), a customer asking for it, or a formatter that needs configuration and several methods. Then I would first make `format_price` take a `currency` or a formatting function as an argument (strategy as a function, section 7.1), and only grow to a class if the formatting needs several cooperating methods.

</details>

## 13. Common traps

1. **Using `if not x` where `0`, `""` or `[]` is a valid value.** Use `is None` when you mean "missing" (section 2.3).
2. **A mutable default argument** (`def f(x, items=[])`). Use `None` and create the list inside (section 3.1).
3. **A bare `except:` or a wide `except Exception: pass`.** It hides typos and real failures. Catch the specific exception, around the smallest piece of code (sections 2.4, 3.2).
4. **`[... for ...]` for side effects**, or a three-`for` comprehension nobody can read. Write a loop (section 2.5).
5. **Late-binding lambdas in a loop** (`lambda: i`). Bind the value: `lambda i=i: i` (section 5.2).
6. **`itertools.groupby` on unsorted data.** It groups only adjacent equal keys; sort by the same key first (section 2.7).
7. **Refactoring without tests**, or changing behavior "while you are in there". One step, one purpose; tests before and after (sections 10, 11).
8. **A "harmless" boundary change** (`>` becoming `>=`, a rounding change, a list mutated instead of copied). Test the values *at* each boundary (section 10.1).
9. **Subclassing for code reuse when the subclass cannot keep the parent's promises** (Square/Rectangle, a limited stack). Prefer composition (section 6.4).
10. **Hidden collaborators:** `datetime.now()`, `random`, `open` called deep inside logic. Take them as parameters with real defaults (sections 6.6, 8).
11. **Module-level mutable state that functions change.** It makes test results depend on test order. Own the state in an object or closure (section 8.4).
12. **Patterns by name, not by need:** a factory with one product, an interface with one implementation, a Singleton class. Ask what pain it removes today (section 12).
13. **Mixed return types or `None` meaning "error".** Raise a specific exception instead (section 9.5).
14. **Treating this chapter as rules.** Every idiom and pattern has a "when not to". Judgment beats rule-following.

## 14. Summary

**Pythonic** means code that does the obvious thing the way Python programmers expect; the reader's time is the cost that matters.

- **Idioms** (section 2): iterate over items (`enumerate`, `zip`, `any`, `sum`); unpack to name the parts; `is None` for "missing", truthiness for "empty"; EAFP with a narrow `except`; comprehensions for simple builds, generators for lazy use, loops for side effects; `with` for "do, then always undo"; stdlib first.
- **Smells** (section 3): mutable defaults, bare `except`, god functions, stringly typed values, `isinstance` chains, flag arguments, premature abstraction, copy-paste. A smell is a question, not a verdict.
- **Data and functions** (sections 4, 5): `dict` for open keys, `Enum` for closed names, `NamedTuple` for tiny tuples, `@dataclass` as the default record. A class with `__init__` and one method is usually a function; closures, `partial` and callable objects cover the rest.

| SOLID | In Python |
|---|---|
| S | split by reason to change; pure core, I/O at the edge |
| O | registry or polymorphism: add code, do not edit the chain |
| L | a subclass keeps every promise of its parent, or use composition |
| I | small Protocols; depend on what you use |
| D | pass the clock, `rng`, `opener`, mailer in; defaults for the real thing |

| Pattern | Pain it removes | Pythonic form |
|---|---|---|
| Strategy | rule chosen by `if/elif` | pass a function |
| Factory | creation scattered everywhere | registry or `@classmethod` constructor |
| Observer | one event, many reactions | list of callables; `subscribe` returns `unsubscribe` |
| Adapter | wrong interface, code you cannot edit | small wrapper or closure |
| Command | actions to undo, queue or log | object with `do`/`undo`, or a function in a list |
| Singleton | exactly one instance | a module-level object |
| Null object | `if x is not None` everywhere | a do-nothing default |

- **Dependency injection** (section 8) is just parameters: constructor injection, real defaults, one composition root. No framework.
- **Clean code** (section 9): meaningful names, small functions at one level, guard clauses, pure functions, comments that say why, exceptions instead of `None`.
- **Refactoring** (sections 10, 11): characterization tests first (values from *running* the old code, boundaries included), small steps with tests after each, one purpose per change, stop when the next change is easy.
- **Over-engineering** (section 12): a pattern is a solution to a pain you have today. Ask what problem it solves now, what the simplest thing is, and what changes if you do nothing.

The skill underneath all of it: **read your own code as a stranger would, find where it hurts, and apply the smallest change that removes the pain.**
