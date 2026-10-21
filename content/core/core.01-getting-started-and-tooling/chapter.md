# Core 01: Getting started and tooling

This chapter sets up everything you need before you write serious Python.
It covers what Python actually is, how it runs on your Linux machine, how to
move around the terminal, how to keep projects separate with virtual
environments, how to save your work with Git, and how to read the error
messages Python gives you.

None of this is "boring setup". Every professional programmer uses these
tools every single day. If you understand them deeply now, you will waste far
less time later. Many beginners lose hours to problems like "I installed the
package but Python says it is not found". After this chapter, you will know
exactly why that happens and how to fix it.

## How to use this chapter

- Keep a terminal open while you read. Type every command yourself. Do not copy
  and paste. Typing builds memory in your fingers.
- When you see a **Predict the output** box, stop. Decide your answer first.
  Only then open the hidden answer.
- The "Under the hood" sections go deeper. Read them slowly. They explain *why*
  things behave the way they do, which is what lets you solve new problems
  without help.
- Lines that start with `$` are typed in the terminal (bash). Do not type the
  `$` itself. Lines that start with `>>>` are typed in the Python REPL. Lines
  with no prefix are output.

---

## 1. What Python is

### The plain explanation

Python is a **programming language**. A language is a set of rules: which words
are allowed, how you combine them, and what each combination means. For
example, the rules say that `print("hi")` means "show the text hi on the
screen".

A language on its own does nothing. You need a program that reads your Python
text and carries it out. That program is called an **interpreter**. When people
say "install Python", they really mean "install a Python interpreter".

There is more than one interpreter for the Python language:

| Interpreter | Written in | Notes |
|---|---|---|
| **CPython** | C | The official, standard one. What you get from python.org and from Linux packages. Almost everyone uses it. |
| **PyPy** | RPython (a restricted Python) | Often much faster for long-running pure-Python programs, because it has a JIT compiler. |
| **MicroPython** | C | A tiny Python for microcontrollers such as the ESP32 or Raspberry Pi Pico. |
| **Jython**, **IronPython** | Java, C# | Run Python on the Java or .NET platforms. Less active today. |

When this course says "Python", it means CPython unless stated otherwise.

### Python versions

Python has two big eras. **Python 2** ended in January 2020. Do not use it and
ignore any tutorial written for it (a clue: `print "hello"` without
brackets). **Python 3** is the only current Python.

A version number like `3.14.4` has three parts:

- `3` is the **major** version. It changes only for huge breaking changes.
- `14` is the **minor** version. A new minor version comes out every year,
  around October. It adds new features.
- `4` is the **micro** (or patch) version. It contains only bug fixes and
  security fixes.

Each minor version is supported for about five years. Code written for 3.10
almost always runs on 3.14. Code written for 3.14 may use features that 3.10
does not have.

Check your version in the terminal:

```bash
$ python3 --version
Python 3.14.4
```

Your number may differ. That is fine for this course as long as it is 3.10 or
newer.

### Under the hood: how CPython runs your code

CPython does not run your text directly. It works in two stages.

1. **Compile.** CPython reads your source code and checks it against the
   grammar. If you broke a grammar rule, you get a `SyntaxError` *before any
   line runs*. If the grammar is fine, CPython translates the code into
   **bytecode**: a list of simple instructions for an imaginary machine.
2. **Execute.** A loop inside CPython (the "evaluation loop" or "virtual
   machine") reads the bytecode instructions one at a time and performs them.

You can look at bytecode with the `dis` module (short for "disassemble"):

```python
>>> import dis
>>> dis.dis("x = 2 + 3\nprint(x)")
  0           RESUME                   0

  1           LOAD_SMALL_INT           5
              STORE_NAME               0 (x)

  2           LOAD_NAME                1 (print)
              PUSH_NULL
              LOAD_NAME                0 (x)
              CALL                     1
              POP_TOP
              LOAD_CONST               1 (None)
              RETURN_VALUE
```

The exact instruction names change between versions, so yours may look
different. Notice two things:

- `2 + 3` became the single constant `5`. The compiler worked it out in
  advance. This is called **constant folding**.
- `print` is looked up by name (`LOAD_NAME`) at run time. This is why a typo
  like `pirnt` is only noticed when that line actually runs.

When you **import** a module, CPython saves its bytecode in a folder named
`__pycache__`, in files ending with `.pyc`. Next time, if the source has not
changed, it skips the compile step. You can safely delete `__pycache__`; Python
recreates it. You never need to commit it to Git.

This two-stage design is why Python is called an "interpreted" language even
though there *is* a compile step. The compile step produces bytecode, not
machine code, and the interpreter still has to execute that bytecode
instruction by instruction. PyPy goes further: while your program runs, its
JIT ("just in time") compiler notices code that runs often and turns it into
real machine code.

> **Predict the output.** This file has a typo on line 3. What appears when you
> run it?
>
> ```python
> print("one")
> print("two")
> print("three"
> ```

<details><summary>Answer</summary>

Nothing from `print` appears. Only a `SyntaxError` is shown. The whole file is
compiled before anything runs, and the compile step fails because the bracket on
line 3 is never closed. So "one" and "two" are never printed.

</details>

> **Predict the output.** And this one?
>
> ```python
> print("one")
> pirnt("two")
> print("three")
> ```

<details><summary>Answer</summary>

`one` is printed, then a `NameError` traceback appears. The grammar is fine (a
name followed by brackets is a valid call), so compiling succeeds. Line 2 fails
only when it runs, because there is no name `pirnt`. Line 3 never runs.

</details>

### Common misconceptions

- **"Python is slow, so it is a toy."** Python trades raw speed for fast
  development. Heavy work (NumPy, databases, machine learning) runs in C code
  that Python calls. Many very large companies run Python in production.
- **"The interpreter reads the file line by line."** It compiles the whole file
  first. Syntax errors anywhere stop everything.
- **"python and python3 are the same command."** On many Linux systems `python`
  does not exist at all, or (on older systems) points to Python 2. Always type
  `python3` outside a virtual environment.

---

## 2. Terminal basics

You will run Python from a terminal, so you must be comfortable there. The
program that reads your commands is called a **shell**. On most Linux systems
it is **bash**.

### Paths

Every file lives in a tree of folders (also called directories). The top of the
tree is `/`, called the **root**.

- An **absolute path** starts at the root: `/home/asha/projects/notes.txt`.
- A **relative path** starts from where you are now: `projects/notes.txt`.
- `.` means "the current folder".
- `..` means "the parent folder" (one level up).
- `~` means "my home folder", for example `/home/asha`.

### The core commands

| Command | Meaning | Example |
|---|---|---|
| `pwd` | print working directory: where am I? | `pwd` |
| `ls` | list files here | `ls`, `ls -l` (long form), `ls -a` (show hidden) |
| `cd` | change directory | `cd projects`, `cd ..`, `cd ~`, `cd` (alone goes home) |
| `mkdir` | make a directory | `mkdir notes`, `mkdir -p a/b/c` (creates parents too) |
| `touch` | create an empty file | `touch hello.py` |
| `cat` | print a file's contents | `cat hello.py` |
| `echo` | print text | `echo hello` |
| `cp`, `mv`, `rm` | copy, move or rename, remove | `cp a.txt b.txt`, `mv old.py new.py`, `rm junk.txt` |
| `head`, `tail` | first or last lines of a file | `head -n 5 data.txt` |
| `grep` | find lines that contain text | `grep error log.txt` |
| `wc` | count lines, words, characters | `wc -l data.txt` |
| `which` | which program will run for a command? | `which python3` |

A short session (assume your home folder is `/home/asha`):

```bash
$ cd ~
$ pwd
/home/asha
$ mkdir -p code/day1
$ cd code/day1
$ pwd
/home/asha/code/day1
$ echo "print('hello')" > hello.py
$ cat hello.py
print('hello')
$ python3 hello.py
hello
$ cd ../..
$ pwd
/home/asha
```

Files whose names start with a dot, like `.gitignore` or `.venv`, are
**hidden**. Plain `ls` does not show them. Use `ls -a`.

**Be careful with `rm`.** There is no recycle bin. `rm -r folder` deletes a
folder and everything inside it, permanently.

### Redirection and pipes

By default a program's output goes to the screen. You can send it elsewhere.

- `>` writes output to a file, **replacing** what was there.
- `>>` **appends** output to the end of a file.
- `|` (a **pipe**) sends one program's output into another program's input.

```bash
$ echo "apple" > fruits.txt
$ echo "banana" >> fruits.txt
$ echo "cherry" >> fruits.txt
$ cat fruits.txt
apple
banana
cherry
$ cat fruits.txt | wc -l
3
$ grep an fruits.txt
banana
$ sort -r fruits.txt | head -n 1
cherry
```

Pipes let small tools combine into powerful ones. Your Python scripts can join
in too: a script that reads with `input()` can receive piped text.

```bash
$ echo "Asha" | python3 greet.py
```

Here `greet.py` reads `Asha` from `input()` as if you had typed it.

### Environment variables

The shell keeps a set of named text values called **environment variables**.
Programs can read them. Some are always there:

```bash
$ echo $HOME
/home/asha
$ echo $USER
asha
$ echo $PATH
/home/asha/.local/bin:/usr/local/bin:/usr/bin:/bin
```

`$NAME` means "the value of the variable NAME". To create your own:

```bash
$ GREETING=hello          # a shell variable (no spaces around =)
$ export GREETING         # now it is an environment variable
$ export LEVEL=beginner   # create and export in one step
```

Python reads environment variables through the `os` module:

```python
import os
print(os.environ.get("HOME"))
print(os.environ.get("NOT_SET", "default value"))
```

`os.environ.get(name, default)` returns the value, or the default when the
variable does not exist. Without a default it returns `None`.

You can also set a variable for **one command only** by writing it in front:

```bash
$ LEVEL=expert python3 show_level.py
```

### Under the hood: processes, PATH and exit codes

When you type `python3 hello.py`, bash does this:

1. It splits the line into words: `python3` and `hello.py`.
2. It looks for a program called `python3`. It does not search the whole disk.
   It checks each folder listed in `PATH`, **in order**, and uses the first
   match. `which python3` shows you which one it found.
3. It starts the program as a new **child process**, passing `hello.py` as an
   argument.
4. The child receives a **copy** of the exported environment variables. A
   plain (unexported) shell variable is *not* copied. A child can never change
   its parent's variables.
5. When the child finishes, it returns a number called the **exit status**.
   `0` means success. Anything else means failure. Bash stores it in `$?`.

```bash
$ COLOR=blue
$ python3 -c 'import os; print(os.environ.get("COLOR"))'
None
$ export COLOR
$ python3 -c 'import os; print(os.environ.get("COLOR"))'
blue
$ python3 -c 'print(1/0)'
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    print(1/0)
          ~^~
ZeroDivisionError: division by zero
$ echo $?
1
```

Python exits with status `1` when an uncaught error happens. Testing tools,
including the checker in this course, rely on that.

The `PATH` rule explains many "wrong Python" problems. If two folders in
`PATH` both contain a `python3`, the earlier one wins. Activating a virtual
environment (section 6) works by putting its folder at the **front** of `PATH`.

> **Predict the output.**
>
> ```bash
> $ cd /home/asha
> $ mkdir -p work/a
> $ cd work/a
> $ cd ../..
> $ pwd
> ```

<details><summary>Answer</summary>

`/home/asha`. From `/home/asha/work/a`, the first `..` goes to `/home/asha/work`
and the second to `/home/asha`.

</details>

> **Predict the output.** What does `echo hello | wc -c` print?

<details><summary>Answer</summary>

`6`. `echo` adds a newline after `hello`, so there are 5 letters plus 1 newline
character.

</details>

### Common misconceptions and edge cases

- **Spaces in names.** `cd learning module` fails, because bash sees two
  separate words. Use quotes: `cd "learning module"`. Better: avoid spaces in
  folder names for code.
- **`GREETING = hello` with spaces** does not set a variable. Bash tries to run
  a program named `GREETING`. No spaces around `=` in bash.
- **Case matters.** `Notes.txt` and `notes.txt` are different files on Linux.
- **`>` destroys.** `sort data.txt > data.txt` empties the file before `sort`
  even reads it.

---

## 3. Installing and managing Python versions on Linux

### The plain explanation

Most Linux distributions already include Python 3, because system tools are
written in it. Check:

```bash
$ which python3
/usr/bin/python3
$ python3 --version
Python 3.12.3
```

On Ubuntu or Debian you usually also want the `venv` and `pip` pieces:

```bash
$ sudo apt update
$ sudo apt install python3 python3-venv python3-pip
```

**Never uninstall or replace the system Python.** Parts of your operating
system depend on it. Removing it can break your desktop or package manager.
Install *additional* Pythons beside it instead.

### Version managers: pyenv and uv

Sometimes you need a newer Python than your distribution provides, or several
versions side by side (for example, to test that your code works on 3.11 and
3.14). Two popular tools do this without touching the system Python:

- **pyenv** downloads Python source code and builds each version in your home
  folder (under `~/.pyenv`). You then pick a version per project with
  `pyenv local 3.13.1` or globally with `pyenv global 3.13.1`. It works by
  putting small "shim" programs early in `PATH` that forward to the version you
  chose.
- **uv** is a newer, very fast tool written in Rust. It downloads ready-built
  Pythons (`uv python install 3.14`), creates virtual environments
  (`uv venv`), and installs packages (`uv pip install requests`, or a full
  project workflow with `uv add` and `uv run`).

You do not need either for this course. Knowing they exist is enough for now.
If you later see an error saying your Python is too old, a version manager is
the clean fix.

### Under the hood

A "Python installation" is just a folder containing the interpreter program
and its standard library. For example `/usr/bin/python3` is often a
**symbolic link** (a shortcut) to `python3.12`:

```bash
$ ls -l /usr/bin/python3
lrwxrwxrwx 1 root root 10 Apr  1 10:00 /usr/bin/python3 -> python3.12
```

Several installations can live side by side because each has its own folder.
Which one runs when you type `python3` is decided purely by `PATH`. That is the
whole trick behind pyenv shims and virtual environments.

From inside Python you can ask which interpreter is running and which version
it is:

```python
>>> import sys
>>> sys.executable
'/usr/bin/python3'
>>> sys.version_info
sys.version_info(major=3, minor=14, micro=4, releaselevel='final', serial=0)
>>> sys.version_info.major
3
>>> import platform
>>> platform.python_version()
'3.14.4'
>>> platform.python_implementation()
'CPython'
>>> platform.system()
'Linux'
```

---

## 4. The REPL, running scripts and the shebang line

### The REPL

Type `python3` alone and press Enter. You get the **REPL**:

```bash
$ python3
Python 3.14.4 (main, ...) [GCC ...] on linux
Type "help", "copyright", "credits" or "license" for more information.
>>>
```

REPL stands for **Read, Evaluate, Print, Loop**. It reads one statement,
evaluates it, prints the result, and waits for the next. It is perfect for
small experiments.

```python
>>> 2 + 3
5
>>> "py" + "thon"
'python'
>>> name = "Asha"
>>> name
'Asha'
>>> print(name)
Asha
>>> _
'Asha'
```

Things to know:

- If you type an **expression** (something with a value), the REPL shows its
  value automatically.
- An **assignment** like `name = "Asha"` has no value to show, so nothing is
  printed.
- `_` holds the last value the REPL showed.
- For statements that span several lines, the prompt changes to `...`. Press
  Enter on an empty line to finish.
- Leave with `exit()`, `quit()`, or **Ctrl+D**. In 3.13 and later, plain
  `exit` also works.
- Use the up arrow to recall earlier lines.

Notice that `name` showed `'Asha'` *with quotes*, but `print(name)` showed
`Asha` *without* quotes. The REPL shows the **representation** of a value (the
form you would type in code). `print` shows the human-friendly text. You will
study this difference (`repr` versus `str`) in later modules.

### Running scripts

A **script** is a text file of Python code, usually ending in `.py`. Run it by
giving its path to the interpreter:

```bash
$ cat greet.py
name = "Asha"
print("Hello,", name)
$ python3 greet.py
Hello, Asha
```

Important difference: **a script does not echo values**. A line containing just
`2 + 3` in a script computes 5 and throws it away. Only `print` shows output.

Other useful ways to run Python:

```bash
$ python3 -c 'print(6 * 7)'      # run a one-line program
42
$ python3 -i greet.py            # run the script, then stay in the REPL
Hello, Asha
>>> name
'Asha'
$ python3 -m venv .venv          # run a module from the standard library as a program
```

`-i` is handy for exploring: all the script's variables are still there.

### print() and input() basics

`print` takes any number of values. It converts each to text, puts a separator
between them, and an ending after the last one.

- `sep` is the separator. The default is one space.
- `end` is what comes after. The default is a newline (`"\n"`), which is why
  each `print` normally starts a new line.

```python
print("a", "b", "c")             # a b c
print("a", "b", "c", sep="")     # abc
print("a", "b", "c", sep="-")    # a-b-c
print(1, 2, 3, sep=", ", end="!\n")   # 1, 2, 3!
print("Loading", end="")
print("...done")                 # Loading...done
print()                          # an empty line
```

You can join pieces of text with `+`, and repeat text with `*`:

```python
print("=" * 10)              # ==========
print("Hello, " + "Asha")    # Hello, Asha
```

`+` only joins text to text. `"Age: " + 20` is an error (you will see it in
section 8). Either let `print` do the joining, `print("Age:", 20)`, or convert
the number first with `str(20)`.

`input()` waits for the user to type a line and returns it **as text**, without
the final newline:

```python
name = input()
print("Hello, " + name + "!")
```

In this course, always call `input()` **without** a prompt message. The
checker feeds input automatically and compares your printed lines exactly, so a
prompt like `input("Name: ")` would appear as an extra piece of output.

`len(text)` gives the number of characters in a piece of text. `str(x)` turns a
value into text. These two, plus `print`, `input`, `type`, `help` and `dir`,
are all the built-in functions you need in this module.

You will also see **f-strings** in other people's code, like
`f"Hello, {name}!"`. The `f` before the quote makes Python replace `{name}`
with the value of `name`. Module core.03 covers them in depth. You may use them
already if you like.

### The shebang line

On Linux, you can make a script run like a normal command, without typing
`python3` in front. Two steps.

**Step 1.** Make the very first line of the file a **shebang**:

```python
#!/usr/bin/env python3
print("I run by myself!")
```

**Step 2.** Give the file permission to execute, then run it with a path:

```bash
$ chmod +x hello.py
$ ./hello.py
I run by myself!
```

### Under the hood: what the shebang does

When you run `./hello.py`, the Linux kernel opens the file and looks at its
first two bytes. If they are `#!`, the kernel reads the rest of that line as
the program to use, and runs that program with your file's path as an
argument. So `./hello.py` becomes `/usr/bin/env python3 ./hello.py`.

`/usr/bin/env` is a tiny program that searches `PATH` for `python3` and runs
it. Why not write `#!/usr/bin/python3` directly? Because then the script would
always use the system Python, even inside an activated virtual environment.
`env` respects `PATH`, so it picks the venv's Python when one is active.

For Python itself, the shebang line starts with `#`, so it is just a comment.
That is why the same file still works with `python3 hello.py`.

Why `./hello.py` and not just `hello.py`? Bash only searches the folders in
`PATH` for commands, and the current folder is (deliberately) not in `PATH`.
`./` gives an explicit path.

`chmod +x` sets the "execute" permission bit. Look at it with `ls -l`:

```bash
$ ls -l hello.py
-rw-r--r-- 1 asha asha 50 Oct 18 10:00 hello.py
$ chmod +x hello.py
$ ls -l hello.py
-rwxr-xr-x 1 asha asha 50 Oct 18 10:00 hello.py
```

The `x` letters mean "executable".

### `__name__` and `__file__`

Every running file has a few special names that Python creates for you.

- `__name__` is `"__main__"` for the file you ran directly. (When a file is
  *imported* by another, its `__name__` is its module name instead. You will
  use this in the modules on functions and modules.)
- `__file__` is the path of the current file.

```python
import os
print(__name__)                     # __main__
print(os.path.basename(__file__))   # e.g. greet.py
```

> **Predict the output.** A script `calc.py` contains these two lines. What does
> `python3 calc.py` print?
>
> ```python
> 10 * 3
> print(10 * 3)
> ```

<details><summary>Answer</summary>

Only `30`, once. The first line computes 30 but a script never echoes values.
In the REPL, both lines would show 30.

</details>

> **Predict the output.**
>
> ```python
> print("x", "y", sep="")
> print("a", end=" ")
> print("b")
> ```

<details><summary>Answer</summary>

```
xy
a b
```

</details>

### Common misconceptions and edge cases

- **Typing `python3 hello.py` inside the REPL.** That is a terminal command.
  Inside `>>>` it is a `SyntaxError`. Leave the REPL first.
- **Windows line endings.** A shebang line ending with an invisible `\r` (from
  a file saved on Windows) fails with "No such file or directory". VS Code
  shows "CRLF" or "LF" at the bottom right; choose LF.
- **The shebang must be the very first line.** Not the second, and with no
  blank line before it.
- **Permission denied** when running `./script.py` means you forgot
  `chmod +x`.

---

## 5. VS Code setup

VS Code is a free editor. With the right extensions it understands Python
deeply: it highlights mistakes as you type, runs your code, and lets you step
through it line by line.

### Setting it up

1. Install VS Code (from your distribution's software store, or as a `.deb`
   package from the official site).
2. Open the Extensions panel (**Ctrl+Shift+X**). Install **Python** (by
   Microsoft). It brings **Pylance** (code understanding and type checking) and
   the **Python Debugger**.
3. Optionally install **Ruff** (by Astral). Ruff is a fast **linter** (it
   reports style problems and likely bugs) and **formatter** (it rewrites your
   layout to follow PEP 8).
4. Open your project folder with **File > Open Folder**, or from the terminal:

   ```bash
   $ cd ~/code/day1
   $ code .
   ```

### Selecting the interpreter

This is the most important setting. Press **Ctrl+Shift+P** to open the
Command Palette, type **Python: Select Interpreter**, and choose the Python you
want. Inside a project with a virtual environment, choose the one in `.venv`.
The chosen interpreter appears in the bottom status bar.

If VS Code uses a different Python from your terminal, you get confusing
results like "module not found" in the editor while the terminal works fine.
The selected interpreter is the first thing to check.

### The integrated terminal

**Ctrl+`** (the key above Tab) opens a terminal inside VS Code. It is a normal
bash terminal. When an interpreter from a `.venv` is selected, VS Code usually
activates that environment automatically in new terminals.

### The debugger

A **debugger** pauses your program so you can look inside it.

1. Click in the margin left of a line number. A red dot appears. This is a
   **breakpoint**.
2. Press **F5** and choose **Python Debugger: Current File**.
3. The program runs and stops *before* executing the breakpoint line.
4. The **Variables** panel shows every variable and its current value.
5. Press **F10** (Step Over) to run one line and stop again. **F11** (Step
   Into) goes inside a function call. **F5** continues to the next breakpoint.
   **Shift+F5** stops.

Stepping through a short script and watching the variables change is one of
the best ways to understand what code really does.

### Under the hood

VS Code itself does not run Python. It starts the interpreter you selected, as
a separate process, exactly as the terminal would. The debugger works through a
helper library called **debugpy**, which runs inside that process and talks to
the editor. Linting works by running a linter program (Ruff, Pylance) over your
file and drawing squiggly lines where it reports problems. A squiggle is
advice. Your code may still run, and code without squiggles may still be wrong.

Settings are stored as JSON. Workspace settings live in `.vscode/settings.json`
inside the project, for example:

```json
{
    "editor.rulers": [79],
    "files.eol": "\n",
    "[python]": {
        "editor.defaultFormatter": "charliermarsh.ruff",
        "editor.formatOnSave": true
    }
}
```

---

## 6. Virtual environments and pip

### The problem they solve

**pip** is Python's package installer. It downloads packages (libraries other
people wrote) from the Python Package Index, **PyPI**, and installs them.

Suppose project A needs version 1 of a library, and project B needs version 2.
If both install into the same place, one of them breaks. Also, on modern Linux
systems, installing into the system Python with pip is blocked to protect the
operating system:

```bash
$ pip install requests
error: externally-managed-environment
...
```

The answer is a **virtual environment** (a "venv"): a private, self-contained
folder of packages for one project.

### The everyday workflow

```bash
$ cd ~/code/weather
$ python3 -m venv .venv             # 1. create it (once per project)
$ source .venv/bin/activate         # 2. activate it (once per terminal)
(.venv) $ which python
/home/asha/code/weather/.venv/bin/python
(.venv) $ python -m pip install requests      # 3. install packages
(.venv) $ python -m pip list                   # see what is installed
(.venv) $ python -m pip freeze > requirements.txt   # record exact versions
(.venv) $ python weather.py                    # 4. run your code
(.venv) $ deactivate                           # 5. leave (optional)
$
```

Notes:

- `.venv` is just the conventional folder name. The dot hides it from plain
  `ls`.
- After activation, the prompt shows `(.venv)` and `python` and `pip` refer to
  the venv's copies. Plain `python` (without the 3) is fine inside a venv.
- `python -m pip` is safer than `pip` alone, because it guarantees that pip
  installs into the same Python that `python` runs.
- `requirements.txt` lists packages with exact versions, like
  `requests==2.32.3`. Someone else rebuilds the same environment with
  `python -m pip install -r requirements.txt`.
- **Never commit `.venv` to Git.** It is large and machine-specific. Commit
  `requirements.txt` instead, and add `.venv/` to `.gitignore`.
- A broken venv is cheap. Delete it (`rm -rf .venv`) and create it again.
- Do not move or rename a venv folder. Paths to it are written inside its
  files. Recreate it instead.

With **uv** the same steps are `uv venv` and `uv pip install requests`, and
they run much faster.

### Under the hood: what a venv really is

Look inside:

```bash
$ ls .venv
bin  include  lib  lib64  pyvenv.cfg
$ cat .venv/pyvenv.cfg
home = /usr/bin
include-system-site-packages = false
version = 3.14.4
$ ls -l .venv/bin/python
lrwxrwxrwx 1 asha asha 16 Oct 18 10:00 .venv/bin/python -> /usr/bin/python3
```

- `bin/python` is a **link to the real interpreter**. A venv does not copy
  Python. It reuses the base installation.
- `pyvenv.cfg` is the key file. When Python starts, it looks for this file next
  to (or one level above) its own program. If it finds it, Python knows it is
  running "inside" a venv. It then uses the venv's own
  `lib/python3.X/site-packages` folder for third-party packages, instead of the
  system one.
- `site-packages` is where pip puts installed packages.

And `activate`? It is a small bash script that does just two things: it adds
`.venv/bin` to the **front** of `PATH`, and it changes your prompt. That is
all. Therefore **activation is optional**. Running the venv's Python by its
path works exactly the same:

```bash
$ .venv/bin/python weather.py
```

You can check from inside Python whether you are in a venv. `sys.prefix` is
the environment in use. `sys.base_prefix` is the base installation it was built
from. They differ only inside a venv:

```python
>>> import sys
>>> sys.prefix
'/home/asha/code/weather/.venv'
>>> sys.base_prefix
'/usr'
>>> sys.prefix != sys.base_prefix
True
```

`!=` means "is not equal to". It gives `True` or `False`. Module core.02
covers comparisons fully.

> **Predict the output.** You created and activated a venv in one terminal.
> Then you open a *second* terminal window, go to the same folder, and type
> `which python3`. What do you see?

<details><summary>Answer</summary>

`/usr/bin/python3` (the system one). Activation only changed `PATH` in the
*first* shell process. Each new terminal is a new shell with a fresh `PATH`. You
must activate again in each terminal.

</details>

### Common misconceptions

- **"I installed it, but Python cannot find it."** You installed into one
  Python and ran another. Compare `which python` with `python -m pip --version`
  (pip prints the path it installs to). Use `python -m pip` to avoid this.
- **"`sudo pip install` fixes permission errors."** It installs into the
  system Python and can break your OS tools. Use a venv.
- **"The venv contains its own copy of Python."** It links to the base Python.
  If you delete or upgrade the base Python, venvs built from it may break.

---

## 7. Git basics

### Why Git

**Git** is a **version control system**. It records snapshots of your project
over time. With it you can:

- see exactly what changed and when,
- go back to any earlier version,
- try an idea on a separate **branch** without risking working code,
- share code with others (through services like GitHub, later).

Even working alone and offline, Git is your safety net and your diary.

### One-time setup

Tell Git who you are. This is written into every commit you make.

```bash
$ git config --global user.name "Asha Rao"
$ git config --global user.email "asha@example.com"
$ git config --global init.defaultBranch main
```

### The three areas

Git thinks of three places:

1. The **working directory**: your files as you see and edit them.
2. The **staging area** (also called the **index**): changes you have marked to
   go into the next snapshot.
3. The **repository**: the saved snapshots, called **commits**. It lives in a
   hidden `.git` folder.

`git add` moves changes from 1 to 2. `git commit` saves 2 into 3.

### A full session

```bash
$ mkdir diary && cd diary
$ git init
Initialized empty Git repository in /home/asha/diary/.git/
$ echo "Day 1" > notes.txt
$ git status --short
?? notes.txt
$ git add notes.txt
$ git status --short
A  notes.txt
$ git commit -m "Start diary"
[main (root-commit) 3f2a9c1] Start diary
 1 file changed, 1 insertion(+)
 create mode 100644 notes.txt
$ git status
On branch main
nothing to commit, working tree clean
```

Commit hashes like `3f2a9c1` will differ on your machine.

`git status --short` uses two columns of letters before each file name. The
**left** column describes the staging area. The **right** column describes the
working directory.

| Short status | Meaning |
|---|---|
| `?? file` | untracked: Git has never been told about this file |
| `A  file` | added: a new file is staged |
| ` M file` (space, then M) | modified in the working directory, not staged |
| `M  file` (M, then space) | modified and staged |
| `MM file` | staged, then modified again after staging |
| nothing | clean: everything is committed |

Continue the session:

```bash
$ echo "Day 2" >> notes.txt
$ git status --short
 M notes.txt
$ git diff
diff --git a/notes.txt b/notes.txt
index 2ba1e4f..a8b3c79 100644
--- a/notes.txt
+++ b/notes.txt
@@ -1 +1,2 @@
 Day 1
+Day 2
$ git add notes.txt
$ git diff
$ git diff --staged
(shows the same change as before)
$ git commit -m "Add day 2"
$ git log --oneline
b71c0d2 Add day 2
3f2a9c1 Start diary
```

- `git diff` shows changes **not yet staged**. Lines starting with `+` were
  added, `-` removed.
- `git diff --staged` shows changes that **are staged** and will go into the
  next commit.
- `git log` lists commits, newest first. `--oneline` makes it compact.
  `git log --format=%s` shows only the messages.
- `git add .` stages every change in the current folder. Use it with care, and
  check `git status` first.

### Branches

A branch is a separate line of work.

```bash
$ git branch feature            # create a branch (you stay where you are)
$ git branch                    # list branches; * marks the current one
  feature
* main
$ git switch feature            # move to it
$ echo "experiment" > idea.txt
$ git add idea.txt
$ git commit -m "Try an idea"
$ git switch main               # idea.txt disappears from the folder
$ ls
notes.txt
$ git switch feature            # and comes back
$ ls
idea.txt  notes.txt
```

`git switch -c name` creates a branch and moves to it in one step. Older
tutorials use `git checkout` for the same jobs; `switch` is clearer.

### .gitignore

A file named `.gitignore` lists files Git should never track:

```
.venv/
__pycache__/
*.pyc
```

### Under the hood

- Every commit stores a **full snapshot** of the staged files (Git saves space
  by reusing identical file contents), plus the author, date, message and the
  commit before it (its **parent**). Commits therefore form a chain.
- A commit's name is a **hash**: a 40-character fingerprint computed from its
  contents. Change anything and the hash changes. That makes history
  tamper-evident. Short forms like `3f2a9c1` are just the first characters.
- A **branch** is only a small file holding the hash of one commit. Creating a
  branch is instant and costs almost nothing.
- **HEAD** means "where you are now". Usually it points to a branch, and the
  branch points to a commit. When you commit, the current branch moves forward
  to the new commit.
- `git switch` rewrites the files in your working directory to match the
  snapshot of the branch you switch to. That is why `idea.txt` vanished and
  reappeared.

> **Predict the output.** A new file `a.py` is created, added, and committed.
> Then you edit `a.py` and run `git add a.py`. Then you edit it once more. What
> does `git status --short` show?

<details><summary>Answer</summary>

`MM a.py`. The left `M` is the staged edit. The right `M` is the newer edit that
is not staged yet. The staging area holds the file *as it was when you ran
`git add`*, not a live link to it.

</details>

### Common misconceptions

- **"`git add` saves my work."** It only stages it. Nothing is in history until
  you commit.
- **"Git tracks folders."** It tracks files. An empty folder does not appear
  in Git.
- **Committing secrets.** Passwords and API keys in commits stay in history
  even if you delete them later. Keep them out from the start, for example in
  environment variables.
- **Vague messages** like "update" or "fix" make history useless. Write what
  and why: "Add input validation for age".

---

## 8. Reading a traceback

### The plain explanation

When Python hits an error it cannot handle, it stops and prints a
**traceback**. Beginners often panic and skim it. Do the opposite: a traceback
is Python telling you exactly what went wrong and where.

```python
# report.py
name = "Riya"
marks = 87
print("Student:", name)
message = "Marks: " + marks
print(message)
```

```bash
$ python3 report.py
Student: Riya
Traceback (most recent call last):
  File "/home/asha/report.py", line 5, in <module>
    message = "Marks: " + marks
              ~~~~~~~~~~^~~~~~~
TypeError: can only concatenate str (not "int") to str
```

### Read it from the bottom up

1. **Last line: the error type and message.** `TypeError` is the kind of error.
   The message says you tried to join (`concatenate`) text (`str`) with a whole
   number (`int`).
2. **The `File ... line ...` line: where.** The file is `report.py`, the line
   is **5**. `in <module>` means "at the top level of the file", not inside a
   function.
3. **The code line** is shown so you do not need to open the file.
4. **The carets** `~~~^~~~` (Python 3.11 and newer) point at the exact part of
   the line that failed. Here, the `+`.
5. **Output before the traceback** shows how far the program got. `Student:
   Riya` printed, so lines 1 to 4 ran fine.

"Most recent call last" matters when functions call other functions. Then
there is one `File` entry per call, oldest at the top, and the **last** entry
is where the error actually happened. In this module everything is at the top
level, so you will see just one entry.

The fix here: `message = "Marks: " + str(marks)`, or simply
`print("Marks:", marks)`.

### Error types you will meet first

| Error | Meaning | Typical cause |
|---|---|---|
| `SyntaxError` | The code breaks the grammar. Nothing runs. | Missing bracket or quote, missing colon |
| `IndentationError` | Wrong spaces at the start of a line. | A stray space before a statement |
| `NameError` | A name is used that does not exist. | Typo, wrong case (`Print`), using before assigning |
| `TypeError` | An operation got the wrong kind of value. | `"a" + 1`, calling something that is not a function |
| `ValueError` | Right type, unacceptable value. | `int("abc")` |
| `ZeroDivisionError` | Division by zero. | `10 / 0` |
| `ModuleNotFoundError` | `import` cannot find the module. | Typo, or the package is in a different venv |
| `AttributeError` | The object has no such attribute. | `sys.verison` |

### SyntaxError looks different

A syntax error is found while **compiling**, before anything runs. So there is
no "Traceback (most recent call last)" header, and nothing is printed first:

```bash
$ cat broken.py
print("hi"
print("bye")
$ python3 broken.py
  File "/home/asha/broken.py", line 1
    print("hi"
         ^
SyntaxError: '(' was never closed
```

Warning: for syntax errors, the line Python reports is where it **noticed**
the problem, which can be *after* the real mistake. An unclosed bracket on line
1 is sometimes reported on line 2 or later, because Python keeps reading,
hoping the bracket will close. If the reported line looks fine, look at the
line **above** it.

Python 3.10 and newer give much friendlier messages, and even suggestions:

```bash
$ python3 -c 'pirnt("hi")'
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    pirnt("hi")
    ^^^^^
NameError: name 'pirnt' is not defined. Did you mean: 'print'?
```

`<string>` appears as the file name because the code came from `-c`, not from
a file.

### A method for any error

1. Read the **last line**. Name the error type. Read the message word by word.
2. Find the **line number** in the last `File` entry. Open that line.
3. Ask: which value on this line is not what I expected? Print it, or use the
   debugger, to check.
4. For a `SyntaxError` that looks fine, check the line above.
5. Fix **one** error and run again. Later errors are often hidden behind the
   first.

### Under the hood

A traceback describes the **call stack**: the chain of active calls at the
moment of the error. Each `File` entry is one **frame**. The error itself is
an **exception object**. Its type (like `TypeError`) is a class, and its
message is stored inside it. If nothing catches the exception, it travels up
through every frame, and the interpreter finally prints the traceback to the
**standard error** stream (stderr, not stdout) and exits with status 1. You
will learn to catch exceptions with `try`/`except` in a later module.

Because the traceback goes to stderr, redirecting output with `>` does not
capture it:

```bash
$ python3 report.py > out.txt
Traceback (most recent call last):
...
$ cat out.txt
Student: Riya
```

> **Predict the output.** Which line number will the traceback report?
>
> ```python
> a = 10
> b = 0
> print("Start")
> c = a / b
> print(c)
> ```

<details><summary>Answer</summary>

`Start` is printed, then a traceback reporting **line 4**, ending with
`ZeroDivisionError: division by zero`. Line 5 never runs.

</details>

### Common misconceptions

- **"The error is on the line shown, so the bug is on that line."** Often true
  for runtime errors, but the *cause* may be earlier, for example a variable
  given the wrong value on line 2 and used on line 9.
- **"A long traceback means many errors."** It is one error, shown through
  several frames.
- **Fixing by guessing.** Change one thing, rerun, read the new message.

---

## 9. help(), dir() and type()

These three built-in functions let Python teach you about itself. They work
offline, which matters for you.

### type()

`type(x)` tells you what **kind** of object `x` is:

```python
>>> type(42)
<class 'int'>
>>> type(3.5)
<class 'float'>
>>> type("42")
<class 'str'>
>>> type(True)
<class 'bool'>
>>> type(None)
<class 'NoneType'>
>>> type(print)
<class 'builtin_function_or_method'>
>>> type(7 / 2)
<class 'float'>
>>> type(input)
<class 'builtin_function_or_method'>
```

`"42"` with quotes is text (`str`), not a number. `type` is the quickest way to
discover that `input()` always gives you a `str`.

To get just the name of the type, use `type(x).__name__`:

```python
>>> type(42).__name__
'int'
```

### dir()

`dir(x)` lists the names (attributes) available on an object:

```python
>>> dir("hello")
['__add__', '__class__', ..., 'upper', 'zfill']
>>> import platform
>>> dir(platform)
[..., 'machine', 'node', 'platform', 'processor', 'python_version', ...]
```

`dir()` with no argument lists the names defined in the current scope, such as
your variables.

Names with double underscores on both sides, like `__add__` or `__doc__`, are
called **dunder** ("double underscore") names. Python uses them internally.
`"a" + "b"` actually calls `"a".__add__("b")`. You can ignore most dunder names
for now.

### help()

`help(x)` shows the documentation for `x`:

```python
>>> help(len)
Help on built-in function len in module builtins:

len(obj, /)
    Return the number of items in a container.
```

Long help opens in a **pager**. Use the arrow keys or Space to scroll, `/word`
to search, and **q** to quit. `help()` with no argument starts an interactive
help system; type `quit` to leave it. Other useful forms:

```python
>>> help("keywords")     # list Python's reserved words
>>> help(str.upper)      # help on one method
>>> import os
>>> help(os.environ.get)
```

From the terminal, without opening the REPL:

```bash
$ python3 -m pydoc len
```

### Under the hood

`help()` reads documentation strings, called **docstrings**, stored on objects
in the `__doc__` attribute. It also reads the function's parameters. You can
read the raw docstring yourself:

```python
>>> abs.__doc__
'Return the absolute value of the argument.'
>>> abs.__name__
'abs'
>>> abs.__module__
'builtins'
```

`builtins` is the module that holds every built-in name like `print`, `len` and
`type`. Python searches it last whenever it looks up a name. That is why you
can use `print` without importing anything.

`type` itself is an object. `type(type)` is `<class 'type'>`. Classes are
objects too, and their type is `type`. You will explore this in the module on
classes.

> **Predict the output.**
>
> ```python
> print(type("3" + "4"))
> print("3" + "4")
> print(type(3 + 4.0))
> ```

<details><summary>Answer</summary>

```
<class 'str'>
34
<class 'float'>
```

Joining two strings gives a string, `"34"`. Adding an int and a float gives a
float, `7.0`.

</details>

---

## 10. PEP 8 and the Zen of Python

### PEP 8

A **PEP** (Python Enhancement Proposal) is a design document. **PEP 8** is the
official style guide for Python code. Code that follows it looks familiar to
every Python programmer, so it is faster to read and review. Remember: code is
read many more times than it is written.

The rules you need now:

**Names**

| Kind | Style | Example |
|---|---|---|
| variables, functions | `snake_case` (lowercase, words joined by `_`) | `total_marks`, `student_name` |
| constants | `UPPER_SNAKE_CASE` | `MAX_SIZE = 100` |
| classes | `CapWords` | `StudentRecord` |

- Never use `l` (lower L), `O` (capital o) or `I` (capital i) as single-letter
  names. They look like `1` and `0`.
- Choose names that say what the value means: `seconds_left`, not `x` or `sl`.

**Layout**

- Indent with **4 spaces**. Never tabs.
- Keep lines at most **79 characters**.
- One statement per line. Do not join statements with `;`.
- Put a single space around assignment and binary operators: `total = a + b`.
- No spaces around `=` in keyword arguments: `print(a, b, sep="-")`.
- No space before the brackets of a call: `print(x)`, not `print (x)`.
- A space after each comma: `print(a, b)`.
- Imports at the top of the file, one module per line.
- A comment starts with `# ` (hash and a space) and explains *why*, not *what*.

Before and after:

```python
# Bad
import os,sys
studentName="Asha";Marks=87
print ( studentName,Marks )

# Good
import os
import sys

student_name = "Asha"
marks = 87
print(student_name, marks)
```

You do not need to memorise every rule. Tools check them for you:

```bash
(.venv) $ python -m pip install ruff
(.venv) $ ruff check report.py      # report problems
(.venv) $ ruff format report.py     # rewrite the layout automatically
```

Other common tools are `black` (formatter) and `flake8` (linter).

PEP 8 itself says consistency within a project matters more than any single
rule, and that it is fine to break a rule when following it would make the code
less readable.

### The Zen of Python

Type this in the REPL:

```python
>>> import this
The Zen of Python, by Tim Peters

Beautiful is better than ugly.
Explicit is better than implicit.
Simple is better than complex.
Complex is better than complicated.
Flat is better than nested.
Sparse is better than dense.
Readability counts.
Special cases aren't special enough to break the rules.
Although practicality beats purity.
Errors should never pass silently.
Unless explicitly silenced.
In the face of ambiguity, refuse the temptation to guess.
There should be one-- and preferably only one --obvious way to do it.
Although that way may not be obvious at first unless you're Dutch.
Now is better than never.
Although never is often better than *right* now.
If the implementation is hard to explain, it's a bad idea.
If the implementation is easy to explain, it may be a good idea.
Namespaces are one honking great idea -- let's do more of those!
```

These 19 lines are the design values of Python. A few, in plain words:

- **Explicit is better than implicit.** Make your intent visible. Writing
  `import math` and then `math.sqrt(x)` shows where `sqrt` comes from.
- **Readability counts.** Clear names and simple layout are worth more than
  clever tricks.
- **Errors should never pass silently.** A crash with a clear traceback is
  better than a program that quietly gives wrong answers. This is why Python
  refuses `"Marks: " + 87` instead of guessing what you meant.
- **In the face of ambiguity, refuse the temptation to guess.** Should
  `"3" + 4` be `"34"` or `7`? Python will not guess. It raises `TypeError`.
- **Simple is better than complex.** Prefer the straightforward solution.
- **Flat is better than nested.** Deeply nested code is hard to follow.

"Dutch" refers to Guido van Rossum, Python's creator, who is from the
Netherlands.

### Under the hood

`this` is a real module in the standard library. Its source code stores the
Zen in scrambled form (using a simple letter-rotation cipher called ROT13) and
decodes it when imported. That is a joke: the code that prints "Beautiful is
better than ugly" is deliberately ugly. Modules run their top-level code only
on their **first** import in a process, so typing `import this` a second time
in the same REPL prints nothing.

> **Predict the output.** In a fresh REPL you type `import this` twice. How many
> times is the Zen printed?

<details><summary>Answer</summary>

Once. The second `import` finds the module already loaded (in a cache called
`sys.modules`) and does not run its code again.

</details>

---

## 11. Putting it together: the module project

The project for this module is a **personal command-line script that prints
system and environment information**. A typical session to build it uses
everything above:

```bash
$ mkdir -p ~/code/sysinfo && cd ~/code/sysinfo
$ git init
$ python3 -m venv .venv
$ source .venv/bin/activate
(.venv) $ echo ".venv/" > .gitignore
(.venv) $ code .                      # write sysinfo.py in VS Code
(.venv) $ chmod +x sysinfo.py
(.venv) $ ./sysinfo.py
(.venv) $ git add .gitignore sysinfo.py
(.venv) $ git commit -m "Add system info script"
(.venv) $ git log --oneline
```

A starting point for `sysinfo.py`:

```python
#!/usr/bin/env python3
"""Print information about this computer and Python."""
import os
import platform
import sys

print("Python version:", platform.python_version())
print("Implementation:", platform.python_implementation())
print("Executable:", sys.executable)
print("Operating system:", platform.system(), platform.release())
print("User:", os.environ.get("USER", "unknown"))
print("Working folder:", os.getcwd())
print("In a virtual environment:", sys.prefix != sys.base_prefix)
```

The text in triple quotes on line 2 is a **module docstring**: it describes
what the file does, and `help()` will show it. Problem p025 asks you to build a
complete version of this script.

---

## Summary

- Python is a language. **CPython** is the standard interpreter. It compiles
  your file to **bytecode** (so syntax errors stop everything) and then
  executes it. PyPy is a faster alternative interpreter with a JIT.
- Versions are `major.minor.micro`. Use Python 3 only. Check with
  `python3 --version` or `sys.version_info`.
- Leave the system Python alone. Use **pyenv** or **uv** when you need other
  versions.
- The shell finds programs through **PATH**, starts them as child processes,
  and passes them **exported** environment variables. Exit status 0 means
  success.
- `pwd`, `ls`, `cd`, `mkdir`, `cat`, `>`, `>>` and `|` cover most daily
  terminal work.
- The **REPL** echoes values; **scripts** do not. `print` has `sep` and `end`.
  `input()` always returns a `str`.
- A **shebang** (`#!/usr/bin/env python3`) plus `chmod +x` makes a script
  runnable as `./script.py`.
- In VS Code, the **selected interpreter** decides which Python runs. The
  debugger pauses at breakpoints so you can inspect variables.
- A **venv** is a folder with a link to Python and its own `site-packages`.
  Activation only edits `PATH`. Use `python -m pip`. Never commit `.venv`.
- **Git**: `init`, `status`, `add` (stage), `commit` (save a snapshot), `log`,
  `diff`, `branch`, `switch`. A branch is a pointer to a commit.
- Read a **traceback** from the bottom: error type and message, then file and
  line number, then the code and carets.
- `type()`, `dir()` and `help()` let Python explain itself. `help` reads
  `__doc__`.
- **PEP 8** is the style guide: `snake_case`, 4 spaces, 79 columns, spaces
  around operators. The **Zen of Python** (`import this`) states the values
  behind it.

## Checklist

Tick each item only when you can do it without looking at this chapter.

- [ ] I can create a virtual environment with `python3 -m venv .venv`, activate
      it, install a package with `python -m pip install`, and run a script,
      all from the terminal.
- [ ] I can explain what activation changes (`PATH`) and how to check which
      Python is running (`which python`, `sys.executable`).
- [ ] I can read a traceback, name the error type, and point to the exact file
      and line that failed.
- [ ] I know that a `SyntaxError` may be reported on a line after the real
      mistake.
- [ ] I can initialise a Git repository, stage and commit changes, and view the
      history with `git log` and changes with `git diff`.
- [ ] I can create a branch, switch between branches, and read
      `git status --short`.
- [ ] I can navigate with `pwd`, `ls`, `cd`, and use `>`, `>>` and `|`.
- [ ] I can set an environment variable with `export` and read it in Python
      with `os.environ.get`.
- [ ] I can make a script executable with a shebang and `chmod +x`.
- [ ] I can use `type()`, `dir()` and `help()` to learn about an unfamiliar
      object.
- [ ] I can rewrite messy code to follow PEP 8 naming and spacing.

## Further reading

All of these are official documentation, worth downloading or reading slowly.

- The Python Tutorial: https://docs.python.org/3/tutorial/index.html
- Using the Python interpreter: https://docs.python.org/3/tutorial/interpreter.html
- Command line and environment options: https://docs.python.org/3/using/cmdline.html
- Using Python on Unix platforms: https://docs.python.org/3/using/unix.html
- Virtual environments and packages (tutorial): https://docs.python.org/3/tutorial/venv.html
- The venv module: https://docs.python.org/3/library/venv.html
- Installing Python modules: https://docs.python.org/3/installing/index.html
- Errors and exceptions (tutorial): https://docs.python.org/3/tutorial/errors.html
- Built-in exceptions: https://docs.python.org/3/library/exceptions.html
- Built-in functions (help, dir, type, print, input): https://docs.python.org/3/library/functions.html
- The sys module: https://docs.python.org/3/library/sys.html
- The platform module: https://docs.python.org/3/library/platform.html
- The dis module: https://docs.python.org/3/library/dis.html
- Glossary of Python terms: https://docs.python.org/3/glossary.html
- PEP 8, the style guide: https://peps.python.org/pep-0008/
- PEP 20, the Zen of Python: https://peps.python.org/pep-0020/
- PEP 668, externally managed environments: https://peps.python.org/pep-0668/
- Python release status and support dates: https://devguide.python.org/versions/
- pip documentation: https://pip.pypa.io/en/stable/
- Python Packaging User Guide: https://packaging.python.org/en/latest/
- Git documentation and the free Pro Git book: https://git-scm.com/doc
- VS Code Python tutorial: https://code.visualstudio.com/docs/python/python-tutorial
- uv documentation: https://docs.astral.sh/uv/
- pyenv: https://github.com/pyenv/pyenv
- Ruff documentation: https://docs.astral.sh/ruff/
