## Hint 1

Do not change how the queue works. A level is still found from left to right. What do you have to do to a **finished** level list to make it go right to left, and for which levels?

## Hint 2

Count the levels from 0. The levels with an odd number are reversed: `level[::-1]` or `level.reverse()`. Keep a counter (or use `len(levels) % 2`) to know which level you are on.

## Hint 3

```
levels, queue = [], deque([root]) (if root)
while queue:
    level = [ values of the len(queue) nodes, children appended left then right ]
    if len(levels) % 2 == 1:
        level.reverse()
    levels.append(level)
return levels
```
