# Chapter 15: Python data model essentials

In chapter 14 you built your own classes. They worked, but they felt a little foreign. A `Tank` object printed as `<__main__.Tank object at 0x...>`. You could not add two of them with `+`, compare them with `==`, sort them, take their `len()`, loop over them, or use them in a `with` block. Meanwhile a `list`, a `str` and a `dict` do all of these things without any fuss.

The reason is not magic. Python has a set of **special method names**, each written with two underscores on both sides, like `__len__` and `__add__`. They are called **dunder methods** ("double underscore"). The built-in types define them. When you define the same names in your own class, your objects start to behave like the built-ins. This set of hooks is called the **Python data model**.

This chapter teaches the most useful part of it:

- **Showing objects** (sections 2 and 3): `__repr__`, `__str__`, `__format__`.
- **Equality, hashing and ordering** (sections 4 to 7): `__eq__`, `__hash__`, `__lt__` and friends, `functools.total_ordering`.
- **Operators** (sections 8 to 11): `+`, `*`, `-x`, `abs()`, reflected operators like `__radd__`, and in-place operators like `__iadd__`.
- **Containers** (sections 12 to 16): `len()`, `[]`, `in`, `for`, truth testing, and the `collections.abc` helpers.
- **Callable objects and class-based decorators** (sections 17 to 19).
- **Context managers** (sections 20 to 23): `with`, `__enter__`, `__exit__`, and `contextlib`.
- **Dataclasses and enums** (sections 24 to 27): less code for classes that mostly hold data.
- **`__slots__`** (section 28): memory and speed.
- **The project** (section 29): a small Vector and Matrix library.

By the end you reach the three outcomes of the module:

- You can make a custom class behave like a **built-in container**.
- You can **explain why defining `__eq__` removes `__hash__`**.
- You can **write a context manager** as a class and with `contextlib`.

**A note on how examples are shown.** As in earlier chapters, every block of code is followed by the exact output of really running it with **Python 3.14** on Linux. When a value is **machine-specific** (a memory address, for example) the text says so. Tracebacks are shortened: the `File "...", line N` lines are replaced by `...` so you can focus on the error itself.

**How to read this chapter.** Type the examples and run them. Every few sections there is a **Try it** exercise. Decide on an answer, or write the code, *before* you open the answer. Being wrong is useful: it shows you which rule you have not understood yet.

## Table of contents

1. [What the data model is](#1-what-the-data-model-is)
2. [`__repr__` and `__str__`](#2-__repr__-and-__str__)
3. [`__format__` and format specs](#3-__format__-and-format-specs)
4. [Equality with `__eq__`](#4-equality-with-__eq__)
5. [Hashing with `__hash__`](#5-hashing-with-__hash__)
6. [Why defining `__eq__` removes `__hash__`](#6-why-defining-__eq__-removes-__hash__)
7. [Ordering and `total_ordering`](#7-ordering-and-total_ordering)
8. [Arithmetic operators](#8-arithmetic-operators)
9. [Reflected operators](#9-reflected-operators)
10. [In-place operators](#10-in-place-operators)
11. [Unary operators, `abs`, `bool`](#11-unary-operators-abs-bool)
12. [`__len__` and `__getitem__`](#12-__len__-and-__getitem__)
13. [Slices, `__setitem__`, `__delitem__`, `__contains__`](#13-slices-__setitem__-__delitem__-__contains__)
14. [Iteration: iterable vs iterator](#14-iteration-iterable-vs-iterator)
15. [Truth testing and the old sequence protocol](#15-truth-testing-and-the-old-sequence-protocol)
16. [`collections.abc`: getting methods for free](#16-collectionsabc-getting-methods-for-free)
17. [`__call__`: callable objects](#17-__call__-callable-objects)
18. [Class-based decorators](#18-class-based-decorators)
19. [Decorating classes](#19-decorating-classes)
20. [The context manager protocol](#20-the-context-manager-protocol)
21. [Exceptions inside `with`](#21-exceptions-inside-with)
22. [`contextlib.contextmanager`](#22-contextlibcontextmanager)
23. [More `contextlib`: `suppress`, `redirect_stdout`, `ExitStack`](#23-more-contextlib-suppress-redirect_stdout-exitstack)
24. [Dataclasses: the basics](#24-dataclasses-the-basics)
25. [Dataclasses in depth](#25-dataclasses-in-depth)
26. [Enums](#26-enums)
27. [`IntEnum` and `Flag`](#27-intenum-and-flag)
28. [`__slots__` and memory](#28-__slots__-and-memory)
29. [Project: a Vector and Matrix library](#29-project-a-vector-and-matrix-library)
30. [Common traps](#30-common-traps)
31. [Summary](#31-summary)

## 1. What the data model is

### 1.1 Syntax is a request to an object

When you write `len(x)`, Python does not know how to count anything. It asks the object `x`: "please tell me your length." The object answers by running its `__len__` method. The same idea holds all over the language:

| You write | Python really calls |
|---|---|
| `len(x)` | `type(x).__len__(x)` |
| `x[i]` | `type(x).__getitem__(x, i)` |
| `x + y` | `type(x).__add__(x, y)` |
| `x == y` | `type(x).__eq__(x, y)` |
| `repr(x)` | `type(x).__repr__(x)` |
| `for a in x:` | `type(x).__iter__(x)` |
| `with x:` | `type(x).__enter__(x)` and later `type(x).__exit__(...)` |
| `x(1, 2)` | `type(x).__call__(x, 1, 2)` |

You can see this directly:

```python
class Box:
    def __len__(self):
        return 42

b = Box()
print(len(b))
print(b.__len__())
print(type(b).__len__(b))
```
```text
42
42
42
```

All three lines give the same answer, because `len(b)` is just a polite way to ask for `b.__len__()`. You almost never call a dunder method by hand. You define it, and Python calls it for you.

### 1.2 Why Python is designed this way

Many languages give special objects (arrays, strings) special syntax, and your own objects are second-class. Python takes another road: **the syntax belongs to everyone**. A class written by you can be indexed, added, looped over and used in `with`, exactly like a built-in, if it defines the right methods. That is why libraries such as NumPy, pandas and pathlib feel natural: `Path("a") / "b"` and `array1 + array2` are just `__truediv__` and `__add__`.

### 1.3 Rules to remember

- **Dunder methods are looked up on the type, not on the instance.** `len(x)` finds `__len__` on `type(x)`. If you store a function named `__len__` in one instance's `__dict__`, `len()` ignores it.
- **You call the public function, not the dunder.** Write `len(x)`, not `x.__len__()`.
- **Do not invent your own dunder names.** Names like `__foo__` are reserved for Python. Use ordinary names for your own methods.
- **Only define what makes sense.** A `Money` class can be added, but adding two `Person` objects is meaningless. Leave `__add__` out, and Python will tell the user clearly that `+` is not supported.

Here is the first point in action:

```python
class Thing:
    def __len__(self):
        return 1

t = Thing()
t.__len__ = lambda: 99
print(len(t))
print(t.__len__())
```
```text
1
99
```

`len(t)` ignored the instance attribute, because it looks on the class. This is the reason the dunder methods must be written in the `class` body.

### Try it 1.1

A class `Bag` has `__len__` returning `3`. What does `bool(Bag())` give, and why? (Hint: section 15 explains it in full, but think about what Python can do when no `__bool__` exists.)

<details><summary>Answer</summary>

```python
class Bag:
    def __len__(self):
        return 3

print(bool(Bag()))
```
```text
True
```

It prints `True`. With no `__bool__`, Python falls back to `__len__`, and a non-zero length means true.

</details>

## 2. `__repr__` and `__str__`

### 2.1 Two ways to turn an object into text

An object can be shown as text in two ways, for two different readers:

- `repr(x)` is for **developers**. It should be exact and unambiguous. If possible, it looks like the code that would build the object. It is what you see in the interactive prompt, in tracebacks, in debuggers, and inside lists.
- `str(x)` is for **users**. It should be readable and friendly. It is what `print(x)` and f-strings use.

Built-in types already follow this idea:

```python
from datetime import date

d = date(2025, 3, 9)
print(str(d))
print(repr(d))
s = "hi\n"
print(str(s))
print(repr(s))
```
```text
2025-03-09
datetime.date(2025, 3, 9)
hi

'hi\n'
```

The `str` of a string is the string itself. Its `repr` has quotes and shows the newline as `\n`, so you can see exactly what it holds.

### 2.2 The default is not helpful

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

p = Point(3, 4)
print(repr(p).split(" at ")[0])
print(str(p).split(" at ")[0])
```
```text
<__main__.Point object
<__main__.Point object
```

The default shows the class name and (after `at`) a memory address, which I cut off here because it is machine-specific. It tells you nothing about the data. A good `__repr__` is the first thing to add to almost every class.

### 2.3 Writing `__repr__`

The rule of thumb: make `repr(obj)` look like a valid expression that rebuilds the object, when that is easy.

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Point({self.x!r}, {self.y!r})"

p = Point(3, 4)
print(repr(p))
print(p)
print([p, Point("a", None)])
```
```text
Point(3, 4)
Point(3, 4)
[Point(3, 4), Point('a', None)]
```

Three things to notice:

1. `!r` inside an f-string means "use `repr()` of this value". So strings get quotes: `Point('a', None)`. That keeps the representation honest.
2. `print(p)` used `__repr__` too. We did not define `__str__`, and **`str()` falls back to `__repr__`** (the reverse is not true).
3. Inside the list, Python used `repr` on each element. Containers always show their items with `repr`.

A more careful `__repr__` uses the real class name, so subclasses show correctly:

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"{type(self).__name__}({self.x!r}, {self.y!r})"

class Point3(Point):
    pass

print(Point3(1, 2))
```
```text
Point3(1, 2)
```

### 2.4 Writing `__str__`

Add `__str__` only when the friendly text should differ from the exact one.

```python
class Money:
    def __init__(self, cents):
        self.cents = cents

    def __repr__(self):
        return f"Money({self.cents})"

    def __str__(self):
        return f"${self.cents // 100}.{self.cents % 100:02d}"

m = Money(1999)
print(m)
print(repr(m))
print(f"price: {m}")
print(f"debug: {m!r}")
print(str([m, m]))
```
```text
$19.99
Money(1999)
price: $19.99
debug: Money(1999)
[Money(1999), Money(1999)]
```

Look at the last line: `str()` of a *list* still uses `repr` for its items, so we see `Money(1999)`, not `$19.99`. That surprises many people. A list has no idea what a friendly form of its items should be, so it picks the exact one.

### 2.5.1 The round-trip test

When the `repr` is meant to rebuild the object, test it with `eval`. (Only do this in your own tests with your own data. Never `eval` text from outside.)

```python
class Money:
    def __init__(self, cents):
        self.cents = cents

    def __repr__(self):
        return f"Money({self.cents})"

    def __eq__(self, other):
        return isinstance(other, Money) and self.cents == other.cents

m = Money(250)
print(eval(repr(m)) == m)
```
```text
True
```

This round trip is a very good check that your `__repr__` and `__eq__` agree.

## 3. `__format__` and format specs

### 3.1 What is inside the braces

You know `f"{value:>8.2f}"`. The part after the colon, `>8.2f`, is a **format spec**. Python hands it to the object by calling `format(value, ">8.2f")`, which calls `type(value).__format__(value, ">8.2f")`.

```python
import datetime

d = datetime.date(2025, 3, 9)
print(f"{d}")
print(f"{d:%d/%m/%Y}")
print(f"{d:%A, %B %d}")
print(format(3.14159, ".2f"), format(255, "x"), format(42, "08b"))
```
```text
2025-03-09
09/03/2025
Sunday, March 09
3.14 ff 00101010
```

Each type decides what its own spec language means. `date` uses `strftime` codes. Numbers use the mini-language you know.

### 3.3 Writing `__format__`

A simple pattern: look at the spec, handle your own special cases, and pass everything else to something that already works.

```python
class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    def __repr__(self):
        return f"Temperature({self.celsius!r})"

    def __format__(self, spec):
        if spec.endswith("F"):
            value = self.celsius * 9 / 5 + 32
            return format(value, spec[:-1] + "f") + " F"
        if spec.endswith("C"):
            return format(self.celsius, spec[:-1] + "f") + " C"
        return format(self.celsius, spec)

t = Temperature(21.5)
print(f"{t:.1F}")
print(f"{t:.0C}")
print(f"{t:8.2f}|")
print(f"{t}")
```
```text
70.7 F
22 C
   21.50|
21.5
```

Here the unit letters `F` and `C` are our own invention. Anything else is passed to `format(float, spec)`. The empty spec `f"{t}"` becomes `format(21.5, "")`, which is `'21.5'`.

## 4. Equality with `__eq__`

### 4.1 The default: identity

By default two objects are equal only if they are the **same object**.

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

a = Point(1, 2)
b = Point(1, 2)
print(a == b)
print(a == a)
print(a is b)
```
```text
False
True
False
```

Two points with equal coordinates are not equal, because the default `__eq__` is the same as `is`. For a **value object** (point, money, date) this is wrong. We want equal data to mean equal objects.

### 4.2 Writing `__eq__`

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

a = Point(1, 2)
b = Point(1, 2)
print(a == b)
print(a != b)
print(a == 5)
```
```text
True
False
Traceback (most recent call last):
  ...
AttributeError: 'int' object has no attribute 'x'
```

Two lessons. First, **`!=` comes free**: unless you define `__ne__`, it just negates `__eq__`. Second, the last line crashed: our `__eq__` assumed `other` has `.x`. Comparing with the number 5 should simply say "not equal", not crash.

### 4.3 `NotImplemented`: "I do not know this type"

The correct tool is the special value `NotImplemented`. It means "I cannot answer for this kind of operand; ask someone else."

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if not isinstance(other, Point):
            return NotImplemented
        return (self.x, self.y) == (other.x, other.y)

print(Point(1, 2) == Point(1, 2))
print(Point(1, 2) == 5)
print(Point(1, 2) != 5)
print(Point(1, 2) == (1, 2))
```
```text
True
False
True
False
```

Why does `Point(1, 2) == 5` print `False` and not something odd? Python's rule for `a == b`:

1. Call `a.__eq__(b)`. If the result is not `NotImplemented`, use it.
2. Otherwise call the **reflected** version, `b.__eq__(a)`. If it answers, use that.
3. If both gave `NotImplemented`, fall back to **identity** (`a is b`), which is `False` here.

So `NotImplemented` is not an error. It is a polite "pass". The other side gets a chance. That is what makes two different classes able to cooperate.

### 4.4 `NotImplemented` is not `False`

It is tempting to write `return False` for unknown types. That works in simple cases, but it blocks the other side from answering.

```python
class Meters:
    def __init__(self, v):
        self.v = v

    def __eq__(self, other):
        if not isinstance(other, Meters):
            return False
        return self.v == other.v

class AnyNumber:
    def __eq__(self, other):
        return True

print(Meters(5) == AnyNumber())
print(AnyNumber() == Meters(5))
```
```text
False
True
```

The first line is `False` even though `AnyNumber` claims to equal everything, because `Meters` said a firm `False` and the other side never got asked. Change `return False` to `return NotImplemented` and the first line becomes `True`. The comparison is now symmetric.

**Rule: return `NotImplemented` when `other` is a type you do not handle. Return `True`/`False` only when you really decided.**

Never `return NotImplemented` and then *use* it as a value. `bool(NotImplemented)` is deprecated and raises a `TypeError` in recent Python versions when you test it in an `if`:

```python
try:
    if NotImplemented:
        print("truthy")
except TypeError as e:
    print("TypeError:", e)
```
```text
TypeError: NotImplemented should not be used in a boolean context
```

### Try it 4.1

Predict `Card(1, "H") == "1H"` when `__eq__` returns `NotImplemented` for non-cards, and then `Card(1, "H") != Card(2, "H")`.

<details><summary>Answer</summary>

```python
class Card:
    def __init__(self, rank, suit):
        self.rank, self.suit = rank, suit

    def __eq__(self, other):
        if not isinstance(other, Card):
            return NotImplemented
        return (self.rank, self.suit) == (other.rank, other.suit)

print(Card(1, "H") == "1H", Card(1, "H") != Card(2, "H"))
```
```text
False True
```

Both sides pass on the string comparison, so identity decides: `False`. `!=` is derived from `__eq__`.

</details>

## 5. Hashing with `__hash__`

### 5.1 What a hash is for

Sets and dict keys must find an item **fast**, without comparing it with every other item. They use a **hash**: an integer computed from the object. Roughly, the dict uses `hash(key)` to jump to a small "bucket" and only then compares keys with `==` inside that bucket.

```python
print(hash(42), hash("a") == hash("a"), hash((1, 2)) == hash((1, 2)))
print(hash(1) == hash(1.0) == hash(True))
```
```text
42 True True
True
```

`1`, `1.0` and `True` are equal, and they have the same hash. That is not an accident. It is the central rule of hashing.

### 5.2 The contract

> If `a == b`, then `hash(a) == hash(b)`.

The reverse need not hold: different objects may share a hash (a "collision"), and the dict then falls back on `==`. But **equal objects must always have equal hashes**. If they did not, a set might look in the wrong bucket and miss an object that is really in it.

### 5.5 Writing `__hash__`

When you define value-based `__eq__`, you must define a matching `__hash__`. The standard recipe is to hash a **tuple of exactly the fields used in `__eq__`**.

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        if not isinstance(other, Point):
            return NotImplemented
        return (self.x, self.y) == (other.x, other.y)

    def __hash__(self):
        return hash((self.x, self.y))

seen = {Point(1, 2), Point(1, 2), Point(3, 4)}
print(len(seen))
print(Point(3, 4) in seen)
visits = {Point(0, 0): "start"}
print(visits[Point(0, 0)])
```
```text
2
True
start
```

Two separate `Point(1, 2)` objects collapsed into one set member, and a brand-new `Point(0, 0)` finds the dict entry. This is value semantics: the set cares about what the point *is*, not which object it is.

### 5.6 Hashing a key, not the object

Suppose a case-insensitive tag compares with `casefold()`. The hash must use the same thing. (A key function like this is a common way to define equality.)

```python
class Tag:
    def __init__(self, text):
        self.text = text

    def __eq__(self, other):
        if not isinstance(other, Tag):
            return NotImplemented
        return self.text.casefold() == other.text.casefold()

    def __hash__(self):
        return hash(self.text.casefold())

counts = {}
for word in ["Python", "PYTHON", "python", "Java"]:
    key = Tag(word)
    counts[key] = counts.get(key, 0) + 1
print(len(counts), counts[Tag("pYtHoN")])
```
```text
2 3
```

If the hash had used `self.text` directly, `Tag("Python")` and `Tag("PYTHON")` would be equal but land in different buckets, and the count would be wrong. That is breaking the contract.

## 6. Why defining `__eq__` removes `__hash__`

### 6.1 What Python does

Here is the surprising behaviour in one example:

```python
class A:
    pass

class B:
    def __eq__(self, other):
        return True

print(A.__hash__ is None)
print(B.__hash__ is None)
try:
    hash(B())
except TypeError as e:
    print("TypeError:", e)
try:
    {B()}
except TypeError as e:
    print("TypeError:", e)
```
```text
False
True
TypeError: unhashable type: 'B'
TypeError: cannot use 'B' as a set element (unhashable type: 'B')
```

`A` has the default identity hash. `B` defined `__eq__` and did not define `__hash__`, so Python sets `B.__hash__ = None`. The instances become **unhashable**: they cannot be set members or dict keys.

### 6.2 Why

Python cannot guess how to hash your objects. Suppose it kept the old identity-based hash while you changed `__eq__` to compare values. Then two *equal* `Point(1, 2)` objects would have *different* hashes (their addresses). The contract "equal objects have equal hashes" would be broken silently, and dicts and sets would behave wrongly, with no error to warn you.

So Python chooses the safe path: **when you take over equality, you lose the hash until you provide one that matches.** An error now ("unhashable type") is much better than wrong lookups later.

### 6.3 Your three options

1. **Value-hashable** (immutable value object): define both, hash the same fields.
2. **Unhashable** (mutable object): define only `__eq__`. That is the right choice for classes whose fields change, like a mutable list-like class. The `list` class does exactly this.
3. **Keep the identity hash on purpose**: `__hash__ = object.__hash__`. Rarely right, since it breaks the contract; only use it if you know the objects will never be equal-but-different.

Only an explicit `__hash__` in the same class body restores hashing. The reverse also holds: if you define `__hash__` only, `__eq__` stays identity, and nothing breaks.

### 6.4 The mutable-hash trap

What if the fields used in `__hash__` change after the object is stored in a set?

```python
class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return isinstance(other, Point) and (self.x, self.y) == (other.x, other.y)

    def __hash__(self):
        return hash((self.x, self.y))

p = Point(1, 2)
s = {p}
print(p in s)
p.x = 99
print(p in s)
print(len(s), any(item is p for item in s))
print(Point(99, 2) in s)
```
```text
True
False
1 True
False
```

After mutation the object is **still in the set**, as the `any(...)` line proves, but `p in s` is `False`. The set stored `p` under the old hash bucket. The new hash points to a different bucket, where nothing lives. Even `Point(99, 2)` fails, because its hash matches the new value but the stored entry lives in the old bucket. The object is lost: you cannot find it, nor remove it normally.

The fix is to design value objects as **immutable**. Make fields read-only (properties without setters, `frozen=True` in dataclasses, or `__slots__` plus discipline) so that nothing used in the hash can change. If you need a mutable object, do not hash it.

## 7. Ordering and `total_ordering`

### 7.1 The six comparison methods

| Operator | Method |
|---|---|
| `a < b` | `__lt__` |
| `a <= b` | `__le__` |
| `a > b` | `__gt__` |
| `a >= b` | `__ge__` |
| `a == b` | `__eq__` |
| `a != b` | `__ne__` (derived from `__eq__`) |

These are the **rich comparisons**. `sorted()`, `list.sort()`, `min()`, `max()` and `heapq` all need only `__lt__`. The others are for the operators you write yourself.

### 7.2 `__lt__` and sorting

```python
class Version:
    def __init__(self, major, minor):
        self.major = major
        self.minor = minor

    def __repr__(self):
        return f"Version({self.major}, {self.minor})"

    def __lt__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return (self.major, self.minor) < (other.major, other.minor)

vs = [Version(1, 10), Version(1, 2), Version(0, 9)]
print(sorted(vs))
print(min(vs), max(vs))
print(Version(1, 2) < Version(1, 10))
```
```text
[Version(0, 9), Version(1, 2), Version(1, 10)]
Version(0, 9) Version(1, 10)
True
```

The trick in the body is tuple comparison: Python compares tuples item by item. This gives an easy, correct order for many keys.

### 7.3 `functools.total_ordering`

Writing four methods is boring and error-prone. Define `__eq__` and **one** of `__lt__`, `__le__`, `__gt__`, `__ge__`, then decorate the class:

```python
from functools import total_ordering

@total_ordering
class Card:
    ORDER = "23456789TJQKA"

    def __init__(self, rank):
        self.rank = rank

    def _value(self):
        return Card.ORDER.index(self.rank)

    def __repr__(self):
        return f"Card({self.rank!r})"

    def __eq__(self, other):
        if not isinstance(other, Card):
            return NotImplemented
        return self.rank == other.rank

    def __lt__(self, other):
        if not isinstance(other, Card):
            return NotImplemented
        return self._value() < other._value()

print(Card("K") > Card("9"))
print(Card("2") <= Card("2"))
print(Card("A") >= Card("K"))
print(sorted([Card("Q"), Card("3"), Card("A")]))
```
```text
True
True
True
[Card('3'), Card('Q'), Card('A')]
```

The decorator generated `__le__`, `__gt__` and `__ge__` from `__eq__` and `__lt__`. This is a **class decorator** (section 19 explains how they work).

Notes:

- Do not forget `__eq__`. `total_ordering` needs both pieces: ordering plus equality.
- It is a little **slower** than hand-written methods, because each generated method calls two others. For hot loops, write all six.
- If `__eq__` is defined, remember `__hash__` too (section 6) when the card is a value object.

### Try it 7.1

Write `Version` with `__eq__` and `__lt__` from a string like `"1.10.2"` (split by dots into ints), decorated with `total_ordering`. Predict `Version("1.10") > Version("1.9")`.

<details><summary>Answer</summary>

```python
from functools import total_ordering

@total_ordering
class Version:
    def __init__(self, text):
        self.parts = tuple(int(p) for p in text.split("."))

    def __eq__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return self.parts == other.parts

    def __lt__(self, other):
        if not isinstance(other, Version):
            return NotImplemented
        return self.parts < other.parts

print(Version("1.10") > Version("1.9"))
print(Version("1.2") <= Version("1.2.0"))
```
```text
True
True
```

Comparing integers, not strings, makes `1.10` bigger than `1.9`. As strings, `"1.10" < "1.9"` would wrongly be true. Tuples of different length compare by prefix first, so `(1, 2) < (1, 2, 0)`, and the `<=` line is true even though the two are not `==`.

</details>

## 8. Arithmetic operators

### 8.1 The idea

Every arithmetic operator has a method name:

| Operator | Method | Operator | Method |
|---|---|---|---|
| `a + b` | `__add__` | `a // b` | `__floordiv__` |
| `a - b` | `__sub__` | `a % b` | `__mod__` |
| `a * b` | `__mul__` | `a ** b` | `__pow__` |
| `a / b` | `__truediv__` | `a @ b` | `__matmul__` |

`a + b` calls `a.__add__(b)`. The method should return a **new object** and leave `a` and `b` alone. That is what the built-in immutable types do (`"a" + "b"` makes a new string).

### 8.2 A first class: 2D vectors

```python
class Vec:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Vec({self.x!r}, {self.y!r})"

    def __eq__(self, other):
        if not isinstance(other, Vec):
            return NotImplemented
        return (self.x, self.y) == (other.x, other.y)

    def __add__(self, other):
        if not isinstance(other, Vec):
            return NotImplemented
        return Vec(self.x + other.x, self.y + other.y)

    def __sub__(self, other):
        if not isinstance(other, Vec):
            return NotImplemented
        return Vec(self.x - other.x, self.y - other.y)

a = Vec(1, 2)
b = Vec(10, 20)
print(a + b)
print(b - a)
print(a)
print(a + b == Vec(11, 22))
```
```text
Vec(11, 22)
Vec(9, 18)
Vec(1, 2)
True
```

The originals did not change: `a` is still `Vec(1, 2)`.

### 8.3 Return `NotImplemented` for unknown types

Again, the check `isinstance(other, Vec)` followed by `return NotImplemented` is important. Without it, `Vec(1, 2) + 5` fails with a confusing `AttributeError` deep inside our method. With it, Python reports the standard message:

```python
class Vec:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __add__(self, other):
        if not isinstance(other, Vec):
            return NotImplemented
        return Vec(self.x + other.x, self.y + other.y)

try:
    Vec(1, 2) + 5
except TypeError as e:
    print("TypeError:", e)
```
```text
TypeError: unsupported operand type(s) for +: 'Vec' and 'int'
```

Do **not** raise the `TypeError` yourself. Returning `NotImplemented` lets Python try the other operand's reflected method first (next section), and only then raise the error.

### 8.4 Scalar multiplication

A vector times a number should scale it. We accept ints and floats, but not other vectors (the meaning would be unclear: dot product? element-wise?).

```python
from numbers import Number

class Vec:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Vec({self.x!r}, {self.y!r})"

    def __mul__(self, k):
        if not isinstance(k, Number):
            return NotImplemented
        return Vec(self.x * k, self.y * k)

    def __truediv__(self, k):
        if not isinstance(k, Number):
            return NotImplemented
        return Vec(self.x / k, self.y / k)

v = Vec(3, 4)
print(v * 2)
print(v * 0.5)
print(v / 2)
```
```text
Vec(6, 8)
Vec(1.5, 2.0)
Vec(1.5, 2.0)
```

`numbers.Number` is a base class that `int`, `float`, `complex`, `Fraction` and `Decimal` all belong to. It is handy for "any kind of number". Notice `v * 2` works, but `2 * v` will not yet. That needs the reflected method.

## 9. Reflected operators

### 9.1 The problem: the left operand does not know us

`2 * v` starts with `int.__mul__(2, v)`. The `int` class does not know our `Vec`, so it returns `NotImplemented`. Python then tries the **reflected** method on the right operand: `v.__rmul__(2)`.

For each binary operator `__op__` there is a reflected `__rop__`: `__radd__`, `__rsub__`, `__rmul__`, `__rtruediv__`, and so on. The reflected method is called **with the operands in their written order flipped**: `self` is the right operand, `other` is the left one.

```python
class Vec:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Vec({self.x!r}, {self.y!r})"

    def __mul__(self, k):
        return Vec(self.x * k, self.y * k)

    def __rmul__(self, k):
        print("__rmul__ called")
        return self * k

v = Vec(1, 2)
print(v * 3)
print(3 * v)
```
```text
Vec(3, 6)
__rmul__ called
Vec(3, 6)
```

For a commutative operation like scalar multiplication, `__rmul__` can simply reuse `__mul__`.

### 9.3 `sum()` needs `__radd__`

`sum([a, b, c])` starts with the integer `0` and computes `0 + a`, then `+ b`, and so on. So the first addition is `int + Vec`, which needs `Vec.__radd__`.

```python
class Vec:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Vec({self.x}, {self.y})"

    def __add__(self, other):
        if not isinstance(other, Vec):
            return NotImplemented
        return Vec(self.x + other.x, self.y + other.y)

vs = [Vec(1, 1), Vec(2, 2), Vec(3, 3)]
try:
    print(sum(vs))
except TypeError as e:
    print("TypeError:", e)
```
```text
TypeError: unsupported operand type(s) for +: 'int' and 'Vec'
```

Two ways to fix it. One is to give `sum` a proper start value: `sum(vs, Vec(0, 0))`. The other is to let `Vec` accept `0` as "nothing":

```python
class Vec:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Vec({self.x}, {self.y})"

    def __add__(self, other):
        if not isinstance(other, Vec):
            return NotImplemented
        return Vec(self.x + other.x, self.y + other.y)

    def __radd__(self, other):
        if other == 0:
            return self
        return NotImplemented

vs = [Vec(1, 1), Vec(2, 2), Vec(3, 3)]
print(sum(vs))
print(sum(vs, Vec(10, 10)))
print(sum([]))
```
```text
Vec(6, 6)
Vec(16, 16)
0
```

The special case `other == 0` exists only to support `sum`. The empty sum is `0`, an `int`, not a `Vec`. That is a known wart, and the explicit start value `sum(vs, Vec(0, 0))` avoids it.

### 9.4 The full dispatch rule

For `a + b`, Python does the following:

1. If `type(b)` is a **proper subclass** of `type(a)` and overrides `__radd__`, try `b.__radd__(a)` **first**.
2. Otherwise try `a.__add__(b)`.
3. If that returns `NotImplemented` (or `a` has no `__add__`), try `b.__radd__(a)`, provided the types differ.
4. If everything returned `NotImplemented`, raise `TypeError`.

Rule 1 lets a subclass override the behaviour of its parent, even when the parent is on the left. Here it is in action:

```python
class Base:
    def __add__(self, other):
        return "Base.__add__"

    def __radd__(self, other):
        return "Base.__radd__"

class Sub(Base):
    def __add__(self, other):
        return "Sub.__add__"

    def __radd__(self, other):
        return "Sub.__radd__"

class Other:
    pass

print(Base() + Sub())
print(Sub() + Base())
print(Base() + Base())
print(Other() + Base())
print(Base() + Other())
```
```text
Sub.__radd__
Sub.__add__
Base.__add__
Base.__radd__
Base.__add__
```

Read each line:

- `Base() + Sub()`: `Sub` is a subclass of `Base` and overrides `__radd__`, so **`Sub.__radd__` goes first**.
- `Sub() + Base()`: left first, `Sub.__add__`.
- `Base() + Base()`: same types, only `__add__`.
- `Other() + Base()`: `Other` has no `__add__`, so `Base.__radd__` runs.
- `Base() + Other()`: `Base.__add__` answers, nobody else needs to.

### Try it 9.1

If `__sub__` returns `"sub"` and `__rsub__` returns `"rsub"`, what do `3 - N()`, `N() - 3` and `N() - N()` give?

<details><summary>Answer</summary>

```python
class N:
    def __sub__(self, other):
        return "sub"

    def __rsub__(self, other):
        return "rsub"

print(3 - N(), N() - 3, N() - N())
```
```text
rsub sub sub
```

`int` cannot handle `N`, so `rsub` runs. Two operands of the same type only try `__sub__`.

</details>

## 10. In-place operators

### 10.1 `+=` is not always `+`

`a += b` is **augmented assignment**. Python first looks for `__iadd__`. If it exists, it is called and **its return value is assigned back to `a`**. If it does not exist, Python falls back to `a = a + b` using `__add__`.

The point of `__iadd__` is to **change the object in place**. For mutable objects (lists), this is faster and, more importantly, other names that refer to the same object see the change.

```python
a = [1, 2]
b = a
a += [3]
print(a, b, a is b)

x = (1, 2)
y = x
x += (3,)
print(x, y, x is y)
```
```text
[1, 2, 3] [1, 2, 3] True
(1, 2, 3) (1, 2) False
```

For a list, `+=` calls `list.__iadd__`, which extends the list in place, so `b` sees the change and `a is b` is still true. For a tuple, there is no `__iadd__`. Python builds a new tuple and rebinds `x`, so `y` is untouched.

### 10.2 Writing `__iadd__`

The method must **return `self`** (or whatever object should become the new value). Forgetting to return is a very common bug, because then `a += b` makes `a` equal to `None`.

```python
class Basket:
    def __init__(self, items=None):
        self.items = list(items or [])

    def __repr__(self):
        return f"Basket({self.items!r})"

    def __add__(self, other):
        if not isinstance(other, Basket):
            return NotImplemented
        return Basket(self.items + other.items)

    def __iadd__(self, other):
        if not isinstance(other, Basket):
            return NotImplemented
        self.items.extend(other.items)
        return self

a = Basket([1])
alias = a
a += Basket([2, 3])
print(a, alias, a is alias)

c = Basket([1])
alias2 = c
c = c + Basket([9])
print(c, alias2, c is alias2)
```
```text
Basket([1, 2, 3]) Basket([1, 2, 3]) True
Basket([1, 9]) Basket([1]) False
```

With `+=`, `alias` sees the change because the same object was changed. With `c = c + ...`, a new object is made, and `alias2` keeps the old content.

### 10.4 When to define in-place operators

- **Mutable** types usually define them (`list`, `set`, `dict |=`).
- **Immutable** value types (numbers, strings, tuples, a frozen `Money`) should **not**. Without `__iadd__`, `+=` falls back to `__add__`, which is exactly what you want.

Aliasing is the thing to understand. A well-known trap is a list inside a tuple:

```python
t = ([1], 2)
try:
    t[0] += [5]
except TypeError as e:
    print("TypeError:", e)
print(t)
```
```text
TypeError: 'tuple' object does not support item assignment
([1, 5], 2)
```

This is subtle. `t[0] += [5]` first runs `t[0].__iadd__([5])`, which really extends the list, and **then** tries to store the result back into `t[0]`, which fails because tuples do not allow item assignment. So you get the error **and** the change. Section 30 lists this among the traps.

## 11. Unary operators, `abs`, `bool`

### 11.1 Unary methods

| Expression | Method |
|---|---|
| `-x` | `__neg__` |
| `+x` | `__pos__` |
| `~x` | `__invert__` |
| `abs(x)` | `__abs__` |
| `bool(x)` | `__bool__` |
| `int(x)`, `float(x)` | `__int__`, `__float__` |
| `round(x)` | `__round__` |

```python
import math

class Vec:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Vec({self.x}, {self.y})"

    def __neg__(self):
        return Vec(-self.x, -self.y)

    def __pos__(self):
        return Vec(self.x, self.y)

    def __abs__(self):
        return math.hypot(self.x, self.y)

    def __bool__(self):
        return bool(self.x or self.y)

v = Vec(3, 4)
print(-v)
print(+v)
print(abs(v))
print(bool(Vec(0, 0)), bool(v))
```
```text
Vec(-3, -4)
Vec(3, 4)
5.0
False True
```

`abs()` of a vector is its **length**, so it returns a number, not a `Vec`. That is allowed: the unary methods can return any type.

## 12. `__len__` and `__getitem__`

### 12.1 What makes something a container

The container protocols are small. The core pair:

- `__len__(self)` gives `len(obj)`.
- `__getitem__(self, key)` gives `obj[key]`.

With just these two, your class can act like a read-only sequence. Here is a deck of cards:

```python
class Deck:
    RANKS = "A23456789TJQK"
    SUITS = "SHDC"

    def __init__(self):
        self.cards = [r + s for s in self.SUITS for r in self.RANKS]

    def __len__(self):
        return len(self.cards)

    def __getitem__(self, index):
        return self.cards[index]

d = Deck()
print(len(d))
print(d[0], d[-1], d[13])
print(d[:3])
```
```text
52
AS KC AH
['AS', '2S', '3S']
```

We delegated `__getitem__` to the inner list, so negative indexes and even **slices** work. Indexing with `d[:3]` passes a `slice` object to our method, and the inner list knows what to do with it (section 13).

### Try it 12.1

Write `Countdown(n)` with `__len__` returning `n` and `__getitem__(i)` returning `n - i` (`IndexError` when `i` is out of range). Predict `list(Countdown(3))` and `3 in Countdown(5)`.

<details><summary>Answer</summary>

```python
class Countdown:
    def __init__(self, n):
        self.n = n

    def __len__(self):
        return self.n

    def __getitem__(self, i):
        if not 0 <= i < self.n:
            raise IndexError(i)
        return self.n - i

print(list(Countdown(3)), 3 in Countdown(5))
```
```text
[3, 2, 1] True
```

`list` and `in` ask for index 0, 1, 2, ... until `IndexError` tells them to stop.

</details>

## 13. Slices, `__setitem__`, `__delitem__`, `__contains__`

### 13.1 What a slice looks like to your method

`obj[1:4]` calls `__getitem__(slice(1, 4, None))`. You can ask the slice object for its three parts, or pass it to a list.

```python
class Show:
    def __getitem__(self, key):
        return key

s = Show()
print(s[3])
print(s[1:4])
print(s[::2])
print(s[1:4, 0])
print(slice(1, 10, 2).indices(5))
```
```text
3
slice(1, 4, None)
slice(None, None, 2)
(slice(1, 4, None), 0)
(1, 5, 2)
```

`key.indices(length)` turns any slice into three concrete numbers (start, stop, step) that fit a sequence of that length. It handles negatives and `None` for you.

### 13.2 Slices that return the same type

If we simply delegate, `d[:3]` returns a plain `list`. Often we want the slice of a `Playlist` to be a `Playlist`. Check the key type:

```python
class Playlist:
    def __init__(self, songs):
        self._songs = list(songs)

    def __repr__(self):
        return f"Playlist({self._songs!r})"

    def __len__(self):
        return len(self._songs)

    def __getitem__(self, key):
        if isinstance(key, slice):
            return Playlist(self._songs[key])
        return self._songs[key]

p = Playlist(["a", "b", "c", "d", "e"])
print(p[1])
print(p[1:3])
print(p[::-1])
print(type(p[:2]).__name__)
```
```text
b
Playlist(['b', 'c'])
Playlist(['e', 'd', 'c', 'b', 'a'])
Playlist
```

### 13.3 `__setitem__` and `__delitem__`

`obj[k] = v` calls `__setitem__(k, v)`. `del obj[k]` calls `__delitem__(k)`. A mutable container usually defines both.

```python
class Row:
    def __init__(self, values):
        self._values = list(values)

    def __repr__(self):
        return f"Row({self._values!r})"

    def __len__(self):
        return len(self._values)

    def __getitem__(self, i):
        return self._values[i]

    def __setitem__(self, i, value):
        self._values[i] = value

    def __delitem__(self, i):
        del self._values[i]

r = Row([1, 2, 3, 4])
r[0] = 10
del r[1]
r[1:3] = [7, 8, 9]
print(r, len(r))
```
```text
Row([10, 7, 8, 9]) 4
```

Slice assignment `r[1:3] = [...]` works here because the same slice object is passed on to the list.

### 13.5 `__contains__`

`x in obj` calls `__contains__(x)` if it exists. If not, Python falls back to iterating (`__iter__`, or the old `__getitem__` protocol) and comparing each item. A custom `__contains__` can be **much faster** than scanning:

```python
class Evens:
    """All even numbers up to limit, without storing them."""
    def __init__(self, limit):
        self.limit = limit

    def __contains__(self, x):
        print("contains called")
        return isinstance(x, int) and 0 <= x < self.limit and x % 2 == 0

e = Evens(10 ** 12)
print(4 in e)
print(7 in e)
print(10 ** 13 in e)
```
```text
contains called
True
contains called
False
contains called
False
```

Checking `in` on a trillion-number sequence took no time, because `__contains__` is arithmetic, not a scan. That is the way `range` does it too.

## 14. Iteration: iterable vs iterator

### 14.2 The simplest `__iter__`: a generator

The best way to write `__iter__` is as a **generator function**. Each call gives a fresh, independent generator.

```python
class Playlist:
    def __init__(self, songs):
        self._songs = list(songs)

    def __iter__(self):
        for song in self._songs:
            yield song

p = Playlist(["a", "b", "c"])
print(list(p))
print(list(p))
for s in p:
    for t in p:
        print(s + t, end=" ")
print()
```
```text
['a', 'b', 'c']
['a', 'b', 'c']
aa ab ac ba bb bc ca cb cc 
```

We loop over the same object twice at once (nested loops), and each loop has its own iterator. That is what iterables are for. If `__iter__` returned `self` (an iterator), the inner loop would use up the shared state.

### 14.3 The mistake: an iterator that is its own iterable

```python
class CountDown:
    def __init__(self, n):
        self.n = n

    def __iter__(self):
        return self

    def __next__(self):
        if self.n <= 0:
            raise StopIteration
        self.n -= 1
        return self.n + 1

c = CountDown(3)
print(list(c))
print(list(c))
```
```text
[3, 2, 1]
[]
```

The second `list(c)` is empty. `CountDown` is an **iterator**: it is single-use. This is fine for things like file handles, but a **collection** should be reusable, so it should be an iterable that makes new iterators.

### 14.5 A ring buffer

A ring buffer holds the last `capacity` items. When full, the oldest item drops out. With `collections.deque(maxlen=...)` this is trivial, but let us write the container interface ourselves:

```python
from collections import deque

class RingBuffer:
    def __init__(self, capacity):
        self._items = deque(maxlen=capacity)

    def append(self, item):
        self._items.append(item)

    def __len__(self):
        return len(self._items)

    def __getitem__(self, i):
        return self._items[i]

    def __iter__(self):
        return iter(self._items)

    def __contains__(self, item):
        return item in self._items

    def __repr__(self):
        return f"RingBuffer({list(self._items)!r})"

rb = RingBuffer(3)
for n in range(5):
    rb.append(n)
print(rb, len(rb), rb[0], rb[-1], 3 in rb, 0 in rb)
print(sum(rb), max(rb), sorted(rb, reverse=True))
```
```text
RingBuffer([2, 3, 4]) 3 2 4 True False
9 4 [4, 3, 2]
```

`__iter__` returns `iter(self._items)`: a ready-made iterator from the inner container. Once your class has `__iter__`, **everything that consumes iterables** works: `sum`, `max`, `sorted`, `list`, `tuple`, `set`, unpacking and `in`.

## 15. Truth testing and the old sequence protocol

### 15.1 How `if obj:` decides

When you write `if obj:` or `while obj:` or `not obj`, Python calls `bool(obj)`. The steps:

1. If the class defines `__bool__`, call it. It must return a real `bool`.
2. Otherwise, if it defines `__len__`, the object is true if the length is non-zero.
3. Otherwise the object is always true.

```python
class OnlyLen:
    def __init__(self, n):
        self.n = n

    def __len__(self):
        return self.n

class Both:
    def __len__(self):
        return 0

    def __bool__(self):
        return True

class Neither:
    pass

print(bool(OnlyLen(0)), bool(OnlyLen(3)))
print(bool(Both()))
print(bool(Neither()))
```
```text
False True
True
True
```

That explains why `if my_list:` means "not empty": lists have `__len__`. It is also why **a class with `__len__` returning 0 is falsy**, a classic surprise:

```python
class Queue:
    def __init__(self):
        self.items = []

    def __len__(self):
        return len(self.items)

def process(queue=None):
    if not queue:
        queue = Queue()
        return "made a new queue"
    return "used the queue given"

print(process(Queue()))
print(process())
```
```text
made a new queue
made a new queue
```

We passed an empty `Queue`, and the `if not queue` check treated it as "nothing given". The fix is to test `if queue is None`. The same trap exists with empty lists (`def f(items=None): if not items:`).

### 15.3 The old sequence protocol

Before `__iter__` existed, Python iterated over a class by calling `__getitem__(0)`, `__getitem__(1)`, ... until `IndexError`. This is still supported as a fallback, which is why the `Deck` class of section 12 can be looped over.

```python
class OldStyle:
    def __getitem__(self, i):
        print("asked for", i)
        if i >= 3:
            raise IndexError
        return i * 10

print(list(OldStyle()))
print(20 in OldStyle())
```
```text
asked for 0
asked for 1
asked for 2
asked for 3
[0, 10, 20]
asked for 0
asked for 1
asked for 2
True
```

The order of preference for `for x in obj`: `__iter__` if present; otherwise this old fallback. For `x in obj`: `__contains__`; then iteration.

## 16. `collections.abc`: getting methods for free

### 16.1 The problem

Python's full list interface has many methods: `index`, `count`, `__contains__`, `__reversed__`, `append`, `pop`, `remove`, `extend`... Writing them all is tedious. The module `collections.abc` offers **abstract base classes**. You implement a few **abstract methods**, and the base class supplies the rest as **mixin methods**.

(You met abstract base classes in chapter 14, section 16. Same tool, new use.)

### 16.2 `Sequence`: two methods, a dozen features

Implement `__len__` and `__getitem__`. In return you get `__contains__`, `__iter__`, `__reversed__`, `index` and `count`.

```python
from collections.abc import Sequence

class Countdown(Sequence):
    def __init__(self, n):
        self.n = n

    def __len__(self):
        return self.n

    def __getitem__(self, i):
        if isinstance(i, slice):
            return [self[k] for k in range(*i.indices(self.n))]
        if not -self.n <= i < self.n:
            raise IndexError(i)
        return self.n - (i % self.n)

c = Countdown(5)
print(list(c))
print(3 in c, 9 in c)
print(list(reversed(c)))
print(c.index(2), c.count(2))
print(c[1:4])
```
```text
[5, 4, 3, 2, 1]
True False
[1, 2, 3, 4, 5]
3 1
[4, 3, 2]
```

If you forget one of the two abstract methods, you cannot create the object:

```python
from collections.abc import Sequence

class Half(Sequence):
    def __len__(self):
        return 3

try:
    Half()
except TypeError as e:
    print("TypeError:", e)
```
```text
TypeError: Can't instantiate abstract class Half without an implementation for abstract method '__getitem__'
```

### 16.3 `MutableMapping`: five methods, a whole dict

For a dict-like class, subclass `MutableMapping` and write `__getitem__`, `__setitem__`, `__delitem__`, `__iter__` and `__len__`. You then get `get`, `pop`, `popitem`, `setdefault`, `update`, `keys`, `items`, `values`, `clear`, `==`, `in`, and more.

Here is a dict that ignores key case (`"Host"` and `"host"` are one key), but remembers the original spelling:

```python
from collections.abc import MutableMapping

class CaseInsensitiveDict(MutableMapping):
    def __init__(self, data=None, **kwargs):
        self._store = {}
        self.update(data or {}, **kwargs)

    def __getitem__(self, key):
        return self._store[key.lower()][1]

    def __setitem__(self, key, value):
        self._store[key.lower()] = (key, value)

    def __delitem__(self, key):
        del self._store[key.lower()]

    def __iter__(self):
        return (original for original, _ in self._store.values())

    def __len__(self):
        return len(self._store)

    def __repr__(self):
        return f"CaseInsensitiveDict({dict(self.items())!r})"

h = CaseInsensitiveDict({"Content-Type": "text/html"})
h["ACCEPT"] = "*/*"
print(h["content-type"], h["accept"])
print("CONTENT-TYPE" in h, len(h))
print(h)
print(h.get("missing", "n/a"))
h.update({"accept": "text/plain"}, X_Id="7")
print(sorted(h.keys()))
print(h.pop("x_id"), len(h))
print(h == {"content-type": "text/html", "accept": "text/plain"})
```
```text
text/html */*
True 2
CaseInsensitiveDict({'Content-Type': 'text/html', 'ACCEPT': '*/*'})
n/a
['Content-Type', 'X_Id', 'accept']
7 2
False
```

Look at how much we get: `in`, `get`, `update` with keyword arguments, `pop`, `keys`, and even `==` against a plain dict. That `==` compares `dict(h.items())` with the other mapping, so it uses original spellings; the example happened to match because we passed the same spelling that is stored. Keep this in mind: a mapping equality built on mixin methods does not know about your case folding. If you need case-insensitive equality, override `__eq__`.


## 17. `__call__`: callable objects

### 17.1 Objects that act like functions

`f(args)` calls `type(f).__call__(f, args)`. A function is only one kind of **callable**. If your class defines `__call__`, its instances can be called too. Why would you want that? Because an object can **remember state** between calls, and a plain function cannot (without tricks).

```python
class Counter:
    def __init__(self):
        self.calls = 0

    def __call__(self, step=1):
        self.calls += step
        return self.calls

tick = Counter()
print(tick(), tick(), tick(10))
print(callable(tick), callable(Counter), callable(5))
print(tick.calls)
```
```text
1 2 12
True True False
12
```

`callable(x)` is `True` for functions, classes (calling a class makes an instance) and any object whose class has `__call__`.

## 18. Class-based decorators

### 18.1 Recall: a decorator is a callable that takes a function

From core.11: `@deco` above `def f` means `f = deco(f)`. Nothing says `deco` must be a function. A **class** is callable, so `deco(f)` can be a class call that builds an object holding `f`. That object is then called whenever you call `f(...)`, through `__call__`.

```python
import functools

class CountCalls:
    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func
        self.calls = 0

    def __call__(self, *args, **kwargs):
        self.calls += 1
        return self.func(*args, **kwargs)

@CountCalls
def greet(name):
    "Say hello."
    return f"hello {name}"

print(greet("Asha"), greet("Ben"))
print(greet.calls)
print(greet.__name__, greet.__doc__)
print(type(greet).__name__)
```
```text
hello Asha hello Ben
2
greet Say hello.
CountCalls
```

Three things: state lives on the object (`greet.calls`), so no `nonlocal` is needed. `functools.update_wrapper(self, func)` copies the name and doc string, like `functools.wraps` does for function decorators. And `greet` is no longer a function but a `CountCalls` instance.

### 18.2 A trap: class decorators on methods

A function becomes a **bound method** when looked up on an instance (core.14), because functions define `__get__`. An instance of `CountCalls` does not, so it is **not** bound, and `self` is lost:

```python
class CountCalls:
    def __init__(self, func):
        self.func = func

    def __call__(self, *args):
        return self.func(*args)

class Dog:
    @CountCalls
    def bark(self):
        return "woof"

try:
    Dog().bark()
except TypeError as e:
    print("TypeError:", e)
```
```text
TypeError: Dog.bark() missing 1 required positional argument: 'self'
```

`Dog().bark` returned the `CountCalls` object itself, with no `Dog` attached, so `self.func(*args)` ran `bark()` without `self`. Class-based decorators are best used on **plain functions**. For methods, use a function-based decorator. (The cure for the class form is the descriptor protocol, which is for core.23.)

### 18.3 Decorators with arguments

`@Retry(times=3)` first **calls** `Retry(times=3)`, creating an object. Python then applies that object to the function, so the object's `__call__` receives the function and returns the wrapper.

```python
import functools

class Retry:
    def __init__(self, times=3, exceptions=(Exception,)):
        self.times = times
        self.exceptions = exceptions

    def __call__(self, func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, self.times + 1):
                try:
                    return func(*args, **kwargs)
                except self.exceptions as exc:
                    print(f"attempt {attempt} failed: {exc}")
                    if attempt == self.times:
                        raise
        return wrapper

calls = {"n": 0}

@Retry(times=3, exceptions=(ValueError,))
def flaky():
    calls["n"] += 1
    if calls["n"] < 3:
        raise ValueError("not yet")
    return "ok"

print(flaky())
```
```text
attempt 1 failed: not yet
attempt 2 failed: not yet
ok
```

Here `__init__` takes the **settings**, and `__call__` takes the **function**. It is a neat way to avoid the "three-level nested function" pattern of decorator factories.

### Try it 18.1

Write a class decorator `Timed` that keeps the duration of the last call in `.last` (`None` before the first call). Use `time.perf_counter()` and `try`/`finally`.

<details><summary>Answer</summary>

```python
import time

class Timed:
    def __init__(self, func):
        self.func = func
        self.last = None

    def __call__(self, *args, **kwargs):
        start = time.perf_counter()
        try:
            return self.func(*args, **kwargs)
        finally:
            self.last = time.perf_counter() - start

@Timed
def work():
    return sum(range(1000))

print(work.last)
work()
print(isinstance(work.last, float))
```
```text
None
True
```

</details>

## 19. Decorating classes

### 19.1 A decorator can receive a class

`@deco` above a `class` statement means `Cls = deco(Cls)`. The decorator gets the finished class object and may change it or return another one. You have used this already: `@total_ordering` and `@dataclass` are class decorators.

### 19.2 Registering classes

A very common use: put each decorated class in a registry.

```python
PLUGINS = {}

def register(cls):
    PLUGINS[cls.__name__.lower()] = cls
    return cls

@register
class CsvReader:
    pass

@register
class JsonReader:
    pass

print(sorted(PLUGINS))
reader = PLUGINS["csvreader"]()
print(type(reader).__name__)
```
```text
['csvreader', 'jsonreader']
CsvReader
```

The decorator must **return the class** (usually the same one). Forgetting the `return` makes the class name `None`.

## 20. The context manager protocol

### 20.1 What `with` guarantees

From core.12, you know `with open(...) as f:` closes the file even if an error occurs. The `with` statement is a promise: **setup runs before the block, and cleanup always runs after it**, whatever happens. The protocol has two methods:

- `__enter__(self)` runs at the start. Its return value is bound to the name after `as`.
- `__exit__(self, exc_type, exc_value, traceback)` runs at the end, always. The three arguments describe an exception that happened inside the block, or are all `None` if there was none.

```python
class Demo:
    def __enter__(self):
        print("enter")
        return "the value"

    def __exit__(self, exc_type, exc_value, tb):
        print("exit", exc_type)
        return False

with Demo() as value:
    print("inside:", value)
print("after")
```
```text
enter
inside: the value
exit None
after
```

### 20.2 A timer

```python
import time

class Timer:
    def __enter__(self):
        self.start = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_value, tb):
        self.elapsed = time.perf_counter() - self.start
        return False

with Timer() as t:
    total = sum(range(100_000))
print(total, t.elapsed < 1.0)
```
```text
4999950000 True
```

`__enter__` returns `self`, so `t` is the timer, and its `elapsed` is readable after the block ends. Returning `self` is the most common pattern.

### 20.3 What `with` is really doing

`with A() as x: body` is roughly:

```python
mgr = A()
x = mgr.__enter__()
try:
    body
except BaseException as e:
    if not mgr.__exit__(type(e), e, e.__traceback__):
        raise
else:
    mgr.__exit__(None, None, None)
```

Study this carefully. It explains the next section. Note that `__enter__` is **outside** the `try`: if `__enter__` itself raises, `__exit__` is not called, because setup never finished.

## 21. Exceptions inside `with`

### 21.1 The three arguments

If the block raises, `__exit__` receives the exception's type, value and traceback. What `__exit__` **returns** decides what happens next:

- A **falsy** value (`None`, `False`, or no `return`): the exception **continues** to propagate. This is the right default.
- A **truthy** value (`True`): the exception is **suppressed**. Execution continues after the `with` block as if nothing happened.

```python
class Quiet:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        print("saw:", exc_type.__name__, exc_value)
        return True

with Quiet():
    1 / 0
print("carried on")
```
```text
saw: ZeroDivisionError division by zero
carried on
```

### 21.2 Suppress only what you mean to

Returning `True` blindly hides every bug, including `KeyboardInterrupt`. A good `__exit__` checks the type first:

```python
class IgnoreMissing:
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, tb):
        return exc_type is not None and issubclass(exc_type, FileNotFoundError)

with IgnoreMissing():
    open("/no/such/file")
print("file error ignored")
try:
    with IgnoreMissing():
        raise ValueError("a different problem")
except ValueError as e:
    print("ValueError still raised:", e)
```
```text
file error ignored
ValueError still raised: a different problem
```

If there was no exception, `exc_type` is `None`, so the expression is `False`, and nothing is suppressed.

### 21.3 Order of events with several managers and an error

```python
class CM:
    def __init__(self, name):
        self.name = name

    def __enter__(self):
        print("enter", self.name)
        return self

    def __exit__(self, exc_type, exc_value, tb):
        print("exit", self.name, exc_type.__name__ if exc_type else None)
        return False

try:
    with CM("A"), CM("B"):
        print("body")
        raise KeyError("boom")
except KeyError:
    print("caught outside")
```
```text
enter A
enter B
body
exit B KeyError
exit A KeyError
caught outside
```

Managers are entered **left to right** and exited **right to left** (like stacked plates). The exception passes `B`, then `A`, then reaches the `except`. `with A, B:` is the same as nesting `with A:` around `with B:`.

### Predict the output 21.1

```python
class CM:
    def __init__(self, name, suppress=False):
        self.name, self.suppress = name, suppress
    def __enter__(self):
        print("in", self.name)
    def __exit__(self, *exc):
        print("out", self.name)
        return self.suppress

with CM("A"):
    with CM("B", suppress=True):
        raise ValueError
    print("between")
print("end")
```

<details><summary>Answer</summary>

```text
in A
in B
out B
between
out A
end
```
`B` suppresses the error, so `between` and `end` are printed. `A` sees no exception.

</details>

## 22. `contextlib.contextmanager`

### 22.1 A generator instead of a class

Writing a class with two methods is long for simple jobs. The decorator `contextlib.contextmanager` lets you write a **generator with exactly one `yield`**. Code before `yield` is `__enter__`. The `yielded` value is the `as` value. Code after `yield` is `__exit__`.

```python
from contextlib import contextmanager

@contextmanager
def tag(name):
    print(f"<{name}>")
    yield name.upper()
    print(f"</{name}>")

with tag("b") as shout:
    print("text", shout)
```
```text
<b>
text B
</b>
```

### 22.2 The try/finally rule

What if the block raises? The exception is **thrown into the generator at the `yield` line**. Without a `try`/`finally`, the cleanup after `yield` never runs:

```python
from contextlib import contextmanager

@contextmanager
def bad():
    print("setup")
    yield
    print("cleanup")

try:
    with bad():
        raise RuntimeError("boom")
except RuntimeError:
    print("caught")
```
```text
setup
caught
```

`cleanup` is missing! The exception left the generator at `yield`. The right way:

```python
from contextlib import contextmanager

@contextmanager
def good():
    print("setup")
    try:
        yield
    finally:
        print("cleanup")

try:
    with good():
        raise RuntimeError("boom")
except RuntimeError:
    print("caught")
```
```text
setup
cleanup
caught
```

**Rule: put `yield` inside `try`, and put the cleanup in `finally`** (or in an `except` you mean to have).

## 23. More `contextlib`: `suppress`, `redirect_stdout`, `ExitStack`

### 23.1 `suppress` and `redirect_stdout`

`contextlib` already ships useful managers. `suppress(*types)` ignores those exceptions. `redirect_stdout(target)` sends `print` output into a file-like object.

```python
import io
from contextlib import suppress, redirect_stdout

with suppress(FileNotFoundError):
    open("/no/such/file")
print("still here")

buf = io.StringIO()
with redirect_stdout(buf):
    print("captured")
    print("also captured")
print(repr(buf.getvalue()))
```
```text
still here
'captured\nalso captured\n'
```

`suppress` is the tidy form of `try: ... except X: pass`. `redirect_stdout` is useful for testing code that prints. There is also `redirect_stderr`.

### 23.3 `ExitStack`: a variable number of managers

What if the number of files to open is only known at run time? You cannot write one `with` line for it. `ExitStack` collects managers and exits them all, in reverse order, even if one fails.

```python
from contextlib import ExitStack, contextmanager

@contextmanager
def resource(name):
    print("open", name)
    try:
        yield name
    finally:
        print("close", name)

with ExitStack() as stack:
    handles = [stack.enter_context(resource(n)) for n in ("a", "b", "c")]
    print("working with", handles)
```
```text
open a
open b
open c
working with ['a', 'b', 'c']
close c
close b
close a
```

`enter_context(cm)` enters the manager and returns its `as` value. When the `with ExitStack()` block ends, everything is closed in **reverse** order: `c`, `b`, `a`. If opening `c` fails, `a` and `b` are still closed properly. You can also register plain cleanup functions with `stack.callback(func, *args)`.

## 24. Dataclasses: the basics

### 24.1 The boilerplate problem

A class that mainly holds data needs `__init__`, `__repr__` and `__eq__`, all repeating the same field names. A **dataclass** writes them for you from **annotated fields**.

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int = 0

p = Point(3)
print(p)
print(p == Point(3, 0), p == Point(3, 1))
p.y = 9
print(p)
```
```text
Point(x=3, y=0)
True False
Point(x=3, y=9)
```

`@dataclass` read the annotations `x: int` and `y: int = 0` and generated `__init__(self, x, y=0)`, `__repr__` and `__eq__`. The types are hints only (core.09): nothing checks them at run time. It is a class decorator (section 19), and it is not magic: you can inspect the generated methods.

### 24.2 Rules for fields

- Fields **without a default must come before** fields with defaults (as for function parameters).
- A field is created **only if it has an annotation**. `z = 5` without `: int` is a normal class attribute.
- By default instances are **mutable and unhashable** (like any class with a custom `__eq__`: see section 6; Python sets `__hash__ = None`).

```python
from dataclasses import dataclass

@dataclass
class Item:
    name: str
    price: float = 0.0

print(Item("pen", 1.5))
print(Item.__hash__ is None)
try:
    @dataclass
    class Bad:
        a: int = 1
        b: int
except TypeError as e:
    print("TypeError:", e)
```
```text
Item(name='pen', price=1.5)
True
TypeError: non-default argument 'b' follows default argument 'a'
```

## 25. Dataclasses in depth

### 25.1 `field()` and the mutable default trap

A plain mutable default like `tags: list = []` would be **shared by all instances**, the same trap as the mutable default argument (core.06). Dataclasses refuse it:

```python
from dataclasses import dataclass

try:
    @dataclass
    class Post:
        title: str
        tags: list = []
except ValueError as e:
    print("ValueError:", e)
```
```text
ValueError: mutable default <class 'list'> for field tags is not allowed: use default_factory
```

The cure is `field(default_factory=...)`: a function called **for each new instance**.

```python
from dataclasses import dataclass, field

@dataclass
class Post:
    title: str
    tags: list = field(default_factory=list)

a, b = Post("a"), Post("b")
a.tags.append("x")
print(a.tags, b.tags)
```
```text
['x'] []
```

`field` also takes `repr=False` (hide from repr), `compare=False` (ignore in `==`), `init=False` (not a parameter), and `default=`.

### 25.2 `frozen=True`: immutable, and hashable

```python
from dataclasses import dataclass, FrozenInstanceError

@dataclass(frozen=True)
class Coord:
    lat: float
    lon: float

c = Coord(1.0, 2.0)
try:
    c.lat = 5
except FrozenInstanceError as e:
    print("FrozenInstanceError:", e)
print(hash(c) == hash(Coord(1.0, 2.0)))
print({c: "home"}[Coord(1.0, 2.0)])
```
```text
FrozenInstanceError: cannot assign to field 'lat'
True
home
```

With `eq=True` (the default) and `frozen=True`, dataclass also generates a **matching `__hash__`**, from the same fields. This is the safe answer to section 6: immutable, so the hash can never change.

### 25.3 `order=True`

```python
from dataclasses import dataclass

@dataclass(order=True)
class Version:
    major: int
    minor: int = 0

print(Version(1, 2) < Version(1, 10))
print(sorted([Version(2), Version(1, 5), Version(1)]))
```
```text
True
[Version(major=1, minor=0), Version(major=1, minor=5), Version(major=2, minor=0)]
```

`order=True` writes `__lt__`, `__le__`, `__gt__`, `__ge__` comparing the fields **as a tuple, in order**. It replaces `total_ordering` when field order is the order you want. Fields can also be left out with `field(compare=False)`.

### 25.4 `__post_init__`: validate and derive

The generated `__init__` calls `self.__post_init__()` after setting the fields, if you define it. That is the place for checks and for computed fields.

```python
from dataclasses import dataclass, field

@dataclass
class Rect:
    w: float
    h: float
    area: float = field(init=False)

    def __post_init__(self):
        if self.w <= 0 or self.h <= 0:
            raise ValueError(f"sides must be positive, got {self.w}x{self.h}")
        self.area = self.w * self.h

print(Rect(2, 3))
try:
    Rect(-1, 5)
except ValueError as e:
    print("ValueError:", e)
```
```text
Rect(w=2, h=3, area=6)
ValueError: sides must be positive, got -1x5
```

With `frozen=True`, you cannot assign `self.area = ...`. Use `object.__setattr__(self, "area", value)` in `__post_init__` as the standard workaround.

### Try it 25.1

A dataclass has `tags: list = []`. Fix it with `default_factory`, and show that two instances do not share the list.

<details><summary>Answer</summary>

```python
from dataclasses import dataclass, field

@dataclass
class Post:
    tags: list = field(default_factory=list)

a, b = Post(), Post()
a.tags.append("x")
print(a, b)
```
```text
Post(tags=['x']) Post(tags=[])
```

</details>

## 26. Enums

### 26.1 Names for a fixed set of choices

Strings and numbers such as `"red"` or `3` for choices are easy to mistype and hard to search. An `Enum` makes a **small, closed set of named constants**.

```python
from enum import Enum

class Color(Enum):
    RED = 1
    GREEN = 2
    BLUE = 3

c = Color.RED
print(c, repr(c))
print(c.name, c.value)
print(Color(2), Color["BLUE"])
print(c is Color.RED, c == Color.GREEN)
print(list(Color))
```
```text
Color.RED <Color.RED: 1>
RED 1
Color.GREEN Color.BLUE
True False
[<Color.RED: 1>, <Color.GREEN: 2>, <Color.BLUE: 3>]
```

Each member has a `name` and a `value`. Members are **singletons**: compare them with `is` or `==`. Lookup by value is `Color(2)`, by name `Color["BLUE"]`.

```python
from enum import Enum

class Color(Enum):
    RED = 1

try:
    Color(9)
except ValueError as e:
    print("ValueError:", e)
print(Color.RED == 1)
```
```text
ValueError: 9 is not a valid Color
False
```

An enum member is **not** equal to its raw value. That is the point: `Color.RED` can never be confused with `1`.

### 26.2 `auto()`

When the values do not matter, let Python number them:

```python
from enum import Enum, auto

class Status(Enum):
    PENDING = auto()
    ACTIVE = auto()
    DONE = auto()

print([(s.name, s.value) for s in Status])
```
```text
[('PENDING', 1), ('ACTIVE', 2), ('DONE', 3)]
```

## 27. `IntEnum` and `Flag`

### 27.1 `IntEnum`: members that are also integers

`IntEnum` members **are** ints, so they compare equal to numbers and can be used wherever an int is expected. Use it for codes that must also work as numbers (HTTP statuses, exit codes).

```python
from enum import Enum, IntEnum

class Http(IntEnum):
    OK = 200
    NOT_FOUND = 404

class Plain(Enum):
    OK = 200

print(Http.OK == 200, Plain.OK == 200)
print(Http.NOT_FOUND > Http.OK, sorted([Http.NOT_FOUND, Http.OK]))
print(Http(404).name, int(Http.OK) + 1)
```
```text
True False
True [<Http.OK: 200>, <Http.NOT_FOUND: 404>]
NOT_FOUND 201
```

The price: an `IntEnum` also equals *any other* `IntEnum` with the same number, so you can compare unrelated things by mistake. Prefer plain `Enum` unless you need the integer behaviour.

### 27.2 `Flag`: sets of options with bit operations

A `Flag` combines members with `|` (union), `&` (intersection) and `~` (not). Values are **powers of two**, so each flag is one bit. This is the classic model for permissions.

```python
from enum import Flag, auto

class Perm(Flag):
    READ = auto()
    WRITE = auto()
    EXEC = auto()

p = Perm.READ | Perm.WRITE
print(p, p.value)
print(Perm.READ in p, Perm.EXEC in p)
print(p & Perm.WRITE, bool(p & Perm.EXEC))
print(p ^ Perm.READ)
print(Perm(0), bool(Perm(0)))
```
```text
Perm.READ|WRITE 3
True False
Perm.WRITE False
Perm.WRITE
Perm(0) False
```

`in` tests whether a flag is **included**. The empty flag `Perm(0)` is false. `IntFlag` is a `Flag` whose members also behave as ints (like Unix permission bits `0o755`).

## 28. `__slots__` and memory

### 28.1 Where instance attributes live

Every normal instance has a **`__dict__`**: a dictionary holding its attributes (core.14). A dict is flexible (you can add any attribute at any time), but it costs memory for every single object. If you create a million small objects, the dicts add up.

`__slots__` tells Python to reserve **fixed storage** for a named list of attributes and to skip the `__dict__`.

```python
class Plain:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Slim:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x = x
        self.y = y

p, s = Plain(1, 2), Slim(1, 2)
print(hasattr(p, "__dict__"), hasattr(s, "__dict__"))
print(p.__dict__)
print(Slim.__slots__)
```
```text
True False
{'x': 1, 'y': 2}
('x', 'y')
```

### 28.2 No new attributes

Without a `__dict__`, you cannot add attributes that are not listed. That is both a limit and a safety net: a typo like `s.z = 3` raises an error instead of silently creating a new attribute.

```python
class Slim:
    __slots__ = ("x", "y")

    def __init__(self, x, y):
        self.x = x
        self.y = y

s = Slim(1, 2)
try:
    s.z = 3
except AttributeError as e:
    print("AttributeError:", e)
try:
    print(s.__dict__)
except AttributeError as e:
    print("AttributeError:", e)
```
```text
AttributeError: 'Slim' object has no attribute 'z' and no __dict__ for setting new attributes
AttributeError: 'Slim' object has no attribute '__dict__'
```

### 28.3 Measuring the saving

```python
import sys

class Plain:
    def __init__(self, a, b, c):
        self.a, self.b, self.c = a, b, c

class Slim:
    __slots__ = ("a", "b", "c")

    def __init__(self, a, b, c):
        self.a, self.b, self.c = a, b, c

p, s = Plain(1, 2, 3), Slim(1, 2, 3)
print("plain:", sys.getsizeof(p) + sys.getsizeof(p.__dict__))
print("slim: ", sys.getsizeof(s))
```
```text
plain: 344
slim:  56
```

The exact numbers depend on the Python version and machine (they are machine-specific), but the slotted object is clearly smaller. Over a million instances, that is tens of megabytes. Access to slot attributes is also a little faster.

### 28.4 Rules and traps

- **Inheritance:** a subclass that does not define `__slots__` gets a `__dict__` again, and the saving is gone. Each class in the chain should define `__slots__` (use `()` if it adds nothing).
- **Weak references and multiple inheritance:** slotted classes cannot be weakly referenced unless `"__weakref__"` is listed, and several parents with non-empty slots conflict.
- **No class-level defaults for slot names:** `x = 0` in the class body conflicts with a slot named `x`.
- **Dataclasses:** `@dataclass(slots=True)` creates the slots for you.

```python
from dataclasses import dataclass

@dataclass(slots=True)
class P:
    x: int
    y: int

p = P(1, 2)
print(p, hasattr(p, "__dict__"))

class Base:
    __slots__ = ("a",)

class Child(Base):
    pass

print(hasattr(Child(), "__dict__"))
```
```text
P(x=1, y=2) False
True
```

## 29. Project: a Vector and Matrix library

Put the chapter together. We write a small immutable `Vector` with operators, `repr`, iteration, indexing, length, equality and hashing.

```python
import math

class Vector:
    __slots__ = ("_items",)

    def __init__(self, *items):
        self._items = tuple(items)

    def __repr__(self):
        return f"Vector({', '.join(map(repr, self._items))})"

    def __len__(self):
        return len(self._items)

    def __iter__(self):
        return iter(self._items)

    def __getitem__(self, i):
        return self._items[i]

    def __eq__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented
        return self._items == other._items

    def __hash__(self):
        return hash(self._items)

    def __add__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented
        if len(self) != len(other):
            raise ValueError("vectors must have the same length")
        return Vector(*(a + b for a, b in zip(self, other)))

    def __sub__(self, other):
        if not isinstance(other, Vector):
            return NotImplemented
        return self + (-other)

    def __neg__(self):
        return Vector(*(-a for a in self))

    def __mul__(self, k):
        if isinstance(k, (int, float)):
            return Vector(*(a * k for a in self))
        return NotImplemented

    __rmul__ = __mul__

    def __matmul__(self, other):
        if not isinstance(other, Vector) or len(self) != len(other):
            return NotImplemented
        return sum(a * b for a, b in zip(self, other))

    def __abs__(self):
        return math.sqrt(self @ self)

v, w = Vector(1, 2, 3), Vector(4, 5, 6)
print(v + w, w - v, -v)
print(v * 2, 2 * v, v @ w, abs(Vector(3, 4)))
print(len(v), v[0], list(v), v == Vector(1, 2, 3))
print(sum([v, v], Vector(0, 0, 0)))
```
```text
Vector(5, 7, 9) Vector(3, 3, 3) Vector(-1, -2, -3)
Vector(2, 4, 6) Vector(2, 4, 6) 32 5.0
3 1 [1, 2, 3] True
Vector(2, 4, 6)
```

`@` is the **dot product** for vectors. `__rmul__ = __mul__` is safe because scalar multiplication commutes. The vector is immutable and hashable, and it uses `__slots__`. Every method returns a **new** object. Errors for a wrong *type* are `NotImplemented` ("I do not know this operand"), but a right type with a wrong value, such as vectors of different length, is a real `ValueError`.

A `Matrix` follows the same recipe: store a list of rows, give it `__repr__`, `__eq__`, `__len__`, `__iter__`, `__getitem__` (with `m[r, c]` through a tuple key), `+` and `*` by a number, and `@` for the matrix product (the shapes must fit: columns of the left equal rows of the right). You build both classes in the final problem of this module.

## 30. Common traps

1. **Defining `__eq__` and forgetting `__hash__`.** The class becomes unhashable (section 6). Define both for immutable value objects, or neither for mutable ones.
2. **Hashing mutable fields.** If the hash changes after you put the object in a set, it is lost (6.4). Make value objects immutable (`frozen=True`).
3. **Returning `False` instead of `NotImplemented`** for unknown types. It blocks the other operand. Return `NotImplemented`.
4. **`__repr__` missing.** `__str__` alone does not give a good `repr`. Write `__repr__` first.
5. **Wrong operand order in `__rsub__` and `__rtruediv__`.** `other` is on the **left**.
6. **`__iadd__` without `return self`.** The variable becomes `None` (section 10).
7. **A mutable operation in `__add__`.** `a + b` must not change `a` or `b`.
8. **An iterator used as a collection.** `__iter__` returning `self` gives a one-shot object. A collection's `__iter__` must create a new iterator every time (section 14).
9. **`if not obj:` for "was it given?"** A class with `__len__` is falsy when empty. Use `is None` (section 15).
10. **`@contextmanager` without `try/finally`.** Cleanup is skipped on errors (section 22).
11. **An `__exit__` that returns `True` by habit.** It hides every error. Suppress only specific types.
12. **A class-based decorator on a method.** `self` is lost (section 18).
13. **Mutable default in a dataclass.** Use `field(default_factory=...)`.
14. **A frozen dataclass holding a list.** The hash fails when the list is hashed.
15. **A subclass of a `__slots__` class without its own `__slots__`.** The `__dict__` comes back.
16. **Tuple of a list with `+=`.** Both the change and the `TypeError` happen (10.4).

## 31. Summary

- The **data model** is a set of dunder methods. Python syntax (`len`, `[]`, `+`, `==`, `for`, `with`, `()`) calls them on the **type** of the object.
- `__repr__` is for developers (exact, ideally `eval`-able); `__str__` is for users and falls back to `__repr__`; `__format__` handles `f"{x:spec}"`. Containers show their items with `repr`.
- Define `__eq__` to compare by value. Return `NotImplemented` for foreign types. Equal objects **must** have equal hashes, so defining `__eq__` sets `__hash__` to `None` until you define a matching one. Hash exactly the fields you compare, and keep them immutable.
- Define `__lt__` (plus `__eq__`) and use `functools.total_ordering` to get the other comparisons.
- Arithmetic methods return **new** objects and `NotImplemented` for unknown operands. Python then tries the reflected `__radd__` and friends (a subclass's reflected method goes first). In-place methods (`__iadd__`) mutate and **return `self`**.
- `__len__` plus `__getitem__` makes a sequence. Add `__iter__` (a generator is easiest), `__contains__`, `__setitem__`, `__delitem__` as needed. Truth testing uses `__bool__`, then `__len__`. Use `collections.abc.Sequence` or `MutableMapping` to get many methods free.
- `__call__` makes objects callable. A class can be a decorator, with state on the instance. A class decorator receives and returns a class.
- `with` calls `__enter__` and always `__exit__`. A truthy return from `__exit__` suppresses the error. `@contextmanager` writes the same in a generator: use `try/finally` around `yield`. `suppress`, `redirect_stdout`, `closing` and `ExitStack` cover many needs.
- `@dataclass` generates `__init__`, `__repr__`, `__eq__` (and more) from annotations. Use `field(default_factory=...)` for mutable defaults, `frozen=True` for hashable values, `order=True` for ordering, `__post_init__` for checks.
- `Enum` gives named constants; `IntEnum` adds int behaviour; `Flag` combines options with `|` and `&`.
- `__slots__` removes the per-instance `__dict__`, saving memory for many small objects, and forbids new attributes.

Next you apply these ideas in the problems, and finish with the Vector and Matrix project: the type of library you will meet again in NumPy and pandas.
