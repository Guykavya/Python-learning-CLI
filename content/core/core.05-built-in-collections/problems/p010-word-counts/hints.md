## Hint 1

A dict maps each word to its count so far. Dicts keep insertion order, so first-seen order is free.

## Hint 2

`counts[w] = counts.get(w, 0) + 1` works for both new and old words.

## Hint 3

Loop `for word, n in counts.items(): print(f"{word}: {n}")`.
