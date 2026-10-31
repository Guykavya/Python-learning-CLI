# A decorator by hand, without @

A decorator is just a function that takes a function and returns a new function.
Before you use the `@` sign, build one by hand.

Write `shout(func)` in `solution.py`. It returns a new function (call it `wrapper`) that:

1. accepts the same arguments as `func` (use `*args` and `**kwargs`),
2. calls `func` with them,
3. returns the result in **upper case**.

`shout` must not change `func` and must not call it straight away.

Then, in the same file, write a plain function `greet(name)` that returns `"hello, " + name`, and create a
second name for the decorated version **by hand**, without `@`:

```python
loud_greet = shout(greet)
```

**Examples**

```python
greet("ann")                 # 'hello, ann'      (the original still works)
loud_greet("ann")            # 'HELLO, ANN'

def label(item, price=0):
    return f"{item}: {price}"

shout(label)("tea", price=20)   # 'TEA: 20'
```
