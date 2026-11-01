# Explain: code that only works on CPython

Now that you know how CPython works inside, you can also spot code that works **by accident**:
it depends on a CPython implementation detail, not on a rule of the Python language. Such code
passes every test on your laptop and then breaks on PyPy, on the next Python version, in another
process, or with different data.

A teammate's pull request contains these four pieces of code. Each one "works" when they try it.

**Snippet A: checking a role**

```python
def can_delete(user):
    role = user["role"]          # loaded from a JSON file or a database
    return role is "admin"       # (Python even warns here: SyntaxWarning)
```

**Snippet B: saving a report and reading it back**

```python
def save_and_check(path, text):
    open(path, "w").write(text)
    return open(path).read() == text
```

**Snippet C: limiting a cache's memory**

```python
import sys

cache = {}

def remember(key, value):
    if sys.getsizeof(cache) > 50_000_000:     # "about 50 MB"
        cache.clear()
    cache[key] = value
```

**Snippet D: a stable "first tag" for a filename**

```python
def filename_for(tags):
    unique = set(tags)                  # e.g. ["sql", "python", "git", "python"]
    return list(unique)[0] + ".txt"     # the team's tests expect "git.txt"
```

Write `answer.md` (about 350 to 500 words). For **each** snippet:

1. Name the CPython detail it relies on (interning, reference counting, object sizes, hash order...).
2. Say concretely when it breaks: on PyPy, on another Python version, in another run, or with
   other data. Give an example input or situation.
3. Give the fix that relies only on what the language **guarantees**, with the key line of code.

Finish with two or three sentences: **how can you tell** a language guarantee from an
implementation detail when you read the documentation?

**Example of the level of detail expected (a different snippet)**

> *`if len(items) is 0:`* relies on CPython's small-int cache: ints from -5 to 256 are shared
> objects, so `is` happens to work for 0. Python does not promise this (another implementation,
> or a bigger number such as `len(items) is 1000`, gives `False`). Fix: `if len(items) == 0:` or
> simply `if not items:`.
