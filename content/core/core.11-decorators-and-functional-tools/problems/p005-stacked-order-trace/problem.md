# Stacked decorators: who wraps whom?

Two decorators with arguments are stacked on one function. Predict the exact output.
Watch three different moments: when `tag(...)` is called, when `decorate` runs, and when `show` is called.

```python
def tag(name):
    print("make", name)

    def decorate(func):
        print("decorate", name)

        def wrapper(text):
            print("enter", name)
            result = func(text)
            print("exit", name)
            return f"<{name}>{result}</{name}>"

        return wrapper

    return decorate


@tag("b")
@tag("i")
def show(text):
    print("body")
    return text


print("ready")
print(show("hi"))
```

Write exactly what the program prints, one line for each printed line, in `answer.txt`.
If you think the program stops with an error, the program catches it and prints a line, so you never need to write a traceback.
