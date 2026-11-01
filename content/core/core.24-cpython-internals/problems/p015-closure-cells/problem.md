# Trace: closures, cells and late binding

When an inner function uses a variable of the enclosing function, CPython does not copy the
value. It moves the variable into a **cell**: a tiny object that holds one reference. The outer
function and every inner function that uses the variable share that same cell.

- `outer.__code__.co_cellvars`: names of the outer function's variables that live in cells
  (because some inner function uses them).
- `inner.__code__.co_freevars`: names the inner function reads from cells it did not create.
- `inner.__closure__`: a tuple of the actual cell objects (in `co_freevars` order), or `None`
  for a function that has no free variables. Each cell has a `cell_contents` attribute, which
  you can read and even assign. Reading an empty cell raises an exception.

These attributes (and the rules below) are the same on every Python from 3.11 to 3.14.

Work out exactly what this program prints. Write one line per `print` call, with the same
spacing and quotes that `print` would give. Where the program catches an exception it prints
only the exception's class name.

```python
def make_counter():
    count = 0
    def step():
        nonlocal count
        count += 1
        return count
    return step


c = make_counter()
print(make_counter.__code__.co_cellvars, make_counter.__code__.co_freevars)
print(c.__code__.co_freevars, c.__code__.co_cellvars)
print(c.__qualname__, type(c.__closure__[0]).__name__)
print(c(), c(), c.__closure__[0].cell_contents)
d = make_counter()
print(d(), c(), c.__closure__[0] is d.__closure__[0])
c.__closure__[0].cell_contents = 100
print(c(), d())


def outer(x):
    def middle():
        def inner():
            return x
        return inner
    return middle


m = outer(5)
print(outer.__code__.co_cellvars)
print(m.__code__.co_freevars, m.__code__.co_cellvars)
print(m().__code__.co_freevars, m().__closure__[0].cell_contents)
print(make_counter.__closure__, outer.__closure__)


def make_adders():
    adders = []
    for n in range(3):
        adders.append(lambda x: x + n)
    return adders


adders = make_adders()
print([a(10) for a in adders])
print(adders[0].__closure__[0] is adders[2].__closure__[0], adders[0].__closure__[0].cell_contents)


def make_adders_fixed():
    adders = []
    for n in range(3):
        adders.append(lambda x, n=n: x + n)
    return adders


fixed = make_adders_fixed()
print([a(10) for a in fixed], fixed[0].__closure__, fixed[1].__defaults__)


def early():
    def show():
        return later
    cell = show.__closure__[0]
    try:
        cell.cell_contents
    except ValueError as e:
        print(type(e).__name__)
    try:
        show()
    except NameError as e:
        print(type(e).__name__)
    later = "ready"
    print(cell.cell_contents, show())


early()
```

Write your answer in `answer.txt`, one output line per `print`.

**Example (a different program)**

```python
def f():
    a = 1
    b = 2
    def g():
        return a
    return g

g = f()
print(f.__code__.co_cellvars, g.__code__.co_freevars, g.__closure__[0].cell_contents)
```

prints

```
('a',) ('a',) 1
```

`b` is an ordinary local of `f`: no inner function uses it, so it is not in a cell.
