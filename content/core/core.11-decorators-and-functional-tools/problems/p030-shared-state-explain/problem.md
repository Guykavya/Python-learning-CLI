# Explain: one counter for every function

Neha wrote a decorator that should count how many times **each** function is called:

```python
calls = 0


def count(func):
    def wrapper(*args):
        global calls
        calls += 1
        print(f"{func.__name__} call {calls}")
        return func(*args)
    return wrapper


@count
def add(a, b):
    return a + b


@count
def mul(a, b):
    return a * b


add(1, 2)
mul(2, 3)
add(3, 4)
```

It prints:

```text
add call 1
mul call 2
add call 3
```

She expected `add call 1`, `mul call 1`, `add call 2`.

In `answer.md` (about 150 to 300 words), explain:

1. Why does `mul` say "call 2"? Where does the number live, and how many copies of it are there?
2. Which part of a decorator runs **once per decorated function**, and why is that the right
   place for per-function state?
3. Show a fixed version. Use either a closure variable with `nonlocal` or a function attribute
   such as `wrapper.calls`.
4. When is **shared** state what you actually want? Give one example, and say how you would
   make the sharing deliberate.
