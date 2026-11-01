# Chapter 23: Attribute machinery and metaprogramming

Every time you write `obj.name`, Python runs a small algorithm. Most days you never think about it: the value comes back and you move on. But that algorithm is where some of Python's most useful features live. `property` is not built into the language: it is an ordinary class that plugs into the algorithm. Methods are not special either: a function stored on a class turns into a "bound method" because of the same algorithm. Dataclasses, Django models, SQLAlchemy columns, `functools.cached_property`, `enum.Enum`: all of them work by hooking into how attributes are looked up and how classes are created.

This chapter opens the machine. You will learn the exact steps of attribute lookup, the hooks that let a class change those steps, and the objects (called **descriptors**) that make properties and methods work. Then you will go one level up: classes are objects too, something creates them, and you can hook into that as well. That is **metaprogramming**: code that writes or changes other code, here meaning classes that shape other classes.

The chapter has two learning outcomes:

1. **Explain how a function becomes a bound method**: say, step by step, what Python does when you write `obj.method(1)`, and why `obj.method` is a new object every time.
2. **Build a validated-field system with descriptors**: write `Typed`, `Range` and `OneOf` fields that check every assignment, know their own names, and store values safely per instance.

There is also a third, quieter goal, and it may be the most important: **knowing when not to use any of this.** Metaprogramming is powerful and easy to overuse. Section 20 is about that, and it is not a footnote.

**A note on how examples are shown.** Every block that has output was really run, with **Python 3.14** on Linux. The course supports Python 3.11 and later; where 3.11 to 3.13 behave differently, the text says so. Memory addresses (like `0x7f3a...`) change on every run and are labelled when they appear; most examples give classes a `__repr__` so addresses do not appear at all. Error messages written by CPython itself sometimes change wording between versions, so examples usually print only the exception's type name (`type(e).__name__`). Everything uses features from core.01 to core.22 plus this chapter's topics.

## Table of contents

[1. Why this module: attributes are function calls in disguise](#1-why-this-module-attributes-are-function-calls-in-disguise) · [2. What `obj.x` really does](#2-what-objx-really-does) · [3. `__getattr__`: the fallback hook](#3-__getattr__-the-fallback-hook) · [4. `__getattribute__`: the every-time hook](#4-__getattribute__-the-every-time-hook) · [5. `__setattr__` and `__delattr__`](#5-__setattr__-and-__delattr__) · [6. Descriptors: the protocol](#6-descriptors-the-protocol) · [7. Data vs non-data descriptors and precedence](#7-data-vs-non-data-descriptors-and-precedence) · [8. `__set_name__` and where to store per-instance values](#8-__set_name__-and-where-to-store-per-instance-values) · [9. How functions become bound methods](#9-how-functions-become-bound-methods) · [10. How `property`, `classmethod` and `staticmethod` really work](#10-how-property-classmethod-and-staticmethod-really-work) · [11. `functools.cached_property` and lazy attributes](#11-functoolscached_property-and-lazy-attributes) · [12. Build a validated-field system](#12-build-a-validated-field-system) · [13. `__slots__` are descriptors too](#13-__slots__-are-descriptors-too) · [14. `__init_subclass__`: hooking subclass creation](#14-__init_subclass__-hooking-subclass-creation) · [15. `__class_getitem__`: what `list[int]` is](#15-__class_getitem__-what-listint-is) · [16. Classes are objects: `type(name, bases, ns)`](#16-classes-are-objects-typename-bases-ns) · [17. Metaclasses: how a class is created](#17-metaclasses-how-a-class-is-created) · [18. Metaclass `__call__`: controlling instance creation](#18-metaclass-__call__-controlling-instance-creation) · [19. Class decorators vs `__init_subclass__` vs metaclasses](#19-class-decorators-vs-__init_subclass__-vs-metaclasses) · [20. When metaprogramming is the wrong choice](#20-when-metaprogramming-is-the-wrong-choice) · [21. Common traps](#21-common-traps) · [22. Project preview: a Mini ORM using descriptors](#22-project-preview-a-mini-orm-using-descriptors) · [23. Summary](#23-summary)

## 1. Why this module: attributes are function calls in disguise

### 1.1 The repetition problem

Here is a common task. A `Product` has a `price` and a `stock`. Both must be numbers, and both must be zero or more. You already know one way to guard an attribute: a `property` (core.14).

```python
class Product:
    def __init__(self, name, price, stock):
        self.name = name
        self.price = price      # goes through the property setter
        self.stock = stock

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        if not isinstance(value, (int, float)) or value < 0:
            raise ValueError(f"price must be a number >= 0, got {value!r}")
        self._price = value

    @property
    def stock(self):
        return self._stock

    @stock.setter
    def stock(self, value):
        if not isinstance(value, (int, float)) or value < 0:
            raise ValueError(f"stock must be a number >= 0, got {value!r}")
        self._stock = value

p = Product("pen", 10, 5)
print(p.price, p.stock)
try:
    p.stock = -3
except ValueError as e:
    print("ValueError:", e)
```
```text
10 5
ValueError: stock must be a number >= 0, got -3
```

It works, but look at it. Two attributes cost twenty lines, and the two setters are the same code with one word changed. A real class might have ten such fields. Copy-paste is a smell (core.22): if the rule changes ("allow `Decimal` too"), you must change it in ten places and you will miss one.

What you want is to write the rule **once** and say "this attribute follows that rule":

```python
class NonNegative:
    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        return obj.__dict__[self.name]

    def __set__(self, obj, value):
        if not isinstance(value, (int, float)) or value < 0:
            raise ValueError(f"{self.name} must be a number >= 0, got {value!r}")
        obj.__dict__[self.name] = value


class Product:
    price = NonNegative()
    stock = NonNegative()

    def __init__(self, name, price, stock):
        self.name = name
        self.price = price
        self.stock = stock

p = Product("pen", 10, 5)
print(p.price, p.stock)
try:
    p.stock = -3
except ValueError as e:
    print("ValueError:", e)
```
```text
10 5
ValueError: stock must be a number >= 0, got -3
```

Same behavior, and the rule lives in one place. Adding a third guarded field is one line. `NonNegative` is a **descriptor**: an object stored on a class that takes over reading and writing of one attribute. You do not need to understand the three methods yet. By section 12 you will write a whole family of them.

### 1.2 The key idea

The surprising thing in that example is that `p.stock = -3` ran a method on an object that is not `p`. The assignment looked like "put -3 into `p`", but Python first asked the **class**: "is there anything on you called `stock` that wants to handle this?" There was, so Python called it.

So an attribute access is really a **function call in disguise**. `p.price` may call `NonNegative.__get__`, `p.price = 10` may call `NonNegative.__set__`, and `p.speak()` first calls `function.__get__` to make a bound method, then calls that. Once you see attribute access this way, a lot of Python stops being magic.

### 1.3 The map of this chapter

The chapter climbs a ladder:

1. **Lookup** (sections 2 to 5): the exact algorithm behind `obj.x`, and the four hooks a class can define to change it: `__getattr__`, `__getattribute__`, `__setattr__`, `__delattr__`.
2. **Descriptors** (sections 6 to 13): the protocol, data versus non-data descriptors, `__set_name__`, then the payoff: how methods, `property`, `classmethod`, `staticmethod`, `cached_property` and `__slots__` all work, and the validated-field system.
3. **Class creation** (sections 14 to 19): `__init_subclass__`, `__class_getitem__`, building classes with `type()`, metaclasses, and how to choose the lightest tool.
4. **Judgment** (sections 20 to 23): when all of this is the wrong choice, the common traps, a design sketch of a mini ORM, and a summary.

## 2. What `obj.x` really does

### 2.1 Two places to look, and one rule of priority

You met a short version of this in core.14 (section 9). Now here is the full version. When you read `obj.x`, there are two main places a value can come from:

- the **instance dictionary**, `obj.__dict__`, which holds what was assigned to this object (`self.x = ...`);
- the **class and its parents**, walked in **MRO order** (`type(obj).__mro__`, core.14 section 12). Each class has its own `__dict__` holding what the class body defined: methods, class attributes, properties.

If the name is in both places, who wins? It depends on **what kind of object** sits on the class:

- A **data descriptor** on the class wins over the instance dictionary. A data descriptor is an object whose type defines `__get__` and also `__set__` or `__delete__`. `property` is one. That is why a property cannot be hidden by `obj.__dict__["x"] = ...`.
- Otherwise the **instance dictionary** wins.
- If the instance dictionary does not have it, the class attribute is used. If it is a **non-data descriptor** (its type defines only `__get__`, like a plain function), Python calls its `__get__` and returns the result (for a function: a bound method). Otherwise the class attribute is returned as it is.
- If nothing is found anywhere, Python raises `AttributeError`. If the class defines `__getattr__`, Python calls it as a last chance instead.

### 2.2 The algorithm as a picture

```text
obj.x
  |
  v
cls_attr = first "x" found in the __dict__ of each class in type(obj).__mro__
  |
  +-- cls_attr is a DATA descriptor?  ---- yes --> return cls_attr.__get__(obj, type(obj))
  |
  +-- "x" in obj.__dict__?           ---- yes --> return obj.__dict__["x"]
  |
  +-- cls_attr is a NON-DATA descriptor? - yes --> return cls_attr.__get__(obj, type(obj))
  |
  +-- cls_attr found at all?         ---- yes --> return cls_attr
  |
  +-- raise AttributeError
        |
        +-- type(obj) has __getattr__? --- yes --> return type(obj).__getattr__(obj, "x")
```

Three details matter:

1. The class is searched **first**, even though the instance dictionary usually wins. Python must know whether a data descriptor is there before it is allowed to look at the instance.
2. The search uses **`type(obj)`**, not `obj`. Descriptors and special methods work only when they live on the class, never when stored on the instance.
3. All of the boxes above (except the last one) are the body of one method: **`object.__getattribute__`**. Every class inherits it. Section 4 shows how to replace it, and why you rarely should.

### 2.3 The algorithm in Python

You can write the algorithm yourself. This is a simplified version (no `__slots__`, no metaclass details), but it is close enough to predict almost every real case:

```python
def find_on_class(cls, name):
    for klass in cls.__mro__:
        if name in vars(klass):
            return True, vars(klass)[name]
    return False, None

def is_data_descriptor(attr):
    t = type(attr)
    return hasattr(t, "__get__") and (hasattr(t, "__set__") or hasattr(t, "__delete__"))

def lookup(obj, name):
    found, attr = find_on_class(type(obj), name)
    if found and is_data_descriptor(attr):
        return "data descriptor", type(attr).__get__(attr, obj, type(obj))
    if name in vars(obj):
        return "instance dict", vars(obj)[name]
    if found and hasattr(type(attr), "__get__"):
        return "non-data descriptor", type(attr).__get__(attr, obj, type(obj))
    if found:
        return "class attribute", attr
    return "missing", None


class Base:
    kind = "base kind"

class Demo(Base):
    color = "red"

    @property
    def size(self):
        return 42

    def greet(self):
        return "hi"

    def __repr__(self):
        return "Demo()"

d = Demo()
d.color = "blue"
d.__dict__["size"] = "ignored"
for name in ["color", "kind", "size", "greet", "nope"]:
    print(f"{name:6}", lookup(d, name))
```
```text
color  ('instance dict', 'blue')
kind   ('class attribute', 'base kind')
size   ('data descriptor', 42)
greet  ('non-data descriptor', <bound method Demo.greet of Demo()>)
nope   ('missing', None)
```

Read each line against the picture:

- `color`: the class has a plain string, not a descriptor, so the instance dictionary wins.
- `kind`: not in the instance, found on `Base` through the MRO, returned as it is.
- `size`: `property` is a data descriptor, so it beats the `"ignored"` string sitting in `d.__dict__`.
- `greet`: functions are non-data descriptors, so `__get__` turned the function into a **bound method**. Its repr names the function and the object it is bound to (`Demo()`, from our `__repr__`; without one you would see a memory address).
- `nope`: found nowhere. Real lookup would raise `AttributeError` here.

Notice the trick in the code: it calls `type(attr).__get__(attr, ...)`, not `attr.__get__(...)`. Python looks up special methods on the **type** of an object, and our imitation does the same.

### 2.4 Writing and deleting follow a shorter path

Assignment `obj.x = value` is simpler, because there is no fallback chain:

1. Find `x` on `type(obj)` through the MRO. If it is a descriptor whose type defines **`__set__`**, call `__set__(obj, value)`. Done.
2. Otherwise, store the value in `obj.__dict__["x"]`.

Deletion `del obj.x` is the same with `__delete__` instead of `__set__`. The body of these steps is `object.__setattr__` and `object.__delattr__` (section 5).

This explains a rule you may have hit in core.14: a `property` with no setter makes the attribute read-only. `property` always defines `__set__`, so step 1 always takes over, and `property.__set__` raises `AttributeError` when you did not give it a setter. Python never falls through to step 2.

Assignment **never** looks at plain class attributes. That is why `self.count = self.count + 1` reads the class attribute (lookup falls back to the class) but writes a brand new instance attribute (assignment goes to the instance dictionary). From that moment the instance has its own `count` that hides the class one.

### 2.5 Special methods skip the instance

When Python itself calls a special method, for example `len(obj)` calls `__len__` and `obj + 1` calls `__add__`, it looks the method up **on the type only**. It skips the instance dictionary, and it even skips `__getattribute__` and `__getattr__` (sections 3 and 4).

```python
class Box:
    def __len__(self):
        return 3

b = Box()
b.__len__ = lambda: 99          # stored in the instance dict
print(b.__len__())              # normal attribute lookup: instance dict wins
print(len(b))                   # implicit lookup: type(b).__len__ only
```
```text
99
3
```

Why does Python do this? Speed is one reason: `len()` is called millions of times, and checking the instance dictionary first would slow every call. The deeper reason is correctness for classes themselves: `int` has a `__repr__` meant for *integers*, but `type(int)` (which is `type`) has a `__repr__` meant for *classes*. `repr(int)` must use the second one, so Python looks on the type of the object.

Keep this in mind for section 3: a wrapper that forwards attributes with `__getattr__` does **not** automatically support `len()`, `+`, `[]` or `in`.

#### Predict the output 2.1

```python
class Config:
    debug = False
    tags = []

    @property
    def mode(self):
        return "debug" if self.debug else "normal"

a = Config()
b = Config()
a.debug = True
a.tags.append("x")
b.__dict__["mode"] = "fake"
print(a.mode, b.mode)
print(Config.debug, vars(a), vars(b))
print(b.tags)
del a.debug
print(a.mode)
```

<details><summary>Answer</summary>

```text
debug normal
False {'debug': True} {'mode': 'fake'}
['x']
normal
```

- `a.debug = True` creates an instance attribute on `a` only; `Config.debug` stays `False`.
- `a.tags.append("x")` does **not** assign: it reads `tags` (found on the class) and changes that one shared list. So `b.tags` shows `['x']` too, and neither instance dictionary has `tags`.
- `b.mode` is still `"normal"`: `property` is a data descriptor, so it beats the `"fake"` in `b.__dict__`.
- `del a.debug` removes the instance attribute, so `a.debug` falls back to the class value `False`.

</details>

#### Try it 2.2

Without running anything, write down which step of the picture in section 2.2 answers each lookup, then check with the `lookup()` function from section 2.3:

```python
class Animal:
    legs = 4
    def speak(self):
        return "..."

class Bird(Animal):
    legs = 2

tweety = Bird()
tweety.speak = "chirp"
# tweety.legs   tweety.speak   Bird.legs   tweety.wings
```

<details><summary>Answer</summary>

- `tweety.legs`: no data descriptor, not in the instance dictionary, found on `Bird` first (the MRO is `Bird, Animal, object`), a plain value: **class attribute 2**.
- `tweety.speak`: found on `Animal` as a function (a *non-data* descriptor), but the instance dictionary is checked first and holds `"chirp"`: **instance dict wins**. Calling `tweety.speak()` now fails, because a string is not callable.
- `Bird.legs`: this is lookup on a class, which uses `type(Bird)` (that is `type`) and then the MRO of `Bird` itself. Answer: 2. Section 17 explains class-level lookup.
- `tweety.wings`: found nowhere: `AttributeError` (Bird has no `__getattr__`).

</details>

## 3. `__getattr__`: the fallback hook

### 3.1 Called only when lookup fails

`__getattr__(self, name)` is the last box in the picture. Python calls it **only after normal lookup has failed** with `AttributeError`. If the attribute exists anywhere (instance, class, parents), `__getattr__` is never called.

That makes it safe and cheap: normal attributes run at full speed, and you only pay for the missing ones. It fits three jobs:

1. **Defaults**: answer for names that were never set.
2. **Delegation**: forward unknown names to a wrapped object.
3. **Dynamic names**: compute attributes from data, like keys of a dictionary.

```python
class Settings:
    DEFAULTS = {"theme": "light", "font_size": 12}

    def __init__(self, **values):
        self.__dict__.update(values)

    def __getattr__(self, name):
        print(f"  __getattr__({name!r})")
        try:
            return self.DEFAULTS[name]
        except KeyError:
            raise AttributeError(name) from None

s = Settings(theme="dark")
print(s.theme)          # in the instance dict: hook not called
print(s.font_size)      # missing: hook called, default returned
print(s.DEFAULTS["theme"])  # found on the class: hook not called
try:
    s.volume
except AttributeError as e:
    print("AttributeError:", e)
```
```text
dark
  __getattr__('font_size')
12
light
  __getattr__('volume')
AttributeError: volume
```

The hook ran only for `font_size` and `volume`. Reading `self.DEFAULTS` inside the hook is fine, because `DEFAULTS` exists on the class, so it does not call the hook again.

### 3.2 The contract: missing means `AttributeError`

The one rule for `__getattr__`: **if you do not have the attribute, raise `AttributeError`**. Not `KeyError`, not `None`, not a log message. Many tools depend on it:

- `hasattr(obj, name)` returns `False` only for `AttributeError`; any other exception escapes.
- `getattr(obj, name, default)` returns the default only for `AttributeError`.
- `copy`, `pickle`, `dataclasses` and `inspect` probe objects for optional dunder names like `__deepcopy__` or `__setstate__`, and expect `AttributeError` for "not there".

Here is what goes wrong when the rule is broken:

```python
class Bad:
    def __init__(self, data):
        self.data = data

    def __getattr__(self, name):
        return self.data[name]          # KeyError for a missing name

class AlsoBad:
    def __getattr__(self, name):
        return None                     # pretends every name exists

b = Bad({"x": 1})
print(b.x)
try:
    print(hasattr(b, "y"))
except Exception as e:
    print("hasattr raised", type(e).__name__)

a = AlsoBad()
print(hasattr(a, "anything"), a.typo_here)
```
```text
1
hasattr raised KeyError
True None
```

`Bad` makes `hasattr` crash. `AlsoBad` is worse in a quiet way: every typo returns `None` instead of an error, and the bug shows up far away. It also tells every tool that probes for optional methods "yes, I have that", which is a lie. The fix in both cases is the pattern from `Settings`: `raise AttributeError(name) from None`. (`from None` hides the original `KeyError` from the traceback, core.14 section 18.)

### 3.3 Delegation and its limit

`__getattr__` is the classic tool for a **wrapper** that adds a little behavior and forwards everything else:

```python
class LoggedList:
    def __init__(self, items):
        self._items = list(items)
        self.log = []

    def __getattr__(self, name):
        self.log.append(name)
        return getattr(self._items, name)

nums = LoggedList([3, 1, 2])
nums.append(5)
nums.sort()
print(nums._items, nums.count(1))
print(nums.log)
try:
    print(len(nums))
except TypeError as e:
    print("len(nums) raised", type(e).__name__)
```
```text
[1, 2, 3, 5] 1
['append', 'sort', 'count']
len(nums) raised TypeError
```

`append`, `sort` and `count` were not found on `LoggedList`, so they were forwarded to the real list. They came back as bound methods of the list, so calling them changed `_items`. But `len(nums)` fails: as section 2.5 showed, `len()` looks for `__len__` on the **type** and never asks `__getattr__`. A wrapper that should support `len`, iteration or indexing must define `__len__`, `__iter__`, `__getitem__` itself (each can simply forward to `self._items`).

### 3.4 The recursion trap

The most famous `__getattr__` bug looks innocent:

```python
import copy

class Wrapper:
    def __init__(self, target):
        self.target = target

    def __getattr__(self, name):
        return getattr(self.target, name)

w = Wrapper("hello")
print(w.upper())
try:
    copy.copy(w)
except RecursionError as e:
    print("copy.copy:", type(e).__name__)
```
```text
HELLO
copy.copy: RecursionError
```

Why did copying crash? `copy.copy` creates the new object **without calling `__init__`**, then probes it for methods such as `__setstate__`. On that bare object `self.target` does not exist yet. So reading `self.target` inside `__getattr__` fails, which calls `__getattr__("target")`, which reads `self.target` again, and so on until Python gives up with `RecursionError`.

Any attribute that `__getattr__` itself uses must be read in a way that cannot call `__getattr__` again. Two safe ways:

```python
import copy

class Wrapper:
    def __init__(self, target):
        self.target = target

    def __getattr__(self, name):
        if name.startswith("__") or name == "target":
            raise AttributeError(name)          # never forward dunders or our own field
        return getattr(self.target, name)

class Wrapper2:
    def __init__(self, target):
        self.target = target

    def __getattr__(self, name):
        try:
            target = vars(self)["target"]       # plain dict read: no attribute lookup
        except KeyError:
            raise AttributeError(name) from None
        return getattr(target, name)

for cls in (Wrapper, Wrapper2):
    w2 = copy.copy(cls("hello"))
    print(cls.__name__, w2.upper(), w2.target)
```
```text
Wrapper HELLO hello
Wrapper2 HELLO hello
```

Refusing to forward dunder names is a good habit for any delegating `__getattr__`: it stops the wrapper from pretending to support protocols (`__deepcopy__`, `__getstate__`) that it does not really support.

### 3.5 `__dir__`: telling tools what exists

`dir(obj)` lists the names an object has. It cannot know about names that `__getattr__` invents, so tab completion in the REPL and in editors will not show them. A class with dynamic attributes can define `__dir__` to return a list (Python sorts it for you):

```python
class Row:
    def __init__(self, **fields):
        self._fields = fields

    def __getattr__(self, name):
        try:
            return self._fields[name]
        except KeyError:
            raise AttributeError(name) from None

    def __dir__(self):
        return list(super().__dir__()) + list(self._fields)

r = Row(id=7, title="Dune")
print(r.title)
print([n for n in dir(r) if not n.startswith("_")])
```
```text
Dune
['id', 'title']
```

#### Predict the output 3.1

```python
class Fallback:
    color = "red"

    def __init__(self):
        self.size = 10

    def __getattr__(self, name):
        return f"<default {name}>"

f = Fallback()
print(f.size)
print(f.color)
print(f.weight)
f.weight = 5
print(f.weight)
del f.weight
print(f.weight)
print(hasattr(f, "anything"))
```

<details><summary>Answer</summary>

```text
10
red
<default weight>
5
<default weight>
True
```

`size` (instance) and `color` (class) are found normally, so the hook is not called. `weight` is missing at first, so the hook answers. After `f.weight = 5` the instance has it and the hook is skipped. After `del`, it is missing again. The last line is the problem with this class: because the hook never raises `AttributeError`, `hasattr` says `True` for **every** name.

</details>

#### Try it 3.2

Write a class `Defaults(primary, fallback)` that takes two dictionaries. Reading `obj.key` returns `primary[key]` if present, else `fallback[key]`, else raises `AttributeError`. `hasattr(obj, "missing")` must be `False`, and `copy.copy(obj)` must not crash. Which attributes of your own does `__getattr__` read, and how did you protect them?

<details><summary>Answer</summary>

```python
import copy

class Defaults:
    def __init__(self, primary, fallback):
        self._primary = primary
        self._fallback = fallback

    def __getattr__(self, name):
        if name.startswith("_"):
            raise AttributeError(name)      # protects _primary, _fallback and dunders
        for source in (self._primary, self._fallback):
            if name in source:
                return source[name]
        raise AttributeError(name)

d = Defaults({"a": 1}, {"a": 0, "b": 2})
print(d.a, d.b, hasattr(d, "missing"))
print(copy.copy(d).b)
```
```text
1 2 False
2
```

The hook reads `self._primary` and `self._fallback`. On a copied object they may be missing while `copy` probes it; then the lookup comes back to `__getattr__("_primary")`, which must fail at once. Refusing every name that starts with `_` handles that and the dunder probes in one line.

</details>

## 4. `__getattribute__`: the every-time hook

### 4.1 Replacing the whole algorithm

`__getattr__` is called when lookup fails. `__getattribute__(self, name)` is called for **every** attribute read on an instance: found or missing, data or method, from outside or from `self.x` inside a method. It *is* the lookup algorithm. The version every class inherits is `object.__getattribute__`, the picture from section 2.2.

When you define your own, you take over everything, so you almost always do a little extra work and then hand the real lookup back to `object`:

```python
class Counted:
    def __init__(self, x):
        self.x = x

    def __getattribute__(self, name):
        if not name.startswith("__"):
            print(f"  get {name!r}")
        return super().__getattribute__(name)    # the normal algorithm

    def double(self):
        return self.x * 2

c = Counted(5)
print(c.x)
print(c.double())
```
```text
  get 'x'
5
  get 'double'
  get 'x'
10
```

Calling `c.double()` printed **two** lines: one for looking up `double` (it returned a bound method), and one for `self.x` inside the method. Every attribute read goes through the hook, including the ones you do not see.

### 4.2 The recursion trap, again

Inside `__getattribute__`, writing `self.anything` calls `__getattribute__` again. Even `self.__dict__` does, because `__dict__` is an attribute too. So the hook must reach its own data through `super().__getattribute__(...)` or `object.__getattribute__(self, ...)`:

```python
class Broken:
    def __init__(self):
        self.hits = 0                           # assignment: no read, fine

    def __getattribute__(self, name):
        self.hits += 1                          # reads self.hits -> calls this again
        return super().__getattribute__(name)

class Fixed:
    def __init__(self):
        self.hits = 0
        self.value = 10

    def __getattribute__(self, name):
        d = object.__getattribute__(self, "__dict__")   # safe: no hook involved
        d["hits"] = d["hits"] + 1
        return object.__getattribute__(self, name)

try:
    Broken().hits
except RecursionError as e:
    print("Broken:", type(e).__name__)

f = Fixed()
f.value; f.value; f.value
print("hits:", object.__getattribute__(f, "__dict__")["hits"])
```
```text
Broken: RecursionError
hits: 3
```

Even reading the counter for the final `print` needs the long form, or the act of reading it would add one more hit. That is the price of `__getattribute__`: you cannot touch your own object normally.

### 4.3 How the two hooks work together

If a class defines both hooks, Python does this for `obj.x`:

```text
try:
    return type(obj).__getattribute__(obj, "x")
except AttributeError:
    if type(obj) defines __getattr__:
        return type(obj).__getattr__(obj, "x")
    raise
```

Any `AttributeError` raised *anywhere inside* `__getattribute__` triggers the fallback. That includes an `AttributeError` raised by code running inside a property getter, and this causes one of the most confusing bugs in Python:

```python
class Account:
    ALIASES = {"bal": "balance"}            # old names still accepted

    def __init__(self, balance):
        self._balance = balance

    @property
    def balance(self):
        return self._balanse                # typo -> AttributeError inside the property

    def __getattr__(self, name):
        if name in self.ALIASES:
            return getattr(self, self.ALIASES[name])
        raise AttributeError(f"Account has no attribute {name!r}")

a = Account(100)
try:
    print(a.balance)
except AttributeError as e:
    print("AttributeError:", e)
```
```text
AttributeError: Account has no attribute 'balance'
```

Read the message: "Account has no attribute `'balance'`". But `balance` clearly exists; it is right there as a property. Here is what really happened:

1. `a.balance` found the property and ran its getter.
2. The typo `self._balanse` failed, so the getter raised `AttributeError` (after a quick, failed visit to `__getattr__("_balanse")`).
3. That error escaped from the normal lookup of `balance`. Python cannot tell "the getter crashed with `AttributeError`" apart from "`balance` does not exist", so it called `__getattr__("balance")`.
4. `__getattr__` did not know `balance` and raised its own error, which replaced the real one.

The real mistake (a typo on `_balanse`) is gone from the message, and you will spend your time staring at a property that obviously exists. If `__getattr__` returned a default instead of raising, it is worse: you get a wrong value and no error at all (Predict 4.1 shows that version).

Two lessons. When a class has both properties and `__getattr__`, an error message about a property that "does not exist" means: look **inside** the getter. And a getter that might fail with `AttributeError` for a reason of its own should catch it and raise a different exception (for example `RuntimeError`), so the real cause is not swallowed by the fallback.

### 4.4 When to use `__getattribute__`

Rarely. Every attribute read, including every method call and every `self.x`, now runs your Python function, so the class gets slower everywhere, and every line of the hook is a recursion risk. Prefer, in this order:

| Need | Use |
|---|---|
| Control one attribute | `property` or a descriptor (sections 6 to 12) |
| Answer for missing names, forward to a wrapped object | `__getattr__` |
| Watch or block **every** read, including existing attributes | `__getattribute__` |

Real uses of the last row are narrow: debugging tools that trace access, security proxies that must also block existing attributes, and libraries that load data lazily. If you write one, keep it tiny and always end with `super().__getattribute__(name)`.

#### Predict the output 4.1

```python
class Both:
    kind = "class"

    def __init__(self):
        self.x = 1

    def __getattribute__(self, name):
        print("getattribute", name)
        return super().__getattribute__(name)

    def __getattr__(self, name):
        print("getattr", name)
        return 0

    @property
    def broken(self):
        raise AttributeError("inner")

b = Both()
print(b.x)
print(b.kind)
print(b.y)
print(b.broken)
```

<details><summary>Answer</summary>

```text
getattribute x
1
getattribute kind
class
getattribute y
getattr y
0
getattribute broken
getattr broken
0
```

`__getattribute__` runs for every read. For `x` and `kind` it succeeds, so `__getattr__` is never called. For `y` the normal lookup fails, so `__getattr__` answers `0`. For `broken`, the property runs and raises `AttributeError("inner")`; Python cannot tell that apart from "not found", so `__getattr__("broken")` runs and the result is `0`. The message `"inner"` is lost.

</details>

## 5. `__setattr__` and `__delattr__`

### 5.1 Every assignment goes through one method

`obj.x = value` calls `type(obj).__setattr__(obj, "x", value)`. `del obj.x` calls `type(obj).__delattr__(obj, "x")`. The defaults, `object.__setattr__` and `object.__delattr__`, run the steps from section 2.4 (descriptor `__set__` first, else the instance dictionary).

Unlike `__getattr__`, `__setattr__` has no "only when missing" version: it runs for **every** assignment, including the ones in `__init__`. And just like `__getattribute__`, writing `self.x = ...` inside it calls it again. So the body must store the value through the default:

```python
class User:
    def __init__(self, name, email):
        self.name = name
        self.email = email

    def __setattr__(self, name, value):
        if name == "email":
            value = value.strip().lower()
        super().__setattr__(name, value)        # the default: descriptors, then __dict__

u = User("Asha", "  Asha@Example.COM ")
print(u.email)
u.email = "NEW@Mail.com"
print(u.email, vars(u))
```
```text
asha@example.com
new@mail.com {'name': 'Asha', 'email': 'new@mail.com'}
```

The assignments inside `__init__` went through the hook as well, so the email was cleaned from the very first value.

### 5.2 `super().__setattr__` versus `self.__dict__[name]`

You will see two ways to store the value inside `__setattr__`:

```python
super().__setattr__(name, value)      # recommended
self.__dict__[name] = value           # bypass
```

The first runs the full default algorithm: if the class has a property or descriptor for that name, its `__set__` runs. The second writes straight into the instance dictionary and silently skips any property, descriptor or `__slots__` entry. Use the bypass only when you *mean* to skip descriptors, and say so in a comment.

### 5.3 Frozen objects

A classic use of these hooks is an object that cannot change after `__init__`: block `__setattr__` and `__delattr__` (raise `AttributeError`), and have `__init__` store its values with `object.__setattr__(self, name, value)`, which skips the hook. This is exactly how `@dataclass(frozen=True)` works (core.15): it generates a `__setattr__` that raises `FrozenInstanceError` (a subclass of `AttributeError`), and its generated `__init__` uses `object.__setattr__`. "Frozen" is a convention, not a wall: `object.__setattr__(p, "x", 9)` still works from outside. Python has no truly private or constant attributes; these hooks stop accidents, not determined code.

### 5.4 The "set only during `__init__`" pattern and its trap

Sometimes you want assignments to work while `__init__` runs and then stop. A flag does it, but the obvious code has a trap:

```python
class Locked:
    def __init__(self, a, b):
        self.a = a
        self.b = b
        object.__setattr__(self, "_locked", True)

    def __setattr__(self, name, value):
        if getattr(self, "_locked", False):     # self._locked would fail during __init__
            raise AttributeError(f"{type(self).__name__} is locked: {name!r}")
        super().__setattr__(name, value)

obj = Locked(1, 2)
print(obj.a, obj.b)
try:
    obj.a = 10
except AttributeError as e:
    print("AttributeError:", e)
```
```text
1 2
AttributeError: Locked is locked: 'a'
```

While `__init__` is running, `_locked` does not exist yet. Reading it as `self._locked` would raise `AttributeError` inside `__setattr__`, and the first assignment would fail. `getattr(self, "_locked", False)` says "not locked yet" instead.

#### Try it 5.1

Write a class `Temperature` with one attribute `celsius`. Every assignment must store a `float` (so `t.celsius = 20` stores `20.0`), assigning a value below -273.15 raises `ValueError`, and `del t.celsius` raises `AttributeError`. Use `__setattr__` and `__delattr__`, not a property. Then answer: why might a property be the better tool here?

<details><summary>Answer</summary>

```python
class Temperature:
    def __init__(self, celsius):
        self.celsius = celsius

    def __setattr__(self, name, value):
        if name == "celsius":
            value = float(value)
            if value < -273.15:
                raise ValueError(f"below absolute zero: {value}")
        super().__setattr__(name, value)

    def __delattr__(self, name):
        raise AttributeError(f"cannot delete {name!r}")

t = Temperature(20)
print(t.celsius)
for bad in (lambda: setattr(t, "celsius", -300), lambda: delattr(t, "celsius")):
    try:
        bad()
    except (ValueError, AttributeError) as e:
        print(type(e).__name__, e)
```
```text
20.0
ValueError below absolute zero: -300.0
AttributeError cannot delete 'celsius'
```

A property is better because the rule concerns **one** attribute. `__setattr__` runs for every assignment, so the `if name == "celsius"` check costs time on all of them, and the rule is hidden in a general method instead of sitting next to the attribute. `__setattr__` is the right tool when the rule applies to **all** attributes (freezing, logging, normalizing every name).

</details>

## 6. Descriptors: the protocol

### 6.1 What a descriptor is

A **descriptor** is any object whose class defines at least one of these methods, **stored as an attribute of a class**:

```python
def __get__(self, instance, owner): ...     # reading:   instance.attr  or  Owner.attr
def __set__(self, instance, value): ...     # writing:   instance.attr = value
def __delete__(self, instance): ...         # deleting:  del instance.attr
```

There are three objects in play, and keeping them apart is half of understanding descriptors:

- `self` is the **descriptor** object, the thing stored on the class (there is one per attribute, shared by all instances);
- `instance` is the **object the attribute was accessed through** (the `p` in `p.price`), or `None` when it was accessed on the class;
- `owner` is the **class** of the instance, `type(instance)`, or the class you accessed the attribute through when there is no instance. (It is not necessarily the class that defines the descriptor: Predict 6.1 shows a subclass.)

The rule from section 2.2 decides when these methods run: only when the descriptor sits on the **class**. Store the same object in an instance dictionary and it is just a plain value.

### 6.2 Watching the protocol work

A descriptor that prints every call makes the protocol visible:

```python
class Traced:
    def __get__(self, instance, owner):
        print(f"  __get__(instance={instance!r}, owner={owner.__name__})")
        return 42

    def __set__(self, instance, value):
        print(f"  __set__(instance={instance!r}, value={value!r})")

    def __delete__(self, instance):
        print(f"  __delete__(instance={instance!r})")


class Thing:
    attr = Traced()

    def __repr__(self):
        return "Thing()"

t = Thing()
print("read via instance:", t.attr)
print("read via class:", Thing.attr)
t.attr = 7
del t.attr
print("instance dict:", vars(t))
t.__dict__["plain"] = Traced()
print("descriptor stored on instance:", type(t.plain).__name__)
```
```text
  __get__(instance=Thing(), owner=Thing)
read via instance: 42
  __get__(instance=None, owner=Thing)
read via class: 42
  __set__(instance=Thing(), value=7)
  __delete__(instance=Thing())
instance dict: {}
descriptor stored on instance: Traced
```

Every read, write and delete of `t.attr` became a method call, and nothing was ever stored in `t.__dict__`. Reading on the class called `__get__` with `instance=None`. The last line shows the rule from section 2.2: the `Traced` object stored in the instance dictionary did nothing special; Python simply returned it.

### 6.3 The `instance is None` case

When code reads `Owner.attr`, there is no instance. The convention is: **return the descriptor itself**. Then `Owner.attr` gives you the descriptor object, which is useful for introspection (`Owner.price.name`, help texts, ORMs listing their fields). `property` follows this convention:

```python
class Field:
    def __get__(self, instance, owner):
        if instance is None:
            return self                     # accessed on the class
        return instance.__dict__.get("value", 0)

class Careless:
    def __get__(self, instance, owner):
        return instance.__dict__.get("value", 0)    # forgets the None case

class Model:
    good = Field()
    bad = Careless()
    @property
    def prop(self):
        return 1

print(type(Model.good).__name__, type(Model.prop).__name__)
print(Model().good, Model().bad)
try:
    Model.bad
except AttributeError as e:
    print("Model.bad raised", type(e).__name__)
```
```text
Field property
0 0
Model.bad raised AttributeError
```

`Careless` works on instances and crashes on the class, because it reads `None.__dict__`. Tools like `help()`, `inspect` and documentation generators read attributes on the class, so this bug appears in surprising places. Always handle `instance is None` first.

### 6.4 A descriptor need not store anything

A descriptor's `__get__` can compute its value, for example `return instance.celsius * 9 / 5 + 32` for a `fahrenheit` attribute. That is exactly what a read-only `@property` does, and section 10 shows that `property` is itself a descriptor.

#### Predict the output 6.1

```python
class Echo:
    def __get__(self, instance, owner):
        if instance is None:
            return "class access"
        return f"instance access ({type(instance).__name__})"

class A:
    e = Echo()

class B(A):
    pass

print(A.e)
print(B().e)
b = B()
b.e = "stored"
print(b.e)
print(vars(b))
```

<details><summary>Answer</summary>

```text
class access
instance access (B)
stored
{'e': 'stored'}
```

`A.e` has no instance, so `__get__` gets `None`. `B().e` finds `e` on `A` through the MRO; the descriptor still runs, and `instance` is the `B` object. `Echo` defines only `__get__`, so it is a **non-data** descriptor: `b.e = "stored"` goes straight into the instance dictionary (there is no `__set__` to call), and from then on the instance value wins.

</details>

## 7. Data vs non-data descriptors and precedence

### 7.1 Two kinds, two priorities

Predict 6.1 showed that defining `__set__` or not changes the behavior completely. The two kinds have names:

| Kind | Defines | Compared to the instance `__dict__` | Examples |
|---|---|---|---|
| **data descriptor** | `__get__` and `__set__` and/or `__delete__` | **wins**: the dict cannot hide it | `property`, `__slots__` members, validated fields |
| **non-data descriptor** | only `__get__` | **loses**: a dict entry hides it | functions (methods), `classmethod`, `staticmethod`, `cached_property` |

The difference is not an accident. Each kind is designed for its job:

- A **validated field** must run its check on every assignment. If an instance could hide it with a plain dict entry, validation could be skipped. So it must be a data descriptor.
- A **method** may reasonably be replaced on one instance (a test that swaps one method on one object, or a cache that stores a computed value). So functions are non-data descriptors and the instance dictionary may hide them.

### 7.2 Precedence, side by side

```python
class DataDesc:
    def __get__(self, instance, owner):
        return "from data descriptor"
    def __set__(self, instance, value):
        print(f"  DataDesc.__set__ got {value!r}, stores nothing")

class NonDataDesc:
    def __get__(self, instance, owner):
        return "from non-data descriptor"

class C:
    d = DataDesc()
    n = NonDataDesc()

c = C()
c.d = "assigned"        # goes to DataDesc.__set__
c.n = "assigned"        # no __set__: goes to the instance dict
c.__dict__["d"] = "forced into dict"
print(c.d)
print(c.n)
print(vars(c))
del c.n
print(c.n)
```
```text
  DataDesc.__set__ got 'assigned', stores nothing
from data descriptor
assigned
{'n': 'assigned', 'd': 'forced into dict'}
from non-data descriptor
```

`c.__dict__["d"] = ...` really put a value in the instance dictionary, but `c.d` still answers from the data descriptor: it is checked before the dictionary. For `n`, the instance value hides the descriptor until it is deleted.

### 7.3 A read-only data descriptor

To make an attribute read-only you must define `__set__` (so the descriptor is a data descriptor and wins) and make it **raise** `AttributeError`. Leaving `__set__` out does **not** make the attribute read-only: it makes the descriptor non-data, and `obj.attr = 5` quietly creates an instance attribute that hides it from then on, exactly like `b.e = "stored"` in Predict 6.1.

This is why a property without a setter is read-only: `property` always defines `__set__`, and it raises when no setter was given.

#### Predict the output 7.1

```python
class Loud:
    def __init__(self, label):
        self.label = label
    def __get__(self, instance, owner):
        return f"{self.label}.get"

class LoudData(Loud):
    def __delete__(self, instance):
        print(f"{self.label}.delete")

class K:
    a = Loud("a")
    b = LoudData("b")

k = K()
k.__dict__.update(a="dict a", b="dict b")
print(k.a)
print(k.b)
del k.b
try:
    k.b = 1
except AttributeError as e:
    print("assignment failed:", type(e).__name__)
```

<details><summary>Answer</summary>

```text
dict a
b.get
b.delete
assignment failed: AttributeError
```

`LoudData` defines `__delete__`, and **that alone** makes it a data descriptor, even without `__set__`. So `k.b` ignores `"dict b"` and asks the descriptor. `del k.b` calls `__delete__`. Assignment `k.b = 1` finds a data descriptor with no `__set__`; Python does not fall back to the instance dictionary and raises `AttributeError` instead. `Loud` (only `__get__`) is non-data, so `"dict a"` wins.

</details>

## 8. `__set_name__` and where to store per-instance values

### 8.1 A descriptor needs its name

A descriptor that validates should say *which* field was wrong. A descriptor that stores values needs a key to store them under. Both need the attribute's **name**. But the descriptor object is created by `Positive()` on the right side of `price = Positive()`, before Python has assigned it to anything, so it cannot see the name on the left.

Old code solved this by typing the name twice: `price = Positive("price")`. Since Python 3.6 there is a hook: when a class is created, Python calls `__set_name__(self, owner, name)` on every object in the class body that has one.

```python
class Named:
    def __set_name__(self, owner, name):
        print(f"  __set_name__(owner={owner.__name__}, name={name!r})")
        self.name = name

print("before class")
class Order:
    total = Named()
    discount = Named()
print("after class")

o1, o2 = Order(), Order()
print(Order.total.name, Order.discount.name)
```
```text
before class
  __set_name__(owner=Order, name='total')
  __set_name__(owner=Order, name='discount')
after class
total discount
```

`__set_name__` ran **once per descriptor, while the class was being created**, in the order the attributes appear in the body. Creating instances did not call it again. (Section 17 shows exactly where in class creation this happens.)

One trap: the hook runs only for attributes present in the **class body**. A descriptor attached later is not told its name, and you must call the hook yourself:

```python
class Named:
    def __set_name__(self, owner, name):
        self.name = name

class Order:
    pass

Order.late = Named()
print(hasattr(Order.late, "name"))
Order.late.__set_name__(Order, "late")
print(Order.late.name)
```
```text
False
late
```

### 8.2 Where do the values go?

There is **one** descriptor object per class attribute, shared by every instance. That fact makes the storage question important. Here is the most common descriptor bug of all:

```python
class Positive:
    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return self.value                       # BUG: stored on the descriptor

    def __set__(self, instance, value):
        if value <= 0:
            raise ValueError(f"{self.name} must be > 0")
        self.value = value                      # BUG: one slot for all instances

class Product:
    price = Positive()
    def __init__(self, price):
        self.price = price

pen = Product(10)
car = Product(900000)
print(pen.price, car.price)
```
```text
900000 900000
```

The pen now costs as much as the car. `self` inside `__set__` is the descriptor, and there is only one, so every product writes into the same `self.value`. The value must be stored **per instance**, keyed by `instance`.

### 8.3 Three safe places to store

**1. The instance dictionary, under the same name.** This is the most common choice for a data descriptor:

```python
class Positive:
    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner):
        if instance is None:
            return self
        try:
            return instance.__dict__[self.name]
        except KeyError:
            raise AttributeError(self.name) from None

    def __set__(self, instance, value):
        if value <= 0:
            raise ValueError(f"{self.name} must be > 0, got {value!r}")
        instance.__dict__[self.name] = value

class Product:
    price = Positive()
    def __init__(self, price):
        self.price = price

pen, car = Product(10), Product(900000)
print(pen.price, car.price, vars(pen))
try:
    Product.__new__(Product).price          # an object whose price was never set
except AttributeError as e:
    print("unset field raised AttributeError:", e)
```
```text
10 900000 {'price': 10}
unset field raised AttributeError: price
```

It looks as if the instance dictionary should hide the descriptor (same name!), but it cannot: `Positive` is a **data** descriptor, so it is checked first and the dictionary entry is only reached through `instance.__dict__[...]` inside the descriptor. A nice side effect: `vars(pen)` shows `{'price': 10}`, so printing and debugging look normal. Notice also that a missing value raises `AttributeError`, not `KeyError`, to keep the contract from section 3.2.

**2. The instance dictionary, under a private name** such as `_price`. Then `getattr(instance, "_price")` and `setattr(instance, "_price", value)` work, and anything that reads the dictionary sees `_price`. This is what a hand-written property does (`self._price`). It is fine, but the name-mangling-like prefix is one more thing to keep consistent.

**3. A dictionary on the descriptor, keyed by instance.** This is the only option when the instances have no `__dict__` (a class with `__slots__`, section 13). A plain `dict` would keep every instance alive forever, so real code uses `weakref.WeakKeyDictionary`, a dictionary from the standard library that drops an entry when its key object is garbage collected. It requires the instances to be hashable and weak-referenceable, so it is the least general choice. Use it only when the first option is impossible.

#### Try it 8.1

The descriptor below has three bugs. Find them before reading the answer.

```python
class Label:
    def __get__(self, instance, owner):
        return instance.__dict__[self.name]

    def __set__(self, instance, value):
        self.current = str(value).strip()
        instance.__dict__[self.name] = self.current

class Item:
    title = Label()
```

<details><summary>Answer</summary>

1. **No `__set_name__`**, so `self.name` never exists: the first assignment fails with `AttributeError` on `self.name`. Add `def __set_name__(self, owner, name): self.name = name`.
2. **No `instance is None` check**, so `Item.title` crashes on `None.__dict__`. Return `self` when `instance is None`.
3. **`self.current` is shared state** on the one descriptor object. It does not break reading here, but it is the shared-storage bug waiting to happen: the next person to "simplify" `__get__` to `return self.current` makes all items share one title. Use a local variable.

A fourth point for style: a missing value raises `KeyError` from `__get__`. Catch it and raise `AttributeError` so `hasattr(item, "title")` works.

</details>

## 9. How functions become bound methods

This section is the first learning outcome. By the end you should be able to explain, step by step, what happens in `d.speak("hi")`.

### 9.1 A method is just a function stored on a class

When Python runs a `def` inside a class body, it creates an ordinary function object and stores it in the class dictionary. There is no special "method" object at that moment:

```python
class Dog:
    def __init__(self, name):
        self.name = name

    def speak(self, word):
        return f"{self.name} says {word}"

    def __repr__(self):
        return f"Dog({self.name!r})"

raw = Dog.__dict__["speak"]
print(type(raw).__name__)
print(Dog.speak is raw)                     # class access gives the plain function
print(raw(Dog("Rex"), "woof"))              # call it like any function
print(hasattr(type(raw), "__get__"), hasattr(type(raw), "__set__"))
```
```text
function
True
Rex says woof
True False
```

So `Dog.speak` is just the function, and you can call it with any object as the first argument. The last line is the key: the class of every function, `function`, defines `__get__` but not `__set__`. **Every function is a non-data descriptor.** That single fact is the whole secret of methods.

### 9.2 What `function.__get__` returns

Reading `d.speak` follows the algorithm from section 2.2: `speak` is found on `Dog`, it is a non-data descriptor, `d.__dict__` has no `speak`, so Python returns `type(raw).__get__(raw, d, Dog)`. That call builds a **bound method**: a small object that remembers two things, the function and the instance.

```python
import types

class Dog:
    def __init__(self, name):
        self.name = name
    def speak(self, word):
        return f"{self.name} says {word}"
    def __repr__(self):
        return f"Dog({self.name!r})"

d = Dog("Rex")
m = d.speak
print(m)
print(type(m) is types.MethodType)
print(m.__func__ is Dog.__dict__["speak"], m.__self__ is d)

manual = Dog.__dict__["speak"].__get__(d, Dog)   # what d.speak does for you
print(manual("hi"), m("hi"), m.__func__(m.__self__, "hi"))
```
```text
<bound method Dog.speak of Dog('Rex')>
True
True True
Rex says hi Rex says hi Rex says hi
```

All three calls on the last line are the same call. When you call a bound method, it calls its `__func__` with its `__self__` inserted as the first argument. That is where `self` comes from: **nobody passes `self`; the bound method inserts it.**

### 9.3 `d.speak("hi")` step by step

Here is the complete story, the answer to learning outcome 1:

1. Python evaluates `d.speak`. That calls `type(d).__getattribute__(d, "speak")`, which is `object.__getattribute__`.
2. The algorithm searches `type(d).__mro__` (`Dog`, then `object`) and finds `"speak"` in `Dog.__dict__`: a function object.
3. The function's type defines `__get__` but not `__set__`, so it is a **non-data** descriptor. Python checks `d.__dict__` first; it has only `name`, no `speak`.
4. So Python calls `function.__get__(speak_function, d, Dog)`.
5. Because `instance` is not `None`, `__get__` returns `types.MethodType(speak_function, d)`: a new bound method with `__func__ = speak_function` and `__self__ = d`.
6. Python calls that bound method with `("hi")`.
7. The bound method calls `__func__(__self__, "hi")`, that is `speak_function(d, "hi")`. Inside, `self` is `d`.

If `instance` is `None` (step 5 when you write `Dog.speak`), `function.__get__` simply returns the function itself. Python 2 had "unbound method" objects for that case; Python 3 removed them.

### 9.4 Consequences you can now explain

**`d.speak is d.speak` is `False`.** Each lookup runs step 5 again and builds a fresh bound method:

```python
class Dog:
    def speak(self):
        return "woof"

d = Dog()
print(d.speak is d.speak)       # two different bound-method objects
print(d.speak == d.speak)       # equal: same __func__ and same __self__
saved = d.speak
print(saved is saved)
print(Dog.speak is Dog.speak)   # class access returns the one function
```
```text
False
True
True
True
```

Do not compare methods with `is`. Also do not trust `id(d.speak) == id(d.speak)`: the first bound method is freed right after `id()` reads it, and the second one often reuses the same memory, so the ids can match even though the objects are different. That is a CPython implementation detail, not a rule.

**A function stored on the instance is not bound.** The descriptor protocol only works for attributes found on the class, so a function in `d.__dict__` is returned as it is, and no `self` is inserted (you saw this in core.14 section 9.2).

**You can bind any function to any object.** `types.MethodType(func, obj)` is the same as `func.__get__(obj)`:

```python
import types

class Dog:
    def __init__(self, name):
        self.name = name

def wag(self, times):
    return f"{self.name} wags {times} times"

rex = Dog("Rex")
rex.wag = types.MethodType(wag, rex)     # bound to rex only
print(rex.wag(3))
print(hasattr(Dog("Fido"), "wag"))
```
```text
Rex wags 3 times
False
```

**A bound method keeps its object alive.** `callback = d.speak` holds a reference to `d` through `__self__`, so `d` cannot be garbage collected while the callback is stored. That is usually what you want (a button that calls `window.close` needs the window), but remember it when you store callbacks in long-lived lists.

**Built-in methods behave the same way.** `[1, 2].append` is a `builtin_function_or_method`, not a `types.MethodType`, but it also has a `__self__` (the list) and is created fresh on each lookup.

### 9.5 Payoff: fixing the class-based decorator from core.15

In core.15 (section 18) a class-based decorator `CountCalls` lost `self` when used on a method, and the chapter said the cure was the descriptor protocol. Now you can see why: `Dog.__dict__["bark"]` is a `CountCalls` object, and `CountCalls` has no `__get__`, so `d.bark` returns it unchanged and nothing inserts `self`. The fix is to make it a non-data descriptor that binds itself like a function does:

```python
import types

class CountCalls:
    def __init__(self, func):
        self.func = func
        self.calls = 0

    def __call__(self, *args, **kwargs):
        self.calls += 1
        return self.func(*args, **kwargs)

    def __get__(self, instance, owner):
        if instance is None:
            return self
        return types.MethodType(self, instance)     # bind like a function would

class Dog:
    @CountCalls
    def bark(self, times):
        return "woof " * times

d = Dog()
print(d.bark(2))
print(d.bark(1))
print(Dog.bark.calls)
```
```text
woof woof 
woof 
2
```

`d.bark` now returns a bound method whose `__func__` is the `CountCalls` object and whose `__self__` is `d`. Calling it calls `CountCalls.__call__(d, 2)`, which passes `d` on to the real `bark` as `self`.

#### Predict the output 9.1

```python
class Greeter:
    greeting = "Hello"

    def greet(self, name):
        return f"{self.greeting}, {name}"

g = Greeter()
f = Greeter.greet
m = g.greet
print(f(g, "Asha"))
print(m("Ben"))
print(m.__self__ is g, m.__func__ is f)
g.greeting = "Hi"
print(m("Chen"))
g.greet = lambda name: f"lambda {name}"
print(g.greet("Dev"), m("Eve"))
```

<details><summary>Answer</summary>

```text
Hello, Asha
Hello, Ben
True True
Hi, Chen
lambda Dev Hi, Eve
```

`Greeter.greet` is the plain function, so `f(g, "Asha")` passes `self` by hand. `m` is bound to `g`; its `__func__` is the very same function `f`. Changing `g.greeting` after creating `m` still shows up, because `m` stores the object `g`, not a copy of its data. Putting a lambda in `g.__dict__` hides the method for new lookups (functions are non-data descriptors), but `m` was created earlier and still calls the original function.

</details>

#### Try it 9.2

Explain in your own words, in four or five sentences, without looking at section 9.3: "Why does `self` hold the object, when I never pass it?" Use the words *non-data descriptor*, `__get__`, *bound method*, `__self__` and `__func__`.

<details><summary>Answer</summary>

A model answer: A method is a plain function stored in the class dictionary, and functions are non-data descriptors because their type defines `__get__`. When I write `obj.method`, attribute lookup finds the function on the class, sees no entry in `obj.__dict__` that hides it, and calls the function's `__get__` with `obj` as the instance. `__get__` returns a new bound method object that remembers the function in `__func__` and the object in `__self__`. When I call the bound method with some arguments, it calls `__func__(__self__, *arguments)`. So `self` is not magic: the bound method inserts the object as the first argument.

</details>

## 10. How `property`, `classmethod` and `staticmethod` really work

### 10.1 They are just descriptors

`property`, `classmethod` and `staticmethod` are written in C, but nothing about them needs C. Each is a small descriptor class, and writing them in Python is the best way to stop seeing them as magic.

| Built-in | Kind | What `__get__(instance, owner)` returns |
|---|---|---|
| function | non-data | `instance` is `None`: the function; else a bound method with `__self__ = instance` |
| `classmethod` | non-data | a bound method with `__self__ = owner` (the class), even when read through an instance |
| `staticmethod` | non-data | the plain function, never bound |
| `property` | data | `instance` is `None`: the property itself; else `fget(instance)` |

### 10.2 A pure-Python `property`

```python
class Property:
    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        self.fget, self.fset, self.fdel = fget, fset, fdel
        self.__doc__ = doc if doc is not None else getattr(fget, "__doc__", None)

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        if self.fget is None:
            raise AttributeError("unreadable attribute")
        return self.fget(instance)

    def __set__(self, instance, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self.fset(instance, value)

    def __delete__(self, instance):
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        self.fdel(instance)

    def setter(self, fset):            # returns a NEW Property; the old one is unchanged
        return type(self)(self.fget, fset, self.fdel, self.__doc__)

    def deleter(self, fdel):
        return type(self)(self.fget, self.fset, fdel, self.__doc__)


class Account:
    def __init__(self, balance):
        self.balance = balance

    @Property
    def balance(self):
        "The balance in rupees."
        return self._balance

    @balance.setter
    def balance(self, value):
        if value < 0:
            raise ValueError("balance cannot be negative")
        self._balance = value

a = Account(50)
a.balance += 25
print(a.balance, Account.balance.__doc__)
try:
    a.balance = -1
except ValueError as e:
    print("ValueError:", e)
try:
    del a.balance
except AttributeError as e:
    print("AttributeError:", e)
```
```text
75 The balance in rupees.
ValueError: balance cannot be negative
AttributeError: can't delete attribute
```

Follow the decorator lines. `@Property` turns the first `balance` function into `Property(fget=balance)`. Then `@balance.setter` calls the `setter` method **of that object**, which returns a new `Property` with both functions, and the name `balance` is rebound to it. That is why the setter function must have the same name as the getter: otherwise the class ends up with two attributes, and the getter-only one is still read-only.

Because `Property` always defines `__set__` and `__delete__`, it is a data descriptor even without a setter, and it wins over the instance dictionary: exactly the behavior from core.14.

### 10.3 Pure-Python `classmethod` and `staticmethod`

```python
import types

class ClassMethod:
    def __init__(self, func):
        self.func = func
    def __get__(self, instance, owner=None):
        if owner is None:
            owner = type(instance)
        return types.MethodType(self.func, owner)   # bind to the CLASS

class StaticMethod:
    def __init__(self, func):
        self.func = func
    def __get__(self, instance, owner=None):
        return self.func                            # never bound


class Pizza:
    def __init__(self, size):
        self.size = size

    @ClassMethod
    def small(cls):
        return cls(20)

    @StaticMethod
    def area(diameter):
        return round(3.14159 * (diameter / 2) ** 2, 1)

class VeggiePizza(Pizza):
    pass

print(type(Pizza.small()).__name__, type(VeggiePizza.small()).__name__)
print(type(VeggiePizza(30).small()).__name__)
print(Pizza.area(20), Pizza(30).area(30))
```
```text
Pizza VeggiePizza
VeggiePizza
314.2 706.9
```

`ClassMethod.__get__` binds the function to `owner`, the class the attribute was looked up through. That is why `VeggiePizza.small()` builds a `VeggiePizza`: the alternative-constructor pattern from core.14 works because `owner` is the subclass. Calling through an instance (`VeggiePizza(30).small()`) still binds to the class. `StaticMethod.__get__` returns the plain function, so no first argument is inserted.

**A version trap.** Python 3.9 to 3.12 let `classmethod` wrap another descriptor, so `@classmethod` stacked on `@property` made a "class property". It was deprecated in 3.11 and **removed in 3.13**. Do not use that stack; if you need a computed class-level value, use a plain class attribute, a classmethod you call, or a small custom descriptor whose `__get__` uses `owner`.

#### Try it 10.1

Using only the `Property` class from section 10.2, write a `Rectangle` with `width` and `height` stored normally and a read-only computed `area`. What happens on `r.area = 5`, and which method of `Property` decides that?

<details><summary>Answer</summary>

```python
class Rectangle:
    def __init__(self, width, height):
        self.width = width
        self.height = height

    @Property
    def area(self):
        return self.width * self.height
```

`r.area` returns `width * height`. `r.area = 5` raises `AttributeError("can't set attribute")`. The decision is made by `Property.__set__`: it exists (so `Property` is a data descriptor and assignment goes to it, not to `r.__dict__`), and it raises because `fset` is `None`.

</details>

## 11. `functools.cached_property` and lazy attributes

### 11.1 Compute once, then get out of the way

Some attributes are expensive to compute but never change: a parsed file, a big statistic, a database lookup. A property recomputes on every read. `functools.cached_property` computes on the **first** read and caches the result:

```python
from functools import cached_property

class Report:
    def __init__(self, numbers):
        self.numbers = numbers

    @cached_property
    def total(self):
        print("  computing total...")
        return sum(self.numbers)

r = Report([1, 2, 3])
print(vars(r))
print(r.total)
print(r.total)
print(vars(r))
del r.total             # clear the cache
r.numbers.append(10)
print(r.total)
```
```text
{'numbers': [1, 2, 3]}
  computing total...
6
6
{'numbers': [1, 2, 3], 'total': 6}
  computing total...
16
```

The design is clever, and you already know every piece. `cached_property` is a **non-data** descriptor (only `__get__`). On the first read, the instance dictionary has no `total`, so its `__get__` runs, calls the function and **writes the result into `instance.__dict__["total"]`**. On the next read, the algorithm from section 2.2 finds `total` in the instance dictionary *before* it would call a non-data descriptor, so the descriptor is never called again. No checks, no overhead: after the first read it is a plain attribute. `del r.total` removes the dictionary entry, and the descriptor is visible again.

### 11.2 Writing your own `lazy`

```python
class lazy:
    def __init__(self, func):
        self.func = func

    def __set_name__(self, owner, name):
        self.name = name

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        value = self.func(instance)
        instance.__dict__[self.name] = value    # hides this descriptor from now on
        return value

class Circle:
    def __init__(self, r):
        self.r = r

    @lazy
    def area(self):
        print("  computing area")
        return round(3.14159 * self.r ** 2, 2)

c = Circle(2)
print(c.area, c.area)
print(type(Circle.area).__name__)
```
```text
  computing area
12.57 12.57
lazy
```

Notice this only works because `lazy` is a **non-data** descriptor. Add a `__set__` method and it becomes a data descriptor: it would then beat the cached dictionary entry, `__get__` would run on every read, and the cache would be useless.

### 11.3 Where it breaks

Because the cache lives in the instance dictionary:

- A class with `__slots__` (and no `__dict__`) cannot use `cached_property`. The first read raises `TypeError`.
- The cached value goes stale if the inputs change. Above, appending to `numbers` did not update `total` until the cache was deleted. Use `cached_property` only for values that really do not change, or document how to reset them.
- It is per instance. Two objects compute their own values.

(Before Python 3.12, `cached_property` also held a lock so that two threads could not compute the same value at once. The lock was removed in 3.12 because it was shared by all instances and slowed programs down. If thread safety matters, protect the computation yourself with a `threading.Lock`, core.21.)

#### Predict the output 11.1

```python
from functools import cached_property

class Counter:
    runs = 0

    @cached_property
    def value(self):
        Counter.runs += 1
        return Counter.runs * 10

a, b = Counter(), Counter()
print(a.value, a.value, b.value)
a.value = 99
print(a.value)
del a.value
print(a.value, Counter.runs)
```

<details><summary>Answer</summary>

```text
10 10 20
99
30 3
```

Each instance computes once: `a` gets 10 (first run), `b` gets 20 (second run), and the second `a.value` is read from `a.__dict__`. `a.value = 99` is allowed, because a non-data descriptor has no `__set__`: it simply writes the instance dictionary. After `del`, the next read computes again (third run, 30).

</details>

## 12. Build a validated-field system

This section is the second learning outcome. You will combine everything from sections 6 to 11 into a small library of reusable fields.

### 12.1 The design

What we want, from the user's side:

```python
class Employee:
    name = Typed(str)
    age = Range(18, 65)
    dept = OneOf("sales", "tech", "hr")
```

Every assignment, including the ones in `__init__`, is checked. Error messages name the class and the field (`Employee.age must be >= 18, got 12`). `vars(employee)` shows the real values. `Employee.age` returns the field object so tools can inspect it.

The decisions, each with its reason:

| Decision | Reason |
|---|---|
| One base class `Validator` with `__get__`, `__set__`, `__set_name__` | the plumbing is the same for every field; only the check differs |
| Subclasses override one method, `validate(value)` | the base does the fixed work and calls one method that each subclass fills in |
| Data descriptor (`__set__` defined) | an instance dictionary entry must never bypass the check (section 7.1) |
| Store in `instance.__dict__[name]` | per-instance storage, clean `vars()` output (section 8.3) |
| `__set_name__` records the field and owner names | messages say *which* field failed (section 8.1) |
| `instance is None` returns the field | `Employee.age` works for introspection (section 6.3) |
| Missing value raises `AttributeError` | `hasattr` and `getattr` with a default keep working (section 3.2) |

### 12.2 The base class

```python
from abc import ABC, abstractmethod

class Validator(ABC):
    def __set_name__(self, owner, name):
        self.name = name
        self.label = f"{owner.__name__}.{name}"

    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        try:
            return instance.__dict__[self.name]
        except KeyError:
            raise AttributeError(f"{self.label} has not been set") from None

    def __set__(self, instance, value):
        self.validate(value)                    # raises if the value is bad
        instance.__dict__[self.name] = value

    @abstractmethod
    def validate(self, value):
        """Raise TypeError or ValueError if value is not allowed."""


class Typed(Validator):
    def __init__(self, *types):
        self.types = types

    def validate(self, value):
        # bool is a subclass of int (core.02), but True is rarely a valid age
        if isinstance(value, bool) and bool not in self.types:
            ok = False
        else:
            ok = isinstance(value, self.types)
        if not ok:
            names = " or ".join(t.__name__ for t in self.types)
            raise TypeError(f"{self.label} must be {names}, got {type(value).__name__}")


class Range(Validator):
    def __init__(self, low=None, high=None):
        self.low, self.high = low, high

    def validate(self, value):
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise TypeError(f"{self.label} must be a number, got {type(value).__name__}")
        if self.low is not None and value < self.low:
            raise ValueError(f"{self.label} must be >= {self.low}, got {value}")
        if self.high is not None and value > self.high:
            raise ValueError(f"{self.label} must be <= {self.high}, got {value}")


class OneOf(Validator):
    def __init__(self, *options):
        self.options = options

    def validate(self, value):
        if value not in self.options:
            raise ValueError(f"{self.label} must be one of {self.options}, got {value!r}")
```

Each subclass is short because the base class does all the descriptor work. `Validator` is an abstract base class (core.14 section 16), so `Validator()` itself cannot be created: a field with no rule would be a mistake.

### 12.3 Using it

(To keep examples short, the code from section 12.2 was saved as `fields.py` next to this script.)

```python
from fields import Typed, Range, OneOf

class Employee:
    name = Typed(str)
    age = Range(18, 65)
    dept = OneOf("sales", "tech", "hr")

    def __init__(self, name, age, dept):
        self.name = name
        self.age = age
        self.dept = dept

    def __repr__(self):
        return f"Employee({self.name!r}, {self.age}, {self.dept!r})"

e = Employee("Asha", 30, "tech")
print(e, vars(e))
e.age += 1
print(e.age)

attempts = [("age", 12), ("age", "30"), ("age", True), ("dept", "admin"), ("name", 42)]
for field, value in attempts:
    try:
        setattr(e, field, value)
    except (TypeError, ValueError) as err:
        print(f"{type(err).__name__}: {err}")
print(e)
print(Employee.age.low, Employee.age.high)
```
```text
Employee('Asha', 30, 'tech') {'name': 'Asha', 'age': 30, 'dept': 'tech'}
31
ValueError: Employee.age must be >= 18, got 12
TypeError: Employee.age must be a number, got str
TypeError: Employee.age must be a number, got bool
ValueError: Employee.dept must be one of ('sales', 'tech', 'hr'), got 'admin'
TypeError: Employee.name must be str, got int
Employee('Asha', 31, 'tech')
18 65
```

Every bad value was stopped, the object was left unchanged, and each message tells you exactly what to fix. `Employee.age` gave back the `Range` object, so code can read its limits, for example to build a form or a help message.

### 12.4 Combining rules

What if a field needs two rules, say "a `str`, and one of these values"? Composition beats a subclass for every combination. An `All` field holds other validators and runs each one. It must also pass its name on to them, because only `All` is in the class body, so only `All` gets `__set_name__` (section 8.1):

```python
from fields import Validator, Typed, Range, OneOf

class All(Validator):
    def __init__(self, *rules):
        self.rules = rules

    def __set_name__(self, owner, name):
        super().__set_name__(owner, name)
        for rule in self.rules:
            rule.__set_name__(owner, name)      # inner rules learn the name too

    def validate(self, value):
        for rule in self.rules:
            rule.validate(value)

class Exam:
    score = All(Typed(int), Range(0, 100))
    grade = All(Typed(str), OneOf("A", "B", "C", "F"))

x = Exam()
x.score, x.grade = 87, "A"
print(vars(x))
for field, value in [("score", 87.5), ("score", 101), ("grade", "E")]:
    try:
        setattr(x, field, value)
    except (TypeError, ValueError) as err:
        print(f"{type(err).__name__}: {err}")
```
```text
{'score': 87, 'grade': 'A'}
TypeError: Exam.score must be int, got float
ValueError: Exam.score must be <= 100, got 101
ValueError: Exam.grade must be one of ('A', 'B', 'C', 'F'), got 'E'
```

### 12.5 Listing a class's fields

Because the fields are objects on the class, a function can find them. Scanning `vars(cls)` keeps the order of the class body:

```python
from fields import Validator, Typed, Range

def fields_of(cls):
    found = {}
    for klass in reversed(cls.__mro__):          # parents first, children override
        for name, value in vars(klass).items():
            if isinstance(value, Validator):
                found[name] = value
    return found

class Person:
    name = Typed(str)
    age = Range(0, 150)

class Student(Person):
    roll_no = Typed(int)

print(list(fields_of(Student)))
print({name: type(f).__name__ for name, f in fields_of(Student).items()})
```
```text
['name', 'age', 'roll_no']
{'name': 'Typed', 'age': 'Range', 'roll_no': 'Typed'}
```

This is the seed of an ORM (section 22): a `Model` base class can list its fields to build a `CREATE TABLE` statement or to validate a whole row. Notice that it finds fields through the **descriptor objects**, not through type annotations. That is deliberate: it works the same on every Python version, while annotations changed how they are stored in 3.14 (section 17.4).

#### Try it 12.1

Add a `NonEmptyStr(max_len)` validator: the value must be a `str`, must not be empty after `.strip()`, and must have at most `max_len` characters. Use it in a class `Book` with `title = NonEmptyStr(40)`. What three error messages do `""`, `"   "` and `"x" * 41` give?

<details><summary>Answer</summary>

```python
from fields import Validator

class NonEmptyStr(Validator):
    def __init__(self, max_len):
        self.max_len = max_len

    def validate(self, value):
        if not isinstance(value, str):
            raise TypeError(f"{self.label} must be str, got {type(value).__name__}")
        if not value.strip():
            raise ValueError(f"{self.label} must not be empty")
        if len(value) > self.max_len:
            raise ValueError(f"{self.label} is longer than {self.max_len} characters")

class Book:
    title = NonEmptyStr(40)

b = Book()
b.title = "Dune"
for value in ["", "   ", "x" * 41]:
    try:
        b.title = value
    except ValueError as err:
        print("ValueError:", err)
print(b.title)
```
```text
ValueError: Book.title must not be empty
ValueError: Book.title must not be empty
ValueError: Book.title is longer than 40 characters
Dune
```

`""` and `"   "` give the same "must not be empty" message, because both are empty after `strip()`. Only `validate` was written; storage, names and the `None` case all came from `Validator`.

</details>

## 13. `__slots__` are descriptors too

### 13.1 What `__slots__` creates

In core.15 (section 28) you used `__slots__` to save memory: instances get fixed storage and no `__dict__`. Now you can see *how* attribute access still works without a dictionary. For each name in `__slots__`, Python puts a **member descriptor** on the class:

```python
class Point:
    __slots__ = ("x", "y")
    def __init__(self, x, y):
        self.x, self.y = x, y

p = Point(1, 2)
d = Point.__dict__["x"]
print(type(d).__name__)
print(hasattr(type(d), "__get__"), hasattr(type(d), "__set__"))
print(d.__get__(p, Point))
d.__set__(p, 10)
print(p.x, hasattr(p, "__dict__"))
```
```text
member_descriptor
True True
1
10 False
```

The member descriptor is a **data** descriptor. It knows a fixed position (an offset) inside the object's memory, and its `__get__` and `__set__` read and write that position. So `p.x` follows the normal algorithm: found on the class, data descriptor, call `__get__`. Even `__dict__` itself, on a normal class, is a descriptor (a `getset_descriptor` on the class) that hands out the instance dictionary.

Two consequences follow from this:

- A class attribute with the same name as a slot is an error (`ValueError` when the class is created), because both would need the same entry in the class dictionary.
- Descriptors that store values in `instance.__dict__` (like `Validator` in section 12) do not work on slotted classes. Store under a private slot name instead.

```python
class Positive:
    def __set_name__(self, owner, name):
        self.name, self.slot = name, "_" + name
    def __get__(self, instance, owner=None):
        if instance is None:
            return self
        return getattr(instance, self.slot)         # read the slot
    def __set__(self, instance, value):
        if value <= 0:
            raise ValueError(f"{self.name} must be > 0")
        setattr(instance, self.slot, value)         # write the slot

class Item:
    __slots__ = ("_price",)                         # storage for the descriptor
    price = Positive()
    def __init__(self, price):
        self.price = price

i = Item(5)
print(i.price, hasattr(i, "__dict__"))
```
```text
5 False
```

#### Try it 13.1

`class Bad: __slots__ = ("x",); x = 5` fails at class creation. Using what you know about member descriptors, explain why, and say what the programmer probably wanted.

<details><summary>Answer</summary>

`__slots__ = ("x",)` asks Python to put a member descriptor called `x` into the class dictionary, but the class body already put `5` there under the same key. Both cannot be stored, so Python raises `ValueError`. The programmer probably wanted a **default value** for `x`. With slots, set it in `__init__` (`def __init__(self, x=5): self.x = x`), or use `@dataclass(slots=True)` with `x: int = 5`, which handles the default for you.

</details>

## 14. `__init_subclass__`: hooking subclass creation

### 14.1 Code that runs when a subclass is defined

Sometimes a base class wants to act each time someone **subclasses** it: register the subclass, check that it defined something, add a method. Since Python 3.6, the base class can define `__init_subclass__(cls, **kwargs)`. Python calls it on the parent right after each new subclass is created, passing the new subclass as `cls`. It is automatically a classmethod; you do not write `@classmethod`.

```python
class Exporter:
    registry = {}

    def __init_subclass__(cls, /, fmt=None, **kwargs):
        super().__init_subclass__(**kwargs)
        if fmt is None:
            raise TypeError(f"{cls.__name__} must pass fmt=... in its class line")
        if fmt in Exporter.registry:
            raise TypeError(f"format {fmt!r} already taken")
        Exporter.registry[fmt] = cls
        cls.fmt = fmt

class CsvExporter(Exporter, fmt="csv"):
    def export(self, rows):
        return "\n".join(",".join(map(str, r)) for r in rows)

class JsonExporter(Exporter, fmt="json"):
    def export(self, rows):
        return str(rows)

print(Exporter.registry)
print(Exporter.registry["csv"]().export([(1, 2), (3, 4)]))
try:
    class Broken(Exporter):
        pass
except TypeError as e:
    print("TypeError:", e)
```
```text
{'csv': <class '__main__.CsvExporter'>, 'json': <class '__main__.JsonExporter'>}
1,2
3,4
TypeError: Broken must pass fmt=... in its class line
```

Keyword arguments in the class line (`fmt="csv"`) go to `__init_subclass__`. Two habits make it play well with other base classes: accept unknown keywords as `**kwargs`, and call `super().__init_subclass__(**kwargs)` so the next class in the MRO gets its turn. The `/` makes `cls` positional-only (core.06), so a keyword called `cls` could never clash with it.

The check ran at **class definition time**: the mistake was caught when the module was imported, not later when someone tried to use `Broken`. That is the big win of class-creation hooks: errors move to the earliest possible moment.

### 14.2 Enforcing a contract

```python
class Model:
    required = ("table", "columns")

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        missing = [name for name in cls.required if not hasattr(cls, name)]
        if missing:
            raise TypeError(f"{cls.__name__} is missing {', '.join(missing)}")

class User(Model):
    table = "users"
    columns = ("id", "name")

try:
    class Order(Model):
        table = "orders"
except TypeError as e:
    print("TypeError:", e)
print(User.table)
```
```text
TypeError: Order is missing columns
users
```

Note that `__init_subclass__` runs for subclasses only, never for the class that defines it: `Model` itself has no `table`, and that is fine.

#### Predict the output 14.1

```python
class Base:
    def __init_subclass__(cls, **kwargs):
        print("init_subclass:", cls.__name__, kwargs)
        super().__init_subclass__()

class A(Base):
    pass

class B(A, color="red"):
    pass

print("done")
```

<details><summary>Answer</summary>

```text
init_subclass: A {}
init_subclass: B {'color': 'red'}
done
```

Nothing prints for `Base` itself. `A` is a subclass of `Base`, so the hook runs. `B` is a subclass of `A`, and `A` inherits `__init_subclass__` from `Base`, so it runs again for `B`, with `color="red"` in `kwargs`. Here the hook swallows unknown keywords; if it passed them on with `super().__init_subclass__(**kwargs)`, `object.__init_subclass__` would raise `TypeError`, because it accepts no keywords.

</details>

## 15. `__class_getitem__`: what `list[int]` is

### 15.1 Square brackets on a class

You have written `list[int]` and `dict[str, int]` since core.09. Square brackets on an *object* call `__getitem__`. Square brackets on a *class* call the classmethod `__class_getitem__(cls, item)` (like `__init_subclass__`, it is a classmethod automatically). For built-in collections it returns a `types.GenericAlias`, a small object that remembers the original class and the arguments:

```python
import types

alias = list[int]
print(alias, type(alias) is types.GenericAlias)
print(alias.__origin__, alias.__args__)
print(dict[str, int].__args__)
print(alias(["a", "b"]))        # calling the alias creates a plain list, no checking
```
```text
list[int] True
<class 'list'> (<class 'int'>,)
(<class 'str'>, <class 'int'>)
['a', 'b']
```

The last line matters: `list[int]` does **no runtime checking**. It exists for type checkers and readers (core.16). Python stores the information and moves on.

### 15.2 Your own `__class_getitem__`

Any class can define it. Python passes whatever is inside the brackets: one object, or a **tuple** if there are commas. The return value can be anything; most real uses return an alias for type hints, but you can return a specialised subclass that does check at runtime:

```python
class Array:
    _cache = {}
    item_type = object

    def __class_getitem__(cls, item):
        if isinstance(item, tuple):
            raise TypeError("Array takes exactly one type")
        if item not in cls._cache:
            cls._cache[item] = type(f"Array[{item.__name__}]", (cls,), {"item_type": item})
        return cls._cache[item]

    def __init__(self, *items):
        for x in items:
            if not isinstance(x, self.item_type):
                raise TypeError(f"{type(self).__name__} got {type(x).__name__}")
        self.items = list(items)

ints = Array[int](1, 2, 3)
print(type(ints).__name__, ints.items, Array[int] is Array[int])
for bad in (lambda: Array[int](1, "two"), lambda: Array[int, str]):
    try:
        bad()
    except TypeError as e:
        print("TypeError:", e)
```
```text
Array[int] [1, 2, 3] True
TypeError: Array[int] got str
TypeError: Array takes exactly one type
```

The cache makes `Array[int] is Array[int]` true, so `isinstance` checks and class identity stay predictable. The `type(...)` call that builds the subclass is the subject of the next section. In everyday code, prefer `typing.Generic` (core.16) for type hints and keep runtime checks in validators (section 12); a custom `__class_getitem__` is for small, specific cases like this.

## 16. Classes are objects: `type(name, bases, ns)`

### 16.1 The `class` statement is a function call

A class is an object like any other: you can store it in a variable, pass it to a function, put it in a list. Something must create that object. With one argument, `type(obj)` tells you an object's class. With three arguments, `type(name, bases, namespace)` **creates a new class**:

```python
def greet(self):
    return f"Hello from {self.name}"

Person = type("Person", (object,), {"species": "human", "greet": greet,
                                    "__init__": lambda self, name: setattr(self, "name", name)})

p = Person("Asha")
print(Person.__name__, Person.species, p.greet())
print(type(Person), isinstance(p, Person))
```
```text
Person human Hello from Asha
<class 'type'> True
```

That is exactly the class you would get from:

```python
class Person:
    species = "human"
    def __init__(self, name):
        self.name = name
    def greet(self):
        return f"Hello from {self.name}"
```

The `class` statement is a convenient way of calling `type(...)`: Python runs the body to fill a dictionary, then passes the name, the bases and that dictionary to `type`.

### 16.2 When it is useful

Building classes with `type()` is useful when the class shape comes from **data**: field names read from a file, a family of exception classes generated from a table of error codes (`type(name, (AppError,), {"status": code})` in a loop), or a test that needs ten small classes. Section 15.2 used it to build one subclass per item type.

The cost: tools cannot see these classes until the program runs. An editor cannot autocomplete them, and a type checker knows nothing about their attributes. If the list of classes is fixed, writing a few short `class` statements is clearer. Section 20 returns to this trade-off.

#### Try it 16.1

Use `type()` to create a class `Point` with a `__slots__` of `("x", "y")`, an `__init__(self, x, y)` and a `__repr__` that returns `Point(x, y)`. Then write the same class with a `class` statement. Which would you rather read?

<details><summary>Answer</summary>

```python
def __init__(self, x, y):
    self.x, self.y = x, y

def __repr__(self):
    return f"Point({self.x}, {self.y})"

Point = type("Point", (), {"__slots__": ("x", "y"), "__init__": __init__, "__repr__": __repr__})
print(Point(1, 2), hasattr(Point(1, 2), "__dict__"))
```
```text
Point(1, 2) False
```

An empty tuple of bases means "inherit from `object`". The `class` statement version has the same three parts in the same order, and almost everyone would rather read it: `type()` pays off only when the name or fields really come from data.

</details>

## 17. Metaclasses: how a class is created

### 17.1 The class of a class

If a class is an object, it has a class too. That class is called its **metaclass**. For almost every class it is `type`:

```python
class Dog:
    pass

print(type(Dog()), type(Dog), type(int), type(type))
print(isinstance(Dog, type))
```
```text
<class '__main__.Dog'> <class 'type'> <class 'type'> <class 'type'>
True
```

`type` is the metaclass of every ordinary class, and also of itself. A **custom metaclass** is a subclass of `type`. Since `Dog(...)` creates a `Dog`, and `type(...)` creates a class, a subclass of `type` lets you change **how classes are created**, just as overriding `__init__` changes how instances are created.

### 17.2 The class statement, step by step

When Python executes a `class` statement, it does these steps in order:

1. **Resolve the metaclass**: the `metaclass=` keyword if given, otherwise the metaclass of the bases (the most derived one), otherwise `type`.
2. **`__prepare__`**: call `metaclass.__prepare__(name, bases, **kwargs)` to get the namespace mapping. The default returns an empty `dict`.
3. **Run the class body** inside that namespace. Each `def` and assignment becomes a key.
4. **`metaclass.__new__(mcls, name, bases, namespace, **kwargs)`** creates the class. Inside, `type.__new__` does two more things before returning:
    1. calls **`__set_name__`** on every attribute that has one (section 8);
    2. calls **`__init_subclass__`** on the parent of the new class (section 14), passing the class keywords.
5. **`metaclass.__init__(cls, name, bases, namespace, **kwargs)`** runs on the finished class.
6. **Class decorators** run, from the bottom one up, and the result is bound to the name.

A trace shows every step really happening in that order:

```python
class Meta(type):
    @classmethod
    def __prepare__(mcls, name, bases, **kwargs):
        print(f"1. Meta.__prepare__  {name} {kwargs}")
        return {}

    def __new__(mcls, name, bases, ns, **kwargs):
        print(f"3. Meta.__new__ start {name}, body names: {[k for k in ns if not k.startswith('__')]}")
        cls = super().__new__(mcls, name, bases, ns, **kwargs)
        print(f"6. Meta.__new__ end   {name}")
        return cls

    def __init__(cls, name, bases, ns, **kwargs):
        print(f"7. Meta.__init__      {name}")
        super().__init__(name, bases, ns, **kwargs)

class Field:
    def __set_name__(self, owner, name):
        print(f"4. Field.__set_name__ {owner.__name__}.{name}")

class Base(metaclass=Meta):
    def __init_subclass__(cls, **kwargs):
        print(f"5. Base.__init_subclass__ {cls.__name__} {kwargs}")

def decorate(cls):
    print(f"8. decorator          {cls.__name__}")
    return cls

print("---- defining Child ----")

@decorate
class Child(Base, table="kids"):
    print("2. class body runs")
    name = Field()
```
```text
1. Meta.__prepare__  Base {}
3. Meta.__new__ start Base, body names: []
6. Meta.__new__ end   Base
7. Meta.__init__      Base
---- defining Child ----
1. Meta.__prepare__  Child {'table': 'kids'}
2. class body runs
3. Meta.__new__ start Child, body names: ['name']
4. Field.__set_name__ Child.name
5. Base.__init_subclass__ Child {'table': 'kids'}
6. Meta.__new__ end   Child
7. Meta.__init__      Child
8. decorator          Child
```

The first four lines come from creating `Base` itself (it has the metaclass too, but no parent with `__init_subclass__` and no fields). For `Child`, the numbers line up with the steps. Two orderings surprise most people, so remember them: `__set_name__` and `__init_subclass__` both run **inside** `type.__new__`, before the metaclass `__init__`; and class decorators run **last**, after the metaclass is completely done.

The trace filters out names starting with `__`. The namespace always has some automatic dunder entries, and which ones depends on the version: every version has `__module__` and `__qualname__`; 3.13 added `__firstlineno__` and `__static_attributes__`; 3.14 can add more. Code that inspects a namespace should never depend on those.

### 17.3 Writing a useful metaclass

Here is a metaclass that uses two powers only a metaclass has: `__prepare__`, to see every assignment in the body, and acting on the class **that declares it** (not only subclasses). It refuses a class body that defines the same name twice, a common copy-paste bug that Python normally allows silently:

```python
class NoDupDict(dict):
    def __setitem__(self, key, value):
        if key in self and not key.startswith("__"):
            raise TypeError(f"{key!r} defined twice in the class body")
        super().__setitem__(key, value)

class NoDuplicates(type):
    @classmethod
    def __prepare__(mcls, name, bases, **kwargs):
        return NoDupDict()

    def __new__(mcls, name, bases, ns, **kwargs):
        return super().__new__(mcls, name, bases, dict(ns), **kwargs)

class Fine(metaclass=NoDuplicates):
    def total(self):
        return 1

try:
    class Copied(metaclass=NoDuplicates):
        def total(self):
            return 1
        def total(self):           # pasted twice: the first one would be lost
            return 2
except TypeError as e:
    print("TypeError:", e)
print(Fine().total())
```
```text
TypeError: 'total' defined twice in the class body
1
```

`__prepare__` must return a mapping. The class body writes into it through `__setitem__`, so our dictionary subclass sees every definition as it happens. `type.__new__` needs a real `dict`, so we pass `dict(ns)`. (In Python 2 and very old Python 3, `__prepare__` was also how you kept definition order; since 3.6 a plain `dict` remembers insertion order, so that reason is gone.)

### 17.4 A version trap: annotations in the namespace

If a class body has type annotations (`x: int = 1`), you might be tempted to read `ns["__annotations__"]` in a metaclass or `vars(cls)["__annotations__"]` in `__init_subclass__` to discover fields. **Do not.** Python 3.14 changed how annotations are stored (PEP 649 and PEP 749): they are now evaluated lazily, and during class creation the namespace no longer holds an `__annotations__` dictionary. It holds a function instead (stored as `__annotate_func__` in 3.14.4, the version used here; do not rely on that internal name either). On 3.11 to 3.13 the namespace does hold `__annotations__`. Code that reads it works on one set of versions and breaks on the other.

Two safe options: discover fields through **descriptor objects** (section 12.5), which works everywhere, or, if you really need annotations, call `inspect.get_annotations(cls)` on the **finished** class (it exists since 3.10, and 3.14 also adds the `annotationlib` module).

### 17.5 Lookup on a class, and methods on a metaclass

Reading `Cls.x` uses the same algorithm as section 2, one level up: the "type" is the metaclass. So an attribute defined on the metaclass is visible from the **class**, but not from its **instances**:

```python
class Meta(type):
    def describe(cls):
        return f"I am the class {cls.__name__}"

class Thing(metaclass=Meta):
    pass

print(Thing.describe())
print(hasattr(Thing(), "describe"))
```
```text
I am the class Thing
False
```

`Thing.describe` found `describe` on `type(Thing)`, which is `Meta`, and bound it to `Thing` (a function is a descriptor, and `Thing` is the instance here). `Thing()` is an instance of `Thing`, whose MRO is `Thing, object`; `Meta` is not in it.

#### Predict the output 17.1

```python
class Meta(type):
    def __new__(mcls, name, bases, ns):
        print("new", name)
        return super().__new__(mcls, name, bases, ns)

    def __init__(cls, name, bases, ns):
        print("init", name)
        super().__init__(name, bases, ns)

class Base(metaclass=Meta):
    def __init_subclass__(cls):
        print("subclass", cls.__name__)

class Child(Base):
    print("body")

class Grandchild(Child):
    pass

print(type(Grandchild).__name__)
```

<details><summary>Answer</summary>

```text
new Base
init Base
body
new Child
subclass Child
init Child
new Grandchild
subclass Grandchild
init Grandchild
Meta
```

`Base` goes through `Meta.__new__` and `Meta.__init__`, but `__init_subclass__` is not called for the class that defines it. For `Child`, the body runs first (step 3), then `Meta.__new__`, inside which `type.__new__` calls `Base.__init_subclass__`, then `Meta.__init__`. `Grandchild` has no `metaclass=` keyword, but it **inherits** the metaclass from its base, and it inherits `__init_subclass__` too.

</details>

## 18. Metaclass `__call__`: controlling instance creation

### 18.1 What `Cls(...)` really calls

`Cls(1, 2)` is a call on the object `Cls`, so Python runs `type(Cls).__call__(Cls, 1, 2)`: the metaclass's `__call__`. The default, `type.__call__`, does this:

```python
def __call__(cls, *args, **kwargs):
    obj = cls.__new__(cls, *args, **kwargs)
    if isinstance(obj, cls):
        obj.__init__(*args, **kwargs)        # skipped if __new__ returned something else
    return obj
```

So a metaclass that overrides `__call__` controls instance creation for all its classes. The textbook example is a singleton per class:

```python
class SingletonMeta(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in SingletonMeta._instances:
            SingletonMeta._instances[cls] = super().__call__(*args, **kwargs)
        return SingletonMeta._instances[cls]

class Config(metaclass=SingletonMeta):
    def __init__(self):
        print("  Config.__init__ runs")
        self.values = {}

class TestConfig(Config):
    pass

a, b = Config(), Config()
print(a is b)
print(TestConfig() is TestConfig(), TestConfig() is a)
```
```text
  Config.__init__ runs
True
  Config.__init__ runs
True False
```

`__init__` ran once per class, and each subclass got its own instance because the dictionary is keyed by `cls`. Remember core.22 (section 12.2): in most programs a module-level object does the same job with no machinery at all. A metaclass `__call__` earns its place in frameworks, for example to record every instance created, or to return cached objects for equal arguments.

### 18.2 Metaclass conflicts

A class has exactly one metaclass, and it must be a subclass of the metaclass of **every** base. Mixing two unrelated metaclasses fails:

```python
from abc import ABCMeta

class Meta(type):
    pass

class A(metaclass=Meta):
    pass

class B(metaclass=ABCMeta):          # ABC uses the metaclass ABCMeta
    pass

try:
    class C(A, B):
        pass
except TypeError as e:
    print("class C(A, B) raised", type(e).__name__)

class CombinedMeta(Meta, ABCMeta):
    pass

class C(A, B, metaclass=CombinedMeta):
    pass
print(type(C).__name__)
```
```text
class C(A, B) raised TypeError
CombinedMeta
```

The fix is a metaclass that inherits from both, but you only can do that if you control the code. This is one of the strongest reasons to avoid metaclasses in a library: every user who also uses `ABC`, `Enum`, or another library's metaclass may hit this wall. `__init_subclass__` and class decorators never conflict this way.

## 19. Class decorators vs `__init_subclass__` vs metaclasses

### 19.1 Three tools that act on classes

You now have three ways to run code when a class is created. They overlap a lot, so the question is always: **which is the lightest tool that does the job?**

| | Class decorator (core.15) | `__init_subclass__` | Metaclass |
|---|---|---|---|
| Runs | after the class is fully built | inside `type.__new__`, for each subclass | around the whole creation |
| Applies to | the class you decorate, only | every subclass, automatically (inherited) | the class that declares it and all subclasses |
| Sees the body before the class exists | no | no | yes (`__prepare__`, `__new__`) |
| Can control `Cls(...)` calls | no | no | yes (`__call__`) |
| Can give the *class* operators (`len(Color)`, `for c in Color`) | no | no | yes (methods on the metaclass) |
| Conflicts with other libraries | never | almost never | yes (section 18.2) |
| How hard to read | easy: the `@` line is visible | easy: plain method on the base | hard: behavior lives in another class |

The rules of thumb that follow:

- To change **one** class, or a few chosen ones: a **class decorator**. It is explicit: the reader sees `@register` right above the class.
- To act on **every subclass** of a base (registries, contracts, auto-generated methods): **`__init_subclass__`**.
- Use a **metaclass** only for what the other two cannot do: customize the namespace with `__prepare__`, control instance creation for a family of classes with `__call__`, or give the class objects themselves behavior (this is how `enum.Enum` makes `len(Color)` and `Color["RED"]` work).

#### Try it 19.1

Pick the lightest tool for each task:

1. Every subclass of `Command` must be registered under its lowercase class name.
2. Add a `to_dict()` method to three specific classes in a project.
3. A class body must not be allowed to define the same name twice.
4. Iterating over a class (`for level in LogLevel:`) should yield its members.

<details><summary>Answer</summary>

1. **`__init_subclass__`** on `Command`: it runs for every subclass, automatically, and needs no extra syntax in the subclasses.
2. A **class decorator** `@add_to_dict` (or even a plain mixin base class with a `to_dict` method): it is explicit and touches only the classes you choose.
3. A **metaclass with `__prepare__`** (section 17.3): only the metaclass sees the assignments while the body runs; afterwards, the first definition is already gone.
4. A **metaclass** defining `__iter__`: `for x in LogLevel` calls `type(LogLevel).__iter__`, so the method must live on the metaclass. (In real code, just use `enum.Enum`, which already does this.)

</details>

## 20. When metaprogramming is the wrong choice

Everything in this chapter is real, useful and used by the libraries you depend on. It is also the easiest way to make a codebase that nobody else can work on. This section is about the judgment that the earlier sections cannot give you.

### 20.1 What magic costs

Each hook you add makes some code do something that is **not written where it happens**. That has costs, and they are paid by every future reader:

- **Readability: action at a distance.** In `user.email = text`, nothing tells the reader that a `__setattr__` in a base class three files away lowercases the text, logs it, and might raise. With a plain method call, `user.set_email(text)`, the reader at least knows to look.
- **Debugging.** A traceback through `__getattribute__`, `__set__` and a metaclass `__call__` is long and full of frames that are not your logic. Bugs like the swallowed `AttributeError` (section 4.3) and `__getattr__` recursion (section 3.4) exist *only* because of hooks. Errors in class-creation hooks fire at import time, before any of your code runs.
- **Tools go blind.** Editors autocomplete and type checkers verify by reading code, not by running it. They cannot see attributes invented by `__getattr__`, classes built by `type()` from data, or methods added by a metaclass. You lose autocomplete, "go to definition", and type errors caught before running. Dataclasses are the exception that proves the rule: type checkers have special support for them because they are standard.
- **Speed.** A Python-level `__getattribute__` or `__setattr__` runs a function on every access. Descriptors cost a call per access too, which is usually fine but adds up in tight loops.
- **Composition.** Metaclasses conflict (section 18.2). Two libraries that each own `__getattr__` or `__setattr__` on the same class fight over it.
- **Learning cost.** A new teammate must understand your machinery before they can change a model class. "Explicit is better than implicit" and "if the implementation is hard to explain, it's a bad idea" (core.22 section 1.2) are aimed exactly at this.

### 20.2 Four rewrites: magic versus plain

**A metaclass that only adds methods.** Someone writes a metaclass to give every class an automatic `__repr__` and `__eq__`. That is exactly what `@dataclass` does, in one visible line, with tool support:

```python
from dataclasses import dataclass

@dataclass
class Point:
    x: int
    y: int

print(Point(1, 2), Point(1, 2) == Point(1, 2))
```
```text
Point(x=1, y=2) True
```

**`__getattr__` over a dictionary for configuration.** `cfg.db_host` reading from a dict looks neat, but typos become runtime errors, nothing autocompletes, and `__getattr__` brings the contract and recursion traps of section 3. If the keys are known, a dataclass (or a frozen dataclass built from the parsed file) is clearer. If they are not known, a plain dictionary with `cfg["db_host"]` is honest about that.

**A metaclass registry.** A registry of plugins needs no metaclass: `__init_subclass__` does it (section 14.1), and an explicit decorator is even clearer when not every subclass should register:

```python
EXPORTERS = {}

def exporter(fmt):
    def register(cls):
        EXPORTERS[fmt] = cls
        return cls
    return register

@exporter("csv")
class CsvExporter: ...
```

**A descriptor for one field.** A `Validator` family pays off when many classes need the same rules. For one rule on one attribute of one class, a `property` is shorter, and every Python programmer reads it at once.

### 20.3 The ladder: climb only as high as you must

Before reaching for a hook, walk up this ladder and stop at the first step that solves the problem:

1. **Plain code**: an attribute, a function, an explicit method call.
2. **A `property`** for one computed or checked attribute.
3. **A `@dataclass`** (or `NamedTuple`, `Enum`) for records, equality, ordering, freezing.
4. **A descriptor** when the *same* attribute rule repeats across many fields or classes.
5. **A class decorator** or **`__init_subclass__`** when classes themselves need registering, checking or extending.
6. **`__getattr__`** for real delegation or truly dynamic names; **`__setattr__`** for a rule on *every* attribute.
7. **A metaclass** or **`__getattribute__`**, only for what nothing below can do.

Each step down the list is easier to read, debug and type-check. Steps 4 to 7 are mostly for **library and framework code**: code written once by someone who understands it, and used many times by people who should not need to.

### 20.4 When it *is* the right choice

Metaprogramming is right when it removes a large amount of real repetition **and** the users of the result do not need to understand how it works. That describes frameworks: Django models and SQLAlchemy columns (descriptors and class-creation hooks), `dataclasses` (a class decorator that writes code), `enum` (a metaclass), `pytest` fixtures, `functools.cached_property`. In each, a small amount of hard code makes thousands of user classes short, safe and boring. Inside one application, that trade rarely pays: there are few users of the machinery, and they all have to maintain it.

### 20.5 A checklist before you merge

Ask these questions about any hook you are about to add:

1. Which step of the ladder in 20.3 is the lowest that solves this? Why is it not enough?
2. Can a newcomer find out what `obj.x = 1` does by reading the class they are looking at?
3. Will the editor still autocomplete, and will the type checker still catch typos?
4. What does the traceback look like when a user makes a mistake? Is the message clear, and does it name the field?
5. Does it still work with `copy`, `pickle`, `hasattr`, `dataclasses`, `ABC` and subclassing?
6. Is there a test for each hook, including the "missing attribute" and "subclass" cases?

#### Try it 20.1

For each snippet, name the lighter tool and say why in one sentence.

```python
# A
class Meta(type):
    def __new__(mcls, name, bases, ns):
        ns["created_by"] = "app"
        return super().__new__(mcls, name, bases, ns)

# B
class Celsius:
    def __getattr__(self, name):
        if name == "fahrenheit":
            return self.celsius * 9 / 5 + 32
        raise AttributeError(name)

# C
class Point:
    def __init__(self, x, y):
        object.__setattr__(self, "x", x)
        object.__setattr__(self, "y", y)
    def __setattr__(self, name, value):
        raise AttributeError("frozen")
    def __repr__(self): ...
    def __eq__(self, other): ...
```

<details><summary>Answer</summary>

- **A**: a plain class attribute `created_by = "app"` on a base class does the same; every subclass inherits it. If it must be set per class, `__init_subclass__` is still lighter than a metaclass.
- **B**: a `property` named `fahrenheit`. The name is fixed and known, so there is nothing dynamic about it; a property is visible to tools and cannot swallow other errors.
- **C**: `@dataclass(frozen=True)` with fields `x` and `y`. It generates the frozen `__setattr__`, `__init__`, `__repr__` and `__eq__`, and type checkers understand it.

</details>

## 21. Common traps

1. **`__getattr__` that does not raise `AttributeError`** for unknown names. `hasattr`, `getattr` defaults, `copy` and `pickle` misbehave (section 3.2).
2. **Reading `self.x` inside `__getattr__`** when `x` may be missing: infinite recursion, for example on `copy.copy` (section 3.4).
3. **`self.anything` inside `__getattribute__`** or **`self.x = ...` inside `__setattr__`**: recursion. Use `super()` / `object.__...__` (sections 4.2, 5.1).
4. **A property getter raising `AttributeError`** on a class with `__getattr__`: the real error is swallowed (section 4.3).
5. **Expecting `__getattr__` to provide `len()`, `+`, `[]`**: implicit special-method lookup goes to the type only (section 2.5).
6. **Storing values on the descriptor** (`self.value = ...` in `__set__`): one value shared by all instances (section 8.2).
7. **Forgetting `instance is None`** in `__get__`: `Cls.attr` crashes (section 6.3).
8. **Leaving out `__set__` to make a read-only field**: the descriptor becomes non-data and assignment silently hides it (section 7.3).
9. **Adding `__set__` to a caching descriptor**: it becomes a data descriptor and the cache is never used (section 11.2).
10. **Attaching a descriptor after class creation** and expecting `__set_name__` to run (section 8.1).
11. **Comparing bound methods with `is`**: every lookup builds a new one (section 9.4).
12. **`cached_property` on a `__slots__` class**, or on a value whose inputs change (section 11.3).
13. **Stacking `@classmethod` on `@property`**: removed in Python 3.13 (section 10.3).
14. **Reading `__annotations__` from a class namespace** in a metaclass or `__init_subclass__`: it changed in 3.14 (section 17.4).
15. **Not forwarding `**kwargs` to `super().__init_subclass__()`**, or forwarding unknown ones to `object` (section 14).
16. **Mixing metaclasses** from different libraries: metaclass conflict (section 18.2).
17. **Reaching for a metaclass first.** Walk the ladder (section 20.3).

## 22. Project preview: a Mini ORM using descriptors

The module project (problem p035) is a small **ORM** (object-relational mapper): Python classes that map to SQLite tables (core.17). This section is only the **design sketch**; the full build is yours.

### 22.1 What the user writes

```python
class Book(Model):
    id = IntegerField(primary_key=True)
    title = TextField()
    pages = IntegerField(null=True)
    status = TextField(default="new")

conn = sqlite3.connect(":memory:")
conn.execute(Book.create_table_sql())
b = Book(title="Dune", pages=412)
b.save(conn)                    # INSERT; b.id is set from the new row
b.pages = 420
b.save(conn)                    # UPDATE, because b.id is set
Book.get(conn, b.id)            # one Book or None
Book.filter(conn, status="new") # list of Books
```

### 22.2 The pieces and the chapter sections they use

| Piece | Job | Built from |
|---|---|---|
| `Field` base | data descriptor; stores in `instance.__dict__`; validates on `__set__`; knows its name | sections 8, 12 |
| `IntegerField`, `TextField` | the `validate` rule and the SQL type (`INTEGER`, `TEXT`) | section 12.2 |
| `null`, `default`, `primary_key` options | stored on the field; `__get__` returns the default when unset | section 6 |
| `Model.__init_subclass__` | collects the fields **in definition order** by scanning `vars(cls)` for `Field` objects; sets `table_name` (for example `"book"`) | sections 12.5, 14 |
| `Model.__init__(**kwargs)` | assigns each keyword through the descriptors, so values are validated; unknown names raise `TypeError` | section 12.3 |
| `create_table_sql()` | a classmethod that builds `CREATE TABLE` from the collected fields | section 10.3 |
| `save`, `get`, `filter` | SQL with `?` placeholders only, never string formatting of values (core.17) | core.17 |

### 22.3 Design rules to keep

- **Fields are discovered through descriptor objects, never through annotations**, so the ORM behaves the same on 3.11 to 3.14 (section 17.4).
- **No metaclass is needed.** `__set_name__` gives each field its name, and `__init_subclass__` collects them. This is the lightest-tool rule of section 19 in action.
- **Column names come from your own field list, values always go through `?`.** `filter(conn, **kw)` must reject unknown keyword names instead of pasting them into SQL.
- **Error messages name the field**, as in section 12: `Book.pages must be int, got str`.

The design deliberately stops here: writing `save`, `get` and `filter`, and the tests that pin them, is the project.

## 23. Summary

**Attribute access is a function call in disguise.** `obj.x` runs `type(obj).__getattribute__`, which follows one algorithm:

```text
data descriptor on type(obj)  >  obj.__dict__  >  non-data descriptor / class attribute  >  __getattr__
```

- **Assignment** (`obj.x = v`): a descriptor's `__set__` if the class has one, else `obj.__dict__`. Special methods (`len`, `+`) are looked up on the **type only**.
- **Hooks** (sections 3 to 5): `__getattr__` runs only when lookup fails, and must raise `AttributeError` for unknown names. `__getattribute__` runs for every read; `__setattr__` and `__delattr__` for every write and delete. Inside them, use `super()` or `object.__...__` to avoid recursion.
- **Descriptors** (sections 6 to 8): objects on a class with `__get__(self, instance, owner)`, `__set__`, `__delete__`. **Data** descriptors (with `__set__` or `__delete__`) beat the instance dictionary; **non-data** descriptors lose to it. Return `self` when `instance is None`. `__set_name__` tells a descriptor its name at class creation. Store per-instance values in `instance.__dict__`, never on the descriptor.
- **Bound methods** (section 9): functions are non-data descriptors. `obj.f` calls `function.__get__(obj, type(obj))`, which returns a new `types.MethodType` with `__func__` and `__self__`; calling it calls `__func__(__self__, *args)`. That is where `self` comes from, and why `obj.f is obj.f` is `False`.
- **Built-ins revealed** (sections 10 to 13): `property` is a data descriptor calling `fget`/`fset`/`fdel`; `classmethod` binds to `owner`; `staticmethod` returns the plain function; `cached_property` is a non-data descriptor that writes into `__dict__` and then gets out of the way; `__slots__` entries are member (data) descriptors.
- **Validated fields** (section 12): a `Validator` base does the descriptor plumbing; subclasses (`Typed`, `Range`, `OneOf`, `All`) implement `validate`. Messages name `Class.field`.
- **Class creation** (sections 14 to 18): `__init_subclass__` runs on the parent for each new subclass; `__class_getitem__` handles `Cls[item]`; `type(name, bases, ns)` builds a class. A `class` statement runs: resolve metaclass, `__prepare__`, body, `__new__` (which calls `__set_name__`, then `__init_subclass__`), `__init__`, then decorators. A metaclass `__call__` controls `Cls(...)`.
- **Judgment** (sections 19, 20): use the lightest tool: plain code, `property`, dataclass, descriptor, class decorator or `__init_subclass__`, and only then `__getattr__`, metaclasses or `__getattribute__`. Magic costs readability, debugging, tool support and composability; it pays off mainly in frameworks.

The idea underneath the whole chapter: **Python's "magic" is ordinary objects following a few documented rules.** Once you know the rules, you can read any framework's source, and you can also see when the plainest code is the best design.
