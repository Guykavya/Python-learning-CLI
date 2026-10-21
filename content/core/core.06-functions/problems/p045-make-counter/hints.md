## Hint 1

Where does the count live, so that it survives between calls of the inner function?

## Hint 2

Without `nonlocal`, `count += step` in the inner function raises `UnboundLocalError`. Why?

## Hint 3

```
def make_counter(start=0, step=1):
    count = start
    def counter():
        nonlocal count
        count += step
        return count
    return counter
```
