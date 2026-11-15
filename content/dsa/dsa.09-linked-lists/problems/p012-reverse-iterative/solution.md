## Approach

Split the list into a reversed part (starting at `prev`, initially empty: `None`) and a rest (starting at `cur`). Each step moves one node from the rest to the front of the reversed part: save `cur.next`, point `cur` at `prev`, then advance both. When the rest is empty, `prev` is the new head. The old head pointed at `prev = None` in the first step, so it correctly becomes the tail.

## Code

```python
def reverse_list(head):
    prev = None
    cur = head
    while cur is not None:
        nxt = cur.next          # 1. save the rest of the list
        cur.next = prev         # 2. flip the arrow
        prev = cur              # 3. the reversed part now starts at cur
        cur = nxt               # 4. move on
    return prev
```

## Complexity

`O(n)` time, one pass; `O(1)` extra memory (three variables). No node is created and no value changes.

## Another way

Recursion (problem 13) gives a short, elegant version, but it uses one stack frame per node, so it fails beyond about 1,000 nodes in Python. Another way: push every node onto a Python list and relink them from the end; that is `O(n)` extra memory. Swapping **values** instead of arrows (`a[i], a[n-1-i]`) is not a reversal of the list structure, and with a singly linked list it is not even easy.
