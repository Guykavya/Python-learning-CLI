## Approach

**Build** with a dummy node and a `tail` variable. The dummy is a fake node in front of the list, so the first real node is linked exactly like every other node: `tail.next = ListNode(v)`, then `tail` moves to the new node. At the end the real list starts at `dummy.next`, which is `None` when there were no values.

**Walk** with a separate variable `cur`, moving `cur = cur.next` until `cur` is `None`. Testing the node, not the value, keeps values like `0` and `None` in the output.

## Code

```python
class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


def from_list(values):
    dummy = ListNode()
    tail = dummy
    for v in values:
        tail.next = ListNode(v)     # link the new node after the current last one
        tail = tail.next            # the new node is now the last one
    return dummy.next               # skip the dummy; None for an empty list


def to_list(head):
    out = []
    cur = head
    while cur is not None:
        out.append(cur.val)
        cur = cur.next
    return out
```

## Complexity

Both are `O(n)` time. `from_list` creates `n` nodes (`O(n)` memory, which is the result itself); `to_list` uses `O(n)` for the output list and `O(1)` besides.

## Another way

Build **backwards**, pushing at the front: `head = None`, then for `v` in `reversed(values)`: `head = ListNode(v, head)`. No dummy and no tail are needed, because each new node simply points at the old head. It is just as fast; the dummy-and-tail pattern is worth learning because the same lines build the result of merge, partition and add-two-numbers later.
