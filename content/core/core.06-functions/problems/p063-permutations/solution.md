## Approach

Choose each position's item in turn to go first; the rest of the ordering is any ordering of the
remaining items, which the recursive call supplies. Building `rest` with slicing never touches
the input. For anagrams, a set comprehension removes duplicate strings and `sorted` returns a list.

## Code

```python
def permutations(items):
    """Return every ordering of items (as lists), first-item-first order. Recursive."""
    if not items:
        return [[]]
    result = []
    for i in range(len(items)):
        rest = items[:i] + items[i + 1:]
        for p in permutations(rest):
            result.append([items[i]] + p)
    return result


def anagrams(word):
    """Return the sorted list of distinct rearrangements of word."""
    return sorted({"".join(p) for p in permutations(list(word))})
```

## Complexity

O(n × n!) time and output size; recursion depth n.

## Another way

Backtracking with one shared list and a `used` list of booleans: append an item, recurse, then pop
it. It avoids building many temporary lists, and it is the standard technique in the DSA modules.
`itertools.permutations` is the library version.
