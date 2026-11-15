## Hint 1

To link a new node after the last one you need to **hold** the last one. Which variable would you keep while building, and what must it point to after each new node is linked? Why would starting with a dummy node mean that even the first value is "linked after the previous node"?

## Hint 2

For `to_list`: copy `head` into a walking variable `cur`. Loop **while the node exists** (`while cur is not None`), not while the value is truthy.

## Hint 3

```
from_list:
    dummy = new node; tail = dummy
    for each v: tail.next = new node(v); tail = tail.next
    return dummy.next

to_list:
    out = []; cur = head
    while cur is not None: out.append(cur.val); cur = cur.next
    return out
```
