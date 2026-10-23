## Hint 1

`iter(f, stop)` calls `f()` with no arguments each time. When does it stop? Does the sentinel value itself appear in the results?

## Hint 2

Pass the function itself (no parentheses!) as the first argument. Wrap the result in `list(...)`.

## Hint 3

```
return list(iter(read, ""))
```
