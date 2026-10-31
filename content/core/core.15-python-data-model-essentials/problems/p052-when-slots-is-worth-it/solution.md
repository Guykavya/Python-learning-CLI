## Approach

State the mechanism first (dict per object vs fixed storage), then the consequences (memory, errors on
unknown names, lost flexibility), then the rule of thumb (many small objects), then the habit
(measure). Compare with `answer.md`.

## Code

```python
import tracemalloc

class Plain:
    def __init__(self, x, y):
        self.x, self.y = x, y

class Slotted:
    __slots__ = ("x", "y")
    def __init__(self, x, y):
        self.x, self.y = x, y

for cls in (Plain, Slotted):
    tracemalloc.start()
    objects = [cls(i, i) for i in range(100_000)]
    print(cls.__name__, tracemalloc.get_traced_memory()[0])
    tracemalloc.stop()
```

## Complexity

Memory per object drops from about 300 bytes to about 50 bytes in the example (O(1) per object either
way; the difference is the constant, multiplied by the number of objects).

## Another way

`@dataclass(slots=True)` generates `__slots__` for you. A `typing.NamedTuple` or plain tuple is even
smaller, but immutable.
