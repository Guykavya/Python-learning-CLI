## Hint 1

What is the reversed version of an empty list, and of a list with one node? Those are the base cases: return `head` unchanged.

## Hint 2

For a longer list, trust the recursive call: `new_head = reverse_rec(head.next)` reverses everything after `head` and returns its new first node. Draw the picture right after that call for `1 -> 2 -> 3`. Node `1` still points at node `2`; where is node `2` now in the reversed rest?

## Hint 3

```
if head is None or head.next is None: return head
new_head = reverse_rec(head.next)
head.next.next = head
head.next = None
return new_head
```
