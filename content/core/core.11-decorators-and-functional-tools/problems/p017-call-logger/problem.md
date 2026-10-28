# @logged(log): record every call

Printing is hard to test. A better logger **appends text to a list** that you hand to it. Write the
decorator factory `logged(log)` in `solution.py`. For each call of the decorated function it appends one
line to `log`:

- Normal call: `name(arguments) -> result`
- Call that raises: `name(arguments) raised ErrorType`, and then the same exception is raised again for the caller.

Rules for the text:

- `name` is the function's `__name__`.
- Arguments: each positional argument as `repr(value)`, then each keyword argument as `key=repr(value)`, in the
  order they were given, all joined by `", "`.
- The result is shown with `repr` too.
- Use `functools.wraps`.

**Examples**

```python
log = []

@logged(log)
def add(a, b):
    return a + b

@logged(log)
def greet(name, loud=False):
    text = "hi " + name
    return text.upper() if loud else text

@logged(log)
def div(a, b):
    return a / b

add(2, 3)
greet("Ann", loud=True)
div(1, 0)        # raises ZeroDivisionError, after logging

log
# ["add(2, 3) -> 5",
#  "greet('Ann', loud=True) -> 'HI ANN'",
#  "div(1, 0) raised ZeroDivisionError"]
```
