## Approach

Each day has two phases: update every value, then remove the zeros. Never delete from the dict
while looping over it. Collect the keys to remove first, then delete them.

## Code

```python
fridge = {}
for _ in range(int(input())):
    item, days = input().split()
    fridge[item] = int(days)
for day in range(1, int(input()) + 1):
    for item in fridge:
        fridge[item] -= 1
    expired = [item for item, left in fridge.items() if left == 0]
    for item in expired:
        del fridge[item]
    if expired:
        print(f"Day {day}: expired {', '.join(expired)}")
    else:
        print(f"Day {day}: nothing expired")
print("Left:", ", ".join(fridge) if fridge else "nothing")
```

## Complexity

O(D × n) for D days and n items.

## Another way

Loop over a snapshot: `for item in list(fridge):` lets you delete safely inside the loop,
because the loop walks the list, not the dict.
