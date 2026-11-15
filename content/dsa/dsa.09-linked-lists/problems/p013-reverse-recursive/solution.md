## Approach

Base case: zero or one node is its own reversal. Otherwise reverse the rest (`head.next` onwards). That call returns the new head (the old last node), and it leaves `head.next` pointing at the old second node, which is now the **last** node of the reversed rest. So `head.next.next = head` attaches `head` at the end, and `head.next = None` makes it the tail. Every level returns the same `new_head`, passed up unchanged from the deepest call.

## Code

```python
def reverse_rec(head):
    if head is None or head.next is None:      # 0 or 1 node: already reversed
        return head
    new_head = reverse_rec(head.next)          # reverse everything after head
    head.next.next = head                      # the old next now points back at head
    head.next = None                           # head becomes the tail
    return new_head
```

## Complexity

`O(n)` time. `O(n)` extra memory: one stack frame per node, held until the deepest call returns. That is why Python raises `RecursionError` for a few thousand nodes (`sys.getrecursionlimit()` is 1,000 by default), and why the loop of problem 12 is the version to use on real data.

## Another way

A recursive helper with an accumulator mirrors the loop exactly: `helper(cur, prev)` returns `prev` when `cur` is `None`, else it saves `nxt = cur.next`, sets `cur.next = prev` and returns `helper(nxt, cur)`. Some languages turn such *tail calls* into a loop automatically; Python does not, so it still uses `n` frames.
