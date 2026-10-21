## Hint 1

Remove duplicates first, or use a **set** for each group so repeats vanish.

## Hint 2

`groups.setdefault(len(w), set()).add(w)` builds a dict from length to a set of words.

## Hint 3

Loop over `sorted(groups)` (the lengths), and print `sorted(groups[length])`.
