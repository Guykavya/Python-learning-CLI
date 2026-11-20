## Hint 1

The nine inserts give `50` with children `30` and `70`. `30` has `20` and `40`; `40` has the left child `35`. `70` has `60` and `80`; `60` has the right child `65`. As a list this is the `start` line: `[50, 30, 70, 20, 40, 60, 80, None, None, 35, None, None, 65]`. Delete `40` first: it has only a left child, `35`, so `35` takes its place under `30`.

## Hint 2

Delete `70`: it has two children, `60` and `80`. The smallest key of its right subtree is `80` itself (it has no left child). The value `80` is copied into the node, and the old `80` leaf is removed, so the node (now `80`) keeps the left subtree `60 - 65` and has no right child. Delete `50`, the root: the smallest key of the right subtree (rooted at `80`) is `60`. Copy `60` into the root, then delete `60` from the right subtree: the node `60` has no left child, so its right child `65` replaces it, as the left child of `80`.
