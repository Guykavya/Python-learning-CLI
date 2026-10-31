## Approach

`__call__` makes an instance behave like a function **and** lets it carry state in its attributes. `@CallCounter` works because a decorator is just "call this with the function and use the result": `greet = CallCounter(greet)`. The result is an object, not a function, but it can be called, so the rest of the program does not care. Compared with a closure and `nonlocal`, the counter lives in a normal, readable attribute (`greet.count`).

## Code

```python
class CallCounter:
    def __init__(self, func):
        self.func = func
        self.count = 0

    def __call__(self, *args, **kwargs):
        self.count += 1
        return self.func(*args, **kwargs)

    def reset(self):
        self.count = 0
```

## Complexity

O(1) overhead per call.

## Another way

A function decorator with an attribute on the wrapper (`wrapper.count += 1`) or a closure with `nonlocal` gives the same result; the class form is easier to extend with methods like `reset()`.
