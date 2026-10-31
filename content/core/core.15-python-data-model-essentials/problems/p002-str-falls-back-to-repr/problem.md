# str() falls back to repr()

Python has two text forms. `repr(x)` is for programmers (unambiguous, like code). `str(x)` is for
readers (friendly). If a class defines only `__repr__`, then `str(x)` uses it too. The reverse is **not**
true: defining only `__str__` does not change `repr`.

Write two classes in `solution.py`:

- `Book(title, author)`:
  - `repr(b)` is `Book('Dune', 'Frank Herbert')`
  - `str(b)` is `Dune by Frank Herbert`
- `Tag(name)` defines **only** `__repr__`: `repr(t)` is `Tag('python')`. Do **not** write `__str__`
  for `Tag`; show that `str(t)` gives the same text anyway.

**Example**

```python
b = Book("Dune", "Frank Herbert")
print(b)            # Dune by Frank Herbert
print([b])          # [Book('Dune', 'Frank Herbert')]    (containers use repr)
t = Tag("python")
print(t)            # Tag('python')
```
