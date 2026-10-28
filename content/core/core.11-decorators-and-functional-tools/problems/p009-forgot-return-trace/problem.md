# Two forgotten returns

These two decorators each miss one `return`, in different places. Predict the exact output.
The error message of the `TypeError` is part of the output: write it as Python would.

```python
def trace(func):
    def wrapper(*args):
        print("calling", func.__name__)
        return func(*args)
    # the author forgot: return wrapper


def quiet(func):
    def wrapper(*args):
        print("calling", func.__name__)
        func(*args)
    return wrapper


@trace
def add(a, b):
    return a + b


@quiet
def mul(a, b):
    return a * b


print(add)
try:
    print(add(2, 3))
except TypeError as error:
    print("TypeError:", error)
print(mul(4, 5))
print(mul.__name__)
```

Write exactly what the program prints, one line for each printed line, in `answer.txt`.
If you think the program stops with an error, the program catches it and prints a line, so you never need to write a traceback.
