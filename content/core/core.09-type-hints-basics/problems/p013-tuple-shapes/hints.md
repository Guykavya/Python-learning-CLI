## Hint 1

Which results always have exactly two parts, with a fixed meaning for each position? Those are fixed tuples. Which one is "a collection of ints that can have any length"?

## Hint 2

`sorted(...)` returns a list, and a set loses the order. How do you get a **tuple** back from a sorted list? For `split_name`, `text.split(maxsplit=1)` gives a list with 0, 1 or 2 parts. Handle each length.

## Hint 3

```
def min_max(numbers): return min(numbers), max(numbers)
def sorted_unique(numbers): return tuple(sorted(set(numbers)))
def split_name(full):
    parts = full.split(maxsplit=1)
    if len(parts) == 0: return "", ""
    if len(parts) == 1: return parts[0], ""
    return parts[0], parts[1]
def head_tail(numbers):
    if not numbers: return None, ()
    return numbers[0], numbers[1:]
```
