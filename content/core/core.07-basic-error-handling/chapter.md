# Chapter 7: Basic error handling

Every program you have written so far has a weak spot. Ask it for a number, type `abc`, and it dies with a red wall of text. Give a function an empty list when it expected marks, and it divides by zero. Look up a student who is not in the dict, and it stops with `KeyError`. Until now that was acceptable: the traceback told you what went wrong, you fixed the program, you ran it again. Real programs cannot work like that. The person typing into your quiz program is not going to read a traceback, fix your code and restart it. They are going to close it and never open it again.

This chapter is about **exceptions**: what they are, where they come from, how they travel through your program, and how to handle them. Handling them well is a skill with two halves, and beginners usually learn only the first:

1. **Catching** the errors you expect, so the program can recover: ask again, use a default, skip a bad line, explain to the user what to type.
2. **Not catching** the errors you do not expect, so that real bugs still stop the program loudly, with a traceback that points at the mistake.

The second half is as important as the first. A program that "never crashes" because it silently ignores every error is not robust. It is broken in a way you cannot see. The goal of this chapter is code that handles **exactly** the exceptions it can raise, **and nothing more**.

Along the way you will answer these questions:

- What *is* an exception, as an object in memory, and what happens to the call stack when one is raised?
- How are the built-in exceptions organised into a family tree, and why does that tree matter when you write `except`?
- In a `try` statement with `except`, `else` and `finally`, which blocks run, in what order, and what happens if there is a `return` in the middle?
- How do you raise your own exceptions, and how do you write a message that tells the reader what to do next?
- Why is a bare `except:` dangerous, and what does "Ask forgiveness, not permission" mean?
- What is `assert` for, and why must it never check user input?

The "Under the hood" subsections show the machinery: how the interpreter unwinds frames, the traceback object every exception carries, and the hidden `__context__` and `__cause__` links that make Python print "During handling of the above exception, another exception occurred".

A note on how examples are shown. A block of code is followed by the exact output it produces when run as a script with Python 3.14. When an example ends in an error, the traceback is shown with the file name shortened to `example.py`. When a program reads input, the text the user typed is shown after the prompt, as it would appear in the terminal. Answer every "Predict the output" question on paper before you open the answer.

Custom exception **classes** (your own `class OutOfStockError(Exception)`) need classes, which come in the object-oriented programming module. In this chapter you raise only the built-in exceptions, which are enough for almost every situation a beginner meets.

## Table of contents

1. [Why programs need error handling](#1-why-programs-need-error-handling)
2. [Reading a traceback, again](#2-reading-a-traceback-again)
3. [What an exception is](#3-what-an-exception-is)
4. [The built-in exception hierarchy](#4-the-built-in-exception-hierarchy)
5. [try and except](#5-try-and-except)
6. [Catching specific exceptions](#6-catching-specific-exceptions)
7. [The exception object: as e](#7-the-exception-object-as-e)
8. [else and finally](#8-else-and-finally)
9. [Raising exceptions yourself](#9-raising-exceptions-yourself)
10. [Writing error messages that help](#10-writing-error-messages-that-help)
11. [Re-raising and chaining](#11-re-raising-and-chaining)
12. [Why bare except is dangerous](#12-why-bare-except-is-dangerous)
13. [Keep try blocks narrow](#13-keep-try-blocks-narrow)
14. [EAFP versus LBYL](#14-eafp-versus-lbyl)
15. [assert and when not to use it](#15-assert-and-when-not-to-use-it)
16. [Programs that never crash on bad input](#16-programs-that-never-crash-on-bad-input)
17. [Designing error handling](#17-designing-error-handling)
18. [Summary](#summary)
19. [Learning outcomes](#learning-outcomes)
20. [Module project](#module-project)
21. [Further reading](#further-reading)

---

## 1. Why programs need error handling

Here is a tiny program from chapter 2. When the user types a number, it works. When the user types `twenty`, this happens:

```python
age = int(input("Enter your age: "))
print("Next year you will be", age + 1)
```

Output:

```text
Enter your age: twenty
Traceback (most recent call last):
  File "example.py", line 1, in <module>
    age = int(input("Enter your age: "))
ValueError: invalid literal for int() with base 10: 'twenty'
```

The program did nothing wrong in the sense of a bug: `int("twenty")` really cannot be done. The **input** was bad. But the program's response, dying, is the wrong response. A person would say "That is not a number, please type your age in digits" and ask again. By the end of this chapter you will write exactly that.

### Three kinds of problems

It helps to separate three kinds of things that go wrong.

1. **Syntax errors.** The code is not valid Python, for example a missing colon. Python finds these **before** it runs a single line, while it is compiling the file. You cannot handle a syntax error in the same file with `try`, because the `try` itself never starts running. You fix syntax errors by editing the code.
2. **Exceptions.** The code is valid, but while it runs, an operation cannot be done: converting `"twenty"` to an int, dividing by zero, looking up a missing key, opening a file that does not exist. Python **raises** an exception. This chapter is about these.
3. **Logic errors.** The code runs without any exception but gives the wrong answer, for example `average = total / len(marks) + 1`. No error handling can find these. Tests find them.

### The world's fault, or the programmer's fault?

Exceptions themselves come from two very different sources, and they need opposite treatment.

| Source | Examples | What to do |
|---|---|---|
| **The world**: users, files, networks, data you did not create | user types `abc` for a number; a file is missing; a line in a data file has 3 fields instead of 4 | **Expect** it. Catch the specific exception and recover: ask again, skip, use a default, explain. |
| **The programmer**: a bug in your code | a typo in a variable name (`NameError`); calling `len(5)` (`TypeError`); an index off by one (`IndexError`) | **Do not hide it.** Let it crash during development so the traceback shows you the bug. Then fix the code. |

Almost every error-handling mistake in this chapter comes from mixing these up: catching a programmer's bug as if it were bad input (so the bug is hidden), or failing to catch bad input as if it were a bug (so the user sees a crash).

### Common misconceptions

- "Error handling means wrapping everything in `try`." No. It means handling the **specific** failures that the world can cause, at the place where you know what to do about them.
- "A good program never raises exceptions." Good programs raise exceptions all the time; that is how a function says "I cannot do what you asked". The skill is deciding where they are caught.
- "`try` can catch a syntax error in my file." It cannot. The file is compiled before anything runs.

---

## 2. Reading a traceback, again

Chapter 1 (section 8) taught you to read a traceback **from the bottom up**: the last line names the exception and its message, the lines above show where it happened. Now that you write functions, tracebacks have several entries, and it is worth reading one again carefully.

### A traceback through several functions

```python
def average(marks):
    return sum(marks) / len(marks)

def report(name, marks):
    avg = average(marks)
    return name + ": " + str(round(avg, 1))

print(report("Asha", [72, 85, 64]))
print(report("Ravi", []))
```

Output:

```text
Asha: 73.7
Traceback (most recent call last):
  File "example.py", line 9, in <module>
    print(report("Ravi", []))
          ~~~~~~^^^^^^^^^^^^
  File "example.py", line 5, in report
    avg = average(marks)
  File "example.py", line 2, in average
    return sum(marks) / len(marks)
           ~~~~~~~~~~~^~~~~~~~~~~~
ZeroDivisionError: division by zero
```

Read it from the bottom:

1. **What**: `ZeroDivisionError: division by zero`.
2. **Where it happened**: the last `File` entry, line 2, inside `average`, the expression `sum(marks) / len(marks)`. The `^` under the carets points at the `/` operator.
3. **How we got there**: each entry above is one **frame** on the call stack (chapter 6, section 5): `<module>` called `report` on line 9, `report` called `average` on line 5. "most recent call last" means the newest frame is at the bottom.

### Where it happened versus where the mistake is

The exception happened in `average`, but is `average` wrong? It does what it says for every non-empty list. The real question is "who should have dealt with an empty list?" Maybe `average` should raise a clearer error, maybe `report` should print "no marks yet", maybe the caller should never pass an empty list. A traceback tells you **where the program noticed** the problem. Deciding **where to fix** it is your job, and this chapter gives you the tools for each choice.

### Common misconceptions

- "The top line of the traceback is the error." The top lines are the oldest calls. The error is at the **bottom**.
- "The function in the last frame has the bug." Often the bug is in a caller that passed bad data. Read the whole stack.
- "Tracebacks are printed to standard output." They go to **standard error** (chapter 1), which is why `>` does not capture them.

---

## 3. What an exception is

### An exception is an object

Chapter 2 taught you that everything in Python is an object with a type, an identity and a value. Exceptions are no different. `ValueError` is a type (a class), and you can create a `ValueError` object without raising it, just like you create a list:

```python
problem = ValueError("age must be a whole number")
print(type(problem))
print(problem)
print(repr(problem))
print(problem.args)
```

Output:

```text
<class 'ValueError'>
age must be a whole number
ValueError('age must be a whole number')
('age must be a whole number',)
```

Nothing went wrong in that program. Creating an exception object is harmless; it is just a value that holds a message. The message you pass is stored in the tuple `problem.args`, and `str(problem)` (what `print` shows) gives you the message back.

### raise: start the exception travelling

An exception object becomes an **error** only when you **raise** it. The `raise` statement stops the current code immediately and starts the exception travelling:

```python
problem = ValueError("age must be a whole number")
print("before")
raise problem
print("after")
```

Output:

```text
before
Traceback (most recent call last):
  File "example.py", line 3, in <module>
    raise problem
ValueError: age must be a whole number
```

`print("after")` never ran. Usually you create and raise in one step: `raise ValueError("age must be a whole number")`. Built-in operations do the same thing internally: when `int("twenty")` fails, the C code inside `int` creates a `ValueError` object with the message `invalid literal for int() with base 10: 'twenty'` and raises it.

### Propagation: up the call stack

When an exception is raised inside a function, that function stops at once. Python looks for a handler (a matching `except`, coming in section 5) in the current function. If there is none, the function's frame is **thrown away** and the exception appears in the **caller**, at the line that made the call, as if that line had raised it. If the caller has no handler either, its frame is thrown away too, and so on up the stack. If the exception reaches the top (`<module>`) with no handler, Python prints the traceback and the program ends with exit status 1.

```python
def level3():
    print("level3 starts")
    raise ValueError("deep problem")
    print("level3 ends")

def level2():
    print("level2 starts")
    level3()
    print("level2 ends")

def level1():
    print("level1 starts")
    level2()
    print("level1 ends")

level1()
print("program ends")
```

Output:

```text
level1 starts
level2 starts
level3 starts
Traceback (most recent call last):
  File "example.py", line 16, in <module>
    level1()
    ~~~~~~^^
  File "example.py", line 13, in level1
    level2()
    ~~~~~~^^
  File "example.py", line 8, in level2
    level3()
    ~~~~~~^^
  File "example.py", line 3, in level3
    raise ValueError("deep problem")
ValueError: deep problem
```

None of the "ends" lines ran. Each function was abandoned at the exact line where the exception came through: `level3` at `raise`, `level2` at the call `level3()`, `level1` at the call `level2()`. This is called **propagation**: the exception propagates up the stack until something handles it or there is nothing left.

Here is the picture just before the `raise`, and what happens next:

```text
call stack (newest on top)            after raise ValueError

+---------------------+
| level3  line 3      |  <- raise     frame discarded, no handler
+---------------------+
| level2  line 8      |               frame discarded, no handler
+---------------------+
| level1  line 13     |               frame discarded, no handler
+---------------------+
| <module> line 16    |               no handler: print traceback, exit 1
+---------------------+
```

### Under the hood: how the interpreter unwinds frames

Each function call runs in a **frame** (chapter 6, section 5) holding the function's local variables and the position of the instruction it is executing. When an instruction raises, the interpreter does three things:

1. It looks in the current code object's **exception table**, a small table the compiler built, which says "instructions from here to here are inside a `try`; on an exception, jump to this handler". If the failing instruction is covered, execution jumps to the handler and the exception is "caught" (whether the handler actually matches the type is decided by the handler's own code).
2. If the instruction is not covered, the frame is finished. The interpreter records the frame and line in the exception's **traceback** and returns to the caller's frame, **without a return value**, carrying the exception instead.
3. In the caller, the instruction that made the call is now treated as the one that raised, and step 1 repeats.

The record of where the exception went is a chain of **traceback objects**, stored on the exception as `__traceback__`. Each link knows its frame, its line number, and the next link toward the place where it was raised. You never need to walk it yourself (Python prints it for you), but seeing it makes the traceback less magical. This example catches the exception (with `try`/`except`, explained in section 5) so we can look at it:

```python
def level3():
    raise ValueError("deep problem")

def level2():
    level3()

def level1():
    level2()

try:
    level1()
except ValueError as error:
    tb = error.__traceback__
    while tb is not None:
        print(tb.tb_frame.f_code.co_name, "line", tb.tb_lineno)
        tb = tb.tb_next
```

Output:

```text
<module> line 11
level1 line 8
level2 line 5
level3 line 2
```

That is exactly the list of `File ... line ..., in ...` entries a printed traceback would show, oldest first. Two consequences are worth remembering:

- An exception **remembers where it came from** even after the frames are gone. That is why you can catch an exception, store it, and print a traceback later.
- Unwinding is **not free**, but it is cheap enough that Python itself uses exceptions for normal control flow: every `for` loop ends when the iterator raises `StopIteration` internally.

### Predict the output

```python
def check(n):
    print("checking", n)
    if n < 0:
        raise ValueError("negative")
    print("ok", n)
    return n * 2

def run():
    total = 0
    for n in [3, 5, -1, 7]:
        total += check(n)
        print("total", total)
    print("finished run")

run()
```

<details><summary>Answer</summary>

```text
checking 3
ok 3
total 6
checking 5
ok 5
total 16
checking -1
Traceback (most recent call last):
  File "example.py", line 15, in <module>
    run()
    ~~~^^
  File "example.py", line 11, in run
    total += check(n)
             ~~~~~^^^
  File "example.py", line 4, in check
    raise ValueError("negative")
ValueError: negative
```

The loop runs for 3 and 5. For -1, `check` raises before printing "ok", so `total += check(n)` never completes and `total` is never printed again. The exception leaves `check`, then `run` (the loop and "finished run" are abandoned), then the module. The 7 is never checked.

</details>

### Common misconceptions and edge cases

- "An exception is a message." It is an **object** with a type, an `args` tuple and a traceback. The message is one part of it.
- "Creating an exception raises it." `ValueError("x")` is just a value. Only `raise` starts it travelling.
- "When a function raises, it returns `None`." It does not return at all. The caller's assignment (`total += check(n)`) never happens.
- "Only the function that raised is stopped." Every frame between the `raise` and the handler is abandoned at the line that was running.

---

## 4. The built-in exception hierarchy

Python has about seventy built-in exception types. You do not need to memorise them, but you do need to know how they are **organised**, because `except SomeType` catches that type **and every type below it** in the family tree.

### The tree

Here is the part of the tree you will meet most often. Each indented name is a **subclass** (a more specific kind) of the name above it.

```text
BaseException
 +-- SystemExit                 raised by sys.exit()
 +-- KeyboardInterrupt          raised when the user presses Ctrl+C
 +-- Exception                  base of all "ordinary" errors
      +-- ArithmeticError
      |    +-- ZeroDivisionError
      |    +-- OverflowError
      +-- LookupError
      |    +-- IndexError        list/str/tuple index out of range
      |    +-- KeyError          dict key not found
      +-- ValueError            right type, unacceptable value
      |    +-- UnicodeError      (and UnicodeDecodeError, ...)
      +-- TypeError             wrong type for the operation
      +-- NameError
      |    +-- UnboundLocalError
      +-- AttributeError        object has no such attribute or method
      +-- OSError               the operating system said no
      |    +-- FileNotFoundError
      |    +-- PermissionError
      +-- EOFError              input() reached end of input
      +-- RuntimeError
      |    +-- RecursionError
      +-- StopIteration
      +-- AssertionError        a failed assert
```

The full tree is in the official documentation (see Further reading).

### BaseException versus Exception

Everything that can be raised descends from `BaseException`. Directly under it are a few special exceptions that are **not errors** in the usual sense:

- `KeyboardInterrupt` is raised when the user presses **Ctrl+C**. It means "the human wants this program to stop".
- `SystemExit` is raised by `sys.exit()`. It means "the program has decided to stop".

Everything else, all the ordinary errors, descends from `Exception`. The design is deliberate: code that catches `Exception` catches every ordinary error but still lets Ctrl+C and `sys.exit()` through, so the program can still be stopped. Section 12 shows what goes wrong when you catch *everything* instead.

### Families: LookupError and ArithmeticError

Some exceptions share a parent because they describe the same kind of failure.

- `IndexError` (bad position in a sequence) and `KeyError` (missing key in a dict) are both **lookups that failed**, so both are subclasses of `LookupError`. When you dig into nested data, such as a dict of lists of dicts, `except LookupError` handles both with one clause.
- `ZeroDivisionError` and `OverflowError` are both **arithmetic** failures, children of `ArithmeticError`.

```python
data = {"marks": [72, 85]}

for key, index in [("marks", 0), ("marks", 5), ("ages", 0)]:
    try:
        print(data[key][index])
    except LookupError as error:
        print("lookup failed:", type(error).__name__, error)
```

Output:

```text
72
lookup failed: IndexError list index out of range
lookup failed: KeyError 'ages'
```

### ValueError versus TypeError

These two are confused more than any other pair, and you will choose between them every time you raise an exception yourself.

- **`TypeError`**: the operation does not work on this **kind** of object at all. `len(5)`, `"a" + 1`, `int(None)`, calling a function with the wrong number of arguments.
- **`ValueError`**: the type is acceptable, but this particular **value** is not. `int("twenty")` (int accepts strings, but not that one), `math.sqrt(-1)`, `[1, 2].index(9)`.

```python
for value in ["42", "forty-two", None, 4.7]:
    try:
        print(value, "->", int(value))
    except ValueError as error:
        print(value, "-> ValueError:", error)
    except TypeError as error:
        print(value, "-> TypeError:", error)
```

Output:

```text
42 -> 42
forty-two -> ValueError: invalid literal for int() with base 10: 'forty-two'
None -> TypeError: int() argument must be a string, a bytes-like object or a real number, not 'NoneType'
4.7 -> 4
```

`int` accepts strings and floats, so `"forty-two"` is a bad **value** of an accepted type; `None` is a type `int` does not accept at all. Notice `int(4.7)` is not an error: it truncates.

### OSError and friends

Errors that come from the operating system, such as a missing file, a permission problem, or a full disk, are subclasses of `OSError`. The one you will meet first is `FileNotFoundError`. Files are a later module, so here is only a taste:

```python
try:
    open("no_such_file.txt")
except FileNotFoundError as error:
    print("Could not open:", error.filename)
    print(error)
```

Output:

```text
Could not open: no_such_file.txt
[Errno 2] No such file or directory: 'no_such_file.txt'
```

### Under the hood: checking the family

Exception types are classes, and the tree above is the **class hierarchy**. You can ask Python about it directly with two built-in functions: `issubclass(A, B)` asks "is type A a kind of B?", and `isinstance(obj, B)` asks "is this object an instance of B or of a subclass?". An `except B` clause matches an exception exactly when `isinstance(the_exception, B)` is true.

```python
print(issubclass(KeyError, LookupError))
print(issubclass(KeyError, Exception))
print(issubclass(KeyboardInterrupt, Exception))
print(isinstance(ZeroDivisionError("x"), ArithmeticError))
print(ZeroDivisionError.__mro__)
```

Output:

```text
True
True
False
True
(<class 'ZeroDivisionError'>, <class 'ArithmeticError'>, <class 'Exception'>, <class 'BaseException'>, <class 'object'>)
```

`__mro__` (method resolution order, more about it in the OOP module) lists the class and all its ancestors, nearest first. It is the quickest way to answer "which `except` clauses would catch this?": exactly the clauses naming one of these classes.

### Common misconceptions and edge cases

- "`except Exception` catches everything." It does not catch `KeyboardInterrupt` or `SystemExit`, by design.
- "`KeyError` and `IndexError` are unrelated." Both are `LookupError`s.
- "A bad argument is always a `ValueError`." Only if the **type** was acceptable. Wrong type is `TypeError`.
- `bool` is a subclass of `int` (chapter 2), so `int(True)` works and gives `1`. The exception hierarchy uses exactly the same subclass idea.
- `UnboundLocalError` (chapter 6, section 13) is a kind of `NameError`.

---

## 5. try and except

### The basic shape

```python
text = "twenty"
try:
    age = int(text)
    print("You are", age)
except ValueError:
    print("Please type your age in digits, for example 20.")
print("done")
```

Output:

```text
Please type your age in digits, for example 20.
done
```

The `try` block holds code that might raise. Each `except` clause names an exception type and holds the code that runs if that type is raised **inside the `try` block**.

### What happens, step by step

1. Python runs the `try` block line by line.
2. If no exception is raised, every `except` clause is **skipped**, and execution continues after the whole `try` statement.
3. If an exception is raised, the rest of the `try` block is **abandoned** at that point. Python checks the `except` clauses **from top to bottom** and runs the **first** one whose type matches (the exception is an instance of that type or of a subclass).
4. After the handler finishes, the exception is **finished**: it does not propagate any further, and execution continues after the whole `try` statement.
5. If no clause matches, the exception keeps propagating as if there were no `try` at all.

Watch both paths with the same code:

```python
for text in ["20", "twenty"]:
    print("--- text =", repr(text))
    try:
        print("A: converting")
        age = int(text)
        print("B: converted to", age)
    except ValueError:
        print("C: not a number")
    print("D: after try")
```

Output:

```text
--- text = '20'
A: converting
B: converted to 20
D: after try
--- text = 'twenty'
A: converting
C: not a number
D: after try
```

For `"20"` the order is A, B, D. For `"twenty"` it is A, C, D: line B never ran, because `int(text)` raised before it.

### An unhandled type still crashes

An `except` clause handles only the types it names. Anything else passes straight through:

```python
values = [10, 5, 0]
try:
    print(values[1] / values[2])
except ValueError:
    print("bad value")
```

Output:

```text
Traceback (most recent call last):
  File "example.py", line 3, in <module>
    print(values[1] / values[2])
          ~~~~~~~~~~^~~~~~~~~~~
ZeroDivisionError: division by zero
```

The `except ValueError` did not match `ZeroDivisionError`, so the exception propagated and the program crashed exactly as if there were no `try`. That is a **feature**: you handle what you planned for, and anything else is reported.

### Catching in the caller

A `try` does not have to be in the function that raises. It catches anything raised **during** the `try` block, including inside any function called from it, however deep. Propagation (section 3) carries the exception up to the frame that has the `try`.

```python
def parse_age(text):
    age = int(text)          # may raise ValueError
    return age

def ask_age(text):
    try:
        return parse_age(text)
    except ValueError:
        return None

print(ask_age("31"))
print(ask_age("thirty"))
```

Output:

```text
31
None
```

This leads to an important design question: **which** function should handle an error? The answer is: the one that knows **what to do about it**. `parse_age` cannot know whether to ask again, use a default, or give up, so it lets the exception propagate. `ask_age` has decided that "no answer" (`None`) is the right result. Low-level functions raise; higher-level functions that understand the situation catch.

### Predict the output

```python
def risky(n):
    print("risky", n)
    return 10 // n

total = 0
for n in [2, 0, 5]:
    try:
        total += risky(n)
        print("added")
    except ZeroDivisionError:
        print("skipped", n)
print("total", total)
```

<details><summary>Answer</summary>

```text
risky 2
added
risky 0
skipped 0
risky 5
added
total 7
```

`10 // 2` is 5 and `10 // 5` is 2, so the total is 7. For 0, `risky` prints "risky 0" and then raises; `total += ...` and "added" are skipped, the handler prints "skipped 0", and the **loop continues**, because the `try` is inside the loop. Putting the `try` inside the loop is how you keep processing after one bad item.

</details>

### Common misconceptions and edge cases

- "After the `except` block, Python goes back and finishes the `try` block." Never. The rest of the `try` block is abandoned for good.
- "A `try` only catches errors on its own lines." It catches errors from any function called during the `try` block.
- "If no `except` matches, the program continues anyway." It does not; the exception propagates.
- A `try` must have at least one `except` or a `finally` (section 8). `try:` alone is a syntax error.
- Variables assigned inside the `try` block before the exception keep their values; assignments after the failing line never happen. If you use such a variable after the `try`, make sure every path gave it a value.

---

## 6. Catching specific exceptions

### Several except clauses

A piece of code can fail in several different ways, and each may need a different response. Give each its own `except` clause:

```python
def pick(items, position_text):
    try:
        position = int(position_text)
        return "You chose " + items[position - 1]
    except ValueError:
        return "Type the item's number, for example 2."
    except IndexError:
        return "There is no item " + position_text + ". Choose 1 to " + str(len(items)) + "."

menu = ["tea", "coffee", "juice"]
print(pick(menu, "2"))
print(pick(menu, "two"))
print(pick(menu, "7"))
```

Output:

```text
You chose coffee
Type the item's number, for example 2.
There is no item 7. Choose 1 to 3.
```

Each message tells the user exactly what to do next, which is only possible because the two failures are caught separately.

(There is a hidden bug in this function: what does `pick(menu, "0")` return? `items[-1]` is valid, so it returns "You chose juice". Python's negative indexes are not an error. A careful version checks `1 <= position <= len(items)`. Handling exceptions does not replace thinking about the valid range.)

### Order matters: the first match wins

The `except` clauses are tried top to bottom, and the **first** match runs. If a parent class comes first, the child's clause can never run:

```python
data = {"a": 1}
try:
    data["b"]
except LookupError:
    print("some lookup failed")
except KeyError:
    print("the key is missing")
```

Output:

```text
some lookup failed
```

`KeyError` is a `LookupError`, so the first clause matched and the second is dead code. Python does not warn you. **Rule: put the most specific types first, the general ones last.**

### One clause for several types: a tuple

When different exceptions need the **same** response, list them in a tuple:

```python
def to_number(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return None

for v in ["3.5", "abc", None, [1]]:
    print(repr(v), "->", to_number(v))
```

Output:

```text
'3.5' -> 3.5
'abc' -> None
None -> None
[1] -> None
```

The parentheses are required when you also write `as name` (section 7). Python 3.14 allows `except ValueError, TypeError:` without parentheses when there is no `as`, but older versions treat it as a syntax error, and most code you read writes the tuple with parentheses. Always use them.

### Catching a family

Naming a parent class catches every child: `except LookupError` handles `KeyError` and `IndexError`; `except ArithmeticError` handles `ZeroDivisionError` and `OverflowError`. Use this when the response really is the same for the whole family, as in the nested-data example of section 4.

### Handle exactly what the code can raise

How do you know which exceptions to catch? Look at each operation in the `try` block and ask what can **legitimately** go wrong with the data you expect:

| Operation | Expected failure | Type |
|---|---|---|
| `int(text)`, `float(text)` | text is not a number | `ValueError` |
| `d[key]` | key missing | `KeyError` |
| `seq[i]` | position out of range | `IndexError` |
| `a / b`, `a // b`, `a % b` | `b` is zero | `ZeroDivisionError` |
| `seq.index(x)`, `s.index(sub)`, `lst.remove(x)` | item not present | `ValueError` |
| `open(name)` | file missing | `FileNotFoundError` |
| `input()` | no more input (end of file, Ctrl+D) | `EOFError` |

Catch those, and **nothing else**. A `TypeError` from `int(None)` usually means a bug upstream (who passed `None`?), so let it crash and show you.

The documentation of each built-in function and method says what it raises. When you are unsure, try it in the REPL with a bad value and read the last line of the traceback: that is the type to catch.

### Common misconceptions and edge cases

- "Python picks the best matching `except` clause." It picks the **first** matching one.
- "`except ValueError or TypeError:` catches both." `ValueError or TypeError` is an expression that evaluates to `ValueError` (a class is truthy), so only `ValueError` is caught. Use a tuple.
- "More `except` clauses make code safer." Every extra clause is one more kind of bug that can be hidden. Add a clause only for a failure you can name and handle.
- At most **one** handler runs per exception, even if several would match.

---

## 7. The exception object: as e

### Naming the exception

Often the handler needs the exception itself: to show its message, to record it, or to look at its details. `except SomeType as name:` binds the exception object to `name` inside the handler. The usual names are `e`, `err` or `error`.

```python
for text in ["12", "1.5", "", "  7  "]:
    try:
        print(repr(text), "->", int(text))
    except ValueError as error:
        print(repr(text), "-> problem:", error)
```

Output:

```text
'12' -> 12
'1.5' -> problem: invalid literal for int() with base 10: '1.5'
'' -> problem: invalid literal for int() with base 10: ''
'  7  ' -> 7
```

`int` happily ignores spaces around the digits, which is why `"  7  "` works.

### type, args, str and repr

An exception object gives you four useful views:

```python
try:
    {"tea": 15}["cake"]
except KeyError as e:
    print("type name:", type(e).__name__)
    print("args:     ", e.args)
    print("str:      ", str(e))
    print("repr:     ", repr(e))
```

Output:

```text
type name: KeyError
args:      ('cake',)
str:       'cake'
repr:      KeyError('cake')
```

- `type(e).__name__` is the name of the exception's class as a plain string, handy for messages and logs.
- `e.args` is the tuple of arguments passed when the exception was created. Most built-in exceptions have one argument, the message (for `KeyError`, the missing key itself).
- `str(e)` is what `print(e)` shows: normally the message.
- `repr(e)` shows the type and the arguments, which is the most informative for debugging.

### KeyError's quoted message

Look again at `str(e)` above: it printed `'cake'` **with quotes**. `KeyError` is special: its `str` is the `repr` of the missing key, so that an empty-string key or a key with spaces is visible. That surprises people who write `print("Missing: " + str(e))` and get `Missing: 'cake'`. If you want the key itself, use `e.args[0]`:

```python
try:
    {"tea": 15}["green tea"]
except KeyError as e:
    print("str(e):    ", str(e))
    print("e.args[0]: ", e.args[0])
```

Output:

```text
str(e):     'green tea'
e.args[0]:  green tea
```

### An exception with several args, or none

You can pass any number of arguments when you create an exception. With zero arguments the message is empty; with more than one, `str` shows the whole tuple, which is rarely what you want. **Give one clear message string.**

```python
print(repr(str(ValueError())))
print(str(ValueError("one message")))
print(str(ValueError("two", "parts")))
```

Output:

```text
''
one message
('two', 'parts')
```

### The name is deleted after the except block

This one surprises everyone once. At the end of an `except ... as e` block, Python **deletes** the name `e`:

```python
try:
    int("x")
except ValueError as e:
    print("inside:", e)
print("outside:", e)
```

Output:

```text
inside: invalid literal for int() with base 10: 'x'
Traceback (most recent call last):
  File "example.py", line 5, in <module>
    print("outside:", e)
                      ^
NameError: name 'e' is not defined
```

**Why?** The exception holds its traceback, the traceback holds the frames, and the frame holds the local variable `e`, which holds the exception: a loop of references (a **reference cycle**) that keeps every local variable of every frame in the traceback alive. Deleting `e` at the end of the handler breaks that loop. If you need the exception later (problem p020, a retry helper, needs exactly this), copy it to another name inside the handler: `last_error = e`.

### Predict the output

```python
def describe(func, value):
    try:
        result = func(value)
    except (ValueError, TypeError) as e:
        return type(e).__name__ + ": " + str(e)
    return "ok: " + str(result)

print(describe(int, "15"))
print(describe(int, "1 5"))
print(describe(len, 15))
print(describe(abs, -2.5))
```

<details><summary>Answer</summary>

```text
ok: 15
ValueError: invalid literal for int() with base 10: '1 5'
TypeError: object of type 'int' has no len()
ok: 2.5
```

`int("1 5")` fails because spaces are only ignored at the ends. `len(15)` raises `TypeError` because an int has no length. `abs(-2.5)` succeeds. Notice `return "ok: ..."` is after the `try` statement; we will see in section 8 that an `else` block is the tidier place for it.

</details>

### Common misconceptions and edge cases

- "`print(e)` prints the traceback." It prints only `str(e)`, the message. The traceback is a separate thing.
- "`str(e)` always gives the plain message." Not for `KeyError`, whose `str` is quoted.
- "`e` is still available after the handler." It is deleted. Copy it to another name if you need it.
- `e.args` is a tuple even when there is one argument: `('message',)`.

---

## 8. else and finally

A `try` statement can have two more clauses. Together they let you say precisely **when** each piece of code runs.

```python
try:
    ...               # code that might raise
except SomeError:
    ...               # runs if SomeError was raised in the try block
else:
    ...               # runs if the try block finished WITHOUT an exception
finally:
    ...               # runs ALWAYS, last, whatever happened
```

The order of the clauses is fixed: `try`, then `except` clauses, then optional `else`, then optional `finally`. `else` needs at least one `except`; `finally` can stand alone with `try`.

### else: the success path

The `else` block runs only if the `try` block **completed without raising**. Why not just put that code at the end of the `try` block? Because then **its** exceptions would be caught too, by a handler that was written for something else.

```python
prices = {"tea": 15, "coffee": 25}

def bill(item, quantity_text):
    try:
        quantity = int(quantity_text)
    except ValueError:
        return "Quantity must be a whole number, for example 2."
    else:
        return item + ": " + str(prices[item] * quantity)

print(bill("tea", "3"))
print(bill("tea", "three"))
```

Output:

```text
tea: 45
Quantity must be a whole number, for example 2.
```

Only `int(quantity_text)` is protected. If `prices[item]` raised a `KeyError` (a bug in the menu, or an item that should have been checked earlier), it would **not** be mistaken for a bad quantity. Section 13 comes back to this idea: keep the `try` block as small as possible and put the follow-up work in `else`.

### finally: runs no matter what

The `finally` block runs on **every** way out of the `try` statement: after success, after a handled exception, after an **unhandled** exception that is about to propagate, and even after `return`, `break` or `continue` inside the `try`. It is for **clean-up**: things that must happen whether or not the work succeeded, such as closing a file or a network connection, releasing something you reserved, or printing "done".

```python
def divide(a, b):
    print("start", a, b)
    try:
        result = a / b
    except ZeroDivisionError:
        print("  cannot divide by zero")
        result = None
    else:
        print("  ok")
    finally:
        print("  clean up")
    return result

print(divide(6, 3))
print(divide(6, 0))
```

Output:

```text
start 6 3
  ok
  clean up
2.0
start 6 0
  cannot divide by zero
  clean up
None
```

### The exact order

Here is the complete flow. Read it as a decision diagram; every path ends in `finally`.

```text
              run TRY block
                    |
         +----------+-------------+
         |                        |
   no exception             exception E raised
         |                        |
    run ELSE            first EXCEPT clause matching E?
         |                 |                  |
         |                yes                 no
         |                 |                  |
         |         run that handler      (E is pending)
         |                 |                  |
         +---------+-------+------------------+
                   |
              run FINALLY
                   |
     E still pending?  -- yes -->  E propagates to the caller
                   |
                   no
                   |
        continue after the try statement
        (or finish a pending return / break / continue)
```

Two more rules complete the picture:

- If the `except` or `else` block **itself raises**, that new exception becomes pending; `finally` still runs, and then the new exception propagates.
- If `finally` itself raises, that exception replaces whatever was pending.

### finally when the exception is not handled

`finally` runs **before** the exception leaves the function. This is what makes it reliable for clean-up:

```python
def process(text):
    print("open connection")
    try:
        return int(text) * 2
    finally:
        print("close connection")

print(process("21"))
print(process("abc"))
```

Output:

```text
open connection
close connection
42
open connection
close connection
Traceback (most recent call last):
  File "example.py", line 9, in <module>
    print(process("abc"))
          ~~~~~~~^^^^^^^
  File "example.py", line 4, in process
    return int(text) * 2
           ~~~^^^^^^
ValueError: invalid literal for int() with base 10: 'abc'
```

For `"abc"`, there is no `except`, so the `ValueError` is pending; `finally` prints "close connection", and **then** the exception propagates and the traceback appears. The connection was closed even though the function crashed.

### return inside try with finally

What happens when the `try` block says `return`? The return value is **computed** and the function is **about to** return, but first `finally` runs. Then the function returns the value computed earlier.

```python
def f():
    try:
        print("try: computing return value")
        return "from try"
    finally:
        print("finally: still runs")

print(f())
```

Output:

```text
try: computing return value
finally: still runs
from try
```

A detail with a twist: the return **value** is fixed when the `return` statement runs. If `finally` changes the variable afterwards, the returned value does not change (for an immutable value like an int):

```python
def g():
    x = 1
    try:
        return x
    finally:
        x = 99
        print("finally set x to", x)

print(g())
```

Output:

```text
finally set x to 99
1
```

### Never return from finally

If `finally` contains its own `return`, that return **wins**: it replaces the earlier return value, and worse, it **throws away** a pending exception, as if it had never happened.

```python
def h(text):
    try:
        return int(text)
    finally:
        return -1

print(h("5"))
print(h("abc"))
```

Output:

```text
example.py:5: SyntaxWarning: 'return' in a 'finally' block
  return -1
-1
-1
```

Both calls returned `-1`. The `ValueError` from `int("abc")` vanished without a trace, which is exactly the kind of silent bug this chapter warns against. Because this is almost always a mistake, Python 3.14 prints a `SyntaxWarning` when it compiles a `return`, `break` or `continue` inside `finally` (the warning goes to standard error, shown first above because Python compiles the whole file before running it). The rule is simple: **`finally` is for clean-up only; never `return`, `break` or `continue` out of it.**

### Under the hood: how finally is implemented

The compiler copies the `finally` block into **every** exit path of the `try` statement: once for the normal path, and once inside an invisible handler that catches **everything** (even `KeyboardInterrupt`), runs the `finally` code, and then **re-raises** the pending exception. For a `return` inside `try`, the return value is pushed onto the frame's value stack, the `finally` code runs, and then the saved value is returned. That is why the returned value in `g()` above was the old `1`: it had already been saved. A `return` in `finally` simply returns before the "re-raise" step is reached, which is how it swallows the exception.

### Predict the output

```python
def check(n):
    try:
        print("try", n)
        if n == 0:
            raise ValueError("zero")
        if n < 0:
            return "negative"
    except ValueError:
        print("except", n)
        return "zero"
    else:
        print("else", n)
    finally:
        print("finally", n)
    print("after", n)
    return "positive"

for n in [1, 0, -1]:
    print("->", check(n))
```

<details><summary>Answer</summary>

```text
try 1
else 1
finally 1
after 1
-> positive
try 0
except 0
finally 0
-> zero
try -1
finally -1
-> negative
```

- `n = 1`: no exception, no return in `try`, so `else` runs, then `finally`, then the line after the statement, which returns "positive".
- `n = 0`: the handler runs and returns "zero"; `finally` runs before the function actually returns. `else` does not run, and "after" is never reached.
- `n = -1`: `return "negative"` inside `try`. The `try` block did not *complete normally* (it returned), so `else` is **skipped**; `finally` runs; the function returns "negative".

That last case is the one most people get wrong: `else` runs only if the `try` block falls off its end. A `return`, `break` or `continue` that leaves the `try` block skips `else`.

</details>

### Common misconceptions and edge cases

- "`else` runs when no `except` matched." No: it runs when **no exception happened at all** and the `try` block ended normally.
- "`finally` runs only when there was an error." It runs every time.
- "`finally` handles the exception." It does not. After `finally`, an unhandled exception continues to propagate.
- "A `return` in `try` skips `finally`." `finally` runs before the function actually returns.
- `return` (or `break`/`continue`) in `finally` overrides the return value and silently discards a pending exception. Python 3.14 warns about it. Do not do it.
- `try`/`finally` without any `except` is common and useful: "do this, and whatever happens, clean up afterwards; let the caller handle errors".

---

## 9. Raising exceptions yourself

### Why raise

When **your** function is asked to do something impossible or meaningless, it should raise an exception, exactly like the built-ins do. Consider:

```python
def set_marks(marks):
    if marks < 0 or marks > 100:
        print("invalid marks")
        return None
    return marks
```

This function prints a message and returns `None`. The caller may not check for `None`, and the program carries on with a wrong value until it fails somewhere far away, where the cause is hard to find. Printing is also the wrong job for a small function: maybe the caller is a test, or a web page, or a program with no screen.

Raising is better:

```python
def set_marks(marks):
    if marks < 0 or marks > 100:
        raise ValueError("marks must be between 0 and 100, got " + str(marks))
    return marks

print(set_marks(85))
print(set_marks(120))
```

Output:

```text
85
Traceback (most recent call last):
  File "example.py", line 7, in <module>
    print(set_marks(120))
          ~~~~~~~~~^^^^^
  File "example.py", line 3, in set_marks
    raise ValueError("marks must be between 0 and 100, got " + str(marks))
ValueError: marks must be between 0 and 100, got 120
```

Now the problem cannot be ignored by accident. A caller who knows what to do with bad marks catches `ValueError`; a caller who does not, crashes with a message that says exactly what was wrong. **Raise when the caller has made a request you cannot fulfil; let the caller decide what to do about it.**

### Choosing the type

Pick the built-in type that describes the failure, using the same meanings as the built-ins. Almost all your raises will use these four:

| Situation | Raise |
|---|---|
| Right type, unacceptable value: negative age, empty name, marks 120, unknown menu choice | `ValueError` |
| Wrong type altogether: a list where a number was needed, `None` where text was needed | `TypeError` |
| A key or name that must exist is missing (when you are acting like a dict) | `KeyError` |
| A position out of range (when you are acting like a list) | `IndexError` |

Two others you may meet: `RuntimeError` for "something is in a state where this cannot be done" when nothing more specific fits, and `NotImplementedError` for "this part has not been written yet" (core.06 starter files use it).

**Do not raise `Exception` itself.** A caller who wants to handle your error would have to write `except Exception`, which also catches every bug in their own code (section 12). A specific type lets them catch exactly your failure.

### Checking types: isinstance

To raise `TypeError` you must check the type. Use `isinstance(value, type)` (section 4), which also accepts a tuple of types:

```python
def check_age(age):
    if isinstance(age, bool) or not isinstance(age, int):
        raise TypeError("age must be a whole number (int), got " + type(age).__name__)
    if age < 0 or age > 130:
        raise ValueError("age must be between 0 and 130, got " + str(age))
    return age

for value in [21, -4, "21", True]:
    try:
        print(check_age(value))
    except (TypeError, ValueError) as e:
        print(type(e).__name__ + ":", e)
```

Output:

```text
21
ValueError: age must be between 0 and 130, got -4
TypeError: age must be a whole number (int), got str
TypeError: age must be a whole number (int), got bool
```

Why the extra `isinstance(age, bool)` test? Because `bool` is a subclass of `int` (chapter 2), `isinstance(True, int)` is `True`, and `check_age(True)` would otherwise return `True` as an age of 1. Most of the time you will not check types at all; Python's own operations raise `TypeError` for you when the type is wrong. Check types when a wrong type would otherwise **not** fail, or would fail with a confusing message far away.

### raise with a class or an instance

`raise ValueError` (the class) and `raise ValueError()` (an instance) both work: given a class, Python creates an instance with no arguments. Without a message, though, the traceback ends with a bare `ValueError` and tells the reader nothing. Always raise an instance with a message.

You can only raise exception objects. `raise "bad input"` is itself an error:

```python
raise "bad input"
```

Output:

```text
Traceback (most recent call last):
  File "example.py", line 1, in <module>
    raise "bad input"
TypeError: exceptions must derive from BaseException
```

### Validate early, at the boundary

Where should the checks go? As close as possible to where the data **enters** your program or your function, before any work is done with it. A function that checks its arguments in its first lines and raises immediately gives a traceback that points at the real cause. A function that starts working and fails halfway gives a traceback that points somewhere inside its own logic, and may have done half of its work (changed half a list) before failing.

```python
def withdraw(balances, name, amount):
    if amount <= 0:
        raise ValueError("amount must be positive, got " + str(amount))
    if name not in balances:
        raise KeyError(name)
    if balances[name] < amount:
        raise ValueError(name + " has only " + str(balances[name]) + ", cannot withdraw " + str(amount))
    balances[name] -= amount
    return balances[name]

accounts = {"asha": 500}
print(withdraw(accounts, "asha", 200))
try:
    withdraw(accounts, "asha", 400)
except ValueError as e:
    print("refused:", e)
print(accounts)
```

Output:

```text
300
refused: asha has only 300, cannot withdraw 400
{'asha': 300}
```

All checks come **before** the one line that changes anything, so a refused withdrawal leaves the accounts exactly as they were.

### Raise, or return a special value?

Sometimes a function could return a special value (`None`, `-1`, `""`) instead of raising. `str.find` returns `-1` when the substring is missing, while `str.index` raises `ValueError` (chapter 3). Guidelines:

- **Raise** when the situation is an **error** for most callers and ignoring it would cause harm later. An exception cannot be ignored by accident.
- **Return a special value** when "not found" is a **normal, expected** answer that most callers check anyway, and the special value cannot be mistaken for a real result. `dict.get(key)` returning `None` is a good example; returning `0` for "no marks" is a bad one, because `0` is also a real mark.
- Never do both at random: a function that sometimes returns `None` and sometimes raises for the same kind of problem is hard to use.

### Common misconceptions and edge cases

- "Raising an exception means my function failed." It means the **request** could not be met. That is valuable information for the caller.
- "Print an error and return `None`." The caller can ignore `None`; it cannot ignore an exception.
- "`raise Exception('...')` is fine." It forces callers to catch everything. Use the specific type.
- "Check every argument's type." Usually unnecessary: Python's operations already raise `TypeError`. Check where a wrong type would slip through silently (like `bool` for `int`).
- Do all checks **before** changing anything, so a refused call leaves no half-done changes.

---

## 10. Writing error messages that help

An error message is a tiny piece of documentation that appears at the worst moment: when someone is confused. Compare:

```text
ValueError: invalid input
```

```text
ValueError: quantity must be a whole number from 1 to 10, got '12.5'
```

The first tells you that something went wrong. The second tells you **what was expected**, **what was actually received**, and therefore **what to do**.

### What a good message contains

1. **What was expected**, in the reader's terms: "a whole number from 1 to 10", "a date like 2025-03-14", "one of: add, list, quit".
2. **What was actually received**, shown with `repr()` so that empty strings, spaces and types are visible: `got ''`, `got ' 5'`, `got None`. The `!r` conversion in an f-string does this: `f"got {text!r}"`.
3. **What to do** next, when it is not obvious from (1): "Type the number of an item from the list above."
4. **Where**, when the data has many parts: "line 14", "field 'age'", "question 3".

```python
def parse_quantity(text):
    try:
        quantity = int(text)
    except ValueError:
        raise ValueError(f"quantity must be a whole number from 1 to 10, got {text!r}") from None
    if not 1 <= quantity <= 10:
        raise ValueError(f"quantity must be from 1 to 10, got {quantity}")
    return quantity

for text in ["3", "12.5", "", "0"]:
    try:
        print(parse_quantity(text))
    except ValueError as e:
        print("Error:", e)
```

Output:

```text
3
Error: quantity must be a whole number from 1 to 10, got '12.5'
Error: quantity must be a whole number from 1 to 10, got ''
Error: quantity must be from 1 to 10, got 0
```

Look at the empty-input case: `got ''`. Without `repr`, the message would end with `got ` and the reader would wonder whether the message was cut off. (`from None` is explained in section 11; it keeps the traceback short.)

### Messages for users and messages for programmers

There are two audiences.

- **Programmers** read exception messages in tracebacks and logs. They want precision: the function's expectation, the bad value, the field name.
- **Users** of a finished program should never see a traceback. The program catches the exception at the top and shows a friendly sentence: what happened and what to type instead. It does not mention `ValueError`, `int()` or "base 10".

Often the same message serves both, if you write it in plain words like the ones above. When it does not, the code that catches the exception chooses the user-facing words.

### Style rules

- Start with the subject: "quantity must be ...", "age must be ...", "unknown command ...".
- Lower-case start, no full stop at the end, is the style of Python's own messages (`division by zero`, `list index out of range`). Either style is fine; be consistent.
- Do not blame: "you entered garbage" helps nobody.
- Do not lie or guess: if you do not know why it failed, report what you know (the value and the operation), not a guess.
- One message, one string. Do not pass several arguments to the exception.

### Common misconceptions and edge cases

- "The type name is enough." `ValueError` says which family of problem; only the message says which problem.
- "Show the value with `str()`." Use `repr()` (or `!r`) so that `''`, `' 5'` and `'5'` look different.
- "Users should see the exception message exactly." For a finished program, translate it into words the user understands, at the place where you catch it.

---

## 11. Re-raising and chaining

### Bare raise: handle a little, then pass it on

Sometimes a handler wants to **do something** with the exception, such as record it, count it, or print a note, but **not stop it**: the caller should still see it. Inside an `except` block, `raise` on its own, with nothing after it, re-raises the exception currently being handled, unchanged, with its original traceback.

```python
log = []

def load_score(scores, name):
    try:
        return scores[name]
    except KeyError:
        log.append("missing score for " + name)
        raise

scores = {"asha": 82}
print(load_score(scores, "asha"))
try:
    load_score(scores, "ravi")
except KeyError as e:
    print("caller saw KeyError:", e)
print(log)
```

Output:

```text
82
caller saw KeyError: 'ravi'
['missing score for ravi']
```

The `KeyError` reached the caller exactly as if `load_score` had not caught it, but the log entry was made first. A bare `raise` outside any `except` block is an error: `RuntimeError: No active exception to reraise`.

### Translating an exception: raise ... from ...

Low-level exceptions often use the wrong words for the caller. `parse_time("9.30")` failing with `ValueError: invalid literal for int() with base 10: '9.30'` describes an implementation detail. The caller wants to hear "time must look like HH:MM". The fix is to **catch the low-level exception and raise a new one** with a better message, and to record the original as the **cause** with `from`:

```python
def parse_time(text):
    parts = text.split(":")
    if len(parts) != 2:
        raise ValueError(f"time must look like HH:MM, for example 09:30, got {text!r}")
    try:
        hours = int(parts[0])
        minutes = int(parts[1])
    except ValueError as e:
        raise ValueError(f"time must use digits, like 09:30, got {text!r}") from e
    return hours, minutes

print(parse_time("09:30"))
parse_time("9:3O")
```

Output:

```text
(9, 30)
Traceback (most recent call last):
  File "example.py", line 7, in parse_time
    minutes = int(parts[1])
ValueError: invalid literal for int() with base 10: '3O'

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "example.py", line 13, in <module>
    parse_time("9:3O")
    ~~~~~~~~~~^^^^^^^^
  File "example.py", line 9, in parse_time
    raise ValueError(f"time must use digits, like 09:30, got {text!r}") from e
ValueError: time must use digits, like 09:30, got '9:3O'
```

Python printed **both** exceptions, the original first, joined by "The above exception was the direct cause of the following exception". The user-level message comes last, where the reader looks first, and nothing about the real cause was lost.

### Implicit chaining: "During handling of the above exception"

If a **new** exception is raised **while handling** another, even by accident, Python links them automatically. That is how you see a different linking sentence:

```python
def average(marks):
    try:
        return sum(marks) / len(marks)
    except ZeroDivisionError:
        print("No marks for " + student)

average([])
```

Output:

```text
Traceback (most recent call last):
  File "example.py", line 3, in average
    return sum(marks) / len(marks)
           ~~~~~~~~~~~^~~~~~~~~~~~
ZeroDivisionError: division by zero

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "example.py", line 7, in <module>
    average([])
    ~~~~~~~^^^^
  File "example.py", line 5, in average
    print("No marks for " + student)
                            ^^^^^^^
NameError: name 'student' is not defined
```

The handler was supposed to print a message but contains a bug (`student` is not defined). Python shows the original `ZeroDivisionError` and then the `NameError`, joined by "During handling of the above exception, another exception occurred". When you see that sentence, it usually means **the handler itself has a bug**. When you see "was the direct cause", someone deliberately translated the exception with `from`.

### from None: hiding the context

Sometimes the original exception adds nothing but noise. `raise NewError(...) from None` cuts the link, so only the new exception is printed:

```python
def price_of(menu, item):
    try:
        return menu[item]
    except KeyError:
        raise KeyError(f"{item!r} is not on the menu; choose one of {sorted(menu)}") from None

price_of({"tea": 15, "coffee": 25}, "cake")
```

Output:

```text
Traceback (most recent call last):
  File "example.py", line 7, in <module>
    price_of({"tea": 15, "coffee": 25}, "cake")
    ~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "example.py", line 5, in price_of
    raise KeyError(f"{item!r} is not on the menu; choose one of {sorted(menu)}") from None
KeyError: "'cake' is not on the menu; choose one of ['coffee', 'tea']"
```

Only one exception is printed now. Notice that `KeyError`'s quoting (section 7) wraps the whole message in double quotes. That is harmless, but it is one reason many programmers raise a `ValueError` for "not on the menu" messages meant for people, and keep `KeyError` for plain missing keys.

Use `from e` when the original error helps someone debug (a parse failure deep inside), and `from None` when it is just the obvious low-level form of the same problem (a missing key reported as a missing key).

### Under the hood: __context__, __cause__ and __suppress_context__

Every exception object has three attributes that record chaining:

- `__context__`: the exception that was being handled when this one was raised. Python sets it **automatically**.
- `__cause__`: the exception named in `raise ... from cause`. Set only by `from`.
- `__suppress_context__`: set to `True` by any `raise ... from ...` (including `from None`), and it tells the traceback printer not to show the automatic context.

```python
def convert(text):
    try:
        return int(text)
    except ValueError as e:
        raise ValueError("not a number: " + repr(text)) from e

try:
    convert("abc")
except ValueError as outer:
    print("outer:", outer)
    print("cause:", repr(outer.__cause__))
    print("context:", repr(outer.__context__))
    print("suppress context:", outer.__suppress_context__)
    print("same object?", outer.__cause__ is outer.__context__)
```

Output:

```text
outer: not a number: 'abc'
cause: ValueError("invalid literal for int() with base 10: 'abc'")
context: ValueError("invalid literal for int() with base 10: 'abc'")
suppress context: True
same object? True
```

When printing a traceback, Python follows `__cause__` if it is set ("direct cause"), otherwise `__context__` unless it is suppressed ("during handling"). Tests in this module check `__cause__` to make sure you used `from e`.

One more tool: since Python 3.11, `e.add_note("text")` attaches an extra line to an exception, shown under its message in the traceback. It is handy for adding context ("while reading question 4") and then re-raising with a bare `raise`.

### Predict the output

```python
def inner():
    raise KeyError("k")

def middle():
    try:
        inner()
    except KeyError as e:
        raise ValueError("bad key") from e

def outer():
    try:
        middle()
    except ValueError as e:
        print("caught", type(e).__name__, e)
        print("cause", type(e.__cause__).__name__, e.__cause__)
        raise

try:
    outer()
except Exception as e:
    print("top", type(e).__name__, e.__cause__ is not None)
```

<details><summary>Answer</summary>

```text
caught ValueError bad key
cause KeyError 'k'
top ValueError True
```

`inner` raises `KeyError('k')`; `middle` translates it into `ValueError('bad key')` with the `KeyError` as cause. `outer` catches the `ValueError`, prints it and its cause (note the quotes from `KeyError`'s `str`), then re-raises the **same** object with a bare `raise`, so the top level still sees a `ValueError` whose `__cause__` is set.

</details>

### Common misconceptions and edge cases

- "`raise e` and bare `raise` are the same." Bare `raise` re-raises the current exception unchanged. `raise e` also works, but adds the current line to the traceback; prefer bare `raise`.
- "Translating an exception loses the original." Not with `from e`: it is kept as `__cause__` and printed.
- "'During handling...' means two separate problems." Usually it means the handler itself is broken.
- Bare `raise` outside an `except` block raises `RuntimeError`.

---

## 12. Why bare except is dangerous

You will see this pattern in old tutorials and in code written in a hurry:

```python
try:
    ...
except:
    ...
```

An `except` with no type is called a **bare except**. It catches **everything** that can be raised: every ordinary error, every bug, and also `KeyboardInterrupt` and `SystemExit`. Its cousin `except Exception:` catches every ordinary error and every bug. Both feel safe ("my program will never crash!"), and both are dangerous for the same reason: they cannot tell the difference between the failure you expected and the bugs you did not.

### It hides bugs

```python
def average_marks(records):
    try:
        total = 0
        for record in records:
            total += record["marks"]
        return total / len(recrods)
    except:
        return 0

students = [{"name": "Asha", "marks": 80}, {"name": "Ravi", "marks": 70}]
print(average_marks(students))
print(average_marks([]))
```

Output:

```text
0
0
```

The author meant the bare except to handle one case: an empty list, where `len(records)` is 0. But look at the first call. Two students with 80 and 70 should average 75, and the function says `0`. There is a typo, `len(recrods)`, which raises `NameError` on **every** call. The bare except catches the `NameError` and turns it into `0`, for every input, forever, with no message. The program "works", and every average it reports is wrong.

A bare except turns a crash that points straight at the bug into a wrong answer that points nowhere. Remove the bare except, catch only what you expect, and the typo version announces itself:

```python
def average_marks(records):
    try:
        total = 0
        for record in records:
            total += record["marks"]
        return total / len(recrods)
    except ZeroDivisionError:
        return 0

print(average_marks([{"name": "Asha", "marks": 80}]))
```

Output:

```text
Traceback (most recent call last):
  File "example.py", line 10, in <module>
    print(average_marks([{"name": "Asha", "marks": 80}]))
          ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "example.py", line 6, in average_marks
    return total / len(recrods)
                       ^^^^^^^
NameError: name 'recrods' is not defined. Did you mean: 'records'?
```

### It swallows Ctrl+C and sys.exit

`sys.exit()` stops a program by **raising** `SystemExit`; pressing Ctrl+C raises `KeyboardInterrupt` in whatever code is running. A bare except catches both, so the program refuses to stop. This loop simulates a user pressing Ctrl+C three times (`raise KeyboardInterrupt` is exactly what Python does when the key is pressed):

```python
for attempt in range(1, 4):
    try:
        print("working... attempt", attempt)
        raise KeyboardInterrupt
    except:
        print("  something went wrong, trying again")
print("still running!")
```

Output:

```text
working... attempt 1
  something went wrong, trying again
working... attempt 2
  something went wrong, trying again
working... attempt 3
  something went wrong, trying again
still running!
```

The user is pressing Ctrl+C and the program keeps going. With `except Exception:` instead, `KeyboardInterrupt` would pass through and stop the program, which is what the user wanted. That difference is the whole reason `KeyboardInterrupt` and `SystemExit` live outside `Exception` in the hierarchy (section 4).

### except Exception: pass, the silent killer

The worst form of all:

```python
settings = {}

def load_setting(line):
    try:
        key, value = line.split("=")
        settings[key.strip()] = int(value)
    except Exception:
        pass

for line in ["volume = 7", "brightness=high", "speed = 3 = 4", "level = 2"]:
    load_setting(line)
print(settings)
```

Output:

```text
{'volume': 7, 'level': 2}
```

Two lines were bad, for two different reasons, and the program said nothing. Nobody will know why `brightness` is missing until something else breaks much later. `pass` in an `except` block means "I am sure this failure does not matter and nobody needs to know". That is almost never true. At the very least, report what was skipped and why.

### When catching broadly is right

There is one legitimate place for `except Exception`: a **boundary** where an unexpected error must not take down something bigger, and where you **report** it instead of hiding it. Examples: the top level of a program, which shows a friendly message instead of a traceback; or a loop that processes many independent jobs, where one broken job should be reported and the rest should still run.

```python
import sys

def main():
    data = {"a": 1}
    print("processing...")
    return data["b"]          # a bug we did not foresee

try:
    main()
except Exception as e:
    print("Sorry, something unexpected went wrong:", type(e).__name__, e)
    print("Please report this message to the developer.")
    sys.exit(1)
```

Output:

```text
processing...
Sorry, something unexpected went wrong: KeyError 'b'
Please report this message to the developer.
```

Even here, three rules hold: catch `Exception`, never bare; **show** the type and the message (or the whole traceback, with the `traceback` module's `print_exc()`); and do not pretend the work succeeded. `sys.exit(1)` ends the program with exit status 1, which tells the terminal (and scripts that run your program) that it failed.

### Common misconceptions and edge cases

- "A bare except makes my program robust." It makes it **quiet**. A robust program handles the expected failures and reports the unexpected ones.
- "`except Exception` is as bad as bare `except`." It is better, because Ctrl+C and `sys.exit()` still work, but it still hides bugs. Use it only at a reporting boundary.
- "`pass` is fine if the error is rare." Rare silent failures are the hardest bugs to find.
- Linters (tools that check style, like the ones in VS Code) warn about bare `except:` (rule E722) for exactly these reasons.

---

## 13. Keep try blocks narrow

A `try` block should contain **only the operations whose failure you are handling**. Everything else goes before it, after it, or in `else`. Here is why:

```python
def parse_entry(line):
    try:
        name, marks_text = line.split(",")
        marks = int(marks_text)
        return name.strip(), marks
    except ValueError:
        return "error: marks must be a whole number"

print(parse_entry("Asha, 82"))
print(parse_entry("Ravi, eighty"))
print(parse_entry("Meena, 75, 80"))
```

Output:

```text
('Asha', 82)
error: marks must be a whole number
error: marks must be a whole number
```

The third line has a perfectly good number. Its real problem is **three** fields instead of two. But unpacking three values into two names also raises `ValueError` ("too many values to unpack"), and the wide `try` block caught it with the wrong explanation. The message now lies to the user.

A narrow version checks each step separately, so each failure gets its own, true, message:

```python
def parse_entry(line):
    parts = line.split(",")
    if len(parts) != 2:
        return f"error: expected 'name, marks', got {len(parts)} fields"
    name, marks_text = parts
    try:
        marks = int(marks_text)
    except ValueError:
        return f"error: marks must be a whole number, got {marks_text.strip()!r}"
    return name.strip(), marks

print(parse_entry("Asha, 82"))
print(parse_entry("Ravi, eighty"))
print(parse_entry("Meena, 75, 80"))
```

Output:

```text
('Asha', 82)
error: marks must be a whole number, got 'eighty'
error: expected 'name, marks', got 3 fields
```

### A checklist for narrowing

- Put **setup** (code that cannot raise the handled exception, or should crash if it does) **before** the `try`.
- Put the **one operation** that can fail in the expected way inside the `try`.
- Put the **follow-up work** that uses the result in `else`, or after the whole statement if the `except` block returns or continues.
- If two operations can fail in the same way for different reasons (two `int()` calls on two fields), use two `try` statements or include which one failed in the message.

### Common misconceptions and edge cases

- "One big `try` around the function is simpler." It is shorter, and it makes every message a guess.
- "Narrow means one line." It means the **smallest region** whose failures share one cause and one response. Sometimes that is two or three lines.
- Narrowing is also faster to debug: when an unexpected exception escapes, its traceback points at code that was never meant to be protected.

---

## 14. EAFP versus LBYL

There are two styles of dealing with something that might not work.

- **LBYL**, "Look Before You Leap": check first, act only if the check passes. `if key in d: value = d[key]`.
- **EAFP**, "Easier to Ask Forgiveness than Permission": just do it, and handle the exception if it fails. `try: value = d[key] except KeyError: ...`.

Python code tends to prefer EAFP, for reasons this section explains. But it is not a religion: each style has cases where it is clearly better.

### Dict lookups

Counting words, three ways:

```python
words = "the cat and the hat and the bat".split()

counts_lbyl = {}
for w in words:
    if w in counts_lbyl:
        counts_lbyl[w] += 1
    else:
        counts_lbyl[w] = 1

counts_eafp = {}
for w in words:
    try:
        counts_eafp[w] += 1
    except KeyError:
        counts_eafp[w] = 1

counts_get = {}
for w in words:
    counts_get[w] = counts_get.get(w, 0) + 1

print(counts_lbyl)
print(counts_lbyl == counts_eafp == counts_get)
```

Output:

```text
{'the': 3, 'cat': 1, 'and': 2, 'hat': 1, 'bat': 1}
True
```

All three are correct. For a dict, the third, `dict.get` with a default (chapter 5), is the clearest of all. Python often provides a method that makes the question disappear; prefer it when it exists. EAFP shines when there is no such method, and when the check would repeat the work of the operation.

### Parsing numbers: the check is harder than it looks

LBYL for numbers seems easy: `if text.isdigit(): number = int(text)`. But `isdigit` asks a different question from the one `int` answers:

```python
samples = ["42", "-5", " 7", "+3", "1_000", "²", "4.0"]
for s in samples:
    try:
        result = int(s)
    except ValueError:
        result = "ValueError"
    print(f"{s!r:8} isdigit={s.isdigit()!s:5}  int -> {result}")
```

Output:

```text
'42'     isdigit=True   int -> 42
'-5'     isdigit=False  int -> -5
' 7'     isdigit=False  int -> 7
'+3'     isdigit=False  int -> 3
'1_000'  isdigit=False  int -> 1000
'²'      isdigit=True   int -> ValueError
'4.0'    isdigit=False  int -> ValueError
```

- `isdigit` rejects `"-5"`, `" 7"`, `"+3"` and `"1_000"`, which `int` accepts. An LBYL program would wrongly refuse a negative number or an answer with a stray space.
- Worse, `isdigit` **accepts** `"²"` (a superscript two is a "digit" character in Unicode), which `int` **rejects**. The LBYL program would pass the check and then crash anyway.

The only check that exactly matches "can `int` convert this?" is calling `int`. That is the core argument for EAFP: **when the check would have to duplicate the operation's own rules, let the operation be the check.**

```python
def parse_int(text, default=None):
    try:
        return int(text)
    except ValueError:
        return default

print([parse_int(s) for s in ["42", "-5", " 7", "abc", "²"]])
```

Output:

```text
[42, -5, 7, None, None]
```

### Races: the world can change between the look and the leap

LBYL has a deeper problem when the thing you check is **outside your program**: a file, a network connection, a shared resource. Between the moment you check and the moment you act, something else can change it.

```text
your program                          another program (or the user)
------------                          -----------------------------
if file "scores.txt" exists:   ok
                                      deletes "scores.txt"
    open "scores.txt"          -> FileNotFoundError, crash
```

The check passed, the file existed, and the program still crashed, because the check and the action are two separate moments. This bug is called a **race condition** (two things "racing" to touch the same resource), or more specifically "time of check to time of use". It appears only now and then, which makes it miserable to debug. The EAFP version has no gap: it just tries to open the file and handles `FileNotFoundError` **at the moment it actually happens**. With files coming in a later module, remember the rule now: **for anything outside your program, try it and handle the failure; do not check first**.

### Which one to choose

| Prefer LBYL when | Prefer EAFP when |
|---|---|
| The check is simple, cheap and exactly right: `if not items:`, `if n < 0:` | The check would duplicate complicated rules (`int()`, date formats) |
| Failure is **common**, part of normal flow (half the inputs are missing a key) | Failure is **rare** (an exception costs more than an `if`, but only when it is actually raised) |
| You must not start an action that cannot be undone halfway | The resource is outside your program (files, network): no race window |
| A method already answers the question: `dict.get`, `str.startswith` | The check and the action would look up the same thing twice |

When the two styles are equally good, choose the one that reads more clearly. And do not mix them pointlessly: checking `if key in d` **and** wrapping `d[key]` in `try` is twice the code for no gain.

### Common misconceptions and edge cases

- "EAFP is always faster." Entering a `try` costs almost nothing, but raising and catching an exception costs noticeably more than an `if`. In a loop where failure is common, LBYL can be faster. Measure before caring.
- "`isdigit()` checks whether `int()` will work." It does not: see the table above.
- "EAFP means catching everything." EAFP still catches **one specific** exception from **one** operation. `try: ... except: pass` is not EAFP; it is hiding.
- "LBYL is un-Pythonic." Simple checks like `if not name:` are perfectly good Python.

---

## 15. assert and when not to use it

### The assert statement

```python
assert condition, "message"
```

means: "I, the programmer, am certain that `condition` is true here. If it is not, my program has a bug: stop at once." If the condition is false, Python raises `AssertionError` with the message.

```python
def average(marks):
    assert len(marks) > 0, "average() needs at least one mark"
    return sum(marks) / len(marks)

print(average([70, 80]))
print(average([]))
```

Output:

```text
75.0
Traceback (most recent call last):
  File "example.py", line 6, in <module>
    print(average([]))
          ~~~~~~~^^^^
  File "example.py", line 2, in average
    assert len(marks) > 0, "average() needs at least one mark"
           ^^^^^^^^^^^^^^
AssertionError: average() needs at least one mark
```

An assertion documents an **assumption** and checks it while you develop. You have been reading thousands of them already: every test in this system is a list of `assert` statements, and pytest's job is to report the ones that fail.

### assert is switched off by -O

Python has an optimisation flag, `-O`. Running `python -O program.py` removes every `assert` statement from the program before it runs. The same program, run with `-O`:

```python
def average(marks):
    assert len(marks) > 0, "average() needs at least one mark"
    return sum(marks) / len(marks)

print(average([70, 80]))
print(average([]))
```

Output:

```text
75.0
Traceback (most recent call last):
  File "example.py", line 6, in <module>
    print(average([]))
          ~~~~~~~^^^^
  File "example.py", line 3, in average
    return sum(marks) / len(marks)
           ~~~~~~~~~~~^~~~~~~~~~~~
ZeroDivisionError: division by zero
```

The check is gone, and the empty list reaches the division. This is by design: assertions are meant to be **removable** without changing what a correct program does. Some servers and tools run Python with `-O`, so you cannot rely on an `assert` ever running.

### assert is for programmer mistakes, never for user input

From that one fact follows the rule:

- Use `assert` to state things that are true **if your code is correct**: an internal invariant ("the list is sorted at this point"), a result that should be in a range ("a discounted price is never more than the original"), a branch that should be impossible.
- **Never** use `assert` to check user input, file contents, function arguments from other people's code, or anything else that can legitimately be wrong. Those need `if ...: raise ValueError(...)`, which always runs, raises the **right** type, and carries a message for the user.

```python
def apply_discount(price, percent):
    if not 0 <= percent <= 100:                       # caller's mistake: always checked
        raise ValueError(f"percent must be from 0 to 100, got {percent}")
    new_price = price - price * percent / 100
    assert 0 <= new_price <= price, "discount arithmetic is wrong"   # my mistake
    return new_price

print(apply_discount(200, 15))
try:
    apply_discount(200, 150)
except ValueError as e:
    print("refused:", e)
```

Output:

```text
170.0
refused: percent must be from 0 to 100, got 150
```

There is a second reason not to use `assert` for input: it raises `AssertionError`, which says "a programmer's assumption is broken". A caller who wants to handle bad input expects `ValueError` or `TypeError`. Catching `AssertionError` in normal code is a sign something is designed wrong.

### The tuple trap

```python
x = 5
assert (x > 10, "x must be greater than 10")
print("reached the end")
```

Output:

```text
example.py:2: SyntaxWarning: assertion is always true, perhaps remove parentheses?
  assert (x > 10, "x must be greater than 10")
reached the end
```

The parentheses turned the condition and the message into **one tuple**, and a non-empty tuple is always truthy (chapter 2), so this assertion can never fail. Python 3.14 warns about it at compile time. Write `assert x > 10, "message"` without parentheses around the pair.

### Common misconceptions and edge cases

- "`assert` is a short way to raise `ValueError`." It raises `AssertionError`, and only when assertions are enabled.
- "Assertions slow the program down, so avoid them." They are cheap, and `-O` removes them. Use them generously for internal checks.
- "If the condition is false, `assert` returns `False`." It is a statement, not a function: it raises or does nothing.
- Do not put work with side effects in an assertion, such as `assert items.pop() == 3`: with `-O`, the `pop` disappears too.

---

## 16. Programs that never crash on bad input

Everything comes together here. A program that talks to a person must survive anything the person types.

### The ask-until-valid loop

The pattern: loop forever; read; try to convert; on failure, explain and `continue`; check the range; on success, `return` (which ends the loop).

```python
def ask_int(prompt, low, high):
    while True:
        text = input(prompt)
        try:
            number = int(text)
        except ValueError:
            print(f"{text!r} is not a whole number. Type digits, like {low}.")
            continue
        if low <= number <= high:
            return number
        print(f"{number} is out of range. Choose from {low} to {high}.")

choice = ask_int("Pick a number from 1 to 5: ", 1, 5)
print("You picked", choice)
```

Output:

```text
Pick a number from 1 to 5: three
'three' is not a whole number. Type digits, like 1.
Pick a number from 1 to 5: 9
9 is out of range. Choose from 1 to 5.
Pick a number from 1 to 5:  
' ' is not a whole number. Type digits, like 1.
Pick a number from 1 to 5:  3 
You picked 3
```

The user typed `three`, then `9`, then a single space, then ` 3 ` with spaces. Every bad answer got a message that says what to type, and the program never crashed. Notice the `try` contains only `int(text)`: the range check is not an exception and is not inside the `try`.

### Making it testable: pass ask in

`ask_int` calls `input()` and `print()` directly, so a test would have to type at the keyboard. Chapter 6 showed that functions are values you can pass around. Pass the **asking** and **telling** functions in as parameters, with `input` and `print` as the defaults:

```python
def ask_int(prompt, low, high, ask=input, tell=print):
    while True:
        text = ask(prompt)
        try:
            number = int(text)
        except ValueError:
            tell(f"{text!r} is not a whole number. Type digits, like {low}.")
            continue
        if low <= number <= high:
            return number
        tell(f"{number} is out of range. Choose from {low} to {high}.")

answers = iter(["abc", "0", "4"])
messages = []

def fake_ask(prompt):
    return next(answers)

result = ask_int("> ", 1, 5, ask=fake_ask, tell=messages.append)
print(result)
print(messages)
```

Output:

```text
4
["'abc' is not a whole number. Type digits, like 1.", '0 is out of range. Choose from 1 to 5.']
```

`fake_ask` hands out prepared answers (`iter` and `next` are from chapter 4), and `messages.append` collects everything the function would have printed. The real program still calls `ask_int("Pick: ", 1, 5)` and gets the keyboard and the screen. The build problem in this module uses exactly this design.

### End of input and Ctrl+C

Two more things can come out of `input()`:

- `EOFError`, when there is no more input: the user pressed **Ctrl+D** (Linux, macOS) or **Ctrl+Z then Enter** (Windows), or the program's input came from a file or pipe that ran out.
- `KeyboardInterrupt`, when the user pressed **Ctrl+C** while the program was waiting.

Neither is "bad input" to retry. They mean "the person wants to stop". The right place to handle them is the **top** of the program, once, with a polite goodbye instead of a traceback:

```python
def main():
    name = input("Your name: ")
    age = input("Your age: ")
    print("Hello", name)

try:
    main()
except (EOFError, KeyboardInterrupt):
    print()
    print("Goodbye.")
```

Output:

```text
Your name: Asha
Your age: 
Goodbye.
```

The input ran out after the name, `input("Your age: ")` raised `EOFError`, and the top level said goodbye. (The `print()` moves to a new line, because the prompt "Your age: " was still waiting on the current one.)

### Processing many items: skip, collect, report

When a program processes a **batch** (lines of a file, answers of a quiz, rows of marks), one bad item should not stop the rest. Put the `try` **inside** the loop, collect what went wrong, and report at the end:

```python
lines = ["Asha,82", "Ravi,eighty", "Meena", "Kiran,91", "Zoya,-5"]

marks = {}
errors = []
for number, line in enumerate(lines, start=1):
    parts = line.split(",")
    if len(parts) != 2:
        errors.append(f"line {number}: expected 'name,marks', got {line!r}")
        continue
    name, text = parts
    try:
        value = int(text)
    except ValueError:
        errors.append(f"line {number}: marks must be a whole number, got {text!r}")
        continue
    if not 0 <= value <= 100:
        errors.append(f"line {number}: marks must be from 0 to 100, got {value}")
        continue
    marks[name] = value

print(marks)
print(len(errors), "problem(s):")
for e in errors:
    print(" ", e)
```

Output:

```text
{'Asha': 82, 'Kiran': 91}
3 problem(s):
  line 2: marks must be a whole number, got 'eighty'
  line 3: expected 'name,marks', got 'Meena'
  line 5: marks must be from 0 to 100, got -5
```

Every good line was used, every bad line was reported with its line number and a message that says what was wrong, and nothing was silently dropped.

### Common misconceptions and edge cases

- "Wrap the whole program in `try/except Exception` and it will never crash." It will never **crash**, but it will also never tell you about its bugs. Handle bad **input** where it is read; let bugs surface.
- "Retry `EOFError` like bad input." With no input left, every retry fails again: an infinite loop. Treat it as "stop".
- "Use recursion to ask again (`return ask_int(...)` in the handler)." It works for a few retries, but each one adds a frame, and a determined user (or a script feeding bad input) hits `RecursionError` (chapter 6). Use a loop.
- `int(" 3 ")` is `3`: `int` strips surrounding whitespace for you. `int("")` and `int(" ")` raise `ValueError`.
- `float()` accepts `"nan"`, `"inf"` and `"-infinity"` without any exception, and such values silently break averages and comparisons. When a program needs an ordinary number, also check `math.isfinite(value)` (chapter 2 met its cousin `math.isnan`). Not every bad value announces itself with an exception.

---

## 17. Designing error handling

When you write a function or a program, walk through these questions.

1. **What can go wrong, legitimately?** List the operations that touch the world: conversions of user text, lookups of user-chosen keys, division by user numbers, files. Write down the exception each one raises.
2. **Who knows what to do about it?** The low-level function usually does not; let it raise (or translate the exception into a clearer one with `from`). The code that talks to the user, or that owns the loop over a batch, usually does; catch there.
3. **What exactly should be caught?** The specific types from step 1. Never bare `except:`. `except Exception` only at a reporting boundary.
4. **How small can the `try` be?** Only the failing operation; the rest goes before, in `else`, or after.
5. **What does the message say?** What was expected, what was received (with `repr`), what to do, and where.
6. **What must happen whatever the outcome?** Put clean-up in `finally`, and never `return` from it.
7. **What am I assuming about my own code?** State it with `assert`, and never use `assert` for anything a user or a file can break.

And one question for every `except` block you write: **if this handler runs because of a bug, will I ever find out?** If the answer is no, narrow the handler.

---

## Summary

- An **exception** is an object (type, `args`, message, traceback) that `raise` sends **up the call stack**. Each frame without a matching handler is abandoned at the line that was running; if no frame handles it, Python prints a traceback and exits with status 1.
- Built-in exceptions form a **hierarchy**. `except T` catches `T` and all its subclasses. `LookupError` covers `KeyError` and `IndexError`; `ArithmeticError` covers `ZeroDivisionError`. Ordinary errors descend from `Exception`; `KeyboardInterrupt` and `SystemExit` do not.
- `ValueError`: acceptable type, bad value. `TypeError`: wrong type altogether.
- In `try/except/else/finally`: `except` runs for a matching exception (the first matching clause only), `else` runs only if the `try` block finished normally, and `finally` runs **always**, last, even after `return` or an unhandled exception. A `return` in `finally` overrides everything and swallows exceptions: never do it.
- `except T as e` gives you the object; `e` is deleted after the block. `KeyError`'s `str` is quoted; use `e.args[0]` for the key.
- **Raise** built-in exceptions with messages that say what was expected, what was received (`!r`) and what to do. Validate early, before changing anything.
- Bare `raise` re-raises the current exception. `raise New(...) from e` translates and records the cause (`__cause__`); a new exception during handling is linked automatically (`__context__`); `from None` hides the context.
- Bare `except:` catches bugs, Ctrl+C and `sys.exit()`. `except Exception: pass` hides every bug. Catch specific exceptions in **narrow** `try` blocks.
- **EAFP** (try it, handle the failure) beats **LBYL** (check first) when the check would duplicate complicated rules or when the world can change between check and action. Simple, exact checks are fine LBYL.
- `assert` states programmer assumptions; it is removed by `-O`. Never use it for user input.
- A program that never crashes reads input in a loop, catches the specific conversion errors, explains, asks again, and handles `EOFError`/`KeyboardInterrupt` once at the top.

## Learning outcomes

After this chapter and its problems you should be able to:

- Read a multi-frame traceback, including chained ones, and say where the exception was raised and through which calls it travelled.
- Place any common built-in exception in the hierarchy and predict which `except` clauses catch it.
- **Handle the exact exceptions a piece of code can raise, and nothing more**, in a `try` block that contains only the code that can fail.
- **Explain when `else` and `finally` run**, including with `return` inside `try`, and predict the output of any `try` statement.
- Raise `ValueError` and `TypeError` correctly, and **write error messages that tell the user what to do**.
- Re-raise with bare `raise`, translate with `raise ... from e`, and explain `__cause__` and `__context__`.
- Explain why bare `except:` and `except Exception: pass` are dangerous, and find bugs they hide.
- Choose between EAFP and LBYL and justify the choice, including the race-condition argument.
- Explain what `assert` is for, why `-O` matters, and why it must not validate input.
- Write input loops and batch processors that never crash on bad data, and that are testable without a keyboard.

## Module project

The project for this module is a **robust, input-driven quiz program that never crashes**. Questions live in data: a list of dicts such as `{"question": "7 x 8?", "answer": "56", "kind": "int"}`, with kinds like `"int"`, `"text"` and `"choice"` (with a list of options). The program asks each question, checks the answer, keeps score, and prints a report at the end. Whatever the user types, including nothing, letters for numbers, `7.5`, a choice that does not exist, Ctrl+D or Ctrl+C, the program responds with a helpful message and keeps going (or says goodbye politely), and never shows a traceback.

Suggested milestones:

1. **Ask until valid.** Write `ask_int(prompt, low, high, ask=input, tell=print)` and `ask_choice(prompt, options, ask=input, tell=print)` with narrow `try` blocks and messages that say what to type. Test them with fake `ask` functions.
2. **Check answers.** `check_answer(question, text)` returns `True`/`False`, and **raises** `ValueError` with a clear message when the answer cannot even be interpreted (for example `"abc"` for an `int` question), so the caller can ask again without counting a wrong answer.
3. **Validate the question data.** Before the quiz starts, check every question dict: required keys present, known kind, options present for `"choice"`. Raise `ValueError` naming the question number and the problem. Bad data is the **author's** mistake, so it should stop the program before the first question, with a precise message.
4. **The quiz loop.** Score, number of attempts, a report at the end. One retry per invalid answer, unlimited; a wrong answer counts.
5. **The top level.** `main()` with `EOFError` and `KeyboardInterrupt` handled once ("Quiz stopped. You scored 3 of 5 so far."), and a `finally` that always prints the score summary.
6. **Stretch.** Load questions from a text format (`question | answer | kind`), reporting every bad line with its number instead of stopping at the first; then run with a deliberately broken question file and a deliberately rude user.

Problem p034 in this module is the assessed stepping stone: a small quiz engine with exactly this design. Be ready to explain which exceptions each function can raise, where each one is caught, and why there is no bare `except` anywhere.

## Further reading

All links are to the official Python documentation.

- Tutorial, errors and exceptions: https://docs.python.org/3/tutorial/errors.html
- Built-in exceptions, with the full hierarchy at the end: https://docs.python.org/3/library/exceptions.html
- Language reference, the try statement (exact rules for except, else, finally): https://docs.python.org/3/reference/compound_stmts.html#the-try-statement
- Language reference, the raise statement (chaining with from): https://docs.python.org/3/reference/simple_stmts.html#the-raise-statement
- Language reference, the assert statement: https://docs.python.org/3/reference/simple_stmts.html#the-assert-statement
- Glossary entries EAFP and LBYL: https://docs.python.org/3/glossary.html#term-EAFP
- The traceback module (printing tracebacks yourself): https://docs.python.org/3/library/traceback.html
- Command line option -O: https://docs.python.org/3/using/cmdline.html#cmdoption-O
- PEP 765, disallowing return/break/continue that exit a finally block (the 3.14 warning): https://peps.python.org/pep-0765/
- PEP 3134, exception chaining and embedded tracebacks (`__cause__`, `__context__`): https://peps.python.org/pep-3134/
- PEP 678, enriching exceptions with notes (`add_note`): https://peps.python.org/pep-0678/
