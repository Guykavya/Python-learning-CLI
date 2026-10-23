## Hint 1

The hint for a function parameter is `Callable[[ARGUMENT TYPES], RETURN TYPE]`. The argument types go in their **own** square brackets. How would you write "takes an int and returns a bool"?

## Hint 2

`compose` and `make_adder` return a function, so their return hint is also a `Callable`. Where do you define the inner function, and what do you return: `inner` or `inner(...)`? (Recall closures from core.06.)

## Hint 3

```
def apply_all(func, numbers): return [func(n) for n in numbers]
def keep_if(test, numbers): return [n for n in numbers if test(n)]
def compose(first, second):
    def both(x): return second(first(x))
    return both
def make_adder(n):
    def add(x): return x + n
    return add
```
