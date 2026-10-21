# Causes and contexts

Predict **exactly** what this program prints. For each call, decide which exception reaches
`show`, then work out its three chaining attributes from chapter section 11:

- `__cause__`: set only by `raise ... from X` (to `X`, or `None` for `from None`);
- `__context__`: set automatically to the exception being handled when this one was raised;
- `__suppress_context__`: `True` after any `raise ... from ...`, otherwise `False`.

`type(None).__name__` is `'NoneType'`.

```python
def parse(text):
    try:
        return int(text)
    except ValueError as e:
        raise ValueError("not a number: " + text) from e

def lookup(table, key):
    try:
        return table[key]
    except KeyError:
        raise LookupError("no entry for " + key) from None

def careless(values):
    try:
        return values[3]
    except IndexError:
        return values[0] / 0

def relay(x):
    try:
        return 10 / x
    except ZeroDivisionError:
        print("  relay saw it")
        raise

def show(func, *args):
    try:
        print("ok", func(*args))
    except Exception as e:
        print(type(e).__name__, "|", e)
        print("  cause:", type(e.__cause__).__name__)
        print("  context:", type(e.__context__).__name__)
        print("  suppress:", e.__suppress_context__)

show(parse, "12")
show(parse, "x")
show(lookup, {"a": 1}, "b")
show(careless, [5])
show(careless, [])
show(relay, 0)
```

Write your answer in `answer.txt`, one line per printed line. Keep the leading spaces that some lines print.
