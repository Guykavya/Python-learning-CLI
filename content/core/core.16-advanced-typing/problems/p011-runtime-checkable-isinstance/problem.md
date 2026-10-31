# `runtime_checkable`: `isinstance` with a Protocol

A protocol is normally only for the type checker. If you also want to ask `isinstance(x, MyProtocol)`
while the program runs, decorate it with `@runtime_checkable`. Without the decorator
`isinstance` raises `TypeError`.

But beware what the runtime check can do. It only checks that the **names exist** (`hasattr`).
It does not check the argument types, the return type, or the type of an attribute.

In `solution.py` write two runtime-checkable protocols:

```python
@runtime_checkable
class HasArea(Protocol):
    def area(self) -> float: ...

@runtime_checkable
class Named(Protocol):
    name: str
```

and three functions:

1. `total_area(things: Iterable[object]) -> float`: the sum of `thing.area()` for every item that
   is a `HasArea`; ignore all other items (numbers, strings, anything). Empty: `0.0`.
2. `names_of(things: Iterable[object]) -> list[str]`: the `name` of every item that is a `Named`
   **and whose `name` really is a `str`**, in order. (The runtime check cannot see the
   attribute's type; you must check it yourself.)
3. `classify(thing: object) -> str`: `"both"` if it is a `HasArea` and a `Named`, `"area"` if
   only `HasArea`, `"name"` if only `Named`, otherwise `"neither"`. (For `"name"`, a `Named` with a
   non-`str` name still counts as `Named` for this function.)

**Example**

```python
class Circle:
    def __init__(self, r): self.r = r
    def area(self): return 3 * self.r ** 2

total_area([Circle(1), "text", 5, Circle(2)])    # 15.0 (3 + 12)
class Pet:
    name = 42            # a name that is not a str
names_of([Pet()])        # []   isinstance(Pet(), Named) is True, but the name is not a str
```
