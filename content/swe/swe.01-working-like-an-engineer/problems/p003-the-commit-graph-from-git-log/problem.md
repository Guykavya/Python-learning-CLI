# The commit graph from `git log`

`git log --all --format="%h %p"` prints one line per commit: its short hash, then the hashes of its **parents** (`%p`). A root commit has no parent, a normal commit has one, a **merge** commit has two or more.

```text
m2 d e
e c
d m1
m1 b c
c a
b a
a
```

Write three functions (no recursion on the history: a project can have 100,000 commits):

```python
parse_graph(text)           # {sha: [parent, ...]}, in the order of the lines
merge_commits(graph)        # the commits with two or more parents, in the order of the graph
ancestors(graph, sha)       # a set: the commit itself and all commits reachable through parents
```

Blank lines are ignored. A parent that does not appear as a line of its own (a shallow clone) still belongs to the set of ancestors, but has no parents.

## Example

```python
g = parse_graph("m2 d e\ne c\nd m1\nm1 b c\nc a\nb a\na\n")
g["a"]                    # []
g["m1"]                   # ["b", "c"]
merge_commits(g)          # ["m2", "m1"]
ancestors(g, "d")         # {"d", "m1", "b", "c", "a"}
```
