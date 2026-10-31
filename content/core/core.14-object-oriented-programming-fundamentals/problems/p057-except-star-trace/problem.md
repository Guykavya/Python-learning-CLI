# Trace: nested exception groups through `except*`

`except*` does not pick **one** clause like `except`. It **splits** the group: every clause takes
the part that matches it, keeping the nesting, and whatever nobody handled is raised again at the end.
Trace this program and write its output in `answer.txt`.

```python
class AppError(Exception):
    pass


class DbError(AppError):
    pass


class NetError(AppError):
    pass


def leaves(eg):
    out = []
    for e in eg.exceptions:
        if isinstance(e, ExceptionGroup):
            out += leaves(e)
        else:
            out.append(str(e))
    return out


def make():
    return ExceptionGroup("batch", [
        ValueError("bad age"),
        DbError("db down"),
        ExceptionGroup("io", [NetError("timeout"), KeyError("id"), ValueError("bad zip")]),
        TypeError("not int"),
    ])


def run():
    try:
        raise make()
    except* ValueError as g:
        print("V:", g.message, leaves(g))
    except* AppError as g:
        print("A:", g.message, leaves(g))
        print("A nested:", [type(e).__name__ for e in g.exceptions])
    except* DbError as g:
        print("D:", leaves(g))
    print("end of run")


print("--- part 1")
try:
    run()
except ExceptionGroup as rest:
    print("left:", rest.message, leaves(rest))

print("--- part 2")
try:
    raise NetError("solo")
except* AppError as g:
    print("solo:", type(g).__name__, repr(g.message), leaves(g))

print("--- part 3")
try:
    try:
        raise ExceptionGroup("g", [ValueError(1), TypeError(2), KeyError(3)])
    except* ValueError:
        print("handling V")
        raise RuntimeError("from handler")
    except* TypeError:
        print("handling T")
    finally:
        print("finally")
except ExceptionGroup as eg:
    print("outer:", repr(eg.message), [type(e).__name__ for e in eg.exceptions])
    print("inner:", eg.exceptions[1].message, leaves(eg.exceptions[1]))

print("--- part 4")
try:
    raise ExceptionGroup("all fine", [DbError("a"), NetError("b")])
except* AppError as g:
    print("caught", len(g.exceptions))
else:
    print("else")
print("after")
```

Facts you need:

- In `except* T as g`, `g` is always an `ExceptionGroup`. It has the **same message** and the **same
  nesting** as the original, but contains only the leaves that match `T` (subclasses count). Empty
  sub-groups are dropped.
- Each `except*` clause runs **at most once**, and only if something is left that matches it. A leaf
  handled by an earlier clause is gone for the later ones.
- A plain exception (not a group) that reaches `except*` is wrapped into `ExceptionGroup("", [exc])`.
- After all clauses ran, the leaves nobody handled are raised again as a group with the original
  message. If a clause **raised** a new exception, Python raises
  `ExceptionGroup("", [new exceptions..., group of unhandled leaves])` instead.
- `str(KeyError("id"))` is `'id'` **with** the quotes; `str(KeyError(3))` is `3`.

## Example of the format

```python
try:
    raise ExceptionGroup("x", [ValueError("a"), TypeError("b")])
except* ValueError as g:
    print("got", g.message, len(g.exceptions))
except* TypeError:
    print("T too")
```

prints

```text
got x 1
T too
```
