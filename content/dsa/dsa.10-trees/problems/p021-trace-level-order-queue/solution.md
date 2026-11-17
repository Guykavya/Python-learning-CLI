## Approach

Keep the queue as a row of values on paper. For each pop: remove the front, append its existing children left then right, and write the queue.

## Expected output

```text
level 1: size 1
pop 8: queue=[3, 10]
level 2: size 2
pop 3: queue=[10, 1, 6]
pop 10: queue=[1, 6, 14]
level 3: size 3
pop 1: queue=[6, 14]
pop 6: queue=[14]
pop 14: queue=[]
[[8], [3, 10], [1, 6, 14]]
```

## Why

| round | queue at the start | pops | queue after the last pop |
|---|---|---|---|
| level 1 | `[8]` | 8 | `[3, 10]` |
| level 2 | `[3, 10]` | 3, 10 | `[1, 6, 14]` |
| level 3 | `[1, 6, 14]` | 1, 6, 14 | `[]` |

At the start of every round the queue holds exactly the nodes of one level, and nothing else: all the nodes of the previous level are gone, and their children, the next level, are the only ones in the queue. That is why `range(len(queue))` finds the end of the level: the size is read once, before the children of this level are added to the back. The queue is largest at level 3 (three nodes), the widest level. The loop ends when a level adds no children.
