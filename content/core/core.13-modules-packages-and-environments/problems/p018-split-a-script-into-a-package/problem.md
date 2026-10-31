# Split a script into a package

Kavya's script `textstats.py` grew to one long file. It works, but nothing in it can be imported
without running the whole program, and every function sits in one place:

```python
import sys
from collections import Counter

STOP_WORDS = {"the", "a", "an", "and", "of", "to", "is"}


def normalise(text):
    return "".join(ch if ch.isalpha() or ch.isspace() else " " for ch in text.lower())


def words(text):
    return [w for w in normalise(text).split() if w not in STOP_WORDS]


def count_words(text):
    return Counter(words(text))


def top_words(text, n=3):
    return count_words(text).most_common(n)


def report(text, n=3):
    lines = [f"words: {len(words(text))}"]
    for word, count in top_words(text, n):
        lines.append(f"{word}: {count}")
    return "\n".join(lines)


n = int(sys.argv[1]) if len(sys.argv) > 1 else 3
print(report(sys.stdin.read(), n))
```

Turn it into a package `textkit` with this layout:

```text
textkit/
├── __init__.py     the public API
├── __main__.py     the program part, so `python -m textkit [N]` works
├── clean.py        STOP_WORDS, normalise, words
├── stats.py        count_words, top_words
└── reporting.py    report
```

Rules:

1. Every function is defined in **exactly one** module (the one in the table). Other modules
   import it; they never copy it.
2. Modules inside the package import each other with **relative imports** (`from .clean import words`).
3. Importing any module of the package prints nothing and does not read the keyboard. Only
   `__main__.py` reads `sys.stdin` and `sys.argv`, and only when it runs as the program.
4. `textkit/__init__.py` re-exports the public API: `report`, `count_words` and `top_words`, lists exactly
   these three names in `__all__`, and sets `__version__ = "0.1.0"`.
5. `python -m textkit` reads the text from stdin and prints the report. An optional first argument
   is `N`, the number of top words (default 3). The output is the same as the old script's.

### What you write

The tests build the package in a temporary folder, so your `solution.py` must **write** the files.
Fill the dict `FILES` (relative path -> file content as a string). The function
`split_script(root)` that writes them is already in the starter.

## Example

```python
>>> split_script("out")
['textkit/__init__.py', 'textkit/__main__.py', 'textkit/clean.py', 'textkit/reporting.py', 'textkit/stats.py']
```

Then, from inside `out/`:

```bash
$ echo "The cat and the dog. A cat, a DOG, a cat!" | python -m textkit
words: 5
cat: 3
dog: 2
$ echo "The cat and the dog. A cat, a DOG, a cat!" | python -m textkit 1
words: 5
cat: 3
```

```python
>>> import textkit
>>> textkit.top_words("b a b c b c", 2)
[('b', 3), ('c', 2)]
>>> textkit.stats.count_words.__module__
'textkit.stats'
```

(In `top_words`, the stop word `a` is removed first.)

Watch out: do not name the module `report.py`. `from .report import report` in `__init__.py` would
replace the submodule attribute `textkit.report` with the function of the same name. That is why the
module is called `reporting.py`.
