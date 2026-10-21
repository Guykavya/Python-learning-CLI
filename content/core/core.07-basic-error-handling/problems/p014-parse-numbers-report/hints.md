## Hint 1

Where must the `try` be so that one bad item does not stop the loop: around the loop, or inside it?

## Hint 2

There are two different failures. Only one of them is an exception. Which one needs `try`, and
which one needs an `if` after the conversion succeeded?

## Hint 3

```
for n, item in enumerate(items, start=1):
    try:
        value = float(item)
    except ValueError:
        errors.append(...); continue
    if not math.isfinite(value):
        errors.append(...); continue
    numbers.append(value)
```
