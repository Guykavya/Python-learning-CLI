# Chapter 16: Advanced typing

In chapter 9 you learned the basic vocabulary: `int`, `list[str]`, `str | None`, `Callable`. That vocabulary is enough for small scripts. It starts to hurt in real code, and you have probably already felt it:

- You write a function that returns *the first item of a list*. What is its return type? For `list[int]` it is `int`. For `list[str]` it is `str`. You do not want to write the function twice.
- You write a function that needs "anything with a `.close()` method". You do not care about the class. A base class feels like too much.
- You read a JSON file. You get a `dict`. It *always* has the keys `"title"` and `"year"`, but `dict[str, object]` says nothing about that.
- You write a decorator. After decorating, the editor forgets the parameters of the original function.
- A library you use has no hints at all, and every call to it turns into `Any`.

This chapter fixes all five. It gives you the **advanced** half of Python's type system: the tools that let hints describe real programs without lying and without becoming a mess.

The big ideas, in the order you meet them:

1. **Generics** (sections 3 to 7): functions and classes that work for *many* types and still keep track of which one. `TypeVar`, `class Box[T]`, bounds, constraints, and the `type` statement for aliases.
2. **Protocols** (sections 8 to 10): "anything that has these methods", checked by shape, not by inheritance.
3. **Precise shapes** (sections 11 to 16): `TypedDict` for dict-shaped records, `Literal` for a fixed set of values, `Final` for constants, `Callable` and `ParamSpec` for functions and decorators, `@overload` for functions whose result depends on the argument.
4. **Narrowing** (sections 17 and 18): how a checker learns more about a value from an `if`, and how you teach it new tricks with `TypeGuard` and `TypeIs`.
5. **`Any` versus `object`** (section 19): two types that look similar and behave in opposite ways.
6. **The outside world** (section 20): typing code you do not own, stub files, and the `py.typed` marker.
7. **Strategy and project** (sections 21 to 23): how to add types to an existing codebase *step by step*, and a project where you take an earlier program all the way to **mypy strict clean**.

By the end you can reach the three outcomes of this module:

- Write a **generic, fully typed container class**.
- **Explain when to use a `Protocol` instead of a base class**.
- Get a real project **clean under `mypy --strict`**.

**A note on how examples are shown.** Like in earlier chapters, every block that has output was really run. Python output comes from **Python 3.14** on Linux. Type-checker output comes from **mypy 2.4.0** run as `python -m mypy --strict file.py`. mypy's wording can change a little between versions, so read the *meaning* and the error code in square brackets, such as `[arg-type]`. To save space, mypy's last line (`Found N errors in 1 file`) is left out; the `Success` line is kept. Where a real message is long, a note says so.

**Python version.** This chapter uses the syntax of **Python 3.12 and newer**: `def f[T](...)`, `class Box[T]:` and `type Alias = ...`. A lot of real code still uses the older spelling with `TypeVar` and `Generic`. Both are shown side by side, because you will meet both. Everything works the same way; only the spelling differs.

**How to read this chapter.** Type the examples. Every few pages there is a **Try it**. Decide your answer on paper *before* you open it. When a Try it asks for a type checker verdict ("error" or "ok"), reason from the rules in the section first. You do not need mypy to answer; mypy is only there to confirm.

## Table of contents

1. [Why more typing, and what stays true](#1-why-more-typing-and-what-stays-true)
2. [Looking at types at runtime](#2-looking-at-types-at-runtime)
3. [Generic functions and `TypeVar`](#3-generic-functions-and-typevar)
4. [Generic classes](#4-generic-classes)
5. [Type aliases and the `type` statement](#5-type-aliases-and-the-type-statement)
6. [Bounded and constrained type variables](#6-bounded-and-constrained-type-variables)
7. [A generic repository](#7-a-generic-repository)
8. [Protocols: structural typing](#8-protocols-structural-typing)
9. [Protocol details](#9-protocol-details)
10. [Protocol or base class?](#10-protocol-or-base-class)
11. [`TypedDict`](#11-typeddict)
12. [`Literal`](#12-literal)
13. [`Final` and `@final`](#13-final-and-final)
14. [`Callable` and function types](#14-callable-and-function-types)
15. [`ParamSpec`: decorators that keep the signature](#15-paramspec-decorators-that-keep-the-signature)
16. [`@overload`](#16-overload)
17. [Type narrowing](#17-type-narrowing)
18. [`TypeGuard` and `TypeIs`](#18-typeguard-and-typeis)
19. [`Any` versus `object`](#19-any-versus-object)
20. [Typing code you do not own: stubs and `py.typed`](#20-typing-code-you-do-not-own-stubs-and-pytyped)
21. [Gradual typing strategy](#21-gradual-typing-strategy)
22. [Two worked designs: an event emitter and an LRU cache](#22-two-worked-designs-an-event-emitter-and-an-lru-cache)
23. [Project: a fully typed refactor, mypy strict clean](#23-project-a-fully-typed-refactor-mypy-strict-clean)
24. [Common traps](#24-common-traps)
25. [Summary](#25-summary)

## 1. Why more typing, and what stays true

### 1.1 Three facts from chapter 9 that still hold

Everything advanced in this chapter sits on three facts. Keep them in front of you.

1. **Python does not enforce hints.** A hint is a note for humans and tools. The program runs the same with or without it.
2. **mypy is a separate program.** It reads your source *without running it* and tells you where the notes do not fit together.
3. **A hint is a promise to the checker, not a check.** If you lie in a hint, nothing stops you at run time. The checker simply believes you, and its later conclusions are wrong.

The third fact matters more as hints get fancier: a wrong fancy hint (say, a decorator that "keeps the signature" but does not) is worse than no hint, because it gives false confidence.

None of the tools in this chapter does anything at run time that you could not do by hand. They all exist for one reason: **to let a checker follow your reasoning**. Two questions guide every section: *what does this tool let me say?* and *what does the checker do with it?*

### 1.3 Both spellings, side by side

Since Python 3.12 the type parameters are part of the language syntax. Before that you built them with helper objects from `typing`. You will meet both in real projects, so here is the map for the whole chapter:

| Idea | Python 3.12+ spelling | Older spelling |
| --- | --- | --- |
| generic function | `def first[T](xs: list[T]) -> T:` | `T = TypeVar("T")` then `def first(xs: list[T]) -> T:` |
| generic class | `class Box[T]:` | `class Box(Generic[T]):` |
| type alias | `type Row = list[int]` | `Row: TypeAlias = list[int]` |
| bound / constraints | `def f[T: Base](...)`, `def f[T: (int, str)](...)` | `TypeVar("T", bound=Base)`, `TypeVar("T", int, str)` |
| ParamSpec | `def f[**P, R](...)` | `P = ParamSpec("P")` |

The new spelling has two practical advantages: you do not have to declare a variable at the top of the file, and each type parameter belongs to **one** function or class, so you cannot accidentally share `T` between unrelated things. If you must support Python older than 3.12, use the old spelling.

### 1.4 `reveal_type`, once more

`reveal_type(expr)` asks mypy "what type do you think this is?". It only works under mypy: Python itself raises `NameError`. You will see it all through this chapter. A block that contains it is shown with mypy output only.

## 2. Looking at types at runtime

Hints are not only for checkers. Python keeps them on the function or class object, and you can read them. This is useful for tools that build things from hints (validators, documentation generators, command line parsers), and it is how the exercises of this chapter check your work *without* running mypy. So learn the toolbox now.

### 2.1 `__annotations__`, `get_type_hints` and `inspect.signature`

```python
from typing import get_type_hints, get_origin, get_args, Optional, Union
import inspect


def f(a: int, b: "list[str]", c: int | None = None, *rest: float,
      key: str = "k", **kw: object) -> dict[str, int]:
    return {}


print(f.__annotations__)
print(get_type_hints(f))
print(inspect.signature(f))
```
```text
$ python rt_hints.py
{'a': <class 'int'>, 'b': 'list[str]', 'c': int | None, 'rest': <class 'float'>, 'key': <class 'str'>, 'kw': <class 'object'>, 'return': dict[str, int]}
{'a': <class 'int'>, 'b': list[str], 'c': int | None, 'rest': <class 'float'>, 'key': <class 'str'>, 'kw': <class 'object'>, 'return': dict[str, int]}
(a: int, b: 'list[str]', c: int | None = None, *rest: float, key: str = 'k', **kw: object) -> dict[str, int]
```

Look at the first two lines. `__annotations__` shows `b` as the text `'list[str]'` because I wrote it in quotes. `get_type_hints` **evaluates** such text and gives the real type `list[str]`. Prefer `get_type_hints` when you want types you can work with.

Two helpers take a type apart:

```python
from typing import get_origin, get_args, Optional, Union, Callable

print(get_origin(list[int]), get_args(list[int]))
print(get_origin(dict[str, int]), get_args(dict[str, int]))
print(get_origin(int | None), get_args(int | None))
print(get_origin(Callable[[int], str]), get_args(Callable[[int], str]))
print(get_origin(int), get_args(int))
print(Optional[int] == (int | None), Union[int, str] == (int | str))
```
```text
$ python rt_origin.py
<class 'list'> (<class 'int'>,)
<class 'dict'> (<class 'str'>, <class 'int'>)
<class 'typing.Union'> (<class 'int'>, <class 'NoneType'>)
<class 'collections.abc.Callable'> ([<class 'int'>], <class 'str'>)
None ()
True True
```

`get_origin` gives the "outer" type and `get_args` the pieces inside the brackets. A plain class such as `int` has no origin (`None`) and no arguments (`()`). The last line shows that the old `Optional[int]` and `Union[int, str]` are the same objects as `int | None` and `int | str`.

A function without hints has an empty `__annotations__`, and its signature's `return_annotation` is `inspect.Signature.empty`. A tool that asks "how much of this module is typed?" looks for exactly that. You will write one in Try it 2.1.

### 2.2 Forward references and Python 3.14

Sometimes a hint names a class that is not defined yet:

```python
from typing import get_type_hints


class Node:
    next: "Node | None"
    value: int


print(Node.__annotations__)
print(get_type_hints(Node))


def f(x: Missing) -> None: ...


class Missing: ...


print(get_type_hints(f))
```
```text
$ python rt_forward.py
{'next': 'Node | None', 'value': <class 'int'>}
{'next': __main__.Node | None, 'value': <class 'int'>}
{'x': <class '__main__.Missing'>, 'return': <class 'NoneType'>}
```

In older Python (3.13 and earlier) the line `def f(x: Missing)` would crash immediately with `NameError`, because the hint was evaluated when the function was defined. You had to write `x: "Missing"` or add `from __future__ import annotations`. **Python 3.14 evaluates annotations lazily**, so the definition is fine, and the error only appears if something asks for the hints before `Missing` exists. Rule of thumb for code that must run on 3.12 and 3.13: put forward references in quotes.

### Try it 2.1

Write a function `coverage(func)` that returns the fraction (a float from 0 to 1) of a function's parameters and return value that have annotations. A function `def f(a: int, b)` has three slots (`a`, `b`, return) and two of them are empty... which one is annotated?

<details><summary>Answer</summary>

Only `a` is annotated, so the answer is `1/3`. Use `inspect.signature`: its parameters have `.annotation` equal to `inspect.Parameter.empty` when missing, and `return_annotation` equals `inspect.Signature.empty`.

```python
import inspect
from collections.abc import Callable


def coverage(func: Callable[..., object]) -> float:
    sig = inspect.signature(func)
    slots = [p.annotation is not inspect.Parameter.empty for p in sig.parameters.values()]
    slots.append(sig.return_annotation is not inspect.Signature.empty)
    return sum(slots) / len(slots)


def f(a: int, b): ...


print(coverage(f))
```

```text
0.3333333333333333
```

</details>

## 3. Generic functions and `TypeVar`

### 3.1 The problem: one function, many types

Here is the "first item" function. Which hints can you give it?

```python
def first_int(items: list[int]) -> int:
    return items[0]
```

This works only for lists of ints. A list of names needs `first_str`, a list of floats needs `first_float`. The body is identical every time. The tempting fix is `Any`:

```python
from typing import Any


def first_any(items: list[Any]) -> Any:
    return items[0]


names = ["ada", "alan"]
x = first_any(names)
reveal_type(x)
print(x.upper())
print(x.no_such_method())
```
```text
$ python -m mypy --strict generic_any.py
generic_any.py:10: note: Revealed type is "Any"
Success: no issues found in 1 source file
```

mypy says: no problem, anywhere. `x` is `Any`, so mypy stops checking it, and even `x.no_such_method()` goes through (it would crash at run time). `Any` solved "one function for all types" by **throwing the type away**.

What we want to say is: "the thing that comes out has **the same type as the items that went in**". That sentence has a name in it ("the same type as...") that must be shared between the parameter and the result. That name is a **type variable**.

### 3.2 `TypeVar`, the older spelling

```python
from typing import TypeVar

T = TypeVar("T")


def first_item(items: list[T]) -> T:
    return items[0]


print(first_item([3, 1, 2]))
print(first_item(["ada", "alan"]))
print(first_item.__annotations__)
print(T, T.__name__, T.__bound__, T.__constraints__)
```
```text
$ python tv_old.py
3
ada
{'items': list[~T], 'return': ~T}
~T T None ()
```

`T = TypeVar("T")` creates a type variable. The string must match the variable name. Read the signature as: "for any type `T`: takes a list of `T`, returns a `T`". At run time `T` is a small object and the function runs like any other. The checker is where `T` has meaning: for each *call* it looks at the argument, solves for `T` (`int` for `first_item([3, 1, 2])`, `str` for the names) and puts that type in place of `T` in the result.

### 3.3 The 3.12 spelling: `def first_item[T](...)`

```python
def first_item[T](items: list[T]) -> T:
    return items[0]


print(first_item([3, 1, 2]))
print(first_item.__type_params__)
print(first_item.__annotations__)
```
```text
$ python tv_new.py
3
(T,)
{'items': list[T], 'return': T}
```

The `[T]` right after the function name declares `T` for this function only; no separate line is needed. `__type_params__` lists the declared parameters. The checker sees exactly the same thing: `first_item([1.5])` is a `float`.

### 3.4 When is a type variable needed?

When the **same unknown type appears in at least two places** in the signature (parameters and return type, or two parameters). If `T` appears only once, it carries no information and a plain type is better. `first[T](xs: list[T]) -> T`, `pair[A, B](a: A, b: B) -> tuple[A, B]` and `to_list[T](xs: Sequence[T]) -> list[T]` are typical.

### 3.5 How the checker solves for `T`

For each call, mypy collects what each argument says about `T`, then picks the **most specific type that fits all of them**. When the arguments disagree, it moves up to a common supertype (the "join"). In the worst case that is `object`.

```python
def same[T](a: T, b: T) -> T:
    return a


reveal_type(same(1, 2))
reveal_type(same(1, 2.5))
reveal_type(same(1, "a"))
reveal_type(same([1], ["a"]))
x: float = same(1, 2)
y: str = same(1, 2)
```
```text
$ python -m mypy --strict tv_infer.py
tv_infer.py:5: note: Revealed type is "int"
tv_infer.py:6: note: Revealed type is "float"
tv_infer.py:7: note: Revealed type is "object"
tv_infer.py:8: note: Revealed type is "object"
tv_infer.py:10: error: Incompatible types in assignment (expression has type "int", variable has type "str")  [assignment]
```

Read the verdicts one by one:

- `same(1, 2)` is `int`: both arguments say `int`.
- `same(1, 2.5)` is `float`: an `int` may be used where a `float` is expected, so `float` fits both.
- `same(1, "a")` is `object`: the only type that fits both is `object`. mypy **does not complain**. This is the most surprising rule: a generic function with two `T` parameters accepts two unrelated arguments and quietly widens. If you wanted "both must be the same", `same` cannot say it; you need a bound or constraints (section 6).
- `same([1], ["a"])` is `object` too: `list[int]` and `list[str]` share only `object` (lists are invariant, section 4.5).
- `y: str = same(1, 2)` is an error: the result is `int`, not `str`.

A type variable that appears **only in the return type** cannot be solved from the arguments:

```python
def make[T]() -> T:
    raise NotImplementedError
```
```text
$ python -m mypy --strict tv_return_only.py
tv_return_only.py:1: error: A function returning TypeVar should receive at least one argument containing the same TypeVar  [type-var]
```

What the message says: the caller would have to *guess* `T`. Remove the variable, or add a parameter that carries it.

### Try it 3.1

Write a generic function `last_item` that returns the last element of a list. Then say what mypy reveals for `last_item([1.5, 2.5])` and for `last_item(["a", None])`.

<details><summary>Answer</summary>

```python
def last_item[T](items: list[T]) -> T:
    return items[-1]
```

For `[1.5, 2.5]`, `T` is `float`, so the result is `float`. For `["a", None]` the list itself has the type `list[str | None]`, so `T` is `str | None`.

</details>

### Try it 3.2

What is wrong with `def parse[T](text: str) -> T: ...`, and how can a caller say which type it wants?

<details><summary>Answer</summary>

`T` appears only in the return type, so nothing tells the checker what `T` is. Pass something that *carries* `T`, for example the function that builds the value:

```python
from collections.abc import Callable


def parse[T](text: str, kind: Callable[[str], T]) -> T:
    return kind(text)


print(parse("12", int) + 1)
```

`int` is a callable from `str` to `int`, so `T` is solved as `int` and `parse("12", int)` is an `int` for the checker.

```text
13
```

</details>

## 4. Generic classes

### 4.1 A stack that remembers what it holds

Functions can be generic. Classes can too, and this is where generics matter most: every container in the standard library (`list[int]`, `dict[str, float]`) is a generic class. Here is a stack in the older spelling first:

```python
from typing import Generic, TypeVar

T = TypeVar("T")


class Stack(Generic[T]):
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()

    def __len__(self) -> int:
        return len(self._items)


nums = Stack[int]()
nums.push(1)
nums.push(2)
print(nums.pop(), len(nums))
print(Stack.__orig_bases__)
print(Stack.__parameters__)
print(Stack[int])
print(type(nums))
```
```text
$ python stack_old.py
2 1
(typing.Generic[~T],)
(~T,)
__main__.Stack[int]
<class '__main__.Stack'>
```

Three things to notice.

- `class Stack(Generic[T])` marks the class as generic in `T`. Inside the class, `T` is "whatever the user chose".
- `Stack[int]()` **chooses** `T = int`. The brackets are an ordinary expression: `Stack[int]` is a small alias object, and calling it builds a normal `Stack`.
- `type(nums)` is plain `Stack`. The `[int]` is **not remembered** by the object at run time. It exists for the checker.

Now what the checker does with it, in the 3.12 spelling (it adds `Generic[T]` as a base for you, see `Stack.__orig_bases__`, and lists the parameters in `Stack.__type_params__`):

```python
class Stack[T]:
    def __init__(self) -> None:
        self._items: list[T] = []

    def push(self, item: T) -> None:
        self._items.append(item)

    def pop(self) -> T:
        return self._items.pop()


nums = Stack[int]()
nums.push(1)
s = Stack[str]()
s.push("a")
s.push(5)
reveal_type(nums.pop())
reveal_type(s.pop())
t = Stack()
```
```text
$ python -m mypy --strict stack_check.py
stack_check.py:16: error: Argument 1 to "push" of "Stack" has incompatible type "int"; expected "str"  [arg-type]
stack_check.py:17: note: Revealed type is "int"
stack_check.py:18: note: Revealed type is "str"
stack_check.py:19: error: Need type annotation for "t"  [var-annotated]
```

Python itself does not enforce the type argument: `Stack()` with no brackets works, and so would pushing a string into a `Stack[int]`. When a generic object is built without brackets, the checker works out the parameter from the constructor arguments. For a container that starts empty, it cannot, and it asks for an annotation: `s: Stack[int] = Stack()`. So `Stack[int]()` or a variable annotation is common.

### 4.3 More than one type parameter

```python
class Pair[A, B]:
    def __init__(self, first: A, second: B) -> None:
        self.first = first
        self.second = second

    def swap(self) -> "Pair[B, A]":
        return Pair(self.second, self.first)


p = Pair(1, "one")
reveal_type(p)
reveal_type(p.swap())
```
```text
$ python -m mypy --strict pair.py
pair.py:11: note: Revealed type is "pair.Pair[int, str]"
pair.py:12: note: Revealed type is "pair.Pair[str, int]"
Success: no issues found in 1 source file
```

Here the type was inferred from the constructor arguments: `Pair(1, "one")` is `Pair[int, str]`, and `swap()` flips the parameters. (The quotes around `"Pair[B, A]"` are a forward reference: the class is not finished while its own methods are being defined. On 3.14 you may drop them.)

### 4.4 Subclassing a generic class

You can choose the parameter in the class statement:

```python
from typing import Generic, TypeVar

T = TypeVar("T")


class Box(Generic[T]):
    def __init__(self, item: T) -> None:
        self.item = item


class IntBox(Box[int]):
    pass


b = Box[str](5)
print(b.item, type(b))
print(IntBox.__orig_bases__, IntBox.__bases__)
```
```text
$ python generic_sub.py
5 <class '__main__.Box'>
(__main__.Box[int],) (<class '__main__.Box'>,)
```

`IntBox(Box[int])` fixes `T` to `int`; `IntBox` itself is not generic any more. `Box[str](5)` stores an `int` in a "`Box[str]`" and Python does not care: the parameter is not kept at run time. For the same reason `isinstance(b, Box[int])` raises `TypeError`; use plain `isinstance(b, Box)`.

### 4.5 Variance in one page

Is a `list[int]` acceptable where a `list[float]` is expected? An `int` can be used as a `float`, so it feels fine, but it is not. If it were accepted where a `list[float]` is expected, a function could `append(2.5)` to it and break the promise that it holds only ints. So `list` is **invariant**: `list[int]` is *not* a `list[float]`. mypy even suggests the fix: a type that is only **read**, such as `Sequence[float]`, is **covariant**, and accepts `list[int]`.

With the new syntax you do not declare variance at all: the checker **infers** it from how `T` is used in the class.

`ReadOnly[T]` (a class with a method that only *returns* a `T`) is accepted as `ReadOnly[float]` when you hold a `ReadOnly[int]`; `Mut[T]` (a class with a public writable attribute of type `T`) is **not**, because someone could write a float into it. With the old spelling you declare this yourself: `TypeVar("T", covariant=True)`. You will rarely need to think harder about variance than this.

### 4.6 `Self`: a method that returns "the same class"

A method that returns `self` should be annotated `-> Self` (from `typing`), not with the class name; then a subclass keeps its own type: `SubNode().link(SubNode())` is a `SubNode`, not a `Node`. `Self` is itself a kind of type variable that the checker fills in for you.

### Try it 4.1

Write a generic class `Queue[T]` with methods `put(item: T) -> None`, `get() -> T` (first in, first out) and `__len__`. Use `collections.deque`.

<details><summary>Answer</summary>

```python
from collections import deque


class Queue[T]:
    def __init__(self) -> None:
        self._items: deque[T] = deque()

    def put(self, item: T) -> None:
        self._items.append(item)

    def get(self) -> T:
        return self._items.popleft()

    def __len__(self) -> int:
        return len(self._items)


q = Queue[str]()
q.put("a")
q.put("b")
print(q.get(), len(q))
```

```text
a 1
```

The one trap is the `deque[T]` annotation on `self._items`. Without it the checker cannot know what the empty deque holds.

</details>

## 5. Type aliases and the `type` statement

### 5.1 Names for long types

Long types are hard to read and easy to mistype. An **alias** gives one a short name:

```python
type Number = int | float
type Matrix = list[list[float]]
type Pair[T] = tuple[T, T]

print(Number)
print(type(Number))
print(Number.__name__, Number.__value__)
print(Pair, Pair.__type_params__)
print(Pair[int])
```
```text
$ python alias_basic.py
Number
<class 'typing.TypeAliasType'>
Number int | float
Pair (T,)
Pair[int]
```

The `type` statement (Python 3.12) creates a `TypeAliasType` object. Its right-hand side is **evaluated lazily**: only when someone asks for `__value__`. This is what makes **recursive** aliases possible, such as the shape of any JSON value:

```python
type Json = dict[str, Json] | list[Json] | str | int | float | bool | None

print(Json.__value__)
```
```text
$ python alias_json.py
dict[str, Json] | list[Json] | str | int | float | bool | None
```

`Json` refers to itself on the right side. With the old spelling that is impossible to write without quoting.

An alias can be **generic**, as `Pair[T]` is. `Pair[float]` means `tuple[float, float]`:

```python
import math

type Number = int | float
type Pair[T] = tuple[T, T]


def total(xs: list[Number]) -> Number:
    return sum(xs)


def dist(p: Pair[float], q: Pair[float]) -> float:
    return math.hypot(p[0] - q[0], p[1] - q[1])


reveal_type(total([1, 2.5]))
reveal_type(dist((0, 0), (3, 4)))
dist((0, 0), (3, 4, 5))
```
```text
$ python -m mypy --strict alias_use.py
alias_use.py:15: note: Revealed type is "int | float"
alias_use.py:16: note: Revealed type is "float"
alias_use.py:17: error: Argument 2 to "dist" has incompatible type "tuple[int, int, int]"; expected "tuple[float, float]"  [arg-type]
```

### 5.2 The older spellings

Before 3.12 you wrote a plain assignment, optionally marked with `TypeAlias`:

```python
from typing import TypeAlias

IntOrStr: TypeAlias = int | str
OldMatrix = list[list[float]]
print(IntOrStr, type(IntOrStr))
print(isinstance(3, IntOrStr))
```
```text
$ python alias_old.py
int | str <class 'typing.Union'>
True
```

The old spellings are ordinary values: `IntOrStr` really is the union object, so it even works in `isinstance`. A `type` alias is a special object meant only for annotations (`isinstance(3, Number)` raises `TypeError`). Without `TypeAlias`, a plain assignment may be read as a normal variable, which is why `TypeAlias` was invented. Use `type` on 3.12+.

### 5.3 An alias is a name, not a new type

`type UserId = int` creates no new type: a function taking `UserId` accepts any `int`. For a type that cannot be mixed up with `int`, use `NewType("UserId", int)` or a class.

### Try it 5.1

Write a generic alias `Grid[T]` for a list of lists of `T`, and a function `width(g: Grid[str]) -> int` that returns the length of the first row (0 for no rows).

<details><summary>Answer</summary>

```python
type Grid[T] = list[list[T]]


def width(g: Grid[str]) -> int:
    return len(g[0]) if g else 0


print(width([["a", "b"], ["c", "d"]]), width([]))
```

```text
2 0
```

</details>

## 6. Bounded and constrained type variables

An unrestricted `T` accepts any type, which means that **inside the function you can do nothing with it**: not `T + T`, not `T.upper()`. To do something useful, you have to restrict `T`. There are two ways, and they are *not* the same.

### 6.1 A bound: "`T` is this type or a subtype"

```python
class Animal:
    def name(self) -> str:
        return "animal"


class Dog(Animal):
    def bark(self) -> str:
        return "woof"


def loudest[A: Animal](a: A) -> A:
    print(a.name().upper())
    return a


d = loudest(Dog())
reveal_type(d)
print(d.bark())
loudest(42)
```
```text
$ python -m mypy --strict bound.py
bound.py:17: note: Revealed type is "bound.Dog"
bound.py:19: error: Value of type variable "A" of "loudest" cannot be "int"  [type-var]
```

`A: Animal` is a **bound**. Inside the function, `a` can use everything `Animal` has. The result keeps the *precise* type: `Dog`, so `d.bark()` is allowed. Compare with `def loudest(a: Animal) -> Animal`, which would have returned a plain `Animal` and forced you to cast before calling `bark()`. The old spelling is `A = TypeVar("A", bound=Animal)`.

A bound is the right tool for "any subclass of X, and give me the same subclass back".

### 6.2 Constraints: "`T` is exactly one of these"

```python
def double[S: (str, bytes)](x: S) -> S:
    return x + x


reveal_type(double("ab"))
reveal_type(double(b"ab"))
double(3)
```
```text
$ python -m mypy --strict constraints.py
constraints.py:5: note: Revealed type is "str"
constraints.py:6: note: Revealed type is "bytes"
constraints.py:7: error: Value of type variable "S" of "double" cannot be "int"  [type-var]
```

`S: (str, bytes)` lists **constraints**. The old spelling is `TypeVar("S", str, bytes)`. A call must use one of them, and the checker type-checks the function body **once for each constraint**: it checks `x + x` as `str + str`, then as `bytes + bytes`. That is why the body is legal.

Contrast it with a union, `def double_union(x: str | bytes) -> str | bytes: return x + x`. The checker must consider `x` being `str` **or** `bytes`, and rejects `x + x` because the two might be mixed (the real output has two such errors). The union also *forgets the link* between input and output: put in a `str`, get back `str | bytes`. A constrained type variable keeps it: `str` in, `str` out.

### 6.3 Bound, constraints, union: which one?

| You want to say | Use |
| --- | --- |
| "any subtype of `X`, and return the same subtype" | bound: `T: X` |
| "exactly `int` or exactly `str`; the body needs a different check for each" | constraints: `T: (int, str)` |
| "either kind, but the output type need not match the input" | a union: `int | str` |

A subtle difference: with constraints, a *subclass* is treated as its constraint. If you pass a `MyStr(str)` to `double`, the result is `str`, not `MyStr`. A bound would keep `MyStr`. When in doubt, choose the bound.

### 6.4 A bound that names a protocol

The most useful bound in practice is "anything that supports an operation", for example `<`:

```python
from typing import Any, Protocol


class Comparable(Protocol):
    def __lt__(self, other: Any, /) -> bool: ...


def max_of[C: Comparable](a: C, b: C) -> C:
    return b if a < b else a


reveal_type(max_of(3, 5))
reveal_type(max_of("a", "b"))
max_of(object(), object())
```
```text
$ python -m mypy --strict bound_proto.py
bound_proto.py:12: note: Revealed type is "int"
bound_proto.py:13: note: Revealed type is "str"
bound_proto.py:14: error: Value of type variable "C" of "max_of" cannot be "object"  [type-var]
```

`Protocol` is the subject of the next three sections: here read it as "any type with a `__lt__` method". `int` and `str` have one; a bare `object` does not. The standard library ships a ready-made version in the type stubs (`SupportsRichComparison`), but writing your own once teaches you how bounds and protocols fit together.

A bound and constraints are stored on the type variable (`f.__type_params__[0].__bound__`), and as always **nothing is enforced** at run time.

### Try it 6.1

Pick bound, constraints or union for each: (a) `def clamp(x, low, high)` that works for `int` and `float` and returns the same kind it was given; (b) `def describe(x)` that takes an `int` or a `str` and always returns a `str`; (c) `def newest[?](items)` taking a list of any `Event` subclass and returning an item of the same subclass.

<details><summary>Answer</summary>

(a) Constraints `(int, float)`: the body is the same for both, and the result must match the input. (A bound to a protocol also works.) (b) A union `int | str`: input and output are not linked. (c) A bound `[E: Event]` with `list[E]` in, `E` out.

</details>

## 7. A generic repository

A **repository** stores objects by id. The same code should work for users, tags and orders, and each repository should remember what it holds. This is a typical generic class, so here is a design from start to end.

```python
class Entity:
    def __init__(self, id: int) -> None:
        self.id = id


class User(Entity):
    def __init__(self, id: int, name: str) -> None:
        super().__init__(id)
        self.name = name


class Tag:
    def __init__(self, label: str) -> None:
        self.label = label


class Repository[T: Entity]:
    def __init__(self) -> None:
        self._items: dict[int, T] = {}

    def add(self, item: T) -> None:
        self._items[item.id] = item

    def get(self, id: int) -> T | None:
        return self._items.get(id)


users = Repository[User]()
users.add(User(1, "ada"))
reveal_type(users.get(1))
tags = Repository[Tag]()
users.add(Tag("x"))
```
```text
$ python -m mypy --strict repository.py
repository.py:30: note: Revealed type is "repository.User | None"
repository.py:31: error: Value of type variable "T" of "Repository" cannot be "Tag"  [type-var]
repository.py:32: error: Argument 1 to "add" of "Repository" has incompatible type "Tag"; expected "User"  [arg-type]
```

Decisions to notice:

1. The bound `T: Entity` is what allows the body to use `item.id`. Without it, `item.id` would be an error on an unrestricted `T`.
2. `get` returns `T | None`: a missing id is a normal case, and the checker will make every caller handle it (section 17).
3. `Repository[Tag]()` is rejected at the creation line, not later when the first `Tag` is added.

## 8. Protocols: structural typing

### 8.1 The problem with base classes

A function needs to close something. You write:

```python
def shutdown(thing: ???) -> None:
    thing.close()
```

What goes in place of `???`? Files have `.close()`. Sockets have `.close()`. Your own `Database` has `.close()`. They share no base class, and you cannot add one to the standard library's classes. This is **duck typing**: "if it has `close()`, it works". Python already runs this way. A **protocol** lets you write the duck down so that the checker can follow it.

### 8.2 A first protocol

```python
from typing import Protocol


class SupportsClose(Protocol):
    def close(self) -> None: ...


class File:
    def close(self) -> None:
        print("file closed")


class Socket:
    def close(self) -> None:
        print("socket closed")


class Rock:
    pass


def shutdown(thing: SupportsClose) -> None:
    thing.close()


shutdown(File())
shutdown(Socket())
shutdown(Rock())
```
```text
$ python -m mypy --strict proto_close.py
proto_close.py:28: error: Argument 1 to "shutdown" has incompatible type "Rock"; expected "SupportsClose"  [arg-type]
```

`File` and `Socket` **never mention** `SupportsClose`. They fit because they have a method `close(self) -> None`. `Rock` does not, so the call is rejected. This is **structural typing** ("same shape"), as opposed to **nominal typing** ("same name in the inheritance tree"), which is what base classes give you.

The body of the protocol method is `...`. A protocol is not code that runs; it only describes a shape.

### 8.3 Matching rules, and run time

A class matches if, for each member the protocol lists, it has a member with the same name, parameters that accept at least what the protocol's method accepts, and a return type that is the same or narrower. At run time a protocol is almost nothing: by default it cannot be used with `isinstance` and it cannot be instantiated (`TypeError: Protocols cannot be instantiated`). It exists for the checker. Section 9 shows a limited run-time check.

### Try it 8.1

Define a protocol `HasArea` with one method `area(self) -> float`, and a function `total_area(shapes: list[HasArea]) -> float`. Then write two unrelated classes `Square` and `Circle` that satisfy it without inheriting from it.

<details><summary>Answer</summary>

```python
import math
from typing import Protocol


class HasArea(Protocol):
    def area(self) -> float: ...


class Square:
    def __init__(self, side: float) -> None:
        self.side = side

    def area(self) -> float:
        return self.side**2


class Circle:
    def __init__(self, r: float) -> None:
        self.r = r

    def area(self) -> float:
        return math.pi * self.r**2


def total_area(shapes: list[HasArea]) -> float:
    return sum(s.area() for s in shapes)


print(round(total_area([Square(2), Circle(1)]), 3))
```

```text
7.142
```

A caveat that bites: `list[HasArea]` is a *list of the protocol*. Passing a variable of type `list[Square]` is rejected, because lists are invariant (section 4.5). Use `Sequence[HasArea]` or `Iterable[HasArea]` for parameters that only read.

</details>

## 9. Protocol details

### 9.1 Attributes and properties

A protocol can describe data members, not only methods:

```python
from typing import Protocol


class Plugin(Protocol):
    name: str
    version: int

    def run(self, data: str) -> str: ...


class Upper:
    name = "upper"
    version = 1

    def run(self, data: str) -> str:
        return data.upper()


class Broken:
    name = "broken"

    def run(self, data: str) -> str:
        return data


def apply(p: Plugin, text: str) -> str:
    return p.run(text)


apply(Upper(), "x")
apply(Broken(), "x")
```
```text
$ python -m mypy --strict proto_attr.py
proto_attr.py:31: error: Argument 1 to "apply" has incompatible type "Broken"; expected "Plugin"  [arg-type]
proto_attr.py:31: note: "Broken" is missing following "Plugin" protocol member:
proto_attr.py:31: note:     version
```

mypy even tells you *what* is missing (`version`); a method with a conflicting signature is reported with both signatures. Note that a class-level `name = "upper"` and an instance attribute set in `__init__` both count as attributes.

There is a catch. `name: str` in a protocol means **a settable attribute**. A class that exposes a *read-only* `name` (a `@property`, or a frozen dataclass) does **not** match. If you only need to read, declare it as a read-only property:

```python
from dataclasses import dataclass
from typing import Protocol


class Named(Protocol):
    name: str


class NamedRO(Protocol):
    @property
    def name(self) -> str: ...


@dataclass(frozen=True)
class Frozen:
    name: str


def hello(n: Named) -> str:
    return n.name


def hello_ro(n: NamedRO) -> str:
    return n.name


hello(Frozen("a"))
hello_ro(Frozen("a"))
```
```text
$ python -m mypy --strict proto_property.py
proto_property.py:27: error: Argument 1 to "hello" has incompatible type "Frozen"; expected "Named"  [arg-type]
proto_property.py:27: note: Protocol member Named.name expected settable variable, got read-only attribute
```

Rule: **if the function only reads the attribute, declare it as a property in the protocol.** It accepts the most classes.

### 9.2 `@runtime_checkable`: a limited `isinstance`

```python
from typing import Protocol, runtime_checkable


@runtime_checkable
class SupportsClose(Protocol):
    def close(self) -> None: ...


class File:
    def close(self) -> None: ...


class Rock:
    pass


class WrongClose:
    def close(self, force: bool, now: int) -> str:
        return "?"


print(isinstance(File(), SupportsClose))
print(isinstance(Rock(), SupportsClose))
print(isinstance(WrongClose(), SupportsClose))
```
```text
$ python proto_rc.py
True
False
True
```

With the decorator, `isinstance` works, but it checks **only that the names exist**, not the signatures: `WrongClose` is reported as a `SupportsClose` even though its `close` has a different signature and return type. Think of it as a polite `hasattr`. Two more limits: data protocols (those with attributes) cannot be used with `issubclass`, and a check against a protocol with many members is slow-ish. Use `@runtime_checkable` when you need a branch such as "if it has `close`, close it", never as a type validator.

`isinstance` also works for protocols with data members, but the instance must really have them: a class that never sets `version` is not a `Plugin`. The standard library's `Sized` (a protocol with `__len__`) works the same way.

### 9.3 Callback protocols

A `Callable[[int], str]` cannot describe keyword-only arguments or default values. A protocol with `__call__` can:

```python
from typing import Protocol


class Handler(Protocol):
    def __call__(self, event: str, *, retries: int = 0) -> bool: ...


def good(event: str, *, retries: int = 0) -> bool:
    return True


def no_kw(event: str) -> bool:
    return True


h1: Handler = good
h2: Handler = no_kw
```
```text
$ python -m mypy --strict proto_callback.py
proto_callback.py:17: error: Incompatible types in assignment (expression has type "Callable[[str], bool]", variable has type "Handler")  [assignment]
proto_callback.py:17: note: "Handler.__call__" has type "def __call__(self, event: str, *, retries: int = ...) -> bool"
```

`no_kw` fails because it has no `retries`. (A function whose first parameter is named `e` instead of `event` would fail too: parameter names are part of the signature.) Use a callback protocol when names, keyword-only parameters or defaults matter. Use plain `Callable` otherwise (section 14).

### 9.4 Generic protocols

A protocol can have type parameters: `class Repo[K, V](Protocol): def get(self, key: K) -> V | None: ...`. A class with `get` and `put` methods of matching types then counts as a `Repo[str, int]`, and `Repo[int, int]` is rejected. The standard library does this everywhere: `Iterable[T]`, `Sequence[T]` and `SupportsAbs[T]` are generic protocols (or abstract classes that behave like them). Prefer them in parameters: accept `Iterable[int]`, not `list[int]`.

### Try it 9.1

Which of these is accepted by a parameter of type `Named` (with `name: str`) and which by `NamedRO` (with a read-only `name` property)? (a) a normal class with `self.name = ...` (b) a frozen dataclass (c) a class with a `@property name`.

<details><summary>Answer</summary>

`Named`: only (a). `NamedRO`: all three. The settable attribute in `Named` is a promise that you can assign to it. A property without a setter, or a frozen dataclass field, does not keep that promise.

</details>

## 10. Protocol or base class?

You now have three ways to say "this function accepts several kinds of things".

### 10.1 What each tool does

| Tool | Relationship is | Run-time `isinstance` | Shared code | Third-party classes can join |
| --- | --- | --- | --- | --- |
| Base class (`class Shape:`) | declared by inheritance | yes, exact | yes (inherited methods) | no (you cannot edit them) |
| ABC (`class Shape(ABC)`) | declared by inheritance; abstract methods enforced | yes, exact | yes | no |
| `Protocol` | by shape, never declared | only with `@runtime_checkable`, names only | no | yes, automatically |

The ABC check at run time is real: instantiating a subclass that forgot an abstract method raises `TypeError`. The checker's verdicts differ, too:

```python
from abc import ABC, abstractmethod
from typing import Protocol


class Shape(ABC):
    @abstractmethod
    def area(self) -> float: ...


class HasArea(Protocol):
    def area(self) -> float: ...


class Square:
    def __init__(self, s: float) -> None:
        self.s = s

    def area(self) -> float:
        return self.s * self.s


def show_abc(s: Shape) -> None:
    print(s.area())


def show_proto(s: HasArea) -> None:
    print(s.area())


show_proto(Square(2))
show_abc(Square(2))
```
```text
$ python -m mypy --strict abc_vs_proto.py
abc_vs_proto.py:31: error: Argument 1 to "show_abc" has incompatible type "Square"; expected "Shape"  [arg-type]
```

`Square` has the right method but never joined the `Shape` family, so the ABC version rejects it.

### 10.2 When to choose which

Use a **`Protocol`** when:

- you are writing a *consumer* (a function or class that **uses** objects) and you only need a few methods;
- the objects come from several places, including libraries you cannot change;
- you want tests to pass in simple fakes without inheriting from anything.

Use a **base class or ABC** when:

- you are writing a *family* of related classes that **share code** (a template method, common attributes, `__init__` logic);
- you need an exact `isinstance` check at run time (for example, to dispatch on a class);
- you want the author of a new subclass to be **forced** to implement certain methods, with an immediate `TypeError` at creation.

A useful slogan: **protocols describe what a function needs; base classes describe what a class is.** A good design often uses both: a protocol at the boundary where objects arrive, and a base class inside a family.

### 10.3 Subclassing a protocol on purpose

You may inherit from a protocol explicitly. The class then inherits any methods the protocol *implemented*, and the checker verifies the class at the point where you declare it:

A protocol method with a real body acts as a default for classes that inherit it. If the body is just `...`, mypy treats the method as abstract, and instantiating a subclass that did not implement it is an error (`Cannot instantiate abstract class "Explicit" with abstract attribute "greet"`).

### Try it 10.1

A plugin system loads classes written by other teams. The host calls `plugin.run(data)`. Base class or protocol? Give two reasons.

<details><summary>Answer</summary>

A protocol. (1) The plugin authors may be in other repositories, and a protocol lets them provide the right shape without importing the host's base class. (2) The host is a consumer: it only needs `run`, so describing exactly that makes tests easy (a plain function-holding class passes). A base class would be the better choice if the host also supplied shared behaviour (logging, configuration loading) that every plugin should inherit.

</details>

## 11. `TypedDict`

### 11.1 A dict with a known shape

JSON data, config files and database rows arrive as dicts with a fixed set of keys. `dict[str, object]` forgets which keys exist and what each holds. A `TypedDict` writes the shape down:

```python
from typing import TypedDict


class Movie(TypedDict):
    title: str
    year: int


m: Movie = {"title": "Alien", "year": 1979}
print(m, type(m))
print(Movie.__annotations__)
print(sorted(Movie.__required_keys__), sorted(Movie.__optional_keys__), Movie.__total__)
bad: Movie = {"title": "x"}
print(bad)
try:
    isinstance(m, Movie)
except TypeError as e:
    print("TypeError:", e)
```
```text
$ python td_basic.py
{'title': 'Alien', 'year': 1979} <class 'dict'>
{'title': <class 'str'>, 'year': <class 'int'>}
['title', 'year'] [] True
{'title': 'x'}
TypeError: TypedDict does not support instance and class checks
```

A `TypedDict` is **a plain `dict` at run time**: `type(m)` is `dict`, `Movie(...)` just builds a dict, and the incomplete `bad` is accepted. The shape lives only in the annotations, which you can read back (`__annotations__`, `__required_keys__`). You cannot use `isinstance` with it. The checker, however, is strict:

```python
from typing import TypedDict


class Movie(TypedDict):
    title: str
    year: int


def describe(m: Movie) -> str:
    return f"{m['title']} ({m['year']})"


ok: Movie = {"title": "Alien", "year": 1979}
missing: Movie = {"title": "Alien"}
extra: Movie = {"title": "Alien", "year": 1979, "stars": 5}
wrong: Movie = {"title": "Alien", "year": "1979"}
print(ok["rating"])
ok["year"] = "x"
reveal_type(ok["title"])
reveal_type(ok.get("year"))
```
```text
$ python -m mypy --strict td_check.py
td_check.py:14: error: Missing key "year" for TypedDict "Movie"  [typeddict-item]
td_check.py:15: error: Extra key "stars" for TypedDict "Movie"  [typeddict-unknown-key]
td_check.py:16: error: Incompatible types (expression has type "str", TypedDict item "year" has type "int")  [typeddict-item]
td_check.py:17: error: TypedDict "Movie" has no key "rating"  [typeddict-item]
td_check.py:18: error: Value of "year" has incompatible type "str"; expected "int"  [typeddict-item]
td_check.py:19: note: Revealed type is "str"
td_check.py:20: note: Revealed type is "int"
```

Each mistake has its own message: missing key, extra key, wrong value type, unknown key on reading, wrong type on writing. A plain `dict[str, object]` variable is also **not** accepted as a `Movie`: the checker cannot know it has the right keys.

### 11.2 Optional keys: `total=False`, `NotRequired`, `Required`

By default every key is required. There are two ways to change that:

```python
from typing import TypedDict, NotRequired, get_type_hints


class Opt(TypedDict, total=False):
    nickname: str
    age: int


class User(TypedDict):
    name: str
    email: NotRequired[str]


print(sorted(Opt.__required_keys__), sorted(Opt.__optional_keys__))
print(sorted(User.__required_keys__), sorted(User.__optional_keys__))
print(User.__annotations__)
print(get_type_hints(User))
```
```text
$ python td_optional.py
[] ['age', 'nickname']
['name'] ['email']
{'name': <class 'str'>, 'email': typing.NotRequired[str]}
{'name': <class 'str'>, 'email': <class 'str'>}
```

`total=False` makes **all** keys optional; `NotRequired[...]` makes **one** optional in an otherwise required class, and `Required[...]` does the reverse inside a `total=False` class. A subclass adds keys. Look at the last two lines: `__annotations__` keeps the `NotRequired[...]` wrapper, `get_type_hints` removes it.

Reading an optional key needs care:

```python
from typing import TypedDict, NotRequired


class User(TypedDict):
    name: str
    email: NotRequired[str]


u: User = {"name": "Ada"}
print(u["email"])
reveal_type(u.get("email"))
if "email" in u:
    reveal_type(u["email"])
del u["name"]
```
```text
$ python -m mypy --strict td_notreq.py
td_notreq.py:11: note: Revealed type is "str | None"
td_notreq.py:13: note: Revealed type is "str"
td_notreq.py:14: error: Key "name" of TypedDict "User" cannot be deleted  [misc]
```

Plain `u["email"]` is accepted by mypy, and raises `KeyError` here. Use `u.get("email")` (type `str | None`), or test `"email" in u` first. Deleting a *required* key is an error.

### 11.3 Data from outside is still unchecked

`json.loads` returns `Any`. Declaring `-> Person` does not validate anything; the checker believes you. To really check, write a function that walks the keys. The hints give you everything you need at run time:

```python
from typing import TypedDict, NotRequired, get_type_hints, Any


class Person(TypedDict):
    name: str
    age: int
    nick: NotRequired[str]


def validate(data: dict[str, Any], schema: type) -> list[str]:
    """Return a list of problems; empty means valid."""
    problems: list[str] = []
    hints = get_type_hints(schema)
    for key in schema.__required_keys__:
        if key not in data:
            problems.append(f"missing key: {key}")
    for key, value in data.items():
        if key not in hints:
            problems.append(f"unexpected key: {key}")
            continue
        expected = hints[key]
        if not isinstance(value, expected):
            problems.append(f"{key}: expected {expected.__name__}, got {type(value).__name__}")
    return problems


print(validate({"name": "Ada", "age": 36}, Person))
print(validate({"age": "36", "x": 1}, Person))
```
```text
$ python td_validate.py
[]
['missing key: name', 'age: expected int, got str', 'unexpected key: x']
```

(Nested `TypedDict`s need a recursive call; the idea is the same.) This is the usual pattern: **type hints describe the shape, a small validator proves it at the boundary**, and from then on the rest of the program can trust the hint. (A third-party library such as pydantic does this for you; the idea is the same.)

### Try it 11.1

Write a `TypedDict` `Config` with required `host: str` and `port: int` and optional `debug: bool`. Print the required keys.

<details><summary>Answer</summary>

```python
from typing import NotRequired, TypedDict


class Config(TypedDict):
    host: str
    port: int
    debug: NotRequired[bool]


print(sorted(Config.__required_keys__))
```

```text
['host', 'port']
```

The other spelling is `class Config(TypedDict, total=False)` with `host` and `port` marked `Required[...]`.

</details>

## 12. `Literal`

### 12.1 Specific values as types

Some parameters accept only a few exact values: a file mode, a log level, a direction. `str` is too wide, because `"banana"` is also a string. `Literal` lists the allowed values:

```python
from typing import Literal

Mode = Literal["r", "w", "a"]


def open_file(path: str, mode: Mode) -> str:
    return f"{path}:{mode}"


open_file("x", "r")
open_file("x", "z")
choice = "w"
open_file("x", choice)
s = input()
open_file("x", s)


def f(m: Mode) -> int:
    if m == "r":
        return 1
    elif m == "w":
        return 2
    else:
        reveal_type(m)
        return 3
```
```text
$ python -m mypy --strict literal_basic.py
literal_basic.py:11: error: Argument 2 to "open_file" has incompatible type "Literal['z']"; expected "Literal['r', 'w', 'a']"  [arg-type]
literal_basic.py:13: error: Argument 2 to "open_file" has incompatible type "str"; expected "Literal['r', 'w', 'a']"  [arg-type]
literal_basic.py:15: error: Argument 2 to "open_file" has incompatible type "str"; expected "Literal['r', 'w', 'a']"  [arg-type]
literal_basic.py:24: note: Revealed type is "Literal['a']"
```

The checker accepts the literal `"r"` and rejects `"z"`. Look at the third case: `choice = "w"` is **inferred as `str`**, not `Literal["w"]`, because a variable could be reassigned later, so passing it is an error. (Write `choice: Mode = "w"`, or use `Final`, next section.) A `str` coming from the user is `str`, always: the checker cannot know the text. You must **validate it** first, and then tell the checker, for example with a narrowing guard (section 18).

Inside `f` the checker **narrows** `m` with each `==` test: after `"r"` and `"w"` are excluded, only `Literal['a']` remains.

At run time `Literal` is a plain annotation, and its values can be read back, which makes a handy validator: `get_args(Literal["r", "w", "a"])` is `('r', 'w', 'a')`, so `value in get_args(Mode)` tests the text.

### 12.2 Exhaustive checks with `assert_never`

If you handle every literal value, you can ask the checker to **prove it**:

```python
from typing import Literal, assert_never

Color = Literal["red", "green", "blue"]


def hex_of(c: Color) -> str:
    if c == "red":
        return "#f00"
    elif c == "green":
        return "#0f0"
    else:
        assert_never(c)
```
```text
$ python -m mypy --strict literal_never.py
literal_never.py:12: error: Argument 1 to "assert_never" has incompatible type "Literal['blue']"; expected "Never"  [arg-type]
```

`blue` was forgotten, and the message names it. Add a fourth colour to the `Literal` months later and every function with an `assert_never` branch lights up. At run time `assert_never` raises an `AssertionError` if it is ever reached.

### Try it 12.1

Verdicts for `def paint(c: Literal["red", "blue"]) -> None`: (a) `paint("red")` (b) `paint("Red")` (c) `x = "red"; paint(x)` (d) `x: Literal["red"] = "red"; paint(x)`.

<details><summary>Answer</summary>

(a) ok. (b) error (case matters). (c) error: `x` is inferred as `str`. (d) ok: the annotation keeps the literal.

</details>

## 13. `Final` and `@final`

`Final` marks a name that must never be reassigned. `@final` marks a class that must not be subclassed, or a method that must not be overridden.

```python
from typing import Final, final

MAX: Final = 10
NAME: Final[str] = "app"
MAX = 11


@final
class Leaf:
    pass


class Sub(Leaf):
    pass
```
```text
$ python -m mypy --strict final_demo.py
final_demo.py:5: error: Cannot assign to final name "MAX"  [misc]
final_demo.py:13: error: Cannot inherit from final class "Leaf"  [misc]
```

mypy rejects each breach: reassigning a final name (or a final attribute, `self.id: Final = 1`), subclassing a `@final` class (and likewise overriding a `@final` method).

At run time **none of this is enforced**: `MAX = 11` runs without complaint. `Final` is a promise checked only by tools, so constants in Python are by *convention* (UPPER_CASE) plus `Final`. `@final` at least leaves a trace (`Leaf.__final__` is `True`). Use `Final` for module constants and configuration, and `@final` on classes you designed to be used but not extended.

### Try it 13.1

Which lines does mypy reject? `RATE: Final = 0.2`, then (a) `RATE = 0.3` (b) `total = RATE * 100` (c) `RATE += 0.1` (d) `def f(r: float = RATE): ...`

<details><summary>Answer</summary>

(a) and (c) are rejected: both assign to a final name. (b) and (d) only *read* it, which is fine.

</details>

## 14. `Callable` and function types

### 14.1 The syntax

`Callable[[ArgTypes], ReturnType]` describes "a thing you can call". Import it from `collections.abc`:

`Callable[[], int]` is a function with no arguments, and `Callable[..., X]` means "any arguments, returns `X`": an escape hatch that gives up argument checking. With the `type` statement you can name them: `type IntOp = Callable[[int, int], int]`. At run time `get_origin(Callable[[int], str])` is `collections.abc.Callable` and `get_args` gives `([int], str)`. What does the checker do with mismatches?

```python
from collections.abc import Callable


def apply(op: Callable[[int, int], int], a: int, b: int) -> int:
    return op(a, b)


def add(a: int, b: int) -> int:
    return a + b


def add3(a: int, b: int, c: int) -> int:
    return a + b + c


def concat(a: str, b: str) -> str:
    return a + b


apply(add, 1, 2)
apply(add3, 1, 2)
apply(concat, 1, 2)
apply(lambda a, b: a + b, 1, 2)
apply(max, 1, 2)
```
```text
$ python -m mypy --strict callable_check.py
callable_check.py:21: error: Argument 1 to "apply" has incompatible type "Callable[[int, int, int], int]"; expected "Callable[[int, int], int]"  [arg-type]
callable_check.py:22: error: Argument 1 to "apply" has incompatible type "Callable[[str, str], str]"; expected "Callable[[int, int], int]"  [arg-type]
```

Wrong number of parameters, or wrong parameter types, are both rejected. A `lambda` is accepted and its parameters get the types from the context. Return types are compared too.

### 14.2 Generic callables: composing functions

Type variables flow through callable types:

```python
from collections.abc import Callable


def compose[A, B, C](f: Callable[[A], B], g: Callable[[B], C]) -> Callable[[A], C]:
    def both(x: A) -> C:
        return g(f(x))

    return both


def to_str(n: int) -> str:
    return str(n)


def shout(s: str) -> str:
    return s.upper() + "!"


h = compose(to_str, shout)
reveal_type(h)
bad = compose(shout, to_str)
```
```text
$ python -m mypy --strict callable_compose.py
callable_compose.py:20: note: Revealed type is "def (int) -> str"
callable_compose.py:21: error: Cannot infer value of type parameter "B" of "compose"  [misc]
```

Read the signature as a chain: `f` goes from `A` to `B`, `g` goes from `B` to `C`, so the result goes from `A` to `C`. The shared `B` is the *link*. In `bad`, the output of `shout` is `str`, but `to_str` needs an `int`, so `B` cannot be solved. (The message is wordy: "Cannot infer value of type parameter 'B'".)

### 14.3 When `Callable` is not enough

`Callable` cannot express keyword-only arguments, argument names or defaults. For those, use a callback protocol (section 9.3). And there is one more thing it cannot do: say "the decorated function has **the same parameters as the original**". That needs `ParamSpec`.

### Try it 14.1

Write `type Predicate[T] = Callable[[T], bool]` and a function `keep[T](items: list[T], pred: Predicate[T]) -> list[T]`. Call `keep([1, 2, 3, 4], lambda n: n % 2 == 0)`.

<details><summary>Answer</summary>

```python
from collections.abc import Callable

type Predicate[T] = Callable[[T], bool]


def keep[T](items: list[T], pred: Predicate[T]) -> list[T]:
    return [x for x in items if pred(x)]


print(keep([1, 2, 3, 4], lambda n: n % 2 == 0))
```

```text
[2, 4]
```

</details>

## 15. `ParamSpec`: decorators that keep the signature

### 15.1 The problem

Here is the most common typing failure in real code. You write a decorator, and after decorating, the checker no longer knows what the function accepts:

```python
from collections.abc import Callable
from typing import Any


def bad_decorator(f: Callable[..., int]) -> Callable[..., int]:
    return f


@bad_decorator
def h(a: int) -> int:
    return a


reveal_type(h)
h("nope", 2, 3)
```
```text
$ python -m mypy --strict pp_problem.py
pp_problem.py:14: note: Revealed type is "def (*Any, **Any) -> int"
Success: no issues found in 1 source file
```

`Callable[..., int]` says "any arguments". The parameters of `h` are gone: `h("nope", 2, 3)` is accepted. We need to say: "the wrapper takes **the same parameters as the function it wraps**". That is a `ParamSpec` (parameter specification), written `**P`.

### 15.2 A typed decorator

```python
import functools
from collections.abc import Callable


def logged[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        print(f"calling {func.__name__}")
        result = func(*args, **kwargs)
        print(f"{func.__name__} returned {result!r}")
        return result

    return wrapper


@logged
def greet(name: str, excited: bool = False) -> str:
    return f"Hello {name}" + ("!" if excited else "")


print(greet("Ada", excited=True))
print(greet.__name__, greet.__wrapped__.__name__)
```
```text
$ python pp_logged.py
calling greet
greet returned 'Hello Ada!'
Hello Ada!
greet greet
```

Read `logged[**P, R]` as: "`P` is a whole parameter list and `R` is a return type". `Callable[P, R]` is any function with parameter list `P` and result `R`. The wrapper takes `*args: P.args, **kwargs: P.kwargs`, the only correct way to forward "all of `P`". The decorator returns `Callable[P, R]`: the same parameter list, the same result.

```python
import functools
from collections.abc import Callable


def logged[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        return func(*args, **kwargs)

    return wrapper


@logged
def greet(name: str, excited: bool = False) -> str:
    return f"Hello {name}" + ("!" if excited else "")


reveal_type(greet)
greet(42)
greet("a", loud=True)
x: int = greet("a")
```
```text
$ python -m mypy --strict pp_logged_check.py
pp_logged_check.py:18: note: Revealed type is "def (name: str, excited: bool =) -> str"
pp_logged_check.py:19: error: Argument 1 to "greet" has incompatible type "int"; expected "str"  [arg-type]
pp_logged_check.py:20: error: Unexpected keyword argument "loud" for "greet"  [call-arg]
pp_logged_check.py:21: error: Incompatible types in assignment (expression has type "str", variable has type "int")  [assignment]
```

The decorated `greet` keeps its names, its types and its default. All three mistakes are caught.

The older spelling declares the variables first: `P = ParamSpec("P")` and `R = TypeVar("R")`, then `def logged(func: Callable[P, R]) -> Callable[P, R]:` with the same body.

### 15.3 `Concatenate`: adding or removing a parameter

A decorator can supply an extra first argument. `Callable[Concatenate[Request, P], R]` means "a function taking a `Request` first, then everything in `P`", and the decorator returns `Callable[P, R]`: the `Request` is injected, so callers no longer pass it. (`from typing import Concatenate`.)

### 15.4 Decorators with arguments, and class-based decorators

A decorator **factory** has one more level: `def repeat[**P, R](times: int) -> Callable[[Callable[P, R]], Callable[P, R]]`. Type each level in turn, outer to inner. A **class-based** decorator can be generic too: `class CountCalls[**P, R]` with `__init__(self, func: Callable[P, R])` and `__call__(self, *args: P.args, **kwargs: P.kwargs) -> R`. Section 22 uses this shape for an event emitter.

### Try it 15.1

Write a decorator `timed` using `ParamSpec` that calls the function, measures the time with `time.perf_counter()`, and returns the function's result *unchanged*. It must keep the parameters and the return type.

<details><summary>Answer</summary>

```python
import functools
import time
from collections.abc import Callable


def timed[**P, R](func: Callable[P, R]) -> Callable[P, R]:
    @functools.wraps(func)
    def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
        start = time.perf_counter()
        try:
            return func(*args, **kwargs)
        finally:
            print(f"{func.__name__} took {time.perf_counter() - start:.6f}s")

    return wrapper


@timed
def square(n: int) -> int:
    return n * n


print(square(7))
```

The output has a machine-specific timing line (`square took 0.000001s` or similar) followed by `49`. The `try/finally` makes sure the time is printed even when `func` raises.

</details>

## 16. `@overload`

### 16.1 When the result depends on the argument

`double(2)` returns an `int`, `double("ab")` returns a `str`. With a union the link is lost:

```python
def double_union(x: int | str) -> int | str:
    return x * 2


n = double_union(2)
reveal_type(n)
n + 1
```
```text
$ python -m mypy --strict overload_union.py
overload_union.py:6: note: Revealed type is "int | str"
overload_union.py:7: error: Unsupported operand types for + ("str" and "int")  [operator]
overload_union.py:7: note: Left operand is of type "int | str"
```

The checker thinks `n` could be a `str`, and `n + 1` fails. A type variable constrained to `(int, str)` would work here, but often the cases differ more (different return types for *unrelated* inputs). `@overload` lists the allowed call shapes:

```python
from typing import overload


@overload
def double(x: int) -> int: ...
@overload
def double(x: str) -> str: ...
def double(x: int | str) -> int | str:
    return x * 2


reveal_type(double(2))
reveal_type(double("ab"))
double(2.5)
```
```text
$ python -m mypy --strict overload_basic.py
overload_basic.py:12: note: Revealed type is "int"
overload_basic.py:13: note: Revealed type is "str"
overload_basic.py:14: error: No overload variant of "double" matches argument type "float"  [call-overload]
overload_basic.py:14: note: Possible overload variants:
overload_basic.py:14: note:     def double(x: int) -> int
overload_basic.py:14: note:     def double(x: str) -> str
```

There are two parts. The `@overload` lines are **signatures only**, with `...` bodies: they are the promises the caller sees. The last definition, without `@overload`, is the **implementation**: the only code that runs, with a signature wide enough to cover all the overloads. mypy checks that the implementation can *accept* the arguments of every overload, but it cannot prove that the implementation returns the right type for each one, so make sure they agree.

At run time the overload stubs are thrown away:

At run time the overload stubs are thrown away: only the implementation remains (`double.__annotations__` is empty here), though `typing.get_overloads(double)` can list the stubs.

### 16.2 Rules and a classic pattern: `Literal` flags

- At least two overloads, and an implementation (outside stub files).
- Order matters: the checker tries the overloads **top to bottom**, so write the specific one first.
- Overloads whose parameters overlap but whose return types are incompatible are reported as unsafe.

A classic use is a function whose return type depends on a `Literal[True]` or `Literal[False]` flag (`@overload def read(path: str, binary: Literal[True]) -> bytes: ...` and so on). When the flag is a literal (`read("a", True)`), the checker picks the precise overload `-> bytes`; with a general `bool` it falls to a third overload returning `str | bytes`. A function whose return type depends on a `bool` flag is the classic use, and `open()` is declared this way.

### 16.3 Traps

- Do not use `@overload` just to avoid thinking: if the result is simply "the same type as the input", use a type variable.
- A single `@overload` is an error ("Single overload definition, multiple required"), and a later overload hidden by an earlier, broader one is also reported (`overload-cannot-match`).

### Try it 16.1

Write overloads for `first_or(items, default)`: with a `list[int]` and an `int` default it returns an `int`; with a `list[str]` and a `str` default it returns a `str`. Could a type variable do the same job?

<details><summary>Answer</summary>

```python
from typing import Any, overload


@overload
def first_or(items: list[int], default: int) -> int: ...
@overload
def first_or(items: list[str], default: str) -> str: ...
def first_or(items: list[Any], default: Any) -> Any:
    return items[0] if items else default


print(first_or([], 7), first_or(["a"], "z"))
```

```text
7 a
```

Yes, and it would be better: `def first_or[T](items: list[T], default: T) -> T` covers every type with one signature. Use overloads only when no single generic signature can express the relation.

</details>

## 17. Type narrowing

A value's declared type is often wider than what you know at one particular line. `x: int | str | None` is three things; after `if x is None: return`, it is only two. The checker follows this reasoning, and it is called **narrowing**. Without it, every union would have to be fought with casts.

```python
def show(x: int | str | list[int] | None) -> str:
    if x is None:
        reveal_type(x)
        return "none"
    reveal_type(x)
    if isinstance(x, int):
        reveal_type(x)
        return str(x + 1)
    elif isinstance(x, str):
        reveal_type(x)
        return x.upper()
    else:
        reveal_type(x)
        return str(sum(x))


def g(x: int | str, items: list[str] | None) -> None:
    x.upper()
    if not isinstance(x, str):
        reveal_type(x)
        return
    reveal_type(x)
    if items:
        reveal_type(items)
    else:
        reveal_type(items)
```
```text
$ python -m mypy --strict narrow_basic.py
narrow_basic.py:3: note: Revealed type is "None"
narrow_basic.py:5: note: Revealed type is "int | str | list[int]"
narrow_basic.py:7: note: Revealed type is "int"
narrow_basic.py:10: note: Revealed type is "str"
narrow_basic.py:13: note: Revealed type is "list[int]"
narrow_basic.py:18: error: Item "int" of "int | str" has no attribute "upper"  [union-attr]
narrow_basic.py:20: note: Revealed type is "int"
narrow_basic.py:22: note: Revealed type is "str"
narrow_basic.py:24: note: Revealed type is "list[str]"
narrow_basic.py:26: note: Revealed type is "list[str] | None"
```

Walk through it. Each test splits the type in two: the "yes" branch and the "no" branch. Excluded types disappear from the *rest* of the function (the `else` of the `isinstance` chain is `list[int]`). `x.upper()` at the top is rejected, because it is not true for every member of the union. After `if not isinstance(x, str): return`, the code below sees `str`: an **early return narrows what follows**. And a truthiness test is not as strong as you might hope: in the `else` branch, `items` is still `list[str] | None`, because an empty list is also false.

### 17.1 What narrows

| Test | Effect |
| --- | --- |
| `x is None`, `x is not None` | removes or keeps `None` |
| `isinstance(x, C)` or `isinstance(x, (A, B))` | keeps only subtypes of `C` (or `A`/`B`) in the "yes" branch |
| `x == literal` for `Literal` types | picks the literal |
| `if x:` / `if not x:` | removes `None`; may keep empty containers |
| `callable(x)` | keeps callable members |
| `assert x is not None`, `assert isinstance(x, C)` | narrows for the rest of the function |
| a `TypeGuard` / `TypeIs` function (section 18) | whatever the function declares |

What does **not** narrow: `x.__class__ == C`, `hasattr` tricks in older checkers, a test stored in a variable (`ok = x is not None; if ok:` does not narrow `x`), and anything the checker cannot see through, such as `len(x) > 0` (it does not narrow a `list | None` to `list`).

### 17.2 The most common use: `None`

```python
def lookup(d: dict[str, int], key: str) -> int:
    v = d.get(key)
    reveal_type(v)
    return v + 1


def lookup_ok(d: dict[str, int], key: str) -> int:
    v = d.get(key)
    if v is None:
        raise KeyError(key)
    return v + 1
```
```text
$ python -m mypy --strict narrow_none.py
narrow_none.py:3: note: Revealed type is "int | None"
narrow_none.py:4: error: Unsupported operand types for + ("None" and "int")  [operator]
narrow_none.py:4: note: Left operand is of type "int | None"
```

`dict.get` may return `None`, so the checker will not let you add `1` until you have dealt with it. In `lookup_ok` the `raise` leaves only `int` for the last line. Use `assert v is not None` when `None` is a bug that "cannot happen" and you want to say so: it crashes loudly if the claim is false. Do not use it for data from outside; use a real `if` with an error.

Narrowing works on **names and simple attributes**. If a method call or a nested function may change the value, the checker forgets what it learned; copy the value into a local variable first (`value = self.cache`), then test and use `value`.

### Try it 17.1

A trace exercise. What does `reveal_type(x)` show on each marked line?

```python
def f(x: int | str | None) -> None:
    if x is None or isinstance(x, int):
        reveal_type(x)       # (a)
    else:
        reveal_type(x)       # (b)
    if isinstance(x, str) and x:
        reveal_type(x)       # (c)
```

<details><summary>Answer</summary>

(a) `int | None` (the "yes" branch of `A or B` can be either test). (b) `str`: it is neither `None` nor `int`. (c) `str`: `isinstance(x, str)` is true, and the extra `and x` test does not change the type.

</details>

## 18. `TypeGuard` and `TypeIs`

### 18.1 When the checker does not know your test

You often hide a check in a helper function. A helper that returns a plain `bool` tells the checker nothing about its argument. Two annotations let a function **announce what its `True` result means**.

```python
from typing import TypeGuard, TypeIs


def is_str_list(val: list[object]) -> TypeGuard[list[str]]:
    return all(isinstance(x, str) for x in val)


def is_int(val: int | str) -> TypeIs[int]:
    return isinstance(val, int)


def is_str_plain(val: int | str) -> bool:
    return isinstance(val, str)


def process(items: list[object], v: int | str) -> None:
    if is_str_list(items):
        reveal_type(items)
        print(", ".join(items))
    else:
        reveal_type(items)
    if is_int(v):
        reveal_type(v)
    else:
        reveal_type(v)
    if is_str_plain(v):
        v.upper()
```
```text
$ python -m mypy --strict guards.py
guards.py:18: note: Revealed type is "list[str]"
guards.py:21: note: Revealed type is "list[object]"
guards.py:23: note: Revealed type is "int"
guards.py:25: note: Revealed type is "str"
guards.py:27: error: Item "int" of "int | str" has no attribute "upper"  [union-attr]
```

- `TypeGuard[list[str]]` says: "when I return `True`, the argument is a `list[str]`". The `else` branch learns **nothing**.
- `TypeIs[int]` says: "when I return `True`, the argument is an `int`; when I return `False`, it is **not** an `int`". The `else` branch is narrowed too.
- A plain `bool` function narrows nothing, and `v.upper()` fails.

(Python 3.13 added `TypeIs`; on 3.12 and older import it from the `typing_extensions` package. `TypeGuard` exists since 3.10.)

### 18.2 `TypeGuard` versus `TypeIs`

| | `TypeGuard[X]` | `TypeIs[X]` |
| --- | --- | --- |
| "yes" branch | `X` | `X` (intersected with the input type) |
| "no" branch | unchanged | the input type **minus** `X` |
| `X` must be a subtype of the input type | no | **yes** |
| Needed when | narrowing to a type that is not a subtype, e.g. `list[object]` to `list[str]` | the check is an exact `isinstance`-style test |

**Prefer `TypeIs`** when it fits: it behaves just like a built-in `isinstance` and gives you the "no" branch for free. Use `TypeGuard` when the narrowed type is *not* a subtype of the parameter (`list[object]` is not a supertype of `list[str]` in the checker's eyes, because lists are invariant), or when the "no" answer would not mean "not X".

### 18.3 You can lie

The checker believes the annotation. It does not check the function body:

```python
from typing import TypeIs


def is_positive_int(v: object) -> TypeIs[int]:
    return isinstance(v, int) and v > 0


def f(v: int | str) -> None:
    if is_positive_int(v):
        pass
    else:
        reveal_type(v)
```
```text
$ python -m mypy --strict guard_lie.py
guard_lie.py:12: note: Revealed type is "str"
Success: no issues found in 1 source file
```

This function returns `False` for `0` and `-5`, which *are* ints. But `TypeIs[int]` promised that `False` means "not an int", so in the `else` branch mypy says `v` is a `str`. A call `f(-5)` would then break code that trusts that. **A guard must answer exactly the question its annotation asks.** For "positive int", return a plain `bool`, or use `TypeGuard[int]`, where the `False` branch learns nothing.

### Try it 18.1

Write `is_str_list(val: list[object]) -> TypeGuard[list[str]]`, and a function `join(val: list[object]) -> str` that uses it.

<details><summary>Answer</summary>

```python
from typing import TypeGuard


def is_str_list(val: list[object]) -> TypeGuard[list[str]]:
    return all(isinstance(x, str) for x in val)


def join(val: list[object]) -> str:
    if is_str_list(val):
        return ", ".join(val)
    return "not all strings"


print(join(["a", "b"]), join(["a", 1]))
```

```text
a, b not all strings
```

</details>

### Try it 18.2

Choose `TypeGuard` or `TypeIs`. (a) `def is_cat(p: Cat | Dog) -> ...: return isinstance(p, Cat)` (b) `def all_ints(xs: list[object]) -> ...` narrowing to `list[int]` (c) `def is_nonempty(xs: list[int] | None) -> ...` narrowing to `list[int]`, returning true for any non-empty list.

<details><summary>Answer</summary>

(a) `TypeIs[Cat]`: an exact test, and "False" means it is a `Dog`. (b) `TypeGuard[list[int]]`: `list[int]` is not a subtype of `list[object]`. (c) `TypeGuard[list[int]]`. `TypeIs` would be a lie: an *empty* list returns `False` yet is still a `list[int]`.

</details>

## 19. `Any` versus `object`

Both accept every value. The difference is what the checker lets you **do** with it afterwards.

```python
from typing import Any


def use_any(x: Any) -> None:
    x.whatever
    x + 1
    y: int = x
    reveal_type(x.upper())


def use_object(x: object) -> None:
    x.whatever
    x + 1
    y: int = x
    if isinstance(x, str):
        reveal_type(x)
        x.upper()
```
```text
$ python -m mypy --strict any_object.py
any_object.py:8: note: Revealed type is "Any"
any_object.py:12: error: "object" has no attribute "whatever"  [attr-defined]
any_object.py:13: error: Unsupported operand types for + ("object" and "int")  [operator]
any_object.py:14: error: Incompatible types in assignment (expression has type "object", variable has type "int")  [assignment]
any_object.py:16: note: Revealed type is "str"
```

- **`Any` is "do not check me"**. Any attribute, any operation, any assignment is accepted, and the result is `Any` again, so the silence spreads. It switches the checker **off** for that value.
- **`object` is "I know nothing"**. You may only do what every object can do (`print`, `str`, `==`, `hash`). To do more you must *narrow* it with `isinstance`. It keeps the checker **on**.

A short way to remember: `Any` opts **out** of the type system, `object` is the safest type **in** it. Use `object` for "I accept anything and will not look inside" (a logger, `print`-like functions), and narrow when you need more.

### 19.1 `Any` is contagious, and it hides at the edges

```python
import json
from typing import cast

data = json.loads("[1, 2]")
reveal_type(data)
total: int = data
names: list[str] = data
nums = cast(list[int], data)
reveal_type(nums)


def takes_object_list(xs: list[object]) -> None: ...


ints: list[int] = [1]
takes_object_list(ints)
```
```text
$ python -m mypy --strict any_edges.py
any_edges.py:5: note: Revealed type is "Any"
any_edges.py:9: note: Revealed type is "list[int]"
any_edges.py:16: error: Argument 1 to "takes_object_list" has incompatible type "list[int]"; expected "list[object]"  [arg-type]
any_edges.py:16: note: "list" is invariant -- see https://mypy.readthedocs.io/en/stable/common_issues.html#variance
any_edges.py:16: note: Consider using "Sequence" instead, which is covariant
```

`json.loads` returns `Any`, so `data` can be assigned to a variable of any type and the checker says nothing: the first two assignments are both wrong (the data is a list) and both accepted. This is how `Any` gets in: JSON, untyped libraries, `**kwargs` with no hint, and functions without annotations.

`cast(list[int], data)` tells the checker "trust me" and does **nothing at run time**: `cast("int", "not an int")` simply returns the string.

The last mypy error above shows another difference: `list[int]` is not a `list[object]` (invariance, section 4.5), so `object` does not stretch over *containers* of everything. For parameters that only read, use `Sequence[object]` or `Iterable[object]`.

### 19.2 Rules of thumb

1. **Validate at the boundary, then use real types.** `json.loads` returns `Any`: check the data (section 11.3), then pass a `TypedDict` or dataclass inward. `Any` should live at the edge, not in the middle.
2. Prefer `object` over `Any` when you mean "anything".
3. Prefer a `TypeVar` over `Any` when output depends on input (section 3).
4. Use `Any` when you truly must, for example a decorator that cannot be typed yet, and leave a comment saying why.
5. `mypy --strict` warns when an `Any` leaks out (`warn-return-any`) and when a generic is left bare (`disallow-any-generics`), so strict mode is the tool that keeps `Any` honest.

### Try it 19.1

Verdicts for the three lines after `def f(a: Any, o: object) -> None:`: (a) `a.foo()` (b) `o.foo()` (c) `n: int = o`.

<details><summary>Answer</summary>

(a) ok: `Any` allows everything. (b) error: `object` has no attribute `foo`. (c) error: an `object` is not known to be an `int`. With `a` instead of `o`, line (c) would be accepted.

</details>

## 20. Typing code you do not own: stubs and `py.typed`

### 20.1 What mypy does when it imports something

When your code does `import something`, mypy looks for *type information* for that module. There are four outcomes:

```python
import fancylib
import yaml
```
```text
$ python -m mypy imports_missing.py
imports_missing.py:1: error: Cannot find implementation or library stub for module named "fancylib"  [import-not-found]
imports_missing.py:1: note: See https://mypy.readthedocs.io/en/stable/running_mypy.html#missing-imports
imports_missing.py:2: error: Library stubs not installed for "yaml"  [import-untyped]
imports_missing.py:2: note: Hint: "python3 -m pip install types-PyYAML"
imports_missing.py:2: note: (or run "mypy --install-types" to install all missing stub packages)
```

1. **The module ships its own types.** A package with a file named `py.typed` in it tells tools "my inline hints are real, use them".
2. **Types come from a separate stub package** (`types-PyYAML`, installed with pip), as in the `yaml` message above. These are made from the **typeshed** project.
3. **No types anywhere**: mypy skips the package and the import is `Any` (the `fancylib` message says it could not find the module at all).
4. **You write the types yourself**: a stub file.

The difference between 1 and 3 is exactly one marker file. To show it, I made three small fake libraries and put them on the path: one with no types, one with hints and `py.typed`, and one with an extra stub package.

```text
site/untypedlib/__init__.py       def parse(text, sep=","):   (no hints, no py.typed)
site/typedlib/__init__.py         def parse(text: str, sep: str = ",") -> list[str]:
site/typedlib/py.typed            (an empty file)
site/stubbed/__init__.py          def parse(text, sep=","):   (no hints)
site/stubbed-stubs/__init__.pyi   def parse(text: str, sep: str = ...) -> list[str]: ...
```

```python
import untypedlib
import typedlib
import stubbed

reveal_type(untypedlib.parse("a,b"))
reveal_type(typedlib.parse("a,b"))
reveal_type(stubbed.parse("a,b"))
typedlib.parse(5)
```
```text
$ python -m mypy --strict imports_site.py
imports_site.py:1: error: Skipping analyzing "untypedlib": module is installed, but missing library stubs or py.typed marker  [import-untyped]
imports_site.py:1: note: See https://mypy.readthedocs.io/en/stable/running_mypy.html#missing-imports
imports_site.py:5: note: Revealed type is "Any"
imports_site.py:6: note: Revealed type is "list[str]"
imports_site.py:7: note: Revealed type is "list[str]"
imports_site.py:8: error: Argument 1 to "parse" has incompatible type "int"; expected "str"  [arg-type]
```

`untypedlib` is "installed, but missing library stubs or `py.typed`", so it is `Any`. `typedlib` works because of `py.typed`. `stubbed` works through its `-stubs` package, which mypy finds by the naming rule `<name>-stubs`.

### 20.2 Stub files (`.pyi`)

A **stub** is a file with only signatures, no code, next to or in place of a module: `parse.pyi` describes `parse.py`. The syntax is ordinary Python with `...` for bodies:

```text
# stubs/untypedlib.pyi
def parse(text: str, sep: str = ...) -> list[str]: ...
```

Defaults are written `...` (their value is irrelevant to types). To make mypy find a stub of your own, put the folder on its path, with `mypy_path = stubs` in the config or `MYPYPATH=stubs` on the command line:

```python
import untypedlib

reveal_type(untypedlib.parse("a,b"))
untypedlib.parse(5)
```
```text
$ python -m mypy --strict imports_stub.py
imports_stub.py:3: note: Revealed type is "list[str]"
imports_stub.py:4: error: Argument 1 to "parse" has incompatible type "int"; expected "str"  [arg-type]
```

You do not have to write a stub from zero. `stubgen` (it comes with mypy) generates a first version. For a small untyped module, `stubgen oldmod.py -o out` produced lines such as `def __init__(self, path, sep=...) -> None: ...` and `path: Incomplete`. `Incomplete` is a special `Any` that means "stubgen did not know: fill me in". Replace each one with a real type by reading the code or the docs. A stub only needs to cover the part of a library you use.

Because a stub is valid Python syntax, your own tools can read it with the `ast` module, without importing anything:

```python
import ast

stub = """
VERSION: str
def count(path: str, limit: int = ...) -> int: ...
"""
for node in ast.parse(stub).body:
    if isinstance(node, ast.FunctionDef):
        params = [f"{a.arg}: {ast.unparse(a.annotation)}" for a in node.args.args]
        print(f"function {node.name}({', '.join(params)}) -> {ast.unparse(node.returns)}")
```
```text
$ python stub_ast.py
function count(path: str, limit: int) -> int
```

### 20.3 Making your own package typed

If you publish a library (even only for your own other projects), you decide how it is typed:

1. Annotate the code, and check it with `mypy --strict`.
2. Add an **empty file `py.typed`** inside the package folder, and make sure it is included when you build the package (a `package-data` entry in `pyproject.toml`).
3. Without `py.typed`, users get `Any`, no matter how good your hints are.

Add `py.typed` only when the package is annotated for real and *kept* so. The marker is a promise that the hints are correct. If the hints are patchy, ship a separate stub package or none.

### 20.4 When a library has no types and no stubs

In order of preference: install the `types-*` package; write a minimal stub for the part you use; and as a last resort set `ignore_missing_imports = true` in a `[[tool.mypy.overrides]]` section with `module = ["fancylib.*"]`, **for that one module**. Never set it globally: then a *typo* in an import also becomes `Any`, and mypy says nothing.

### Try it 20.1

An untyped helper has `def clamp(x, low=0, high=100): return max(low, min(x, high))`. Write the stub line, assuming integers.

<details><summary>Answer</summary>

```text
def clamp(x: int, low: int = ..., high: int = ...) -> int: ...
```

Defaults become `...`: only the fact that a default exists matters in a stub.

</details>

### Try it 20.2

Choose the right action. (a) `import requests` gives "Library stubs not installed" (b) your teammate's internal package `corp_utils` is untyped and you only call two functions of it (c) your own package is well annotated and clean under `--strict`, and other projects import it.

<details><summary>Answer</summary>

(a) Install `types-requests` (the hint in the mypy message names the package). (b) Write a small stub with those two functions, or add a `[[tool.mypy.overrides]]` for `corp_utils` if you accept `Any`. (c) Add `py.typed` to the package and include it in the build.

</details>

## 21. Gradual typing strategy

### 21.1 Why you must not "type everything at once"

A real codebase has hundreds of functions written without hints. Running `mypy --strict` on it on day one gives hundreds of errors, nobody fixes them, and the effort is abandoned. **Gradual typing** is the opposite approach: types are added in small steps, and each step leaves the project clean.

It works because mypy treats every function **without annotations as untyped**: it does not check the body, and all its parameters are `Any`. That is also its danger. Here is a small untyped module with two real bugs:

```python
def total_value(items):
    total = 0
    for it in items:
        total += it["price"] * it["qty"]
    return total


def find(items, name):
    for it in items:
        if it["name"] == name:
            return it


def report(items):
    first = find(items, "bolt")
    print("Bolt qty:", first["qty"])
    print("Total:", total_value(items) + " EUR")


report([{"name": "nut", "price": 0.2, "qty": 40}])
```
```text
$ python inventory.py
Traceback (most recent call last):
  File "/home/you/project/inventory.py", line 20, in <module>
    report([{"name": "nut", "price": 0.2, "qty": 40}])
    ~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/you/project/inventory.py", line 16, in report
    print("Bolt qty:", first["qty"])
                       ~~~~~^^^^^^^
TypeError: 'NoneType' object is not subscriptable
```
```text
$ python -m mypy inventory.py
Success: no issues found in 1 source file
```

mypy is happy and the program crashes. `find` returns `None` when nothing matches, and `report` forgets to handle it. The second bug (adding a number to a string) sits just behind the first. mypy saw neither, because nothing was annotated.

### 21.2 The ratchet: stricter, one step at a time

mypy has a switch for each kind of strictness. A "ratchet" turns them on one by one, and never turns one off again:

| Step | Setting | What it adds |
| --- | --- | --- |
| 0 | defaults | checks only annotated functions |
| 1 | `check_untyped_defs = true` | checks the *bodies* of unannotated functions too (parameters still `Any`) |
| 2 | `disallow_untyped_defs = true` (per module) | every function in that module needs annotations |
| 3 | `disallow_any_generics`, `warn_return_any`, `warn_unused_ignores`, `no_implicit_optional` | no bare `list`, no leaking `Any`, no stale ignores |
| 4 | `strict = true` | all of the above plus `disallow_untyped_calls`, `disallow_untyped_decorators`, `strict_equality`, `warn_redundant_casts`, and more |

Step 1 is the cheapest and finds real bugs, but in our example it still would not: the parameter `items` is `Any`, so `first["qty"]` is fine. Only real annotations create the information the checker needs, so step 2 is where the benefit starts.

### 21.3 Where to start

1. **Leaves first.** Annotate functions that call nothing of yours (helpers, parsers, formatters), then the functions that call them, and so on upward. Each annotated function gives its callers real types.
2. **Data shapes early.** The dicts and tuples that flow everywhere are the best first investment: a `TypedDict`, a dataclass or a `Protocol` turns hundreds of `Any` into one definition.
3. **Boundaries last.** Files, JSON, user input and network are where `Any` comes from; add validation there (section 11.3).
4. **Do not change behaviour while adding types.** If an annotation reveals a bug, fix it in a separate step with a test. Types and logic in one commit make failures hard to explain.
5. **Keep tests green at every step**, and run `mypy` in the same command as `pytest`.

### 21.4 Step 2 in action

Now annotate. A first attempt uses `list[dict[str, Any]]` for the items, since that is what the code says:

```python
from typing import Any


def total_value(items: list[dict[str, Any]]) -> float:
    total = 0.0
    for it in items:
        total += it["price"] * it["qty"]
    return total


def find(items: list[dict[str, Any]], name: str) -> dict[str, Any] | None:
    for it in items:
        if it["name"] == name:
            return it
    return None


def report(items: list[dict[str, Any]]) -> None:
    first = find(items, "bolt")
    print("Bolt qty:", first["qty"])
    print("Total:", total_value(items) + " EUR")
```
```text
$ python -m mypy --strict inventory.py
inventory.py:20: error: Value of type "dict[str, Any] | None" is not indexable  [index]
inventory.py:21: error: Unsupported operand types for + ("float" and "str")  [operator]
```

Both bugs are found, and what found them was the return type `dict[str, Any] | None`. The shape of the data is still vague (`Any` for each value). Step 3 replaces it with a `TypedDict` and fixes the bugs:

```python
from typing import TypedDict


class Item(TypedDict):
    name: str
    price: float
    qty: int


def total_value(items: list[Item]) -> float:
    total = 0.0
    for it in items:
        total += it["price"] * it["qty"]
    return total


def find(items: list[Item], name: str) -> Item | None:
    for it in items:
        if it["name"] == name:
            return it
    return None


def report(items: list[Item]) -> None:
    first = find(items, "bolt")
    if first is None:
        print("Bolt: not in stock")
    else:
        print("Bolt qty:", first["qty"])
    print("Total:", f"{total_value(items):.2f} EUR")


report([{"name": "nut", "price": 0.2, "qty": 40}])
```
```text
$ python inventory.py
Bolt: not in stock
Total: 8.00 EUR
```
```text
$ python -m mypy --strict inventory.py
Success: no issues found in 1 source file
```

Clean under `--strict`, and the program works. Note what changed: *two lines of behaviour* (the missing `None` case and the string concatenation), because the checker proved them wrong. Everything else is annotation.

### 21.5 Two escape hatches, used carefully

- `# type: ignore[code]`: silence **one** error on **one** line. Always give the error code in brackets, and turn on `warn_unused_ignores` so a stale ignore is reported once the problem is fixed. A bare `# type: ignore` hides *any* future error on that line.
- `cast(T, value)`: tell the checker a type it cannot work out. A wrong cast is a lie that spreads, so put it in **one** well-named function at a boundary and add a comment.

### Try it 21.1

Put these in a sensible order for converting a project: (a) turn on `strict = true` globally, (b) annotate leaf helper functions, (c) add `check_untyped_defs`, (d) add a `types-*` stub package for a library, (e) mark finished modules with `disallow_untyped_defs`.

<details><summary>Answer</summary>

(c), (d), (b), (e), (a). Cheap global checks first (c); remove noise from missing library types (d); annotate bottom-up (b); lock in each finished module so it cannot regress (e); flip the global switch only when no module needs an exception (a).

</details>

## 22. Two worked designs: an event emitter and an LRU cache

Both are small, fully typed, and each is the kind of container class the problems of this module ask for.

### 22.1 A typed event emitter

An emitter keeps handlers and calls all of them with the same arguments. Which arguments? That depends on the event, so the **argument list itself** is a type parameter: a `ParamSpec` on a class.

```python
from collections.abc import Callable


class Emitter[**P]:
    def __init__(self) -> None:
        self._handlers: list[Callable[P, None]] = []

    def subscribe(self, handler: Callable[P, None]) -> None:
        self._handlers.append(handler)

    def emit(self, *args: P.args, **kwargs: P.kwargs) -> int:
        for h in self._handlers:
            h(*args, **kwargs)
        return len(self._handlers)


def on_click(x: int, y: int) -> None:
    print(f"click at {x},{y}")


def on_key(key: str) -> None:
    print("key", key)


clicks = Emitter[[int, int]]()
clicks.subscribe(on_click)
print(clicks.emit(3, 4))


def broken() -> None:
    clicks.subscribe(on_key)
    clicks.emit("a")
```
```text
$ python emitter.py
click at 3,4
1
```
```text
$ python -m mypy --strict emitter.py
emitter.py:31: error: Argument 1 to "subscribe" of "Emitter" has incompatible type "Callable[[str], None]"; expected "Callable[[int, int], None]"  [arg-type]
emitter.py:32: error: Too few arguments for "emit" of "Emitter"  [call-arg]
emitter.py:32: error: Argument 1 to "emit" of "Emitter" has incompatible type "str"; expected "int"  [arg-type]
```

At run time everything works (the two bad lines sit in a function that is never called). The checker rejects the handler with the wrong parameters and the call with the wrong arguments: the shape of one event is written once, in `Emitter[[int, int]]`, and enforced on both sides. The bracket syntax `Emitter[[int, int]]` with a list inside is how you spell a concrete parameter list.

### 22.2 A typed LRU cache

A **least recently used** cache keeps at most `capacity` entries and, when full, drops the one that was used longest ago. Design decisions: two type parameters (key and value), the key must be hashable, `get` may find nothing, and the cache has a `len`.

```python
from collections import OrderedDict
from collections.abc import Hashable


class LRUCache[K: Hashable, V]:
    def __init__(self, capacity: int) -> None:
        if capacity < 1:
            raise ValueError("capacity must be at least 1")
        self._capacity = capacity
        self._data: OrderedDict[K, V] = OrderedDict()

    def get(self, key: K) -> V | None:
        if key not in self._data:
            return None
        self._data.move_to_end(key)
        return self._data[key]

    def put(self, key: K, value: V) -> None:
        self._data[key] = value
        self._data.move_to_end(key)
        if len(self._data) > self._capacity:
            self._data.popitem(last=False)

    def __len__(self) -> int:
        return len(self._data)



cache = LRUCache[str, int](2)
cache.put("a", 1)
cache.put("b", 2)
cache.get("a")
cache.put("c", 3)
print(len(cache), cache.get("b"), cache.get("a"))


def misuse() -> None:
    cache.put(1, 2)
    bad = LRUCache[list[int], int](2)
```
```text
$ python lru.py
2 None 1
```
```text
$ python -m mypy --strict lru.py
lru.py:38: error: Argument 1 to "put" of "LRUCache" has incompatible type "int"; expected "str"  [arg-type]
lru.py:39: error: Value of type variable "K" of "LRUCache" cannot be "list[int]"  [type-var]
```

`get("b")` is `None` because `"b"` was evicted: after `get("a")`, `"a"` was the most recent, so `put("c")` dropped `"b"`. The bound `K: Hashable` rejects a `list` as the key. Strict mode forces a full signature on every method, including `__len__`.

## 23. Project: a fully typed refactor, mypy strict clean

**Task.** Take one of your earlier projects (any module project from chapters 10 to 15 will do; one with several functions, a `dict` or two and a file or JSON boundary is best) and convert it, step by step, until `python -m mypy --strict .` reports no errors. Behaviour must not change: the tests that passed before must still pass.

### 23.1 The path

1. **Baseline.** Run the tests and `python -m mypy .`. Write down both results. Commit or copy the project first (never convert your only copy).
2. **Configure.** Create `pyproject.toml` with a `[tool.mypy]` section: `python_version`, `check_untyped_defs = true`, `warn_unused_ignores = true`. Fix the new errors. Many are real bugs.
3. **Stubs.** For each "Library stubs not installed" message, install the `types-*` package. For libraries with none, add an override with `ignore_missing_imports = true` for that module only (section 20).
4. **Model the data.** Find the dicts that always have the same keys and make them `TypedDict`s (or dataclasses, chapter 15). Find the "anything with a `.read()`" parameters and write a `Protocol`.
5. **Annotate bottom-up.** Leaf functions first. After each function or small group, run `mypy` and the tests. Prefer `Iterable`/`Sequence`/`Mapping` for parameters and concrete types for results.
6. **Lock modules as you finish them** with a per-module override.
7. **Boundaries.** Where `json.load` or `input()` produces `Any`, add a validator that returns a typed value (section 11.3), and narrow instead of casting.
8. **Flip to `strict = true`**, delete the per-module overrides, and fix what remains.
9. **Hold the line.** Keep `mypy --strict` in your routine (a script, a pre-commit hook, or the CI). If the project is a package, add `py.typed`.

The per-module override from step 6, as a configuration file:

```toml
[tool.mypy]
python_version = "3.12"
strict = true

[[tool.mypy.overrides]]
module = ["legacy"]            # not converted yet
disallow_untyped_defs = false
disallow_untyped_calls = false
check_untyped_defs = true

[[tool.mypy.overrides]]
module = ["yaml"]              # no stubs installed
ignore_missing_imports = true
```

An important detail about it: the exception for `legacy` is only for code **inside** `legacy`. When a typed module *calls* an untyped one, strict mode complains in the **caller**. With a tiny `app.py` that calls `legacy.report(items)` I got:

```text
$ python -m mypy .
app.py:7: error: Call to untyped function "report" in typed context  [no-untyped-call]
Found 1 error in 1 file (checked 3 source files)
```

The error is in `app.py`, but the cure is in `legacy.py`: annotate `report`. That is the ratchet working as intended: untyped code is pushed toward the edge, and every typed module is protected from it.

### 23.2 Errors you will see in strict mode, and what they mean

| Message (code) | Usual cause | Fix |
| --- | --- | --- |
| `Function is missing a type annotation` (`no-untyped-def`) | a function without hints | annotate; use `-> None` for procedures |
| `Missing type arguments for generic type "list"` (`type-arg`) | bare `list` or `dict` | `list[int]`, `dict[str, float]` |
| `Returning Any from function declared to return "int"` (`no-any-return`) | returning something from `json.loads` or an untyped call | validate, or `cast` once at the boundary |
| `Call to untyped function ... in typed context` (`no-untyped-call`) | calling code that is not annotated yet | annotate the callee |
| `Unused "type: ignore" comment` (`unused-ignore`), `Redundant cast` (`redundant-cast`) | the problem was fixed, or the checker already knew | delete the comment or cast |
| `Item "None" of "X \| None" has no attribute ...` (`union-attr`) | you forgot the `None` case | narrow (section 17) |
| `Missing return statement` (`return`) | a code path ends without `return` | add `return None` or raise |

### 23.3 Checklist before you call it done

- `python -m mypy --strict .` prints "Success".
- Tests pass, same count as the baseline.
- No bare `# type: ignore`; every remaining ignore has a code and a reason in a comment.
- No `Any` in a function *signature* unless a comment explains why.
- You can name, for each `Protocol`, `TypedDict` and `Generic` class you added, what it **replaced**.

### Try it 23.1

mypy strict reports `Missing return statement` for `def sign(n: int) -> int:` containing `if n > 0: return 1` then `elif n < 0: return -1`. What is the fix, and what bug did the checker find?

<details><summary>Answer</summary>

When `n == 0` neither branch returns, so the function returns `None`, which contradicts `-> int`. Add `return 0` at the end (or turn the `elif` into an `else`, depending on what zero should mean). The checker found a path that really exists.

</details>

## 24. Common traps

1. **Believing a hint is a check.** `Stack[int]` does not stop a `str` at run time, and `TypedDict` does not validate JSON. Validate at the boundary.
2. **Unconstrained `T` hides mistakes.** `same(1, "a")` quietly becomes `object`. Add a bound or constraints when "same type" matters.
3. **A `T` that appears once.** If the type variable is in only one place, it does nothing (and in a return type alone, it is an error).
4. **Bound versus constraints versus union.** Bound keeps the subclass; constraints check the body once per type; a union forgets the link between input and output.
5. **`list[Sub]` is not `list[Base]`.** Invariance. Use `Sequence[Base]` for read-only parameters.
6. **`@runtime_checkable` checks names only.** A class with a `close` of the wrong signature still passes `isinstance`.
7. **Mutable protocol attributes.** `name: str` in a protocol rejects frozen dataclasses and properties; use a read-only `@property` when you only read.
8. **`TypeIs` lies.** A guard that returns `False` for a value that *is* the type breaks the checker's "else" branch. For anything but an exact test, use `TypeGuard` or `bool`.
9. **`Any` spreads.** One `Any` from `json.loads` can silence checking for a whole call tree. Narrow it at the edge. Prefer `object` for "anything".
10. **Decorators that return `Callable[..., X]`.** The parameters disappear. Use `ParamSpec`.
11. **Bare `# type: ignore`.** Always write the code (`# type: ignore[arg-type]`) and enable `warn_unused_ignores`.
12. **`ignore_missing_imports` globally.** It also hides import typos. Scope it to one module.
13. **Annotating everything at once.** Use the ratchet (section 21): one step, tests green, next step.

## 25. Summary

- A **type variable** links types across a signature: `def first[T](xs: list[T]) -> T`. Use `class Box[T]` for generic classes (3.12+), or `TypeVar` and `Generic[T]` in older code. At run time the type argument is not kept and not enforced.
- **Bounds** (`T: Base`) keep the precise subtype; **constraints** (`T: (int, str)`) check the body once for each type; a **union** forgets the link.
- The `type` statement names (and can recurse) a type: `type Json = ...`. An alias is a name, not a new type.
- A **`Protocol`** describes a shape: whoever has the methods fits, with no inheritance. It is for consumers; use a base class or ABC for families that share code or need an exact `isinstance`. `@runtime_checkable` only tests that names exist.
- **`TypedDict`** types dict-shaped data (`total=False`, `NotRequired`); it is a plain `dict` at run time, so validate external data. **`Literal`** limits a value to listed constants and enables exhaustive checks with `assert_never`. **`Final`** and `@final` forbid reassigning and subclassing.
- **`Callable[[A], B]`** types functions; **`ParamSpec`** (`**P`, `P.args`, `P.kwargs`) lets a decorator keep the original signature; **`@overload`** lists call shapes whose result depends on the arguments.
- The checker **narrows** unions through `is None`, `isinstance`, early returns and `TypeGuard`/`TypeIs`. Prefer `TypeIs` for exact tests; never let a guard lie.
- **`Any` switches checking off; `object` keeps it on.** Keep `Any` at the edges and validate there.
- **Third-party code:** `py.typed` marks a package as typed, `types-*` packages and `.pyi` stubs supply types for others, and `ignore_missing_imports` belongs to one module only.
- **Gradual typing** is a ratchet: `check_untyped_defs`, then `disallow_untyped_defs` per module, then `strict`; annotate bottom-up, model data early, keep tests green, and never change behaviour and types in the same step.
- Runtime tools for hints: `get_type_hints`, `get_origin`, `get_args`, `inspect.signature`, `__required_keys__`, `__orig_bases__`, `__type_params__`.

You can now write a generic, fully typed container, choose between a protocol and a base class, and take a real project to a clean `mypy --strict`. The next chapters build on the same discipline: when you write the tests for them, write the hints first.
