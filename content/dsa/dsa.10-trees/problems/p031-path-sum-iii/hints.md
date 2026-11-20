## Hint 1

Take the running sum along the path from the root to the current node: `5, 8, 11, ...`. A downward path that ends at the current node is "a stretch of this root path". Its sum is `running_now - running_before_the_stretch`. So you need to know how many earlier points on this root path have `running_before = running_now - target`. Which dictionary answers that in `O(1)`?

## Hint 2

Keep `counts[s]` = how many times the running sum `s` appeared on the **current** root path. Start with `counts = {0: 1}` (the empty stretch before the root: it lets a path that starts at the root count). At a node: add its value to `running`, **first** add `counts.get(running - target, 0)` to the answer, **then** do `counts[running] += 1`, recurse into both children, and when both are done do `counts[running] -= 1` so a sibling branch does not see this path (this is the backtracking of the paths section).

## Hint 3

```
counts = {0: 1}; total = 0
def go(node, running):
    if node is None: return
    running += node.val
    total += counts.get(running - target, 0)      # paths that END here
    counts[running] = counts.get(running, 0) + 1  # choose
    go(node.left, running); go(node.right, running)
    counts[running] -= 1                          # un-choose
go(root, 0)
```
