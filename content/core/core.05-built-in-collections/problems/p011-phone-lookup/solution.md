## Approach

A dict from name to number. Assigning to an existing key replaces the value, which gives the
"later wins" rule for free. Each lookup is O(1) on average.

## Code

```python
book = {}
for _ in range(int(input())):
    name, number = input().split()
    book[name] = number
for _ in range(int(input())):
    name = input().strip()
    if name in book:
        print(book[name])
    else:
        print(f"Not found: {name}")
```

## Complexity

O(n + m). Storing pairs in a list and searching it for each query would be O(n × m).
