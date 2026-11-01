## Approach

Turn each dict key into a typed field and each helper function into a method.

- `frozen=True` makes instances read-only and (with the generated `__eq__`) hashable, so books
  can live in sets and be dict keys.
- `order=True` generates `<`, `<=`, `>`, `>=` that compare the fields **as a tuple in
  declaration order**: title, then author, then year. That is the old sort key for free.
- `__post_init__` is where validation goes. It also runs for `dataclasses.replace`, because
  `replace` calls the constructor, so you cannot create a bad copy.
- A mutable default needs `field(default_factory=list)`: the factory is called once per new
  object, so shelves never share a list.

## Code

```python
from dataclasses import dataclass, field


@dataclass(frozen=True, order=True)
class Book:
    title: str
    author: str
    year: int

    def __post_init__(self):
        if not self.title:
            raise ValueError("title must not be empty")
        if self.year < 1450 or self.year > 2100:
            raise ValueError("year out of range")

    def describe(self):
        return f"{self.title} by {self.author} ({self.year})"


@dataclass
class Shelf:
    name: str
    books: list = field(default_factory=list)

    def add(self, book):
        self.books.append(book)

    def titles(self):
        return [b.title for b in self.books]

    def sorted_books(self):
        return sorted(self.books)
```

## Complexity

Creation and comparison are O(1) (O(number of fields)). `sorted_books` is O(n log n).

## Another way

`typing.NamedTuple` is also immutable, hashable and ordered (as a tuple), but cannot validate
in `__init__` without extra work. `@dataclass(slots=True)` (3.10+) saves memory for many objects.
For validation that also converts types, libraries such as pydantic exist; the standard library
only checks what you write.
