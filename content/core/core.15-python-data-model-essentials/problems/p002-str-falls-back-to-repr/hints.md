## Hint 1

Which method does `print(b)` call, and which does `print([b])` call for the item inside the list? Write both `__str__` and `__repr__` on `Book`.

## Hint 2

For `Tag`, write only `__repr__`. Then check with `str(Tag('x'))` in the REPL: it falls back to `__repr__`.

## Hint 3

```
class Book:
    __repr__: "Book(" + repr(title) + ", " + repr(author) + ")"
    __str__:  title + " by " + author
class Tag:
    __repr__: "Tag(" + repr(name) + ")"      # no __str__ at all
```
