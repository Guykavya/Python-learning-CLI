## Approach

Build the result after a dummy node with a `tail` pointer. While both lists have nodes, link the smaller front node after `tail` and move that list forward. On equal values take the node from `a` (stability). When one list is used up, the other one's remaining nodes are already sorted and linked to each other, so one assignment attaches them all.

## Code

```python
def merge_two(a, b):
    dummy = ListNode()
    tail = dummy
    while a is not None and b is not None:
        if b.val < a.val:                # strictly smaller: on a tie, a goes first (stable)
            tail.next = b
            b = b.next
        else:
            tail.next = a
            a = a.next
        tail = tail.next
    tail.next = a if a is not None else b    # one list is used up: link the rest of the other
    return dummy.next
```

## Complexity

`O(n + m)` time; each node is linked once. `O(1)` extra memory (one dummy). The last line is `O(1)`, not a loop.

## Another way

Recursion: the smaller head, followed by the merge of the rest: `if a.val <= b.val: a.next = merge(a.next, b); return a`. It is short, but uses one frame per node and fails for long lists in Python. Merging is the core step of merge sort (problem 25) and of merging `k` lists (problem 24).
