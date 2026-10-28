# curry: take the arguments a few at a time

A **curried** function can be given its arguments in several steps. Each step that does not yet
have enough arguments returns a new function that waits for the rest:

```python
@curry
def volume(l, w, h):
    return l * w * h

volume(2)(3)(4)      # 24
volume(2, 3)(4)      # 24
volume(2)(3, 4)      # 24
volume(2, 3, 4)      # 24

double_base = volume(2)        # remembers l=2
double_base(3)(4)              # 24
double_base(5)(1)              # 10   (double_base was not changed by the call above)
```

Write `curry(func)` in `solution.py`:

1. Count the **required positional** parameters of `func`: those of kind
   `POSITIONAL_ONLY` or `POSITIONAL_OR_KEYWORD` with no default. Use `inspect.signature`.
   (`param.kind`, `param.default`, and `param.empty` tell you this.)
2. Calling the curried function adds the new positional arguments to the ones collected so far.
   When there are **at least** as many as required, call `func` with all of them and return the
   result. Otherwise return a new curried function that remembers what it has so far.
3. Keyword arguments may be given at any step; they are collected (a later one wins) and passed
   to `func` at the end. They are for parameters with defaults and do not count toward the
   required number.
4. Every partly-applied function is **independent**: using it never changes it, so it can be
   reused many times.
5. A function with no required parameters is called on the first call: `curry(f)()` is `f()`.
6. Every curried function keeps the name and docstring of `func` (`functools.wraps`).

More examples:

```python
@curry
def greet(greeting, name, punct="!"):
    return f"{greeting}, {name}{punct}"

hello = greet("Hello")
hello("Ann")                 # "Hello, Ann!"
hello(punct="?")("Bo")       # "Hello, Bo?"
greet.__name__               # "greet"
```
