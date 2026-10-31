# Trace: running a package file directly vs with `-m`

"attempted relative import with no known parent package" is one of the most common Python errors.
This trace shows exactly when it happens and what Python does differently in the two ways of
running a file.

```text
project/
└── app/
    ├── __init__.py
    ├── helpers.py
    └── main.py
```

`app/__init__.py`:

```python
print("app package loaded")
```

`app/helpers.py`:

```python
print("helpers loaded as", __name__)


def shout(text):
    return text.upper() + "!"
```

`app/main.py`:

```python
print("main: __name__ =", __name__)
print("main: __package__ =", repr(__package__))

try:
    from . import helpers
    print("relative import worked")
except ImportError as e:
    print(type(e).__name__ + ":", e)
    import helpers

print(helpers.shout("hi"), "from", helpers.__name__)
```

Kavya runs two commands, both from inside `project/`:

```bash
python app/main.py
python -m app.main
```

In `answer.txt`, write the output of the first command, and then, directly below it, the output of
the second command. One line per printed line, no blank line between them. Neither command stops
with an error.

Two facts you need:

- `python some/folder/file.py` puts `some/folder` at the front of `sys.path`, and the file runs with
  `__package__` set to `None`.
- `python -m pkg.mod` puts the current folder at the front of `sys.path`, imports the package `pkg`
  first, and runs `mod` as `__main__` with `__package__` set to `"pkg"`.

## Example of the format

`print("x =", repr(None))` prints `x = None`, and `print("x =", repr("a"))` prints `x = 'a'`.
