# Dataclass instead of dict

A dict for a record is easy to start and hard to live with: a typo in a key (`book["titel"]`)
fails only at run time, nothing checks the data, you cannot sort or hash it, and a tool cannot
tell you which keys exist. A `@dataclass` gives you a named, checked, comparable record, and
writes `__init__`, `__repr__` and `__eq__` for you.

```python
@dataclass(frozen=True, order=True)     # frozen: read-only and hashable; order: sorts by fields
class Point:
    x: int
    y: int
    def __post_init__(self):             # runs after __init__; validate here
        ...

@dataclass
class Box:
    items: list = field(default_factory=list)   # a NEW list per object (never `= []`)
```

`starter.py` stores books and shelves as dicts, with helper functions. Copy it to `solution.py`
and replace it with two dataclasses (the old functions can go):

**`Book`**: `@dataclass(frozen=True, order=True)` with fields `title: str`, `author: str`,
`year: int` (in that order).

- `__post_init__`: an empty title or a year below 1450 or above 2100 raises `ValueError`.
- method `describe()` returns `"Title by Author (year)"`.
- no hand-written `__init__`, `__eq__`, `__hash__`, `__repr__` or ordering methods.

**`Shelf`**: `@dataclass` with fields `name: str` and `books: list` (default: a new empty list via
`field(default_factory=list)`), and methods `add(book)`, `titles()` (insertion order) and
`sorted_books()` (a new sorted list; the shelf keeps its order).

Tests check equality, hashing, the error when you assign to a frozen book, validation, sorting,
`dataclasses.replace` (which must also validate), separate lists per shelf, and the structure
(decorators, `__post_init__`, `default_factory`, no dict literals).

**Example**

```python
b = Book("Dune", "Herbert", 1965)
b.describe()                        # 'Dune by Herbert (1965)'
b == Book("Dune", "Herbert", 1965)  # True
replace(b, year=1966)               # Book(title='Dune', author='Herbert', year=1966)
b.year = 1                          # raises FrozenInstanceError
Book("", "x", 2000)                 # raises ValueError
```
