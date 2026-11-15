## Approach

Move `slow` one step and `fast` two steps per round. If `fast` (or `fast.next`) becomes `None`, the chain ends, so there is no cycle. If there is a cycle, compare the nodes after every move: they will be the same node after at most `n` rounds.

## Why it works

Without a cycle the chain ends, `fast` reaches the end first, and the loop stops with `False`. With a cycle, both pointers eventually enter it and then never leave. Look at the distance from `slow` forward to `fast` along the cycle (length `L`). Each round `fast` moves 2 and `slow` moves 1, so the distance **shrinks by exactly 1**. A distance that shrinks by 1 cannot jump over 0: after at most `L - 1` rounds it is 0, which means the two pointers are on the same node. The tail before the cycle is crossed by `slow` within `n` steps, so the whole check takes `O(n)` rounds. (If `fast` moved 3 steps, the distance would shrink by 2 and could skip from 1 to `L - 1`; it still meets eventually, but the simple proof is lost.)

## Code

```python
def has_cycle(head):
    slow = fast = head
    while fast is not None and fast.next is not None:
        slow = slow.next
        fast = fast.next.next
        if slow is fast:             # same node, not just equal values
            return True
    return False
```

## Complexity

`O(n)` time, `O(1)` extra memory (two variables).

## Another way

Keep a `set` of the node ids you have seen; a repeated id means a cycle. It is easy to write and also `O(n)` time, but it stores `n` entries (`O(n)` memory), which is what the test with 100,000 nodes measures. Marking visited nodes (`node.seen = True`) also works on plain classes, but it changes the data you were given and fails on nodes with `__slots__`.
