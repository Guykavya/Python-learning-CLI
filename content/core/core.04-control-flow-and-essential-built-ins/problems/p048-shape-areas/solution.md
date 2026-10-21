## Approach

`match` on the words. One case per valid shape; one case per shape for wrong lengths;
a general case for unknown words. Compute an area (or `None`), then handle it in one place.

## Code

```python
import math

count = 0
total = 0.0
while True:
    words = input().split()
    if words == ["done"]:
        break
    area = None
    sizes = []
    match words:
        case []:
            continue
        case ["circle", r]:
            sizes = [float(r)]
            area = math.pi * sizes[0] ** 2
        case ["rect", w, h]:
            sizes = [float(w), float(h)]
            area = sizes[0] * sizes[1]
        case ["square", s]:
            sizes = [float(s)]
            area = sizes[0] ** 2
        case ["triangle", b, h]:
            sizes = [float(b), float(h)]
            area = sizes[0] * sizes[1] / 2
        case ["circle", *_]:
            print("Usage: circle R")
        case ["rect", *_]:
            print("Usage: rect W H")
        case ["square", *_]:
            print("Usage: square S")
        case ["triangle", *_]:
            print("Usage: triangle B H")
        case [word, *_]:
            print(f"Unknown shape: {word}")
    if area is not None:
        if min(sizes) <= 0:
            print("Sizes must be positive")
        else:
            print(f"{words[0]} area: {area:.2f}")
            count += 1
            total += area
print(f"Shapes: {count}")
print(f"Total area: {total:.2f}")
```

## Why exact cases come before the `*_` cases

`["rect", *_]` also matches `["rect", "3", "4"]`. Order matters: exact shapes first, then the
catch-all usage cases.

## About `sizes = [float(w), float(h)]`

Writing values inside square brackets makes a small list so that `min(sizes)` can check them
all at once. Lists are the next chapter; this is all you need of them here.

## Another way

Check positivity inside each case with a guard: `case ["rect", w, h] if float(w) > 0 and float(h) > 0:`.
That needs a second case per shape for the non-positive version.
