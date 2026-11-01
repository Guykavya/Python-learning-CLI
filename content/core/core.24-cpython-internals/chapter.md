# Chapter 24: CPython internals

You have written Python for twenty-three chapters without ever asking what happens when you press Enter. The answer is: a lot. Your source text is cut into tokens, the tokens are arranged into a tree, the tree is turned into a list of small instructions called **bytecode**, and a loop written in C runs those instructions one by one. Every object you create gets a small header with its type and a counter of how many references point at it. When that counter reaches zero, the memory is given back at once. When objects point at each other in a circle, the counter can never reach zero, and a second mechanism, the **garbage collector**, has to step in.

This chapter opens that machine. It is not about writing C. It is about understanding the program that runs your Python, so that you can explain performance ("why is a local variable faster than a global?"), memory ("why did my objects not go away?"), and strange results ("why is `a is b` true here and false there?") from first principles instead of guessing.

The chapter has two learning outcomes:

1. **Read bytecode for a function and explain what the interpreter does**: take a `dis` listing, follow the values on the stack instruction by instruction, and say in plain words what each step does.
2. **Explain why a reference cycle needs the garbage collector**: say why reference counting alone can never free objects that point at each other, and how the collector finds and frees them.

There is a third goal that runs through the whole chapter: telling apart **what the Python language promises** from **what CPython happens to do today**. Section 21 is about that, and you will see the theme in every section before it.

**A note on how examples are shown.** Every block that has output was really run, with **CPython 3.14** on 64-bit Linux. The course supports Python 3.11 and later, and this chapter is the one where versions matter most: bytecode instruction names, reference counts and object sizes all change between versions. Such values are labelled every time they appear. Memory addresses and `id()` numbers change on every run, so they are labelled too. When an example could print a CPython error message whose wording changes between versions, it prints only the exception's type name. Everything uses features from core.01 to core.23 plus this chapter's topics.

## Table of contents

[1. Why look under the hood](#1-why-look-under-the-hood) · [2. From source to running](#2-from-source-to-running) · [3. Code objects](#3-code-objects) · [4. The `dis` module: reading bytecode](#4-the-dis-module-reading-bytecode) · [5. A tour of the common instructions](#5-a-tour-of-the-common-instructions) · [6. Frames and the evaluation loop](#6-frames-and-the-evaluation-loop) · [7. The specialising adaptive interpreter](#7-the-specialising-adaptive-interpreter) · [8. Constant folding and other compile-time tricks](#8-constant-folding-and-other-compile-time-tricks) · [9. Objects in memory](#9-objects-in-memory) · [10. Reference counting](#10-reference-counting) · [11. Reference cycles and the garbage collector](#11-reference-cycles-and-the-garbage-collector) · [12. `weakref`: references that do not keep objects alive](#12-weakref-references-that-do-not-keep-objects-alive) · [13. `__del__` and finalizers](#13-__del__-and-finalizers) · [14. Interning and caches](#14-interning-and-caches) · [15. How `list` works](#15-how-list-works) · [16. How `dict` works](#16-how-dict-works) · [17. How `set` works](#17-how-set-works) · [18. Strings inside CPython](#18-strings-inside-cpython) · [19. The GIL, free threading and the JIT](#19-the-gil-free-threading-and-the-jit) · [20. Extending Python: C extensions, `ctypes` and Cython](#20-extending-python-c-extensions-ctypes-and-cython) · [21. Using internals knowledge responsibly](#21-using-internals-knowledge-responsibly) · [22. Project preview: a mini stack-based bytecode interpreter](#22-project-preview-a-mini-stack-based-bytecode-interpreter) · [23. Summary](#23-summary)

## 1. Why look under the hood

### 1.1 Python the language, CPython the program

"Python" is two things that people usually mix up.

- **Python the language** is a specification: the grammar, what `for` means, what a `dict` must do, which methods `__eq__` and `__hash__` are. It is written down in the *Python Language Reference* and the *Library Reference*.
- **CPython** is one program that implements that language. It is written in C (hence the name), it is what you download from python.org, and it is what runs when you type `python3`. It is the **reference implementation**: when the specification is unclear, CPython's behaviour usually becomes the answer.

There are other implementations of the same language:

| Implementation | Written in | Main idea |
|---|---|---|
| **CPython** | C | the reference; huge ecosystem of C extensions |
| **PyPy** | RPython (a subset of Python) | a tracing JIT compiler; often several times faster on pure-Python loops |
| **MicroPython** | C | a tiny Python for microcontrollers |
| **GraalPy** | Java | runs on the GraalVM, can call Java code |

A program that sticks to the language rules runs on all of them. A program that relies on a CPython detail (for example, that a file is closed the moment its last name goes away) may work on CPython and break on PyPy. You can ask which implementation you are on:

```python
import sys
import platform

print(sys.implementation.name)
print(platform.python_implementation())
print(sys.version_info[:2])
```
```text
cpython
CPython
(3, 14)
```

The third line is the version this book was run with; yours may differ.

### 1.2 What knowing the internals buys you

You can write good Python without any of this chapter. So why learn it? Because certain questions have no good answer without it:

- **Performance.** Why is `x in some_set` fast but `x in some_list` slow? Why does `list.insert(0, x)` get slower as the list grows? Why does a loop run faster inside a function than at module level? Each answer is a fact about how CPython stores data or runs bytecode.
- **Memory.** Why does memory not drop after you `del` a big structure? Why does a cache keep objects alive forever? Why does `sys.getsizeof` say a list of a million strings is only 8 MB? These are facts about reference counting, cycles and object layout.
- **Debugging.** A traceback is a printout of a chain of **frames**. `pdb` (core.20) works by hooking into the evaluation loop. Knowing what a frame is makes both much less mysterious.
- **Reading the docs.** The official documentation has boxes labelled *"CPython implementation detail"*. After this chapter you will know why those boxes exist and how seriously to take them.

### 1.3 A warning before we start

Everything in this chapter that is marked as a CPython detail **can change**, and much of it did change in the last few releases. Python 3.11 rewrote big parts of the interpreter for speed. 3.12 made some objects immortal. 3.13 added an optional build without the GIL and an experimental JIT compiler. 3.14 changed bytecode again and gave the garbage collector a new design.

So learn the **ideas** (a stack machine, reference counts, a cycle detector, hash tables, over-allocated arrays). The ideas have been stable for decades. Learn to **look** (with `dis`, `sys`, `gc`, `weakref`) rather than memorising numbers. And never write a program whose correctness depends on a number printed in this chapter.

### 1.4 The map of this chapter

Sections 2 to 8 show **how code runs**: source to bytecode, code objects, reading `dis` output, frames, the specialising interpreter and constant folding. Sections 9 to 14 show **how memory works**: object layout, reference counting, cycles and the garbage collector, weak references, finalizers and caches. Sections 15 to 18 open up `list`, `dict`, `set` and `str`. Sections 19 to 22 cover the edges: the GIL, free threading and the JIT; C extensions, `ctypes` and Cython; using this knowledge responsibly; and the design of the module project, a small bytecode interpreter of your own.

## 2. From source to running

### 2.1 The pipeline

When CPython runs a file, it goes through these stages:

```text
 source text  "total = price * 2"
      |
      |  1. tokenizer: cut the text into tokens
      v
 tokens       NAME 'total'  OP '='  NAME 'price'  OP '*'  NUMBER '2'
      |
      |  2. parser: arrange the tokens into a tree, following the grammar
      v
 AST          Assign(targets=[Name('total')], value=BinOp(Name('price'), Mult(), Constant(2)))
      |
      |  3. compiler: decide which names are local/global, emit instructions
      v
 code object  bytecode + constants + names + ...
      |
      |  4. evaluation loop: run the instructions one by one
      v
 effects      objects created, names bound, output printed
```

Stages 1 to 3 happen **once** per file (and the result is cached on disk, section 2.6). Stage 4 happens every time the code runs: a loop body that runs a million times is compiled once and evaluated a million times. That is why almost all performance work is about stage 4.

Each stage has a standard-library module that lets you look at its output: `tokenize` for tokens, `ast` for the tree, `compile()` and `dis` for code objects and bytecode. Let us look at each in turn.

### 2.2 Stage 1: tokens

The **tokenizer** reads characters and groups them into **tokens**: names, numbers, strings, operators, and the special `NEWLINE`, `INDENT` and `DEDENT` tokens that make indentation meaningful. The `tokenize` module exposes the same process:

```python
import io
import tokenize

source = "total = price * 2\n"
for tok in tokenize.generate_tokens(io.StringIO(source).readline):
    print(f"{tokenize.tok_name[tok.type]:<10} {tok.string!r}")
```
```text
NAME       'total'
OP         '='
NAME       'price'
OP         '*'
NUMBER     '2'
NEWLINE    '\n'
ENDMARKER  ''
```

`generate_tokens` wants a function that returns one line at a time, and `io.StringIO(source).readline` (core.12) is exactly that. Notice that spaces have disappeared: the tokenizer throws them away, except at the start of a line, where it turns changes of indentation into `INDENT` and `DEDENT` tokens.

You rarely need tokens directly. Tools that must keep comments and exact spacing, such as code formatters, work at this level, because the next stage throws comments away.

### 2.3 Stage 2: the abstract syntax tree

The **parser** checks the tokens against Python's grammar and builds an **abstract syntax tree** (AST): a tree of node objects, one per piece of syntax. "Abstract" means the details that do not change meaning (spaces, comments, extra parentheses) are gone. A `SyntaxError` is raised in this stage, before a single line runs.

The `ast` module gives you the tree:

```python
import ast

tree = ast.parse("total = price * 2")
print(ast.dump(tree, indent=2))
```
```text
Module(
  body=[
    Assign(
      targets=[
        Name(id='total', ctx=Store())],
      value=BinOp(
        left=Name(id='price', ctx=Load()),
        op=Mult(),
        right=Constant(value=2)))])
```

Read it from the outside in. A `Module` holds a list of statements in `body`. The only statement is an `Assign` with one target, the name `total`, stored to (`Store()`). Its value is a `BinOp` (binary operation) whose left side is the name `price`, loaded (`Load()`), whose operator is `Mult()`, and whose right side is the constant `2`. The `ctx` field already tells you whether a name is being read or written: the parser knows that `total` here is a target.

Node classes are ordinary Python classes (`ast.Assign`, `ast.Name`, `ast.BinOp` and so on), and each node has fields you can read. `ast.walk(tree)` yields every node in the tree, which is enough for many small analysis tools:

```python
import ast
from collections import Counter

source = """
def area(w, h):
    return w * h

for side in range(3):
    print(area(side, side + 1))
"""

tree = ast.parse(source)
kinds = Counter(type(node).__name__ for node in ast.walk(tree))
print(kinds.most_common(4))

names = sorted({node.id for node in ast.walk(tree) if isinstance(node, ast.Name)})
print(names)
```
```text
[('Name', 8), ('Load', 7), ('Call', 3), ('arg', 2)]
['area', 'h', 'print', 'range', 'side', 'w']
```

A dozen lines of code, and you have a tool that finds every name used in a file. Linters such as `ruff` (core.20) are built on exactly this idea, at a much larger scale.

For bigger jobs there are two classes. `ast.NodeVisitor` calls a method `visit_<NodeName>` for each node of that kind, and `ast.NodeTransformer` does the same but lets each method **return a replacement node**, so you can rewrite code. `ast.unparse(tree)` turns a tree back into source text:

```python
import ast

class DoubleNumbers(ast.NodeTransformer):
    def visit_Constant(self, node):
        if isinstance(node.value, int):
            return ast.Constant(node.value * 2)
        return node

tree = ast.parse("x = 10 + y * 3")
new_tree = DoubleNumbers().visit(tree)
print(ast.unparse(new_tree))
```
```text
x = 20 + y * 6
```

That is a toy, but the same pattern powers real tools: `pytest` rewrites your `assert` statements this way (core.08) so that a failing assert can show the values involved.

**One more useful function.** `ast.literal_eval(text)` safely turns text like `"[1, 2, {'a': 3}]"` into the Python value. It only accepts literals (numbers, strings, lists, tuples, dicts, sets, `True`, `False`, `None`), so unlike `eval` it cannot run arbitrary code. Prefer it whenever you need to read a Python-literal string from a file or a user.

### 2.4 Stage 3: compiling to a code object

The **compiler** walks the AST and does two jobs. First, it builds a **symbol table**: for every name in every function it decides whether the name is local, global, or a closure variable (core.06, section on scope). This is why the scope of a name is fixed when the function is *compiled*, not when it runs. Second, it emits the **bytecode**: a sequence of small instructions for a virtual machine.

The built-in `compile()` runs stages 1 to 3 and hands you the result, a **code object**:

```python
code = compile("total = price * 2", "<demo>", "exec")
print(type(code).__name__)
print(code.co_names)

namespace = {"price": 21}
exec(code, namespace)
print(namespace["total"])
```
```text
code
('price', 'total')
42
```

`compile(source, filename, mode)` takes three arguments:

- `source`: a string (or an AST from `ast.parse`).
- `filename`: only used in error messages and tracebacks. By convention you pass something in angle brackets, like `"<demo>"`, when there is no real file.
- `mode`: what kind of code the source is.

| Mode | Accepts | Run it with | Result |
|---|---|---|---|
| `"exec"` | any sequence of statements | `exec(code, ns)` | always `None` |
| `"eval"` | exactly one expression | `eval(code, ns)` | the value of the expression |
| `"single"` | one interactive statement | `exec(code, ns)` | prints the value of an expression statement, like the REPL |

`exec` and `eval` take an optional dictionary to use as the global namespace. Passing your own dictionary keeps the code from touching your module's names. It is **not** a security sandbox: never `exec` or `eval` text from an untrusted user, because it can run any code at all, such as deleting your files (`ast.literal_eval` is the safe tool for literals).

#### Predict the output 2.1

```python
code1 = compile("2 + 3", "<a>", "eval")
code2 = compile("2 + 3", "<b>", "exec")
print(eval(code1))
print(eval(code2))
code3 = compile("2 + 3", "<c>", "single")
exec(code3)
try:
    compile("x = 1", "<d>", "eval")
except SyntaxError as e:
    print(type(e).__name__)
```

<details><summary>Answer</summary>

```text
5
None
5
SyntaxError
```

- `code1` is an expression compiled in `"eval"` mode, so `eval` returns its value, `5`.
- `code2` is the same text compiled as a *statement* in `"exec"` mode. Running it computes `5` and throws it away; the result of running statements is always `None`.
- `"single"` mode behaves like the REPL: an expression statement prints its value (through `sys.displayhook`), so `5` appears even though nobody called `print`.
- `x = 1` is a statement, not an expression, so `"eval"` mode rejects it at compile time with a `SyntaxError`, before anything runs.

</details>

### 2.5 Stage 4: the evaluation loop

The code object is data. To run it, CPython hands it to the **evaluation loop**, a big C function (`_PyEval_EvalFrameDefault` in the CPython source, if you ever go looking). In very simplified form it looks like this:

```text
loop forever:
    instruction = next instruction in the bytecode
    if instruction is LOAD_CONST:   push the constant onto the stack
    elif instruction is BINARY_OP:  pop two values, combine them, push the result
    elif instruction is STORE_NAME: pop a value and bind it to a name
    elif instruction is RETURN_VALUE: pop a value and return it to the caller
    ... about 200 more kinds ...
```

This loop is the "virtual machine" that people mean when they say Python is interpreted. It is a **stack machine**: instructions take their inputs from a stack of values and push their results back on it. Sections 4 and 5 teach you to read the instructions, and section 22 sketches a tiny stack machine of your own.

### 2.6 `.pyc` files and `__pycache__`

When you `import` a module, CPython saves the compiled code object to a file in a folder called `__pycache__` next to the source, for example `__pycache__/shapes.cpython-314.pyc`. The next import checks that the source has not changed (by its modification time and size) and loads the saved code object, skipping stages 1 to 3.

```python
import importlib.util

print(importlib.util.cache_from_source("/home/you/project/shapes.py"))
print(len(importlib.util.MAGIC_NUMBER), "bytes of magic number")
```
```text
/home/you/project/__pycache__/shapes.cpython-314.pyc
4 bytes of magic number
```

The file name contains the version tag (`cpython-314` here), and each `.pyc` starts with a **magic number** that changes whenever the bytecode format changes. That is how CPython knows not to load a 3.13 `.pyc` in 3.14. It is also your first hint that **bytecode is not portable between versions**.

A `.pyc` file does **not** make your program run faster, only *start* faster: the bytecode inside is identical to what would be compiled from source. The script you run directly (`python3 main.py`) is never cached; only imported modules are. And deleting `__pycache__` is always safe: it is rebuilt on the next import (which is also why it belongs in `.gitignore`, core.13).

## 3. Code objects

### 3.1 A function is a code object plus context

When Python executes a `def` statement, it does not compile anything: the function body was already compiled, along with the rest of the file, into a code object. `def` simply wraps that code object in a new **function object** together with the things that can differ from one `def` execution to the next:

| Function attribute | What it holds |
|---|---|
| `f.__code__` | the code object: bytecode and everything the compiler knew |
| `f.__globals__` | the module namespace the function was defined in, used to look up global names |
| `f.__defaults__` | the default argument values, evaluated once when `def` ran (core.06's mutable-default trap) |
| `f.__closure__` | the cells holding variables captured from enclosing functions, or `None` |
| `f.__name__`, `f.__qualname__` | the name, which can be changed (decorators do, core.11) |

So two functions made by the same `def` in a loop share one code object but can have different defaults and closures:

```python
def make_multiplier(n):
    def multiply(x):
        return x * n
    return multiply

double = make_multiplier(2)
triple = make_multiplier(3)
print(double is triple)
print(double.__code__ is triple.__code__)
print(double.__closure__[0].cell_contents, triple.__closure__[0].cell_contents)
```
```text
False
True
2 3
```

Two different function objects, one shared code object, two different closures. The compiled instructions are the same; only the data they work on differs.

### 3.2 The attributes worth knowing

A code object has many `co_` attributes. These are the ones that are stable across Python 3.11 to 3.14 and that you will use:

| Attribute | Meaning |
|---|---|
| `co_name` | the function's name as written in the `def` (`"<module>"` for module code) |
| `co_qualname` | the qualified name, like `"Outer.method"` (3.11+) |
| `co_argcount` | number of positional parameters (including positional-only, excluding `*args`) |
| `co_posonlyargcount`, `co_kwonlyargcount` | positional-only and keyword-only parameter counts |
| `co_varnames` | names of local variables, **parameters first**, in order |
| `co_names` | names used for globals, built-ins and attributes |
| `co_consts` | constant values the bytecode uses (numbers, strings, nested code objects...) |
| `co_cellvars` | locals that inner functions capture |
| `co_freevars` | variables this function captures from an enclosing function |
| `co_flags` | bit flags: is it a generator, does it take `*args`, ... |
| `co_filename`, `co_firstlineno` | where the code came from |
| `co_code` | the raw bytecode as `bytes` (do not decode it by hand; use `dis`) |

Here is a real function taken apart:

```python
RATE = 0.18

def price_with_tax(amount, qty=1):
    "Return the total price with tax."
    subtotal = amount * qty
    tax = subtotal * RATE
    label = "total"
    return round(subtotal + tax, 2), label, 1000

c = price_with_tax.__code__
print("co_name     ", c.co_name)
print("co_argcount ", c.co_argcount)
print("co_varnames ", c.co_varnames)
print("co_names    ", c.co_names)
print("co_consts   ", c.co_consts)
```
```text
co_name      price_with_tax
co_argcount  2
co_varnames  ('amount', 'qty', 'subtotal', 'tax', 'label')
co_names     ('RATE', 'round')
co_consts    ('Return the total price with tax.', 'total', 1000)
```

Look at what the compiler decided:

- **`co_varnames`** starts with the two parameters, then the locals in the order they are first assigned. `amount`, `qty`, `subtotal`, `tax` and `label` are all **local**, because they are assigned (or are parameters) inside the function.
- **`co_names`** holds `RATE` and `round`. They are used but never assigned inside the function, so the compiler made them **global** lookups. At this point the compiler does not know or care whether `round` is a built-in: at run time the lookup checks the module globals first, then the built-ins (core.06, the LEGB rule).
- **`co_consts`** holds the docstring, `"total"` and `1000`.

Where are `2` and `None`? This is your first version trap. Python 3.14 has an instruction that loads small integers directly, without storing them in `co_consts`, and in 3.14 a function that does not need `None` as a constant does not store it either. In Python 3.11 to 3.13 you would also see `2` in this tuple, and whether `None` appears changes between versions too. **Rule: test whether a value is *in* `co_consts`, never its position, and do not rely on small integers or `None` being there at all.**

#### Predict the output 3.1

For this function, predict `co_argcount`, `co_varnames` and `co_names`. (Do not worry about `co_consts`.)

```python
import math

def hypotenuse(a, b, *, rounded=False):
    total = a * a + b * b
    result = math.sqrt(total)
    if rounded:
        result = round(result)
    return result

c = hypotenuse.__code__
print(c.co_argcount, c.co_kwonlyargcount)
print(c.co_varnames)
print(c.co_names)
```

<details><summary>Answer</summary>

```text
2 1
('a', 'b', 'rounded', 'total', 'result')
('math', 'sqrt', 'round')
```

- `co_argcount` counts positional parameters only: `a` and `b`. `rounded` comes after `*`, so it is counted in `co_kwonlyargcount`.
- `co_varnames` lists all parameters first (`a`, `b`, `rounded`), then locals in order of first assignment (`total`, `result`). `result` is assigned twice but appears once.
- `co_names` holds `math` (a global), `sqrt` (an **attribute** name: attribute names also live in `co_names`), and `round` (a built-in, looked up as a global).

</details>

### 3.3 Nested functions, cells and free variables

When an inner function uses a variable of the outer function, that variable cannot simply live in the outer function's local slots: the inner function may still need it after the outer function has returned. The compiler spots this and stores the variable in a **cell**, a tiny box object that both functions can reach.

- In the outer function, the name appears in **`co_cellvars`** ("I own a cell for this").
- In the inner function, it appears in **`co_freevars`** ("I use a cell that someone else owns").
- The function object of the inner function keeps the actual cells in `__closure__`, a tuple of cell objects. `cell.cell_contents` reads the box.

```python
def make_counter():
    count = 0
    def step():
        nonlocal count
        count += 1
        return count
    return step

print("outer cellvars:", make_counter.__code__.co_cellvars)
counter = make_counter()
print("inner freevars:", counter.__code__.co_freevars)
counter()
counter()
print("cell holds:", counter.__closure__[0].cell_contents)

inner_codes = [k for k in make_counter.__code__.co_consts if hasattr(k, "co_code")]
print("nested code:", [k.co_name for k in inner_codes])
```
```text
outer cellvars: ('count',)
inner freevars: ('count',)
cell holds: 2
nested code: ['step']
```

The last two lines show something worth remembering: the inner function's **code object is a constant of the outer code object**. It was compiled once, with the outer function. Each call of `make_counter` only builds a new *function object* around it, with a new cell. That is why the closures in section 3.1 shared a code object.

This also explains the famous late-binding trap from core.06: a cell is a box, and an inner function reads the box **when it is called**, not when it is created. Closures made in a loop all share the loop variable's one cell, so they all see its final value. The fix is to bind the current value early, for example with a default argument `def show(i=i):`. Problem p015 explores this with `co_freevars` and `__closure__`.

### 3.4 Flags: what kind of code is this?

`co_flags` is an integer whose bits record facts about the code. The `inspect` module has names for the useful bits:

```python
import inspect

def plain(a, b): return a + b
def star(*args, **kwargs): return args
def gen():
    yield 1

FLAGS = ["CO_VARARGS", "CO_VARKEYWORDS", "CO_GENERATOR", "CO_COROUTINE"]
for func in (plain, star, gen):
    names = [name for name in FLAGS if func.__code__.co_flags & getattr(inspect, name)]
    print(f"{func.__name__:<6}", names)
```
```text
plain  []
star   ['CO_VARARGS', 'CO_VARKEYWORDS']
gen    ['CO_GENERATOR']
```

The generator flag is how Python knows that calling `gen()` must not run the body but return a generator object (core.10). It is set by the compiler when it sees a `yield` anywhere in the body, which is why even a `yield` in a branch that never runs makes the whole function a generator. `inspect.isgeneratorfunction(f)` simply checks this bit.

The raw value of `co_flags` also contains private bits whose meaning changes between versions, so always test a single named bit with `&`, never compare the whole number.

Code objects are also **immutable**: they are shared by every function made from them and may be cached in `.pyc` files. Tools that need a modified copy use `code.replace(co_name="new")`, which returns a new code object.

#### Try it 3.2

Write a function `local_and_global(func)` that returns a tuple of two sorted lists: the names of `func`'s parameters and local variables, and the names it uses as globals, built-ins or attributes. Test it on `price_with_tax` from section 3.2. Why can the second list contain names that are not globals at all?

<details><summary>Answer</summary>

```python
RATE = 0.18

def price_with_tax(amount, qty=1):
    subtotal = amount * qty
    tax = subtotal * RATE
    return round(subtotal + tax, 2)

def local_and_global(func):
    code = func.__code__
    return sorted(code.co_varnames), sorted(code.co_names)

print(local_and_global(price_with_tax))
print(local_and_global(lambda s: s.upper()))
```
```text
(['amount', 'qty', 'subtotal', 'tax'], ['RATE', 'round'])
(['s'], ['upper'])
```

`co_names` mixes global names with **attribute** names: in the lambda, `upper` is in `co_names` even though it is not a global, because `s.upper` looks up the attribute name `upper`. To separate the two you must look at *which instruction* uses each name, which is what `dis` (next section) shows: `LOAD_GLOBAL` for globals, `LOAD_ATTR` for attributes.

</details>

## 4. The `dis` module: reading bytecode

### 4.1 Why read bytecode at all

Bytecode is the level where "one line of Python" turns into the separate steps the interpreter really takes. It answers questions the source hides: is `counter += 1` one step or several (several, which is why threads can interleave inside it, core.21)? Is this name local, global or a closure variable? Was `24 * 60 * 60` computed once at compile time (section 8)? You will not read bytecode every day, but once you can, you never have to guess what a line does.

### 4.2 Your first listing

The `dis` module ("disassembler") prints the bytecode of a function, a code object, or a source string:

```python
import dis

def area(w, h):
    result = w * h
    return result

dis.dis(area)
```
```text
  3           RESUME                   0

  4           LOAD_FAST_BORROW_LOAD_FAST_BORROW 1 (w, h)
              BINARY_OP                5 (*)
              STORE_FAST               2 (result)

  5           LOAD_FAST_BORROW         2 (result)
              RETURN_VALUE
```

*Python 3.14; other versions show different instruction names and layout.*

Each row is one instruction. The columns are:

1. **Source line number** (`3`, `4`, `5`), printed only on the first instruction of each line. Line 3 is the `def` line here, because the snippet starts with `import dis` and a blank line.
2. **Jump label** (`L1:` and so on), shown only on instructions that some jump can land on. This listing has no jumps.
3. **Operation name** (`opname`), such as `BINARY_OP`.
4. **Argument** (`arg`), a small integer. Its meaning depends on the instruction: an index into `co_varnames`, `co_consts` or `co_names`, an operator number, a jump distance, or a count.
5. **Argument meaning** (`argrepr`) in brackets: `dis` looks the integer up for you. `2 (result)` means "slot 2 of `co_varnames`, which is `result`". `5 (*)` means "operator number 5, which is multiplication".

Now read it as a story:

- `RESUME` marks the start of the function. It does nothing you can see (the interpreter uses it for bookkeeping). Skip it.
- Line 4: load `w` and `h` (one combined instruction in 3.14, explained in 4.4), multiply them, store the result in the local variable `result`.
- Line 5: load `result` and return it.

That is all a function call does: a handful of loads, an operation, a store, a load, a return.

### 4.3 Following the stack

The interpreter is a **stack machine**. Each frame (one running function call) has a small **value stack**. Load instructions push values on it; operations pop their inputs and push their result; store instructions pop a value and put it in a variable. Here is `area(3, 4)` step by step, with the top of the stack on the right:

```text
instruction                         stack after          locals after
-----------                         -----------          ------------
(start)                             []                   w=3  h=4
LOAD_FAST... (w, h)                 [3, 4]               w=3  h=4
BINARY_OP (*)                       [12]                 w=3  h=4
STORE_FAST result                   []                   w=3  h=4  result=12
LOAD_FAST... result                 [12]                 w=3  h=4  result=12
RETURN_VALUE                        []   -> returns 12
```

Three rules make every listing readable:

1. A value is always **pushed before it is used**. To compute `w * h`, both operands are pushed first, then the operation runs.
2. Operations **consume** their inputs. After `BINARY_OP` the two operands are gone and only the result is left.
3. At the end of each statement the stack is back to where it started (here empty). A statement that leaves a value it does not need throws it away with `POP_TOP`.

This order, operands first and operator last, is called **postfix** or **Reverse Polish notation**. `w * h` becomes `w h *`. `(a - b) * c + a` becomes `a b - c * a +`, which you can check against this listing:

```python
import dis

def calc(a, b, c):
    return (a - b) * c + a

dis.dis(calc)
```
```text
  3           RESUME                   0

  4           LOAD_FAST_BORROW_LOAD_FAST_BORROW 1 (a, b)
              BINARY_OP               10 (-)
              LOAD_FAST_BORROW         2 (c)
              BINARY_OP                5 (*)
              LOAD_FAST_BORROW         0 (a)
              BINARY_OP                0 (+)
              RETURN_VALUE
```

*Python 3.14; other versions differ.* The instructions come out in exactly the postfix order: `a b - c * a +`. The compiler produces it by walking the AST from section 2.3: for a `BinOp` node it emits code for the left child, then the right child, then the operator. Every expression, however complicated, becomes a sequence like this.

#### Predict the output 4.1

Without running it, write down the stack after each instruction of `calc(10, 4, 2)`. What is the largest number of values the stack ever holds?

```python
def calc(a, b, c):
    return (a - b) * c + a

print(calc(10, 4, 2))
print(calc.__code__.co_stacksize)
```

<details><summary>Answer</summary>

```text
LOAD a, b        [10, 4]
BINARY_OP -      [6]
LOAD c           [6, 2]
BINARY_OP *      [12]
LOAD a           [12, 10]
BINARY_OP +      [22]
RETURN_VALUE     returns 22
```

The stack never holds more than two values at once. The compiler works this out ahead of time and stores it in `co_stacksize`, so the interpreter can reserve exactly enough room when the frame is created. Running the code confirms both numbers:

```text
22
2
```

(The exact `co_stacksize` can be larger in some versions, because some instructions also push hidden helper values. The idea, a maximum depth computed at compile time, is the same in every version.)

</details>

### 4.4 Version noise: superinstructions, borrowing and caches

You saw `LOAD_FAST_BORROW_LOAD_FAST_BORROW 1 (w, h)` and may have wondered about that monster name. Three kinds of version-specific detail make listings look harder than they are:

- **Superinstructions.** When two instructions very often come in a row, CPython may fuse them into one to save a trip around the evaluation loop. `LOAD_FAST_LOAD_FAST` (3.13+) is simply "`LOAD_FAST` twice". Its argument packs both slot numbers into one integer, and the brackets show both names.
- **Borrowing.** `LOAD_FAST_BORROW` (3.14) is a `LOAD_FAST` that skips updating the reference count when the compiler can prove that is safe (you will meet reference counts in section 10). For reading purposes, it is `LOAD_FAST`.
- **Inline caches.** Some instructions are followed by hidden `CACHE` entries that the interpreter uses to remember things between runs (section 7). `dis` hides them unless you pass `show_caches=True`. You can spot them with `dis.dis(area, show_offsets=True)` (3.13+): each instruction takes 2 bytes, so offsets normally go 0, 2, 4, but in 3.14 the instruction after `BINARY_OP` (at offset 4) sits at offset 16. The bytes in between are `BINARY_OP`'s cache.

**The reading rule:** strip the version noise and read the base word. `LOAD_FAST_BORROW_LOAD_FAST_BORROW` is "load two locals". If you meet a name you do not know, the `dis` documentation for your exact Python version (docs.python.org, then pick the version) has a list of every instruction.

### 4.5 A cheat sheet that works for every version

Instruction names change between versions, but the **naming scheme** has been stable for a long time. Read the name in two parts, a verb and a kind:

| Verb | Meaning |
|---|---|
| `LOAD_...` | push a value onto the stack |
| `STORE_...` | pop a value and store it in a variable |
| `DELETE_...` | remove a variable (`del x`) |
| `BUILD_...` | pop several values and push a new tuple, list, dict, set or string |
| `BINARY_OP`, `COMPARE_OP`, `UNARY_...` | pop operands, push the result |
| `CALL` | call a function with `n` arguments from the stack, push the return value |
| `..._JUMP_...`, `JUMP_...` | continue at another instruction (if, loops, `and`/`or`) |
| `RETURN_VALUE` | pop the top value and return it to the caller |

| Kind (suffix of LOAD/STORE) | Where the name lives | Speed |
|---|---|---|
| `_FAST` | a local variable slot in the frame (array index) | fastest |
| `_CONST`, `_SMALL_INT` | a constant from `co_consts`, or a small int built into the instruction | fast |
| `_DEREF` | a cell, for closure variables (section 3.3) | fast |
| `_GLOBAL` | module globals, then built-ins (two dictionary lookups at worst) | slower |
| `_NAME` | module-level code and class bodies, where locals *are* a dictionary | slower |
| `_ATTR` | an attribute of the object on top of the stack (`obj.name`) | depends on the object |

And a short list of instructions you can usually **ignore** when reading for meaning: `RESUME`, `NOP`, `CACHE`, `NOT_TAKEN`, `PUSH_NULL`, `TO_BOOL`, `COPY_FREE_VARS`, `END_FOR`, `POP_ITER`. They are bookkeeping for the interpreter, not steps of your program.

### 4.6 Instructions as objects: `dis.get_instructions`

Printing is good for humans. For programs, `dis.get_instructions(func)` yields one `Instruction` object per instruction, with fields you can read:

```python
import dis

def greet(name):
    msg = "Hello, " + name.title()
    print(msg)
    return len(msg)

for ins in dis.get_instructions(greet):
    if ins.opname in ("LOAD_GLOBAL", "LOAD_ATTR", "STORE_FAST"):
        print(f"{ins.offset:>3} {ins.opname:<12} arg={ins.arg} argval={ins.argval!r}")
```
```text
  6 LOAD_ATTR    arg=1 argval='title'
 46 STORE_FAST   arg=1 argval='msg'
 48 LOAD_GLOBAL  arg=3 argval='print'
 70 LOAD_GLOBAL  arg=5 argval='len'
```

*Python 3.14; offsets and `arg` numbers differ by version.* The fields you can rely on in every version from 3.11 are `opname`, `arg`, `argval` (the looked-up value: the actual name or constant), `argrepr` (the text `dis` prints in brackets), and `offset`. `argval` is the useful one: for `LOAD_GLOBAL` it is the global's name, whatever integer encoding the version uses for `arg` (the encoding of `LOAD_GLOBAL`'s `arg` did change in 3.11, which is why `arg` here is `3` and `5`, not `1` and `2`). Fields about line numbers changed in 3.13, so avoid them if your code must run on several versions.

This is how you can finally answer Try it 3.2 properly: the globals are the `argval`s of the `LOAD_GLOBAL` instructions. That is a small but real static-analysis tool:

```python
import dis

def globals_used(func):
    return sorted({ins.argval for ins in dis.get_instructions(func)
                   if ins.opname == "LOAD_GLOBAL"})

def report(items):
    print(len(items), max(items), sorted(items).count(0))

print(globals_used(report))
```
```text
['len', 'max', 'print', 'sorted']
```

`count` does not appear: it is an attribute, looked up on the list that `sorted` returns. `print`, `len`, `max` and `sorted` are global lookups that end in the built-ins. (A complete version must also look inside nested functions, whose code objects sit in `co_consts`, section 3.3. Problem p014 does that.)

### 4.7 Stack effects

`dis.stack_effect(opcode, arg)` tells you how much an instruction changes the stack depth: `+1` for a push, `-1` for an instruction that pops two values and pushes one, and so on. `dis.opmap` maps names to opcode numbers:

```python
import dis

for name, arg in [("LOAD_CONST", 0), ("BINARY_OP", 0), ("STORE_FAST", 0), ("BUILD_LIST", 3)]:
    print(f"{name:<11} arg={arg}  effect={dis.stack_effect(dis.opmap[name], arg):+d}")
```
```text
LOAD_CONST  arg=0  effect=+1
BINARY_OP   arg=0  effect=-1
STORE_FAST  arg=0  effect=-1
BUILD_LIST  arg=3  effect=-2
```

*Effects of some instructions (especially calls) differ by version.* `BUILD_LIST 3` pops three values and pushes one list, so the net change is `-2`. Adding the effects in order gives the depth after each step; the largest depth reached is the `co_stacksize` from Predict 4.1. The mini interpreter in section 22 uses this same way of thinking.

### 4.8 Other ways to look

`dis.dis("x = a + 1")` disassembles a source string; `python3 -m dis myfile.py` disassembles a file from the terminal; `dis.show_code(func)` prints a summary of the code object (counts, flags, constants, names); and `dis.dis(func, adaptive=True)` shows specialised instructions (section 7).

#### Try it 4.2

Here is a listing (*Python 3.14*) of a function whose source has been hidden. Work out the source.

```text
  3           RESUME                   0

  4           LOAD_GLOBAL              1 (len + NULL)
              LOAD_FAST_BORROW         0 (items)
              CALL                     1
              LOAD_SMALL_INT           2
              BINARY_OP                2 (//)
              STORE_FAST               1 (half)

  5           LOAD_FAST_BORROW_LOAD_FAST_BORROW 1 (items, half)
              BINARY_OP               26 ([])
              RETURN_VALUE
```

<details><summary>Answer</summary>

```python
import dis

def middle(items):
    half = len(items) // 2
    return items[half]

print(middle([10, 20, 30, 40, 50]))
dis.dis(middle)
```
```text
30
  3           RESUME                   0

  4           LOAD_GLOBAL              1 (len + NULL)
              LOAD_FAST_BORROW         0 (items)
              CALL                     1
              LOAD_SMALL_INT           2
              BINARY_OP                2 (//)
              STORE_FAST               1 (half)

  5           LOAD_FAST_BORROW_LOAD_FAST_BORROW 1 (items, half)
              BINARY_OP               26 ([])
              RETURN_VALUE
```

Line 4 loads the global `len`, loads the local `items`, calls `len` with one argument, pushes `2`, applies `//` and stores into `half`. Line 5 loads `items` and `half` and applies the subscript operator `[]`. (In 3.14 subscripting is a `BINARY_OP`; in 3.11 to 3.13 it was a separate `BINARY_SUBSCR` instruction. The idea, pop the container and the index, push the item, is the same.) The function name is not in the listing, so `middle` is a guess; any name is fine.

</details>

## 5. A tour of the common instructions

The previous section taught you how to read. This one shows how each kind of Python statement turns into instructions, so you recognise the patterns. All listings are *Python 3.14; other versions differ in names but follow the same patterns.*

### 5.1 Names: why local variables are fast

The same statement compiles to different instructions depending on where the name lives. At module level, names live in a dictionary, so the compiler uses `LOAD_NAME`/`STORE_NAME`:

```python
import dis

dis.dis(compile("x = 10\ny = x + 1\n", "<module>", "exec"))
```
```text
  0           RESUME                   0

  1           LOAD_SMALL_INT          10
              STORE_NAME               0 (x)

  2           LOAD_NAME                0 (x)
              LOAD_SMALL_INT           1
              BINARY_OP                0 (+)
              STORE_NAME               1 (y)
              LOAD_CONST               1 (None)
              RETURN_VALUE
```

Inside a function, the compiler knows all the local names in advance (they are in `co_varnames`), so it gives each one a numbered **slot** in the frame and uses `LOAD_FAST`/`STORE_FAST` with the slot number. Reading a local is an array access: no hashing, no dictionary. A global is looked up by name in the module dictionary, and if it is not there, in the built-ins dictionary.

Notice also the last two instructions of the module code: `LOAD_CONST None` and `RETURN_VALUE`. Module code, like every function without a `return`, ends by returning `None`.

This difference is the real reason behind the old advice "put your loop inside a function":

```python
import time

module_code = compile("""
total = 0
for item in data:
    total += item
""", "<module-level>", "exec")

def in_function(data):
    total = 0
    for item in data:
        total += item
    return total

data = list(range(1_000_000))

start = time.perf_counter()
exec(module_code, {"data": data})
t_module = time.perf_counter() - start

start = time.perf_counter()
in_function(data)
t_function = time.perf_counter() - start

print(f"module-level loop: {t_module:.3f} s")
print(f"loop in function:  {t_function:.3f} s")
print(f"ratio: {t_module / t_function:.1f}x")
```
```text
module-level loop: 0.560 s
loop in function:  0.132 s
ratio: 4.2x
```

*Times are from the test machine and change on every run; compare the ratio, not the seconds.* The compiled module code runs with a dictionary as its namespace, exactly like a real module, so `total`, `item` and `data` are dictionary entries there. Inside `in_function` they are slots. The work is identical; only the kind of name changed.

A trap if you try this with `timeit`: `timeit` secretly wraps your statement inside a function before timing it, so "module-level" code timed with `timeit` is actually function code with fast locals, and you will measure no difference at all. Knowing the internals tells you why the benchmark lies. The size of the ratio varies a lot between Python versions, because 3.11+ also speeds up global lookups with caches (section 7). The direction does not.

### 5.2 Operators and comparisons

All binary operators (`+ - * / // % ** @ & | ^ << >>`, their in-place forms like `+=`, and in 3.14 also subscripting `[]`) share one instruction, `BINARY_OP`, whose argument says which operator. Comparisons (`< <= == != > >=`) use `COMPARE_OP`. Identity and membership have their own: `IS_OP` (`is`, `is not`) and `CONTAINS_OP` (`in`, `not in`).

What does `BINARY_OP (+)` actually do? Exactly what core.15 described for operators: it calls `type(left).__add__(left, right)`, and if that returns `NotImplemented`, tries `type(right).__radd__(right, left)`. The instruction is a **generic dispatcher**: it does not know in advance whether it will add two ints, two strings or two of your `Vector` objects. Keep this in mind for section 7, where CPython learns to specialise it.

### 5.3 Building containers, subscripts and attributes

```python
import dis

def pack(a):
    return a[0], [a, 1], {"k": a}, a.real

dis.dis(pack)
```
```text
  3           RESUME                   0

  4           LOAD_FAST_BORROW         0 (a)
              LOAD_SMALL_INT           0
              BINARY_OP               26 ([])
              LOAD_FAST_BORROW         0 (a)
              LOAD_SMALL_INT           1
              BUILD_LIST               2
              LOAD_CONST               1 ('k')
              LOAD_FAST_BORROW         0 (a)
              BUILD_MAP                1
              LOAD_FAST_BORROW         0 (a)
              LOAD_ATTR                0 (real)
              BUILD_TUPLE              4
              RETURN_VALUE
```

Read it with the stack in mind:

- `a[0]`: push `a`, push `0`, apply `[]`. One value (the item) is left.
- `[a, 1]`: push `a`, push `1`, then `BUILD_LIST 2` pops two values and pushes one new list.
- `{"k": a}`: push the key, push the value, `BUILD_MAP 1` pops one key/value pair and pushes a dict.
- `a.real`: push `a`, then `LOAD_ATTR real` replaces it with the attribute's value (running the full lookup algorithm from core.23).
- Finally `BUILD_TUPLE 4` collects the four values left on the stack into the returned tuple.

### 5.4 Calls and method calls

```python
import dis

def shout(word):
    print(word)
    return word.upper()

dis.dis(shout)
```
```text
  3           RESUME                   0

  4           LOAD_GLOBAL              1 (print + NULL)
              LOAD_FAST_BORROW         0 (word)
              CALL                     1
              POP_TOP

  5           LOAD_FAST_BORROW         0 (word)
              LOAD_ATTR                3 (upper + NULL|self)
              CALL                     0
              RETURN_VALUE
```

A function call pushes the **callable**, then the **arguments**, then runs `CALL n`, which pops `n` arguments and the callable and pushes the return value. Two details:

- **`+ NULL` and `NULL|self`.** The calling convention reserves one extra stack slot next to the callable. For a plain function call such as `print(word)`, it holds a `NULL` placeholder. For a method call `word.upper()`, `LOAD_ATTR` with the method flag looks up `upper` on the type and, if it is a plain function, pushes the **function** and **`word` itself** into the two slots, instead of creating a bound method object. `CALL` then passes `word` as the first argument. This is the shortcut promised in core.23 (section 9): in a direct call `obj.method()`, CPython usually never builds the bound method at all. You only get a bound-method object when you take `obj.method` without calling it right away.
- **`POP_TOP`.** `print(word)` is an expression statement: its result (`None`) is not used, so it is popped and discarded. The `return word.upper()` line has no `POP_TOP`, because its value is returned.

### 5.5 `if` statements and jumps

```python
import dis

def sign(x):
    if x > 0:
        return "pos"
    return "neg"

dis.dis(sign)
```
```text
  3           RESUME                   0

  4           LOAD_FAST_BORROW         0 (x)
              LOAD_SMALL_INT           0
              COMPARE_OP             148 (bool(>))
              POP_JUMP_IF_FALSE        3 (to L1)
              NOT_TAKEN

  5           LOAD_CONST               1 ('pos')
              RETURN_VALUE

  6   L1:     LOAD_CONST               2 ('neg')
              RETURN_VALUE
```

`COMPARE_OP` pops `x` and `0` and pushes `True` or `False` (in 3.14 the `bool(>)` text means it pushes a real `bool`). `POP_JUMP_IF_FALSE` pops that value: if it is false, execution **jumps** to label `L1`; otherwise it continues with the next instruction. (`NOT_TAKEN` is 3.14 bookkeeping for the jump; ignore it.) So an `if` statement is just "evaluate the condition, conditionally jump past the body". `elif` and `else` are more jumps of the same kind, and `and`/`or` are compiled as jumps too, which is how short-circuiting works: the right operand's instructions are simply jumped over.

### 5.6 Loops

A `for` loop uses two special instructions:

```python
import dis

def sum_squares(n):
    total = 0
    for i in range(n):
        total += i * i
    return total

dis.dis(sum_squares)
```
```text
  3           RESUME                   0

  4           LOAD_SMALL_INT           0
              STORE_FAST               1 (total)

  5           LOAD_GLOBAL              1 (range + NULL)
              LOAD_FAST_BORROW         0 (n)
              CALL                     1
              GET_ITER
      L1:     FOR_ITER                18 (to L2)
              STORE_FAST               2 (i)

  6           LOAD_FAST_BORROW_LOAD_FAST_BORROW 18 (total, i)
              LOAD_FAST_BORROW         2 (i)
              BINARY_OP                5 (*)
              BINARY_OP               13 (+=)
              STORE_FAST               1 (total)
              JUMP_BACKWARD           20 (to L1)

  5   L2:     END_FOR
              POP_ITER

  7           LOAD_FAST_BORROW         1 (total)
              RETURN_VALUE
```

- `GET_ITER` replaces the iterable (the `range` object) with an iterator by calling `iter()` on it (core.10).
- `FOR_ITER` calls `next()` on the iterator. If a value comes back, it is pushed and the loop body runs. If the iterator is exhausted, `FOR_ITER` jumps to the label after the loop (`L2` here).
- At the end of the body, `JUMP_BACKWARD` goes back to `FOR_ITER` for the next item.
- `END_FOR` and `POP_ITER` clean up the iterator afterwards (version-specific names).

The `for` statement is therefore exactly the iterator protocol from core.10, written in bytecode: `iter()` once, `next()` repeatedly, stop at exhaustion. A `while` loop is even simpler: test at the top, `POP_JUMP_IF_FALSE` out of the loop, body, `JUMP_BACKWARD` to the test.

### 5.7 Worked example: running `sum_squares(2)` by hand

This is the first learning outcome in action. Here is what the interpreter does for `sum_squares(2)`, with the stack after each instruction (top on the right; `it` is the range iterator; the hidden `NULL` slot is left out):

```text
line  instruction            stack after       locals                note
  4   LOAD_SMALL_INT 0       [0]               n=2
  4   STORE_FAST total       []                n=2 total=0
  5   LOAD_GLOBAL range      [range]                                 the built-in
  5   LOAD_FAST n            [range, 2]
  5   CALL 1                 [range(0, 2)]                           range(2) built
  5   GET_ITER               [it]                                    iter() called
  5   FOR_ITER               [it, 0]                                 next() -> 0
  5   STORE_FAST i           [it]              ... i=0
  6   LOAD_FAST total, i     [it, 0, 0]
  6   LOAD_FAST i            [it, 0, 0, 0]
  6   BINARY_OP *            [it, 0, 0]                              0 * 0
  6   BINARY_OP +=           [it, 0]                                 0 + 0
  6   STORE_FAST total       [it]              total=0 i=0
  6   JUMP_BACKWARD L1       [it]                                    back to FOR_ITER
  5   FOR_ITER               [it, 1]                                 next() -> 1
  5   STORE_FAST i           [it]              total=0 i=1
  6   ... same six steps ... [it]              total=1 i=1           0 + 1 * 1
  5   FOR_ITER               [it] -> jump L2                         next() raised StopIteration
  5   END_FOR, POP_ITER      []                                      iterator discarded
  7   LOAD_FAST total        [1]
  7   RETURN_VALUE           []                                      returns 1
```

Things worth noticing:

- The `range` lookup and the `range(2)` call happen **once**, before the loop. The six instructions of line 6 happen **once per item**. That is where a loop spends its time, and why moving work out of a loop body helps.
- The iterator `it` sits on the stack for the whole loop. That is how the loop remembers where it is.
- `total += i * i` is five steps (load, load, multiply, add, store). In a threaded program, a thread switch can happen between any two of them (core.21).

#### Predict the output 5.1

For each line in this function, say which variables are loaded with a **local** instruction, which with a **global** instruction, which with a **closure (deref)** instruction, and which names are **attributes**. Then check with the program, which groups the names by instruction kind (so it does not depend on exact opcode names).

```python
import dis

LIMIT = 10

def make_filter(words):
    banned = {"spam"}
    def keep(word):
        return word.lower() not in banned and len(word) < LIMIT
    return [w for w in words if keep(w)]

def kinds(func):
    inner = [c for c in func.__code__.co_consts if hasattr(c, "co_code")]
    code = inner[0]
    found = {}
    for ins in dis.get_instructions(code):
        for kind in ("FAST", "GLOBAL", "DEREF", "ATTR"):
            if ins.opname.startswith("LOAD_") and kind in ins.opname:
                found.setdefault(kind, set()).add(ins.argval)
    return {k: sorted(v) for k, v in sorted(found.items())}

print(kinds(make_filter))
```

<details><summary>Answer</summary>

```text
{'ATTR': ['lower'], 'DEREF': ['banned'], 'FAST': ['word'], 'GLOBAL': ['LIMIT', 'len']}
```

This shows the inner function `keep`. `word` is its parameter, so it is a local (`FAST`). `banned` belongs to the enclosing `make_filter` and is used by `keep`, so `keep` reads it through a cell (`DEREF`). `len` and `LIMIT` are not assigned anywhere in `keep` or `make_filter`, so they are global lookups; `len` is found in the built-ins only after the module dictionary misses. `lower` is an attribute name. (Since 3.12 list comprehensions are inlined into the enclosing function rather than compiled as separate functions, PEP 709, which is why `keep` is the only nested code object here. In 3.11 the comprehension would be a second one.)

</details>

### 5.8 Exceptions cost nothing until they happen

If you disassemble a function with `try`/`except`, you will find no "set up the handler" instruction at the start of the `try` block. Since Python 3.11 the compiler writes an **exception table** next to the bytecode instead ("if an exception happens between instruction A and instruction B, jump to handler H"), and `dis` prints it under the heading `ExceptionTable:` at the end of the listing. The happy path runs exactly as if the `try` were not there; the table is consulted only when something is raised. This design is called **zero-cost exceptions**, and it is one reason the EAFP style (core.07) is cheap in modern Python as long as exceptions are rare. Raising and catching is still much slower than an `if`, so do not use exceptions for the common case.

## 6. Frames and the evaluation loop

### 6.1 What a frame is

A code object says *what* to do. A **frame** is one *running execution* of a code object. Every time you call a function, CPython creates a frame that holds:

- the **code object** being run (`f_code`);
- the **instruction pointer**: which instruction comes next (exposed as `f_lasti`, and as the current line, `f_lineno`);
- the **local variable slots** and the **value stack** from section 4.3;
- references to the **globals** and **built-ins** dictionaries used for global lookups;
- a link to the **caller's frame** (`f_back`).

Call `a()`, which calls `b()`, which calls `c()`, and there are four frames: one for the module and one for each function, each pointing back to its caller. This chain *is* the call stack. When `c` returns, its frame is thrown away and the evaluation loop continues in `b`'s frame at the instruction after the call.

**A CPython detail (3.11+).** To make calls cheap, CPython stores frames in a compact internal form and creates a full Python **frame object** only when someone asks for one: a debugger, a traceback, or your code calling `sys._getframe()`. You will not notice this, except that it is one reason function calls got much faster in 3.11.

### 6.2 Walking the call stack

`sys._getframe()` returns the frame of the code that calls it. The leading underscore means "CPython-specific, use with care": other implementations may not support it. `inspect.currentframe()` is the documented wrapper (and returns `None` on implementations without frame support).

```python
import sys

def a():
    return b()

def b():
    return c()

def c():
    chain = []
    frame = sys._getframe()
    while frame is not None:
        chain.append(f"{frame.f_code.co_name}:{frame.f_lineno}")
        frame = frame.f_back
    return chain

print(a())
```
```text
['c:13', 'b:7', 'a:4', '<module>:17']
```

Each entry is a function name and the line that frame is currently on. `c` is on line 13 (the `chain.append` line, when the frame was read); `b` is paused at line 7, in the middle of calling `c`; `a` is paused at line 4; the module is paused at line 17, the `print(a())` call. This is exactly what a traceback shows, in the opposite order.

Logging libraries use this to find "which function called me"; `warnings.warn(..., stacklevel=2)` uses it to blame the caller instead of itself. In your own code, prefer passing information explicitly: code that inspects its caller is hard to read and test.

### 6.3 `f_locals`: looking at a frame's variables

A frame's local variables can be read by name through `frame.f_locals`; debuggers like `pdb` use it to show you variables. In Python 3.13+ it is a live `FrameLocalsProxy` (PEP 667); in 3.11 and 3.12 it is a plain `dict` snapshot. Writing through it behaves differently between versions, so treat it as **read-only**.

A warning about keeping frames. If you write `frame = inspect.currentframe()` inside a function, the frame refers to its local variables, and one of those variables (`frame`) refers back to the frame: a **reference cycle** (section 11). Write `del frame` when you are done, so the frame can be freed at once. Code that stores frames for later (in a list, on an object) keeps every local of every one of those frames alive, which is a real source of memory leaks.

### 6.4 Tracebacks are frame chains

When an exception escapes a function, Python records each frame it passes through. An exception's `__traceback__` attribute is a linked list of traceback entries, one per frame, each with the frame (`tb_frame`), the line (`tb_lineno`) and the next entry (`tb_next`):

```python
def parse(text):
    return int(text)

def load(rows):
    return [parse(r) for r in rows]

try:
    load(["1", "two"])
except ValueError as e:
    tb = e.__traceback__
    while tb is not None:
        print(tb.tb_frame.f_code.co_name, "line", tb.tb_lineno)
        tb = tb.tb_next
```
```text
<module> line 8
load line 5
parse line 2
```

That is the same information the printed traceback gives you (core.20): outermost frame first, the frame where the error happened last. The `traceback` module (`traceback.extract_tb(e.__traceback__)`) turns this chain into a friendlier list. And because each entry holds a **frame**, a stored exception keeps all those frames and their local variables alive. That is why Python deletes the name `e` automatically at the end of an `except ... as e:` block.

#### Predict the output 6.1

```python
import sys

def depth():
    count = 0
    frame = sys._getframe()
    while frame.f_back is not None:
        count += 1
        frame = frame.f_back
    return count

def wrapper(n):
    if n == 0:
        return depth()
    return wrapper(n - 1)

print(depth())
print(wrapper(0))
print(wrapper(3))
```

<details><summary>Answer</summary>

```text
1
2
5
```

`depth` counts how many frames lie *below* its own (it stops at the frame with no `f_back`, the module frame). Called from the module: one frame below it. Called from `wrapper(0)`: `wrapper` and the module, so 2. `wrapper(3)` calls itself down to `wrapper(0)`: four `wrapper` frames plus the module, so 5. Recursion really does stack up one frame per call, which is what `sys.getrecursionlimit()` (normally 1000) limits.

</details>

### 6.5 Generators keep their frame

An ordinary frame dies when its function returns. A **generator** is a function whose frame is *kept*: `yield` pauses the evaluation loop, saves the instruction pointer and the stack in the frame, and returns a value to the caller. `next()` resumes the same frame where it stopped (core.10). You can watch the frame through `gi_frame`:

```python
def countdown(n):
    while n > 0:
        yield n
        n -= 1

g = countdown(2)
print("created, line", g.gi_frame.f_lineno)
print(next(g), "paused at line", g.gi_frame.f_lineno, dict(g.gi_frame.f_locals))
print(next(g), "paused at line", g.gi_frame.f_lineno, dict(g.gi_frame.f_locals))
print(list(g), g.gi_frame)
```
```text
created, line 1
2 paused at line 3 {'n': 2}
1 paused at line 3 {'n': 1}
[] None
```

Before the first `next()`, the frame exists but has not started (it reports the `def` line). After each `next()`, it is paused at the `yield` with its locals intact: `n` really is remembered between calls, because the frame holding it is still alive. When the generator finishes, the frame is released and `gi_frame` becomes `None`. Coroutines (`async def`, core.21) work the same way, with `cr_frame`.

### 6.6 How debuggers hook in: `sys.settrace`

The evaluation loop can call a Python function of your choice on certain events: a function is entered, a new line starts, a function returns. `sys.settrace(func)` installs such a **trace function**. This is how `pdb` stops at breakpoints and how `coverage.py` knows which lines ran.

```python
import sys

def tracer(frame, event, arg):
    if frame.f_code.co_name == "work":
        if event == "line":
            print("  line", frame.f_lineno - frame.f_code.co_firstlineno)
        elif event == "return":
            print("  return", arg)
    return tracer

def work(x):
    y = x * 2
    if y > 5:
        y -= 5
    return y

sys.settrace(tracer)
work(4)
sys.settrace(None)
print("tracing off")
```
```text
  line 1
  line 2
  line 3
  line 4
  return 3
tracing off
```

The trace function is called with `"call"` when a frame starts; whatever it returns becomes the frame's local trace function, which then gets `"line"` and `"return"` events. Here lines are printed relative to the `def` line, so the output does not depend on where the function sits in the file. Always switch tracing off (`sys.settrace(None)`) when done, ideally in a `finally` block: a trace function slows every line of Python down a lot.

Since 3.12 there is also `sys.monitoring`, a newer and much faster event API that tools like debuggers and coverage are moving to. `sys.settrace` still works and is simpler for learning. Problem p032 builds a line tracer with it.

If you write a helper that switches tracing on and off, save `sys.gettrace()` first and put it back in a `finally` block instead of setting `None`: otherwise you silently switch off a debugger or coverage tool that was already tracing the program.

## 7. The specialising adaptive interpreter

### 7.1 The cost of being generic

Section 5.2 said `BINARY_OP (+)` is a generic dispatcher. Every time it runs, it must find out the types of both operands, look up the right `__add__`, check for `NotImplemented`, and so on. Most of that work gives the same answer every time: in a loop that adds integers, the operands are integers on the first iteration and on the millionth. The same is true for `LOAD_ATTR` on objects of one class, and `LOAD_GLOBAL` of a name that never changes.

### 7.2 The idea: rewrite instructions while running

Python 3.11 introduced the **specialising adaptive interpreter** (PEP 659). It works like this:

1. **Warm up.** When code has run a few times, the interpreter considers it "hot".
2. **Specialise.** It replaces a generic instruction **in place** with a specialised one for the types it has seen, for example `BINARY_OP` becomes `BINARY_OP_ADD_INT`, which only knows how to add two ints. It stores helpful facts in the instruction's inline `CACHE` entries (section 4.4): for `LOAD_GLOBAL`, which dictionary slot holds the name; for `LOAD_ATTR`, where the attribute sits in the object.
3. **Guard.** The specialised instruction first checks, very cheaply, that its assumption still holds ("are both operands exact ints?"). If yes, it takes the fast path.
4. **De-specialise.** If the guard fails, it falls back to the generic behaviour, and after enough failures goes back to the generic instruction, ready to specialise again for the new types.

The behaviour of your program never changes; only the speed does. That is why specialisation is called **transparent**.

### 7.3 Seeing it happen

`dis.dis(func, adaptive=True)` shows the instructions as they are *now*, after specialisation:

```python
import dis

def add(a, b):
    return a + b

for i in range(1000):
    add(i, i)
dis.dis(add, adaptive=True)

for i in range(1000):
    add(str(i), "x")
dis.dis(add, adaptive=True)
```
```text
  3           RESUME_CHECK             0

  4           LOAD_FAST_BORROW_LOAD_FAST_BORROW 1 (a, b)
              BINARY_OP_ADD_INT        0 (+)
              RETURN_VALUE
  3           RESUME_CHECK             0

  4           LOAD_FAST_BORROW_LOAD_FAST_BORROW 1 (a, b)
              BINARY_OP_ADD_UNICODE    0 (+)
              RETURN_VALUE
```

*Python 3.14; specialised names, and how quickly code warms up, differ between versions and may differ between runs.* After a thousand calls with ints, `BINARY_OP (+)` has become `BINARY_OP_ADD_INT`. After a thousand calls with strings, the guard failed, the instruction was de-specialised and re-specialised as `BINARY_OP_ADD_UNICODE` (CPython calls `str` objects "unicode" internally). `RESUME` became `RESUME_CHECK` as well.

### 7.4 What it means for your code

Specialisation rewards **type-stable** hot code: a loop where the same line always sees the same types, attributes are read from objects of the same class, and globals are not reassigned while the loop runs. Most normal code is already like this, which is why 3.11 ran typical programs about 25% faster than 3.10 with no code changes (figure from the Python 3.11 "What's New" document; your programs will vary).

What you should *not* do is contort your code for it. The rules from core.20 still apply: measure first, fix the algorithm first. The useful lesson is negative: a hot loop that mixes ints, floats and `Decimal`s on the same line, or that keeps adding new attributes to objects, defeats the specialiser and stays on the slow, generic path.

#### Try it 7.1

The loop below calls `mul` with a float pair, then an int pair, alternating. Will the interpreter keep flipping the instruction between an int version and a float version? Predict, then run it.

```python
import dis

def mul(a, b):
    return a * b

for i in range(2000):
    if i % 2:
        mul(i, 3)
    else:
        mul(1.5, 2.0)

for ins in dis.get_instructions(mul, adaptive=True):
    if ins.opname.startswith("BINARY_OP"):
        print(ins.opname)
```

<details><summary>Answer</summary>

```text
BINARY_OP_MULTIPLY_FLOAT
```

*Python 3.14 on the test machine; another version may show a different name, or the generic `BINARY_OP`.* It does not keep flipping. Re-specialising costs time, so after a guard fails the interpreter waits longer and longer before it tries again (an "exponential back-off"). Here one specialised form, for floats, happened to survive. Every call with ints fails its guard and takes the slow generic path for that one execution. So half the calls get the fast path and half pay the price of a failed guard. The program is still correct; type-stable code would simply be fast on every call.

</details>

## 8. Constant folding and other compile-time tricks

### 8.1 Doing arithmetic before the program runs

The compiler evaluates some expressions **at compile time** when all their parts are constants. This is called **constant folding**:

```python
def seconds_per_day():
    return 24 * 60 * 60

print(86400 in seconds_per_day.__code__.co_consts)
```
```text
True
```

*Exact contents of `co_consts` differ by version; checking membership is safe.* The multiplication happens once, when the file is compiled, not on every call. So writing `24 * 60 * 60` instead of a mysterious `86400` costs nothing at run time. Write the readable form.

### 8.2 Tuples, membership tests and sets

Three more folds that hold in all versions from 3.11:

- A **tuple of constants** like `(1, 2, 3)` becomes one constant, built once at compile time.
- In a **membership test** against a list display, `x in [1, 2, 3]`, the list can never be seen by anyone else, so the compiler stores a **tuple** instead: no list is built per call.
- `x in {1, 2, 3}` with a set display becomes a test against a constant **frozenset**.

```python
def check(x):
    small = (1, 2, 3)
    in_list = x in [1, 2, 3]
    in_set = x in {4, 5, 6}
    return small, in_list, in_set

consts = check.__code__.co_consts
print((1, 2, 3) in consts)
print(frozenset({4, 5, 6}) in consts)
print(any(isinstance(c, list) for c in consts))
```
```text
True
True
False
```

So the idiom `if command in {"quit", "exit", "q"}:` is both readable and efficient: the set is built once, and each test is a hash lookup (section 17).

### 8.3 What is not folded

Folding only happens when it is safe and cheap:

- **Anything with a name** is never folded, even `PI * 2` where `PI` is a module constant, because the name could be rebound before the function runs.
- **Large results** are not folded, so that a line like `"x" * 10**9` cannot blow up the size of your `.pyc` file. The exact size limits differ by version.
- **Calls** are never folded, not even `len("abc")`, because `len` could be replaced.

There is also some dead-code removal: the body of `if 0:` or `if False:` is not compiled at all, and running Python with `-O` removes `assert` statements and `if __debug__:` blocks. That is why `assert` must never be used for checks your program relies on (core.07).

#### Predict the output 8.1

Which of these values end up in `co_consts`? Answer True or False for each line.

```python
RATE = 2

def f(x):
    a = 60 * 60
    b = "ab" * 2
    c = RATE * 10
    d = x in ["red", "green"]
    return a, b, c, d

consts = f.__code__.co_consts
print(3600 in consts)
print("abab" in consts)
print(20 in consts)
print(("red", "green") in consts)
```

<details><summary>Answer</summary>

```text
True
True
False
True
```

`60 * 60` and `"ab" * 2` are made only of literals and small results, so they are folded to `3600` and `"abab"`. `RATE * 10` involves a name, so it is computed at run time and `20` is never a constant. The list in the membership test becomes the tuple `("red", "green")`.

</details>

## 9. Objects in memory

### 9.1 Every object starts with the same header

In CPython, every object is a block of memory (a C structure) that begins with the same two fields:

```text
  every object                     a list object, [10, 20]
 +--------------------+           +--------------------+
 | reference count    |           | reference count    |
 | pointer to type    |           | pointer to type ------> list
 +--------------------+           | size: 2            |
 | ... type-specific  |           | items: pointer --------> [ ptr | ptr | spare | spare ]
 |     data ...       |           | allocated: 4       |         |     |
 +--------------------+           +--------------------+         v     v
                                                                10    20
```

- The **reference count** says how many references point at this object (section 10).
- The **type pointer** says what kind of object this is. `type(x)` simply follows this pointer. This is why every value in Python "knows its type": the type is stored in the object, not in the variable. Variables are just names that point at objects (core.02).
- Objects whose length can vary (`int`, `tuple`, `str`) also store a size. A `list` stores its size, a pointer to a separate array of item pointers, and how many slots that array has room for (section 15).

### 9.2 `id()` is (in CPython) an address

`id(x)` returns a number that is unique among all objects **alive at the same time**. In CPython it is the object's memory address. Two consequences:

- `id(a) == id(b)` means `a is b`, *as long as both are alive*.
- After an object dies, its address can be **reused** for a new object. So `id([]) == id([])` is often `True` in CPython: the first list is created, its id taken, and it is freed at once; the second list may land in the same spot. The two lists were never alive together. Never store ids of objects you are not keeping alive.

### 9.3 `sys.getsizeof`: the shallow size

`sys.getsizeof(obj)` returns the number of bytes of the object's own memory block, plus any separate buffer it owns (like a list's item array):

```python
import sys

for value in [0, 2**30, 2**100, 1.5, "", "hello", (), [], [1, 2, 3], {}, set(), None]:
    print(f"{value!r:<35} {sys.getsizeof(value):>4} bytes")
```
```text
0                                     28 bytes
1073741824                            32 bytes
1267650600228229401496703205376       40 bytes
1.5                                   24 bytes
''                                    41 bytes
'hello'                               46 bytes
()                                    48 bytes
[]                                    56 bytes
[1, 2, 3]                             88 bytes
{}                                    64 bytes
set()                                216 bytes
None                                  16 bytes
```

*64-bit CPython 3.14. Every number here differs between versions and platforms; do not memorise them.* What *is* worth noticing:

- An int is not 4 or 8 bytes but around 28 or more, because of the header. Big ints grow: CPython stores them as a sequence of 30-bit "digits", so `2**100` needs more room than `2**30`.
- Even `None` takes 16 bytes: just the header.
- An empty `set` or `dict` is larger than an empty `list`, because hash tables reserve empty slots (section 16).

The big trap: **`getsizeof` does not follow references.** A list's size counts the pointers, not the objects they point to:

```python
import sys

names = ["x" * 1000, "y" * 1000, "z" * 1000]
print(sys.getsizeof(names))
print(sum(sys.getsizeof(s) for s in names))
```
```text
88
3123
```

*64-bit CPython 3.14.* The list itself is under 100 bytes; the three strings it points to are about 3,000. To measure a structure, you must walk it. Here is a **deep size** helper that counts each object once (two lists may share an object, and cycles must not loop forever):

```python
import sys

def deep_size(obj, seen=None):
    if seen is None:
        seen = set()
    if id(obj) in seen:
        return 0
    seen.add(id(obj))
    size = sys.getsizeof(obj)
    if isinstance(obj, dict):
        for k, v in obj.items():
            size += deep_size(k, seen) + deep_size(v, seen)
    elif isinstance(obj, (list, tuple, set, frozenset)):
        for item in obj:
            size += deep_size(item, seen)
    return size

shared = "x" * 1000
data = {"a": [shared, shared], "b": (1, 2)}
data["self"] = data
print(sys.getsizeof(data), deep_size(data))
```
```text
184 1546
```

*64-bit CPython 3.14; the numbers differ by version.* The shared string is counted once, and the dictionary that contains itself does not loop forever, because `seen` remembers ids (safe here, because every object in the structure stays alive during the walk). For real programs, use `tracemalloc` (core.20), which measures what was actually allocated, including memory that no `getsizeof` walk can see.

### 9.4 Instances, `__dict__` and `__slots__`

A normal instance stores its attributes in a separate dictionary, so its real cost is `getsizeof(obj) + getsizeof(obj.__dict__)`. `__slots__` (core.15) replaces the dictionary with fixed slots inside the instance. On 64-bit CPython 3.14, a two-attribute instance plus its `__dict__` measured 344 bytes, against 48 for the slotted version. Recent versions also share key tables between instances of one class, so the real gap can be smaller than that sum suggests; problem p021 measures it, and `tracemalloc` is the tool when it matters.

## 10. Reference counting

### 10.1 The rule

CPython's main memory manager is simple: every object counts the references to it.

- When a new reference to an object is made, its count goes **up** by one. (In the C source this is `Py_INCREF`.)
- When a reference goes away, the count goes **down** by one (`Py_DECREF`).
- When the count reaches **zero**, nobody can reach the object any more, so it is **freed immediately**. Freeing it removes *its* references to other objects, which may bring their counts to zero too, and so on, like dominoes.

What makes and removes references?

| Makes a reference | Removes it |
|---|---|
| binding a name: `x = obj` | rebinding the name: `x = other`, or `del x` |
| putting it in a container: `lst.append(obj)`, `d[k] = obj` | removing it from the container, or the container dying |
| storing it as an attribute: `self.item = obj` | rebinding or deleting the attribute, or the owner dying |
| passing it as an argument (the parameter is a local name) | the function returning (its locals go away) |

### 10.2 Watching counts with `sys.getrefcount`

`sys.getrefcount(obj)` returns the current count. It is always at least one higher than you expect, because passing `obj` to `getrefcount` creates a temporary reference. Exact numbers also vary between versions (3.14 avoids some reference updates entirely, section 4.4's "borrowing"), so watch the **changes**, on a **freshly created** object:

```python
import sys

thing = object()
base = sys.getrefcount(thing)

box = [thing]
print("in a list:   +", sys.getrefcount(thing) - base)
table = {"key": thing}
print("in a dict:   +", sys.getrefcount(thing) - base)
del box
print("list gone:   +", sys.getrefcount(thing) - base)
table.clear()
print("dict cleared:+", sys.getrefcount(thing) - base)
```
```text
in a list:   + 1
in a dict:   + 2
list gone:   + 1
dict cleared:+ 0
```

Each container holding `thing` adds one; removing it takes one away. Absolute values like `2` or `3` are CPython-version details, so tests in this module only ever check differences like these.

### 10.3 `del` removes a name, not an object

A very common misunderstanding: `del x` does **not** destroy the object. It removes the **name** `x`, which removes one reference. The object dies only if that was the last one. To see the moment an object is freed, here is a small probe class with a `__del__` method, which CPython calls just before freeing an object. (Use `__del__` only as a probe like this; section 13 explains why real code should not rely on it.)

```python
class Probe:
    def __init__(self, name):
        self.name = name
    def __del__(self):
        print("  freed", self.name)

a = Probe("A")
b = a
print("del a")
del a
print("del b")
del b
print("rebind c")
c = Probe("C1")
c = Probe("C2")
print("list dies")
items = [Probe("L1"), Probe("L2")]
items = None
print("end of script")
```
```text
del a
del b
  freed A
rebind c
  freed C1
list dies
  freed L2
  freed L1
end of script
  freed C2
```

- `del a` printed nothing: `b` still refers to the object. `del b` removed the last reference, and the object was freed **at that exact moment**.
- Rebinding `c` dropped the last reference to `C1`, so `C1` was freed as soon as the new object was bound.
- Setting `items = None` freed the list, which dropped its references to `L1` and `L2`: the domino effect. (A dying list releases its items from the end, which is why `L2` went first. That order is a detail, not a rule.)
- `C2` was freed at the very end, when the interpreter shut down and cleared the module's names.

This promptness is a real CPython feature: memory comes back the moment you are done with an object, and you can predict exactly when. But it is not a language promise, as section 13 shows.

#### Predict the output 10.1

```python
class Probe:
    def __init__(self, name):
        self.name = name
    def __del__(self):
        print("freed", self.name)

def make():
    temp = Probe("temp")
    keep = Probe("keep")
    return keep

result = make()
print("after make")
holder = {"x": Probe("x")}
holder["x"] = Probe("y")
print("after replace")
result = None
print("done")
```

<details><summary>Answer</summary>

```text
freed temp
after make
freed x
after replace
freed keep
done
freed y
```

- When `make` returns, its local names disappear. `temp` had no other reference, so it is freed during the return. `keep` survives because the returned reference is bound to `result`.
- Replacing `holder["x"]` drops the dictionary's reference to `x`, freeing it the moment the new value is stored.
- `result = None` frees `keep`.
- `y` is still in `holder`, so it is freed only at shutdown, after `done`.

</details>

### 10.4 Immortal objects (3.12+)

Some objects are used by nearly every program: `None`, `True`, `False`, small integers, the empty tuple, many common strings. Updating their counts millions of times a second costs time, and in programs that share memory between processes or threads it forces needless writes to memory. Since Python 3.12 (PEP 683), these objects are **immortal**: their reference count is set to a special huge value and is never changed, and they are never freed.

```python
import sys

print(sys.getrefcount(None))
print(sys.getrefcount(7))
```
```text
3221225472
3221225472
```

*64-bit CPython 3.14; 3.11 shows ordinary (still large) counts.* That number is not "three billion references"; it is a marker meaning "immortal". This is one more reason never to write code or tests that depend on an absolute reference count.

### 10.5 Strengths and weaknesses of reference counting

Strengths: memory is returned **immediately and predictably**; there are no long pauses; and the idea is simple enough to follow by hand, as you just did.

Weaknesses:

- **Cost on every operation.** Every assignment, every argument passed, every container update changes a counter in memory.
- **Thread safety.** Two threads changing the same count at once could corrupt it. Protecting the counts is the main reason the GIL exists (core.21; section 19 shows how the free-threaded build solves it differently).
- **Cycles.** Reference counting alone can never free objects that refer to each other. That is the subject of the next section, and the second learning outcome.

## 11. Reference cycles and the garbage collector

### 11.1 The problem: counts that never reach zero

Take two objects that point at each other:

```python
import gc

class Node:
    def __init__(self, name):
        self.name = name
        self.other = None
    def __del__(self):
        print("  freed", self.name)

gc.disable()   # keep an automatic collection from running in the middle of the demo

a = Node("A")
b = Node("B")
a.other = b
b.other = a
print("deleting the names")
del a, b
print("names gone, nothing freed yet")
print("collecting")
found = gc.collect()
print("collector found something:", found > 0)
gc.enable()
```
```text
deleting the names
names gone, nothing freed yet
collecting
  freed A
  freed B
collector found something: True
```

Follow the counts. After the four assignments, `A` has two references (the name `a` and `b.other`), and so does `B`. `del a, b` removes the names, so each count drops to **one**: `A` is still referred to by `B.other`, and `B` by `A.other`.

```text
 before del                         after del a, b
   a ---> [A] --other--> [B] <--- b        [A] --other--> [B]
            ^                |               ^                |
            +-----other------+               +-----other------+
   A: 2 refs   B: 2 refs                A: 1 ref   B: 1 ref   (no names left!)
```

Nothing in the program can reach `A` or `B` any more, yet neither count is zero, and reference counting only frees objects whose count is zero. **Each object keeps the other alive.** Without help, this memory would be lost until the program ends. This is a **reference cycle**, and it is the reason CPython has a second mechanism: the **cyclic garbage collector** in the `gc` module. `gc.collect()` found the two objects and freed them. (Which of the two is freed first is not specified, so do not rely on the order. The exact number `gc.collect()` returns also differs between versions; it counts every unreachable object found, which can include internal helper objects.)

### 11.2 Cycles are everywhere

You rarely build cycles on purpose, but they appear naturally:

- a **tree with parent pointers**: each child refers to its parent, and the parent's `children` list refers to the child;
- a **doubly linked list**: each node points to the next and the previous one;
- an object that stores **its own bound method**, for example `self.on_click = self.handle`: the bound method refers back to `self` (core.23);
- an **exception stored in a local variable** of a function its traceback passes through: exception → traceback → frame → locals → exception (section 6.4);
- a **frame stored in one of its own locals**, as in section 6.3;
- a list or dict that contains **itself**.

### 11.3 How the collector finds cycles

The collector cannot just look for objects with count zero; the whole point is that garbage in a cycle has non-zero counts. Instead it asks a different question: **which references come from outside the group of objects I am examining?**

1. **Only containers are tracked.** Objects that cannot refer to other objects (ints, floats, strings) can never be part of a cycle, so the collector ignores them. Lists, dicts, instances, functions and so on are tracked. `gc.is_tracked([])` is `True`; `gc.is_tracked(1)` is `False`.
2. **Copy the counts.** For every tracked object, copy its reference count into a scratch number, `gc_refs`.
3. **Subtract internal references.** For every tracked object, look at each object it refers to (each type knows how to list its references), and subtract 1 from that object's `gc_refs`.
4. **What is left came from outside.** An object whose `gc_refs` is still above zero is referred to by something that is not a tracked container: a local variable in a running frame, a module's name, a C extension. Such objects are definitely alive.
5. **Mark everything reachable from the live ones** as alive too.
6. **Everything else is garbage.** The collector breaks the references inside the garbage (it clears the objects' contents), the counts fall to zero, and ordinary reference counting frees them.

The idea fits in a few lines of Python. Here objects are just names, `refcount` gives each object's real count, and `edges` says who refers to whom:

```python
def find_garbage(refcount, edges):
    gc_refs = dict(refcount)                      # step 2
    for source, targets in edges.items():         # step 3
        for target in targets:
            gc_refs[target] -= 1
    alive = set()
    stack = [obj for obj, n in gc_refs.items() if n > 0]   # step 4
    while stack:                                  # step 5
        obj = stack.pop()
        if obj not in alive:
            alive.add(obj)
            stack.extend(edges.get(obj, []))
    return sorted(set(refcount) - alive)          # step 6

# A <-> B: a cycle nobody else refers to.
# C <-> D: a cycle, but a variable also refers to C.
# E refers to itself only.
refcount = {"A": 1, "B": 1, "C": 2, "D": 1, "E": 1}
edges = {"A": ["B"], "B": ["A"], "C": ["D"], "D": ["C"], "E": ["E"]}
print(find_garbage(refcount, edges))
```
```text
['A', 'B', 'E']
```

Trace it: after subtracting internal references, `gc_refs` is `A 0, B 0, C 1, D 0, E 0`. Only `C` has a reference from outside (the variable). Starting from `C`, the walk marks `C` and `D` alive. `A`, `B` and `E` are garbage. Notice that `D` had `gc_refs` 0 but survived, because it is **reachable** from a live object. Being in a cycle does not make an object garbage; being in a cycle that nothing outside can reach does.

That is the answer to the second learning outcome in one sentence: **reference counting only sees how many references an object has, not where they come from, so objects that refer to each other keep each other's counts above zero forever; the garbage collector looks at the whole group, subtracts the references that come from inside it, and frees the objects that nothing outside the group can reach.**

#### Try it 11.1

Use `find_garbage` on this situation: a parent object `P` is referred to by a variable; `P` refers to its children `X` and `Y`; each child refers back to `P`; and a detached pair `M <-> N` was dropped by the program. Write the `refcount` and `edges` dictionaries (count every reference, including the variable), predict the result, then run it. What changes if the variable is deleted?

<details><summary>Answer</summary>

```python
def find_garbage(refcount, edges):
    gc_refs = dict(refcount)
    for source, targets in edges.items():
        for target in targets:
            gc_refs[target] -= 1
    alive = set()
    stack = [obj for obj, n in gc_refs.items() if n > 0]
    while stack:
        obj = stack.pop()
        if obj not in alive:
            alive.add(obj)
            stack.extend(edges.get(obj, []))
    return sorted(set(refcount) - alive)

edges = {"P": ["X", "Y"], "X": ["P"], "Y": ["P"], "M": ["N"], "N": ["M"]}
with_variable = {"P": 3, "X": 1, "Y": 1, "M": 1, "N": 1}
print(find_garbage(with_variable, edges))
without_variable = {"P": 2, "X": 1, "Y": 1, "M": 1, "N": 1}
print(find_garbage(without_variable, edges))
```
```text
['M', 'N']
['M', 'N', 'P', 'X', 'Y']
```

`P` has three references: the variable, `X` and `Y`. After subtracting the two internal ones, one remains (the variable), so the whole family is alive, and only the detached pair is garbage. Once the variable is gone, `P`'s count is 2, both come from inside, and the whole tree becomes garbage: a parent-child tree with back pointers can **only** be freed by the collector. Section 12.4 shows how a weak reference avoids that.

</details>

### 11.4 When the collector runs: generations

Examining every container in the program takes time, so the collector does not run constantly. It runs automatically when the number of new container objects created (minus those freed) passes a **threshold**. And it uses a fact observed in almost every program: **most objects die young.** A temporary list in a loop lives for microseconds; a configuration object lives for the whole run.

So the collector sorts objects into **generations**. New objects start in the young generation, which is collected often and cheaply. Objects that survive a collection move to an older generation, which is examined much less often. Until Python 3.13 there were three generations (0, 1 and 2). **Python 3.14 introduced an incremental collector** with a young and an old generation, where the old generation is examined a slice at a time, so that one collection never pauses the program for long (from the 3.14 "What's New" document).

```python
import gc

print(gc.isenabled())
print(gc.get_threshold())
print(gc.get_count())
```
```text
True
(2000, 10, 0)
(1972, 0, 0)
```

*64-bit CPython 3.14; thresholds and counts differ between versions, and between runs.* `get_threshold()` gives the trigger values; `get_count()` shows how close each generation is to its threshold right now. Treat both as diagnostics, never as fixed numbers.

### 11.5 Useful `gc` functions

| Function | What it does |
|---|---|
| `gc.collect()` | run a full collection now; returns how many unreachable objects it found |
| `gc.disable()`, `gc.enable()`, `gc.isenabled()` | switch automatic collection off and on (reference counting is not affected) |
| `gc.is_tracked(obj)` | is this object watched by the collector? |
| `gc.get_referents(obj)` | the objects that `obj` refers to |
| `gc.get_referrers(obj)` | the tracked objects that refer to `obj` (slow: scans everything; for debugging only) |
| `gc.freeze()` | move all current objects to a permanent generation that is never examined (used before `fork`) |

`get_referrers` is the classic leak-hunting tool: "who is keeping this object alive?" In a real hunt it also returns frames, module dictionaries and other internals, so you filter the result and follow the chain one step at a time. `get_referents` goes the other way, and is enough to build a small object-graph explorer (problems p019 and p033).

### 11.6 Should you ever disable the collector?

Turning off automatic collection with `gc.disable()` removes the collector's pauses. Reference counting still frees everything that is not in a cycle, so a program that creates few cycles barely notices. Some large services have done this, or raised the thresholds, to reduce pauses or to avoid memory being copied in forked worker processes. The price: every cycle your code (or any library) creates is now leaked until you call `gc.collect()` yourself. For normal programs the default settings are right. If you suspect the collector is slowing you down, measure first (core.20), then consider raising thresholds with `gc.set_threshold()` before disabling it.

### 11.7 Why not only a tracing collector?

Java, Go, JavaScript engines and PyPy use only a **tracing** garbage collector: from time to time they find everything reachable and free the rest, with no reference counts at all. CPython combines both: reference counting for prompt, predictable freeing of most objects, and a tracing cycle collector as the backup. The practical consequence for you: on CPython an object without cycles dies the moment its last reference goes; **on PyPy it dies whenever the collector next runs**, which could be much later. Code that relies on prompt freeing ("the file is closed when the variable goes out of scope") works on one and fails on the other. The language-level fix, always, is to release resources explicitly with `with` (core.12).

#### Predict the output 11.2

Each object records its own death in a shared list (so the printing order inside one collection does not matter). Predict the three printed lists.

```python
import gc

log = []

class Item:
    def __init__(self, name):
        self.name = name
        self.ref = None
    def __del__(self):
        log.append(self.name)

gc.disable()
solo = Item("solo")
x, y = Item("x"), Item("y")
x.ref, y.ref = y, x
me = Item("me")
me.ref = me

del solo, x, y, me
print(sorted(log))
gc.collect()
print(sorted(log))
gc.enable()
keeper = Item("keeper")
keeper.ref = Item("child")
del keeper
print(sorted(log))
```

<details><summary>Answer</summary>

```text
['solo']
['me', 'solo', 'x', 'y']
['child', 'keeper', 'me', 'solo', 'x', 'y']
```

- `solo` has no cycle, so `del solo` frees it at once by reference counting.
- `x`/`y` and the self-referencing `me` are cycles. Deleting the names leaves each count at 1 or more, so nothing happens until `gc.collect()`, which frees all three.
- `keeper` refers to `child`, but `child` does not refer back. No cycle: `del keeper` frees `keeper`, which drops the only reference to `child`, which is freed too. No collector needed.

</details>

## 12. `weakref`: references that do not keep objects alive

### 12.1 The idea

Sometimes you want to *refer* to an object without *keeping it alive*: a cache that should forget an image nobody uses, a child that needs to find its parent, an event system that should not keep every listener alive forever. A **weak reference** does exactly this: it points at an object **without adding to its reference count**.

```python
import weakref

class Image:
    def __init__(self, name):
        self.name = name

img = Image("cat.png")
ref = weakref.ref(img)
print(ref() is img, ref().name)
del img
print(ref())
```
```text
True cat.png
None
```

Calling the weak reference, `ref()`, returns the object while it is alive, and `None` after it has been freed. Always call it once, store the result in a local name, and check for `None`: the object might die between two calls.

Not every object can be weakly referenced. Instances of your own classes can (unless they use `__slots__` without `"__weakref__"`, core.15), and so can functions, sets and classes. Instances of `int`, `str`, `tuple`, `list` and `dict` cannot, to keep those very common objects small; `weakref.ref(5)` raises `TypeError`. A subclass such as `class MyList(list): pass` can be weakly referenced.

### 12.2 Weak containers

The `weakref` module offers containers built on weak references:

- **`WeakValueDictionary`**: values are held weakly. When a value dies, its entry disappears. Perfect for a **cache** of objects that are also used elsewhere: the cache never keeps an object alive by itself.
- **`WeakKeyDictionary`**: keys are held weakly. Use it to attach extra data to objects you do not own, without keeping them alive (core.23 used it for descriptor storage).
- **`WeakSet`**: a set of weakly held objects, for example "all currently open windows".

```python
import gc
import weakref

class Image:
    def __init__(self, name):
        self.name = name

cache = weakref.WeakValueDictionary()

def load(name):
    image = cache.get(name)
    if image is None:
        print("  loading", name)
        image = Image(name)
        cache[name] = image
    return image

a = load("cat.png")
b = load("cat.png")
print(a is b, list(cache.keys()))
del a, b
gc.collect()   # not needed on CPython here, but makes the example safe everywhere
print(list(cache.keys()))
load("cat.png")
```
```text
  loading cat.png
True ['cat.png']
[]
  loading cat.png
```

The second `load` was served from the cache. Once the program dropped its last strong reference, the entry vanished on its own, so the next `load` reloaded the image. A normal `dict` would have kept every image ever loaded alive until the program ended: a classic slow memory leak.

### 12.3 `weakref.finalize`: cleanup without `__del__`

`weakref.finalize(obj, func, *args)` registers `func(*args)` to be called **once**, when `obj` is freed, or at interpreter exit if it is still alive then. You can also call the finalizer yourself; it runs only the first time:

```python
import weakref

class TempDir:
    def __init__(self, path):
        self.path = path
        self._cleanup = weakref.finalize(self, print, "  removing", path)
    def close(self):
        self._cleanup()

t = TempDir("/tmp/job1")
del t
u = TempDir("/tmp/job2")
u.close()
u.close()
print("alive?", u._cleanup.alive)
```
```text
  removing /tmp/job1
  removing /tmp/job2
alive? False
```

Notice that the cleanup function receives `path`, **not** `self`. If it held a reference to `self`, the object could never die. This is the main advantage over `__del__` (section 13): the cleanup code is separate from the object, cannot bring the object back to life, and runs at most once.

### 12.4 Breaking cycles with weak references

Section 11.2 listed trees with parent pointers as a typical cycle. If the child holds its parent through a weak reference, there is no cycle, and reference counting frees the tree at once, with no collector needed:

```python
import gc
import weakref

class TreeNode:
    def __init__(self, name, parent=None):
        self.name = name
        self.children = []
        self._parent = weakref.ref(parent) if parent is not None else None
        if parent is not None:
            parent.children.append(self)
    @property
    def parent(self):
        return self._parent() if self._parent is not None else None
    def __del__(self):
        print("  freed", self.name)

gc.disable()
root = TreeNode("root")
leaf = TreeNode("leaf", root)
print(leaf.parent.name)
del leaf
print("deleting root")
del root
print("no gc.collect() was needed")
gc.enable()
```
```text
root
deleting root
  freed root
  freed leaf
no gc.collect() was needed
```

The parent owns its children (strong references, going down); each child only *knows about* its parent (weak reference, going up). Ownership flows one way, so there is no cycle. The `property` from core.14 hides the weak reference behind a normal-looking attribute.

### 12.5 `WeakMethod`: weak references to bound methods

Bound methods are created fresh on every attribute access (core.23), so a plain weak reference to one dies immediately, because nobody else holds that particular bound-method object. `weakref.WeakMethod` stores the function and a weak reference to the instance separately, and rebuilds the bound method when called:

```python
import weakref

class Button:
    def click(self):
        return "clicked"

button = Button()
plain = weakref.ref(button.click)
smart = weakref.WeakMethod(button.click)
print(plain(), smart()())
del button
print(smart())
```
```text
None clicked
None
```

Event systems use `WeakMethod` so that subscribing an object's method does not keep the object alive forever. Problem p024 fixes a leaky event system this way.

#### Predict the output 12.1

```python
import gc
import weakref

class User:
    def __init__(self, name):
        self.name = name

alice, bob = User("alice"), User("bob")
online = weakref.WeakSet([alice, bob])
by_name = weakref.WeakValueDictionary({"alice": alice, "bob": bob})
friends = [bob]

del alice, bob
gc.collect()
print(len(online), sorted(by_name))
friends.clear()
gc.collect()
print(len(online), sorted(by_name))
```

<details><summary>Answer</summary>

```text
1 ['bob']
0 []
```

Weak containers never keep anything alive. After the names are deleted, `alice` has no strong references left and disappears from both containers. `bob` survives because the ordinary list `friends` still holds him. Clearing the list removes the last strong reference, and `bob` vanishes too.

</details>

## 13. `__del__` and finalizers

### 13.1 When `__del__` runs, and when it does not

`__del__` is called just before CPython frees an object. Section 10 used it as a probe, and it showed that on CPython it runs promptly when the last reference disappears. But the rules are weaker than they look:

- **On CPython, objects in cycles** are only finalized when the garbage collector runs (section 11), which could be much later. (Since Python 3.4, PEP 442, the collector *does* call `__del__` on objects in cycles and then frees them. Before that, such cycles were never freed at all.)
- **On PyPy and other implementations**, `__del__` runs whenever their tracing collector gets to the object: maybe seconds later, maybe never in a short program.
- **At interpreter exit**, objects that are still alive may or may not be finalized, and by then the modules they need (even `print`) may already be partly torn down.
- **Exceptions raised inside `__del__` are not propagated.** CPython prints an "Exception ignored" warning to stderr and carries on, so a bug in `__del__` is easy to miss.
- `__del__` can **resurrect** the object by storing `self` somewhere. CPython calls `__del__` at most once per object, so a resurrected object will not get a second call.

### 13.2 The rules to follow

1. **Release resources explicitly** with a context manager: `with open(...)`, `with conn:`, or your own `__enter__`/`__exit__` (core.12). This is the only approach the *language* guarantees.
2. Use **`weakref.finalize`** (section 12.3) as a safety net for objects that may not be closed properly. It is more reliable than `__del__`: it runs once, it cannot resurrect, and it also runs at interpreter exit.
3. Use `__del__` only for debugging or last-resort logging, and keep it tiny.

#### Try it 13.1

This function works on CPython but is a bug according to the language rules. What is the bug, why does CPython hide it, and what is the fix?

```python
def save(path, text):
    open(path, "w").write(text)
```

<details><summary>Answer</summary>

The file is never closed explicitly. On CPython, the file object's reference count drops to zero as soon as the line ends, so it is freed, which flushes and closes the file immediately: the bug is hidden. On PyPy the file object lives until the next garbage collection, so the text may stay in a buffer, other code may read an empty file, and a long-running program may run out of file handles. The fix relies only on the language: `with open(path, "w") as f: f.write(text)`, or `pathlib.Path(path).write_text(text)`, which closes the file for you.

</details>

## 14. Interning and caches

### 14.1 The small-int cache

Creating an int object for every `0`, `1` or loop counter would be wasteful, so CPython creates the integers from **-5 to 256** once, at start-up, and reuses them. (Since 3.12 they are also immortal, section 10.4.) Any computation whose result falls in that range returns the cached object; larger results create new objects:

```python
small_a, small_b = int("100"), int("100")
big_a, big_b = int("1000"), int("1000")
print(small_a == small_b, small_a is small_b)
print(big_a == big_b, big_a is big_b)
print(int("-5") is int("-5"), int("-6") is int("-6"))
```
```text
True True
True False
True False
```

The values are computed at run time with `int("...")` on purpose. If you write the literal `1000` twice in the same file, the compiler may store **one** constant and use it twice (section 8), and then `is` says `True`. That depends on how the code was compiled (a file, the REPL, two different functions), and it changed between versions. This is exactly why `is` must never be used to compare numbers.

### 14.2 String interning

**Interning** means keeping one shared copy of each distinct string value in a table, so equal strings can be compared by address. CPython automatically interns the names in your program (variable, function, attribute and keyword names) and many short string constants that look like identifiers. Strings built while the program runs are usually **not** interned, but `sys.intern(s)` returns the shared copy:

```python
import sys

a = "".join(["he", "llo"])
b = "".join(["hel", "lo"])
print(a == b, a is b)
print(sys.intern(a) is sys.intern(b))
```
```text
True False
True
```

Why bother? Attribute lookup is dictionary lookup with string keys (core.23). When the key you search for is the *same object* as the key stored in the dictionary, the comparison succeeds by address without comparing characters. Since attribute and variable names are interned, lookups in `obj.__dict__` and module globals are fast. You can call `sys.intern` yourself when a program keeps millions of copies of the same few strings (for example, the column names of a big CSV): equal strings then share memory and compare faster.

### 14.3 `is` versus `==`, once and for all

- `==` asks "do these have equal **values**?" It calls `__eq__`, and is what you want almost always.
- `is` asks "are these the **same object**?" It compares addresses.
- Use `is` only for **singletons**: `None`, `True`, `False`, `NotImplemented`, `Ellipsis`, and your own sentinel objects (`MISSING = object()`). Python promises there is only one of each.
- Results of `is` on ints, strings, tuples and floats depend on caches, interning and constant folding, all of which are CPython details. Since Python 3.8 the compiler even emits a `SyntaxWarning` when you write something like `x is 1000`.

#### Predict the output 14.1

```python
import sys

def make(n):
    return n * 2

x = make(64)
y = make(64)
p = make(600)
q = make(600)
s = "-".join(["a", "b"])
t = "-".join(["a", "b"])
print(x is y, p is q, p == q)
print(s is t, s == t, sys.intern(s) is sys.intern(t))
```

<details><summary>Answer</summary>

```text
True False True
False True True
```

`128` is inside the small-int cache, so both calls return the same cached object. `1200` is outside it, so each call creates a new int: equal values, different objects. The two `join` results are built at run time and are not interned, so they are different objects until `sys.intern` maps both to one shared copy. Every `==` is `True`: values are what matter.

</details>

## 15. How `list` works

### 15.1 A dynamic array of pointers

A `list` is a **dynamic array**: one contiguous block of memory holding **pointers** to the item objects (the picture in section 9.1). Because all slots are the same size, the address of item `i` is "start + i × 8 bytes" (on 64-bit), so `lst[i]` takes the same time for any `i`: O(1). The list also stores how many items it has (`len`) and how many slots the block has room for (its **capacity**).

### 15.2 Over-allocation and amortised O(1) append

If the block had exactly as many slots as items, every `append` would have to allocate a bigger block and copy all the pointers: O(n) per append, O(n²) to build a list. Instead, when the block is full, CPython allocates **extra room**, proportional to the current size (roughly 12.5% more plus a little, in recent versions). You can see the capacity jumps with `getsizeof`:

```python
import sys

points = []
lst = []
previous = sys.getsizeof(lst)
for i in range(100):
    lst.append(i)
    size = sys.getsizeof(lst)
    if size != previous:
        points.append(len(lst))
        previous = size
print(points)
```
```text
[1, 5, 9, 17, 25, 33, 41, 53, 65, 77, 93]
```

*64-bit CPython 3.14; the exact growth pattern differs by version.* In 100 appends, the block was reallocated only about a dozen times, and the gaps get wider as the list grows. Because each resize makes room for a number of future appends proportional to the size, the total copying work over n appends is proportional to n. The average cost per append is therefore constant: **amortised O(1)**. Occasionally one append is slow (a resize); on average they are all fast.

### 15.3 What each operation costs

| Operation | Cost | Why |
|---|---|---|
| `lst[i]`, `lst[i] = x`, `len(lst)` | O(1) | address arithmetic; length is stored |
| `lst.append(x)`, `lst.pop()` | O(1) amortised | work at the end; occasional resize |
| `lst.insert(0, x)`, `lst.pop(0)` | O(n) | every pointer after the position must shift |
| `x in lst`, `lst.index(x)` | O(n) | compares items one by one |
| `lst[a:b]` | O(b - a) | copies that many pointers |
| `lst.sort()` | O(n log n) | Timsort |

Core.05 claimed that inserting at the front gets slower as the list grows. Now you can measure it, comparing **ratios** rather than absolute times:

```python
import timeit

for n in (1_000, 100_000):
    setup = f"lst = list(range({n}))"
    t_end = timeit.timeit("lst.append(1); lst.pop()", setup, number=2000)
    t_front = timeit.timeit("lst.insert(0, 1); lst.pop(0)", setup, number=2000)
    print(f"n={n:>7}: front/end time ratio = {t_front / t_end:6.1f}")
```
```text
n=   1000: front/end time ratio =    9.5
n= 100000: front/end time ratio =  733.1
```

*Ratios from the test machine; they vary, but the pattern does not.* At the end of the list, the cost does not depend on `n`. At the front, every insert and pop shifts all `n` pointers, so the gap grows with the size of the list. When you need fast operations at both ends, use `collections.deque` (core.17), which is built as a linked list of blocks.

## 16. How `dict` works

### 16.1 Hash tables in one paragraph

A `dict` finds a key without comparing it to every other key. It computes `hash(key)`, an integer, and uses it to pick a **slot** in a table: in a table of 8 slots, slot = `hash(key) % 8` (CPython uses the low bits, which is the same thing for powers of two). To look the key up later, it computes the same hash, goes straight to the same slot, and checks that the key there is equal (`==`). That is why lookup is O(1) on average, whatever the size of the dictionary.

### 16.2 `hash()`

- Equal objects must have equal hashes: `1 == 1.0 == True`, so all three hash to `1` and are the **same dict key**.
- Small ints hash to themselves, with one odd exception: `hash(-1)` is `-2`, because CPython's C code uses `-1` to signal an error. You can rely on this on CPython; it is a fun fact, not something to use.
- **String hashes are randomised per process.** Each time Python starts, it picks a random secret that changes `hash("abc")`. This protects web servers against "hash flooding" attacks, where an attacker sends many keys that all collide. You can fix the secret with the environment variable `PYTHONHASHSEED`, which is sometimes useful for reproducing a bug. Never store string hashes in files or rely on their values.

```python
print(hash(10), hash(-1), hash(1.0) == hash(1) == hash(True))
print(hash("abc") == hash("ab" + "c"))
d = {1: "int"}
d[1.0] = "float"
d[True] = "bool"
print(d)
```
```text
10 -2 True
True
{1: 'bool'}
```

Because `1`, `1.0` and `True` are equal and hash equally, they are the same key. The dict kept the **first key object** (`1`) and replaced only the value.

### 16.3 Collisions and probing

Two different keys can land in the same slot: a **collision**. CPython uses **open addressing**: if the slot is taken by a different key, it tries another slot, following a fixed pseudo-random sequence (it mixes in more bits of the hash as it goes). Lookup follows the same sequence until it finds the key or an empty slot. With a simpler rule, "try the next slot" (**linear probing**), a 8-slot table could fill like this:

```text
insert "a" (hash % 8 = 3)  ->  slot 3
insert "b" (hash % 8 = 5)  ->  slot 5
insert "c" (hash % 8 = 3)  ->  slot 3 taken by "a", try 4: free -> slot 4
lookup "c": slot 3 holds "a" (not equal), slot 4 holds "c" -> found after 2 probes
```

Deleting is subtle: if `"a"` were simply removed from slot 3, a later lookup of `"c"` would stop at the empty slot 3 and wrongly report "not found". So a deleted slot is marked with a **tombstone** ("deleted, keep probing"). Problem p017 builds a full toy dict with all of this.

### 16.4 The compact dict and insertion order

Since CPython 3.6, a dict is stored in two parts:

```text
 indices (the hash table, small integers)    entries (in insertion order)
 slot: 0    1    2    3    4    5    6    7         hash   key     value
      [ -  | -  | -  | 0  | 2  | 1  | -  | - ]   0: h_a    "a"     1
                                                 1: h_b    "b"     2
                                                 2: h_c    "c"     3
```

The hash table holds only small indices into a dense **entries** array, where key/value pairs are appended in insertion order. This uses less memory than a table of full entries (the empty slots are just small integers), and iterating means walking the entries array, which naturally gives **insertion order**. That property started as a side effect of this design in 3.6 and became a **language guarantee** in 3.7: every Python implementation must now keep dicts in insertion order.

### 16.5 Load factor and resizing

Probing stays short only while the table has plenty of empty slots. CPython keeps the table at most about **two-thirds full**. When an insert would pass that limit, it builds a bigger table and re-inserts every key: an O(n) step that, like list growth, happens rarely enough that inserts are O(1) amortised. You can see the jumps:

```python
import sys

d = {}
points = []
previous = sys.getsizeof(d)
for i in range(100):
    d[i] = i
    size = sys.getsizeof(d)
    if size != previous:
        points.append(len(d))
        previous = size
print(points)
```
```text
[1, 6, 11, 22, 43, 86]
```

*64-bit CPython 3.14; resize points differ by version.* The resizes come at roughly doubling sizes. This is also why an empty dict or set reports more memory than an empty list (section 9.3): it keeps empty slots on purpose.

### 16.6 Why keys must not change

The slot of a key is decided by its hash **when it is inserted**. If the key's hash could change afterwards, the dict would look in the wrong slot and never find it again. That is why `list` and `dict` are unhashable, and why a class that defines `__eq__` must define `__hash__` from immutable data only (core.15):

#### Predict the output 16.1

```python
class Badge:
    def __init__(self, code):
        self.code = code
    def __eq__(self, other):
        return isinstance(other, Badge) and self.code == other.code
    def __hash__(self):
        return hash(self.code)

b = Badge("A1")
access = {b: "lab"}
print(access[Badge("A1")])
b.code = "Z9"
print(b in access)
print(Badge("A1") in access)
print(len(access), list(access.values()))
```

<details><summary>Answer</summary>

```text
lab
False
False
1 ['lab']
```

- Before the change, a new `Badge("A1")` has the same hash and compares equal, so it finds `"lab"`.
- After `b.code = "Z9"`, looking up `b` computes the hash of `"Z9"`, goes to a different slot, and finds nothing.
- Looking up `Badge("A1")` goes to the *right* slot, finds the stored key, and compares it with `==`. But the stored key is `b`, whose code is now `"Z9"`, so they are not equal: not found either.
- The entry is still inside the dict, but **no lookup can ever reach it**. The fix is to make the fields used by `__hash__` and `__eq__` immutable, for example with `@dataclass(frozen=True)` (core.15).

</details>

### 16.7 When hashing goes wrong

If many keys share one hash, every lookup must probe past all of them, and O(1) becomes O(n). A class whose `__hash__` returns a constant is legal (equal objects still have equal hashes) but turns a dict into a slow list:

```python
import timeit

class Good:
    def __init__(self, n): self.n = n
    def __eq__(self, other): return self.n == other.n
    def __hash__(self): return hash(self.n)

class Bad(Good):
    def __hash__(self): return 42

for cls in (Good, Bad):
    keys = [cls(i) for i in range(2000)]
    t = timeit.timeit(lambda: {k: None for k in keys}, number=3)
    print(f"{cls.__name__}: {t:.3f} s")
```
```text
Good: 0.002 s
Bad: 1.306 s
```

*Times from the test machine.* The same 2,000 keys, but every `Bad` key collides with every other, so building the dict compares each new key with all the earlier ones. This is precisely the attack that string-hash randomisation (section 16.2) prevents. A good `__hash__` hashes a tuple of the fields that define equality: `return hash((self.x, self.y))`.

## 17. How `set` works

### 17.1 A hash table of keys only

A `set` uses the same hashing and probing as a dict (section 16), but each slot holds only a key and its cached hash: no values, and **no separate entries array**. Iterating a set walks the table slot by slot, so the order you see is **slot order**, decided by the hashes, not insertion order. Small ints hash to themselves, so small ranges often *look* sorted; strings have randomised hashes (section 16.2), so their order changes from one run of Python to the next:

```python
import os
import subprocess
import sys

print({3, 1, 2}, {30, 1, 17, 4})
code = 'print(list({"pear", "fig", "apple", "kiwi"}))'
for seed in ("1", "2"):
    env = dict(os.environ, PYTHONHASHSEED=seed)
    result = subprocess.run([sys.executable, "-c", code], env=env,
                            capture_output=True, text=True)
    print("seed", seed, result.stdout.strip())
```
```text
{1, 2, 3} {1, 4, 30, 17}
seed 1 ['pear', 'fig', 'kiwi', 'apple']
seed 2 ['fig', 'apple', 'pear', 'kiwi']
```

*64-bit CPython 3.14; the orders shown are not promised by any version.* `{3, 1, 2}` looks sorted, but once numbers exceed the table size, wrap-around and collisions scramble them, as `{1, 4, 30, 17}` shows. Each child process uses a fixed hash seed, so its order is repeatable; change the seed and the strings land in different slots. **Never depend on set order**: sort the result (`sorted(s)`) when order matters, or use `dict.fromkeys(items)` when you need unique items *in insertion order*.

### 17.2 Why sets are fast, and what they cost

`x in s` hashes `x` and checks a slot or two: O(1) on average. `x in lst` compares `x` with each item: O(n).

```python
import timeit

for n in (1_000, 100_000):
    items = list(range(n))
    as_set = set(items)
    t_list = timeit.timeit(lambda: n - 1 in items, number=200)
    t_set = timeit.timeit(lambda: n - 1 in as_set, number=200)
    print(f"n={n:>7}: list/set time ratio = {t_list / t_set:8.0f}")
```
```text
n=   1000: list/set time ratio =       74
n= 100000: list/set time ratio =    12377
```

*Ratios from the test machine; they vary between runs.* The ratio grows roughly a hundredfold when `n` does: the list search slows down in proportion to its length, while the set lookup stays the same. Set operations reuse this: `a & b` walks the **smaller** set and tests each element in the other, O(min(len(a), len(b))); `a | b` is O(len(a) + len(b)). Building a set from a list costs O(n) once, which pays off as soon as you test membership more than a few times (core.20). The price is memory: the table keeps empty slots (section 9.3).

### 17.3 Hashable elements and `frozenset`

Elements must be hashable for the same reason dict keys must be (section 16.6): the slot is chosen from the hash at insertion time. A `set` itself is mutable and therefore unhashable, so sets cannot contain sets. A **`frozenset`** is the same table but immutable, so it *is* hashable and can be a dict key or a set element. The compiler uses one for `x in {1, 2, 3}` (section 8.2).

```python
try:
    bad = {[1, 2], [3]}
except TypeError as e:
    print(type(e).__name__)

groups = {frozenset({"ana", "raj"}): "team A"}
print(groups[frozenset({"raj", "ana"})])
```
```text
TypeError
team A
```

A frozenset compares and hashes by its elements, not their order, so `{"raj", "ana"}` finds the key stored as `{"ana", "raj"}`.

#### Predict the output 17.1

```python
a = {"x", "y", "z"}
b = frozenset({"y", "z", "w"})
print(sorted(a & b), sorted(a - b), sorted(a ^ b))
print(type(a | b).__name__, type(b | a).__name__)
print(len({1, 1.0, True, "1"}))
```

<details><summary>Answer</summary>

```text
['y', 'z'] ['x'] ['w', 'x']
set frozenset
2
```

Sorting makes the answer independent of slot order. `&` keeps common elements, `-` those only in `a`, `^` those in exactly one. A mixed operation returns the type of the **left** operand. `1`, `1.0` and `True` are equal with equal hashes, so they count once; `"1"` is a string, a different element.

</details>

## 18. Strings inside CPython

### 18.1 One, two or four bytes per character

A Python `str` is a sequence of Unicode code points (core.03). Storing every character in 4 bytes would make ASCII text four times bigger than needed. Since Python 3.3 (PEP 393), CPython looks at the **widest character** in each string and picks a storage width for the whole string:

- all characters below 256 (ASCII and Latin-1, such as `é`): **1 byte** each;
- all below 65,536 (most living languages, `€`, Hindi, Chinese): **2 bytes** each;
- anything higher (emoji, rare scripts): **4 bytes** each.

#### Predict the output 18.1

Rank these five strings by `sys.getsizeof`, smallest first. Each has 100 characters.

```python
import sys

samples = {
    "ascii": "a" * 100,
    "latin1": "é" * 100,
    "euro": "€" * 100,
    "emoji": "😀" * 100,
    "one_emoji": "a" * 99 + "😀",
}
for name, text in sorted(samples.items(), key=lambda kv: sys.getsizeof(kv[1])):
    print(f"{name:<10} {len(text)} chars  {sys.getsizeof(text)} bytes")
```

<details><summary>Answer</summary>

```text
ascii      100 chars  141 bytes
latin1     100 chars  157 bytes
euro       100 chars  258 bytes
emoji      100 chars  460 bytes
one_emoji  100 chars  460 bytes
```

*64-bit CPython 3.14; exact byte counts differ by version.* ASCII is cheapest (1 byte per character). Latin-1 also uses 1 byte per character, plus a slightly larger header for non-ASCII strings. `€` needs 2 bytes per character, emoji 4. The surprise is the last one: a **single** emoji forces the whole string into 4-byte storage, so 99 `a`s plus one emoji cost as much as 100 emoji. Indexing stays O(1) in every case, because all characters in one string have the same width.

</details>

### 18.2 Immutability and building strings

Strings are immutable, so `s += piece` must, in principle, create a new string and copy everything: O(n²) for a loop of n pieces. CPython has an optimisation that sometimes extends the string in place when nobody else refers to it, so the slow loop can look fast on CPython. That is a detail other implementations do not share and that small code changes defeat. The guaranteed linear way is to collect pieces in a list and call `"".join(pieces)` once (core.03).

## 19. The GIL, free threading and the JIT

This section is based on the official Python documentation and PEPs, not on measurements, because these features depend on how Python was built. Treat the details as "how it works today", which may change.

### 19.1 The GIL from the inside

Core.21 explained what the GIL does for your threads. From the inside, its main job is now clear: it protects the **reference counts** (section 10) and the internal state of every object. With one lock held by the running thread, `Py_INCREF` and `Py_DECREF` can be plain, fast memory updates, and a `dict` never sees two threads resizing it at once. The running thread releases the GIL around blocking I/O and is asked to release it every few milliseconds (`sys.getswitchinterval()`), so other threads get a turn.

### 19.2 The free-threaded build (3.13t, 3.14t)

PEP 703 added a build without the GIL: experimental in 3.13, officially supported but still optional in 3.14. Removing one lock is the easy part; keeping reference counting correct and fast without it is the hard part. According to the PEP and the docs, the free-threaded build uses:

- **biased reference counting**: each object remembers the thread that created it; that thread updates the count with fast ordinary instructions, and other threads use slower atomic instructions;
- **immortal objects** (section 10.4) and deferred counting for objects shared by everyone, such as functions and code objects, so their counts are rarely touched;
- **per-object locks** inside built-in containers like `list` and `dict`, so a single operation such as `append` stays safe;
- a thread-safe memory allocator (mimalloc) and a garbage collector that briefly pauses all threads.

The cost is that single-threaded code runs somewhat slower than on the normal build (the 3.14 docs speak of roughly 5 to 10%). You can check which build you are running:

```python
import sys
import sysconfig

gil_check = getattr(sys, "_is_gil_enabled", None)   # only exists on 3.13+
print("GIL enabled:", gil_check() if gil_check else "yes (3.12 or older)")
print("free-threaded build:", bool(sysconfig.get_config_var("Py_GIL_DISABLED")))
```
```text
GIL enabled: True
free-threaded build: False
```

*Output from the normal (GIL) build of 3.14 on the test machine.*

### 19.3 The experimental JIT compiler (3.13+)

A **JIT** (just-in-time) compiler turns hot code into machine code while the program runs. PEP 744 added an experimental one to CPython in 3.13. According to the docs, it builds on the specialising interpreter of section 7:

1. Hot specialised bytecode is translated into a sequence of smaller **micro-operations** ("tier 2").
2. The JIT turns that sequence into machine code using a technique called **copy-and-patch**: when CPython itself is built, each micro-operation is compiled in advance into a small machine-code template with "holes". At run time the JIT copies the templates one after another and patches the holes with the actual constants and addresses. This is much simpler and faster than a traditional compiler, at the cost of less optimised code.

In 3.13 the JIT had to be enabled when building CPython from source. In 3.14 the official Windows and macOS installers include it, switched off by default; setting the environment variable `PYTHON_JIT=1` turns it on. The docs describe the speed-up as modest so far, from slightly slower to somewhat faster depending on the program. It changes nothing about how Python behaves. For this course the lesson is the same as in section 7: type-stable, simple hot loops are what all these optimisations can speed up.

## 20. Extending Python: C extensions, `ctypes` and Cython

### 20.1 Why extend Python in another language

Many of the modules you have used are not written in Python. `math`, `json`'s fast parts, `sqlite3`, `zlib` and `_pickle` are **C extension modules**: compiled C code that CPython loads like any module. Libraries such as NumPy do most of their work in C. There are three reasons to write code this way:

1. **Speed** for a hot loop that the interpreter is too slow for (after measuring, core.20).
2. **Reuse** of an existing C library: database drivers, compression, image formats.
3. **Parallelism**: C code that does not touch Python objects can release the GIL and run on other cores.

### 20.2 The C API in one example (reading only)

C extensions talk to CPython through the **C API**. You do not need to write any C in this course, but reading one function shows how much of this chapter is visible from C:

```c
/* reading only: a C function callable from Python as add(a, b) */
static PyObject *
add(PyObject *self, PyObject *args)
{
    long a, b;
    if (!PyArg_ParseTuple(args, "ll", &a, &b)) {
        return NULL;                 /* NULL means: an exception has been set */
    }
    return PyLong_FromLong(a + b);   /* a new int object, refcount 1, owned by the caller */
}
```

- Every Python value is a `PyObject *`: a pointer to the object header from section 9.1.
- Errors are returned as `NULL` with an exception recorded; the evaluation loop sees the `NULL` and starts unwinding frames (section 6.4).
- The extension author must manage **reference counts by hand** with `Py_INCREF` and `Py_DECREF`. Forget a `DECREF` and memory leaks; one `DECREF` too many and the program crashes. This is the main reason people prefer the higher-level tools below.
- A compiled extension is tied to one Python version unless it restricts itself to the "limited API", which is why packages publish separate wheels per version.

Tools that write most of this for you: **Cython** (section 20.4), **pybind11** (C++), **PyO3** (Rust) and **cffi**.

### 20.3 `ctypes`: C data types from pure Python

The standard-library `ctypes` module gives you C data types without a compiler. Its main purpose is to call functions in existing shared libraries (`.so`, `.dll`, `.dylib`) via `ctypes.CDLL(...)`, which is platform-specific and not shown here. But its data types alone already teach a lot about how memory is laid out:

```python
import ctypes

print(ctypes.sizeof(ctypes.c_int), ctypes.sizeof(ctypes.c_double), ctypes.sizeof(ctypes.c_char))

class Pixel(ctypes.Structure):
    _fields_ = [("r", ctypes.c_uint8), ("g", ctypes.c_uint8), ("b", ctypes.c_uint8)]

row = (Pixel * 4)()          # a C array of 4 pixels, all zero
row[1].g = 300               # does not fit in 8 bits
print(ctypes.sizeof(row), row[1].g)

number = ctypes.c_int(5)
pointer = ctypes.pointer(number)
pointer.contents.value = 7
print(number.value)
```
```text
4 8 1
12 44
7
```

*Sizes are for 64-bit Linux, macOS and Windows.* A `Structure` lays its fields out exactly as a C compiler would. `Pixel * 4` is a C array type, one contiguous block of 12 bytes: no headers, no pointers, unlike a Python list of objects. Assigning 300 to an 8-bit field silently **wraps around** (300 - 256 = 44), as it would in C: you have left Python's safe world of unlimited integers. And a pointer lets you change a value through another name, which is how C functions return results.

`ctypes` can also lay a C view over memory owned by a Python object:

```python
import ctypes

buffer = bytearray(8)
numbers = (ctypes.c_int32 * 2).from_buffer(buffer)
numbers[0] = 1
numbers[1] = 258
print(buffer)
```
```text
bytearray(b'\x01\x00\x00\x00\x02\x01\x00\x00')
```

*Byte order shown is little-endian (x86 and ARM machines).* Writing to the C array changed the bytes of the `bytearray`, because both share one block of memory. `258` is `0x0102`, stored lowest byte first. This kind of sharing is how libraries pass large buffers between Python and C without copying.

#### Try it 20.1

Predict `ctypes.sizeof` of this structure, then check. Why is it not 5?

```python
import ctypes

class Record(ctypes.Structure):
    _fields_ = [("flag", ctypes.c_char), ("count", ctypes.c_int)]

print(ctypes.sizeof(Record), Record.count.offset)
```

<details><summary>Answer</summary>

```text
8 4
```

*Typical for 64-bit platforms.* A `c_char` is 1 byte and a `c_int` is 4, but the C compiler rules that `ctypes` follows require a 4-byte `int` to start at an address divisible by 4 (**alignment**). So 3 bytes of **padding** are inserted after `flag`, `count` starts at offset 4, and the structure is 8 bytes. Putting the largest fields first is the classic way to reduce padding.

</details>

### 20.4 Cython (reading only)

**Cython** is a language that is almost Python, plus optional C type declarations. A Cython file (`.pyx`) is translated to C, compiled, and imported like any module:

```cython
# primes.pyx (reading only: needs Cython and a C compiler to build)
def count_primes(int limit):
    cdef int n, d, count = 0
    for n in range(2, limit):
        d = 2
        while d * d <= n:
            if n % d == 0:
                break
            d += 1
        else:
            count += 1
    return count
```

Without the `cdef int` declarations this is ordinary Python, and Cython compiles it to C that still goes through the C API for every operation, giving a modest speed-up. With the declarations, `n`, `d` and `count` become plain C integers: no objects, no reference counts, no bytecode, and loops like this one often run tens of times faster. The price is a build step, a compiler on every machine that builds it, and C's integer overflow rules. As always: measure first, and try a better algorithm or a library before reaching for C.

## 21. Using internals knowledge responsibly

This chapter showed you many things CPython does. Only some of them are promises. Before you rely on something, ask which column it is in:

| Guaranteed by the language | CPython detail (may change or differ on PyPy) |
|---|---|
| dicts keep insertion order (3.7+) | the exact sizes and resize points of lists and dicts |
| `is` works for `None`, `True`, `False` and your own sentinels | `is` results on ints, strings and other values |
| `with` closes files and releases locks | objects are freed the moment their last reference goes |
| `weakref` callbacks and `finalize` run after the object is collected | *when* that collection happens |
| a code object has `co_consts`, `co_names`, `co_varnames` | the bytecode instructions, their names and order |
| `sys.getsizeof` returns a size in bytes | the numbers it returns |
| `hash(x) == hash(y)` whenever `x == y` | the actual hash values (and strings change per run) |

Three habits follow from this:

1. **Write code against the left column.** Use the right column to *explain* and *measure*, not to make your program work.
2. **Measure before optimising** (core.20). Knowing that local variables are faster than globals is useful when a profiler has pointed at a loop, not as a reason to rewrite every function.
3. **When you see "CPython implementation detail" in the docs, believe it.** It means exactly that this behaviour may differ on another version or implementation.

## 22. Project preview: a mini stack-based bytecode interpreter

The module project (problem p035) is your own tiny virtual machine: the same design as CPython's evaluation loop from sections 2.5 and 4.3, small enough to build in an afternoon or two. This section is only the **design sketch**.

### 22.1 The instruction set

Programs are lists of `(op, arg)` tuples. They are written as text, one instruction per line, with `label:` lines marking jump targets and `#` starting a comment. The shared instruction set (also used by problems p005, p031 and p034) is:

| Op | Stack effect | Meaning |
|---|---|---|
| `PUSH n` | +1 | push the integer `n` |
| `POP`, `DUP`, `SWAP` | -1, +1, 0 | discard the top; copy the top; swap the top two |
| `ADD`, `SUB`, `MUL`, `DIV` | -1 | pop `b`, pop `a`, push `a op b` (`DIV` is `//`) |
| `LT`, `EQ` | -1 | pop `b`, pop `a`, push `1` if `a < b` (or `a == b`) else `0` |
| `LOAD name`, `STORE name` | +1, -1 | push a variable's value; pop into a variable |
| `JUMP label` | 0 | continue at the label |
| `JUMP_IF_FALSE label` | -1 | pop; if the value is false (0), continue at the label |
| `PRINT` | -1 | pop and append the value to the output list |
| `CALL label nargs`, `RET` | | call a function at a label with `nargs` arguments in a new frame; return the top value to the caller |
| `HALT` | 0 | stop |

Here is a countdown program and its stack, the same kind of trace as section 5.7:

```text
        PUSH 3            # n = 3
        STORE n
loop:   LOAD n            # while n > 0 (written as 0 < n)
        PUSH 0
        SWAP
        LT
        JUMP_IF_FALSE end
        LOAD n            # print n
        PRINT
        LOAD n            # n = n - 1
        PUSH 1
        SUB
        STORE n
        JUMP loop
end:    HALT
```

Output: `[3, 2, 1]`. Notice how `while n > 0` becomes "test at the top, jump out if false, body, jump back": the pattern you saw CPython use in section 5.6.

### 22.2 The pieces

| Piece | Job | Chapter sections |
|---|---|---|
| **assembler** | text to a list of `(op, arg)`; resolve each label to an instruction index; reject unknown ops with the line number | 2.1 (a tiny tokenizer and parser) |
| **VM loop** | `while` loop with an instruction pointer `ip`: fetch, decode, execute, `ip += 1` unless the instruction jumped | 2.5, 4.3 |
| **value stack** | a Python list; `pop` from an empty stack raises `StackUnderflow` naming the offset | 4.3, 4.7 |
| **frames** | each `CALL` pushes a frame with its own variables and return address; `RET` pops it | 6.1 |
| **errors and limits** | `UnknownOp`, `StackUnderflow`, `StepLimitExceeded` (so an infinite loop in a test cannot hang), each with the instruction offset | 6.4 |
| **optional compiler** | `ast.parse` a tiny expression language and emit instructions in postfix order | 2.3, 4.3 |

### 22.3 Design rules to keep

- **One dispatch loop**, like `_PyEval_EvalFrameDefault`: a `dict` from op name to a small handler method is cleaner than a 20-branch `if` chain.
- **Errors carry the offset** of the failing instruction, so a learner can find the bad line, just as a traceback gives a line number.
- **The step limit is not optional.** Every program that can jump backwards can loop forever.
- **Test with traces.** A test that checks the output list *and* the final stack catches far more bugs than one that checks only the output.

## 23. Summary

**How code runs.** Source is tokenized, parsed into an AST (`ast`), and compiled once into a **code object**; the evaluation loop then runs its **bytecode**, a stack machine (sections 2 to 5).

- A **function** is a code object plus globals, defaults and closure cells. The stable `co_*` attributes (`co_varnames`, `co_names`, `co_consts`, `co_freevars`, `co_cellvars`, `co_flags`) tell you what the compiler decided. Test membership in `co_consts`, never positions.
- **Reading bytecode** (`dis`): operands are pushed first, operations pop them and push results, stores pop into variables. The suffix says where a name lives: `FAST` local, `GLOBAL` global/built-in, `DEREF` closure cell, `NAME` dictionary namespace, `ATTR` attribute. `if` and loops are jumps; `for` is `GET_ITER` plus `FOR_ITER`. Instruction names change between versions; the scheme does not.
- **Frames** hold the instruction pointer, locals and value stack, and link to their caller with `f_back`; tracebacks are chains of frames; generators keep their frame between `next()` calls; `sys.settrace` lets debuggers watch every line.
- The **specialising adaptive interpreter** (3.11+) rewrites hot instructions for the types it sees and falls back when a guard fails; type-stable hot code benefits. The compiler **folds constants** such as `24 * 60 * 60` and turns membership tests against literal lists and sets into tuple and frozenset constants.

**How memory works** (sections 9 to 14).

- Every object has a header with a **reference count** and a **type pointer**. `id()` is the address in CPython. `sys.getsizeof` is shallow; walk containers (or use `tracemalloc`) for real sizes.
- **Reference counting** frees an object the moment its last reference goes. `del` removes a name, not an object. Since 3.12, `None`, small ints and other common objects are **immortal**. Only ever compare reference-count *differences*.
- A **reference cycle** keeps every member's count above zero even when nothing outside can reach the group, so reference counting alone can never free it. The **garbage collector** examines tracked containers, subtracts references that come from inside the group, keeps whatever is reachable from outside references, and frees the rest. It runs by generations (incremental in 3.14); `gc.collect()` forces it.
- **Weak references** (`weakref.ref`, `WeakValueDictionary`, `WeakSet`, `WeakMethod`, `finalize`) refer without keeping alive, for caches, back-pointers and cleanup. Release resources with `with`, not `__del__`.
- Small ints (-5 to 256) are cached and many strings are interned, so `is` on values gives unreliable results: use `==`, and `is` only for singletons.

**How the containers work** (sections 15 to 18). `list` is an over-allocated array of pointers: O(1) indexing and amortised O(1) `append`, O(n) at the front. `dict` is a compact hash table kept under about two-thirds full, with an insertion-ordered entries array; keys must keep their hash. `set` is a hash table without values. `str` stores 1, 2 or 4 bytes per character, chosen by its widest character.

**The edges** (sections 19 to 21). The GIL protects reference counts; the free-threaded build replaces it with biased reference counting and per-object locks; the experimental JIT uses copy-and-patch on top of the specialising interpreter. C extensions use the C API with manual reference counting; `ctypes` gives C data types from Python; Cython compiles typed Python to C. Rely only on what the language guarantees; use the internals to explain and to measure.

The idea underneath the whole chapter: **CPython is an ordinary program with a few simple ideas (a stack machine, reference counts, a cycle detector, hash tables, over-allocated arrays) applied very carefully.** Once you know them, performance and memory behaviour stop being mysteries, and you can tell which of them you may rely on.
