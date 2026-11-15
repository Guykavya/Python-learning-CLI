## Approach

The same backtracking as the list version, but each answer is handed out with `yield` instead of being stored. Python pauses the whole chain of generator frames after each `yield`, so only the part of the tree that the caller asks for is ever explored. Copies (`path[:]`) keep the yielded lists independent of the shared `path`.

## Code

```python
def iter_subsets(items):
    path = []

    def go(start):
        yield path[:]
        for i in range(start, len(items)):
            path.append(items[i])     # choose
            yield from go(i + 1)      # explore, passing answers outwards
            path.pop()                # un-choose

    yield from go(0)
```

## Complexity

`O(n)` extra memory at any time (the path and up to `n` paused frames), and `O(n)` work per yielded subset (the copy). The total for all subsets is the same as the list version, but you only pay for the ones you take.

## Another way

An explicit stack of `(start, path)` pairs (chapter section 15) can also be turned into a generator: pop a pair, `yield path`, push the children in reverse order so that the smallest index is popped first.
