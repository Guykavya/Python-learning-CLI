## Hint 1

`split()` gives the words. `enumerate(..., start=1)` gives human word numbers.

## Hint 2

Clean each word with `.strip(".,!?").lower()` before comparing it with `target.lower()`.

## Hint 3

```
for n, word in enumerate(sentence.split(), start=1):
    if clean word == clean target:
        print found; break
else:
    print not found
```
