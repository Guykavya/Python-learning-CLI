## Hint 1

First build a mapping from each parent id to the list of its children. Which key holds the roots?

## Hint 2

Visit nodes depth-first: a node, then its children. With a stack, push the children in **reverse** id order so the smallest id is popped first.

## Hint 3

```text
children[parent] = [(id, detail), ...]
stack = roots (parent 0) in reverse order, each with depth 0
while stack: pop (node, depth); output "  " * depth + detail; push its children (reverse order) with depth + 1
```
