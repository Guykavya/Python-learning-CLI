## Hint 1

The program needs two things: the order of first appearance, and a fast answer to "have I already printed
this value?". Can one structure do both well?

## Hint 2

Use two: a list `result` for the order, and a set `seen` for the fast membership test. Add every new value to both.

## Hint 3

```
for x in a:
    if x not in seen:
        add x to seen
        append x to result
```
