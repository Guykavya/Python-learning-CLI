# Subsets as a generator

Write a **generator function** `iter_subsets(items)` that yields the subsets of the sequence `items` (a list, tuple or `range` of different values) **one at a time**, as lists, in exactly this order: the order of `subsets` from chapter section 6, view 2 (every node of the "choose the next item from the rest" tree, in preorder).

```python
>>> list(iter_subsets([1, 2, 3]))
[[], [1], [1, 2], [1, 2, 3], [1, 3], [2], [2, 3], [3]]
```

It must be **lazy**: asking for the first three subsets of `range(40)` must be instant, although there are `2^40` (about a trillion) of them.

```python
>>> it = iter_subsets(range(40))
>>> next(it), next(it), next(it)
([], [0], [0, 1])
```

Every yielded list must be a separate copy: changing a list you received, or asking for the next subset, must not change lists you already have.

## Constraints

- Use `yield` / `yield from` (core.10 and chapter section 15). Do not build a list of all subsets.

## Think about

In the list version, `result.append(path[:])` records a node. What replaces it in a generator? And how do the answers of the inner call reach the caller?
