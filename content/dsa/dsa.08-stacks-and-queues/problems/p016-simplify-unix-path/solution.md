## Approach

Walking a path is walking into and out of directories; the current location is a stack of names. A name is pushed, `..` pops (if there is anything to pop), and `.` or an empty piece changes nothing. Joining the stack with `/` and putting one `/` in front gives the canonical path; an empty stack gives `/`.

## Code

```python
def simplify_path(path):
    stack = []
    for part in path.split("/"):
        if part == "..":
            if stack:
                stack.pop()
        elif part and part != ".":
            stack.append(part)
    return "/" + "/".join(stack)
```

## Complexity

`O(n)` time and memory for a path of length `n` (`split` and `join` are both linear).

## Another way

The standard library does this for you: `posixpath.normpath("/a/./b/../../c/")` gives `'/c'`. But be careful: `normpath` keeps a leading `//` (POSIX allows it to mean something special), so `normpath("//a")` is `'//a'`, while this problem wants `'/a'`. Knowing the stack version means you know exactly what happens.
