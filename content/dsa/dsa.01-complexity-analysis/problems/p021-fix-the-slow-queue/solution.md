## Finding the slow spots

| line | cost per run | runs | total |
|---|---|---|---|
| `while len(queue) > 0` | O(1) (`len` of a list is stored) | n | O(n) |
| `user = queue.pop(0)` | O(remaining items): all shift left | n | O(n^2) |
| `if user in seen` | O(number of users seen) | n | up to O(n^2) |
| `seen.append(user)` | amortised O(1) | up to n | O(n) |

So the starter is O(n^2) for two separate reasons. The test with only 10 users shows the first: `in seen` is cheap,
but 300000 `pop(0)` calls move about 4.5 * 10^10 items in total. The test with all-different users shows the second.
Fixing only one of them leaves one test failing.

## Code

```python
n = int(input())
queue = [int(x) for x in input().split()]

seen = set()
served = 0
repeat_visits = 0
for user in queue:
    if user in seen:
        repeat_visits += 1
    else:
        seen.add(user)
    served += 1

print("served", served)
print("new users", len(seen))
print("repeat visits", repeat_visits)
```

## Complexity

O(n) time on average and O(d) extra space for `d` different users. On this machine the fixed version handles 300000
visits in about 0.1 seconds; the starter needed over 30 seconds for the pop(0) part alone.

## Another way

If you really need a queue (items arrive while you are still removing them), use `collections.deque`, whose
`popleft()` is O(1). You will meet it in the stacks and queues module. Here a plain `for` loop is enough because
nothing is added during processing.

## The general lesson

When a program is slow, do not guess. List each line inside the main loop with its cost and how often it runs, as in
the table above. The slow parts are the lines whose cost grows with `n`.
