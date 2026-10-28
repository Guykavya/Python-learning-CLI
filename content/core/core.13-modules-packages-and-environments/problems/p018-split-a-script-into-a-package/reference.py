from pathlib import Path

FILES = {
    "textkit/__init__.py": '''"""textkit: small word statistics."""
from .reporting import report
from .stats import count_words, top_words

__all__ = ["report", "count_words", "top_words"]
__version__ = "0.1.0"
''',
    "textkit/clean.py": '''STOP_WORDS = {"the", "a", "an", "and", "of", "to", "is"}


def normalise(text):
    return "".join(ch if ch.isalpha() or ch.isspace() else " " for ch in text.lower())


def words(text):
    return [w for w in normalise(text).split() if w not in STOP_WORDS]
''',
    "textkit/stats.py": '''from collections import Counter

from .clean import words


def count_words(text):
    return Counter(words(text))


def top_words(text, n=3):
    return count_words(text).most_common(n)
''',
    "textkit/reporting.py": '''from .clean import words
from .stats import top_words


def report(text, n=3):
    lines = [f"words: {len(words(text))}"]
    for word, count in top_words(text, n):
        lines.append(f"{word}: {count}")
    return "\\n".join(lines)
''',
    "textkit/__main__.py": '''import sys

from .reporting import report


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    n = int(argv[0]) if argv else 3
    print(report(sys.stdin.read(), n))


if __name__ == "__main__":
    main()
''',
}


def split_script(root):
    """Write every file in FILES under root. Return the sorted relative paths."""
    root = Path(root)
    for rel, text in FILES.items():
        path = root / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
    return sorted(FILES)
