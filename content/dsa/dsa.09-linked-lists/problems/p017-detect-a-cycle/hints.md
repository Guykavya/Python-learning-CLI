## Hint 1

Without a cycle, the faster pointer reaches the end first. So what must the loop condition be, so that `fast = fast.next.next` never crashes? What do you return when the loop ends normally?

## Hint 2

With a cycle, both pointers are eventually inside it, and the loop never ends by itself. Inside the cycle, `fast` gains one node on `slow` per round. So after each move, compare: are they the **same node**?

## Hint 3

```
slow = fast = head
while fast is not None and fast.next is not None:
    slow = slow.next; fast = fast.next.next
    if slow is fast: return True
return False
```
