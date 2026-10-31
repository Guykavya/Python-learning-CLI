# Chapter 11: Decorators and functional tools

Imagine you have written twenty functions for a small shop program: `add_item`, `remove_item`, `total_price`, `apply_discount`, and so on. Your teacher (or your team lead) now asks for three things:

1. "Print how long each function takes, so we can find the slow one."
2. "Log every call with its arguments, so we can debug customer complaints."
3. "If the payment server fails, try again two more times before giving up."

The simple way is to open all twenty functions and paste the same timing code, the same logging code and the same retry loop into each one. That is sixty copies of almost the same lines. When you later want to change the log format, you must change twenty places, and you will forget one. Worse, the real work of each function is now hidden under lines that have nothing to do with it.

Python has a clean answer: the **decorator**. A decorator is a function that takes your function and gives back an **improved version** of it: the same work, plus some extra behaviour around it (timing, logging, retrying, checking arguments, caching results). You write the extra behaviour **once**, and you add it to any function with one line:

```text
@timer
def total_price(cart):
    ...
```

Decorators are everywhere in real Python. Web frameworks use `@app.route("/home")` to connect a URL to a function. Test tools use `@pytest.mark.parametrize(...)`. The standard library has `@functools.lru_cache`, `@functools.wraps`, `@functools.singledispatch`, and (for classes, later) `@property` and `@staticmethod`. After this chapter, none of these will look like magic to you. You will know exactly what the `@` line does, and you will be able to write your own.

There is no new Python machinery here. Decorators are built **only** from things you already know: functions are values, functions can be passed in and returned, closures remember variables, and `*args, **kwargs` can pass along any arguments. This chapter puts those pieces together.

The second half of the chapter is about the **functional tools** in the standard library: the `functools` module (`lru_cache`, `cache`, `partial`, `reduce`, `singledispatch`) and the `operator` module (`itemgetter`, `methodcaller`, `add`, `mul`, ...). These are ready-made higher-order functions: tools that take or return functions. We finish with **functional style** in Python: what a pure function is, when `map`/`filter`/`reduce` are good, and when a plain comprehension or loop is clearer.

Along the way you will answer these questions:

- What exactly does the `@decorator` line do, and **when** does it run?
- Why does a wrapper need `*args, **kwargs`, and why does it need `return`?
- After decorating, why does `my_function.__name__` suddenly say `"wrapper"`, and how does `functools.wraps` fix it?
- How do you write a decorator that takes its own arguments, like `@retry(times=3)`, and why does it need **three** nested functions?
- If you stack two decorators, which one runs first? (The answer is different at decoration time and at call time. This is the most important idea of the chapter.)
- How can a decorator remember things between calls, like a call counter?
- How does `lru_cache` turn a function that takes minutes into one that takes microseconds, and when is caching wrong?
- What are `partial`, `reduce`, `singledispatch`, `itemgetter` and `methodcaller` for?
- When is functional style good Python, and when is it just a puzzle for the reader?

A note on how examples are shown. Every block of code is followed by the exact output produced by really running it with **Python 3.14**. Tracebacks show the folder path as `/home/you/project`. Some outputs contain a **memory address**, like `<function greet at 0x7f3a2c1b8a40>`. The hex number after `at` is different on your machine and on every run; only the words before it matter. Outputs that show **timings** (seconds, milliseconds) will also differ on your computer: a faster or slower laptop gives other numbers. Only the comparison matters. Answer every "Predict the output" question on paper before you open the answer.

What this chapter leaves out on purpose: decorators written as **classes**, and decorators applied **to classes**, need classes, which come in core.14. `@property`, `@staticmethod`, `@classmethod` and `functools.cached_property` also belong to classes; we only mention them. Real files come in core.12, and your own modules come in core.13.

## Table of contents

1. [Functions are objects](#1-functions-are-objects)
2. [The problem decorators solve](#2-the-problem-decorators-solve)
3. [A decorator by hand, then the `@` syntax](#3-a-decorator-by-hand-then-the--syntax)
4. [Wrappers that work for any function](#4-wrappers-that-work-for-any-function)
5. [Metadata and `functools.wraps`](#5-metadata-and-functoolswraps)
6. [Decorators with arguments](#6-decorators-with-arguments)
7. [Stacking decorators: the order of things](#7-stacking-decorators-the-order-of-things)
8. [Decorators that keep state](#8-decorators-that-keep-state)
9. [Useful decorator patterns](#9-useful-decorator-patterns)
10. [`functools.lru_cache` and `cache`](#10-functoolslru_cache-and-cache)
11. [`functools.partial`](#11-functoolspartial)
12. [`functools.reduce`](#12-functoolsreduce)
13. [`functools.singledispatch`](#13-functoolssingledispatch)
14. [The `operator` module](#14-the-operator-module)
15. [Functional style in Python](#15-functional-style-in-python)
16. [Project: a decorator toolkit](#16-project-a-decorator-toolkit)
17. [Common traps](#17-common-traps)
18. [Summary](#18-summary)

## 1. Functions are objects

Everything in this chapter rests on one fact: **in Python, a function is a value**, just like a number, a string or a list. You already used this fact in earlier chapters (for example `sorted(words, key=len)`), but now we need it fully, so let us look at it slowly.

### 1.1 A function is a value with a name

When Python runs a `def` statement, it does two things:

1. it builds a **function object** (the code, plus some information about it);
2. it binds a **name** to that object, exactly like `x = 5` binds the name `x` to the object `5`.

So the name and the function are two separate things. You can give the same function a second name, put it in a list, or store it in a dict.

```python
def greet(name):
    return f"Hello, {name}!"

print(greet)
print(type(greet))

say_hi = greet          # no brackets: we do NOT call it, we copy the reference
print(say_hi("Asha"))
print(say_hi is greet)

tools = [greet, len, str.upper]
for tool in tools:
    print(tool("kavya"))
```

```text
$ python obj1.py
<function greet at 0x735cf2a2f110>
<class 'function'>
Hello, Asha!
True
Hello, kavya!
5
KAVYA
```

Look at the line `say_hi = greet`. There are **no brackets**. `greet` (without brackets) is the function object itself. `greet("Asha")` (with brackets) **calls** the function and gives you its result. This difference, `f` versus `f()`, is the key to the whole chapter. Most decorator bugs come from adding or forgetting a pair of brackets.

The address `0x...` in `<function greet at 0x...>` is where the object lives in memory; yours will differ.

### 1.2 Passing a function in: higher-order functions

A function that **takes a function as an argument**, or **returns a function**, is called a **higher-order function**. You have used several already: `sorted(..., key=...)`, `max(..., key=...)`, `map`, `filter`. Here is one we write ourselves.

```python
def apply_twice(func, value):
    return func(func(value))

def add_three(n):
    return n + 3

print(apply_twice(add_three, 10))
print(apply_twice(str.upper, "ok"))
print(apply_twice(lambda s: s + "!", "hey"))
```

```text
$ python obj2.py
16
OK
hey!!
```

`apply_twice` does not know or care **which** function it gets. It only knows "I will call it twice". This is the first idea behind decorators: **code that works with any function**.

A dict of functions is a common pattern. It replaces a long `if/elif` chain:

```python
def add(a, b):
    return a + b

def sub(a, b):
    return a - b

operations = {"+": add, "-": sub, "*": lambda a, b: a * b}

for symbol in ["+", "-", "*"]:
    print(7, symbol, 3, "=", operations[symbol](7, 3))
```

```text
$ python obj3.py
7 + 3 = 10
7 - 3 = 4
7 * 3 = 21
```

`operations[symbol]` looks up a function; the `(7, 3)` after it calls that function. Keep this pattern in mind: in section 9 a decorator will fill such a dict for us.

### 1.3 Returning a function out

A function can also **create** a new function inside itself and return it.

```python
def make_multiplier(factor):
    def multiply(n):
        return n * factor
    return multiply          # return the function, do not call it

double = make_multiplier(2)
triple = make_multiplier(3)

print(double(10), triple(10))
print(double)
print(double.__name__)
```

```text
$ python obj4.py
20 30
<function make_multiplier.<locals>.multiply at 0x75601c3671c0>
multiply
```

Each call of `make_multiplier` runs the `def multiply` line again, so it builds a **new** function object each time. `double` and `triple` are two different functions that share the same code. Notice the printed form: `make_multiplier.<locals>.multiply`. Python is telling you "this is the `multiply` that lives inside `make_multiplier`". The short name, `__name__`, is just `multiply`.

### 1.4 Closures: a function that remembers

How does `double` still know `factor = 2` after `make_multiplier` has finished? You met the answer in the functions chapter: a **closure**. When an inner function uses a variable of the outer function, Python keeps that variable alive and attaches it to the inner function. (You can even see it: `double.__closure__[0].cell_contents` is `2`.) The closure is like a small backpack: the inner function carries the outer variables it needs.

To **change** a remembered variable (not just read it), the inner function needs `nonlocal`. A counter is the classic example:

```python
def make_counter():
    count = 0

    def tick():
        nonlocal count
        count += 1
        return count

    return tick

a = make_counter()
b = make_counter()
print(a(), a(), a())
print(b())
```

```text
$ python obj6.py
1 2 3
1
```

`a` and `b` each have their **own** `count`, because each call of `make_counter` created a new `count` variable. This is exactly how decorators will keep state (section 8).

### 1.5 A function carries information about itself

A function object has **attributes**: pieces of information stored on it. Some are filled in by Python, and you can add your own.

```python
def area(width: float, height: float) -> float:
    """Return the area of a rectangle."""
    return width * height

print(area.__name__)
print(area.__doc__)
print(area.__annotations__)
print(area.__module__)

area.unit = "square metres"      # our own attribute
print(area.unit)
print(area.__dict__)
```

```text
$ python obj7.py
area
Return the area of a rectangle.
{'width': <class 'float'>, 'height': <class 'float'>, 'return': <class 'float'>}
__main__
square metres
{'unit': 'square metres'}
```

- `__name__` is the name written after `def`.
- `__doc__` is the docstring (the string on the first line of the body).
- `__annotations__` holds the type hints.
- `__module__` is the module the function was defined in; for the script you run directly it is `"__main__"`.
- `__dict__` holds any attributes you added yourself.

`help(area)` and many tools (pytest, debuggers, documentation generators) read these attributes. Remember them: in section 5 a decorator will accidentally destroy them, and we will learn how to keep them.

## 2. The problem decorators solve

### 2.1 The same code, pasted everywhere

Let us measure how long some functions take. Python's `time.perf_counter()` returns a time in seconds from a very precise clock. The number itself means nothing; the **difference** between two readings is the time that passed.

Here are two functions, each with timing code pasted in:

```python
import time

def slow_sum(n):
    start = time.perf_counter()
    total = 0
    for i in range(n):
        total += i
    elapsed = time.perf_counter() - start
    print(f"slow_sum took {elapsed:.4f} s")
    return total

def count_vowels(text):
    start = time.perf_counter()
    result = sum(1 for ch in text if ch in "aeiou")
    elapsed = time.perf_counter() - start
    print(f"count_vowels took {elapsed:.4f} s")
    return result

print(slow_sum(1_000_000))
print(count_vowels("decorators are functions" * 10_000))
```

```text
$ python prob1.py
slow_sum took 0.0233 s
499999500000
count_vowels took 0.0038 s
90000
```

(Your timings will differ.) It works, but look at what happened to the functions:

- Three of the seven lines in `slow_sum` are about timing, not about summing. The real work is hidden.
- The timing lines are **copied**. If you want to change the message, you change it everywhere.
- To turn timing **off**, you must edit every function again.
- `count_vowels` used to be one line: `return sum(...)`. Now it needs a variable `result` just so the timing code can run after it.

The timing code is a **cross-cutting concern**: something many functions need, but which is not part of what any of them is about. Logging, timing, caching, retrying, checking permissions and checking arguments are all cross-cutting concerns.

### 2.2 The idea: wrap the function

What we want is to keep `slow_sum` clean:

```text
def slow_sum(n):
    total = 0
    for i in range(n):
        total += i
    return total
```

and put the timing **around** it, from the outside. Think of a gift. The gift (your function) stays the same. You put it inside wrapping paper (the extra behaviour). Whoever receives it first touches the paper, then reaches the gift, and the gift itself never changed.

In code: we write a function `timer` that

1. **receives** a function (say `slow_sum`),
2. **builds** a new function, `wrapper`, which reads the clock, calls the original, reads the clock again and prints the difference,
3. **returns** `wrapper`.

Then we let the name `slow_sum` point to `wrapper` instead of the original. Everybody who calls `slow_sum(...)` now runs the wrapper, and the wrapper runs the original. That is all a decorator is. The next section builds it step by step.

## 3. A decorator by hand, then the `@` syntax

### 3.1 The smallest decorator

We start with a function that takes no arguments, so we can focus on the wrapping.

```python
def announce(func):
    def wrapper():
        print("before the call")
        func()
        print("after the call")
    return wrapper

def say_hello():
    print("Hello!")

say_hello()                      # the plain function
print("---")
wrapped = announce(say_hello)    # build the improved version
wrapped()
```

```text
$ python deco1.py
Hello!
---
before the call
Hello!
after the call
```

Read `announce` slowly:

- `announce(func)` receives a function. It does **not** call it yet.
- Inside, it defines `wrapper`. The `def` line only builds the function; nothing is printed yet.
- `wrapper` uses `func`, so `func` is remembered in its closure (section 1.4).
- `announce` returns `wrapper` (no brackets: the function, not a call).

Only when we call `wrapped()` does the body of `wrapper` run: print, call the original, print.

### 3.2 Re-using the old name

In the example above, we have two names: `say_hello` (plain) and `wrapped` (improved). Usually we want the improved version **under the original name**, so that all existing calls get the new behaviour. So we rebind the name:

```text
say_hello = announce(say_hello)   # the name now points to wrapper
say_hello()                       # prints the same three lines as wrapped() did
```

How can `wrapper` still call the original if the name `say_hello` no longer points to it? Because `wrapper` does not use the **name** `say_hello`. It uses `func`, its own closure variable, which still holds the original function object. Draw it like this:

```text
before:   say_hello ──────────────► [original say_hello]

after:    say_hello ──► [wrapper] ── func ──► [original say_hello]
```

The original function still exists. Only the name moved.

### 3.3 The `@` syntax is just a shortcut

Writing `say_hello = announce(say_hello)` after every function is noisy, and it comes **after** the function, so a reader may miss it. Python gives a shortcut. These two programs do **exactly** the same thing:

```text
# long form                          # @ form
def say_hello():                     @announce
    print("Hello!")                  def say_hello():
say_hello = announce(say_hello)          print("Hello!")
```

```python
def announce(func):
    def wrapper():
        print("before the call")
        func()
        print("after the call")
    return wrapper

@announce
def say_hello():
    print("Hello!")

say_hello()
print(say_hello.__name__)
```

```text
$ python deco3.py
before the call
Hello!
after the call
wrapper
```

The rule, word for word: **`@something` above a `def` means "after you build this function, call `something(the_function)` and bind the name to whatever it returns."** Two details follow from this rule:

1. The thing after `@` must be **callable with one argument** (the function). We will use this in section 6.
2. The name gets **whatever the decorator returns**. Here it returned `wrapper`, so `say_hello.__name__` is now `"wrapper"`. That is a problem we fix in section 5.

The word "decorator" names the role, not a special kind of object. `announce` is an ordinary function. It becomes a decorator because we use it with `@`.

### 3.4 When does a decorator run?

This question confuses many learners, so let us answer it with prints. There are **two** different moments:

- **Decoration time**: when Python reaches the `@deco` / `def` lines. The decorator function runs **once**, here. This is usually when the program starts (when the module is loaded).
- **Call time**: every time somebody calls the decorated function. The **wrapper** runs, here, again and again.

```python
print("1. program starts")

def announce(func):
    print(f"  [decoration time] announce got {func.__name__}")

    def wrapper():
        print("  [call time] wrapper runs")
        func()
    return wrapper

print("2. about to define say_hello")

@announce
def say_hello():
    print("  Hello!")

print("3. say_hello is defined, nothing called yet")
say_hello()
say_hello()
print("4. end")
```

```text
$ python when1.py
1. program starts
2. about to define say_hello
  [decoration time] announce got say_hello
3. say_hello is defined, nothing called yet
  [call time] wrapper runs
  Hello!
  [call time] wrapper runs
  Hello!
4. end
```

`announce` printed its line **once**, between step 2 and step 3, although we never "called" `say_hello` there. The wrapper printed its line once **per call**. Keep these two moments apart in your head. Code in the decorator body (outside `wrapper`) runs once at definition; code inside `wrapper` runs on every call.

### 3.5 Predict the output

```python
def double_it(func):
    print("decorating", func.__name__)

    def wrapper():
        return func() * 2
    return wrapper

@double_it
def five():
    return 5

@double_it
def word():
    return "ab"

print("start")
print(five())
print(word())
print(five())
```

<details><summary>Answer</summary>

```text
$ python try2.py
decorating five
decorating word
start
10
abab
10
```

Both "decorating" lines print first, at definition time, before `start`. Each call runs only the wrapper: `5 * 2` is `10`, and `"ab" * 2` is `"abab"` (repeating a string). The decorator itself does not run again on the second `five()` call.

</details>


## 4. Wrappers that work for any function

### 4.1 The problem: arguments

Our `announce` decorator has a hidden weakness. Its `wrapper` takes **no** arguments. Try it on a function that takes one:

```python
def announce(func):
    def wrapper():
        print("before the call")
        func()
        print("after the call")
    return wrapper

@announce
def greet(name):
    print(f"Hello, {name}!")

greet("Asha")
```

```text
$ python args1.py
Traceback (most recent call last):
  File "/home/you/project/args1.py", line 12, in <module>
    greet("Asha")
    ~~~~~^^^^^^^^
TypeError: announce.<locals>.wrapper() takes 0 positional arguments but 1 was given
```

Read the error carefully: it is `wrapper` that complains, not `greet`. Remember, the name `greet` now points to `wrapper`. So `greet("Asha")` is really `wrapper("Asha")`, and `wrapper` was defined with no parameters.

We could write `def wrapper(name):`, but then the decorator only works for functions with exactly one argument. A decorator should work for **any** function: zero arguments, three arguments, keyword arguments, defaults. We need a wrapper that accepts **anything** and passes **everything** on.

### 4.2 `*args` and `**kwargs`: accept anything, pass everything

You met these in the functions chapter:

- In a `def`, `*args` collects all extra **positional** arguments into a tuple, and `**kwargs` collects all extra **keyword** arguments into a dict.
- In a call, `*args` spreads a tuple back out into positional arguments, and `**kwargs` spreads a dict back out into keyword arguments.

So `def wrapper(*args, **kwargs)` accepts any arguments, and `func(*args, **kwargs)` passes them on **exactly as they came in**.

```python
def announce(func):
    def wrapper(*args, **kwargs):
        print(f"before: args={args} kwargs={kwargs}")
        func(*args, **kwargs)
        print("after")
    return wrapper

@announce
def greet(name, punctuation="!"):
    print(f"Hello, {name}{punctuation}")

@announce
def nothing():
    print("no arguments here")

greet("Asha")
greet("Ravi", punctuation="?")
nothing()
```

```text
$ python args2.py
before: args=('Asha',) kwargs={}
Hello, Asha!
after
before: args=('Ravi',) kwargs={'punctuation': '?'}
Hello, Ravi?
after
before: args=() kwargs={}
no arguments here
after
```

One wrapper, any function. The names `args` and `kwargs` are only a habit; the stars do the work. But use these names: every Python programmer recognises them at once.

### 4.3 The second problem: the lost return value

Now try a function that **returns** something instead of printing:

```python
def announce(func):
    def wrapper(*args, **kwargs):
        print("before")
        func(*args, **kwargs)
        print("after")
    return wrapper

@announce
def add(a, b):
    return a + b

result = add(2, 3)
print("result is", result)
```

```text
$ python ret1.py
before
after
result is None
```

`add` computed `5`, but the wrapper **threw it away**. The wrapper called `func(...)` and ignored the result, and a function that reaches its end without `return` gives `None`. The caller only ever sees what the **wrapper** returns.

The fix: keep the result, do the "after" work, then return it.

```python
def announce(func):
    def wrapper(*args, **kwargs):
        print("before")
        result = func(*args, **kwargs)
        print("after")
        return result
    return wrapper

@announce
def add(a, b):
    return a + b

print("result is", add(2, 3))
```

```text
$ python ret2.py
before
after
result is 5
```

This is the most common decorator bug of all. The decorated function "works" (you see the prints), so the bug hides until somebody uses the result. **Every wrapper must return the result of the call** unless it changes the result on purpose.

### 4.4 The general template

Put the two fixes together, and you have the shape of almost every decorator you will ever write:

```text
def my_decorator(func):                  # runs once, at decoration time
    def wrapper(*args, **kwargs):        # runs on every call
        # ... do something BEFORE ...
        result = func(*args, **kwargs)   # call the original
        # ... do something AFTER ...
        return result                    # give the result back
    return wrapper                       # no brackets!
```

Learn this shape by heart. Every later decorator is this template with something in the "before" and "after" slots (and `functools.wraps`, added in section 5).

### 4.5 Example: a `timer` decorator

Now we can solve the problem from section 2 properly.

```python
import time

def timer(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start
        print(f"{func.__name__} took {elapsed:.4f} s")
        return result
    return wrapper

@timer
def slow_sum(n):
    total = 0
    for i in range(n):
        total += i
    return total

@timer
def count_vowels(text):
    return sum(1 for ch in text if ch in "aeiou")

print(slow_sum(1_000_000))
print(count_vowels("decorators are functions" * 10_000))
```

```text
$ python timer1.py
slow_sum took 0.0215 s
499999500000
count_vowels took 0.0038 s
90000
```

(Your timings will differ.) Compare with section 2.1. `slow_sum` and `count_vowels` are back to their clean form. The timing code exists once. To stop timing a function, delete one line (`@timer`). Inside the wrapper, `func.__name__` is the **original** function's name, so the message is correct for each function.

### 4.6 Example: a `log_calls` decorator

A logger prints each call with its arguments and its result. What should it do when the function raises an error? Without any special code, the line after `func(...)` never runs, and the error travels up to the caller as usual. That is right: a decorator should not hide errors unless that is its job. But a good logger should also **record** the error. So we catch it, print it, and `raise` it again (a bare `raise` inside `except` re-raises the same exception).

`!r` in an f-string shows a value with `repr()`, so strings keep their quotes.

```python
def log_calls(func):
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
        except Exception as e:
            print(f"!! {func.__name__}{args} raised {type(e).__name__}: {e}")
            raise
        print(f"<- {func.__name__}{args} returned {result!r}")
        return result
    return wrapper

@log_calls
def divide(a, b):
    return a / b

divide(6, 3)
try:
    divide(1, 0)
except ZeroDivisionError:
    print("the caller still sees the error")
```

```text
$ python log3.py
<- divide(6, 3) returned 2.0
!! divide(1, 0) raised ZeroDivisionError: division by zero
the caller still sees the error
```

### 4.7 Predict the output

```python
def plus_one(func):
    def wrapper(*args, **kwargs):
        func(*args, **kwargs) + 1

    return wrapper

@plus_one
def square(n):
    return n * n

print(square(4))
```

<details><summary>Answer</summary>

```text
$ python try3.py
None
```

The wrapper computes `16 + 1 = 17` and then throws it away: there is no `return`. So `square(4)` returns `None`. The fix is `return func(*args, **kwargs) + 1`.

</details>

## 5. Metadata and `functools.wraps`

### 5.1 The problem: the function forgets who it is

In section 1.5 you saw that a function carries information about itself: `__name__`, `__doc__`, `__annotations__`. Watch what a decorator does to it.

```python
def log_calls(func):
    def wrapper(*args, **kwargs):
        print(f"calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@log_calls
def area(width: float, height: float) -> float:
    """Return the area of a rectangle."""
    return width * height

print(area.__name__)
print(area.__doc__)
print(area.__annotations__)
help(area)
```

```text
$ python meta1.py
wrapper
None
{}
Help on function wrapper in module __main__:

wrapper(*args, **kwargs)
```

Of course! The name `area` now points to `wrapper`, so we see **wrapper's** name, wrapper's docstring (it has none), wrapper's type hints (none) and wrapper's signature `(*args, **kwargs)`. The original information still exists on the original function, but nobody can see it.

### 5.2 Why this matters

"It still computes the right area, so who cares?" Many tools care:

- `help(area)` and code editors show the wrong name and no documentation. Your function is now undocumented.
- Error messages and logs print `wrapper` instead of the real name. Imagine a log with fifty different functions, all called `wrapper`.
- pytest and other tools find and report things by name.
- A **registry** that stores functions by `func.__name__` (section 9.2) would store them all under the key `"wrapper"`, each one overwriting the last.
- If you stack decorators, the next decorator sees `wrapper` instead of `area`, so a timer above a logger would print `wrapper took ...`.

A good decorator should be **invisible** from the outside: the decorated function should look like the original, only with extra behaviour.

### 5.3 `functools.wraps`

We could copy the attributes by hand (`wrapper.__name__ = func.__name__`, `wrapper.__doc__ = func.__doc__`), but there are more of them (`__qualname__`, `__module__`, `__annotations__`, the custom `__dict__`...), and we would have to remember them in every decorator. The standard library does it for you. `functools` is a standard module of tools for working with functions. Its `wraps` is itself a decorator, and you put it on the **wrapper**:

```python
import functools

def log_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print(f"calling {func.__name__}")
        return func(*args, **kwargs)
    return wrapper

@log_calls
def area(width: float, height: float) -> float:
    """Return the area of a rectangle."""
    return width * height

print(area.__name__)
print(area.__qualname__)
print(area.__doc__)
print(area.__annotations__)
help(area)
print(area(3, 4))
```

```text
$ python meta3.py
area
area
Return the area of a rectangle.
{'width': <class 'float'>, 'height': <class 'float'>, 'return': <class 'float'>}
Help on function area in module __main__:

area(width: float, height: float) -> float
    Return the area of a rectangle.

calling area
12
```

Everything is back: the name, the docstring, the type hints, and even `help` shows the real signature `(width: float, height: float) -> float`. Notice that `@functools.wraps(func)` has **brackets and an argument**. It is a decorator **with arguments**, the kind we learn to write in section 6. Read it as: "make this wrapper look like `func`".

`wraps` copies these attributes from `func` to `wrapper`: `__module__`, `__name__`, `__qualname__`, `__doc__`, `__annotations__` (plus a few rarer ones), and it **merges** `func.__dict__` (your own attributes) into `wrapper.__dict__`.

From now on, **every decorator in this chapter uses `@functools.wraps(func)`**. Make it a habit: there is no good reason to leave it out.

### 5.4 `__wrapped__`: the way back to the original

`wraps` also adds one new attribute: `wrapper.__wrapped__`, which points to the **original** function. That gives you a way to call the function **without** the decorator, which is useful in tests:

```python
import functools

def shout_result(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return str(func(*args, **kwargs)).upper() + "!!!"
    return wrapper

@shout_result
def greet(name):
    return f"hello {name}"

print(greet("asha"))
print(greet.__wrapped__("asha"))
print(greet.__wrapped__)
print(greet)
```

```text
$ python meta4.py
HELLO ASHA!!!
hello asha
<function greet at 0x7d128b084300>
<function greet at 0x7d128aeea560>
```

Both objects print as `<function greet ...>` (because `wraps` copied the name), but the addresses differ: they are two different functions. `greet` is the wrapper; `greet.__wrapped__` is the original.

Tools that report a function's parameters, such as `inspect.signature` from the standard `inspect` module, follow `__wrapped__` to the original. That is why `help(area)` in section 5.3 showed the real parameters `(width: float, height: float)` and not `(*args, **kwargs)`.

### 5.5 Predict the output

```python
import functools

def tag(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return "<" + func(*args, **kwargs) + ">"
    return wrapper

def untagged(func):
    def wrapper(*args, **kwargs):
        return "[" + func(*args, **kwargs) + "]"
    return wrapper

@tag
def first():
    """First function."""
    return "a"

@untagged
def second():
    """Second function."""
    return "b"

print(first.__name__, first.__doc__, first())
print(second.__name__, second.__doc__, second())
```

<details><summary>Answer</summary>

```text
$ python try4.py
first First function. <a>
wrapper None [b]
```

`first` was wrapped with `functools.wraps`, so it keeps its name and docstring. `second` was not, so it shows `wrapper` and `None` (the wrapper has no docstring). Both still work correctly when called.

</details>

## 6. Decorators with arguments

### 6.1 The wish: configure the decorator

Our decorators so far do the same thing for every function. Often you want to **configure** them:

- `@repeat(3)`: run the function three times.
- `@retry(times=5)`: try up to five times.
- `@log_calls(prefix="DB")`: put a label in front of every log line.

Look again at the rule from section 3.3: **`@something` calls `something(the_function)`**. The "something" is any **expression** that gives a callable. So in

```text
@repeat(3)
def say_hi():
    ...
```

Python first **evaluates** `repeat(3)`, and then uses **whatever that returns** as the decorator. So `repeat(3)` must **return a decorator**: a function that takes `say_hi` and returns a wrapper. That is one level more than before.

### 6.2 Three layers

Here is `repeat`:

```python
import functools

def repeat(times):                       # layer 1: takes the settings
    def decorator(func):                 # layer 2: takes the function
        @functools.wraps(func)
        def wrapper(*args, **kwargs):    # layer 3: takes the call's arguments
            result = None
            for _ in range(times):
                result = func(*args, **kwargs)
            return result
        return wrapper
    return decorator

@repeat(3)
def say_hi(name):
    print(f"hi {name}")

say_hi("Asha")
print(say_hi.__name__)
```

```text
$ python rep1.py
hi Asha
hi Asha
hi Asha
say_hi
```

Each layer has one job, and each layer runs at a different moment:

| Layer | Receives | Returns | Runs when |
|---|---|---|---|
| `repeat(times)` | the settings (`3`) | `decorator` | once, when Python evaluates `@repeat(3)` |
| `decorator(func)` | the function (`say_hi`) | `wrapper` | once, right after, at decoration time |
| `wrapper(*args, **kwargs)` | the call's arguments | the result | on every call |

Why can `wrapper` still use `times` and `func` after `repeat` and `decorator` have returned? Closures, again. `wrapper` lives inside `decorator`, which lives inside `repeat`, so it remembers the variables of both.

It helps to see what `@repeat(3)` turns into without the `@`. These are the same:

```text
@repeat(3)                         def say_hi(name): ...
def say_hi(name): ...              decorator = repeat(3)
                                   say_hi = decorator(say_hi)
```

or in one line: `say_hi = repeat(3)(say_hi)`. The two pairs of brackets are the two calls: `repeat(3)` gives a decorator, and `(say_hi)` calls that decorator with the function.

### 6.3 Watching the three layers run

Prints make the three moments visible:

```python
import functools

def repeat(times):
    print(f"1. repeat({times}) runs: making a decorator")

    def decorator(func):
        print(f"2. decorator runs: wrapping {func.__name__}")

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            print(f"3. wrapper runs: calling {func.__name__} {times} times")
            for _ in range(times):
                func(*args, **kwargs)
        return wrapper
    return decorator

@repeat(2)
def beep():
    print("   beep")

print("--- definitions finished ---")
beep()
beep()
```

```text
$ python rep2.py
1. repeat(2) runs: making a decorator
2. decorator runs: wrapping beep
--- definitions finished ---
3. wrapper runs: calling beep 2 times
   beep
   beep
3. wrapper runs: calling beep 2 times
   beep
   beep
```

Steps 1 and 2 happen once, while Python is reading the definitions. Step 3 happens on every call.

### 6.4 `@deco` versus `@deco()`: the bracket mistake

A decorator **with** settings must be used **with** brackets, even when you pass no settings. Take a logger with a label, `def log_calls(prefix="LOG")`, built with three layers like `repeat`. To use the default label you must still write `@log_calls()`. Forget the brackets, and the layers slip by one. Python calls `log_calls(shout)`, so `prefix` becomes the function `shout`, and the name `shout` gets bound to `decorator`:

```python
import functools

def log_calls(prefix="LOG"):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            print(f"[{prefix}] {func.__name__} -> {result!r}")
            return result
        return wrapper
    return decorator

@log_calls                # brackets forgotten!
def shout(word):
    return word.upper()

print(shout)
print(shout("hey"))
```

```text
$ python brk1.py
<function log_calls.<locals>.decorator at 0x777a50906560>
<function log_calls.<locals>.decorator.<locals>.wrapper at 0x777a50904510>
```

No error at definition time. The error, or here the strange result, appears only later when you call `shout`. `shout("hey")` actually called `decorator("hey")`, which returned a wrapper function. So you see a function printed where you expected `"HEY"`.

The opposite mistake: putting brackets on a decorator that does **not** take settings:

```python
import functools

def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return func(*args, **kwargs)
    return wrapper

@timer()                  # brackets added by mistake
def work():
    return 42
```

```text
$ python brk2.py
Traceback (most recent call last):
  File "/home/you/project/brk2.py", line 9, in <module>
    @timer()                  # brackets added by mistake
     ~~~~~^^
TypeError: timer() missing 1 required positional argument: 'func'
```

`timer()` is called with no arguments, but `timer` needs `func`. This error at least happens at once, when the program starts.

**How to remember**: look at the decorator's outermost `def`. If it takes `func`, use `@name`. If it takes settings, use `@name(...)`, with brackets even when you pass nothing.

A note: some libraries let you write both `@log_calls` and `@log_calls(prefix="X")`. They do it by making the first parameter `func=None` and the settings keyword-only (`def log_calls(func=None, *, prefix="LOG")`), then checking: if a function arrived, decorate it at once; if not, return the decorator. It is handy for users but harder to read. In your own code, the plain three-layer form, always used with brackets, is fine.

### 6.5 Predict the output

```python
import functools

def multiply_result(factor):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs) * factor
        return wrapper
    return decorator

@multiply_result(10)
def add(a, b):
    return a + b

triple = multiply_result(3)

@triple
def seven():
    return 7

print(add(1, 2))
print(seven())
print(multiply_result(2)(add)(1, 1))
```

<details><summary>Answer</summary>

```text
$ python try5.py
30
21
40
```

- `add(1, 2)` is `3 * 10 = 30`.
- `triple = multiply_result(3)` stores a decorator in a variable. `@triple` is just `@` with a name, so `seven()` is `7 * 3 = 21`.
- The last line decorates the **already decorated** `add` again, by hand: `multiply_result(2)(add)` wraps it once more. Calling it with `(1, 1)` gives `(1 + 1) * 10 * 2 = 40`.

</details>

## 7. Stacking decorators: the order of things

This section answers the main outcome of the module: **in which order do stacked decorators run?** Read it slowly, run the examples yourself, and do every prediction.

### 7.1 Two decorators on one function

You can put several decorators on one function:

```text
@bold
@italic
def hello():
    return "hello"
```

What does this mean? Apply the rule from section 3.3 twice, starting from the decorator **closest to the `def`**:

```text
hello = italic(hello)     # first the inner one (closest to def)
hello = bold(hello)       # then the outer one
```

or in one line: **`hello = bold(italic(hello))`**. The decorators are applied **bottom-up**, exactly like nested function calls are evaluated from the inside out.

```python
import functools

def bold(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return "<b>" + func(*args, **kwargs) + "</b>"
    return wrapper

def italic(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        return "<i>" + func(*args, **kwargs) + "</i>"
    return wrapper

@bold
@italic
def hello():
    return "hello"

@italic
@bold
def bye():
    return "bye"

print(hello())
print(bye())
```

```text
$ python stack1.py
<b><i>hello</i></b>
<i><b>bye</b></i>
```

`hello` is `bold(italic(hello))`: the italic tags are inside, the bold tags outside. `bye` is the reverse. **The decorator written on top ends up on the outside.**

### 7.2 Two moments, two orders

Now the important part. Remember the two moments from section 3.4: decoration time and call time. Stacked decorators have a **different order at each moment**.

- **Decoration time: bottom-up.** The decorator nearest the `def` wraps the function first. The top decorator wraps last, and it wraps the **result** of the one below.
- **Call time: top-down on the way in, bottom-up on the way out.** A call enters the outermost wrapper (the top decorator) first. That wrapper calls the next one inside, and so on, down to the original function. Then the results travel back out through the same wrappers in reverse order.

Let us prove it with prints. Each decorator prints when it decorates, when its wrapper starts, and when its wrapper finishes.

```python
import functools

def first(func):
    print(f"[decorate] first  wraps {func.__name__}")

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print("  first : enter")
        result = func(*args, **kwargs)
        print("  first : exit")
        return result
    return wrapper

def second(func):
    print(f"[decorate] second wraps {func.__name__}")

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        print("  second: enter")
        result = func(*args, **kwargs)
        print("  second: exit")
        return result
    return wrapper

@first
@second
def work():
    print("    work runs")
    return "done"

print("=== calling work() ===")
print(work())
```

```text
$ python order1.py
[decorate] second wraps work
[decorate] first  wraps work
=== calling work() ===
  first : enter
  second: enter
    work runs
  second: exit
  first : exit
done
```

Read the output from top to bottom:

1. At decoration time, `second` wraps first (it is nearest the `def`), and then `first` wraps. Bottom-up.
2. At call time, `first` enters first (it is on the outside), then `second`, then `work` itself. Top-down.
3. On the way out, `second` exits first, then `first`. Bottom-up again.

One more detail: the line `[decorate] first  wraps work` says `work`, not `wrapper`, although `first` received `second`'s wrapper. That is `functools.wraps` at work: `second`'s wrapper already looks like `work`. Without `wraps`, it would say `first  wraps wrapper`.

### 7.3 The onion picture

Think of an **onion**, or of the gift in wrapping paper, now with two layers of paper. The layer written at the top of the code is the **outer skin**.

```text
            @first
            @second
            def work

  decoration time (building the onion, inside -> out):

      work  ──second──►  second_wrapper(work)  ──first──►  first_wrapper(second_wrapper(work))
      step 1: second wraps work           step 2: first wraps the result

  call time (a call passes through the onion, outside -> in -> out):

      work()   (the name work now means first_wrapper)
        │
        ▼
      ┌─────────────────────────────────────────────┐
      │ first wrapper:   "first : enter"            │
      │   ┌─────────────────────────────────────┐   │
      │   │ second wrapper: "second: enter"     │   │
      │   │   ┌─────────────────────────────┐   │   │
      │   │   │ original work: "work runs"  │   │   │
      │   │   └─────────────────────────────┘   │   │
      │   │ second wrapper: "second: exit"      │   │
      │   └─────────────────────────────────────┘   │
      │ first wrapper:   "first : exit"             │
      └─────────────────────────────────────────────┘
        │
        ▼
      "done" returned to the caller
```

A short way to remember all three facts:

- **Decorate bottom-up.** (Closest to `def` first.)
- **Enter top-down.** (Outermost wrapper first.)
- **Exit bottom-up.** (Innermost wrapper finishes first.)

Why the two orders? To **build** the onion you must start from the core and add skins outwards. To **reach** the core from outside you must go through the outer skin first. Same onion, two directions.

### 7.4 Three decorators, fully traced

With settings, so you can see all layers at once. One decorator factory, used three times with different labels:

```python
import functools

def layer(label):
    print(f"[factory]  layer({label!r}) called")

    def decorator(func):
        print(f"[decorate] {label} wraps {func.__name__}")

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            print(f"  {label}: enter")
            result = func(*args, **kwargs)
            print(f"  {label}: exit, result={result}")
            return result + 1
        return wrapper
    return decorator

@layer("A")
@layer("B")
@layer("C")
def base():
    print("    base runs")
    return 0

print("=== call ===")
print("final:", base())
```

```text
$ python order2.py
[factory]  layer('A') called
[factory]  layer('B') called
[factory]  layer('C') called
[decorate] C wraps base
[decorate] B wraps base
[decorate] A wraps base
=== call ===
  A: enter
  B: enter
  C: enter
    base runs
  C: exit, result=0
  B: exit, result=1
  A: exit, result=2
final: 3
```

Something new is visible here. The **factories** `layer("A")`, `layer("B")`, `layer("C")` run **top-down**: Python evaluates the decorator expressions in the order they are written. Only after all three decorators exist are they applied, bottom-up. So the full timeline is:

```text
1. evaluate the @ expressions, top to bottom:  layer("A"), layer("B"), layer("C")
2. build the function base
3. apply the decorators, bottom to top:        C wraps base, B wraps that, A wraps that
4. on each call: enter A, enter B, enter C, base, exit C, exit B, exit A
```

And look at the results: `base` returns `0`. C sees `0` and returns `1`, B sees `1` and returns `2`, A sees `2` and returns `3`. Each wrapper sees the result of the layer **inside** it.

### 7.5 Why the order matters

The order is not just a puzzle. It changes behaviour. Two real examples.

**A timer and a cache.** We have not built a cache yet, but imagine `@cache` returns a stored result immediately if it has seen the arguments before.

```text
@timer          # timer is outside: it measures EVERY call, including fast cache hits
@cache
def report(day): ...

@cache          # cache is outside: a cache hit returns before the timer runs,
@timer          # so only the real (slow) computations get timed and printed
def report(day): ...
```

Neither is wrong; they answer different questions ("how fast is each call?" versus "how slow is the real work?").

**A logger and a retry.** Imagine `@retry(3)` calls the function again when it fails.

```text
@log_calls      # one log line per call by the user (retries are invisible)
@retry(3)
def fetch(): ...

@retry(3)       # one log line per attempt (you see every retry)
@log_calls
def fetch(): ...
```

You will see the first of these stacks running for real in the project (section 16.5).

**Rule of thumb**: decide what each decorator should "see". A decorator sees everything **below** it in the stack as one black box.

### 7.6 Predict the output (1)

```python
import functools

def add_one(func):
    @functools.wraps(func)
    def wrapper(n):
        return func(n) + 1
    return wrapper

def double(func):
    @functools.wraps(func)
    def wrapper(n):
        return func(n) * 2
    return wrapper

@add_one
@double
def f(n):
    return n

@double
@add_one
def g(n):
    return n

print(f(5), g(5))
```

<details><summary>Answer</summary>

```text
$ python try6.py
11 12
```

`f = add_one(double(f))`. The call enters `add_one`'s wrapper, which calls `double`'s wrapper, which calls the original: `5`. On the way out, `double` makes it `10`, then `add_one` makes it `11`. For `g`, the order is reversed: `5 + 1 = 6`, then `6 * 2 = 12`. The **bottom** decorator acts on the result **first**.

</details>

### 7.7 Predict the output (2)

Here only the decoration-time prints matter. Nothing is called.

```python
def deco(name):
    print("make", name)

    def decorator(func):
        print("apply", name)
        return func
    return decorator

@deco("x")
@deco("y")
def h():
    pass

print("done")
```

<details><summary>Answer</summary>

```text
$ python try7.py
make x
make y
apply y
apply x
done
```

The `@` expressions `deco("x")` and `deco("y")` are evaluated top-down ("make x", "make y"). Then the decorators are applied bottom-up ("apply y", "apply x"). Notice this decorator returns `func` unchanged; that is allowed (section 9.2 uses it).

</details>

### 7.8 Predict the output (3)

```python
import functools

def trace(label):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            print("in ", label)
            result = func(*args, **kwargs)
            print("out", label)
            return result
        return wrapper
    return decorator

@trace("outer")
@trace("middle")
@trace("inner")
def ping():
    print("ping!")

ping()
```

<details><summary>Answer</summary>

```text
$ python try8.py
in  outer
in  middle
in  inner
ping!
out inner
out middle
out outer
```

Enter top-down (`outer`, `middle`, `inner`), run the function, exit bottom-up (`inner`, `middle`, `outer`). Like opening three nested boxes and closing them again.

</details>


## 8. Decorators that keep state

Some decorators must **remember** something between calls: how many times the function ran, which arguments it got, when it was last called. Where can a decorator keep that memory? Not in a normal local variable of `wrapper`: those are created fresh on every call and lost at the end. There are two good places.

### 8.1 State in the closure, with `nonlocal`

Exactly like `make_counter` in section 1.4: put the variable in the **decorator** (the outer function), and change it from the wrapper with `nonlocal`.

```python
import functools

def count_calls(func):
    calls = 0

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        nonlocal calls
        calls += 1
        print(f"{func.__name__} call #{calls}")
        return func(*args, **kwargs)
    return wrapper

@count_calls
def hello():
    return "hi"

@count_calls
def bye():
    return "bye"

hello()
hello()
bye()
hello()
```

```text
$ python state1.py
hello call #1
hello call #2
bye call #1
hello call #3
```

`hello` and `bye` each have their **own** counter. Why? `count_calls` ran twice (once per `@count_calls`), and each run created a new `calls` variable for its own wrapper.

The weakness: `calls` is hidden. Code outside cannot read it or reset it.

### 8.2 State as a function attribute

A function is an object, and you can put attributes on it (section 1.5). So store the state **on the wrapper**. Then anybody can read it as `hello.calls`.

```python
import functools

def count_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.calls += 1
        return func(*args, **kwargs)
    wrapper.calls = 0
    return wrapper

@count_calls
def square(n):
    return n * n

for n in range(5):
    square(n)
print("square was called", square.calls, "times")
square.calls = 0          # reset from outside
square(9)
print("after reset:", square.calls)
```

```text
$ python state2.py
square was called 5 times
after reset: 1
```

Note the order inside `count_calls`: we set `wrapper.calls = 0` **after** the `def` (the wrapper must exist first) and **before** `return`. Inside the wrapper, `wrapper.calls += 1` needs no `nonlocal`: we do not rebind the name `wrapper`, we change an attribute of the object it points to.

You can attach **functions** too, for example a `wrapper.reset` helper. `lru_cache` (section 10) uses exactly this idea: it attaches the functions `cache_info` and `cache_clear` to its wrapper.

### 8.3 Trap: state shared by every function

If you put the state **outside** the decorator, all decorated functions share it:

```python
import functools

calls = []                     # one list for the whole program

def record(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        calls.append(func.__name__)
        return func(*args, **kwargs)
    return wrapper

@record
def a():
    pass

@record
def b():
    pass

a()
b()
a()
print(calls)
```

```text
$ python state4.py
['a', 'b', 'a']
```

Sometimes that is what you want (one global log of everything). But if you wanted "a list per function", this is a bug. **State created inside the decorator belongs to one function. State created outside is shared.**

### 8.4 Predict the output

```python
import functools

def limit(max_calls):
    def decorator(func):
        used = 0

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal used
            if used >= max_calls:
                return "limit reached"
            used += 1
            return func(*args, **kwargs)
        return wrapper
    return decorator

@limit(2)
def hi():
    return "hi"

@limit(1)
def yo():
    return "yo"

print(hi(), yo(), hi(), yo(), hi())
```

<details><summary>Answer</summary>

```text
$ python try9.py
hi yo hi limit reached limit reached
```

`hi` may run twice and `yo` once, each with its own `used` counter (each decoration made a new one). The arguments to `print` are evaluated left to right: `hi` (1st), `yo` (1st), `hi` (2nd), `yo` (blocked), `hi` (blocked).

</details>

## 9. Useful decorator patterns

### 9.1 Checking arguments

A decorator can check the arguments **before** the function runs, and refuse bad ones. This keeps the checks out of the function body.

```python
import functools

def positive_ints(func):
    @functools.wraps(func)
    def wrapper(*args):
        for value in args:
            if not isinstance(value, int) or value <= 0:
                raise ValueError(f"{func.__name__}: expected positive int, got {value!r}")
        return func(*args)
    return wrapper

@positive_ints
def rectangle_area(width, height):
    return width * height

print(rectangle_area(3, 4))
for bad in [(3, -1), (2, "5")]:
    try:
        rectangle_area(*bad)
    except ValueError as e:
        print("refused:", e)
```

```text
$ python check1.py
12
refused: rectangle_area: expected positive int, got -1
refused: rectangle_area: expected positive int, got '5'
```

This wrapper takes only `*args`, because it checks positional arguments. That is fine: a decorator does not **have** to accept everything, as long as it fits the functions you use it on.

### 9.2 Registering functions: a plugin registry

A decorator does not have to wrap anything. It can **record** the function somewhere and return it **unchanged**. This is how web frameworks connect URLs to functions. Here is a tiny command system, using the dict-of-functions pattern from section 1.2:

```python
COMMANDS = {}

def command(name):
    def decorator(func):
        COMMANDS[name] = func
        return func          # unchanged: no wrapper, nothing to wrap
    return decorator

@command("add")
def add(a, b):
    return a + b

@command("max")
def biggest(a, b):
    return max(a, b)

print(sorted(COMMANDS))
for line in ["add 2 3", "max 7 4", "pow 2 8"]:
    name, *numbers = line.split()
    func = COMMANDS.get(name)
    if func is None:
        print(f"{line!r}: unknown command")
    else:
        print(f"{line!r}: {func(*map(int, numbers))}")
```

```text
$ python reg1.py
['add', 'max']
'add 2 3': 5
'max 7 4': 7
'pow 2 8': unknown command
```

To add a new command, you write a new function with `@command("...")`. The loop that runs commands never changes. The registration happens at **decoration time**: the dict is full before any command is run.

### 9.3 Retry, with an injectable `sleep`

Network calls fail sometimes for no good reason. A retry decorator calls the function again after a short pause. Two design ideas make it good:

1. It retries **only** for the exceptions you name. A `TypeError` is a bug in your code; retrying it is pointless.
2. It takes the `sleep` function as a setting, `sleep=time.sleep` by default. In tests we pass a **fake** sleep that only records the delays, so the test runs instantly and we can check the delays. This is called **injecting** a dependency.

```python
import functools
import time

def retry(times=3, delay=1.0, exceptions=(Exception,), sleep=time.sleep):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == times:
                        raise
                    print(f"attempt {attempt} failed ({e}), waiting {delay} s")
                    sleep(delay)
        return wrapper
    return decorator

waits = []                                 # our fake sleep writes here
attempts = 0

@retry(times=4, delay=0.5, exceptions=(ConnectionError,), sleep=waits.append)
def fetch_price():
    global attempts
    attempts += 1
    if attempts < 3:
        raise ConnectionError("server busy")
    return 499

print("price:", fetch_price())
print("slept:", waits)
```

```text
$ python retry1.py
attempt 1 failed (server busy), waiting 0.5 s
attempt 2 failed (server busy), waiting 0.5 s
price: 499
slept: [0.5, 0.5]
```

`sleep=waits.append` is the trick: `waits.append(0.5)` "sleeps" by recording `0.5`. No real time passes. (`except exceptions as e` works because `except` accepts a tuple of exception types.) If every attempt fails, the last `raise` passes the error to the caller. The project in section 16 adds **backoff**: waiting longer after each failure.

### 9.4 A note on type hints for decorators

What type is a decorator? It takes a callable and returns a callable. With the `typing` tools you know, the honest simple answer is:

```text
from typing import Any, Callable

def log_calls(func: Callable[..., Any]) -> Callable[..., Any]:
    @functools.wraps(func)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        ...
    return wrapper
```

`Callable[..., Any]` means "a function taking any arguments and returning anything". It is correct but loose: after decorating `def add(a: int, b: int) -> int`, a type checker no longer knows that `add` takes two ints. Python has a precise tool for this (`ParamSpec`, and in Python 3.12+ the syntax `def log_calls[**P, R](func: Callable[P, R]) -> Callable[P, R]`). It is advanced; `Callable[..., Any]` is fine for this course.

## 10. `functools.lru_cache` and `cache`

### 10.1 The slow Fibonacci

The Fibonacci numbers are 0, 1, 1, 2, 3, 5, 8, 13, ...: each is the sum of the two before. The recursive definition is short and beautiful, and terribly slow. Let us count the calls with the `count_calls` decorator from section 8.2.

```python
import functools

def count_calls(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        wrapper.calls += 1
        return func(*args, **kwargs)
    wrapper.calls = 0
    return wrapper

@count_calls
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

for n in [10, 20, 25]:
    fib.calls = 0
    print(f"fib({n}) = {fib(n)}, calls: {fib.calls}")
```

```text
$ python fib1.py
fib(10) = 55, calls: 177
fib(20) = 6765, calls: 21891
fib(25) = 75025, calls: 242785
```

Notice that the recursive calls inside `fib` go through the name `fib`, which is now the wrapper, so they are counted too. Almost 250,000 calls for `fib(25)`! The reason: `fib(25)` computes `fib(24)` and `fib(23)`, but `fib(24)` **also** computes `fib(23)`, and so on. The same small values are computed again and again. The number of calls grows about 1.6 times for each step of `n`.

### 10.2 `functools.lru_cache`

The cure is to **remember** each answer the first time: store results in a dict keyed by the argument, and look there before computing. This is called **memoisation** (from "memo", a note to yourself). You will write such a `memo` decorator yourself in the project (section 16.3). The standard library already has a ready, well-tested one:

```python
import functools

@functools.lru_cache(maxsize=None)
def fib(n):
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

print(fib(100))
print(fib.cache_info())
print(fib(100))
print(fib.cache_info())
fib.cache_clear()
print(fib.cache_info())
```

```text
$ python lru1.py
354224848179261915075
CacheInfo(hits=98, misses=101, maxsize=None, currsize=101)
354224848179261915075
CacheInfo(hits=99, misses=101, maxsize=None, currsize=101)
CacheInfo(hits=0, misses=0, maxsize=None, currsize=0)
```

`lru_cache` attaches tools to the wrapper (like our section 8.2):

- `cache_info()` reports **hits** (answers found in the cache), **misses** (answers that had to be computed), `maxsize` and `currsize` (how many results are stored).
- `cache_clear()` empties the cache.

In the first call there were 101 misses (each `fib(k)` computed once) and 98 hits (the second recursive call found its answer already stored). The second `fib(100)` was one more hit.

How much faster is it? A quick measurement:

```python
import functools
import time

def fib_slow(n):
    return n if n < 2 else fib_slow(n - 1) + fib_slow(n - 2)

@functools.lru_cache(maxsize=None)
def fib_fast(n):
    return n if n < 2 else fib_fast(n - 1) + fib_fast(n - 2)

for func in [fib_slow, fib_fast]:
    start = time.perf_counter()
    value = func(27)
    print(f"{func.__name__}(27) = {value} in {time.perf_counter() - start:.6f} s")
```

```text
$ python lru2.py
fib_slow(27) = 196418 in 0.014301 s
fib_fast(27) = 196418 in 0.000013 s
```

(Your timings will differ; the huge gap will not.)

### 10.3 `maxsize` and "least recently used"

A cache that only grows can eat all your memory if the function is called with millions of different arguments. `maxsize` sets a limit. When the cache is full and a new result arrives, the result that was **least recently used** (LRU) is thrown out. That is where the name comes from.

```python
import functools

@functools.lru_cache(maxsize=2)
def slow_square(n):
    print(f"  computing {n}")
    return n * n

for n in [1, 2, 1, 3, 2, 1]:
    print(f"slow_square({n}) = {slow_square(n)}")
print(slow_square.cache_info())
```

```text
$ python lru3.py
  computing 1
slow_square(1) = 1
  computing 2
slow_square(2) = 4
slow_square(1) = 1
  computing 3
slow_square(3) = 9
  computing 2
slow_square(2) = 4
  computing 1
slow_square(1) = 1
CacheInfo(hits=1, misses=5, maxsize=2, currsize=2)
```

Trace it with a cache of two places:

```text
call   cache before   what happens                         cache after (oldest first)
1      []             miss, compute 1                      [1]
2      [1]            miss, compute 2                      [1, 2]
1      [1, 2]         hit                                  [2, 1]   (1 is now the most recent)
3      [2, 1]         miss, compute 3, cache full: drop 2  [1, 3]
2      [1, 3]         miss, compute 2, drop 1              [3, 2]
1      [3, 2]         miss, compute 1, drop 3              [2, 1]
```

`@functools.lru_cache` without brackets (or `lru_cache()`) uses `maxsize=128`. `maxsize=None` means "no limit".

### 10.4 `functools.cache`

Since Python 3.9, `functools.cache` is a short name for `lru_cache(maxsize=None)`: unlimited and a little faster. It is used without brackets:

```python
import functools

@functools.cache
def ways_to_climb(steps):
    """Ways to climb `steps` stairs taking 1 or 2 steps at a time."""
    if steps <= 1:
        return 1
    return ways_to_climb(steps - 1) + ways_to_climb(steps - 2)

print(ways_to_climb(50))
print(ways_to_climb.cache_info())
print(ways_to_climb.__doc__)
```

```text
$ python cache1.py
20365011074
CacheInfo(hits=48, misses=51, maxsize=None, currsize=51)
Ways to climb `steps` stairs taking 1 or 2 steps at a time.
```

`lru_cache` and `cache` use `functools.wraps` inside, so the docstring survives.

### 10.5 Trap: arguments must be hashable

The cache is a dict, and the arguments are the key. Dict keys must be **hashable** (unchangeable types: numbers, strings, tuples of those). A list is not hashable:

```python
import functools

@functools.cache
def total(prices):
    return sum(prices)

print(total((10, 20, 30)))
print(total([10, 20, 30]))
```

```text
$ python hash1.py
60
Traceback (most recent call last):
  File "/home/you/project/hash1.py", line 8, in <module>
    print(total([10, 20, 30]))
          ~~~~~^^^^^^^^^^^^^^
TypeError: unhashable type: 'list'
```

The tuple works; the list fails before the function even runs. Why must it be so? If you could cache with a list as key and then change the list, the stored answer would belong to values that no longer exist. Fix: pass a tuple (`total(tuple(my_list))`), or convert inside a small un-cached front function.

### 10.6 When NOT to cache

A cache returns the **old answer** for the same arguments. That is only correct for **pure functions**: functions whose result depends only on their arguments, and which do nothing else. Do not cache:

- functions that depend on the time, on random numbers, or on data that changes (a price list, a file, user input);
- functions whose job is a **side effect** (printing, saving, sending): with a cache, the second call does nothing;
- functions that return a **mutable** object, if the caller might change it. Everybody gets the **same** object:

```python
import functools

@functools.cache
def default_settings():
    return {"theme": "light", "size": 12}

mine = default_settings()
mine["theme"] = "dark"           # I change MY copy... or do I?
print(default_settings())        # somebody else asks for the defaults
```

```text
$ python cache2.py
{'theme': 'dark', 'size': 12}
```

There was never a copy. The cache handed out one dict, and changing it changed the "defaults" for everybody. Return a tuple, or let the caller make a copy.

A last mention: for **classes** (core.14) there is `functools.cached_property`, which computes an attribute once and stores it on the object. You will meet it with classes.

## 11. `functools.partial`

### 11.1 Fixing some arguments in advance

Often you call a function again and again with one argument always the same. `int(text, base=2)` reads a binary number; if your program reads many binary numbers, you write `base=2` every time. `functools.partial` makes a **new function** with some arguments already filled in:

```python
import functools

from_binary = functools.partial(int, base=2)
print(from_binary("1010"), from_binary("1111"))

def power(base, exponent):
    return base ** exponent

square = functools.partial(power, exponent=2)
cube = functools.partial(power, exponent=3)
two_to_the = functools.partial(power, 2)       # fills the FIRST positional argument

print(square(5), cube(2), two_to_the(10))
print(square)
print(square.func.__name__, square.args, square.keywords)
```

```text
$ python part1.py
10 15
25 8 1024
functools.partial(<function power at 0x707a9b6a3110>, exponent=2)
power () {'exponent': 2}
```

`partial(func, *some_args, **some_kwargs)` returns an object that, when called with more arguments, calls `func(*some_args, *more_args, **some_kwargs, **more_kwargs)`. Positional arguments you fix go **first**. It remembers `func`, `args` and `keywords` as attributes.

You could write the same with a closure (`def square(b): return power(b, 2)`) or a `lambda`. `partial` is shorter, says clearly "this is `power` with `exponent=2`", and you can see its settings when you print it.

### 11.2 `partial` with higher-order functions

`partial` shines when a higher-order function (like `map`, `sorted` or a callback) wants a function with **fewer** arguments than yours has:

```python
import functools

def add_tax(price, rate):
    return round(price * (1 + rate), 2)

prices = [100, 250, 80]
print(list(map(functools.partial(add_tax, rate=0.18), prices)))

log_error = functools.partial(print, "[ERROR]", sep=" | ")
log_error("disk full", "retrying")
```

```text
$ python part2.py
[118.0, 295.0, 94.4]
[ERROR] | disk full | retrying
```

## 12. `functools.reduce`

### 12.1 Folding a sequence into one value

`reduce(func, items)` combines the items **two at a time** from left to right: first `func(item0, item1)`, then `func(that_result, item2)`, and so on, until one value is left. It "folds" a list into a single value.

```python
import functools

def show_add(a, b):
    print(f"  {a} + {b} = {a + b}")
    return a + b

print(functools.reduce(show_add, [3, 5, 2, 10]))
```

```text
$ python red1.py
  3 + 5 = 8
  8 + 2 = 10
  10 + 10 = 20
20
```

So `reduce(f, [a, b, c, d])` is `f(f(f(a, b), c), d)`. You can give a **start value** as a third argument. It is placed before the first item, and it is also what you get for an empty list:

```python
import functools

print(functools.reduce(lambda acc, x: acc * x, [2, 3, 4], 1))
print(functools.reduce(lambda acc, x: acc * x, [], 1))
try:
    functools.reduce(lambda acc, x: acc * x, [])
except TypeError as e:
    print("TypeError:", e)
```

```text
$ python red2.py
24
1
TypeError: reduce() of empty iterable with no initial value
```

Without a start value, an empty list is an error. **Always give a start value** unless you know the list is never empty.

### 12.2 When to use `reduce` (rarely)

Most common reductions already have a clear built-in: `sum`, `max`, `min`, `math.prod`, `any`, `all`, `"".join`. Use those. `reduce` is good when you combine things that have no built-in, for example merging several dicts, or composing a list of functions into one:

```python
import functools

configs = [{"size": 10}, {"color": "red"}, {"size": 12, "bold": True}]
merged = functools.reduce(lambda acc, d: acc | d, configs, {})   # | merges two dicts
print(merged)

def compose(*funcs):
    """compose(f, g, h)(x) == f(g(h(x)))"""
    return functools.reduce(lambda f, g: lambda x: f(g(x)), funcs)

clean = compose(str.title, str.strip, str.lower)
print(repr(clean("   hELLO wORLD  ")))
```

```text
$ python red3.py
{'size': 12, 'color': 'red', 'bold': True}
'Hello World'
```

The `compose` line is clever, and that is the danger: a reader needs a minute to understand it. If a plain `for` loop with an accumulator is clearer, write the loop. Guido van Rossum, who created Python, moved `reduce` out of the built-ins into `functools` for exactly this reason.

### 12.3 Predict the output

```python
import functools

words = ["to", "be", "or", "not"]
print(functools.reduce(lambda acc, w: acc + w[0], words, ""))
print(functools.reduce(lambda a, b: a if len(a) >= len(b) else b, words))
print(functools.reduce(lambda acc, x: acc * 10 + x, [4, 0, 7], 0))
```

<details><summary>Answer</summary>

```text
$ python try10.py
tbon
not
407
```

1. Starting from `""`, add the first letter of each word: `"t"`, `"tb"`, `"tbo"`, `"tbon"`.
2. Keep the longer of each pair, the first one on a tie: `"to"` vs `"be"` keeps `"to"`, vs `"or"` keeps `"to"`, vs `"not"` gives `"not"`.
3. Digits to a number: `0*10+4 = 4`, `4*10+0 = 40`, `40*10+7 = 407`.

</details>

## 13. `functools.singledispatch`

### 13.1 One function, different behaviour per type

Suppose you want a `describe(x)` function that works differently for ints, lists and dicts. The usual way is an `if/elif` chain on the type:

```text
def describe(x):
    if isinstance(x, bool): ...
    elif isinstance(x, int): ...
    elif isinstance(x, list): ...
    else: ...
```

Every time you support a new type, you edit this one function, and it grows forever. `functools.singledispatch` lets you write **one small function per type** instead, and picks the right one by looking at the **type of the first argument**.

```python
import functools

@functools.singledispatch
def describe(x):
    return f"something else: {x!r}"

@describe.register
def _(x: int):
    return f"an int, {'even' if x % 2 == 0 else 'odd'}"

@describe.register
def _(x: list):
    return f"a list of {len(x)} items: " + ", ".join(describe(item) for item in x)

@describe.register
def _(x: dict):
    return f"a dict with keys {sorted(x)}"

print(describe(7))
print(describe([2, "hi"]))
print(describe({"b": 1, "a": 2}))
print(describe(3.5))
```

```text
$ python sd1.py
an int, odd
a list of 2 items: an int, even, something else: 'hi'
a dict with keys ['a', 'b']
something else: 3.5
```

How it works:

- `@functools.singledispatch` turns `describe` into a **generic function**. The body you write there is the **fallback** for types nobody registered.
- `@describe.register` adds an **implementation** for one type. It reads the type from the **type hint** of the first parameter (`x: int`).
- The implementations are usually named `_`: we never call them by name, only through `describe`. (Reusing the name `_` is fine.)
- Only the **first** argument decides. Other arguments are passed along.

Notice the list version calls `describe` again for each item, so each item is described by its own type.

### 13.2 Subclasses, and the `bool` surprise

`singledispatch` also matches **subtypes**. In Python `bool` is a special kind of `int` (`True == 1`), so a `bool` uses the `int` version unless you register `bool` itself:

```python
import functools

@functools.singledispatch
def show(x):
    return "other"

@show.register
def _(x: int):
    return "int"

print(show(True))

@show.register
def _(x: bool):
    return "bool"

print(show(True), show(5))
print(list(show.registry))
```

```text
$ python sd2.py
int
bool int
[<class 'object'>, <class 'int'>, <class 'bool'>]
```

`show.registry` is a dict from type to implementation. The most specific registered type wins. (Classes and subclasses are explained properly in core.14.)

## 14. The `operator` module

### 14.1 Operators as functions

`+`, `*`, `<` and the other operators are not functions, so you cannot pass them to `reduce`, `map` or `sorted`. You could write `lambda a, b: a + b` each time, but the standard `operator` module already has a function for every operator:

```python
import functools
import operator

print(operator.add(2, 3), operator.mul(4, 5), operator.neg(7))
print(operator.truediv(7, 2), operator.floordiv(7, 2), operator.mod(7, 2))
print(operator.lt(1, 2), operator.eq("a", "b"), operator.contains([1, 2], 2))
print(functools.reduce(operator.mul, [1, 2, 3, 4, 5], 1))
print(list(map(operator.add, [1, 2, 3], [10, 20, 30])))
```

```text
$ python op1.py
5 20 -7
3.5 3 1
True False True
120
[11, 22, 33]
```

`map` with two lists calls the function with one item from each: `add(1, 10)`, `add(2, 20)`, ... The `operator` versions are slightly faster than a `lambda` and, once you know them, easier to read.

### 14.2 `itemgetter`: pick by index or key

`operator.itemgetter(k)` builds a function that does `x[k]`. With several keys, it returns a tuple. This is perfect for `key=` in `sorted`, `min` and `max`:

```python
import operator

marks = [("Asha", 82, "B"), ("Ravi", 91, "A"), ("Meera", 82, "A")]

by_mark = operator.itemgetter(1)
print(by_mark(marks[0]))
print(sorted(marks, key=by_mark, reverse=True))
print(sorted(marks, key=operator.itemgetter(2, 0)))      # section, then name

people = [{"name": "Zoya", "age": 21}, {"name": "Arjun", "age": 19}]
print(min(people, key=operator.itemgetter("age"))["name"])
print(list(map(operator.itemgetter("name"), people)))
```

```text
$ python op2.py
82
[('Ravi', 91, 'A'), ('Asha', 82, 'B'), ('Meera', 82, 'A')]
[('Meera', 82, 'A'), ('Ravi', 91, 'A'), ('Asha', 82, 'B')]
Arjun
['Zoya', 'Arjun']
```

`itemgetter(1)` is the same as `lambda row: row[1]`, and `itemgetter(2, 0)` is `lambda row: (row[2], row[0])`. Sorting by a tuple sorts by the first part, and uses the second part only to break ties.

`operator.attrgetter("name")` is the same idea for **attributes** (`x.name`). You will use it with objects in core.14.

### 14.3 `methodcaller`: call a method by name

`operator.methodcaller("strip")` builds a function that calls `x.strip()` on whatever it receives. Extra arguments are passed to the method:

```python
import operator

raw = ["  apple ", "BANANA  ", " cherry"]
print(list(map(operator.methodcaller("strip"), raw)))

split_comma = operator.methodcaller("split", ",")
print(split_comma("a,b,c"))
print(sorted(["b.txt", "A.TXT", "c.Txt"], key=operator.methodcaller("lower")))
```

```text
$ python op3.py
['apple', 'BANANA', 'cherry']
['a', 'b', 'c']
['A.TXT', 'b.txt', 'c.Txt']
```

For a method with no arguments, `str.strip` (the method taken from the class) also works: `map(str.strip, raw)`. But `str.strip` works only for strings, while `methodcaller("strip")` works for any object with a `strip` method.

### 14.4 Predict the output

```python
import operator

rows = [("pen", 3, 10.0), ("ink", 1, 45.5), ("pad", 3, 25.0)]
print(max(rows, key=operator.itemgetter(2))[0])
print([name for name, *_ in sorted(rows, key=operator.itemgetter(1, 0))])
print(list(map(operator.mul, [2, 3], [5, 7])))
```

<details><summary>Answer</summary>

```text
$ python try11.py
ink
['ink', 'pad', 'pen']
[10, 21]
```

1. The row with the biggest price (index 2) is `("ink", 1, 45.5)`; index 0 is `"ink"`.
2. Sort by quantity (index 1), then name: `ink` (1), then `pad` and `pen` (both 3, alphabetical).
3. `2*5` and `3*7`.

</details>


## 15. Functional style in Python

### 15.1 Pure functions

You have now seen many tools that take and return functions. Together they form a **functional style** of programming. Its central idea is the **pure function**:

- its result depends **only on its arguments** (same input, same output, every time);
- it has **no side effects**: it does not print, change a global variable, change its arguments, or touch files.

```python
cart = [100, 250]


def add_item_impure(price):           # changes the outside world
    cart.append(price)
    return sum(cart)


def add_item_pure(items, price):      # builds and returns a new list
    return items + [price]


print(add_item_impure(50), add_item_impure(50))
new_cart = add_item_pure([100, 250], 50)
print(new_cart, add_item_pure([100, 250], 50) == new_cart)
```

```text
$ python fp1.py
400 450
[100, 250, 50] True
```

The impure version gives a **different answer** for the same argument, because it depends on hidden state. Pure functions are easy to test (no setup), safe to cache (section 10.6), and easy to reason about: you can understand them by reading only them. Real programs need side effects (printing, saving), so the good habit is: keep **most** functions pure, and do the side effects in a few clear places, like the `main` part of a script.

### 15.2 `map` and `filter` versus comprehensions

`map(f, items)` applies `f` to each item; `filter(pred, items)` keeps the items where `pred` is true. Both are lazy iterators (core.10). A comprehension does the same job:

```python
words = ["  Apple", "kiwi ", " fig", "banana "]

print(list(map(str.strip, words)))
print([w.strip() for w in words])

print(list(filter(lambda w: len(w.strip()) > 3, words)))
print([w for w in words if len(w.strip()) > 3])

print(list(map(lambda w: w.strip().upper(), filter(lambda w: "a" in w, words))))
print([w.strip().upper() for w in words if "a" in w])
```

```text
$ python fp2.py
['Apple', 'kiwi', 'fig', 'banana']
['Apple', 'kiwi', 'fig', 'banana']
['  Apple', 'kiwi ', 'banana ']
['  Apple', 'kiwi ', 'banana ']
['BANANA']
['BANANA']
```

Same results. Which is better?

- When you already have a **named function**, `map(str.strip, words)` is short and clear.
- When you would need a `lambda`, the comprehension is usually clearer: `[w.strip() for w in words]` reads like English.
- When you combine mapping and filtering, the comprehension wins clearly. Compare the last two lines.

### 15.3 When not to be clever

Functional tools are good servants and bad masters. Signs you went too far:

- a `lambda` inside a `map` inside a `filter` inside a `reduce`;
- a `reduce` where `sum`, `max`, `"".join` or a short loop would do (section 12.2);
- a decorator for something that happens in **one** place only (just write the code there);
- a stack of five decorators whose order nobody can explain.

The test is always the same: **can a classmate read it in one pass?** Python's own style guide says: "Readability counts." Use decorators for cross-cutting concerns that repeat; use `partial`, `itemgetter` and `methodcaller` when they make a `key=` or `map` call clearer; use `lru_cache` for expensive pure functions. Write plain loops and comprehensions for everything else.

## 16. Project: a decorator toolkit

We now build the module project: a small toolkit of five decorators (**timer**, **retry**, **memo**, **rate limiter**, **logger**), and stack them on one function. Every block below belongs in **one file**, `toolkit.py`, in this order. Two design rules run through all of them:

1. **Every decorator uses `functools.wraps`**, so stacked decorators still see the real function name.
2. **Time is injectable.** Any decorator that reads a clock or sleeps takes `clock=` / `sleep=` settings, with the real `time` functions as defaults. Tests and demos pass fake ones, so they run instantly and print the same numbers every time.

### 16.1 `timer` and `logger`

```python
import functools
import time


def timer(clock=time.perf_counter, report=print):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = clock()
            try:
                return func(*args, **kwargs)
            finally:
                report(f"[timer] {func.__name__} took {clock() - start:.3f} s")
        return wrapper
    return decorator


def logger(prefix="LOG", report=print):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            shown = [repr(a) for a in args] + [f"{k}={v!r}" for k, v in kwargs.items()]
            report(f"[{prefix}] call {func.__name__}({', '.join(shown)})")
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                report(f"[{prefix}] {func.__name__} raised {type(e).__name__}: {e}")
                raise
            report(f"[{prefix}] {func.__name__} returned {result!r}")
            return result
        return wrapper
    return decorator
```


The timer uses `try/finally`, so it reports the time **even when the function fails**. `report=print` lets a test collect messages into a list (`report=messages.append`) instead of printing.

### 16.2 `retry` with backoff

After each failure, wait, and make the next wait longer (`delay`, then `delay * backoff`, ...). This is called **exponential backoff**: a busy server gets more and more breathing room.

```python
def retry(times=3, delay=1.0, backoff=2.0, exceptions=(Exception,),
          sleep=time.sleep, report=print):
    if times < 1:
        raise ValueError("times must be at least 1")

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            wait = delay
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    if attempt == times:
                        raise
                    report(f"[retry] {func.__name__} attempt {attempt} failed: {e}; "
                           f"waiting {wait} s")
                    sleep(wait)
                    wait *= backoff
        return wrapper
    return decorator
```


The check `times < 1` happens in the outer layer, so a wrong setting fails **at decoration time**, when the program starts, not hours later on the first call.

### 16.3 `memo` and `rate_limit`

```python
def memo(func):
    results = {}

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        key = (args, tuple(sorted(kwargs.items())))
        if key not in results:
            results[key] = func(*args, **kwargs)
        return results[key]

    wrapper.cache = results
    wrapper.cache_clear = results.clear
    return wrapper


def rate_limit(calls, period, clock=time.monotonic):
    def decorator(func):
        recent = []                      # times of the recent calls

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            now = clock()
            recent[:] = [t for t in recent if now - t < period]
            if len(recent) >= calls:
                raise RuntimeError(f"{func.__name__}: more than {calls} calls in {period} s")
            recent.append(now)
            return func(*args, **kwargs)
        return wrapper
    return decorator
```


- `memo` builds a hashable key from the positional arguments and the **sorted** keyword arguments, so `f(1, a=2, b=3)` and `f(1, b=3, a=2)` share one key. Like `lru_cache`, it fails with `TypeError` for list arguments. It is a plain decorator (no settings), so it is used as `@memo` without brackets.
- `rate_limit` keeps the times of recent calls. On each call it forgets the times older than `period`, and refuses the call if `calls` calls are still "recent". `recent[:] = ...` replaces the list's **contents**, so we do not need `nonlocal`. `time.monotonic` is a clock that never jumps backwards (unlike the wall clock, which can change when the computer syncs its time).

### 16.4 A fake clock for demos and tests

A fake clock is two closures sharing one variable: `clock()` reads it, `sleep(s)` moves it forward. No time really passes.

```python
def make_fake_time():
    now = 0.0

    def clock():
        return now

    def sleep(seconds):
        nonlocal now
        now += seconds

    return clock, sleep
```


### 16.5 Stacking the toolkit

Now a function that fails twice and then succeeds, with logger, timer and retry stacked:

```python
clock, sleep = make_fake_time()
attempts = 0


@logger(prefix="API")
@timer(clock=clock)
@retry(times=3, delay=0.5, backoff=2, exceptions=(ConnectionError,), sleep=sleep)
def get_rate(currency):
    global attempts
    attempts += 1
    if attempts <= 2:
        raise ConnectionError("timeout")
    return {"USD": 83.2, "EUR": 90.1}[currency]


print("result:", get_rate("USD"))
print("name:", get_rate.__name__)
```

```text
$ python demo1.py
[API] call get_rate('USD')
[retry] get_rate attempt 1 failed: timeout; waiting 0.5 s
[retry] get_rate attempt 2 failed: timeout; waiting 1.0 s
[timer] get_rate took 1.500 s
[API] get_rate returned 83.2
result: 83.2
name: get_rate
```

Read this output with section 7 in mind:

- The **logger** is on top, so the call enters it first and it prints the first line and the last line. It sees one call and one result: the retries are hidden inside it.
- The **timer** is in the middle. It measures everything below it: both waits, `0.5 + 1.0 = 1.5` fake seconds.
- The **retry** is at the bottom, right around the function, so it repeats only the real work.
- The name is still `get_rate`, thanks to `wraps` in every layer.

Now the rate limiter and the memo, also with the fake clock:

```python
clock, sleep = make_fake_time()
work_done = []


@memo
@rate_limit(calls=2, period=1.0, clock=clock)
def lookup(code):
    work_done.append(code)
    return code.upper()


for code in ["in", "us", "in", "fr"]:
    try:
        print(code, "->", lookup(code))
    except RuntimeError as e:
        print(code, "-> refused:", e)

sleep(1.0)
print("fr ->", lookup("fr"), "(after waiting)")
print("real work:", work_done)
```

```text
$ python demo2.py
in -> IN
us -> US
in -> IN
fr -> refused: lookup: more than 2 calls in 1.0 s
fr -> FR (after waiting)
real work: ['in', 'us', 'fr']
```

`memo` is on top, so the second `"in"` is answered from the cache and never reaches the rate limiter: cache hits are free. `"fr"` is the third **real** call within one second, so it is refused. After one (fake) second, the old calls are forgotten and `"fr"` goes through. If you swapped the order (`@rate_limit` on top), every lookup, even a cached one, would count against the limit.

**Extend it yourself.** Ideas to practise: make `timer` store timings in a `wrapper.timings` list; give `retry` a `max_delay`; give `memo` a `maxsize` like `lru_cache`; write pytest tests that pass `report=messages.append` and a fake `sleep`, and check the exact messages.

## 17. Common traps

Most of these were shown earlier; the section number tells you where.

1. **Forgetting `return` in the wrapper** (4.3). The decorated function silently returns `None`. Always `return func(*args, **kwargs)` or `return result`.
2. **Returning `wrapper()` instead of `wrapper`** in the decorator. With brackets, you call the wrapper at decoration time and bind the name to its **result**. The function runs once while the program starts, and later `my_func()` fails with "object is not callable".
3. **`@deco` versus `@deco()`** (6.4). A decorator with settings needs brackets, even with no settings passed. A plain decorator must not have them. Check the outermost `def`: does it take `func` or settings?
4. **Missing `functools.wraps`** (5.1). Names become `wrapper`, docs disappear, registries and logs get confused, and stacked decorators report the wrong name.
5. **A wrapper that only takes fixed arguments** (4.1). Use `*args, **kwargs` unless you have a reason not to.
6. **State in the wrong place** (8.3). State created **inside** the decorator belongs to one decorated function; state created **outside** is shared by all of them.
7. **Caching the wrong thing** (10.5, 10.6). `lru_cache` needs hashable arguments (tuples, not lists). Never cache impure functions, and be careful with cached mutable results: every caller gets the same object.
8. **Work at decoration time** (3.4, 7.7). Code in the decorator body runs once, when the function is **defined**, often while the program starts. Slow work or side effects there (connecting to a server, printing) happen even if the function is never called. Put per-call work inside the wrapper.
9. **Wrong stacking order** (7.5). The top decorator is the outermost layer: it sees everything below as one black box. Decide what each layer should see: should the timer include retries? Should the cache skip the rate limiter?
10. **Hiding errors**. A wrapper with `except Exception: pass` (or `return None`) swallows real bugs. Catch only what you handle, and use a bare `raise` to pass the error on.

## 18. Summary

- **Functions are objects**: you can store them, pass them in, and return them. `f` is the function; `f()` calls it. Closures let an inner function remember the outer function's variables; `nonlocal` lets it change them.
- A **decorator** is a function that takes a function and returns a replacement, usually a **wrapper** that adds behaviour before and after the call. `@deco` above `def f` means exactly `f = deco(f)`.
- The **wrapper template**: `def wrapper(*args, **kwargs): ...; result = func(*args, **kwargs); ...; return result`, and the decorator returns `wrapper` (no brackets).
- **Decoration time vs call time**: the decorator body runs once when the function is defined; the wrapper runs on every call.
- **`functools.wraps(func)`** on the wrapper copies `__name__`, `__doc__`, `__qualname__`, `__module__`, `__annotations__` and `__dict__`, and adds `__wrapped__` (the original). Use it every time.
- **Decorators with arguments** have three layers: `factory(settings) -> decorator(func) -> wrapper(*args, **kwargs)`. `@f(x)` means `func = f(x)(func)`. Brackets are required.
- **Stacking**: `@a @b def f` means `f = a(b(f))`.
  - the `@` expressions are evaluated **top-down**;
  - decorators are **applied bottom-up** (nearest the `def` first);
  - a call **enters top-down** and **exits bottom-up**, like the layers of an onion.
- **State** lives in the decorator's closure (`nonlocal`) or as attributes on the wrapper (`wrapper.calls`), one copy per decorated function.
- Patterns: argument checking, registries (return `func` unchanged), retry with injectable `sleep`, rate limiting with an injectable clock. Type a decorator loosely with `Callable[..., Any]`.
- **functools**: `lru_cache(maxsize=...)` and `cache` memoise pure functions (`cache_info`, `cache_clear`; arguments must be hashable); `partial` fixes some arguments; `reduce` folds a sequence (give a start value); `singledispatch` picks an implementation by the type of the first argument; `cached_property` waits for classes.
- **operator**: `add`, `mul`, `lt`, ... are operators as functions; `itemgetter` and `methodcaller` (and later `attrgetter`) build small key functions for `sorted`, `max` and `map`.
- **Functional style**: prefer pure functions; use `map`/`filter` with named functions, comprehensions otherwise; choose readability over cleverness.

When you can write a decorator with settings that keeps the wrapped function's name and docstring, and you can explain, with a printed trace, why a stack of decorators is applied bottom-up but entered top-down, you have met the outcomes of this module. The problems that follow practise each part, from tracing a stack by hand to building your own toolkit decorators.

### What comes next

In **core.12, Files and I/O**, your programs finally read and write real files. The pipelines of core.10 and the tools of this chapter come along: a `@timer` will tell you how long a big file takes to parse, and `lru_cache` will save you from reading the same file twice. In **core.14** you meet classes, and with them the class-based decorators and `@property` that this chapter only mentioned.
