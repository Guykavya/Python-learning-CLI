## Approach

Chunks start every `k` positions. A slice that runs past the end is simply cut short, so the
last chunk needs no special handling.

## Code

```python
items = input().split()
k = int(input())
chunks = [items[s:s + k] for s in range(0, len(items), k)]
if not chunks:
    print("No chunks")
for i, chunk in enumerate(chunks, start=1):
    print(f"{i}: {' '.join(chunk)}")
```

## Complexity

O(n): every item is copied into exactly one chunk.
