## Hint 1

List the cases for each method with the two pictures "empty list" and "one node". For `push_back` on an empty list, what must `head` be afterwards? For `pop_front` of the only node, what must `tail` be afterwards?

## Hint 2

`remove` needs the node **before** the match to unlink it, so walk with two variables `prev` and `cur`. Two extra cases: the match is the head (`prev is None`), and the match is the tail (`cur is self.tail`: the tail moves back to `prev`).

## Hint 3

```
push_back(val):
    node = ListNode(val)
    if tail is None: head = tail = node
    else: tail.next = node; tail = node
    size += 1

pop_front():
    if head is None: raise IndexError
    node = head; head = node.next
    if head is None: tail = None
    size -= 1; return node.val

__iter__: cur = head; while cur is not None: yield cur.val; cur = cur.next
```
