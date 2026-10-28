## Hint 1

For each class ask: when does the shared object get created, once at definition time or once per instance? In `Cart.__init__(self, owner, items=[])` the default list is created when the `def` runs. In the other two classes, what exactly does `default_factory` receive? A function that **returns** a new object, or an object?

## Hint 2

`default_factory=set()` evaluates `set()` first and gives the factory an **empty set object**, which is not callable. `lambda: SHARED_COUNTS` is callable but returns the **same** dict each time. What function from the built-ins returns a new empty set or dict when called with no arguments?

## Hint 3

```
@dataclass class Cart:    owner: str ; items: list = field(default_factory=list)   + add, count
@dataclass class Tags:    names: set = field(default_factory=set)
@dataclass class Counter: counts: dict = field(default_factory=dict)
delete SHARED_COUNTS
```
