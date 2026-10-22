## Approach

The `while` loop is exactly what `for item in items:` does: call `iter` once, call `next` again and again, stop when `StopIteration` is raised. When the iterator is exhausted, it stays exhausted. `next(it, default)` returns the default instead of raising. `iter(it)` on an iterator returns the same object.

## Output

```text
got a
got b
got c
done
empty
[]
True
list_iterator
```

## Complexity

O(n) for n items.

## Another way

Replace the whole `while` loop with `for item in items: print('got', item)` and you get the same `got` lines, but not the `done` line, because `for` swallows `StopIteration` silently.
