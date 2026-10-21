# Skip comment lines

Read lines until a line that is exactly `END`. Ignore every line that is **blank** (empty or
only spaces) or whose first non-space character is `#`. Print each kept line, stripped,
numbered from 1:

```
1: <line>
2: <line>
```

Finally print `Kept K of N lines`, where `N` counts all lines before `END`.

**Example**

Input:
```
# settings
width = 10

  # indented comment
height = 4
END
```
Output:
```
1: width = 10
2: height = 4
Kept 2 of 5 lines
```

Use `continue` to skip unwanted lines.
