# When does a decorator run?

A decorator has two moments: the moment the `def` with `@` is executed, and every later call.
Predict the exact output and decide which lines belong to which moment.

```python
def loud(func):
    print("decorating", func.__name__)

    def wrapper():
        print("before", func.__name__)
        result = func()
        print("after", func.__name__)
        return result

    print("returning wrapper")
    return wrapper


print("start")


@loud
def hello():
    print("hello body")
    return "hi"


print("defined")
print(hello())
print(hello())
print(hello.__name__)
```

Write exactly what the program prints, one line for each printed line, in `answer.txt`.
If you think the program stops with an error, the program catches it and prints a line, so you never need to write a traceback.
