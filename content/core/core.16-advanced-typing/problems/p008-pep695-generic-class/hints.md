## Hint 1

In the new syntax, where does the type variable `T` live? Look at the examples: `class Box[T]:`. And a variable that belongs to a single method, like `U` in `map`? Where would its brackets go, and does the method need any other declaration?

## Hint 2

`func: Callable[[T], U]` takes a `T` and returns a `U`; `map` returns `Box[U]` (a new box: the old one is not changed). Inside the class body, `Box[U]` refers to the class itself; Python 3.14 evaluates annotations lazily, but a string `"Box[U]"` also works. For `biggest`, a constraint list goes in parentheses after a colon: `[N: (int, float)]`.

## Hint 3

```
class Box[T]:
    __init__(self, value: T) -> None:   self.value = value
    get(self) -> T:                     return self.value
    map[U](self, func: Callable[[T], U]) -> "Box[U]":   return Box(func(self.value))
    __repr__:  f"Box({self.value!r})"
    __eq__(other): if not Box: return NotImplemented ; return self.value == other.value
    __hash__:  hash(("Box", self.value))

def biggest[N: (int, float)](a: N, b: N) -> N:   return b if b > a else a
```
