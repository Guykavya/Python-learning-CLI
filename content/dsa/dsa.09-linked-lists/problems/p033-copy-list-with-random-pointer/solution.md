## Approach (interleaving)

The difficulty is finding "the copy of `A.random`". The interleaving trick stores that answer inside the list itself: put each copy directly after its original, so the copy of any original `X` is `X.next`.

1. **Weave**: `A -> A' -> B -> B' -> C -> C'`.
2. **Randoms**: for each original `A`, `A'.random = A.random.next`.
3. **Unweave**: restore every original's `next`, and link the copies to each other.

## Code

```python
class RNode:
    def __init__(self, val, next=None, random=None):
        self.val = val
        self.next = next
        self.random = random


def copy_random_list(head):
    if head is None:
        return None
    cur = head                               # 1. weave: A -> A' -> B -> B' -> ...
    while cur is not None:
        cur.next = RNode(cur.val, cur.next)
        cur = cur.next.next
    cur = head                               # 2. randoms: the copy of X.random is X.random.next
    while cur is not None:
        if cur.random is not None:
            cur.next.random = cur.random.next
        cur = cur.next.next
    new_head = head.next                     # 3. unweave and restore the original list
    cur = head
    while cur is not None:
        copy = cur.next
        cur.next = copy.next
        copy.next = copy.next.next if copy.next is not None else None
        cur = cur.next
    return new_head
```

## Complexity

`O(n)` time (three passes). Extra memory: only the `n` new nodes, which are the result; no dictionary.

## Another way

The dictionary method of the chapter is simpler and leaves the original untouched at every moment:

```python
def copy_random_list(head):
    old_to_new = {None: None}
    cur = head
    while cur is not None:
        old_to_new[cur] = RNode(cur.val)
        cur = cur.next
    cur = head
    while cur is not None:
        old_to_new[cur].next = old_to_new[cur.next]
        old_to_new[cur].random = old_to_new[cur.random]
        cur = cur.next
    return old_to_new[head]
```

It uses `O(n)` extra memory for the dictionary. Use it in real code; the interleaving version matters when memory is tight, and it is a good exercise in temporarily changing a structure and putting it back. (`copy.deepcopy(head)` also copies this structure correctly, but recursively, so it fails for long lists, and it hides the idea.)
