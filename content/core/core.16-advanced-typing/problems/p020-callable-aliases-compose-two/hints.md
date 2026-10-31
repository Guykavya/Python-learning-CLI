## Hint 1

Which type describes "a function that takes an int and returns a bool"? How do you write the list of parameter types, and where does the return type go? For `compose_two`: if `f` turns an `A` into a `B`, what must `g` accept, and what does the finished function take and give?

## Hint 2

Declare `A = TypeVar("A")`, `B = TypeVar("B")`, `C = TypeVar("C")`. The signature is then `compose_two(f: Callable[[A], B], g: Callable[[B], C]) -> Callable[[A], C]`. The body defines a small inner function and returns it (a closure over `f` and `g`).

## Hint 3

```
IntTransform = Callable[[int], int]
IntPredicate = Callable[[int], bool]

count_matching: count items where pred(item)
apply_all: for step in steps: x = step(x); return x

def compose_two(f, g):
    def composed(x):
        return g(f(x))
    return composed
```
