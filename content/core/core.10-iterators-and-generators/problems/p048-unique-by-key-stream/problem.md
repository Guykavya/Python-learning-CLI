# First of each kind in an endless stream

Write two generator functions in `solution.py`.

## 1. `unique_by(iterable, key=None)`

Yield each item the **first** time its key is seen; skip later items with a key already seen.
The key is `key(item)`, or the item itself if `key` is `None`. Keep the original order. It must
work on an endless stream, so remember keys in a `set` and never read ahead.

```python
list(unique_by([3, 1, 3, 2, 1]))                           # [3, 1, 2]
list(unique_by(["Apple", "avocado", "Bean", "beet"], key=lambda w: w[0].lower()))
# ["Apple", "Bean"]
list(itertools.islice(unique_by(itertools.count(), key=lambda n: n % 4), 4))
# [0, 1, 2, 3]
```

## 2. `new_words(lines)`

`lines` is an iterable of text lines (it may be endless, like a chat). Yield every word the first
time it appears, ignoring case, **in lower case**.

A word is a piece of the line after `line.split()`, with the characters `.,!?;:"'()` removed from
**both ends only** (so `don't` keeps its apostrophe). If nothing is left (for example `"!!"`), skip
the piece. Other characters are not removed, so `"--"` is a word.

```python
lines = ["The cat sat.", "the CAT ran!", "(A) dog -- sat?"]
list(new_words(lines))
# ["the", "cat", "sat", "ran", "a", "dog", "--"]
```

Build `new_words` as a small pipeline: a generator that produces cleaned words from the lines,
then `unique_by` on top of it. Both must be lazy: reading the first new word must not read every line.
