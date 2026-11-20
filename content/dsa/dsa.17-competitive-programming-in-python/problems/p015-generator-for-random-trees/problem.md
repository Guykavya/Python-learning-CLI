# Generator for random trees

A test generator for a graph problem must produce **valid** inputs, or your stress test finds only generator bugs. Write:

```python
random_tree(n, rng, shape="random")
```

It returns a list of `n - 1` edges `(u, v)`, with vertices `1..n`, forming a **tree**: connected, no cycles, no repeated edge, no loop `u == v`. `rng` is a `random.Random`; use it for **all** randomness, so that the same seed gives the same tree.

Shapes:

- `"random"`: a random tree where a new vertex attaches to a random earlier vertex.
- `"path"`: one long chain (the worst case for recursion).
- `"star"`: one centre joined to all others.

An unknown shape raises `ValueError`. For `n = 1` return `[]`.

Also required:

1. The **labels** are shuffled: vertex `1` is not always the root, and in the edge `(u, v)` either end may be the smaller number. A generator that always makes edges `(parent, child)` with `parent < child` hides bugs of solutions that assume this.
2. The list of edges is in **random order**.

## Example

```python
import random
print(random_tree(5, random.Random(1)))                 # four edges
print(random_tree(5, random.Random(1), shape="path"))   # a chain
```
