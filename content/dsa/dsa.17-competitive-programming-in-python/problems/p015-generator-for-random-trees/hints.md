## Hint 1

How can you be sure that adding an edge never makes a cycle and keeps the graph connected? What if every new vertex is joined to **exactly one** earlier vertex?

## Hint 2

Build the tree on positions `0..n-1` first: position `i` gets a parent `p[i] < i`. For `"random"`, `p[i] = rng.randrange(i)`; for `"path"`, `p[i] = i - 1`; for `"star"`, `p[i] = 0`. Then relabel the positions with a random permutation of `1..n`.

## Hint 3

```text
parent for i in 1..n-1  (by shape)
perm = shuffled [1..n]
edges = [(perm[parent[i]], perm[i]) for i in 1..n-1]
swap the two ends of an edge with probability 1/2
shuffle the list of edges
```
