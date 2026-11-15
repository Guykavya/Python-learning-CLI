## Hint 1

Picture `None <- 1    2 -> 3 -> None` in the middle of the work: the left part is already reversed (it starts at `prev`), the right part is not yet (it starts at `cur`). What does one step have to do to move node `2` from the right part to the left part?

## Hint 2

The step changes `cur.next`, which is the only link to the rest. So it must be saved first. Four lines: save, flip, move `prev`, move `cur`.

## Hint 3

```
prev = None; cur = head
while cur is not None:
    nxt = cur.next
    cur.next = prev
    prev = cur
    cur = nxt
return prev
```
