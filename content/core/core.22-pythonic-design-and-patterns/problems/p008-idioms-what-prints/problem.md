# Trace: what do these idioms print?

Idioms are short, but each one hides a rule. This program uses twelve of them. Work out, **line by
line**, exactly what it prints. Write one line of output per `print` call, in order, with the same
spacing and quotes that `print` would give. The program is deterministic and needs no input.

Rules you may need:

- `a < b < c` means `a < b and b < c` (and `b` is evaluated once).
- `x or y` gives `x` if `x` is truthy, else `y`. `x and y` gives `x` if `x` is falsy, else `y`.
- Function arguments are evaluated **before** the call, always.
- `sorted` is stable: equal keys keep their original order.

```python
calls = []


def default():
    calls.append("default")
    return "d"


config = {"a": 1}

print(1 < 2 < 3, 1 < 3 < 2)
print(5 > 3 == 3, 2 < 1 < 5)
name = ""
print(repr(name or "guest"), repr(0 or None), repr([] or [0]))
print(1 and 2, 0 and 2, None or 0)
print(config.get("a", default()), config.get("b", default()), len(calls))
words = ["bb", "a", "cc", "d", "aa"]
print(sorted(words, key=len))
print(sorted(words, key=len, reverse=True))
print(list(zip([1, 2, 3], "ab")))
a, b = 1, 2
for _ in range(3):
    a, b = b, a + b
print(a, b)
grid = [[0] * 2] * 2
grid[0][0] = 9
print(grid)
good = [[0] * 2 for _ in range(2)]
good[0][0] = 9
print(good)
print(any([]), all([]), any([0, ""]), all([1, "x"]))
x = [1, 2, 3]
y = x
y += [4]
z = x + [5]
print(x, y is x, z is x)
print([i for i in range(5) if i % 2], [i * i for i in range(3)][-1])
```

Write your answer in `answer.txt`, one output line per `print`.

**Example (a different program)**

```python
print(1 < 2 < 3)
print("" or "x")
```

prints

```
True
x
```
