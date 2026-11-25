## Hint 1

Walking top to bottom, what single number do you need to remember to decide whether the next cell is "out of order"? Is it the previous cell's count, or something else? (Try `5, 3, 4`.)

## Hint 2

```text
largest = 0 (or None)
for index, cell in enumerate(cells):
    if cell is not code: continue
    count = cell["execution_count"]
    if count is None: report index; continue
    if count <= largest: report index
    else: largest = count
```
