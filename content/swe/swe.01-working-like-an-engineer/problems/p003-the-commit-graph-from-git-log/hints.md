## Hint 1

Each line, split on whitespace, gives a list of tokens. Which token is the commit, and what are the rest?

## Hint 2

`ancestors` is a graph search going from a commit to its parents. Use a stack (a list) and a set of seen commits instead of recursion.

## Hint 3

```text
seen = {sha}; stack = [sha]
while stack:
    c = stack.pop()
    for p in graph.get(c, []):
        if p not in seen: seen.add(p); stack.append(p)
return seen
```
