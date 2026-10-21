# Chapter 6: Functions

So far every program you have written runs from the top to the bottom, once. If the same steps are needed in three places, you have copied them three times. If one copy has a bug, you fix it in one place and forget the other two. If the program grows past a hundred lines, nobody, including you, can hold it in their head.

A **function** solves all three problems. It is a named block of code that you write once and **call** as often as you like. You give it some input values, it does its work, and it hands back a result. Once a function works, you can stop thinking about *how* it works and think only about *what* it does. That idea, hiding the how behind a name, is called **abstraction**, and it is the single most important tool for building programs bigger than a page.

You have been calling functions since the first chapter: `print`, `len`, `input`, `sorted`, `max`. In this chapter you learn to **write** them. That sounds like a small step, but it opens a large set of questions that this chapter answers carefully:

- How do the values you pass in get matched to the function's parameters?
- If you pass a list to a function and the function changes it, does *your* list change?
- Which names can a function see, and why does adding one line sometimes make a working function crash with `UnboundLocalError`?
- What does it mean that functions are **objects**, and why is that so useful?
- What is a **closure**, and why do functions created in a loop sometimes all behave like the last one?
- How can a function call **itself**, and what stops it from doing that forever?

Each of these has a short answer that is easy to memorise and wrong in some cases. We aim for the full answer, with a picture of what Python actually does in memory. The "Under the hood" subsections show the real machinery: call frames, how CPython binds arguments to parameters, where default values are stored, the cell objects behind closures, and the call stack that recursion grows.

A note on how examples are shown. A block of code is followed by the exact output it produces when run as a script with Python 3.14. When an example ends in an error, the traceback is shown with the file name shortened to `example.py`. Answer every "Predict the output" question on paper before you open the answer.

## Table of contents

1. [Why functions exist](#1-why-functions-exist)
2. [Defining and calling functions](#2-defining-and-calling-functions)
3. [Return values](#3-return-values)
4. [Docstrings](#4-docstrings)
5. [Under the hood: function objects and call frames](#5-under-the-hood-function-objects-and-call-frames)
6. [Positional, keyword and default arguments](#6-positional-keyword-and-default-arguments)
7. [Under the hood: how CPython binds arguments](#7-under-the-hood-how-cpython-binds-arguments)
8. [The mutable default argument trap](#8-the-mutable-default-argument-trap)
9. [*args and **kwargs](#9-args-and-kwargs)
10. [Positional-only and keyword-only parameters](#10-positional-only-and-keyword-only-parameters)
11. [Argument passing through object references](#11-argument-passing-through-object-references)
12. [Mutation versus rebinding inside a function](#12-mutation-versus-rebinding-inside-a-function)
13. [Scope and the LEGB rule](#13-scope-and-the-legb-rule)
14. [global and nonlocal](#14-global-and-nonlocal)
15. [Functions as first-class objects](#15-functions-as-first-class-objects)
16. [lambda](#16-lambda)
17. [map, filter and functools.reduce](#17-map-filter-and-functoolsreduce)
18. [Closures](#18-closures)
19. [Late binding in closures](#19-late-binding-in-closures)
20. [Recursion](#20-recursion)
21. [Under the hood: the call stack and the recursion limit](#21-under-the-hood-the-call-stack-and-the-recursion-limit)
22. [Designing good functions](#22-designing-good-functions)
23. [Summary](#summary)
24. [Learning outcomes](#learning-outcomes)
25. [Module project](#module-project)
26. [Further reading](#further-reading)

---

## 1. Why functions exist

Here is a small program without functions. It reports the average of three lists of marks.

```python
maths = [72, 85, 64, 90]
physics = [55, 61, 70]
english = [88, 92]

total = 0
for m in maths:
    total += m
print("maths", round(total / len(maths), 1))

total = 0
for m in physics:
    total += m
print("physics", round(total / len(physics), 1))

total = 0
for m in english:
    total += m
print("english", round(total / len(english), 1))
```

Output:

```text
maths 77.8
physics 62.0
english 90.0
```

It works, but look at what is wrong with it.

1. **Repetition.** The same four lines appear three times. Adding a fourth subject means copying them again.
2. **Fragile copies.** If you find a bug, say, it crashes for an empty list, you must fix it in three places. Miss one and the bug lives on.
3. **No name for the idea.** The reader has to read four lines to discover "this computes an average". The idea has no name.

Now the same program with a function:

```python
def average(marks):
    total = 0
    for m in marks:
        total += m
    return round(total / len(marks), 1)

print("maths", average([72, 85, 64, 90]))
print("physics", average([55, 61, 70]))
print("english", average([88, 92]))
```

Output:

```text
maths 77.8
physics 62.0
english 90.0
```

The steps are written once, under the name `average`. Each line at the bottom says *what* it wants, not *how* to get it. A fix inside `average` fixes every use at once.

Functions give you four things:

- **Reuse**: write once, call many times.
- **Naming**: a good function name is documentation. `average(marks)` explains itself.
- **Isolation**: the names a function uses inside (`total`, `m`) are its own. They cannot collide with names elsewhere in the program. Section 13 explains exactly how.
- **Testing**: a function that takes input and returns output can be checked on its own. From this chapter on, the tests for your problems call your functions directly, the same way professional test suites do.

The rest of the chapter is about using these four things well.

---

## 2. Defining and calling functions

### The def statement

You create a function with a `def` statement:

```python
def greet(name):
    print("Hello,", name)

greet("Asha")
greet("Ravi")
```

Output:

```text
Hello, Asha
Hello, Ravi
```

The parts of a definition:

```
def greet(name):          <- header: the keyword def, the function's name,
    print("Hello,", name)    parameters in parentheses, and a colon
                          <- body: the indented block that runs on each call
```

- `def` is a keyword. It means "define a function".
- `greet` is the function's **name**. The same rules apply as for variable names: letters, digits and underscores, not starting with a digit. By convention function names are lowercase with underscores, like `average_marks`, and usually start with a verb when they *do* something (`print_report`, `load_scores`) or name the result when they *compute* something (`average`, `area`).
- `name` is a **parameter**: a name that will refer to the value given in a call.
- The **body** is indented, just like the body of an `if` or a `for`.

### Parameters and arguments

Two words that beginners mix up:

- A **parameter** is the name in the definition: `name` in `def greet(name)`.
- An **argument** is the value you pass in a call: `"Asha"` in `greet("Asha")`.

When you call `greet("Asha")`, Python makes the parameter `name` refer to the argument `"Asha"`, then runs the body. When the body ends, the call is over and the program continues after the call.

A function can have zero parameters or many:

```python
def line():
    print("-" * 20)

def show_sum(a, b):
    print(a, "+", b, "=", a + b)

line()
show_sum(3, 4)
show_sum(10, -2)
line()
```

Output:

```text
--------------------
3 + 4 = 7
10 + -2 = 8
--------------------
```

Even with no parameters, the call needs its parentheses: `line()`. Writing just `line` does not call anything, as you will see in section 15.

### Defining is not running

`def` does **not** run the body. It only creates the function and stores it under its name. The body runs each time the function is **called**, and only then.

```python
def shout():
    print("THIS RUNS ONLY WHEN CALLED")

print("defined shout")
shout()
shout()
```

Output:

```text
defined shout
THIS RUNS ONLY WHEN CALLED
THIS RUNS ONLY WHEN CALLED
```

A consequence: a mistake inside a body is only discovered when the body runs. A function that is never called can contain a misspelled name and the program still runs fine. (A *syntax* error, such as a missing colon, is different: Python reads the whole file before running anything, so it is caught at once.)

### Define before you call

Python runs a file from top to bottom. A `def` statement is executed like any other statement: when Python reaches it, it creates the function. So the call must come **after** the `def` has run:

```python
greet("Asha")

def greet(name):
    print("Hello,", name)
```

Output:

```text
Traceback (most recent call last):
  File "example.py", line 1, in <module>
    greet("Asha")
    ^^^^^
NameError: name 'greet' is not defined
```

The name `greet` does not exist yet on line 1. But a function body may freely mention a function defined *later in the file*, because the body only runs when it is called, and by then every `def` has run:

```python
def main():
    helper()          # helper is defined below; fine

def helper():
    print("helper called")

main()                # by now both defs have run
```

Output:

```text
helper called
```

This is why many programs put all the `def`s first and a single call such as `main()` at the very bottom.

### An empty function: pass

A body cannot be empty. While you are planning, use `pass`, the statement that does nothing (core.04):

```python
def todo_later():
    pass

todo_later()
print("still fine")
```

Output:

```text
still fine
```

### Common misconceptions and edge cases

- "Defining a function runs it." No. `def` only creates it. Nothing happens until a call.
- "Parameters and arguments are the same thing." The parameter is the name in the definition; the argument is the value in the call.
- "I can call a function anywhere in the file." Only after its `def` has run, unless the call is itself inside another function's body that runs later.
- Forgetting the parentheses: `line` names the function, `line()` calls it. A line that says just `line` does nothing at all, silently.

---

## 3. Return values

### return sends a value back

`greet` *prints* something, but it does not give anything back to the caller. Most useful functions **compute** a value and hand it back with `return`:

```python
def square(x):
    return x * x

a = square(5)
b = square(a) + 1
print(a, b)
print(square(square(2)))
```

Output:

```text
25 626
16
```

`return x * x` does two things: it works out the value of `x * x`, and it **ends** the call immediately, sending that value back. The call expression `square(5)` then *is* that value, `25`, and can be used anywhere a value can: stored in a name, used in arithmetic, passed to another function.

### print versus return

This is the most common beginner confusion with functions, so it is worth a clear statement:

- `print` shows a value **to the human** on the screen. The program cannot use what was printed.
- `return` gives a value **to the code** that called the function. Nothing appears on the screen.

```python
def double_print(x):
    print(x * 2)

def double_return(x):
    return x * 2

a = double_print(4)
b = double_return(4)
print("a is", a)
print("b is", b)
```

Output:

```text
8
a is None
b is 8
```

`double_print(4)` printed `8` and then gave back `None`, so `a` is `None`. `double_return(4)` printed nothing and gave back `8`. A function that prints its answer is like a calculator that shows the result on its screen but will not let you copy it into the next sum. Almost always, a function should **return** its result and let the caller decide whether to print it.

### A function without return gives back None

If the body finishes without reaching a `return`, or reaches a bare `return` with no value, the call gives back `None`:

```python
def nothing():
    x = 1

def bare():
    return

print(nothing())
print(bare())
print(print("inside"))
```

Output:

```text
None
None
inside
None
```

The last line is a classic puzzle. The inner `print("inside")` prints `inside` and returns `None`. The outer `print` then prints that `None`. Recall from core.05 that methods which change a list, such as `append` and `sort`, also return `None` for the same reason: they *do* something rather than *compute* something.

### return ends the call: early return

The moment a `return` runs, the function stops. Anything after it in the body is skipped for that call. This lets you handle special cases first and leave early:

```python
def describe(n):
    if n < 0:
        return "negative"
    if n == 0:
        return "zero"
    if n % 2 == 0:
        return "positive even"
    return "positive odd"

for n in [-3, 0, 4, 7]:
    print(n, describe(n))
```

Output:

```text
-3 negative
0 zero
4 positive even
7 positive odd
```

Because each `return` leaves the function, the later `if`s do not need `elif`, and the final line needs no `else`: we only reach it if no earlier `return` ran. This style is called **guard clauses**: check the special cases at the top, return early, and keep the main logic un-indented at the bottom.

A `return` inside a loop ends the loop *and* the function. That makes searching very natural:

```python
def first_negative(numbers):
    for n in numbers:
        if n < 0:
            return n
    return None

print(first_negative([4, 7, -2, 9, -5]))
print(first_negative([1, 2, 3]))
```

Output:

```text
-2
None
```

Notice where the final `return None` is: **after** the loop, not inside it. If you put it in an `else` inside the loop, the function would give up after checking only the first number. That is one of the most common bugs in search functions.

### Returning several values

A function returns exactly one object. But that object can be a tuple, and the comma makes a tuple (core.05), so returning "several values" is easy:

```python
def min_max(numbers):
    return min(numbers), max(numbers)

result = min_max([4, 9, 1, 7])
print(result, type(result).__name__)
low, high = min_max([4, 9, 1, 7])
print(low, high)
```

Output:

```text
(1, 9) tuple
1 9
```

`return min(numbers), max(numbers)` builds the tuple `(1, 9)` and returns it. The caller can keep the tuple or unpack it straight into two names.

### Consistent return types

A function that sometimes returns a number and sometimes returns `None` forces every caller to check which one they got. Sometimes that is right ("not found" really is a different answer), but be deliberate about it, and say so in the docstring. A function that returns a list should return an **empty list** when there is nothing to return, not `None`, so callers can loop over the result without checking.

### Common misconceptions and edge cases

- "My function printed the answer, so it returned it." Printing is not returning. The caller receives `None`.
- "`return` and `print` can be swapped." Only `return` lets other code use the value.
- "A `return` inside a loop just ends the loop." It ends the whole function call.
- Putting the "not found" `return` inside the loop's `else` branch, so the search stops after one item.
- `return a, b` returns **one** tuple, not two separate things.
- Code after a `return` in the same block can never run. Python will not warn you; it is simply dead code.

---

## 4. Docstrings

A **docstring** is a string literal written as the very first statement in a function body. It describes what the function does, what it expects, and what it returns.

```python
def average(marks):
    """Return the mean of a non-empty list of numbers, rounded to 1 decimal place.

    marks: a list of int or float values. Must not be empty.
    """
    return round(sum(marks) / len(marks), 1)

print(average([72, 85, 64]))
print(average.__doc__.splitlines()[0])
```

Output:

```text
73.7
Return the mean of a non-empty list of numbers, rounded to 1 decimal place.
```

A docstring is not a comment. Comments (`#`) are thrown away when Python reads your file. A docstring is kept and stored on the function object, in the attribute `__doc__`. That is why tools can show it: `help(average)` in the interactive shell prints it, and editors show it when you hover over a call.

Conventions (from PEP 257, the docstring style guide):

- Use triple double quotes `"""` even for one line, so it is easy to extend later.
- The first line is a short summary that ends with a full stop. Write it as a command: "Return the mean...", not "Returns the mean..." or "This function returns...".
- If more is needed, leave one blank line after the summary, then describe the parameters, the return value, and anything surprising (what happens with an empty list, whether the argument is changed).

A good docstring describes the **contract**: what the caller must provide, and what they get back. It does not narrate the code line by line; the code already says that.

```python
def no_doc():
    return 1

def with_comment():
    # just a comment
    return 1

print(no_doc.__doc__)
print(with_comment.__doc__)
```

Output:

```text
None
None
```

A function without a docstring has `__doc__` equal to `None`. A comment does not count.

### Common misconceptions and edge cases

- "A docstring is just a fancy comment." It is a real string object stored on the function; comments are discarded.
- "Any string in the body is a docstring." Only a string that is the **first statement** of the body.
- "Docstrings should explain every line." They explain the contract (inputs, output, special cases). Explain tricky lines with comments.

---

## 5. Under the hood: function objects and call frames

To answer the hard questions later in this chapter, you need a clear picture of two things: what `def` creates, and what happens in memory during a call.

### def creates a function object

`def` is an executable statement, like an assignment. When Python runs it, it builds a **function object** and binds the function's name to it, exactly as `x = 5` binds `x` to an int object.

```python
def square(x):
    """Return x squared."""
    return x * x

print(type(square))
print(square.__name__)
print(square.__doc__)
print(square.__code__.co_varnames)
print(square.__defaults__)
```

Output:

```text
<class 'function'>
square
Return x squared.
('x',)
None
```

A function object carries, among other things:

| Attribute | What it holds |
|---|---|
| `__name__` | the name given in the `def` |
| `__doc__` | the docstring, or `None` |
| `__code__` | the **code object**: the compiled body, plus facts such as the parameter names and the local variable names |
| `__defaults__` | a tuple of default values for parameters, or `None` (section 7) |
| `__closure__` | the cells for variables from enclosing functions, or `None` (section 18) |
| `__globals__` | the module's global namespace, where the function looks up global names |

The **code object** is created once, when Python compiles your file. The **function object** is created each time the `def` statement runs. Usually that is once, but a `def` inside a loop or inside another function runs many times and makes a new function object each time, all sharing one code object. That detail is the key to closures.

### A call creates a frame

Every time you call a function, Python creates a fresh **frame** for that call. A frame is a small record that holds:

- the function's **local variables**, including its parameters,
- the position of the instruction currently running in the body,
- a link back to the **caller's** frame, so Python knows where to return.

When the call returns, its frame is thrown away, and with it every local variable. A second call gets a brand new frame with brand new locals. Nothing is remembered between calls (unless you deliberately keep it somewhere outside the frame, as later sections show).

```python
def count_up():
    n = 0
    n += 1
    return n

print(count_up(), count_up(), count_up())
```

Output:

```text
1 1 1
```

Each call starts with a new `n = 0`, so each returns `1`.

Frames are stacked on top of one another. If `main` calls `report`, which calls `average`, then while `average` runs there are three frames, plus one for the module itself:

```
            the call stack (newest on top)
          +--------------------------------+
          | average   marks=[...] total=..|   <- running now
          +--------------------------------+
          | report    name='maths'        |   waiting for average to return
          +--------------------------------+
          | main                          |   waiting for report to return
          +--------------------------------+
          | <module>  (your file)         |   waiting for main to return
          +--------------------------------+
```

When `average` returns, its frame is removed ("popped"), the value travels to `report`'s frame, and `report` continues from where it paused. This structure is the **call stack**. A traceback is simply a printout of the call stack at the moment of the error, oldest call at the top:

```python
def average(marks):
    return sum(marks) / len(marks)

def report(name, marks):
    print(name, average(marks))

def main():
    report("maths", [70, 80])
    report("art", [])

main()
```

Output:

```text
maths 75.0
Traceback (most recent call last):
  File "example.py", line 11, in <module>
    main()
    ~~~~^^
  File "example.py", line 9, in main
    report("art", [])
    ~~~~~~^^^^^^^^^^^
  File "example.py", line 5, in report
    print(name, average(marks))
                ~~~~~~~^^^^^^^
  File "example.py", line 2, in average
    return sum(marks) / len(marks)
           ~~~~~~~~~~~^~~~~~~~~~~~
ZeroDivisionError: division by zero
```

Read a traceback from the **bottom up**: the last line says what went wrong (`ZeroDivisionError`), the line above it says where (`average`, line 2), and each earlier pair shows who called whom to get there. Seeing the frames in a traceback is the fastest way to locate a bug.

### Local variables live in the frame

Because each call has its own frame, the names inside a function are **local** to that call. A local `total` in one function has nothing to do with a `total` in another function or at the top level of the file:

```python
total = 1000

def add_up(numbers):
    total = 0
    for n in numbers:
        total += n
    return total

print(add_up([1, 2, 3]))
print(total)
```

Output:

```text
6
1000
```

The function's `total` lived in its frame and disappeared when the call ended. The global `total` was never touched. Section 13 gives the full rules.

### Common misconceptions and edge cases

- "A function remembers its local variables between calls." Each call has a new frame; locals start fresh.
- "`def` is a declaration, like in C." It is a statement that runs and creates an object. A `def` inside an `if` creates the function only if that branch runs.
- "A traceback shows where the bug is." It shows where the error was **noticed**. The real mistake (here, passing an empty list) may be in a caller further up.

---

## 6. Positional, keyword and default arguments

### Positional arguments

The simplest way to pass arguments is by **position**: the first argument goes to the first parameter, the second to the second, and so on.

```python
def describe(name, age, city):
    return f"{name}, {age}, from {city}"

print(describe("Asha", 19, "Pune"))
print(describe(19, "Pune", "Asha"))
```

Output:

```text
Asha, 19, from Pune
19, Pune, from Asha
```

The second call is "valid" Python, but nonsense. Position is the only thing linking an argument to a parameter, so passing them in the wrong order silently gives wrong results. With three parameters of different types you might notice; with `transfer(100, 200)` you would not.

### Keyword arguments

You can also name the parameter in the call with `name=value`. This is a **keyword argument**:

```python
def describe(name, age, city):
    return f"{name}, {age}, from {city}"

print(describe(city="Pune", name="Asha", age=19))
print(describe("Asha", city="Pune", age=19))
```

Output:

```text
Asha, 19, from Pune
Asha, 19, from Pune
```

With keywords, order does not matter, and the call documents itself. You can mix the two styles, but **positional arguments must come first**. Once you start naming, every later argument must be named too:

```python
def describe(name, age, city):
    return f"{name}, {age}, from {city}"

print(describe(name="Asha", 19, "Pune"))
```

Output:

```text
  File "example.py", line 4
    print(describe(name="Asha", 19, "Pune"))
                                          ^
SyntaxError: positional argument follows keyword argument
```

This is a syntax error, so Python rejects the whole file before running a single line.

### Default values

A parameter can have a **default value**, written `param=value` in the definition. If the call does not supply that argument, the default is used:

```python
def greet(name, greeting="Hello", punctuation="!"):
    return f"{greeting}, {name}{punctuation}"

print(greet("Asha"))
print(greet("Ravi", "Welcome"))
print(greet("Meena", punctuation="?"))
print(greet("Kiran", "Hi", "."))
```

Output:

```text
Hello, Asha!
Welcome, Ravi!
Hello, Meena?
Hi, Kiran.
```

Defaults make the common case short and the unusual case possible. The third call shows why keywords and defaults work so well together: you can skip `greeting` and set only `punctuation`.

In the definition, parameters **without** defaults must come before parameters **with** defaults. Otherwise Python could not tell which positional argument goes where:

```python
def bad(greeting="Hello", name):
    return greeting + name
```

Output:

```text
  File "example.py", line 1
    def bad(greeting="Hello", name):
                              ^^^^
SyntaxError: parameter without a default follows parameter with a default
```

### Errors when arguments do not match

Python checks every call against the function's parameters and refuses calls that do not fit. Learn to read these three messages, because you will see them often:

```python
def area(width, height):
    return width * height

print(area(3))
```

Output:

```text
Traceback (most recent call last):
  File "example.py", line 4, in <module>
    print(area(3))
          ~~~~^^^
TypeError: area() missing 1 required positional argument: 'height'
```

```python
def area(width, height):
    return width * height

print(area(3, 4, 5))
```

Output:

```text
Traceback (most recent call last):
  File "example.py", line 4, in <module>
    print(area(3, 4, 5))
          ~~~~^^^^^^^^^
TypeError: area() takes 2 positional arguments but 3 were given
```

```python
def area(width, height):
    return width * height

print(area(3, width=4))
```

Output:

```text
Traceback (most recent call last):
  File "example.py", line 4, in <module>
    print(area(3, width=4))
          ~~~~^^^^^^^^^^^^
TypeError: area() got multiple values for argument 'width'
```

The last one is the subtle one. `3` is the first positional argument, so it already went to `width`. Then `width=4` tries to fill `width` again. Every parameter can receive **exactly one** value.

Python also rejects keyword names that do not exist, which catches typos:

```python
def area(width, height):
    return width * height

print(area(width=3, hieght=4))
```

Output:

```text
Traceback (most recent call last):
  File "example.py", line 4, in <module>
    print(area(width=3, hieght=4))
          ~~~~^^^^^^^^^^^^^^^^^^^
TypeError: area() got an unexpected keyword argument 'hieght'. Did you mean 'height'?
```

### When to use which

- Use **positional** arguments when the meaning is obvious from the function name and there are one or two of them: `square(5)`, `max(a, b)`.
- Use **keyword** arguments for anything that would be unclear: flags (`sorted(items, reverse=True)`), options, and functions with several parameters of the same type. `make_rect(width=3, height=5)` cannot be misread; `make_rect(3, 5)` can.
- Use **defaults** for options that most callers will not want to change.

### Predict the output

```python
def f(a, b=2, c=3):
    return a * 100 + b * 10 + c

print(f(1))
print(f(1, 5))
print(f(1, c=9))
print(f(c=1, a=2))
print(f(4, 5, 6))
```

<details><summary>Answer</summary>

```text
123
153
129
221
456
```

The function packs `a`, `b` and `c` into one three-digit number so you can see which value each parameter received. `f(c=1, a=2)` gives `a=2`, `b` its default `2`, `c=1`.

</details>

### Common misconceptions and edge cases

- "Keyword arguments must be in the same order as the parameters." No, any order works; only positional ones depend on order.
- "I can put a positional argument after a keyword one." Never. It is a syntax error.
- "`f(3, width=4)` sets width to 4." It is an error: 3 already went to width.
- A default parameter is just a parameter. A caller can still pass a value for it, by position or by keyword.

---

## 7. Under the hood: how CPython binds arguments

When you call a function, before the first line of the body runs, Python must decide which value each parameter gets. This step is called **binding** the arguments. Knowing the algorithm lets you predict every error message in the last section, and it explains `*args`, `**kwargs`, `/` and `*` in the next sections.

### Where the information lives

For a function such as

```python
def greet(name, greeting="Hello", punctuation="!"):
    return f"{greeting}, {name}{punctuation}"

code = greet.__code__
print(code.co_argcount)
print(code.co_varnames)
print(greet.__defaults__)
```

Output:

```text
3
('name', 'greeting', 'punctuation')
('Hello', '!')
```

the code object records that there are 3 positional-or-keyword parameters and their names, in order. The function object holds the defaults as a tuple, `('Hello', '!')`, lined up with the **last** parameters: the last default belongs to the last parameter. That is why parameters with defaults must come last: the tuple is matched from the right.

### The binding algorithm

For a call, CPython creates the new frame with an empty slot for every parameter, then fills the slots in this order:

1. **Positional arguments**, left to right, go into the parameter slots left to right. If there are more positional arguments than slots (and no `*args`), raise `TypeError: ... takes N positional arguments but M were given`.
2. **Keyword arguments**: for each `name=value`, find the slot called `name`. If there is no such parameter (and no `**kwargs`), raise `TypeError: ... got an unexpected keyword argument`. If the slot is already filled (by step 1), raise `TypeError: ... got multiple values for argument`.
3. **Defaults**: every slot still empty that has a default gets the default value from `__defaults__`. This is the **same object** every time; it is not copied. Remember this for the next section.
4. **Check**: if any slot is still empty, raise `TypeError: ... missing N required positional argument(s)`.

Only then does the body start, with every parameter already bound as a local variable.

Let us run the algorithm by hand on `greet("Ravi", punctuation="?")`:

```
slots:        name        greeting      punctuation
step 1:       'Ravi'      -             -
step 2:       'Ravi'      -             '?'
step 3:       'Ravi'      'Hello'       '?'       (from __defaults__[0])
step 4:       all filled -> run the body
```

Binding is plain assignment. `name = 'Ravi'` inside the new frame is exactly like writing `name = 'Ravi'` at the top of the body. Nothing is copied. This one fact explains sections 8, 11 and 12.

### Common misconceptions and edge cases

- "Defaults are filled in before the arguments." They are filled in last, only for slots that are still empty.
- "A default is computed fresh for every call." It is computed **once**, when `def` runs, and stored in `__defaults__`. See the next section.

---

## 8. The mutable default argument trap

### The trap

Here is a function that looks perfectly reasonable. It adds an item to a basket, and if you do not pass a basket, it starts a new empty one:

```python
def add_item(item, basket=[]):
    basket.append(item)
    return basket

print(add_item("apple"))
print(add_item("bread"))
print(add_item("milk"))
```

Output:

```text
['apple']
['apple', 'bread']
['apple', 'bread', 'milk']
```

Each call was supposed to start with a new empty basket and return a one-item list. Instead the items pile up across calls. This is the most famous trap in Python, and the binding algorithm explains it completely.

### Why it happens

The default value `[]` is evaluated **once**, when the `def` statement runs. The resulting list object is stored in `add_item.__defaults__`. Every call that does not pass `basket` gets step 3 of binding: `basket = <that same list>`. So every such call appends to the **same** list.

You can watch the stored default change:

```python
def add_item(item, basket=[]):
    basket.append(item)
    return basket

print(add_item.__defaults__)
add_item("apple")
print(add_item.__defaults__)
first = add_item("bread")
second = add_item("milk")
print(first is second, first is add_item.__defaults__[0])
```

Output:

```text
([],)
(['apple'],)
True True
```

```
                       add_item function object
                       +------------------------------+
                       | __defaults__: ( o , )        |
                       +-----------------|------------+
                                         v
  call 1: basket ----------------->  ['apple', 'bread', 'milk']
  call 2: basket ----------------->       (the same list)
  call 3: basket ----------------->       (the same list)
```

The list lives as long as the function does, so it outlives every call. The function "remembers" data between calls, which is exactly what section 5 said a function normally cannot do.

Defaults that are **immutable**, such as numbers, strings, `None` and tuples, are safe. They are shared too, but nothing can change them, so sharing is invisible. The trap is only with **mutable** defaults: lists, dicts and sets.

### The fix: None as a sentinel

The standard fix is to use `None` as the default and create the new object **inside** the body, where it is created fresh on every call:

```python
def add_item(item, basket=None):
    if basket is None:
        basket = []
    basket.append(item)
    return basket

print(add_item("apple"))
print(add_item("bread"))
mine = ["tea"]
print(add_item("sugar", mine))
print(mine)
```

Output:

```text
['apple']
['bread']
['tea', 'sugar']
['tea', 'sugar']
```

`None` here is a **sentinel**: a special value that means "the caller did not pass anything". Test it with `is None`, not with `if not basket:`. The difference matters: if a caller deliberately passes their own **empty** list, `if not basket:` would throw it away and make a new list, so the caller's list would never be filled. `is None` only fires when nothing was passed.

```python
def add_item_wrong(item, basket=None):
    if not basket:          # also true for a caller's empty list!
        basket = []
    basket.append(item)
    return basket

mine = []
add_item_wrong("apple", mine)
print(mine)
```

Output:

```text
[]
```

### The same trap with other "evaluated once" defaults

The rule "defaults are evaluated once, when `def` runs" also bites with values that should be computed fresh, such as the current time. `def log(msg, when=time.time())` records the time the function was **defined**, forever. The fix is the same: default to `None` and compute the value inside the body.

### Is a shared default ever useful?

Occasionally people use a mutable default on purpose, as a cache that survives between calls. It works, but it surprises every reader and any caller can accidentally pass their own value and bypass it. Section 18 shows the clean way to keep state between calls: a closure.

### Predict the output

```python
def track(x, seen=[], count=0):
    seen.append(x)
    count += 1
    return seen, count

print(track("a"))
print(track("b"))
print(track("c", []))
print(track("d"))
```

<details><summary>Answer</summary>

```text
(['a'], 1)
(['a', 'b'], 1)
(['c'], 1)
(['a', 'b', 'd'], 1)
```

`seen` defaults to one shared list that keeps growing, except for the third call, which passes its own fresh list. `count` defaults to the int `0`; `count += 1` **rebinds** the local name `count` to a new int and never changes the default, so it is `1` every time. Mutable versus immutable is the whole difference.

</details>

### Common misconceptions and edge cases

- "The default `[]` creates a new list on each call." It is created once, when `def` runs.
- "The trap applies to all defaults." Only to mutable ones that the function **changes**. A list default that is only read is harmless, though `None` is still the clearer habit.
- "`if not basket:` is the same as `if basket is None:`." Not for an empty list passed by the caller.
- The trap is invisible in a single test. You need **two calls** to see it. Good tests call the function twice.

---

## 9. *args and **kwargs

### Any number of positional arguments: *args

`print` and `max` accept any number of arguments. You can write such functions too. A parameter written with one star, `*args`, collects **all the extra positional arguments into a tuple**:

```python
def total(*numbers):
    print("numbers is", numbers)
    result = 0
    for n in numbers:
        result += n
    return result

print(total(1, 2, 3))
print(total(10))
print(total())
```

Output:

```text
numbers is (1, 2, 3)
6
numbers is (10,)
10
numbers is ()
0
```

The name `args` is only a convention; the **star** is what matters. Inside the function, `numbers` is an ordinary tuple, possibly empty. Use a descriptive name when you can (`*numbers`, `*words`, `*paths`).

You can combine ordinary parameters with `*args`. The ordinary ones are filled first, and the star collects whatever positional arguments are left:

```python
def tag(label, *items):
    return label + ": " + ", ".join(items)

print(tag("fruit", "apple", "mango", "fig"))
print(tag("empty"))
```

Output:

```text
fruit: apple, mango, fig
empty: 
```

### Any number of keyword arguments: **kwargs

Two stars collect all the **extra keyword arguments into a dict**, mapping each name to its value:

```python
def build_profile(name, **details):
    profile = {"name": name}
    for key, value in details.items():
        profile[key] = value
    return profile

print(build_profile("Asha", age=19, city="Pune"))
print(build_profile("Ravi"))
```

Output:

```text
{'name': 'Asha', 'age': 19, 'city': 'Pune'}
{'name': 'Ravi'}
```

`details` is a new dict on every call, in the order the keywords were written. Again `kwargs` is just the conventional name.

### The full order of parameters

When a function has several kinds of parameters, they must appear in this order:

```
def f(a, b=2, *args, c, d=4, **kwargs):
      |   |      |    |   |      |
      |   |      |    |   |      +-- extra keyword arguments (dict)
      |   |      |    +---+-- keyword-only (after *args; see section 10)
      |   |      +-- extra positional arguments (tuple)
      +---+-- ordinary positional-or-keyword parameters
```

```python
def f(a, b=2, *args, c, d=4, **kwargs):
    print(a, b, args, c, d, kwargs)

f(1, c=3)
f(1, 5, 6, 7, c=3, e=9)
```

Output:

```text
1 2 () 3 4 {}
1 5 (6, 7) 3 4 {'e': 9}
```

### Unpacking at the call: * and ** in a call

The stars also work in the other direction, in a **call**. `*sequence` spreads the items of a list or tuple out as separate positional arguments; `**mapping` spreads a dict out as keyword arguments:

```python
def describe(name, age, city):
    return f"{name}, {age}, from {city}"

row = ["Asha", 19, "Pune"]
print(describe(*row))

info = {"city": "Delhi", "age": 21, "name": "Ravi"}
print(describe(**info))

print(*[1, 2, 3], sep=" | ")
```

Output:

```text
Asha, 19, from Pune
Ravi, 21, from Delhi
1 | 2 | 3
```

`describe(*row)` means exactly `describe("Asha", 19, "Pune")`. `describe(**info)` means `describe(city="Delhi", age=21, name="Ravi")`. The dict's keys must match parameter names, or you get the "unexpected keyword argument" error.

Be careful to keep the two meanings apart:

- In a **definition**, `*args` and `**kwargs` **collect** arguments into a tuple and a dict.
- In a **call**, `*seq` and `**d` **spread** a sequence and a dict out into arguments.

### Forwarding arguments

Combining both directions lets one function pass "whatever it was given" on to another, without knowing or caring what those arguments are. This is called **forwarding**:

```python
def shout(text, times=1, end="!"):
    return (text.upper() + end) * times

def logged(func, *args, **kwargs):
    print("calling", func.__name__, "with", args, kwargs)
    result = func(*args, **kwargs)
    print("got", repr(result))
    return result

logged(shout, "hi")
logged(shout, "hey", times=2, end="? ")
```

Output:

```text
calling shout with ('hi',) {}
got 'HI!'
calling shout with ('hey',) {'times': 2, 'end': '? '}
got 'HEY? HEY? '
```

`logged` collects everything into `args` and `kwargs`, then spreads them back out unchanged with `func(*args, **kwargs)`. It works for any function with any signature. A very common bug is forgetting the stars on the inner call: `func(args, kwargs)` passes **one tuple and one dict** as two positional arguments, which is not at all the same thing.

### Under the hood

Binding with stars just adds two steps to the algorithm in section 7. In step 1, positional arguments left over after the normal slots are filled are put into a new tuple for `*args`, instead of raising an error. In step 2, keyword arguments that match no parameter name are put into a new dict for `**kwargs`, instead of raising an error. The code object records which parameters these are. Because the tuple and the dict are **built new on every call**, changing `kwargs` inside the function can never affect the caller's dict, even when the caller used `**their_dict`.

### Predict the output

```python
def f(*args, **kwargs):
    return len(args), sorted(kwargs)

nums = [1, 2, 3]
opts = {"x": 1, "y": 2}
print(f(nums))
print(f(*nums))
print(f(nums, opts))
print(f(*nums, **opts))
print(f(*"hi", z=0))
```

<details><summary>Answer</summary>

```text
(1, [])
(3, [])
(2, [])
(3, ['x', 'y'])
(2, ['z'])
```

Without a star, the list is **one** argument. With a star, it becomes three. A string is a sequence of characters, so `*"hi"` is two arguments.

</details>

### Common misconceptions and edge cases

- "`args` is a list." It is a **tuple**. You cannot `append` to it.
- "`*args` must be called `args`." Only the star matters.
- "`func(args, kwargs)` forwards the arguments." It passes a tuple and a dict as two arguments. Use `func(*args, **kwargs)`.
- `**d` in a call needs string keys that match parameter names.
- With no extra arguments, `args` is `()` and `kwargs` is `{}`, never `None`. Your function must handle the empty case: what is the `total()` of nothing? (Zero, as above.) What is the `longest()` word of nothing? Decide, and document it.

---

## 10. Positional-only and keyword-only parameters

Keyword arguments make calls clear, but sometimes you want to **force** one style. Python gives you two markers for this in the parameter list: `*` and `/`.

### Keyword-only parameters: after *

Any parameter that comes after `*args` can only be filled by keyword, because `*args` swallows every remaining positional argument. If you want that effect **without** collecting extra arguments, write a bare `*`:

```python
def connect(host, port, *, timeout=10, retries=3):
    return f"{host}:{port} timeout={timeout} retries={retries}"

print(connect("example.org", 80))
print(connect("example.org", 80, timeout=5))
print(connect("example.org", 80, 5))
```

Output:

```text
example.org:80 timeout=10 retries=3
example.org:80 timeout=5 retries=3
Traceback (most recent call last):
  File "example.py", line 6, in <module>
    print(connect("example.org", 80, 5))
          ~~~~~~~^^^^^^^^^^^^^^^^^^^^^^
TypeError: connect() takes 2 positional arguments but 3 were given
```

`timeout` and `retries` are **keyword-only**. A call like `connect("example.org", 80, 5, 1)` would be unreadable: which number is the timeout? The `*` makes that call impossible. Keyword-only parameters do not need defaults; a keyword-only parameter without a default is simply **required**, and must be named.

Keyword-only is the right choice for:

- **Boolean flags**. `sort_items(items, True)` tells the reader nothing; `sort_items(items, reverse=True)` tells them everything. Python's own `sorted` makes `key` and `reverse` keyword-only.
- **Options** that most callers leave alone.
- Parameters you might want to **reorder or add to** later. Since callers must name them, their position does not matter.

### Positional-only parameters: before /

The opposite marker, `/`, makes every parameter **before** it positional-only. They cannot be passed by keyword:

```python
def power(base, exp, /):
    return base ** exp

print(power(2, 10))
print(power(base=2, exp=10))
```

Output:

```text
1024
Traceback (most recent call last):
  File "example.py", line 5, in <module>
    print(power(base=2, exp=10))
          ~~~~~^^^^^^^^^^^^^^^^
TypeError: power() got some positional-only arguments passed as keyword arguments: 'base, exp'
```

Why would you forbid keywords? Three reasons:

1. **The parameter name is not meaningful to callers.** For `len(obj)` or `abs(x)`, the name of the parameter is an internal detail. Many built-ins are positional-only; that is why `len(obj=[1])` is an error.
2. **Freedom to rename.** If no caller can write `power(base=2, ...)`, you can rename `base` to `b` later without breaking anyone's code.
3. **No clash with `**kwargs`.** A function that accepts arbitrary keyword arguments may want one of them to be called `name`. If its own first parameter is `name` and positional-only, the two never collide.

### Both together

A full signature can use both markers. The parameters between them are ordinary (positional or keyword):

```
def f(pos_only, /, normal, *, kw_only):
```

```python
def f(a, /, b, *, c):
    return (a, b, c)

print(f(1, 2, c=3))
print(f(1, b=2, c=3))
```

Output:

```text
(1, 2, 3)
(1, 2, 3)
```

Two calls are impossible with this signature: `f(a=1, b=2, c=3)` fails because `a` is positional-only, and `f(1, 2, 3)` fails because `c` is keyword-only. `b` accepts either style.

### Designing a signature that is hard to misuse

A function signature is a **user interface** for programmers. A good one makes correct calls easy and wrong calls impossible or obvious. Compare two versions of a money transfer function:

```python
def transfer(amount, source, target, dry_run):
    ...

transfer(500, "ravi", "asha", False)     # who pays whom? what is False?
```

```python
def transfer(amount, /, *, source, target, dry_run=False):
    ...

transfer(500, source="ravi", target="asha")
```

In the second version, `source` and `target` must be named, so they can never be swapped by accident; `dry_run` is a keyword-only flag with a safe default; `amount` is positional-only because "the thing being transferred" is obvious and its name is not part of the interface. A few habits give most of the benefit:

- Put the one or two **obvious, essential** inputs first, as positional parameters.
- Make **flags and options keyword-only**, with sensible defaults.
- Never make a caller pass several values of the same type by position when swapping them would be a silent bug.
- Use `None` as the default for "not given", never a mutable object.

### Common misconceptions and edge cases

- "A bare `*` collects arguments." It collects nothing; it only marks where keyword-only parameters begin. Passing an extra positional argument is still an error.
- "Keyword-only parameters must have defaults." No. Without a default they are required, but must be named.
- `/` must come before `*` if both appear, and nothing can come before `/` except parameters.
- The error messages tell you which rule you broke: "takes 2 positional arguments but 3 were given" for keyword-only, "got some positional-only arguments passed as keyword arguments" for positional-only.

---

## 11. Argument passing through object references

Now the question every programmer must be able to answer: **if I pass my list to a function, and the function changes it, does my list change?**

### The rule

Recall from core.02 and core.05: a name is a label attached to an object, and assignment never copies. Section 7 showed that binding a parameter is just an assignment in the new frame. Put those together and you get the whole rule:

> Calling `f(x)` makes the parameter refer to **the same object** that `x` refers to. Nothing is copied.

So during the call there are two labels, the caller's name and the parameter, on **one** object.

```python
def show_identity(param):
    print("inside: ", id(param))

data = [1, 2, 3]
print("outside:", id(data))
show_identity(data)
```

Output:

```text
outside: 124841208176000
inside:  124841208176000
```

The ids are equal: one object, two names. (The actual number will differ on your machine.)

```
   caller's frame              function's frame
  +--------------+            +------------------+
  | data  ---+   |            |  param  ---+     |
  +----------|---+            +------------|-----+
             |                             |
             +---------->  [1, 2, 3]  <----+
```

This model has several names. Python's documentation says arguments are passed "by assignment" or "using call by value where the value is always an object reference". You will also hear "call by sharing" and "pass by object reference". They all mean the picture above. It is **neither** classic "pass by value" (a copy is made) **nor** classic "pass by reference" (the parameter becomes an alias for the caller's *variable*, so assigning to it changes the caller's variable). The next section shows why both of those older descriptions give wrong predictions in Python.

### Common misconceptions and edge cases

- "Python passes numbers by value and lists by reference." Python passes **everything** the same way: a reference to the object. Numbers only *seem* different because they cannot be changed (section 12).
- "Passing a big list to a function is slow because it is copied." Nothing is copied. Passing a ten-million-item list costs the same as passing the number 1.
- "`id()` shows the memory address." In CPython it happens to, but treat it only as "a number that is unique to this object while it exists".

---

## 12. Mutation versus rebinding inside a function

With one object and two names, what happens next depends entirely on **what the function does with its name**. There are exactly two possibilities, and you must learn to tell them apart at a glance.

- **Mutation** changes the object itself: `lst.append(x)`, `lst[0] = x`, `lst.sort()`, `d[key] = v`, `del d[key]`, `s.add(x)`, `lst += [x]` on a list. Every name attached to that object sees the change, including the caller's.
- **Rebinding** moves the function's own name to a different object: `lst = [...]`, `lst = lst + [x]`, `n = n + 1`, `n += 1` on an int. Only the function's local label moves. The caller's name still points at the original object, which is untouched.

### Mutation is visible to the caller

```python
def add_bonus(marks):
    for i in range(len(marks)):
        marks[i] += 5
    marks.append(100)

scores = [60, 70]
add_bonus(scores)
print(scores)
```

Output:

```text
[65, 75, 100]
```

`marks[i] += 5` replaces item `i` *in the list*, and `append` changes the list. That list is the caller's list, so the caller sees both changes.

### Rebinding is not visible to the caller

```python
def reset(marks):
    marks = []
    marks.append(0)
    print("inside:", marks)

scores = [60, 70]
reset(scores)
print("outside:", scores)
```

Output:

```text
inside: [0]
outside: [60, 70]
```

`marks = []` creates a new empty list and moves the **local** label `marks` to it. From that line on, the function is working on its own new list. The caller's `scores` was never touched.

```
  before marks = []:        scores --> [60, 70] <-- marks

  after  marks = []:        scores --> [60, 70]
                                                    marks --> [0]
```

This is why "pass by reference" is the wrong description: in a true pass-by-reference language, `marks = []` would empty the caller's variable too.

### Why ints and strings "cannot be changed" by a function

```python
def increment(n):
    n += 1
    print("inside:", n)

count = 5
increment(count)
print("outside:", count)
```

Output:

```text
inside: 6
outside: 5
```

Ints are immutable. `n += 1` cannot change the int `5` (nothing can); it computes a new int `6` and **rebinds** `n` to it. The same holds for strings, floats, bools, tuples and `None`. A function can never change a caller's int or string. If you want a new value, **return** it and let the caller assign it: `count = increment(count)`.

This is why "pass by value" is also the wrong description: with a list, the function *can* change the caller's data, which pass-by-value would never allow.

### The += puzzle

core.05 showed that on a list, `a += b` mutates in place while `a = a + b` builds a new list. Inside a function that difference decides whether the caller sees the change:

```python
def extend_in_place(items):
    items += [99]

def extend_copy(items):
    items = items + [99]

a = [1]
extend_in_place(a)
b = [1]
extend_copy(b)
print(a, b)
```

Output:

```text
[1, 99] [1]
```

### A decision procedure

To predict whether a call changes the caller's data, ask two questions about each line in the function that uses the parameter:

1. **Is the object mutable?** (list, dict, set: yes. int, float, str, tuple, bool, None: no.) If not, the caller's object can never change.
2. **Does the line change the object, or move the name?** Method calls like `append`, item assignment `x[i] = ...`, `del x[i]` and `+=` on a list change the object. A plain `x = ...` moves the name, and after that line, nothing the function does with `x` can reach the caller's object any more.

### Two good styles, and one bad one

There are two clean designs for a function that "updates" a collection:

- **Return a new object and leave the input alone.** The caller writes `new = f(old)`. This is the safest style: the caller's data never changes behind their back. `sorted()` works this way.
- **Change the object in place and return `None`.** The caller writes `f(data)` and knows `data` changes. `list.sort()` works this way. The `None` return is a deliberate signal: "I changed your object; there is nothing new to give you."

The bad design does both: it changes the caller's object **and** returns it, or, worse, sometimes changes it and sometimes does not. Callers cannot tell what they will get.

When you need to clean or rearrange an input **without** changing it, make a copy first:

```python
def without_negatives(numbers):
    result = []
    for n in numbers:
        if n >= 0:
            result.append(n)
    return result

def drop_negatives(numbers):
    numbers[:] = [n for n in numbers if n >= 0]

data = [3, -1, 4, -5]
clean = without_negatives(data)
print(clean, data)
drop_negatives(data)
print(data)
```

Output:

```text
[3, 4] [3, -1, 4, -5]
[3, 4]
```

`drop_negatives` uses **slice assignment** (core.05), `numbers[:] = ...`, which replaces the *contents* of the existing list. Writing `numbers = [...]` instead would only rebind the local name, and the caller's list would keep its negatives: a silent bug.

### Shallow copies inside functions

Copying with `list(x)`, `x[:]` or `x.copy()` is shallow (core.05). If the input is a list of lists and the function changes an inner list, the caller sees that change even though you "copied":

```python
def add_column(grid):
    result = grid[:]
    for row in result:
        row.append(0)
    return result

g = [[1, 2], [3, 4]]
new = add_column(g)
print(g)
```

Output:

```text
[[1, 2, 0], [3, 4, 0]]
```

Build new inner lists (`row + [0]`) or use `copy.deepcopy` when nested data must stay untouched.

### Predict the output

```python
def f(a, b, c, d):
    a.append(1)
    b = b + [2]
    c += [3]
    d = "changed"
    return b

w, x, y, z = [], [], [], "orig"
r = f(w, x, y, z)
print(w, x, y, z, r)
```

<details><summary>Answer</summary>

```text
[1] [] [3] orig [2]
```

`append` mutates `w`'s list. `b = b + [2]` rebinds the local `b` to a new list, so `x` is unchanged, but the new list is returned into `r`. `c += [3]` mutates `y`'s list in place. `d = "changed"` rebinds a local name; strings cannot be changed anyway.

</details>

### Common misconceptions and edge cases

- "Assigning to a parameter changes the caller's variable." Assignment only moves the local name.
- "If I modify a parameter, I must return it for the caller to see the change." Mutations are already visible. Returning it as well is confusing.
- "Copying with `[:]` protects nested data." It is a shallow copy; inner lists are shared.
- "`items += [x]` and `items = items + [x]` are the same inside a function." The first mutates the caller's list; the second does not.
- A function that rebinds its parameter and then mutates it (`lst = lst[:]` then `lst.append(...)`) works on its own copy: a deliberate, useful pattern.

---

## 13. Scope and the LEGB rule

### What scope means

The **scope** of a name is the region of the program where that name can be used. Python decides scope by **where a name is assigned**:

- A name assigned **inside a function** (including its parameters) is **local** to that function. It lives in the call's frame.
- A name assigned at the **top level of a file** (the module) is **global** to that file.
- Names such as `print`, `len` and `range` are **built-in**. They live in a special module called `builtins`, available everywhere.

A function can **read** global names freely:

```python
TAX_RATE = 0.18

def price_with_tax(price):
    return round(price * (1 + TAX_RATE), 2)

print(price_with_tax(100))
```

Output:

```text
118.0
```

### The LEGB lookup order

When Python meets a name in a function, it looks for it in four places, in this order, and uses the first one it finds:

1. **L**ocal: names assigned in the current function.
2. **E**nclosing: names in any function this function is nested inside (section 18), innermost first.
3. **G**lobal: names assigned at the top level of the module.
4. **B**uilt-in: names in the `builtins` module.

If the name is in none of them, you get `NameError`.

```python
x = "global x"

def outer():
    x = "enclosing x"
    def inner():
        x = "local x"
        print(x)
    inner()
    print(x)

outer()
print(x)
print(len("four"))     # len found in built-ins
```

Output:

```text
local x
enclosing x
global x
4
```

Each `x` is a different variable in a different scope. The innermost one **shadows** (hides) the others while you are inside `inner`.

### Shadowing built-ins

Since global names are searched before built-ins, you can accidentally hide a built-in by naming a variable after it:

```python
list = [3, 1, 2]
print(sorted(list))
print(list("abc"))
```

Output:

```text
[1, 2, 3]
Traceback (most recent call last):
  File "example.py", line 3, in <module>
    print(list("abc"))
          ~~~~^^^^^^^
TypeError: 'list' object is not callable
```

`list` now means your list, not the built-in type, for the rest of the file. The same happens with `sum`, `max`, `input`, `str`, `id` and `dict`. Avoid these as variable names. Inside a function, a local `sum = 0` shadows `sum` only within that function, which is less harmful but still confusing.

### Local is decided at compile time: UnboundLocalError

Here is the rule that surprises everyone once:

> If a name is **assigned anywhere** in a function body, it is local **everywhere** in that body, even on lines **before** the assignment.

Python decides this when it compiles the function, before any line runs. It does not watch the order of lines at run time.

```python
count = 0

def bump():
    print("count is", count)

bump()
```

Output:

```text
count is 0
```

Reading a global works. Now add one line that assigns:

```python
count = 0

def bump():
    print("count is", count)
    count = count + 1

bump()
```

Output:

```text
Traceback (most recent call last):
  File "example.py", line 7, in <module>
    bump()
    ~~~~^^
  File "example.py", line 4, in bump
    print("count is", count)
                      ^^^^^
UnboundLocalError: cannot access local variable 'count' where it is not associated with a value
```

Because `count = ...` appears in the body, the compiler marks `count` as local for the **whole** function. The first line then tries to read the local `count`, which has not been assigned yet. The global `count` is never even considered. The error message names the cause exactly: "cannot access local variable 'count' where it is not associated with a value".

`count += 1` on its own triggers it too, because `+=` is an assignment: it must read the local `count` before it can store the new value.

You can see the compiler's decision on the code object:

```python
count = 0

def reads():
    return count

def assigns():
    count = 1
    return count

print(reads.__code__.co_varnames)
print(assigns.__code__.co_varnames)
```

Output:

```text
()
('count',)
```

`co_varnames` lists the local variables. `reads` has none, so its `count` is looked up as a global. `assigns` has `count` as a local.

### Fixing UnboundLocalError

There are three fixes, from best to worst:

1. **Pass the value in and return the result.** `def bump(count): return count + 1`, called as `count = bump(count)`. The function no longer depends on a global at all.
2. Use a **different local name** if you only meant to compute something new: `new_count = count + 1`.
3. Declare `global count` (next section), if you really want the function to change the global.

### Loops and if do not create scopes

Only functions (and modules, and classes, in a later module) create scopes. A name assigned in a `for` or `if` block inside a function is local to the **function**, and still exists after the block:

```python
def last_even(numbers):
    for n in numbers:
        if n % 2 == 0:
            found = n
    return found

print(last_even([1, 4, 7, 8, 9]))
```

Output:

```text
8
```

This also means a function like this one crashes with `UnboundLocalError` if no even number exists, because `found` was never assigned. Initialise names before the loop (`found = None`).

Comprehension variables are the exception that proves the rule: a comprehension runs in its own small scope, so its loop variable does not leak out (core.05).

### Common misconceptions and edge cases

- "A function cannot see global variables." It can **read** them. It cannot **assign** them without `global`.
- "Python reads the function line by line, so the global is used until the local assignment." Locality is decided for the whole body at compile time.
- "`if` and `for` have their own scopes, like in C or Java." They do not.
- Naming variables `list`, `sum`, `max` or `input` shadows the built-in for the rest of that scope.

---

## 14. global and nonlocal

### global

The `global` statement tells the compiler: "in this function, this name refers to the module-level variable; assignments should change that one".

```python
balance = 0

def deposit(amount):
    global balance
    balance += amount
    return balance

deposit(100)
deposit(50)
print(balance)
```

Output:

```text
150
```

`global` must appear before the name is used in the function. It does not create anything by itself; it only changes where assignments go.

### Why to avoid global state

`global` works, but functions that change globals are hard to reason about and hard to test:

- You cannot understand `deposit(50)` by looking at the call. Its effect depends on, and changes, something far away.
- Two parts of the program can change the same global and interfere.
- Tests must remember to reset the global before every test, or one test's leftovers break the next.

Compare the pure version:

```python
def deposit(balance, amount):
    return balance + amount

balance = 0
balance = deposit(balance, 100)
balance = deposit(balance, 50)
print(balance)
```

Output:

```text
150
```

Everything the function needs comes in as arguments, and everything it produces goes out as the return value. A function like this, whose result depends only on its arguments and which changes nothing outside itself, is called a **pure function**. Pure functions are the easiest code in the world to test and to trust. Prefer them. Reserve `global` for genuine module-wide settings, and even then, reading a global constant (like `TAX_RATE`) is fine; it is *assigning* globals that causes trouble.

Note that `global` is needed only for **assignment**. Mutating a global list or dict (`log.append(x)`) never needs `global`, because no name is being rebound.

### nonlocal

Functions can be defined inside other functions (sections 15 and 18). The inner function can **read** the outer function's variables through the E in LEGB. But assigning to one of them, by the rule of section 13, would make it local to the inner function. The `nonlocal` statement says: "this name belongs to the nearest enclosing function; assign to that one".

```python
def make_counter():
    count = 0
    def increment():
        nonlocal count
        count += 1
        return count
    return increment

counter = make_counter()
print(counter(), counter(), counter())
```

Output:

```text
1 2 3
```

Without `nonlocal`, `count += 1` would raise `UnboundLocalError`, for exactly the reason in section 13. Section 18 explains how `count` survives after `make_counter` has returned.

`nonlocal` only searches enclosing **functions**, never the global scope. Writing `nonlocal x` when no enclosing function has an `x` is a `SyntaxError`, caught before the program runs.

### Common misconceptions and edge cases

- "I need `global` to read a global." Only to assign one.
- "I need `global` to append to a global list." Mutation does not assign the name, so no.
- "`nonlocal` can reach module-level variables." It cannot; that is what `global` is for.
- Using `global` to "return" results from a function. Return them instead.

---

## 15. Functions as first-class objects

### A function is a value

In Python, functions are **first-class objects**: they are values like ints and lists. You can give them other names, store them in lists and dicts, pass them to other functions, and return them from functions. The `def` statement is just one way of creating such a value and attaching a name to it.

```python
def shout(text):
    return text.upper() + "!"

yell = shout
print(yell("hello"))
print(yell is shout, yell.__name__)
print(shout)
```

Output:

```text
HELLO!
True shout
<function shout at 0x7bfdff5973d0>
```

`yell = shout` copies nothing; it attaches a second name to the same function object, exactly like list aliasing. Note the difference between `shout`, the function itself, and `shout("hi")`, the **result** of calling it. Printing `shout` shows the function object (the hex address will differ on your machine).

### Passing functions to functions

You already did this in core.05: `sorted(words, key=len)` passes the function `len` to `sorted`, which calls it on each item. A function that takes or returns another function is called a **higher-order function**. You can write your own:

```python
def apply_twice(func, value):
    return func(func(value))

def add_three(n):
    return n + 3

print(apply_twice(add_three, 10))
print(apply_twice(str.upper, "hi"))
print(apply_twice(lambda s: s + "!", "hey"))
```

Output:

```text
16
HI
hey!!
```

(The last line previews `lambda` from the next section.) `apply_twice` does not know or care what `func` does. It only knows `func` can be called with one argument. This is enormously powerful: the "what to do" becomes a parameter, so one function can serve many purposes.

A very common bug is writing `apply_twice(add_three(), 10)` or `sorted(words, key=len())`. The parentheses **call** the function right there and pass its *result*. Pass the function itself: no parentheses.

### Storing functions in collections: dispatch tables

Because functions are values, a dict can map names to functions. This replaces long `if`/`elif` chains with a table lookup, and it is the core technique of this module's project:

```python
def add(a, b):
    return a + b

def sub(a, b):
    return a - b

def mul(a, b):
    return a * b

OPERATIONS = {"+": add, "-": sub, "*": mul}

for a, op, b in [(6, "+", 3), (6, "-", 3), (6, "*", 3), (6, "/", 3)]:
    func = OPERATIONS.get(op)
    if func is None:
        print(a, op, b, "= unknown operator")
    else:
        print(a, op, b, "=", func(a, b))
```

Output:

```text
6 + 3 = 9
6 - 3 = 3
6 * 3 = 18
6 / 3 = unknown operator
```

`OPERATIONS[op]` looks up a function; `(a, b)` after it calls that function. Adding a new operator means adding one function and one dict entry; the loop never changes. This pattern is called a **dispatch table**. A text adventure uses exactly this: a dict from command words (`"go"`, `"take"`, `"look"`) to the functions that handle them.

### Returning functions from functions

A function can also **create** and return a function. The inner `def` runs each time the outer function is called, producing a new function object each time:

```python
def make_greeter(greeting):
    def greeter(name):
        return f"{greeting}, {name}!"
    return greeter

hello = make_greeter("Hello")
namaste = make_greeter("Namaste")
print(hello("Asha"))
print(namaste("Ravi"))
print(hello is namaste)
```

Output:

```text
Hello, Asha!
Namaste, Ravi!
False
```

A function that builds and returns other functions is a **factory**. Notice that `greeter` still knows the `greeting` it was created with, even though `make_greeter` has already returned. That is a closure; section 18 explains how it works.

### callable

`callable(x)` tells you whether `x` can be called with `()`. Functions, built-ins, methods and types (`int`, `list`) are callable; numbers, strings and lists are not.

```python
def shout(text):
    return text.upper()

print(callable(len), callable(shout), callable(int), callable("text"), callable([]))
```

Output:

```text
True True True False False
```

Calling something that is not callable gives `TypeError: 'str' object is not callable`. You see that error most often after shadowing a function's name with a value, for example `max = max(scores)` followed later by another `max(...)` call.

### Common misconceptions and edge cases

- "`key=len()` passes len." It calls `len()` immediately (and fails). Pass `len`.
- "Assigning a function makes a copy." It makes an alias, like any assignment.
- "Functions in a dict must be called when the dict is built." Store the function (`add`), not its result (`add(1, 2)`).
- A dict of functions works only if every function has a compatible signature. Design the handlers so they can all be called the same way.

---

## 16. lambda

### A function in one expression

Often you need a small function only once, to pass to `sorted`, `max` or `map`. Writing a full `def` with a name for it is clumsy. A **lambda expression** creates a function inline:

```python
square = lambda x: x * x
print(square(7))

def square_def(x):
    return x * x
print(square_def(7))
```

Output:

```text
49
49
```

The form is `lambda parameters: expression`. It produces a function object that, when called, evaluates the expression and returns it. There is no `return` keyword: the expression **is** the return value. A lambda can take any parameters a `def` can, including defaults and `*args`, or none at all: `lambda: 42`.

The limits are deliberate. The body is a **single expression**: no statements, so no assignments with `=`, no `if` blocks (a conditional expression `a if c else b` is fine), no loops, no docstring. Its `__name__` is just `<lambda>`, which makes tracebacks less helpful.

### Where lambda shines: key functions

The best use of a lambda is as a short argument to a higher-order function:

```python
students = [("Asha", 82), ("Ravi", 75), ("Meena", 91), ("Kiran", 75)]

print(sorted(students, key=lambda s: s[1]))
print(sorted(students, key=lambda s: (-s[1], s[0])))
print(max(students, key=lambda s: s[1]))
words = ["banana", "Fig", "apple", "Cherry"]
print(sorted(words, key=lambda w: (len(w), w.lower())))
```

Output:

```text
[('Ravi', 75), ('Kiran', 75), ('Asha', 82), ('Meena', 91)]
[('Meena', 91), ('Asha', 82), ('Kiran', 75), ('Ravi', 75)]
('Meena', 91)
['Fig', 'apple', 'banana', 'Cherry']
```

`key=lambda s: s[1]` says "sort by the mark". The tuple key `(-s[1], s[0])` sorts by mark, highest first, then by name for ties: negating a number reverses its order, so you need no `reverse=True` (which would also reverse the names). This "decorate with a tuple" technique was introduced in core.05; lambda is what makes it a one-liner.

### When not to use lambda

- **Do not assign a lambda to a name.** `square = lambda x: x * x` works, but `def square(x): return x * x` is clearer, has a real `__name__` for tracebacks, and can have a docstring. The official style guide (PEP 8) says to use `def` here.
- **Do not cram logic into a lambda.** If the expression does not fit comfortably on one line, or needs a comment to explain, write a named function. A name such as `by_score_then_name` is itself documentation.
- **Do not wrap a function that already exists.** `key=lambda w: len(w)` is just `key=len`, and `key=lambda w: w.lower()` is `key=str.lower`.

### Common misconceptions and edge cases

- "A lambda is a special, faster kind of function." It creates an ordinary function object. The only differences are syntax and the name `<lambda>`.
- "A lambda can contain `return`." The expression is returned automatically; `return` is a syntax error there.
- "`lambda x: print(x)` returns what it prints." It returns `print`'s result, `None`.

---

## 17. map, filter and functools.reduce

Three classic higher-order functions apply a function across a sequence. You will meet them in other people's code and in other languages, so know them well, and know when a comprehension (core.05) is clearer.

### map: apply a function to every item

`map(func, iterable)` calls `func` on each item and gives you the results:

```python
words = ["apple", "fig", "banana"]
lengths = map(len, words)
print(lengths)
print(list(lengths))
print(list(map(str.upper, words)))
print(list(map(lambda n: n * n, [1, 2, 3, 4])))
print(sum(map(int, "1 2 3 40".split())))
```

Output:

```text
<map object at 0x7c93d6485e40>
[5, 3, 6]
['APPLE', 'FIG', 'BANANA']
[1, 4, 9, 16]
46
```

Notice the first print (the hex address will differ on your machine). `map` does **not** return a list. It returns a **map object**, an *iterator* that produces results one at a time when something asks for them: `list()`, a `for` loop, `sum`, `join` and so on. This is called being **lazy**. The work happens only when the values are needed.

With more than one iterable, `map` takes one item from each and passes them all to the function, stopping at the shortest, much like `zip` (core.04):

```python
print(list(map(lambda a, b: a * b, [1, 2, 3], [10, 20, 30])))
print(list(map(max, [3, 9, 2], [5, 1, 8])))
```

Output:

```text
[10, 40, 90]
[5, 9, 8]
```

### filter: keep the items that pass a test

`filter(func, iterable)` keeps each item for which `func(item)` is truthy:

```python
nums = [5, -2, 0, 8, -7, 3]
print(list(filter(lambda n: n > 0, nums)))
print(list(filter(str.isdigit, ["12", "ab", "7", "3x"])))
print(list(filter(None, [0, 1, "", "a", [], [0], None])))
```

Output:

```text
[5, 8, 3]
['12', '7']
[1, 'a', [0]]
```

`filter(None, items)` is a special case: with `None` as the function, it keeps the truthy items.

### An iterator can be used only once

Because map and filter objects produce values lazily and do not store them, you can walk through one **only once**. After that it is exhausted, and it silently produces nothing:

```python
evens = filter(lambda n: n % 2 == 0, range(10))
print(list(evens))
print(list(evens))
print(sum(evens))
```

Output:

```text
[0, 2, 4, 6, 8]
[]
0
```

No error, just empty results. That makes this bug hard to see. If you need the results more than once, turn them into a list straight away: `evens = list(filter(...))`.

### Under the hood: why lazy?

A map object holds only the function, a reference to the input, and its current position. It does not compute anything until asked, and it never holds more than one result at a time. So `map` over a million-line file uses almost no memory, and `any(map(is_bad, items))` can stop at the first bad item without processing the rest. The generator expressions previewed in core.04 work the same way. The cost of laziness is the one-pass rule above.

### map and filter versus comprehensions

Every `map` and `filter` can be written as a comprehension:

```python
nums = [1, 2, 3, 4, 5, 6]
print(list(map(lambda n: n * n, filter(lambda n: n % 2 == 0, nums))))
print([n * n for n in nums if n % 2 == 0])
```

Output:

```text
[4, 16, 36]
[4, 16, 36]
```

Most Python programmers find the comprehension clearer when you would need a `lambda`. `map` reads nicely when the function already exists and has a good name: `map(int, parts)`, `map(str.strip, lines)`. Use whichever reads better; both are correct.

### functools.reduce: combine everything into one value

`reduce` lives in the `functools` module. It takes a two-argument function and **folds** a sequence into a single value: it combines the first two items, then combines that result with the third, and so on.

```python
from functools import reduce

nums = [3, 5, 2, 4]
print(reduce(lambda acc, n: acc + n, nums))
print(reduce(lambda acc, n: acc * n, nums))
print(reduce(lambda acc, n: acc if acc > n else n, nums))
```

Output:

```text
14
120
5
```

Trace the product by hand: `3 * 5 = 15`, then `15 * 2 = 30`, then `30 * 4 = 120`. The first parameter (`acc`, the **accumulator**) holds the result so far; the second is the next item.

`reduce` takes an optional third argument, the **initial value**, which is used as the starting accumulator. You need it whenever the sequence might be empty:

```python
from functools import reduce

print(reduce(lambda acc, n: acc * n, [], 1))
print(reduce(lambda acc, w: acc + len(w), ["ab", "cde"], 0))
print(reduce(lambda acc, n: acc * n, []))
```

Output:

```text
1
5
Traceback (most recent call last):
  File "example.py", line 5, in <module>
    print(reduce(lambda acc, n: acc * n, []))
          ~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^
TypeError: reduce() of empty iterable with no initial value
```

Without an initial value, an empty sequence is an error, and a one-item sequence returns that item without calling the function. With an initial value, the function is called once per item, which also lets the accumulator have a different type from the items (the second line adds lengths of strings into an int).

When the operation already has a built-in, use the built-in: `sum`, `max`, `min`, `any`, `all`, `"".join`, and `math.prod` are clearer than `reduce`. Use `reduce` when you are folding with an operation that has no built-in, such as composing a list of functions.

### Common misconceptions and edge cases

- "`map` returns a list." It returns a lazy iterator. Wrap it in `list()` to see or reuse the values.
- "I can loop over a map object twice." The second loop gets nothing.
- "`filter` removes the items where the function is true." It **keeps** them.
- `reduce` on an empty sequence without an initial value raises `TypeError`.
- `reduce(f, items, init)` calls `f(acc, item)`, accumulator first. Getting the order of the lambda's parameters backwards gives wrong results for non-symmetric operations such as subtraction.

---

## 18. Closures

### Nested functions

A function can be defined inside another function. The inner function is created each time the outer one runs, and is local to it:

```python
def report(marks):
    def grade(m):
        if m >= 75:
            return "distinction"
        if m >= 40:
            return "pass"
        return "fail"
    for m in marks:
        print(m, grade(m))

report([82, 55, 31])
```

Output:

```text
82 distinction
55 pass
31 fail
```

`grade` exists only inside `report`. This keeps helper functions out of the way when nothing else needs them.

### Inner functions can see the outer function's variables

By the E in LEGB, an inner function can read variables of the function around it:

```python
def make_multiplier(factor):
    def multiply(n):
        return n * factor
    return multiply

double = make_multiplier(2)
triple = make_multiplier(3)
print(double(10), triple(10))
print(double(triple(5)))
```

Output:

```text
20 30
30
```

Look closely at what is strange here. `make_multiplier(2)` **has returned**. Its frame is gone. Yet `double` still knows that `factor` is `2`. And `triple` has its own `factor`, `3`. Each returned function carries its own copy of the environment it was born in.

A function that remembers variables from an enclosing scope, even after that scope has finished, is called a **closure**. The remembered variables are its **free variables**: they are used in the function but not defined in it.

### Under the hood: cells

How can `factor` survive the end of `make_multiplier`'s frame? When CPython compiles `make_multiplier`, it notices that `factor` is used by an inner function. Instead of storing `factor` directly in the frame like an ordinary local, it stores it in a small separate object called a **cell**. A cell is just a box holding one reference.

When the `def multiply` statement runs, the new function object is given a tuple of references to the cells it needs, stored in its `__closure__` attribute. When `make_multiplier` returns, its frame is discarded, but the cell is still referenced by the function object, so it stays alive.

```python
def make_multiplier(factor):
    def multiply(n):
        return n * factor
    return multiply

double = make_multiplier(2)
triple = make_multiplier(3)
print(double.__code__.co_freevars)
print(double.__closure__)
print(double.__closure__[0].cell_contents, triple.__closure__[0].cell_contents)
print(double.__code__ is triple.__code__)
```

Output:

```text
('factor',)
(<cell at 0x707bd197a770: int object at 0xad7e90>,)
2 3
True
```

The two hex addresses in the cell line will be different on your machine. What matters is that it is a `cell` holding an `int`.

```
     double --> function object            triple --> function object
                __code__ ----------+                  __code__ ---------+
                __closure__: (o,)  |                  __closure__: (o,) |
                               |   +----> one shared code object <------+
                               v                                  |
                         cell [ 2 ]                            cell [ 3 ]
```

Two function objects share one compiled code object, but each has its own cell. Inside `multiply`, reading `factor` means "look in my cell and read what it holds right now". Remember the words **right now**: they are the key to the next section.

### Changing enclosed state: nonlocal

A closure can also **change** its remembered variables, using `nonlocal` (section 14). Assignment through `nonlocal` stores a new reference into the cell. This gives you a function with private memory that persists between calls, without any global variable:

```python
def make_counter():
    count = 0
    def counter():
        nonlocal count
        count += 1
        return count
    return counter

a = make_counter()
b = make_counter()
print(a(), a(), a())
print(b())
print(a())
```

Output:

```text
1 2 3
1
4
```

Each call to `make_counter` makes a new cell, so `a` and `b` count independently. No other code can reach `count` at all: the state is fully **encapsulated**. Compare this with the mutable default trick in section 8, which keeps state in a place any caller can tamper with by passing an argument.

You do not need `nonlocal` to **mutate** an enclosed object, only to **rebind** the name. An enclosed list can be appended to freely:

```python
def make_logger():
    lines = []
    def log(message):
        lines.append(message)
        return len(lines)
    def history():
        return lines[:]
    return log, history

log, history = make_logger()
log("start")
log("load")
print(history())
```

Output:

```text
['start', 'load']
```

Here two closures, `log` and `history`, share the same cell for `lines`, so they work on the same list. `history` returns a copy, so a caller who changes the returned list cannot change the log itself.

### A useful closure: caching results

A closure can remember previous answers so it never computes the same thing twice. This is called **memoisation**:

```python
def make_cached(func):
    cache = {}
    def cached(n):
        if n not in cache:
            cache[n] = func(n)
        return cache[n]
    return cached

def slow_square(n):
    print("  computing", n)
    return n * n

fast = make_cached(slow_square)
print(fast(4))
print(fast(4))
print(fast(5))
```

Output:

```text
  computing 4
16
16
  computing 5
25
```

The second `fast(4)` found the answer in the cache and did not call `slow_square`. The standard library has a ready-made version of this idea, `functools.cache`, which you will meet with decorators in a later module. Writing it yourself first shows there is no magic in it: just a dict in a closure.

### Common misconceptions and edge cases

- "A closure copies the outer variable's value when it is created." It keeps a reference to a **cell**, and reads the cell's current contents each time it runs. The next section shows why this matters.
- "Local variables always die when a function returns." Variables captured by an inner function live on in cells.
- "I need `nonlocal` to append to an enclosed list." Only rebinding needs `nonlocal`.
- Forgetting `nonlocal` before `count += 1` in an inner function gives `UnboundLocalError`, by the compile-time rule of section 13.

---

## 19. Late binding in closures

### The trap

You want three functions: one that returns 0, one that returns 1, one that returns 2. You create them in a loop:

```python
funcs = []
for i in range(3):
    funcs.append(lambda: i)

print([f() for f in funcs])
```

Output:

```text
[2, 2, 2]
```

All three return `2`. The same happens with `def` instead of `lambda`, and with a list comprehension:

```python
funcs = [lambda: i * 10 for i in range(3)]
print([f() for f in funcs])

def make_all():
    result = []
    for name in ["Asha", "Ravi", "Meena"]:
        def hello():
            return "Hello " + name
        result.append(hello)
    return result

print([h() for h in make_all()])
```

Output:

```text
[20, 20, 20]
['Hello Meena', 'Hello Meena', 'Hello Meena']
```

### Why it happens: closures capture variables, not values

Each lambda refers to the **variable** `i`, not to the value `i` had when the lambda was created. There is only **one** variable `i` in that scope (and in the `make_all` example, one cell for `name`). The loop keeps rebinding it: 0, then 1, then 2. The lambdas do not look at `i` until they are **called**, and by then the loop has finished and `i` is `2`.

This is called **late binding**: the free variable's value is looked up when the function runs, not when it is defined. It is exactly the "reads the cell right now" rule from the last section.

```python
funcs = []
for i in range(3):
    funcs.append(lambda: i)

print(funcs[0]() , "while i is", i)
i = 99
print(funcs[0]() , "after i = 99")
```

Output:

```text
2 while i is 2
99 after i = 99
```

At the top level of a file, `i` is a global, so the lambdas read the global; changing it changes every answer. Inside a function, the loop variable is a cell shared by all the inner functions, with the same effect.

### Fix 1: bind the value with a default argument

Default values are evaluated **once, when the function is defined** (section 8). Usually that is a trap; here it is exactly what we want:

```python
funcs = []
for i in range(3):
    funcs.append(lambda i=i: i)

print([f() for f in funcs])
```

Output:

```text
[0, 1, 2]
```

`lambda i=i: i` has a parameter `i` whose default is the **current value** of the loop variable, captured when this lambda is created. Inside the lambda, `i` now means the parameter, a local, not the shared loop variable. The downside: a caller could pass an argument and override it (`funcs[0](7)`), and the signature is a little confusing to read.

### Fix 2: a factory function

Give each function its own enclosing scope by creating it inside a separate function call. Each call has its own frame and therefore its own cell:

```python
def make_returner(value):
    return lambda: value

funcs = []
for i in range(3):
    funcs.append(make_returner(i))

print([f() for f in funcs])
```

Output:

```text
[0, 1, 2]
```

Each call `make_returner(i)` creates a new cell holding the value passed in. The loop variable changing later cannot affect those cells. This is the cleaner fix, and it is the same factory pattern as `make_multiplier`.

### When late binding is what you want

Late binding is not a bug in Python; it is a rule, and sometimes the rule is helpful. A closure that reads a setting will see the **latest** setting, not a stale copy. The trap is specifically about creating several functions in a loop and expecting each to remember a different loop value.

### Predict the output

```python
def build():
    actions = {}
    for word in ["go", "look"]:
        actions[word] = lambda: "doing " + word
    word = "quit"
    return actions

acts = build()
print(acts["go"]())
print(acts["look"]())

adders = [lambda x, n=n: x + n for n in range(1, 4)]
print([add(10) for add in adders])
```

<details><summary>Answer</summary>

```text
doing quit
doing quit
[11, 12, 13]
```

Both lambdas in `build` read the same cell for `word`, and the last value stored in it before they are called is `"quit"`. In `adders`, each lambda captured `n` as a default when it was created, so they add 1, 2 and 3.

</details>

### Common misconceptions and edge cases

- "Each lambda in the loop captures the value of `i` at that moment." It captures the variable, which keeps changing.
- "Using `def` instead of `lambda` avoids the problem." It does not; both create closures in the same way.
- "A list comprehension creates a new `i` for each item, so it is safe." The comprehension has one scope with one `i` for the whole loop.
- The bug only shows when the functions are **called after** the loop moves on. Calling each function inside the loop, right after creating it, would hide the bug.

---

## 20. Recursion

### A function that calls itself

A function can call any function, including **itself**. This is called **recursion**. It sounds like a trick, but it is the natural way to solve any problem that contains a smaller copy of itself.

Consider the factorial: `5! = 5 × 4 × 3 × 2 × 1`. Notice that `5! = 5 × 4!`, and `4! = 4 × 3!`, and so on. The problem "factorial of 5" contains the smaller problem "factorial of 4". We need only one fact that does not refer to a smaller factorial: `0! = 1`.

```python
def factorial(n):
    if n == 0:
        return 1
    return n * factorial(n - 1)

print(factorial(5))
print(factorial(0))
print(factorial(20))
```

Output:

```text
120
1
2432902008176640000
```

Every correct recursive function has two parts:

1. A **base case**: an input simple enough to answer directly, without recursion. Here, `n == 0`.
2. A **recursive case**: the answer is built from the answer to a **smaller** version of the same problem. Here, `n * factorial(n - 1)`.

And one promise: every recursive call must move **closer to a base case**. If it does not, the function calls itself forever (until Python stops it; see the next section).

### Trusting the recursion

The hardest part of recursion for beginners is that it seems to require following every call in your head. It does not. When you write the recursive case, **assume the recursive call already works** for the smaller input, and ask only: "given the right answer for the smaller problem, how do I get the answer for this one?" This is sometimes called the **leap of faith**, and it is the same reasoning as mathematical induction. If the base case is right, and each step is right assuming the smaller one is, the whole function is right.

For `factorial`: assume `factorial(n - 1)` correctly returns `(n-1)!`. Then `n * (n-1)!` is `n!`. Done. Three questions check any recursive function:

1. Is there a base case, and is it correct?
2. Does each recursive call get a smaller input?
3. Assuming the smaller calls return correct answers, does this call combine them correctly?

### Watching the calls

It still helps, once, to see what really happens. Let us add printing, indented by depth:

```python
def factorial(n, depth=0):
    pad = "  " * depth
    print(pad + f"factorial({n}) called")
    if n == 0:
        print(pad + "base case, return 1")
        return 1
    result = n * factorial(n - 1, depth + 1)
    print(pad + f"factorial({n}) returns {result}")
    return result

factorial(3)
```

Output:

```text
factorial(3) called
  factorial(2) called
    factorial(1) called
      factorial(0) called
      base case, return 1
    factorial(1) returns 1
  factorial(2) returns 2
factorial(3) returns 6
```

The calls go **down** until they reach the base case, then the results come back **up**, each one multiplied on the way. While `factorial(0)` runs, four frames exist at once, each with its own `n`. Each frame is paused at the multiplication, waiting for the call below it to return.

### Recursion on numbers: sum of digits

The sum of the digits of 4729 is 4 + 7 + 2 + 9 = 22. The last digit is `n % 10` and the rest of the number is `n // 10` (core.02). So "sum of digits of 4729" is "9 plus sum of digits of 472":

```python
def sum_digits(n):
    if n < 10:
        return n
    return n % 10 + sum_digits(n // 10)

print(sum_digits(4729), sum_digits(5), sum_digits(1000))
```

Output:

```text
22 5 1
```

The base case is a single digit. What about a negative number? `-5 < 10`, so it returns `-5`, which is probably not what a caller wants. Handle it once, at the start, with `abs` or a check, and think about it for every recursive function: **what inputs reach the base case, and are there any that never do?**

### Recursion on lists

A list is either empty, or a first item followed by a (shorter) list. That shape is naturally recursive:

```python
def total(items):
    if not items:
        return 0
    return items[0] + total(items[1:])

print(total([4, 7, 1]), total([]))
```

Output:

```text
12 0
```

This works and shows the idea, but `items[1:]` copies the rest of the list on every call, so it costs O(n²) time and memory in total, and it uses one frame per item. For a flat list, a loop or `sum` is simply better. Recursion earns its place on data that is **nested**, where a loop alone cannot easily follow the shape.

### Recursion on nested data: flatten

Here is a list that contains lists, which contain lists, to any depth: `[1, [2, [3, 4]], 5, [[6]]]`. We want every number in order: `[1, 2, 3, 4, 5, 6]`. A loop handles one level; but how many nested loops would we need? We cannot know. Recursion handles any depth:

```python
def flatten(nested):
    result = []
    for item in nested:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result

data = [1, [2, [3, 4]], 5, [[6]], []]
print(flatten(data))
print(data)
```

Output:

```text
[1, 2, 3, 4, 5, 6]
[1, [2, [3, 4]], 5, [[6]], []]
```

`isinstance(item, list)` asks "is this item a list?" (it returns `True` or `False`; it is the clear, standard way to check a type). The leap of faith: if an item is a list, *assume* `flatten(item)` returns its numbers, flat, and extend our result with them. The base case is hidden but present: a list containing no lists makes no recursive calls. The original list is not changed, because `flatten` builds a new result list.

### Multiple recursion: the Fibonacci trap

The Fibonacci numbers are 0, 1, 1, 2, 3, 5, 8, ...: each is the sum of the previous two. The definition translates directly into code that calls itself **twice**:

```python
calls = 0

def fib(n):
    global calls
    calls += 1
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

for n in [5, 10, 20, 25]:
    calls = 0
    print(n, fib(n), calls, "calls")
```

Output:

```text
5 5 15 calls
10 55 177 calls
20 6765 21891 calls
25 75025 242785 calls
```

The answer is right, but the number of calls explodes. `fib(25)` makes almost a quarter of a million calls, because `fib(23)` is computed twice, `fib(22)` three times, `fib(21)` five times, and so on: the same small problems are solved over and over. The work grows roughly as 1.6ⁿ, which is **exponential**. `fib(40)` would take over three hundred million calls.

The fix is to remember answers: the memoising closure from section 18, or a simple loop. Recursion makes code clear; it does not make it fast. Always ask whether the recursive calls repeat the same work.

### Recursion that builds collections: subsets and permutations

Recursion is the natural tool when you must generate **every combination** of something. The **power set** of a list is the list of all its subsets. Think recursively: take the first item. Every subset of the whole list either does not contain it (a subset of the rest), or does (a subset of the rest with the first item added).

```python
def subsets(items):
    if not items:
        return [[]]
    first = items[0]
    rest = subsets(items[1:])
    return rest + [[first] + s for s in rest]

print(subsets(["a", "b", "c"]))
print(len(subsets(list(range(10)))))
```

Output:

```text
[[], ['c'], ['b'], ['b', 'c'], ['a'], ['a', 'c'], ['a', 'b'], ['a', 'b', 'c']]
1024
```

The base case is the empty list, whose only subset is the empty subset `[[]]` (not `[]`, which would mean "no subsets at all", and would make every larger answer empty too). A list of n items has 2ⁿ subsets, so no algorithm can be faster than exponential here; the output itself is that big.

Permutations (every ordering) follow the same pattern: each item in turn goes first, followed by every permutation of the remaining items. You will write that in the problems.

### Common misconceptions and edge cases

- "Recursion is a loop in disguise, so it is always interchangeable with one." Many recursions can become loops, but recursion over nested or branching structures is much easier to write recursively.
- "The base case is optional if the input is small." Without a base case, every call makes another call, forever.
- "The recursive call must be the last line." It can be anywhere; what matters is that the input shrinks.
- Writing `return [] ` instead of `return [[]]` for an empty power set, which wipes out every result above it.
- Forgetting to **return** the recursive result: `factorial(n - 1)` on its own computes the value and throws it away, and the function returns `None`.
- Using a mutable default (`def flatten(nested, result=[])`) to collect results: the trap from section 8 strikes on the second call.

---

## 21. Under the hood: the call stack and the recursion limit

### Every call is a frame on the stack

Section 5 described the call stack: each active call has a frame, and frames are stacked newest on top. Recursion simply makes the stack tall. `factorial(3)` needs four frames at its deepest point. `factorial(1000)` would need 1001.

Each frame costs memory, and in CPython, each Python-level call also uses some of the underlying C machinery's own stack, which is small and fixed. If the stack grew without limit, a runaway recursion would crash the whole interpreter with no helpful message. So Python sets a limit.

### The recursion limit

```python
import sys

print(sys.getrecursionlimit())

def countdown(n):
    if n == 0:
        return "done"
    return countdown(n - 1)

print(countdown(900))
```

Output:

```text
1000
done
```

The default limit is 1000 frames. Note that the limit counts **all** frames, including the module and any functions already running, so the deepest recursion you can actually reach is a little under 1000. Going past it raises `RecursionError`:

```python
def countdown(n):
    if n == 0:
        return "done"
    return countdown(n - 1)

print(countdown(5000))
```

Output:

```text
Traceback (most recent call last):
  File "example.py", line 6, in <module>
    print(countdown(5000))
          ~~~~~~~~~^^^^^^
  File "example.py", line 4, in countdown
    return countdown(n - 1)
  File "example.py", line 4, in countdown
    return countdown(n - 1)
  File "example.py", line 4, in countdown
    return countdown(n - 1)
  [Previous line repeated 996 more times]
RecursionError: maximum recursion depth exceeded
```

The traceback would show thousands of identical lines, so Python prints the first few and summarises the rest with "Previous line repeated ... more times". When you see that, you have one of two bugs:

1. **Infinite recursion**: a missing or unreachable base case. For example `countdown(-1)` would step past `0` forever. This is the usual cause.
2. **Recursion that is simply too deep**: correct, but the input needs more than about 1000 levels. Processing a 5000-item list one item per call is the classic example.

### Why not just raise the limit?

`sys.setrecursionlimit(10000)` raises the limit, and for a moderate increase it often works. But the limit exists to protect the C stack. Set it too high, and a deep recursion can crash the interpreter outright with a "segmentation fault" instead of a clean Python error. Raising the limit treats the symptom. The real fixes are:

- **Fix the base case**, if the recursion is infinite.
- **Use a loop** when the recursion is a straight line (one recursive call that just walks down a list or a number). Python does **not** do "tail-call optimisation": even when the recursive call is the very last thing a function does, as in `countdown`, Python still keeps every frame. Languages such as Scheme reuse the frame in that case; Python's designer chose not to, partly so that tracebacks always show every call.
- **Reduce the depth**: halve the problem in each call instead of shrinking it by one. Fast exponentiation computes `x**n` with about log₂(n) levels of recursion instead of n, so `power(2, 5000)` needs only about 13 levels:

```python
def power(base, exp):
    if exp == 0:
        return 1
    half = power(base, exp // 2)
    if exp % 2 == 0:
        return half * half
    return half * half * base

print(power(2, 10), power(3, 5))
print(len(str(power(2, 5000))), "digits")
```

Output:

```text
1024 243
1506 digits
```

### Recursion versus iteration

| | Recursion | Loop |
|---|---|---|
| Natural for | nested data, branching (trees, subsets, permutations), divide in halves | straight sequences, counting, accumulating |
| Memory | one frame per active call | constant |
| Depth limit | about 1000 in CPython | none |
| Typical bug | missing or wrong base case | wrong loop bounds |

A good rule: if each call makes **one** recursive call on an input only a little smaller, a loop is usually better in Python. If each call makes **several** recursive calls, or follows a nested structure, recursion is usually clearer.

### Common misconceptions and edge cases

- "RecursionError means recursion is the wrong tool." Usually it means the base case is wrong. Check what happens to inputs at and around the base case: 0, 1, negative numbers, empty lists.
- "Python optimises tail calls." It does not.
- "Raising the recursion limit is the standard fix." It is a last resort, and can crash the interpreter.
- The limit counts frames, not calls: a function that recurses a million times but never more than 20 deep (like the subset example) is fine.

---

## 22. Designing good functions

You now know the mechanics. This section collects the habits that turn working functions into good ones.

### One job, well named

A function should do **one** thing, which you can describe in one sentence without "and". `load_marks`, `average`, `print_report` are three functions. `load_and_average_and_print` is a sign that one function is doing three jobs and cannot be reused for any one of them.

Names: verbs for actions (`save_file`, `add_item`), nouns or descriptions for computed values (`average`, `area`, `is_valid` for a function returning a bool). A reader should be able to guess what the function does from its name and arguments alone.

### Inputs in, results out

Prefer **pure** functions: everything they need comes in through parameters, everything they produce goes out through `return`, and they change nothing else. Pure functions:

- give the same output for the same input every time, so they are trivial to test;
- can be understood without reading the rest of the program;
- can be reused anywhere.

Keep `input()` and `print()` at the edges of the program (often in a `main` function), and make the functions that do the real work pure. That is exactly how the tests in this module's problems are designed: they call your functions with arguments and check the returned values, with no keyboard and no screen involved.

### A signature that is hard to misuse

From section 10:

- One or two obvious positional parameters first.
- Flags and options keyword-only, with defaults.
- `None` as the default for "not given", never `[]` or `{}`.
- Never several same-typed values by position when a swap would be a silent bug.

### Say what happens to the arguments

If a function changes its argument, say so in the docstring and return `None`. If it does not, do not change it, not even "temporarily". Callers should never be surprised that their list is different after a call.

### Return consistently

Return the same type in every case where you can: an empty list rather than `None` for "no results", `0` rather than `None` for an empty total. Where "no answer" really is different (a search that fails), return `None` and document it.

### Small enough to see at once

If a function no longer fits on your screen, look for a block inside it that does one identifiable thing, give that block a name, and move it into its own function. Then the big function reads like a list of steps:

```python
def read_scores(lines):
    """Turn lines like 'Asha 82' into a dict of name -> int score."""
    scores = {}
    for line in lines:
        name, score = line.split()
        scores[name] = int(score)
    return scores

def top_students(scores, count=2):
    """Return the names of the `count` highest scorers, best first, ties by name."""
    ranked = sorted(scores, key=lambda name: (-scores[name], name))
    return ranked[:count]

def format_report(names):
    """Return a numbered report, one line per name."""
    return "\n".join(f"{i}. {name}" for i, name in enumerate(names, start=1))

lines = ["Asha 82", "Ravi 91", "Meena 91", "Kiran 64"]
print(format_report(top_students(read_scores(lines))))
```

Output:

```text
1. Meena
2. Ravi
```

Each function is short, has one job, can be tested on its own, and the last line reads almost like English.

### Common misconceptions and edge cases

- "Fewer, longer functions are more efficient." Function calls are cheap; confused code is expensive.
- "A function should print its result so I can see it." Return it; print at the edge.
- "Every helper needs to be at the top level." A helper used by only one function can be nested inside it.

---

## Summary

- `def` runs at the point it appears and creates a **function object**; the body runs only when called. Each call gets a fresh **frame** for its local variables, and frames form the **call stack** that a traceback prints.
- `return` ends the call and sends back one object (a tuple for several values). No `return` means `None`. **Return, do not print**, so callers can use the result.
- A **docstring** is the first statement of the body and is stored in `__doc__`.
- Arguments bind to parameters in four steps: positionals, then keywords, then defaults, then a check for missing ones. Each parameter gets exactly one value.
- **Defaults are evaluated once**, when `def` runs, and stored in `__defaults__`. A mutable default is shared by every call; use `None` and create the object in the body.
- `*args` collects extra positionals into a **tuple**; `**kwargs` collects extra keywords into a **dict**. In a call, `*seq` and `**d` spread them out. `func(*args, **kwargs)` forwards everything.
- Parameters after `*` are **keyword-only**; parameters before `/` are **positional-only**. Use them to make signatures hard to misuse.
- Passing an argument binds the parameter to **the same object**: no copy. **Mutation** (methods, item assignment, `+=` on a list) is visible to the caller; **rebinding** (`x = ...`) is not. Immutable objects can never be changed by a function.
- **LEGB**: names are looked up Local, Enclosing, Global, Built-in. A name assigned anywhere in a function is local throughout it, which causes `UnboundLocalError`. `global` and `nonlocal` redirect assignment.
- Functions are **first-class**: assign them, store them in dicts (dispatch tables), pass them (`key=`), return them (factories).
- `lambda params: expr` is a one-expression function, best as a short `key=`. `map` and `filter` return **lazy, one-pass iterators**; `reduce` folds a sequence and needs an initial value for empty input.
- A **closure** remembers enclosing variables in **cells**, read at call time. Closures created in a loop share one variable (**late binding**); fix with a default argument (`i=i`) or a factory function.
- **Recursion** needs a correct base case and a smaller input every call. Trust the recursive call. Beware repeated work (Fibonacci). CPython's **recursion limit** is about 1000 frames and there is no tail-call optimisation; prefer loops for deep, linear recursion.

## Learning outcomes

After this chapter you should be able to:

- [ ] Write functions with parameters, return values and a proper docstring, and explain print versus return.
- [ ] Explain how CPython binds positional, keyword and default arguments, and read every argument error message.
- [ ] Explain and fix the mutable default argument trap, using `__defaults__` to show what is happening.
- [ ] Write functions with `*args`, `**kwargs`, `/` and `*`, and forward arguments with `func(*args, **kwargs)`.
- [ ] **Predict whether a function call changes the caller's data**, by telling mutation from rebinding.
- [ ] Apply the LEGB rule, explain `UnboundLocalError`, and use `global` and `nonlocal` correctly (and sparingly).
- [ ] Use functions as values: dispatch tables, key functions, higher-order functions and factories.
- [ ] Use `lambda`, `map`, `filter` and `functools.reduce`, and know when a comprehension is clearer.
- [ ] **Write a closure and explain the late-binding trap**, with both standard fixes.
- [ ] Write recursive functions with correct base cases for numbers, lists and nested data, and explain the call stack and the recursion limit.
- [ ] **Design a function signature that is hard to misuse.**

## Module project

The project for this module is a **text-adventure engine driven by functions and dicts**. The world is data: a dict of rooms, where each room is a dict with a description, a dict of exits (`{"north": "hall"}`) and a list of items. The player's state is a small dict: current room and inventory. The engine reads a command, splits it into a verb and the rest, and looks the verb up in a **dispatch table**, a dict from verbs to handler functions. Every handler has the same signature, for example `handler(state, world, argument)`, and returns the text to show. The main loop is the only place that calls `input()` and `print()`; every handler is a pure-ish function you can test by calling it.

Suggested milestones:

1. **Look and move.** Rooms as a dict; handlers for `look` and `go DIRECTION`; an unknown verb prints a helpful message. Write tests that call the handlers directly.
2. **Items.** `take ITEM`, `drop ITEM` and `inventory`. Decide (and document) whether handlers mutate `state` in place or return a new state, and be consistent.
3. **Aliases and help.** Map `n`, `s`, `e`, `w` and `l` to the full commands with a second dict. `help` lists the verbs from the dispatch table itself, sorted, so it can never get out of date.
4. **Conditions.** A locked door that needs a key: give each exit an optional condition function, stored in the world data, that is called with the state and returns `True` or `False`. This is where first-class functions really pay off.
5. **Events with closures.** Use a factory such as `make_counter()` to count turns, and a dict of `on_enter` functions for rooms with special behaviour.
6. **Load the world** from a simple text format with a recursive or nested parser, and add a `save` command that prints the state.

Problem p064 in this module is the assessed stepping stone: a small command dispatcher with exactly this design. Be ready to explain your handler signature, why the dispatch table beats an `if`/`elif` chain, and which of your functions are pure.

## Further reading

All links are to the official Python documentation.

- Tutorial, defining functions and more on defining functions (defaults, keyword arguments, special parameters, lambda): https://docs.python.org/3/tutorial/controlflow.html#defining-functions
- Language reference, function definitions: https://docs.python.org/3/reference/compound_stmts.html#function-definitions
- Language reference, calls and argument binding: https://docs.python.org/3/reference/expressions.html#calls
- Language reference, naming and binding (scopes, LEGB, global, nonlocal): https://docs.python.org/3/reference/executionmodel.html#naming-and-binding
- Programming FAQ, "Why are default values shared between objects?": https://docs.python.org/3/faq/programming.html#why-are-default-values-shared-between-objects
- Programming FAQ, "Why am I getting an UnboundLocalError?": https://docs.python.org/3/faq/programming.html#why-am-i-getting-an-unboundlocalerror-when-the-variable-has-a-value
- Programming FAQ, "Why do lambdas defined in a loop all return the same result?": https://docs.python.org/3/faq/programming.html#why-do-lambdas-defined-in-a-loop-with-different-values-all-return-the-same-result
- Programming FAQ, "How do I write a function with output parameters (call by reference)?": https://docs.python.org/3/faq/programming.html#how-do-i-write-a-function-with-output-parameters-call-by-reference
- Built-in functions map, filter, callable, isinstance: https://docs.python.org/3/library/functions.html
- functools.reduce: https://docs.python.org/3/library/functools.html#functools.reduce
- sys.getrecursionlimit and sys.setrecursionlimit: https://docs.python.org/3/library/sys.html#sys.getrecursionlimit
- The data model, function objects and their attributes (`__defaults__`, `__code__`, `__closure__`): https://docs.python.org/3/reference/datamodel.html#user-defined-functions
- PEP 257, docstring conventions: https://peps.python.org/pep-0257/
- PEP 570 (positional-only parameters) and PEP 3102 (keyword-only arguments): https://peps.python.org/pep-0570/ and https://peps.python.org/pep-3102/
