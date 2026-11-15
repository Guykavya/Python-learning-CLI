## Hint 1

Dictionary method: first walk the list and create a copy of every node, storing `old_to_new[node] = copy` (plain nodes can be dictionary keys: they hash by identity). In a second walk set `copy.next = old_to_new.get(node.next)` and `copy.random = old_to_new.get(node.random)`.

## Hint 2

Interleaving method, no dictionary: insert each copy right **after** its original: `A -> A' -> B -> B' -> ...`. Now the copy of any node `X` is `X.next`. So for every original `A`: `A'.random = A.random.next` (if `A.random` exists).

## Hint 3

Separate the woven list in a third walk: for each original `cur`, `copy = cur.next`; `cur.next = copy.next` (restores the original); `copy.next = copy.next.next` if `copy.next` exists. Return the first copy, saved before separating.
