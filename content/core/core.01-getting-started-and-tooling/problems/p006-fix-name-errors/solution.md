## Approach

A `NameError` means Python looked up a name and found nothing with that exact
spelling. Compare the name in the message with the names you defined.

## Code

```python
print("Course:", course)
print("Semester:", semester)
print("College:", college_name)
```

## The three bugs

1. `Print` has a capital P. The built-in function is `print`.
2. `semster` is missing an `e`.
3. `collegename` is missing the underscore of `college_name`.

Python 3.10+ often adds `Did you mean: 'print'?` to the message. Use it, but
still understand why.

## Another way

None really: names must match exactly. An editor with linting (Pylance or Ruff
in VS Code) underlines undefined names before you even run the file.
