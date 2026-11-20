# Maximum path sum

A **path** here may start and end at **any** nodes and may go up and then down: it has one highest node, with a branch going down on the left and/or on the right. It uses each node at most once and has at least one node. Write `max_path_sum(root)` that returns the **largest sum of the values** on any path. The tree is not empty. Values can be negative.

## Example

```python
>>> max_path_sum(build([1, 2, 3]))                        # 2 - 1 - 3
6
>>> max_path_sum(build([-10, 9, 20, None, None, 15, 7]))  # 15 - 20 - 7 (the root is not used)
42
>>> max_path_sum(build([-3]))
-3
>>> max_path_sum(build([2, -1]))                          # just the 2
2
```

`build([...])` in the examples is the tests' helper: a level-order list where `None` means "no node here" (it is the chapter's `build_tree`, section 2).

## Constraints

- Up to a few thousand nodes, depth below the recursion limit. `O(n)` time.

## Think about

The function must **return** one thing to its parent and **record** another. A parent can extend only **one** branch of its child (a path that has already bent at the child cannot bend again). What is the best sum of a path that starts at this node and goes straight down? What is the best path that bends at this node? Why can you not start `best` at `0`?
