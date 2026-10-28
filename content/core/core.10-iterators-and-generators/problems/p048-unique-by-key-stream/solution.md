## Approach

A set answers "seen before?" in O(1), and a generator yields each new item at once, so the output
keeps the input order and nothing is read ahead. The key function decides what "the same" means
while the item itself is what we yield. `new_words` is a two-stage pipeline: one stage turns lines
into clean words, the next keeps the first of each. Each stage is lazy, so the whole pipeline is lazy.

## Code

```python
from collections.abc import Callable, Hashable, Iterable, Iterator

PUNCTUATION = ".,!?;:\"'()"


def unique_by(iterable: Iterable[object], key: Callable[[object], Hashable] | None = None) -> Iterator[object]:
    seen = set()
    for item in iterable:
        k = item if key is None else key(item)
        if k not in seen:
            seen.add(k)
            yield item


def clean_words(lines: Iterable[str]) -> Iterator[str]:
    for line in lines:
        for piece in line.split():
            word = piece.strip(PUNCTUATION).lower()
            if word:
                yield word


def new_words(lines: Iterable[str]) -> Iterator[str]:
    return unique_by(clean_words(lines))
```

`new_words` returns a generator made by `unique_by`. It does not need its own `yield`.

## Complexity

O(1) average time per item. Memory grows with the number of **different keys** seen. On an endless
stream with endless new keys, the set grows for ever; that is the real limit of this idea.

## Another way

`dict.fromkeys(iterable)` keeps the first of each value in order, but it reads the whole input, so it
is not lazy and cannot handle an endless stream. If memory is a worry, you can only remember the last
N keys (a "window"), accepting that an old key may be yielded again.
