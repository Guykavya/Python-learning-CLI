## Approach

Split by **responsibility** and keep the dependencies pointing one way: `clean` (text cleaning) is at
the bottom, `stats` (counting) uses it, `reporting` (formatting) uses both. One-way arrows mean no
circular import. `__init__.py` only collects the public names; `__main__.py` holds the program part
(argv, stdin, print), which is what made the old script impossible to import.

## Code

The `FILES` dict, file by file (see `reference.py` for the full `solution.py`):

```python
# textkit/__init__.py
from .reporting import report
from .stats import count_words, top_words

__all__ = ["report", "count_words", "top_words"]
__version__ = "0.1.0"

# textkit/clean.py
STOP_WORDS = {"the", "a", "an", "and", "of", "to", "is"}

def normalise(text):
    return "".join(ch if ch.isalpha() or ch.isspace() else " " for ch in text.lower())

def words(text):
    return [w for w in normalise(text).split() if w not in STOP_WORDS]

# textkit/stats.py
from collections import Counter
from .clean import words

def count_words(text):
    return Counter(words(text))

def top_words(text, n=3):
    return count_words(text).most_common(n)

# textkit/reporting.py
from .clean import words
from .stats import top_words

def report(text, n=3):
    lines = [f"words: {len(words(text))}"]
    for word, count in top_words(text, n):
        lines.append(f"{word}: {count}")
    return "\n".join(lines)

# textkit/__main__.py
import sys
from .reporting import report

def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    n = int(argv[0]) if argv else 3
    print(report(sys.stdin.read(), n))

if __name__ == "__main__":
    main()
```

## Complexity

The package does exactly the same work as the script: O(L) for text of length L.

## Another way

Absolute imports (`from textkit.clean import words`) also work and some teams prefer them because
the line reads the same everywhere. Relative imports keep working if the package is renamed or moved
inside another package. Pick one style per project.

You could also keep `main()` in a `cli.py` module and make `__main__.py` just
`from .cli import main; main()`. That is the layout of the build project, p030.
