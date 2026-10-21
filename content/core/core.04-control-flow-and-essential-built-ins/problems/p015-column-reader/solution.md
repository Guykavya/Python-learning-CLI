## Approach

Column `c` is every `width`-th character starting at `c`. An outer loop over the columns and
an inner `range` with a step visit them in the right order.

## Code

```python
message = input()
width = int(input())
if width <= 0:
    print("invalid width")
else:
    result = ""
    for c in range(width):
        for pos in range(c, len(message), width):
            result += message[pos]
    print(result)
```

## Why the short last row needs no special code

`range(c, len(message), width)` stops before `len(message)`. If the last row has no
character in column `c`, the range simply has one fewer number. And if the width is larger
than the message, the extra columns have empty ranges.

## Another way

Slicing with a step does the inner loop for you: `result += message[c::width]`.
