## Hint 1

Which features do you need from a record: read-only, comparable, hashable, sortable, a default
list per object, a check on creation? Each one is an option of `@dataclass(...)`, a `field(...)`,
or a method with a special name. Which one runs right after `__init__`?

## Hint 2

```
@dataclass(frozen=True, order=True)
class Book:
    title: str ; author: str ; year: int
    def __post_init__(self): raise ValueError for empty title or bad year
    def describe(self): f"{self.title} by {self.author} ({self.year})"

@dataclass
class Shelf:
    name: str
    books: list = field(default_factory=list)
    add / titles / sorted_books (sorted(self.books) uses order=True)
```
Why would `books: list = []` be a bug? (Python even refuses it in a dataclass.)
