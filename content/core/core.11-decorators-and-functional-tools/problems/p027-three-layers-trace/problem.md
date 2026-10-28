# Trace: three decorators with arguments, start to finish

This is the full story of stacked decorators. Three things happen at three different moments:

1. **Factory time**: `tag("b")` and the others are called, which builds the decorators.
2. **Decoration time**: each decorator receives a function and returns a wrapper.
3. **Call time**: `word("hi")` runs the wrappers, which run code before and after the inner call.

Note that `twice` does **not** use `functools.wraps`, but `tag` does. Predict the exact output.

```python
from functools import wraps


def tag(label):
    print(f"make tag {label}")

    def decorator(func):
        print(f"wrap {label} around {func.__name__}")

        @wraps(func)
        def wrapper(*args):
            print(f"{label} in {args}")
            result = func(*args)
            print(f"{label} out {result}")
            return f"<{label}>{result}</{label}>"
        return wrapper
    return decorator


def twice(times):
    print(f"make twice {times}")

    def decorator(func):
        print(f"wrap twice around {func.__name__}")

        def wrapper(*args):
            print(f"twice in {args}")
            return [func(*args) for _ in range(times)]
        return wrapper
    return decorator


print("start")


@tag("b")
@twice(2)
@tag("i")
def word(w):
    print(f"body {w}")
    return w.upper()


print("defined", word.__name__)
print(word("hi"))
```

Write exactly what the program prints, one line for each printed line, in `answer.txt`.
If you think the program stops with an error, the program catches it and prints a line, so you never need to write a traceback.
