# Chapter 13: Modules, packages and environments

Until now, almost every program you wrote lived in **one file**. That is fine for 50 lines. It is painful for 500 lines and impossible for 50,000. Real programs are split into many files. Each file has one job, and the files **import** each other. Real programs also use code that other people wrote: libraries such as `requests`, `pytest` or `numpy`. That code must be **installed**, in the right version, on every computer that runs the program.

This chapter is about both sides of that story:

- **Inside your project**: how one file uses another (`import`), how files are grouped into folders (**packages**), and what goes wrong (wrong folder, circular imports, a file named `random.py`).
- **Around your project**: where installed libraries live, why every project should have its own **virtual environment**, how `pip` installs things, how to write down exact versions so that the program works the same tomorrow, and how to turn **your own** code into a package that anyone can install with one command.

By the end of this chapter you reach the three outcomes of the module:

- You can **split a script into a package** with clean imports.
- You can **diagnose and fix a circular import**.
- You can **build an installable package** from `pyproject.toml`.

Along the way you will answer these questions:

- What does `import` really do, step by step? Why does a module run only once, even if you import it ten times?
- Where does Python look for modules, and why does a file called `random.py` in your folder break `import random`?
- What does `if __name__ == "__main__":` mean, and what is the difference between `python file.py` and `python -m file`?
- What is a package, what is `__init__.py` for, and what does "attempted relative import with no known parent package" mean?
- What is a "partially initialized module", and how do you fix it?
- How can a program import a module whose name it learns only at run time (plugins)?
- What is a virtual environment, and why should you never `pip install` into the system Python?
- What is the difference between `requests>=2`, `requests==2.32.3` and a lock file?
- What is a wheel, what is an sdist, and what does `pip install -e .` do?

**A note on how examples are shown.** Every block of code is followed by the exact output produced by really running it with **Python 3.14** on Linux (Ubuntu), in an empty practice folder. Many outputs in this chapter contain **paths**: where a file lives, where Python looks, where a package was installed. Those paths are machine-specific. They are shown as `/home/you/project` (or a similar folder under `/home/you`); **yours will differ**. System paths such as `/usr/lib/python3.14` are typical for Linux; on Windows and macOS they look different. Version numbers of `pip` and `setuptools` are the ones on the test machine; yours may be newer. Only the idea matters.

When an example needs several files, the chapter **shows every file**: first the folder tree, then the content of each file. You can rebuild every example yourself in an empty folder. Please do: typing the files and running them teaches more than reading.

**No internet needed.** The `pip` examples install small practice packages that we build ourselves, from a local folder. The commands that would download from the internet (for example `pip install requests`, `uv`, `poetry`) are shown and explained, but their output is **described, not captured**, and is clearly marked so.

What this chapter leaves out on purpose: classes come in **core.14**. You will meet a few objects here (modules, module specs) but you will not build classes.

## Table of contents

1. [Why modules](#1-why-modules)
2. [A module is a file](#2-a-module-is-a-file)
3. [What `import` really does](#3-what-import-really-does)
4. [Where Python looks: `sys.path`](#4-where-python-looks-syspath)
5. [`__name__` and `"__main__"`](#5-__name__-and-__main__)
6. [Packages and `__init__.py`](#6-packages-and-__init__py)
7. [Absolute and relative imports](#7-absolute-and-relative-imports)
8. [Namespace packages](#8-namespace-packages)
9. [`__all__` and public APIs](#9-__all__-and-public-apis)
10. [Circular imports](#10-circular-imports)
11. [`importlib`: dynamic imports and plugins](#11-importlib-dynamic-imports-and-plugins)
12. [Virtual environments](#12-virtual-environments)
13. [`pip`: installing and pinning](#13-pip-installing-and-pinning)
14. [Lock files, `uv` and `poetry`](#14-lock-files-uv-and-poetry)
15. [`pyproject.toml` anatomy](#15-pyprojecttoml-anatomy)
16. [Building and installing a package](#16-building-and-installing-a-package)
17. [Project: package the file organiser](#17-project-package-the-file-organiser)
18. [Common traps](#18-common-traps)
19. [Summary](#19-summary)

## 1. Why modules

### 1.1 One file gets too big

Think about the file organiser from core.12. It was one file, `organise.py`, about 130 lines. It had sort rules, a planner, a part that moves files, and the command line. Now imagine it grows: rules for music, a config file, an "undo" feature, a log, tests. Soon the file has 1,500 lines. Then you **cannot find things**; **names collide** (a second `parse` function silently replaces the first); you **cannot reuse a part** without copy and paste (and then there are two copies to fix); two people editing one huge file **get in each other's way**; and you cannot easily **test** the rules without the command line.

The fix is old and simple: **split the program into files**, and let one file **import** what it needs from another.

### 1.2 Three levels of organisation

Python gives you three levels:

| Level | What it is | Example |
|---|---|---|
| **Function** | a named piece of code | `folder_by_type(path)` |
| **Module** | one `.py` file full of functions and values | `rules.py` |
| **Package** | a folder of modules | `organise/` with `rules.py`, `planner.py`, `cli.py` |

And one level **around** your code: the **environment**, one Python plus the set of packages installed for it (for example the folder `.venv/` in your project). A module groups related functions. A package groups related modules. An environment holds the right Python and the right libraries for one project. This chapter walks up these levels.

### 1.3 You have used modules all along

Every `import` you wrote so far loaded a module: `import math`, `import sys`, `from pathlib import Path`, `import json`. These come with Python, in the **standard library**. Libraries such as `pytest` (core.08) are **third-party**: someone else wrote them and you installed them. Your own files are modules too: in core.08 your tests did `from solution import f`, and in core.12 the test did `from organise import main`. This chapter explains what really happens on those lines.

## 2. A module is a file

### 2.1 Your first module

A **module** is simply a `.py` file. Its name is the file name without `.py`. Make a folder with two files:

```text
project/
├── shop.py
└── main.py
```

`shop.py`:

```python
"""Tiny shop helpers."""
print("shop.py is running")

TAX_RATE = 0.18

def price_with_tax(price):
    return round(price * (1 + TAX_RATE), 2)

def _secret():
    return "hidden"
```

`main.py`:

```python
import shop
print(shop.price_with_tax(100))
print(shop.TAX_RATE)
import shop
print("imported twice")
import sys
print("shop" in sys.modules)
print(sys.modules["shop"] is shop)
print(type(shop))
print(shop.__name__)
print(shop.__doc__)
print([n for n in dir(shop) if not n.startswith("__")])
```

Run it from inside `project/`:

```text
$ python main.py
shop.py is running
118.0
0.18
imported twice
True
True
<class 'module'>
shop
Tiny shop helpers.
['TAX_RATE', '_secret', 'price_with_tax']
```

Read the output slowly. It already shows most of this chapter:

- `import shop` **ran** the file `shop.py`: we see its `print`.
- After the import, the name `shop` in `main.py` refers to a **module object**. Everything defined at the top level of `shop.py` became an **attribute** of it: `shop.TAX_RATE`, `shop.price_with_tax`.
- The second `import shop` printed **nothing**. The file did not run again. (Section 3 explains why.)
- `sys.modules` is a dictionary of every module loaded so far. Our `shop` is in it.
- A module is an object of type `module`. It has a `__name__` (`"shop"`) and a `__doc__` (the docstring at the top of the file).
- `dir(shop)` lists the names inside the module. `_secret` is there too: a leading underscore is a **convention** ("private, please do not use"), not a lock. Section 9 comes back to this.

### 2.2 The four forms of `import`

```python
import shop                         # 1. the module; use shop.price_with_tax
import shop as s                    # 2. the module, under another name: s.price_with_tax
from shop import price_with_tax     # 3. one name from the module
from shop import price_with_tax as pwt   # 4. one name, renamed
```

A small check of forms 2 to 4, in a file `fromimp.py` next to `shop.py`:

```python
from shop import price_with_tax, TAX_RATE
import shop as s
print(price_with_tax(50), TAX_RATE)
print(s.TAX_RATE)
from shop import price_with_tax as pwt
print(pwt is price_with_tax)
print("shop" in dir())
```
```text
shop.py is running
59.0 0.18
0.18
True
False
```

The last line is interesting. After `from shop import ...` and `import shop as s`, the name **`shop`** is not defined in `fromimp.py`: `dir()` lists the names of the current module, and there is `s`, `price_with_tax`, `TAX_RATE`, `pwt`, but no `shop`. `import X as Y` only creates the name `Y`.

When should you use which form?

| Form | Good for | Watch out |
|---|---|---|
| `import json` | most cases; the reader sees where a name comes from (`json.loads`) | longer to type |
| `import numpy as np` | long names with a well-known short form | invent short names only when the whole community uses them |
| `from pathlib import Path` | names you use very often | too many `from` imports hide where names come from |
| `from shop import *` | the interactive prompt only | pulls in unknown names; see section 9 |

A good default: `import module` for most things, `from module import Name` for a few names you use all the time.

### 2.3 Module names must be valid identifiers

The module name is used in Python code (`import shop`), so the file name must be a valid identifier: letters, digits and underscores, not starting with a digit. `my-tool.py` cannot be imported with `import my-tool` (the `-` is a minus sign). Use `my_tool.py`. Also avoid names of standard modules, such as `random.py`, `json.py`, `math.py`, `test.py`, `email.py`: section 4.4 shows why.

## 3. What `import` really does

### 3.1 The steps

When Python meets `import shop`, it does this:

1. **Check the cache.** Is `"shop"` already a key in `sys.modules`? If yes, take that module object and jump to step 5.
2. **Find** the module. Look through the folders in `sys.path`, in order, for `shop.py` (or a package folder `shop/`, or a compiled extension). The first match wins. If nothing matches: `ModuleNotFoundError`.
3. **Create** an empty module object and **put it into `sys.modules` at once**, before running any code.
4. **Execute** the file, top to bottom, *inside* that module object. Every `def`, every assignment, every `print` at the top level runs now. The names created become the module's attributes.
5. **Bind** a name in the importing file: `import shop` creates the variable `shop`; `from shop import price_with_tax` creates `price_with_tax`.

Two facts follow, and they explain many surprises. **A module runs only once per program**: the second import finds it in the cache (step 1) and skips steps 2 to 4. And **the module is in the cache *before* it has finished running** (step 3). Remember this; it is the key to circular imports in section 10.

### 3.2 Importing is running

Step 4 deserves attention. **Importing a file executes it.** Every top-level statement runs. That is why the `print` in `shop.py` appeared. It is also why a module should do **nothing slow or dangerous at the top level**: no `input()`, no deleting files, no long computations. It should only **define** things (functions, constants). Real work belongs in functions that the caller calls.

Here is a module that breaks this rule. `noguard.py`:

```python
def c_to_f(c):
    return c * 9 / 5 + 32
answer = input("Celsius? ")
print(c_to_f(float(answer)))
```

And a second file that only wants the function, `use_noguard.py`:

```python
from noguard import c_to_f
print("ready")
```

Run it (here we type `10` when it asks):

```text
$ python use_noguard.py
Celsius? 10
50.0
ready
```

We only wanted `c_to_f`, but the import asked a question and printed an answer. Section 5 shows the cure: `if __name__ == "__main__":`.

### 3.3 Predict the output: import inside a function

Two files. `heavy.py`:

```python
print("heavy: loading (slow!)")
def work(x):
    return x * 2
```

`main.py`:

```python
def compute(x):
    import heavy
    return heavy.work(x)

print("start")
for n in [1, 2, 3]:
    print(compute(n))
print("end")
```

How many times does `heavy: loading (slow!)` appear, and where?

<details><summary>Answer</summary>

```text
start
heavy: loading (slow!)
2
4
6
end
```

Once, on the first call. The `import` statement runs three times, but only the first one loads the file. The second and third find `"heavy"` in `sys.modules` and only bind the name `heavy` inside the function, which is very cheap. Nothing loads before `start`, because the import is inside the function: it happens when the function first runs. Section 10 uses exactly this trick to break circular imports.
</details>

### 3.4 Module attributes: `__name__`, `__file__`, `__doc__`

Every module gets some special attributes when it is created:

| Attribute | Meaning |
|---|---|
| `__name__` | the module's full name, such as `"shop"` or `"json.decoder"` |
| `__file__` | the path of the file it was loaded from |
| `__doc__` | the docstring at the top of the file, or `None` |
| `__cached__` | where the compiled bytecode is stored |
| `__package__` | the package this module belongs to (section 6) |

Let us look at them. We need a small module, `counter.py` (we use it again in section 3.7):

```python
print("loading counter")
count = 0
def tick():
    global count
    count += 1
    return count
```

Next to it, `where.py`:

```python
import counter, json, math, sys
print(counter.__file__)
print(json.__file__)
print(getattr(math, "__file__", "no file: built in"))
print("math" in sys.builtin_module_names, "sys" in sys.builtin_module_names)
print(counter.__cached__)
```
```text
loading counter
/home/you/project/counter.py
/usr/lib/python3.14/json/__init__.py
no file: built in
True True
/home/you/project/__pycache__/counter.cpython-314.pyc
```

(The paths are from the test machine; yours will differ.)

- `json` is a normal Python file inside the standard library folder. You can open it and read it: a good way to learn.
- `math` and `sys` have no `__file__`: they are **built in**, written in C and compiled into the Python program itself. (On some systems `math` is a separate compiled file instead; then you see a path ending in `.so` or `.pyd`.)

### 3.5 The `__pycache__` folder

After your first import you will find a new folder next to your files. Here is the practice folder after running the examples of sections 3.4, 3.6 and 3.7:

```text
project/
├── __pycache__/
│   ├── counter.cpython-314.pyc
│   └── settings.cpython-314.pyc
├── counter.py
├── main.py
├── reload_demo.py
├── settings.py
└── where.py
```

Before Python runs a module, it **compiles** the source code into **bytecode**, a simpler form that the Python interpreter executes. Compiling takes a little time, so Python saves the result in `__pycache__/NAME.cpython-314.pyc` (`314` is the Python version). Next time, if the `.py` file has not changed, Python loads the `.pyc` directly.

It is **safe to delete** `__pycache__` (Python makes it again), and you should **not commit it** to git (put `__pycache__/` in `.gitignore`). Only **imported** modules get a `.pyc`; the script you run directly is compiled each time and not saved.

### 3.6 `from ... import` copies a reference, not a live link

`from settings import debug` creates a **new variable** `debug` in your file that points to the same object that `settings.debug` points to **at that moment**. If the module later rebinds `settings.debug` to a different object, your `debug` does not change.

`settings.py`:

```python
debug = False

def turn_on():
    global debug
    debug = True
```

`main.py`:

```python
import settings
from settings import debug, turn_on

turn_on()
print("settings.debug:", settings.debug)
print("debug:        ", debug)
```

Predict the two lines before you read on.

<details><summary>Answer</summary>

```text
settings.debug: True
debug:         False
```

`turn_on()` rebinds the name `debug` **inside the module** to `True`. Your own variable `debug` was a copy of the reference made at import time, and it still points to `False`. `settings.debug` looks the name up in the module **each time**, so it sees the new value. Rule: for values that can change (settings, counters, flags), use `import settings` and write `settings.debug`. `from ... import` is fine for functions and constants that never change.
</details>

This is the same rule you learned for variables in core.02: assignment makes a name point to a new object; other names that pointed to the old object are not affected.

### 3.7 `importlib.reload` and its trap

Because a module runs only once, editing a file while a program (or the interactive prompt) is running has no effect: the old module stays in `sys.modules`. `importlib.reload(module)` runs the file **again**, inside the **same** module object.

We use `counter.py` from section 3.4 again. Next to it, `reload_demo.py`:

```python
import importlib
import counter
from counter import tick

counter.tick()
counter.tick()
print("before reload:", counter.count)
importlib.reload(counter)
print("after reload: ", counter.count)
print(tick())
print(counter.count)
print(tick is counter.tick)
```

Predict the output. Hint: think about which function object each name refers to after the reload.

<details><summary>Answer</summary>

```text
loading counter
before reload: 2
loading counter
after reload:  0
1
1
False
```

- `reload` runs the file again: `loading counter` appears a second time, and `count = 0` resets the counter.
- `reload` creates **new** function objects. `counter.tick` now points to the new `tick`. But our name `tick` (from `from counter import tick`) still points to the **old** function. `tick is counter.tick` is `False`.
- The old `tick` still works on the module's globals (the module object is the same one), so it raises `count` to 1.

Two functions with the same name, one old and one new, living side by side: this is why `reload` causes confusing bugs. It also does **not** reload modules that `counter` itself imports. Use `reload` only for quick experiments at the interactive prompt. In a real program, **restart the program**.
</details>

## 4. Where Python looks: `sys.path`

### 4.1 The search list

Step 2 of an import ("find the module") searches the folders in the list **`sys.path`**, **in order**, and stops at the **first** match. Print it. `show_path.py`:

```python
import sys
for entry in sys.path:
    print(repr(entry))
```
```text
$ python show_path.py
'/home/you/project'
'/usr/lib/python314.zip'
'/usr/lib/python3.14'
'/usr/lib/python3.14/lib-dynload'
'/usr/local/lib/python3.14/dist-packages'
'/usr/lib/python3/dist-packages'
```

(Machine-specific: this is the system Python of an Ubuntu machine. On Windows you see folders such as `C:\Users\you\AppData\Local\Programs\Python\Python314\Lib`. Inside a virtual environment the last entries differ; see section 12.)

The entries, in order:

1. **The folder of the script you ran** (`/home/you/project`). This is why `import shop` finds `shop.py` next to `main.py`.
2. The **standard library**: a zip file (usually missing, that is fine), the main folder, and `lib-dynload` (compiled modules).
3. **site-packages** (on Debian/Ubuntu called `dist-packages`): where third-party packages are installed.

The first entry depends on **how** you start Python:

| How you start Python | `sys.path[0]` |
|---|---|
| `python path/to/script.py` | the folder of the script, `path/to` |
| `python -m module` | the **current working directory** |
| `python -c "..."` or the interactive prompt | `''`, meaning the current working directory |

```text
$ python -c "import sys; print(sys.path[0]==''); print(sys.path[:2])"
True
['', '/usr/lib/python314.zip']
```

Notice that for `python script.py` it is the folder of the **script**, not the folder you are standing in. That is a common surprise: `python tools/report.py` can import modules in `tools/`, but not modules in your current folder.

### 4.2 `ModuleNotFoundError`

If no folder in `sys.path` contains the module, you get `ModuleNotFoundError` (a subclass of `ImportError`). Take this layout:

```text
project/
├── textkit/          (a package; section 6)
│   └── ...
└── elsewhere/
```

From inside `elsewhere/`:

```text
$ cd elsewhere
$ python -c "import textkit; print('ok')"
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    import textkit; print('ok')
    ^^^^^^^^^^^^^^
ModuleNotFoundError: No module named 'textkit'
```

`textkit` lives in the parent folder, which is not in `sys.path`. When you see this error, ask three questions:

1. **Is the name spelled right?** (`import Shop` is not `import shop` on Linux.)
2. **Which folder did I start Python from, and which file did I run?** That decides `sys.path[0]`.
3. **Is it a third-party package that is not installed in *this* environment?** (Section 12: `pip` and `python` may belong to different environments.)

### 4.3 Changing the search path (and why you usually should not)

There are two ways to add a folder: the **`PYTHONPATH`** environment variable (its folders are put near the front of `sys.path`), or `sys.path.append(...)` inside your code. From `elsewhere/`:

```text
$ PYTHONPATH=.. python -c "import sys, textkit; print(textkit.slugify('It works'))"
it-works
```

Both work, but both are **fragile**. They depend on where the files are on one machine, and they hide the real problem: your code is not installed. The proper fix is to make your code a package and install it into the environment (sections 15 to 17). Then it is importable from anywhere, like `json`. Use `PYTHONPATH` only for quick experiments.

### 4.4 The shadowing trap: `random.py`

Because the script's folder comes **first** in `sys.path`, your own files win over the standard library. Make a folder with two files:

```text
shadow/
├── random.py
└── dice.py
```

`random.py` (a student named their practice file after the topic):

```python
print("my random.py was imported!")
```

`dice.py`:

```python
import random
print(random.randint(1, 6))
```

Predict what happens when you run `python dice.py`.

<details><summary>Answer</summary>

```text
$ python dice.py
my random.py was imported!
Traceback (most recent call last):
  File "/home/you/shadow/dice.py", line 2, in <module>
    print(random.randint(1, 6))
          ^^^^^^^^^^^^^^
AttributeError: module 'random' has no attribute 'randint' (consider renaming '/home/you/shadow/random.py' since it has the same name as the standard library module named 'random' and prevents importing that standard library module)
```

`import random` found `shadow/random.py` first, because the script's folder is searched first. The real `random` was never loaded. Your file has no `randint`, so the attribute lookup fails. Modern Python (3.13 and later) even suggests the fix in the message: **rename your file**. Older versions only say `has no attribute 'randint'`, which is much harder to understand.
</details>

This is called **shadowing**: your file hides ("shadows") the real module. Classic victims: `random.py`, `json.py`, `math.py`, `email.py`, `test.py`, `string.py`, `csv.py`, `statistics.py`, and also third-party names such as `requests.py` or `pytest.py`. The trap is worse than it looks: other library modules that use `random` internally will also get **your** file. After renaming, also delete the old `__pycache__` folder, so that no stale `random.cpython-314.pyc` is left behind.

## 5. `__name__` and `"__main__"`

### 5.1 One file, two jobs

A file can be used in two ways:

- **Run** as a program: `python temperature.py`.
- **Imported** as a module by another file: `import temperature`.

Often you want both. The file should offer functions to others, and when run directly, it should do something useful (a demo, a command-line tool). The variable `__name__` tells the file which case it is in:

- When the file is **run directly**, Python sets its `__name__` to the string `"__main__"`.
- When the file is **imported**, `__name__` is the module's normal name, for example `"temperature"`.

### 5.2 The idiom

`temperature.py`:

```python
def c_to_f(c):
    return c * 9 / 5 + 32

print("temperature.__name__ is", repr(__name__))

if __name__ == "__main__":
    for c in [0, 37, 100]:
        print(c, "->", c_to_f(c))
```

`report.py`, next to it:

```python
import temperature
print("report.__name__ is", repr(__name__))
print(temperature.c_to_f(25))
```

Run each file:

```text
$ python temperature.py
temperature.__name__ is '__main__'
0 -> 32.0
37 -> 98.6
100 -> 212.0
```

Predict the output of `python report.py` before you open the answer.

<details><summary>Answer</summary>

```text
$ python report.py
temperature.__name__ is 'temperature'
report.__name__ is '__main__'
77.0
```

`report.py` is the file that was run, so **its** `__name__` is `"__main__"`. `temperature.py` was imported, so its `__name__` is `"temperature"`, the condition is false, and the demo loop does not run. The unguarded `print` at the top level still runs: importing executes the file.
</details>

So `if __name__ == "__main__":` means: "run this block only when this file is the program, not when it is imported". The standard shape of a script that is also a module:

```python
import sys

def main(argv=None):
    ...              # the real work, in a function
    return 0         # exit code

if __name__ == "__main__":
    sys.exit(main())
```

This is the shape you used for the core.12 file organiser. Putting the work into `main()` (instead of directly under the `if`) has two benefits: tests can call `main([...])` with any arguments, and variables inside `main` stay local instead of becoming global names of the module.

### 5.3 `python file.py` versus `python -m module`

There are two ways to run code as the main program:

```text
$ python temperature.py      # run a FILE by its path
$ python -m temperature      # run a MODULE by its import name
```

```text
$ python -m temperature
temperature.__name__ is '__main__'
0 -> 32.0
37 -> 98.6
100 -> 212.0
```

Here the result is the same. The differences matter when packages are involved:

| | `python path/file.py` | `python -m package.module` |
|---|---|---|
| you give | a file path (with `/` and `.py`) | an import name (with `.` and no `.py`) |
| `sys.path[0]` | the folder of the file | the current folder |
| the module knows its package | **no** | **yes** |
| relative imports (`from . import x`) | fail | work |

You already used `-m` many times: `python -m pytest`, `python -m venv`, `python -m pip`, `python -m json.tool`. Each one finds an installed module by name and runs it as `__main__`. Section 7 shows why `-m` is the right way to run a module that lives inside a package.

## 6. Packages and `__init__.py`

### 6.1 A folder of modules

When a project has many modules, you group them in folders. A **package** is a folder of modules that you can import with **dotted names**: `import shop.prices` means "the module `prices` inside the package `shop`". A package can contain other packages (**subpackages**), so the names can get longer: `shop.payments.upi`. The standard library is full of packages: `json`, `email`, `xml.etree`, `importlib`, `concurrent.futures`.

A **regular package** is a folder with a file called **`__init__.py`** inside. The file may be empty. Its presence says "this folder is a package". (Section 8 shows folders without it.)

Here is a small shop, split into a package. Build this folder tree:

```text
project/
├── app.py
└── shop/
    ├── __init__.py
    ├── prices.py
    ├── cart.py
    └── payments/
        ├── __init__.py
        └── upi.py
```

Each file prints a line when it runs, so that we can watch the import order.

`shop/__init__.py`:

```python
print("running shop/__init__.py")
```

`shop/prices.py`:

```python
print("running shop/prices.py")
TAX_RATE = 0.18

def with_tax(price):
    return round(price * (1 + TAX_RATE), 2)
```

`shop/cart.py`:

```python
print("running shop/cart.py")
from .prices import with_tax

def total(items):
    return sum(with_tax(price) for price in items)
```

`shop/payments/__init__.py`:

```python
print("running shop/payments/__init__.py")
```

`shop/payments/upi.py`:

```python
print("running shop/payments/upi.py")
from ..cart import total

def pay(items):
    return f"paid {total(items)} by UPI"
```

`app.py`:

```python
from shop.payments.upi import pay
print(pay([100, 50]))
```

The lines `from .prices import ...` and `from ..cart import ...` are **relative imports**: the dots mean "this package" and "the parent package". Section 7 explains them. For now, read `.prices` as "the module `prices` in my own package".

### 6.2 Predict the output: import order

Run `python app.py` from `project/`. In what order do the six lines appear?

<details><summary>Answer</summary>

```text
$ python app.py
running shop/__init__.py
running shop/payments/__init__.py
running shop/payments/upi.py
running shop/cart.py
running shop/prices.py
paid 177.0 by UPI
```

To import `shop.payments.upi`, Python must first import **every package on the way**: `shop` (runs `shop/__init__.py`), then `shop.payments` (runs `shop/payments/__init__.py`), then the module `upi` itself. While `upi.py` runs, its line `from ..cart import total` imports `shop.cart` (the package `shop` is already loaded, so its `__init__.py` does not run again). `cart.py` then imports `shop.prices`. Only after all of that does `app.py` call `pay`. Total: 100 and 50 with 18 % tax give 118.0 + 59.0 = 177.0.
</details>

The rule: **importing `a.b.c` runs `a/__init__.py`, then `a/b/__init__.py`, then `a/b/c.py`**, each only once per program.

### 6.3 Importing a package does not import its modules

A common surprise. `only_pkg.py`, next to `shop/`:

```python
import shop
print(shop.prices.with_tax(10))
```
```text
$ python only_pkg.py
running shop/__init__.py
Traceback (most recent call last):
  File "/home/you/project/only_pkg.py", line 2, in <module>
    print(shop.prices.with_tax(10))
          ^^^^^^^^^^^
AttributeError: module 'shop' has no attribute 'prices'
```

`import shop` runs **only** `shop/__init__.py`. It does not load every module in the folder (that would be slow for big packages). The submodule becomes an attribute of the package only after it is imported. `sub_then.py`:

```python
import shop.prices
print(shop.prices.with_tax(10))
print(shop.__file__.endswith("__init__.py"), shop.__path__ is not None)
print(shop.prices.__name__, shop.prices.__package__)
```
```text
$ python sub_then.py
running shop/__init__.py
running shop/prices.py
11.8
True True
shop.prices shop
```

- `import shop.prices` loads both, and binds the name `shop` (the top package). You then write the full path: `shop.prices.with_tax`.
- A package's `__file__` is its `__init__.py`. A package also has a **`__path__`**: the list of folders where its submodules are searched. Having a `__path__` is what makes a module a package.
- A module's `__package__` is the package it belongs to. Relative imports use it.

### 6.4 What belongs in `__init__.py`

`__init__.py` runs the first time anything in the package is imported. Often it is **empty**, which is perfectly fine. Otherwise use it for a **docstring**, a **version** string (`__version__ = "1.2.0"`), and **re-exporting** the main names so users can write `from textkit import slugify` instead of `from textkit.slugs import slugify` (section 9). Avoid slow work, printing, reading files and importing heavy submodules "just in case": every user pays that cost on every import.

### 6.5 Running a package: `__main__.py`

If a package contains a file named **`__main__.py`**, then `python -m package` runs that file. This is how `python -m pip`, `python -m venv` and `python -m json.tool` work.

Here is a second package, `textkit`, that we also use in section 9:

```text
project/
├── app.py
└── textkit/
    ├── __init__.py
    ├── __main__.py
    ├── counting.py
    └── slugs.py
```

`textkit/__init__.py`:

```python
"""textkit - small helpers for cleaning text."""
from .counting import count_vowels, count_words
from .slugs import slugify

__all__ = ["count_vowels", "count_words", "slugify"]
```

`textkit/counting.py`:

```python
VOWELS = "aeiou"

def count_vowels(text):
    return sum(1 for ch in text.lower() if ch in VOWELS)

def count_words(text):
    return len(text.split())
```

`textkit/slugs.py`:

```python
import re

def slugify(text):
    return _join(re.findall(r"[a-z0-9]+", text.lower()))

def _join(words):
    return "-".join(words)
```

`textkit/__main__.py`:

```python
import sys
from textkit import count_words, slugify

for line in sys.argv[1:]:
    print(f"{slugify(line)!r}: {count_words(line)} words")
```

```text
$ python -m textkit "Hello World" "Python 3.14 is here"
'hello-world': 2 words
'python-3-14-is-here': 4 words
```

Python imported the package `textkit` (running `__init__.py`), then ran `textkit/__main__.py` as the main program. Inside `__main__.py`, `__name__` is `"__main__"`, so you do not need the `if __name__ == "__main__":` guard there: the file exists only to be run.

## 7. Absolute and relative imports

### 7.1 Two ways to name a module in your own package

Inside `shop/cart.py` we want `with_tax` from `shop/prices.py`. There are two correct ways:

```python
from shop.prices import with_tax    # absolute: the full name from the top package
from .prices import with_tax        # relative: "prices" in my own package
```

- An **absolute import** names the module from the top: `shop.prices`. It works the same in every file, and the reader sees exactly which module is meant.
- A **relative import** starts with dots. One dot is **the current package**, two dots are **the parent package**, three dots the grandparent, and so on:

| Written in `shop/payments/upi.py` | Means |
|---|---|
| `from . import helpers` | `shop.payments.helpers` |
| `from .helpers import x` | `x` from `shop.payments.helpers` |
| `from .. import cart` | `shop.cart` |
| `from ..cart import total` | `total` from `shop.cart` |
| `from ..prices import with_tax` | `with_tax` from `shop.prices` |

Relative imports only exist in the `from` form. `import .prices` is a syntax error.

Which one should you use? Both are fine. The official style guide (PEP 8) prefers **absolute** imports because they are clearer. Relative imports are handy inside a big package, and they keep working if you rename the top package. Pick one style per project and stay with it. What you must **not** do is the third, wrong way, shown in 7.3.

### 7.2 "attempted relative import with no known parent package"

A relative import needs to know **which package the current module is in**. Python knows this only when the module was **imported as part of the package** (or run with `-m`). Watch what happens when you run `cart.py` directly by its path. Predict first: `python shop/cart.py`, then `python -m shop.cart`, both from `project/`.

<details><summary>Answer</summary>

```text
$ python shop/cart.py
running shop/cart.py
Traceback (most recent call last):
  File "/home/you/project/shop/cart.py", line 2, in <module>
    from .prices import with_tax
ImportError: attempted relative import with no known parent package
```

```text
$ python -m shop.cart
running shop/__init__.py
running shop/cart.py
running shop/prices.py
```

With `python shop/cart.py`, Python treats `cart.py` as a lonely script named `__main__`. It does not know that the file sits inside a package, so "the current package" (`.`) means nothing. With `python -m shop.cart`, Python imports the package `shop` first and then runs `shop.cart` as the main module, knowing its package. The relative import works.
</details>

The fix is always the same: **run modules that live inside a package with `-m`, from the folder that contains the top package.**

```text
$ python -m shop.cart        # right: from project/, the folder that contains shop/
```

Running `-m` from the wrong folder does not help: `cd shop` and then `python -m cart` gives the same `ImportError`, because from inside `shop/` the name `cart` is a top-level module, not `shop.cart`.

### 7.3 The wrong way: script-style imports inside a package

Beginners often "fix" the error above by removing the dot. Suppose `shop/cart2.py` is:

```python
from prices import with_tax

def total(items):
    return sum(with_tax(price) for price in items)

if __name__ == "__main__":
    print(total([100]))
```

Predict two runs from `project/`: first `python shop/cart2.py`, then `python use_cart2.py`, where `use_cart2.py` is:

```python
from shop import cart2
print(cart2.total([100]))
```

<details><summary>Answer</summary>

```text
$ python shop/cart2.py
running shop/prices.py
118.0
```

```text
$ python use_cart2.py
running shop/__init__.py
Traceback (most recent call last):
  File "/home/you/project/use_cart2.py", line 1, in <module>
    from shop import cart2
  File "/home/you/project/shop/cart2.py", line 1, in <module>
    from prices import with_tax
ModuleNotFoundError: No module named 'prices'
```

Run as a script, `sys.path[0]` is `project/shop/`, so the **top-level** module `prices` is found. (Notice that `shop/__init__.py` did not run: Python loaded `prices.py` as a lonely module, not as `shop.prices`.) Imported as part of the package, `sys.path[0]` is `project/`, and there is no top-level `prices` there. The file works in one situation and breaks in the other.
</details>

Inside a package, always use the **package name** (`from shop.prices import ...`) or a **relative** import (`from .prices import ...`). Never write a bare `from prices import ...` for a sibling module. It "works on my machine" until somebody imports your package properly, and it can load the same file twice under two names (`prices` and `shop.prices`), with two separate copies of every global variable.

### 7.4 Rules of thumb

1. Every folder of your code that should be a package gets an `__init__.py`, and siblings import each other with the full package name or with dots.
2. Run things from the **project root** (the folder that contains the top package) with `python -m package.module`, or through a test runner or console script. Never add `sys.path.append("..")` hacks; fix the layout instead.

## 8. Namespace packages

### 8.1 A package without `__init__.py`

Since Python 3.3, a folder **without** `__init__.py` can also be imported as a package. It is called a **namespace package**. Its special power: one package name can be **spread over several folders**. Python collects every folder with that name along `sys.path` and treats them as one package.

Two teams each ship a part of a `plugins` package:

```text
project/
├── main.py
├── team_a/
│   └── plugins/
│       └── csv_export.py
└── team_b/
    └── plugins/
        └── pdf_export.py
```

`team_a/plugins/csv_export.py`:

```python
NAME = "csv export"
```

`team_b/plugins/pdf_export.py`:

```python
NAME = "pdf export"
```

`main.py`:

```python
import sys
sys.path.append("team_a")
sys.path.append("team_b")

import plugins
from plugins import csv_export, pdf_export
print(csv_export.NAME, "|", pdf_export.NAME)
print(plugins.__file__)
print(list(plugins.__path__))
```
```text
$ python main.py
csv export | pdf export
None
['/home/you/project/team_a/plugins', '/home/you/project/team_b/plugins']
```

(We used `sys.path.append` only to simulate two separately installed parts; section 4.3 says why you avoid it in real code.)

`plugins` has **no `__file__`** (there is no `__init__.py`), and its `__path__` lists **both** folders: `csv_export` came from one, `pdf_export` from the other.

### 8.2 When to use them

Namespace packages are meant for **big projects split into separately installed pieces** that share one top name (for example, a company's `acme.billing` and `acme.reports`, installed by different teams). For your own normal projects, **always write `__init__.py`**. Without it, any folder (say `data/`) can be imported by accident, mistakes give confusing results instead of clear errors, and some tools that look for packages skip the folder. If you ever see an import "work" from a folder that has no `__init__.py`, now you know why.

## 9. `__all__` and public APIs

### 9.1 Public and private names

A module is a little **API** (application programming interface): the set of names other code is allowed to use. Some names are for the users; others are internal helpers that you may change at any time. Python has no `private` keyword. It uses **conventions**:

- A name starting with **one underscore** (`_join`, `_cache`) means **internal: do not use from outside**. Nothing stops you, but if you use it and it changes, it is your problem.
- Everything else is **public**: users may rely on it, so you must not break it without warning.

### 9.2 What `from module import *` takes

`from module import *` copies names into your file. Which names? A single-file module, `textkit.py` (not the package from 6.5; use a separate practice folder):

```python
import re

VOWELS = "aeiou"

def count_vowels(text):
    return sum(1 for ch in text.lower() if ch in VOWELS)

def slugify(text):
    return _join(re.findall(r"[a-z0-9]+", text.lower()))

def _join(words):
    return "-".join(words)
```

`star1.py`:

```python
from textkit import *
names = sorted(n for n in dir() if not n.startswith("__"))
print(names)
```

Predict the list.

<details><summary>Answer</summary>

```text
['VOWELS', 'count_vowels', 're', 'slugify']
```

Without `__all__`, `import *` takes **every name that does not start with an underscore**. So `_join` stays out, but `re` comes in: the module `re` that `textkit` imported for itself. Your file now has a name `re` it never imported, and if it had its own `re` or `VOWELS`, they would be silently replaced.
</details>

### 9.3 `__all__`: the official list

Put a list called **`__all__`** at the top of the module. It names the public API. Add this as the first line of `textkit.py`:

```python
__all__ = ["count_vowels", "slugify"]
```

Run `star1.py` again:

```text
['count_vowels', 'slugify']
```

Now `import *` takes exactly those names. `__all__` does **not** make other names unreachable. `direct.py`:

```python
import textkit
from textkit import _join, VOWELS
print(_join(["still", "reachable"]), VOWELS)
print(textkit.slugify("Hello, World 2026!"))
```
```text
still-reachable aeiou
hello-world-2026
```

So what is `__all__` for, if it does not hide anything? It controls `import *`; it is **documentation** (the first thing a reader sees is the list of public names); and editors, linters and documentation generators treat the names in it as the public API. Even so, the advice stays: **do not use `import *` in your own code** (except at the interactive prompt). It makes it impossible to tell where a name came from.

### 9.4 Designing a package API: re-export in `__init__.py`

Look again at `textkit/__init__.py` from section 6.5:

```python
"""textkit - small helpers for cleaning text."""
from .counting import count_vowels, count_words
from .slugs import slugify

__all__ = ["count_vowels", "count_words", "slugify"]
```

The real code lives in `counting.py` and `slugs.py`. The `__init__.py` **re-exports** the public functions, so users write short, stable imports. `app.py`, next to the `textkit/` folder:

```python
import textkit
from textkit import slugify

print(slugify("Modules and Packages!"))
print(textkit.count_vowels("environment"))
print(textkit.__all__)
print(textkit.counting.VOWELS)
```
```text
modules-and-packages
4
['count_vowels', 'count_words', 'slugify']
aeiou
```

Why is this good design? Users do not need to know your file layout: `from textkit import slugify` is all they learn. You can **reorganise freely**: if `slugs.py` is later split into two files, you change one line in `__init__.py` and no user code breaks. And the public API is visible in one place.

A common extra step is to name internal modules with an underscore (`_counting.py`, `_slugs.py`), which tells users "import from the package, not from these files". The last line of the output shows that the submodule `textkit.counting` is still reachable: re-exporting never hides anything.

## 10. Circular imports

### 10.1 How the problem appears

A **circular import** happens when module A imports module B, and module B (directly or through other modules) imports module A. It is the most common import error in growing projects. Typical story: two modules that started separate begin to need each other.

Here is a shop package with orders and stock:

```text
project/
├── main.py
└── shop/
    ├── __init__.py        (empty)
    ├── orders.py
    └── inventory.py
```

`shop/orders.py` needs `in_stock` from the inventory:

```python
from shop.inventory import in_stock

def place_order(item, qty):
    if not in_stock(item, qty):
        return f"sorry, not enough {item}"
    return f"ordered {qty} x {item}"

def order_log(text):
    print("LOG:", text)
```

`shop/inventory.py` wants to log through `order_log` from the orders module:

```python
from shop.orders import order_log

STOCK = {"pen": 10, "book": 2}

def in_stock(item, qty):
    ok = STOCK.get(item, 0) >= qty
    if not ok:
        order_log(f"low stock: {item}")
    return ok
```

`main.py`:

```python
from shop.orders import place_order

print(place_order("pen", 3))
print(place_order("book", 5))
```

```text
$ python main.py
Traceback (most recent call last):
  File "/home/you/project/main.py", line 1, in <module>
    from shop.orders import place_order
  File "/home/you/project/shop/orders.py", line 1, in <module>
    from shop.inventory import in_stock
  File "/home/you/project/shop/inventory.py", line 1, in <module>
    from shop.orders import order_log
ImportError: cannot import name 'order_log' from partially initialized module 'shop.orders' (most likely due to a circular import) (/home/you/project/shop/orders.py)
```

### 10.2 Reading the traceback

The traceback is a **story of nested imports**. Read it from the top:

1. `main.py` line 1 starts importing `shop.orders`.
2. `orders.py` line 1 (its very first line) starts importing `shop.inventory`.
3. `inventory.py` line 1 asks `shop.orders` for the name `order_log`.

And the last line says why that fails: `shop.orders` is **partially initialized**. Remember step 3 of section 3.1: a module is put into `sys.modules` **before** its code runs. So when `inventory.py` asks for `shop.orders`, Python finds it in the cache and does not load it again (that would loop forever). But `orders.py` has only reached line 1. The line `def order_log` has not run yet. The module object exists, but it is still empty. The name `order_log` is not in it.

Step by step, with the state of `shop.orders`:

| Step | What runs | Names in `shop.orders` so far |
|---|---|---|
| 1 | `main.py`: `from shop.orders import place_order` | (module created, cached, empty) |
| 2 | `orders.py` line 1: `from shop.inventory import in_stock` | (still empty: paused at line 1) |
| 3 | `inventory.py` line 1: `from shop.orders import order_log` | (still empty) → **`order_log` missing: ImportError** |

The words to look for in a traceback: **"partially initialized module"** and **"most likely due to a circular import"**, and a chain where the same module name appears twice.

### 10.3 Predict the output: start from the other side

Keep the two broken modules. Change `main.py` to import the inventory first:

```python
from shop.inventory import in_stock

print(in_stock("pen", 3))
```

Which name is missing now, and from which module?

<details><summary>Answer</summary>

The last lines of the traceback:

```text
  File "/home/you/project/shop/orders.py", line 1, in <module>
    from shop.inventory import in_stock
ImportError: cannot import name 'in_stock' from partially initialized module 'shop.inventory' (most likely due to a circular import) (/home/you/project/shop/inventory.py)
```

Now `inventory` starts first, pauses at its line 1 to import `orders`, and `orders` asks the half-empty `inventory` for `in_stock`. The cycle is the same; only the victim changes. That is why circular imports can seem "random": the error depends on **which module happens to be imported first**. A program can work for months and break when someone adds an import in a third file.
</details>

### 10.4 Fix 1: move the shared code into its own module (the best fix)

A cycle usually means the design is mixed up: `order_log` is not really about orders. Both modules need it, so it belongs in a **third** module that imports neither of them.

```text
shop/
├── __init__.py
├── log.py           (new)
├── orders.py
└── inventory.py
```

`shop/log.py`:

```python
def order_log(text):
    print("LOG:", text)
```

`shop/orders.py`:

```python
from shop.inventory import in_stock
from shop.log import order_log

def place_order(item, qty):
    if not in_stock(item, qty):
        return f"sorry, not enough {item}"
    order_log(f"ordered {item}")
    return f"ordered {qty} x {item}"
```

In `shop/inventory.py`, only the first line changes:

```python
from shop.log import order_log
```

Run the original `main.py` (the one that calls `place_order` twice):

```text
$ python main.py
LOG: ordered pen
ordered 3 x pen
LOG: low stock: book
sorry, not enough book
```

(We also made `place_order` log successful orders, to show that both modules now share `order_log`.) The import graph is now a **tree with no loop**: `orders → inventory → log` and `orders → log`. This is the fix to prefer. Draw your modules as boxes and imports as arrows. Arrows should point "down" from high-level modules (the command line, the app) to low-level ones (rules, helpers, constants), never back up.

### 10.5 Fix 2: import inside the function

If moving code is not possible right now, delay the import until it is really needed. `shop/inventory.py`:

```python
STOCK = {"pen": 10, "book": 2}

def in_stock(item, qty):
    ok = STOCK.get(item, 0) >= qty
    if not ok:
        from shop.orders import order_log   # imported only when needed
        order_log(f"low stock: {item}")
    return ok
```

With the original `orders.py` and `main.py`, it prints `ordered 3 x pen`, `LOG: low stock: book`, `sorry, not enough book`. At import time, `inventory.py` imports nothing, so there is no cycle. By the time `in_stock` is **called**, both modules have finished loading, and `order_log` exists. Because of the cache (section 3.3), the import inside the function is cheap after the first call. The cost: the dependency is hidden inside a function, where readers do not expect it. Leave a comment.

### 10.6 Fix 3: import the module, not the name

`from shop.orders import order_log` needs the **name** `order_log` at import time. `from shop import orders` (or `import shop.orders`) needs only the **module object**, which exists in the cache even while it is half-loaded. Then the name is looked up later, when the function runs. `shop/inventory.py`:

```python
from shop import orders          # the module, not a name inside it

STOCK = {"pen": 10, "book": 2}

def in_stock(item, qty):
    ok = STOCK.get(item, 0) >= qty
    if not ok:
        orders.order_log(f"low stock: {item}")   # looked up at call time
    return ok
```

`python main.py` prints the same three lines as fix 2. This works **only if** the name is used inside functions, not at the top level of the module. Predict what happens with this version of `inventory.py`:

```python
from shop import orders

STOCK = {"pen": 10, "book": 2}
log = orders.order_log          # used at import time!

def in_stock(item, qty):
    ok = STOCK.get(item, 0) >= qty
    if not ok:
        log(f"low stock: {item}")
    return ok
```

<details><summary>Answer</summary>

```text
$ python main.py
Traceback (most recent call last):
  File "/home/you/project/main.py", line 1, in <module>
    from shop.orders import place_order
  File "/home/you/project/shop/orders.py", line 1, in <module>
    from shop.inventory import in_stock
  File "/home/you/project/shop/inventory.py", line 4, in <module>
    log = orders.order_log          # used at import time!
          ^^^^^^^^^^^^^^^^
AttributeError: partially initialized module 'shop.orders' from '/home/you/project/shop/orders.py' has no attribute 'order_log' (most likely due to a circular import)
```

Line 4 runs while `inventory` is being imported, which is while `orders` is still paused at its line 1. The module object exists (so `from shop import orders` worked), but `order_log` is not defined in it yet. Same cycle, now an `AttributeError` instead of an `ImportError`. Any use at import time breaks it: a top-level assignment, a default argument value (`def f(log=orders.order_log)`), or a decorator.
</details>

### 10.7 Summary of the fixes

| Fix | How | When |
|---|---|---|
| 1. Move shared code | put it in a new low-level module that imports neither side | **the default**: it fixes the design |
| 2. Import inside a function | `from x import y` inside the function that needs it | quick fix; also for slow or optional imports |
| 3. Import the module | `from shop import orders`, then `orders.y` inside functions | when the two modules really belong together |

A note on files that are **not** in a package. If `orders.py` and `inventory.py` sit directly next to the script you run (no `shop/` folder), Python 3.13 and later show a different message for the same cycle:

```text
ImportError: cannot import name 'order_log' from 'orders' (consider renaming '/home/you/project/orders.py' if it has the same name as a library you intended to import)
```

Python cannot be sure whether the problem is a cycle or a shadowed library (section 4.4), so it suggests renaming. Read the chain of `File ... line ...` lines anyway: if the same module appears twice, it is a cycle.

## 11. `importlib`: dynamic imports and plugins

### 11.1 Importing a name you get at run time

`import json` needs the name `json` written in the source code. Sometimes the program learns the module name only **while running**: from a config file, a command-line argument, or by looking at the files in a folder. For this, use **`importlib.import_module(name)`**. It takes a **string** and returns the module object, with exactly the same rules as `import` (search `sys.path`, use the cache, run once).

`imp.py`:

```python
import importlib

name = "json"
json_module = importlib.import_module(name)
print(json_module.dumps({"a": 1}))

math_module = importlib.import_module("math")
print(math_module.sqrt(16))

for name in ["statistics", "fancy_stats"]:
    try:
        module = importlib.import_module(name)
        print("loaded", module.__name__)
    except ModuleNotFoundError as e:
        print("missing:", e)
```
```text
{"a": 1}
4.0
loaded statistics
missing: No module named 'fancy_stats'
```

`import_module("a.b.c")` imports the dotted name, running the packages on the way, just like `import a.b.c`, but it **returns the module `a.b.c` itself** (not the top package `a`). Prefer it to the low-level `__import__` or to `exec("import " + name)`.

### 11.2 Is a module available? `find_spec`

`importlib.util.find_spec(name)` searches for a module **without running it**. It returns `None` if the module cannot be found. This is the usual way to support an **optional** library:

```python
import importlib.util
for name in ["json", "fancy_stats", "textplugins.shout"]:
    print(name, "->", importlib.util.find_spec(name) is not None)
```

Run in the plugin folder of the next section:

```text
json -> True
fancy_stats -> False
textplugins.shout -> True
```

(Careful: for a dotted name such as `textplugins.shout`, `find_spec` imports the parent package `textplugins` first, so its `__init__.py` does run.)

### 11.3 A plugin system in 30 lines

A **plugin** is a piece of code that adds a feature **without changing the main program**. The main program discovers plugins at run time. With `importlib`, a plugin system can be as simple as "every module in this package folder is a plugin".

```text
project/
├── tool.py
└── textplugins/
    ├── __init__.py      (empty)
    ├── count.py
    ├── reverse.py
    └── shout.py
```

Every plugin has a docstring and a function `run(text)`. `textplugins/shout.py`:

```python
"""Make text loud."""

def run(text):
    return text.upper() + "!"
```

`textplugins/reverse.py`:

```python
"""Reverse the text."""

def run(text):
    return text[::-1]
```

`textplugins/count.py`:

```python
"""Count the words."""

def run(text):
    return f"{len(text.split())} words"
```

`tool.py` finds the plugins with `pkgutil.iter_modules` (it lists the modules inside a list of folders, without importing them) and loads each one with `import_module`:

```python
import importlib
import pkgutil
import sys

import textplugins

def load_plugins(package):
    """Return {name: module} for every module inside the package folder."""
    found = {}
    for info in pkgutil.iter_modules(package.__path__):
        module = importlib.import_module(f"{package.__name__}.{info.name}")
        if hasattr(module, "run"):
            found[info.name] = module
    return found

def main(argv):
    plugins = load_plugins(textplugins)
    if len(argv) != 2 or argv[0] not in plugins:
        print("usage: tool.py PLUGIN TEXT", file=sys.stderr)
        for name in sorted(plugins):
            print(f"  {name:8} {plugins[name].__doc__}", file=sys.stderr)
        return 2
    print(plugins[argv[0]].run(argv[1]))
    return 0

if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
```

```text
$ python tool.py shout "hello there"
HELLO THERE!
$ python tool.py reverse "hello there"
ereht olleh
$ python tool.py
usage: tool.py PLUGIN TEXT
  count    Count the words.
  reverse  Reverse the text.
  shout    Make text loud.
```

(The last command exits with code 2: wrong usage, as in core.12.) The registry is just a dictionary from a name to a module. `hasattr(module, "run")` skips modules that are not real plugins.

### 11.4 Try it: add a plugin without touching `tool.py`

Create `textplugins/title.py` that turns `"hello there"` into `"Hello There"`, with a docstring. Do not change `tool.py`. Then run `python tool.py title "hello there"` and `python tool.py`.

<details><summary>Answer</summary>

`textplugins/title.py`:

```python
"""Capitalise Each Word."""

def run(text):
    return text.title()
```

```text
$ python tool.py title "hello there"
Hello There
```

And `python tool.py` now lists `title` as well, after `shout`. The main program learned a new feature by itself: that is the point of a plugin system. Real tools work the same way at a bigger scale: `pytest` finds plugins, and installed packages can announce plugins to each other through **entry points** (the same mechanism as the console scripts of section 15).
</details>

### 11.5 Plugins are code: a safety note

`import_module` **runs** the module. Loading plugins from a folder means running every `.py` file in it. Load plugins only from folders you control, never from a folder where other people (or downloads) can put files. It is the same lesson as `pickle` in core.12: loading can run code.

A plugin system might be tempted to "reload plugins while running" with `importlib.reload`. Remember the trap of section 3.7: old references still point to old functions. For a command-line tool, simply run it again.

## 12. Virtual environments

### 12.1 The problem: one Python, many projects

So far we talked about **your** modules. Now look at **installed** packages: the ones in `site-packages`, the last entry of `sys.path` (section 4.1). If every project installs its libraries into that **one** shared folder, trouble comes quickly:

- **Version conflicts.** Project A needs `django 4.2`; project B needs `django 5.1`. One folder holds only one version.
- **"Works on my machine".** Your project quietly uses a library you installed a year ago and never wrote down. On your friend's laptop it fails.
- **Breaking the system.** On Linux, the operating system's own tools use the system Python's packages; upgrading one with `pip` can break them (section 12.6).

The solution is a **virtual environment** (often called a **venv**): a small folder that holds its **own** `site-packages` and its own `python` and `pip` commands, linked to a base Python installation. Each project gets its own. Packages installed into one environment are invisible to all others.

### 12.2 Creating one

`venv` is part of the standard library. In your project folder:

```text
$ python3 -m venv .venv
$ ls .venv/bin
Activate.ps1
activate
activate.csh
activate.fish
pip
pip3
pip3.14
python
python3
python3.14
𝜋thon
```

(Captured on Linux. On Windows the folder is `.venv\Scripts` and holds `python.exe`, `pip.exe` and `activate.bat`. The command there is usually `py -m venv .venv`. The odd name `𝜋thon` is a small joke added in Python 3.14: it is just one more name for the same `python`.)

`.venv` is the conventional name: the dot hides it in normal listings, and tools such as editors and `uv` look for it. Besides `bin/`, it contains `lib/`, `include/` and a file `pyvenv.cfg`:

- `bin/python` is the environment's Python. It is a **link to the base Python** (here `/usr/bin/python3.14`), not a copy.
- `lib/python3.14/site-packages/` is the environment's **own, empty** package folder.
- `pyvenv.cfg` tells Python "you are inside an environment, and here is your base":

```text
$ cat .venv/pyvenv.cfg
home = /usr/bin
include-system-site-packages = false
version = 3.14.4
executable = /usr/bin/python3.14
command = /usr/bin/python3 -m venv /home/you/project/.venv
```

(Machine-specific values: your version and paths will differ.)

Three rules about the `.venv` folder. **Do not commit it** to git (it is big and machine-specific; put `.venv/` in `.gitignore` and commit the **list** of what to install instead, section 13). **Do not move or rename it** (its scripts contain absolute paths). And treat it as **disposable**: if it gets messy, delete it and create it again, which takes a minute when your requirements are written down.

### 12.3 Activating

**Activating** an environment changes your shell so that `python` and `pip` mean the environment's versions. On Linux and macOS (bash or zsh):

```text
$ which python3
/usr/bin/python3
$ source .venv/bin/activate
(.venv) $ which python
/home/you/project/.venv/bin/python
(.venv) $ python -c "import sys; print(sys.prefix); print(sys.base_prefix); print(sys.prefix != sys.base_prefix)"
/home/you/project/.venv
/usr
True
(.venv) $ pip list
Package Version
------- -------
pip     25.1.1
(.venv) $ deactivate
$ which python3
/usr/bin/python3
```

(The `(.venv)` prefix in the prompt is added by `activate` so that you can see which environment is active. The paths and the pip version are from the test machine.)

On Windows: `.venv\Scripts\activate` in `cmd`, or `.venv\Scripts\Activate.ps1` in PowerShell. (Not captured here; the effect is the same.)

What `activate` really does is small: it puts `.venv/bin` at the **front of `PATH`** (so the shell finds `.venv/bin/python` before `/usr/bin/python3`), sets the variable `VIRTUAL_ENV`, changes the prompt, and defines a `deactivate` command that undoes all of this.

Activation is only a **convenience**. You can always call the environment's Python by its path, without activating anything. Scripts, cron jobs and editors often do exactly that:

```text
$ .venv/bin/python -c "import sys; print(sys.prefix)"
/home/you/project/.venv
```

### 12.4 How Python knows it is in an environment

Inside the environment, look at `sys.path`:

```text
(.venv) $ python -c "import sys; print(*sys.path, sep=chr(10))"

/usr/lib/python314.zip
/usr/lib/python3.14
/usr/lib/python3.14/lib-dynload
/home/you/project/.venv/lib/python3.14/site-packages
```

(The first, empty line is `''`, the current folder, because we used `-c`.)

The **standard library** still comes from the base Python (`/usr/lib/python3.14`): it is shared, not copied. But the system's `dist-packages` folders are **gone**, replaced by the environment's own `site-packages`. When Python starts, it finds `pyvenv.cfg` next to (or one folder above) its executable and sets `sys.prefix` to the environment. That is all a virtual environment is: **a different `site-packages` folder**.

In your own code, `sys.prefix != sys.base_prefix` tells you that you are running inside a virtual environment.

### 12.5 `python -m pip`, not just `pip`

A very common confusion: `pip` installs into one environment, but `python` runs from another. Then you install a package, and `import` still says `ModuleNotFoundError`. This happens when `pip` and `python` on your `PATH` belong to different installations (for example after creating an environment but forgetting to activate it in a new terminal).

The safe habit: **run pip through the Python you are going to use.**

```text
(.venv) $ python -m pip --version
pip 25.1.1 from /home/you/project/.venv/lib/python3.14/site-packages/pip (python 3.14)
```

The output shows **where** pip will install. `python -m pip install x` always installs into the environment of **that** `python`. When in doubt, also check `which python` (Linux, macOS) or `where python` (Windows).

### 12.6 Why not install into the system Python?

On Ubuntu and Debian (and more and more other systems), the system Python is marked **externally managed**: the operating system's package manager owns it. If you try `pip install something` there, outside any environment, pip stops with an error that starts like this (**not captured**: we did not try to install into the system on purpose; the text below is copied from the system's `EXTERNALLY-MANAGED` file and shortened):

```text
error: externally-managed-environment

× This environment is externally managed
╰─> To install Python packages system-wide, try apt install
    python3-xyz, where xyz is the package you are trying to
    install.

    If you wish to install a non-Debian-packaged Python package,
    create a virtual environment using python3 -m venv path/to/venv.
    Then use path/to/venv/bin/python and path/to/venv/bin/pip. ...
```

The message gives the right advice: **create a virtual environment**. Do not "fix" it with `--break-system-packages` or `sudo pip install`. Those flags exist for experts who know exactly what they are breaking.

The rule for the rest of your career: **one project, one virtual environment.** Make it the first thing you do in a new project.

## 13. `pip`: installing and pinning

### 13.1 What `pip install` does

**pip** is the standard installer for Python packages. `pip install NAME` **finds** the package (by default on **PyPI**, the Python Package Index at `pypi.org`, with over half a million packages), **chooses a version** that matches your request and your Python, **resolves dependencies** (the package's requirements, and theirs, and so on), **downloads** the files (usually **wheels**, ready-to-install archives; section 16), and **installs** them into the `site-packages` of the current environment, plus any command-line scripts into `bin/`.

For example, `pip install requests` downloads `requests` and its dependencies (`charset-normalizer`, `idna`, `urllib3`, `certifi`) and prints `Successfully installed ...` with the five names and versions (**not captured**: that needs the internet).

### 13.2 Our offline practice packages

To show pip's real behaviour without the internet, this chapter uses three tiny practice packages that we build ourselves. A folder of built packages is called a **wheelhouse**. We tell pip to look **only** there:

- `--no-index` means "do not contact PyPI";
- `--find-links wheelhouse` means "look for package files in the folder `wheelhouse`".

The wheelhouse holds three versions of `greetkit` and one `shoutkit`:

```text
project/
└── wheelhouse/
    ├── greetkit-1.0.0-py3-none-any.whl
    ├── greetkit-1.2.0-py3-none-any.whl
    ├── greetkit-2.0.0-py3-none-any.whl
    └── shoutkit-0.3.0-py3-none-any.whl
```

`greetkit` has one function, `hello(name)`, which also says its own version. `shoutkit` **depends on** `greetkit`: its `pyproject.toml` contains `dependencies = ["greetkit>=1.0,<2"]`, and its code is:

```python
from greetkit import hello

def shout(name):
    return hello(name).upper()
```

Section 16 explains how a folder with a `pyproject.toml` becomes a `.whl` file. At the end of section 16.5 you will find the full source of these practice packages and the command that builds them, so you can repeat every step of this section yourself.

### 13.3 Installing, upgrading, downgrading

All commands below run inside a fresh, activated environment in `project/`. The first one asks for `greetkit` with no version:

```text
(.venv) $ pip install --no-index --find-links wheelhouse greetkit
Looking in links: wheelhouse
Processing ./wheelhouse/greetkit-2.0.0-py3-none-any.whl
Installing collected packages: greetkit
Successfully installed greetkit-2.0.0
```

With no version given, pip takes the **newest** one available: 2.0.0. Now ask for "at least 1.0, but below 2":

```text
(.venv) $ pip install --no-index --find-links wheelhouse "greetkit>=1.0,<2"
Looking in links: wheelhouse
Processing ./wheelhouse/greetkit-1.2.0-py3-none-any.whl
Installing collected packages: greetkit
  Attempting uninstall: greetkit
    Found existing installation: greetkit 2.0.0
    Uninstalling greetkit-2.0.0:
      Successfully uninstalled greetkit-2.0.0
Successfully installed greetkit-1.2.0
```

The installed 2.0.0 did not match, so pip **replaced** it with the newest version that does: 1.2.0. An environment holds **one version** of each package at a time. Put the requirement in quotes: without them the shell would treat `<` as "read input from a file".

An exact version works the same way: `pip install ... greetkit==1.0.0` uninstalls 1.2.0 and installs 1.0.0 (same kind of output, so not repeated). A version that does not exist:

```text
(.venv) $ pip install --no-index --find-links wheelhouse greetkit==3.0
Looking in links: wheelhouse
ERROR: Could not find a version that satisfies the requirement greetkit==3.0 (from versions: 1.0.0, 1.2.0, 2.0.0)
ERROR: No matching distribution found for greetkit==3.0
```

The error helpfully lists the versions it **can** see. Other everyday commands: `pip install --upgrade NAME` (newest allowed version), `pip uninstall NAME`, `pip list`, `pip show NAME`.

### 13.4 Dependencies

Now install `shoutkit`, which needs `greetkit>=1.0,<2`:

```text
(.venv) $ pip install --no-index --find-links wheelhouse shoutkit
Looking in links: wheelhouse
Processing ./wheelhouse/shoutkit-0.3.0-py3-none-any.whl
Requirement already satisfied: greetkit<2,>=1.0 in ./.venv/lib/python3.14/site-packages (from shoutkit) (1.0.0)
Installing collected packages: shoutkit
Successfully installed shoutkit-0.3.0
(.venv) $ python -c 'from shoutkit import shout; print(shout("Asha"))'
HELLO, ASHA! (GREETKIT 1.0.0)
(.venv) $ pip show shoutkit | grep -E "Version|Location|Requires"
Version: 0.3.0
Location: /home/you/project/.venv/lib/python3.14/site-packages
Requires: greetkit
```

pip read `shoutkit`'s requirement, saw that the installed `greetkit 1.0.0` already satisfies it, and kept it. `pip show` prints facts about an installed package (here filtered with `grep` to three lines): its version, where it is installed, and what it **requires**.

What if you now force a version that breaks `shoutkit`'s rule?

```text
(.venv) $ pip install --no-index --find-links wheelhouse greetkit==2.0.0
Looking in links: wheelhouse
Processing ./wheelhouse/greetkit-2.0.0-py3-none-any.whl
Installing collected packages: greetkit
  Attempting uninstall: greetkit
    Found existing installation: greetkit 1.0.0
    Uninstalling greetkit-1.0.0:
      Successfully uninstalled greetkit-1.0.0
ERROR: pip's dependency resolver does not currently take into account all the packages that are installed. This behaviour is the source of the following dependency conflicts.
shoutkit 0.3.0 requires greetkit<2,>=1.0, but you have greetkit 2.0.0 which is incompatible.
Successfully installed greetkit-2.0.0
(.venv) $ pip check
shoutkit 0.3.0 has requirement greetkit<2,>=1.0, but you have greetkit 2.0.0.
```

Read this carefully: pip printed `ERROR`, **but it still installed 2.0.0**, and the command finished with exit code 0. You asked for it explicitly, so pip did it and warned you. The environment is now **broken**: `shoutkit` may fail at run time. `pip check` (exit code 1 here) verifies the whole environment; it is a good command to run in automated checks.

This is why environments drift into a mess when people install things one by one by hand, and why the next sections are about **writing requirements down**.

### 13.5 Version specifiers

The text after the package name is a **version specifier**. Versions are compared part by part as numbers (`1.10.0` is newer than `1.9.0`).

| Specifier | Meaning | With versions 1.0.0, 1.2.0, 2.0.0 available, pip picks |
|---|---|---|
| (none) | any version | 2.0.0 |
| `==1.0.0` | exactly this version | 1.0.0 |
| `>=1.0` | this or newer | 2.0.0 |
| `>1` | strictly newer than 1 | 2.0.0 |
| `<1.2` | older than 1.2 | 1.0.0 |
| `>=1.0,<2` | both conditions (comma means "and") | 1.2.0 |
| `!=1.2.0` | anything except this one (for a known bad release) | |
| `~=1.0` | "compatible release": `>=1.0` and `==1.*` | 1.2.0 |
| `==1.*` | any 1.x version | 1.2.0 |

Most packages follow **semantic versioning** (`MAJOR.MINOR.PATCH`): a new **patch** fixes bugs, a new **minor** adds features without breaking anything, and a new **major** version may break your code. So `>=1.0,<2` (or `~=1.0`) says "any 1.x release, but not the next major version that might break me". This is the normal way to declare a dependency in a library.

### 13.6 Predict: which version is installed?

The wheelhouse has `greetkit` 1.0.0, 1.2.0 and 2.0.0. What does each command install?

1. `pip install "greetkit>=1.0,!=1.2.0,<2"`
2. `pip install "greetkit<1.2"`
3. `pip install "greetkit~=1.0"`
4. `pip install "greetkit>1"`

<details><summary>Answer</summary>

Checked with `pip list` after each command:

1. **1.0.0**: 1.2.0 is excluded by `!=`, and 2.0.0 by `<2`.
2. **1.0.0**: the only version below 1.2.
3. **1.2.0**: `~=1.0` means `>=1.0, ==1.*`, and pip takes the newest match.
4. **2.0.0**: `1.0.0` is not *greater* than `1`, because `1` means `1.0.0`. Only 2.0.0 is.

pip always picks the **newest** version that satisfies **all** the conditions.
</details>

### 13.7 `requirements.txt` and `pip freeze`

A **requirements file** is a plain text file with one requirement per line. By tradition it is called `requirements.txt`, and it lives in the project root and **is committed to git**:

```text
greetkit==1.2.0
shoutkit==0.3.0
```

`pip install -r requirements.txt` installs everything in it. In a brand-new environment:

```text
(.venv) $ pip install --no-index --find-links wheelhouse -r requirements.txt
Looking in links: wheelhouse
Processing ./wheelhouse/greetkit-1.2.0-py3-none-any.whl (from -r requirements.txt (line 1))
Processing ./wheelhouse/shoutkit-0.3.0-py3-none-any.whl (from -r requirements.txt (line 2))
Installing collected packages: greetkit, shoutkit

Successfully installed greetkit-1.2.0 shoutkit-0.3.0
```

How do you produce such a file? **`pip freeze`** prints every installed package with its **exact** version, in requirements format:

```text
(.venv) $ pip freeze
greetkit==1.2.0
shoutkit==0.3.0
(.venv) $ pip freeze > requirements.txt
```

`pip freeze > requirements.txt` takes a snapshot of the environment. On another computer, `python -m venv .venv`, activate, `pip install -r requirements.txt`, and you have the same versions.

Two weaknesses of `pip freeze`: it records **everything** in the environment, even a package you installed once for an experiment; and it does not separate what **you** asked for (`shoutkit`) from what came **along** as a dependency (`greetkit`), so later you cannot tell which lines you may delete.

A common, simple fix is two files: `requirements.in` lists only what you need, with ranges (`shoutkit>=0.3`); `requirements.txt` is the frozen, exact result. Tools such as `pip-tools` (`pip-compile`) and `uv pip compile` produce the second file from the first. Lock files (next section) take the idea further.

### 13.8 Ranges or pins? Applications and libraries

Should you write `greetkit>=1.0,<2` (a **range**) or `greetkit==1.2.0` (a **pin**)? It depends on what you are building:

| You are building | Write | Why |
|---|---|---|
| A **library** (other people install it inside their projects) | **ranges** in `pyproject.toml`: `greetkit>=1.0,<2` | Your library lives in someone else's environment, next to other libraries. Exact pins would make it impossible to install together with anything that needs a different patch version. |
| An **application** (a website, a tool, a script you deploy) | **pins** in a lock file or `requirements.txt`: `greetkit==1.2.0` | You control the whole environment and want the **same** versions everywhere: your laptop, your teammate's, the server, next year. |

Most applications have both: ranges that say what is **allowed** (in `pyproject.toml`), and pins that say what is **used** (in a lock file).

### 13.9 Why reproducibility matters

Imagine your project only says `requests`, with no version. Today pip installs version X and everything works. Six months later, a new teammate gets version Y, which changed one function. Their copy fails; yours works; nobody changed a line of your code. A **reproducible** environment (the same input files always give the same installed versions) prevents this. Pins also make upgrades a **decision**: you change the pin on purpose, run the tests, and commit, instead of upgrades happening to you by surprise.

## 14. Lock files, `uv` and `poetry`

### 14.1 What a lock file adds

A frozen `requirements.txt` already pins versions. A **lock file** goes further. For **every** package in the dependency tree it records the **exact version**, **where** it came from, and a **hash** of the file (a fingerprint such as `sha256 = "..."`, so the installer can refuse a changed or corrupted file). Tool lock files often also cover **every platform** (Linux, Windows, macOS) at once.

A lock file is written by a tool, never by hand. It is committed to git. Everyone installs **from the lock file**, so everyone gets exactly the same bytes.

Since 2025 there is a standard lock file format, `pylock.toml` (PEP 751). The pip version on the test machine can already write one with the **experimental** command `pip lock`:

```text
(.venv) $ pip lock --no-index --find-links wheelhouse shoutkit
WARNING: pip lock is currently an experimental command. It may be removed/changed in a future release without prior warning.
Looking in links: wheelhouse
Processing ./wheelhouse/shoutkit-0.3.0-py3-none-any.whl
Processing ./wheelhouse/greetkit-1.2.0-py3-none-any.whl (from shoutkit)
(.venv) $ cat pylock.toml
lock-version = "1.0"
created-by = "pip"

[[packages]]
name = "greetkit"
version = "1.2.0"

[[packages.wheels]]
name = "greetkit-1.2.0-py3-none-any.whl"
url = "file:///home/you/project/wheelhouse/greetkit-1.2.0-py3-none-any.whl"

[packages.wheels.hashes]
sha256 = "2eb838f8d0504907695bc243200cd1e1471a81cc2f4771d9f1e3fc1e59f0b1ea"

[[packages]]
name = "shoutkit"
version = "0.3.0"

[[packages.wheels]]
name = "shoutkit-0.3.0-py3-none-any.whl"
url = "file:///home/you/project/wheelhouse/shoutkit-0.3.0-py3-none-any.whl"

[packages.wheels.hashes]
sha256 = "2bdbb3d3e79c1d99042dafc079dc3b36f43ce529aa2fd6c74078bf5b57cd306a"
```

(Machine-specific: the URLs and the hashes. Your wheels are built on a different day, so their bytes and hashes differ.)

You asked only for `shoutkit`, but the lock file lists `greetkit` too, with the version chosen by the resolver (1.2.0, the newest below 2), plus a hash for each file. It is TOML, which you can read with `tomllib` (core.12).

### 14.2 `uv`: a fast all-in-one tool

**uv** is a newer tool (written in Rust, by the company Astral) that replaces `pip`, `venv`, `pip-tools` and more, and is much faster. It is not part of Python; you install it once (see its documentation). It was **not installed on the test machine**, so the commands below are **shown, not run**, and their effects are described in words.

The everyday project workflow:

```text
$ uv init organise-tool        # new project folder with pyproject.toml
$ cd organise-tool
$ uv add requests              # add a dependency: updates pyproject.toml AND uv.lock
$ uv add --dev pytest          # a development-only dependency
$ uv run python main.py        # run inside the project's environment
$ uv run pytest                # same for tools
$ uv lock                      # recompute uv.lock after editing pyproject.toml by hand
$ uv sync                      # make .venv match uv.lock exactly
```

Behind the scenes, `uv add requests` writes a range such as `"requests>=2.32.3"` into the `dependencies` list of `pyproject.toml`, resolves the whole tree, writes **`uv.lock`** (exact versions and hashes for all platforms), and installs everything into `.venv`, creating it if needed. `uv run ...` first makes sure `.venv` matches `uv.lock`, then runs the command inside it, so you never need to activate anything. A teammate who clones the repository runs `uv sync` and gets exactly your versions.

uv also has a pip-compatible mode for older projects: `uv venv` creates `.venv`, `uv pip install -r requirements.txt` installs, and `uv pip compile requirements.in -o requirements.txt` produces a pinned file. `uv tool install NAME` installs a command-line tool into its own private environment (like `pipx`).

### 14.3 `poetry`

**Poetry** is an older, very popular project manager with the same idea: one tool for dependencies, environments, locking and building. Also **not installed on the test machine**; commands shown, not run:

```text
$ poetry new organise-tool     # create a project skeleton
$ poetry add requests          # add a dependency, update poetry.lock, install
$ poetry add --group dev pytest
$ poetry install               # install everything from poetry.lock
$ poetry run pytest            # run inside the project's environment
$ poetry lock                  # recompute the lock file
$ poetry build                 # build the wheel and the sdist (section 16)
```

Poetry writes **`poetry.lock`**. Newer Poetry versions (2.0 and later) use the standard `[project]` table in `pyproject.toml`; older projects keep their settings in a `[tool.poetry]` table instead.

### 14.4 Which tool should you use?

All of them work with the same standards: `pyproject.toml`, wheels, PyPI, virtual environments. The choice matters less than **using one consistently**:

| Tool | Comes with Python | Lock file | Good for |
|---|---|---|---|
| `venv` + `pip` | yes | `requirements.txt` from `pip freeze` (or `pip lock`) | learning, small scripts, any machine, no extra install |
| `uv` | no | `uv.lock` | speed and one tool for everything; increasingly the default for new projects |
| `poetry` | no | `poetry.lock` | many existing projects use it |

In this course we use **`venv` and `pip`**, because they are always available and they show what the other tools automate. If you join a project, use whatever it already uses: look for `uv.lock`, `poetry.lock` or `requirements.txt` in the repository.

Rules for every tool: **commit** `pyproject.toml` and the lock file (or `requirements.txt`), never `.venv/`; do not edit lock files by hand (change the requirement, then re-lock); and do not mix tools in one project (a `pip install` by hand into a `uv`-managed environment makes the lock file lie).

## 15. `pyproject.toml` anatomy

### 15.1 From folder to installable package

Until now, your own packages were importable only from the folder that contains them (section 4). To use your code **anywhere**, like `json` or `requests`, you **install** it into an environment. For that, pip needs to know a few facts: the package's name and version, which Python it needs, what it depends on, which commands it provides, and which tool can turn the source folder into an installable file.

All of this goes in one file in the project root: **`pyproject.toml`**. It is TOML, the format you read with `tomllib` in core.12. (Older projects used a `setup.py` script or a `setup.cfg` file for the same job. You will still meet them; new projects use `pyproject.toml`.)

Two words to keep apart. An **import package** is a folder with `__init__.py` (section 6). A **distribution package** is the thing you `pip install`: a named, versioned archive, such as `requests-2.32.3`. Usually a distribution contains one import package with the same name, but not always (installing `beautifulsoup4` gives you `import bs4`).

### 15.2 A complete example

Here is the `pyproject.toml` we will use for the file organiser in section 17:

```toml
[build-system]
requires = ["setuptools>=77"]
build-backend = "setuptools.build_meta"

[project]
name = "organise"
version = "0.1.0"
description = "Sort the files of a folder into sub-folders."
readme = "README.md"
requires-python = ">=3.11"
license = "MIT"
authors = [{ name = "Your Name" }]
dependencies = []

[project.optional-dependencies]
dev = ["pytest>=8"]

[project.scripts]
organise = "organise.cli:main"
```

It has three parts. We go through them one by one.

### 15.3 `[build-system]`: who builds the package

pip does not build packages itself. It asks a **build backend**, a library that knows how to turn your source folder into a wheel (section 16). `[build-system]` names it:

- `requires`: what must be installed to **build** (not to run) the package. Here: `setuptools`, version 77 or newer (77 is the first version that understands `license = "MIT"` as a plain string).
- `build-backend`: the module inside that library that pip calls. For setuptools it is `setuptools.build_meta`.

Popular backends and their lines:

| Backend | `requires` | `build-backend` |
|---|---|---|
| setuptools | `["setuptools>=77"]` | `"setuptools.build_meta"` |
| hatchling | `["hatchling"]` | `"hatchling.build"` |
| flit | `["flit_core>=3.4"]` | `"flit_core.buildapi"` |

For a pure-Python package they all do the same job. The `[project]` table below is standard and works the same with all of them. We use setuptools in this chapter because it was available offline on the test machine.

### 15.4 `[project]`: the metadata

| Key | Meaning |
|---|---|
| `name` | the **distribution name**, used in `pip install organise`. Letters, digits, `-`, `_`, `.`. |
| `version` | the version string, `MAJOR.MINOR.PATCH` (section 13.5). Change it for every release. |
| `description` | one line; shown by `pip show` and on PyPI |
| `readme` | a file whose text becomes the long description |
| `requires-python` | which Python versions are supported; pip refuses to install on others |
| `license` | the licence, as a standard short name such as `"MIT"` |
| `authors` | a list of tables with `name` (and optionally `email`) |
| `dependencies` | what must be installed to **run** the package, as a list of requirement strings |

`dependencies` uses the same specifiers as pip (section 13.5), and, because this is a description of what is **allowed**, it should use **ranges**, not pins:

```toml
dependencies = [
    "requests>=2.31,<3",
    "rich>=13",
]
```

Our organiser uses only the standard library, so its list is empty. When pip installs `organise`, it installs every package in `dependencies` too, just as installing `shoutkit` pulled in `greetkit` in section 13.4.

### 15.5 Optional dependencies ("extras")

```toml
[project.optional-dependencies]
dev = ["pytest>=8"]
```

An **extra** is a named group of additional dependencies that are installed only when asked for, with square brackets:

```text
$ pip install "organise[dev]"      # organise + pytest
$ pip install -e ".[dev]"          # the same, for the project in this folder (section 16.6)
```

Typical extras: `dev` or `test` (tools for developers), or optional features (`pandas[excel]` adds Excel support). Users who do not need them do not pay for them.

### 15.6 `[project.scripts]`: console scripts

```toml
[project.scripts]
organise = "organise.cli:main"
```

This line says: "when the package is installed, create a **command** called `organise`. When someone runs it, import the module `organise.cli` and call its function `main()`; the return value becomes the exit code." It is called an **entry point** or **console script**. The format is `command = "module.path:function"`.

This is how `pip`, `pytest` and `uv` become commands that you can type in the terminal. After installation there is a small script file in the environment's `bin/` folder (`Scripts\organise.exe` on Windows). Section 17.6 shows its content.

The function should take **no required arguments** (it is called as `main()`), read `sys.argv` itself (through `argparse`), and **return an exit code**. The `main(argv=None)` shape from core.12 is exactly right.

### 15.7 `[tool.*]`: settings for other tools

Many tools read their settings from `pyproject.toml` too, each from its own table: `[tool.pytest.ini_options]`, `[tool.uv]`, `[tool.setuptools]`. pip ignores them. One file holds the whole project configuration.

## 16. Building and installing a package

### 16.1 The src layout

Where do the package files go inside the project? There are two common layouts:

```text
flat layout                      src layout
-----------                      ----------
organise-project/                organise-project/
├── pyproject.toml               ├── pyproject.toml
├── organise/                    ├── src/
│   ├── __init__.py              │   └── organise/
│   └── ...                      │       ├── __init__.py
└── tests/                       │       └── ...
                                 └── tests/
```

The **src layout** puts the import package one level down, inside `src/`. That looks like an extra folder for nothing. The reason is section 4.1: Python puts the **current folder** (or the script's folder) at the front of `sys.path`. With the flat layout, when you run anything from the project root, `import organise` finds the **local folder**, not the installed package.

We can see it. Below, the package was installed into an environment called `fresh` (section 17.5 shows how). Then we import it from a flat-layout folder, and from the src-layout project root, with the same Python:

```text
$ cd /home/you/flat
$ ls
organise
$ /home/you/elsewhere/fresh/bin/python -c "import organise; print(organise.__file__)"
/home/you/flat/organise/__init__.py

$ cd /home/you/organise-project
$ /home/you/elsewhere/fresh/bin/python -c "import organise; print(organise.__file__)"
/home/you/elsewhere/fresh/lib/python3.14/site-packages/organise/__init__.py
```

(Here `flat/` holds a copy of the `organise` package folder and nothing else. We call the environment's Python by its full path; section 12.3 explains why that works without activating.)

In the flat folder, the local copy **shadows** the installed one. Why does that matter? Suppose you forgot to include a file in the package, or your package depends on a library you forgot to list. With the flat layout, your tests still pass, because they import the local folder. Your users get the broken installed version. With the src layout, the project root has no `organise` folder, so tests and tools must use the **installed** package. You test what your users get.

And without installing, the src layout refuses to import at all:

```text
$ cd organise-project
$ python3 -c "import organise"
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    import organise
ModuleNotFoundError: No module named 'organise'
```

That is a feature, not a bug: it forces you to install the package (usually as an editable install, section 16.6) into your development environment. setuptools finds packages under `src/` automatically; no extra settings are needed.

### 16.2 Wheel and sdist

**Building** a package turns the source folder into files that pip can install. There are two kinds:

| | **sdist** (source distribution) | **wheel** (built distribution) |
|---|---|---|
| File | `organise-0.1.0.tar.gz` | `organise-0.1.0-py3-none-any.whl` |
| Contains | the source tree: `pyproject.toml`, `src/`, `README.md`, tests | the files **exactly as they will be installed**, plus metadata |
| To install it, pip must | **build** it first (run the backend) | only **unzip** it into `site-packages` |
| Speed and safety | slower; runs build code | fast; no code runs during install |

When you publish a release, you upload **both**. pip prefers the wheel; the sdist is the fallback (and the archive of your source).

A wheel is a zip file. Its name is a code: `organise` (name) - `0.1.0` (version) - `py3` (any Python 3) - `none` (no specific Python C interface) - `any` (any operating system). Packages with compiled C code, such as `numpy`, ship one wheel per platform, with names like `...-cp314-cp314-manylinux_2_28_x86_64.whl`. A pure-Python package needs just one `py3-none-any` wheel.

### 16.3 Building: `python -m build`

The standard command is:

```text
$ pip install build
$ python -m build
```

(**Not captured**: installing `build` needs the internet.) `python -m build` creates a temporary, isolated environment, installs what `[build-system] requires` says (setuptools), calls the backend twice, and finishes with a line like `Successfully built organise-0.1.0.tar.gz and organise-0.1.0-py3-none-any.whl`. Both files land in a new `dist/` folder.

Offline, we can do the same steps by hand, and this also shows what `build` does inside. In a build environment that already has setuptools installed:

```text
(buildenv) $ pip wheel --no-deps --no-build-isolation --no-index -w dist .
Processing /home/you/organise-project
  Preparing metadata (pyproject.toml): started
  Preparing metadata (pyproject.toml): finished with status 'done'
Building wheels for collected packages: organise
  Building wheel for organise (pyproject.toml): started
  Building wheel for organise (pyproject.toml): finished with status 'done'
  Created wheel for organise: filename=organise-0.1.0-py3-none-any.whl size=4350 sha256=7a7b89b24c30f7ffbe01befe4662392d0f3469c571bd8cd619811ec7d2bcb2a7
  Stored in directory: /home/you/.cache/pip/wheels/09/b7/0a/4b67d26b989ce25917287386666e303bcfc521aae3092d3b52
Successfully built organise
```

(Machine-specific: the size, the hash and the cache folder.)

`pip wheel` builds a wheel instead of installing it, and `-w dist` writes it into `dist/`. `--no-build-isolation` means "use the setuptools already installed here; do not create a fresh build environment" (that would need the internet). `--no-deps` builds only our package, not its dependencies.

For the sdist, we call the **backend** directly. This is exactly the function that `python -m build` calls:

```text
(buildenv) $ python -c "from setuptools import build_meta; print(build_meta.build_sdist('dist'))"
...
Writing organise-0.1.0/setup.cfg
Creating tar archive
removing 'organise-0.1.0' (and everything under it)
organise-0.1.0.tar.gz
(buildenv) $ ls dist
organise-0.1.0-py3-none-any.whl
organise-0.1.0.tar.gz
```

(The `...` stands for many lines of setuptools progress messages, cut here.) A build backend is just a module with a few agreed functions (`build_wheel`, `build_sdist`, and some helpers). That agreement (PEP 517) is why pip, `build`, `uv` and `poetry` can all build any project, whichever backend it names.

Building also leaves helper folders behind: `build/` and `src/organise.egg-info/`. Add them, and `dist/`, to `.gitignore`.

### 16.4 Looking inside

A wheel is a zip file and an sdist is a `.tar.gz`, so the standard library can list them. `peek.py`, in the folder that contains the project:

```python
import tarfile
import zipfile

with zipfile.ZipFile("dist/organise-0.1.0-py3-none-any.whl") as wheel:
    print("wheel:")
    for name in wheel.namelist():
        print("  ", name)
with tarfile.open("dist/organise-0.1.0.tar.gz") as sdist:
    print("sdist:")
    for name in sorted(sdist.getnames()):
        print("  ", name)
```

Run from the project root (`python ../peek.py`):

```text
wheel:
   organise/__init__.py
   organise/__main__.py
   organise/cli.py
   organise/planner.py
   organise/rules.py
   organise-0.1.0.dist-info/METADATA
   organise-0.1.0.dist-info/WHEEL
   organise-0.1.0.dist-info/entry_points.txt
   organise-0.1.0.dist-info/top_level.txt
   organise-0.1.0.dist-info/RECORD
sdist:
   organise-0.1.0
   organise-0.1.0/PKG-INFO
   organise-0.1.0/README.md
   organise-0.1.0/pyproject.toml
   organise-0.1.0/setup.cfg
   organise-0.1.0/src
   organise-0.1.0/src/organise
   organise-0.1.0/src/organise.egg-info
   organise-0.1.0/src/organise.egg-info/PKG-INFO
   organise-0.1.0/src/organise.egg-info/SOURCES.txt
   organise-0.1.0/src/organise.egg-info/dependency_links.txt
   organise-0.1.0/src/organise.egg-info/entry_points.txt
   organise-0.1.0/src/organise.egg-info/requires.txt
   organise-0.1.0/src/organise.egg-info/top_level.txt
   organise-0.1.0/src/organise/__init__.py
   organise-0.1.0/src/organise/__main__.py
   organise-0.1.0/src/organise/cli.py
   organise-0.1.0/src/organise/planner.py
   organise-0.1.0/src/organise/rules.py
   organise-0.1.0/tests
   organise-0.1.0/tests/test_planner.py
```

- The **wheel** has the import package `organise/` (no `src/`: that folder exists only in your project) and a `.dist-info` folder with metadata. It has **no tests and no `pyproject.toml`**: only what gets installed.
- The **sdist** has the whole source tree, ready to be built again anywhere.

Two of the metadata files can be read straight from the wheel with `ZipFile.read`, which returns bytes. `meta.py`, next to `peek.py`:

```python
import zipfile

with zipfile.ZipFile("dist/organise-0.1.0-py3-none-any.whl") as wheel:
    print(wheel.read("organise-0.1.0.dist-info/entry_points.txt").decode())
    metadata = wheel.read("organise-0.1.0.dist-info/METADATA").decode()
    print("\n".join(metadata.splitlines()[:10]))
```
```text
[console_scripts]
organise = organise.cli:main

Metadata-Version: 2.4
Name: organise
Version: 0.1.0
Summary: Sort the files of a folder into sub-folders.
Author: Your Name
License-Expression: MIT
Requires-Python: >=3.11
Description-Content-Type: text/markdown
Provides-Extra: dev
Requires-Dist: pytest>=8; extra == "dev"
```

Every line of `pyproject.toml` ended up somewhere: `[project.scripts]` in `entry_points.txt`, and the rest in `METADATA`, which is what `pip show` reads after installation.

### 16.5 The practice packages of section 13

Now you can build the `greetkit` and `shoutkit` wheels of section 13 yourself. Each one is a tiny src-layout project:

```text
src-greetkit-1.0.0/
├── pyproject.toml
└── src/
    └── greetkit/
        └── __init__.py
```

`src-greetkit-1.0.0/pyproject.toml`:

```toml
[build-system]
requires = ["setuptools>=61"]
build-backend = "setuptools.build_meta"

[project]
name = "greetkit"
version = "1.0.0"
requires-python = ">=3.10"
```

`src-greetkit-1.0.0/src/greetkit/__init__.py`:

```python
def hello(name):
    return f"Hello, {name}! (greetkit 1.0.0)"
```

The folders `src-greetkit-1.2.0` and `src-greetkit-2.0.0` are the same, with the version number changed in both files. `src-shoutkit/` has the same shape: `src/shoutkit/__init__.py` (shown in section 13.2), and a `pyproject.toml` like greetkit's with `name = "shoutkit"`, `version = "0.3.0"` and one more line at the end of `[project]`: `dependencies = ["greetkit>=1.0,<2"]`.

Build all four into one folder, from an environment that has setuptools:

```text
(buildenv) $ pip wheel --no-index --no-build-isolation --no-deps -q -w wheelhouse ./src-greetkit-1.0.0
(buildenv) $ pip wheel --no-index --no-build-isolation --no-deps -q -w wheelhouse ./src-greetkit-1.2.0
(buildenv) $ pip wheel --no-index --no-build-isolation --no-deps -q -w wheelhouse ./src-greetkit-2.0.0
(buildenv) $ pip wheel --no-index --no-build-isolation --no-deps -q -w wheelhouse ./src-shoutkit
(buildenv) $ ls wheelhouse
greetkit-1.0.0-py3-none-any.whl
greetkit-1.2.0-py3-none-any.whl
greetkit-2.0.0-py3-none-any.whl
shoutkit-0.3.0-py3-none-any.whl
```

(How did the build environment get setuptools without the internet? `python -m venv buildenv`, then `pip install setuptools`, which normally downloads it from PyPI. On the test machine it was installed from a wheel that Ubuntu ships in `/usr/share/python-wheels`, with `pip install --no-index --find-links /usr/share/python-wheels setuptools`. With internet, the plain command is enough.)

### 16.6 Editable installs: `pip install -e .`

During development you change the code all the time. Rebuilding and reinstalling a wheel after every change would be slow. An **editable install** installs the package as a **link to your source folder**: the environment imports your files directly from `src/`, so every change is visible at once.

From the project root, inside the development environment (here it has setuptools, so we can switch off build isolation and work offline):

```text
(.venv) $ pip install --no-index --no-build-isolation -e .
Obtaining file:///home/you/organise-project
Building wheels for collected packages: organise
  Created wheel for organise: filename=organise-0.1.0-0.editable-py3-none-any.whl size=1716 sha256=f39ad6b5c2c55acb1b6832e9b87809eb72799d10f668efb68baf65b386826f7f
  Stored in directory: /tmp/pip-ephem-wheel-cache-wehoeinb/wheels/66/9c/5b/4fc19451581ef49e75e0d84dfb5ec54d38771bd5aa29444f58
Successfully built organise
Installing collected packages: organise
Successfully installed organise-0.1.0
(.venv) $ python -c "import organise; print(organise.__file__)"
/home/you/organise-project/src/organise/__init__.py
```

(Some progress lines were removed; the hashes and temporary folder names are machine-specific. With internet you simply write `pip install -e .`, or `pip install -e ".[dev]"` to get the `dev` extra too.)

`organise.__file__` points into **`src/`**, not into `site-packages`. Now edit the source and run the command again, without reinstalling. Create a test folder with one file, `box/song.mp3`, and try:

```text
(.venv) $ organise box -n
would move song.mp3 -> other/song.mp3
```

Add one line to the `TYPE_FOLDERS` dictionary in `src/organise/rules.py`:

```python
    "music": {".mp3", ".ogg", ".flac"},
```

```text
(.venv) $ organise box -n
would move song.mp3 -> music/song.mp3
(.venv) $ pip list
Package    Version Editable project location
---------- ------- ----------------------------------
organise   0.1.0   /home/you/organise-project
pip        25.1.1
setuptools 78.1.1
```

The change worked immediately. `pip list` shows the **editable project location**.

What still needs a reinstall: changes to `pyproject.toml` itself, for example a new dependency or a new console script. Those are read only at install time.

The normal development setup for any project is therefore:

```text
$ python -m venv .venv
$ source .venv/bin/activate
(.venv) $ pip install -e ".[dev]"
```

and then `pytest`, your editor and your console scripts all use the code in `src/`.

## 17. Project: package the file organiser

### 17.1 The goal

In core.12 you wrote `organise.py`, one file of about 130 lines that sorts the files of a folder into sub-folders by type, date or size. Now we turn it into a **real package**:

- split into modules with clean imports and **no cycles**;
- with a `pyproject.toml`, in the src layout;
- built into a wheel;
- installed into a **fresh** environment, where the command `organise` works from any folder.

This uses every part of the chapter. The code of the functions is the same as in core.12; only the **organisation** changes.

### 17.2 Plan the split

First, decide which function goes where. Group by **job**, and make sure imports only point "down":

| Module | Job | Imports from the package |
|---|---|---|
| `rules.py` | choose a sub-folder for one file (`TYPE_FOLDERS`, `folder_by_*`, `RULES`) | nothing |
| `planner.py` | `unique_target`, `plan_moves`, `carry_out` | `rules` |
| `cli.py` | `argparse` parser and `main` | `rules`, `planner`, the package's `__version__` |
| `__init__.py` | public API and version | `rules`, `planner` |
| `__main__.py` | `python -m organise` | `cli` |

The import graph, with arrows meaning "imports":

```text
__main__.py ──> cli.py ──> planner.py ──> rules.py
                  │                          ▲
                  └──────────────────────────┘
__init__.py ──> planner.py, rules.py
```

`rules.py` imports nothing from the package, so it can never be part of a cycle. `cli.py` is at the top: no other module imports it except `__main__.py` and the console script. There is one subtle import: `cli.py` reads `__version__` from the package (`from . import __version__`). That is safe because `__init__.py` does **not** import `cli`. If it did, the package would be half-initialised while `cli` asks it for `__version__`: a cycle (section 10).

### 17.3 The files

The project tree:

```text
organise-project/
├── pyproject.toml
├── README.md
├── src/
│   └── organise/
│       ├── __init__.py
│       ├── __main__.py
│       ├── cli.py
│       ├── planner.py
│       └── rules.py
└── tests/
    └── test_planner.py
```

`pyproject.toml` is the one from section 15.2. `README.md`:

```text
# organise

Sort the files of a folder into sub-folders by type, date or size.

    organise ~/Downloads --dry-run
```

`src/organise/rules.py`: everything that decides **where** a file goes. Its body is copied **unchanged** from `organise.py` in core.12 (section 18.2 there): from `TYPE_FOLDERS` down to the `RULES` dictionary. Only the top of the file is new:

```python
"""Rules that choose a sub-folder for one file. Nothing here touches the disk."""
from datetime import datetime, timezone

TYPE_FOLDERS = {
    ...                     # unchanged from core.12
}
SMALL = 10 * 1024          # below 10 KB: "small"
LARGE = 1024 * 1024        # 1 MB and more: "large"

# folder_by_type, folder_by_date, folder_by_size: unchanged from core.12

RULES = {"type": folder_by_type, "date": folder_by_date, "size": folder_by_size}
```

`src/organise/planner.py`: the plan and its execution. The three functions `unique_target`, `plan_moves` and `carry_out` are also copied **unchanged** from core.12. The new part is the top: `planner` needs `RULES` from its sibling module, and gets it with a **relative import**:

```python
"""Plan the moves, then carry them out."""
import shutil

from .rules import RULES

# unique_target, plan_moves, carry_out: unchanged from core.12
```

To build the files, open the complete `organise.py` listing in core.12, section 18.2, and copy each function into the module named here. This is exactly the work of splitting a script into a package: the code stays, the **places** change, and each file gets the imports it needs.

`src/organise/cli.py`: the command line. Compared with core.12 it has one new option, `--version`, and **no** `if __name__ == "__main__":` block: the console script and `__main__.py` call `main()` for us.

```python
"""The command line: parse arguments, call the planner, return an exit code."""
import argparse
import sys
from pathlib import Path

from . import __version__
from .planner import carry_out, plan_moves
from .rules import RULES


def existing_folder(text):
    path = Path(text)
    if not path.is_dir():
        raise argparse.ArgumentTypeError(f"{text!r} is not a folder")
    return path


def build_parser():
    parser = argparse.ArgumentParser(
        prog="organise",
        description="Sort the files of a folder into sub-folders.")
    parser.add_argument("source", type=existing_folder,
                        help="folder whose files should be sorted")
    parser.add_argument("--by", choices=sorted(RULES), default="type",
                        help="sort rule (default: %(default)s)")
    parser.add_argument("--dest", type=Path,
                        help="where the sub-folders go (default: inside SOURCE)")
    parser.add_argument("--copy", action="store_true",
                        help="copy the files instead of moving them")
    parser.add_argument("-n", "--dry-run", action="store_true",
                        help="show what would happen, change nothing")
    parser.add_argument("-q", "--quiet", action="store_true",
                        help="print nothing except errors")
    parser.add_argument("--version", action="version",
                        version=f"%(prog)s {__version__}")
    return parser


def main(argv=None):
    args = build_parser().parse_args(argv)
    dest = args.dest if args.dest is not None else args.source
    say = (lambda text: None) if args.quiet else print
    try:
        plan = plan_moves(args.source, dest, args.by)
        if not plan:
            say("nothing to do")
            return 0
        carry_out(plan, args.copy, args.dry_run, say)
    except OSError as e:
        print(f"organise: error: {e}", file=sys.stderr)
        return 1
    return 0
```

(`action="version"` is an `argparse` feature: it prints the given text and exits with code 0.)

`src/organise/__init__.py`: the public API, and the version. The version is written **once**, in `pyproject.toml`. At run time, `importlib.metadata.version("organise")` reads it from the installed package's `METADATA` (section 16.4), so the two can never disagree.

```python
"""organise - sort the files of a folder into sub-folders."""
from importlib.metadata import PackageNotFoundError, version

from .planner import carry_out, plan_moves
from .rules import RULES

__all__ = ["RULES", "carry_out", "plan_moves", "__version__"]

try:
    __version__ = version("organise")
except PackageNotFoundError:      # running from a folder, not installed
    __version__ = "0.0.0"
```

`src/organise/__main__.py`, so that `python -m organise` works too:

```python
"""Run with: python -m organise"""
import sys

from .cli import main

sys.exit(main())
```

`tests/test_planner.py`: it imports from the **package**, exactly as a user would.

```python
import tempfile
from pathlib import Path

from organise import plan_moves


def test_plan_by_type_touches_nothing():
    with tempfile.TemporaryDirectory() as d:
        root = Path(d)
        (root / "a.jpg").write_text("x")
        (root / "b.py").write_text("x")
        plan = plan_moves(root, root, "type")
        assert [t.parent.name for _, t in plan] == ["images", "code"]
        assert not (root / "images").exists(), "plan_moves must not create folders"
```

### 17.4 Build it

Section 16.3 showed the build of exactly this project. The result:

```text
dist/
├── organise-0.1.0-py3-none-any.whl
└── organise-0.1.0.tar.gz
```

The wheel is the file you give to other people (or upload to PyPI). Everything they need is inside it.

### 17.5 Install it into a fresh environment

The real test of a package: does it work **somewhere else**, in an environment that has never seen your source folder? We copy the wheel into another folder, `elsewhere/`, and make a brand-new environment there:

```text
$ cd elsewhere
$ ls
organise-0.1.0-py3-none-any.whl
$ python3 -m venv fresh
$ source fresh/bin/activate
(fresh) $ pip install --no-index organise-0.1.0-py3-none-any.whl
Processing ./organise-0.1.0-py3-none-any.whl
Installing collected packages: organise
Successfully installed organise-0.1.0
(fresh) $ pip list
Package  Version
-------- -------
organise 0.1.0
pip      25.1.1
(fresh) $ which organise
/home/you/elsewhere/fresh/bin/organise
(fresh) $ organise --version
organise 0.1.0
```

(`--no-index` only stops pip from asking PyPI; our package has no dependencies, so nothing else is needed. With the internet you can leave it out.)

`organise` is now a command, like `ls` or `pip`. (`organise --help` prints the same help as in core.12, plus the new `--version` line.) Use it on a practice folder with five small files:

```text
(fresh) $ ls downloads
Holiday.JPG
cv.pdf
prices.csv
run.py
song.mp3
(fresh) $ organise downloads --dry-run
would move Holiday.JPG -> images/Holiday.JPG
would move cv.pdf -> documents/cv.pdf
would move prices.csv -> data/prices.csv
would move run.py -> code/run.py
would move song.mp3 -> other/song.mp3
(fresh) $ organise downloads
moved Holiday.JPG -> images/Holiday.JPG
moved cv.pdf -> documents/cv.pdf
moved prices.csv -> data/prices.csv
moved run.py -> code/run.py
moved song.mp3 -> other/song.mp3
(fresh) $ find downloads -type f | sort
downloads/code/run.py
downloads/data/prices.csv
downloads/documents/cv.pdf
downloads/images/Holiday.JPG
downloads/other/song.mp3
(fresh) $ organise downloads
nothing to do
(fresh) $ python -m organise --version
organise 0.1.0
```

Errors still work as designed in core.12 (exit code 2 for bad usage):

```text
(fresh) $ organise nowhere
usage: organise [-h] [--by {date,size,type}] [--dest DEST] [--copy] [-n] [-q]
                [--version]
                source
organise: error: argument source: 'nowhere' is not a folder
```

### 17.6 What a console script really is

pip created the `organise` command from the line in `[project.scripts]`. It is a tiny Python script:

```text
(fresh) $ cat fresh/bin/organise
#!/bin/sh
'''exec' /home/you/elsewhere/fresh/bin/python3 "$0" "$@"
' '''
# -*- coding: utf-8 -*-
import re
import sys
from organise.cli import main
if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw|\.exe)?$', '', sys.argv[0])
    sys.exit(main())
```

Look at the last lines: `from organise.cli import main`, then `sys.exit(main())`. That is the entry point `organise.cli:main`, plus the `if __name__ == "__main__":` idiom of section 5.

The first three lines are a trick that starts the environment's **own** Python (`fresh/bin/python3`), even if the environment is not activated. pip uses this shell form when the path to Python is very long or contains a space (on the test machine the path was long). With a short path without spaces, the first line is simply `#!/home/you/elsewhere/fresh/bin/python3`. Either way, the script is bound to **this** environment. That is why you can run `fresh/bin/organise` from anywhere, activated or not.

### 17.7 Test it in the development environment

Back in the project, the development setup from section 16.6 (`pip install -e ".[dev]"`) installs the package in editable mode plus `pytest`. Then:

```text
(.venv) $ pytest -q
.                                                                        [100%]
1 passed in 0.00s
```

(The install line needs the internet for `pytest` and was not run here; the `pytest` output is real.) The test says `from organise import plan_moves`: it works only because the package is installed. With the src layout, there is no way to accidentally test a local copy instead.

### 17.8 Your turn

Extend the project, one step at a time, and rebuild and reinstall the wheel after each step:

1. Add a `music` type rule (as in section 16.6). Bump the version to `0.2.0` in `pyproject.toml` only, rebuild, reinstall into `fresh`, and check that `organise --version` says `0.2.0`.
2. Add a second console script, `organise-rules`, that prints each type folder and its suffixes. Where does its function live, and what line do you add to `[project.scripts]`?
3. Move `unique_target` into a new module `naming.py`. Which imports change? Draw the new import graph and check that it has no cycle.
4. Make **plugin** rules (section 11): a sub-package `organise/rules_extra/` whose modules each define `folder(path)`, loaded into `RULES` with `pkgutil.iter_modules` and `importlib.import_module`. Which module should do the loading so that the import graph stays a tree?

## 18. Common traps

The section number tells you where each trap was explained.

1. **Naming your file like a library** (4.4): `random.py`, `json.py`, `test.py`, `requests.py`. Your file shadows the real module. Rename it and delete `__pycache__`.
2. **Code at the top level of a module runs on import** (3.2). Put work into functions, and the script part under `if __name__ == "__main__":` (5.2).
3. **Expecting a second import to run the file again** (3.1, 3.3). It does not; the module is cached in `sys.modules`. Restart the program after editing, and avoid `importlib.reload` (3.7).
4. **`from module import value` for a value that changes** (3.6). You get a copy of the reference at import time. Use `module.value`.
5. **Running a module inside a package by its path** (7.2): "attempted relative import with no known parent package". Use `python -m package.module` from the folder that contains the package.
6. **Script-style imports of siblings inside a package** (7.3): `from prices import x` in `shop/cart.py`. Use `from shop.prices import x` or `from .prices import x`.
7. **`import package` without importing its submodule** (6.3): `AttributeError: module 'shop' has no attribute 'prices'`. Import `shop.prices`, or re-export in `__init__.py`.
8. **Forgetting `__init__.py`** (8.2). The folder may still import as a namespace package, which hides mistakes. Always add it to your own packages.
9. **`from module import *`** (9.2). It brings in unknown names (even the module's own imports, if there is no `__all__`).
10. **Circular imports** (10). Look for "partially initialized module". Move shared code down into a new module; or import inside the function; or import the module and use names at call time only.
11. **`sys.path.append` and `PYTHONPATH` hacks** (4.3). They work on one machine only. Install the package (editable during development).
12. **`pip` and `python` from different environments** (12.5). Use `python -m pip`, and check `which python`.
13. **Installing into the system Python** (12.6), with `sudo pip` or `--break-system-packages`. Always create a virtual environment.
14. **Committing `.venv/`, or not committing the requirements** (12.2, 13.7). Commit `pyproject.toml` and the lock file or `requirements.txt`; ignore `.venv/`, `__pycache__/`, `build/`, `dist/`, `*.egg-info/`.
15. **No versions at all, or exact pins in a library** (13.8). Applications pin (lock files); libraries declare ranges.
16. **Ignoring pip's dependency `ERROR`** (13.4). pip may install anyway and leave a broken environment. Run `pip check`.
17. **Flat layout tests that pass against the local folder** (16.1). Use the src layout and install the package.
18. **Changing `pyproject.toml` and not reinstalling** (16.6). New dependencies and new console scripts appear only after `pip install -e .` again.

## 19. Summary

- A **module** is a `.py` file; its top-level names become attributes of a module object. `import m`, `import m as x`, `from m import name`, `from m import name as y`. Prefer `import m` and use `from` for a few frequent names.
- **`import` step by step**: look in the cache `sys.modules`; if missing, **find** the file along `sys.path`, **create** the module, put it **in the cache before running it**, **execute** the file once, and **bind** the name. Importing runs code, so modules should only define things. `__pycache__` holds compiled bytecode; it is safe to delete and should not be committed. `importlib.reload` re-runs a file but leaves old references behind.
- **`sys.path`** is searched in order and the first match wins. The first entry is the script's folder (or the current folder for `-m`, `-c` and the prompt), then the standard library, then `site-packages`. Your own `random.py` **shadows** the real one.
- **`__name__`** is `"__main__"` for the program you run and the module name otherwise. `if __name__ == "__main__": sys.exit(main())` gives a file both roles. `python -m pkg.mod` runs a module by name, with its package known.
- A **package** is a folder with `__init__.py`. Importing `a.b.c` runs `a/__init__.py`, `a/b/__init__.py` and `a/b/c.py`, once each. Importing a package does not import its submodules. `__main__.py` makes `python -m package` work. Folders **without** `__init__.py` are **namespace packages** that can span several folders; use them only for that purpose.
- **Absolute imports** (`from shop.prices import x`) and **relative imports** (`from .prices import x`, `from ..cart import y`) are both fine inside a package. Relative imports need a known parent package: run with `-m`, never `python shop/cart.py`. Never use bare script-style imports for siblings.
- **Public API**: names without a leading underscore. **`__all__`** lists them and controls `import *`, but hides nothing. Re-export the public names in `__init__.py` so users write `from package import name`, and you can reorganise freely.
- **Circular imports** happen when modules import each other and one asks for a name that the other has not defined yet: "partially initialized module ... most likely due to a circular import". Fix by moving shared code into a lower module (best), importing inside a function, or importing the module and using its names only at call time.
- **`importlib.import_module(name)`** imports a module named by a string; `importlib.util.find_spec` checks without running; `pkgutil.iter_modules` lists modules in a package folder. Together they make a plugin system. Loading plugins runs their code.
- A **virtual environment** (`python -m venv .venv`) is a private `site-packages` linked to a base Python. Activate it (`source .venv/bin/activate`, or `.venv\Scripts\activate` on Windows) or call `.venv/bin/python` directly. One project, one environment; never commit it; never install into the system Python. Use `python -m pip`.
- **pip** installs from PyPI (or a local folder) into the current environment and resolves dependencies. **Specifiers**: `==`, `>=`, `<`, `!=`, `~=`, combined with commas; pip picks the newest match. `pip freeze > requirements.txt` and `pip install -r requirements.txt` reproduce an environment; `pip check` finds conflicts. Libraries declare **ranges**; applications **pin**.
- **Lock files** (`pylock.toml`, `uv.lock`, `poetry.lock`) record exact versions and hashes of the whole dependency tree, for reproducible installs. **uv** (`uv add`, `uv sync`, `uv run`) and **poetry** (`poetry add`, `poetry install`, `poetry run`) manage dependencies, environments and lock files in one tool. Commit the lock file.
- **`pyproject.toml`**: `[build-system]` names the build backend (`setuptools.build_meta`, `hatchling.build`, ...); `[project]` holds the name, version, `requires-python`, `dependencies`; `[project.optional-dependencies]` defines extras such as `dev`; `[project.scripts]` creates console commands (`organise = "organise.cli:main"`); `[tool.*]` holds other tools' settings.
- The **src layout** stops tests from importing the local folder instead of the installed package. `python -m build` creates an **sdist** (`.tar.gz`, the source) and a **wheel** (`.whl`, ready to unzip and install). `pip install -e ".[dev]"` gives an **editable install** for development.

When you can split a script into a package whose imports form a tree, recognise and fix a circular import from its traceback, and build a wheel from `pyproject.toml` that installs into a fresh environment and gives you a working command, you have met the outcomes of this module. The problems that follow practise each part.

### What comes next

In **core.14, Object-oriented programming**, you learn to build your own types with **classes**. You have used objects from other people's modules all along: `Path`, file objects, `csv.DictReader`, and in this chapter the module objects themselves. Next you write your own, and you will place each class in the right module of a package, with exactly the import skills you learned here.
