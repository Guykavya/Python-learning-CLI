# dsa.04 Hashing

## 1. Why hashing: removing the inner loop

In dsa.03 you learned that most slow programs hide a **nested loop**: for every element, search the rest of the data. The fast versions
did not search at all. A prefix sum *remembered* a total. A sliding window *remembered* a count. This module is about the most general
way of remembering things: a **hash table**, which Python gives you as `dict` and `set`.

A hash table answers one question very fast: **"have I seen this key before, and what do I know about it?"** "Very fast" means `O(1)` on
average, no matter whether the table holds ten items or ten million. Once you can ask that question in `O(1)`, a whole family of nested
loops collapses into a single loop.

### The shape of the problem: "find a partner"

Look at this task. Given a list `a` and a number `target`, is there a pair of values that adds up to `target`?

The brute force tries every pair:

```python
def has_pair_slow(a, target):
    n = len(a)
    for i in range(n):
        for j in range(i + 1, n):
            if a[i] + a[j] == target:
                return True
    return False

print(has_pair_slow([8, 3, 11, 6], 14))
print(has_pair_slow([8, 3, 11, 6], 100))
```
```text
True
False
```

For `n = 200,000` the two loops make about `2 * 10^10` comparisons. At roughly `10^7` simple Python steps per second that is more than half an
hour. Now ask: for one fixed `x = a[i]`, what **exactly** are we looking for? Not "any other value", but the single value `target - x`.
The inner loop is only a *search for one known value*. If we had a structure that tells us "is this value present?" in `O(1)`, the inner loop disappears:

```python
def has_pair_fast(a, target):
    seen = set()
    for x in a:
        if target - x in seen:
            return True
        seen.add(x)
    return False

print(has_pair_fast([8, 3, 11, 6], 14))
print(has_pair_fast([8, 3, 11, 6], 100))
```
```text
True
False
```

One loop, `n` steps. That is the **learning outcome of this module**: *use a hash map or set to remove a nested loop.* The recipe is always the same:

1. Find the inner loop. Say what it searches for.
2. If it searches for one **known value** (or one known key), store the values you have already passed in a set or dictionary.
3. Replace the inner loop by one lookup.

### How much faster?

Let us measure instead of guessing. We search `n` times in a list and in a set (the values are all different, so every search of the list
scans a lot):

```python
import time

n = 5000
items_list = list(range(n))
items_set = set(items_list)
queries = list(range(n, 2 * n))          # none of these is present: a failed search is the worst case for a list

t0 = time.perf_counter()
hits = sum(1 for q in queries if q in items_list)
t_list = time.perf_counter() - t0

t0 = time.perf_counter()
hits2 = sum(1 for q in queries if q in items_set)
t_set = time.perf_counter() - t0

print("hits:", hits, hits2)
print("list is slower than set:", t_list > t_set)
print("ratio at least 50x:", t_list / t_set > 50)
```
```text
hits: 0 0
list is slower than set: True
ratio at least 50x: True
```

(We print only comparisons, because the exact times depend on your machine.) A failed search in a list of 5000 items compares with all of them;
in a set it looks at one place. As `n` grows, the gap grows linearly.

### What a hash table costs

Nothing is free. A hash table pays with:

- **Memory.** A set of `n` integers takes several times more memory than a list of `n` integers, because the table keeps empty slots on purpose.
- **No order of positions.** You cannot ask for "the third item" of a set. (A `dict` remembers *insertion* order, but not positions you can index.)
- **Hashable keys only.** Keys must be values whose hash never changes (section 3).
- **"Average" speed.** `O(1)` is the **average** case. A bad hash function or an attacker can make it `O(n)` (sections 9, 13 and 14).

For almost every problem in this course these costs are worth paying.

### Signals that say "use a hash table"

| Words in the statement | Think of |
|---|---|
| "have I seen this before", "duplicate", "distinct" | a `set` |
| "how many times does ... appear", "most frequent" | a counting `dict` / `Counter` |
| "group by", "anagram", "same pattern" | a `dict` from a canonical key to a list |
| "find two values that add to / differ by ..." | the complement lookup |
| "number of subarrays with sum / balance / remainder ..." | a dictionary of prefix sums |
| "longest run / window with a property" (not sorted) | a dictionary of counts or first indices |
| "substring equals substring", "pattern search", "compare many substrings" | a polynomial rolling hash |
| "cache", "least recently used" | a dictionary that keeps order |

Also check the constraints, as in dsa.03: `n <= 2 * 10^5` rules out a quadratic loop, and "need a pair" or "count with a property" very often points here.

**Try it 1: which loop disappears?**

Look at this code. What is the inner loop searching for, and what would you store to remove it?

```python
count = 0
for i in range(n):
    for j in range(n):
        if i != j and a[i] == 2 * a[j]:
            count += 1
```

<details><summary>Answer</summary>

For a fixed `i` the inner loop searches for positions `j` whose value is `a[i] / 2`. That is one known value. Store how many times each value
occurs (`freq`), then for every `x = a[i]` that is even add `freq[x // 2]`, subtracting 1 if `x == 0` (because then `j == i` is not allowed and `0 == 2 * 0`).
The nested loop becomes one pass plus one table, `O(n)`.
</details>

## 2. `dict` and `set` in Python

### A dictionary is a table of key -> value

```python
ages = {"ana": 30, "ben": 25}
ages["cy"] = 41            # insert
ages["ana"] = 31           # update: same key, new value
print(ages)
print(ages["ben"])         # read
print(len(ages))
print("ana" in ages, "zoe" in ages)   # membership tests KEYS
del ages["ben"]
print(ages)
```
```text
{'ana': 31, 'ben': 25, 'cy': 41}
25
3
True False
{'ana': 31, 'cy': 41}
```

Every operation above is `O(1)` on average, and all of them use the **hash of the key** to find the right place. You never search through the keys.

### Reading safely

Indexing a missing key raises `KeyError`. Three safe ways to read:

```python
ages = {"ana": 31, "cy": 41}

print(ages.get("zoe"))            # None
print(ages.get("zoe", 0))         # default value
if "zoe" in ages:
    print("found")
else:
    print("not found")

try:
    ages["zoe"]
except KeyError as e:
    print("KeyError:", e)
```
```text
None
0
not found
KeyError: 'zoe'
```

`ages.get(key, default)` is the tool you will use most. The pattern `d[key] = d.get(key, 0) + 1` is how you count.

### Looping

```python
ages = {"ana": 31, "cy": 41, "dev": 22}

for key in ages:                  # keys, in insertion order
    print(key, end=" ")
print()
for value in ages.values():
    print(value, end=" ")
print()
for key, value in ages.items():   # pairs
    print(key, "->", value)
```
```text
ana cy dev 
31 41 22 
ana -> 31
cy -> 41
dev -> 22
```

Since Python 3.7, a `dict` iterates in the order the keys were **first inserted**. Updating a value does not move a key; deleting a key and inserting
it again puts it at the end. You may rely on this for `dict`. You may **not** rely on any order for a `set`.

### Useful methods

```python
d = {"a": 1, "b": 2}

print(d.pop("a"))            # remove and return the value
print(d.pop("zzz", "none"))  # missing key with a default: no error
d.setdefault("c", []).append(5)   # create the list if missing, then append
d.setdefault("c", []).append(6)
print(d)
d.update({"b": 20, "e": 7})  # merge another dictionary in
print(d)
print(list(d.keys()), list(d.values()))
copy = d.copy()
copy["b"] = 0
print(d["b"], copy["b"])
```
```text
1
none
{'b': 2, 'c': [5, 6]}
{'b': 20, 'c': [5, 6], 'e': 7}
['b', 'c', 'e'] [20, [5, 6], 7]
20 0
```

`setdefault(key, default)` returns the existing value, or stores the default and returns it. With `setdefault(key, [])` you create a group list the first time.
Careful: the default is built **every call** (the `[]` is created even if the key exists); that is fine for small values.

### A set is a dictionary with only keys

```python
s = {3, 1, 2, 3, 3}
print(len(s))                 # duplicates vanish
print(2 in s, 9 in s)
s.add(9)
s.discard(1)                  # no error if missing
print(sorted(s))              # sets have no order: sort to print
a = {1, 2, 3, 4}
b = {3, 4, 5}
print(sorted(a & b))          # intersection
print(sorted(a | b))          # union
print(sorted(a - b))          # difference
print(sorted(a ^ b))          # symmetric difference
print(a <= {1, 2, 3, 4, 5})   # subset test
```
```text
3
True False
[2, 3, 9]
[3, 4]
[1, 2, 3, 4, 5]
[1, 2]
[1, 2, 5]
True
```

An empty set is written `set()`, **not** `{}` (that is an empty dictionary):

```python
print(type({}), type(set()))
```
```text
<class 'dict'> <class 'set'>
```

### Complexity cheat sheet

| Operation | `list` | `set` | `dict` |
|---|---|---|---|
| `x in container` | `O(n)` | `O(1)` average | `O(1)` average (keys) |
| add / insert at the end | `O(1)` | `O(1)` average | `O(1)` average |
| remove a given value | `O(n)` | `O(1)` average | `O(1)` average |
| get by position `a[i]` | `O(1)` | impossible | impossible |
| iterate everything | `O(n)` | `O(n)` | `O(n)` |
| smallest / largest | `O(n)` | `O(n)` | `O(n)` |

Two lines to remember: `x in list` is a **loop in disguise**, and sets and dictionaries are the tools when you ask "is it there?" many times.

### Building a set or dictionary in one line

```python
words = ["apple", "bob", "cat", "apple", "dog", "bob"]
lengths = {w: len(w) for w in words}        # dictionary comprehension
firsts = {w[0] for w in words}              # set comprehension
print(lengths)
print(sorted(firsts))
index = {w: i for i, w in enumerate(words)} # later duplicates overwrite earlier ones
print(index)
```
```text
{'apple': 5, 'bob': 3, 'cat': 3, 'dog': 3}
['a', 'b', 'c', 'd']
{'apple': 3, 'bob': 5, 'cat': 2, 'dog': 4}
```

The last line shows a classic trap: for repeated keys the **last** value wins. If you want the **first** index, store only if the key is absent (`if w not in index`).

**Try it 2: predict the output**

```python
d = {}
for ch in "banana":
    d[ch] = d.get(ch, 0) + 1
print(d)
print(list(d)[0])
s = set("banana")
print(len(s))
```

<details><summary>Answer</summary>

```python
d = {}
for ch in "banana":
    d[ch] = d.get(ch, 0) + 1
print(d)
print(list(d)[0])
s = set("banana")
print(len(s))
```
```text
{'b': 1, 'a': 3, 'n': 2}
b
3
```

Counts are `b 1`, `a 3`, `n 2`, in the order of first appearance (`b`, `a`, `n`). `list(d)[0]` is the first key, `b`. The set of letters has 3 elements.
</details>

## 3. Hashable keys: what can be a key, and why

### What `hash` does

`hash(x)` turns a value into an integer. A dictionary uses that integer to decide **where** to store the key, and later where to look for it.

```python
print(hash(1), hash(2), hash(-1), hash(-2))
print(hash(1) == hash(1.0) == hash(True))
print(hash((1, 2)) == hash((1, 2)))
```
```text
1 2 -2 -2
True
True
```

Note that `hash(-1)` and `hash(-2)` are both `-2` in CPython: `-1` is reserved internally as an error signal. Equal hashes for different values are allowed; they are
called **collisions** and every hash table has to handle them (section 9).

### The contract

For a value to be a key it must follow two rules:

1. **Equal values have equal hashes.** If `a == b` then `hash(a) == hash(b)`.
2. **The hash never changes** while the value is stored.

Rule 1 is why `1`, `1.0` and `True` are one key:

```python
d = {}
d[1] = "int"
d[1.0] = "float"
d[True] = "bool"
print(d)
print(len(d))
```
```text
{1: 'bool'}
1
```

### Immutable types are hashable

| Hashable | Not hashable |
|---|---|
| `int`, `float`, `bool`, `None` | `list` |
| `str`, `bytes` | `dict` |
| `tuple` of hashable items | `set` |
| `frozenset` | a `tuple` that contains a list |
| `range` | |

```python
d = {}
d[(1, 2)] = "tuple"
d[frozenset({1, 2})] = "frozenset"
d["text"] = "str"
print(len(d))
for bad in ([1, 2], {1, 2}, (1, [2])):
    try:
        d[bad] = 1
    except TypeError:
        print("unhashable:", type(bad).__name__, bad)
```
```text
3
unhashable: list [1, 2]
unhashable: set {1, 2}
unhashable: tuple (1, [2])
```

A tuple is hashable only if **every item** is. `(1, [2])` fails because of the list inside.

### Why mutable keys would be a disaster

Imagine a dictionary let you use a list as a key. You store `d[[1, 2]] = "x"`. The dictionary computes the hash of `[1, 2]` and puts the entry in that place. Then you write
`key.append(3)`. The list is now `[1, 2, 3]`, whose hash is different. A lookup with `key` goes to the place for the *new* hash, finds nothing, and your entry is lost
inside the dictionary: it is there, but no lookup can reach it. Python prevents this by refusing to hash mutable containers.

You can see the same effect by building a hash-by-contents class yourself (do not do this in real code):

```python
class Box:
    def __init__(self, items):
        self.items = items
    def __hash__(self):
        return hash(tuple(self.items))
    def __eq__(self, other):
        return self.items == other.items

b = Box([1, 2])
d = {b: "stored"}
print(b in d)
b.items.append(3)
print(b in d)          # the hash changed: the entry is lost
print(len(d))          # but it is still in there
```
```text
True
True
1
```

### Keys you will use all the time

| Need | Key |
|---|---|
| a cell in a grid | a tuple `(row, col)` |
| a set of letters | `frozenset(letters)`, or a sorted string |
| an anagram class | `"".join(sorted(word))` |
| a pair of ids, unordered | `tuple(sorted((a, b)))` |
| a position in a game state | a tuple of the relevant values |

### `hash()` of strings is randomised

Python deliberately **randomises** the hash of `str` and `bytes` every time the interpreter starts (so that a hostile input cannot predict it). Run this twice; the numbers will differ
(they are machine- and run-specific):

```python
print(hash("hello"))
print(hash("hello") % 8)
```
```text
-676457257837088995
5
```

Two lessons: **never** print or store `hash(str)` and expect it to match later (not in a file, not in a test, not between two runs), and never depend on the iteration order of a `set` of strings,
because that order comes from these hashes. Integers are different: `hash(5) == 5`, so a set of small integers *looks* sorted, but that is an accident of implementation, not a promise.

**Try it 3: which of these can be keys?**

(a) `(1, 2, 3)` (b) `[1, 2, 3]` (c) `("a", (1, 2))` (d) `("a", [1, 2])` (e) `frozenset([1, 2])` (f) `{1, 2}` (g) `3.0` (h) `None`

<details><summary>Answer</summary>

```python
tests = {
    "(1, 2, 3)": (1, 2, 3),
    "[1, 2, 3]": [1, 2, 3],
    "('a', (1, 2))": ("a", (1, 2)),
    "('a', [1, 2])": ("a", [1, 2]),
    "frozenset([1, 2])": frozenset([1, 2]),
    "{1, 2}": {1, 2},
    "3.0": 3.0,
    "None": None,
}
for name, value in tests.items():
    try:
        hash(value)
        print(name, "ok")
    except TypeError:
        print(name, "unhashable")
```
```text
(1, 2, 3) ok
[1, 2, 3] unhashable
('a', (1, 2)) ok
('a', [1, 2]) unhashable
frozenset([1, 2]) ok
{1, 2} unhashable
3.0 ok
None ok
```

A list and a set are mutable. The tuple with a list inside is unhashable because one item is.
</details>

## 4. Frequency counting

### The pattern

"How many times does each value occur?" is the most common use of a dictionary. The loop is always:

```python
text = "mississippi"
count = {}
for ch in text:
    count[ch] = count.get(ch, 0) + 1
print(count)
```
```text
{'m': 1, 'i': 4, 's': 4, 'p': 2}
```

Every character costs one lookup and one store: `O(n)` for the whole string, instead of `O(n * distinct)` when you call `text.count(ch)` for each distinct letter.

### `collections.Counter`

`Counter` is a dictionary built for counting:

```python
from collections import Counter

c = Counter("mississippi")
print(c)
print(c["s"], c["z"])           # a missing key gives 0 and is NOT inserted
print(c.most_common(2))
print(sum(c.values()), len(c))  # items counted, distinct keys
c["m"] += 10
c.update("pp")
print(c)
print(Counter([3, 1, 3, 2, 3]).most_common(1))
```
```text
Counter({'i': 4, 's': 4, 'p': 2, 'm': 1})
4 0
[('i', 4), ('s', 4)]
11 4
Counter({'m': 11, 'i': 4, 's': 4, 'p': 4})
[(3, 3)]
```

Useful facts:

- `Counter(iterable)` counts; `c[key]` is the count (0 if absent).
- `most_common(k)` gives the `k` biggest, ties in insertion order. When a problem wants a specific tie rule, **sort yourself**: `sorted(c, key=lambda v: (-c[v], v))`.
- `c1 - c2` keeps only positive differences; `c1 & c2` takes minimums; `c1 + c2` adds counts.
- `c1 == c2` compares the counts (and ignores order): the basis of the anagram test.

```python
from collections import Counter

magazine = Counter("aabbcc")
note = Counter("abcabc")
print(note - magazine)            # empty: the magazine has enough
print(Counter("aaab") - Counter("ab"))
print(Counter("listen") == Counter("silent"))
```
```text
Counter()
Counter({'a': 2})
True
```

### `defaultdict`

`defaultdict(factory)` creates a missing value by calling `factory()` the first time you **read** a key:

```python
from collections import defaultdict

groups = defaultdict(list)
for word in ["tea", "ate", "to", "at", "tan"]:
    groups[len(word)].append(word)
print(dict(groups))

total = defaultdict(int)
for ch in "banana":
    total[ch] += 1
print(dict(total))
```
```text
{3: ['tea', 'ate', 'tan'], 2: ['to', 'at']}
{'b': 1, 'a': 3, 'n': 2}
```

The trap from problem 11: reading a missing key **creates** it.

```python
from collections import defaultdict

d = defaultdict(int)
d["x"] += 1
print(d["y"])             # creates "y" with 0
print(sorted(d))          # y is now a key
print("z" in d)           # membership never creates
print(sorted(d))
```
```text
0
['x', 'y']
False
['x', 'y']
```

If you only want to *ask*, use `in` or `.get`. When you *build* groups or counts, `defaultdict` is shorter than `.get(key, 0) + 1` or `if key not in d`.

### Which one to use?

| You want | Use |
|---|---|
| counts of items | `Counter(...)`, or `d[x] = d.get(x, 0) + 1` |
| groups of items | `defaultdict(list)`, or `setdefault(key, []).append(x)` |
| to ask without changing | `key in d`, `d.get(key)` |
| first-seen position | `if x not in first: first[x] = i` |

Either style is fine in the problems; the plain `dict` with `.get` always works and you can write it anywhere.

### Worked example: most frequent value, smallest on ties

```python
def most_frequent(a):
    count = {}
    for x in a:
        count[x] = count.get(x, 0) + 1
    best = None
    for value, c in count.items():
        if best is None or c > count[best] or (c == count[best] and value < best):
            best = value
    return best, count[best]

print(most_frequent([4, 1, 2, 2, 1, 4, 4]))
print(most_frequent([5, 5, 7, 7]))
```
```text
(4, 3)
(5, 2)
```

One pass to count, one pass over the distinct values to pick: `O(n)`.

### Frequency of frequencies

Sometimes you count the counts: "how many values appear exactly twice?"

```python
from collections import Counter

a = [1, 1, 2, 3, 3, 3, 4, 4]
freq = Counter(a)
freq_of_freq = Counter(freq.values())
print(freq)
print(freq_of_freq)
print(freq_of_freq[2])
```
```text
Counter({3: 3, 1: 2, 4: 2, 2: 1})
Counter({2: 2, 1: 1, 3: 1})
2
```

### Counting pairs from counts

If a value occurs `c` times, there are `c * (c - 1) // 2` pairs of **positions** holding that value. That formula appears again and again:

```python
from collections import Counter

a = [3, 3, 3, 5, 5, 8]
pairs = sum(c * (c - 1) // 2 for c in Counter(a).values())
print(pairs)
```
```text
4
```

(three 3s give 3 pairs, two 5s give 1 pair, one 8 gives 0.)

**Try it 4: predict the output**

```python
from collections import Counter
c = Counter("abracadabra")
print(c.most_common(2))
print(c["z"], len(c))
c.update(["z"])
print(len(c))
```

<details><summary>Answer</summary>

```python
from collections import Counter
c = Counter("abracadabra")
print(c.most_common(2))
print(c["z"], len(c))
c.update(["z"])
print(len(c))
```
```text
[('a', 5), ('b', 2)]
0 5
6
```

`a` occurs 5 times, `b` and `r` twice each (`b` first), `c` and `d` once. Reading `c["z"]` does not insert it, so `len(c)` is 5. After `update(["z"])` the key exists: 6.
</details>

## 5. Grouping and anagram keys

### The idea: a canonical form

Grouping means: put items that are "the same in some sense" together. The standard trick is to compute, for each item, a **canonical key**: a value that is equal for all
items of the same group and different for items of different groups. Then a dictionary from key to list does the grouping in one pass.

For anagrams the "sameness" is "same letters with the same counts". Two good canonical keys:

```python
def key_sorted(word):
    return "".join(sorted(word))

def key_counts(word):
    counts = [0] * 26
    for ch in word:
        counts[ord(ch) - ord("a")] += 1
    return tuple(counts)

print(key_sorted("listen"), key_sorted("silent"), key_sorted("enlist"))
print(key_counts("abca"))
print(key_counts("abca") == key_counts("baca"))
```
```text
eilnst eilnst eilnst
(2, 1, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)
True
```

Why `"".join(...)` and `tuple(...)`? `sorted(word)` returns a **list**, which is not hashable. A string or a tuple is.

### Grouping all words

```python
def group_anagrams(words):
    groups = {}
    for w in words:
        key = "".join(sorted(w))
        if key not in groups:
            groups[key] = []
        groups[key].append(w)
    return list(groups.values())

print(group_anagrams(["eat", "tea", "tan", "ate", "nat", "bat"]))
```
```text
[['eat', 'tea', 'ate'], ['tan', 'nat'], ['bat']]
```

Cost: `O(n * L log L)` for `n` words of length `L` (the sorts). With the 26-count tuple it is `O(n * (L + 26))`.

### Keys that look right but are wrong

A key must be equal **exactly** for the items you want in one group. These two are tempting and wrong:

```python
def key_sum(word):
    return sum(ord(c) for c in word)

def key_set(word):
    return frozenset(word)

print(key_sum("ad"), key_sum("bc"))            # same sum, not anagrams
print(key_set("aab") == key_set("ab"))          # same letters, different counts
```
```text
197 197
True
```

The sum throws away too much information (many different words add to the same number). The set forgets counts. When you design a key, test it on the smallest counterexamples
(`ad` / `bc`, `aab` / `ab`). Problem 39 asks you to reason about this.

### Canonical forms for other kinds of "sameness"

The same recipe handles many problems:

| "Same" means | Canonical key |
|---|---|
| anagram | sorted letters, or 26 counts |
| same shape of repeats ("isomorphic") | each letter replaced by the order of its first appearance |
| same multiset of numbers | `tuple(sorted(numbers))` |
| same up to shifting every letter | differences of consecutive letters |
| same unordered pair | `(min(a, b), max(a, b))` |

```python
def pattern(word):
    first = {}
    out = []
    for ch in word:
        if ch not in first:
            first[ch] = len(first)
        out.append(first[ch])
    return tuple(out)

print(pattern("egg"), pattern("add"), pattern("foo"), pattern("bar"))
print(pattern("egg") == pattern("add"))
```
```text
(0, 1, 1) (0, 1, 1) (0, 1, 1) (0, 1, 2)
True
```

`egg` and `add` become `(0, 1, 1)`: isomorphic. This is the one-line proof that two strings can be matched one-to-one in both directions (problems 9 and 10 do it with two dictionaries instead).

### Two-way matching with two dictionaries

For "letter to word" or "letter to letter" matching you must check **both directions**:

```python
def isomorphic(s, t):
    forward, backward = {}, {}
    for a, b in zip(s, t):
        if forward.get(a, b) != b or backward.get(b, a) != a:
            return False
        forward[a] = b
        backward[b] = a
    return True

print(isomorphic("egg", "add"))
print(isomorphic("foo", "bar"))
print(isomorphic("ab", "aa"))
```
```text
True
False
False
```

`forward.get(a, b)` means: "what did `a` map to before, or `b` if it is new". A new letter always passes. `ab` against `aa` fails only in the **backward** direction (`a` and `b` both want `a`).

### Grouping with an order requirement

Often the output must be in a stable order, for example "groups sorted by their first word". A dictionary gives you groups in first-appearance order. To impose an order, sort at the end:

```python
groups = {}
for w in ["tan", "eat", "nat", "tea"]:
    groups.setdefault("".join(sorted(w)), []).append(w)
result = sorted(sorted(g) for g in groups.values())
print(result)
```
```text
[['eat', 'tea'], ['nat', 'tan']]
```

Sorting a list of lists compares them element by element, so groups end up ordered by their smallest word.

**Try it 5: predict the output**

```python
words = ["ab", "ba", "abc", "cab", "b"]
groups = {}
for w in words:
    groups.setdefault("".join(sorted(w)), []).append(w)
print(groups)
print(len(groups))
```

<details><summary>Answer</summary>

```python
words = ["ab", "ba", "abc", "cab", "b"]
groups = {}
for w in words:
    groups.setdefault("".join(sorted(w)), []).append(w)
print(groups)
print(len(groups))
```
```text
{'ab': ['ab', 'ba'], 'abc': ['abc', 'cab'], 'b': ['b']}
3
```

Words of different lengths can never be anagrams. Three groups: `ab`, `abc`, `b`.
</details>

## 6. The complement pattern: two sum and its relatives

### Why "check first, then store"

For two sum the question at position `j` is: "has a value `target - a[j]` appeared at an earlier position?" Keep a dictionary of earlier values.

```python
def two_sum(a, target):
    seen = {}                       # value -> index
    for j, x in enumerate(a):
        need = target - x
        if need in seen:
            return seen[need], j
        seen[x] = j
    return None

print(two_sum([2, 7, 11, 15], 9))
print(two_sum([3, 2, 4], 6))
print(two_sum([3, 3], 6))
print(two_sum([1, 2], 10))
```
```text
(0, 1)
(1, 2)
(0, 1)
None
```

Order matters: look up **before** you store. If you stored `x` first, then for `a = [3, 2, 4]` and `target = 6` the first `3` would find itself and report `(0, 0)`, one element used twice. The look-up-first order
means you only ever pair with **earlier** positions, which also guarantees each pair is seen exactly once (when its later member is processed).

Why does `[3, 3]` work? The first `3` is stored; the second `3` asks for `6 - 3 = 3` and finds it at index 0.

### Counting pairs instead of finding one

If you want **how many** pairs, store counts and add them up:

```python
def count_pairs(a, k):
    seen = {}
    total = 0
    for x in a:
        total += seen.get(k - x, 0)
        seen[x] = seen.get(x, 0) + 1
    return total

print(count_pairs([1, 5, 3, 3, 3], 6))
print(count_pairs([3, 3, 3], 6))
```
```text
4
3
```

Three `3`s give three pairs: when the second `3` arrives it pairs with one earlier `3`; the third pairs with two. That is `0 + 1 + 2 = 3 = 3 * 2 / 2`.

### Other relations are complements too

Two sum is one case of "find a partner given a relation". The partner can be computed from `x` for many relations:

| Relation | Partner of `x` |
|---|---|
| `x + y = k` | `k - x` |
| `x - y = d` | `x - d` (and `x + d` if order is free) |
| `x * y = p` | `p / x` (if it divides) |
| `x xor y = z` | `x ^ z` |
| `y = 2 * x` | `2 * x` |
| `a[j] - j = a[i] - i` (equal "shifted" values) | the same `a - index` key |

The last row is the Codeforces problem "Same Differences": count pairs `i < j` with `a[j] - a[i] = j - i`. Rewrite it as `a[j] - j = a[i] - i`; now it is "count pairs of **equal keys**":

```python
from collections import Counter

a = [3, 5, 1, 4, 6, 6]
keys = Counter(x - i for i, x in enumerate(a))
print(keys)
print(sum(c * (c - 1) // 2 for c in keys.values()))
```
```text
Counter({1: 2, 3: 1, 4: 1, -1: 1, 2: 1})
1
```

Whenever a condition mixes two elements `i` and `j` in a way you can **separate** into "something about `i`" equals "something about `j`", a dictionary of that something finds the partners. Look
for that rewriting before you reach for a second loop.

### Four lists: meet in the middle

Four nested loops cost `n^4`. Split into two halves of two lists each. All sums `a + b` go into a dictionary of counts (`n^2` entries); then every `c + d` asks for `-(c + d)`:

```python
def four_sum_count(A, B, C, D):
    pair_count = {}
    for a in A:
        for b in B:
            pair_count[a + b] = pair_count.get(a + b, 0) + 1
    total = 0
    for c in C:
        for d in D:
            total += pair_count.get(-(c + d), 0)
    return total

print(four_sum_count([1, 2], [-2, -1], [-1, 2], [0, 2]))
```
```text
2
```

`n^4` became `2 * n^2` (time) and `n^2` (memory). This **meet in the middle** idea appears whenever you split a search into two halves and join them with a lookup.

### When the table is the bottleneck: sorted input

If the input is already **sorted**, two pointers solve two sum in `O(n)` with `O(1)` memory (dsa.03). The dictionary solution also works on unsorted data and returns **original indices**,
which sorting would lose. Memory is the price.

**Try it 6: trace it**

Run `two_sum([4, 9, 1, 6, 5, 3, 2], 8)` by hand. After each step, what does `seen` hold, and what is returned?

<details><summary>Answer</summary>

```python
a = [4, 9, 1, 6, 5, 3, 2]
seen = {}
for j, x in enumerate(a):
    need = 8 - x
    print(j, x, need, seen)
    if need in seen:
        print("pair", seen[need], j)
        break
    seen[x] = j
```
```text
0 4 4 {}
1 9 -1 {4: 0}
2 1 7 {4: 0, 9: 1}
3 6 2 {4: 0, 9: 1, 1: 2}
4 5 3 {4: 0, 9: 1, 1: 2, 6: 3}
5 3 5 {4: 0, 9: 1, 1: 2, 6: 3, 5: 4}
pair 4 5
```

The pair is found at `j = 5` (`x = 3`, need `5`, stored at index 4). Problem 12 traces the same idea.
</details>

## 7. Prefix sums plus a dictionary (the recall from dsa.03)

### Why equal prefix sums matter

Prefix sums: `p[0] = 0`, `p[i+1] = p[i] + a[i]`. The sum of `a[l..r]` is `p[r+1] - p[l]`. In dsa.03 you counted subarrays with sum `k` by asking, at each end `r`: how many earlier prefixes `p[l]`
equal `p[r+1] - k`? That is a **complement lookup on prefix sums**. The dictionary stores *how many times* each prefix sum occurred so far.

```python
def count_subarrays_sum(a, k):
    seen = {0: 1}                      # the empty prefix
    s = 0
    total = 0
    for x in a:
        s += x
        total += seen.get(s - k, 0)
        seen[s] = seen.get(s, 0) + 1
    return total

print(count_subarrays_sum([1, 2, 3], 3))
print(count_subarrays_sum([1, -1, 1, -1], 0))
```
```text
2
4
```

Why `{0: 1}`? The empty prefix (before the first element) has sum 0 and must be counted, otherwise every subarray that starts at index 0 is missed.

### Zero-sum subarrays and "equal prefixes"

With `k = 0` the condition `p[r+1] - p[l] = 0` just says **two prefix sums are equal**. If a prefix value occurs `c` times, it makes `c * (c - 1) / 2` zero-sum subarrays:

```python
from collections import Counter
from itertools import accumulate

a = [1, -1, 2, -2, 3, -3]
prefix = list(accumulate(a, initial=0))
print(prefix)
c = Counter(prefix)
print(c)
print(sum(v * (v - 1) // 2 for v in c.values()))
```
```text
[0, 1, 0, 2, 0, 3, 0]
Counter({0: 4, 1: 1, 2: 1, 3: 1})
6
```

### Longest instead of counting: store the first index

For "the **longest** subarray with property X" store the **first** index at which each prefix value appeared, and never overwrite it. The earliest start gives the longest block.

```python
def longest_sum_k(a, k):
    first = {0: -1}                  # empty prefix sits before index 0
    s = 0
    best = 0
    for i, x in enumerate(a):
        s += x
        if s - k in first:
            best = max(best, i - first[s - k])
        if s not in first:
            first[s] = i
    return best

print(longest_sum_k([1, -1, 5, -2, 3], 3))
print(longest_sum_k([0, 0, 0, 5], 5))
```
```text
4
4
```

Three things must be right (problem 30 breaks all three): look up `s - k` (not `s + k`), start with `{0: -1}`, and store a prefix only if it is **absent**.

### Balanced subarrays: transform first

"Equal number of 0 and 1" is a sum problem after replacing every `0` by `-1`:

```python
def longest_balanced(a):
    first = {0: -1}
    s = 0
    best = 0
    for i, x in enumerate(a):
        s += 1 if x == 1 else -1
        if s in first:
            best = max(best, i - first[s])
        else:
            first[s] = i
    return best

print(longest_balanced([0, 1, 0, 1, 1, 1, 0]))
print(longest_balanced([1, 1, 1]))
```
```text
4
0
```

### Remainders: subarrays divisible by `m`

A block sum is divisible by `m` exactly when the two prefix sums have the **same remainder** modulo `m`. So count prefix remainders:

```python
def count_divisible(a, m):
    seen = {0: 1}
    s = 0
    total = 0
    for x in a:
        s = (s + x) % m          # Python's % keeps the result in 0..m-1, even for negative sums
        total += seen.get(s, 0)
        seen[s] = seen.get(s, 0) + 1
    return total

print(count_divisible([4, 5, 0, -2, -3, 1], 5))
```
```text
7
```

The same transformation "turn the condition into *equal keys*" solves problems on prefix XOR, balance counters and differences of two counters.

### A small checklist for prefix + dictionary

1. Define the prefix value (sum, remainder, balance, xor).
2. Decide what a valid block means in terms of two prefix values (difference `k`, equal, equal remainder).
3. Count: store *counts*. Longest: store *first index*. Shortest: store *last index* (overwrite).
4. Put the empty prefix in the dictionary first.
5. Look up **before** storing the current prefix (unless `k = 0` and you are careful about it).

**Try it 7: predict the output**

```python
from itertools import accumulate
a = [2, -2, 2, -2, 2]
p = list(accumulate(a, initial=0))
print(p)
print(p.count(0), p.count(2))
```

How many zero-sum subarrays does `a` have?

<details><summary>Answer</summary>

```python
from itertools import accumulate
a = [2, -2, 2, -2, 2]
p = list(accumulate(a, initial=0))
print(p)
print(p.count(0), p.count(2))
print(3 * 2 // 2 + 3 * 2 // 2)
```
```text
[0, 2, 0, 2, 0, 2]
3 3
6
```

The prefix `0` occurs 3 times (3 pairs) and `2` occurs 3 times (3 pairs), so `a` has `3 + 3 = 6` zero-sum subarrays.
</details>

## 8. Seen-sets, duplicates and "first" questions

### Duplicates

```python
def has_duplicate(a):
    seen = set()
    for x in a:
        if x in seen:
            return True
        seen.add(x)
    return False

print(has_duplicate([4, 8, 15, 8, 23]))
print(has_duplicate([4, 8, 15, 16, 23]))
print(len(set([4, 8, 15, 8, 23])) < 5)    # the one-line version
```
```text
True
False
True
```

The loop can stop early; the one-liner builds the full set first. Both are `O(n)`.

### Finding the duplicated values themselves

```python
def repeated_values(a):
    seen, repeated = set(), set()
    for x in a:
        if x in seen:
            repeated.add(x)
        else:
            seen.add(x)
    return sorted(repeated)

print(repeated_values([1, 2, 3, 2, 1, 2, 5]))
```
```text
[1, 2]
```

A value that occurs three times is added to `repeated` twice, but a set keeps one copy.

### First unique, first repeated

Two different questions with similar names:

- **First repeated** element (the first position at which we see something already seen): one pass with a set, stop at the first hit.
- **First unique** element (the first value that occurs once in the whole array): needs the **final counts**, so two passes.

```python
def first_repeated(a):
    seen = set()
    for x in a:
        if x in seen:
            return x
        seen.add(x)
    return None

def first_unique_index(s):
    count = {}
    for ch in s:
        count[ch] = count.get(ch, 0) + 1
    for i, ch in enumerate(s):
        if count[ch] == 1:
            return i
    return -1

print(first_repeated([5, 1, 2, 1, 5]))
print(first_unique_index("loveleetcode"))
print(first_unique_index("aabb"))
```
```text
1
2
-1
```

You cannot decide "unique" before you have seen the whole string, which is why the first pass only counts.

### Distinct values in every window

A set per window costs `O(n * k)`. Keep one count dictionary and **delete a key when its count reaches 0**:

```python
def distinct_in_windows(a, k):
    count = {}
    for x in a[:k]:
        count[x] = count.get(x, 0) + 1
    out = [len(count)]
    for i in range(k, len(a)):
        count[a[i]] = count.get(a[i], 0) + 1
        old = a[i - k]
        count[old] -= 1
        if count[old] == 0:
            del count[old]
        out.append(len(count))
    return out

print(distinct_in_windows([1, 2, 1, 3, 4, 2, 3], 4))
```
```text
[3, 4, 4, 3]
```

If you forgot the `del`, `len(count)` would count values that left the window long ago: `len(count)` is the number of distinct values only if every key has count at least 1.

### Substrings and fixed windows

The repeated-DNA problem uses a set of windows (slices of fixed length):

```python
def repeated_segments(s, L):
    seen, repeated = set(), set()
    for i in range(len(s) - L + 1):
        seg = s[i:i + L]
        if seg in seen:
            repeated.add(seg)
        else:
            seen.add(seg)
    return sorted(repeated)

print(repeated_segments("AAAAACCCCCAAAAACCCCCCAAAAAGGGTTT", 10))
print(repeated_segments("AAAA", 2))
```
```text
['AAAAACCCCC', 'CCCCCAAAAA']
['AA']
```

Each slice costs `O(L)` to build and hash, so this is `O(n * L)`: fine for `L <= 20`, bad for `L = 100000`. Section 12 replaces the slice by a rolling hash whose update is `O(1)`.

### Longest consecutive run with a set

Sorting would be `O(n log n)`. A set gives `O(n)` with one trick: only start counting at a **run start** (a value `x` whose `x - 1` is missing).

```python
def longest_run(a):
    values = set(a)
    best = 0
    for x in values:
        if x - 1 not in values:
            length = 1
            while x + length in values:
                length += 1
            best = max(best, length)
    return best

print(longest_run([100, 4, 200, 1, 3, 2]))
print(longest_run([]))
```
```text
4
0
```

Why is it linear? The inner `while` runs only from run starts, and every value belongs to exactly one run, so every value is stepped over at most once in total. If you started from *every* value, a run of
length `m` would be walked `m + (m-1) + ... + 1` times, quadratic.

### Intersection, union, difference

Sets do these directly, in `O(len)` of the sets involved:

```python
a = [1, 2, 2, 3, 7]
b = [2, 2, 7, 9]
print(sorted(set(a) & set(b)))
print(sorted(set(a) - set(b)))
print(sorted(set(a) | set(b)))
```
```text
[2, 7]
[1, 3]
[1, 2, 3, 7, 9]
```

**Try it 8: predict the output**

```python
def f(a):
    seen = set()
    out = []
    for x in a:
        if x not in seen:
            out.append(x)
            seen.add(x)
    return out

print(f([3, 1, 3, 2, 1]))
```

What does `f` do? How would the answer change if you wrote `list(set(a))`?

<details><summary>Answer</summary>

```python
def f(a):
    seen = set()
    out = []
    for x in a:
        if x not in seen:
            out.append(x)
            seen.add(x)
    return out

print(f([3, 1, 3, 2, 1]))
print(sorted(set([3, 1, 3, 2, 1])))
```
```text
[3, 1, 2]
[1, 2, 3]
```

`f` removes duplicates and **keeps the order of first appearance**. `list(set(a))` removes duplicates too but gives no promise about the order (for small integers it often looks sorted by accident).
</details>

## 9. Implementing a hash table from scratch

So far `dict` and `set` were magic boxes. In this section you open the box. Nothing here is hard, but each idea builds on the last, so go slowly. By the end you will have written a working
hash map, and you will know why it is fast, when it is slow, and why the numbers in section 13 matter.

### The problem a hash table solves

We want a structure with three operations: `put(key, value)`, `get(key)`, `delete(key)`, all fast. Two simple answers are both too slow:

- **An unsorted list of pairs**: `put` is fast (append) but `get` must scan: `O(n)`.
- **A sorted list with binary search**: `get` is `O(log n)`, but inserting in the middle shifts elements: `O(n)`.

An **array** has `O(1)` access by index. If keys were small non-negative integers we could store `value` in `table[key]` and be done (a **direct-address table**). The catch is that keys are
huge (`10^9`), strings, or tuples. We cannot have an array with a slot for every possible key.

The hash table idea: **shrink the key space into a small array with a function**. A **hash function** `h(key)` maps every key to an index `0 .. m - 1` in an array of `m` **buckets**.

### Step 1: the index is `hash(key) % m`

```python
m = 8
for key in [5, 13, 21, 7, 100, 12]:
    print(key, "->", key % m)
```
```text
5 -> 5
13 -> 5
21 -> 5
7 -> 7
100 -> 4
12 -> 4
```

Different keys can land on the same bucket: `5`, `13` and `21` all give 5. That is a **collision**. There are infinitely many possible keys and only `m` buckets, so by the pigeonhole principle
collisions cannot be avoided. A hash table is a plan for **living with collisions**.

Why `% m`? The hash function returns a big integer (Python's `hash` can be any 64-bit value, negative included). The remainder modulo `m` folds it into the range `0 .. m - 1`. In Python the result of
`%` with a positive `m` is never negative, which is exactly what an array index needs.

### Step 2: chaining

The simplest way to handle collisions: each bucket holds a **list** of the pairs that landed there (a **chain**).

- `put`: go to bucket `h(key) % m`; scan the chain; if the key is there, replace the value; else append a pair.
- `get`: go to the bucket and scan its chain.
- `delete`: go to the bucket and remove the pair.

```python
class ChainedMap:
    def __init__(self, m=4):
        self.m = m
        self.buckets = [[] for _ in range(m)]
        self.size = 0

    def _find(self, key):
        chain = self.buckets[hash(key) % self.m]
        for pos, pair in enumerate(chain):
            if pair[0] == key:
                return chain, pos
        return chain, -1

    def put(self, key, value):
        chain, pos = self._find(key)
        if pos >= 0:
            chain[pos][1] = value
        else:
            chain.append([key, value])
            self.size += 1

    def get(self, key, default=None):
        chain, pos = self._find(key)
        return chain[pos][1] if pos >= 0 else default

    def delete(self, key):
        chain, pos = self._find(key)
        if pos >= 0:
            chain.pop(pos)
            self.size -= 1
            return True
        return False

t = ChainedMap()
for k in [5, 9, 12, 13, 7, 16]:
    t.put(k, k * 10)
print(t.buckets)
print(t.get(13), t.get(99), t.get(99, "none"))
t.put(13, "new")
print(t.get(13), t.size)
print(t.delete(9), t.delete(9), t.size)
```
```text
[[[12, 120], [16, 160]], [[5, 50], [9, 90], [13, 130]], [], [[7, 70]]]
130 None none
new 6
True False 5
```

Integers hash to themselves in Python (`hash(13) == 13`), so with `m = 4` the keys `5, 9, 13` all go to bucket 1: you can see the chain `[5, 9, 13]` formed. (We use integer keys here so the output
is the same on every machine; with string keys the layout would change from run to run.)

### How long is a chain?

A lookup costs: one hash computation, then a scan of **one chain**. So the cost is the **length of one chain**, not the size of the table. If `n` keys spread evenly over `m` buckets, the average
chain length is `n / m`. This ratio is called the **load factor**:

```
load factor  alpha = n / m
```

If `alpha` is kept below a constant (say 0.75), the average chain has under one item and a lookup costs `O(1)` on average. If `alpha` grows (many keys, few buckets) chains get long and the table
slides toward the `O(n)` of a plain list.

```python
def longest_chain(keys, m):
    counts = [0] * m
    for k in keys:
        counts[k % m] += 1
    return max(counts)

keys = list(range(1000))
for m in [4, 16, 64, 256, 1024]:
    print("m =", m, " load factor =", round(len(keys) / m, 2), " longest chain =", longest_chain(keys, m))
```
```text
m = 4  load factor = 250.0  longest chain = 250
m = 16  load factor = 62.5  longest chain = 63
m = 64  load factor = 15.62  longest chain = 16
m = 256  load factor = 3.91  longest chain = 4
m = 1024  load factor = 0.98  longest chain = 1
```

(Sequential integers spread perfectly, so the longest chain is `ceil(n / m)`. Real keys are less polite, but the trend is the same: more buckets, shorter chains.)

### Step 3: resizing

We cannot know in advance how many keys will arrive. So the table **grows itself**: when the load factor crosses a limit, allocate a bigger array (usually **double**) and **rehash**: insert every key
again, because the bucket depends on `m`, and `m` just changed.

```python
class ResizingMap:
    LIMIT = 0.75

    def __init__(self):
        self.m = 4
        self.buckets = [[] for _ in range(self.m)]
        self.size = 0

    def _chain(self, key):
        return self.buckets[hash(key) % self.m]

    def put(self, key, value):
        chain = self._chain(key)
        for pair in chain:
            if pair[0] == key:
                pair[1] = value
                return
        chain.append([key, value])
        self.size += 1
        if self.size / self.m > self.LIMIT:
            self._grow()

    def _grow(self):
        old = [pair for chain in self.buckets for pair in chain]
        self.m *= 2
        self.buckets = [[] for _ in range(self.m)]
        for key, value in old:
            self._chain(key).append([key, value])
        print("  grew to", self.m, "buckets")

    def get(self, key, default=None):
        for pair in self._chain(key):
            if pair[0] == key:
                return pair[1]
        return default

t = ResizingMap()
for k in range(1, 14):
    t.put(k * 8, k)         # multiples of 8 all collide while m is 4 or 8
    print(k * 8, "size", t.size, "m", t.m)
print(t.get(48), t.get(49))
```
```text
8 size 1 m 4
16 size 2 m 4
24 size 3 m 4
  grew to 8 buckets
32 size 4 m 8
40 size 5 m 8
48 size 6 m 8
  grew to 16 buckets
56 size 7 m 16
64 size 8 m 16
72 size 9 m 16
80 size 10 m 16
88 size 11 m 16
96 size 12 m 16
  grew to 32 buckets
104 size 13 m 32
6 None
```

Watch what happens: keys that are all multiples of 8 collide completely while `m` is 4 and 8 (everything is in bucket 0), and even at `m = 16` half of them still share a bucket. Only a much larger `m` separates them.
Resizing helps with load, but it cannot fix a badly matched hash function: keys with a common factor of `m` still pile up. This is why real implementations mix the bits of the hash before taking the remainder,
and why a prime or a randomised modulus is often chosen.

### Why doubling? Amortised `O(1)`

A resize costs `O(m + n)`: it touches every key. If you resized after **every** insert, `n` inserts would cost `O(n^2)`. By **doubling**, resizes become rarer as the table grows:

```python
def total_copy_work(n_inserts, grow):
    size = 1
    copies = 0
    count = 0
    for _ in range(n_inserts):
        count += 1
        if count > size:
            copies += count - 1       # rehash every key that was present
            size = grow(size)
    return copies

n = 4096
print("doubling :", total_copy_work(n, lambda s: s * 2))
print("grow by 1:", total_copy_work(n, lambda s: s + 1))
```
```text
doubling : 4095
grow by 1: 8386560
```

Doubling copies fewer than `2n` keys in total: on average each insert pays for about two copies, `O(1)`. This is **amortised** analysis: a single insert may be expensive, but the total is small
spread over all inserts. Growing by a constant amount copies `1 + 2 + 3 + ... = O(n^2)` keys.

### Step 4: deletion in a chaining table

Chaining makes deletion easy: remove the pair from its chain. Tables usually do **not** shrink on delete (or shrink only when very empty), to avoid resizing back and forth around the limit.

### What Python really does

CPython's `dict` is a hash table, but with **open addressing** (next section) instead of chains, and with a separate compact array that stores entries in insertion order (that is why a `dict` remembers order).
It resizes when about two thirds full. You do not need those details to solve problems; you need the *ideas*: bucket index from the hash, collisions, load factor, resizing.

**Try it 9: predict the output**

A chaining table has `m = 5` buckets and `h(k) = k % 5`. You insert `7, 12, 3, 8, 17`. Draw the buckets, then say how many comparisons `get(17)` needs.

<details><summary>Answer</summary>

```python
m = 5
buckets = [[] for _ in range(m)]
for k in [7, 12, 3, 8, 17]:
    buckets[k % m].append(k)
print(buckets)
chain = buckets[17 % m]
print(chain.index(17) + 1, "comparisons")
```
```text
[[], [], [7, 12, 17], [3, 8], []]
3 comparisons
```

`7`, `12`, `17` all have remainder 2: the chain is `[7, 12, 17]`, and `17` is third, so 3 comparisons. `3` and `8` share bucket 3.
</details>

## 10. Open addressing, probing and tombstones

### The idea: no chains, one array

In **open addressing** every key is stored **directly in the array**. If the home slot `h(key) % m` is taken, we **probe**: look at another slot, and another, until we find a free one. The order of
slots visited is the **probe sequence**. The simplest is **linear probing**: try `home`, `home + 1`, `home + 2`, ... wrapping around at the end.

```python
class ProbingSet:
    def __init__(self, m=7):
        self.m = m
        self.slots = [None] * m
        self.size = 0

    def add(self, key):
        if self.size == self.m:
            raise RuntimeError("table full")
        i = key % self.m
        probes = [i]
        while self.slots[i] is not None:
            if self.slots[i] == key:
                return probes
            i = (i + 1) % self.m
            probes.append(i)
        self.slots[i] = key
        self.size += 1
        return probes

    def contains(self, key):
        i = key % self.m
        for _ in range(self.m):
            if self.slots[i] is None:
                return False            # an empty slot ends the search
            if self.slots[i] == key:
                return True
            i = (i + 1) % self.m
        return False

s = ProbingSet()
for k in [10, 17, 3, 24, 8, 15]:
    print("add", k, "probes", s.add(k))
print(s.slots)
print(s.contains(3), s.contains(31))
```
```text
add 10 probes [3]
add 17 probes [3, 4]
add 3 probes [3, 4, 5]
add 24 probes [3, 4, 5, 6]
add 8 probes [1]
add 15 probes [1, 2]
[None, 8, 15, 10, 17, 3, 24]
True False
```

Home slot for 10, 17, 3 and 24 is slot 3 (`k % 7 == 3`). They fill 3, 4, 5, 6. A block of consecutive full slots is a **cluster**. A key whose home lies inside a cluster has to walk to the end of the
cluster: clusters make probes longer, and longer clusters grow faster (a *rich get richer* effect).

### Why can a search stop at an empty slot?

Say we search for `x` and arrive at an empty slot. If `x` had been inserted, its own insertion walked the same probe sequence and stopped at the **first** empty slot, which was this slot or one earlier.
Since the slot is empty now, `x` is not there. That argument is why **empty means "absent"**, and it is also why it breaks if you empty slots carelessly.

### Load factor matters even more

With open addressing the load factor can never exceed 1 (each key needs its own slot), and performance collapses as it approaches 1. A common rule is to resize before it reaches about 0.5 to 0.7.

```python
def average_probes(keys, m):
    slots = [None] * m
    total = 0
    for k in keys:
        i = k % m
        steps = 1
        while slots[i] is not None:
            i = (i + 1) % m
            steps += 1
        slots[i] = k
        total += steps
    return total / len(keys)

import random
rng = random.Random(1)
m = 1009                                   # a prime table size
for load in [0.25, 0.5, 0.75, 0.9, 0.99]:
    n = int(m * load)
    keys = rng.sample(range(10**6), n)
    print("load", load, "average probes per insert", round(average_probes(keys, m), 2))
```
```text
load 0.25 average probes per insert 1.23
load 0.5 average probes per insert 1.5
load 0.75 average probes per insert 2.34
load 0.9 average probes per insert 4.64
load 0.99 average probes per insert 14.66
```

Probes per insert stay near 1 to 2 at load 0.5 and rise steeply near 1. The numbers come from a seeded random generator, so they are the same on every machine.

### Deletion and tombstones

Suppose `10, 17, 3` sit in slots 3, 4, 5 and we delete `17` by setting slot 4 to `None`. Now `contains(3)` starts at slot 3 (holds 10), moves to slot 4, finds it **empty**, and answers "absent",
although 3 is stored in slot 5. The hole cut the probe run.

The fix is a **tombstone**: a special marker meaning "something was here". Searches treat a tombstone as occupied (keep probing); inserts may reuse it.

```python
EMPTY = None
DELETED = "<deleted>"

class TombstoneSet:
    def __init__(self, m=7):
        self.m = m
        self.slots = [EMPTY] * m

    def add(self, key):
        i = key % self.m
        for _ in range(self.m):
            if self.slots[i] is EMPTY or self.slots[i] == DELETED:
                self.slots[i] = key
                return
            if self.slots[i] == key:
                return
            i = (i + 1) % self.m

    def contains(self, key):
        i = key % self.m
        for _ in range(self.m):
            if self.slots[i] is EMPTY:
                return False
            if self.slots[i] == key:
                return True
            i = (i + 1) % self.m
        return False

    def remove(self, key):
        i = key % self.m
        for _ in range(self.m):
            if self.slots[i] is EMPTY:
                return
            if self.slots[i] == key:
                self.slots[i] = DELETED
                return
            i = (i + 1) % self.m

s = TombstoneSet()
for k in [10, 17, 3]:
    s.add(k)
s.remove(17)
print(s.slots)
print(s.contains(3))       # still found: the tombstone does not stop the search
s.add(24)                  # home slot 3 is full, 4 holds a tombstone: reuse it
print(s.slots)
```
```text
[None, None, None, 10, '<deleted>', 3, None]
True
[None, None, None, 10, 24, 3, None]
```

A simpler (and slower) alternative is to re-insert the keys that follow the deleted one in its cluster. Python's `dict` uses tombstones internally too.

### Chaining versus open addressing

| | Chaining | Open addressing |
|---|---|---|
| Memory | pointers and list overhead | one flat array |
| Load factor | can exceed 1 (long chains) | at most 1; keep it well below |
| Delete | trivial | needs tombstones |
| Cache behaviour | follows pointers | contiguous: faster in practice |
| Bad hash / clustering | a long chain | a long cluster that grows |

For solving problems you will use `dict` and `set`; knowing both designs lets you reason about their cost and about why a weak hash function is dangerous.

### Why `hash(x) % m` and not `x % m`?

If you reduce the raw key, patterns in the data become patterns in the buckets: keys that are all multiples of 8 land in the same bucket of an 8-bucket table, as you saw. A good hash function
first **mixes the bits** of the key, so that structure in the key does not become structure in the index. Python also uses all the bits of the hash, not just the low ones, in its probe sequence. Whenever
you build your own hash for tuples or strings, mix the parts, for example the polynomial hash of section 12.

**Try it 10: trace it**

An open-addressing table has `m = 5` slots, `h(k) = k % 5`, linear probing. Insert `5, 10, 3, 8, 15`. Where does each key go?

<details><summary>Answer</summary>

```python
m = 5
slots = [None] * m
for k in [5, 10, 3, 8, 15]:
    i = k % m
    path = [i]
    while slots[i] is not None:
        i = (i + 1) % m
        path.append(i)
    slots[i] = k
    print(k, path)
print(slots)
```
```text
5 [0]
10 [0, 1]
3 [3]
8 [3, 4]
15 [0, 1, 2]
[5, 10, 15, 3, 8]
```

Slot 0: `5`. `10` also wants slot 0, so it goes to slot 1. `3` takes slot 3. `8` wants slot 3 and goes to slot 4. `15` wants slot 0, finds 0 and 1 taken, and lands in slot 2.
Every probe visits the **next** slot, so the cluster `5, 10` makes `15` walk two extra steps.
</details>

## 11. Designing with hash maps: caches and ordered dictionaries

### An LRU cache

A **cache** keeps the `c` most useful items so repeated requests are fast. When it is full and a new key arrives, it evicts one entry. **LRU** (least recently used) evicts the entry that was used
longest ago. Both `get` and `put` must be `O(1)`.

Idea: a Python `dict` remembers insertion order. To mark a key as "just used", **remove it and insert it again**: it moves to the end. The **first** key in the dictionary is then always the least recently used.

```python
class LRU:
    def __init__(self, capacity):
        self.cap = capacity
        self.data = {}

    def get(self, key):
        if key not in self.data:
            return -1
        value = self.data.pop(key)
        self.data[key] = value          # now the most recent
        return value

    def put(self, key, value):
        if key in self.data:
            del self.data[key]
        elif len(self.data) == self.cap:
            oldest = next(iter(self.data))
            del self.data[oldest]
        self.data[key] = value

cache = LRU(2)
cache.put(1, 1)
cache.put(2, 2)
print(cache.get(1))
cache.put(3, 3)           # evicts 2
print(cache.get(2))
cache.put(4, 4)           # evicts 1
print(cache.get(1), cache.get(3), cache.get(4))
print(list(cache.data))
```
```text
1
-1
-1 3 4
[3, 4]
```

Two subtle rules from problem 37: **updating** an existing key never evicts anything, and `get` counts as a use.

The textbook structure uses a hash map plus a **doubly linked list** (the map finds the node in `O(1)`, the list moves a node to the front in `O(1)`). In Python the ordered dict does the same job.

### Design problems: `O(1)` insert, delete and random pick

"Insert, delete and get a random element, all `O(1)`": a set cannot pick a random element in `O(1)`; a list cannot delete in `O(1)`. Combine them: keep the values in a **list**, and a **dictionary from
value to its index in the list**. To delete, swap the value with the last list item, pop, and fix one index:

```python
class RandomSet:
    def __init__(self):
        self.items = []
        self.pos = {}

    def insert(self, x):
        if x in self.pos:
            return False
        self.pos[x] = len(self.items)
        self.items.append(x)
        return True

    def remove(self, x):
        if x not in self.pos:
            return False
        i = self.pos.pop(x)
        last = self.items.pop()
        if last != x:
            self.items[i] = last
            self.pos[last] = i
        return True

r = RandomSet()
for x in [10, 20, 30, 40]:
    r.insert(x)
print(r.remove(20), r.remove(99))
print(r.items, r.pos)
```
```text
True False
[10, 40, 30] {10: 0, 30: 2, 40: 1}
```

The list gives index access for random picks; the dictionary gives `O(1)` location for deletion. Combining two structures, each covering the other's weakness, is a very common design trick.

### A hash map as a "memo" of past answers

A dictionary can remember answers so that repeated work is skipped (**memoisation**, covered fully in the dynamic programming module):

```python
memo = {}

def collatz_length(n):
    if n == 1:
        return 1
    if n in memo:
        return memo[n]
    nxt = n // 2 if n % 2 == 0 else 3 * n + 1
    memo[n] = 1 + collatz_length(nxt)
    return memo[n]

print(collatz_length(27), len(memo))
print(max(range(1, 30), key=collatz_length))
```
```text
112 111
27
```

Here the key is the **state** of the computation and the value is its answer. This is the same pattern as every problem in the module: if a question can be asked again with the same key, store the answer under that key.

### Designing a key for a state

When you need to remember "visited states" (for example positions in a grid, or the pair `(i, j)`), use a tuple as the key:

```python
visited = set()
visited.add((0, 0))
visited.add((0, 1))
print((0, 1) in visited, (1, 0) in visited)
```
```text
True False
```

A tuple of two ints is the most common key in grid problems (BFS in later modules).

**Try it 11: predict the output**

```python
d = {}
d["a"] = 1
d["b"] = 2
d["c"] = 3
v = d.pop("a")
d["a"] = v
d["b"] = 20
print(list(d.items()))
print(next(iter(d)))
```

<details><summary>Answer</summary>

```python
d = {}
d["a"] = 1
d["b"] = 2
d["c"] = 3
v = d.pop("a")
d["a"] = v
d["b"] = 20
print(list(d.items()))
print(next(iter(d)))
```
```text
[('b', 20), ('c', 3), ('a', 1)]
b
```

`pop` then insert moved `a` to the end. Updating `b` in place did not move it, so the order is `b, c, a`, and the oldest key is `b`.
</details>

## 12. String hashing and the polynomial rolling hash

### The problem: comparing substrings

Python compares two strings of length `L` in `O(L)`. Problems like "does this pattern occur in the text", "which substrings of length `L` repeat" or "is the substring `s[l..r]` equal to
`s[x..y]`" compare many substrings. Comparing each pair letter by letter is far too slow. The idea: give every string a **fingerprint**, a number that is cheap to compare, and compare fingerprints.
If two fingerprints differ the strings are definitely different. If they are equal the strings are *probably* equal. This is **string hashing**.

### The polynomial hash

Treat the string as a number in base `B`. With letter values `v('a') = 1, ..., v('z') = 26`:

```
H(t) = v(t0) * B^(k-1) + v(t1) * B^(k-2) + ... + v(t(k-1))      (mod M)
```

Computing it from the left is Horner's rule: start with `h = 0`; for each letter `h = (h * B + v) % M`.

```python
B = 31
M = 101

def poly(s):
    h = 0
    for ch in s:
        h = (h * B + (ord(ch) - 96)) % M
    return h

for word in ["abc", "cab", "abd", "ga"]:
    print(word, poly(word))
```
```text
abc 16
cab 88
abd 17
ga 16
```

(Small numbers so you can check by hand: `abc` is `((1*31 + 2)*31 + 3) % 101 = 1026 % 101 = 16`.) Three facts:

- **Order matters.** `abc` and `cab` differ because earlier letters are multiplied by `B` more times.
- **Equal strings have equal hashes** (always).
- **Different strings can share a hash**: `abc` and `ga` both give 16. A collision. With real moduli (around `10^9` or `2^61 - 1`) collisions are rare, but never impossible.

### Why a modulus, why letters start at 1

Without `% M` the number has about `k * log2(B)` bits: thousands of digits for long strings, and every operation costs `O(k)` again. Taking the remainder keeps the numbers small (they fit
in a machine word when `M < 2^31`; Python integers never overflow, but they get slower when big).

Letters must map to **1 or more**. If `v('a')` were 0, then `a`, `aa` and `aaa` would all hash to 0, because leading zeros change nothing:

```python
def poly0(s, B=31, M=101):
    h = 0
    for ch in s:
        h = (h * B + (ord(ch) - 97)) % M      # 'a' counts as 0: a bug
    return h

print(poly0("a"), poly0("aa"), poly0("aaa"), poly0("b"), poly0("ab"))
```
```text
0 0 0 1 1
```

### Prefix hashes: any substring in `O(1)`

Compute `P[0] = 0` and `P[i+1] = (P[i] * B + v(s[i])) % M` once, in `O(n)`. Think of `P[r]` as the hash of the prefix `s[0..r-1]`. To get the hash of `s[l..r-1]`, take `P[r]` and remove the
first `l` letters. In `P[r]` those letters carry the weight `B^(r-l)` (they are shifted left by the length of the block), so:

```
H(s[l..r-1]) = (P[r] - P[l] * B^(r-l)) mod M
```

```python
B = 131
M = 1_000_000_007

s = "abcabc"
P = [0]
pw = [1]
for ch in s:
    P.append((P[-1] * B + (ord(ch) - 96)) % M)
    pw.append(pw[-1] * B % M)

def sub_hash(l, r):                 # hash of s[l:r]
    return (P[r] - P[l] * pw[r - l]) % M

print(sub_hash(0, 3), sub_hash(3, 6), sub_hash(0, 3) == sub_hash(3, 6))
print(sub_hash(1, 4), sub_hash(0, 3))
```
```text
17426 17426 True
34716 17426
```

`abc` at `0..3` and `abc` at `3..6` have the same hash; `bca` has another. After an `O(n)` precomputation each comparison of two substrings costs `O(1)`, whatever their length. Problem 32 asks you to
build exactly this.

Details worth noticing:

- `pw[i]` is `B^i mod M`, built by repeated multiplication so no number ever gets big. You can also write `pow(B, e, M)`, which does fast modular exponentiation.
- `P[r] - P[l] * pw[r - l]` can be negative before the `%`. Python's `%` always returns a value in `0 .. M-1` for positive `M`, so you need no fix-up. In C++ or Java you must add `M` back.

### Rolling a fixed-length window

If every window has the same length `L`, you do not even need the prefix array. Keep the hash of the current window and **roll** it one step: remove the leaving letter, shift, add the entering letter:

```
H_next = ((H - v(old) * B^(L-1)) * B + v(new)) mod M
```

```python
B = 10
M = 97
s = "31415926"
L = 3
top = pow(B, L - 1, M)

h = 0
for ch in s[:L]:
    h = (h * B + int(ch)) % M
print("start", s[:L], h)
for i in range(L, len(s)):
    h = ((h - int(s[i - L]) * top) * B + int(s[i])) % M
    window = s[i - L + 1:i + 1]
    print(window, h, int(window) % M)
```
```text
start 314 23
141 44 44
415 27 27
159 62 62
592 10 10
926 53 53
```

The two last columns always agree: the rolling update is exact arithmetic modulo `M`, not an approximation. Cost of one step: a constant number of operations, independent of `L`.
Problem 38 asks you to trace this.

### Rabin-Karp: pattern search

To find a pattern `p` of length `m` in a text `t`: hash `p` once, roll a window of length `m` over `t`, and compare hashes. When they are equal, **verify** by comparing the actual strings (this protects you from
a collision and costs `O(m)` only for a real match or a rare false one).

```python
def rabin_karp(t, p):
    B = 131
    M = 1_000_000_007
    n, m = len(t), len(p)
    if m > n:
        return []
    hp = h = 0
    for i in range(m):
        hp = (hp * B + ord(p[i]) - 96) % M
        h = (h * B + ord(t[i]) - 96) % M
    top = pow(B, m - 1, M)
    found = []
    for i in range(n - m + 1):
        if h == hp and t[i:i + m] == p:
            found.append(i)
        if i + m < n:
            h = ((h - (ord(t[i]) - 96) * top) * B + ord(t[i + m]) - 96) % M
    return found

print(rabin_karp("abababa", "aba"))
print(rabin_karp("hello", "xyz"))
```
```text
[0, 2, 4]
[]
```

Expected time `O(n + m)`. The worst case is `O(n * m)` if the hash gives many false matches or the pattern really occurs everywhere (every occurrence is verified in `O(m)`). When you only need to **count**
matches and a wrong answer with probability `10^-18` is acceptable, you can skip the verification.

Rabin-Karp beats brute force when you search for **many patterns of the same length** at once (store the pattern hashes in a set) or compare **many pairs of substrings**.
For a single pattern, KMP or the Z-function (later modules) give `O(n + m)` with no hashing risk.

### Distinct substrings of one length and the longest repeat

A set of rolling hashes counts the distinct substrings of length `L` in `O(n)`:

```python
def distinct_windows(s, L):
    B = 911382323
    M = (1 << 61) - 1
    h = 0
    for i in range(L):
        h = (h * B + ord(s[i]) - 96) % M
    top = pow(B, L - 1, M)
    seen = {h}
    for i in range(L, len(s)):
        h = ((h - (ord(s[i - L]) - 96) * top) * B + ord(s[i]) - 96) % M
        seen.add(h)
    return len(seen)

print(distinct_windows("abcabcab", 3))
```
```text
3
```

Combine it with **binary search on the length** to find the **longest repeated substring**. The property "some substring of length `k` occurs twice" is monotone: if it holds for `k`, it holds for `k - 1`.

```python
def longest_repeat(s):
    B = 911382323
    M = (1 << 61) - 1
    vals = [ord(c) - 96 for c in s]
    n = len(s)

    def repeats(k):
        h = 0
        for i in range(k):
            h = (h * B + vals[i]) % M
        top = pow(B, k - 1, M)
        seen = {h}
        for i in range(k, n):
            h = ((h - vals[i - k] * top) * B + vals[i]) % M
            if h in seen:
                return True
            seen.add(h)
        return False

    lo, hi = 0, n - 1
    while lo < hi:
        mid = (lo + hi + 1) // 2
        if repeats(mid):
            lo = mid
        else:
            hi = mid - 1
    return lo

print(longest_repeat("banana"), longest_repeat("abcd"), longest_repeat("aaaaa"))
```
```text
3 0 4
```

`about log2(n)` checks of `O(n)` each: `O(n log n)`. The `(lo + hi + 1) // 2` rounds up, so `lo = mid` always makes progress.

### Hashing other things

The polynomial hash works on any sequence: a list of numbers, a row of a grid, a path. To compare two **rows** of a 2D grid, hash each row; to compare two **sub-rectangles**, hash rows then hash the hashes
(2D rolling hash). To compare a string with its **reverse** (palindrome checks on substrings), keep a prefix hash of `s` and one of `reversed(s)`; a substring is a palindrome exactly when its forward and reverse hashes
match.

```python
B = 131
M = 1_000_000_007

def prefix_hashes(t):
    P = [0]
    for ch in t:
        P.append((P[-1] * B + ord(ch) - 96) % M)
    return P

s = "abacaba"
n = len(s)
pw = [1] * (n + 1)
for i in range(1, n + 1):
    pw[i] = pw[i - 1] * B % M
fwd = prefix_hashes(s)
rev = prefix_hashes(s[::-1])

def sub(P, l, r):
    return (P[r] - P[l] * pw[r - l]) % M

def is_palindrome(l, r):          # s[l:r]
    # the reverse of s[l:r] is the block of the reversed string at n-r .. n-l
    return sub(fwd, l, r) == sub(rev, n - r, n - l)

print(is_palindrome(0, 7), is_palindrome(0, 3), is_palindrome(1, 4), is_palindrome(2, 5))
```
```text
True True False True
```

**Try it 12: compute by hand**

With `B = 10`, `M = 97` and the digit string `2718`, what is the hash of the window `271`, and what is the rolled hash of the window `718`?

<details><summary>Answer</summary>

```python
M = 97
h = 271 % M
print(h)
top = pow(10, 2, M)
h2 = ((h - 2 * top) * 10 + 8) % M
print(h2, 718 % M)
```
```text
77
39 39
```

`271 = 2 * 97 + 77`, so the first hash is 77. Rolling out `2` (weight `100 % 97 = 3`) and rolling in `8` gives the same value as `718 % 97`.
</details>

## 13. Collisions, the modulus, and double hashing

### How likely is a collision?

A hash with `M` possible values behaves like a random function. For **two** fixed different strings the probability that they collide is about `1 / M`. But programs rarely compare two strings; they compare
**many pairs**. Among `n` strings there are `n * (n - 1) / 2` pairs. This is the **birthday effect**: with 23 people the chance that two share a birthday is already about one half.

```python
import random

def collisions(n, M, seed):
    rng = random.Random(seed)
    seen = {}
    pairs = 0
    for _ in range(n):
        h = rng.randrange(M)
        pairs += seen.get(h, 0)
        seen[h] = seen.get(h, 0) + 1
    return pairs

n = 200000
M = 10**9 + 7
print("expected colliding pairs about", round(n * (n - 1) / 2 / M, 1))
print("simulated:", [collisions(n, M, seed) for seed in range(4)])
```
```text
expected colliding pairs about 20.0
simulated: [16, 19, 28, 16]
```

(The simulation uses a seeded generator, so the numbers are the same on every machine.) With `n = 200000` hashes and `M = 10^9 + 7` you expect about **20 colliding pairs**. One modulus near `10^9` is not
safe when the program compares that many substrings.

### Making collisions unlikely

| Technique | Chance of collision per pair | Cost |
|---|---|---|
| `M` around `10^9` | about `10^-9` | cheap; fine for a few thousand comparisons |
| `M = 2^61 - 1` | about `4 * 10^-19` | Python ints handle it; a bit slower |
| **double hashing**: two independent `(B, M)` pairs; compare the pair of hashes | about `1 / (M1 * M2)` | twice the work |
| verify with a real comparison after a match | exact | `O(L)` per match |

```python
B1, M1 = 131, 1_000_000_007
B2, M2 = 137, 998_244_353

def double_hash(s):
    h1 = h2 = 0
    for ch in s:
        v = ord(ch) - 96
        h1 = (h1 * B1 + v) % M1
        h2 = (h2 * B2 + v) % M2
    return (h1, h2)

print(double_hash("abc"))
print(double_hash("abc") == double_hash("abc"), double_hash("abc") == double_hash("abd"))
```
```text
(17426, 19046)
True False
```

A pair `(h1, h2)` is a tuple, so it can be put in a set or used as a dictionary key directly.

### Choosing `B` and `M`

- `M` should be large; a **prime** `M` is the usual choice (`10^9 + 7`, `998244353`, `2^61 - 1` is also prime). With a prime modulus a polynomial of degree `k` has at most `k` roots, which is what makes the collision probability
  small for a random base.
- `B` must be larger than the largest letter value (here more than 26), and not 0 or 1. A **random** base in `[256, M - 1]` chosen at program start makes the hash unpredictable.
- Do not choose `M` that is a power of two with a *fixed* `B`: there are classic strings (the Thue-Morse construction) that collide for any `B` when `M = 2^64`. This is the textbook attack on `unsigned long long` overflow hashing.

### Anti-hash tests

Judges (and programming contests) sometimes include inputs designed to break popular `(B, M)` pairs: two strings of the same length with the same hash under well-known parameters such as `B = 31, M = 10^9 + 7`
or the overflow hash. If your `B` and `M` are fixed and public, an attacker can prepare such strings in advance. Three defences:

1. **Random base** chosen at runtime: `B = random.randrange(256, M - 1)`. The attacker cannot know it.
2. **Double hashing** with two different moduli.
3. **Verify** a match by direct comparison when a wrong answer is unacceptable.

For the problems in this module the base and modulus are **fixed in the statement** so that your output is deterministic and checkable; the tests contain no attack strings. In a real contest, randomise.

### A collision, concretely

The numbers in section 12 had `M = 101`, so collisions are easy to find by search:

```python
B, M = 31, 101

def poly(s):
    h = 0
    for ch in s:
        h = (h * B + ord(ch) - 96) % M
    return h

target = poly("abc")
found = []
for a in "abcdefghijklmnopqrstuvwxyz":
    for b in "abcdefghijklmnopqrstuvwxyz":
        if a + b != "abc" and poly(a + b) == target:
            found.append(a + b)
print(target, found[:5])
```
```text
16 ['cx', 'ga', 'ji', 'mq', 'py']
```

With `M = 101` there are only 101 hashes but 676 two-letter strings, so each hash is shared by about 6 of them. With `M = 2^61 - 1` you would need about `1.5 * 10^9` strings before a collision is likely.

## 14. Pitfalls and surprises

### 1. Do not rely on the order of a `set`

```python
s = {3, 1, 2}
print(s)
print({"b", "a"} == {"a", "b"})
```
```text
{1, 2, 3}
True
```

A set of small integers often *prints* sorted because `hash(n) == n` and the table is small. That is an implementation detail. Sets of strings iterate in a different order in different runs. Whenever the output order
matters, **sort**: `sorted(s)` (or sort the dictionary keys).

A `dict` is different: since Python 3.7 it **guarantees** insertion order. Use that, but remember that an update does not move a key and that `del` then insert moves it to the end.

### 2. `hash()` of strings changes between runs

As seen in section 3. Never print it into a test, never save it to a file, never use it as a stable id. Use your own polynomial hash (fixed `B` and `M`) when you need a reproducible number.

### 3. Changing a dictionary or set while iterating over it

```python
d = {"a": 1, "b": 2, "c": 3}
try:
    for k in d:
        if d[k] == 2:
            del d[k]
except RuntimeError as e:
    print("RuntimeError:", e)

d = {"a": 1, "b": 2, "c": 3}
for k in list(d):                 # iterate over a COPY of the keys
    if d[k] == 2:
        del d[k]
print(d)
```
```text
RuntimeError: dictionary changed size during iteration
{'a': 1, 'c': 3}
```

Iterate over `list(d)` (a copy) if you need to delete while looping, or build a new dictionary.

### 4. Reading a missing key can change a `defaultdict`

Reading `d[key]` on a `defaultdict` creates the key. Use `key in d` to ask. A `Counter` does not create the key on a read.

### 5. Mutable default values and shared lists

```python
bad = dict.fromkeys(["a", "b"], [])      # both keys share ONE list
bad["a"].append(1)
print(bad)

good = {k: [] for k in ["a", "b"]}       # a new list per key
good["a"].append(1)
print(good)
```
```text
{'a': [1], 'b': [1]}
{'a': [1], 'b': []}
```

`dict.fromkeys(keys, value)` uses the **same** object for every key. For lists, build the dictionary with a comprehension.

### 6. Equal numbers are one key

`1`, `1.0` and `True` are the same key. `0.1 + 0.2` is not equal to `0.3`, so using floating point values as keys is dangerous: compute exact keys with integers (for example work in cents, or store the pair
`(numerator, denominator)` in lowest terms).

```python
d = {0.3: "x"}
print(0.1 + 0.2 in d, 0.1 + 0.2)
```
```text
False 0.30000000000000004
```

### 7. `nan` as a key

```python
nan = float("nan")
d = {nan: 1}
print(nan in d, float("nan") in d)
```
```text
True False
```

`nan != nan`, so a *different* `nan` is never found. Avoid it.

### 8. A bad `__hash__` makes everything slow

A hash table is fast only if the hash **spreads** the keys. A class whose `__hash__` returns the same value for all objects puts everything in one bucket:

```python
import time

class Bad:
    def __init__(self, v):
        self.v = v
    def __hash__(self):
        return 1
    def __eq__(self, other):
        return self.v == other.v

class Good:
    def __init__(self, v):
        self.v = v
    def __hash__(self):
        return hash(self.v)
    def __eq__(self, other):
        return self.v == other.v

def build(cls, n):
    t0 = time.perf_counter()
    s = {cls(i) for i in range(n)}
    return time.perf_counter() - t0

n = 1500
t_bad = build(Bad, n)
t_good = build(Good, n)
print("bad hash is at least 20x slower:", t_bad > 20 * t_good)
```
```text
bad hash is at least 20x slower: True
```

With a constant hash the set degrades into a list: every insert compares with every earlier item, `O(n^2)` in total. This is exactly the chain-length effect from section 9.

### 9. Deliberately bad input (hash flooding)

Because Python randomises `str` hashes, an outsider cannot easily craft many strings that collide. Integer keys are **not** randomised, so in contests an adversary can craft many integers that collide in a
`dict`, making it slow. If a judge is known to attack hash tables (some Codeforces problems are), mix the keys: `d[x ^ SECRET]` with a random `SECRET`, or use a sorted structure.

### 10. Memory

A dictionary of `10^6` small integers takes tens of megabytes. If the keys are small non-negative integers (say `0 .. 10^6`), a plain **list** used as a direct-address table is both faster and smaller:

```python
a = [3, 1, 3, 2, 1, 3, 5]
count = [0] * 6              # values are in 0..5
for x in a:
    count[x] += 1
print(count)
```
```text
[0, 2, 1, 3, 0, 1]
```

Use a dictionary when keys are large, sparse, negative, strings or tuples.

## 15. Which tool? A decision guide

| You need to... | Reach for | Cost |
|---|---|---|
| know if a value was seen | `set` | `O(1)` average per lookup |
| count occurrences | `Counter`, or `dict` with `.get(x, 0) + 1` | `O(n)` |
| group items by a property | `dict` of lists with a canonical key | `O(n * key cost)` |
| find a partner with a relation (sum, difference, equal shifted value) | `dict` value -> index or count; look up before you store | `O(n)` |
| count / find subarrays with a sum, balance or remainder condition | dictionary of prefix values (counts, first index) | `O(n)` |
| longest run of consecutive numbers | `set`, start only at run starts | `O(n)` |
| distinct values in every window | one count dictionary, delete keys at 0 | `O(n)` |
| compare many substrings or search a pattern | polynomial prefix or rolling hash | `O(n)` after precomputation |
| a cache with eviction | `dict` that keeps order (pop and reinsert) | `O(1)` per operation |
| keys are small integers | a list used as a table | `O(1)`, least memory |
| data is sorted | two pointers or binary search | `O(n)` / `O(log n)`, no extra memory |
| need the order of keys / min / max / range queries | a sorted structure or heap, not a hash table | `O(log n)` |

### Hash table versus sorting

Many "have I seen this" problems can be solved either way:

| | Hash | Sort |
|---|---|---|
| time | `O(n)` average | `O(n log n)` |
| extra memory | `O(n)` | `O(1)` to `O(n)` |
| guarantee | average only (adversarial inputs can hurt) | worst case guaranteed |
| keeps original indices | yes | only if you carry them |
| ordered output | no | yes |

If the worst case matters more than speed, or if you need order, sort. If you need indices or `O(n)`, hash.

### A short process

1. Write the brute force (two loops) and say what the inner loop searches for.
2. If it searches for one known value or key, store the values you have passed and replace the loop by a lookup.
3. Decide what the dictionary stores: a count, the first index, the last index, a list, or just presence (a set).
4. Decide the order: look up the partner **before** storing the current item.
5. Test edge cases: empty input, one element, all equal, no answer, a repeated key, negative numbers.
6. Keep the brute force as a checker for random small inputs.

## 16. Common traps

1. **Store before lookup.** In two sum, storing `x` first lets an element pair with itself. Look up first, then store (unless the problem allows `i = j`).
2. **Duplicates.** A dictionary built with `{x: i for i, x in enumerate(a)}` keeps the **last** index. Decide whether you need the first, the last, or all.
3. **Forgetting the empty prefix.** Prefix + dictionary needs `{0: 1}` (counting) or `{0: -1}` (longest) at the start.
4. **Overwriting the first index** when you want the longest block.
5. **Counting values instead of positions.** `3 3 3` has `3` pairs of positions. Use `c * (c - 1) // 2`, or count as you go.
6. **Keys that are not canonical.** A sum or a set as anagram key is wrong; a sorted string or a count tuple is right. Test your key on `ad`/`bc` and `aab`/`ab`.
7. **One-directional mapping.** Isomorphism and word patterns need both directions.
8. **Unhashable keys.** Lists and sets cannot be keys; convert to a tuple or a `frozenset`.
9. **Ordering by accident.** Printing a set and expecting sorted output. Sort explicitly.
10. **Leftover zero counts.** In a window of counts, delete keys at 0 or `len(count)` lies.
11. **Slicing in a loop.** `s[i:i+L]` copies `L` letters: the loop is `O(n * L)`. Use indices, or a rolling hash.
12. **Weak hashing.** Letter value 0, a tiny modulus, a fixed well-known base, no verification, `v(a) = ord(a)` mixed with plain Python `hash` on strings (randomised).
13. **Negative modulus results in other languages.** In Python `%` is safe; in C++ add `M` before the final `%`.
14. **Modifying a dict while iterating.** Iterate over `list(d)`.
15. **Using a hash table when a list will do.** Small integer keys: a list is cheaper.
16. **Assuming `O(1)` is a promise.** It is an average. Long chains, collisions or hash flooding make it `O(n)`.
17. **Mutable default sharing.** `dict.fromkeys(keys, [])` shares one list.
18. **Resizing rules in your own table.** Resize on *new* keys only, test the load factor after the insert, and rehash every key (the bucket depends on `m`).

## 17. Summary

- A **hash table** finds a key by turning it into a bucket index with a hash function, in `O(1)` on average. `dict` maps keys to values, `set` stores keys only.
- Its main use in this course is **removing an inner loop**: if the inner loop searches for one known value, remember the values you have passed and look the answer up.
- Keys must be **hashable**: immutable, with equal values having equal hashes. Tuples, strings, numbers and frozensets are fine; lists, sets and dictionaries are not.
- **Frequency counting**: `d[x] = d.get(x, 0) + 1` or `Counter`. A missing `Counter` key reads as 0; a missing `defaultdict` key is created by the read.
- **Grouping**: choose a canonical key (sorted letters, a count tuple, a first-appearance pattern), then `dict` of lists. The key must be equal exactly for the items in one group.
- **Complement pattern**: for each `x`, look up its partner (`target - x`, `x - d`, a shifted key) **before** storing `x`. Counting pairs: add the stored count; or use `c * (c - 1) // 2`.
- **Prefix sums + dictionary**: start with the empty prefix; store counts to count blocks, first indices to find the longest block; transform the condition into "equal prefix values" (sum, balance, remainder).
- **Seen sets**: duplicates, first repeated, first unique (two passes), distinct per window (delete keys at 0), longest consecutive run (start at run starts).
- **Implementation**: bucket = `hash(key) % m`; **chaining** keeps a list per bucket; **open addressing** probes (linear, with tombstones for deletion). **Load factor** `n / m` must stay bounded; when it passes the
  limit, **double** the table and **rehash** every key. Doubling gives amortised `O(1)` inserts.
- **Polynomial hash**: `h = (h * B + v) % M` with `v >= 1`. Prefix hashes give any substring hash in `O(1)`: `(P[r] - P[l] * B^(r-l)) % M`. A fixed-length window rolls in `O(1)`.
  Rabin-Karp, distinct windows, longest repeated substring (binary search) use it.
- **Collisions are unavoidable.** With `M` near `10^9` and 200000 hashes expect about 20 colliding pairs; use `2^61 - 1`, **double hashing**, a **random base**, and **verification** when a wrong answer is not acceptable.
- **Pitfalls**: set order, `hash(str)` is randomised, do not change a dictionary while iterating, `defaultdict` reads create keys, floats as keys, bad `__hash__`, hash flooding on integer keys.

## 18. How this chapter maps to the problems

| Problems | Topic | Section |
|---|---|---|
| 1 (count frequencies), 6 (trace Counter), 11 (trace defaultdict), 16 (top k frequent) | frequency counting | 4 |
| 2 (contains duplicate), 4 (first unique character), 7 (common values), 8 (ransom note), 17 (longest consecutive run) | sets and counts | 2, 4, 8 |
| 3 (trace dictionary basics), 13 (explain why lookup is fast), 26 (explain what can be a key) | dictionary basics, hashing, hashable keys | 1, 2, 3 |
| 5 (valid anagram), 15 (group anagrams), 20 (trace anagram keys), 39 (explain grouping key) | anagram keys and grouping | 5 |
| 9 (isomorphic strings), 10 (word pattern) | two-way matching | 5 |
| 12 (trace two-sum lookup), 14 (two sum), 18 (count pairs with sum), 19 (four lists, sum zero) | the complement pattern | 6 |
| 22 (zero-sum subarrays), 25 (longest balanced subarray), 30 (fix: longest subarray with sum k) | prefix sums + dictionary | 7 |
| 21 (repeated DNA segments), 24 (distinct values in every window) | seen sets, fixed windows | 8 |
| 23 (trace chaining), 27 (trace resize), 29 (explain load factor), 40 (build a hash map) | implementing a hash table | 9 |
| 28 (trace linear probing) | open addressing | 10 |
| 37 (LRU cache) | design with ordered dictionaries | 11 |
| 31 (trace polynomial hash), 32 (substring hash queries), 33 (find every occurrence), 38 (trace rolling window) | polynomial and rolling hashes | 12 |
| 34 (distinct substrings of one length), 35 (longest repeated substring) | rolling hash + set / binary search | 12 |
| 36 (explain collisions in string hashing) | collisions, double hashing, anti-hash | 13 |

Habits that win points in this module: write the brute force first and keep it as a checker; say aloud what the inner loop searches for; decide what the table stores (count, first index, list, presence) before you code;
look up before you store; test empty input, one element, all equal and "no answer"; and use fixed `B` and `M` only when the statement gives them.

## 19. Learning outcomes checklist

By the end of this module you should be able to:

- [ ] Take a nested loop that searches for one known value and replace the inner loop by a set or dictionary lookup, and say why this is `O(n)` on average.
- [ ] Explain what makes a key hashable, why lists cannot be keys, and why `1`, `1.0` and `True` are one key.
- [ ] Count frequencies with `dict` or `Counter`, group with a canonical key, and know the `defaultdict` read-creates-key trap.
- [ ] Solve two sum, count pairs and four-lists problems with the complement lookup (look up before you store).
- [ ] Count, and find the longest, subarrays with a sum, balance or remainder condition using a dictionary of prefix values, with the empty prefix in place.
- [ ] Use sets for duplicates, first unique, longest consecutive run, repeated segments and distinct counts per window.
- [ ] Implement a hash table with chaining, with resizing and rehashing, and explain load factor and amortised `O(1)`.
- [ ] Describe open addressing, linear probing, clusters and tombstones.
- [ ] Build an LRU cache with an ordered dictionary.
- [ ] Compute polynomial hashes, prefix hashes and substring hashes by hand and in code; roll a window hash; write Rabin-Karp.
- [ ] Explain collisions, the birthday effect, double hashing, random bases and verification; avoid anti-hash traps.
- [ ] List the pitfalls: unordered sets, randomised `str` hashes, mutation while iterating, bad `__hash__`.

## 20. Further reading

- Python docs: "dict", "set" and "frozenset" (built-in types), `collections.Counter`, `collections.defaultdict`, `collections.OrderedDict`, and the glossary entry for "hashable".
- CPython notes on the dictionary implementation (Raymond Hettinger's compact dict design) for how open addressing and ordering are combined.
- cp-algorithms.com: "String hashing" (polynomial hash, collisions, choice of base and modulus) and "Rabin-Karp algorithm".
- Codeforces blog: "Anti-hash test" and "Anti-hash tests for unsigned 64-bit overflow" (the Thue-Morse construction), to see how fixed hashes get broken.
- CLRS, "Hash tables" chapter (direct-address tables, chaining, open addressing, universal hashing).
- CSES Problem Set (Sorting and Searching) and LeetCode's hash table problems. Practise the problems listed in `external.toml`.
