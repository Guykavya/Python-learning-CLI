# Trace: yield from, send and return values

This is the trace test of the module. It mixes three ideas:

- `yield from sub` passes every `next()` and every `send()` straight through to `sub`.
- When `sub` finishes with `return value`, the expression `yield from sub` **evaluates to** that value.
- When the outer generator itself ends with `return value`, the caller sees a `StopIteration`
  whose `.value` is that value.

Predict the exact output.

```python
def inner(name):
    print(name, "starts")
    total = 0
    while True:
        x = yield total
        if x is None:
            break
        total += x
        print(name, "got", x)
    print(name, "ends")
    return total


def outer():
    a = yield from inner("A")
    print("A returned", a)
    b = yield from inner("B")
    print("B returned", b)
    yield a + b
    print("outer done")
    return "ok"


g = outer()
print(next(g))
print(g.send(5))
print(g.send(3))
print(next(g))
print(g.send(10))
print(next(g))
try:
    next(g)
except StopIteration as e:
    print("finished", e.value)
```

Write exactly what the program prints, one line for each printed line, in `answer.txt`.
The program does not crash.

**Example of the format**: a program that prints `A starts` and then `0` gives this `answer.txt`:

```text
A starts
0
```

Remember: `next(g)` is the same as `g.send(None)`.
