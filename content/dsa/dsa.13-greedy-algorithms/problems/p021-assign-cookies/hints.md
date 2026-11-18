## Hint 1

Sort both lists. Take the smallest cookie. If it cannot make even the least greedy child happy, can it make anyone happy? If it can, who is the cheapest child to satisfy with it?

## Hint 2

Keep one pointer `child` into the sorted greed list (the least greedy child who is still unhappy). Walk through the sorted cookies once. A cookie that is big enough for `greed[child]` makes that child happy and moves the pointer; a cookie that is too small is useless for everyone left, so skip it.

## Hint 3

```
greed = sorted(greed); sizes = sorted(sizes)
child = 0
for cookie in sizes:
    if child < len(greed) and cookie >= greed[child]:
        child += 1
return child
```
