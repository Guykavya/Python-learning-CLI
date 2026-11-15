## Hint 1

Scan the grid once: put every `2` into the queue and count the fresh oranges. If there are none, the answer is 0. Then process the queue **level by level**: everything that is in the queue at the start of a minute rots its fresh neighbours during that minute.

## Hint 2

```
minutes = 0
while queue and fresh:
    for _ in range(len(queue)):           # one level = one minute
        r, c = queue.popleft()
        for each neighbour that is 1:
            set it to 2; fresh -= 1; queue.append(neighbour)
    minutes += 1
return minutes if fresh == 0 else -1
```

Setting the neighbour to `2` at once is the "mark when you enqueue" rule.
