## Approach

Work with references, not values. Each assignment to `.next` replaces one arrow. Ask, for each arrow you are about to replace, what it used to point at and whether anything else still points there.

## Model answer

See `answer.md`.

## What to check

- You said **why** the nodes are lost: the overwritten field was the only reference to them.
- You explained the cycle: line B reads `node.next` *after* it was changed, so it reads the new node itself.
- You gave the correct order **and** the general rule (save the old link first).
- You connected it to `nxt` in the reversal.

## Another way

Show it with a run instead of words. Print the list with a printer that has a limit (like `show` from the chapter) after the wrong order and after the right order:

```python
head = from_list([1, 2, 3])
new = ListNode(99)
head.next = new
new.next = head.next
print(show(head))          # 1 -> 99 -> 99 -> ... (stopped by the limit)

head = from_list([1, 2, 3])
new = ListNode(99)
new.next = head.next
head.next = new
print(show(head))          # 1 -> 99 -> 2 -> 3 -> None
```

Tuple assignment (`a.next, b = b, a.next`) does not remove the problem: the right-hand side is evaluated first, but the targets are then assigned left to right, so the order still matters when one target is used inside another. The two-line, save-first version is clearer.
