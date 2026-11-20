## Hint 1

Start the queue with the root `1`. Give it the next two list entries: `2` (left) and `3` (right). The queue is now `2, 3`. Take `2` out: its next two entries are `None` (no left child) and `4` (right child). Keep going: `3` takes the next two entries (`5` and `None`), then `4` takes the next two (both `None`), then `5` takes the next entry (`6`) as its left child.

## Hint 2

Once the tree is drawn, `describe` prints a node and then goes left and then right (preorder). The order of the lines is `1, 2, 4, 3, 5, 6`. For each node write the two children, or `None`. The leaves are the nodes whose line says `left=None right=None`; `leaf values` lists them from left to right.
