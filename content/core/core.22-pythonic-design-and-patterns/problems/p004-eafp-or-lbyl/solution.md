## Approach

Replace every "check, then use" pair with one step that does both:

1. `dict.get(key, default)` is one lookup that already knows what to do when the key is missing.
2. `dict.setdefault(key, [])` returns the existing list, or stores and returns a new one.
3. For files, the only reliable test is to open it. Between `exists()` and `open()` another
   program can delete the file. Catch `FileNotFoundError` only: `PermissionError` and others are
   real problems that the caller should see.
4. `getattr(obj, "name", None)` reads the attribute once.
5. `int(text)` is the real definition of "a whole number". `isdigit()` is a guess that fails
   for signs and spaces.

## Code

```python
def get_port(config):
    return int(config.get("port", 8080))


def add_word(index, word, line_no):
    index.setdefault(word, []).append(line_no)


def read_or_default(fs, path, default=""):
    try:
        with fs.open(path) as f:
            return f.read()
    except FileNotFoundError:
        return default


def display_name(obj):
    name = getattr(obj, "name", None)
    return "ANON" if name is None else name.upper()


def parse_int(text):
    try:
        return int(text)
    except ValueError:
        return None
```

## Complexity

All O(1) except reading the file (O(size)). The gain is not speed; it is correctness (no race, no
wrong check) and one lookup instead of two.

## Another way

`get_port` and `add_word` also work with `try: ... except KeyError:`. For counting words many
times, `collections.defaultdict(list)` removes the problem, but only when you own the dict (here the
caller passes it in). Keep `try` blocks **small**: wrapping a long body in `except AttributeError`
can hide a bug inside the body.
