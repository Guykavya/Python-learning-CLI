# Chapter 9: Type hints basics

Look at this function and answer one question: what do you have to pass to it?

```python
def total(prices, tax):
    ...
```

You cannot tell. `prices` could be a list of numbers, a dict, a string. `tax` could be `0.18`, `18`, or the text `"18%"`. To find out, you must read the body, or find a place where the function is called, or run it and see what breaks. In a ten-line script that is fine. In a program with fifty functions, written over three months, it is a constant, small tax on your attention.

Python has a way to write the answer down, right in the function header:

```python
def total(prices: list[float], tax: float) -> float:
    ...
```

Now the header says: give me a list of floats and one float, and I give you back a float. These notes are called **type hints** (or **annotations**). This chapter teaches how to write them, and, just as important, **what they do not do**.

That second part is the one that surprises almost everyone. A type hint is **not a rule that Python enforces**. If you pass the wrong type, Python does not stop you. The program runs exactly as it would without the hint. The hints are read by *other tools* (and by humans), and the most important tool is **mypy**, a program that reads your code without running it and reports places where the types do not fit together.

So this chapter has two halves, just like the chapters before it:

1. **The mechanics**: the syntax for annotating variables, parameters and return values; the annotations for lists, dicts, tuples and "maybe nothing" values; how to run mypy and read what it says.
2. **The judgement**: what hints can and cannot promise, where mypy is blind, and when you still need a real `isinstance` check.

Along the way you will answer these questions:

- How do you annotate a parameter, a return value and a variable?
- How do you describe `list[int]`, `dict[str, float]`, and the two kinds of tuple?
- What does `str | None` mean, and why does mypy insist that you check for `None` before using the value?
- Why does `add("a", "b")` still run when `add` says `int`? Which tool would reject it, and when?
- How do you install and run mypy, and how do you read a line like `app.py:7: error: ... [arg-type]`?
- Where is mypy lenient, and how do you make it strict?
- When do you need a runtime check as well?

A note on how examples are shown. Every block of code is followed by the exact output produced by really running it with Python 3.14 and **mypy 2.4.0**. The wording of mypy's messages can differ a little between mypy versions (a word changed, a note added), so if your output is slightly different, that is normal: read the *meaning*, not the exact words. The line numbers, the error codes in square brackets such as `[arg-type]`, and the idea behind each message stay the same. Python's own tracebacks show the folder path as `/home/you/project`. Answer every "Predict the output" question on paper before you open the answer.

What this chapter leaves out on purpose: hints for classes, generic classes, `TypeVar`, `Protocol`, `TypedDict`, `Literal`, dataclasses. You have not met classes yet, so those come later. What you learn here (variables, functions, the built-in collections, `None`, unions, `Callable`) is exactly the part you will use in nearly every file you write.

## Table of contents

1. [Why type hints exist](#1-why-type-hints-exist)
2. [Your first annotations](#2-your-first-annotations)
3. [Hints are not enforced: Python ignores them](#3-hints-are-not-enforced-python-ignores-them)
4. [Setting up and running mypy](#4-setting-up-and-running-mypy)
5. [Reading mypy errors](#5-reading-mypy-errors)
6. [The basic types, and two surprises](#6-the-basic-types-and-two-surprises)
7. [Collection annotations](#7-collection-annotations)
8. [Functions that return nothing](#8-functions-that-return-nothing)
9. [Optional values: `X | None`](#9-optional-values-x--none)
10. [Unions in general](#10-unions-in-general)
11. [Functions as parameters: `Callable`, and `Any`](#11-functions-as-parameters-callable-and-any)
12. [Defaults, inference and `reveal_type`](#12-defaults-inference-and-reveal_type)
13. [Where mypy is lenient, and how to make it strict](#13-where-mypy-is-lenient-and-how-to-make-it-strict)
14. [When you need a real runtime check](#14-when-you-need-a-real-runtime-check)
15. [Silencing mypy: `# type: ignore`](#15-silencing-mypy--type-ignore)
16. [Hints and tests work together](#16-hints-and-tests-work-together)
17. [Project: add type hints to a real program, step by step](#17-project-add-type-hints-to-a-real-program-step-by-step)
18. [Common traps](#18-common-traps)
19. [Summary](#19-summary)

## 1. Why type hints exist

### 1.1 The problem: a function has a hidden contract

Every function makes a promise to its callers: "give me things of these kinds, and I will give you back a thing of that kind". Without a note, the promise lives only in the author's head, or in a comment that may be out of date. Here is a small function and a small bug:

```python
def average(numbers):
    return sum(numbers) / len(numbers)


scores = [70, 80, 90]
print(average(scores))
print(average(80))
```

The author wanted a list. The caller passed a single number by mistake. What happens?

```text
$ python ch_why1.py
80.0
Traceback (most recent call last):
  File "/home/you/project/ch_why1.py", line 7, in <module>
    print(average(80))
          ~~~~~~~^^^^
  File "/home/you/project/ch_why1.py", line 2, in average
    return sum(numbers) / len(numbers)
           ~~~^^^^^^^^^
TypeError: 'int' object is not iterable
```

The first call printed `80.0`. The second call crashed, but not on the line where the mistake was made. It crashed *inside* `average`, on the `sum(...)` line, with a message about `int` not being iterable. In a big program the crash would be far away from the real cause, and the message would say nothing about what the caller did wrong.

### 1.2 What a hint gives you

Here is the same function with its promise written down:

```python
def average(numbers: list[int]) -> float:
    return sum(numbers) / len(numbers)


scores = [70, 80, 90]
print(average(scores))
print(average(80))
```

Read the header aloud: "`average` takes `numbers`, which is a list of ints, and returns a float". Three benefits follow.

1. **Documentation that cannot drift easily.** The header tells every reader what to pass. Your editor can show it in a tooltip and use it for auto-complete.
2. **A checker can find the mistake before you run anything.** The call `average(80)` passes an `int` where a `list[int]` was promised. The tool **mypy** reports that without executing a single line:

```text
$ python -m mypy ch_why2.py
ch_why2.py:7: error: Argument 1 to "average" has incompatible type "int"; expected "list[int]"  [arg-type]
Found 1 error in 1 file (checked 1 source file)
```

   It points at the exact line of the *caller* that is wrong, which is where the real mistake lives.
3. **It forces you to think.** Writing `-> float` makes you ask "can this function sometimes return `None`?" before a user finds out.

### 1.3 The honest part

Now run the file with Python itself:

```text
$ python ch_why2.py
80.0
Traceback (most recent call last):
  File "/home/you/project/ch_why2.py", line 7, in <module>
    print(average(80))
          ~~~~~~~^^^^
  File "/home/you/project/ch_why2.py", line 2, in average
    return sum(numbers) / len(numbers)
           ~~~^^^^^^^^^
TypeError: 'int' object is not iterable
```

The output is exactly the same crash as before. Python **did not care** about `list[int]`. Look carefully at what just happened, because it is the most important sentence of this chapter:

> Type hints are notes for people and tools. The Python interpreter reads them, stores them, and then ignores them. Nothing is checked when your program runs.

The checking is done by a separate program, which you run on purpose, before or after you write the code. Think of hints as the labels on the drawers in a workshop. The labels do not stop you from putting a hammer in the screwdriver drawer. But a person walking by (or a tool that scans all the drawers) can spot that something is in the wrong place.

### 1.4 When hints pay off, and when they do not

Hints pay off most in code that is **shared** (other people, or you next month), **long-lived**, and **split across many functions**. They pay off least in a 15-line throwaway script. Professional Python teams add hints almost everywhere, and run mypy (or a similar checker) automatically, because it finds a whole class of bugs for free: the wrong thing passed, the wrong thing returned, and the "forgot it can be `None`" bug that is probably the most common bug in all of programming.

## 2. Your first annotations

### 2.1 The syntax

There are only two pieces of new syntax.

- After a **parameter name**, write a colon and the type: `name: str`.
- After the closing parenthesis, write an arrow and the **return type**: `-> str`.

```python
def greet(name: str) -> str:
    return "Hello, " + name + "!"


def add(a: int, b: int) -> int:
    return a + b


print(greet("Asha"))
print(add(2, 3))
```

```text
$ python ch_first1.py
Hello, Asha!
5
```

A function with several parameters annotates each one separately: `a: int, b: int`. There is no way to write "both are ints" once. The return annotation goes after the whole parameter list.

Nothing about *how you call* the function changes. Calling `add(2, 3)` or `add(a=2, b=3)` works as before.

### 2.2 Annotating variables

A variable gets a hint with a colon after its name, then the usual `= value`:

```python
count: int = 0
price: float = 19.99
title: str = "Python"
is_ready: bool = False

count = count + 1
print(count, price, title, is_ready)
```

```text
$ python ch_first2.py
1 19.99 Python False
```

Most of the time you do **not** need to annotate a variable that you assign a value to right away. mypy looks at `count = 0` and works out for itself that `count` is an `int`. This is called **inference**. You annotate a variable in three situations:

1. You want to be clear about the intent (`price: float = 20` says "this is a float, even though I wrote an int").
2. mypy cannot work out the type, which happens with empty collections (section 7.4).
3. You declare a name now and assign it later:

```python
label: str          # declared, but nothing is assigned yet

if 3 > 2:
    label = "big"
else:
    label = "small"

print(label)
```

```text
$ python ch_first3.py
big
```

A bare `label: str` does **not** create the variable. It only records a note. Using `label` before assigning would still give a `NameError`. We will use this form rarely.

### 2.3 Where Python stores the hints

Python does keep the hints. You can look at them:

```python
def add(a: int, b: int) -> int:
    return a + b


print(add.__annotations__)
```

```text
$ python ch_first4.py
{'a': <class 'int'>, 'b': <class 'int'>, 'return': <class 'int'>}
```

`__annotations__` is a plain dict: parameter name to hint, with the return hint under the key `"return"`. Tools such as editors and mypy-like programs read the same information. Later in this module, the tests for your own problems will look at it too: they will check that you wrote the hints, and then also check that the function still behaves correctly.

Hints on module-level variables are stored too, but *how* you read them back changed between Python versions (Python 3.14 reads them lazily), so we do not rely on it here. The function version, `__annotations__`, is the stable one.

### 2.4 Try it

Annotate `shout` so that it takes a `str` and returns a `str`, and `repeat` so that it takes a `str` and an `int` and returns a `str`.

```python
def shout(text):
    return text.upper() + "!"


def repeat(text, times):
    return text * times
```

<details><summary>Answer</summary>

```python
def shout(text: str) -> str:
    return text.upper() + "!"


def repeat(text: str, times: int) -> str:
    return text * times


print(shout("hey"), repeat("ab", 3))
print(repeat.__annotations__)
```

```text
$ python ch_first6.py
HEY! ababab
{'text': <class 'str'>, 'times': <class 'int'>, 'return': <class 'str'>}
```

</details>

## 3. Hints are not enforced: Python ignores them

This section is the heart of the chapter. Read it twice.

### 3.1 A wrong type still runs

```python
def add(a: int, b: int) -> int:
    return a + b


print(add(2, 3))
print(add("2", "3"))
print(add([1], [2]))
print(add(1.5, 2.5))
```

Three of these four calls break the promise `a: int, b: int`. Predict what each `print` shows, and whether Python stops.

<details><summary>Answer</summary>

```text
$ python ch_ignore1.py
5
23
[1, 2]
4.0
```

All four lines ran. `add("2", "3")` joined two strings with `+`, giving `"23"`. `add([1], [2])` joined two lists. `add(1.5, 2.5)` added two floats. The hints said `int`, and Python never asked.

</details>

Why did this work? Because the *body* of the function only uses `+`, and `+` happens to work on strings, lists and floats. The hint was ignored, the body did its job, and the result was a perfectly valid, but surprising, value. The annotation `-> int` was also false: the second call returned a `str`.

### 3.2 A wrong type that crashes: crashes for a different reason

When a wrong type *does* crash, it is the **operation inside the body** that fails, not the hint:

```python
def add(a: int, b: int) -> int:
    return a + b


print(add("2", 3))
```

```text
$ python ch_ignore2.py
Traceback (most recent call last):
  File "/home/you/project/ch_ignore2.py", line 5, in <module>
    print(add("2", 3))
          ~~~^^^^^^^^
  File "/home/you/project/ch_ignore2.py", line 2, in add
    return a + b
           ~~^~~
TypeError: can only concatenate str (not "int") to str
```

Read the message: `can only concatenate str (not "int") to str`. It talks about `+`, not about `a: int`. If the body had been `return a` instead, no error at all would appear, and the wrong value would travel on to the next function, and the next, until something far away finally failed.

### 3.3 Who does check?

| Who | When it looks at hints | What it does if the types do not fit |
|---|---|---|
| The Python interpreter | Never checks them | Nothing. It stores them in `__annotations__` |
| **mypy** (a static checker) | When **you run it**, before the program runs | Prints an error line for each mismatch. Does not run your code |
| Your editor (for example VS Code with a Python extension) | While you type | Underlines the problem, using a checker behind the scenes |
| Your own `isinstance` checks | When the program runs | Raise an exception, if you wrote them (section 14) |
| A library such as **pydantic** (a tool you may meet later) | When the program runs | Validates or converts data against the hints |

The word **static** means "without running the program". A static checker reads the text of your code, reasons about it, and reports problems. The opposite is **runtime** checking, which happens while the program runs, with real values.

This gives you the exact answer to a question that is very likely to come up in an interview: *"Python has type hints. Why did my wrong type still run?"* Because the interpreter ignores them. Only a checker like mypy rejects it, and only if you run it.

### 3.4 Static versus runtime: a small experiment

Static checking sees only what is **written**. Runtime checking sees what **really arrives**. Here is a function that reads a number from the user. The hint says `str` for the return value of `input()`, and the function says it returns an `int`:

```python
def ask_age() -> int:
    text = input("Age: ")
    return int(text)


age = ask_age()
print(age + 1)
```

mypy is happy with this file (`int(text)` really produces an `int`):

```text
$ python -m mypy ch_ignore3.py
Success: no issues found in 1 source file
```

But mypy cannot know what the user will type. If they type `abc`, `int("abc")` raises `ValueError` at runtime, and no hint could have prevented it. Hints describe the shape of your code. They say nothing about whether **data from outside** (keyboard, files, the internet) is good. For that you still need the error handling you learned in core.07, and `isinstance` checks (section 14).

### 3.5 Try it

Without running anything, say whether each statement is true or false.

1. If I write `x: int = "hello"`, Python raises an error when that line runs.
2. If I write `def f(a: int) -> int: return a`, then `f("hi")` returns `"hi"`.
3. mypy can find the bug in `f("hi")` without running the program.
4. `f.__annotations__` is `{'a': <class 'int'>, 'return': <class 'int'>}`.

<details><summary>Answer</summary>

1. **False.** Python runs that line without complaint. `x` becomes `"hello"`. mypy would report `[assignment]`.
2. **True.** The body just returns its argument. The hint is ignored.
3. **True.** That is the whole point of a static checker.
4. **True.** Python stores the hints, exactly as you wrote them. Let us check:

```python
def f(a: int) -> int:
    return a


print(f("hi"))
print(f.__annotations__)
```

```text
$ python ch_ignore4.py
hi
{'a': <class 'int'>, 'return': <class 'int'>}
```

</details>


## 4. Setting up and running mypy

### 4.1 Install it

mypy is an ordinary Python package. It is **not** one of the packages this project requires, so it is not installed for you: you add it yourself, into the same virtual environment you already use for pytest. With the environment active, run:

```bash
pip install mypy
```

You only do this once per environment. If you ever delete the environment, install it again. (The rest of this course works without mypy, and the tests for this module's problems never call it. They check your hints through Python's own `__annotations__`. But mypy is the tool the hints are *for*, so installing it is strongly recommended. Every Python team you will ever join uses it or something very similar.)

To check that it works, ask for its version:

```bash
python -m mypy --version
```

### 4.2 Run it on a file

The command has the same shape as `python -m pytest`:

```bash
python -m mypy my_file.py
```

`python -m mypy` runs mypy using the same Python that you use for your program. That matters: it guarantees mypy and your code agree on which packages exist. Running just `mypy` also works in most setups, but `python -m mypy` is the safe habit, for the same reason you write `python -m pytest`.

Here is a file with correct hints:

```python
def area(width: float, height: float) -> float:
    return width * height


print(area(2.5, 4))
```

```text
$ python -m mypy ch_run1.py
Success: no issues found in 1 source file
```

`Success: no issues found` is the message you want. Notice what mypy did **not** do: it did not print `10.0`. mypy never runs your program. If you want the program's output, you run `python ch_run1.py` as usual. They are two separate steps:

```text
python -m mypy my_file.py     <- checks the types (does not run the program)
python my_file.py             <- runs the program (does not check the types)
```

Now a file with a mistake:

```python
def area(width: float, height: float) -> float:
    return width * height


print(area(2.5, "4"))
```

```text
$ python -m mypy ch_run2.py
ch_run2.py:5: error: Argument 2 to "area" has incompatible type "str"; expected "float"  [arg-type]
Found 1 error in 1 file (checked 1 source file)
```

mypy found one error and says so in the last line. It also sets its **exit code** to 1 (success is 0), which is how automatic tools, such as a continuous-integration server, know that the check failed. As a reminder from core.07: the exit code of a program is a small number it hands back to whoever started it; 0 means "all fine".

Now run the same file with Python:

```text
$ python ch_run2.py
Traceback (most recent call last):
  File "/home/you/project/ch_run2.py", line 5, in <module>
    print(area(2.5, "4"))
          ~~~~^^^^^^^^^^
  File "/home/you/project/ch_run2.py", line 2, in area
    return width * height
           ~~~~~~^~~~~~~~
TypeError: can't multiply sequence by non-int of type 'float'
```

The program crashed with a `TypeError`. In this case the crash and the mypy error agree. The difference is **when** you learn about it: mypy told you without running anything, with the file and line of the mistake. And in a program where the bad call is on a rarely used path, mypy would still report it, while Python would crash only when a user reaches that path.

### 4.3 Checking many files, and a whole folder

You can pass several files, or a folder:

```bash
python -m mypy file_a.py file_b.py
python -m mypy .
```

With `.`, mypy checks every `.py` file below the current folder. The first run creates a folder called `.mypy_cache`, where mypy remembers what it already checked, so the next run is faster. It is safe to delete, and it should never be added to your own work history (add `.mypy_cache/` to a `.gitignore`).

### 4.4 Options you will use

| Command | Meaning |
|---|---|
| `python -m mypy file.py` | Normal check |
| `python -m mypy --strict file.py` | Turn on many extra checks (section 13) |
| `python -m mypy --disallow-untyped-defs file.py` | Complain about every function without full hints |
| `python -m mypy --pretty file.py` | Show the offending source line under each error |
| `python -m mypy --python-version 3.11 file.py` | Check as if running an older Python |

Try `--pretty` once; it is friendly for beginners:

```text
$ python -m mypy --pretty ch_run2.py
ch_run2.py:5: error: Argument 2 to "area" has incompatible type "str"; expected
"float"  [arg-type]
    print(area(2.5, "4"))
                    ^~~
Found 1 error in 1 file (checked 1 source file)
```

### 4.5 Try it

Create a file `try_mypy.py` containing the function `double(n: int) -> int` that returns `n * 2`, followed by the call `double("4")`. Predict how many errors mypy reports, and which line.

<details><summary>Answer</summary>

```python
def double(n: int) -> int:
    return n * 2


double("4")
```

```text
$ python -m mypy ch_run3.py
ch_run3.py:5: error: Argument 1 to "double" has incompatible type "str"; expected "int"  [arg-type]
Found 1 error in 1 file (checked 1 source file)
```

One error, on line 5: the call. The function itself is fine. Python would run this file without any error, because `"4" * 2` is `"44"`:

```text
$ python ch_run3.py

```

(It prints nothing, because the file does not `print` the result.) A wrong call with no crash is the most dangerous kind.

</details>

## 5. Reading mypy errors

### 5.1 Anatomy of an error line

Every mypy message has the same shape:

```text
file.py:LINE: error: MESSAGE  [error-code]
```

- `file.py:LINE` tells you where. Go to that line of the file.
- `error:` is the severity. You will also see `note:` lines, which give extra detail about the error above them.
- The **message** says what is wrong, usually with the two types in conflict: the type you *have* and the type that is *expected*. Read it as "I found X, but the hint demands Y".
- The **error code** in square brackets names the *category* of the problem. It stays stable between versions even when the wording changes, so it is the best thing to search for.

### 5.2 The six errors you will see most

Here is one file that makes each of them once. Every function is correct except for one line, marked with a comment.

```python
def add(a: int, b: int) -> int:
    return a + b


def label(n: int) -> str:
    return n                       # wrong return type


def sign(n: int) -> str:
    if n > 0:
        return "positive"
    elif n < 0:
        return "negative"          # no branch for n == 0


total: int = "ten"                 # wrong value for the variable
result = add("1", 2)               # wrong argument type


def show(text: str) -> None:
    print(text)


value = show("hi")                 # using a result that is always None
names = []                         # mypy cannot guess the element type
```

```text
$ python -m mypy ch_err1.py
ch_err1.py:6: error: Incompatible return value type (got "int", expected "str")  [return-value]
ch_err1.py:9: error: Missing return statement  [return]
ch_err1.py:16: error: Incompatible types in assignment (expression has type "str", variable has type "int")  [assignment]
ch_err1.py:17: error: Argument 1 to "add" has incompatible type "str"; expected "int"  [arg-type]
ch_err1.py:24: error: "show" does not return a value (it only ever returns None)  [func-returns-value]
ch_err1.py:25: error: Need type annotation for "names" (hint: "names: list[<type>] = ...")  [var-annotated]
Found 6 errors in 1 file (checked 1 source file)
```

Go through them one by one.

**`[return-value]`: `Incompatible return value type (got "int", expected "str")`.** The function promised a `str` (`-> str`) but a `return` statement hands back an `int`. Fix the return value or the hint, whichever is wrong.

**`[return]`: `Missing return statement`.** The function promises a value, but there is a path through it that reaches the end without a `return`. In Python such a function silently returns `None`. Here, `sign(0)` would return `None`, not a `str`. The fix is to add the missing branch.

**`[assignment]`: `Incompatible types in assignment (expression has type "str", variable has type "int")`.** The variable was declared as an `int`, and you stored a `str` in it. Also appears when you later assign a different type to a variable whose type mypy had inferred.

**`[arg-type]`: `Argument 1 to "add" has incompatible type "str"; expected "int"`.** A call passes the wrong kind of thing. "Argument 1" counts from 1, so it is the first argument written in the call. This is the error you will meet most.

**`[func-returns-value]`: `"show" does not return a value (it only ever returns None)`.** You wrote `value = show("hi")`, but `show` is declared `-> None`, so `value` can only ever be `None`. A sign you meant a different function, or forgot a `return`.

**`[var-annotated]`: `Need type annotation for "names"`.** mypy sees an empty list and cannot know what you want to put in it. You must tell it: `names: list[str] = []`. Section 7.4 explains.

### 5.3 How to work with a list of errors

1. **Read the first error first.** Later errors are sometimes a result of the first.
2. **Go to the line.** Compare the two types in the message.
3. **Decide who is wrong: the hint, or the code.** This is the same question you asked in core.08 about a failing test: is the test wrong or the code? Here, is the **annotation** wrong (it promised too little, or a wrong thing) or is the **code** wrong (it does not keep the promise)?
4. **Fix one thing, run mypy again.** The output is short, so run it often.

### 5.4 Error codes: `--show-error-codes` and why they matter

mypy shows the code by default in current versions. The code is useful in two ways: for searching the documentation, and for the narrow form of `# type: ignore[code]` (section 15).

### 5.5 Try it

Without running mypy, which lines of this file does it flag?

```python
def half(n: int) -> float:
    return n / 2          # line 2

x: float = half(7)        # line 4
y: int = half(8)          # line 5
z: str = str(half(9))     # line 6
```

<details><summary>Answer</summary>

```python
def half(n: int) -> float:
    return n / 2          # line 2

x: float = half(7)        # line 4
y: int = half(8)          # line 5
z: str = str(half(9))     # line 6
```

```text
$ python -m mypy ch_err2.py
ch_err2.py:5: error: Incompatible types in assignment (expression has type "float", variable has type "int")  [assignment]
Found 1 error in 1 file (checked 1 source file)
```

Only line 5. `half` returns a `float`, and a `float` does not fit in a variable declared `int`. Line 2 is fine because `/` always produces a float. Line 6 is fine because `str(...)` always produces a `str`.

</details>

## 6. The basic types, and two surprises

### 6.1 The names

The first types are simply the names of classes you already know:

| Hint | Values | Example |
|---|---|---|
| `int` | whole numbers | `42` |
| `float` | decimal numbers | `3.14` |
| `str` | text | `"hello"` |
| `bool` | `True` or `False` | `True` |
| `bytes` | raw bytes | `b"abc"` |
| `None` | the one value `None` | `None` |

You write the name of the type with no quotes. (You may see old code with hints inside quotes, like `"int"`. That is a trick for situations you will meet later; for now, never use quotes.)

### 6.2 Surprise one: `float` accepts an `int`

Python programmers pass `3` to a function that wants a `float` all the time, and it works. The type rules agree: wherever a `float` is expected, an `int` is accepted too. (This is sometimes called the numeric tower.) The reverse is not true: an `int` hint does **not** accept a `float`.

```python
def double(x: float) -> float:
    return x * 2


def count_up(n: int) -> int:
    return n + 1


print(double(3))       # an int where a float is wanted
print(count_up(3.0))   # a float where an int is wanted
a: float = 5
b: int = 5.0
```

```text
$ python -m mypy ch_basic1.py
ch_basic1.py:10: error: Argument 1 to "count_up" has incompatible type "float"; expected "int"  [arg-type]
ch_basic1.py:12: error: Incompatible types in assignment (expression has type "float", variable has type "int")  [assignment]
Found 2 errors in 1 file (checked 1 source file)
```

Only lines 10 and 12 are flagged: `count_up(3.0)` and `b: int = 5.0`. The calls with an `int` for a `float` are fine. Python itself runs all of it (try it), because `3.0 + 1` is simply `4.0`.

### 6.3 Surprise two: `int` accepts a `bool`

In Python, `bool` is a kind of `int`: `True` behaves as `1`, and `False` as `0`. You saw `True + True == 2` in core.02. The type rules follow the same fact, so `True` is accepted where an `int` is expected:

```python
def double(n: int) -> int:
    return n * 2


print(double(True))
flag: bool = 1
```

```text
$ python -m mypy ch_basic2.py
ch_basic2.py:6: error: Incompatible types in assignment (expression has type "int", variable has type "bool")  [assignment]
Found 1 error in 1 file (checked 1 source file)
```

Line 5, the call `double(True)`, is fine for mypy, and it prints `2` when run. Line 6, `flag: bool = 1`, is flagged, because an `int` is not necessarily a `bool`. The relation goes only one way: every `bool` is an `int`, but not every `int` is a `bool`.

This matters for runtime checks too: `isinstance(True, int)` is `True`. If you want to reject booleans from a function that wants counts, you must test for `bool` first (section 14.3).

### 6.4 `object` and `Any`

Two special hints are worth knowing by name now.

- **`object`** means "any value at all", but the function may then only do things that every object can do (compare with `==`, call `str()`, test identity).
- **`Any`** (from the `typing` module) means "turn checking off here". mypy accepts anything passed in, and lets you do anything with it.

```python
from typing import Any


def describe(value: object) -> str:
    return "got " + str(value)


def risky(value: Any) -> str:
    return value.upper()       # mypy trusts you, even for an int


print(describe(42))
print(risky("quiet"))
print(risky(42))
```

```text
$ python -m mypy ch_basic3.py
Success: no issues found in 1 source file
```

mypy is silent about the `risky(42)` call, because `Any` switches the check off. At runtime it crashes:

```text
$ python ch_basic3.py
got 42
QUIET
Traceback (most recent call last):
  File "/home/you/project/ch_basic3.py", line 14, in <module>
    print(risky(42))
          ~~~~~^^^^
  File "/home/you/project/ch_basic3.py", line 9, in risky
    return value.upper()       # mypy trusts you, even for an int
           ^^^^^^^^^^^
AttributeError: 'int' object has no attribute 'upper'
```

`Any` is an escape hatch. Every `Any` is a place where mypy can no longer protect you, so use it only when there is truly no better description. When in doubt, use a precise type.

### 6.5 Try it

Which of these assignments does mypy flag? Say yes or no for each.

```python
a: int = True
b: float = 7
c: int = 7.5
d: bool = 0
e: str = 5
f: float = False
```

<details><summary>Answer</summary>

```python
a: int = True
b: float = 7
c: int = 7.5
d: bool = 0
e: str = 5
f: float = False
```

```text
$ python -m mypy ch_basic4.py
ch_basic4.py:3: error: Incompatible types in assignment (expression has type "float", variable has type "int")  [assignment]
ch_basic4.py:4: error: Incompatible types in assignment (expression has type "int", variable has type "bool")  [assignment]
ch_basic4.py:5: error: Incompatible types in assignment (expression has type "int", variable has type "str")  [assignment]
Found 3 errors in 1 file (checked 1 source file)
```

No for `a` (bool is an int), no for `b` (int is accepted for float), **yes** for `c`, **yes** for `d` (an int is not a bool), **yes** for `e`, and no for `f` (a bool is an int, and an int is accepted for float).

</details>

## 7. Collection annotations

### 7.1 Say what is inside

A bare `list` hint says only "this is a list". Almost always you also want to say **what the list contains**. You do that with square brackets directly after the collection's name:

| Hint | Meaning | Example value |
|---|---|---|
| `list[int]` | a list where every item is an int | `[1, 2, 3]` |
| `list[str]` | a list of strings | `["a", "b"]` |
| `set[str]` | a set of strings | `{"a", "b"}` |
| `dict[str, float]` | a dict with `str` keys and `float` values | `{"tea": 2.5}` |
| `dict[str, list[int]]` | keys are strings, values are lists of ints | `{"asha": [70, 80]}` |
| `list[list[int]]` | a list of lists of ints (a grid) | `[[1, 2], [3, 4]]` |
| `list[tuple[str, int]]` | a list of pairs | `[("a", 1), ("b", 2)]` |

These are the **built-in** collection names, written in lower case, and they work directly in Python 3.9 and later. (Old code imports `List`, `Dict` from `typing`. You will see that in older tutorials. Do not use it: the lower-case names are simpler and are the modern way.)

Brackets nest as deep as the data does. Read from the outside in: `dict[str, list[int]]` is "a dict, from strings, to lists of ints".

```python
def total(numbers: list[int]) -> int:
    result = 0
    for n in numbers:
        result += n
    return result


def price_of(menu: dict[str, float], item: str) -> float:
    return menu[item]


def best(scores: dict[str, list[int]]) -> dict[str, int]:
    return {name: max(marks) for name, marks in scores.items()}


print(total([1, 2, 3]))
print(price_of({"tea": 2.5, "cake": 4.0}, "tea"))
print(best({"asha": [70, 90], "ravi": [60, 65]}))
```

```text
$ python ch_coll1.py
6
2.5
{'asha': 90, 'ravi': 65}
```

```text
$ python -m mypy ch_coll1.py
Success: no issues found in 1 source file
```

### 7.2 Wrong contents are caught

The checker looks inside the brackets:

```python
def total(numbers: list[int]) -> int:
    return sum(numbers)


print(total([1, 2, 3]))     # fine
print(total(["1", "2"]))    # a list, but of the wrong kind of item
print(total((1, 2, 3)))     # a tuple instead of a list
print(total({1, 2, 3}))     # a set instead of a list
```

```text
$ python -m mypy ch_coll2.py
ch_coll2.py:6: error: List item 0 has incompatible type "str"; expected "int"  [list-item]
ch_coll2.py:6: error: List item 1 has incompatible type "str"; expected "int"  [list-item]
ch_coll2.py:7: error: Argument 1 to "total" has incompatible type "tuple[int, int, int]"; expected "list[int]"  [arg-type]
ch_coll2.py:8: error: Argument 1 to "total" has incompatible type "set[int]"; expected "list[int]"  [arg-type]
Found 4 errors in 1 file (checked 1 source file)
```

Notice the third and fourth mistakes. `sum` would happily add a tuple or a set, so these calls *run* and give `6`, but they break the promise `list[int]`. That is the kind of loose end hints are for: if the function later started using `numbers[0]` or `numbers.append(...)`, the set would fail, and the hint warned you.

mypy checks the **kind of collection** and the **type of its items**, both. For the list literal on line 6 it points at each bad item (`List item 0 has incompatible type "str"; expected "int"`, error code `[list-item]`). For the tuple and the set it reports the whole argument (`[arg-type]`).

### 7.3 Two kinds of tuple

A tuple is special. It is usually used in one of two ways, and there is a hint for each.

**A fixed shape, where each position has its own meaning and type.** You list one type per position:

```python
point: tuple[int, int] = (3, 4)
person: tuple[str, int] = ("Asha", 21)
```

`tuple[str, int]` means: exactly two items, a `str` first and an `int` second. A tuple of three items does not fit.

**A tuple of any length, where every item has the same type.** You write the type, a comma, and three dots (`...`, the Ellipsis, which here means "and so on"):

```python
scores: tuple[int, ...] = (70, 80, 90, 100)
```

`tuple[int, ...]` means: zero or more ints.

```python
point: tuple[int, int] = (3, 4)
person: tuple[str, int] = ("Asha", 21)
bad_len: tuple[int, int] = (1, 2, 3)         # fixed shape, wrong length
bad_type: tuple[str, int] = (21, "Asha")     # fixed shape, wrong order

scores: tuple[int, ...] = (70, 80, 90, 100)
empty: tuple[int, ...] = ()
mixed: tuple[int, ...] = (1, "two")          # one wrong item
whole: tuple[int, int] = scores              # length is unknown here
```

```text
$ python -m mypy ch_coll3.py
ch_coll3.py:3: error: Incompatible types in assignment (expression has type "tuple[int, int, int]", variable has type "tuple[int, int]")  [assignment]
ch_coll3.py:4: error: Incompatible types in assignment (expression has type "tuple[int, str]", variable has type "tuple[str, int]")  [assignment]
ch_coll3.py:8: error: Incompatible types in assignment (expression has type "tuple[int, str]", variable has type "tuple[int, ...]")  [assignment]
ch_coll3.py:9: error: Incompatible types in assignment (expression has type "tuple[int, ...]", variable has type "tuple[int, int]")  [assignment]
Found 4 errors in 1 file (checked 1 source file)
```

The last error is a good one to think about. `scores` is a tuple of *any* length of ints, so mypy cannot promise that it has exactly two. The fixed shape `tuple[int, int]` is stricter than `tuple[int, ...]`.

A rule of thumb: use a **fixed tuple** for a small record with different kinds of fields (a name and an age; a min and a max), and use **`tuple[T, ...]`** for "a sequence that happens not to change". A function that returns two things naturally uses the fixed form:

```python
def min_max(numbers: list[int]) -> tuple[int, int]:
    return min(numbers), max(numbers)


low, high = min_max([4, 9, 1, 7])
print(low, high)
```

```text
$ python ch_coll4.py
1 9
```

```text
$ python -m mypy ch_coll4.py
Success: no issues found in 1 source file
```

Unpacking `low, high = ...` works well with the fixed form, because mypy knows there are exactly two items and what type each one has.

### 7.4 Empty collections need a hint

mypy works out types from the values you write. An empty list gives it nothing to go on:

```python
names = []                  # list of what?

lookup = {}                 # dict of what to what?

typed_names: list[str] = []
typed_lookup: dict[str, int] = {}
typed_names.append("Asha")
typed_lookup["Asha"] = 21
```

```text
$ python -m mypy ch_coll5.py
ch_coll5.py:1: error: Need type annotation for "names" (hint: "names: list[<type>] = ...")  [var-annotated]
ch_coll5.py:3: error: Need type annotation for "lookup" (hint: "lookup: dict[<type>, <type>] = ...")  [var-annotated]
Found 2 errors in 1 file (checked 1 source file)
```

`Need type annotation` is mypy's way of asking "what do you plan to put in there?". The fix is one annotation at the point where the empty collection is created. A non-empty literal, such as `names = ["Asha"]`, needs no annotation: mypy reads it as `list[str]`.

### 7.5 Mixed contents and the `list[int]` versus `list[float]` surprise

A list that holds both ints and strings needs a union (section 10): `list[int | str]`. Prefer lists with a single kind of item; they are easier to hint and easier to work with.

Now the surprise. Since an `int` is accepted where a `float` is wanted, you might expect a `list[int]` to be accepted where a `list[float]` is wanted. It is not:

```python
def average(values: list[float]) -> float:
    return sum(values) / len(values)


whole_numbers: list[int] = [1, 2, 3]
print(average(whole_numbers))
print(average([1, 2, 3]))
```

```text
$ python -m mypy ch_coll6.py
ch_coll6.py:6: error: Argument 1 to "average" has incompatible type "list[int]"; expected "list[float]"  [arg-type]
ch_coll6.py:6: note: "list" is invariant -- see https://mypy.readthedocs.io/en/stable/common_issues.html#variance
ch_coll6.py:6: note: Consider using "Sequence" instead, which is covariant
Found 1 error in 1 file (checked 1 source file)
```

Why? A function that receives a `list[float]` is allowed to put a `2.5` *into* that list. If you had passed your `list[int]`, your list of ints would suddenly contain a float. The checker cannot allow that, so it says a list is **invariant**: `list[int]` and `list[float]` are different, unrelated types, even though `int` and `float` are related. (The second call, `average([1, 2, 3])`, is fine, because mypy sees the literal and treats it as a `list[float]` right there.)

The note says "Consider using Sequence". `Sequence` is a hint for "something list-like that you only read". You will meet it when you learn more about the standard library. For now, if this error appears, the simplest fix is to write the hint of the variable to match what the function wants (`list[float]`).

### 7.6 Try it

Write the hint for each of these values.

1. `[3.5, 4.0, 9.25]`
2. `{"asha": 21, "ravi": 22}`
3. `("red", 255, 0, 0)` (a colour name and three channels)
4. `(255, 128, 0, 64, 32)` (any number of channel values)
5. `{"asha": [70, 80], "ravi": []}`
6. `[("tea", 2.5), ("cake", 4.0)]`

<details><summary>Answer</summary>

1. `list[float]`
2. `dict[str, int]`
3. `tuple[str, int, int, int]`: four positions with different meanings. (Do not use `tuple[str | int, ...]`; it loses the fixed shape.)
4. `tuple[int, ...]`
5. `dict[str, list[int]]`. The empty list for `"ravi"` is fine once the type is declared.
6. `list[tuple[str, float]]`

```python
a: list[float] = [3.5, 4.0, 9.25]
b: dict[str, int] = {"asha": 21, "ravi": 22}
c: tuple[str, int, int, int] = ("red", 255, 0, 0)
d: tuple[int, ...] = (255, 128, 0, 64, 32)
e: dict[str, list[int]] = {"asha": [70, 80], "ravi": []}
f: list[tuple[str, float]] = [("tea", 2.5), ("cake", 4.0)]
```

```text
$ python -m mypy ch_coll7.py
Success: no issues found in 1 source file
```

</details>

## 8. Functions that return nothing

### 8.1 `-> None`

Many functions do something (print, change a list, write a file) and return nothing useful. Their return hint is `-> None`:

```python
def show_total(prices: list[float]) -> None:
    print("Total:", sum(prices))


def add_item(items: list[str], item: str) -> None:
    items.append(item)


cart: list[str] = []
add_item(cart, "tea")
show_total([2.5, 4.0])
print(cart)
```

```text
$ python ch_none1.py
Total: 6.5
['tea']
```

```text
$ python -m mypy ch_none1.py
Success: no issues found in 1 source file
```

Always write `-> None` for such a function. If you write nothing, mypy treats the return type as unknown and stops checking how the function's result is used (more in section 13). Writing `-> None` is a promise that a caller must not use the result.

### 8.2 The classic mistake: using a `None` result

Because `print`, `list.append`, `list.sort` and your own `-> None` functions return `None`, assigning their result is almost always a bug:

```python
def add_item(items: list[str], item: str) -> None:
    items.append(item)


cart: list[str] = ["tea"]
new_cart = add_item(cart, "cake")
print(new_cart)

numbers = [3, 1, 2]
ordered = numbers.sort()
print(ordered)
```

Predict what each `print` shows, and which lines mypy flags.

<details><summary>Answer</summary>

```text
$ python ch_none2.py
None
None
```

```text
$ python -m mypy ch_none2.py
ch_none2.py:6: error: "add_item" does not return a value (it only ever returns None)  [func-returns-value]
Found 1 error in 1 file (checked 1 source file)
```

Both print `None`. mypy flags the first assignment, because `add_item` is declared `-> None`. It stays silent about the second one: mypy is not all-seeing, and it makes an exception for a few very common built-in methods such as `list.sort()`. So the lesson is not "mypy will always catch it". The lesson is to know the rule yourself: `list.sort()` sorts **in place** and returns `None`; the function that returns a new sorted list is `sorted(...)`. This is a real bug you may have already made once in core.05.

</details>

### 8.3 A function that sometimes returns something

If a function returns a value on some paths and nothing on others, the return type is **not** `-> None`. It is `-> int | None` or similar. That is the next section.


## 9. Optional values: `X | None`

### 9.1 The most common bug in programming

Many functions can fail to find an answer. `dict.get` returns `None` for a missing key. A search function returns `None` when nothing matches. Reading a setting that was never set gives "nothing". Python uses the single value `None` for "no value here". Programmers constantly forget that `None` is a possible result, and then they call a method on it:

```text
AttributeError: 'NoneType' object has no attribute 'upper'
```

You have probably met this error already. It happens at runtime, often far from the real cause. Type hints let you say "this might be `None`", and then mypy forces you to deal with it **before** the program runs.

### 9.2 Writing it: `str | None`

You write a union with a vertical bar `|`, read as "or". `str | None` means "a `str`, or `None`".

```python
def find_user(users: dict[str, str], user_id: str) -> str | None:
    if user_id in users:
        return users[user_id]
    return None


users = {"u1": "Asha", "u2": "Ravi"}
print(find_user(users, "u1"))
print(find_user(users, "u9"))
```

```text
$ python ch_opt1.py
Asha
None
```

```text
$ python -m mypy ch_opt1.py
Success: no issues found in 1 source file
```

The `|` spelling works in Python 3.10 and later. This course uses Python 3.11 or later, so you can always use it.

> **The older spelling.** In older code and tutorials you will see `Optional[str]`, imported with `from typing import Optional`. It means exactly the same as `str | None`. This course writes `str | None`, because it says what it means. When you read old code, translate `Optional[X]` in your head to `X | None`.

### 9.3 The error mypy gives, and why it is right

Now use the result of `find_user` without thinking about `None`:

```python
def find_user(users: dict[str, str], user_id: str) -> str | None:
    if user_id in users:
        return users[user_id]
    return None


users = {"u1": "Asha", "u2": "Ravi"}
name = find_user(users, "u1")
print(name.upper())
```

```text
$ python -m mypy ch_opt2.py
ch_opt2.py:9: error: Item "None" of "str | None" has no attribute "upper"  [union-attr]
Found 1 error in 1 file (checked 1 source file)
```

Read the message slowly: `Item "None" of "str | None" has no attribute "upper"`. The value is `str | None`. The `str` item has `.upper`. The `None` item does not. Because the value *might* be `None`, the call is not safe. And look at what Python does with this very file:

```text
$ python ch_opt2.py
ASHA
```

Python printed `ASHA`, because for `"u1"` the user exists. The program **works today**. It is a bug waiting for the day `find_user` returns `None`. mypy finds it without waiting for that day. This is the best example of what static checking buys you.

### 9.4 Narrowing: how to convince mypy it is safe

You make the code safe by **checking for `None` first**. After the check, mypy knows what the value is. This is called **narrowing**: inside the safe branch, the type is narrowed from `str | None` to just `str`.

**Way 1: `if x is None`, then return or fall through.**

```python
def find_user(users: dict[str, str], user_id: str) -> str | None:
    return users.get(user_id)


def shout_name(users: dict[str, str], user_id: str) -> str:
    name = find_user(users, user_id)
    if name is None:
        return "NOBODY"
    return name.upper()        # here name is a str, not None


print(shout_name({"u1": "Asha"}, "u1"))
print(shout_name({"u1": "Asha"}, "u9"))
```

```text
$ python ch_opt3.py
ASHA
NOBODY
```

```text
$ python -m mypy ch_opt3.py
Success: no issues found in 1 source file
```

mypy reads the `return` inside the `if`: if the code gets past it, `name` cannot be `None` any more. This "early return" pattern (also called a guard) keeps the rest of the function un-indented and is the most common way to narrow.

Always compare with **`is None`** and **`is not None`**, not `== None`. `None` is a single object, and `is` tests identity. You met `is` in core.02.

**Way 2: `if x is not None:` around the use.**

```python
def label(name: str | None) -> str:
    if name is not None:
        return "Name: " + name
    return "Name: unknown"


print(label("Asha"))
print(label(None))
```

```text
$ python -m mypy ch_opt4.py
Success: no issues found in 1 source file
```

```text
$ python ch_opt4.py
Name: Asha
Name: unknown
```

**Way 3: give a default with `or`, when the "empty" values are all unwanted.**

```python
def display(name: str | None) -> str:
    return name or "anonymous"


print(display("Asha"))
print(display(None))
print(display(""))
```

```text
$ python -m mypy ch_opt5.py
Success: no issues found in 1 source file
```

```text
$ python ch_opt5.py
Asha
anonymous
anonymous
```

Note the third line: `""` is **falsy**, so `or` replaced the empty string too. That is fine if you want it, and a bug if an empty string is a valid value. The same trap hits numbers: `count or 10` replaces a legitimate `0`. When `0` or `""` are valid answers, use `is None`.

**Way 4: `assert x is not None`.** An `assert` tells both the reader and mypy "this cannot be `None` here". At runtime, a false assert raises `AssertionError`, so use it only for things that are truly impossible, not for user input:

```python
def first_word(text: str | None) -> str:
    assert text is not None, "text must be given"
    return text.split()[0]


print(first_word("hello world"))
```

```text
$ python -m mypy ch_opt6.py
Success: no issues found in 1 source file
```

**Way 5: `dict.get` with a default.** When a dict lookup has a sensible default, give it, and the `None` never appears:

```python
ages: dict[str, int] = {"asha": 21}

maybe = ages.get("ravi")            # int | None
sure = ages.get("ravi", 0)          # int
print(maybe, sure)
reveal_type(maybe)
reveal_type(sure)
```

```text
$ python -m mypy ch_opt7.py
ch_opt7.py:6: note: Revealed type is "int | None"
ch_opt7.py:7: note: Revealed type is "int"
Success: no issues found in 1 source file
```

(`reveal_type` is explained in section 12. It makes mypy print the type it has worked out. It only exists inside mypy, so this file would crash if you ran it with Python.)

### 9.5 `Optional` does not mean "optional parameter"

This is the most common confusion. The word `Optional` sounds as if it describes a parameter that you may leave out. It does **not**. It only says "the value may be `None`". Whether you can *omit* the argument depends only on whether it has a **default value**.

```python
def a(x: str | None) -> str:        # must be given, may be None
    return "a:" + str(x)


def b(x: str = "none") -> str:      # may be omitted, can never be None
    return "b:" + x


def c(x: str | None = None) -> str:  # may be omitted, may be None
    return "c:" + str(x)


print(a(None))
print(b())
print(c())
print(a())
```

```text
$ python -m mypy ch_opt8.py
ch_opt8.py:16: error: Missing positional argument "x" in call to "a"  [call-arg]
Found 1 error in 1 file (checked 1 source file)
```

```text
$ python ch_opt8.py
a:None
b:none
c:None
Traceback (most recent call last):
  File "/home/you/project/ch_opt8.py", line 16, in <module>
    print(a())
          ~^^
TypeError: a() missing 1 required positional argument: 'x'
```

`a` says "None is allowed", yet you still *must* pass something, so `a()` fails. Only `c` is both: it has a default value (`= None`), and its hint admits `None`.

Note that `def f(x: str = None)` is an error in mypy, because the default `None` does not fit `str`. Older tools allowed that; modern mypy does not:

```python
def greet(name: str = None) -> str:
    return "hi " + str(name)
```

```text
$ python -m mypy ch_opt9.py
ch_opt9.py:1: error: Incompatible default for parameter "name" (default has type "None", parameter has type "str")  [assignment]
ch_opt9.py:1: note: PEP 484 prohibits implicit Optional. Accordingly, mypy has changed its default to no_implicit_optional=True
ch_opt9.py:1: note: Use https://github.com/hauntsaninja/no_implicit_optional to automatically upgrade your codebase
Found 1 error in 1 file (checked 1 source file)
```

### 9.6 A function that returns "maybe a value"

Remember section 8.3. A function that returns a value on some paths and falls off the end (returning `None` automatically) on others is an `X | None` function, and you should say so, and preferably write the `return None` out so that the reader sees it:

```python
def first_even(numbers: list[int]) -> int | None:
    for n in numbers:
        if n % 2 == 0:
            return n
    return None


print(first_even([1, 3, 4, 6]))
print(first_even([1, 3]))
```

```text
$ python ch_opt10.py
4
None
```

```text
$ python -m mypy ch_opt10.py
Success: no issues found in 1 source file
```

Now a call such as `first_even(data) + 1` is flagged until the caller checks for `None`. That is exactly the discipline you want.

### 9.7 Try it

Which of the lines marked A to D does mypy flag? (Think about narrowing.)

```python
def f(text: str | None) -> int:
    n = len(text)                 # A
    if text is None:
        return 0
    return len(text)              # B

def g(text: str | None) -> int:
    if not text:
        return 0
    return len(text)              # C

def h(text: str | None) -> int:
    if text is None:
        print("no text")
    return len(text)              # D
```

<details><summary>Answer</summary>

```python
def f(text: str | None) -> int:
    n = len(text)                 # A
    if text is None:
        return 0
    return len(text)              # B

def g(text: str | None) -> int:
    if not text:
        return 0
    return len(text)              # C

def h(text: str | None) -> int:
    if text is None:
        print("no text")
    return len(text)              # D
```

```text
$ python -m mypy ch_opt11.py
ch_opt11.py:2: error: Argument 1 to "len" has incompatible type "str | None"; expected "Sized"  [arg-type]
ch_opt11.py:15: error: Argument 1 to "len" has incompatible type "str | None"; expected "Sized"  [arg-type]
Found 2 errors in 1 file (checked 1 source file)
```

**A** (file line 2): flagged, the check comes too late. **B**: fine. **C**: fine, `if not text` covers both `None` and `""`, so after it `text` is a non-empty `str`. **D** (file line 15): flagged. The `if` branch prints, but does not `return`, so after the `if` the value may still be `None`. A narrowing branch must *leave* the function (or assign a new value), not just "handle" the case.

</details>

## 10. Unions in general

`|` is not only for `None`. It joins any types: `int | str` is "an int or a str".

```python
def describe(value: int | str) -> str:
    return "value is " + str(value)


print(describe(7))
print(describe("seven"))
```

```text
$ python -m mypy ch_union1.py
Success: no issues found in 1 source file
```

```text
$ python ch_union1.py
value is 7
value is seven
```

You can use `str(value)` because *every* member of the union supports it. If you use something that only some members support, mypy objects, exactly as with `None`:

```python
def shout(value: int | str) -> str:
    return value.upper()


def shout_safe(value: int | str) -> str:
    if isinstance(value, str):
        return value.upper()
    return str(value)
```

```text
$ python -m mypy ch_union2.py
ch_union2.py:2: error: Item "int" of "int | str" has no attribute "upper"  [union-attr]
Found 1 error in 1 file (checked 1 source file)
```

`isinstance(value, str)` narrows the union, in the same way `is None` did: inside the `if`, `value` is a `str`, and after it, mypy knows it must be an `int`.

Two good rules for unions:

1. A union is a sign that the function must **branch** on what it received. If you find yourself writing a union with many members, ask whether the function is doing too much.
2. Avoid mixing unrelated types in a collection (`list[int | str]`). They are hard to use safely, because every use needs an `isinstance` check.

You can annotate a variable with a union too: `result: int | None = None`.

### 10.1 Try it

What is the hint for a function `parse(text)` that returns an `int` when `text` is all digits, and the string `"error"` otherwise? And how must a caller handle the result?

<details><summary>Answer</summary>

`def parse(text: str) -> int | str:`. The caller has to check, usually with `isinstance(result, int)`, before using the result as a number. (A more convenient design is usually to return `int | None`, or to raise `ValueError`. Returning two unrelated types forces every caller to branch.)

```python
def parse(text: str) -> int | str:
    if text.isdigit():
        return int(text)
    return "error"


result = parse("42")
print(result + 1)
```

```text
$ python -m mypy ch_union3.py
ch_union3.py:8: error: Unsupported operand types for + ("str" and "int")  [operator]
ch_union3.py:8: note: Left operand is of type "int | str"
Found 1 error in 1 file (checked 1 source file)
```

mypy flags the `+ 1`, because `result` might be a `str`. That is the "two unrelated types" cost in action.

</details>

## 11. Functions as parameters: `Callable`, and `Any`

In core.06 you passed functions to other functions (`map`, `sorted(key=...)`, your own `apply`). A parameter that is a function is hinted with `Callable`, imported from `collections.abc`:

```python
from collections.abc import Callable
```

The syntax is `Callable[[ARGUMENT TYPES], RETURN TYPE]`. The argument types go inside **their own square brackets**, then a comma, then the return type.

| Hint | Meaning |
|---|---|
| `Callable[[int], int]` | takes one `int`, returns an `int` |
| `Callable[[str, int], bool]` | takes a `str` and an `int`, returns a `bool` |
| `Callable[[], str]` | takes nothing, returns a `str` |
| `Callable[..., int]` | takes anything, returns an `int` (arguments unchecked) |

```python
from collections.abc import Callable


def apply_all(func: Callable[[int], int], numbers: list[int]) -> list[int]:
    return [func(n) for n in numbers]


def double(n: int) -> int:
    return n * 2


print(apply_all(double, [1, 2, 3]))
print(apply_all(lambda n: n + 10, [1, 2, 3]))
print(apply_all(abs, [-4, 5]))
```

```text
$ python ch_call1.py
[2, 4, 6]
[11, 12, 13]
[4, 5]
```

```text
$ python -m mypy ch_call1.py
Success: no issues found in 1 source file
```

A `lambda` cannot carry annotations itself; mypy works out its types from the place where it is used. Passing the wrong function is caught:

```python
from collections.abc import Callable


def apply_all(func: Callable[[int], int], numbers: list[int]) -> list[int]:
    return [func(n) for n in numbers]


def shout(text: str) -> str:
    return text.upper()


def add(a: int, b: int) -> int:
    return a + b


print(apply_all(shout, [1, 2]))     # takes str, returns str
print(apply_all(add, [1, 2]))       # takes two arguments
```

```text
$ python -m mypy ch_call2.py
ch_call2.py:16: error: Argument 1 to "apply_all" has incompatible type "Callable[[str], str]"; expected "Callable[[int], int]"  [arg-type]
ch_call2.py:17: error: Argument 1 to "apply_all" has incompatible type "Callable[[int, int], int]"; expected "Callable[[int], int]"  [arg-type]
Found 2 errors in 1 file (checked 1 source file)
```

Both errors say that the callable passed in does not have the shape `Callable[[int], int]`. Read the two shapes in the message and compare them.

### 11.1 `Any`, once more

You already met `Any` in section 6.4. Its usual home is the places where you cannot say more: a function that takes "any kind of function", `Callable[..., Any]`, or data of unknown shape. Think of `Any` as a way to tell mypy "stop checking here". Use it sparingly, and prefer precise types.

## 12. Defaults, inference and `reveal_type`

### 12.1 Default values

A default value follows the hint, with spaces around the `=` when there is a hint (this is the style guide PEP 8's rule: `x: int = 5`, but `x=5` without a hint):

```python
def power(base: float, exponent: int = 2) -> float:
    return base ** exponent


def join(words: list[str], sep: str = " ") -> str:
    return sep.join(words)


print(power(3))
print(power(2, 10))
print(join(["a", "b"]), join(["a", "b"], sep="-"))
```

```text
$ python ch_def1.py
9
1024
a b a-b
```

```text
$ python -m mypy ch_def1.py
Success: no issues found in 1 source file
```

mypy also checks that the default fits the hint (as with `name: str = None` above).

### 12.2 The mutable default trap does not go away

A hint does not repair the old trap from core.06. A list as a default value is created **once**, when the function is defined, and shared by every call:

```python
def add_tag(tag: str, tags: list[str] = []) -> list[str]:
    tags.append(tag)
    return tags


print(add_tag("a"))
print(add_tag("b"))
```

Predict the two lines.

<details><summary>Answer</summary>

```text
$ python ch_def2.py
['a']
['a', 'b']
```

```text
$ python -m mypy ch_def2.py
Success: no issues found in 1 source file
```

The second call shows `['a', 'b']`: the default list survived the first call. mypy is satisfied, since `[]` really is a `list[str]`. The hint cannot see the trap. The fix is the same as before: use `None` as the default and create the list inside.

```python
def add_tag(tag: str, tags: list[str] | None = None) -> list[str]:
    if tags is None:
        tags = []
    tags.append(tag)
    return tags


print(add_tag("a"))
print(add_tag("b"))
```

```text
$ python ch_def3.py
['a']
['b']
```

```text
$ python -m mypy ch_def3.py
Success: no issues found in 1 source file
```

Here `X | None = None` is exactly the right use: `None` means "not given".

</details>

### 12.3 Inference: what mypy works out by itself

mypy does not need a hint on every variable. It looks at the first assignment and remembers that type. A later assignment of a different type is flagged:

```python
count = 5
count = count + 1        # fine, still an int
count = "six"            # flagged: count was inferred as int

names = ["asha", "ravi"]
names.append(7)          # flagged: list[str] cannot take an int
```

```text
$ python -m mypy ch_inf1.py
ch_inf1.py:3: error: Incompatible types in assignment (expression has type "str", variable has type "int")  [assignment]
ch_inf1.py:6: error: Argument 1 to "append" of "list" has incompatible type "int"; expected "str"  [arg-type]
Found 2 errors in 1 file (checked 1 source file)
```

This catches a real mistake: a variable that "changes its type" is nearly always confusing. Python lets you do it, but mypy asks you to use a new name or a union.

Inference works for return values too. If you hint the parameters, mypy can often work out what comes back. But you should still write the `->` hint on your functions, as it is the part readers see first, and without it mypy treats the result as `Any`.

### 12.4 `reveal_type`: ask mypy what it thinks

When you are unsure what mypy has concluded, add `reveal_type(expression)`. mypy prints a `note:` with the type. Remove it when you are done, because it exists **only inside mypy**: running the file with Python raises `NameError`.

```python
scores = {"asha": [70, 80], "ravi": [60]}
reveal_type(scores)
reveal_type(scores["asha"])
reveal_type(scores.get("zed"))
reveal_type(max(scores["asha"]))
reveal_type([n * 1.5 for n in scores["ravi"]])
```

```text
$ python -m mypy ch_reveal1.py
ch_reveal1.py:2: note: Revealed type is "dict[str, list[int]]"
ch_reveal1.py:3: note: Revealed type is "list[int]"
ch_reveal1.py:4: note: Revealed type is "list[int] | None"
ch_reveal1.py:5: note: Revealed type is "int"
ch_reveal1.py:6: note: Revealed type is "list[float]"
Success: no issues found in 1 source file
```

```text
$ python ch_reveal1.py
Traceback (most recent call last):
  File "/home/you/project/ch_reveal1.py", line 2, in <module>
    reveal_type(scores)
    ^^^^^^^^^^^
NameError: name 'reveal_type' is not defined
```

`reveal_type` is the quickest way to learn how the rules behave. Whenever a message surprises you, reveal the type of the expression and compare.

## 13. Where mypy is lenient, and how to make it strict

### 13.1 Unannotated functions are not checked

Here is something that surprises people. mypy, by default, **skips the body of any function that has no annotations at all**, and it treats its parameters and result as `Any`. The reason is history: mypy was designed so that you could add hints to an old program one function at a time, without being flooded with errors.

```python
def add(a, b):                 # no hints at all
    return a + b + "!"         # nothing is checked in here


def add_typed(a: int, b: int) -> int:
    return a + b + "!"         # checked: flagged


print(add(1, 2))
```

```text
$ python -m mypy ch_lax1.py
ch_lax1.py:6: error: Unsupported operand types for + ("int" and "str")  [operator]
Found 1 error in 1 file (checked 1 source file)
```

mypy reports only `add_typed`. The function `add` contains an obvious bug (adding a string to numbers) and mypy shows nothing, because it is not annotated. Run the program and `add(1, 2)` crashes. So **"mypy passes" only means something where you added hints**. A file with no hints passes mypy trivially.

The same leniency applies to the **callers** of an unannotated function. The result is `Any`, so anything you do with it is accepted:

```python
def twice(x):
    return x * 2


result = twice("ab")
print(result + 1)              # "abab" + 1 is a crash, but result is Any
```

```text
$ python -m mypy ch_lax2.py
Success: no issues found in 1 source file
```

```text
$ python ch_lax2.py
Traceback (most recent call last):
  File "/home/you/project/ch_lax2.py", line 6, in <module>
    print(result + 1)              # "abab" + 1 is a crash, but result is Any
          ~~~~~~~^~~
TypeError: can only concatenate str (not "int") to str
```

### 13.2 Making mypy insist

You turn the leniency off with options.

| Option | Effect |
|---|---|
| `--disallow-untyped-defs` | Error for every function missing a hint on a parameter or the return value |
| `--disallow-incomplete-defs` | Error for a function that is only partly annotated |
| `--check-untyped-defs` | Check the *bodies* of unannotated functions anyway |
| `--strict` | A bundle of many strict options, including those above |

```python
def add(a, b):
    return a + b + "!"


def half(n: int):              # return hint missing
    return n / 2
```

```text
$ python -m mypy --disallow-untyped-defs ch_lax3.py
ch_lax3.py:1: error: Function is missing a type annotation  [no-untyped-def]
ch_lax3.py:5: error: Function is missing a return type annotation  [no-untyped-def]
Found 2 errors in 1 file (checked 1 source file)
```

```text
$ python -m mypy --strict ch_lax3.py
ch_lax3.py:1: error: Function is missing a type annotation  [no-untyped-def]
ch_lax3.py:5: error: Function is missing a return type annotation  [no-untyped-def]
Found 2 errors in 1 file (checked 1 source file)
```

Both options force you to write the hints on every function, and `--strict` goes further (it has more checks than this small file shows). For a new project of your own, running with `--strict` from the start is a good habit: it is much easier than adding it later.

### 13.3 A settings file

Instead of typing options every time, you can put them in a file named `mypy.ini` next to your code:

```ini
[mypy]
strict = True
```

Then `python -m mypy my_file.py` reads it automatically. (mypy can also read `pyproject.toml`. Keep this to a separate `mypy.ini` in your own projects, so you do not touch settings of other tools.)

### 13.4 What mypy cannot see even in strict mode

Strict mode is thorough about *types*, but it still knows nothing about **values**. All of these pass `--strict`:

```python
def average(numbers: list[int]) -> float:
    return sum(numbers) / len(numbers)      # ZeroDivisionError for []


def third(numbers: list[int]) -> int:
    return numbers[2]                       # IndexError for short lists


def to_int(text: str) -> int:
    return int(text)                        # ValueError for "abc"


print(to_int("12"))
```

```text
$ python -m mypy --strict ch_lax4.py
Success: no issues found in 1 source file
```

Every one of those can crash with the right input, and mypy is happy. Types are one tool. Tests (core.08) and error handling (core.07) are the others, and none of them replaces the rest.

### 13.5 Try it

You run `python -m mypy shop.py` and get `Success: no issues found`. Your friend says the file is therefore safe. Give two reasons why that conclusion is too strong.

<details><summary>Answer</summary>

1. The file may contain functions without hints. mypy skips their bodies by default, so "no issues" says nothing about them. Re-run with `--strict` (or `--disallow-untyped-defs`) to find them.
2. Types do not describe values. `average([])`, `int("abc")` and `numbers[5]` are all fine for mypy and all crash at runtime. Also, `Any` and `# type: ignore` switch checks off locally. And data from outside the program (files, input) is not checked by the hints at all.

</details>


## 14. When you need a real runtime check

### 14.1 Hints for the programmer, checks for the boundary

If you want the program itself to refuse a wrong type, you must write the check. The tool is `isinstance`, which you know from core.04, and the exception for "wrong type" is `TypeError`, which you know from core.07:

```python
def set_age(age: int) -> int:
    if not isinstance(age, int):
        raise TypeError("age must be an int, got " + type(age).__name__)
    if age < 0:
        raise ValueError("age must not be negative")
    return age


print(set_age(21))
try:
    set_age("21")
except TypeError as error:
    print("TypeError:", error)
```

```text
$ python ch_rt1.py
21
TypeError: age must be an int, got str
```

```text
$ python -m mypy ch_rt1.py
ch_rt1.py:11: error: Argument 1 to "set_age" has incompatible type "str"; expected "int"  [arg-type]
Found 1 error in 1 file (checked 1 source file)
```

Ask yourself: if mypy already guarantees `age` is an `int`, why check again? Because mypy only checks code **you run it on**, and only what is **written**. A caller in an unannotated file, a value read from a file, a number typed by the user, JSON from the internet: none of these pass through mypy at the moment the program runs. The sensible split is:

- **Inside your program**, between your own annotated functions, trust the hints and let mypy police them.
- **At the boundary**, where data enters (`input()`, files, network, other people's code that may not use hints), check at runtime and convert: `int(text)` inside a `try`, `isinstance` for values of unknown kind.

You can think of a hint as a promise made by the *caller*, and a runtime check as the *function* refusing to trust it. Libraries such as **pydantic**, which you may meet later, automate the second part: they read your hints and check the real data against them while the program runs. Their whole reason to exist is that Python itself does not do this.

### 14.2 What a runtime check can and cannot say

Python can only check what a value *is* right now. It cannot check the inside of a `list[int]` cheaply:

```python
numbers = [1, 2, "three"]

print(isinstance(numbers, list))
print(all(isinstance(n, int) for n in numbers))
```

```text
$ python ch_rt2.py
True
False
```

`isinstance(numbers, list)` is `True`, and says nothing about the items. (Also, `isinstance(x, list[int])` is not allowed: the bracketed form exists for the hint, not for the check.) To check the contents you must look at each item, as the second line does. That costs time, which is one more reason why checks belong at the boundary and not in every call.

### 14.3 The `bool` trap, again

Because `True` is an `int`, a check meant to reject booleans must ask about `bool` first:

```python
def positive_int(value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError("expected a real int")
    if value <= 0:
        raise ValueError("expected a positive number")
    return value


print(positive_int(5))
for bad in (True, 2.5, "7"):
    try:
        positive_int(bad)
    except TypeError as error:
        print(repr(bad), "->", error)
```

```text
$ python ch_rt3.py
5
True -> expected a real int
2.5 -> expected a real int
'7' -> expected a real int
```

```text
$ python -m mypy ch_rt3.py
Success: no issues found in 1 source file
```

Notice the parameter type `object`: the function accepts anything on purpose, because its job is to look at an unknown value and decide. After the `isinstance` checks, mypy knows that `value` is an `int`, so `return value` is accepted.

### 14.4 Try it

`def half(n: int) -> float` returns `n / 2`. A user writes `half("8")`. What happens with Python alone, and what would you do to make the function itself reject strings with a clear message?

<details><summary>Answer</summary>

With Python alone, `"8" / 2` raises `TypeError: unsupported operand type(s) for /: 'str' and 'int'`: a crash from the operator, not a message about the hint. To reject it clearly, add an explicit check at the start:

```python
def half(n: int) -> float:
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError("n must be an int")
    return n / 2


print(half(8))
try:
    half("8")
except TypeError as error:
    print("TypeError:", error)
```

```text
$ python ch_rt4.py
4.0
TypeError: n must be an int
```

Whether to add the check at all depends on who calls the function. For an internal helper, the hint is enough. For a function that receives raw data from outside, add the check.

</details>

## 15. Silencing mypy: `# type: ignore`

Sometimes mypy complains about a line you know is correct, or a line in a test that is deliberately wrong. A comment at the end of the line tells mypy to skip errors on that line:

```python
def add(a: int, b: int) -> int:
    return a + b


print(add("2", "3"))                       # type: ignore
print(add("2", "3"))                       # type: ignore[arg-type]
print(add("2", "3"))
```

```text
$ python -m mypy ch_ign1.py
ch_ign1.py:7: error: Argument 1 to "add" has incompatible type "str"; expected "int"  [arg-type]
ch_ign1.py:7: error: Argument 2 to "add" has incompatible type "str"; expected "int"  [arg-type]
Found 2 errors in 1 file (checked 1 source file)
```

Only line 7 is reported (with two messages, because both arguments are wrong). The comment is plain text to Python; it affects nothing at runtime. Rules for using it:

1. **Use it rarely, and as a last resort.** Each one is a hole in the safety net. First try to fix the hint or the code.
2. **Prefer the narrow form** with the error code, `# type: ignore[arg-type]`, so that a *different* error on the same line is still reported.
3. **Say why**, in a short comment next to it, so a reader knows it was deliberate.
4. A good use: a test that **intentionally passes a wrong type** to see how the function reacts (section 16).

If you turn on `--strict`, mypy also complains about ignore comments that are no longer needed (`warn_unused_ignores`), which keeps them from piling up.

## 16. Hints and tests work together

Hints and tests catch **different** bugs, and neither replaces the other.

| Question | Hints and mypy | Tests (pytest) |
|---|---|---|
| Did I pass a `str` where an `int` is needed, anywhere in the program? | Yes, everywhere, at once | Only on the paths the tests run |
| Does `average([1, 2, 3])` return `2.0`? | No idea | Yes |
| Does `average([])` crash? | No idea | Yes, if you write the test |
| Do all callers handle `None` from `find_user`? | Yes | Only if you test each caller |

A test that deliberately passes a wrong type needs the ignore comment, otherwise mypy would reject your test file:

```python
import pytest


def half(n: int) -> float:
    if isinstance(n, bool) or not isinstance(n, int):
        raise TypeError("n must be an int")
    return n / 2


def test_half_rejects_text():
    with pytest.raises(TypeError, match="int"):
        half("8")  # type: ignore[arg-type]  # deliberately wrong
```

```text
$ python -m pytest -q ch_test1.py
.                                                                        [100%]
1 passed in 0.01s
```

(You did not need to install any extra tool for the tests of this module: the checks on your hints use Python's own `__annotations__` and the `inspect` module.)

## 17. Project: add type hints to a real program, step by step

The project of this module is to add type hints to **two of your earlier projects** and make mypy pass. Do not do it with a big bang. This section walks through one small program, so that you can use the same steps on yours.

### 17.1 Step 0: the program as it is

Here is a small gradebook program with no hints at all. Lines like `"asha, 70"` go in, an average per student and the best student come out.

```python
def parse_line(line):
    name, score = line.split(",")
    return name.strip(), int(score)


def load(lines):
    book = {}
    for line in lines:
        name, score = parse_line(line)
        book.setdefault(name, []).append(score)
    return book


def average(scores):
    return sum(scores) / len(scores)


def best_student(book):
    best = None
    best_avg = -1
    for name, scores in book.items():
        avg = average(scores)
        if avg > best_avg:
            best, best_avg = name, avg
    return best


def report(book):
    for name in sorted(book):
        print(name, round(average(book[name]), 1))


data = ["asha, 70", "ravi, 60", "asha, 90", "ravi, 65"]
book = load(data)
report(book)
print("Best:", best_student(book).upper())
```

```text
$ python gradebook.py
asha 80.0
ravi 62.5
Best: ASHA
```

It works. Now ask mypy:

```text
$ python -m mypy gradebook.py
Success: no issues found in 1 source file
```

`Success`. But we learned in section 13 that this means nothing here: no function has a hint, so mypy skipped every body. We need the strict view.

### 17.2 Step 1: find what is missing

```text
$ python -m mypy --disallow-untyped-defs gradebook.py
gradebook.py:1: error: Function is missing a type annotation  [no-untyped-def]
gradebook.py:6: error: Function is missing a type annotation  [no-untyped-def]
gradebook.py:14: error: Function is missing a type annotation  [no-untyped-def]
gradebook.py:18: error: Function is missing a type annotation  [no-untyped-def]
gradebook.py:28: error: Function is missing a type annotation  [no-untyped-def]
Found 5 errors in 1 file (checked 1 source file)
```

This gives you the **to-do list**: four functions to annotate. (The variable `book` at the bottom is fine.) Work through them **from the bottom up**: start with the small helper functions that call nothing else, then the functions that call them. That way, when you annotate a function you already know the types of what it calls.

### 17.3 Step 2: annotate the helpers

Look at what each function really receives and returns:

- `parse_line(line)`: receives a `str` such as `"asha, 70"`. Returns a pair: the name (a `str`) and the score (an `int`). A fixed two-item tuple: `tuple[str, int]`.
- `average(scores)`: receives a list of ints, returns a float (`/` always gives a float).

```python
def parse_line(line: str) -> tuple[str, int]:
    name, score = line.split(",")
    return name.strip(), int(score)


def average(scores: list[int]) -> float:
    return sum(scores) / len(scores)
```

```text
$ python -m mypy --strict gradebook1.py
Success: no issues found in 1 source file
```

### 17.4 Step 3: annotate `load` and meet `[var-annotated]`

`load` receives a list of lines and returns a dict from names to lists of scores. The hint is `-> dict[str, list[int]]`. We also have to say what the empty dict `book = {}` is for:

```python
def parse_line(line: str) -> tuple[str, int]:
    name, score = line.split(",")
    return name.strip(), int(score)


def load(lines: list[str]) -> dict[str, list[int]]:
    book = {}
    for line in lines:
        name, score = parse_line(line)
        book.setdefault(name, []).append(score)
    return book
```

```text
$ python -m mypy --strict gradebook2.py
gradebook2.py:7: error: Need type annotation for "book" (hint: "book: dict[<type>, <type>] = ...")  [var-annotated]
Found 1 error in 1 file (checked 1 source file)
```

mypy asks the question from section 7.4. Answer it at the point where the dict is created:

```python
def parse_line(line: str) -> tuple[str, int]:
    name, score = line.split(",")
    return name.strip(), int(score)


def load(lines: list[str]) -> dict[str, list[int]]:
    book: dict[str, list[int]] = {}
    for line in lines:
        name, score = parse_line(line)
        book.setdefault(name, []).append(score)
    return book
```

```text
$ python -m mypy --strict gradebook3.py
Success: no issues found in 1 source file
```

### 17.5 Step 4: annotate `best_student` and find a real bug

`best_student` returns a name, so `-> str`? Look at the code: it starts with `best = None` and only replaces it inside the loop. If the book is empty, the loop never runs and `None` is returned. So the honest hint is `str | None`. Write it, and annotate the others:

```python
def parse_line(line: str) -> tuple[str, int]:
    name, score = line.split(",")
    return name.strip(), int(score)


def load(lines: list[str]) -> dict[str, list[int]]:
    book: dict[str, list[int]] = {}
    for line in lines:
        name, score = parse_line(line)
        book.setdefault(name, []).append(score)
    return book


def average(scores: list[int]) -> float:
    return sum(scores) / len(scores)


def best_student(book: dict[str, list[int]]) -> str | None:
    best = None
    best_avg = -1
    for name, scores in book.items():
        avg = average(scores)
        if avg > best_avg:
            best, best_avg = name, avg
    return best


def report(book: dict[str, list[int]]) -> None:
    for name in sorted(book):
        print(name, round(average(book[name]), 1))


data = ["asha, 70", "ravi, 60", "asha, 90", "ravi, 65"]
book = load(data)
report(book)
print("Best:", best_student(book).upper())
```

```text
$ python -m mypy --strict gradebook4.py
gradebook4.py:24: error: Incompatible types in assignment (expression has type "float", variable has type "int")  [assignment]
gradebook4.py:36: error: Item "None" of "str | None" has no attribute "upper"  [union-attr]
Found 2 errors in 1 file (checked 1 source file)
```

This is the payoff of the whole chapter. mypy reports two things.

- **Line 36**, the big one. By writing the honest hint `str | None`, we made mypy find a bug: `best_student(book).upper()` crashes with `AttributeError` when the book is empty. The program "worked" on our sample data only because the sample was not empty.
- **Line 24**, a smaller one. `best_avg = -1` made mypy infer `int` (section 12.3). Later the loop stores a `float` average in it. Python does not care, but the variable changes its type, which is exactly what inference-based checking flags. The fix is to start with `-1.0`.

Prove the first bug with an empty book (importing the file also runs its report lines first, which is why they print above the error):

```python
from gradebook4 import best_student

print(best_student({}).upper())
```

```text
$ python gradebook_empty.py
asha 80.0
ravi 62.5
Best: ASHA
Traceback (most recent call last):
  File "/home/you/project/gradebook_empty.py", line 3, in <module>
    print(best_student({}).upper())
          ^^^^^^^^^^^^^^^^^^^^^^
AttributeError: 'NoneType' object has no attribute 'upper'
```

### 17.6 Step 5: fix the code, not just the hint

The hint was right; the **caller** was wrong. Handle the `None`:

```python
def parse_line(line: str) -> tuple[str, int]:
    name, score = line.split(",")
    return name.strip(), int(score)


def load(lines: list[str]) -> dict[str, list[int]]:
    book: dict[str, list[int]] = {}
    for line in lines:
        name, score = parse_line(line)
        book.setdefault(name, []).append(score)
    return book


def average(scores: list[int]) -> float:
    return sum(scores) / len(scores)


def best_student(book: dict[str, list[int]]) -> str | None:
    best: str | None = None
    best_avg = -1.0
    for name, scores in book.items():
        avg = average(scores)
        if avg > best_avg:
            best, best_avg = name, avg
    return best


def report(book: dict[str, list[int]]) -> None:
    for name in sorted(book):
        print(name, round(average(book[name]), 1))


def main() -> None:
    data = ["asha, 70", "ravi, 60", "asha, 90", "ravi, 65"]
    book = load(data)
    report(book)
    winner = best_student(book)
    if winner is None:
        print("No students yet")
    else:
        print("Best:", winner.upper())


main()
```

```text
$ python -m mypy --strict gradebook5.py
Success: no issues found in 1 source file
```

```text
$ python gradebook5.py
asha 80.0
ravi 62.5
Best: ASHA
```

We also moved the top-level code into a `main()` function, annotated `-> None`, wrote `best: str | None = None` so the variable says outright what it can hold, and changed `best_avg = -1` to `-1.0`, which fixes the line 24 error. The output is the same as in step 0, which is what we want: adding hints must not change what the program does.

### 17.7 The recipe for your own two projects

1. **Run the program** and keep a copy of its output, so that you can see that adding hints changes nothing at runtime (it must not).
2. **Run mypy with `--disallow-untyped-defs`** (or `--strict`) to get the to-do list.
3. **Annotate bottom-up**: small helpers first. Write the *honest* type: if a function can return `None`, say `X | None`.
4. **Run mypy after every function or two**, not at the end. Fix the first error first.
5. For each error decide: is the **hint** wrong, or is the **code** wrong? Real bugs found this way are the reward. (If you must silence one, use `# type: ignore[code]` with a comment.)
6. **Run the tests** (core.08) if you have them, and run the program again. The output should be as before.
7. Leave `reveal_type` calls out of the final file.

## 18. Common traps

1. **Believing the interpreter checks hints.** It does not. `add("a", "b")` runs. Only mypy (or another checker you run) rejects it.
2. **Thinking "mypy passes" means "the code is correct".** It only says that the *hints fit together*, in the functions that have hints. Unannotated functions are skipped, and `Any` and `# type: ignore` are holes.
3. **Forgetting `-> None`.** An unannotated return means "unknown" to mypy, which switches off some checks.
4. **Using a `str | None` value without narrowing.** The classic `Item "None" of "str | None" has no attribute ...` error. Check with `is None`, `is not None`, or an early return.
5. **Using `if x:` for "is not None".** `0`, `""` and `[]` are falsy but may be valid values. Use `is None`.
6. **Confusing `Optional` with "optional parameter".** It means "may be `None`". An argument may be omitted only if it has a default.
7. **`def f(x: list = [])`.** The mutable default is still shared between calls. Use `None` and create the list inside.
8. **Hinting `list` where you mean `list[int]`.** A bare `list` hides the item type, and mypy then cannot help with it.
9. **Using a fixed tuple for a growing sequence**, or `tuple[int, ...]` for a record. Fixed shape for a record, `...` for "any number".
10. **Annotating an empty collection too late.** `items = []` needs `items: list[str] = []` at that line.
11. **Expecting `list[int]` to fit `list[float]`.** A list is invariant. Match the types exactly, or hint the variable as `list[float]` from the start.
12. **Expecting `isinstance(x, list[int])` to work.** Only the plain class names work with `isinstance`.
13. **Forgetting that `bool` is an `int`.** `isinstance(True, int)` is `True`, and mypy lets `True` in where an `int` is wanted.
14. **Using the old names** (`List`, `Dict`, `Optional`) in new code. Write `list[...]`, `dict[...]`, `X | None`.
15. **Quoting types** like `"int"`. Not needed in this course.
16. **Leaving `reveal_type` in a file.** It works only under mypy and raises `NameError` in Python.
17. **Treating a hint as validation of input.** Data from `input()`, files and the network is not checked by any hint. Parse it and check it at the boundary.
18. **Sprinkling `# type: ignore` to get a green result.** You then have the look of safety without the safety.

## 19. Summary

- A **type hint** is a note about what a value should be: `name: str`, `-> int`, `list[int]`, `dict[str, float]`, `tuple[int, ...]`, `str | None`.
- **Python ignores hints at runtime.** `add("a", "b")` runs even if `add` says `int`. Hints are stored in `__annotations__` and read by tools.
- **mypy** is a *static* checker: it reads your code without running it and reports mismatches. Install it with `pip install mypy`, run it with `python -m mypy file.py`. Reading an error: `file:line: error: message  [code]`.
- Common errors: `[arg-type]` wrong argument, `[return-value]` wrong return, `[assignment]` wrong value for a variable, `[return]` missing return, `[var-annotated]` empty collection, `[union-attr]` forgot `None`, `[func-returns-value]` using a `-> None` result.
- `float` accepts an `int`, and `int` accepts a `bool`. A `list[int]` does **not** fit a `list[float]`.
- `X | None` means "may be `None`". Narrow it with `is None` / `is not None` / an early return before use. `Optional[X]` is the old spelling of the same thing, and does **not** mean "optional parameter".
- Use `Callable[[int], int]` for function parameters, `Any` as a last resort, and `-> None` for functions that return nothing.
- mypy is **lenient by default**: unannotated functions are not checked. `--strict` (or `--disallow-untyped-defs`) makes it insist.
- Hints do not validate data. At the boundary use `isinstance`, `try/except`, or (later) a library such as pydantic.
- `# type: ignore[code]` and `reveal_type` exist; use the first rarely and never ship the second.
- Hints and tests catch different bugs. Use both.

When you can annotate a whole module, run mypy until it passes, and explain in your own words why a wrongly typed call still runs, you have met the outcomes of this module. The problems that follow practise each part, and the project puts it all together on your own code.

