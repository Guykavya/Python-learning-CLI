## Hint 1

Draw the path between two nodes: it goes **up** from `p` to the lowest common ancestor, then **down** to `q`. How many edges is the way up? (Compare the depths of `p` and of the LCA.) How many edges is the way down?

## Hint 2

`distance = depth(p) + depth(q) - 2 * depth(lca)`. You need the LCA (problem 47) and the depth of three nodes. One way: a parent map (a dictionary `node -> parent`), then count the steps up to the root for each node. Another way: one recursive call that returns the depth at which each of `p` and `q` was found.

## Hint 3

```
parent = {root: None}                    # fill it with a loop (a stack) over the tree
depth(x): count the steps from x up to the root
a = lca(root, p, q)
return depth(p) + depth(q) - 2 * depth(a)
```
