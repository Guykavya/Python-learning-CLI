## Approach

A list is the natural home for "an unknown number of things, in order". Read with a
`while True` loop, stop at the sentinel `done`, and `append` everything else.

## Code

```python
items = []
while True:
    line = input()
    if line == "done":
        break
    items.append(line)
print(f"Items: {len(items)}")
if not items:
    print("The list is empty.")
for i, item in enumerate(items, start=1):
    print(f"{i}. {item}")
```

## Complexity

Each `append` is amortised O(1), so reading n items is O(n). Printing is O(n).

## Another way

`items = items + [line]` also works, but it builds a brand new list every time, which copies
all the old items. That makes the whole loop O(n²). `append` changes the list in place.
