## Hint 1

Look at the repeated work in the hand-written class: `self.x = x`, `self.y = y`. What does `@dataclass` read from your class body to write that for you? In which order are the parameters of the generated `__init__`?

## Hint 2

```
@dataclass
class Point:
    x: int
    y: int = 0
    def distance_to_origin(self): ...
```
Same pattern for `Product`: three annotated names, `qty` with a default.
