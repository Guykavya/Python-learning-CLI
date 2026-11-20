## Hint 1

Two questions decide everything: is `other` part of the history of `current`? Is `current` part of the history of `other`? What follows from each answer?

## Hint 2

Compute `ancestors(graph, x)`: the set of `x` and everything reachable by following parents (use a stack, not recursion). Ask the first question first: if it is yes, nothing can be done.

## Hint 3

```text
if other in ancestors(current): "up-to-date"
elif current in ancestors(other): "fast-forward"
else: "merge"
```
