## Hint 1

Which of the three options solves "every object needs its own list"? What does `default_factory` receive: the list itself or a function that makes one? And which two arguments of `field(...)` control `repr` and `==`?

## Hint 2

`songs: list = field(default_factory=list)` (note: no parentheses after `list`). `plays: int = field(default=0, repr=False, compare=False)`. A field with a default can follow a field without; `songs` and `plays` come after `name`. For `Version`: `@dataclass(frozen=True, order=True)`, three fields in the order major, minor, patch, and `__str__` returning `f"{self.major}.{self.minor}.{self.patch}"`.
