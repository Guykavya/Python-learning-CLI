## Approach

`print` and `str` call `__str__`; `repr`, the REPL and container display call `__repr__`. When `__str__` is missing, `object.__str__` calls `__repr__`, so one method is enough for `Tag`.

## Code

```python
class Book:
    def __init__(self, title, author):
        self.title = title
        self.author = author

    def __repr__(self):
        return f"Book({self.title!r}, {self.author!r})"

    def __str__(self):
        return f"{self.title} by {self.author}"


class Tag:
    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return f"Tag({self.name!r})"
```

## Complexity

O(1).

## Another way

A common habit: always write `__repr__`, and add `__str__` only when the user-facing text must differ.
