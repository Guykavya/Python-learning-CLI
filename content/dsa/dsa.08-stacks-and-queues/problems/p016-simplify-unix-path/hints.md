## Hint 1

Split the path on `/`. The pieces are names, `.`, `..`, or empty strings (from `//` and the ends). The directories you are "inside" form a stack: entering pushes, `..` pops. What do `""` and `.` do?

## Hint 2

```
for part in path.split("/"):
    if part == "..": pop if the stack is not empty
    elif part and part != ".": push part
return "/" + "/".join(stack)
```
