## Approach

A list holds the queue in order. `append` adds to the back, `pop(0)` takes from the front,
`remove` takes someone out of the middle, and `in` checks for duplicates.

## Code

```python
queue = []
while True:
    parts = input().split()
    match parts:
        case ["end"]:
            break
        case ["join", name]:
            if name in queue:
                print(f"{name} is already in the queue")
            else:
                queue.append(name)
        case ["serve"]:
            if queue:
                print("Serving", queue.pop(0))
            else:
                print("Nobody to serve")
        case ["leave", name]:
            if name in queue:
                queue.remove(name)
            else:
                print(f"{name} is not in the queue")
        case ["show"]:
            print("Queue:", " ".join(queue) if queue else "(empty)")
```

## Complexity

`append` is O(1). `pop(0)`, `remove` and `in` are O(n) because they shift or scan the list.
For a counter queue with a few dozen people that is perfectly fine. For millions of operations
you would use `collections.deque` (core.17) for the front, plus a set for membership.
