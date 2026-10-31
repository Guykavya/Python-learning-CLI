# Chapter 20: Debugging, profiling and code quality

Every programmer writes bugs. The difference between a beginner and a professional is not that the professional writes fewer bugs (they write plenty); it is that the professional **finds them quickly, fixes them properly, and makes sure they never come back**. The same is true of slow code: everyone writes slow code sometimes, but a professional *measures* before guessing, and fixes the part that really matters.

Up to now you have met bugs one at a time and fixed them by staring at the code until the problem jumped out. That works for ten lines. It does not work for a thousand lines written by three people over two years. This chapter replaces staring with **methods and tools**:

a repeatable **method** for hunting any bug and reading the clues Python gives you (tracebacks); **debuggers** (`pdb`, the VS Code debugger) that stop a running program so you can look inside; **logging**, the grown-up form of `print` debugging; **search techniques** (bisection, shrinking an input) that work even when you have no idea where the bug is; **measurement tools** for speed (`timeit`, `cProfile`, line profilers) and memory (`tracemalloc`), and the habits that turn a measurement into a real speed-up; **code quality tools** (`ruff`, `black`, `mypy`, `pre-commit`) that catch whole families of mistakes before the code even runs; and the quiet skill of **reading other people's code**.

The chapter has three learning outcomes:

1. **Find bugs systematically**: reproduce, read the traceback, use a debugger and logging, and narrow the search with bisection and shrinking.
2. **Measure before you optimise**: time code honestly, profile it to find the hot spot, check memory, and prove a speed-up with before/after numbers.
3. **Keep code healthy**: set up linters, a formatter, a type checker and pre-commit hooks, and read unfamiliar code with a plan.

**A note on how examples are shown.** Every block that has output was really run, with **Python 3.14** on Linux. Folder names are shown as `/home/you/debug/...`. **Timings, memory sizes and addresses are machine-specific**: your numbers will differ, but the *ratios* (this one is 10 times faster than that one) should be similar. The tools `ruff 0.17.3`, `black 26.10.1`, `mypy 2.4.1`, `pre-commit 4.7.0` and `line_profiler 5.1.0` were run in a separate virtual environment; their messages can change a little between versions. The debugger `pdb` also changes its look a little between Python versions (section 4 says where). All code works on Python 3.11 and newer.

**Setup.** Everything up to section 12 uses only the standard library. Section 13 uses extra tools that you install yourself if you want to follow along (`pip install ruff black mypy pre-commit`); this course does not need them to run.

## Table of contents

1. [Debugging is a method](#1-debugging-is-a-method)
2. [Reading tracebacks](#2-reading-tracebacks)
3. [Print debugging and `assert`](#3-print-debugging-and-assert)
4. [`pdb` and `breakpoint()`](#4-pdb-and-breakpoint)
5. [The VS Code debugger](#5-the-vs-code-debugger)
6. [Logging as a debugging tool](#6-logging-as-a-debugging-tool)
7. [Narrowing down: bisection, shrinking, the rubber duck](#7-narrowing-down-bisection-shrinking-the-rubber-duck)
8. [Measuring speed with `timeit` and `perf_counter`](#8-measuring-speed-with-timeit-and-perf_counter)
9. [`cProfile` and `pstats`](#9-cprofile-and-pstats)
10. [Line-level profiling](#10-line-level-profiling)
11. [Memory: `tracemalloc`](#11-memory-tracemalloc)
12. [Making it faster](#12-making-it-faster)
13. [Code quality tools: ruff, black, mypy, pre-commit](#13-code-quality-tools-ruff-black-mypy-pre-commit)
14. [Reading other people's code](#14-reading-other-peoples-code)
15. [Project walkthrough: profile and speed up a slow program](#15-project-walkthrough-profile-and-speed-up-a-slow-program)
16. [Common traps and summary](#16-common-traps-and-summary)

## 1. Debugging is a method

### 1.1 Why "try things until it works" fails

When a program misbehaves, the natural reaction is to change something, run it again, change something else, run it again. Sometimes the bug disappears. But did you *fix* it, or did you only hide it? Do you know *why* it happened? Will it come back next week with different data?

Random changes have three problems:

1. **They are slow.** Each guess costs a run, and the number of possible guesses is huge.
2. **They add new bugs.** Every change you do not understand is a new risk.
3. **They teach you nothing.** After an hour you have a working program and no idea what was wrong.

Debugging is closer to a **science experiment** than to guessing. A scientist does not mix random chemicals; they form a hypothesis and design an experiment that can prove it wrong. That is exactly the loop you will use.

### 1.2 The debugging loop

```text
   1. REPRODUCE   make the bug happen on demand, the smaller the better
        |
   2. ISOLATE     find where it goes wrong: which input, which function, which line
        |
   3. HYPOTHESISE say one precise guess: "the total is wrong because rounding drops a paisa"
        |
   4. TEST        run an experiment that could prove the guess WRONG
        |         (wrong guess? go back to 2 or 3 with what you learned)
   5. FIX         change the code for the cause, not the symptom
        |
   6. PREVENT     add a test that fails on the old code and passes on the new
```

Each step has a reason:

- **Reproduce first**, because you cannot check a fix for a bug you cannot trigger. "It crashes sometimes" is not a bug report you can work with; "it crashes when the file has an empty last line" is.
- **Isolate**, because a bug in a 2,000-line program is hard, and a bug in a 5-line function is easy. Every step in this chapter (tracebacks, debuggers, bisection) is a tool for shrinking the search area.
- **Hypothesise precisely**, because a vague guess ("something with the loop") cannot be tested. A precise guess ("on the last iteration `i` is `len(items)`") can.
- **Test the hypothesis**, not the fix. First *prove* you understand the bug, then change the code.
- **Fix the cause.** If a function receives `None` where it expected a list, adding `if x is None: return` inside it may hide a bug in the caller that produced the `None`.
- **Prevent** with a test, so the same bug can never come back silently. This is called a **regression test**.

### 1.3 A worked example

A bill-splitting app has a complaint: "When 3 friends split ₹100, the app says everyone pays ₹33.33, but the restaurant wants ₹100, not ₹99.99."

**Reproduce.** Write a tiny script that calls the function with the reported input and a few others:

```python
def split_bill(total, people):
    share = round(total / people, 2)
    return [share] * people


for total, people in [(90, 3), (100, 4), (100, 3), (10, 6)]:
    shares = split_bill(total, people)
    print(total, people, shares, round(sum(shares), 2))
```
```text
90 3 [30.0, 30.0, 30.0] 90.0
100 4 [25.0, 25.0, 25.0, 25.0] 100.0
100 3 [33.33, 33.33, 33.33] 99.99
10 6 [1.67, 1.67, 1.67, 1.67, 1.67, 1.67] 10.02
```

Now the bug is on demand, and we found a second case the user did not report: ₹10 for 6 people adds up to ₹10.02, *more* than the bill.

**Isolate.** Splits that divide evenly (90/3, 100/4) are fine. Only uneven splits break. The function is two lines, so the problem is in `round(total / people, 2)`.

**Hypothesise.** "When the bill does not divide evenly into whole paise, rounding each share throws away (or adds) a fraction of a paisa, and multiplying by the number of people makes that error bigger."

**Test.** The hypothesis predicts: 100 / 3 = 33.333..., rounded down to 33.33, error 0.0033 per person, times 3 people = 0.01 short. 10 / 6 = 1.666..., rounded *up* to 1.67, error 0.0033 per person, times 6 = 0.02 too much. Both numbers match the output. The hypothesis survives.

**Fix the cause.** Money cannot be split into equal parts of a paisa, so *someone* must pay one paisa more. Work in whole paise (integers, no rounding errors) and give the leftover paise to the first people:

```python
def split_bill(total, people):
    paise = round(total * 100)
    base, extra = divmod(paise, people)
    # the first `extra` people pay one paisa more
    return [(base + 1) / 100 if i < extra else base / 100 for i in range(people)]
```
```text
90 3 [30.0, 30.0, 30.0] 90.0
100 4 [25.0, 25.0, 25.0, 25.0] 100.0
100 3 [33.34, 33.33, 33.33] 100.0
10 6 [1.67, 1.67, 1.67, 1.67, 1.66, 1.66] 10.0
```

**Prevent.** A regression test states the *rule* the bug broke (shares add up to the total and differ by at most one paisa) over many inputs:

```python
def test_shares_add_up():
    for total in (1, 10, 99.99, 100, 1234.5):
        for people in range(1, 13):
            shares = split_bill(total, people)
            assert round(sum(shares), 2) == total, f"{total} / {people} -> {shares}"
            assert max(shares) - min(shares) <= 0.011, "shares differ by more than 1 paisa"
```
```text
.                                                                        [100%]
1 passed in 0.13s
```

Notice what we did *not* do: we did not try `math.floor`, then `math.ceil`, then `round(..., 3)` to see what happens. Each step had a reason.

### 1.4 Keep a debugging log

For any bug that takes more than ten minutes, write down what you tried in a text file: "Hypothesis: X. Experiment: Y. Result: Z." It feels slow, but it stops you running the same experiment twice, and when you ask someone for help you can show them exactly what you already ruled out.

#### Try it 1.1

Match each action to the step of the loop (reproduce, isolate, hypothesise, test, fix, prevent).

1. "I think `parse_date` fails only for dates with a single-digit day, like `5/3/2024`."
2. You add `test_single_digit_day()` to the test file.
3. You copy the customer's CSV file and run the import on your laptop until it crashes the same way.
4. You call `parse_date("5/3/2024")` and `parse_date("15/3/2024")` directly in a Python shell.
5. You notice the crash happens only in the import step, not in the export step.

<details><summary>Answer</summary>

1. Hypothesise: one precise, testable guess.
2. Prevent: a regression test.
3. Reproduce: make the bug happen on demand.
4. Test: an experiment whose result could prove the guess wrong (if `15/3/2024` also fails, the guess "single-digit day" is wrong).
5. Isolate: shrinking the search area to one part of the program.

</details>

## 2. Reading tracebacks

### 2.1 A traceback is a map, not an insult

When an exception is not caught, Python prints a **traceback** and stops. Many beginners read only the last line, or nothing at all. That wastes the best clue you will ever get: the traceback tells you **what** went wrong, **where** it happened, and **how the program got there**.

Here is a small order-totalling program with a bad line in its data:

```python
def parse_line(line):
    name, qty, price = line.split(",")
    return name, int(qty), float(price)


def load(lines):
    return [parse_line(line) for line in lines]


def total(lines):
    rows = load(lines)
    return sum(qty * price for _, qty, price in rows)


print(total(["pen,2,10.5", "book,1,250", "bag,two,800"]))
```
```text
Traceback (most recent call last):
  File "/home/you/debug/orders.py", line 15, in <module>
    print(total(["pen,2,10.5", "book,1,250", "bag,two,800"]))
          ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/you/debug/orders.py", line 11, in total
    rows = load(lines)
  File "/home/you/debug/orders.py", line 7, in load
    return [parse_line(line) for line in lines]
            ~~~~~~~~~~^^^^^^
  File "/home/you/debug/orders.py", line 3, in parse_line
    return name, int(qty), float(price)
                 ~~~^^^^^
ValueError: invalid literal for int() with base 10: 'two'
```

### 2.2 How to read it

A traceback is a list of **frames**. A frame is one function call that was still running when the error happened: its code, its line, its local variables. The list is printed **outermost first, innermost last** ("most recent call last").

Read it in this order:

1. **The last line first.** `ValueError: invalid literal for int() with base 10: 'two'`. The exception type (`ValueError`) tells you the *kind* of problem; the message tells you the details. Here: something tried `int('two')`.
2. **The last frame next.** `File ".../orders.py", line 3, in parse_line`. This is where the exception was *raised*. The `~~~^^^^^` marks under the code (Python 3.11+) point at the exact part of the line: `int(qty)`.
3. **Walk upwards** to see how you got there: `<module>` (line 15) called `total`, which called `load`, which called `parse_line`. Each frame is a link in the chain.
4. **Find the first frame in *your* code that made a wrong decision.** The crash is in `parse_line`, but is `parse_line` wrong? It was given bad data. Maybe the real fix is in the data, or maybe `parse_line` should give a clearer error. The traceback tells you where the program *noticed* the problem, which is not always where the *mistake* is.

`<module>` in a frame line means "the top level of the file", outside any function.

### 2.3 When the last frame is not your code

Often the deepest frames are inside the standard library or a package (the middle of this traceback is shortened):

```python
import json


def load_settings(text):
    return json.loads(text)


print(load_settings("{'debug': true}"))
```
```text
Traceback (most recent call last):
  File "/home/you/debug/settings.py", line 8, in <module>
    print(load_settings("{'debug': true}"))
          ~~~~~~~~~~~~~^^^^^^^^^^^^^^^^^^^
  File "/home/you/debug/settings.py", line 5, in load_settings
    return json.loads(text)
           ~~~~~~~~~~^^^^^^
  File "/usr/lib/python3.14/json/__init__.py", line 352, in loads
    return _default_decoder.decode(s)
           ~~~~~~~~~~~~~~~~~~~~~~~^^^
  ... (two more frames inside json/decoder.py) ...
json.decoder.JSONDecodeError: Expecting property name enclosed in double quotes: line 1 column 2 (char 1)
```

The bug is almost never in `json/decoder.py`, which millions of people use every day. Skip the library frames and look at the **last frame in your own files**: `load_settings`, line 5, which passed `"{'debug': true}"`. The message explains the rest: JSON needs double quotes, and this text uses single quotes. Rule of thumb: **suspect your own code first**.

### 2.4 Chained exceptions: cause and context

Sometimes one exception leads to another, and Python prints **two** tracebacks joined by a sentence. That sentence matters, because there are two different kinds of chain.

**Explicit chain: `raise ... from ...`.** You catch a low-level error and raise a clearer one, and you say on purpose "this was caused by that":

```python
import json


class ConfigError(Exception):
    pass


def read_port(text):
    try:
        data = json.loads(text)
        return int(data["port"])
    except KeyError as exc:
        raise ConfigError("config has no 'port'") from exc


read_port('{"host": "x"}')
```
```text
Traceback (most recent call last):
  File "/home/you/debug/chain.py", line 11, in read_port
    return int(data["port"])
               ~~~~^^^^^^^^
KeyError: 'port'

The above exception was the direct cause of the following exception:

Traceback (most recent call last):
  File "/home/you/debug/chain.py", line 16, in <module>
    read_port('{"host": "x"}')
    ~~~~~~~~~^^^^^^^^^^^^^^^^^
  File "/home/you/debug/chain.py", line 13, in read_port
    raise ConfigError("config has no 'port'") from exc
ConfigError: config has no 'port'
```

"**The above exception was the direct cause of the following exception**" means: someone wrote `from`. The original error is stored in the new exception's `__cause__` attribute. This is a deliberate translation, usually good design.

**Implicit chain: an error inside an `except` block.** If new code in an `except` (or `finally`) block crashes, Python keeps the first error too, because you probably want to know about both:

```python
def average(nums):
    try:
        return sum(nums) / len(nums)
    except ZeroDivisionError:
        print("log: empty list in", nums.name)   # bug inside the handler


average([])
```
```text
Traceback (most recent call last):
  File "/home/you/debug/context.py", line 3, in average
    return sum(nums) / len(nums)
           ~~~~~~~~~~^~~~~~~~~~~
ZeroDivisionError: division by zero

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  File "/home/you/debug/context.py", line 8, in <module>
    average([])
    ~~~~~~~^^^^
  File "/home/you/debug/context.py", line 5, in average
    print("log: empty list in", nums.name)   # bug inside the handler
                                ^^^^^^^^^
AttributeError: 'list' object has no attribute 'name'
```

"**During handling of the above exception, another exception occurred**" usually means **a bug in the error handler**. The first error was expected and being dealt with; the second one was an accident. Fix the second one first. The earlier exception is stored in `__context__`.

**Hiding the chain: `from None`.** When the inner error is an implementation detail that would only confuse the reader, write `raise LookupError(f"unknown code {key!r}") from None`. Then only the new exception's traceback is printed. `from None` sets `__suppress_context__ = True`; the old exception is still stored in `__context__`, but not shown.

| You see | Meaning | Attribute set |
|---|---|---|
| "direct cause of the following exception" | someone wrote `raise New(...) from old` | `__cause__` = old |
| "During handling of the above exception..." | a new error happened inside `except`/`finally` | `__context__` = old |
| only one traceback, though `raise` was inside `except` | `raise New(...) from None` | `__suppress_context__` = True |

### 2.5 Notes and exception groups

Since Python 3.11 you can attach extra lines to an exception with `add_note`, without changing its type. This is useful when the low-level message lacks context:

```python
def to_int(value, row):
    try:
        return int(value)
    except ValueError as exc:
        exc.add_note(f"while reading row {row}")
        raise


to_int("12a", 7)
```
```text
Traceback (most recent call last):
  File "/home/you/debug/notes.py", line 9, in <module>
    to_int("12a", 7)
    ~~~~~~^^^^^^^^^^
  File "/home/you/debug/notes.py", line 3, in to_int
    return int(value)
ValueError: invalid literal for int() with base 10: '12a'
while reading row 7
```

The note appears after the message. A bare `raise` re-raises the *same* exception, so the traceback still points at the original line.

An **`ExceptionGroup`** (also 3.11+) carries several exceptions at once, for example "3 of the 10 rows were bad". Its traceback is drawn as a box, with a numbered part (`+---- 1 ----`, `+---- 2 ----`) per sub-exception; read each part like a normal traceback. You will meet them mostly in libraries that run many tasks at once.

The `traceback` module turns an exception into the same text, so a program can save it in a log instead of dying: `traceback.format_exc()` inside an `except` block returns the full traceback as one string. Logging does this for you (section 6.6).

#### Try it 2.1

Look at the `orders.py` traceback in 2.1. (a) Which function raised the exception? (b) Which function called `load`? (c) Which *data* is to blame, and what are two reasonable fixes?

<details><summary>Answer</summary>

(a) `parse_line`, at line 3: the innermost (last) frame.
(b) `total`, at line 11: the frame just above `load`.
(c) The line `"bag,two,800"`: the quantity is a word. Fix one: correct the data (`"bag,2,800"`). Fix two: make `parse_line` give a better error, for example catch the `ValueError` and raise `ValueError(f"bad quantity in {line!r}") from exc`, or add a note naming the line. Which one is right depends on the spec: should bad lines stop the program or be reported and skipped?

</details>

#### Try it 2.2

Predict the sentence that joins the two tracebacks, then the type of the exception's `__cause__` and `__context__`.

```python
def load(name):
    try:
        return {"a": 1}[name]
    except KeyError:
        raise ValueError(f"no setting {name!r}")


load("b")
```

<details><summary>Answer</summary>

```text
KeyError: 'b'

During handling of the above exception, another exception occurred:

Traceback (most recent call last):
  ...
ValueError: no setting 'b'
```

(Shortened; the full output has both tracebacks.) There is no `from`, so the `ValueError` has `__cause__ = None` and `__context__` is the `KeyError`. The printed sentence says "During handling", which makes it look like an accident even though the `raise` was on purpose. Writing `from exc` (or `from None`) states your intent and gives the reader the right sentence.

</details>

## 3. Print debugging and `assert`

### 3.1 Print debugging is fine, used well

Adding `print` calls is the oldest debugging technique, and there is nothing shameful about it. It is fast, it works everywhere, and sometimes it is the quickest way to see what a loop is doing. The trick is to print **useful** things.

The f-string `=` specifier (Python 3.8+) prints both the expression and its value, so you never wonder which number is which:

```python
def dedupe(names):
    seen = []
    for name in names:
        key = name.strip().lower()
        print(f"{name=} {key=} {seen=}")
        if key not in seen:
            seen.append(name)
    return seen


print(dedupe(["Asha", "asha ", "Ravi"]))
```
```text
name='Asha' key='asha' seen=[]
name='asha ' key='asha' seen=['Asha']
name='Ravi' key='ravi' seen=['Asha', 'asha ']
['Asha', 'asha ', 'Ravi']
```

The second line shows the bug at once: `key` is `'asha'` but `seen` holds `'Asha'`, the *original* name, so `key not in seen` is always true. The fix is to keep the keys in a separate set (`seen_keys.add(key)`) and the original names in the result list.

Notice that `name=` printed `'asha '` with quotes. That is `repr()`, not `str()`, and it matters:

```python
values = ["10", 10, "10 ", None, "None"]
for v in values:
    print(v)
print("---")
for v in values:
    print(repr(v))
```
```text
10
10
10 
None
None
---
'10'
10
'10 '
None
'None'
```

With plain `print` the string `"10"`, the number `10` and the string `"10 "` look identical. With `repr` you see the types and the trailing space. **When debugging, always print `repr`** (or use `{x=}` / `{x!r}`).

### 3.2 The limits of print

Print debugging has real costs. **You must know in advance what to print**: guess wrong and you edit and run again, while a debugger (section 4) lets you look at *anything* once the program is stopped. **It floods**: a `print` in a loop that runs 100,000 times buries the one interesting line. **It is forgotten**: debug prints get committed and end up in production output. **It cannot be switched off**: logging (section 6) can, by level, without touching the code.

A good rule: print for a two-minute investigation, a debugger for a "where does it go wrong?" question, and logging for anything you might need again.

### 3.3 `assert` as a debugging tool

An `assert` states something you believe is **always** true at that point (an **invariant**). If your belief is wrong, the program stops right there, at the first moment the belief breaks, instead of ten functions later when the damage becomes visible:

```python
def apply(balance, transactions):
    for amount in transactions:
        balance += amount
        assert balance >= 0, f"balance went negative: {balance} after {amount}"
    return balance


print(apply(100, [50, -30, -200, 40]))
```
```text
Traceback (most recent call last):
  File "/home/you/debug/invariant.py", line 8, in <module>
    print(apply(100, [50, -30, -200, 40]))
          ~~~~~^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/home/you/debug/invariant.py", line 4, in apply
    assert balance >= 0, f"balance went negative: {balance} after {amount}"
           ^^^^^^^^^^^^
AssertionError: balance went negative: -80 after -200
```

Without the `assert`, the function would return `-40` and some report three steps later would show a strange number. With it, you know the exact transaction that broke the rule. Asserts **move the crash closer to the cause**, which is the whole job of isolation.

Good things to assert while debugging:

- a list is still sorted after you insert into it;
- a total equals the sum of its parts;
- an id is unique; a date is after the previous one;
- a function's result has the type and length you expect.

### 3.4 What `assert` must never do

`assert` statements are **removed** when Python runs with the `-O` (optimise) flag:

```text
$ python -O invariant.py
-40
```

The check vanished and the wrong answer came out. So:

- **Never use `assert` to check user input or data from outside** (files, the network, function arguments in a public API). Use `if ...: raise ValueError(...)` for that.
- **Never put side effects in an assert**: `assert items.pop() == 3` stops popping under `-O`.
- Use `assert` for **"this cannot happen if my code is right"** checks. They are a debugging net, not a guard rail.

#### Try it 3.1

A function receives `qty` from a web form. A teammate writes `assert qty > 0, "quantity must be positive"`. What goes wrong, and what should they write?

<details><summary>Answer</summary>

Two problems. First, under `python -O` the check disappears and a zero or negative quantity is accepted. Second, an `AssertionError` says "the programmer made a mistake", but here the *user* typed a bad value, which is an expected situation. Write a real check:

```python
if qty <= 0:
    raise ValueError(f"quantity must be positive, got {qty!r}")
```

</details>

## 4. `pdb` and `breakpoint()`

### 4.1 Why a debugger?

A **debugger** pauses a running program and lets you look around: print any variable, walk up to the function that called this one, run one line at a time and watch values change, then continue. You no longer have to guess in advance what to print. You stop at the interesting moment and *ask*.

Python ships with a debugger called **`pdb`** (Python DeBugger). It runs in the terminal, so it works everywhere: on your laptop, on a server over SSH, inside a test run. Graphical debuggers like the one in VS Code (section 5) do the same things with buttons; once you understand `pdb`, they are easy.

### 4.2 Three ways to start `pdb`

1. **`breakpoint()` in your code.** The program runs normally until it reaches that line, then pauses and shows the `(Pdb)` prompt. This is the most common way.
2. **`python -m pdb script.py`.** Starts the script *already paused* on its first line. Useful when you cannot or do not want to edit the file. If the script crashes, `pdb` enters **post-mortem** mode at the crash (4.6).
3. **After a crash: `pdb.pm()`** in an interactive shell, or `pdb.post_mortem()` inside an `except` block, to inspect the frame where the exception happened.

### 4.3 A first session

This program counts grades. It has a bug that we will hunt in a moment, but first we just walk around:

```python
def letter(score):
    if score >= 90:
        return "A"
    if score >= 75:
        return "B"
    if score > 50:
        return "C"
    return "F"


def report(scores):
    counts = {}
    for name, score in scores.items():
        grade = letter(score)
        counts[grade] = counts.get(grade, 0) + 1
    return counts


marks = {"asha": 91, "ravi": 50, "meera": 75, "john": 49}
breakpoint()
print(report(marks))
```

Here is a real session. The commands typed by the user are shown after each `(Pdb)` prompt; everything else is printed by `pdb`.

```text
$ python grades.py
> /home/you/debug/grades.py(20)<module>()
-> breakpoint()
(Pdb) l
 15             counts[grade] = counts.get(grade, 0) + 1
 16         return counts
 17
 18
 19     marks = {"asha": 91, "ravi": 50, "meera": 75, "john": 49}
 20  -> breakpoint()
 21     print(report(marks))
[EOF]
(Pdb) n
> /home/you/debug/grades.py(21)<module>()
-> print(report(marks))
(Pdb) s
--Call--
> /home/you/debug/grades.py(11)report()
-> def report(scores):
(Pdb) ll
 11  -> def report(scores):
 12         counts = {}
 13         for name, score in scores.items():
 14             grade = letter(score)
 15             counts[grade] = counts.get(grade, 0) + 1
 16         return counts
(Pdb) n
> /home/you/debug/grades.py(12)report()
-> counts = {}
(Pdb) n
> /home/you/debug/grades.py(13)report()
-> for name, score in scores.items():
(Pdb) n
> /home/you/debug/grades.py(14)report()
-> grade = letter(score)
(Pdb) p name, score
('asha', 91)
(Pdb) n
> /home/you/debug/grades.py(15)report()
-> counts[grade] = counts.get(grade, 0) + 1
(Pdb) p grade
'A'
(Pdb) w
  /home/you/debug/grades.py(21)<module>()
-> print(report(marks))
> /home/you/debug/grades.py(15)report()
-> counts[grade] = counts.get(grade, 0) + 1
(Pdb) r
--Return--
> /home/you/debug/grades.py(16)report()->{'A': 1, 'B': 1, 'F': 2}
-> return counts
(Pdb) c
{'A': 1, 'F': 2, 'B': 1}
```

How to read this:

- `> /home/you/debug/grades.py(20)<module>()` is the **current position**: file, line 20, at module level. The line after `->` is the line **about to run** (it has not run yet).
- `l` (list) shows source around the current line; the arrow marks the current line. `ll` (long list) shows the whole current function.
- `n` (next) runs the current line and stops at the next line **in the same function**. It does not go inside function calls.
- `s` (step) runs the current line but **goes into** a function call: here it entered `report`. `--Call--` marks the entry.
- `p expr` prints any Python expression in the current frame. `p name, score` prints a tuple.
- `w` (where) prints the **call stack**, like a traceback, outermost first; the `>` marks the frame you are looking at.
- `r` (return) runs until the current function is about to return, and shows the return value after `->`.
- `c` (continue) runs until the next breakpoint or the end of the program.

**Version note.** Since Python 3.13, `breakpoint()` stops *on* the `breakpoint()` line itself (line 20 above). Python 3.11 and 3.12 stop on the line *after* it (line 21). The listing layout and some messages also differ slightly between versions. The commands are the same everywhere. (Also, `pdb` shows the dict in the `--Return--` line in sorted key order; the program's own `print` shows insertion order. Same dict, different display.)

### 4.4 The commands you will actually use

| Command | Long name | What it does |
|---|---|---|
| `l` / `ll` | list / longlist | show source near the current line / the whole function |
| `n` | next | run this line, stop at the next line of this function |
| `s` | step | run this line, stop inside any function it calls |
| `c` | continue | run until a breakpoint (or the end) |
| `r` | return | run until this function returns |
| `until` | until | run until a line **greater** than the current one is reached (leaves a loop) |
| `p expr` | print | print the value of an expression |
| `pp expr` | pretty-print | print big structures over several lines |
| `w` | where | show the call stack |
| `u` / `d` | up / down | move one frame up (to the caller) / down again, to inspect its variables |
| `b` | break | `b 14` (line), `b letter` (function), `b 14, score <= 50` (conditional); `b` alone lists breakpoints |
| `cl N` | clear | delete breakpoint number N |
| `condition N expr` | condition | add or change the condition of breakpoint N |
| `display expr` | display | show `expr` every time it changes when the program stops |
| `interact` | interact | open a normal Python shell with the current variables (Ctrl-D to return) |
| `q` | quit | stop the program |
| `h cmd` | help | help for any command |

Two practical notes. If a variable is called `n` or `c`, typing `n` runs the *command*; use `p n`, or prefix Python with `!` (`!n = 5`). And an empty line repeats the last command, so you can keep pressing Enter to step with `n`.

### 4.5 Hunting the bug: conditional breakpoints, `up` and `down`

The report says `{'A': 1, 'F': 2, 'B': 1}`. Ravi scored exactly 50 and the school rule says "50 and above is a C". Two students got F; one of them should not have. We do not want to step through every student, so we set a **conditional breakpoint** that only stops when the score is 50 or lower. This time we start the program with `python -m pdb` (and no `breakpoint()` line in the file):

```text
$ python -m pdb grades2.py
> /home/you/debug/grades2.py(1)<module>()
-> def letter(score):
(Pdb) b 14, score <= 50
Breakpoint 1 at /home/you/debug/grades2.py:14
(Pdb) c
> /home/you/debug/grades2.py(14)report()
-> grade = letter(score)
(Pdb) p name, score
('ravi', 50)
(Pdb) s
--Call--
> /home/you/debug/grades2.py(1)letter()
-> def letter(score):
(Pdb) n
> /home/you/debug/grades2.py(2)letter()
-> if score >= 90:
(Pdb) n
> /home/you/debug/grades2.py(4)letter()
-> if score >= 75:
(Pdb) n
> /home/you/debug/grades2.py(6)letter()
-> if score > 50:
(Pdb) n
> /home/you/debug/grades2.py(8)letter()
-> return "F"
(Pdb) p score > 50
False
(Pdb) u
> /home/you/debug/grades2.py(14)report()
-> grade = letter(score)
(Pdb) p counts
{'A': 1}
(Pdb) d
> /home/you/debug/grades2.py(8)letter()
-> return "F"
(Pdb) cl 1
Deleted breakpoint 1 at /home/you/debug/grades2.py:14
(Pdb) c
{'A': 1, 'F': 2, 'B': 1}
The program finished and will be restarted
> /home/you/debug/grades2.py(1)<module>()
-> def letter(score):
(Pdb) q
```

The conditional breakpoint skipped Asha (91) and stopped on Ravi (50). Stepping into `letter` showed the path: past `>= 90`, past `>= 75`, then `score > 50` was `False`, so 50 fell through to `"F"`. We confirmed the hypothesis with `p score > 50`. The fix is `>=` on line 6. Then `u` moved **up** to the caller's frame (`report`), where we could inspect `counts`, and `d` moved back **down**. Moving up and down does not run any code; it only changes which frame's variables `p` sees.

The same check could be written in two steps: `b 14` sets the breakpoint, then `condition 1 score <= 50` adds the condition. `condition 1` with no expression removes it again.

### 4.6 Leaving a loop with `until`, watching with `display`

```python
def running_max(nums):
    best = nums[0]
    out = []
    for x in nums:
        if x > best:
            best = x
        out.append(best)
    return out


print(running_max([3, 1, 4, 1, 5]))
```

```text
$ python -m pdb loop.py
> /home/you/debug/loop.py(1)<module>()
-> def running_max(nums):
(Pdb) b 7
Breakpoint 1 at /home/you/debug/loop.py:7
(Pdb) c
> /home/you/debug/loop.py(7)running_max()
-> out.append(best)
(Pdb) display best
display best: 3
(Pdb) cl 1
Deleted breakpoint 1 at /home/you/debug/loop.py:7
(Pdb) until
> /home/you/debug/loop.py(8)running_max()
-> return out
display best: 5  [old: 3]
(Pdb) p out
[3, 3, 4, 4, 5]
```

`display best` asks `pdb` to show `best` whenever the program stops and the value has changed (here it shows the old value too). `until` at the last line of the loop body ran the **rest of the loop** and stopped at the first line after it (line 8). With `n` you would have needed about a dozen presses. Note that we cleared the breakpoint on line 7 first; otherwise `until` would have stopped there again on the next iteration.

### 4.7 Post-mortem debugging

When a program crashes, the frames still exist for a moment. **Post-mortem** debugging means opening `pdb` at the crash, with all variables intact. With `python -m pdb`, type `c` and the crash drops you into post-mortem mode automatically:

```text
$ python -m pdb orders.py
> /home/you/debug/orders.py(1)<module>()
-> def parse_line(line):
(Pdb) c
Traceback (most recent call last):
  ... (pdb's own frames, then the same traceback as in 2.1) ...
ValueError: invalid literal for int() with base 10: 'two'
Uncaught exception. Entering post mortem debugging
Running 'cont' or 'step' will restart the program
> /home/you/debug/orders.py(3)parse_line()
-> return name, int(qty), float(price)
(Pdb) p line
'bag,two,800'
(Pdb) p qty
'two'
(Pdb) u
> /home/you/debug/orders.py(7)load()
-> return [parse_line(line) for line in lines]
(Pdb) pp lines
['pen,2,10.5', 'book,1,250', 'bag,two,800']
(Pdb) q
```

The traceback in the middle is abbreviated here; the real one starts with a few frames from `pdb.py` and `bdb.py` (the debugger's own machinery), which you skip.

Inside your own code, `pdb.post_mortem()` called in an `except` block opens the debugger at the frame where the current exception was raised, so you can look at the values that caused it before the program goes on. In an interactive Python shell, after an uncaught exception, `import pdb; pdb.pm()` does the same for the last crash.

### 4.8 `PYTHONBREAKPOINT` and `sys.breakpointhook`

`breakpoint()` is not hard-wired to `pdb`. It calls the function stored in `sys.breakpointhook`, which by default reads the environment variable **`PYTHONBREAKPOINT`**:

- `PYTHONBREAKPOINT=0` turns every `breakpoint()` into a no-op. The grades program runs straight through:

  ```text
  $ PYTHONBREAKPOINT=0 python grades.py
  {'A': 1, 'F': 2, 'B': 1}
  ```

  This is a safety net: a forgotten `breakpoint()` on a server would otherwise freeze the program waiting for input.
- `PYTHONBREAKPOINT=some.module.function` calls that function instead (for example a different debugger you installed).

You can also replace the hook in code. The hook receives no information about where it was called from, but `sys._getframe(1)` gives the caller's frame (the leading underscore means "implementation detail": fine for debugging tools, not for normal code):

```python
import sys


def show_locals(*args, **kwargs):
    caller = sys._getframe(1)
    print("breakpoint at line", caller.f_lineno, "locals:", caller.f_locals)


sys.breakpointhook = show_locals


def area(w, h):
    result = w * h
    breakpoint()
    return result


area(3, 4)
sys.breakpointhook = sys.__breakpointhook__
```
```text
breakpoint at line 14 locals: {'w': 3, 'h': 4, 'result': 12}
```

`sys.__breakpointhook__` always holds the original hook, so you can restore it. Tools like test runners use this trick to make `breakpoint()` behave differently.

#### Try it 4.1

Which `pdb` command fits each situation?

1. You are inside `parse_line` and want to see the variables of the function that called it.
2. The current line is `total = compute(items)`. You trust `compute` and want to move to the next line.
3. The current line is `total = compute(items)`. You suspect `compute`.
4. You are on the last line of a loop that has 500 iterations left; you want to be after the loop.
5. A loop processes 10,000 orders and only order id 7731 misbehaves.
6. You want to see a big nested dict in a readable layout.

<details><summary>Answer</summary>

1. `u` (up), then `p` the variables. `d` brings you back.
2. `n`: run the line without going inside `compute`.
3. `s`: step into `compute`.
4. `until` (or set a breakpoint after the loop and `c`).
5. A conditional breakpoint: `b <line>, order.id == 7731`, then `c`.
6. `pp the_dict`.

</details>

#### Try it 4.2

In the `running_max` session, suppose you did **not** clear breakpoint 1 before typing `until`. Where would the program stop, and what would `display` show?

<details><summary>Answer</summary>

`until` runs until a line greater than 7 is reached **or a breakpoint is hit**. The next iteration reaches line 7 again, which has a breakpoint, so it stops at line 7 (second iteration, `x = 1`). `best` is still 3, so `display` shows nothing new. That is why the session cleared the breakpoint first.

</details>

## 5. The VS Code debugger

### 5.1 Same ideas, with a mouse

The VS Code debugger (from the Python extension) does everything `pdb` does, with a graphical layout: variables in a side panel, the call stack as a clickable list, and breakpoints as red dots. For long investigations it is more comfortable; `pdb` remains useful on servers, in plain terminals and when you only have a few seconds.

The controls map one-to-one onto `pdb`: **Continue** (F5) is `c`, **Step Over** (F10) is `n`, **Step Into** (F11) is `s`, **Step Out** (Shift+F11) is `r`, **Stop** (Shift+F5) is `q`. Clicking left of a line number sets a breakpoint (`b`). Hovering a name, or typing in the *Debug Console*, is `p`. The *Watch* panel is `display`, and the *Call Stack* panel replaces `w`, `u` and `d`: click any frame to see its variables.

### 5.2 `launch.json`

To start a program under the debugger, VS Code needs a **launch configuration**. Open the *Run and Debug* view, choose "create a launch.json file", pick *Python Debugger*. The file lives at `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "Report with sample data",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder}/report.py",
            "args": ["data/sample.csv", "--verbose"],
            "env": {"REPORT_MODE": "test"},
            "console": "integratedTerminal",
            "justMyCode": true
        }
    ]
}
```

- `program` is the script to run (`${file}` would mean "the file open in the editor").
- `args` are the command-line arguments (`sys.argv[1:]`), `env` adds environment variables.
- `justMyCode: true` makes *Step Into* skip library code, like our rule "suspect your own code first". Set it to `false` when you really need to step into a library.
- (Older versions of the extension used `"type": "python"`; the current one is `"debugpy"`.)

### 5.3 Conditional breakpoints, hit counts and logpoints

Right-click a breakpoint dot and choose *Edit Breakpoint*. There are three kinds:

- **Expression**: stop only when the expression is true (`score <= 50`), exactly like `pdb`'s conditional breakpoint.
- **Hit Count**: stop on the N-th time the line runs (for example `100`). Useful for "it breaks on the 100th iteration".
- **Log Message** (a **logpoint**, shown as a diamond): do *not* stop, just print a message to the Debug Console, with expressions in braces: `student {name} scored {score}`. A logpoint is a `print` you do not have to add to the code and cannot forget to remove.

### 5.4 Debugging a failing test

Most bugs are found by a failing test, so debugging tests directly is the common case.

**In VS Code:** open the *Testing* view (the beaker icon), find the test, and click *Debug Test*. Breakpoints in the test or in the code under test work as usual. The extension discovers pytest tests once it knows which interpreter (virtual environment) to use.

**In the terminal:** `pytest --pdb` opens `pdb` post-mortem at the first failure. Take this function and its tests:

```python
# discount.py
def final_price(price, percent):
    cut = price * percent // 100
    return price - cut
```
```python
# test_discount.py
from discount import final_price


def test_ten_percent():
    assert final_price(250, 10) == 225


def test_odd_price():
    assert final_price(95, 10) == 85.5
```

```text
$ python -m pytest -q --pdb test_discount.py
.F
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> traceback >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

    def test_odd_price():
>       assert final_price(95, 10) == 85.5
E       assert 86 == 85.5
E        +  where 86 = final_price(95, 10)

test_discount.py:9: AssertionError
>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>> entering PDB >>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>

>>>>>>>>>>>>>>>>>> PDB post_mortem (IO-capturing turned off) >>>>>>>>>>>>>>>>>>>
> /home/you/debug/test_discount.py(9)test_odd_price()
-> assert final_price(95, 10) == 85.5
(Pdb) p final_price(95, 10)
86
(Pdb) p 95 * 10 // 100, 95 * 10 / 100
(9, 9.5)
(Pdb) q
=========================== short test summary info ============================
FAILED test_discount.py::test_odd_price - assert 86 == 85.5
!!!!!!!!!!!!!!!!!!! _pytest.outcomes.Exit: Quitting debugger !!!!!!!!!!!!!!!!!!!
1 failed, 1 passed in 0.40s
```

The failure was an `assert` in the test itself, so post-mortem stopped in the test frame. We used `p` to **call** the function and test a hypothesis directly: `//` (floor division) drops the half rupee. Other useful pytest options: `--trace` stops at the *start* of each test, `-x` stops after the first failure, and `-k name` picks one test.

#### Try it 5.1

Write the logpoint message that prints the order id and total for every order, and the breakpoint expression that stops only for orders over ₹10,000 that have no customer.

<details><summary>Answer</summary>

Logpoint: `order {order.id} total {order.total}`.
Expression: `order.total > 10_000 and order.customer is None`.

</details>

## 6. Logging as a debugging tool

### 6.1 Why logging instead of print

A `print` is a one-off. A **log message** is a permanent, labelled, switchable record. Each message has a **level** (how serious it is), so you can show only warnings in normal use and every detail when hunting a bug, **without editing code**. Each comes from a named **logger** (`"shop.cart"`), so you can turn on details for one part of the program only. Where the output goes (screen, file, both) and how it looks is decided in **one place**. And a library that logs does not force output on the programs that use it; a library that prints does. Logging is what you leave in the code after the bug is fixed, so that next time the clues are already there.

### 6.2 Levels

| Level | Number | Use it for |
|---|---|---|
| `DEBUG` | 10 | details for developers: values, decisions, loop steps |
| `INFO` | 20 | normal milestones: "started", "processed 120 rows" |
| `WARNING` | 30 | something odd but handled: "coupon expired, ignored" |
| `ERROR` | 40 | an operation failed: "payment failed" |
| `CRITICAL` | 50 | the program cannot go on |

A logger has a **level**, and messages below that level are dropped. The quickest setup is `logging.basicConfig`, which configures the **root** logger once:

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s %(levelname)-8s %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)
log = logging.getLogger("shop.cart")

log.debug("cart has %d items", 3)
log.info("checkout started for %s", "asha")
log.warning("coupon %r expired", "DIWALI10")
log.error("payment failed")
log.critical("database unreachable")
```
```text
13:04:40 DEBUG    shop.cart: cart has 3 items
13:04:40 INFO     shop.cart: checkout started for asha
13:04:40 WARNING  shop.cart: coupon 'DIWALI10' expired
13:04:40 ERROR    shop.cart: payment failed
13:04:40 CRITICAL shop.cart: database unreachable
```

(The times are machine-specific, of course.) Change `level=logging.DEBUG` to `logging.WARNING` and only the last three lines appear. That one-word change is the whole point.

Without any configuration, the root logger's level is `WARNING`, so `debug` and `info` messages silently vanish, and warnings go to standard error with no format at all (Python's "last resort" handler). This surprises everyone once: "my `log.info` does nothing!" means "nobody configured logging".

### 6.3 Loggers, handlers, formatters

The logging system has three kinds of objects:

- A **logger** is what your code calls: `log.info(...)`. Get one with `logging.getLogger(name)`. The same name always returns the **same** logger object. Convention: `logging.getLogger(__name__)`, so the logger is named after the module.
- A **handler** decides **where** a message goes: `StreamHandler` (a stream such as `sys.stdout` or `sys.stderr`), `FileHandler` (a file), and others. A logger can have several handlers.
- A **formatter** decides **how** a message looks, using `%(name)s`, `%(levelname)s`, `%(message)s`, `%(asctime)s`, `%(funcName)s`, `%(lineno)d` and more.

Both loggers **and** handlers have levels. A message must pass the logger's level, then each handler's level, to be written by that handler.

### 6.4 The logger tree and propagation

Logger names with dots form a **tree**: `"app.db"` is a child of `"app"`, which is a child of the **root** logger (`""`). After a logger's own handlers have handled a message, it **propagates** the message up to its parent's handlers, and so on to the root.

```python
import logging
import sys

handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter("[%(name)s] %(levelname)s %(message)s"))

app = logging.getLogger("app")
app.setLevel(logging.INFO)
app.addHandler(handler)

db = logging.getLogger("app.db")          # child of "app"
db.info("connected")                        # travels up to app's handler
db.debug("query plan ...")                  # below app.db's effective level
db.setLevel(logging.DEBUG)
db.debug("now debug is on for app.db only")

print(db.parent.name, db.handlers, db.propagate)
```
```text
[app.db] INFO connected
[app.db] DEBUG now debug is on for app.db only
app [] True
```

Observe:

- `app.db` has **no handlers of its own**, yet its messages appear: they propagated to `app`'s handler.
- `app.db` has no level of its own at first, so its **effective level** is inherited from its parent (`INFO`). So the first `debug` was dropped.
- After `db.setLevel(logging.DEBUG)`, debug messages from `app.db` pass, while other children of `app` stay at `INFO`. This is how you "turn on debugging for the database part only".

One subtle rule: when a message propagates, the **parent loggers' levels are not checked again**, only the parent **handlers'** levels. Try 6.1 shows the consequence.

### 6.5 The duplicate-handler trap

```python
import logging
import sys


def get_logger():
    log = logging.getLogger("report")
    log.setLevel(logging.INFO)
    log.addHandler(logging.StreamHandler(sys.stdout))
    return log


get_logger().info("first")
get_logger().info("second")
get_logger().info("third")
```
```text
first
second
second
third
third
third
```

`getLogger("report")` returns the same object every time, and each call adds **another** handler. After three calls there are three handlers, so the third message is written three times. Fixes: configure logging **once**, at program start; or check `if not log.handlers:` before adding. Messages appearing twice is also the symptom of a handler on both a child and the root, with `propagate` left `True`. Set `log.propagate = False` when a logger has its own handler and you do not want the root to repeat its messages.

### 6.6 Logging exceptions

Inside an `except` block, `log.exception(...)` logs at `ERROR` level **and adds the full traceback**:

```python
import logging
import sys

logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format="%(levelname)s %(message)s")
log = logging.getLogger("prices")

for text in ["120", "abc", "80"]:
    try:
        price = int(text)
    except ValueError:
        log.exception("bad price %r", text)
    else:
        log.info("price ok: %d", price)
```
```text
INFO price ok: 120
ERROR bad price 'abc'
Traceback (most recent call last):
  File "/home/you/debug/exc.py", line 10, in <module>
    price = int(text)
ValueError: invalid literal for int() with base 10: 'abc'
INFO price ok: 80
```

The program kept going, and the log still has the traceback for later. `log.error("...", exc_info=True)` does the same at any level you choose. Compare with `log.error(f"bad price {text}")`, which loses the traceback: the most valuable clue is gone.

### 6.7 Lazy formatting: pass arguments, not f-strings

Notice that the examples write `log.info("price ok: %d", price)`, not `log.info(f"price ok: {price}")`. With `%`-style arguments, the logger builds the final string **only if the message will be written**:

```python
import logging

calls = 0


class Expensive:
    def __str__(self):
        global calls
        calls += 1
        return "big report"


log = logging.getLogger("lazy")
log.setLevel(logging.INFO)
thing = Expensive()

log.debug(f"state: {thing}")       # f-string: formatted even though DEBUG is off
log.debug("state: %s", thing)      # %-style: never formatted
print("__str__ calls:", calls)
```
```text
__str__ calls: 1
```

Both debug messages were dropped, but the f-string was built anyway (one `__str__` call), because Python evaluates arguments before calling `log.debug`. In a hot loop with debug logging off, that waste adds up. There is a second benefit: tools that collect logs can group all messages with the same template `"bad price %r"`, which they cannot do with already-formatted strings. (If the *argument itself* is expensive to compute, guard it: `if log.isEnabledFor(logging.DEBUG): ...`.)

### 6.8 `basicConfig` versus `dictConfig`

`basicConfig` is fine for scripts. It only works **once**: if the root logger already has handlers, later calls do nothing (unless you pass `force=True`). Larger programs describe the whole setup as a dictionary with `logging.config.dictConfig`, often loaded from a file:

```python
import logging
import logging.config
import sys

CONFIG = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "short": {"format": "%(levelname)s %(name)s: %(message)s"},
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "short",
            "level": "INFO",
        },
    },
    "loggers": {
        "shop": {"level": "DEBUG", "handlers": ["console"], "propagate": False},
    },
}

logging.config.dictConfig(CONFIG)
logging.getLogger("shop.cart").debug("hidden by the handler level")
logging.getLogger("shop.cart").info("visible")
```
```text
INFO shop.cart: visible
```

The `shop` logger lets `DEBUG` through, but the console handler only writes `INFO` and above. `"disable_existing_loggers": False` matters: the default `True` silences every logger created before the call (for example module-level loggers in imported modules), a classic "my logs disappeared" bug.

**Rules of thumb.** Libraries and modules: `log = logging.getLogger(__name__)` and *never* configure handlers. The program's entry point (`main`): configure once. Tests: use pytest's `caplog` fixture (chapter 19) to check messages.

#### Try it 6.1

Predict the output. The root logger has a handler with no level of its own; the root logger itself keeps its default level `WARNING`.

```python
import logging
import sys

root_handler = logging.StreamHandler(sys.stdout)
root_handler.setFormatter(logging.Formatter("root saw: %(name)s %(message)s"))
logging.getLogger().addHandler(root_handler)        # root logger, level WARNING

api = logging.getLogger("api")
api.setLevel(logging.DEBUG)
api_handler = logging.StreamHandler(sys.stdout)
api_handler.setLevel(logging.INFO)
api_handler.setFormatter(logging.Formatter("api saw: %(name)s %(message)s"))
api.addHandler(api_handler)

logging.getLogger("api.users").debug("one")
logging.getLogger("api.users").info("two")
logging.getLogger("worker").info("three")
logging.getLogger("worker").error("four")
```

<details><summary>Answer</summary>

```text
root saw: api.users one
api saw: api.users two
root saw: api.users two
root saw: worker four
```

- `"one"` (DEBUG): `api.users` inherits `DEBUG` from `api`, so the message is created. `api_handler` (INFO) drops it. It propagates to the root, whose **handler** has no level, and the root **logger's** `WARNING` level is **not** checked during propagation. So the root handler prints it. Surprising, but that is the rule.
- `"two"` (INFO): passes `api_handler`, then propagates to the root handler too: printed twice.
- `"three"` (INFO): `worker` inherits `WARNING` from the root, so the message is dropped at the very start.
- `"four"` (ERROR): passes, printed by the root handler.

To stop the double messages, set `api.propagate = False`, or give the root handler a level.

</details>

## 7. Narrowing down: bisection, shrinking, the rubber duck

### 7.1 When you have no idea where the bug is

Tracebacks and debuggers work when you know roughly where to look. Some bugs give no such clue: "the report total was right last month and is wrong now", or "the import crashes on this 50,000-line file". For these, there are **search methods** that work even when you understand nothing yet. They all rely on the idea behind binary search: **cut the search space in half with each experiment**.

### 7.2 Bisecting history

Suppose the program worked at version 1 and fails at version 12, and you have every version in between. Testing each version one by one takes up to 11 experiments. **Bisection** tests the middle version first:

- If the middle is **bad**, the first bad version is in the first half.
- If the middle is **good**, it is in the second half.

Each experiment halves the range. For `n` versions you need about `log2(n)` experiments: 4 for 12 versions, 10 for 1,000, 20 for a million. The only requirement is a **reliable test** that answers "good or bad" for one version, and the assumption that once the bug appears it stays.

Git has this built in: **`git bisect`**. You tell it one bad commit and one good commit, and it checks out commits in the middle for you. With `git bisect run`, it even runs your test script for each one: exit code 0 means good, anything else (from 1 to 127, except 125) means bad.

Here is a real run. A repository has 12 commits of a `price.py` file; somewhere a `>=` became `>`, so an order of exactly ₹1000 lost its discount. The check script lives *outside* the repository so that checking out old commits does not change it:

```python
# check.py (outside the repository)
import sys

sys.path.insert(0, ".")          # import price.py from the checked-out folder
from price import discount

assert discount(1000) == 900, "1000 should get the discount"
```

```text
$ git bisect start HEAD HEAD~11
Bisecting: 5 revisions left to test after this (roughly 3 steps)
[8af2fe17a16334a51fc23b2f394d39b27ad0d847] change 6
$ git bisect run python3 ../check.py
running 'python3' '../check.py'
Bisecting: 2 revisions left to test after this (roughly 2 steps)
[a9d9ecf568090b6055efb88d75301964a34734cb] change 9
running 'python3' '../check.py'
Traceback (most recent call last):
  File "/home/you/debug/repo/../check.py", line 6, in <module>
    assert discount(1000) == 900, "1000 should get the discount"
           ^^^^^^^^^^^^^^^^^^^^^
AssertionError: 1000 should get the discount
Bisecting: 0 revisions left to test after this (roughly 1 step)
[9d55629a65b507d2d912e5a47713634cd61954b1] change 8
running 'python3' '../check.py'
Traceback (most recent call last):
  ...
AssertionError: 1000 should get the discount
Bisecting: 0 revisions left to test after this (roughly 0 steps)
[da70ddc1c58e9db7ba33f751f62a1e4bde6eed21] change 7
running 'python3' '../check.py'
9d55629a65b507d2d912e5a47713634cd61954b1 is the first bad commit
commit 9d55629a65b507d2d912e5a47713634cd61954b1
  ... (author, date, message "change 8", and the files it changed) ...
bisect found first bad commit
$ git bisect reset
```

(Commit hashes and dates are machine-specific.) Four test runs (change 6 good, 9 bad, 8 bad, 7 good) pinned the bug to "change 8" out of 11 candidates. Now `git show` on that one commit shows the small diff that contains the bug. `git bisect reset` returns to where you started.

**A trap we fell into while preparing this example.** The first version of `check.py` forgot the `sys.path` line and failed with `ModuleNotFoundError` on *every* commit. `git bisect` happily reported "change 2" as the first bad commit, which was nonsense. **Bisection is only as good as its test.** Before you trust the answer, run your check by hand on one known-good and one known-bad version.

The same halving idea works without git: on dates in a log file ("which day did the numbers go wrong?"), on configuration options, on library versions, on the lines of a data file. Problem p011 asks you to write it as a function that counts its experiments.

### 7.3 Shrinking a failing input

A program crashes on a 10,000-row file. You could debug with the whole file, but every run is slow and every `print` floods. Much better: find a **small** input that still fails. Small failing inputs are easy to reason about, make perfect regression tests, and often make the cause obvious.

The simplest shrinking strategy is again halving: try the first half; if it still fails, keep it. Otherwise try the second half. Stop when neither half fails on its own.

```python
def buggy_mean(nums):
    total = 0
    for x in nums:
        if x < 0:
            x = -x            # the bug: negative numbers become positive
        total += x
    return total / len(nums) if nums else 0


def fails(nums):
    return buggy_mean(nums) != (sum(nums) / len(nums) if nums else 0)


def shrink_by_halves(items, fails):
    """Keep the half that still fails, as long as one does."""
    steps = 0
    while len(items) > 1:
        half = len(items) // 2
        first, second = items[:half], items[half:]
        steps += 1
        if fails(first):
            items = first
        elif fails(second):
            items = second
        else:
            break                 # the bug needs pieces from both halves
        print(f"step {steps}: {items}")
    return items


data = [4, 8, 15, 16, 23, 42, -7, 1, 2, 9, 30, 11]
print("fails on full data:", fails(data))
print("shrunk to:", shrink_by_halves(data, fails))
```
```text
fails on full data: True
step 1: [-7, 1, 2, 9, 30, 11]
step 2: [-7, 1, 2]
step 3: [-7]
shrunk to: [-7]
```

Twelve numbers became one: `[-7]`. Now the cause is obvious: negative numbers are handled wrongly. Notice that `fails` is a small function that answers one question, "does this input still show the bug?". Writing that function is the real work; the shrinking loop is generic.

Halving has a weakness, shown in Try it 7.2: when the bug needs **two** elements that sit in different halves, neither half fails and the loop gives up. The full algorithm, **delta debugging** (*ddmin*, by Andreas Zeller), keeps going with finer pieces (quarters, eighths, ...) and finally tries removing single elements, until no single element can be removed without the bug disappearing. Such a result is called **1-minimal**. Problem p012 asks you to build a simple version. Property-based testing tools such as `hypothesis` (chapter 19) do the same thing automatically when they "shrink" a failing example.

### 7.4 The rubber duck

The cheapest debugging tool is an object on your desk. **Rubber duck debugging** means explaining your code, line by line, out loud, to someone who knows nothing, even a toy duck. It works because explaining forces you to say what each line *actually* does instead of what you *meant* it to do; the gap between the two is usually the bug. If you have ever found your own bug in the middle of asking someone for help, you have already used the duck.

A written version: before asking for help, write down (1) what you expected, (2) what happened instead, (3) the smallest input that shows it, and (4) what you already tried. Half the time the answer appears while writing; the other half, your helper gets everything they need.

#### Try it 7.1

A bug appeared somewhere in the last 1,000 commits. (a) What is the most number of test runs `git bisect` needs? (b) Each test run takes 3 minutes. How long is that, compared with testing every commit?

<details><summary>Answer</summary>

(a) About 10, since 2^10 = 1024 ≥ 1000 (each run halves the candidates: 1000, 500, 250, ..., 1).
(b) About 30 minutes, against up to 1,000 × 3 = 3,000 minutes (two days) for testing every commit one by one.

</details>

#### Try it 7.2

Predict what `shrink_by_halves` prints and returns here:

```python
def fails(nums):
    return 0 in nums and 99 in nums     # needs both a 0 and a 99


print(shrink_by_halves([5, 0, 7, 3, 2, 99, 8, 1], fails))
```

<details><summary>Answer</summary>

```text
[5, 0, 7, 3, 2, 99, 8, 1]
```

No `step` lines at all. The first half `[5, 0, 7, 3]` has no 99, and the second half `[2, 99, 8, 1]` has no 0, so neither fails and the loop stops on the first try, returning the input unchanged. This is exactly why delta debugging goes on to try smaller pieces, and removing single elements, instead of only halves. Removing one element at a time would reach `[0, 99]`.

</details>

## 8. Measuring speed with `timeit` and `perf_counter`

### 8.1 Measure first, always

Programmers are famously bad at guessing where their programs spend time. The slow part is often a line that "obviously" costs nothing: a `x in some_list` inside a loop, a function that rebuilds the same table every call, a string grown one piece at a time. So the rule of this half of the chapter is:

> **Do not optimise what you have not measured.**

Measurement answers two questions: **how long does this take?** (this section) and **where does the time go?** (sections 9 and 10).

### 8.2 `time.perf_counter` for one rough measurement

`time.perf_counter()` returns a high-resolution clock reading in seconds. Its absolute value means nothing; only the **difference** between two readings does:

```python
import time

start = time.perf_counter()
total = sum(i * i for i in range(1_000_000))
elapsed = time.perf_counter() - start
print(f"total={total}  took {elapsed:.3f} s")
```
```text
total=333332833333500000  took 0.054 s
```

(Machine-specific timing.) Use `perf_counter`, not `time.time()`: `time.time()` is the wall-clock date and time, which can jump when the computer adjusts its clock, and it often has coarser resolution.

One measurement like this is fine for "is this 50 ms or 5 seconds?". For comparing two versions of a small piece of code it is not enough, because of **noise**.

### 8.3 Why one run lies: noise

Your program shares the computer with the operating system, the browser, music, antivirus. Any of them can steal a few milliseconds during your measurement. CPU frequency changes, caches are warm or cold. If you time a 50-microsecond operation once, the noise can be bigger than the thing you measure.

The `timeit` module fights noise in two ways:

1. It runs the statement **many times in a loop** (`number`) and measures the total, so tiny per-run noise averages out and the clock's resolution stops mattering.
2. It repeats that whole measurement **several times** (`repeat`) and lets you take the **minimum**.

Why the **minimum** and not the average? Noise only ever makes code *slower*; nothing makes it run faster than it can. The fastest of several repeats is the one with the least interference, the closest to the true cost. The average mixes in the noise. (The spread between repeats is still useful: a big spread warns you that the machine was busy.)

### 8.4 `timeit` from the command line

```text
$ python -m timeit -s "nums = list(range(1000))" "sum(nums)"
50000 loops, best of 5: 3.97 usec per loop
$ python -m timeit -s "nums = list(range(1000))" "total = 0" "for x in nums: total += x"
10000 loops, best of 5: 21.3 usec per loop
```

(Machine-specific timings.) `-s` is **setup**: run once per measurement, not timed. The statements after it are timed; several statement arguments become several lines. `timeit` chose the number of loops itself (50000, 10000) so that each measurement takes long enough, then reported the **best of 5** repeats, per loop. The built-in `sum` is about 5 times faster than the hand-written loop.

### 8.5 `timeit` in code

```python
import timeit

setup = "data = list(range(10_000)); s = set(data)"
for stmt in ["9_999 in data", "9_999 in s"]:
    times = timeit.repeat(stmt, setup=setup, number=1_000, repeat=5)
    best = min(times) / 1_000
    print(f"{stmt:<14} best {best * 1e6:8.3f} µs per run")
    print("   five totals (ms):", [round(t * 1000, 3) for t in times])
```
```text
9_999 in data  best   46.390 µs per run
   five totals (ms): [55.199, 48.598, 47.465, 49.061, 46.39]
9_999 in s     best    0.032 µs per run
   five totals (ms): [0.035, 0.033, 0.032, 0.033, 0.033]
```

(Machine-specific timings.) `timeit.repeat(stmt, setup, number, repeat)` returns a **list** of `repeat` totals, each the time for `number` runs of `stmt`; divide `min(...)` by `number` to get the time **per run**. In the list totals, the first one (55.2 ms) is the slowest: a cold start, then the noise settles, and the minimum ignores it. And the result itself: a list is searched item by item, a set jumps straight to the answer, more than 1,000 times faster here.

`stmt` and `setup` can also be **functions** (with no arguments). To time a function that needs arguments, wrap it in a `lambda`, for example `timeit.repeat(lambda: fn(words), number=200, repeat=5)`. The lambda adds a tiny constant cost to each run, which does not matter when comparing two functions that both pay it. Section 8.6 and section 12 use this form.

### 8.6 Benchmarks that lie

A benchmark is an experiment, and experiments can be badly designed. Watch for these:

1. **Caching.** After the first run, a cached function costs almost nothing, so timing 100 runs measures the cache, not the function. In a real run, a sum of 100,000 squares behind `@lru_cache` took 5,509 µs on the first call and 0.09 µs per call afterwards (machine-specific). The same happens with files (the operating system keeps them in memory after the first read) and anything else that remembers results.
2. **Tiny inputs.** Searching a 10-item list took 91 ns in the same run; a 10,000-item list took 46,478 ns, 500 times more. A tiny input hides how the cost **grows**. Measure with realistic sizes, and with two or three sizes.
3. **Measuring the wrong thing.** Building test data inside the timed statement, or printing in it, can cost more than the code you care about. Put preparation in `setup`.
4. **Different answers.** Check that both versions really do the same work and **give the same answer**. A fast wrong function is not an optimisation.
5. **Different conditions.** Compare versions in the same process, one after the other, on the same data; not on different machines or days.

#### Try it 8.1

Predict what this prints.

```python
import timeit

counts = {"setup": 0, "stmt": 0}


def setup():
    counts["setup"] += 1


def stmt():
    counts["stmt"] += 1


times = timeit.repeat(stmt, setup=setup, number=4, repeat=3)
print(len(times), counts)
```

<details><summary>Answer</summary>

```text
3 {'setup': 3, 'stmt': 12}
```

`repeat=3` measurements, so 3 totals in the list. Setup runs **once per measurement** (3 times); the statement runs `number=4` times per measurement, so 3 × 4 = 12 times.

</details>

## 9. `cProfile` and `pstats`

### 9.1 From "how long" to "where"

`timeit` tells you a piece of code is slow. A **profiler** tells you **which functions** the time is spent in. Python's built-in profiler, **`cProfile`**, records every function call and return, and adds up the time per function. It is a *deterministic* profiler: it sees every call, so call counts are exact. The price is overhead: the program runs slower under the profiler (often 1.5 to 2 times), so treat the times as **relative**.

### 9.2 A program to profile

This program counts the most common words in a text, ignoring punctuation, case and "stop words":

```python
import random
import string

STOPWORDS = [f"stop{i}" for i in range(300)] + ["the", "a", "and", "of", "to", "in"]


def clean(word):
    table = str.maketrans("", "", string.punctuation)
    return word.translate(table).lower()


def is_stopword(word):
    return word in STOPWORDS


def count_words(text):
    counts = {}
    for raw in text.split():
        word = clean(raw)
        if word and not is_stopword(word):
            counts[word] = counts.get(word, 0) + 1
    return counts


def top_words(counts, n):
    return sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))[:n]


def make_text(n_words, seed=1):
    rng = random.Random(seed)
    vocab = ["python", "debug", "the", "a", "profile", "speed", "of", "code,", "Test.", "and"]
    return " ".join(rng.choice(vocab) for _ in range(n_words))


def main():
    text = make_text(200_000)
    print(top_words(count_words(text), 3))


if __name__ == "__main__":
    main()
```

### 9.3 Running `cProfile` from the command line

`python -m cProfile -s tottime script.py` runs the script under the profiler and prints a table sorted by `tottime`:

```text
$ python -m cProfile -s tottime wordstats.py
[('test', 20248), ('code', 20100), ('debug', 20049)]
         2640646 function calls (2640617 primitive calls) in 1.706 seconds

   Ordered by: internal time

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
   200000    0.571    0.000    0.571    0.000 wordstats.py:12(is_stopword)
   200000    0.227    0.000    0.227    0.000 {built-in method maketrans}
        1    0.166    0.166    1.247    1.247 wordstats.py:16(count_words)
   200000    0.154    0.000    0.474    0.000 wordstats.py:7(clean)
   200000    0.128    0.000    0.356    0.000 random.py:347(choice)
   200000    0.120    0.000    0.187    0.000 random.py:245(_randbelow_with_getrandbits)
   200001    0.063    0.000    0.419    0.000 wordstats.py:32(<genexpr>)
   200000    0.061    0.000    0.061    0.000 {method 'translate' of 'str' objects}
   ...
```

(Machine-specific times; the list was cut after a few rows.) The columns:

| Column | Meaning |
|---|---|
| `ncalls` | how many times the function was called. `120/5` means 120 calls, 5 of them not recursive ("primitive") |
| `tottime` | time spent **inside** the function itself, **excluding** the functions it called |
| `percall` (first) | `tottime / ncalls` |
| `cumtime` | **cumulative** time: inside the function **plus everything it called** |
| `percall` (second) | `cumtime / primitive calls` |
| `filename:lineno(function)` | which function; built-ins appear in `{braces}` |

The difference between `tottime` and `cumtime` is the key idea:

- **`cumtime` answers "which part of the program is slow?"** `count_words` has `cumtime` 1.247 s: almost all of the counting work happens under it. The top-level `main` would have the largest `cumtime` of all, which tells you nothing new.
- **`tottime` answers "which function's own code is slow?"** `count_words` has only 0.166 s of `tottime`: its own loop is cheap; it is slow because of what it *calls*. `is_stopword` has 0.571 s of `tottime`, the biggest of all, all in its single line `word in STOPWORDS`.

So you **read `cumtime` from the top down** to find the slow area, then **look at `tottime`** to find the hot spot inside it. And always look at **`ncalls`**: 200,000 calls of `maketrans` is suspicious, because it builds the *same* translation table every time.

Note that `make_text` (the `random.py` lines) also shows up: it is part of the run. The profiler measures whatever you run, setup included. That is why the next step profiles only the part we care about.

### 9.4 Profiling one function with `pstats`

In code, you can profile exactly the call you are interested in and then explore the results with **`pstats`**:

```python
import cProfile
import pstats

import wordstats

text = wordstats.make_text(200_000)

profiler = cProfile.Profile()
profiler.enable()
counts = wordstats.count_words(text)
profiler.disable()

stats = pstats.Stats(profiler)
stats.strip_dirs().sort_stats("cumulative").print_stats(6)
stats.print_callers("maketrans")
```
```text
         1119886 function calls in 1.225 seconds

   Ordered by: cumulative time
   List reduced from 9 to 6 due to restriction <6>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.163    0.163    1.225    1.225 wordstats.py:16(count_words)
   200000    0.563    0.000    0.563    0.000 wordstats.py:12(is_stopword)
   200000    0.150    0.000    0.464    0.000 wordstats.py:7(clean)
   200000    0.221    0.000    0.221    0.000 {built-in method maketrans}
   200000    0.061    0.000    0.061    0.000 {method 'translate' of 'str' objects}
   200000    0.032    0.000    0.032    0.000 {method 'lower' of 'str' objects}


   Ordered by: cumulative time
   List reduced from 9 to 1 due to restriction <'maketrans'>

Function                     was called by...
                                 ncalls  tottime  cumtime
{built-in method maketrans}  <-  200000    0.221    0.221  wordstats.py:7(clean)
```

(Machine-specific times.) The useful `pstats` methods:

- `strip_dirs()` shortens file names; `sort_stats(key)` sorts by `"cumulative"`, `"tottime"`, `"ncalls"`, `"name"`, ...
- `print_stats(n)` prints the first `n` rows; `print_stats("clean")` only rows matching the text.
- `print_callers("name")` shows **who calls** a function, and how often (here: all 200,000 `maketrans` calls come from `clean`); `print_callees("name")` shows **what it calls**.
- `profiler.runcall(fn, *args)` is a shortcut for enable, call, disable.
- `stats.dump_stats("out.prof")` (or `python -m cProfile -o out.prof script.py`) saves the data. The viewer `snakeviz` (a separate pip install) draws such a file in the browser as nested boxes, big boxes being slow functions.

`pstats.Stats` also stores the raw numbers in `stats.stats`, a dict that tools and tests can read; problem p018 uses it to count calls.

### 9.5 From profile to fix

The profile pointed at two things:

1. `is_stopword`: `word in STOPWORDS` searches a **list** of 306 strings. Use a **set**.
2. `clean`: rebuilds the same `maketrans` table 200,000 times. Build it **once**, outside the function.

Small functions also cost a call each; inlining the two helpers into the loop removes 400,000 calls. (Only do this in a hot loop that the profile points at; elsewhere, small named functions are better for reading.)

```python
import string

from wordstats import STOPWORDS, make_text

STOPWORD_SET = set(STOPWORDS)
TABLE = str.maketrans("", "", string.punctuation)


def count_words(text):
    counts = {}
    for raw in text.split():
        word = raw.translate(TABLE).lower()
        if word and word not in STOPWORD_SET:
            counts[word] = counts.get(word, 0) + 1
    return counts
```

And we **measure** before claiming victory. A short script timed both `count_words` versions with `perf_counter` on the same 200,000-word text and asserted that both return the same dict:

```text
wordstats       0.835 s
wordstats_fast  0.064 s
same result: yes
```

(Machine-specific.) About 13 times faster, same result, and the code is not harder to read.

#### Try it 9.1

A colleague's report program is slow. Here is its profile, sorted by `cumulative`:

```text
   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
        1    0.000    0.000    0.482    0.482 e91.py:20(main)
        1    0.006    0.006    0.482    0.482 e91.py:12(build_report)
     5000    0.007    0.000    0.475    0.000 e91.py:8(find_customer)
     5000    0.002    0.000    0.467    0.000 {built-in method builtins.next}
    10000    0.467    0.000    0.467    0.000 e91.py:9(<genexpr>)
```

(Machine-specific times.) Which function do you optimise, and what is your guess about line 9?

<details><summary>Answer</summary>

`find_customer`. Its own `tottime` is tiny, but under it, 0.467 s of 0.482 s is spent in a generator expression on line 9, driven by `next`: almost all the program's time. A `next(...)` over a generator expression, called once per order, is the classic linear search: `next(c for c in customers if c["id"] == cid)`, which walks the customer list for every order. The fix is to build a dict `{c["id"]: c for c in customers}` once and look up in it. `main` and `build_report` have big `cumtime` only because they are above it. (The real line 9 was exactly that `next(...)` line.)

</details>

## 10. Line-level profiling

### 10.1 When a function is long

`cProfile` works at function level. If the hot function is 40 lines long, which line is slow? One answer is to split the function into smaller ones and profile again. Another is a **line profiler**, which measures each line.

### 10.2 `line_profiler`

`line_profiler` is a third-party package (`pip install line_profiler`; this example used version 5.1.0). You decorate the function with `@profile`, then run the script with the `kernprof` command, which provides that `profile` name:

```python
import string

STOPWORDS = [f"stop{i}" for i in range(300)] + ["the", "a", "and", "of", "to", "in"]


@profile
def count_words(text):
    counts = {}
    for raw in text.split():
        table = str.maketrans("", "", string.punctuation)
        word = raw.translate(table).lower()
        if word and word not in STOPWORDS:
            counts[word] = counts.get(word, 0) + 1
    return counts


words = ["python", "debug", "the", "a", "profile", "speed", "of", "code,", "Test.", "and"]
count_words(" ".join(words * 10_000))
```

```text
$ kernprof -l -v lp_demo.py
Wrote profile results to 'lp_demo.py.lprof'
Timer unit: 1e-06 s

Total time: 0.604941 s
File: lp_demo.py
Function: count_words at line 6

Line #      Hits         Time  Per Hit   % Time  Line Contents
==============================================================
     6                                           @profile
     7                                           def count_words(text):
     8         1          1.1      1.1      0.0      counts = {}
     9    100001      41432.8      0.4      6.8      for raw in text.split():
    10    100000     162006.9      1.6     26.8          table = str.maketrans("", "", string.punctuation)
    11    100000      57853.8      0.6      9.6          word = raw.translate(table).lower()
    12    100000     314016.7      3.1     51.9          if word and word not in STOPWORDS:
    13     60000      29626.8      0.5      4.9              counts[word] = counts.get(word, 0) + 1
    14         1          3.1      3.1      0.0      return counts
```

(Machine-specific times.) `-l` means line-by-line, `-v` means "show the results now". The columns: **Hits** (how many times the line ran), **Time** (total, in the timer unit, here microseconds), **Per Hit**, and **% Time**. The same two hot spots as before, now pointed at by line: line 12 (the list search) takes 52%, line 10 (rebuilding the table) 27%. Notice `Hits`: the `for` line runs once more than the body (100,001), because the last check finds the loop finished. Line 13 runs 60,000 times: only 6 of the 10 words are not stop words.

Remember to remove `@profile` afterwards: without `kernprof`, the name `profile` is not defined and the script crashes.

### 10.3 Building a line counter with `sys.settrace`

How can a tool know which line runs? Python has a hook for exactly this: **`sys.settrace(func)`** installs a **trace function** that the interpreter calls on events:

- `"call"`: a new frame (function call) starts. The return value of the trace function decides whether this frame is traced line by line: return a function to trace it, `None` to skip it.
- `"line"`: a new line is about to run in a traced frame.
- `"return"` and `"exception"`: the frame is returning or an exception happened.

The trace function receives `(frame, event, arg)`. `frame.f_code.co_name` is the function name, `frame.f_lineno` the current line number. Debuggers (including `pdb`) and coverage tools are built on this hook.

```python
import sys
from collections import Counter

hits = Counter()


def tracer(frame, event, arg):
    if frame.f_code.co_name != "collatz_steps":
        return None                 # do not trace other functions
    if event == "line":
        hits[frame.f_lineno] += 1
    return tracer                   # keep tracing lines in this frame


def collatz_steps(n):
    steps = 0
    while n != 1:
        if n % 2 == 0:
            n //= 2
        else:
            n = 3 * n + 1
        steps += 1
    return steps


sys.settrace(tracer)
try:
    result = collatz_steps(6)
finally:
    sys.settrace(None)

print("result:", result)
for line in sorted(hits):
    print(f"line {line}: {hits[line]}")
```
```text
result: 8
line 16: 1
line 17: 9
line 18: 8
line 19: 6
line 21: 2
line 22: 8
line 23: 1
```

Check it by hand: 6 → 3 → 10 → 5 → 16 → 8 → 4 → 2 → 1 is 8 steps. The `while` test (line 17) runs 9 times: 8 times true, once false. The even branch (line 19) runs for 6, 10, 16, 8, 4, 2: six times. The odd branch (line 21) for 3 and 5: twice. These are exactly the "Hits" a line profiler shows.

Three rules for trace functions:

1. **Always remove it** in a `finally`, otherwise everything after it runs slowly under tracing. Better still, save the old one with `sys.gettrace()` and put **that** back, because a debugger or coverage tool may have installed its own.
2. **Tracing is slow**: every line calls a Python function. Use it for counting and teaching, not for timing (the measured times would be mostly tracer overhead).
3. **Line numbers are absolute** (lines of the file). To report "line 3 of this function", subtract `frame.f_code.co_firstlineno`. Problem p020 builds exactly that.

#### Try it 10.1

Using the same tracer, predict `result` and the hits per line for `collatz_steps(3)`.

<details><summary>Answer</summary>

```text
result: 7 {16: 1, 17: 8, 18: 7, 19: 5, 21: 2, 22: 7, 23: 1}
```

(The program was changed to print the dict on one line.) 3 → 10 → 5 → 16 → 8 → 4 → 2 → 1: 7 steps. Line 17 runs 8 times (7 true, 1 false); lines 18 and 22 run once per step (7). Even values 10, 16, 8, 4, 2 give line 19 five hits; odd values 3, 5 give line 21 two hits.

</details>

## 11. Memory: `tracemalloc`

### 11.1 Why memory matters

Memory problems show up in two ways. A program that **needs too much at once** (a high *peak*) crashes with `MemoryError` or makes the whole computer swap and crawl. A program that **keeps growing** (a *leak*) runs fine for an hour and dies after a day. Both are invisible in a quick test with small data, which is why they need tools.

### 11.2 `sys.getsizeof` and its limits

`sys.getsizeof(obj)` returns the size of **one object** in bytes:

```python
import sys

print(sys.getsizeof(0), sys.getsizeof(10**100))
print(sys.getsizeof("a"), sys.getsizeof("a" * 1000))
big = ["x" * 10_000, "y" * 10_000, "z" * 10_000]
print(sys.getsizeof(big))
print(sum(sys.getsizeof(s) for s in big))
```
```text
28 72
42 1041
80
30123
```

(Sizes are for 64-bit CPython 3.14 and differ slightly between versions.) Even a small integer is 28 bytes: every Python object carries a header (type, reference count). The surprise is the list: **80 bytes**, while the three strings inside it take 30,123 bytes. A list stores only **references** (pointers) to its items, and `getsizeof` does not follow them. So `getsizeof` is useful for comparing containers' own overhead, but it does not tell you how much memory a data structure really uses. For that you need to watch the allocations.

### 11.3 `tracemalloc`: current and peak

**`tracemalloc`** (in the standard library) records every memory block Python allocates while it is running, with the line of code that allocated it. The simplest use: start it, run some code, read the **current** and **peak** traced memory:

```python
import tracemalloc


def total_with_list(n):
    squares = [i * i for i in range(n)]
    return sum(squares)


def total_with_generator(n):
    return sum(i * i for i in range(n))


for fn in (total_with_list, total_with_generator):
    tracemalloc.start()
    result = fn(1_000_000)
    current, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    print(f"{fn.__name__:<22} result={result} current={current:>9,} B peak={peak:>11,} B")
```
```text
total_with_list        result=333332833333500000 current=    3,232 B peak= 40,448,224 B
total_with_generator   result=333332833333500000 current=       32 B peak=        408 B
```

(Machine-specific numbers.) Same answer, wildly different peaks: the list version held a million integers at once (about 40 MB); the generator produced one value at a time (a few hundred bytes). After both functions returned, `current` is small, because the list was freed. **Peak** is what decides whether a program fits in memory. Problem p021 turns this into a reusable `peak_bytes` function.

Call `tracemalloc.start()` **before** the allocations you want to see (it knows nothing about earlier ones). Tracing slows the program and uses memory itself, so use it while investigating. `tracemalloc.stop()` clears the data; `tracemalloc.reset_peak()` starts a new peak measurement without stopping.

### 11.4 Finding a leak with snapshots

In Python, an object is freed when nothing refers to it any more. So a "leak" in Python almost always means **something still refers to objects you no longer need**: a module-level list that only grows, a cache with no size limit, a list of callbacks (listeners) that are added and never removed. These live as long as the program.

A **snapshot** is a picture of all traced allocations at one moment. Comparing two snapshots shows which lines allocated memory **between** them:

```python
import tracemalloc

_history = []                       # module-level: lives as long as the program


def handle_request(user_id):
    page = f"<html>profile of user {user_id}</html>" * 50
    _history.append(page)            # "for debugging later" - never removed
    return len(page)


tracemalloc.start()
before = tracemalloc.take_snapshot()
for user_id in range(20_000):
    handle_request(user_id)
after = tracemalloc.take_snapshot()

for stat in after.compare_to(before, "lineno")[:3]:
    print(stat)
tracemalloc.stop()
```
```text
/home/you/debug/leak.py:7: size=32.7 MiB (+32.7 MiB), count=20000 (+20000), average=1713 B
/home/you/debug/leak.py:8: size=169 KiB (+169 KiB), count=1 (+1), average=169 KiB
/usr/lib/python3.14/tracemalloc.py:560: size=328 B (+328 B), count=1 (+1), average=328 B
```

(Machine-specific sizes and paths.) Read the first line: line 7 (building `page`) is responsible for 32.7 MiB of memory that is **still alive**, in 20,000 blocks: one page per request, never freed. Each request should have freed its page when it returned, so something keeps them: line 8 (169 KiB, the list's own array of references) points to the culprit, `_history`. `compare_to(old, "lineno")` groups by line and sorts by the biggest growth.

The fix is to **bound** what is kept. A `deque` with `maxlen` keeps only the last N items:

```python
from collections import deque

_history = deque(maxlen=100)        # keeps only the last 100 pages
```
```text
/home/you/debug/leak_fixed.py:8: size=170 KiB (+170 KiB), count=100 (+100), average=1741 B
/home/you/debug/leak_fixed.py:9: size=1056 B (+1056 B), count=2 (+2), average=528 B
peak: 178,996 bytes
```

Only 100 pages remain alive. The same idea applies to caches: `functools.lru_cache(maxsize=1000)` instead of `maxsize=None` when the inputs are unbounded, and an `unsubscribe` method next to every `subscribe`. Problem p022 asks you to fix a leak of that kind.

### 11.5 A leak-hunting routine

1. **Reproduce** the growth: call the suspect operation many times in a loop.
2. Take a snapshot **after a warm-up** (the first calls fill caches legitimately), then another after many more calls.
3. `compare_to` shows the line that allocates the growing objects.
4. Ask: **who keeps a reference** to those objects? Look for module-level lists, dicts and sets, class attributes, caches, and registered callbacks.
5. Fix by bounding, removing, or not storing; then repeat the measurement to prove the growth stopped.

#### Try it 11.1

Predict the three booleans.

```python
import tracemalloc

tracemalloc.start()
words = [str(i) * 1000 for i in range(1000)]     # 1,000 different long strings
current1, peak1 = tracemalloc.get_traced_memory()
del words
current2, peak2 = tracemalloc.get_traced_memory()
tracemalloc.stop()
print(current1 > 1_000_000, current2 < 10_000, peak2 >= current1)
```

<details><summary>Answer</summary>

```text
True True True
```

1,000 strings of at least 1,000 characters each are more than 1 MB, so `current1 > 1_000_000`. `del words` removes the only reference to the list, so the list and its strings are freed and `current2` falls to almost nothing. The peak never goes down, so `peak2 >= current1`.

A trap: with `"x" * 1000` instead of `str(i) * 1000`, the first answer is `False`. Python computes the constant `"x" * 1000` once when compiling, and all 1,000 list items refer to that **same** string object. Memory tools measure objects, not how many times you mention them.

</details>

## 12. Making it faster

### 12.1 The order of attack

Once a profile shows you **where** the time goes, there are many ways to make that part faster. Try them in this order, because the first ones give the biggest wins for the least risk:

1. **A better algorithm.** Turning O(n²) work into O(n) changes 10 seconds into 10 milliseconds, and the gain grows with the data.
2. **The right data structure.** Sets and dicts for lookups, `deque` for queues.
3. **Avoid repeated work.** Compute once, outside the loop; cache results that are needed again.
4. **Use built-ins.** `sum`, `sorted`, `str.join`, `collections.Counter` run in C.
5. Only then, **micro-optimisations** (fewer function calls, local variables). They give a few percent and make code uglier, so only in a measured hot loop.

And always: **measure before, measure after, check the result is the same**.

### 12.2 Algorithm first

Does any pair of numbers in a list add up to a target? The obvious way checks every pair:

```python
import random
import time


def has_pair_slow(nums, target):
    for i in range(len(nums)):
        for j in range(i + 1, len(nums)):
            if nums[i] + nums[j] == target:
                return True
    return False


def has_pair_fast(nums, target):
    seen = set()
    for x in nums:
        if target - x in seen:
            return True
        seen.add(x)
    return False


rng = random.Random(7)
for n in (1_000, 2_000, 4_000):
    nums = [rng.randrange(0, 10**9) * 2 for _ in range(n)]   # all even
    target = 1                                              # odd: never found
    for fn in (has_pair_slow, has_pair_fast):
        start = time.perf_counter()
        found = fn(nums, target)
        ms = (time.perf_counter() - start) * 1000
        print(f"n={n:<5} {fn.__name__:<14} {found!s:<5} {ms:9.2f} ms")
```
```text
n=1000  has_pair_slow  False     38.58 ms
n=1000  has_pair_fast  False      0.20 ms
n=2000  has_pair_slow  False    156.04 ms
n=2000  has_pair_fast  False      0.37 ms
n=4000  has_pair_slow  False    625.45 ms
n=4000  has_pair_fast  False      0.54 ms
```

(Machine-specific.) The test data is the **worst case** (no pair exists, so both functions must look at everything). Watch the growth: every time `n` doubles, the slow version takes about **4 times** longer (O(n²): about n²/2 pairs), while the fast one roughly doubles (O(n)). At 4,000 items the gap is over 1,000 times; at 100,000 items the slow version would take minutes. No amount of micro-tuning the slow loop could ever catch up. The trick of the fast version: for each `x`, the partner we need is `target - x`, and a set answers "have I seen it?" in constant time.

### 12.3 The right data structure

`list.pop(0)` removes the first item, and then **shifts every other item** one place left. In a loop that empties a list from the front, that is O(n²). `collections.deque` is built for both ends: `q.popleft()` is O(1). In a real run, emptying 50,000 items from the front took 281 ms with a list and 2.3 ms with a deque (machine-specific timings, measured with `timeit` as in section 8).

A cheat sheet of costs you already met in earlier chapters:

| Operation | list | set / dict | deque |
|---|---|---|---|
| `x in c` | O(n) | O(1) average | O(n) |
| add at end | O(1) | O(1) | O(1) |
| remove from front | O(n) | n/a | O(1) |
| index `c[i]` | O(1) | `d[key]` O(1) | O(n) in the middle |

### 12.4 Avoid repeated work

The most common slow pattern in real code is **computing the same thing again and again inside a loop**:

```python
import timeit

prices = list(range(1, 2001))


def above_average_slow(prices):
    return [p for p in prices if p > sum(prices) / len(prices)]


def above_average_fast(prices):
    average = sum(prices) / len(prices)       # computed once
    return [p for p in prices if p > average]


assert above_average_slow(prices) == above_average_fast(prices)
for fn in (above_average_slow, above_average_fast):
    t = min(timeit.repeat(lambda: fn(prices), number=5, repeat=3)) / 5
    print(f"{fn.__name__:<19} {t * 1000:8.3f} ms")
```
```text
above_average_slow    16.072 ms
above_average_fast     0.074 ms
```

(Machine-specific.) The slow version hides an O(n²): `sum(prices)` walks the whole list for **every** item. Look for these in loops: `sum`, `len` of a generator, `sorted`, `max`, `str.maketrans`, `re.compile`, opening a file, parsing the same date string. If the value does not change between iterations, compute it once before the loop. (`sorted` inside a loop is a favourite; problem p024 is about it.)

### 12.5 Caching

When a function is called again and again **with the same arguments**, and always returns the same result for them (no side effects, no dependency on time or files), you can **cache** it: remember each answer and return it the next time. `functools.lru_cache` (chapter 11's decorators) does this for you:

```python
from functools import lru_cache

calls = 0


def fib(n):
    global calls
    calls += 1
    return n if n < 2 else fib(n - 1) + fib(n - 2)


@lru_cache(maxsize=None)
def fib_cached(n):
    return n if n < 2 else fib_cached(n - 1) + fib_cached(n - 2)


print(fib(25), "calls:", calls)
print(fib_cached(25), fib_cached.cache_info())
```
```text
75025 calls: 242785
75025 CacheInfo(hits=23, misses=26, maxsize=None, currsize=26)
```

The plain version made 242,785 calls, because it recomputes the same small values millions of times in its call tree. The cached one computed each `n` from 0 to 25 once (26 misses) and answered the rest from memory (23 hits). `cache_info()` is a free measurement: a cache with few hits is not helping.

Cautions:

- Arguments must be **hashable** (no lists or dicts).
- `maxsize=None` means **unbounded**: with endless different arguments, that is a memory leak (section 11). Choose a `maxsize` when inputs are not limited.
- Never cache a function whose result can change (it reads a file, the clock, the database), or the cache returns stale answers.

#### Try it 12.1

Predict the two `CacheInfo` lines.

```python
from functools import lru_cache


@lru_cache(maxsize=None)
def fib(n):
    return n if n < 2 else fib(n - 1) + fib(n - 2)


fib(10)
print(fib.cache_info())
fib(10)
fib(12)
print(fib.cache_info())
```

<details><summary>Answer</summary>

```text
CacheInfo(hits=8, misses=11, maxsize=None, currsize=11)
CacheInfo(hits=12, misses=13, maxsize=None, currsize=13)
```

`fib(10)` computes each value from 10 down to 0 exactly once: 11 misses. Inside `fib(n)`, the first call `fib(n - 1)` is new (a miss) and the second call `fib(n - 2)` was just computed by it (a hit), for every `n` from 3 to 10: 8 hits. (In `fib(2)`, the call `fib(0)` is still new, so it is a miss, not a hit.)

The second `fib(10)` is 1 more hit (9). `fib(12)` is new (miss), calls `fib(11)` (new, miss: 13 misses in total); `fib(11)` calls `fib(10)` (hit) and `fib(9)` (hit); back in `fib(12)`, `fib(10)` is a hit. That is 3 more hits: 12.

</details>

#### Try it 12.2

Without timing anything, put these in order from fastest to slowest for a list `names` of 100,000 strings, and say the complexity of each.

```python
# A
result = [n for n in names if n in banned_list]     # banned_list: 1,000 strings
# B
banned = set(banned_list)
result = [n for n in names if n in banned]
# C
result = [n for n in names if n in set(banned_list)]
```

<details><summary>Answer</summary>

B is fastest: building the set once costs 1,000 steps, then each of 100,000 lookups is O(1). A searches a 1,000-item list for every name: about 100,000 × 1,000 = 100 million comparisons in the worst case. C is the slowest trap: it **rebuilds** the set (1,000 steps) for every name, the same 100 million steps as A **plus** allocating 100,000 sets. "I used a set" does not help if you build it inside the loop.

</details>

## 13. Code quality tools: ruff, black, mypy, pre-commit

### 13.1 Why let tools check your code?

Many mistakes have a **shape** that a program can recognise without running your code: an import never used, a bare `except:` that swallows every error, a mutable default argument, `== None`, a function that promises `str` but returns an `int`. Finding these by hand in code review is boring and unreliable; a tool finds all of them in a second, every time.

There are three kinds of tools:

| Kind | Tool | It checks | It does **not** check |
|---|---|---|---|
| **Linter** | `ruff` (older: `flake8`, `pylint`) | suspicious patterns, likely bugs, style rules, unused names | whether the program does the right thing |
| **Formatter** | `black`, `ruff format` | layout: spaces, line breaks, quotes | anything about meaning; it never changes behaviour |
| **Type checker** | `mypy` (others: `pyright`) | that values match their type hints (`str` where `str` is expected, `None` handled) | values, logic, performance |

None of them replaces tests. Tests check **behaviour**; these tools check **shape**. Together they catch most mistakes before they reach a user. Problem p029 asks you to argue what each one catches and misses.

### 13.2 Ruff, a fast linter

`ruff` is a linter written in Rust that implements hundreds of rules from older tools. Each rule has a **code**: a letter prefix for the rule family and a number. Some families:

| Prefix | Family | Example |
|---|---|---|
| `F` | Pyflakes: real errors | `F401` unused import, `F821` undefined name |
| `E`, `W` | pycodestyle: style errors and warnings | `E711` `== None`, `E722` bare `except`, `E701` two statements on one line |
| `I` | isort: import order | `I001` unsorted imports |
| `B` | bugbear: likely bugs | `B006` mutable default argument |
| `UP` | pyupgrade: old syntax | `UP006` `List[int]` instead of `list[int]` |

Here is a file with many problems (all shown in earlier chapters):

```python
import os, sys
import json

def add_item(cart, item, qty = 1, history=[]):
    history.append(item)
    if qty == None:
        qty = 1
    try:
        cart[item] = cart.get(item,0)+qty
    except:
        print("could not add")
    total=0
    for k in cart: total += cart[k]
    return total
```

Ruff is configured in `pyproject.toml`. This selects the rule families above:

```toml
[tool.ruff]
line-length = 88
target-version = "py311"
output-format = "concise"

[tool.ruff.lint]
select = ["E", "F", "W", "I", "B", "UP"]
```

```text
$ ruff check shop.py
shop.py:1:1: E401 [*] Multiple imports on one line
shop.py:1:1: I001 [*] Import block is un-sorted or un-formatted
shop.py:1:8: F401 [*] `os` imported but unused
shop.py:1:12: F401 [*] `sys` imported but unused
shop.py:2:8: F401 [*] `json` imported but unused
shop.py:4:43: B006 Do not use mutable data structures for argument defaults
shop.py:6:15: E711 Comparison to `None` should be `cond is None`
shop.py:10:5: E722 Do not use bare `except`
shop.py:13:18: E701 Multiple statements on one line (colon)
Found 9 errors.
[*] 5 fixable with `--fix` (2 unsafe fixes available with `--fix --unsafe-fixes`).
```

Each line is `file:line:column: CODE message`. `[*]` means ruff can fix it automatically with `ruff check --fix`. "Unsafe" fixes might change behaviour (for example `B006`: replacing `history=[]` with `None` changes what callers see), so ruff only applies them when you ask with `--unsafe-fixes`, and you should read the diff.

Without `output-format = "concise"`, ruff prints each problem with the source lines and a suggested fix underneath. Without a `select` list, it uses its default rule set, which is smaller and depends on the ruff version; always write the list down in the config so everyone on the team gets the same checks.

When a rule is wrong for one line, silence it on that line only, with the code and a reason: `# noqa: F403  (re-export on purpose)`. A bare `# noqa` silences everything on the line; avoid it.

### 13.3 Formatters: black and `ruff format`

A formatter rewrites your file's **layout** to one fixed style. Why accept a tool's taste over your own? Because then nobody argues about spaces in code review, every file in the project looks the same, and diffs show only real changes. `black` popularised this ("any colour you like, as long as it is black"); `ruff format` produces almost identical output.

`--diff` shows what would change without changing the file:

```text
$ ruff format --diff shop.py
--- shop.py
+++ shop.py
@@ -1,14 +1,16 @@
 import os, sys
 import json
 
-def add_item(cart, item, qty = 1, history=[]):
+
+def add_item(cart, item, qty=1, history=[]):
     history.append(item)
     if qty == None:
         qty = 1
     try:
-        cart[item] = cart.get(item,0)+qty
+        cart[item] = cart.get(item, 0) + qty
     except:
         print("could not add")
-    total=0
-    for k in cart: total += cart[k]
+    total = 0
+    for k in cart:
+        total += cart[k]
     return total

1 file would be reformatted
```

`black --diff shop.py` showed the same changes (plus time stamps in the header and a cheerful "All done!" message). Notice what the formatter did **not** touch: the unused imports, `== None`, the bare `except`, the mutable default. Layout only. That is the linter's job. Running without `--diff` (`ruff format shop.py`, `black shop.py`) rewrites the file; `--check` only reports, which is what you use in automated checks.

### 13.4 mypy, a type checker

Type hints (chapters 9 and 16) are ignored when Python runs. **mypy** reads them and checks that the code agrees with them, without running it:

```python
def find_price(prices: dict[str, float], name: str) -> float | None:
    return prices.get(name)


def total(prices: dict[str, float], names: list[str]) -> float:
    result = 0
    for name in names:
        result += find_price(prices, name)
    return result


def label(count: int) -> str:
    return "items: " + count


print(total({"pen": 10.0}, ["pen", "ink"]))
```

```text
$ mypy stock.py
stock.py:8: error: Unsupported operand types for + ("int" and "None")  [operator]
stock.py:8: note: Right operand is of type "float | None"
stock.py:8: error: Incompatible types in assignment (expression has type "float | int", variable has type "int")  [assignment]
stock.py:13: error: Unsupported operand types for + ("str" and "int")  [operator]
Found 3 errors in 1 file (checked 1 source file)
```

Three real bugs, found without running anything:

1. `find_price` can return `None` (the price of `"ink"` is unknown), and line 8 adds it to a number. At run time this crashes, but only when a name is missing: a test with only known names would pass.
2. `result = 0` makes mypy decide `result` is an `int`; adding floats to it changes its type. Write `result = 0.0`.
3. `"items: " + count` adds a `str` and an `int`.

The fixed version handles `None` explicitly:

```python
def total(prices: dict[str, float], names: list[str]) -> float:
    result = 0.0
    for name in names:
        price = find_price(prices, name)
        if price is not None:
            result += price
    return result
```

With `label` fixed as `return "items: " + str(count)`:

```text
$ mypy --strict stock_fixed.py
Success: no issues found in 1 source file
```

After `if price is not None:`, mypy knows `price` is a `float` inside the `if`. This is called **narrowing**, and it is how you satisfy "X or None" types.

**Strict mode.** By default mypy **does not check functions without type hints at all**:

```python
def double(x):
    return x * 2


print(double("ab") + 1)
```
```text
$ mypy untyped.py
Success: no issues found in 1 source file
$ mypy --strict untyped.py
untyped.py:1: error: Function is missing a type annotation  [no-untyped-def]
untyped.py:5: error: Call to untyped function "double" in typed context  [no-untyped-call]
Found 2 errors in 1 file (checked 1 source file)
```

"Success" here means "nothing was checked", not "no bugs"; the program crashes when run. `--strict` turns on many extra checks, including "every function must have hints". It is the right setting for new code. In `pyproject.toml`:

```toml
[tool.mypy]
python_version = "3.11"
strict = true
```

### 13.5 pre-commit: run the checks automatically

Tools only help if they are run. **pre-commit** is a tool that installs a **git hook**: a script that git runs before every `git commit`. If any check fails, the commit is stopped and you see why. Its configuration is a YAML file at the root of the repository, `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.17.3
    hooks:
      - id: ruff-check
        args: [--fix]
      - id: ruff-format
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v6.0.0
    hooks:
      - id: end-of-file-fixer
      - id: trailing-whitespace
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v2.4.1
    hooks:
      - id: mypy
```

Each `repo` is a git repository that provides hooks, and `rev` pins its **exact version**, so every developer and every CI machine runs the same checks (`pre-commit autoupdate` moves the pins when you decide to). Each `id` is one hook: `ruff-check` is the linter (older configurations call it `ruff`), `ruff-format` the formatter, the two whitespace fixers do what their names say, and `mypy` runs the type checker. `args` passes extra options; the tools still read their settings from `pyproject.toml`. Set-up, once per clone: `pip install pre-commit`, then `pre-commit install`, which answers `pre-commit installed at .git/hooks/pre-commit`.

The first run downloads each hook into its own environment (it prints `[INFO] Initializing environment ...` lines and needs internet that one time); later runs reuse them. Here is a real run over the original messy `shop.py` (with the mypy hook not yet added):

```text
$ pre-commit run --all-files
ruff check...............................................................Failed
- hook id: ruff-check
- exit code: 1
- files were modified by this hook

shop.py:2:43: B006 Do not use mutable data structures for argument defaults
shop.py:4:15: E711 Comparison to `None` should be `cond is None`
shop.py:8:5: E722 Do not use bare `except`
shop.py:11:18: E701 Multiple statements on one line (colon)
Found 8 errors (4 fixed, 4 remaining).
2 unsafe fixes available with `--fix --unsafe-fixes`.

ruff format..............................................................Failed
- hook id: ruff-format
- files were modified by this hook

1 file reformatted

fix end of files.........................................................Passed
trim trailing whitespace.................................................Passed
```

The hooks **fixed** what they safely could (unused imports removed, imports sorted, layout formatted), reported what needs a human, and failed the run. After you fix the rest by hand and `git add` the files again, the commit goes through. A hook that modifies files always "fails", so that you look at the changes before committing them.

With the mypy hook added, a file containing `return "items: " + len(cart)` made the run end with `mypy....Failed` and the same `Unsupported operand types for + ("str" and "int")` error that mypy reports on its own.

(One caution: the mypy hook runs in its own isolated environment, so it does not see the packages installed in your project; you list the ones it needs under `additional_dependencies`.)

**Order and cost.** Put fast, auto-fixing hooks first (formatting, whitespace), then the linter, then the slower type checker. Keep the slow things (the full test suite) out of the commit hook, or people start skipping hooks with `git commit --no-verify`; run tests in CI instead. A useful pipeline: format → lint → type check on every commit; tests on every push.

#### Try it 13.1

Which tool would catch each problem: linter (ruff), formatter, type checker (mypy), tests, or none of them?

1. `def f(items=[])`.
2. A function returns the wrong discount for orders over ₹1000.
3. `return "total: " + count` where `count: int`.
4. `x=1;y=2` on one line.
5. `import json` that is never used.
6. A function that is correct but O(n²) and takes a minute on real data.

<details><summary>Answer</summary>

1. Linter: `B006`.
2. Tests. The code is the right shape; only its behaviour is wrong.
3. Type checker: unsupported operand types `str` + `int`. (A test that calls it would crash too.)
4. Formatter (it splits the line) and linter (`E702`).
5. Linter: `F401`.
6. None of the static tools. A profiler finds it, or a test with realistic data and a time budget.

</details>

#### Try it 13.2

With the configuration from 13.2, predict the rule codes ruff reports for this file:

```python
import math


def area(r, unit="cm", seen={}):
    if r == None:
        return 0
    return 3.14 * r * r
```

<details><summary>Answer</summary>

```text
e132.py:1:8: F401 [*] `math` imported but unused
e132.py:4:29: B006 Do not use mutable data structures for argument defaults
e132.py:5:13: E711 Comparison to `None` should be `cond is None`
Found 3 errors.
[*] 1 fixable with `--fix` (2 unsafe fixes available with `--fix --unsafe-fixes`).
```

`unit` is unused, but unused **arguments** are not in the selected families (the `ARG` family would report it). And ruff cannot know that `3.14` should be `math.pi`: that is a judgement for humans.

</details>

## 14. Reading other people's code

### 14.1 Why this is a skill

Most of a programmer's working time is spent **reading** code, not writing it: fixing a bug in a library, joining a project, reviewing a teammate's change. Reading code is harder than writing it, because you do not know the author's intent. Like debugging, it goes faster with a method.

### 14.2 A method

1. **Top-down first.** Read the README, the folder layout, and the entry point (`main`, the command-line handler) before any detail. Ask "what does this program do, for whom?" Draw a box for each module and arrows for "calls" or "imports".
2. **Follow the data.** Pick one real input and follow it: where is it read, what shape does it have after each step, where does it end up? Data flow explains more than control flow.
3. **Run it.** Run the program, or the function, on a small input. Put a `breakpoint()` in the middle and look at real values; read the call stack with `w` to learn who calls what.
4. **Read the tests.** Tests are documentation that cannot go out of date: each one shows an input and the expected output. A test file is often the fastest explanation of what a function is *supposed* to do.
5. **Rename and extract as you understand.** When you work out what `g` or `tmp2` means, rename it (your editor's *Rename Symbol* changes every use safely). When you understand a block, extract it into a function with a good name. Do this with tests running, in small steps: each rename should leave the tests green.
6. **Write down questions.** "Why is this sorted twice?" Either you find the answer later (and write a comment), or you found a bug.

### 14.3 A worked example

You find this in a project, with no comment:

```python
def g(s):
    r, i = "", 0
    while i < len(s):
        j = i
        while j < len(s) and s[j] == s[i]: j += 1
        r += s[i] + (str(j - i) if j - i > 1 else "")
        i = j
    return r
```

**Run it** on small inputs before reading closely; the outputs are below, next to the rewrite. **Read it**: `i` marks the start of a group; the inner loop moves `j` forward while the character equals `s[i]`, so `s[i:j]` is a **run** of the same character, of length `j - i`. The run is written as the character plus its length, but a length of 1 is left out. Then the next run starts at `j`. So this is **run-length encoding**: `"aaab"` becomes `"a3b"`.

Now rewrite it with names that say what it does, a docstring, and the same behaviour, and **check** the two agree:

```python
def compress_runs(text):
    """Write each run of a repeated character as the character plus its count.

    A run of length 1 is written without a count: "aaab" -> "a3b".
    """
    parts = []
    start = 0
    while start < len(text):
        end = start
        while end < len(text) and text[end] == text[start]:
            end += 1
        run_length = end - start
        parts.append(text[start] + (str(run_length) if run_length > 1 else ""))
        start = end
    return "".join(parts)


for sample in ["aaab", "abc", "", "zzzzzzzzzzzz", "a11"]:
    print(repr(sample), "->", repr(g(sample)), g(sample) == compress_runs(sample))
```
```text
'aaab' -> 'a3b' True
'abc' -> 'abc' True
'' -> '' True
'zzzzzzzzzzzz' -> 'z12' True
'a11' -> 'a12' True
```

The rewrite also replaced `r += ...` with a list and `"".join` (repeated string `+=` can be slow on long inputs). And the edge-case inputs found a real problem: the input `"a11"` encodes to `"a12"`, which looks exactly like "a, twelve times". **Text containing digits cannot be decoded unambiguously.** That is a question for the author: are digits impossible in this program's input, or is this a bug? Write the question down; that is what careful reading produces.

#### Try it 14.1

What does this function do? Give it a good name and find the input where it misbehaves.

```python
def h(xs):
    return [xs[i] for i in range(len(xs)) if xs[i] not in xs[:i]]
```

<details><summary>Answer</summary>

It keeps the first occurrence of each item, in order: it removes duplicates while keeping order. A good name is `unique_in_order` or `dedupe_keep_order`. It gives correct answers for every list, so the problem is speed: `xs[:i]` copies the first `i` items and searches them, for every `i`, so it is O(n²). On 100,000 items it takes a very long time. A faster version keeps a `seen` set. (It also works with unhashable items such as lists, which the set version does not; that is worth a comment if it matters.)

</details>

## 15. Project walkthrough: profile and speed up a slow program

### 15.1 The program

A small social app suggests new friends: for each user, the people they are **not** yet friends with who share the **most** mutual friends with them (ties broken by name, at most 3). The input is one friendship per line, `"u0001,u0042"`. Here is the first version, which works, and is slow:

```python
"""Suggest new friends: people who share the most friends with you."""
import random


def load_friendships(lines):
    users = []
    friends = {}
    for line in lines:
        a, b = line.strip().split(",")
        if a not in users:
            users.append(a)
        if b not in users:
            users.append(b)
        friends.setdefault(a, []).append(b)
        friends.setdefault(b, []).append(a)
    return users, friends


def mutual_count(friends, a, b):
    return len([f for f in friends[a] if f in friends[b]])


def suggest(users, friends, user, k=3):
    scores = []
    for other in users:
        if other == user or other in friends[user]:
            continue
        m = mutual_count(friends, user, other)
        if m > 0:
            scores.append((m, other))
    scores.sort(key=lambda pair: (-pair[0], pair[1]))
    return [other for _, other in scores[:k]]


def report(lines):
    users, friends = load_friendships(lines)
    out = ""
    for user in sorted(users):
        out += f"{user}: {', '.join(suggest(users, friends, user))}\n"
    return out


def make_lines(n_users, n_pairs, seed=42):
    rng = random.Random(seed)
    pairs = set()
    while len(pairs) < n_pairs:
        a, b = rng.sample(range(n_users), 2)
        pairs.add((min(a, b), max(a, b)))
    return [f"u{a:04d},u{b:04d}" for a, b in sorted(pairs)]
```

`make_lines` builds a **reproducible** test network (a fixed seed): 1,000 users and 4,000 friendships, so each user has about 8 friends. The goal: make `report` much faster **without changing a single character of its output**.

### 15.2 Step 0: a baseline and a safety net

Before changing anything, record two things: **how long it takes now**, and **what it outputs now**. The saved output is our safety net: every new version must produce exactly the same text. Then profile:

```python
import cProfile
import pstats
import time

import suggest_slow

lines = suggest_slow.make_lines(1_000, 4_000)

start = time.perf_counter()
expected = suggest_slow.report(lines)
print(f"plain run: {time.perf_counter() - start:.2f} s")

profiler = cProfile.Profile()
profiler.runcall(suggest_slow.report, lines)
pstats.Stats(profiler).strip_dirs().sort_stats("tottime").print_stats(6)
```
```text
plain run: 1.82 s
         2132468 function calls in 2.406 seconds

   Ordered by: internal time
   List reduced from 14 to 6 due to restriction <6>

   ncalls  tottime  percall  cumtime  percall filename:lineno(function)
   991000    1.733    0.000    1.837    0.000 suggest_slow.py:19(mutual_count)
     1000    0.458    0.000    2.339    0.002 suggest_slow.py:23(suggest)
   991000    0.104    0.000    0.104    0.000 {built-in method builtins.len}
        1    0.060    0.060    0.065    0.065 suggest_slow.py:5(load_friendships)
     1000    0.027    0.000    0.035    0.000 {method 'sort' of 'list' objects}
    70232    0.010    0.000    0.010    0.000 {method 'append' of 'list' objects}
```

(Machine-specific times. Notice the profiler's overhead: 2.4 s under the profiler against 1.8 s without.)

### 15.3 Reading the profile

The hot spot is clear: `mutual_count`, 1.7 of 2.4 seconds. But the most important number is not a time, it is **`ncalls` = 991,000**. With 1,000 users, that is almost **1,000 × 1,000**: `suggest` compares every user with **every other user** in the network. Yet a person who shares a friend with you must be a **friend of one of your friends**. With about 8 friends who each have about 8 friends, each user has only about 64 real candidates, not 999. The program does about 15 times more comparisons than it needs, and the waste grows with the square of the number of users.

That is an **algorithm** problem (section 12.1), so it comes first. Making `mutual_count` itself faster would only shave a little off 991,000 calls that should not happen at all.

### 15.4 Step 1: only look at friends of friends

```python
from suggest_slow import load_friendships, mutual_count


def suggest(users, friends, user, k=3):
    candidates = set()
    for friend in friends[user]:
        for other in friends[friend]:
            if other != user and other not in friends[user]:
                candidates.add(other)
    scores = [(mutual_count(friends, user, other), other) for other in candidates]
    scores.sort(key=lambda pair: (-pair[0], pair[1]))
    return [other for _, other in scores[:k]]
```

(`report` is unchanged.) Every candidate now shares at least one friend, so the `m > 0` check is no longer needed. We only changed **which** people we score, not **how**, and the sort key is the same, so the output must be identical.

Profiling this version (same script, same data) showed 274,786 function calls instead of 2,132,468. `mutual_count` was called 61,232 times instead of 991,000: about 61 candidates per user, close to our estimate of 64. The new profile also revealed the **next** hot spots, hidden before: `mutual_count` was still the top line (0.13 s; each call searches one friend **list** inside another), and `load_friendships` now stood out with 0.06 s for only 4,000 lines (`a not in users` searches a list of up to 1,000 users, twice per line).

### 15.5 Step 2: the right data structures

- Store friends as **sets**: `in` becomes O(1).
- Drop the `users` list: the keys of `friends` already are the users. (`sorted(friends)` gives the same order as `sorted(users)`.)
- Count mutual friends **while** walking friends of friends: each time we reach `other` through one of our friends, that friend is one mutual friend. A `Counter` counts them, so `mutual_count` disappears completely.
- Build the result as a list of lines and `"".join` them once, instead of `out += ...`.

```python
"""Suggest new friends: people who share the most friends with you (fast)."""
from collections import Counter


def load_friendships(lines):
    friends = {}
    for line in lines:
        a, b = line.strip().split(",")
        friends.setdefault(a, set()).add(b)
        friends.setdefault(b, set()).add(a)
    return friends


def suggest(friends, user, k=3):
    mine = friends[user]
    mutual = Counter()
    for friend in mine:
        for other in friends[friend]:
            if other != user and other not in mine:
                mutual[other] += 1          # one shared friend found
    ranked = sorted(mutual.items(), key=lambda pair: (-pair[1], pair[0]))
    return [other for other, _ in ranked[:k]]


def report(lines):
    friends = load_friendships(lines)
    rows = [f"{user}: {', '.join(suggest(friends, user))}\n" for user in sorted(friends)]
    return "".join(rows)
```

### 15.6 Measure, and compare the output

```python
import time

import suggest_fast
import suggest_slow
import suggest_step1

lines = suggest_slow.make_lines(1_000, 4_000)
expected = suggest_slow.report(lines)

for module in (suggest_slow, suggest_step1, suggest_fast):
    best = float("inf")
    for _ in range(3):
        start = time.perf_counter()
        result = module.report(lines)
        best = min(best, time.perf_counter() - start)
    assert result == expected, f"{module.__name__} changed the output!"
    print(f"{module.__name__:<14} {best * 1000:9.1f} ms   same output: yes")
```
```text
suggest_slow      1792.9 ms   same output: yes
suggest_step1      205.8 ms   same output: yes
suggest_fast        47.0 ms   same output: yes
```

(Machine-specific.) Best of three runs each, and the `assert` checks the full report text every time. The algorithm change gave about 9 times; the data structures another 4 times; together about **38 times faster**. And because the slow version is O(U²) in the number of users while the fast one grows with the number of friendships, the gap gets bigger as the network grows: at 2,000 users the slow version took over 7 seconds.

The same comparison on a few tiny hand-made inputs (no lines, one friendship, a chain of three) also matched: a big random network may never contain such edge cases, so check them separately.

### 15.7 A difference the tests did not ask about

One more experiment: what if the same friendship appears **twice** in the input?

```python
import suggest_fast
import suggest_slow

lines = ["a,b", "a,b", "a,c", "a,d", "b,x", "c,y", "d,y"]
print(suggest_slow.report(lines).splitlines()[0])
print(suggest_fast.report(lines).splitlines()[0])
```
```text
a: x, y
a: y, x
```

The slow version stores `b` **twice** in `a`'s friend list, so it counts `b` as two mutual friends with `x`. The fast version uses sets, so a repeated line changes nothing: `y` (two real mutual friends, `c` and `d`) beats `x` (one, `b`). The fast version is arguably *more* correct, but it is **different**, and "faster" was supposed to mean "same output". This is what every optimisation needs: decide what the specification says about such inputs (here: "duplicates count once" is the sensible rule), write a test for it, and mention the change. Never let a speed-up quietly change behaviour.

### 15.8 What we did

1. **Baseline**: time it, save the output as the safety net.
2. **Profile**, and read `ncalls` as well as times: 991,000 calls revealed an O(n²) algorithm.
3. **Fix the algorithm first** (friends of friends), then **profile again** to find the next hot spot.
4. **Fix the data structures** (sets, a `Counter`, `join`).
5. **Measure** each step on the same data (best of several runs) and **compare outputs** on big random data and small edge cases.
6. **Look for behaviour changes** the old tests did not cover, and decide them on purpose.

Problem p030 asks you to do the same for a different slow program.

#### Try it 15.1

Explain the exact number 991,000 in the first profile. The network has 1,000 users and 4,000 distinct friendships.

<details><summary>Answer</summary>

`suggest` runs once per user (1,000 times), and each time loops over all 1,000 users: 1,000,000 iterations. It skips the user themself (1,000 iterations skipped in total) and every existing friend. Each of the 4,000 friendships is skipped twice, once from each side (8,000). 1,000,000 − 1,000 − 8,000 = 991,000 calls of `mutual_count`. (Every user in this network has at least one friend, so all 1,000 appear in `users`.)

</details>

## 16. Common traps and summary

### 16.1 Common traps

| Trap | What happens | Fix |
|---|---|---|
| Changing code at random until the bug disappears | bug hidden, not understood; new bugs added | reproduce, isolate, hypothesise, test, fix, prevent |
| Reading only the last line of a traceback | you fix the place that *noticed* the problem | read the frames; find the first wrong decision in your code |
| `print(x)` while debugging | `"10"` and `10` look the same | `print(repr(x))`, `f"{x=}"` |
| `assert` for input validation | vanishes under `python -O` | `if ...: raise ValueError(...)` |
| `logging.info` shows nothing | root level is `WARNING` by default | configure once at program start |
| Adding a handler on every call | every message printed 2, 3, 4 times | configure once; `propagate = False` where needed |
| f-strings in log calls, `log.error(str(e))` | wasted formatting; lost traceback | `log.debug("x=%s", x)`, `log.exception(...)` |
| Bisecting with a broken check | "first bad commit" is nonsense | run the check by hand on one good and one bad version |
| Timing once, or averaging | noise decides the result | `timeit.repeat`, take the minimum |
| Benchmarking tiny or cached inputs | the slow part never shows | realistic sizes, two or three sizes, clear caches |
| Optimising without a profile | effort spent on code that was never slow | profile; read `cumtime`, `tottime` and `ncalls` |
| `getsizeof` of a container | counts references, not contents | `tracemalloc` |
| Unbounded caches and module-level lists | memory grows forever | `maxsize`, `deque(maxlen=...)`, unsubscribe |
| A speed-up that changes the output | a fast wrong program | compare outputs on big and edge-case inputs |
| mypy "Success" on untyped code | nothing was checked | `strict = true` |

### 16.2 Summary

- **Debugging is a method**: reproduce, isolate, hypothesise, test, fix the cause, prevent with a regression test.
- **Tracebacks** list frames outermost first, innermost last. Read the last line, then the last frame in your code, then walk up. `from` gives "direct cause"; an error inside `except` gives "During handling"; `from None` hides the context. `add_note` adds context.
- **Print** with `repr`/`{x=}` for quick looks; **assert** invariants to move crashes closer to their cause, never to validate input.
- **pdb**: `breakpoint()`, `python -m pdb`, post-mortem. `n`, `s`, `c`, `r`, `until`, `p`, `pp`, `w`, `u`, `d`, `b` (with conditions), `cl`, `display`, `interact`. `PYTHONBREAKPOINT=0` disables breakpoints; `sys.breakpointhook` replaces the debugger.
- **VS Code** offers the same with buttons: conditional breakpoints, hit counts, logpoints, watches, the call stack, and *Debug Test*; in the terminal, `pytest --pdb`.
- **Logging**: levels, a tree of named loggers, handlers and formatters, propagation. Configure once; `getLogger(__name__)` in modules; `log.exception` in handlers; lazy `%` arguments.
- **Narrowing down**: bisect versions (`git bisect run`), shrink failing inputs (halving, then delta debugging to a 1-minimal input), explain to the rubber duck.
- **Measure speed** with `timeit` (`number`, `repeat`, the minimum) and `perf_counter`; beware caches, tiny inputs and noise.
- **Profile** with `cProfile`/`pstats`: `cumtime` finds the slow area, `tottime` the hot function, `ncalls` the algorithm problem. Line profilers (and `sys.settrace`) go down to single lines.
- **Memory**: `tracemalloc` for current, peak and snapshot differences; leaks are references kept by long-lived containers.
- **Speed-ups**, in order: algorithm, data structure, avoid repeated work, caching, built-ins. Measure before and after; check the output is unchanged.
- **Quality tools**: ruff (lint + format), black, mypy (strict), configured in `pyproject.toml` and run automatically by `pre-commit`; tests for behaviour.
- **Reading code**: top-down, follow the data, run it, read the tests, rename and extract as you understand.

## Learning outcomes

After this chapter you should be able to:

1. Follow a systematic debugging loop and write a regression test for every bug you fix.
2. Read tracebacks, including chained exceptions and notes, and find the frame where the real mistake is.
3. Use `pdb` (breakpoints, stepping, frames, post-mortem) and the VS Code debugger, including on failing tests.
4. Set up logging with levels, named loggers and handlers, and log exceptions with their tracebacks.
5. Narrow down bugs with bisection and input shrinking.
6. Time code honestly with `timeit`, profile it with `cProfile`/`pstats` and line-level tools, and measure memory with `tracemalloc`.
7. Speed up code by fixing the algorithm and data structures first, proving the gain with before/after measurements and unchanged output.
8. Configure ruff, black, mypy and pre-commit, and explain what each catches and misses.
9. Read and refactor unfamiliar code with a plan.
