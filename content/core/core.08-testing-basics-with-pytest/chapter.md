# Chapter 8: Testing basics with pytest

You have now written dozens of functions. Every time, you checked them the same way: run the program, type a few inputs, look at the output, decide "looks right". That works for ten lines. It stops working the day you have forty functions, change one of them, and have to wonder what else you just broke.

This chapter teaches the habit that replaces "looks right": **automated tests**. A test is a small piece of code that calls your function with an input you chose, states the answer you expect, and lets the computer decide pass or fail. You write it once. After that, one command re-checks everything in a second, today, next week, and next year.

The tool is **pytest**, the most widely used testing tool in Python. It is small enough to learn in a day, and it is the same tool used by large companies. Everything in this chapter uses only things you already know: functions, lists, dicts, exceptions, `assert`. There are no classes and no tricks.

Testing is a skill with two halves, and beginners usually learn only the first:

1. **The mechanics**: how to write a test, run it, and read the report when it fails.
2. **The judgement**: which cases are worth testing. A hundred tests that all check the same easy case protect nothing. Five tests that check the borders, the empty case and the error case protect a lot.

Most of the effort in this chapter goes into the second half.

Along the way you will answer these questions:

- What exactly is a test, and why is it better than "running it and looking"?
- How do you write an assert-based test and run it with pytest?
- How do you read a failure report, and find the bug from it in under a minute?
- When a test fails, how do you decide whether the code or the test is wrong?
- How do you test many cases without copy and paste (`parametrize`)?
- How do you test that a function **raises** the right exception (`pytest.raises`, `match=`)?
- Which cases are worth testing: boundaries, empty input, error cases?
- What is test-driven development (TDD), and why would anyone write the test first?

A note on how examples are shown. Every block of code is followed by the exact output produced by running it with Python 3.14 and pytest 9.1. When you see `$ python -m pytest`, that is the command typed in the terminal. Three things in pytest's output differ from machine to machine, and are the only things that will differ on yours: the **versions** on the "platform" line, the **time** at the end (`in 0.01s`, always shown here as 0.01s), and the **folder path** (shown here as `/home/you/project`). Answer every "Predict the output" question on paper before you open the answer.

The classes you will meet later (grouping tests in a class, fixtures that prepare data, mocking) are deliberately left out. This chapter covers the part of testing you will use in every single project.

## Table of contents

1. [Why test at all](#1-why-test-at-all)
2. [Your first test](#2-your-first-test)
3. [Running pytest: discovery and options](#3-running-pytest-discovery-and-options)
4. [Reading a failure report](#4-reading-a-failure-report)
5. [A test failed: who is wrong?](#5-a-test-failed-who-is-wrong)
6. [Writing tests for existing code: how this module's problems are checked](#6-writing-tests-for-existing-code-how-this-modules-problems-are-checked)
7. [What makes a good test](#7-what-makes-a-good-test)
8. [Comparing values: floats, lists, dicts and strings](#8-comparing-values-floats-lists-dicts-and-strings)
9. [parametrize: many cases, one test](#9-parametrize-many-cases-one-test)
10. [Testing that exceptions are raised](#10-testing-that-exceptions-are-raised)
11. [Boundary cases and choosing useful tests](#11-boundary-cases-and-choosing-useful-tests)
12. [Making code easy to test](#12-making-code-easy-to-test)
13. [Does the test really test anything? Thinking in bugs](#13-does-the-test-really-test-anything-thinking-in-bugs)
14. [Test-driven development (TDD)](#14-test-driven-development-tdd)
15. [Common traps](#15-common-traps)
16. [Organising a test suite for a project](#16-organising-a-test-suite-for-a-project)
17. [Summary](#summary)
18. [Learning outcomes](#learning-outcomes)
19. [Module project](#module-project)
20. [Further reading](#further-reading)

---

## 1. Why test at all

### 1.1 The way you test today

Here is a function from chapter 6, and the way you have been checking it:

```python
def is_even(n):
    return n % 2 == 0
```

You open the REPL, type `is_even(4)`, see `True`, type `is_even(7)`, see `False`, and move on. That *is* testing. It is called **manual testing**: you act as the test runner and your eyes are the judge.

Manual testing has three problems that grow with the size of your program.

**Problem 1: it is forgotten.** Nobody remembers to try `is_even(0)` and `is_even(-3)` every time. The REPL session disappears when you close it, and with it all the cases you tried.

**Problem 2: it does not repeat.** You change `is_even` next month. To be sure nothing broke, you must try every case again by hand. Multiply by forty functions. You will skip some of them. Everybody does.

**Problem 3: it depends on your attention.** At the end of a long day, `False` and `True` look alike. A tired reader can look at a wrong answer and see a right one.

### 1.2 What a test is

An **automated test** is a function that does the manual check for you:

1. choose an **input**,
2. call the code,
3. compare the result with the **expected output** you decided *before* looking,
4. report **pass** or **fail**.

Written in Python, the comparison is an `assert` statement. You met `assert` in chapter 7: it does nothing when the condition is true, and raises `AssertionError` when it is false. A test is just a function that makes assertions:

```python
def test_four_is_even():
    assert is_even(4) is True
```

The word **assert** reads naturally: "I claim that `is_even(4)` is `True`". If the claim is false, the test fails and tells you.

### 1.3 Regression: the main reason

The most important reason for tests has a name. A **regression** is a change that breaks something that used to work.

Regressions are the normal way programs break. You do not usually break a function while writing it; you break it three weeks later, while fixing something else, in a different file, and you do not notice. A user finds it a month later.

A test suite catches this in seconds. You change the code, run the tests, and a test that was green yesterday is red today. The red test names the function and the input. You know what you broke while you still remember what you changed.

```text
Day 1:   write function, write tests          all green
Day 20:  change a different function          run tests
                                              one red test in the OLD function: caught at once
Without tests: nobody knows until a user complains.
```

### 1.4 The other benefits

- **Tests are examples that cannot go out of date.** A comment can lie after the code changes. A test that disagrees with the code turns red.
- **Tests let you change code without fear.** You can rewrite an ugly function completely and the tests tell you if the behaviour stayed the same.
- **Writing tests makes you think.** To write the expected value of `average([])` you must decide what *should* happen. That question often reveals a missing case before any user meets it.
- **Tests find bugs faster.** A failing test points at the exact input. Finding the same bug in a 300-line program by running it by hand can take an hour.

### 1.5 The honest costs

Tests are not free.

- They take time to write. For a small function, the tests are often longer than the function.
- They must be kept up to date. If you change what a function is *supposed* to do, you must change its tests too.
- A bad test is worse than none: it gives false confidence (section 13).
- Tests only check the cases you thought of. A passing test suite does **not** prove the code is correct. It proves that no case you tried is wrong.

The trade is almost always worth it, and it gets more worth it the larger the program grows. A good rule: *if you will run the code more than once, test it.*

### 1.6 Predict the output

Before you move on, think about this question.

**Question.** A function has 8 tests and all pass. A friend says: "so the function is correct." Give one reason the claim is not justified.

<details><summary>Answer</summary>

Passing tests only show that the **eight cases someone thought of** give the expected answers. Inputs nobody tried can still be wrong, and an expected value in a test can itself be wrong (a test that checks the wrong thing passes for a wrong function). Tests reduce risk; they cannot prove the absence of bugs.

</details>

---

## 2. Your first test

### 2.1 Install pytest

Python ships with a testing module called `unittest`, but almost everybody uses **pytest**, because tests written for it are shorter and the failure reports are far clearer. Install it once:

```text
$ python -m pip install pytest
```

Check that it works:

```text
$ python -m pytest --version
```

(The version line prints something like `pytest 9.1.1`.) If you are working inside the `learn` project, pytest is already installed.

### 2.2 A function and its test file

Two files are needed: the code, and a file of tests.

```python
# calc.py
def add(a, b):
    return a + b


def is_even(n):
    return n % 2 == 0
```

The test file imports what it tests and defines functions whose names start with `test`:

```python
# test_calc.py
from calc import add, is_even


def test_add_small_numbers():
    assert add(2, 3) == 5


def test_four_is_even():
    assert is_even(4) is True


def test_seven_is_not_even():
    assert is_even(7) is False
```

Run pytest in the folder that contains both files:

```text
$ python -m pytest
============================= test session starts ==============================
platform linux -- Python 3.14.4, pytest-9.1.1, pluggy-1.7.0
rootdir: /home/you/project
collected 3 items

test_calc.py ...                                                         [100%]

============================== 3 passed in 0.01s ===============================
```

Let us read this, line by line.

- `platform linux -- Python 3.14.4, pytest-9.1.1, ...`: the versions (machine-specific).
- `rootdir: /home/you/project`: the folder pytest treats as the project root (machine-specific path).
- `collected 3 items`: pytest *collected* three tests: it searched the folder, found `test_calc.py`, and found three functions starting with `test`.
- `test_calc.py ...`: the file name, and one **dot per test that passed**.
- `[100%]`: how far through the run it is.
- `3 passed in 0.01s`: the summary (the time is machine-specific).

All three are green. Pytest shows passing tests as a single quiet dot. This is on purpose: when everything works, you want to read almost nothing.

### 2.3 The anatomy of a test

```python
def test_add_small_numbers():
    assert add(2, 3) == 5
```

Every test has the same shape:

1. **Name** starting with `test`. Pytest finds tests by the name. A good name says what is checked: `test_add_small_numbers` tells you what broke without opening the file.
2. **No parameters**, for now (section 9 gives a way to add them).
3. **Arrange**: set up the data you need. Here, the numbers inside the call.
4. **Act**: call the code. Here, `add(2, 3)`.
5. **Assert**: compare the result with the expected value.

For small tests the three steps fit on one line. For larger ones, give each its own lines:

```python
def test_removing_an_item_from_the_cart():
    cart = ["pen", "ink"]          # arrange
    cart.remove("pen")             # act
    assert cart == ["ink"]         # assert
```

You do **not** write `if __name__ == "__main__":` or call the tests yourself. pytest finds them and calls them for you. You also do not `print` anything: a passing test is silent.

### 2.4 What happens when the assert is false

Add one wrong test, to see what pytest does:

```python
# test_calc.py
from calc import add, is_even


def test_add_small_numbers():
    assert add(2, 3) == 5


def test_four_is_even():
    assert is_even(4) is True


def test_seven_is_even_by_mistake():
    assert is_even(7) is True
```
```text
$ python -m pytest -q --tb=short
..F                                                                      [100%]
=================================== FAILURES ===================================
________________________ test_seven_is_even_by_mistake _________________________
test_calc.py:13: in test_seven_is_even_by_mistake
    assert is_even(7) is True
E   assert False is True
E    +  where False = is_even(7)
=========================== short test summary info ============================
FAILED test_calc.py::test_seven_is_even_by_mistake - assert False is True
1 failed, 2 passed in 0.01s
```

Now there is an `F` instead of a dot, a section called `FAILURES`, and the last line says `1 failed, 2 passed`. The next section (4) reads this report in detail. For now notice two things: the other two tests still ran and passed, and pytest finished with a clear count. A failing test does not stop the run.

### 2.5 Try it

**Try it.** Without running anything, say what the last line of the report is if you write these three tests and the function is `add(a, b): return a + b`:

```python
def test_a():
    assert add(1, 1) == 2

def test_b():
    assert add(1, 1) == 3

def test_c():
    assert add("1", "1") == "11"
```

<details><summary>Answer</summary>

`test_a` passes. `test_b` fails because `1 + 1` is 2, not 3. `test_c` passes: `+` joins two strings, giving `"11"`. The last line is `1 failed, 2 passed`. (If you thought `test_c` would crash: `add` has no type check, so a string works.)

```text
$ python -m pytest -q --tb=no
.F.                                                                      [100%]
=========================== short test summary info ============================
FAILED test_calc.py::test_b - assert 2 == 3
1 failed, 2 passed in 0.01s
```

</details>

---

## 3. Running pytest: discovery and options

### 3.1 How pytest finds your tests

You never tell pytest which functions are tests. It **discovers** them with simple rules:

1. It looks in the folder you run it from (and all folders below).
2. It reads every file whose name matches `test_*.py` or `*_test.py`.
3. In those files it collects every function whose name starts with `test`.

Anything else is invisible. A function named `check_add` is **not** a test, even if it contains an assert. This is the number one reason for "my test never fails": it never ran.

```python
# calc.py
def add(a, b):
    return a + b
```
```python
# test_calc.py
from calc import add


def test_add():
    assert add(2, 2) == 4


def check_add_negative():
    assert add(-1, -1) == 0


def helper(n):
    return n * 2
```
```text
$ python -m pytest -v --no-header
============================= test session starts ==============================
collecting ... collected 1 item

test_calc.py::test_add PASSED                                            [100%]

============================== 1 passed in 0.01s ===============================
```

Only `test_add` ran. `check_add_negative` has a false assert and nobody noticed, because pytest never looked at it. The `-v` flag (verbose) shows every collected test by name, which makes this easy to see. `--no-header` hides the machine-specific platform lines.

A file named `calc_checks.py` would also be skipped, because the file name does not match `test_*.py`. Name files `test_something.py` and tests `test_something_specific` and you can forget the rules.

**Predict the output.** Which of these names does pytest collect as tests? `test_one`, `testtwo`, `Test_three`, `four_test`, `test`.

<details><summary>Answer</summary>

`test_one`, `testtwo` and `test` are collected: the rule is "starts with lower-case `test`". There is no need for an underscore, though you should always use one. `Test_three` has a capital `T` and `four_test` does not *start* with `test`, so neither is collected.

</details>

### 3.2 Useful options

| Command | What it does |
|---|---|
| `python -m pytest` | run every test found |
| `python -m pytest -q` | **q**uiet: fewer lines |
| `python -m pytest -v` | **v**erbose: one line per test, with its name |
| `python -m pytest test_calc.py` | run one file |
| `python -m pytest test_calc.py::test_add` | run one test function |
| `python -m pytest -k add` | run tests whose name contains `add` |
| `python -m pytest -x` | stop at the **first** failure |
| `python -m pytest --lf` | re-run only the tests that failed last time |

`-v`, `-k` and `-x` are the three you will use every day. Here is `-v` with the project from section 2.4:

```python
# calc.py
def add(a, b):
    return a + b


def is_even(n):
    return n % 2 == 0
```
```python
# test_calc.py
from calc import add, is_even


def test_add_small_numbers():
    assert add(2, 3) == 5


def test_add_negative_numbers():
    assert add(-2, -3) == -5


def test_four_is_even():
    assert is_even(4) is True


def test_seven_is_even_by_mistake():
    assert is_even(7) is True
```
```text
$ python -m pytest -v --no-header
============================= test session starts ==============================
collecting ... collected 4 items

test_calc.py::test_add_small_numbers PASSED                              [ 25%]
test_calc.py::test_add_negative_numbers PASSED                           [ 50%]
test_calc.py::test_four_is_even PASSED                                   [ 75%]
test_calc.py::test_seven_is_even_by_mistake FAILED                       [100%]

=================================== FAILURES ===================================
________________________ test_seven_is_even_by_mistake _________________________

    def test_seven_is_even_by_mistake():
>       assert is_even(7) is True
E       assert False is True
E        +  where False = is_even(7)

test_calc.py:17: AssertionError
=========================== short test summary info ============================
FAILED test_calc.py::test_seven_is_even_by_mistake - assert False is True
========================= 1 failed, 3 passed in 0.01s ==========================
```

Each line has the file, `::`, the test name, and the outcome. That `file::name` form is also how you ask for **one** test. Use `-k` to select by a piece of the name:

```text
$ python -m pytest -v --no-header -k add
============================= test session starts ==============================
collecting ... collected 4 items / 2 deselected / 2 selected

test_calc.py::test_add_small_numbers PASSED                              [ 50%]
test_calc.py::test_add_negative_numbers PASSED                           [100%]

======================= 2 passed, 2 deselected in 0.01s ========================
```

Only the two `add` tests ran. The other two were *deselected*. Use `-k` while you work on one function and you do not need to wait for or read the rest.

The `-x` flag stops the run at the first failure. In a suite of hundreds of tests it saves you from a screen full of follow-up failures.

### 3.3 The exit code

When pytest finishes it returns an **exit code** to the shell: `0` if all tests passed, `1` if some failed, `5` if it collected no tests at all. Programs and scripts use this to decide what to do next (for example, to stop a deployment when a test fails). You will not use it by hand, but note the `5`: *no tests collected is not a pass*. If pytest says `no tests ran`, your names or file names are wrong.

```python
# calc.py
def add(a, b):
    return a + b
```
```python
# check_calc.py
from calc import add


def test_add():
    assert add(2, 2) == 4
```
```text
$ python -m pytest -q; echo "exit code: $?"

no tests ran in 0.01s
exit code: 5
```

The file is called `check_calc.py`, which does not match `test_*.py`, so pytest found nothing.

### 3.4 Where do the test files go

For small projects, keep it simple: the code file and its test file side by side in one folder.

```text
project/
    calc.py
    test_calc.py
```

`from calc import add` works because pytest puts the folder of the test file on Python's import path. Later, as the project grows, you will move tests into a `tests/` folder (section 16). The rule for now: one `test_X.py` for every `X.py`.

### 3.5 Try it

**Try it.** You run `python -m pytest -k "even and not seven"` (pytest accepts `and`, `or` and `not` in `-k`). With the four tests of section 3.2, which tests run?

<details><summary>Answer</summary>

Only `test_four_is_even`. Names containing `even` are `test_four_is_even` and `test_seven_is_even_by_mistake`; the second contains `seven`, which `not seven` removes.

```text
$ python -m pytest -v --no-header -k "even and not seven"
============================= test session starts ==============================
collecting ... collected 4 items / 3 deselected / 1 selected

test_calc.py::test_four_is_even PASSED                                   [100%]

======================= 1 passed, 3 deselected in 0.01s ========================
```

</details>

---

## 4. Reading a failure report

A failing test is the most valuable thing a test suite produces. The report is not an error to be afraid of: it is a map to the bug. Learn to read it in the same order every time and you will find most bugs in seconds.

### 4.1 One failure, read from top to bottom

```python
# shop.py
def apply_discount(price, percent):
    return price - price * percent / 100
```
```python
# test_shop.py
from shop import apply_discount


def test_ten_percent_off():
    assert apply_discount(200, 10) == 180


def test_half_price():
    assert apply_discount(80, 50) == 30
```
```text
$ python -m pytest
============================= test session starts ==============================
platform linux -- Python 3.14.4, pytest-9.1.1, pluggy-1.7.0
rootdir: /home/you/project
collected 2 items

test_shop.py .F                                                          [100%]

=================================== FAILURES ===================================
_______________________________ test_half_price ________________________________

    def test_half_price():
>       assert apply_discount(80, 50) == 30
E       assert 40.0 == 30
E        +  where 40.0 = apply_discount(80, 50)

test_shop.py:9: AssertionError
=========================== short test summary info ============================
FAILED test_shop.py::test_half_price - assert 40.0 == 30
========================= 1 failed, 1 passed in 0.01s ==========================
```

Read it in this order:

1. **The last line** (`1 failed, 1 passed`): how bad is it?
2. **The name in the header** (`____ test_half_price ____`): which test?
3. **The `>` line**: the exact line of the test that failed. The `>` points at it.
4. **The `E` lines**: the explanation. `E       assert 40.0 == 30` says: the left side evaluated to `40.0`, the right side to `30`, and they are not equal.
5. **The `where` line** (`+  where 40.0 = apply_discount(80, 50)`): where the left value came from. Pytest rewrites your `assert` so that it can show you the values of the pieces.
6. **The location line** (`test_shop.py:9: AssertionError`): file and line number.
7. **The short summary** at the bottom: one line per failure, handy when there are many.

Now the question that matters: is the function wrong, or is the test? `apply_discount(80, 50)` is `80 - 80 * 50 / 100`, which is `80 - 40`, which is `40`. Half price of 80 is 40. The **function is right and the test is wrong**: whoever wrote `30` made an arithmetic slip. Section 5 returns to this question, because you must always ask it.

### 4.2 The left side is what the code produced

In `assert LEFT == RIGHT`, the convention is: put the call you are testing on the **left**, the expected value you typed on the **right**. Then every report reads the same way: *left is what the code gave, right is what I expected*. Keep to this habit even though `==` is symmetric. It makes reports instantly readable.

### 4.3 Reports for different kinds of values

Pytest shows more than "not equal" when it can. For **strings**, it shows where they differ:

```python
# test_text.py
def shout(text):
    return text.upper() + "!"


def test_shout():
    assert shout("hello") == "HELLO!!"
```
```text
$ python -m pytest -q
F                                                                        [100%]
=================================== FAILURES ===================================
__________________________________ test_shout __________________________________

    def test_shout():
>       assert shout("hello") == "HELLO!!"
E       AssertionError: assert 'HELLO!' == 'HELLO!!'
E
E         - HELLO!!
E         ?       -
E         + HELLO!

test_text.py:6: AssertionError
=========================== short test summary info ============================
FAILED test_text.py::test_shout - AssertionError: assert 'HELLO!' == 'HELLO!!'
1 failed in 0.01s
```

The `E` lines show the left (`'HELLO!'`) and right (`'HELLO!!'`) strings and mark the difference: the `?` line has a `-` under the extra `!` that only the right side has.

For **lists**, it shows the first index that differs, or the extra item:

```python
# test_lists.py
def squares(n):
    return [i * i for i in range(n)]


def test_squares():
    assert squares(4) == [0, 1, 4, 9, 16]
```
```text
$ python -m pytest -q test_lists.py
F                                                                        [100%]
=================================== FAILURES ===================================
_________________________________ test_squares _________________________________

    def test_squares():
>       assert squares(4) == [0, 1, 4, 9, 16]
E       assert [0, 1, 4, 9] == [0, 1, 4, 9, 16]
E
E         Right contains one more item: 16
E         Use -v to get more diff

test_lists.py:6: AssertionError
=========================== short test summary info ============================
FAILED test_lists.py::test_squares - assert [0, 1, 4, 9] == [0, 1, 4, 9, 16]
1 failed in 0.01s
```

Pytest says the right list contains one more item, `16`, and also prints the lists. (The function computed `[0, 1, 4, 9]`, the test expected one more: the test is asking for `i` from 0 to 4, which is five squares, not four.)

For **dictionaries**, it shows which keys differ:

```python
# test_dicts.py
def count_letters(word):
    counts = {}
    for ch in word:
        counts[ch] = counts.get(ch, 0) + 1
    return counts


def test_count_letters():
    assert count_letters("book") == {"b": 1, "o": 1, "k": 1}
```
```text
$ python -m pytest -q test_dicts.py
F                                                                        [100%]
=================================== FAILURES ===================================
______________________________ test_count_letters ______________________________

    def test_count_letters():
>       assert count_letters("book") == {"b": 1, "o": 1, "k": 1}
E       AssertionError: assert {'b': 1, 'o': 2, 'k': 1} == {'b': 1, 'o': 1, 'k': 1}
E
E         Omitting 2 identical items, use -vv to show
E         Differing items:
E         {'o': 2} != {'o': 1}
E         Use -v to get more diff

test_dicts.py:9: AssertionError
=========================== short test summary info ============================
FAILED test_dicts.py::test_count_letters - AssertionError: assert {'b': 1, 'o...
1 failed in 0.01s
```

The report names the key `o` and shows `2` on the left and `1` on the right. The function counts both `o`s, the test forgot the second one.

All three reports follow the same plan: find the first difference, name it, show the two sides.

### 4.4 When the test crashes instead of failing

An `assert` fails when the claim is false. But the code under test can also **raise an exception**. Pytest reports that as a failure too, and shows the traceback you know from chapter 7:

```python
# shop.py
def average(numbers):
    return sum(numbers) / len(numbers)
```
```python
# test_shop.py
from shop import average


def test_average_of_nothing():
    assert average([]) == 0
```
```text
$ python -m pytest -q
F                                                                        [100%]
=================================== FAILURES ===================================
___________________________ test_average_of_nothing ____________________________

    def test_average_of_nothing():
>       assert average([]) == 0
               ^^^^^^^^^^^

test_shop.py:5:
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

numbers = []

    def average(numbers):
>       return sum(numbers) / len(numbers)
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^
E       ZeroDivisionError: division by zero

shop.py:2: ZeroDivisionError
=========================== short test summary info ============================
FAILED test_shop.py::test_average_of_nothing - ZeroDivisionError: division by...
1 failed in 0.01s
```

Here there is no `assert 40.0 == 30` line. Instead the `E` line says `ZeroDivisionError: division by zero`, and the lines above it show the call chain: the test called `average`, which crashed at its `return` line. Read it exactly like a normal traceback: the **last** line is the exception, the code lines above it are where it happened.

Pytest can print tracebacks in several styles (`--tb=short` is more compact, `--tb=line` shows one line per failure, `--tb=no` shows none). The `learn` checker uses `--tb=short`.

### 4.5 Many failures: read the first, fix, run again

When ten tests fail, do not read ten reports. Very often one bug causes all of them. Read the **first** failure, fix, run again. Use `-x` to stop at the first failure:

```python
# shop.py
def total(prices):
    result = 0
    for p in prices:
        result = p
    return result
```
```python
# test_shop.py
from shop import total


def test_total_one_price():
    assert total([5]) == 5


def test_total_two_prices():
    assert total([5, 7]) == 12


def test_total_three_prices():
    assert total([1, 2, 3]) == 6


def test_total_empty():
    assert total([]) == 0
```
```text
$ python -m pytest -q --tb=line
.FF.                                                                     [100%]
=================================== FAILURES ===================================
E   assert 7 == 12
     +  where 7 = total([5, 7])
/home/you/project/test_shop.py:9: assert 7 == 12
E   assert 3 == 6
     +  where 3 = total([1, 2, 3])
/home/you/project/test_shop.py:13: assert 3 == 6
=========================== short test summary info ============================
FAILED test_shop.py::test_total_two_prices - assert 7 == 12
FAILED test_shop.py::test_total_three_prices - assert 3 == 6
2 failed, 2 passed in 0.01s
```

Two tests fail, and the `--tb=line` option prints only the file, the line and the message for each failure. The first line shows `assert 7 == 12`: the function returned the **last** price instead of the sum. The bug is the line `result = p`, which should be `result += p`. One bug, two failures. Fix it and both go green.

The pattern for finding the bug from a report:

1. Which test failed, and what input did it use?
2. What did the code give (left) and what was expected (right)?
3. What is *different* in this input from the tests that passed? (Here: more than one price.)
4. That difference points at the bug.

### 4.6 Printed output

If your code prints something, pytest hides it for passing tests and shows it under `Captured stdout call` in the report of a failing test. Run with `-s` to see prints live. Remember to remove debugging prints when you are done.

### 4.7 Try it

**Predict the output.** What does the `E` line say (in the form `assert <left> == <right>`) for this test? Do the arithmetic first.

```python
def percent(part, whole):
    return part / whole * 100

def test_percent():
    assert percent(1, 4) == 20
```

<details><summary>Answer</summary>

`1 / 4 * 100` is `25.0`, so the line reads `assert 25.0 == 20`. The function is right; the test expects the wrong number (a quarter is 25 percent).

```text
$ python -m pytest -q --tb=no
F                                                                        [100%]
=========================== short test summary info ============================
FAILED test_percent.py::test_percent - assert 25.0 == 20
1 failed in 0.01s
```

</details>

---

## 5. A test failed: who is wrong?

A red test says only one thing: *the code and the test disagree*. It does not say which is wrong. Beginners assume the code is always at fault and start "fixing" a function that was right. Always ask first.

### 5.1 Three possible causes

1. **The code is wrong.** The test is right. Fix the code. This is the case tests exist for.
2. **The test is wrong.** The expected value was miscalculated or typed wrong. Fix the test.
3. **The requirement is unclear.** Both are reasonable. You must **decide** what the function should do, then make both agree (and write the decision down in the docstring).

### 5.2 How to decide

Work out the expected answer **by hand, from the requirement**, not from the code. If your hand answer agrees with the test, the code is wrong. If it agrees with the code, the test is wrong.

Never copy the code's output into the test to "make it green". That makes the test agree with the code *whatever the code does*, which is the opposite of testing (section 14 comes back to this).

Try it on a real case. A function should return the **second largest** number in a list of distinct numbers:

```python
# ranking.py
def second_largest(numbers):
    ordered = sorted(numbers)
    return ordered[1]
```
```python
# test_ranking.py
from ranking import second_largest


def test_second_largest_of_three():
    assert second_largest([10, 30, 20]) == 20


def test_second_largest_of_four():
    assert second_largest([5, 1, 9, 7]) == 7
```
```text
$ python -m pytest -q --tb=short
.F                                                                       [100%]
=================================== FAILURES ===================================
_________________________ test_second_largest_of_four __________________________
test_ranking.py:9: in test_second_largest_of_four
    assert second_largest([5, 1, 9, 7]) == 7
E   assert 5 == 7
E    +  where 5 = second_largest([5, 1, 9, 7])
=========================== short test summary info ============================
FAILED test_ranking.py::test_second_largest_of_four - assert 5 == 7
1 failed, 1 passed in 0.01s
```

Which one is wrong? Do it by hand. For `[10, 30, 20]` the largest is 30 and the second largest is 20: the test says 20, correct. For `[5, 1, 9, 7]` the largest is 9, the second is 7: the test is correct again. So the **code** is wrong. `sorted` sorts from small to large, so index `1` is the *second smallest*. The first test passed only by luck: in a list of three numbers the second smallest and the second largest are the same one. That is an important warning: a test that passes by coincidence hides the bug. The second test, with four numbers, exposed it. The fix is `ordered[-2]`.

### 5.3 Messages in asserts

You can add a message after a comma. It appears in the report when the assert fails:

```python
# test_msg.py
def total_with_tax(price, tax_percent):
    return price + price * tax_percent // 100


def test_total_with_tax():
    result = total_with_tax(99, 18)
    assert result == 116.82, "99 plus 18 percent tax is 116.82. Check integer division."
```
```text
$ python -m pytest -q --tb=short
F                                                                        [100%]
=================================== FAILURES ===================================
_____________________________ test_total_with_tax ______________________________
test_msg.py:7: in test_total_with_tax
    assert result == 116.82, "99 plus 18 percent tax is 116.82. Check integer division."
E   AssertionError: 99 plus 18 percent tax is 116.82. Check integer division.
E   assert 116 == 116.82
=========================== short test summary info ============================
FAILED test_msg.py::test_total_with_tax - AssertionError: 99 plus 18 percent ...
1 failed in 0.01s
```

The message sits on the `E` line next to the values. A good message says **what the code should do and the most likely mistake**, not just "wrong". Compare:

- Poor: `assert f(0) == 0, "failed"`
- Good: `assert f(0) == 0, "0 has no digits to add, so the sum is 0. Check the empty loop case."`

Every test in this module's problems carries a message like the good one. When you write tests for other people (or for yourself in three months), you will be glad of it.

Remember from chapter 7: write `assert cond, "message"` with **no** parentheses around the pair. `assert (cond, "message")` asserts a non-empty tuple, which is always true, and the test can never fail. Python 3.14 even prints a `SyntaxWarning` for it.

### 5.4 Try it

**Predict the output.** The function should return the number of items in a list that are bigger than 10. Is the code or the test wrong?

```python
def count_big(items):
    count = 0
    for x in items:
        if x >= 10:
            count += 1
    return count

def test_count_big():
    assert count_big([5, 10, 15]) == 1
```

<details><summary>Answer</summary>

By hand: only `15` is *bigger than* 10, so the answer is 1: the test is right. The code counts `10` too (`>=`), so it returns 2: the **code** is wrong; use `>`. The failing assert reads `assert 2 == 1`. This is also a boundary bug: the value exactly on the border (10) is where the mistake hides (section 11).

```text
$ python -m pytest -q --tb=no
F                                                                        [100%]
=========================== short test summary info ============================
FAILED test_big.py::test_count_big - assert 2 == 1
1 failed in 0.01s
```

</details>

---

## 6. Writing tests for existing code: how this module's problems are checked

So far the test code was a helper and the function was yours. In this module, many problems turn this around: **you write the tests** and the program checks *your tests*. You need to understand how that works, because it also teaches a very important idea about what a good test is.

### 6.1 Two kinds of code problems

In this module a code problem is one of two kinds, and the problem statement always says which.

**Kind 1: make the tests pass.** `test_solution.py` (the tests) belongs to the problem, and `solution.py` (the function) is yours. This is how all earlier modules worked. In this module the tests are sometimes the whole specification: the statement tells you to read them, and you write the function. This is the heart of TDD (section 14).

**Kind 2: write the tests.** The function under test is printed in the problem statement. **`solution.py` is your file of tests.** At the top you write

```python
from target import clamp
```

`target` is the name of the module that holds the function being tested. You write test functions like

```python
def test_value_inside_the_range_is_unchanged():
    assert clamp(5, 0, 10) == 5, "A value inside the range must come back unchanged."
```

and you finish when your tests are good enough.

### 6.2 What "good enough" means

How can a program tell whether your tests are good? It cannot read them, but it can **try them on broken code**. The checker does this:

1. It copies your `solution.py` next to a file called `target.py` that contains the **correct** function, and runs pytest. Every test of yours must **pass**. (If one fails, your expected value is wrong.)
2. It then replaces `target.py` by several **buggy copies** of the function, one bug at a time, and runs your tests again on each. For every buggy copy, **at least one of your tests must fail**. A test suite that cannot tell the correct function from a broken one has no value.

This is a real technique called **mutation testing**: make small deliberate bugs ("mutants") and check that the tests notice. A mutant that is not noticed is said to have *survived*, and that tells you exactly which case your suite is missing. When a mutant survives, the report names the bug, for example: "Your tests did NOT catch this bug: values inside the range are replaced by low."

You can see the idea by running it yourself. Here are a correct `clamp` and a first attempt at tests:

```python
# target.py
def clamp(x, low, high):
    if x < low:
        return low
    if x > high:
        return high
    return x
```
```python
# solution.py
from target import clamp


def test_inside_the_range():
    assert clamp(5, 0, 10) == 5, "A value inside the range must come back unchanged."
```
```text
$ python -m pytest solution.py -q
.                                                                        [100%]
1 passed in 0.01s
```

One test, and it passes on the correct function. Now replace `target.py` with a buggy copy that forgets to cut values above `high`:

```python
# target.py
def clamp(x, low, high):
    if x < low:
        return low
    return x
```
```text
$ python -m pytest solution.py -q
.                                                                        [100%]
1 passed in 0.01s
```

Still green! The test only tried a value inside the range, where the buggy and the correct function agree. This is a **survivor**: the checker would answer "your tests did not catch the bug where values above the range are not cut". Add a test that separates the two:

```python
# solution.py
from target import clamp


def test_inside_the_range():
    assert clamp(5, 0, 10) == 5, "A value inside the range must come back unchanged."


def test_above_the_range_is_cut():
    assert clamp(15, 0, 10) == 10, "A value above high must become high."
```
```text
$ python -m pytest solution.py -q --tb=short
.F                                                                       [100%]
=================================== FAILURES ===================================
_________________________ test_above_the_range_is_cut __________________________
solution.py:9: in test_above_the_range_is_cut
    assert clamp(15, 0, 10) == 10, "A value above high must become high."
E   AssertionError: A value above high must become high.
E   assert 15 == 10
E    +  where 15 = clamp(15, 0, 10)
=========================== short test summary info ============================
FAILED solution.py::test_above_the_range_is_cut - AssertionError: A value abo...
1 failed, 1 passed in 0.01s
```

Now the buggy function is caught (the `15` is returned instead of `10`). Put the correct function back and the same two tests pass:

```python
# target.py
def clamp(x, low, high):
    if x < low:
        return low
    if x > high:
        return high
    return x
```
```text
$ python -m pytest solution.py -q
..                                                                       [100%]
2 passed in 0.01s
```

### 6.3 How to work on a "write the tests" problem

1. Copy the function from the problem statement into a file `target.py`, in the same folder as your `solution.py`.
2. Write your tests in `solution.py`. Run them with `python -m pytest solution.py`.
3. Then be the checker: edit `target.py` yourself to introduce bugs (change a `<` to `<=`, remove a branch, return the wrong value). Do your tests go red? If not, add a test. Put the correct function back afterwards.
4. Run `./learn check` to run the real checker.

Step 3 is not cheating. It is exactly the habit that makes a good tester: **"what bug could be hiding here, and would my tests see it?"**

### 6.4 Rules the checker follows

- Your file must contain functions whose names start with `test`. If pytest collects none, the check says so.
- Your tests must pass on the correct function. A failing test on the correct code means *your expected value is wrong*: re-calculate by hand.
- Names must be unique. If two test functions have the same name, Python keeps only the last one, and the first silently disappears.
- Some problems also require a technique: for example, that you use `parametrize` or `pytest.raises(..., match=...)`. The statement says so.
- You do not need to test **every** possible input. The buggy copies are *plausible* bugs: the ones a real programmer makes (off by one at a border, forgetting the empty case, wrong error type). Sections 9 to 11 tell you how to find them.

### 6.5 Try it

**Question.** Here is a function and one test. Describe one buggy copy of `is_adult` that this test would **not** catch, and a test that would catch it.

```python
def is_adult(age):
    return age >= 18

def test_is_adult():
    assert is_adult(30) is True
```

<details><summary>Answer</summary>

Many copies survive: `return age > 18` (wrong at the border), `return age >= 21` (wrong limit), or `return True` (always true). The test uses only a clear-cut adult. Tests that catch them: `assert is_adult(18) is True` (the border; kills `> 18` and `>= 21`), and `assert is_adult(17) is False` (just under the border; kills `return True` and any limit that is too low, such as `>= 16`). The border values 17 and 18 are the most valuable pair.

</details>

---

## 7. What makes a good test

Tests are code, and code can be good or bad. Seven habits separate a test suite you trust from one that wastes time.

### 7.1 One reason to fail

A test should check **one behaviour**. When it fails, the name should tell you what broke. Compare:

```python
def test_everything():
    assert total([1, 2]) == 3
    assert total([]) == 0
    assert total([5]) == 5
    assert discount(100, 10) == 90
```

with

```python
def test_total_of_two_prices():
    assert total([1, 2]) == 3

def test_total_of_nothing_is_zero():
    assert total([]) == 0

def test_total_of_one_price_is_that_price():
    assert total([5]) == 5
```

When the first version fails you know only that "something is wrong". The first failing assert also **stops** the test, so the remaining asserts never run and you cannot see whether they would have passed. In the second version, three names tell you which behaviours are broken and which are fine.

A test may have **more than one `assert`** if they check the *same behaviour* from different sides (for instance the returned value and the changed list). The rule is about behaviours, not about counting lines.

### 7.2 A name that says what is checked

`test_total_of_nothing_is_zero` is a sentence: it names the function, the situation, and the expected result. When it fails, the report line `FAILED test_shop.py::test_total_of_nothing_is_zero` already tells you what is wrong, before you read anything else. Avoid `test1`, `test_total2`, `test_it_works`.

### 7.3 Independence

Each test must work **alone and in any order**. Never let one test depend on another having run first. Here is the trap:

```python
# test_cart.py
cart = []


def test_add_one_item():
    cart.append("pen")
    assert len(cart) == 1


def test_add_second_item():
    cart.append("ink")
    assert len(cart) == 2
```
```text
$ python -m pytest -q
..                                                                       [100%]
2 passed in 0.01s
```
```text
$ python -m pytest -q -k second --tb=short
F                                                                        [100%]
=================================== FAILURES ===================================
_____________________________ test_add_second_item _____________________________
test_cart.py:11: in test_add_second_item
    assert len(cart) == 2
E   AssertionError: assert 1 == 2
E    +  where 1 = len(['ink'])
=========================== short test summary info ============================
FAILED test_cart.py::test_add_second_item - AssertionError: assert 1 == 2
1 failed, 1 deselected in 0.01s
```

Run together, both pass. Run the second test **alone** (`-k second`) and it fails, because the shared list `cart` is empty when it starts. The tests only work in a lucky order. The fix is to build what each test needs **inside** the test:

```python
# test_cart.py
def test_add_one_item():
    cart = []
    cart.append("pen")
    assert len(cart) == 1


def test_add_second_item():
    cart = ["pen"]
    cart.append("ink")
    assert len(cart) == 2
```
```text
$ python -m pytest -q -k second
.                                                                        [100%]
1 passed, 1 deselected in 0.01s
```

### 7.4 No logic in tests

A test should be so simple that it is obviously correct. If a test contains a loop, an `if`, or a complicated calculation, the test itself can have a bug, and then who tests the test? Compare:

```python
def test_squares():
    for n in range(5):
        assert square(n) == n * n      # the test repeats the code's own formula
```

If `square` is written as `n * n` and the test uses `n * n`, they agree even when both are wrong for the same reason. Write the expected values **as numbers you worked out by hand**: `assert square(4) == 16`.

### 7.5 Deterministic: same result every run

A test must give the same answer every time. Do not depend on the current time, random numbers, or files that might change. A test that sometimes passes and sometimes fails (a "flaky" test) is worse than no test: people learn to ignore red. If a function depends on the date or a random number, pass the value in as an argument (section 12).

### 7.6 Fast

A test suite you run after every change must take seconds. Tests that sleep, download or wait for input make people stop running the suite. Never call `input()` inside code under test: it waits for typing and the test hangs (section 12 shows how to avoid it).

### 7.7 Compare with an independent expected value

The expected value must come from **outside the code under test**: from the requirement, from a calculation by hand, from a trusted example. The test `assert total(prices) == sum(prices)` is suspicious if `total` is itself implemented with `sum`. It will pass even if both are wrong in the same way.

### 7.8 Try it

**Predict the output.** Two tests share one dict. In what order does pytest run them and what is the last line?

```python
stock = {"pen": 2}

def test_sell_one():
    stock["pen"] -= 1
    assert stock["pen"] == 1

def test_sell_one_again():
    stock["pen"] -= 1
    assert stock["pen"] == 1
```

<details><summary>Answer</summary>

Pytest runs them in the order they are written. The first passes (`2 - 1 == 1`). The second finds `stock["pen"]` already at 1, subtracts again to 0, and fails with `assert 0 == 1`. So the last line is `1 failed, 1 passed`. Each test must create its own `stock`.

```text
$ python -m pytest -q --tb=no
.F                                                                       [100%]
=========================== short test summary info ============================
FAILED test_stock.py::test_sell_one_again - assert 0 == 1
1 failed, 1 passed in 0.01s
```

</details>

---

## 8. Comparing values: floats, lists, dicts and strings

`assert a == b` handles almost everything, but several kinds of values need a little care.

### 8.1 Floats are not exact

Chapter 2 showed that `0.1 + 0.2` is not exactly `0.3`. That makes this natural test **fail** for a correct function:

```python
# test_float.py
def add(a, b):
    return a + b


def test_add_floats():
    assert add(0.1, 0.2) == 0.3
```
```text
$ python -m pytest -q --tb=short
F                                                                        [100%]
=================================== FAILURES ===================================
_______________________________ test_add_floats ________________________________
test_float.py:6: in test_add_floats
    assert add(0.1, 0.2) == 0.3
E   assert 0.30000000000000004 == 0.3
E    +  where 0.30000000000000004 = add(0.1, 0.2)
=========================== short test summary info ============================
FAILED test_float.py::test_add_floats - assert 0.30000000000000004 == 0.3
1 failed in 0.01s
```

The function is right; the comparison is the problem. The fix is `pytest.approx`, which means "equal to within a tiny tolerance":

```python
# test_float.py
import pytest


def add(a, b):
    return a + b


def test_add_floats():
    assert add(0.1, 0.2) == pytest.approx(0.3)
```
```text
$ python -m pytest -q
.                                                                        [100%]
1 passed in 0.01s
```

By default `approx` allows a **relative** error of one millionth (`1e-6`) of the expected value. You can set your own: `pytest.approx(0.3, abs=0.01)` allows a difference of 0.01. Use `approx` whenever the expected value is a float that came from a calculation. When the answer is a whole number stored in an int, or a float that is exact in binary (such as `2.5`), plain `==` is fine.

### 8.2 Lists: order matters, and so does the type

`[1, 2] == [2, 1]` is `False`. If the order of the result is not part of the promise, sort first (`sorted(result) == [1, 2]`) or compare as sets (`set(result) == {1, 2}`). A set comparison also forgets duplicates, so use it only when duplicates do not matter.

Lists and tuples are never equal: `[1, 2] == (1, 2)` is `False`. A function that is supposed to return a list but returns a tuple fails `== [1, 2]`. That is good, it is a difference the caller can notice.

### 8.3 Dictionaries: order does not matter

`{"a": 1, "b": 2} == {"b": 2, "a": 1}` is `True`. Dictionaries compare by keys and values, not by order. That makes them easy to test.

### 8.4 Strings: every character counts

Strings compare exactly, including case, spaces and the final newline. When a test fails on text, the `?` marker line from section 4.3 shows exactly where the characters differ. Typical hidden causes: a trailing space, `\n`, different quote characters. Use `repr` in your head: `'hi '` and `'hi'` look alike on screen.

### 8.5 True, False, None

Compare with the right operator:

| You want | Write | Why |
|---|---|---|
| a real `True` | `assert f(x) is True` | `assert f(x)` also passes for `1`, `"yes"`, `[0]` |
| a real `False` | `assert f(x) is False` | `assert not f(x)` also passes for `0`, `None`, `""` |
| `None` | `assert f(x) is None` | `None` is a single object; `is` is the right test |
| membership | `assert "a" in result` | clearer than `result.count("a") > 0` |

If the function is documented to return a truthy or falsy *value* (not a bool), plain `assert f(x)` is acceptable. If it is documented to return a bool, use `is True` / `is False`: the test then also guards the *type*.

### 8.6 Functions that change their argument

Some functions change the list they are given (`list.sort`, `append`) and return `None`. Test the effect, not the return value:

```python
# test_side.py
def add_item(cart, item):
    cart.append(item)


def test_add_item_changes_the_cart():
    cart = ["pen"]
    result = add_item(cart, "ink")
    assert result is None
    assert cart == ["pen", "ink"]
```
```text
$ python -m pytest -q
.                                                                        [100%]
1 passed in 0.01s
```

Also test the opposite: a function that should **not** change its argument must be checked by keeping a copy or a second list with the same contents and comparing after the call (see problem "chunk"). A function that destroys its input is a nasty bug that returns the right answer once.

### 8.7 Try it

**Predict the output.** Which of these asserts pass?

```python
import pytest

def test_a():  assert 0.1 * 3 == 0.3
def test_b():  assert 0.1 * 3 == pytest.approx(0.3)
def test_c():  assert [1, 2, 3] == (1, 2, 3)
def test_d():  assert {"x": 1, "y": 2} == {"y": 2, "x": 1}
def test_e():  assert sorted([3, 1, 2]) == [1, 2, 3]
```

<details><summary>Answer</summary>

`test_a` fails (`0.1 * 3` is `0.30000000000000004`). `test_b`, `test_d` and `test_e` pass. `test_c` fails: a list never equals a tuple. Summary: `2 failed, 3 passed`.

```text
$ python -m pytest -q --tb=no
F.F..                                                                    [100%]
=========================== short test summary info ============================
FAILED test_cmp.py::test_a - assert (0.1 * 3) == 0.3
FAILED test_cmp.py::test_c - assert [1, 2, 3] == (1, 2, 3)
2 failed, 3 passed in 0.01s
```

</details>

---

## 9. parametrize: many cases, one test

### 9.1 The copy-and-paste problem

Good testing means many cases. Look what that does to the file when you write each case as its own test:

```python
def test_grade_95():  assert grade(95) == "A"
def test_grade_90():  assert grade(90) == "A"
def test_grade_89():  assert grade(89) == "B"
def test_grade_75():  assert grade(75) == "B"
def test_grade_74():  assert grade(74) == "C"
```

The shape is the same every time: only the input and the expected value change. Copying the line means copying mistakes, and the file grows with each new case.

### 9.2 One test, a table of cases

`@pytest.mark.parametrize` takes the **names of the arguments**, then a **list of rows**. Pytest runs the test function **once per row** and reports each run as a separate test:

```python
# grading.py
def grade(marks):
    if marks >= 90:
        return "A"
    if marks >= 75:
        return "B"
    if marks >= 60:
        return "C"
    return "F"
```
```python
# test_grading.py
import pytest

from grading import grade


@pytest.mark.parametrize("marks, expected", [
    (95, "A"),
    (90, "A"),
    (89, "B"),
    (75, "B"),
    (74, "C"),
    (60, "C"),
    (59, "F"),
    (0, "F"),
])
def test_grade(marks, expected):
    assert grade(marks) == expected, f"grade({marks}) should be {expected!r}"
```
```text
$ python -m pytest -v --no-header
============================= test session starts ==============================
collecting ... collected 8 items

test_grading.py::test_grade[95-A] PASSED                                 [ 12%]
test_grading.py::test_grade[90-A] PASSED                                 [ 25%]
test_grading.py::test_grade[89-B] PASSED                                 [ 37%]
test_grading.py::test_grade[75-B] PASSED                                 [ 50%]
test_grading.py::test_grade[74-C] PASSED                                 [ 62%]
test_grading.py::test_grade[60-C] PASSED                                 [ 75%]
test_grading.py::test_grade[59-F] PASSED                                 [ 87%]
test_grading.py::test_grade[0-F] PASSED                                  [100%]

============================== 8 passed in 0.01s ===============================
```

Look at what you wrote and what you got. One function and one table became **eight** tests. Each has its own name made of the values: `test_grade[95-A]`, `test_grade[90-A]`, and so on. A failing row names itself in the report, so you see at once which border broke.

The pieces:

- `import pytest` at the top.
- `"marks, expected"`: a **string** with the argument names, separated by commas. They must match the test function's parameters exactly, in order.
- The list: one **tuple per row**, with one value per argument name.
- The test function takes those names as parameters and uses them normally.

This is the one case where a test function has parameters. They are filled in by pytest from the table, not by you.

### 9.3 A failing row

Change one expected value to be wrong and run it:

```python
# test_grading.py
import pytest

from grading import grade


@pytest.mark.parametrize("marks, expected", [
    (95, "A"),
    (90, "A"),
    (89, "B"),
    (75, "C"),
    (59, "F"),
])
def test_grade(marks, expected):
    assert grade(marks) == expected, f"grade({marks}) should be {expected!r}"
```
```text
$ python -m pytest -q --tb=short
...F.                                                                    [100%]
=================================== FAILURES ===================================
_______________________________ test_grade[75-C] _______________________________
test_grading.py:14: in test_grade
    assert grade(marks) == expected, f"grade({marks}) should be {expected!r}"
E   AssertionError: grade(75) should be 'C'
E   assert 'B' == 'C'
E
E     - C
E     + B
=========================== short test summary info ============================
FAILED test_grading.py::test_grade[75-C] - AssertionError: grade(75) should b...
1 failed, 4 passed in 0.01s
```

The four good rows pass; the `75` row is the only failure, and the id `test_grade[75-C]` and the message `grade(75) should be 'C'` both name it. (Here the table is wrong, not the function: 75 is a `B`.) With a single test that had five asserts, the first failure would have stopped the rest.

### 9.4 Naming rows with ids

The automatic ids are fine for numbers. For long values, pass `ids`:

```python
# test_ids.py
import pytest


@pytest.mark.parametrize("text, expected", [
    ("", 0),
    ("hello world", 2),
    ("  spaced   out  ", 2),
], ids=["empty", "two words", "extra spaces"])
def test_word_count(text, expected):
    assert len(text.split()) == expected
```
```text
$ python -m pytest -v --no-header
============================= test session starts ==============================
collecting ... collected 3 items

test_ids.py::test_word_count[empty] PASSED                               [ 33%]
test_ids.py::test_word_count[two words] PASSED                           [ 66%]
test_ids.py::test_word_count[extra spaces] PASSED                        [100%]

============================== 3 passed in 0.01s ===============================
```

Now the report line reads `test_word_count[extra spaces]`, which is easier to understand than a long string in brackets.

### 9.5 More than one parameter list

Stack two `parametrize` decorators and pytest runs **every combination**. This is useful for "this must hold for all of these inputs and all of these settings":

```python
# test_stack.py
import pytest


@pytest.mark.parametrize("x", [1, 2])
@pytest.mark.parametrize("y", ["a", "b"])
def test_pair(x, y):
    assert isinstance(y, str)
```
```text
$ python -m pytest -v --no-header
============================= test session starts ==============================
collecting ... collected 4 items

test_stack.py::test_pair[a-1] PASSED                                     [ 25%]
test_stack.py::test_pair[a-2] PASSED                                     [ 50%]
test_stack.py::test_pair[b-1] PASSED                                     [ 75%]
test_stack.py::test_pair[b-2] PASSED                                     [100%]

============================== 4 passed in 0.01s ===============================
```

Two times two is four tests. The bottom decorator's value comes first in the id, and it changes slowest. Do not stack many of them: 5 x 5 x 5 is 125 tests.

### 9.6 When to use parametrize, and when not

Use it when **the same check** runs on many inputs. Do not use it to hide very different checks in one table: if a row needs an `if` in the test body to know what to check, it should be its own test. Keep the table readable: one row per line, the interesting borders marked with a comment.

### 9.7 Parametrize with exceptions

The same idea works for error cases. Put the **bad inputs** in the table and use `pytest.raises` (next section) inside:

```python
@pytest.mark.parametrize("bad", [-1, 101, 1000])
def test_marks_out_of_range(bad):
    with pytest.raises(ValueError):
        grade(bad)
```

### 9.8 Try it

**Predict the output.** How many tests does pytest report, and what is the id of the last one?

```python
@pytest.mark.parametrize("a, b", [(1, 2), (3, 4), (5, 6)])
@pytest.mark.parametrize("op", ["+", "-"])
def test_ops(a, b, op):
    assert True
```

<details><summary>Answer</summary>

Two values for `op` times three rows is six tests. The id is built from the bottom decorator first (`op`), then the top one (`a-b`), and the bottom one changes slowest. So the ids run `test_ops[+-1-2]`, `test_ops[+-3-4]`, `test_ops[+-5-6]`, then the same three with `-` as the operator. The last id is `test_ops[--5-6]`: the first `-` is the operator, then the separator, then `5-6`.

```text
$ python -m pytest -v --no-header
============================= test session starts ==============================
collecting ... collected 6 items

test_ops.py::test_ops[+-1-2] PASSED                                      [ 16%]
test_ops.py::test_ops[+-3-4] PASSED                                      [ 33%]
test_ops.py::test_ops[+-5-6] PASSED                                      [ 50%]
test_ops.py::test_ops[--1-2] PASSED                                      [ 66%]
test_ops.py::test_ops[--3-4] PASSED                                      [ 83%]
test_ops.py::test_ops[--5-6] PASSED                                      [100%]

============================== 6 passed in 0.01s ===============================
```


</details>

---

## 10. Testing that exceptions are raised

A function that gets bad input should **raise an exception** (chapter 7). That is behaviour, and it needs a test: "when the input is bad, an error of this kind is raised, with this kind of message". The tool is `pytest.raises`.

### 10.1 The first version

```python
# bank.py
def withdraw(balance, amount):
    if amount <= 0:
        raise ValueError("amount must be positive")
    if amount > balance:
        raise ValueError("insufficient funds")
    return balance - amount
```
```python
# test_bank.py
import pytest

from bank import withdraw


def test_withdraw_normal():
    assert withdraw(100, 30) == 70


def test_withdraw_negative_amount_is_rejected():
    with pytest.raises(ValueError):
        withdraw(100, -5)
```
```text
$ python -m pytest -q
..                                                                       [100%]
2 passed in 0.01s
```

`with pytest.raises(ValueError):` opens a block. The test **passes** only if the code inside the block raises `ValueError` (or a child of it). If the block finishes without an exception, or raises a different one, the test **fails**.

### 10.2 It fails when nothing is raised

This is the crucial point. Suppose the function forgets its check:

```python
# bank.py
def withdraw(balance, amount):
    return balance - amount
```
```text
$ python -m pytest -q --tb=short
.F                                                                       [100%]
=================================== FAILURES ===================================
__________________ test_withdraw_negative_amount_is_rejected ___________________
test_bank.py:11: in test_withdraw_negative_amount_is_rejected
    with pytest.raises(ValueError):
         ^^^^^^^^^^^^^^^^^^^^^^^^^
E   Failed: DID NOT RAISE ValueError
=========================== short test summary info ============================
FAILED test_bank.py::test_withdraw_negative_amount_is_rejected - Failed: DID ...
1 failed, 1 passed in 0.01s
```

The report says `Failed: DID NOT RAISE ValueError`. Good: the test noticed that the error was not raised. Now see what happens when a **different** exception escapes. Here the function raises `TypeError` for the bad amount:

```python
# bank.py
def withdraw(balance, amount):
    if amount <= 0:
        raise TypeError("amount must be positive")
    return balance - amount
```
```text
$ python -m pytest -q --tb=short
.F                                                                       [100%]
=================================== FAILURES ===================================
__________________ test_withdraw_negative_amount_is_rejected ___________________
test_bank.py:12: in test_withdraw_negative_amount_is_rejected
    withdraw(100, -5)
bank.py:3: in withdraw
    raise TypeError("amount must be positive")
E   TypeError: amount must be positive
=========================== short test summary info ============================
FAILED test_bank.py::test_withdraw_negative_amount_is_rejected - TypeError: a...
1 failed, 1 passed in 0.01s
```

The `TypeError` is not a `ValueError`, so it passes through the `with` block and the test fails with the original error. The type matters, and the test pins it down.

### 10.3 Checking the message: match

A bug can hide in the **message**: the right type, but the wrong reason. Both of these raise `ValueError`:

```python
withdraw(100, -5)     # ValueError("amount must be positive")
withdraw(100, 500)    # ValueError("insufficient funds")
```

A test that only checks `ValueError` would accept a function that mixes the two up. `match=` adds a check on the message:

```python
# bank.py
def withdraw(balance, amount):
    if amount <= 0:
        raise ValueError("amount must be positive")
    if amount > balance:
        raise ValueError("insufficient funds")
    return balance - amount
```
```python
# test_bank.py
import pytest

from bank import withdraw


def test_negative_amount_is_rejected():
    with pytest.raises(ValueError, match="positive"):
        withdraw(100, -5)


def test_too_large_amount_is_rejected():
    with pytest.raises(ValueError, match="insufficient"):
        withdraw(100, 500)
```
```text
$ python -m pytest -q
..                                                                       [100%]
2 passed in 0.01s
```

`match="positive"` searches for `positive` anywhere in the message. If the text is not found, the test fails and shows what the message really was:

```python
# test_bank.py
import pytest

from bank import withdraw


def test_negative_amount_is_rejected():
    with pytest.raises(ValueError, match="insufficient"):
        withdraw(100, -5)
```
```text
$ python -m pytest -q --tb=short
F                                                                        [100%]
=================================== FAILURES ===================================
_______________________ test_negative_amount_is_rejected _______________________
test_bank.py:7: in test_negative_amount_is_rejected
    with pytest.raises(ValueError, match="insufficient"):
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   AssertionError: Regex pattern did not match.
E     Expected regex: 'insufficient'
E     Actual message: 'amount must be positive'
=========================== short test summary info ============================
FAILED test_bank.py::test_negative_amount_is_rejected - AssertionError: Regex...
1 failed in 0.01s
```

Choose a piece of the message that is **stable and meaningful**: a keyword, not the full sentence. If you match the exact sentence, every wording improvement breaks the test.

### 10.4 match is a regular expression

`match` is not a plain substring: it is a **regular expression**, a small pattern language. Most words behave as plain text. But these characters have a special meaning: `.` (any character), `+`, `*`, `?`, `(`, `)`, `[`, `]`, `|`, `^`, `$`. So `match="a+b"` does **not** look for the text `a+b`.

```python
# test_regex.py
import pytest


def explode():
    raise ValueError("bad value: a+b")


def test_plus_is_special():
    with pytest.raises(ValueError, match="a+b"):
        explode()
```
```text
$ python -m pytest -q --tb=short
F                                                                        [100%]
=================================== FAILURES ===================================
_____________________________ test_plus_is_special _____________________________
test_regex.py:9: in test_plus_is_special
    with pytest.raises(ValueError, match="a+b"):
         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   AssertionError: Regex pattern did not match.
E     Expected regex: 'a+b'
E     Actual message: 'bad value: a+b'
=========================== short test summary info ============================
FAILED test_regex.py::test_plus_is_special - AssertionError: Regex pattern di...
1 failed in 0.01s
```

The pattern `a+b` means "one or more a, followed by b": it looks for `ab`, `aab`, and so on. The message has `a+b`, with a plus sign between, so there is no match. To match literal text, escape the special characters with `re.escape` (the function `escape` from `re`, Python's regular-expression module, which you only need for this), or with a backslash in a raw string:

```python
# test_regex.py
import re

import pytest


def explode():
    raise ValueError("bad value: a+b")


def test_plus_is_matched_literally():
    with pytest.raises(ValueError, match=re.escape("a+b")):
        explode()


def test_or_with_a_raw_string():
    with pytest.raises(ValueError, match=r"a\+b"):
        explode()
```
```text
$ python -m pytest -q
..                                                                       [100%]
2 passed in 0.01s
```

For ordinary keywords you will not need any of this. Just remember that `match` is a pattern, and that `.` and `+` in your text can surprise you.

### 10.5 Looking at the exception object

If you want to check more than a message, capture the exception with `as`:

```python
# test_info.py
import pytest


def parse_age(text):
    if not text.isdigit():
        raise ValueError("age must be digits, got " + repr(text))
    return int(text)


def test_error_message_contains_the_bad_text():
    with pytest.raises(ValueError) as info:
        parse_age("x1")
    assert "'x1'" in str(info.value)
    assert info.type is ValueError
```
```text
$ python -m pytest -q
.                                                                        [100%]
1 passed in 0.01s
```

`info.value` is the exception object itself (what you called `e` in `except ... as e`), `info.type` its class. Note that the two `assert` lines are **after** the `with` block, not inside it.

### 10.6 Only one call inside the block

Put **only the one call that should raise** inside `with pytest.raises`. When the first line raises, Python leaves the block and the lines after it **never run**. When you put two calls inside, you are testing only the first, and the second might not even be reached:

```python
# test_two.py
import pytest


def to_int(text):
    return int(text)


def test_two_bad_inputs():
    with pytest.raises(ValueError):
        to_int("abc")
        to_int(42.5)      # never runs, and would not raise anyway
```
```text
$ python -m pytest -q
.                                                                        [100%]
1 passed in 0.01s
```

This test passes and gives false confidence. Make one test per error case, or use a `parametrize` table (section 9.7).

### 10.7 Too-broad: pytest.raises(Exception)

`pytest.raises(Exception)` passes for **any** error: a `NameError` from a typo, a `TypeError` from a mistake in your own code. A test that cannot tell the expected error from a crash is nearly worthless. Name the specific type you expect, and add `match` when the message matters. It is the same rule as chapter 7: catch exactly the exception you mean.

### 10.8 Testing that something does NOT raise

For the normal case there is nothing special. Just call the function. If it raises, the test fails by itself with the traceback. Do not wrap the call in `try/except` to "make sure": that hides the very information you want.

### 10.9 A pattern for error cases

For every `raise` in the function, write one test. A function with three `raise` lines needs three `pytest.raises` tests, and each should fail if you delete that one `if`. If you can delete a `raise` and the suite stays green, an error path is untested.

### 10.10 Try it

**Predict the output.** For each test, say whether it passes.

```python
import pytest

def check(n):
    if n < 0:
        raise ValueError("negative: " + str(n))
    return n

def test_a():
    with pytest.raises(ValueError):
        check(-1)

def test_b():
    with pytest.raises(ValueError):
        check(1)

def test_c():
    with pytest.raises(ValueError, match="negative"):
        check(-5)

def test_d():
    with pytest.raises(TypeError):
        check(-1)

def test_e():
    with pytest.raises(ValueError, match="^negative: -5$"):
        check(-5)

def test_f():
    with pytest.raises(ValueError, match="-5"):
        check(-5)
```

<details><summary>Answer</summary>

`test_a` passes. `test_b` fails (nothing raised). `test_c` passes. `test_d` fails (a `ValueError` is raised, not a `TypeError`). `test_e` passes: `^` and `$` mean "start" and "end" of the text, and the message is exactly `negative: -5`. `test_f` passes. Summary: `2 failed, 4 passed`.

```text
$ python -m pytest -v --no-header --tb=no
============================= test session starts ==============================
collecting ... collected 6 items

test_check.py::test_a PASSED                                             [ 16%]
test_check.py::test_b FAILED                                             [ 33%]
test_check.py::test_c PASSED                                             [ 50%]
test_check.py::test_d FAILED                                             [ 66%]
test_check.py::test_e PASSED                                             [ 83%]
test_check.py::test_f PASSED                                             [100%]

=========================== short test summary info ============================
FAILED test_check.py::test_b - Failed: DID NOT RAISE ValueError
FAILED test_check.py::test_d - ValueError: negative: -1
========================= 2 failed, 4 passed in 0.01s ==========================
```

</details>

---

## 11. Boundary cases and choosing useful tests

You cannot test every input. There are infinitely many integers. The skill is to pick a **small** set of inputs that would catch the bugs real programmers make. This section gives you a method.

### 11.1 Equivalence classes: group the inputs

Most inputs behave the same way as their neighbours. For `ticket_price(age)`, ages 20, 25 and 40 all take the same path through the function and give the same answer. Testing all three adds nothing. Divide the possible inputs into **classes** that the function treats alike, and test **one value from each class**.

For `ticket_price` (0 to 4 free, 5 to 12 child, 13 to 59 adult, 60 and over senior, negative is an error) the classes are:

| class | example |
|---|---|
| negative (error) | -1 |
| babies | 2 |
| children | 8 |
| adults | 30 |
| seniors | 70 |

Five tests, five paths. This alone catches "forgot a whole range" or "returned the wrong price for a range". But it does not catch the bugs that come next.

### 11.2 Boundaries: where bugs live

Programmers make **off-by-one** mistakes: `<` instead of `<=`, `range(n)` instead of `range(n + 1)`, `>` instead of `>=`. These bugs only change the answer **at the border** between two classes. Every other input in the class gets the right result.

So for every border, test the **last value of one class and the first value of the next**:

| border | last of the lower class | first of the upper class |
|---|---|---|
| free / child | 4 | 5 |
| child / adult | 12 | 13 |
| adult / senior | 59 | 60 |
| error / free | -1 | 0 |

Watch it happen. This is a buggy `ticket_price` where the child range stops one year early (`age < 12` instead of `age < 13`), and a "typical value" suite:

```python
# tickets.py
def ticket_price(age):
    if age < 0:
        raise ValueError("age cannot be negative")
    if age < 5:
        return 0
    if age < 12:
        return 50
    if age < 60:
        return 100
    return 60
```
```python
# test_tickets.py
import pytest

from tickets import ticket_price


def test_typical_ages():
    assert ticket_price(2) == 0
    assert ticket_price(8) == 50
    assert ticket_price(30) == 100
    assert ticket_price(70) == 60
```
```text
$ python -m pytest -q
.                                                                        [100%]
1 passed in 0.01s
```

All green, but the code is wrong: a 12-year-old pays the adult price. Add the border values:

```python
# test_tickets.py
import pytest

from tickets import ticket_price


@pytest.mark.parametrize("age, price", [
    (0, 0), (4, 0),       # free
    (5, 50), (12, 50),    # child
    (13, 100), (59, 100), # adult
    (60, 60),             # senior
])
def test_borders(age, price):
    assert ticket_price(age) == price, f"age {age} should pay {price}"


def test_negative_age_is_an_error():
    with pytest.raises(ValueError):
        ticket_price(-1)
```
```text
$ python -m pytest -q --tb=short
...F....                                                                 [100%]
=================================== FAILURES ===================================
_____________________________ test_borders[12-50] ______________________________
test_tickets.py:13: in test_borders
    assert ticket_price(age) == price, f"age {age} should pay {price}"
E   AssertionError: age 12 should pay 50
E   assert 100 == 50
E    +  where 100 = ticket_price(12)
=========================== short test summary info ============================
FAILED test_tickets.py::test_borders[12-50] - AssertionError: age 12 should p...
1 failed, 7 passed in 0.01s
```

The failing row is `(12, 50)`: exactly the bug. The typical values 2, 8, 30 and 70 could never have seen it.

### 11.3 The usual suspects: a checklist

Every time you test a function, walk through this list and ask "does this apply?".

**For numbers**

- zero (the border between positive and negative; often special)
- one (smallest positive whole number; a loop that runs once)
- negative numbers
- the exact border values of any rule in the problem (`>= 18` means 17 and 18)
- a big number (checks for overflow-like assumptions; in Python, mostly for speed)
- a float if floats are allowed (`0.5`, which `int()` turns into 0)

**For strings**

- the empty string `""`
- a one-character string
- spaces only, and spaces at the start or end
- upper and lower case mixed
- characters that are not letters: digits, punctuation, accents
- a string that is **almost** right (`"abca"` for a palindrome check)

**For lists, tuples and dicts**

- empty
- exactly one item
- two items (the smallest list where order matters)
- many items, including duplicates
- the target item first, last, in the middle, and absent
- an input that is already sorted, reversed, all equal
- does the function **change its input** (it should not, unless documented)?

**For all functions**

- the **error cases**: each `raise` in the function needs a test
- does it return the **right type** (list vs tuple, int vs float, `None`)?
- would the answer be different if the arguments were swapped? (If `f(a, b)` and `f(b, a)` give the same result in your tests, a bug that swaps them is invisible. Use different values.)

### 11.4 Make the test values different

A common blind spot: choosing inputs where wrong code and right code agree **by accident**. Examples:

- `clamp(5, 5, 5)`: low, high and x are all equal. Swapping low and high has no effect.
- `power(2, 2)`: `2 ** 2` and `2 * 2` are both 4. The test cannot tell a power from a product. Use `power(2, 3)`.
- `middle([1, 2, 3])` of a sorted list: a function that forgot to sort passes. Use `[3, 1, 2]`.
- A list of three items for "second largest": the second smallest and the second largest are the same item (section 5.2).

Choose values that are distinct, not symmetric, and not special numbers like 0, 1 and 2 *unless* you are testing exactly those.

### 11.5 How many tests is enough?

There is no fixed number. Use the questions:

1. Is every **path** through the function covered (every `if` branch, every loop with zero, one and many iterations, every `raise`)?
2. Is every **border** tested on both sides?
3. Could a **plausible bug** survive? (Section 13.)

For a small function that is 5 to 10 tests, many of them one-line rows in a `parametrize` table. A test for each of the "typical" inputs beyond the first is wasted effort. Eight tests that all use multiples of 4 for a leap-year function prove as much as one: they are *redundant*.

### 11.6 Try it

**Question.** A function `is_valid_pin(text)` returns `True` for exactly four digits (`"1234"`) and `False` otherwise. List the test inputs you would choose, with the reason for each.

<details><summary>Answer</summary>

A good list:

- `"1234"` → `True`: the normal valid case.
- `"123"` → `False` and `"12345"` → `False`: the length borders, one short and one long.
- `""` → `False`: the empty case.
- `"12a4"` → `False`: right length but not all digits (kills a check that looks only at the length).
- `"abcd"` → `False`: right length, no digits at all.
- `"0000"` → `True`: digits starting with 0 (a function that converts to `int` loses the zeros).
- `" 123"` → `False`: right length counting the space, but a space is not a digit.
- `"12 4"` → `False`: a space in the middle.

Nine inputs, each for a different plausible bug. Adding `"5678"`, `"9999"` and `"1111"` would add no new information.

</details>

---

## 12. Making code easy to test

Some code is hard to test, and the reason is nearly always the same: it does too much at once. It reads from the keyboard, computes, and prints, all in one function.

### 12.1 The hard version

```python
# greeter.py
def greet():
    name = input("Your name: ")
    print("Hello, " + name.strip().title() + "!")
```

To test this you would have to type into the keyboard while the test runs, and read what was printed. A test that calls `greet()` under pytest does not wait for typing: pytest has no keyboard connected, so `input()` fails.

```python
# test_greeter.py
from greeter import greet


def test_greet():
    greet()
```
```text
$ python -m pytest -q --tb=line
F                                                                        [100%]
=================================== FAILURES ===================================
E   OSError: pytest: reading from stdin while output is captured!  Consider using `-s`.
----------------------------- Captured stdout call -----------------------------
Your name:
/.../site-packages/_pytest/capture.py:229: OSError: pytest: reading from stdin while output is captured!  Consider using `-s`.
=========================== short test summary info ============================
FAILED test_greeter.py::test_greet - OSError: pytest: reading from stdin whil...
1 failed in 0.01s
```

The test crashed with an error about reading from stdin while it was being captured. That is the design telling you something.

### 12.2 Separate the logic from the input and output

Move the **decision** into a function that takes values and **returns** a result. Keep the `input` and `print` in a thin outer layer that is not worth testing:

```python
# greeter.py
def make_greeting(name):
    return "Hello, " + name.strip().title() + "!"


def main():
    name = input("Your name: ")
    print(make_greeting(name))


if __name__ == "__main__":
    main()
```
```python
# test_greeter.py
import pytest

from greeter import make_greeting


@pytest.mark.parametrize("name, expected", [
    ("asha", "Hello, Asha!"),
    ("  ravi kumar ", "Hello, Ravi Kumar!"),
    ("", "Hello, !"),
])
def test_make_greeting(name, expected):
    assert make_greeting(name) == expected
```
```text
$ python -m pytest -q
...                                                                      [100%]
3 passed in 0.01s
```

`make_greeting` is a **pure function**: the same inputs always give the same output, it reads nothing from outside, and it changes nothing outside. Pure functions are the easiest code to test, which is one more reason chapter 6 told you to prefer returning to printing.

The tiny `main` has no logic left to get wrong: it is checked by running the program once. The `if __name__ == "__main__":` line (chapter 6) means importing the module in a test does not start the program.

### 12.3 Pass the changing things in

Code that reads the clock or a random number is different every run. Pass the value in:

```python
# (datetime is a module for dates, taught later; only the idea matters here)
# hard to test: the answer depends on today's date
def is_weekend():
    return datetime.date.today().weekday() >= 5

# easy to test: the date is an argument
def is_weekend(day):
    return day.weekday() >= 5
```

In the program you call `is_weekend(date.today())`; in the test you call it with fixed dates. The same trick works for randomness (pass the random number or the list to choose from) and for input (pass the text).

When printing *is* the job (a report), keep it in a thin layer and test the function that builds the **text**. (Pytest can also capture printed text with a helper called `capsys`, a *fixture*: a topic for a later module.)

---

## 13. Does the test really test anything? Thinking in bugs

A green test is only valuable if it **could have been red**. This section gives you the habit of checking.

### 13.1 Tests that cannot fail

Three kinds of test pass whatever the code does:

1. **No assert.** The test calls the function and checks nothing. It fails only if the code crashes.
2. **A tautology.** `assert total(prices) == total(prices)` compares a value with itself.
3. **An assert that never runs.** A tuple (`assert (x == 1, "msg")`), a test inside a never-executed `if`, or a loop over an empty list.

```python
# test_useless.py
def total(prices):
    return None          # completely wrong


def test_total_no_assert():
    total([1, 2, 3])


def test_total_tautology():
    assert total([1, 2, 3]) == total([1, 2, 3])


def test_total_tuple():
    assert (total([1, 2, 3]) == 6, "total of 1, 2, 3 is 6")


def test_total_empty_loop():
    for case in []:
        assert total(case) == sum(case)
```
```text
$ python -m pytest -q 2>&1
....                                                                     [100%]
=============================== warnings summary ===============================
test_useless.py:14
  /home/you/project/test_useless.py:14: PytestAssertRewriteWarning: assertion is always true, perhaps remove parentheses?
    assert (total([1, 2, 3]) == 6, "total of 1, 2, 3 is 6")

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
4 passed, 1 warning in 0.01s
```

Four tests, four passes, for a function that returns `None`. (The warning at the bottom is pytest noticing the tuple assert; Python itself also prints a `SyntaxWarning` for it when it compiles the file.) A suite of tests like these is worse than none, because it looks like safety.

### 13.2 The "break it on purpose" check

After you write a test, make the **code** wrong in a small way and see if the test goes red:

- change `<` to `<=` (or the other way round)
- change `+` to `-`
- remove one `if` branch
- return a constant (`0`, `[]`, `None`)
- remove the `raise`
- use the first item instead of the last

If you can make that change and no test fails, your suite has a hole, exactly at that bug. That is what the "write the tests" problems in this module check with their buggy copies. It is also a real technique that large projects automate; it is called mutation testing.

You do not need to do it for every line. Do it on the places where a mistake is **likely**: the borders, the loops, the error branches.

### 13.3 Test behaviour, not the way the code is written

A test should check **what** the function promises, not **how** it does it. A test that looks at internal variables or calls private helper steps breaks every time you tidy the code, even when the behaviour is the same. The only things your tests should rely on are the function's arguments, its return value, its documented effects and the exceptions it raises. That keeps your tests valid while you refactor.

### 13.4 Try it

**Question.** Describe a small bug that this test suite does **not** catch, and the test you would add.

```python
def longest_word(text):
    words = text.split()
    best = words[0]
    for w in words:
        if len(w) > len(best):
            best = w
    return best

def test_longest_word():
    assert longest_word("a bb ccc") == "ccc"
```

<details><summary>Answer</summary>

Several bugs survive. (1) A version that returns `words[-1]` passes, because the longest word is last: use a test where the longest word is first or in the middle, `"aaa b cc"`. (2) A version with `>=` instead of `>` also passes: the tie rule is untested; decide what happens for `"ab cd"` (this code keeps the **first**) and test it. (3) The empty text crashes with `IndexError` in `words[0]`: decide whether that should raise a clear `ValueError` and write the `pytest.raises` test. Every test should be there because some bug would otherwise be invisible.

</details>

---

## 14. Test-driven development (TDD)

So far you wrote the code first, then the tests. **Test-driven development** reverses the order: write a failing test, then the code that makes it pass.

### 14.1 The loop: red, green, refactor

1. **Red.** Write **one** small test for a behaviour that does not exist yet. Run it. It must **fail**, for the reason you expect.
2. **Green.** Write the **smallest** amount of code that makes it pass. Do not write code the tests do not ask for.
3. **Refactor.** Tidy the code (names, duplication) while keeping all tests green.
4. Repeat with the next small behaviour.

The colours come from the test runner: red for failing, green for passing.

### 14.2 A worked example: initials

We want `initials("Ada Lovelace")` to give `"A.L."`. We build it in small steps. First the test, and no code at all:

```python
# test_names.py
from names import initials


def test_two_words():
    assert initials("Ada Lovelace") == "A.L."
```
```text
$ python -m pytest -q --tb=short

==================================== ERRORS ====================================
________________________ ERROR collecting test_names.py ________________________
ImportError while importing test module '/home/you/project/test_names.py'.
Hint: make sure your test modules/packages have valid Python names.
Traceback:
/usr/lib/python3/importlib/__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
test_names.py:1: in <module>
    from names import initials
E   ModuleNotFoundError: No module named 'names'
=========================== short test summary info ============================
ERROR test_names.py
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
1 error in 0.01s
```

**Red**, in the most basic way: `names.py` does not exist, so the file cannot even be imported (an *error during collection*). Create the smallest thing that gets us past this:

```python
# names.py
def initials(full_name):
    pass
```
```text
$ python -m pytest -q --tb=short
F                                                                        [100%]
=================================== FAILURES ===================================
________________________________ test_two_words ________________________________
test_names.py:5: in test_two_words
    assert initials("Ada Lovelace") == "A.L."
E   AssertionError: assert None == 'A.L.'
E    +  where None = initials('Ada Lovelace')
=========================== short test summary info ============================
FAILED test_names.py::test_two_words - AssertionError: assert None == 'A.L.'
1 failed in 0.01s
```

Still red, but now for the **right reason**: the function exists and gives `None`. This failure is what we want to see: the test can fail. Now the simplest code that passes. We do not need loops yet; we only have one example to satisfy:

```python
# names.py
def initials(full_name):
    return "A.L."
```
```text
$ python -m pytest -q
.                                                                        [100%]
1 passed in 0.01s
```

**Green.** Yes, the function returns a constant. That is legal in TDD, and it is not silly: it is a proof that the test passes for a right answer. A single example is not enough information to know the rule. A second test forces the real code:

```python
# test_names.py
from names import initials


def test_two_words():
    assert initials("Ada Lovelace") == "A.L."


def test_three_words():
    assert initials("Grace Brewster Hopper") == "G.B.H."
```
```text
$ python -m pytest -q --tb=short
.F                                                                       [100%]
=================================== FAILURES ===================================
_______________________________ test_three_words _______________________________
test_names.py:9: in test_three_words
    assert initials("Grace Brewster Hopper") == "G.B.H."
E   AssertionError: assert 'A.L.' == 'G.B.H.'
E
E     - G.B.H.
E     + A.L.
=========================== short test summary info ============================
FAILED test_names.py::test_three_words - AssertionError: assert 'A.L.' == 'G....
1 failed, 1 passed in 0.01s
```

**Red** again, so now we need the rule. Write it:

```python
# names.py
def initials(full_name):
    result = ""
    for word in full_name.split():
        result += word[0].upper() + "."
    return result
```
```text
$ python -m pytest -q
..                                                                       [100%]
2 passed in 0.01s
```

**Green.** Next small behaviour: lower-case input and extra spaces. First the tests, which already pass for these (a good sign: the code is more general than the examples), then an edge that does **not**:

```python
# test_names.py
import pytest

from names import initials


def test_two_words():
    assert initials("Ada Lovelace") == "A.L."


def test_three_words():
    assert initials("Grace Brewster Hopper") == "G.B.H."


def test_lower_case_and_extra_spaces():
    assert initials("  ada   lovelace ") == "A.L."


def test_empty_name_gives_empty_text():
    assert initials("") == ""


def test_one_word():
    assert initials("Plato") == "P."
```
```text
$ python -m pytest -q
.....                                                                    [100%]
5 passed in 0.01s
```

All pass already. Which means these three tests do not drive any new code. In TDD that is information: they are **characterisation**, not discovery. Keep them as protection against regressions, but notice that the interesting question is something else: what should `initials("Jean-Luc Picard")` do? A *decision* about the requirement, written down as a test **before** the code is touched:

```python
# test_names.py
from names import initials


def test_two_words():
    assert initials("Ada Lovelace") == "A.L."


def test_three_words():
    assert initials("Grace Brewster Hopper") == "G.B.H."


def test_lower_case_and_extra_spaces():
    assert initials("  ada   lovelace ") == "A.L."


def test_empty_name_gives_empty_text():
    assert initials("") == ""


def test_one_word():
    assert initials("Plato") == "P."


def test_hyphenated_first_name_keeps_both_parts():
    assert initials("Jean-Luc Picard") == "J.L.P."
```
```text
$ python -m pytest -q --tb=short
.....F                                                                   [100%]
=================================== FAILURES ===================================
_________________ test_hyphenated_first_name_keeps_both_parts __________________
test_names.py:25: in test_hyphenated_first_name_keeps_both_parts
    assert initials("Jean-Luc Picard") == "J.L.P."
E   AssertionError: assert 'J.P.' == 'J.L.P.'
E
E     - J.L.P.
E     ?  --
E     + J.P.
=========================== short test summary info ============================
FAILED test_names.py::test_hyphenated_first_name_keeps_both_parts - Assertion...
1 failed, 5 passed in 0.01s
```

**Red**: the code gives `J.P.`. Now the code is forced to change, and we choose how: split on spaces **and** hyphens.

```python
# names.py
def initials(full_name):
    result = ""
    for word in full_name.replace("-", " ").split():
        result += word[0].upper() + "."
    return result
```
```text
$ python -m pytest -q
......                                                                   [100%]
6 passed in 0.01s
```

**Green**, with all six tests. Refactoring would be next (here the code is already tidy), and run the whole suite once more to see nothing broke.

### 14.3 Why do it this way?

- **The test fails first, so you know it can fail.** A test you write after the code might pass for a bad reason; you never saw it red.
- **The tests are written from the requirement**, not from the code, so they are a real specification. (Tests copied from the code's output only agree with the code, section 5.2.)
- **You only write code that something needs.** The program does not grow features nobody asked for.
- **The design improves.** Writing the call first makes you choose names and arguments from the user's point of view, and makes you build functions that are easy to test (section 12).
- **Small steps give fast feedback.** When a test turns red, the cause is in the few lines you just wrote.

### 14.4 The honest limits

- It is slower at the start and demands that you know what the function should do. When you do not yet understand the problem, you may need an experiment first: write a throw-away script to learn, then start again with tests.
- Not every code is worth TDD: a one-off script, or code whose result is a picture or a sound.
- Passing tests do not prove correctness (section 1.5).
- Tests written first can still be wrong; you check them by hand arithmetic.

### 14.5 TDD for bugs: reproduce first

TDD is also the best way to fix bugs. When someone reports a bug:

1. Write a test that **reproduces** it, using the input from the report. Run it: it must fail (red). Now you know the test sees the bug.
2. Fix the code until it is green.
3. Keep the test. This is now a **regression test**: the bug cannot come back unnoticed.

If you fix the code first and write the test after, you never saw the test fail, so you never proved it can catch the bug.

### 14.6 In this module

Many problems in this module are written TDD-style: `test_solution.py` is the specification, `solution.py` is empty or wrong, and you work red, green, refactor. Read the tests in order: the first failing one gives the next step. You do not need to understand the whole function before you start: you need to understand **one failing test**.

### 14.7 Try it

**Predict the output.** You write this test first and have no code yet except the stub. What does pytest print on the last line?

```python
# names.py
def initials(full_name):
    pass

# test_names.py
def test_initials():
    assert initials("Ada Lovelace") == "A.L."
```

<details><summary>Answer</summary>

`1 failed`. The stub returns `None`, and the report line reads `assert None == 'A.L.'`. This is **red for the right reason**: the test ran and compared real values.

```text
$ python -m pytest -q --tb=no
F                                                                        [100%]
=========================== short test summary info ============================
FAILED test_names.py::test_initials - AssertionError: assert None == 'A.L.'
1 failed in 0.01s
```

</details>

---

## 15. Common traps

A checklist of the mistakes that cost beginners the most time. Most have appeared already; here they are in one place.

1. **A test that never runs.** The name does not start with `test`, the file does not match `test_*.py`, or two tests share a name and the first is replaced. Use `-v` to see the list of tests that really ran.
2. **A test that never fails.** No assert; a tautology; `assert (cond, "msg")` with parentheses; an assert inside a loop over an empty list.
3. **Copying the code's output into the expected value.** The test then agrees with the code forever, even when the code is wrong. Work out expected values by hand.
4. **Testing only the typical case.** Add borders, empty input and errors (section 11).
5. **Comparing floats with `==`.** Use `pytest.approx` (section 8.1).
6. **Two behaviours in one test, or many asserts that hide each other.** When the first assert fails, the rest never run.
7. **Tests that depend on each other**, or on shared module-level variables. Build the data inside each test (section 7.3).
8. **`pytest.raises` with too much inside**, or with `Exception`, or without `match` when the message matters (section 10).
9. **Parameters on a test function that are not from `parametrize`.** Pytest treats parameter names as requests for *fixtures*. See the next trap output.
10. **Tests that wait for typing.** Code with `input()` inside cannot be tested; separate the logic (section 12).
11. **A wrong expected value.** When a test fails, check by hand who is wrong before changing the code (section 5).
12. **Never running the tests.** Run them after every change, so that a red test points at what you just did.

Trap 9 in action:

```python
# test_param.py
def test_square(n):
    assert n * n == 16
```
```text
$ python -m pytest -q --tb=short
E                                                                        [100%]
==================================== ERRORS ====================================
________________________ ERROR at setup of test_square _________________________
file /home/you/project/test_param.py, line 1
  def test_square(n):
E       fixture 'n' not found
>       available fixtures: cache, capfd, capfdbinary, caplog, capsys, capsysbinary, capteesys, doctest_namespace, monkeypatch, pytestconfig, record_property, record_testsuite_property, record_xml_attribute, recwarn, subtests, tmp_path, tmp_path_factory, tmpdir, tmpdir_factory
>       use 'pytest --fixtures [testpath]' for help on them.

/home/you/project/test_param.py:1
=========================== short test summary info ============================
ERROR test_param.py::test_square
1 error in 0.01s
```

The report says `fixture 'n' not found`. Pytest tried to find a fixture called `n` and could not. Use `parametrize` when the test needs values, or write the value inside the test. The outcome is an `ERROR`, not a `FAILED`: the test never started.

And the empty-loop trap:

```python
# test_loop.py
def double(n):
    return n * 3        # wrong!


def test_double_many():
    cases = []                       # forgot to fill the list
    for n, expected in cases:
        assert double(n) == expected
```
```text
$ python -m pytest -q --tb=short
.                                                                        [100%]
1 passed in 0.01s
```

Green, for a function that triples instead of doubling. The loop runs zero times. With `parametrize`, an empty table is reported as a skipped test, which at least shows up in the summary:

```python
# test_empty_table.py
import pytest


@pytest.mark.parametrize("n, expected", [])
def test_double_many(n, expected):
    assert n * 2 == expected
```
```text
$ python -m pytest -q -rs
s                                                                        [100%]
=========================== short test summary info ============================
SKIPPED [1] test_empty_table.py:4: got empty parameter set for (n, expected)
1 skipped in 0.01s
```

---

## 16. Organising a test suite for a project

### 16.1 A simple layout

For a project with several modules:

```text
shop_project/
    shop.py
    inventory.py
    tests/
        test_shop.py
        test_inventory.py
```

One test file for each module, named `test_<module>.py`. Run everything from the project folder:

```text
$ python -m pytest
```

Pytest finds the `tests/` folder. Using `python -m pytest` (and not just `pytest`) adds the current folder to Python's import path, so `from shop import ...` works from inside `tests/`.

### 16.2 A routine you can keep

1. **Before you change code**, run the tests. Green means you start from a known good state.
2. **While you work**, run only the tests for the function you are changing (`-k name`), with `-x`.
3. **When you finish**, run everything.
4. **When you find a bug**, write the failing test first (section 14.5).
5. **When you add a feature**, write its tests with it.

### 16.3 What to test in your own earlier projects

The module project asks you to build a test suite for projects you wrote earlier (a to-do list, a quiz, a gradebook, the canteen or the bank). Choose the code that has the **logic**: functions that take values and return values (calculations, parsing, validation, searching, counting). Skip the thin `main()` that only calls `input` and `print`. If a function mixes logic and input/output, this is the moment to split it (section 12).

For each function you test, write down first (on paper or as comments):

- the normal case with an answer worked out by hand,
- the empty, one-item and many-item cases (if it takes a collection),
- every border in its rules,
- every `raise` and the message,
- two plausible bugs, and the test that would catch each.

Then run the "break it on purpose" check (section 13.2) on the three riskiest functions.

---

## Summary

- A **test** is a function that calls your code with a chosen input and `assert`s the expected output. It makes checking automatic, repeatable and fast.
- The biggest reason to test is **regression**: catching a change that breaks old behaviour.
- pytest finds tests by name: files `test_*.py`, functions starting with `test`. Run with `python -m pytest`; useful flags are `-q`, `-v`, `-x`, `-k`.
- Read a failure report from the bottom up: the summary line, the test name, the `>` line, the `E` lines (left is what the code gave, right is what you expected), then the line number.
- A red test means the code **and the test disagree**. Work out the answer by hand to decide who is wrong. Write an assert message that names the likely mistake.
- Use `pytest.approx` for floats, `is True` / `is None` for singletons, and remember that lists, dicts and strings compare exactly.
- `@pytest.mark.parametrize("a, expected", [...])` turns a table of cases into many tests, each reported on its own.
- `with pytest.raises(ValueError, match="word"):` checks both the type and the message. The test fails when nothing is raised. `match` is a regular expression. Keep one call inside the block.
- Choose tests with **equivalence classes** and **boundaries**: one value per class, both sides of every border, plus empty, one, errors.
- A good test has one reason to fail, a descriptive name, independent data, no logic, and an expected value from outside the code.
- Ask of every test: "if the code were wrong, would this fail?" Break the code on purpose to find out.
- **TDD**: red (a failing test), green (the least code), refactor. For bugs: reproduce first with a failing test.

## Learning outcomes

After this chapter and its problems you can

- write a pytest file for a function, covering normal, boundary and error cases;
- read a failing test report and locate the bug (or the wrong test);
- decide which cases are worth testing and why;
- use `parametrize` and `pytest.raises(..., match=...)` correctly;
- write a test before the code and use it to drive the implementation.

## Module project

**Test suite for your own earlier projects.** Pick **three** projects or modules you wrote earlier (for example from core.04 to core.07). For each:

1. Find the **pure functions** in it (values in, values out). Split any function that mixes logic with `input` and `print`.
2. Write a `tests/test_<name>.py` with at least **8 tests** per project: normal cases, borders, empty/one/many, and one `pytest.raises(..., match=...)` per error path. Use `parametrize` at least once per project.
3. Make every assert carry a message that names the likely mistake.
4. Run the "break it on purpose" check: introduce three different bugs into each project (one off-by-one, one missing branch, one wrong return value) and confirm that at least one test goes red each time. Put the code back afterwards. Note which bugs survived and add tests to catch them.
5. Fix any **real** bug your tests find, **test first**: reproduce it in a failing test, then fix it.

You are done when `python -m pytest` runs green on all three, every deliberate bug is caught, and you can explain, for each test file, why every test is there.

## Further reading

- The pytest documentation, "Get started" and "How to write and report assertions" (docs.pytest.org).
- The pytest documentation on `parametrize` and `pytest.raises`.
- *Test-Driven Development: By Example* by Kent Beck: the short, classic introduction to the red/green/refactor loop.
- "What is mutation testing?" The idea in section 13.2 appears in tools such as `mutmut`, which you can try after this module.
