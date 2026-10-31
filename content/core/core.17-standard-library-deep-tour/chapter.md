# Chapter 17: Standard library deep tour

Python is famous for coming with "batteries included". The **standard library** is everything you can `import` without installing anything: more than two hundred modules, written and tested by the people who write Python itself.

You have already used a lot of it. Chapter 5 showed `namedtuple` and `copy.deepcopy`. Chapter 12 used `pathlib`, `csv`, `json`, `argparse`, `tempfile`, `os`, `shutil` and `glob`. Chapter 11 used `functools` and `itertools`. This chapter is a guided tour of the rest of the toolbox that a working Python programmer reaches for every week.

Why spend a whole chapter here? Because the most common mistake of a growing programmer is not a wrong `if`. It is **writing by hand something the standard library already does better**:

- a dict of counters with `if key not in d: d[key] = 0` everywhere, instead of `Counter`;
- a list used as a queue with `pop(0)`, which gets slower and slower, instead of `deque`;
- "add 5.5 hours" to get India time, which breaks twice a year in London, instead of `zoneinfo`;
- `print()` scattered through a program, deleted before release, and badly missed when something breaks at 3 a.m., instead of `logging`;
- building SQL with f-strings, which lets a user delete your table, instead of `sqlite3` parameters.

The library versions are faster, already debugged, and known to every other Python programmer who reads your code. The goal of this chapter is the first learning outcome of the module: **reach for the right standard-library tool before writing your own.**

You do not need to memorise every function. You need to know **that a tool exists, what problem it solves, and which trap it hides**. Then the documentation fills in the details in thirty seconds.

**A note on how examples are shown.** Every block that has output was really run, with **Python 3.14** on Linux. Some values change on every run or every machine: random ids, timings, process ids, file paths. Those are labelled *machine-specific* next to the example. The course supports Python 3.11 and newer; when a feature is newer than 3.11, the text says so.

**Offline and cross-platform.** Nothing in this chapter needs the internet. The HTTP examples start a tiny web server on your own computer (`127.0.0.1`). Commands run by `subprocess` start Python itself (`sys.executable`), so they work the same on Linux, macOS and Windows.

## Table of contents

1. [Reach for the library first](#1-reach-for-the-library-first)
2. [`collections` in depth](#2-collections-in-depth)
3. [`heapq` and `bisect`](#3-heapq-and-bisect)
4. [`datetime`: dates, times and durations](#4-datetime-dates-times-and-durations)
5. [Time zones with `zoneinfo`](#5-time-zones-with-zoneinfo)
6. [Time-zone data, `tzdata`, and the `time` module](#6-time-zone-data-tzdata-and-the-time-module)
7. [`math`, `statistics`, `random` and `secrets`](#7-math-statistics-random-and-secrets)
8. [`copy` and `pprint`](#8-copy-and-pprint)
9. [`sys`, `os`, `shlex` and `subprocess`](#9-sys-os-shlex-and-subprocess)
10. [`hashlib`, `uuid`, `base64` and `struct`](#10-hashlib-uuid-base64-and-struct)
11. [`sqlite3`: a database in a file](#11-sqlite3-a-database-in-a-file)
12. [`zipfile` and `shutil` archives](#12-zipfile-and-shutil-archives)
13. [`urllib` and `http`, offline](#13-urllib-and-http-offline)
14. [`logging` in depth](#14-logging-in-depth)
15. [Project: a backup and log-rotation tool](#15-project-a-backup-and-log-rotation-tool)
16. [Common traps](#16-common-traps)
17. [Summary](#17-summary)

## 1. Reach for the library first

### 1.1 A habit, not a list

Before you write a helper function, ask one question: **"Is this a common problem?"** Counting things, sorting by date, keeping the last ten lines, finding a file's checksum, running another program, writing a log. If the answer is yes, the standard library almost certainly has it.

Here is the map for this chapter. Read it now, and come back to it whenever you start a new program.

| You need to... | Reach for |
|---|---|
| count things, find the most common | `collections.Counter` |
| group items into lists by a key | `collections.defaultdict(list)` |
| a queue, or "keep the last N" | `collections.deque` (with `maxlen`) |
| an LRU cache, order you can change | `collections.OrderedDict` |
| layered settings (defaults, file, command line) | `collections.ChainMap` |
| the k smallest, a priority queue, merge sorted streams | `heapq` |
| look up in a sorted list, keep a list sorted | `bisect` |
| dates, durations, time zones | `datetime`, `zoneinfo` |
| measure how long code takes | `time.perf_counter` |
| exact float sums, combinations, gcd; mean, median, spread | `math`; `statistics` |
| simulations, shuffles (repeatable) | `random.Random(seed)` |
| passwords, tokens, anything secret | `secrets` |
| an independent copy of nested data; readable printing of it | `copy.deepcopy`; `pprint` |
| run another program; split or quote a command line | `subprocess.run`; `shlex` |
| a file checksum, find duplicates | `hashlib` |
| unique ids; bytes inside text; fixed-size binary records | `uuid`; `base64`; `struct` |
| a real database without a server | `sqlite3` |
| zip and unzip | `zipfile`, `shutil.make_archive` |
| build or read URLs; fetch a URL | `urllib.parse`; `urllib.request` |
| messages about what a program is doing | `logging` |

### 1.2 How to explore a module yourself

Three tools find answers faster than any search engine, and they work offline:

- `dir(collections)` lists the names in a module. Names that start with `_` are private.
- `help(thing)` in the REPL shows the full documentation page (press `q` to leave).
- `python -m pydoc collections.deque` prints the same page in a terminal.

The rest of the chapter takes the modules one by one. For each: **why** it exists, **how** to use it, and the **trap** it hides.

## 2. `collections` in depth

Chapter 5 met `namedtuple` and promised the rest of the `collections` module for later. Here it is. Each type in `collections` is a built-in container (dict, list, tuple) with **one extra ability** that you would otherwise write by hand.

### 2.1 `Counter`: counting without the boilerplate

Counting is so common that everyone has written the same loop: `if w not in counts: counts[w] = 0`, then `counts[w] += 1`. `Counter` is a dict subclass made for exactly this. Give it any iterable and it counts:

```python
from collections import Counter

words = "the cat and the hat and the bat".split()
c = Counter(words)
print(c)
print(c["the"], c["dog"])          # missing key -> 0, no KeyError
print(c.most_common(2))
print(c.total())                   # sum of all counts (3.10+)
print(Counter("mississippi").most_common())
```
```text
Counter({'the': 3, 'and': 2, 'cat': 1, 'hat': 1, 'bat': 1})
3 0
[('the', 3), ('and', 2)]
8
[('i', 4), ('s', 4), ('p', 2), ('m', 1)]
```

Three things to notice:

- A **missing key gives 0**, not `KeyError`. Reading `c["dog"]` does **not** add `"dog"` to the counter (compare `defaultdict` below).
- `most_common(n)` returns `(item, count)` pairs, biggest first. Items with **equal counts keep the order in which they were first seen**: in `"mississippi"`, `i` and `s` both appear 4 times, and `i` is listed first because it was met first. Do not rely on any other tie order; if a problem says "ties alphabetically", sort yourself: `sorted(c.items(), key=lambda kv: (-kv[1], kv[0]))`.
- `most_common()` with no argument returns all pairs, sorted.

### 2.2 Updating and combining counters

A counter can grow from more data, and two counters can be combined with arithmetic:

```python
from collections import Counter

stock = Counter(apple=5, pear=2)
stock.update(["apple", "kiwi"])          # add one apple, one kiwi
stock.update({"pear": 3})               # add 3 pears
print(stock)
stock.subtract({"apple": 10})           # may go negative
print(stock)

a = Counter(x=3, y=1)
b = Counter(x=1, y=4, z=2)
print("a + b =", a + b)
print("a - b =", a - b)                 # drops zero and negative results
print("a | b =", a | b)                 # max of each
print("a & b =", a & b)                 # min of each
print(sorted(Counter(a=2, b=1).elements()))
print(+stock)                           # unary plus: keep only positive counts
```
```text
Counter({'apple': 6, 'pear': 5, 'kiwi': 1})
Counter({'pear': 5, 'kiwi': 1, 'apple': -4})
a + b = Counter({'y': 5, 'x': 4, 'z': 2})
a - b = Counter({'x': 2})
a | b = Counter({'y': 4, 'x': 3, 'z': 2})
a & b = Counter({'x': 1, 'y': 1})
['a', 'a', 'b']
Counter({'pear': 5, 'kiwi': 1})
```

The rule that surprises people: **`update` and `subtract` keep every result, even zero or negative; the operators `+`, `-`, `|`, `&` keep only positive counts.** That is why `a - b` has no `y` (1 - 4 is negative) and no `z`. Think of the operators as "multiset" maths, where you cannot own -3 apples. `elements()` repeats each item as many times as its count, which is handy for rebuilding a list.

`Counter` is still a dict. `len(c)` is the number of **distinct** items, `c.total()` is the number of items counted, and `del c["x"]` removes a key (setting it to 0 does not).

#### Try it 2.1

Predict all four lines. Then run it.

```python
from collections import Counter
c = Counter("banana")
c.subtract("nab")
print(c)
print(c + Counter())
print(len(c), c.total())
print(c["z"], "z" in c)
```

<details><summary>Answer</summary>

```text
Counter({'a': 2, 'n': 1, 'b': 0})
Counter({'a': 2, 'n': 1})
3 3
0 False
```

`"banana"` counts a=3, n=2, b=1. Subtracting one each of n, a, b leaves a=2, n=1, b=0. `subtract` keeps the zero, so `b` is still a key and `len(c)` is 3. Adding an empty counter is an operator, so it drops `b: 0`. Reading `c["z"]` gives 0 but does not create the key.
</details>

### 2.3 `defaultdict`: a dict that fills its own gaps

`Counter` handles numbers. For any other "start value", use `defaultdict`. You give it a **factory**: a function with no arguments that makes the start value. When you look up a missing key, it calls the factory, stores the result under that key, and returns it.

The most common use is **grouping**:

```python
from collections import defaultdict

names = ["asha", "bilal", "anil", "chen", "bina", "arjun"]
groups = defaultdict(list)
for name in names:
    groups[name[0]].append(name)     # no "if key not in groups"
print(groups)
print(dict(groups))
```
```text
defaultdict(<class 'list'>, {'a': ['asha', 'anil', 'arjun'], 'b': ['bilal', 'bina'], 'c': ['chen']})
{'a': ['asha', 'anil', 'arjun'], 'b': ['bilal', 'bina'], 'c': ['chen']}
```

Any zero-argument callable works as the factory: `list`, `set` (for example, a graph as `defaultdict(set)` of neighbours), `int` (gives 0), `str` (gives `""`), `dict`, or a `lambda`. Nested counts are `defaultdict(lambda: defaultdict(int))`, used as `d["2025"]["jan"] += 1`.

### 2.4 The `defaultdict` trap: reading creates keys

The factory runs on **every** `d[key]` with a missing key, even when you only meant to *look*:

```python
from collections import defaultdict

scores = defaultdict(int)
scores["asha"] += 10
if scores["ravi"] > 5:         # only a check... or is it?
    print("ravi passed")
print(len(scores), dict(scores))

print("meera" in scores)       # `in` never creates a key
print(scores.get("meera"))     # .get never creates a key
print(len(scores))
```
```text
2 {'asha': 10, 'ravi': 0}
False
None
2
```

The `if` line quietly added `ravi: 0`. In a report loop that "checks" a thousand names, you end up with a thousand fake entries. **Use `in` or `.get()` to look; use `d[key]` only when you mean "create if missing".** Counter does not have this problem, because its missing-key rule returns 0 *without* storing it.

A second trap: a `defaultdict` prints as `defaultdict(<class 'list'>, {...})`, and `json.dumps` and equality with a plain dict still work. Before you return it from a function, `dict(d)` turns it into a plain dict, so callers do not get surprise keys later.

#### Try it 2.2

What does this print? Count carefully which lines create keys.

```python
from collections import defaultdict
d = defaultdict(list)
d["a"].append(1)
x = d["b"]
y = d.get("c")
z = "d" in d
print(sorted(d), x, y, z)
```

<details><summary>Answer</summary>

```text
['a', 'b'] [] None False
```

`d["a"]` and `d["b"]` both run the factory and store a list. `.get("c")` returns `None` without storing anything, and `in` never creates keys.
</details>

### 2.5 `deque`: a queue with two fast ends

A `deque` (say "deck", short for **d**ouble-**e**nded **que**ue) is a sequence that is fast to change at **both** ends. Chapter 5 warned that `list.insert(0, x)` and `list.pop(0)` must shift every other item, so they are O(n). On a deque, `appendleft` and `popleft` are O(1).

```python
from collections import deque

q = deque(["a", "b"])
q.append("c")          # right end
q.appendleft("z")      # left end
print(q)
print(q.popleft(), q.pop(), q)
q.extend([1, 2])
q.rotate(1)            # move the last item to the front
print(q)
q.rotate(-2)           # move two items from the front to the back
print(q, q[0], q[-1])
```
```text
deque(['z', 'a', 'b', 'c'])
z c deque(['a', 'b'])
deque([2, 'a', 'b', 1])
deque(['b', 1, 2, 'a']) b a
```

The price: indexing into the *middle* (`q[500]`) is O(n), and there is no slicing. Use a deque when you work at the ends, a list when you jump around.

**`maxlen`: keep only the last N.** A deque with `maxlen` drops items from the opposite end when it is full. This is exactly what `tail -n 3` does with a file:

```python
from collections import deque
from pathlib import Path

Path("app.log").write_text("".join(f"line {i}\n" for i in range(1, 8)), encoding="utf-8")
with open("app.log", encoding="utf-8") as f:
    last = deque(f, maxlen=3)            # reads the whole file, keeps 3 lines
print([line.rstrip("\n") for line in last])

recent = deque(maxlen=2)
for page in ["home", "cart", "pay"]:
    recent.append(page)
    print(list(recent))
```
```text
['line 5', 'line 6', 'line 7']
['home']
['home', 'cart']
['cart', 'pay']
```

The file is read once, line by line, and the memory used is three lines, however big the log is.

**Round-robin.** A deque also makes a fair scheduler: `popleft` a task, give it one turn, and `append` it back on the right if it still has work left. Tasks A, B, C needing 3, 1 and 2 turns run in the order A B C A C A.

#### Try it 2.3

Trace this by hand, then run it.

```python
from collections import deque
d = deque([1, 2, 3], maxlen=3)
d.append(4)
d.appendleft(0)
d.rotate(1)
print(d)
```

<details><summary>Answer</summary>

```text
deque([3, 0, 2], maxlen=3)
```

After `append(4)`: `[2, 3, 4]` (1 fell off the left). After `appendleft(0)`: `[0, 2, 3]` (4 fell off the **right**: a full deque drops from the opposite end). `rotate(1)` moves 3 to the front.
</details>

### 2.6 `OrderedDict`: order you can change

Since Python 3.7 every dict keeps insertion order, so why does `OrderedDict` still exist? Because it can **change** the order cheaply and it treats order as meaningful:

- `move_to_end(key)` moves a key to the end (or to the front with `last=False`) in O(1).
- `popitem(last=False)` removes the **oldest** item (a plain dict's `popitem` only removes the newest).
- Two `OrderedDict`s are equal only if their **order** matches too. Two plain dicts ignore order.

```python
from collections import OrderedDict

od = OrderedDict.fromkeys("abc", 0)
od.move_to_end("a")                 # a becomes the newest
print(list(od))
od.move_to_end("c", last=False)     # c becomes the oldest
print(list(od), od.popitem(last=False), list(od))
print(OrderedDict(x=1, y=2) == OrderedDict(y=2, x=1), dict(x=1, y=2) == dict(y=2, x=1))
```
```text
['b', 'c', 'a']
['c', 'b', 'a'] ('c', 0) ['b', 'a']
False True
```

Those two methods are exactly what an **LRU cache** (least recently used) needs: on every `get` or `put`, `move_to_end(key)`; when the cache grows past its capacity, `popitem(last=False)` drops the item used longest ago. You will build one in problem p006.

For caching a *function's* results, chapter 11's `functools.lru_cache` already does all of this. Build your own only when you need control, such as caching objects by your own key or logging evictions.

### 2.7 `ChainMap`: layered lookups

Real programs read settings from several places: built-in defaults, a config file, environment variables, the command line. The rule is "the most specific layer wins". You could merge dicts with `{**defaults, **file, **cli}`, but that makes a copy and forgets where each value came from. `ChainMap` keeps the dicts separate and **searches them in order**:

```python
from collections import ChainMap

defaults = {"color": "blue", "size": 10, "debug": False}
from_file = {"size": 12}
from_cli = {"debug": True}

settings = ChainMap(from_cli, from_file, defaults)   # first map wins
print(settings["color"], settings["size"], settings["debug"])
print(dict(settings))

settings["color"] = "red"            # writes go to the FIRST map only
print(from_cli, defaults["color"])

defaults["size"] = 99                # a live view: no copy was made
print(settings["size"])              # still 12: from_file is searched first
del from_file["size"]
print(settings["size"])
```
```text
blue 12 True
{'color': 'blue', 'size': 12, 'debug': True}
{'debug': True, 'color': 'red'} blue
12
99
```

`new_child()` returns a new chain with a fresh empty dict in front, which is how interpreters model nested scopes (local, then enclosing, then global, then built-in names). `parents` gives the chain without the first map.

**Trap:** `del settings["key"]` and assignment only touch the first map. If the key lives only in a lower layer, `del` raises `KeyError`.

### 2.8 `namedtuple`, the rest of the story

Chapter 5 showed the basics: named fields, immutability, `_replace` and `_asdict`. Three more features make it a good choice for read-only records such as rows from a CSV file:

```python
from collections import namedtuple

Row = namedtuple("Row", "name city score", defaults=[0])   # defaults fill from the right
print(Row("asha", "Pune"))
r = Row._make(["ravi", "Delhi", "71"])   # build from any iterable (a CSV row)
print(r, r.score + "!")                  # no conversion happens: still a str
r = r._replace(score=int(r.score))
print(r.score + 1, Row._fields, Row._field_defaults)
name, city, score = r                    # still a tuple: it unpacks
print(name, isinstance(r, tuple))
```
```text
Row(name='asha', city='Pune', score=0)
Row(name='ravi', city='Delhi', score='71') 71!
72 ('name', 'city', 'score') {'score': 0}
ravi True
```

`_make` does **not** convert types: a namedtuple is a labelled tuple, not a validator. If you want type hints on the fields, `typing.NamedTuple` gives the same object with class syntax (`class Row(NamedTuple): name: str`), and when you need mutability or methods, a `@dataclass` (chapter 14) is the better fit.

### 2.9 Choosing between `dict`, `Counter` and `defaultdict`

| Situation | Best fit | Why |
|---|---|---|
| a fixed mapping you fill once | `dict` | simplest; missing keys are real errors |
| counting, top-N, "how many of each" | `Counter` | missing = 0, `most_common`, arithmetic |
| grouping into lists or sets | `defaultdict(list)` / `(set)` | the start value appears by itself |
| missing keys mean a bug | `dict` | `KeyError` tells you at once |
| you will pass it to code that reads unknown keys | `dict` or `Counter` | `defaultdict` would grow silently |

A good test: *"Would a missing key be a mistake?"* If yes, use a plain dict so the mistake is loud.

#### Try it 2.4

For each task, pick `dict`, `Counter`, `defaultdict(list)`, `deque` or `OrderedDict`: (a) the five most common IP addresses in a log; (b) all orders, grouped by customer; (c) the last 100 temperature readings; (d) a country-code to country-name table; (e) a cache of 50 pages that drops the least recently viewed.

<details><summary>Answer</summary>

(a) `Counter` with `most_common(5)`. (b) `defaultdict(list)`. (c) `deque(maxlen=100)`. (d) a plain `dict`: an unknown code should raise `KeyError`. (e) `OrderedDict` with `move_to_end` and `popitem(last=False)` (or `functools.lru_cache` if it caches a function).
</details>

## 3. `heapq` and `bisect`

Both modules work on a **plain list** that you keep in a special shape. `heapq` keeps it as a *heap*: the smallest item is always at index 0. `bisect` keeps it *fully sorted*. Neither is a new type: they are functions that maintain an invariant for you.

### 3.1 What a heap is, and why it is fast

Suppose you receive jobs one by one and must always process the most urgent (smallest priority number) next. Options:

- Keep an unsorted list and call `min()` each time: O(n) per job.
- Keep the list sorted and insert in the right place: finding the place is fast, but inserting shifts items, O(n).
- Keep a **heap**: push and pop are both **O(log n)**. For a million items, that is about 20 steps instead of a million.

A heap is a list where every item at index `i` is `<=` its two "children" at indexes `2*i + 1` and `2*i + 2`. That is all. The list is **not** sorted: only the first item is guaranteed to be the smallest.

```python
import heapq

h = []
for x in [5, 1, 8, 3, 2]:
    heapq.heappush(h, x)
    print("push", x, "->", h)
print("h[0] is the smallest:", h[0])
print("pop", heapq.heappop(h), "->", h)
print("rest:", [heapq.heappop(h) for _ in range(len(h))])
```
```text
push 5 -> [5]
push 1 -> [1, 5]
push 8 -> [1, 5, 8]
push 3 -> [1, 3, 8, 5]
push 2 -> [1, 2, 8, 5, 3]
h[0] is the smallest: 1
pop 1 -> [2, 3, 8, 5]
rest: [2, 3, 5, 8]
```

Look at `[1, 2, 8, 5, 3]`: not sorted, but `1 <= 2`, `1 <= 8`, `2 <= 5`, `2 <= 3`. Each `heappop` takes `h[0]`, moves the last item to the top and lets it "sink" below its smaller child until the rule holds again. Popping everything gives sorted order.

The helpers:

```python
import heapq

data = [9, 4, 7, 1, 8, 2]
heapq.heapify(data)                       # rearrange in place, O(n)
print(data)
print(heapq.nsmallest(3, [9, 4, 7, 1, 8, 2]))
print(heapq.nlargest(2, ["kiwi", "fig", "banana"], key=len))
print(heapq.heappushpop([1, 5, 9], 3))    # push 3, then pop the smallest: 1
print(heapq.heapreplace([1, 5, 9], 0))    # pop first (1), then push 0
```
```text
[1, 4, 2, 9, 8, 7]
[1, 2, 4]
['banana', 'kiwi']
1
1
```

`heapq` only knows **min-heaps**. For the largest first, push `-priority` (numbers) or use `nlargest`. When should you use which?

- One smallest or largest: `min()` / `max()`.
- The k smallest of n, with k much smaller than n: `heapq.nsmallest(k, data)`. It keeps a heap of only k items.
- k close to n: just `sorted(data)[:k]`.
- Items keep arriving and you keep taking the smallest: a heap with `heappush` / `heappop`.

### 3.2 A priority queue that never compares tasks

Heaps compare items with `<`. Pushing `(priority, task)` tuples works, until two tasks have the **same priority**: then Python compares the tasks themselves, which crashes for dicts or objects without `<`, and gives an arbitrary order for strings.

```python
import heapq

h = []
heapq.heappush(h, (2, {"job": "email"}))
try:
    heapq.heappush(h, (2, {"job": "backup"}))
except TypeError as e:
    print("TypeError:", e)
```
```text
TypeError: '<' not supported between instances of 'dict' and 'dict'
```

The fix used everywhere, including the official documentation: put a **counter** between the priority and the task. The counter always differs, so the comparison never reaches the task, and equal priorities come out **first in, first out**.

```python
import heapq
from itertools import count


class TaskQueue:
    def __init__(self):
        self._heap = []
        self._order = count()           # 0, 1, 2, ... a tie-breaker

    def push(self, priority, task):
        heapq.heappush(self._heap, (priority, next(self._order), task))

    def pop(self):
        priority, _, task = heapq.heappop(self._heap)
        return task

    def __len__(self):
        return len(self._heap)


q = TaskQueue()
q.push(2, {"job": "email"})
q.push(1, {"job": "deploy"})
q.push(2, {"job": "backup"})
while q:
    print(q.pop())
```
```text
{'job': 'deploy'}
{'job': 'email'}
{'job': 'backup'}
```

### 3.3 Merging sorted streams

You have three log files, each already sorted by time, and you want one sorted stream. `sorted(a + b + c)` reads everything into memory. `heapq.merge` reads **one item at a time from each input** and always yields the smallest next one, so it works on files of any size:

```python
import heapq

server_a = ["09:00 a start", "09:05 a ok", "09:20 a stop"]
server_b = ["09:01 b start", "09:30 b stop"]
server_c = ["09:04 c ping"]
for line in heapq.merge(server_a, server_b, server_c):
    print(line)
print(list(heapq.merge([5, 3, 1], [4, 2], reverse=True)))
```
```text
09:00 a start
09:01 b start
09:04 c ping
09:05 a ok
09:20 a stop
09:30 b stop
[5, 4, 3, 2, 1]
```

The inputs must **already be sorted** in the same way (`key` and `reverse` describe that order). If one input is not sorted, `merge` does not complain; it just gives wrong output.

### 3.4 Two heaps: a running median

A classic use of heaps: keep the **median** of a stream of numbers as they arrive, without sorting again for every new number. The idea:

- Keep the **smaller half** in a max-heap. `heapq` only has min-heaps, so store the numbers **negated**: the biggest of the small half is then `-low[0]`.
- Keep the **larger half** in a normal min-heap: its smallest is `high[0]`.
- Keep the sizes equal, or let the lower half have one extra.
- For each new number: push it into the lower half, then move the lower half's biggest across to the upper half; if the upper half is now bigger, move its smallest back.
- The median is `-low[0]` when the count is odd, or the average of `-low[0]` and `high[0]` when it is even.

For the stream 5, 15, 1, 3 the medians are 5, 10.0, 5 and 4.0. Each step costs O(log n). You will write it in problem p017; trace the four steps on paper first.

#### Try it 3.1

Trace the list after each line. (Remember: a push adds at the end, then the item "bubbles up" while it is smaller than its parent at index `(i - 1) // 2`.)

```python
import heapq
h = [3, 6, 4]
heapq.heappush(h, 1)
print(h)
print(heapq.heappop(h), h)
```

<details><summary>Answer</summary>

```text
[1, 3, 4, 6]
1 [3, 6, 4]
```

Push 1: `[3, 6, 4, 1]`; 1 is at index 3, its parent index 1 holds 6, swap: `[3, 1, 4, 6]`; parent index 0 holds 3, swap: `[1, 3, 4, 6]`. Pop returns 1, moves the last item (6) to the top and sinks it below its smaller child 3: `[3, 6, 4]`.
</details>

### 3.5 `bisect`: binary search on a sorted list

`bisect` finds where a value **would go** in a sorted list, in O(log n) steps, by halving the search range each time.

- `bisect_left(a, x)`: the first position where `x` could be inserted (before any equal items).
- `bisect_right(a, x)` (also called `bisect`): after any equal items.

```python
from bisect import bisect_left, bisect_right

a = [10, 20, 20, 20, 30]
print(bisect_left(a, 20), bisect_right(a, 20))
print(bisect_right(a, 20) - bisect_left(a, 20), "copies of 20")
i = bisect_left(a, 25)
print(i, i < len(a) and a[i] == 25)          # membership test
```
```text
1 4
3 copies of 20
4 False
```

The classic example from the documentation turns a score into a grade without a ladder of `if`s. The breakpoints are the lowest score of each grade above F:

```python
from bisect import bisect_right

def grade(score, breakpoints=(60, 70, 80, 90), grades="FDCBA"):
    return grades[bisect_right(breakpoints, score)]

print([grade(s) for s in [33, 59, 60, 77, 89, 90, 100]])
```
```text
['F', 'F', 'D', 'C', 'B', 'A', 'A']
```

`bisect_right` is the right choice here because a score **equal** to a breakpoint (60) belongs to the higher grade. With `bisect_left`, 60 would get `"F"`. Off-by-one at the boundaries is *the* bisect bug; always test the exact breakpoint values.

### 3.6 `insort`: keeping a list sorted

`insort(a, x)` inserts `x` in its sorted position. Finding the place is O(log n), but the insert itself still shifts items, so it is O(n) overall. That is fine for thousands of items; for millions of inserts, a heap or a sorted container from PyPI fits better.

Since Python 3.10 the functions take a `key=`. Note that `key` is applied to the list items, and **`x` is passed without the key** for `bisect_*` but **with the key** for `insort` (it inserts the whole record):

```python
from bisect import insort, bisect_left

board = []
for name, pts in [("asha", 70), ("ravi", 95), ("meera", 70), ("chen", 82)]:
    insort(board, (-pts, name))       # highest points first, ties by name
print([(name, -neg) for neg, name in board])

people = [("ravi", 19), ("asha", 23), ("chen", 31)]     # sorted by age
insort(people, ("dev", 25), key=lambda p: p[1])
print(people)
print(bisect_left(people, 30, key=lambda p: p[1]))       # x is an age here
```
```text
[('ravi', 95), ('chen', 82), ('asha', 70), ('meera', 70)]
[('ravi', 19), ('asha', 23), ('dev', 25), ('chen', 31)]
3
```

#### Try it 3.2

A ticket price depends on age: under 5 free, 5-17 pays 50, 18-59 pays 100, 60 and over pays 60. Write `price(age)` with `bisect` and two tuples, and check it at 4, 5, 17, 18, 59, 60.

<details><summary>Answer</summary>

```python
from bisect import bisect_right

def price(age):
    starts = (5, 18, 60)
    prices = (0, 50, 100, 60)
    return prices[bisect_right(starts, age)]

print([price(a) for a in [4, 5, 17, 18, 59, 60]])
```
```text
[0, 50, 50, 100, 100, 60]
```

The "starts" are the first age of each new band, so `bisect_right` puts an age equal to a start into the new band.
</details>

## 4. `datetime`: dates, times and durations

Dates look easy and are not. Months have different lengths, years can be leap years, and clocks jump twice a year in many countries. The `datetime` module knows all the calendar rules, so you never do date arithmetic with plain numbers.

### 4.1 The four main types

| Type | Holds | Example |
|---|---|---|
| `date` | year, month, day | `date(2025, 3, 9)` |
| `time` | hour, minute, second, microsecond | `time(14, 30)` |
| `datetime` | a date and a time (and maybe a time zone) | `datetime(2025, 3, 9, 14, 30)` |
| `timedelta` | a duration | `timedelta(days=2, hours=3)` |

All four are **immutable**. "Changing" a date with `.replace(...)` or `+` gives a new object.

```python
from datetime import date, datetime, timedelta

d = date(2024, 2, 28)
print(d + timedelta(days=1), d + timedelta(days=2))   # 2024 is a leap year
print(d.year, d.month, d.day, d.weekday(), d.isoweekday())   # Monday is 0 / 1
dt = datetime(2025, 3, 9, 14, 30)
print(dt, dt.date(), dt.time())
print(dt.replace(hour=9, minute=0))
print(datetime.combine(date(2025, 1, 1), dt.time()))
```
```text
2024-02-29 2024-03-01
2024 2 28 2 3
2025-03-09 14:30:00 2025-03-09 14:30:00
2025-03-09 09:00:00
2025-01-01 14:30:00
```

`weekday()` counts Monday as 0; `isoweekday()` counts Monday as 1. Both say 2024-02-28 was a Wednesday.

### 4.2 Parsing and formatting

Turning text into a `datetime` is **parsing**; turning a `datetime` into text is **formatting**. There are two families of tools.

**ISO 8601** (`2025-03-09T14:30:00`) is the international standard: biggest unit first, sorts correctly as text, no confusion between 03/09 and 09/03. Use it for anything a program will read.

```python
from datetime import datetime, date

dt = datetime.fromisoformat("2025-03-09T14:30:00")
print(dt, dt.isoformat(), dt.isoformat(sep=" ", timespec="minutes"))
print(date.fromisoformat("2025-03-09"))
print(datetime.fromisoformat("2025-03-09 14:30:00+05:30"))   # with an offset
```
```text
2025-03-09 14:30:00 2025-03-09T14:30:00 2025-03-09 14:30
2025-03-09
2025-03-09 14:30:00+05:30
```

**`strptime` / `strftime`** handle any other layout. The "p" in `strptime` is for *parse*, the "f" in `strftime` is for *format*. Both use the same `%` codes (chapter 3 used them inside f-strings):

| Code | Meaning | Example |
|---|---|---|
| `%Y` / `%y` | year, 4 / 2 digits | `2025` / `25` |
| `%m` / `%d` | month / day, 2 digits | `03` / `09` |
| `%H` / `%I` / `%p` | hour 24h / hour 12h / AM-PM | `14` / `02` / `PM` |
| `%M` / `%S` | minute / second | `30` / `05` |
| `%b` / `%B` | month name short / full | `Mar` / `March` |
| `%a` / `%A` | weekday short / full | `Sun` / `Sunday` |
| `%j` | day of the year | `068` |
| `%z` | UTC offset | `+0530` |

```python
from datetime import datetime

dt = datetime.strptime("09/03/2025 2:30 PM", "%d/%m/%Y %I:%M %p")
print(dt)
print(dt.strftime("%A %d %B %Y, %H:%M"))
print(f"{dt:%Y-%m-%d}", f"{dt:%j}")
try:
    datetime.strptime("2025-02-30", "%Y-%m-%d")
except ValueError as e:
    print("ValueError:", e)
```
```text
2025-03-09 14:30:00
Sunday 09 March 2025, 14:30
2025-03-09 068
ValueError: day 30 must be in range 1..28 for month 2 in year 2025
```

`strptime` checks the calendar: there is no 30 February. The format must match the text **exactly**, including separators; a missing space is a `ValueError`. Month and day names (`%b`, `%A`) depend on the computer's language settings (its *locale*), which is one more reason to prefer ISO numbers in files.

### 4.3 `timedelta`: durations and differences

Subtracting two dates or datetimes gives a `timedelta`. A `timedelta` stores only **days, seconds and microseconds**; everything else is converted.

```python
from datetime import date, datetime, timedelta

print(date(2025, 12, 25) - date(2025, 10, 28))
gap = datetime(2025, 3, 2, 8, 15) - datetime(2025, 3, 1, 20, 0)
print(gap, gap.days, gap.seconds, gap.total_seconds())
print(timedelta(hours=36), timedelta(minutes=-5))
print(timedelta(weeks=1) / timedelta(hours=1), "hours in a week")
print(timedelta(days=1) * 2.5)
```
```text
58 days, 0:00:00
12:15:00 0 44100 44100.0
1 day, 12:00:00 -1 day, 23:55:00
168.0 hours in a week
2 days, 12:00:00
```

Watch two things:

- `gap.seconds` is **only the part after the whole days**, not the total. For "how many seconds in all" use `total_seconds()`. Mixing these up is a classic bug.
- A negative duration is stored as negative days plus positive seconds: `-1 day, 23:55:00` means minus five minutes. Read it with `total_seconds()` (`-300.0`).

There is no `timedelta(months=1)`: months have different lengths, so "one month later" is a business decision (is one month after 31 January the 28th of February or the 3rd of March?). Write that rule yourself with `replace`, deciding what happens to day 31.

### 4.4 ISO weeks

Many companies plan in **ISO weeks**: weeks start on Monday, and week 1 is the week that contains the year's first Thursday. So the first days of January can belong to the last week of the **previous** year, and late December can belong to week 1 of the next.

```python
from datetime import date

for d in [date(2024, 12, 30), date(2025, 1, 1), date(2025, 12, 28), date(2026, 1, 1)]:
    iso = d.isocalendar()
    print(d, iso.year, iso.week, iso.weekday, f"{iso.year}-W{iso.week:02d}")
print(date.fromisocalendar(2025, 1, 1))     # Monday of week 1 of 2025
```
```text
2024-12-30 2025 1 1 2025-W01
2025-01-01 2025 1 3 2025-W01
2025-12-28 2025 52 7 2025-W52
2026-01-01 2026 1 4 2026-W01
2024-12-30
```

So 30 December 2024 is in **week 1 of 2025**. A weekly report that groups by `d.year` and `d.isocalendar().week` puts that day in "2024 week 1", which is wrong by a whole year. **Group by `(iso.year, iso.week)` together.**

#### Try it 4.1

Write `days_until(today, target)` that returns the number of whole days from `today` to the next occurrence of `target` (a `(month, day)` pair) on or after `today`. Check it with today = 2025-10-28 and targets (12, 25) and (1, 1) and (10, 28).

<details><summary>Answer</summary>

```python
from datetime import date

def days_until(today, target):
    month, day = target
    nxt = date(today.year, month, day)
    if nxt < today:
        nxt = date(today.year + 1, month, day)
    return (nxt - today).days

today = date(2025, 10, 28)
print(days_until(today, (12, 25)), days_until(today, (1, 1)), days_until(today, (10, 28)))
```
```text
58 65 0
```

(Careful with a target of 29 February: `date(2026, 2, 29)` is a `ValueError`. Decide a rule for it if your program needs one.)
</details>

### 4.5 Naive and aware datetimes

Here is the most important idea of the chapter's time sections. A `datetime` is one of two kinds:

- **naive**: no time zone. `datetime(2025, 3, 9, 14, 30)` means "14:30 *somewhere*". It is like a price with no currency.
- **aware**: has a `tzinfo`, so it names **one exact instant** in world time.

```python
from datetime import datetime, timezone, timedelta

naive = datetime(2025, 3, 9, 14, 30)
aware = datetime(2025, 3, 9, 14, 30, tzinfo=timezone.utc)
ist = timezone(timedelta(hours=5, minutes=30))
print(naive.tzinfo, naive.utcoffset())
print(aware, aware.utcoffset())
print(aware.astimezone(ist))
print(aware == datetime(2025, 3, 9, 20, 0, tzinfo=ist))   # same instant
try:
    print(naive < aware)
except TypeError as e:
    print("TypeError:", e)
```
```text
None None
2025-03-09 14:30:00+00:00 0:00:00
2025-03-09 20:00:00+05:30
True
TypeError: can't compare offset-naive and offset-aware datetimes
```

Python refuses to compare or subtract a naive and an aware datetime: it cannot know what the naive one means. That error is a friend. It finds the bug the first time you run the code, instead of giving answers that are off by 5.5 hours.

Two aware datetimes are **equal if they are the same instant**, even in different zones: 14:30 UTC and 20:00 in India are the same moment.

**Getting "now".** Choose the kind on purpose. `datetime.now(timezone.utc)` gives an **aware** datetime in UTC. `datetime.now()` with no argument gives **naive local time**: fine for a quick print, wrong for anything you store or compare.

`datetime.utcnow()` looks like the right tool but returns a **naive** datetime holding UTC numbers, which later code mistakes for local time. It is deprecated since Python 3.12. Write `datetime.now(timezone.utc)` instead. The same goes for `utcfromtimestamp`: use `datetime.fromtimestamp(ts, timezone.utc)`, as chapter 12 did for file times.

### 4.6 Converting, and the "replace" trap

There are two ways to put a zone on a datetime, and they do very different things:

- `dt.replace(tzinfo=zone)` **labels** the same wall-clock numbers with a zone. Use it for a naive time you *know* is in that zone.
- `dt.astimezone(zone)` **converts** an aware datetime: same instant, new wall-clock numbers.

```python
from datetime import datetime, timezone, timedelta

ist = timezone(timedelta(hours=5, minutes=30), "IST")
meeting_utc = datetime(2025, 1, 10, 9, 0, tzinfo=timezone.utc)

print(meeting_utc.astimezone(ist))     # convert: 14:30 in India
print(meeting_utc.replace(tzinfo=ist)) # relabel: 09:00 in India -- a different instant!
print(datetime(2025, 1, 10, 9, 0).replace(tzinfo=ist).astimezone(timezone.utc))
```
```text
2025-01-10 14:30:00+05:30
2025-01-10 09:00:00+05:30
2025-01-10 03:30:00+00:00
```

Using `replace` when you meant `astimezone` shifts the instant by the whole offset, silently. The last line shows the right pattern for input you receive as naive text: **label it with the zone it was written in, then convert.**

`astimezone()` with **no argument** on a naive datetime assumes the computer's local zone. That gives different answers on different machines, so pass a zone explicitly in programs.

## 5. Time zones with `zoneinfo`

### 5.1 Why a fixed offset is not a time zone

`timezone(timedelta(hours=5, minutes=30))` is a **fixed offset**. That is fine for India, which has used +05:30 all year for decades. It is wrong for London, New York and much of the world, because they use **daylight saving time** (DST): the offset changes twice a year, on dates set by law.

| Zone | Winter offset | Summer offset | 2025 changes |
|---|---|---|---|
| `Europe/London` | +00:00 (GMT) | +01:00 (BST) | 30 March, 26 October |
| `America/New_York` | -05:00 (EST) | -04:00 (EDT) | 9 March, 2 November |
| `Asia/Kolkata` | +05:30 | +05:30 | none |
| `UTC` | +00:00 | +00:00 | never |

A real time zone is a **set of rules**: "this offset from this date". The rules live in the **IANA time-zone database** (also called tz or zoneinfo), which names zones by region and city: `Europe/London`, `America/New_York`, `Asia/Kolkata`. Since Python 3.9, the `zoneinfo` module reads that database.

```python
from datetime import datetime
from zoneinfo import ZoneInfo

london = ZoneInfo("Europe/London")
for month in (1, 7):
    dt = datetime(2025, month, 15, 12, 0, tzinfo=london)
    print(dt, dt.tzname(), dt.utcoffset())
print(datetime(2025, 7, 15, 12, 0, tzinfo=ZoneInfo("Asia/Kolkata")).tzname())
```
```text
2025-01-15 12:00:00+00:00 GMT 0:00:00
2025-07-15 12:00:00+01:00 BST 1:00:00
IST
```

With `ZoneInfo`, it is safe to attach the zone with `tzinfo=` (or `replace(tzinfo=...)`): the zone looks at the date and picks the right offset itself.

Do not use three-letter names like `"IST"` or `"EST"` as zones. They are ambiguous (IST is India, Ireland and Israel) and do not carry the DST rules. Always use the `Region/City` names.

### 5.2 Converting across zones

The safe recipe for any "what time is it there?" question: **make an aware datetime in the source zone, then `astimezone` to each target zone.**

```python
from datetime import datetime
from zoneinfo import ZoneInfo

zones = ["Asia/Kolkata", "Europe/London", "America/New_York", "UTC"]
start = datetime(2025, 3, 20, 19, 30, tzinfo=ZoneInfo("Asia/Kolkata"))
for name in zones:
    local = start.astimezone(ZoneInfo(name))
    print(f"{name:17} {local:%a %d %b %H:%M} {local:%z}")
```
```text
Asia/Kolkata      Thu 20 Mar 19:30 +0530
Europe/London     Thu 20 Mar 14:00 +0000
America/New_York  Thu 20 Mar 10:00 -0400
UTC               Thu 20 Mar 14:00 +0000
```

On 20 March 2025 New York had already moved to summer time (9 March) but London had not (30 March). So for those three weeks, New York was only **4 hours** behind London instead of the usual 5. Any program that stored "London = New York + 5 hours" would schedule meetings an hour wrong. The zone database gets it right without you thinking about it.

#### Try it 5.1

A call is fixed at 09:00 New York time every Monday. Print the India time of the call on 3 March 2025 and on 10 March 2025. Why do they differ?

<details><summary>Answer</summary>

```python
from datetime import datetime
from zoneinfo import ZoneInfo

ny, india = ZoneInfo("America/New_York"), ZoneInfo("Asia/Kolkata")
for day in (3, 10):
    call = datetime(2025, 3, day, 9, 0, tzinfo=ny)
    print(call.date(), call.astimezone(india).strftime("%H:%M"))
```
```text
2025-03-03 19:30
2025-03-10 18:30
```

New York moved its clocks forward on 9 March, India did not. The meeting stays at 09:00 for New Yorkers, so it moves an hour earlier for everyone in India.
</details>

### 5.3 The DST gap: times that never happen

On 30 March 2025, London clocks jumped from **01:00 straight to 02:00**. A wall-clock time like 01:30 that day **never existed**. What does Python do if you ask for it?

```python
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

london = ZoneInfo("Europe/London")
ghost = datetime(2025, 3, 30, 1, 30, tzinfo=london)
print(ghost, ghost.tzname())
as_utc = ghost.astimezone(timezone.utc)
print(as_utc)
print(as_utc.astimezone(london))      # the round trip lands on a real time
```
```text
2025-03-30 01:30:00+00:00 GMT
2025-03-30 01:30:00+00:00
2025-03-30 02:30:00+01:00
```

Python does not raise an error. It quietly uses the offset from **before** the jump (GMT, +00:00), so "01:30" means 01:30 UTC, which is really **02:30 BST**. The round trip through UTC shows the real wall-clock time. If your program accepts times typed by users (an alarm, a booking), check for the gap: convert to UTC and back (`dt.astimezone(timezone.utc).astimezone(dt.tzinfo)`), and if the wall-clock numbers changed, the time did not exist.

### 5.4 The DST fold: times that happen twice

On 26 October 2025, London clocks went from **02:00 BST back to 01:00 GMT**. Every time from 01:00 to 01:59 that night happened **twice**: once in summer time, once in winter time. The clock "folds" over itself.

Python marks which of the two you mean with the `fold` attribute: `fold=0` (the default) is the **first** time, `fold=1` the **second**.

```python
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

london = ZoneInfo("Europe/London")
first = datetime(2025, 10, 26, 1, 30, tzinfo=london)            # fold=0
second = datetime(2025, 10, 26, 1, 30, fold=1, tzinfo=london)
for dt in (first, second):
    print(dt, dt.tzname(), "=", dt.astimezone(timezone.utc).strftime("%H:%M UTC"))
print(first == second)
print(second.astimezone(timezone.utc) - first.astimezone(timezone.utc))
```
```text
2025-10-26 01:30:00+01:00 BST = 00:30 UTC
2025-10-26 01:30:00+00:00 GMT = 01:30 UTC
True
1:00:00
```

Same wall-clock numbers, different instants, one hour apart. Note the strange `first == second` is `True`: for two datetimes that share **the same `tzinfo` object**, Python compares the wall-clock numbers and ignores `fold`. Compare UTC values when the instant matters.

This leads straight to the next trap.

### 5.5 Arithmetic: wall-clock time or elapsed time?

When you add a `timedelta` to an aware datetime, or subtract two aware datetimes **with the same `tzinfo`**, Python does **wall-clock arithmetic**: it works on the numbers on the clock face and ignores DST. Only when the zones differ (or when you go through UTC) does it compute **real elapsed time**.

```python
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

london = ZoneInfo("Europe/London")
sat = datetime(2025, 3, 29, 12, 0, tzinfo=london)
sun = sat + timedelta(days=1)
print(sun, sun.tzname())                   # still 12:00 on the clock
print(sun - sat)                           # wall-clock difference: 1 day
utc = timezone.utc
print(sun.astimezone(utc) - sat.astimezone(utc))   # real elapsed time
```
```text
2025-03-30 12:00:00+01:00 BST
1 day, 0:00:00
23:00:00
```

Both answers are "right"; they answer different questions:

- "The same time tomorrow" (a daily alarm, a 10:00 standup) is **wall-clock** arithmetic: add `timedelta(days=1)` in the local zone.
- "How long did the job run?", "has 24 hours of a free trial passed?", "rate-limit to one email per hour" is **elapsed** time: do it in UTC.

#### Try it 5.2

Predict the three lines, then run them. Clocks in New York went back one hour at 02:00 on 2 November 2025.

```python
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

ny = ZoneInfo("America/New_York")
a = datetime(2025, 11, 1, 22, 0, tzinfo=ny)
b = a + timedelta(hours=6)
print(b, b.tzname())
print(b - a)
print(b.astimezone(timezone.utc) - a.astimezone(timezone.utc))
```

<details><summary>Answer</summary>

```text
2025-11-02 04:00:00-05:00 EST
6:00:00
7:00:00
```

Adding 6 hours of wall-clock time gives 04:00 on the clock, now in EST. The same-zone subtraction also reads the clock: 6 hours. But the night was one hour longer, so 7 real hours passed, which only the UTC subtraction shows.
</details>

### 5.6 The golden rule: store UTC, show local

Put everything together and you get the rule every experienced team follows:

1. **At the edges, convert in.** When a time arrives (user input, a file, another system), make it aware in the zone it was written in, then convert it to UTC.
2. **Inside, store and compute in UTC.** Database columns, log lines, JSON, comparisons, durations. UTC has no gaps and no folds, so sorting and subtracting are always correct.
3. **At the edges, convert out.** Only when showing a time to a person, `astimezone(their_zone)`.

Store the user's **zone name** too (for example `"Asia/Kolkata"`) when you need future local times, such as "every Monday at 09:00 their time". A stored offset (`+05:30`) is not enough, because offsets change with DST and with laws.

```python
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

typed = "2025-07-04 18:00"                 # entered by a user in New York
local = datetime.fromisoformat(typed).replace(tzinfo=ZoneInfo("America/New_York"))
stored = local.astimezone(timezone.utc).isoformat()
print("stored:", stored)

loaded = datetime.fromisoformat(stored)
for viewer in ["Asia/Kolkata", "Europe/London"]:
    print(viewer, loaded.astimezone(ZoneInfo(viewer)).strftime("%d %b %H:%M"))
```
```text
stored: 2025-07-04T22:00:00+00:00
Asia/Kolkata 05 Jul 03:30
Europe/London 04 Jul 23:00
```

#### Try it 5.3

A colleague wrote this to check whether a 24-hour free trial is over. Find **two** problems.

```python
from datetime import datetime

def trial_over(started_text):
    started = datetime.strptime(started_text, "%Y-%m-%d %H:%M")
    return (datetime.now() - started).seconds >= 24 * 3600
```

<details><summary>Answer</summary>

1. `.seconds` is only the part after whole days, so it is always below 86,400 and the function **never** returns `True`. Use `total_seconds()`, or compare to a `timedelta(hours=24)`.
2. Both datetimes are naive local time, so the answer changes with the server's zone and is an hour off across a DST change. Parse the stored time as UTC (`.replace(tzinfo=timezone.utc)`) and use `datetime.now(timezone.utc)`.

Better, for testing: pass `now` in as a parameter (section 6.3).
</details>

## 6. Time-zone data, `tzdata`, and the `time` module

### 6.1 Where the zone rules come from, and Windows

`zoneinfo` does not contain the rules itself. It looks for them in this order:

1. the operating system's database (on Linux and macOS, files under `/usr/share/zoneinfo`);
2. the **`tzdata`** package from PyPI, if it is installed.

**Windows has no IANA database** that Python can read. On Windows without `tzdata`, every zone name fails with an error like this (the same error you will see below for a made-up zone):

```text
zoneinfo._common.ZoneInfoNotFoundError: 'No time zone found with key Europe/London'
```

The fix is one command, run in PowerShell from the course folder (in the older `cmd` window, write the slashes as `\`):

```text
.venv/Scripts/python -m pip install tzdata
```

**This course's engine does it for you**: `tzdata` is listed as a Windows-only dependency of the `learn` engine, so a normal install on Windows pulls it in. If you still see `ZoneInfoNotFoundError` (an old environment, or a different Python), run the command above. The core.17 tests check for the data first and print that same command instead of a confusing traceback.

Two more facts worth knowing:

- Zone rules change several times a year, when some country changes its law. The OS database is updated by system updates; `tzdata` by `pip install --upgrade tzdata`. Our examples use 2024 and 2025 dates in zones with stable rules, so the answers will not change.
- `zoneinfo.available_timezones()` lists every known zone name (about 600; the exact number is machine-specific). Handy for validating a zone a user types.

```python
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError, available_timezones

print("Asia/Kolkata" in available_timezones(), "Mars/Base" in available_timezones())
try:
    ZoneInfo("Mars/Base")
except ZoneInfoNotFoundError as e:
    print(type(e).__name__, e)
```
```text
True False
ZoneInfoNotFoundError 'No time zone found with key Mars/Base'
```

### 6.2 The `time` module: three different clocks

The `time` module is older and lower level than `datetime`. Its most useful parts today are three **clocks**, each for a different job:

| Function | Gives | Use it for |
|---|---|---|
| `time.time()` | seconds since 1 January 1970 UTC (the "Unix epoch") | timestamps, file times |
| `time.monotonic()` | seconds from an arbitrary start, never goes backwards | timeouts, "has 5 s passed?" |
| `time.perf_counter()` | like monotonic, with the highest resolution | measuring how long code takes |

Why not use `time.time()` for everything? Because the wall clock can **jump**: the computer syncs with a time server, a user changes the clock, a virtual machine wakes up. A duration measured with `time.time()` can come out negative or wildly long. `monotonic` and `perf_counter` only ever move forward, but their numbers mean nothing alone: only the **difference** between two readings is useful.

```python
import time

start = time.perf_counter()
total = sum(i * i for i in range(200_000))
elapsed = time.perf_counter() - start
print(f"took {elapsed * 1000:.1f} ms")       # machine-specific
print(time.time() > 1_700_000_000)           # seconds since 1970: a big number
print(time.strftime("%Y-%m-%d", time.gmtime(0)))
```
```text
took 21.1 ms
True
1970-01-01
```

For timing small pieces of code properly (many repeats, best of several runs) use the `timeit` module, which chapter 11 used. `time.sleep(seconds)` pauses the program; you will see below why tests should avoid it.

### 6.3 Injecting the clock

Code that calls `datetime.now()` or `time.monotonic()` inside is hard to test: the answer changes every run, and testing "after 24 hours" would mean waiting 24 hours. The fix is a design habit, not a module: **let the caller pass the clock in**.

```python
import time

def timed(func, clock=time.perf_counter):      # the real clock by default
    start = clock()
    result = func()
    return result, clock() - start

readings = iter([100.0, 102.5])                 # a test: a fake clock we control
print(timed(lambda: "done", clock=lambda: next(readings)))
```
```text
('done', 2.5)
```

The same idea works for dates: write `def is_expired(start, now)` and call it as `is_expired(start, datetime.now(timezone.utc))` in the program, but with a fixed `now` in tests. The project in section 15 takes a `now` argument for exactly this reason. Many problems in this module do the same.

#### Try it 6.1

Write `RateLimiter(per_seconds, clock)` with a method `allow()` that returns `True` at most once per `per_seconds` (the first call is allowed). Test it with a fake clock reading 0, 0.5, 1.0, 1.2, 2.0 and `per_seconds=1`.

<details><summary>Answer</summary>

```python
class RateLimiter:
    def __init__(self, per_seconds, clock):
        self.per = per_seconds
        self.clock = clock
        self.last = None

    def allow(self):
        now = self.clock()
        if self.last is None or now - self.last >= self.per:
            self.last = now
            return True
        return False

times = iter([0, 0.5, 1.0, 1.2, 2.0])
rl = RateLimiter(1, clock=lambda: next(times))
print([rl.allow() for _ in range(5)])
```
```text
[True, False, True, False, True]
```

In the real program you would pass `clock=time.monotonic`: a rate limit is about elapsed time, so it must not jump when the wall clock changes.
</details>

## 7. `math`, `statistics`, `random` and `secrets`

### 7.1 `math`: the tools that floats need

Chapter 2 showed that `0.1 + 0.2 != 0.3`, because floats are stored in binary. `math` has the tools that make float code correct.

```python
import math

print(0.1 + 0.2 == 0.3, math.isclose(0.1 + 0.2, 0.3))
print(math.isclose(1e-12, 0.0), math.isclose(1e-12, 0.0, abs_tol=1e-9))
print(math.floor(-2.5), math.ceil(-2.5), math.trunc(-2.5), int(-2.5), round(2.5), round(3.5))
print(math.comb(5, 2), math.perm(5, 2), math.factorial(5))
print(math.gcd(12, 18), math.lcm(4, 6), math.prod([2, 3, 4]))
print(math.sqrt(2), math.isqrt(10), math.hypot(3, 4), math.inf > 10**100)
```
```text
False True
False True
-3 -2 -2 -2 2 4
10 20 120
6 12 24
1.4142135623730951 3 5.0 True
```

Things to remember:

- **`isclose` uses a relative tolerance** (by default "equal in the first 9 significant digits"). Relative to zero, nothing is close, so comparing with 0 needs an `abs_tol`.
- **`floor` rounds down, `trunc` (and `int()`) cut towards zero.** They differ only for negative numbers, which is exactly where bugs hide. `round` uses "round half to even" (banker's rounding): `round(2.5)` is 2.
- `comb(n, k)` counts **choices** (order does not matter): 10 pairs from 5 people. `perm(n, k)` counts **arrangements** (order matters): 20. `gcd` and `lcm` accept any number of integers since Python 3.9.
- `isqrt` gives the exact integer square root of huge integers, where `int(math.sqrt(n))` can be off by one for numbers above about 10**15.

**Adding many floats.** Each `+` rounds the result to the nearest float, and the small errors pile up. `math.fsum` tracks the lost bits and returns the correctly rounded total:

```python
import math

values = [0.1] * 10
total = 0.0
for v in values:
    total += v
print(total, math.fsum(values), sum(values))
print(total == 1.0, math.fsum(values) == 1.0)
```
```text
0.9999999999999999 1.0 1.0
False True
```

The plain loop drifts to `0.9999999999999999`. Since **Python 3.12**, the built-in `sum()` also uses a compensated algorithm for floats, which is why it printed `1.0` here; on Python 3.11, `sum(values)` gives `0.9999999999999999` like the loop. `math.fsum` is exact on every version, so use it when the total matters (money is better still as integers of cents, or `decimal.Decimal`), and use `isclose` to compare floats, never `==`.

### 7.2 `statistics`: describing data

```python
import statistics as st

marks = [72, 85, 85, 90, 64, 78, 85, 91]
print(st.mean(marks), st.median(marks), st.mode(marks))
print(st.median([1, 2, 3, 4]), st.median_low([1, 2, 3, 4]), st.median_high([1, 2, 3, 4]))
print(st.multimode(["a", "b", "b", "a", "c"]))
print(round(st.pstdev(marks), 3), round(st.stdev(marks), 3))
print(st.quantiles(marks, n=4))           # the three quartile cut points
try:
    st.mean([])
except st.StatisticsError as e:
    print("StatisticsError:", e)
```
```text
81.25 85.0 85
2.5 2 3
['a', 'b']
8.714 9.316
[73.5, 85.0, 88.75]
StatisticsError: mean requires at least one data point
```

- **`mean`** is the average; it is pulled by outliers. **`median`** is the middle value (the average of the two middle ones for even counts) and ignores outliers: a better "typical" salary or response time. `median_low`/`median_high` always return a real data value.
- **`mode`** returns the first most common value; **`multimode`** returns all of them.
- **`pstdev`** is the standard deviation of a whole *population*; **`stdev`** is the *sample* version (divides by n - 1), for when your data is a sample of something bigger. If you are not sure, you probably want `stdev`.
- Empty data raises `StatisticsError` rather than returning a wrong 0. `fmean` is a faster `mean` that always returns a float.

### 7.3 `random`: repeatable chance

`random` makes **pseudo-random** numbers: a deterministic algorithm (the Mersenne Twister) that looks random. The same **seed** always produces the same sequence. That is a feature: simulations, games and tests can be repeated exactly.

Use your **own `random.Random(seed)` object** instead of the module-level functions. The module functions share one global generator, so any other code that calls `random.random()` changes your sequence.

```python
import random

rng = random.Random(42)
print(rng.random(), rng.randint(1, 6), rng.uniform(1.0, 2.0))
deck = list(range(1, 11))
print(rng.choice(deck), rng.sample(deck, 3))
print(rng.choices(["win", "lose"], weights=[1, 9], k=5))
print(rng.shuffle(deck), deck)            # shuffles in place, returns None

again = random.Random(42)
print(again.random())                      # same seed, same first number
```
```text
0.6394267984578837 1 1.7415504997598328
4 [4, 3, 2]
['lose', 'lose', 'win', 'lose', 'win']
None [3, 6, 8, 9, 7, 2, 5, 1, 10, 4]
0.6394267984578837
```

- `randint(a, b)` **includes both ends**; `randrange(a, b)` excludes `b`, like `range`.
- `sample(pop, k)` picks **without** replacement (no repeats); `choices(pop, k=...)` picks **with** replacement and can take `weights`.
- `shuffle` changes the list **in place** and returns `None`; `x = rng.shuffle(x)` destroys your list. For a shuffled copy, use `rng.sample(x, len(x))`.
- A seed gives the same numbers on every computer **for the same Python version**. Most methods have stayed stable for years, but tests should not hard-code long random outputs; check properties ("all items still there", "length 3") or values from the same seed.

### 7.4 `secrets`: when guessing must be impossible

The Mersenne Twister is predictable: after seeing 624 outputs, anyone can compute all future ones. That is fine for a dice game and a disaster for a password-reset link. The **`secrets`** module uses the operating system's cryptographic random source, which is designed to be unpredictable.

```python
import secrets
import string

print(secrets.token_hex(16))              # 32 hex characters     (machine-specific)
print(secrets.token_urlsafe(16))          # about 22 URL-safe chars (machine-specific)
alphabet = string.ascii_letters + string.digits
print("".join(secrets.choice(alphabet) for _ in range(12)))      # (machine-specific)
print(secrets.randbelow(10) in range(10))
print(secrets.compare_digest("abc123", "abc123"), secrets.compare_digest("abc123", "abc124"))
```
```text
49c5a25f9bd177ef64c5a477871027f2
sg824OoyRj7t_Xdr4olYIQ
rO4bZx1uSmTf
True
True False
```

`compare_digest` compares two strings in a time that does not depend on **where** they first differ. A normal `==` stops at the first different character, and an attacker who measures response times can guess a secret token one character at a time. Use it whenever you compare a token a user sent with the real one.

| Use | Module |
|---|---|
| simulations, games, shuffling test data, sampling | `random.Random(seed)` |
| passwords, tokens, reset links, session ids, API keys | `secrets` |

A simple rule: **if knowing the value would let someone in, it comes from `secrets`.** And `secrets` cannot be seeded, on purpose; test code that uses it by checking properties (length, allowed characters), never exact values.

#### Try it 7.1

Write `make_password(length)` that uses `secrets` and returns a password of letters and digits containing **at least one digit and one uppercase letter**. Hint: generate, check, and try again if the check fails.

<details><summary>Answer</summary>

Loop: build a candidate with `"".join(secrets.choice(alphabet) for _ in range(length))`, where `alphabet = string.ascii_letters + string.digits`; return it if `any(c.isdigit() for c in pw)` and `any(c.isupper() for c in pw)`, otherwise try again. Raise `ValueError` for a length below 2, which could never pass. Retrying keeps every character uniformly random; "forcing" a digit into the first position makes passwords easier to guess. Test it by properties: length, allowed characters, the two rules.
</details>

#### Try it 7.2

`random.Random(seed)` or `secrets`? (a) shuffling quiz questions so a student can replay the same quiz; (b) a 6-digit login code sent by SMS; (c) picking 1% of log lines for a report; (d) the name of an uploaded file that other users must not be able to guess.

<details><summary>Answer</summary>

(a) `random.Random(seed)`: repeatable on purpose. (b) `secrets` (`f"{secrets.randbelow(10**6):06d}"`): guessing it logs someone in. (c) `random`: nobody gains by predicting it. (d) `secrets.token_urlsafe()`: a guessable name leaks other people's files.
</details>

## 8. `copy` and `pprint`

### 8.1 Shallow and deep, one level deeper

Chapter 5 showed the core rule: `copy.copy` (like `list(x)`, `x[:]`, `dict.copy()`) makes a new **outer** container but shares the inner objects; `copy.deepcopy` copies all the way down. Here are three things it did not cover.

**1. The "mutable default" copy trap.** A module-level dict of defaults, copied shallowly for each user:

```python
import copy

DEFAULTS = {"theme": "light", "plugins": ["spell"]}

def new_settings_bad():
    return DEFAULTS.copy()               # shallow

s1 = new_settings_bad()
s1["theme"] = "dark"                     # fine: rebinds a key in s1 only
s1["plugins"].append("git")              # mutates the SHARED list
print(DEFAULTS)

DEFAULTS["plugins"].remove("git")
s2 = copy.deepcopy(DEFAULTS)
s2["plugins"].append("git")
print(DEFAULTS, s2)
```
```text
{'theme': 'light', 'plugins': ['spell', 'git']}
{'theme': 'light', 'plugins': ['spell']} {'theme': 'light', 'plugins': ['spell', 'git']}
```

The same bug appears with a class attribute `defaults = {...}` used as `self.opts = self.defaults`, and with function default arguments (chapter 6). The fix is the same: **deep-copy nested defaults** (or build them fresh in a function).

**2. `deepcopy` keeps shared references and cycles.** `deepcopy` remembers every object it has copied in a dict called the *memo*. If the same inner object appears twice, the copy has **one** new object appearing twice, not two copies. That keeps the shape of your data and also makes cycles safe.

```python
import copy

row = [0, 0]
grid = [row, row]                 # the same list twice
g2 = copy.deepcopy(grid)
print(g2[0] is g2[1], g2[0] is row)
g2[0][0] = 9
print(g2)

node = {"name": "a"}
node["self"] = node               # a cycle
n2 = copy.deepcopy(node)
print(n2["self"] is n2, n2 is node)
```
```text
True False
[[9, 0], [9, 0]]
True False
```

**3. Customising copies.** A class can control both kinds of copy with `__copy__(self)` and `__deepcopy__(self, memo)`. A common reason: an object holds something that must not be copied, such as an open file, a lock or a large cache.

```python
import copy


class Document:
    def __init__(self, title, tags, cache=None):
        self.title = title
        self.tags = tags
        self.cache = cache if cache is not None else {}

    def __copy__(self):
        return Document(self.title, self.tags, self.cache)

    def __deepcopy__(self, memo):
        # copy the data, but start the copy with an empty cache
        return Document(copy.deepcopy(self.title, memo), copy.deepcopy(self.tags, memo))


d = Document("Notes", ["a"], cache={"html": "<p>..."})
shallow, deep = copy.copy(d), copy.deepcopy(d)
print(shallow.tags is d.tags, deep.tags is d.tags, deep.tags == d.tags, deep.cache)
```
```text
True False True {}
```

Pass `memo` on to inner `deepcopy` calls so that shared references inside your object stay shared.

#### Try it 8.1

Predict the four values, then run it.

```python
import copy
inner = [1]
data = {"a": inner, "b": inner, "c": (inner, 2)}
s = copy.copy(data)
d = copy.deepcopy(data)
print(s["a"] is inner, d["a"] is inner, d["a"] is d["b"], d["c"][0] is d["a"])
```

<details><summary>Answer</summary>

```text
True False True True
```

The shallow copy shares `inner`. The deep copy makes **one** new list (thanks to the memo) and uses it everywhere `inner` appeared, including inside the tuple. The tuple itself had to be rebuilt, because one of its items changed.
</details>

### 8.2 `pprint`: printing big data readably

`print` puts a nested structure on one long line. `pprint` ("pretty print") breaks it into lines that fit a width:

```python
from pprint import pprint, pformat, pp

config = {"server": {"host": "127.0.0.1", "ports": [8000, 8001, 8002]},
          "users": ["asha", "ravi", "meera"], "debug": False}
pprint(config, width=50)
pprint(config, depth=1)
pp({"z": 1, "a": 2})              # pp keeps insertion order
pprint({"z": 1, "a": 2})          # pprint sorts keys
```
```text
{'debug': False,
 'server': {'host': '127.0.0.1',
            'ports': [8000, 8001, 8002]},
 'users': ['asha', 'ravi', 'meera']}
{'debug': False, 'server': {...}, 'users': [...]}
{'z': 1, 'a': 2}
{'a': 2, 'z': 1}
```

- `pformat` returns the string instead of printing it: perfect for log messages and test failure messages.
- `width` is the target line width; `depth` replaces deeper levels with `...`; `compact=True` packs many short items onto each line.
- **`pprint` sorts dict keys by default** (`sort_dicts=True`); `pp` (Python 3.8+) does not. If the order of keys matters to what you are checking, use `pp` or `sort_dicts=False`.

## 9. `sys`, `os`, `shlex` and `subprocess`

### 9.1 `sys` and `os`: the program and the machine

Chapter 12 used `sys.argv`, `sys.exit` and the standard streams; chapter 13 used `sys.path`. A few more facts are used all the time:

```python
import os
import sys

print(sys.version_info >= (3, 11), sys.platform)   # 'linux', 'win32' or 'darwin'
print(sys.executable)                    # (machine-specific path)
print(os.getpid())                       # (machine-specific)
print(os.cpu_count() >= 1, repr(os.sep), repr(os.linesep))
os.environ["APP_MODE"] = "test"          # visible to this process and its children
print(os.environ.get("APP_MODE"), os.environ.get("NOT_SET", "default"))
```
```text
True linux
/home/you/learning module/.venv/bin/python3
68222
True '/' '\n'
test default
```

`sys.executable` is the full path of the Python program running *right now*, including the one inside your virtual environment. That makes it the right way to start "another Python" from Python, as the next sections do.

**`os.walk`, more deeply.** Chapter 12 listed the `(folder, dirs, files)` triples. Two more tricks: you can **prune** the walk by changing the `dirs` list in place (only with the default top-down order), and you can add up sizes per folder:

```python
import os
from pathlib import Path

for p in ["proj/a.py", "proj/src/b.py", "proj/.git/obj", "proj/src/__pycache__/b.pyc"]:
    Path(p).parent.mkdir(parents=True, exist_ok=True)
    Path(p).write_text("x" * 100, encoding="utf-8")

total = 0
for folder, dirs, files in os.walk("proj"):
    dirs[:] = sorted(d for d in dirs if d not in {".git", "__pycache__"})   # prune
    size = sum(os.path.getsize(os.path.join(folder, f)) for f in files)
    total += size
    print(folder, size)
print("total", total)
```
```text
proj 100
proj/src 100
total 200
```

`dirs[:] = ...` replaces the list's contents; `dirs = ...` would only rebind the name, and the walk would still go everywhere. Sorting `dirs` also makes the order repeatable.

### 9.2 `shlex`: splitting command lines like a shell

A command line is not just `text.split()`. Quotes group words, and spaces inside a file name must survive:

```python
import shlex

cmd = 'grep -n "hello world" "my notes.txt"'
print(cmd.split())
print(shlex.split(cmd))
args = ["echo", "it's", "a b", "$HOME"]
print(shlex.join(args))
print(shlex.quote("file; rm -rf ~"))
```
```text
['grep', '-n', '"hello', 'world"', '"my', 'notes.txt"']
['grep', '-n', 'hello world', 'my notes.txt']
echo 'it'"'"'s' 'a b' '$HOME'
'file; rm -rf ~'
```

`shlex.split` turns a command string into the **list of arguments** that `subprocess` wants; `shlex.join` and `shlex.quote` go the other way, adding quotes so a shell treats each piece as plain text. `shlex` follows Unix shell rules. Windows command lines quote differently, so on Windows avoid building command strings at all: keep arguments as a list from the start.

### 9.3 `subprocess.run`: running another program

`subprocess.run` starts a program, waits for it to finish, and returns a `CompletedProcess`. Pass the command as a **list**: program first, then each argument.

```python
import subprocess
import sys

result = subprocess.run(
    [sys.executable, "-c", "import sys; print('hi', sys.argv[1:]); print('oops', file=sys.stderr)", "a b", "c"],
    capture_output=True,    # collect stdout and stderr instead of showing them
    text=True,              # decode bytes to str
)
print(result.returncode)
print(repr(result.stdout), repr(result.stderr))
print(result.args[-2:])
```
```text
0
"hi ['a b', 'c']\n" 'oops\n'
['a b', 'c']
```

The useful arguments:

| Argument | Effect |
|---|---|
| `capture_output=True` | fill `result.stdout` and `result.stderr` |
| `text=True` | strings instead of bytes (add `encoding="utf-8"` for non-English output on Windows) |
| `check=True` | raise `CalledProcessError` if the exit code is not 0 |
| `timeout=5` | kill the program after 5 seconds, raise `TimeoutExpired` |
| `input="..."` | send this text to the program's stdin |
| `cwd=path` | run it in another folder |
| `env={...}` | its environment (start from `{**os.environ, ...}` to keep `PATH`) |

**Exit codes and errors.** A program that fails usually does not raise anything in *your* program; it just returns a non-zero `returncode`. Check it, or let `check=True` turn it into an exception:

```python
import subprocess
import sys

r = subprocess.run([sys.executable, "-c", "import sys; sys.exit(3)"])
print("returncode", r.returncode)
try:
    subprocess.run([sys.executable, "-c", "raise SystemExit(2)"], check=True)
except subprocess.CalledProcessError as e:
    print("CalledProcessError:", e.returncode)
try:
    subprocess.run([sys.executable, "-c", "import time; time.sleep(10)"], timeout=0.5)
except subprocess.TimeoutExpired as e:
    print("TimeoutExpired after", e.timeout, "s")
r = subprocess.run([sys.executable, "-c", "print(input().upper())"],
                   input="hello\n", capture_output=True, text=True)
print(r.stdout.strip())
```
```text
returncode 3
CalledProcessError: 2
TimeoutExpired after 0.5 s
HELLO
```

Always give a `timeout` when you run something that could hang (a network tool, a program waiting for input). Without it, your program waits forever. A missing program raises `FileNotFoundError` before anything runs.

`subprocess.run` is all you need for "run and wait". For a long-running process you talk to while it runs, there is the lower-level `subprocess.Popen`; you will rarely need it.

### 9.4 `shell=True` and command injection

`subprocess.run("some command string", shell=True)` hands the whole string to a shell (`/bin/sh` or `cmd.exe`), which interprets `;`, `|`, `&&`, `$VAR` and backticks. If any part of that string comes from a user, the user can run **anything**:

```python
import subprocess
import sys

filename = 'x.txt"); print("INJECTED: I could delete your files"); print("'   # "a file name" from a user
code = f'print("processing {filename}")'
subprocess.run([sys.executable, "-c", code])           # same bug as an f-string into a shell
subprocess.run([sys.executable, "-c", "import sys; print('processing', sys.argv[1])", filename])
```
```text
processing x.txt
INJECTED: I could delete your files

processing x.txt"); print("INJECTED: I could delete your files"); print("
```

The first call pastes user text into code and the "file name" breaks out of the quotes: exactly what happens when you paste it into a shell command with `shell=True`. The second passes it as **one separate argument**, so it can only ever be a file name.

The rules:

1. **Pass a list, and leave `shell=False`** (the default). Each argument goes to the program as-is; no shell ever reads it.
2. If you truly need shell features (pipes, wildcards), do that part in Python instead: `glob` for wildcards, two `run` calls (feeding the first's `stdout` as the second's `input`) for a pipe.
3. If a shell is unavoidable on Unix, quote every user piece with `shlex.quote`.

#### Try it 9.1

Write `run_python(code, timeout=5)` that runs a piece of Python code in a new interpreter and returns `(returncode, stdout, stderr)` with text output, and returns `(None, "", "timeout")` if it runs too long. Test it with `print(6*7)`, `1/0` and an endless loop with a 0.5 s timeout.

<details><summary>Answer</summary>

Call `subprocess.run([sys.executable, "-c", code], capture_output=True, text=True, timeout=timeout)` inside `try`, and return `(r.returncode, r.stdout, r.stderr)`. In `except subprocess.TimeoutExpired:` return `(None, "", "timeout")`. Expected results: `(0, "42\n", "")` for `print(6*7)`; return code `1` and a stderr whose last line is `ZeroDivisionError: division by zero` for `1/0`; `(None, "", "timeout")` for `while True: pass`. Note there is no `check=True`: a failing program is a normal result here, not an exception.
</details>

### 9.5 Which module for which job?

| Job | Use | Not |
|---|---|---|
| copy, move, delete trees, archives, find a program (`which`) | `shutil` | `subprocess` with `cp`, `rm`, `zip` |
| paths, listing, reading files | `pathlib` / `os` | `subprocess` with `ls`, `cat`, `dir` |
| environment variables, process id, walking folders | `os` | |
| the running interpreter: argv, exit, path, version, streams | `sys` | |
| a **different program** (git, ffmpeg, a compiler, another Python) | `subprocess.run` with a list | `os.system`, `shell=True` |

Calling `ls` or `copy` through `subprocess` is the most common misuse: it breaks on the other operating system, is slower, and returns text you must parse. `os.system("...")` is the old way to run a command: it always uses a shell and cannot capture output, so prefer `subprocess.run`.

#### Try it 9.2

Name the tool for each job: (a) is `git` installed? (b) the current git commit id as a string; (c) delete a `build` folder; (d) read the `HOME` variable with a fallback; (e) stop the program with exit code 2.

<details><summary>Answer</summary>

(a) `shutil.which("git")` (`None` if missing). (b) `subprocess.run(["git", "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()`. (c) `shutil.rmtree("build")`, after checking the path. (d) `os.environ.get("HOME", default)`. (e) `sys.exit(2)`.
</details>

## 10. `hashlib`, `uuid`, `base64` and `struct`

### 10.1 `hashlib`: fingerprints of data

A **hash function** turns any amount of data into a short, fixed-size "fingerprint". The same input always gives the same hash; change one bit and the hash changes completely; and (for a cryptographic hash such as SHA-256) nobody can find two inputs with the same hash in practice. Uses: checking a download is not corrupted, finding duplicate files, detecting that a file changed.

```python
import hashlib

print(hashlib.sha256(b"hello").hexdigest())
print(hashlib.sha256(b"hello!").hexdigest())
print(hashlib.sha256("héllo".encode("utf-8")).hexdigest()[:16], len(hashlib.sha256(b"").digest()))
h = hashlib.sha256()
h.update(b"hel")
h.update(b"lo")                          # feeding in pieces gives the same result
print(h.hexdigest() == hashlib.sha256(b"hello").hexdigest())
```
```text
2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824
ce06092fb948d9ffac7d1a376e404b26b7575bcc11ee05a4615fef4fec3a308b
3c48591d8d098a45 32
True
```

Hashes work on **bytes**, so encode text first. `hexdigest()` gives 64 hex characters for SHA-256; `digest()` gives the raw 32 bytes.

**Big files: hash in chunks.** `update` exists so that you never need the whole file in memory. Read a fixed-size block at a time, as in chapter 12's streaming section:

```python
import hashlib
from pathlib import Path

def sha256_file(path, chunk_size=64 * 1024):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while chunk := f.read(chunk_size):
            h.update(chunk)
    return h.hexdigest()

Path("big.bin").write_bytes(b"x" * 1_000_000)
print(sha256_file("big.bin")[:16])
with open("big.bin", "rb") as f:
    print(hashlib.file_digest(f, "sha256").hexdigest()[:16])     # Python 3.11+
```
```text
1b977e9f84f1b26b
1b977e9f84f1b26b
```

**Finding duplicate files** is a nice combination of tools: group files by **size** first with `defaultdict(list)` (cheap: `p.stat().st_size`, no reading), then hash only the files in groups with more than one member, grouping again by digest. Files that share a digest are duplicates. Most files have a unique size and are never read at all.

**Which algorithm?** Use `sha256` by default. `md5` and `sha1` are broken for security (people can make collisions on purpose), although you still see them used as quick checksums. And **never store passwords with a plain hash**: a fast hash lets an attacker try billions of guesses per second. Password storage needs a deliberately slow function with a salt, such as `hashlib.scrypt` or `hashlib.pbkdf2_hmac`, or a library built for it.

### 10.2 `uuid`: unique ids without a central counter

A **UUID** is a 128-bit id, written as 36 characters. You can create one on any computer, at any time, without asking a database for "the next number", and still be confident no one else made the same one.

```python
import uuid

print(uuid.uuid4())                                       # random (machine-specific)
a = uuid.uuid5(uuid.NAMESPACE_URL, "https://example.com/page/1")
b = uuid.uuid5(uuid.NAMESPACE_URL, "https://example.com/page/1")
print(a, a == b)
print(uuid.uuid5(uuid.NAMESPACE_URL, "https://example.com/page/2"))
u = uuid.UUID(str(a))
print(u.version, u.hex[:8], len(str(u)))
```
```text
5507bb15-4dc4-4897-b642-d13f2c18705f
3230a931-a04c-5023-a04e-a09ce6edbfeb True
3e4e273f-553d-5586-b787-285704e8d7bd
5 3230a931 36
```

- **`uuid4()`** is random: use it for new records, upload names, request ids.
- **`uuid5(namespace, name)`** is **deterministic**: the same namespace and name always give the same UUID. Use it when you need a stable id derived from something you already have (a URL, an email, a file path), for example so that importing the same data twice does not create duplicates. `NAMESPACE_URL`, `NAMESPACE_DNS` and friends are predefined; you can also use any UUID of your own as a namespace.
- **`uuid1()`** mixes in the time and the computer's network address. It leaks both, so prefer `uuid4`.

### 10.3 `base64`: bytes that can travel as text

Some places accept only text: JSON, URLs, email, HTML attributes. **Base64** encodes any bytes using only 64 safe characters (letters, digits, `+`, `/`), plus `=` for padding. Every 3 bytes become 4 characters, so the result is about a third bigger.

```python
import base64

raw = bytes([251, 255, 0, 65])
std = base64.b64encode(raw)
url = base64.urlsafe_b64encode(raw)
print(std, url)
print(base64.b64decode(std) == raw, base64.urlsafe_b64decode(url) == raw)
token = url.rstrip(b"=").decode("ascii")         # often sent without padding
padded = token + "=" * (-len(token) % 4)         # put the padding back
print(token, base64.urlsafe_b64decode(padded) == raw)
print(base64.b64encode("नमस्ते".encode("utf-8")).decode("ascii"))
```
```text
b'+/8AQQ==' b'-_8AQQ=='
True True
-_8AQQ True
4KSo4KSu4KS44KWN4KSk4KWH
```

- The **URL-safe** variant uses `-` and `_` instead of `+` and `/`, which mean something special in URLs and file names.
- The input and output are **bytes**. Encode text with UTF-8 first; `.decode("ascii")` the result to get a `str` for JSON.
- Removing `=` padding is common in tokens. To decode, add `-len(s) % 4` equals signs back.
- **Base64 is not encryption.** Anyone can decode it. It only changes the alphabet.

### 10.4 `struct`: fixed-size binary records

Many file formats and network protocols store numbers as raw bytes in a fixed layout: "2 bytes of version, then 4 bytes of length". `struct` converts between Python values and such bytes using a **format string**.

| Code | C type | Size (standard) |
|---|---|---|
| `b` / `B` | signed / unsigned char | 1 |
| `h` / `H` | short | 2 |
| `i` / `I` | int | 4 |
| `q` / `Q` | long long | 8 |
| `f` / `d` | float / double | 4 / 8 |
| `?` | bool | 1 |
| `4s` | 4 bytes | 4 |

The **first character** sets the **byte order** (endianness): `<` little-endian, `>` big-endian, `!` network order (= big-endian). A number like 258 is the two bytes `01 02` in big-endian (biggest part first) and `02 01` in little-endian.

```python
import struct

print(struct.pack(">H", 258), struct.pack("<H", 258))
header = struct.pack("<4sHI", b"LOG1", 2, 1_000_000)     # magic, version, count
print(header, len(header), struct.calcsize("<4sHI"))
magic, version, count = struct.unpack("<4sHI", header)
print(magic, version, count)
print(struct.calcsize("4sHI"), struct.calcsize("=4sHI"))   # native: padding!
records = struct.pack("<hh", -1, 7) + struct.pack("<hh", 3, 4)
print(list(struct.iter_unpack("<hh", records)))
try:
    struct.pack("<B", 300)
except struct.error as e:
    print("struct.error:", e)
```
```text
b'\x01\x02' b'\x02\x01'
b'LOG1\x02\x00@B\x0f\x00' 10 10
b'LOG1' 2 1000000
12 10
[(-1, 7), (3, 4)]
struct.error: 'B' format requires 0 <= number <= 255
```

**Always start the format with `<`, `>` or `!`.** With no prefix (or `@`), struct uses the **native** layout of this machine: native byte order and **alignment padding**, so `"4sHI"` takes 12 bytes instead of 10. A file written that way may not read back correctly on another machine. `<` and `>` mean "standard sizes, no padding".

#### Try it 10.1

Predict the bytes (in hex) of `struct.pack(">HI", 1, 0x0A0B0C0D)` and of the same values with `"<HI"`. Then check with `.hex(" ")`.

<details><summary>Answer</summary>

```python
import struct
print(struct.pack(">HI", 1, 0x0A0B0C0D).hex(" "))
print(struct.pack("<HI", 1, 0x0A0B0C0D).hex(" "))
```
```text
00 01 0a 0b 0c 0d
01 00 0d 0c 0b 0a
```

Big-endian writes the most significant byte first, little-endian the least significant first. Each field reverses separately; the fields keep their order.
</details>

## 11. `sqlite3`: a database in a file

Chapter 12 ended its safe-overwrite section with "for many records with many small updates, use a real database". SQLite is that database, and it ships inside Python. It is not a toy: it runs in every phone and every browser. The whole database is **one file** (or memory, with `":memory:"`), there is no server to install, and it gives you **SQL queries** and **transactions** (all-or-nothing changes, even if the power fails mid-write).

This section assumes only the four basic SQL statements: `CREATE TABLE`, `INSERT`, `SELECT ... WHERE`, `UPDATE`/`DELETE`. The focus is on using them **safely from Python**.

### 11.1 Create, insert, query

```python
import sqlite3

conn = sqlite3.connect(":memory:")        # or a file: sqlite3.connect("shop.db")
conn.execute("CREATE TABLE items (id INTEGER PRIMARY KEY, name TEXT NOT NULL, price REAL)")
cur = conn.execute("INSERT INTO items (name, price) VALUES (?, ?)", ("pen", 10.5))
print("new id", cur.lastrowid)
conn.executemany("INSERT INTO items (name, price) VALUES (?, ?)",
                 [("book", 250.0), ("bag", 799.0), ("ink", 45.0)])
conn.commit()

for row in conn.execute("SELECT id, name, price FROM items WHERE price < ? ORDER BY price", (300,)):
    print(row)
print(conn.execute("SELECT COUNT(*), MAX(price) FROM items").fetchone())

conn.row_factory = sqlite3.Row            # rows you can index by column name
row = conn.execute("SELECT * FROM items WHERE name = :name", {"name": "bag"}).fetchone()
print(row["name"], row["price"], dict(row))
cur = conn.execute("UPDATE items SET price = price * 0.9 WHERE price > ?", (200,))
print("updated", cur.rowcount)
conn.close()
```
```text
new id 1
(1, 'pen', 10.5)
(4, 'ink', 45.0)
(2, 'book', 250.0)
(4, 799.0)
bag 799.0 {'id': 3, 'name': 'bag', 'price': 799.0}
updated 2
```

- **`?` placeholders** take values from a tuple, in order; **`:name`** placeholders take them from a dict. A single value still needs a tuple: `(300,)`.
- `execute` returns a cursor: loop over it, or call `fetchone()` (one row or `None`) or `fetchall()` (a list).
- `executemany` runs one statement for every tuple: far faster than a Python loop of `execute`.
- `sqlite3.Row` lets you write `row["price"]` instead of remembering that price is column 2.

### 11.2 SQL injection: never format SQL with user text

The most famous security bug of all time. A login search built with an f-string:

```python
import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE users (name TEXT, secret TEXT)")
conn.executemany("INSERT INTO users VALUES (?, ?)", [("asha", "s1"), ("ravi", "s2")])

typed = "nobody' OR '1'='1"                       # what an attacker types as a name
bad = f"SELECT name, secret FROM users WHERE name = '{typed}'"
print(bad)
print(conn.execute(bad).fetchall())               # every user's secret!
print(conn.execute("SELECT name, secret FROM users WHERE name = ?", (typed,)).fetchall())
```
```text
SELECT name, secret FROM users WHERE name = 'nobody' OR '1'='1'
[('asha', 's1'), ('ravi', 's2')]
[]
```

The quote in the typed text **ended the string** in the SQL, and the rest became SQL code: `OR '1'='1'` is always true. With a `?` placeholder, the value is sent to SQLite **separately from the SQL text**, so it can only ever be a value. No escaping by hand, no exceptions: **every value from outside goes through a placeholder.**

Placeholders work only for **values**, not for table or column names. If a user may choose the sort column, check it against a fixed set first:

```python
ALLOWED = {"name", "price"}
def order_by(column):
    if column not in ALLOWED:
        raise ValueError(f"cannot sort by {column!r}")
    return f"SELECT * FROM items ORDER BY {column}"     # safe: column is one of ours
```

### 11.3 Transactions: all or nothing

A transfer between two accounts must change **both** rows or **neither**. A transaction groups statements so that either all of them are saved (`commit`) or none (`rollback`).

Python's `sqlite3` (in its default mode) starts a transaction automatically before an `INSERT`, `UPDATE` or `DELETE`, and **nothing is saved until you commit**. Forgetting `commit()` is the number one beginner bug: the program runs fine and the data is gone after `close()`.

Using the connection as a **context manager** does the right thing for you: commit if the block succeeds, roll back if it raises.

```python
import sqlite3

conn = sqlite3.connect("bank.db")
conn.execute("CREATE TABLE IF NOT EXISTS acct (name TEXT PRIMARY KEY, bal INTEGER CHECK (bal >= 0))")
with conn:
    conn.execute("DELETE FROM acct")
    conn.executemany("INSERT INTO acct VALUES (?, ?)", [("asha", 100), ("ravi", 50)])

def transfer(conn, src, dst, amount):
    with conn:                                   # one transaction
        conn.execute("UPDATE acct SET bal = bal + ? WHERE name = ?", (amount, dst))
        conn.execute("UPDATE acct SET bal = bal - ? WHERE name = ?", (amount, src))

transfer(conn, "asha", "ravi", 30)
try:
    transfer(conn, "ravi", "asha", 500)          # ravi's balance would go negative
except sqlite3.IntegrityError as e:
    print("IntegrityError:", e)
print(conn.execute("SELECT * FROM acct ORDER BY name").fetchall())
conn.close()

conn = sqlite3.connect("bank.db")                # reopen: was it saved?
print(conn.execute("SELECT * FROM acct ORDER BY name").fetchall())
conn.close()
```
```text
IntegrityError: CHECK constraint failed: bal >= 0
[('asha', 70), ('ravi', 80)]
[('asha', 70), ('ravi', 80)]
```

The failed transfer had already **added 500 to asha** when the second statement broke the `CHECK`. The `with` block rolled that back too, so no money appeared from nowhere.

Two details that catch everyone:

- **`with conn:` does not close the connection.** It only commits or rolls back. Close it yourself (`conn.close()`), or wrap it: `with contextlib.closing(sqlite3.connect(path)) as conn:`. On Windows an open connection keeps the file locked, so a test that deletes the database file fails.
- Python 3.12 added an `autocommit` option to `connect()` that makes transaction control explicit. The default behaviour shown here works on every supported version.

#### Try it 11.1

Write `add_tag(conn, item_id, tag)` for a table `tags (item_id INTEGER, tag TEXT, UNIQUE(item_id, tag))` that inserts the tag, **ignores** a duplicate without crashing, and is safe from injection. Show that adding `"x'); DROP TABLE tags; --"` just stores that text.

<details><summary>Answer</summary>

```python
import sqlite3

def add_tag(conn, item_id, tag):
    with conn:
        conn.execute("INSERT OR IGNORE INTO tags (item_id, tag) VALUES (?, ?)", (item_id, tag))

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE tags (item_id INTEGER, tag TEXT, UNIQUE(item_id, tag))")
for t in ["red", "red", "x'); DROP TABLE tags; --"]:
    add_tag(conn, 1, t)
print(conn.execute("SELECT tag FROM tags ORDER BY tag").fetchall())
```
```text
[('red',), ("x'); DROP TABLE tags; --",)]
```

`INSERT OR IGNORE` skips rows that would break the `UNIQUE` rule. (Catching `sqlite3.IntegrityError` also works.)
</details>

## 12. `zipfile` and `shutil` archives

### 12.1 `zipfile`: full control

Chapter 12 made a ZIP with one call to `shutil.make_archive`. `zipfile` gives control over **what** goes in, **under which name**, and lets you read an archive without extracting it.

```python
import zipfile
from pathlib import Path

src = Path("site")
for rel in ["index.html", "css/main.css", "img/logo.txt"]:
    (src / rel).parent.mkdir(parents=True, exist_ok=True)
    (src / rel).write_text(f"content of {rel}\n" * 20, encoding="utf-8")

with zipfile.ZipFile("site.zip", "w", compression=zipfile.ZIP_DEFLATED) as zf:
    for path in sorted(src.rglob("*")):
        if path.is_file():
            zf.write(path, arcname=path.relative_to(src).as_posix())
    zf.writestr("VERSION", "1.0\n")             # from a string, no file needed

with zipfile.ZipFile("site.zip") as zf:
    print(zf.namelist())
    for info in zf.infolist()[:2]:
        print(info.filename, info.file_size, "->", info.compress_size, "bytes")
    print(zf.read("VERSION").decode("utf-8").strip(), zf.testzip())
    zf.extractall("restored")
print(sorted(p.as_posix() for p in Path("restored").rglob("*.*")))
```
```text
['css/main.css', 'img/logo.txt', 'index.html', 'VERSION']
css/main.css 480 -> 30 bytes
img/logo.txt 480 -> 31 bytes
1.0 None
['restored/css/main.css', 'restored/img/logo.txt', 'restored/index.html']
```

- **`arcname`** is the name inside the archive. Without it, `write` stores the path as you gave it, so archives end up full of `home/you/...` folders. Use paths **relative** to the folder you are archiving, with forward slashes (`as_posix()`), which is what the ZIP format expects on every system.
- **`ZIP_DEFLATED`** compresses. The default, `ZIP_STORED`, only packs files together without compressing.
- `namelist`, `infolist` (sizes, dates) and `read` work **without extracting**. `testzip()` returns `None` when every file's checksum is fine.
- Mode `"a"` appends to an existing archive. ZIP stores times with 2-second precision and cannot store dates before 1980.

**Trust.** An archive from someone else can contain names like `../../.bashrc`. `zipfile.extractall` removes `..` parts and absolute paths for you, but `tarfile` did not until recently (pass `filter="data"` when you extract tar files). Extract archives you did not make into an **empty** folder, and check sizes first: a small "zip bomb" can expand to gigabytes.

### 12.2 `shutil.make_archive` and `unpack_archive`

When you just want "this folder as an archive", `shutil` is one line. Its arguments are easy to mix up:

```python
import shutil
from pathlib import Path

Path("data/sub").mkdir(parents=True)
Path("data/a.txt").write_text("a", encoding="utf-8")
Path("data/sub/b.txt").write_text("b", encoding="utf-8")

made = shutil.make_archive("backups/data-2025", "zip", root_dir="data")
print(Path(made).relative_to(Path.cwd()).as_posix())
shutil.unpack_archive(made, "out")
print(sorted(p.relative_to("out").as_posix() for p in Path("out").rglob("*")))
print([name for name, _ in shutil.get_archive_formats()])   # depends on the Python version
```
```text
backups/data-2025.zip
['a.txt', 'sub', 'sub/b.txt']
['bztar', 'gztar', 'tar', 'xztar', 'zip', 'zstdtar']
```

- `base_name` is the path **without** the extension: `make_archive` adds `.zip` (or `.tar.gz` for `"gztar"`) and returns the full path it made.
- `root_dir` is the folder whose **contents** go in. Paths inside are relative to it.
- `unpack_archive` guesses the format from the extension.

`shutil` is right for "the whole folder". Use `zipfile` when you need to choose files, skip some, add a generated file (such as a manifest), or inspect an archive.

#### Try it 12.1

A script runs `zf.write(p)` for every file `p` in `Path("/home/you/site").rglob("*")`. What names end up in the archive, and why is that a problem? Fix the line.

<details><summary>Answer</summary>

The names are the full paths without the leading slash, such as `home/you/site/css/main.css`. Whoever extracts it gets a `home/you/site/` folder tree, and the archive reveals your user name and folder layout. Fix: `zf.write(p, arcname=p.relative_to(root).as_posix())` with `root = Path("/home/you/site")`.
</details>

## 13. `urllib` and `http`, offline

### 13.1 `urllib.parse`: URLs are structured text

A URL has parts, and each part has its own escaping rules. Never build or split one with string operations.

```python
from urllib.parse import urlsplit, parse_qs, parse_qsl, urlencode, quote, unquote, urljoin

url = "https://shop.example.com:8443/search/items?q=red+shoes&size=7&size=8#reviews"
parts = urlsplit(url)
print(parts.scheme, parts.hostname, parts.port, parts.path, parts.fragment)
print(parse_qs(parts.query))
print(parse_qsl(parts.query))
print(urlencode({"q": "café & tea", "page": 2}))
print(urlencode({"size": [7, 8]}, doseq=True))
print(quote("my file/1.txt"), quote("my file/1.txt", safe=""), unquote("caf%C3%A9"))
print(urljoin("https://a.com/docs/guide/", "../api/v2"), urljoin("https://a.com/docs/x", "/top"))
```
```text
https shop.example.com 8443 /search/items reviews
{'q': ['red shoes'], 'size': ['7', '8']}
[('q', 'red shoes'), ('size', '7'), ('size', '8')]
q=caf%C3%A9+%26+tea&page=2
size=7&size=8
my%20file/1.txt my%20file%2F1.txt café
https://a.com/docs/api/v2 https://a.com/top
```

- `parse_qs` gives a dict of **lists**, because a key can repeat (`size=7&size=8`). `parse_qsl` keeps the pairs in order.
- `urlencode` escapes values for a query string (spaces become `+`, `&` becomes `%26`); `doseq=True` turns a list into repeated keys.
- `quote` escapes one path part; by default it leaves `/` alone, so pass `safe=""` to escape it too.
- `urljoin` resolves a relative link against a page URL, like a browser does.

#### Try it 13.1

Build the URL `http://127.0.0.1:8000/search` with the query `red & blue shoes` and pages 1 and 2 (as repeated `page` keys). Then split it back into a dict of lists. Predict the query string before you run it.

<details><summary>Answer</summary>

```python
from urllib.parse import urlencode, urlsplit, parse_qs

query = urlencode({"q": "red & blue shoes", "page": [1, 2]}, doseq=True)
url = f"http://127.0.0.1:8000/search?{query}"
print(url)
print(parse_qs(urlsplit(url).query))
```
```text
http://127.0.0.1:8000/search?q=red+%26+blue+shoes&page=1&page=2
{'q': ['red & blue shoes'], 'page': ['1', '2']}
```

Spaces become `+` and `&` inside a value becomes `%26`, so it cannot be confused with the separator between keys. Numbers come back as strings.
</details>

### 13.2 A tiny server and a client, on your own computer

`http.server` contains a small web server, and `urllib.request` a client. Together they let us practise HTTP with no internet: the server listens on `127.0.0.1` (this computer only), on port `0`, which asks the operating system for any free port. It runs in a background **thread** (an idea covered properly in the concurrency module; here it only means "runs at the same time").

```python
import json
import threading
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import parse_qs, urlsplit


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        parts = urlsplit(self.path)
        if parts.path != "/hello":
            self.send_error(404, "no such page")
            return
        name = parse_qs(parts.query).get("name", ["world"])[0]
        body = json.dumps({"greeting": f"hello {name}"}).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format, *args):      # keep the demo quiet
        pass


server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
port = server.server_address[1]                  # the port the OS chose
threading.Thread(target=server.serve_forever, daemon=True).start()
try:
    with urllib.request.urlopen(f"http://127.0.0.1:{port}/hello?name=asha", timeout=5) as resp:
        print(resp.status, resp.headers["Content-Type"])
        print(json.loads(resp.read().decode("utf-8")))
    try:
        urllib.request.urlopen(f"http://127.0.0.1:{port}/missing", timeout=5)
    except urllib.error.HTTPError as e:
        print("HTTPError", e.code, e.reason)
finally:
    server.shutdown()
    server.server_close()
```
```text
200 application/json
{'greeting': 'hello asha'}
HTTPError 404 no such page
```

What to take from it:

- **`urlopen` returns a response** with `.status`, `.headers` and `.read()` (bytes: decode them). Use it in a `with` block.
- **Errors come in two kinds.** `HTTPError` means the server answered with an error code (404, 500): check `e.code`. `URLError` means there was no answer at all (wrong host, refused, no network). `HTTPError` is a subclass of `URLError`, so catch `HTTPError` first.
- **Always pass `timeout=`.** Without it a stuck server makes your program wait forever.
- **Always shut the server down** in a `finally`: `shutdown()` stops the loop, `server_close()` frees the port.
- To send data, pass `data=` (bytes) to `urllib.request.Request(url, data=..., method="POST", headers={...})`.

For real projects that talk to many web services, the third-party `requests` or `httpx` packages are friendlier. Knowing `urllib` still matters: it is always available, and the ideas (status codes, headers, bytes, timeouts) are the same everywhere.

## 14. `logging` in depth

### 14.1 Why not `print`?

`print` is fine for a program's **output**. For messages **about** what a program is doing, it falls short: you cannot turn messages off without editing code, they carry no time or severity, they all go to one place, and a library that prints is impossible to silence. `logging` fixes all of this, and the third outcome of this module is to set it up properly: **levels, handlers and formatting**.

Every log message has a **level**:

| Level | Number | Use for |
|---|---|---|
| `DEBUG` | 10 | details for developers while fixing a bug |
| `INFO` | 20 | normal events: "backup started", "user logged in" |
| `WARNING` | 30 | something unexpected, the program carries on (the default threshold) |
| `ERROR` | 40 | an operation failed |
| `CRITICAL` | 50 | the program cannot continue |

### 14.2 `basicConfig`, and the trap of calling it twice

The quickest setup configures the **root logger** once, at the start of the program:

```python
import logging

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
log = logging.getLogger("shop")
log.debug("not shown: below INFO")
log.info("started with %d items", 3)
log.warning("stock low for %s", "ink")
try:
    1 / 0
except ZeroDivisionError:
    log.exception("price calculation failed")     # ERROR + the traceback
```
```text
INFO shop: started with 3 items
WARNING shop: stock low for ink
ERROR shop: price calculation failed
Traceback (most recent call last):
  File "/home/you/demo/snippet.py", line 9, in <module>
    1 / 0
    ~~^~~
ZeroDivisionError: division by zero
```

Note the style `log.info("started with %d items", 3)`: the message and its arguments are passed **separately**, and the string is only built if the message is actually shown. That costs nothing for disabled debug lines and keeps the raw values available to handlers. `log.exception` (only inside `except`) logs at ERROR and adds the traceback. (The file path in that traceback is machine-specific.)

Now the trap. **`basicConfig` does nothing if the root logger already has a handler.** And calling `logging.info(...)` (the module-level function) before any configuration quietly calls `basicConfig()` with the defaults:

```python
import logging

logging.warning("an early message")                   # secretly calls basicConfig()
logging.basicConfig(level=logging.DEBUG, format=">> %(message)s")   # ignored!
logging.debug("you will not see this")
logging.warning("still the default format")
logging.basicConfig(level=logging.DEBUG, format=">> %(message)s", force=True)
logging.debug("now it works")
```
```text
WARNING:root:an early message
WARNING:root:still the default format
>> now it works
```

The rules: configure logging **once**, at the **very start** of `main()`, before anything logs. Use `force=True` (Python 3.8+) only when you really need to replace an existing setup, such as in a notebook. Inside your own modules, log through a named logger, not the module-level `logging.info`.

### 14.3 Loggers, handlers, formatters

Logging has four kinds of objects. Learn their jobs and every logging setup becomes readable:

- A **logger** is what your code calls (`log.info(...)`). It has a name and a level.
- A **handler** decides **where** a message goes: the console, a file, a rotating file. One logger can have several handlers, and each handler has **its own level**.
- A **formatter** decides **what the line looks like**. Each handler has one.
- A **filter** can drop or change individual records (rarely needed).

A message must pass **the logger's level and then each handler's level**. That lets you send everything to a file but only warnings to the screen:

```python
import io
import logging

log = logging.getLogger("demo.handlers")
log.setLevel(logging.DEBUG)                       # the logger lets everything through

screen = logging.StreamHandler(io.StringIO())     # a StringIO stands in for the console
screen.setLevel(logging.WARNING)
screen.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))

file_like = io.StringIO()                         # stands in for a log file
detail = logging.StreamHandler(file_like)
detail.setFormatter(logging.Formatter("%(levelname)-8s %(name)s:%(funcName)s:%(lineno)d %(message)s"))

log.addHandler(screen)
log.addHandler(detail)
log.propagate = False                             # explained in 14.4

def work():
    log.debug("step 1")
    log.warning("disk 91% full")

work()
print(screen.stream.getvalue(), end="")
print("---")
print(file_like.getvalue(), end="")
for h in (screen, detail):
    log.removeHandler(h)
```
```text
WARNING: disk 91% full
---
DEBUG    demo.handlers:work:20 step 1
WARNING  demo.handlers:work:21 disk 91% full
```

Useful format fields: `%(asctime)s` (time; shape it with `datefmt=`), `%(levelname)s`, `%(name)s`, `%(message)s`, `%(funcName)s`, `%(lineno)d`, `%(process)d`. `%(levelname)-8s` pads to 8 characters so columns line up. `asctime` uses local time; to log in UTC (section 5.6), set `formatter.converter = time.gmtime`.

The same `StringIO` trick is how you **test** logging: attach a handler to a `StringIO`, run the code, read the text, and **remove the handler afterwards** so the next test starts clean. pytest's built-in `caplog` fixture does this for you (`caplog.records`, `caplog.text`, `caplog.set_level(...)`).

### 14.4 The logger hierarchy and propagation

Logger names with dots form a **tree**: `"shop.db"` is a child of `"shop"`, which is a child of the **root** logger (name `""`). The convention is `logging.getLogger(__name__)` in every module, so the tree mirrors your package.

Two rules make the tree work:

1. **Level:** a logger with no level of its own (`NOTSET`) uses the first level set on an ancestor: its **effective level**.
2. **Propagation:** after a logger's own handlers run, the record is passed **up** to the handlers of every ancestor, until a logger has `propagate = False`. The ancestors' *levels* are not checked again; only their *handlers'* levels are.

```python
import io
import logging

out = io.StringIO()
root_handler = logging.StreamHandler(out)
root_handler.setFormatter(logging.Formatter("root saw   %(name)s %(levelname)s %(message)s"))
logging.getLogger().addHandler(root_handler)
logging.getLogger().setLevel(logging.WARNING)

app = logging.getLogger("app")
app_handler = logging.StreamHandler(out)
app_handler.setFormatter(logging.Formatter("app saw    %(name)s %(levelname)s %(message)s"))
app.addHandler(app_handler)
app.setLevel(logging.INFO)

db = logging.getLogger("app.db")
print(db.level, db.getEffectiveLevel(), db.parent.name)
db.info("connected")              # app.db -> app handler -> root handler
db.debug("query plan")            # below the effective level INFO: dropped
app.propagate = False
db.warning("slow query")          # stops at app
print(out.getvalue(), end="")
```
```text
0 20 app
app saw    app.db INFO connected
root saw   app.db INFO connected
app saw    app.db WARNING slow query
```

`"connected"` was printed **twice**, once per handler, even though the root logger's level is WARNING: propagation only checks handler levels. This is also the classic cause of **duplicated log lines**: a handler added both to a module logger and to the root logger (or `basicConfig` called while a module adds its own handler). The fix is to put handlers in **one place**, normally the root logger, and let everything propagate to it.

#### Try it 14.1

With the setup below, which lines appear, and how many times each?

```python
import logging, sys
root = logging.getLogger()
h = logging.StreamHandler(sys.stdout)
h.setFormatter(logging.Formatter("%(name)s:%(message)s"))
root.addHandler(h)
root.setLevel(logging.ERROR)
a = logging.getLogger("a")
a.setLevel(logging.DEBUG)
a.addHandler(h)
logging.getLogger("a.b").debug("one")
logging.getLogger("x").warning("two")
logging.getLogger("x").error("three")
```

<details><summary>Answer</summary>

```text
a.b:one
a.b:one
x:three
```

`a.b` has no level, so its effective level is `a`'s DEBUG: "one" passes, goes to `a`'s handler and then propagates to the root's handler (the same handler object, so it prints twice). `x` uses the root's level ERROR, so "two" is dropped and "three" appears once.
</details>

### 14.5 Rotating log files

A log file that grows forever eventually fills the disk. `logging.handlers` has two handlers that **rotate** files: when the current file is full (or a day ends), it is renamed with a number and a fresh file is started. Only the newest `backupCount` old files are kept.

```python
import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

handler = RotatingFileHandler("app.log", maxBytes=60, backupCount=2, encoding="utf-8")
handler.setFormatter(logging.Formatter("%(levelname)s %(message)s"))
log = logging.getLogger("rotate.demo")
log.addHandler(handler)
log.setLevel(logging.INFO)
log.propagate = False
for i in range(1, 9):
    log.info("event number %d", i)
handler.close()
log.removeHandler(handler)

for p in sorted(Path(".").glob("app.log*")):
    print(p.name, p.read_text(encoding="utf-8").split("\n")[:-1])
```
```text
app.log ['INFO event number 7', 'INFO event number 8']
app.log.1 ['INFO event number 5', 'INFO event number 6']
app.log.2 ['INFO event number 3', 'INFO event number 4']
```

Each line is 20 bytes (19 characters and a newline). A third line would reach the 60-byte limit, so each file holds two lines. `app.log` holds the newest lines, `app.log.1` the previous file, `app.log.2` the one before; older lines are deleted. Real values are more like `maxBytes=5_000_000, backupCount=5`.

`TimedRotatingFileHandler("app.log", when="midnight", backupCount=7)` rotates by time instead: one file per day, a week kept. Always pass `encoding="utf-8"` to file handlers, and close handlers when you are done (on Windows an open log file cannot be renamed or deleted).

### 14.6 Logging in a library versus an application

This is the rule that separates beginner code from professional code:

**An application configures logging. A library only logs.**

A **library** (a module or package other code imports):

- creates `log = logging.getLogger(__name__)` at the top of each module and logs through it;
- **never** calls `basicConfig`, never adds handlers to the root logger, never sets the root level, never `print`s diagnostics;
- may add `logging.NullHandler()` to its top-level logger, which stops Python's "last resort" handler from printing its warnings when the application has not configured anything.

An **application** (the program a person runs):

- configures logging **once**, at the start of `main()`: levels, handlers, format, files;
- decides how noisy each library is: `logging.getLogger("urllib3").setLevel(logging.WARNING)`.

Why? Only the application knows where logs should go (a terminal, a file, a server) and how much detail its user wants. A library that calls `basicConfig` at import time takes that choice away, and, because of the trap in 14.2, silently breaks the application's own `basicConfig` call.

```python
# mylib/storage.py  (library)
import logging
log = logging.getLogger(__name__)          # "mylib.storage" in a real package

def save(name):
    log.debug("saving %s", name)
    return True


# app.py  (application)
app_log = logging.getLogger("app")

def main():
    logging.basicConfig(level=logging.DEBUG, format="%(name)s %(levelname)s %(message)s")
    app_log.info("starting")
    save("report.txt")
    logging.getLogger(__name__).setLevel(logging.INFO)   # the app quiets the library
    save("again.txt")
    app_log.info("done")

main()
```
```text
app INFO starting
__main__ DEBUG saving report.txt
app INFO done
```

(Both "files" are in one block here, so the library's logger is named `__main__`; in a real package it would be `mylib.storage`.) The library logged its debug line without knowing where it would go, and the application turned it down with one line, without touching the library's code. For bigger programs, `logging.config.dictConfig` describes all loggers, handlers and formatters in one dictionary, which can be loaded from a TOML or JSON file.

#### Try it 14.2

Find three problems in this module from a library called `geo`:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

def distance(a, b):
    logging.info("distance called")
    print("debug:", a, b)
    return abs(a - b)
```

<details><summary>Answer</summary>

1. `basicConfig` at import time configures the **application's** root logger, and makes the application's own later `basicConfig` call do nothing.
2. `logging.info` logs through the root logger, so users cannot turn down just this library. Use `log = logging.getLogger(__name__)` and `log.debug(...)`.
3. `print` writes to the user's output and cannot be switched off. It should be a `log.debug` line.
</details>

## 15. Project: a backup and log-rotation tool

Time to combine the chapter. The tool:

1. zips a source folder into `dest/<name>-YYYYMMDD-HHMMSS.zip`, using an **injected** `now` (an aware UTC datetime) so tests are repeatable;
2. puts a **manifest** in the archive: the SHA-256 of every file, so a restore can be verified;
3. keeps only the **N newest** backups and deletes the rest (rotation);
4. logs what it does through a module logger, while `main()` sets up a **rotating log file**.

Modules used: `zipfile`, `hashlib`, `datetime`, `pathlib`, `json`, `logging`, `logging.handlers`, `argparse`.

### 15.1 The core functions

```python
# backup.py
import hashlib
import json
import logging
import zipfile
from datetime import datetime, timezone
from pathlib import Path

log = logging.getLogger("backup")
STAMP = "%Y%m%d-%H%M%S"


def sha256_file(path, chunk=64 * 1024):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        while block := f.read(chunk):
            h.update(block)
    return h.hexdigest()


def make_backup(source, dest, now):
    """Zip `source` into `dest`; return the archive path. `now` must be aware."""
    if now.tzinfo is None:
        raise ValueError("now must be timezone-aware")
    source, dest = Path(source), Path(dest)
    dest.mkdir(parents=True, exist_ok=True)
    stamp = now.astimezone(timezone.utc).strftime(STAMP)
    target = dest / f"{source.name}-{stamp}.zip"
    manifest = {}
    with zipfile.ZipFile(target, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        for path in sorted(source.rglob("*")):
            if path.is_file():
                name = path.relative_to(source).as_posix()
                zf.write(path, arcname=name)
                manifest[name] = sha256_file(path)
        zf.writestr("MANIFEST.json", json.dumps(manifest, indent=2, sort_keys=True))
    log.info("created %s (%d files)", target.name, len(manifest))
    return target


def rotate(dest, prefix, keep):
    """Delete all but the `keep` newest backups; return the deleted names."""
    backups = sorted(Path(dest).glob(f"{prefix}-*.zip"))   # the stamp sorts by time
    old = backups[:-keep] if keep > 0 else backups
    for path in old:
        path.unlink()
        log.info("deleted old backup %s", path.name)
    return [p.name for p in old]


def verify(archive):
    """Return the names whose content no longer matches the manifest."""
    bad = []
    with zipfile.ZipFile(archive) as zf:
        manifest = json.loads(zf.read("MANIFEST.json"))
        for name, digest in manifest.items():
            if hashlib.sha256(zf.read(name)).hexdigest() != digest:
                bad.append(name)
    if bad:
        log.error("%s: %d damaged files", Path(archive).name, len(bad))
    return bad
```

Design decisions worth noticing:

- **The timestamp is `YYYYMMDD-HHMMSS` in UTC.** As text it sorts in time order, so `sorted()` on names is enough for rotation, and a DST change cannot produce two backups with the same name or an out-of-order pair (section 5.4).
- **`now` is a parameter**, and naive values are refused. The real program passes `datetime.now(timezone.utc)`; tests pass fixed times.
- **`sorted(source.rglob("*"))`** makes the archive's file order the same on every run and every system.
- **The functions log but never configure logging**: they are the "library" part.

### 15.2 The application part: arguments and a rotating log

```python
# (continuing backup.py)
import argparse
from logging.handlers import RotatingFileHandler


def setup_logging(log_file):
    handler = RotatingFileHandler(log_file, maxBytes=1_000_000, backupCount=3, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(name)s: %(message)s"))
    root = logging.getLogger()                  # the application owns the root logger
    root.setLevel(logging.INFO)
    root.addHandler(handler)

def main(argv=None, now=None):
    parser = argparse.ArgumentParser(description="Zip a folder and keep the newest N backups.")
    for name in ("source", "dest"):
        parser.add_argument(name)
    parser.add_argument("--keep", type=int, default=5)
    parser.add_argument("--log", default="backup.log")
    args = parser.parse_args(argv)
    setup_logging(args.log)
    archive = make_backup(args.source, args.dest, now or datetime.now(timezone.utc))
    rotate(args.dest, Path(args.source).name, args.keep)
    return 1 if verify(archive) else 0
```

`main` takes `argv` and `now` so a test can call `main(["docs", "backups", "--keep", "2"], now=...)` directly, as chapter 13 recommended. A real entry point would end with `sys.exit(main())`.

### 15.3 A run with an injected clock

A test-style run: four "nightly" backups with a fixed clock, keeping three. The log goes to a `StringIO` so we can print it (the real program would use `setup_logging`).

```python
import io
import logging
import zipfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from backup import log, make_backup, rotate, verify

out = io.StringIO()
handler = logging.StreamHandler(out)
handler.setFormatter(logging.Formatter("%(levelname)s %(name)s: %(message)s"))
log.addHandler(handler)
log.setLevel(logging.INFO)

Path("docs/notes").mkdir(parents=True)
Path("docs/a.txt").write_text("alpha\n", encoding="utf-8")
Path("docs/notes/b.txt").write_text("beta\n", encoding="utf-8")

start = datetime(2025, 10, 25, 23, 30, tzinfo=timezone.utc)
for i in range(4):                               # four nightly runs, keep 3
    now = start + timedelta(days=i)
    archive = make_backup("docs", "backups", now)
    rotate("backups", "docs", keep=3)
print(sorted(p.name for p in Path("backups").iterdir()))
with zipfile.ZipFile(archive) as zf:
    print(zf.namelist())
print("damaged:", verify(archive))
print(out.getvalue(), end="")
```
```text
['docs-20251026-233000.zip', 'docs-20251027-233000.zip', 'docs-20251028-233000.zip']
['a.txt', 'notes/b.txt', 'MANIFEST.json']
damaged: []
INFO backup: created docs-20251025-233000.zip (2 files)
INFO backup: created docs-20251026-233000.zip (2 files)
INFO backup: created docs-20251027-233000.zip (2 files)
INFO backup: created docs-20251028-233000.zip (2 files)
INFO backup: deleted old backup docs-20251025-233000.zip
```

The run covers the night of 26 October 2025, when London's clocks went back. Because the names use UTC, the four stamps are exactly one day apart and in order.

### 15.4 Extending it

Good next steps, each using a section of this chapter:

- `--dry-run`: log what `rotate` **would** delete, delete nothing (chapter 12's safety habit).
- Skip files by pattern (`fnmatch`) and skip unchanged runs: if the new manifest equals the last archive's, delete the new archive and log "no changes".
- A `restore` command: `verify` first, then `extractall` into an **empty** folder.
- Keep backups by age instead of count: parse the stamp back with `datetime.strptime(..., STAMP).replace(tzinfo=timezone.utc)` and compare with `now - timedelta(days=30)`.
- Record each run in a small `sqlite3` table (time, archive, file count, result) and print a history report.

Problem p060 asks you to build a tested version of this tool.

## 16. Common traps

1. **`defaultdict` lookups create keys** (check with `in` or `.get()`); **Counter operators drop zero and negative counts** while `update`/`subtract` keep them.
2. **`(priority, obj)` on a heap** crashes on ties; add a counter. **`bisect_left` versus `bisect_right`**: test the exact breakpoints.
3. **Naive datetimes**, `datetime.now()` without a zone, `utcnow()`. Use `datetime.now(timezone.utc)`.
4. **`replace(tzinfo=...)` when you meant `astimezone(...)`**: it relabels instead of converting.
5. **Fixed offsets or three-letter names for DST zones.** Use `ZoneInfo("Region/City")`.
6. **DST gap and fold**: times that never exist or happen twice; same-zone arithmetic is wall-clock time. Compute durations in UTC.
7. **`timedelta.seconds`** is not the total: use `total_seconds()`.
8. **No time-zone data on Windows**: `pip install tzdata`.
9. **`time.time()` for durations**: it can jump. Use `perf_counter` or `monotonic`.
10. **`==` on floats** and long float sums: use `math.isclose` and `math.fsum`.
11. **`random` for secrets**, or the shared global generator in tests: use `secrets`, and `random.Random(seed)`.
12. **Shallow copies of nested defaults** share the inner lists: `copy.deepcopy`.
13. **`shell=True` with user input**: command injection. Pass a list. And always a `timeout` for `subprocess.run` and `urlopen`.
14. **SQL built with f-strings**: SQL injection. Use placeholders; whitelist names. **Forgetting `commit()`**; `with conn:` does not close.
15. **`struct` without `<`/`>`**: native padding and byte order. **Plain hashes for passwords**; base64 is not encryption.
16. **`zf.write(path)` without `arcname`**: full paths inside the archive.
17. **`basicConfig` called twice**, or after something already logged: silently ignored.
18. **Libraries that configure logging** or add handlers to the root logger; handlers in two places give duplicate lines.

## 17. Summary

- **Reach for the library first.** Counting, grouping, queues, priority, dates, checksums, subprocesses, databases and logging are solved problems.
- **`collections`**: `Counter` (missing = 0, `most_common`, multiset maths), `defaultdict` (factory on missing key, and lookups create keys), `deque` (O(1) at both ends, `maxlen`, `rotate`), `OrderedDict` (`move_to_end`, `popitem(last=False)`, LRU), `ChainMap` (layered lookups, writes to the first map), `namedtuple` (`_make`, `defaults`).
- **`heapq`** keeps a min-heap in a list: push/pop O(log n), `nsmallest`, `merge`, `(priority, counter, item)` tuples. **`bisect`** searches and inserts in sorted lists; mind left versus right.
- **`datetime`**: `date`, `datetime`, `timedelta`, ISO formats, `strptime`/`strftime`, ISO weeks. **Naive versus aware**: compute and store in UTC, attach zones with **`zoneinfo`**, convert with `astimezone`, show local time only at the edge. DST creates gaps and folds; same-zone arithmetic is wall-clock arithmetic.
- **`tzdata`** supplies zone data where the OS has none (Windows). **`time`**: `time()` for timestamps, `monotonic()`/`perf_counter()` for durations. **Inject clocks** to make time testable.
- **`math`** (`isclose`, `fsum`, `floor`/`trunc`, `comb`/`perm`, `gcd`/`lcm`), **`statistics`** (`mean`, `median`, `mode`, `stdev`, `quantiles`), **`random.Random(seed)`** for repeatable chance, **`secrets`** for anything that must not be guessed.
- **`copy.deepcopy`** keeps shared references and cycles; customise with `__copy__`/`__deepcopy__`. **`pprint`/`pformat`** for readable nested data.
- **`subprocess.run([...], capture_output=True, text=True, timeout=..., check=...)`**: a list, never `shell=True` with user input. **`shlex`** splits and quotes command lines. `sys` is about the interpreter, `os` about the machine, `shutil` about files.
- **`hashlib.sha256`** in chunks for file fingerprints; **`uuid4`** random ids, **`uuid5`** stable ids; **`base64`** for bytes in text (not secret); **`struct`** with an explicit byte order.
- **`sqlite3`**: placeholders always, `with conn:` for transactions, close explicitly. **`zipfile`** with `arcname` and `ZIP_DEFLATED`; **`shutil.make_archive`** for whole folders.
- **`urllib.parse`** builds and splits URLs; **`urllib.request.urlopen`** with a timeout; `HTTPError` versus `URLError`; practise against a local `http.server`.
- **`logging`**: levels; loggers (named, in a tree, propagating), handlers (where; with their own level), formatters (how). Configure once in the application; libraries only `getLogger(__name__)`. Rotate files with `RotatingFileHandler`.

You can now reach for the right standard-library tool before writing your own, handle time zones correctly with `zoneinfo`, and set up logging with levels, handlers and formatting. The problems in this module practise each tool in turn and finish with the backup tool from section 15.
