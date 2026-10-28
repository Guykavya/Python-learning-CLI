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
