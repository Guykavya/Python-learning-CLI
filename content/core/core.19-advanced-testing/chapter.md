# Chapter 19: Advanced testing

In chapter 8 you learned the heart of testing: write a small function that calls your code and uses `assert`, run `pytest`, read the failure report, and ask "who is wrong, the code or the test?" That is enough for a function like `clamp(x, lo, hi)`, which takes numbers and returns a number.

Real programs are not like that. Real code **reads files**, **asks what time it is**, **calls other services over the network**, **picks random numbers**, **prints reports**, and **depends on settings** hidden in environment variables. When you try to test such code with only the tools of chapter 8, you hit walls:

- "My test needs a sample file. Where do I put it, and who deletes it?"
- "My function says `Good morning` only before noon. How do I test the afternoon branch at 10 a.m.?"
- "My function sends an e-mail. I do not want to send a real e-mail every time I run the tests."
- "My test passes on Monday and fails on Tuesday, and I changed nothing."
- "I have 40 tests and 100% coverage, and a customer still found a bug."

This chapter has three learning outcomes, and every section serves one of them:

1. **Build test suites that stay clean, fast and independent**: with fixtures, scopes, `conftest.py`, parametrization and pytest's built-in helpers.
2. **Isolate code from the outside world** with test doubles, `unittest.mock`, injected clocks and fake clients, and know when this *helps* and when it only gives you a green tick that means nothing.
3. **Judge the quality of a test suite**: measure it with coverage, challenge it with property-based tests (`hypothesis`), hunt flaky tests, and ask the "mutation question": *if I put a bug here, would any test notice?*

**A note on how examples are shown.** Every block that has output was really run, with **Python 3.14**, `pytest 9.1`, `hypothesis 6.170` and `coverage 7.17` on Linux. Timing lines are removed from the pasted output, and folder names are shown as `/home/you/...`. Memory addresses such as `0x7f3c...` are machine-specific and are marked. The code works on Python 3.11 and newer. Where a result depends on the library *version* (for example the exact examples `hypothesis` chooses), the text says so.

**Setup.** You need `pytest`, `hypothesis` and `coverage`. They are already installed in this course's virtual environment. Every example is a small file (or two) in a folder; to follow along, make a scratch folder, save the files, and run `python -m pytest` inside it.

## Table of contents

1. [Why test more: risk, the pyramid, unit versus integration](#1-why-test-more-risk-the-pyramid-unit-versus-integration)
2. [Fixtures in depth](#2-fixtures-in-depth)
3. [Scopes: how long does a fixture live?](#3-scopes-how-long-does-a-fixture-live)
4. [`conftest.py`: sharing fixtures](#4-conftestpy-sharing-fixtures)
5. [Parametrization and markers](#5-parametrization-and-markers)
6. [Built-in fixtures: `tmp_path`, `capsys`, `monkeypatch`, `caplog`](#6-built-in-fixtures-tmp_path-capsys-monkeypatch-caplog)
7. [Test doubles and the best seam: dependency injection](#7-test-doubles-and-the-best-seam-dependency-injection)
8. [`unittest.mock`](#8-unittestmock)
9. [When mocking hurts](#9-when-mocking-hurts)
10. [Testing time, randomness, files and network](#10-testing-time-randomness-files-and-network)
11. [Coverage](#11-coverage)
12. [Property-based testing with hypothesis](#12-property-based-testing-with-hypothesis)
13. [Flaky tests](#13-flaky-tests)
14. [Integration and end-to-end tests](#14-integration-and-end-to-end-tests)
15. [Project walkthrough: a suite for a buggy codebase](#15-project-walkthrough-a-suite-for-a-buggy-codebase)
16. [Common traps and summary](#16-common-traps-and-summary)

## 1. Why test more: risk, the pyramid, unit versus integration

### 1.1 Tests are about risk, not about numbers

Nobody tests for the joy of it. A test is **insurance**: it costs time now, and it pays out when a change breaks something you would otherwise find late, in front of a user. So the first question is never "how many tests?" but "**where would a bug hurt most, and which test would catch it cheaply?**"

Think of two functions in a shop program:

- `slugify(title)` turns "Hello World" into "hello-world". If it is wrong, one URL looks odd.
- `charge_card(order)` takes money. If it is wrong, a customer pays twice.

Both deserve tests, but `charge_card` deserves more, and different ones: tests for refunds, for network failure in the middle, for the same order sent twice. A good tester spends effort like a good doctor spends attention: more where the danger is.

Tests also have a **cost**. Each test must be written, run, read when it fails, and updated when the code changes on purpose. A test that fails for no good reason (a *flaky* test, section 13) or that must be rewritten after every harmless refactor (a *brittle* test, section 9) costs more than it gives. This chapter is about getting the insurance without the cost.

### 1.2 The test pyramid

Tests come in sizes. The classic picture is a pyramid:

```text
          /\
         /  \      end-to-end: the whole program, as a user uses it
        /----\     few, slow, catch "the pieces do not fit together"
       /      \
      /        \   integration: a few real parts working together
     /----------\  some, medium speed
    /            \
   /              \ unit: one function or class, everything else controlled
  /________________\ many, very fast, point at the exact broken line
```

| Level | What runs for real | Typical speed | When it fails, you learn... |
|---|---|---|---|
| **Unit** | one function or class; its neighbours are simple or replaced | thousandths of a second | exactly which function is wrong |
| **Integration** | several real parts: code + file system, code + database, two modules | a few hundredths of a second | the parts disagree about something |
| **End-to-end (e2e)** | the whole program, started like a user would | tenths of a second to minutes | something is wrong *somewhere* |

The pyramid is wide at the bottom on purpose. Unit tests are cheap and precise, so you want many. End-to-end tests are expensive and vague ("the program printed the wrong thing, but where is the bug?"), so you want only a few, to prove that the pieces fit together. A program with a hundred end-to-end tests and no unit tests is slow to test and hard to debug; people call this the "ice-cream cone" and it is a classic mistake.

### 1.3 What is a "unit"?

There is no official size. A unit can be a function, a class, or a small group of classes that always work together. A practical test: *"When this test fails, do I immediately know where to look?"* If yes, it is unit-sized.

The word **isolated** matters too. A unit test of `greeting()` that reads the real clock is not isolated: it can pass in the morning and fail in the afternoon. Much of this chapter (sections 6 to 10) is about isolating code from the clock, the disk, the network and the random number generator, so that a test result depends only on the code.

#### Try it 1.1

Say whether each test is best written as unit, integration or end-to-end, and why.

1. `is_leap_year(2100)` returns `False`.
2. `save_report(rows, path)` writes a CSV file and `load_report(path)` reads it back to the same rows.
3. You run `python tally.py data.csv` and check what the whole program prints.
4. A `Cart.total()` method adds up prices, with no other class involved.

<details><summary>Answer</summary>

1. Unit. One pure function, no outside world.
2. Integration. It uses the real file system and two functions working together. (It still runs fast, thanks to `tmp_path` from section 6.)
3. End-to-end. The whole program runs, started as a user would start it (section 14).
4. Unit. One class, no collaborators.

</details>

## 2. Fixtures in depth

### 2.1 The problem fixtures solve

Many tests need the same starting point: a list with three numbers, an empty shopping cart, a logged-in user, a temporary folder with a sample file. Without help you repeat the setup lines at the top of every test:

```python
def test_sorted():
    data = [3, 1, 2]          # setup, copy-pasted
    assert sorted(data) == [1, 2, 3]

def test_len():
    data = [3, 1, 2]          # setup, copy-pasted again
    assert len(data) == 3
```

Copy-paste is a bug factory: when the setup changes, you must find every copy. And some setups need **cleanup**: close the database, delete the file. Forgetting cleanup in one test leaves a mess for the next one.

A **fixture** is a function that prepares something a test needs, and pytest **injects** it. You mark the function with `@pytest.fixture`. A test asks for it by writing the fixture's name as a **parameter**.

```python
import pytest


@pytest.fixture
def numbers():
    print("  setup numbers")
    data = [3, 1, 2]
    yield data
    print("  teardown numbers")


def test_sorted(numbers):
    assert sorted(numbers) == [1, 2, 3]


def test_len(numbers):
    assert len(numbers) == 3
```

Run with `-s` so that pytest does not hide the `print` output:

```text
$ python -m pytest -s test_fx.py
test_fx.py   setup numbers
.  teardown numbers
  setup numbers
.  teardown numbers
```

(The dots are pytest's progress marks: one `.` per passing test.) Read the output carefully. It shows the **life of a fixture**:

1. pytest sees `test_sorted(numbers)` and notices the parameter name `numbers`.
2. It finds a fixture with that name and runs it **up to the `yield`**. This is the *setup*.
3. The value after `yield` (here the list) is handed to the test as the argument.
4. The test runs.
5. Whatever comes after the `yield` runs, **even if the test failed**. This is the *teardown*.

Each test got its **own fresh list**, because the default scope of a fixture is one test (section 3).

### 2.2 `yield` versus `return`

If a fixture needs no cleanup, use `return`:

```python
@pytest.fixture
def prices():
    return {"apple": 40, "pear": 55}
```

If it needs cleanup, use `yield` and put the cleanup after it. Typical cleanups: close a connection, remove a temporary file, restore a global setting.

**Why does pytest run the teardown even after a failed test?** Because the point of teardown is to leave the world clean. If cleanup only ran after *passing* tests, the first failure would pollute every later test, and you would debug ten failures that have one cause.

What if the *setup* itself fails? Then the test does not run at all, and pytest reports an **error**, not a failure:

```python
import pytest

@pytest.fixture
def broken():
    raise RuntimeError("cannot connect")

def test_uses_broken(broken):
    assert True
```
```text
E                                                                        [100%]
==================================== ERRORS ====================================
______________________ ERROR at setup of test_uses_broken ______________________

    @pytest.fixture
    def broken():
>       raise RuntimeError("cannot connect")
E       RuntimeError: cannot connect

test_fail_setup.py:5: RuntimeError
=========================== short test summary info ============================
ERROR test_fail_setup.py::test_uses_broken - RuntimeError: cannot connect
```

Learn the difference: **FAILED** means "the test ran and an assert was false". **ERROR** means "the test could not even start" (setup problem) or its teardown broke. When you see `ERROR at setup`, look at the fixture, not at the test body.

### 2.3 Fixtures can use other fixtures

A fixture may take other fixtures as parameters. pytest builds the chain in the right order and tears it down in the **reverse** order, like unpacking boxes.

```python
import pytest


@pytest.fixture
def db():
    print("\n  open db")
    yield {"users": []}
    print("  close db")


@pytest.fixture
def user(db):
    print("  add user")
    db["users"].append("asha")
    yield "asha"
    print("  remove user")
    db["users"].remove("asha")


def test_user_in_db(db, user):
    assert db["users"] == ["asha"]
```
```text
$ python -m pytest -s test_dep.py


  open db
  add user
.  remove user
  close db
```

`user` depends on `db`, so `db` is set up first and torn down **last**. This is why the database is still open while `user` removes itself. The rule is the same as for `with` blocks inside each other: whatever was opened last is closed first.

`--setup-show` prints the order of setup and teardown for a real run (you will use it in section 3), and `--fixtures-per-test` lists the fixtures a test uses.

### 2.5 The `request` object

A fixture can ask for a special built-in fixture named `request`. It gives information about **who is asking**: the test's name, its module, any parameter (section 5), and a way to register cleanup.

```python
import pytest


@pytest.fixture
def name(request):
    return request.node.name


def test_alpha(name):
    assert name == "test_alpha"


@pytest.fixture
def fin(request):
    print("\n  setup")
    request.addfinalizer(lambda: print("  finalizer ran"))
    return 1


def test_fin(fin):
    assert fin == 1
```
```text
$ python -m pytest -s test_req.py
.
  setup
.  finalizer ran
```

`request.addfinalizer(function)` is the older way to register cleanup; `yield` is simpler and preferred. You will use `request` mostly for `request.param` in section 5.

### 2.6 `autouse` fixtures

Sometimes you want a fixture to run for **every test** without each test asking: reset a global, block the network (section 10), start each test in a temp folder. Mark it `autouse=True`:

```python
import pytest

LOG = []


@pytest.fixture(autouse=True)
def log_each():
    LOG.append("start")
    yield
    LOG.append("end")


def test_one():
    assert LOG == ["start"]


def test_two():
    assert LOG == ["start", "end", "start"]
```
```text
..                                                                       [100%]
```

Both tests pass: `test_one` never mentioned `log_each`, yet the fixture ran.

**Use `autouse` sparingly.** It is invisible: a reader of a test cannot see that something runs around it. Good uses are *safety nets* (no real network, no real clock). Bad uses are things the test's meaning depends on; those should be visible as a parameter.

### 2.7 Fixture factories

A fixture returns **one** value. What if a test needs three users with different names? Return a **function** that builds them (a *factory*), and let the fixture clean up everything it created:

```python
import pytest


@pytest.fixture
def make_user():
    created = []

    def make(name, admin=False):
        user = {"name": name, "admin": admin}
        created.append(user)
        return user

    yield make
    for user in created:           # cleanup everything that was made
        user.clear()


def test_two_users(make_user):
    a = make_user("asha")
    b = make_user("ravi", admin=True)
    assert a["admin"] is False
    assert b["admin"] is True
```

Notice the closure from the functions chapter: `make` remembers `created`. The factory pattern gives each test as many objects as it needs, with the exact fields it cares about.

#### Try it 2.1

Predict the output of `python -m pytest -s` for this file, then check.

```python
import pytest

@pytest.fixture
def a():
    print("A-up")
    yield
    print("A-down")

@pytest.fixture
def b(a):
    print("B-up")
    yield
    print("B-down")

def test_it(b):
    print("body")
```

<details><summary>Answer</summary>

```text
A-up
B-up
body
.B-down
A-down
```

`b` needs `a`, so `a` goes up first. Teardown is the reverse: `b` first, then `a`. (The `.` is pytest's progress mark for the finished test, printed right after the body.)

</details>

## 3. Scopes: how long does a fixture live?

### 3.1 The cost of fresh setup

By default, a fixture runs **once per test** (scope `"function"`). That gives perfect isolation: no test can disturb another. But setup can be **expensive**: connecting to a database, loading a 50 MB data file, starting a small server. Doing it before each of 500 tests wastes minutes.

The `scope` argument lets a fixture live longer and be **shared**:

| Scope | Setup runs... | Typical use |
|---|---|---|
| `"function"` (default) | once per test | anything the test may change |
| `"class"` | once per test class | shared by the tests of one class |
| `"module"` | once per `.py` test file | a loaded sample dataset |
| `"package"` | once per package (folder with `__init__.py`) | rare |
| `"session"` | once for the whole run | a started server, a compiled resource |

```python
import pytest


@pytest.fixture(scope="session")
def s():
    print("\n[session setup]")
    yield
    print("[session teardown]")


@pytest.fixture(scope="module")
def m():
    print("[module setup]")
    yield
    print("[module teardown]")


@pytest.fixture
def f():
    print("[function setup]")
    yield
    print("[function teardown]")


def test_a(s, m, f):
    print("test_a")


def test_b(s, m, f):
    print("test_b")
```
```text
[session setup]
[module setup]
[function setup]
test_a
.[function teardown]
[function setup]
test_b
.[function teardown]
[module teardown]
[session teardown]
```

Read it top to bottom: the wide scopes are set up first and torn down last, like nested boxes. The function-scoped fixture is built and destroyed around each test, while session and module fixtures stay up.

### 3.2 The price of sharing: lost isolation

A shared fixture is shared **by value**, so if a test changes it, the next test sees the change. This is the classic way a wider scope breaks a test suite:

```python
import pytest


@pytest.fixture(scope="module")
def basket():
    return []


def test_add_apple(basket):
    basket.append("apple")
    assert basket == ["apple"]


def test_add_pear(basket):
    basket.append("pear")
    assert basket == ["pear"]
```
```text
.F                                                                       [100%]
=================================== FAILURES ===================================
________________________________ test_add_pear _________________________________

basket = ['apple', 'pear']

    def test_add_pear(basket):
        basket.append("pear")
>       assert basket == ["pear"]
E       AssertionError: assert ['apple', 'pear'] == ['pear']
E         
E         At index 0 diff: 'apple' != 'pear'
E         Left contains one more item: 'pear'
E         Use -v to get more diff

test_shared.py:13: AssertionError
=========================== short test summary info ============================
FAILED test_shared.py::test_add_pear - AssertionError: assert ['apple', 'pear...
```

Worse: if you run only `test_add_pear`, it **passes**. A result that depends on which other tests ran is a flaky test in the making (section 13).

**Rule of thumb.**

- Share (wide scope) only things that are **expensive** *and* **read-only** (or that you reset yourself).
- Anything a test may modify stays function-scoped.
- When in doubt, keep the default. A slow-but-correct suite beats a fast-but-lying one.

### 3.3 Scope rules between fixtures

A fixture may only depend on fixtures of the **same or wider** scope. A module-scoped fixture that needs a function-scoped one makes no sense: the function-scoped one would have to be recreated for every test, but the module one is built only once. pytest refuses:

```python
import pytest

@pytest.fixture
def small():
    return 1

@pytest.fixture(scope="module")
def big(small):
    return small + 1

def test_x(big):
    assert big == 2
```
```text
E                                                                        [100%]
==================================== ERRORS ====================================
___________________________ ERROR at setup of test_x ___________________________
ScopeMismatch: You tried to access the function scoped fixture small with a module scoped request object. Requesting fixture stack:
test_mismatch.py:7:  def big(small)
Requested fixture:
test_mismatch.py:3:  def small()
=========================== short test summary info ============================
ERROR test_mismatch.py::test_x - Failed: ScopeMismatch: You tried to access t...
```

The cure: give `small` the module scope as well, or make `big` function-scoped.

### 3.4 The order of setup

With several fixtures of different scopes, pytest sets up the **widest scope first**. Among fixtures of the same scope, **autouse** ones come first, then the others in the order the test lists them (and dependencies before dependents). Look:

```python
import pytest

@pytest.fixture(scope="module")
def a():
    print("\nsetup a (module)")
    yield
    print("teardown a")

@pytest.fixture
def b():
    print("setup b (function)")
    yield
    print("teardown b")

@pytest.fixture(autouse=True)
def c():
    print("setup c (autouse)")
    yield
    print("teardown c")

def test_x(b, a):
    print("test body")
```
```text
$ python -m pytest -s test_order.py

setup a (module)
setup c (autouse)
setup b (function)
test body
.teardown b
teardown c
teardown a
```

Even though the test wrote `(b, a)`, `a` went first: it has the wider scope. Then `c`, because autouse fixtures lead within their scope. Then `b`. Teardown reverses everything. `--setup-show` draws the same thing as a tree, and is the quickest way to answer "in what order does my setup run?":

```text
$ python -m pytest --setup-show test_order.py
    SETUP    M a
        SETUP    F c
        SETUP    F b
        test_order.py::test_x (fixtures used: a, b, c) .
        TEARDOWN F b
        TEARDOWN F c
    TEARDOWN M a
```

(`M` = module scope, `F` = function scope.)

#### Try it 3.1

Predict the output of `python -m pytest -s` for this file. (Careful: three fixtures, two scopes, one autouse.)

```python
import pytest

@pytest.fixture(scope="module")
def a():
    print("A", end=" ")
    yield
    print("a-down", end=" ")

@pytest.fixture
def b(a):
    print("B", end=" ")
    yield
    print("b-down", end=" ")

@pytest.fixture(autouse=True)
def c():
    print("C", end=" ")
    yield
    print("c-down", end=" ")

def test_1(b):
    print("t1", end=" ")

def test_2(b):
    print("t2", end=" ")
```

<details><summary>Answer</summary>

```text
A C B t1 .b-down c-down C B t2 .b-down c-down a-down 
```

`a` is module scoped, so it is set up once, first (widest scope first), and torn down last. Then for each test: autouse `c`, then `b`; after the test, `b` goes down, then `c`. `a` is **not** repeated for the second test.

</details>

#### Try it 3.2

A colleague speeds up the suite by changing `@pytest.fixture` to `@pytest.fixture(scope="session")` on a fixture that returns an empty list which many tests append to. What breaks, and what is a safe way to keep the speed?

<details><summary>Answer</summary>

Every test now shares one list, so tests see each other's items; results depend on the order and on which tests are selected. Safe options: keep the list function-scoped (creating an empty list is not slow anyway), or keep a shared *expensive* thing at session scope and have a cheap function-scoped fixture that copies or resets what the tests may change.

</details>

## 4. `conftest.py`: sharing fixtures

### 4.1 The problem

A fixture written inside `test_orders.py` is visible only to that file. If three test files need the same `sample_user` fixture, you must either copy it (bad) or put it somewhere shared. pytest has a special file for this: **`conftest.py`**.

Rules:

- A file named exactly `conftest.py` is loaded by pytest automatically; you **never import** from it.
- Fixtures in it are visible to every test in **the same folder and all folders below it**.
- A `conftest.py` in a subfolder adds to, or **overrides**, the one above for tests in that subfolder.

### 4.2 The folder hierarchy

Take this project:

```text
./conftest.py                 fixture who -> "root"
./tests/conftest.py           fixture who -> uses the upper one, adds "/tests"
./tests/api/conftest.py       fixture who -> replaces it: "api (replaced)"
./tests/api/test_api.py       def test_api(who): print("api sees:", who)
./tests/ui/test_ui.py         def test_ui(who):  print("ui sees:", who)
./tests/test_top.py           def test_top(who): print("top sees:", who)
```

The files are:

```python
# ./conftest.py
import pytest

@pytest.fixture
def who():
    return "root"
```
```python
# ./tests/conftest.py
import pytest

@pytest.fixture
def who(who):               # asks for the 'who' from the folder above
    return who + "/tests"
```
```python
# ./tests/api/conftest.py
import pytest

@pytest.fixture
def who():                  # does not ask: replaces completely
    return "api (replaced)"
```

Running `python -m pytest -s` from `.`:

```text
api sees: api (replaced)
.top sees: root/tests
.ui sees: root/tests
.
```

(Folders are visited in alphabetical order, so `tests/api` ran first.) Two things to learn here:

1. The closest `conftest.py` wins. `test_ui` has no `conftest.py` of its own, so it uses the one from `tests/`.
2. A fixture can **extend** the fixture of the same name above it by asking for it as a parameter (`def who(who)`), or **replace** it by not asking. This is how you build a default in the root and customise it for one area.

### 4.3 What goes into `conftest.py`, and what does not

Put in `conftest.py`:

- fixtures used by two or more test files (sample data, temp folders, fake clients);
- safety-net autouse fixtures (section 10: no network);
- hooks and plugin settings (advanced; you will rarely need them).

Do **not** put there:

- plain helper functions you want to call from tests. Tests do not `import` from `conftest.py`. Put helpers in a normal module, for example `tests/helpers.py`, and import them.
- fixtures used by one test file only. Keep them next to their tests; a reader should find a fixture near where it is used.

A `conftest.py` that grows to 400 lines is a smell: it becomes a second, hidden program. Split it by folder. (A *plugin*, such as `hypothesis`, is a package that adds fixtures to pytest for every project; a `conftest.py` is a *local* plugin for one folder.)

#### Try it 4.1

With the three `conftest.py` files above, what would a new test `tests/api/v2/test_v2.py` containing `def test_v2(who): print(who)` print? There is no `conftest.py` in `tests/api/v2/`.

<details><summary>Answer</summary>

`api (replaced)`. The nearest `conftest.py` above `v2/` is `tests/api/conftest.py`, and that fixture does not ask for the upper `who`, so the chain stops there.

</details>

#### Try it 4.2

You write a helper `def make_order(**kw)` in `conftest.py` and, in a test file, `from conftest import make_order`. It works on your machine and breaks on a colleague's. Why is it a bad design, and what is the fix?

<details><summary>Answer</summary>

Importing from `conftest.py` depends on how `sys.path` is set up, which differs between machines and runners, and `conftest.py` is meant to be loaded by pytest, not imported. Move the helper into a normal module (`tests/helpers.py`) and import it, or make it a fixture factory (section 2.7) in `conftest.py` and receive it as a parameter.

</details>

## 5. Parametrization and markers

### 5.1 `parametrize` revisited, with names

Chapter 8 introduced `@pytest.mark.parametrize`: one test function, many input rows, one reported test per row. A short refresher:

```python
import pytest


def add(a, b):
    return a + b


@pytest.mark.parametrize("a, b, expected", [
    (1, 2, 3),
    (0, 0, 0),
    (-1, 1, 0),
    (2, 2, 5),
])
def test_add(a, b, expected):
    assert add(a, b) == expected
```
```text
...F                                                                     [100%]
=================================== FAILURES ===================================
_______________________________ test_add[2-2-5] ________________________________

a = 2, b = 2, expected = 5

    ...
>       assert add(a, b) == expected
E       assert 4 == 5
E        +  where 4 = add(2, 2)

test_p.py:13: AssertionError
=========================== short test summary info ============================
FAILED test_p.py::test_add[2-2-5] - assert 4 == 5
```

The failing row is named `test_add[2-2-5]`: pytest builds the **id** by joining the values with `-`. For numbers that is readable. For long strings, objects or lists it becomes unreadable (`test_x[<object object at 0x...>-1]`). Give rows **names** with `pytest.param(..., id="...")`:

```python
import pytest


@pytest.mark.parametrize("text, ok", [
    pytest.param("", False, id="empty"),
    pytest.param("abc", True, id="plain"),
    pytest.param(" ", False, id="blank"),
])
def test_nonblank(text, ok):
    assert bool(text.strip()) == ok
```

and now the ids are `test_nonblank[empty]`, `test_nonblank[plain]`, `test_nonblank[blank]`. A failure then reads like a sentence: "the *blank* case failed". Good ids are cheap documentation.

### 5.2 Stacking parametrize: the grid

Two `parametrize` decorators on one test multiply: every combination runs.

```python
@pytest.mark.parametrize("x", [1, 2])
@pytest.mark.parametrize("y", ["a", "b"])
def test_grid(x, y):
    pass
```
```text
test_ids.py::test_grid[a-1] PASSED
test_ids.py::test_grid[a-2] PASSED
test_ids.py::test_grid[b-1] PASSED
test_ids.py::test_grid[b-2] PASSED
```

2 times 2 gives 4 tests. Notice the id order: the decorator **closest to the function** (`y`) comes first in the id. Stacking is handy for "every operator with every kind of input", but it grows fast: 10 by 10 by 10 is 1,000 tests. Use it with small lists.

### 5.3 Parameters through fixtures: `params=` and `indirect`

Sometimes the thing you vary is **a fixture**, for instance "run these tests once against the SQLite backend and once against the in-memory backend". Give the fixture `params`, and read the current one from `request.param`:

```python
@pytest.fixture(params=["sqlite", "memory"])
def backend(request):
    return request.param


def test_backend(backend):
    assert backend in ("sqlite", "memory")
```

Every test using `backend` now runs twice (`test_backend[sqlite]`, `test_backend[memory]`). If two such fixtures are used by one test, you get the grid again:

```python
@pytest.fixture(params=[1, 2])
def x(request):
    print(f"[x={request.param}]", end=" ")
    return request.param

@pytest.fixture(params=["a", "b"])
def y(request):
    return request.param

def test_xy(x, y):
    print(f"{x}{y}", end=" ")
```
```text
test_try3.py::test_xy[1-a] [x=1] 1a PASSED
test_try3.py::test_xy[1-b] [x=1] 1b PASSED
test_try3.py::test_xy[2-a] [x=2] 2a PASSED
test_try3.py::test_xy[2-b] [x=2] 2b PASSED
```

`indirect=True` is the bridge between the two ideas: the values in `parametrize` are sent **to a fixture** instead of straight to the test, so the fixture can build something from them.

```python
@pytest.fixture
def user(request):
    return {"name": request.param}


@pytest.mark.parametrize("user", ["asha", "ravi"], indirect=True)
def test_name(user):
    assert user["name"] in ("asha", "ravi")
```

Here the test receives a dict built by the fixture, not the plain string. Use `indirect` when the parameter needs setup or teardown (a file, a connection); use plain `parametrize` when the values are the data.

### 5.4 Markers: labels on tests

A **marker** is a label attached with `@pytest.mark.<name>`. pytest has some built-in markers that change how a test is run, and you can invent your own labels to select tests.

| Marker | Meaning |
|---|---|
| `@pytest.mark.skip(reason=...)` | never run this test; report it as skipped |
| `@pytest.mark.skipif(condition, reason=...)` | skip when the condition is true (for example, wrong operating system) |
| `@pytest.mark.xfail(reason=...)` | "expected to fail": a known bug. Failing is *not* an error |
| `@pytest.mark.<custom>` | your own label, such as `slow` or `network` |

Create a `pytest.ini` file next to your tests to **register** custom markers and to make pytest **strict**:

```ini
[pytest]
markers =
    slow: tests that take more than a second
    network: tests that need the internet
addopts = --strict-markers
```

Why register? Because an unregistered marker is almost always a **typo**, and without `--strict-markers` a typo like `@pytest.mark.slwo` silently labels nothing. With it:

```text
ERROR collecting test_typo.py
'slwo' not found in `markers` configuration option
!!!!!!!!!!!!!!!!!!!! Interrupted: 1 error during collection !!!!!!!!!!!!!!!!!!!!
```

Now a file using every marker:

```python
import sys
import pytest


def test_fast():
    assert 1 + 1 == 2

@pytest.mark.slow
def test_slow_thing():
    assert sum(range(1000)) == 499500

@pytest.mark.skip(reason="feature not written yet")
def test_future():
    assert False

@pytest.mark.skipif(sys.platform == "win32", reason="uses POSIX paths")
def test_posix_only():
    assert "/" in "a/b"

@pytest.mark.xfail(reason="bug #12: rounding", strict=True)
def test_known_bug():
    assert round(2.675, 2) == 2.68

@pytest.mark.xfail(reason="was broken, now fixed", strict=True)
def test_fixed_already():
    assert 1 == 1
```

Run with `-rsxX`, which asks pytest to explain **s**kips, **x**fails and **X**passes:

```text
$ python -m pytest -rsxX test_marks.py
..s.xF                                                                   [100%]
=================================== FAILURES ===================================
______________________________ test_fixed_already ______________________________
[XPASS(strict)] was broken, now fixed
=========================== short test summary info ============================
SKIPPED [1] test_marks.py:11: feature not written yet
XFAIL test_marks.py::test_known_bug - bug #12: rounding
```

Read the progress line `..s.xF`: two passes, one `s`kip, one pass (the POSIX test, on Linux), one `x` (expected failure, which is fine), and one `F`.

That last `F` is the lesson of `strict=True`. `test_fixed_already` is marked "expected to fail" but it **passed**. Without `strict`, pytest would show a quiet `XPASS` and nobody would notice that the bug was fixed and the marker is now a lie. With `strict=True`, the unexpected pass **fails the run**, which forces you to delete the marker. (And `round(2.675, 2)` is `2.67`, not `2.68`: floats cannot store 2.675 exactly. That is the xfail's "known bug".)

**Skip versus xfail.** `skip`: "this cannot or should not run here". `xfail`: "this should work but does not yet; I know and I track it". Never use `skip` to hide a failing test you are tired of; use `xfail(strict=True)` with a reason, so the problem stays visible.

### 5.5 Selecting tests: `-k` and `-m`

| Command | Runs |
|---|---|
| `pytest -k "fast or slow"` | tests whose **name** contains `fast` or `slow` (an expression) |
| `pytest -k "not slow"` | everything except names containing `slow` |
| `pytest -m slow` | tests **marked** `slow` |
| `pytest -m "not slow"` | tests not marked `slow`: the quick everyday run |
| `pytest path/test_x.py::test_name` | exactly one test |
| `pytest -x` | stop at the first failure |
| `pytest --maxfail=3` | stop after three failures |
| `pytest --lf` | rerun only tests that failed last time (it needs pytest's cache; see the note in 13.5) |

Typical workflow: run `-m "not slow"` while you work, and everything before you commit.

#### Try it 5.1

How many tests does pytest create from this, and what is the id of the last one?

```python
@pytest.mark.parametrize("a", [1, 2, 3])
@pytest.mark.parametrize("b", ["x", "y"])
@pytest.mark.parametrize("c", [True])
def test_many(a, b, c):
    pass
```

<details><summary>Answer</summary>

3 * 2 * 1 = 6 tests. The decorator nearest the function (`c`) comes first in the id, then `b`, then `a`. The last id is `test_many[True-y-3]`.

</details>

#### Try it 5.2

For each case, choose `skip`, `skipif`, `xfail(strict=True)` or nothing:

1. A test of a new feature that is planned but not coded.
2. A test that only makes sense on Windows.
3. A test that fails because of a bug you have reported and will fix next week.
4. A test that is slow but must run before every release.

<details><summary>Answer</summary>

1. `skip(reason="not written yet")`. (Or do not write the test yet.)
2. `skipif(sys.platform != "win32", reason=...)`.
3. `xfail(strict=True, reason="bug #...")`. Once fixed, strict mode will tell you to remove it.
4. Nothing to skip: give it a custom marker `slow`, so the quick run uses `-m "not slow"` and the release run runs everything.

</details>

## 6. Built-in fixtures: `tmp_path`, `capsys`, `monkeypatch`, `caplog`

pytest ships with fixtures that solve the commonest "outside world" problems. We will test this small module, `notes.py`:

```python
import logging
import os
from pathlib import Path

log = logging.getLogger("notes")
DISCOUNT = 10


def save_notes(path, notes):
    Path(path).write_text("\n".join(notes) + "\n", encoding="utf-8")


def load_notes(path):
    text = Path(path).read_text(encoding="utf-8")
    return [line for line in text.splitlines() if line]


def greet(name):
    print(f"Hello, {name}!")
    print("Welcome back.")


def data_dir():
    return os.environ.get("APP_DATA", "./data")


def risky(n):
    if n < 0:
        log.warning("negative input: %s", n)
        return 0
    return n


def price(base):
    return base - base * DISCOUNT // 100
```

### 6.1 `tmp_path`: a private folder for each test

Code that reads and writes files must be tested with **real files**, but never in your real folders. `tmp_path` gives each test a brand-new, empty folder (a `pathlib.Path`, as in the files chapter) that pytest creates before the test and keeps for a while for inspection:

```python
def test_roundtrip(tmp_path):
    f = tmp_path / "n.txt"
    notes.save_notes(f, ["a", "b"])
    assert f.read_text() == "a\nb\n"
    assert notes.load_notes(f) == ["a", "b"]
```

```python
def test_show(tmp_path):
    print(type(tmp_path).__name__, tmp_path.name)
    print(tmp_path.is_dir(), list(tmp_path.iterdir()))
```
```text
PosixPath test_show0
True []
```

(`PosixPath` is the Linux/macOS type; on Windows you see `WindowsPath`. The folder's full path is machine-specific, and ends with the test's name.) Two good habits: always build paths with `tmp_path / "name"`, and never write outside `tmp_path`. A test that writes to the current folder leaves files behind, and two tests writing the same file name fight each other.

### 6.2 `capsys`: checking what the code prints

`greet` does not return anything; it **prints**. The test must capture the output. `capsys` captures what is written to `sys.stdout` and `sys.stderr`; `readouterr()` returns both as strings and *clears* the buffer:

```python
def test_greet(capsys):
    notes.greet("Asha")
    out, err = capsys.readouterr()
    assert out == "Hello, Asha!\nWelcome back.\n"
    assert err == ""
```

Always include the final `\n` in the expected string: each `print` adds one. `capfd` is the sibling that captures at the *file descriptor* level, so it also sees output from C code and subprocesses; `capsys` only sees Python-level writes:

```python
import os

def test_cap(capfd):
    os.write(1, b"from the OS level\n")
    out, _ = capfd.readouterr()
    assert out == "from the OS level\n"

def test_cap_sys_misses(capsys):
    os.write(1, b"raw write\n")
    out, _ = capsys.readouterr()
    assert out == ""            # capsys never saw it!
```

Both pass. Use `capsys` for ordinary `print`; reach for `capfd` only for low-level writes.

### 6.3 `monkeypatch`: changing things for one test only

Code often depends on **settings that live elsewhere**: an environment variable, a module-level constant, a function in another module, the current folder. To test it, you must change that setting, **and put it back afterwards**, or you poison later tests. `monkeypatch` does both: every change is undone automatically when the test ends.

```python
def test_data_dir_default(monkeypatch):
    monkeypatch.delenv("APP_DATA", raising=False)
    assert notes.data_dir() == "./data"


def test_data_dir_env(monkeypatch):
    monkeypatch.setenv("APP_DATA", "/srv/x")
    assert notes.data_dir() == "/srv/x"


def test_price_discount(monkeypatch):
    monkeypatch.setattr(notes, "DISCOUNT", 50)
    assert notes.price(200) == 100


def test_price_back_to_normal():
    assert notes.price(200) == 180          # DISCOUNT is 10 again


def test_chdir(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    notes.save_notes("here.txt", ["x"])
    assert (tmp_path / "here.txt").exists()
```

The methods you will use:

| Call | Effect (undone after the test) |
|---|---|
| `monkeypatch.setattr(obj, "name", value)` | replace an attribute: a constant or function in a module |
| `monkeypatch.delattr(obj, "name")` | remove an attribute |
| `monkeypatch.setenv("NAME", "value")` | set an environment variable |
| `monkeypatch.delenv("NAME", raising=False)` | remove one (`raising=False`: fine if absent) |
| `monkeypatch.chdir(path)` | change the current folder |
| `monkeypatch.setitem(dict, key, value)` | change a dictionary entry |

Look at `test_price_back_to_normal`: it passes **because** the earlier patch was undone. And `monkeypatch.setattr` protects you from typos, too. By default it raises if the attribute does not exist:

```python
def test_setattr_typo(monkeypatch):
    monkeypatch.setattr(notes, "data_dirr", lambda: "/fake")
```
```text
E   AttributeError: <module 'notes' from '/home/you/s6/notes.py'> has no attribute 'data_dirr'
```

You can also replace a function: `monkeypatch.setattr(notes, "data_dir", lambda: "/fake")`. Where you patch matters; section 8.5 explains the rule.

### 6.4 `caplog`: checking log messages

Good programs log warnings through the `logging` module. `caplog` collects the log records of a test, so you can assert that the warning really happened:

```python
import logging


def test_warning_logged(caplog):
    with caplog.at_level(logging.WARNING, logger="notes"):
        assert notes.risky(-5) == 0
    assert "negative input: -5" in caplog.text
    assert caplog.records[0].levelname == "WARNING"
```

`caplog.text` is all the formatted log output as one string; `caplog.records` is the list of `LogRecord` objects, with `.levelname`, `.getMessage()` and more. Use `caplog.at_level(...)` to make sure the level you care about is recorded.

#### Try it 6.1

This test passes alone. After it, another test calls `notes.price(200)` and expects 180, but gets 100. What is missing?

```python
def test_big_discount():
    notes.DISCOUNT = 50
    assert notes.price(200) == 100
```

<details><summary>Answer</summary>

The test changed a module-level global by plain assignment, and nothing restores it. Every later test in the same run sees `DISCOUNT = 50`. Use `monkeypatch.setattr(notes, "DISCOUNT", 50)`, which undoes the change automatically.

</details>

## 7. Test doubles and the best seam: dependency injection

### 7.1 Why replace a part?

Look at this class:

```python
class WeatherReport:
    def __init__(self, client):
        self.client = client

    def summary(self, city):
        temp = self.client.get_temp(city)
        if temp is None:
            return f"{city}: no data"
        label = "hot" if temp >= 30 else "mild" if temp >= 15 else "cold"
        return f"{city}: {temp}C ({label})"
```

The interesting logic is the `hot`/`mild`/`cold` decision. The `client` talks to a weather service over the internet. In a test we do **not** want the real internet: it is slow, it may be down, and the temperature in Pune changes every hour, so we could never assert `"hot"` reliably. So in tests we hand `WeatherReport` a **stand-in** for the client. Stand-ins are called **test doubles** (like a stunt double in a film).

### 7.2 The five kinds

| Double | What it does | Use it to... |
|---|---|---|
| **Dummy** | does nothing; it only fills a parameter | satisfy a signature that the test never uses |
| **Stub** | returns **canned answers** | control what the code under test *receives* |
| **Spy** | a real or stub object that **records** how it was used | check what the code *did* (`calls == ["Goa"]`) |
| **Fake** | a small **working** implementation, simpler than the real one | replace a database with a dict, for many tests |
| **Mock** | an object that records calls *and* can verify them (`unittest.mock`) | all of the above, built on the fly |

```python
class StubClient:            # stub: canned answers
    def __init__(self, temp):
        self.temp = temp

    def get_temp(self, city):
        return self.temp


class SpyClient:             # spy: records how it was used
    def __init__(self):
        self.calls = []

    def get_temp(self, city):
        self.calls.append(city)
        return 20


class FakeClient:            # fake: a small working replacement
    def __init__(self, table):
        self.table = table

    def get_temp(self, city):
        return self.table.get(city)


def test_hot_with_stub():
    assert WeatherReport(StubClient(35)).summary("Pune") == "Pune: 35C (hot)"


def test_asks_for_the_right_city_with_spy():
    spy = SpyClient()
    WeatherReport(spy).summary("Goa")
    assert spy.calls == ["Goa"]


def test_missing_city_with_fake():
    fake = FakeClient({"Pune": 28})
    report = WeatherReport(fake)
    assert report.summary("Pune") == "Pune: 28C (mild)"
    assert report.summary("Oslo") == "Oslo: no data"
```
```text
...                                                                      [100%]
```

None of these needed any special library: they are ordinary classes written in ten lines. That is the point of the next section.

### 7.3 Dependency injection: the best seam

A **seam** is a place where you can change behaviour without editing the code under test. `WeatherReport` has an excellent seam: it **receives** its client as a constructor argument instead of creating it inside. Giving a function or class its collaborators from outside is called **dependency injection** (DI), and it is the simplest and most powerful testing technique in this chapter.

Compare two designs:

```python
# Hard to test: the dependency is created inside.
class WeatherReportHard:
    def summary(self, city):
        client = RealHttpClient("https://api.weather.example")
        temp = client.get_temp(city)
        ...

# Easy to test: the dependency is passed in.
class WeatherReport:
    def __init__(self, client):
        self.client = client
```

With the first design, the only way to test is to **patch** (section 8.5) the name `RealHttpClient`, which couples the test to the *internal wiring*. With the second, the test just passes a double. In production you write `WeatherReport(RealHttpClient(...))`. The same trick works for functions: `def get_json(url, opener=urllib.request.urlopen)` lets a test pass a fake `opener`.

Rule: **prefer injection; use patching when you cannot change the code** (old code, third-party code, a module-level call such as `time.time()` that you cannot avoid).

### 7.4 Contracts: a fake must behave like the real thing

A fake is only useful if it **behaves like the real object**. A `FakeClient` that returns `None` for missing cities is a lie if the real client raises an error for them: all your tests would pass and production would crash. The cure is a **contract test**: one set of tests that runs against **both** the fake and the real thing, using a parametrized fixture (section 5.3). If the real client is too slow to run always, mark that variant `@pytest.mark.network` and run it now and then. You will write such a contract test in this module's problems.

#### Try it 7.1

Name the kind of double:

1. `def send(msg): pass`, passed because the function wants a callback you will not use.
2. A class holding a `dict` of users with `add`, `get`, `delete`, standing in for a real database.
3. A function that always returns `"2025-01-01"`.
4. A list that every call to `log(...)` appends to, so the test can check what was logged.

<details><summary>Answer</summary>

1. Dummy.
2. Fake (a working but simplified implementation).
3. Stub (a canned answer).
4. Spy (it records how it was used).

</details>

## 8. `unittest.mock`

Writing a `StubClient` class for every test gets long. The standard library module `unittest.mock` builds doubles **on the fly**.

### 8.1 `Mock` and `MagicMock`

A `Mock` object accepts **any** attribute and any call, and remembers what happened:

```python
from unittest.mock import Mock

m = Mock()
print(m.anything)
print(m.send("hi"))
m.send.return_value = 42
print(m.send("x"), m.send("y"))
print(m.send.call_count, m.send.call_args)
print(m.send.call_args_list)
```
```text
<Mock name='mock.anything' id='138481098900544'>
<Mock name='mock.send()' id='138481098901552'>
42 42
3 call('y')
[call('hi'), call('x'), call('y')]
```

(The `id=` numbers are machine-specific.) Study what happened:

- `m.anything` did not fail; a Mock **invents** child mocks for any name. Calling `m.send("hi")` returned another child mock.
- Setting `m.send.return_value = 42` made later calls return `42`.
- The mock **recorded** all three calls, in order: `call_count`, `call_args` (the last call) and `call_args_list`.

`MagicMock` is a `Mock` that also supports Python's special methods such as `len()`, `with`, indexing and iteration; a plain `Mock` does not (`len(Mock())` raises `TypeError: object of type 'Mock' has no len()`). Use `Mock` by default, and `MagicMock` when the code under test does `len(x)`, `for a in x` or `with x:`.

### 8.2 `return_value` and `side_effect`

`return_value` is for one fixed answer. **`side_effect`** is for anything else:

- an **exception class or instance**: the call raises it;
- a **list**: each call returns the next item (and an item that is an exception is raised);
- a **function**: called with the same arguments, its result is returned.

```python
r = Mock()
r.get.side_effect = [1, 2, ValueError("boom")]
print(r.get(), r.get())
try:
    r.get()
except ValueError as e:
    print("raised", e)
try:
    r.get()
except StopIteration:
    print("ran out -> StopIteration")

f = Mock(side_effect=lambda x: x * 2)
print(f(4))
```
```text
1 2
raised boom
ran out -> StopIteration
8
```

The list form is how you test **retry logic**: "the first two calls fail with a timeout, the third succeeds" is `side_effect=[TimeoutError(), TimeoutError(), "ok"]`. If the list is too short, the mock raises `StopIteration`; that error means *your code called more often than you planned*.

### 8.3 Checking calls: the `assert_*` methods

| Method | Passes when |
|---|---|
| `m.assert_called()` | called at least once |
| `m.assert_called_once()` | called exactly once |
| `m.assert_called_with(args)` | the **last** call had these arguments |
| `m.assert_called_once_with(args)` | called exactly once, with these arguments |
| `m.assert_any_call(args)` | some call had these arguments |
| `m.assert_not_called()` | never called |
| `m.assert_has_calls([call(...), ...])` | these calls appear **consecutively, in this order** |

The failure messages are clear, so read them:

```python
m = Mock()
m(1, key="v")
m.assert_called_once_with(1)
```
```text
AssertionError: expected call not found.
Expected: mock(1)
  Actual: mock(1, key='v')
```

Argument **form matters**: `f(1, "v")` and `f(1, key="v")` are different calls to a plain mock. Also notice `assert_has_calls` needs the calls to sit next to each other:

```python
from unittest.mock import Mock, call

m2 = Mock()
m2.a(1); m2.b(2); m2.a(3)
m2.assert_has_calls([call.a(1), call.a(3)])   # fails: b(2) is in between
m2.assert_has_calls([call.b(2), call.a(3)])   # passes
```

Modern Python guards you against a typo in the assertion name: `m.charge.assert_caled_once_with(1)` raises `AttributeError: 'assert_caled_once_with' is not a valid assertion`. (In very old versions a typo like that silently did nothing, so a test could never fail.)

### 8.4 `spec` and `autospec`: mocks that cannot lie so easily

A bare `Mock()` accepts **anything**: a misspelled method, a wrong number of arguments. That is the most dangerous property of mocks: they cannot tell you that your test is wrong.

```python
from unittest.mock import Mock, create_autospec

class Mailer:
    def send(self, to, subject, body=""):
        raise RuntimeError("real mail server not available")

def notify(mailer, user):
    mailer.send(user, "Hi")
    mailer.sendd(user)         # typo!

def test_plain_mock_hides_typo():
    notify(Mock(), "a@x.com")           # passes! the typo is invisible

def test_spec_catches_typo():
    notify(Mock(spec=Mailer), "a@x.com")

def test_autospec_checks_signature():
    m = create_autospec(Mailer, instance=True)
    m.send("a@x.com")                   # missing 'subject'
```
```text
.FF
E   AttributeError: Mock object has no attribute 'sendd'. Did you mean: 'send'?
E   TypeError: missing a required argument: 'subject'
```

- `Mock(spec=Mailer)` allows only the attributes that `Mailer` really has.
- `create_autospec(Mailer, instance=True)` goes further: it also checks the **signature** of every method, so calling `send` without a `subject` fails like the real one would.

Make `spec` or `autospec` your default. A mock with a spec fails when the real class changes (for example `send` renamed to `deliver`); a bare mock keeps passing while production breaks.

### 8.5 `patch`: replacing a name temporarily

When you cannot inject (section 7.3), `patch` replaces a name for the duration of a `with` block or a decorated test, then puts the original back:

```python
from unittest.mock import patch

def test_decorator_form():
    with patch("weather.fetch_temp", return_value=21):
        ...

@patch("weather.fetch_temp", return_value=18)
def test_decorator(mock_fetch):          # the mock is passed as an argument
    assert weather.describe("Goa") == "Goa: 18C"
    mock_fetch.assert_called_once_with("Goa")
```

`patch("module.name")` takes a **string**: the dotted path to the name. `patch.object(thing, "name")` takes the object itself, which avoids typos in strings. Add `autospec=True` to get the signature checks of 8.4. `patch.dict(os.environ, {"MODE": "test"})` temporarily changes a dictionary and restores it afterwards.

### 8.6 The golden rule: patch where the name is *looked up*

This is the most common mocking mistake. Two modules:

```python
# weather.py
def fetch_temp(city):
    raise RuntimeError("real network call")

def describe(city):
    return f"{city}: {fetch_temp(city)}C"
```
```python
# app.py
from weather import fetch_temp      # copies the NAME into app's namespace

def banner(city):
    return f"Today in {city}: {fetch_temp(city)}C"
```

`from weather import fetch_temp` creates a **second name**, `app.fetch_temp`, pointing at the same function. `banner` looks up `fetch_temp` in **app's** namespace. Now two tests:

```python
def test_patch_wrong_place():
    with patch("weather.fetch_temp", return_value=21):
        app.banner("Pune")

def test_patch_right_place():
    with patch("app.fetch_temp", return_value=21):
        assert app.banner("Pune") == "Today in Pune: 21C"
```
```text
E   RuntimeError: real network call
FAILED test_spec.py::test_patch_wrong_place - RuntimeError: real network call
```
The wrong-place test fails with the **real** function's error; the right-place test passes.

Patching `weather.fetch_temp` replaced the name in `weather`, but `app` still held the old function. **Patch the name in the module that uses it.** If `app.py` had written `import weather` and called `weather.fetch_temp(city)`, then patching `weather.fetch_temp` would have worked, because the lookup happens in `weather` at call time.

#### Try it 8.1

Predict the output:

```python
from unittest.mock import Mock

m = Mock()
m.ping.side_effect = [10, 20]
print(m.ping(), m.ping())
print(m.ping.call_count)
try:
    m.ping()
except StopIteration:
    print("too many")
print(m.ping.call_count)
```

<details><summary>Answer</summary>

```text
10 20
2
too many
3
```

The third call **raises** `StopIteration`, but it still counts as a call, so the count is 3.

</details>

#### Try it 8.2

`shop.py` has `from emailer import send_receipt` and a function `checkout()` that calls `send_receipt(order)`. Which patch target makes a test of `checkout` skip the real e-mail: `"emailer.send_receipt"` or `"shop.send_receipt"`? Why?

<details><summary>Answer</summary>

`"shop.send_receipt"`. `checkout` looks the name up in `shop`'s namespace, where `from emailer import send_receipt` put it. Patching `emailer.send_receipt` would only change the original, and `shop` would keep its own reference to the real function.

</details>

#### Try it 8.3

Why can this test never fail on a wrong argument count, and how do you fix it?

```python
def test_sends():
    gateway = Mock()
    pay(gateway, 100)
    gateway.charge.assert_called_once()
```

<details><summary>Answer</summary>

`Mock()` accepts any call with any arguments, so `gateway.charge(100, 7, 9)` is fine, and so is a call to a method the real gateway does not have. Fix: `gateway = create_autospec(Gateway, instance=True)` (or `Mock(spec=Gateway)`) and assert the arguments too: `assert_called_once_with(100)`.

</details>

## 9. When mocking hurts

Mocks are a sharp tool. Used well, they remove the clock and the network from a test. Used badly, they produce tests that are **green and worthless**. Four ways it goes wrong:

### 9.1 The test that tests the mock

Here is a pricing module with a bug: the discount is *added* instead of subtracted.

```python
# pricing.py (buggy copy)
def apply_discount(price, percent):
    return price + price * percent / 100    # BUG: adds instead of subtracts


def total(items, discount_fn=apply_discount, percent=10):
    return sum(discount_fn(p, percent) for p in items)
```

And an "enthusiastic" test that mocks everything:

```python
from unittest.mock import patch
import pricing


def test_total_over_mocked():
    with patch.object(pricing, "apply_discount", return_value=90) as m:
        result = pricing.total([100], discount_fn=m)
    assert result == 90
    m.assert_called_once_with(100, 10)


def test_total_real():
    assert pricing.total([100, 200]) == 270
```
```text
.F                                                                       [100%]
FAILED test_over_mocked.py::test_total_real - assert 330.0 == 270
```

`test_total_over_mocked` **passes** against the broken code. It replaced the one function that contains the bug with a mock that returns the answer the test wants, and then checked that the answer came back. It proves only that `sum` works. The honest test, `test_total_real`, found the bug at once (the output also shows `330.0` where `270` was expected).

**Rule: never mock the code you are testing.** Replace its *neighbours* (the network, the clock), not its own logic.

### 9.2 Testing the implementation instead of the behaviour

```python
def checkout(cart, gateway):
    amount = sum(cart)
    gateway.charge(amount)
    gateway.log("charged")
    return amount


def test_checkout_brittle():
    gw = Mock()
    checkout([5, 5], gw)
    assert gw.mock_calls == [call.charge(10), call.log("charged")]
```

This passes today. Tomorrow someone logs *before* charging, or adds a harmless `gateway.log("start")`. The behaviour the user cares about (the customer is charged 10) is unchanged, yet the test fails. That is a **brittle** test: it is married to *how* the code works, not to *what* it achieves. Brittle tests are expensive: every refactor breaks them, so people stop refactoring or stop trusting the suite.

Assert on the **outcome that matters**: `gw.charge.assert_called_once_with(10)` and `assert checkout(...) == 10`. Leave out the incidental calls.

### 9.3 Mocks that lie

A mock does what you told it, not what the real thing does. If the real `get_user(id)` raises `KeyError` for an unknown id, and your mock returns `None`, your code will handle `None` beautifully, and then crash in production on `KeyError`. The test suite said "all green". The fix is the one from sections 7.4 and 8.4: use `spec`/`autospec`, prefer **fakes** that are checked by contract tests, and run at least some tests against the real thing.

### 9.4 Mock explosion

If a test needs five mocks, each with a `return_value` that returns another mock, the code has too many dependencies, or the test is at the wrong level. Warning signs: the test setup is longer than the code under test; the test breaks when you rename a private helper; you cannot say in one sentence what behaviour it protects. The usual cures: inject a **fake** instead, test at a higher level (integration, section 14), or simplify the design.

### 9.5 A decision guide

| Situation | Prefer |
|---|---|
| Pure logic (maths, parsing, formatting) | no doubles at all |
| Slow, random or unsafe collaborator (network, clock, e-mail) | inject a stub, fake or spy |
| Need to assert a side effect (an e-mail was requested) | spy or `Mock(spec=...)`, assert only the essential call |
| Collaborator with rich behaviour (a repository) | an in-memory **fake** + a contract test |
| Code you cannot change, hard-wired call | `patch` where the name is looked up |
| Whole feature across layers | integration test with real parts (`tmp_path`) |

#### Try it 9.1

A test replaces `parse_price` with a mock returning `10.0`, then calls `total_of(["Rs 10"])` which uses `parse_price`, and asserts `10.0`. If `parse_price` had a bug, would the test fail?

<details><summary>Answer</summary>

No. The buggy function is never executed; the mock answers instead. To test `total_of` you can let the real `parse_price` run (it is pure logic with no outside world). Test `parse_price` itself separately with several inputs.

</details>

## 10. Testing time, randomness, files and network

Four things make tests depend on **the world**: the clock, random numbers, the disk and the network. Each has the same cure: make the world **an input**.

### 10.1 Time: inject a clock

```python
# cache.py
import time


class ExpiringCache:
    def __init__(self, ttl, clock=time.monotonic):
        self.ttl = ttl
        self.clock = clock
        self._data = {}

    def put(self, key, value):
        self._data[key] = (value, self.clock() + self.ttl)

    def get(self, key, default=None):
        item = self._data.get(key)
        if item is None:
            return default
        value, expires = item
        if self.clock() >= expires:
            del self._data[key]
            return default
        return value
```

The cache takes a `clock` function, defaulting to the real one. A test passes a **fake clock** that it controls. No `sleep`, no waiting:

```python
class FakeClock:
    def __init__(self, start=100.0):
        self.now = start

    def __call__(self):
        return self.now

    def advance(self, seconds):
        self.now += seconds


def test_value_lives_until_ttl():
    clock = FakeClock()
    cache = ExpiringCache(ttl=5, clock=clock)
    cache.put("k", "v")
    clock.advance(4.9)
    assert cache.get("k") == "v"
    clock.advance(0.1)
    assert cache.get("k") is None, "expires exactly at ttl"
```
```text
.                                                                        [100%]
```

The test covers a five-second timeout in a few thousandths of a second, and it tests the **boundary** exactly (4.9 s alive, 5.0 s dead), which a real `sleep` could never do reliably.

If you cannot change the signature, wrap the clock in a tiny module-level function and patch that, as in this example with `datetime`:

```python
# greeting.py
from datetime import datetime

def now():
    return datetime.now()

def greeting():
    return "Good morning" if now().hour < 12 else "Good afternoon"
```
```python
def test_morning(monkeypatch):
    monkeypatch.setattr(greeting, "now", lambda: datetime(2025, 1, 1, 9, 30))
    assert greeting.greeting() == "Good morning"

def test_afternoon(monkeypatch):
    monkeypatch.setattr(greeting, "now", lambda: datetime(2025, 1, 1, 15, 0))
    assert greeting.greeting() == "Good afternoon"
```
```text
..                                                                       [100%]
```

Why a wrapper function `now()`? You cannot patch `datetime.now` directly: `datetime` is a built-in type, whose attributes cannot be replaced. A named function in *your* module is easy to patch. Never use `time.sleep` in a test to "wait for" a timeout: it makes the suite slow, and still races against the machine's speed (section 13).

### 10.2 Randomness: seed it or inject it

Random code is tested in two ways. **Inject the generator**, so the test passes `random.Random(seed)`. Or **test a property** that holds for every random outcome.

```python
# shuffle_game.py
import random


def deal(players, rng=None):
    rng = rng or random.Random()
    deck = list(range(1, 11))
    rng.shuffle(deck)
    return {p: deck[i] for i, p in enumerate(players)}
```

A `random.Random(1)` object is **reproducible**: the same seed always gives the same sequence (on a given Python version; the exact numbers below may differ on other versions of Python, but within one version they never change):

```python
print(deal(["a", "b", "c"], random.Random(1)))
print(deal(["a", "b", "c"], random.Random(1)))
print(deal(["a", "b", "c"], random.Random(2)))
```
```text
{'a': 7, 'b': 9, 'c': 10}
{'a': 7, 'b': 9, 'c': 10}
{'a': 6, 'b': 10, 'c': 4}
```

Do **not** assert the exact numbers in your test. They would break whenever Python changes its algorithm. Assert a **property** over many seeds:

```python
def test_everyone_gets_distinct_cards():
    for seed in range(50):
        hands = deal(["a", "b", "c"], random.Random(seed))
        assert len(set(hands.values())) == 3, f"duplicate card with seed {seed}"


def test_same_seed_same_deal():
    assert deal(["a", "b"], random.Random(7)) == deal(["a", "b"], random.Random(7))
```
```text
..                                                                       [100%]
```

The loop over 50 seeds is a hand-made version of what section 12 (`hypothesis`) automates. Note the message in the assert: if seed 31 fails, you can rerun it exactly.

### 10.3 Files: `tmp_path` and a clean boundary

Files are easy now (section 6). Separate **pure logic** from **I/O** (a `summarise(rows)` that takes a list needs no file; a thin `main(path)` reads and calls it), and accept a **path argument** instead of hard-coding `"data/input.csv"`, so tests can point at `tmp_path`.

### 10.4 Network: inject the opener, and install a guard

Network code gets the same treatment as time: the function takes the thing that talks to the world.

```python
# fetcher.py
import json
import urllib.request


def get_json(url, opener=urllib.request.urlopen):
    with opener(url) as resp:
        return json.loads(resp.read().decode("utf-8"))


def user_name(user_id, opener=urllib.request.urlopen):
    data = get_json(f"https://api.example.com/users/{user_id}", opener)
    return data["name"].title()
```

The fake opener returns bytes, behaving like a response (note `io.BytesIO` is a file-like object (from the files chapter), and a response must work as a context manager):

```python
import io


class FakeResponse(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False


def fake_opener(payload):
    def opener(url):
        opener.seen.append(url)
        return FakeResponse(payload)
    opener.seen = []
    return opener


def test_user_name_is_title_cased():
    opener = fake_opener(b'{"name": "asha rao"}')
    assert fetcher.user_name(7, opener) == "Asha Rao"
    assert opener.seen == ["https://api.example.com/users/7"]
```

A fake that records `seen` is a spy; the test also checked that the right URL was requested. There is one more danger: **forgetting to inject**. A test that calls `fetcher.user_name(7)` with no opener would use the real network, would be slow, and would pass or fail by luck. A cheap safety net is an **autouse fixture in `conftest.py`** that makes any real network attempt fail loudly:

```python
# conftest.py
import socket
import pytest


@pytest.fixture(autouse=True)
def no_network(monkeypatch):
    def blocked(*args, **kwargs):
        raise AssertionError("test tried to use the real network!")
    monkeypatch.setattr(socket, "socket", blocked)
    monkeypatch.setattr(socket, "create_connection", blocked)
```
```python
def test_forgot_to_inject():
    fetcher.user_name(7)
```
```text
.F                                                                       [100%]
E   AssertionError: test tried to use the real network!
FAILED test_fetcher.py::test_forgot_to_inject - AssertionError: test tried to use the real network!
```

(The first dot is `test_user_name_is_title_cased`.) The failure message names the mistake. Guards like this turn "mysteriously slow test" into "clear error on the guilty test".

#### Try it 10.1

You test a function `is_expired(created_at)` that calls `time.time()` internally and cannot be changed to take a clock. What are two ways to test it without sleeping?

<details><summary>Answer</summary>

1. Patch the clock where it is looked up: if the module does `import time`, use `monkeypatch.setattr(time, "time", lambda: 1_000.0)` (this patches the shared `time` module for the duration of the test). 2. Better: change the function to accept `now` as a parameter (default: the real time) and pass a number in the test. Passing the value is the simplest seam.

</details>

## 11. Coverage

### 11.1 What coverage measures

**Coverage** answers one narrow question: *"While the tests ran, which lines of my code were executed?"* `coverage.py` watches the program run and records every line that was reached. Lines that never ran are **uncovered**, and uncovered code is code that no test can possibly be checking.

Take `grade.py`:

```python
def letter(score):
    if score < 0 or score > 100:
        raise ValueError("score out of range")
    if score >= 90:
        grade = "A"
    elif score >= 75:
        grade = "B"
    else:
        grade = "C"
    return grade


def bonus(score, extra_credit):
    result = score
    if extra_credit:
        result += 5
    return result
```

with these tests:

```python
from grade import letter, bonus


def test_a():
    assert letter(95) == "A"


def test_b():
    assert letter(80) == "B"


def test_bonus_yes():
    assert bonus(50, True) == 55


def test_bonus_no_but_weak():
    assert bonus(50, False) == 50
```

Run the tests under coverage, then print a report:

```text
$ python -m coverage run -m pytest -q
$ python -m coverage report -m
Name       Stmts   Miss  Cover   Missing
----------------------------------------
grade.py      14      2    86%   3, 9
----------------------------------------
TOTAL         14      2    86%
```

`Stmts` is the number of executable statements, `Miss` the number never run, and `Missing` lists their **line numbers**: line 3 (the `raise` for a bad score) and line 9 (`grade = "C"`). That tells you exactly which tests to write next: a score of 120 and a score of 50. (Without `-m`, the `Missing` column is not shown.)

### 11.2 Line coverage versus branch coverage

Line coverage has a blind spot. Look at `bonus` alone, with only the "yes" test:

```python
def bonus(score, extra_credit):
    result = score
    if extra_credit:
        result += 5
    return result
```
```text
$ python -m coverage run -m pytest -q test_bonus1.py
$ python -m coverage report -m
bonus.py       5      0   100%
```

All five lines ran, so 100%. But the **`False` path** of the `if` was never taken: nobody tested a call without extra credit. A line-coverage tool cannot see a path that has no line of its own. Turn on **branch coverage** with `--branch`:

```text
$ python -m coverage run --branch -m pytest -q test_bonus1.py
$ python -m coverage report -m
Name         Stmts   Miss Branch BrPart  Cover   Missing
--------------------------------------------------------
bonus.py         5      0      2      1    86%   3->5
--------------------------------------------------------
TOTAL            5      0      2      1    86%
```

`BrPart` means "branches partly covered" and `3->5` reads: "the jump from line 3 (the `if`) to line 5 (the `return`) never happened". That jump is exactly the "condition was false" path. **Always use `--branch`** (or `branch = True` in a config file).

### 11.3 The coverage API

The command line is for humans. Your own code, and this module's grader, can drive coverage from Python:

```python
import coverage

cov = coverage.Coverage(branch=True, data_file=None, include=["grade.py"])
cov.start()
import grade
grade.letter(95); grade.bonus(1, True)
cov.stop()
filename, statements, excluded, missing, missing_str = cov.analysis2("grade.py")
print("statements:", statements)
print("missing:", missing)
print("percent:", round(cov.report(file=open("/dev/null", "w")), 1))
```
```text
statements: [1, 2, 3, 4, 5, 6, 7, 9, 10, 13, 14, 15, 16, 17]
missing: [3, 6, 7, 9]
percent: 59.1
```

`data_file=None` keeps the data in memory (no `.coverage` file is written). `analysis2` returns lists of line numbers; `report()` returns the total percentage (and prints a table to `file`; here a throw-away file). Note the percentage is lower than 86% because this run called fewer functions.

### 11.4 Useful options and a config file

A `.coveragerc` file avoids long commands. Useful settings: `branch = True`, `omit = test_*.py` (do not measure the tests themselves; they are always 100% covered, which inflates the number), and `fail_under = 80`, which makes `coverage report` exit with code 2 and print `Coverage failure: total of 39 is less than fail-under=80` when the total is too low. This is how a build can **fail on a coverage drop**. Lines can be excluded with `exclude_also` patterns or with a `# pragma: no cover` comment (use rarely, and with a reason). `coverage html` writes a folder `htmlcov/` with a colour-coded page for each file: red lines were never run. It is the nicest way to explore.

### 11.5 What coverage does NOT prove

Coverage tells you which code ran. It does **not** tell you the code was *checked*. Here is a function with a bug and tests that have **100% line and branch coverage**:

```python
def average(nums):
    if not nums:
        return 0
    return sum(nums) // len(nums)    # BUG: floor division
```
```python
def test_empty():
    assert average([]) == 0

def test_even():
    assert average([2, 4]) == 3
```
```text
Name     Stmts   Miss Branch BrPart  Cover   Missing
----------------------------------------------------
avg.py       4      0      2      0   100%
```

Yet `average([1, 2])` returns `1`, not `1.5`. Both tests use inputs where floor division happens to give the right answer. Every line ran; no test would notice the bug. Coverage can also be inflated by a test with no `assert` at all: it runs the code and checks nothing.

So treat coverage as a **one-way signal**:

- **Low coverage tells you the truth**: that code is untested.
- **High coverage tells you little**: the code ran, perhaps without any real check.

Do not set a goal like "100% or nothing". Chasing the number leads to silly tests that call everything and assert nothing. Use coverage to **find holes**, and use the mutation question (section 15.3) to judge the quality of the tests you have.

#### Try it 11.1

A function has one `if x > 0: ... else: ...` with a statement in each part. Your single test calls it with `x = 5`. Roughly what are the line coverage and the branch coverage?

<details><summary>Answer</summary>

Line coverage is below 100%: the `else` statement never ran (it is listed in `Missing`). Branch coverage is lower still, since one of the two branches from the `if` was never taken. Adding a test with `x = -1` brings both to 100%.

</details>

#### Try it 11.2

Your team requires "100% coverage". A developer writes `def test_run(): process(data)` with no assert, and coverage hits 100%. Why is this dangerous, and what question should reviewers ask?

<details><summary>Answer</summary>

The test executes every line but would pass even if `process` returned garbage, so the number is meaningless. Reviewers should ask: "If I introduced a bug in this function, which assertion would fail?" If no test would fail, the coverage is decoration.

</details>

## 12. Property-based testing with hypothesis

### 12.1 Examples versus properties

Example-based tests check **chosen inputs**: `sorted([3, 1, 2]) == [1, 2, 3]`. They are only as good as your imagination. You pick the inputs *you* thought of, and the bugs live at the inputs you did not.

A **property** is a statement that must hold for **all** inputs of some kind: "sorting a list never changes its length", "reversing twice gives the original". **`hypothesis`** is a library that **generates** many inputs for you, checks the property on each, and, when one fails, **shrinks** it to the smallest failing example.

```python
from hypothesis import given, settings, strategies as st

CFG = settings(derandomize=True, database=None, max_examples=100)


@CFG
@given(st.lists(st.integers()))
def test_reverse_twice_is_identity(xs):
    assert list(reversed(list(reversed(xs)))) == xs


@CFG
@given(st.lists(st.integers()))
def test_sorted_is_ordered_and_same_length(xs):
    out = sorted(xs)
    assert len(out) == len(xs)
    assert all(a <= b for a, b in zip(out, out[1:]))
```
```text
..                                                                       [100%]
```

Read the pieces:

- `@given(st.lists(st.integers()))`: "call this test with a list of integers, many times". The argument `xs` receives one generated list per run. `st.lists(st.integers())` is a **strategy**: a recipe for making values.
- `settings(max_examples=100)`: try up to 100 inputs.
- `derandomize=True`: choose the inputs the same way every time. This makes the run **repeatable**: it matters in this course, where a test must give the same result on every machine.
- `database=None`: do not store failures in a `.hypothesis` folder.

Put `@settings` above `@given`. In a real project you would normally leave randomisation on (it finds new bugs on each run) and let hypothesis remember failures in its database. In this course everything is derandomized so that a result does not depend on luck.

### 12.2 Strategies: building the data

A strategy describes a set of values. The common ones:

| Strategy | Generates |
|---|---|
| `st.integers()`, `st.integers(min_value=1, max_value=6)` | ints, optionally bounded |
| `st.floats()`, `st.booleans()`, `st.none()` | floats (including `nan`, `inf`!), bools, `None` |
| `st.text()`, `st.text(alphabet="abc", min_size=1, max_size=3)` | strings |
| `st.lists(elements, min_size=..., max_size=..., unique=True)` | lists |
| `st.tuples(a, b)` | tuples of fixed shape |
| `st.dictionaries(keys, values)` | dicts |
| `st.sampled_from(["red", "green"])` | one item of a list |
| `st.one_of(a, b)` | values of either strategy |
| `st.builds(Class, field=strategy)` | objects, by calling a class |
| `st.just(5)` | always that value |

To *see* what a strategy produces, collect a few examples inside a test (this is deterministic because of `derandomize`):

```text
integers     [1, 3, 5, 6, 4] | distinct: 6
text         ['a', 'bbc', 'bb', 'ccc', 'baa'] | distinct: 30
lists        [[0, 0], [3, 0], [3, 4], [4, 0], [4, 7, 3]] | distinct: 30
tuples       [(False, 0), (True, 0), (True, 3), (True, 1), (True, 2)] | distinct: 8
dict         [{}, {'x': 0}, {'z': 5}, {'z': 0}, {'z': 0, 'y': 6}] | distinct: 30
one_of       [None, 0, 5, 3, 4] | distinct: 7
sampled      ['red', 'green', 'blue'] | distinct: 3
```

(These came from 30 runs of `integers(1, 6)`, `text(alphabet="abc", min_size=1, max_size=3)`, `lists(integers(0, 9), min_size=2, max_size=3)`, `tuples(booleans(), integers(0, 3))`, `dictionaries(sampled_from("xyz"), integers(0, 9), max_size=2)`, `one_of(none(), integers(0, 5))` and `sampled_from(["red", "green", "blue"])`. The exact values depend on the hypothesis version, but the *shapes* will match.) Notice that bounded strategies still try the edges (`{}`, `0`, `[0, 0]`): hypothesis likes boundaries.

Two more tools: `st.builds(Rect, w=st.integers(1, 100), h=st.integers(1, 100))` fills a class's arguments from strategies, and a function decorated with `@st.composite` that receives `draw` lets you write a strategy as code, where later draws depend on earlier ones (`high = draw(st.integers(low + 1, 100))` makes `high` always greater than `low`).

### 12.3 Shrinking: the counterexample you can read

Here is an insertion sort with a bug: it skips values that are already in the output, so it silently **drops duplicates**.

```python
def my_sort(xs):
    """Insertion sort with a bug: it drops duplicates."""
    out = []
    for x in xs:
        if x in out:
            continue
        i = 0
        while i < len(out) and out[i] < x:
            i += 1
        out.insert(i, x)
    return out
```
```python
@settings(derandomize=True, database=None, max_examples=100)
@given(st.lists(st.integers()))
def test_my_sort_keeps_length(xs):
    assert len(my_sort(xs)) == len(xs)
```
```text
F                                                                        [100%]
E   assert 1 == 2
E    +  where 1 = len([0])
E    +    where [0] = my_sort([0, 0])
E    +  and   2 = len([0, 0])
E   Failing test case: test_my_sort_keeps_length(
E       xs=[0, 0],
E   )
```

(This result was identical on two runs.) The first failing input found was probably long and messy. Hypothesis then **shrinks** it: it tries removing items and making numbers smaller, as long as the test still fails, until nothing can be simplified. The answer, `xs=[0, 0]`, is the smallest list that triggers the bug: a list with a duplicate. You read the bug straight from the example. That is the second gift of property testing: failures arrive **already minimised**.

### 12.4 Which properties to write

Finding properties is the creative part. These patterns cover most cases:

| Pattern | Statement | Example |
|---|---|---|
| **Round trip** | `decode(encode(x)) == x` | serialise/parse, compress/uncompress |
| **Idempotence** | doing it twice equals doing it once: `f(f(x)) == f(x)` | normalise whitespace, remove duplicates |
| **Invariant** | something stays true about the output | sorted output is ordered, same length, same elements |
| **Oracle** | compare with a slow, obviously-correct version | fast algorithm versus brute force |
| **Bounds / relations** | output stays inside a range; `f(a+b)` relates to `f(a)`, `f(b)` | a clamp stays within `[lo, hi]` |

**Round trip.** A run-length encoder (`"aaabcc"` becomes `"3a1b2c"`):

```python
def encode(text):
    out = []
    i = 0
    while i < len(text):
        j = i
        while j < len(text) and text[j] == text[i]:
            j += 1
        out.append(f"{j - i}{text[i]}")
        i = j
    return "".join(out)


def decode(code):
    out = []
    count = ""
    for ch in code:
        if ch.isdigit():
            count += ch
        else:
            out.append(ch * int(count))
            count = ""
    return "".join(out)
```
```python
@settings(derandomize=True, database=None, max_examples=100)
@given(st.text(alphabet=st.characters(min_codepoint=32, max_codepoint=126)))
def test_round_trip_ascii(s):
    assert decode(encode(s)) == s
```
```text
F                                                                        [100%]
E   AssertionError: assert '' == '0'
E     - 0
E   Failing test case: test_round_trip_ascii(
E       s='0',
E   )
```

(Identical on two runs.) The example-based test `encode("aaabcc") == "3a1b2c"` passes. But the input `"0"` encodes to `"10"` ("one zero"), and `decode` reads both characters as digits, so the count becomes 10 and no character ever follows. The format is **ambiguous when the text itself contains digits**. No human thought of testing the character `"0"`; hypothesis found it in under a second. (With `st.text()` and *all* of Unicode it finds even more: the digit `¹` passes `isdigit()` but crashes `int()`. Real data is full of surprises.)

**Idempotence.** A whitespace normaliser that should collapse runs of spaces:

```python
def normalise(text):
    """Collapse runs of spaces to one space and strip the ends."""
    return " ".join(text.split(" ")).strip()
```
```python
@CFG
@given(st.text(alphabet=" ab"))
def test_idempotent(s):
    once = normalise(s)
    assert normalise(once) == once


@CFG
@given(st.text(alphabet=" ab"))
def test_no_double_spaces(s):
    assert "  " not in normalise(s)
```
```text
.F                                                                       [100%]
E   AssertionError: assert '  ' not in 'a  a'
E     '  ' is contained here:
E       a  a
E   Failing test case: test_no_double_spaces(
E       s='a  a',
E   )
```

A sharp lesson: the **idempotence** property passed, although the function is wrong. `split(" ")` followed by `" ".join` does nothing at all, so applying it twice trivially equals applying it once. One property is rarely enough; the second (`no double spaces`) found the bug. Combine properties, and keep a few example tests as well: `normalise("a  b") == "a b"` would have caught this immediately. Property tests and example tests are **partners**, not rivals.

**Oracle.** A fast one-pass "largest sum of a slice" with a subtle bug, checked against a slow brute force:

```python
def max_subarray(nums):
    """Largest sum of a non-empty contiguous slice (fast, one pass)."""
    best = cur = 0           # BUG: should start from nums[0]
    for n in nums:
        cur = max(n, cur + n)
        best = max(best, cur)
    return best
```
```python
def slow_max_subarray(nums):
    return max(sum(nums[i:j]) for i in range(len(nums))
               for j in range(i + 1, len(nums) + 1))


@settings(derandomize=True, database=None, max_examples=100)
@example([1, -2, 3])
@given(st.lists(st.integers(-5, 5), min_size=1, max_size=8))
def test_matches_slow_version(nums):
    assert max_subarray(nums) == slow_max_subarray(nums)
```
```text
E   assert 0 == -1
E    +  where 0 = max_subarray([-1])
E    +  and   -1 = slow_max_subarray([-1])
E   Failing test case: test_matches_slow_version(
E       nums=[-1],
E   )
```

`@example([1, -2, 3])` (from `hypothesis import example`) adds a hand-picked case that always runs. Hypothesis then shrinks the failure to `[-1]`: when every number is negative, the fast version wrongly answers `0`, because it started with `best = 0`. The oracle pattern is the strongest of all: the slow version is so simple that it is obviously right, so *any* disagreement is a bug in the fast one.

### 12.5 `assume`, `filter` and constructive strategies

Sometimes a property only makes sense for some inputs: dividing needs a non-zero divisor. You can **reject** unwanted inputs with `assume(...)` or `.filter(...)`, or **construct** only valid ones:

```python
@CFG
@given(st.integers(), st.integers())
def test_filtered(a, b):
    assume(b != 0)
    assert (a // b) * b + a % b == a


@CFG
@given(st.integers(), st.integers(min_value=1))
def test_constructive(a, b):
    assert (a // b) * b + a % b == a
```
```text
..                                                                       [100%]
```

All variants pass. Rejecting is fine when only a **few** inputs are discarded (`b != 0` discards almost none). But if you throw most inputs away, hypothesis gives up:

```python
@settings(derandomize=True, database=None)
@given(st.integers())
def test_too_picky(n):
    assume(n == 123456789)
    assert True
```
```text
E   hypothesis.errors.FailedHealthCheck: It looks like this test is filtering out a lot of inputs. 0 inputs were generated successfully, while 50 inputs were filtered out.
```

This is a **health check**: hypothesis protects you from a test that never really runs. The cure is to **construct** valid data instead of filtering: `st.integers(min_value=1)` rather than `st.integers().filter(lambda b: b > 0)`; `st.lists(...).map(sorted)` rather than "generate a list, assume it is sorted". Construction is faster and never starves.

#### Try it 12.1

Which property would you write for `my_max(xs)` (largest of a non-empty list), without re-implementing `max`? Name at least two.

<details><summary>Answer</summary>

Examples: the result is **in** the list (`my_max(xs) in xs`); **no element is larger** (`all(x <= my_max(xs) for x in xs)`); adding a smaller element does not change the result; the result of `my_max(xs + ys)` equals `max(my_max(xs), my_max(ys))`. Together the first two already define "largest".

</details>

#### Try it 12.2

Hypothesis reports `Failing test case: test_parse(s='0')` for a `parse_time(s)` function that expects `"HH:MM"`. Is the bug in the test or the function?

<details><summary>Answer</summary>

It depends on the specification, which is the first thing to check. If `parse_time` is documented to accept only `"HH:MM"`, then the *test's strategy* is too wide (generating arbitrary text) and should use a strategy that builds valid times, OR the function should raise a clear `ValueError` for bad input and the test should assert that. If the spec says "any text is allowed and bad text returns `None`", the function is wrong. Never "fix" the test just to make hypothesis stop reporting: decide what is *right*, as in chapter 8, section 5.

</details>

## 13. Flaky tests

A **flaky** test sometimes passes and sometimes fails **with the same code**. Flaky tests are poison: people rerun the suite "until it is green", real failures hide among false alarms, and trust dies. Fixing flakiness is not optional. The good news: nearly every flaky test has one of five causes.

### 13.1 Cause 1: shared state and test order

Tests must not depend on each other. Here they do:

```python
registry = []

def register(name):
    registry.append(name)
    return len(registry)

def test_first_user_gets_id_1():
    assert register("asha") == 1

def test_second_user_gets_id_2():
    assert register("ravi") == 2
```
```text
..                                                                       [100%]
```

Green, but only by accident. Run the second test **alone**, or run the file in the reverse order, and:

```text
$ python -m pytest "test_state.py::test_second_user_gets_id_2" --tb=line
E   AssertionError: assert 1 == 2
FAILED test_state.py::test_second_user_gets_id_2 - AssertionError: assert 1 == 2
```
```text
$ (same file, tests run in reverse order)
FF
FAILED test_state.py::test_second_user_gets_id_2 - AssertionError: assert 1 == 2
FAILED test_state.py::test_first_user_gets_id_1 - AssertionError: assert 2 == 1
```

The cure is to **reset the shared state** around each test with a fixture, or better, not to share it:

```python
import pytest
import test_state as t

@pytest.fixture(autouse=True)
def clean_registry():
    t.registry.clear()
    yield
    t.registry.clear()

def test_ids_start_at_1():
    assert t.register("asha") == 1
```
```text
.                                                                       [100%]
```

A useful habit: run the suite in **random order** now and then (the `pytest-randomly` plugin does this) and run each test **alone** while writing it. An order-dependent test shows itself immediately.

### 13.2 Cause 2: set and dict ordering, hash randomisation

Python randomises string hashes **per process**, so the iteration order of a `set` of strings changes from run to run:

```python
tags = {"red", "green", "blue"}
print(list(tags))
```
```text
$ PYTHONHASHSEED=1 python setorder.py
['red', 'green', 'blue']
$ PYTHONHASHSEED=2 python setorder.py
['blue', 'green', 'red']
```

(The exact orders are machine- and version-specific; the point is that they differ.) A test that compares `list(tags)` to a fixed list passes on some runs only. Compare **sets** with sets (`assert tags == {"red", "green", "blue"}`) or sort first (`sorted(tags)`). Dictionaries keep insertion order, which is reliable, but building them from a set inherits the set's disorder.

### 13.3 Cause 3: time and timing

Two sub-cases. (a) Code that reads the real clock (`datetime.now()`, "is it after 9 a.m.?") gives different answers at different times: tests may pass all day and fail at midnight, at the end of a month, or on 29 February. Cure: inject or patch the clock (section 10.1). (b) Tests that **measure speed**:

```python
import time

def test_fast_enough():
    start = time.perf_counter()
    time.sleep(0.02)
    assert time.perf_counter() - start < 0.021
```

This usually passes, and sometimes fails when the machine is busy (a sleep of 0.02 s may take 0.022 s). It asserts something about the *computer*, not the code. Cure: do not assert on wall-clock speed in unit tests; use a fake clock; if you must check "does not hang", give a very generous limit (`timeout=10`).

### 13.4 Causes 4 and 5: randomness, and concurrency

**Randomness** with no seed makes the test depend on luck: seed it or inject the generator (10.2). In `hypothesis`, `derandomize=True` plays this role.

**Concurrency** (threads, processes, background jobs) lets two things happen in an unpredictable order. A test that starts a thread and checks the result immediately is a race. Cure: wait for a clear signal (`thread.join()`, a queue, an `Event`), never for a time (`sleep(1)`), and test the logic single-threaded wherever possible.

### 13.5 A checklist for a flaky test

1. **Run it alone**, ten times. Passes alone but fails in the suite: shared state or order (13.1).
2. **Run the whole suite in reverse or random order.** Fails: order dependence.
3. Does the code read the **clock**, **random numbers**, a **set order**, the **network** or the **real file system**? Replace each with a controlled input.
4. Does the test use `sleep` or compare **timings**? Remove that.
5. Capture the failure: `pytest -x` stops at the first one; `pytest --lf` ("last failed") reruns only the tests that failed last time (it uses a small cache folder, which this chapter switched off so that the examples stay clean).
6. Never "fix" a flaky test by **rerunning** it or **adding a retry**. A retry hides the bug; it does not remove it.

#### Try it 13.1

A test passes when you run `pytest test_report.py`, but fails when you run `pytest` for the whole project. Name the two most likely causes.

<details><summary>Answer</summary>

(1) Shared state: another test file changes a global, environment variable or file that this test depends on, or this test depends on state that a test in its own file normally sets up. (2) A wider-scoped fixture or a module-level object mutated by an earlier test. Run the suite in different orders and print/inspect the shared object to find the leak, then reset it with a fixture.

</details>

## 14. Integration and end-to-end tests

### 14.1 Testing the pieces together

Unit tests prove that each function works alone. They cannot prove that the functions **fit**: that `clean` really outputs what `totals` expects, that the CSV column is called `amount` and not `Amount`. **Integration tests** run several real parts together. Here is a small tool, `tally.py`, that sums an `amount` column per `category` (shown in full because the tests need it):

```python
"""tally: sum the 'amount' column of a CSV, grouped by 'category'."""
import argparse
import csv
import sys


def read_rows(path):
    with open(path, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def clean(rows):
    good = []
    for row in rows:
        try:
            amount = float(row["amount"])
        except (KeyError, ValueError):
            continue
        good.append({"category": row["category"].strip().lower(), "amount": amount})
    return good


def totals(rows):
    out = {}
    for row in rows:
        out[row["category"]] = out.get(row["category"], 0) + row["amount"]
    return out


def format_report(totals_by_cat):
    lines = [f"{cat:<10}{amount:>8.2f}" for cat, amount in sorted(totals_by_cat.items())]
    return "\n".join(lines)


def main(argv=None):
    parser = argparse.ArgumentParser(prog="tally")
    parser.add_argument("csv_file")
    parser.add_argument("--min", type=float, default=0.0, dest="minimum")
    args = parser.parse_args(argv)
    try:
        rows = read_rows(args.csv_file)
    except FileNotFoundError:
        print(f"error: no such file: {args.csv_file}", file=sys.stderr)
        return 2
    rows = [r for r in clean(rows) if r["amount"] >= args.minimum]
    print(format_report(totals(rows)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

Two design choices make it testable: the pieces are small functions that take data, and `main(argv=None)` takes the argument list as a **parameter** and **returns** an exit code instead of calling `sys.exit` itself (the `if __name__` block does that). That is the seam for testing a command-line tool *in-process*.

First, a fixture that writes a CSV into `tmp_path`: a **factory** (section 2.7) so each test chooses its own rows:

```python
@pytest.fixture
def csv_file(tmp_path):
    def make(*lines):
        path = tmp_path / "data.csv"
        path.write_text("\n".join(("category,amount",) + lines) + "\n")
        return path
    return make


def test_pipeline_end_to_end(csv_file):
    path = csv_file("Food,10", "food ,5.5", "Rent,100", "Food,oops", "Rent,")
    assert tally.totals(tally.clean(tally.read_rows(path))) == {"food": 15.5, "rent": 100.0}
```

This **integration test** chains `read_rows`, `clean` and `totals` over a real file, including messy rows: different capitals, a trailing space, a non-number and an empty amount. Together they must produce the right totals. Test boundaries like this on purpose; this is where "works alone, fails together" bugs live.

### 14.2 Testing a command-line tool in-process

Because `main` takes `argv` and returns an exit code, tests call it directly and use `capsys` to read what it printed:

```python
def test_main_prints_report(csv_file, capsys):
    path = csv_file("Food,10", "Rent,100")
    code = tally.main([str(path)])
    out, err = capsys.readouterr()
    assert code == 0
    assert out == "food         10.00\nrent        100.00\n"
    assert err == ""


def test_main_min_option(csv_file, capsys):
    path = csv_file("Food,10", "Rent,100")
    assert tally.main([str(path), "--min", "50"]) == 0
    assert capsys.readouterr().out == "rent        100.00\n"


def test_main_missing_file(tmp_path, capsys):
    code = tally.main([str(tmp_path / "nope.csv")])
    assert code == 2
    assert "no such file" in capsys.readouterr().err


def test_bad_option_exits_with_2(capsys):
    with pytest.raises(SystemExit) as info:
        tally.main(["x.csv", "--min", "abc"])
    assert info.value.code == 2
```

The last test shows a detail: when `argparse` rejects the arguments it calls `sys.exit(2)` itself, which raises `SystemExit`. `pytest.raises(SystemExit)` catches it and lets you check the code. Testing in-process is fast and lets you inspect everything.

### 14.3 One true end-to-end test with `subprocess`

In-process tests skip one thing: the real **program start-up**: the `if __name__ == "__main__"` block, the interpreter, the real exit code. One test should run the program as a user would:

```python
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).parent


def test_real_process(csv_file):
    path = csv_file("Food,10")
    done = subprocess.run([sys.executable, str(HERE / "tally.py"), str(path)],
                          capture_output=True, text=True, timeout=10)
    assert done.returncode == 0
    assert done.stdout == "food         10.00\n"
```

Use `sys.executable` (the same Python that runs the tests, never the text `"python"`), `capture_output=True, text=True` to get strings, and **always a `timeout`** so a hanging program cannot freeze the suite. All six tests pass. Notice the shape: five fast in-process tests and **one** slow subprocess test: a tiny pyramid.

### 14.4 Test data builders

When objects have many fields, writing all of them in every test buries the one field that matters. A **builder** (or object mother) function gives sensible defaults and lets the test override only what it cares about:

```python
from dataclasses import dataclass, replace


@dataclass
class Ticket:
    id: int
    title: str
    priority: str
    assignee: str | None
    done: bool

    def is_urgent_unassigned(self):
        return self.priority == "high" and self.assignee is None and not self.done


def make_ticket(**overrides):
    base = Ticket(id=1, title="Fix login", priority="low", assignee="asha", done=False)
    return replace(base, **overrides)


def test_urgent_unassigned_true():
    assert make_ticket(priority="high", assignee=None).is_urgent_unassigned()


def test_done_tickets_are_never_urgent():
    assert not make_ticket(priority="high", assignee=None, done=True).is_urgent_unassigned()


def test_assigned_is_not_urgent():
    assert not make_ticket(priority="high").is_urgent_unassigned()
```
```text
...                                                                      [100%]
```

Each test mentions only the fields that *make it interesting*. A reader sees at once that "done" is what matters in the second test. If a field is added to `Ticket`, only `make_ticket` changes.

#### Try it 14.1

`tally.main(["--min"])` is called in a test. What happens, and how do you test it?

<details><summary>Answer</summary>

`argparse` finds the arguments invalid (`csv_file` is missing, and `--min` has no value) and exits with code 2, which raises `SystemExit`, after printing a usage message to stderr. Test it with `with pytest.raises(SystemExit) as info:` and `assert info.value.code == 2`, and read the usage message with `capsys.readouterr().err`.

</details>

## 15. Project walkthrough: a suite for a buggy codebase

This section shows **how to think** when you build a suite for code that may contain bugs, which is what this module's project asks you to do. The subject is a small parking-fee calculator. The rules are the **specification**, and they are all we trust:

```python
"""Parking fee rules.

* Up to and including 15 minutes: free.
* After that: Rs 20 for every started hour.
* A full day (24 h = 1440 min) never costs more than Rs 200; longer stays
  pay Rs 200 per full day plus the fee for the rest, itself capped at Rs 200.
* Members pay 75 percent of the total (whole rupees, rounded down).
* A lost ticket is a flat Rs 300 whatever the time and membership.
* Negative minutes are an error (ValueError).
"""
```

Someone hands you the code and says "it works, probably". Here is that code (it contains four bugs, marked here only so you can follow along; **in a real job nobody marks them**):

```python
DAY = 1440


def _day_fee(minutes):
    if minutes < 15:                      # bug A
        return 0
    hours = minutes // 60 + 1             # bug B
    return min(hours * 20, 200)


def fee(minutes, member=False, lost_ticket=False):
    if minutes < 0:
        raise ValueError("minutes cannot be negative")
    total = min(_day_fee(minutes), 200)   # bug C: no days
    if member:
        total = total * 75 // 100
    if lost_ticket:                       # bug D: after the discount
        total = 300 if not member else 225
    return total
```

### 15.1 Step 1: turn each rule of the spec into behaviours

Do **not** start by reading the code, because then you will test what the code does rather than what it should do (the trap from chapter 8, section 5). Walk through the specification and list, for every rule, the **normal case** and the **boundaries**:

| Rule | Cases to test |
|---|---|
| free up to and including 15 | 0, 15 (free), 16 (first paid minute) |
| Rs 20 per started hour | 60 (one hour exactly), 61 (second hour begins), 120, 121 |
| daily cap 200 | 1440 (exactly one day), a part-day long enough to hit the cap (700) |
| several days | 2 days + 61 minutes, to check "per full day plus the rest" |
| member discount | a value where rounding matters, a day, 0 |
| lost ticket | any time, member and non-member |
| negative | -1 raises `ValueError` |

The boundaries (15, 16, 60, 61, 1440) are the most valuable rows, because **bugs live at the edges**: a `<` that should be `<=`, an off-by-one, a cap applied once instead of per day.

### 15.2 Step 2: write the tests, with messages that name the bug

```python
import pytest
from parking import fee


def test_free_boundary():
    assert fee(15) == 0, "15 minutes is still free"


def test_started_hour():
    assert fee(60) == 20, "exactly one hour is one started hour"
    assert fee(61) == 40


def test_daily_cap():
    assert fee(1440) == 200


def test_two_days():
    assert fee(1440 * 2 + 61) == 440


def test_member_rounds_down():
    assert fee(1440, member=True) == 150


def test_lost_ticket_flat():
    assert fee(5, lost_ticket=True) == 300
    assert fee(5, member=True, lost_ticket=True) == 300


def test_negative():
    with pytest.raises(ValueError):
        fee(-1)
```

Check the numbers by hand from the spec, **not** from the code: 2 days = 400, plus 61 minutes = 2 started hours = 40, total 440. Then run against the buggy module:

```text
FF.F.F.                                                                  [100%]
E   AssertionError: 15 minutes is still free
    assert 20 == 0
E   AssertionError: exactly one hour is one started hour
    assert 40 == 20
E   assert 200 == 440
E   assert 225 == 300
    +  where 225 = fee(5, member=True, lost_ticket=True)
FAILED test_parking.py::test_free_boundary - AssertionError: 15 minutes is st...
FAILED test_parking.py::test_started_hour - AssertionError: exactly one hour ...
FAILED test_parking.py::test_two_days - assert 200 == 440
FAILED test_parking.py::test_lost_ticket_flat - assert 225 == 300
```

Four failures, four bugs found: A (the `<`), B (the rounding up of the hour), C (days) and D (lost ticket). Note which tests *passed* on buggy code: `test_daily_cap` and `test_member_rounds_down` happen to produce correct answers in the buggy version for those inputs. Passing proves little. Now run the same tests against the **correct** module and measure coverage with `--branch`:

```text
Name         Stmts   Miss Branch BrPart  Cover   Missing
--------------------------------------------------------
parking.py      16      0      8      0   100%
--------------------------------------------------------
```

With 100% line and branch coverage and all tests green, are we done? Section 11.5 says: **no**.

### 15.3 Step 3: the mutation question

*If I put a bug in the correct code, would a test notice?* You can ask this by hand: change one thing, rerun the tests, and hope for a failure. Doing it for dozens of changes is boring, so write a tiny script. It copies the correct module with **one change** each time and runs the tests; a change that no test notices is a **survivor**:

```python
"""Poor man's mutation testing: change one thing in parking.py, rerun the tests."""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

HERE = Path(__file__).parent
MUTATIONS = [
    ("<= 15", "< 15"),
    ("-(-minutes // 60)", "minutes // 60"),
    ("min(hours * 20, 200)", "hours * 20"),
    ("total * 75 // 100", "total * 3 // 4 + 1"),
    ("days * 200", "days * 100"),
    ("if minutes < 0", "if minutes < -1"),
    ("return 300", "return 299"),
]

source = (HERE / "parking.py").read_text()
for old, new in MUTATIONS:
    assert old in source, old
    with tempfile.TemporaryDirectory() as tmp:
        (Path(tmp) / "parking.py").write_text(source.replace(old, new, 1))
        shutil.copy(HERE / "test_parking.py", tmp)
        done = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "-x", tmp],
            capture_output=True, text=True, timeout=30)
    verdict = "killed " if done.returncode != 0 else "SURVIVED"
    print(f"{verdict}  {old!r} -> {new!r}")
```
```text
killed   '<= 15' -> '< 15'
killed   '-(-minutes // 60)' -> 'minutes // 60'
SURVIVED  'min(hours * 20, 200)' -> 'hours * 20'
killed   'total * 75 // 100' -> 'total * 3 // 4 + 1'
killed   'days * 200' -> 'days * 100'
killed   'if minutes < 0' -> 'if minutes < -1'
killed   'return 300' -> 'return 299'
```

A survivor, even though coverage is 100%! Removing the cap from the **part-day** fee goes unnoticed. Think about why: our only cap test used exactly 1440 minutes, which takes the "full days" path and never reaches the capped part-day branch with a long rest; and `test_two_days` has a rest of only 61 minutes. The code is *executed* but not *checked*. The fix is a test aimed at the survivor:

```python
def test_part_day_is_capped():
    assert fee(700) == 200, "12 started hours would be 240; the cap is 200"
```

(700 minutes is 12 started hours, so without the cap the fee would be 240.) Rerun the mutation script: that line now says `killed`. This tiny loop (spec, tests, coverage, mutation) is the whole method. Real mutation tools (such as `mutmut`) automate it, but the idea is exactly this script. Your module project is graded the same way: your tests must pass on correct code and **kill each seeded bug**.

### 15.4 A recipe you can reuse

Read the **spec**, not the code. For each rule write a normal case and the **boundaries** (0, 1, n-1, n, n+1, empty, negative). Hand-compute the expected values. Name the likely mistake in each assert message. Check **branch coverage** for holes, then ask the **mutation question** about each important line. For logic with many inputs, add a property test (section 12).

#### Try it 15.1

Add the mutation `("days * 200", "days * 201")` to the script's list. Predict: killed or survived? Which test notices?

<details><summary>Answer</summary>

Killed. `test_daily_cap` expects `fee(1440) == 200`, and with 201 it would return 201. `test_two_days` (expected 440) also fails. Exact `==` comparisons are what make tests strong.

</details>

## 16. Common traps and summary

### 16.1 Common traps

| Trap | What happens | Fix |
|---|---|---|
| Fixture with a wide scope that tests modify | tests depend on order; pass alone, fail together | function scope, or reset in an autouse fixture |
| Importing helpers from `conftest.py` | works on one machine only | helpers in a normal module; fixtures as parameters |
| `Mock()` with no `spec` | typos and wrong signatures pass silently | `create_autospec`, `Mock(spec=...)` |
| Patching where the name is *defined* | the real function still runs | patch where the name is *looked up* |
| Mocking the code under test | the test passes against broken code | mock neighbours only |
| Asserting every internal call | brittle: breaks on harmless refactors | assert outcomes |
| Fake that differs from the real thing | green tests, red production | contract tests, `spec`, some real runs |
| `sleep` in a test | slow and still racy | injected fake clock |
| Exact values from a seeded `random` | breaks on Python upgrade | assert properties, or inject the generator |
| Unregistered markers, `xfail` without `strict` | typos pass; fixed bugs stay "expected" | `--strict-markers`, `strict=True` |
| Coverage as a goal | tests that run everything, check nothing | coverage finds holes; mutation question judges tests |
| `assume` rejecting most inputs | health-check failure, weak test | construct valid data |
| One property, assumed enough | an obviously wrong function passes | combine properties with examples |
| Retrying flaky tests | bug hidden, trust lost | find the cause (13.5) |

### 16.2 Summary

- A test is insurance; spend effort where bugs hurt. Keep a **pyramid**: many fast unit tests, some integration tests, a few end-to-end tests.
- A **fixture** prepares what tests need; code after `yield` is the teardown and runs even when the test fails. Fixtures can depend on fixtures; teardown runs in reverse order.
- A **scope** (`function`, `module`, `session`) decides how long a fixture lives. Share only what is expensive and read-only. `--setup-show` reveals the order.
- `conftest.py` shares fixtures by folder; the nearest one wins; never import from it.
- `parametrize` (with `id=`) turns many cases into many tests; markers label them; use `--strict-markers` and `xfail(strict=True)`; select with `-k` and `-m`.
- `tmp_path`, `capsys`, `monkeypatch` and `caplog` isolate files, printed output, settings and logs, and clean up automatically.
- **Dependency injection** is the best seam. Doubles: dummy, stub, spy, fake, mock. `unittest.mock`: `Mock`/`MagicMock`, `return_value`, `side_effect`, `assert_*`, `spec`/`autospec`, and `patch` **where the name is looked up**.
- Mocking hurts when you mock the code under test, assert internals, or let a mock lie. Prefer fakes with contract tests.
- Control the world: inject a clock, seed or inject a random generator, use `tmp_path`, inject a network opener, and guard against real network use.
- **Coverage** (with `--branch`) shows code that no test ran. It cannot show that code was *checked*.
- **hypothesis** generates inputs and shrinks failures to a minimal example. Use round-trip, idempotence, invariant and oracle properties; construct, do not filter; use `derandomize=True` in this course.
- **Flaky tests** come from shared state, ordering, time, randomness and concurrency. Fix the cause.
- Build a suite from the **spec**: normal cases, boundaries, coverage, then the **mutation question**.

## Learning outcomes

After this chapter you should be able to:

1. Write fixtures with the right scope and teardown, share them through `conftest.py`, and parametrize tests and fixtures.
2. Use `tmp_path`, `capsys`, `monkeypatch` and `caplog` to test code that touches files, output, settings and logs.
3. Choose between a stub, spy, fake and mock; design code with dependency injection; use `unittest.mock` safely with `spec` and `patch` in the right place.
4. Test code that depends on time, randomness, files or network, without sleeping or touching the real world.
5. Measure line and branch coverage, and explain why 100% coverage can still hide bugs.
6. Write property-based tests with `hypothesis` and read a shrunk counterexample.
7. Find and cure the causes of flaky tests.
8. Build a suite from a specification and judge it with the mutation question.
