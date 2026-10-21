## Approach

An inverted index turns "which documents contain this word?" into one dict lookup. Each query
type is then a set operation.

## Code

```python
index = {}
n = int(input())
for number in range(1, n + 1):
    for word in input().lower().split():
        index.setdefault(word, set()).add(number)
for _ in range(int(input())):
    op, *words = input().lower().split()
    sets = [index.get(w, set()) for w in words]
    if op == "and":
        result = set(sets[0])
        for s in sets[1:]:
            result &= s
    elif op == "or":
        result = set()
        for s in sets:
            result |= s
    else:
        result = sets[0] - sets[1]
    print(" ".join(str(d) for d in sorted(result)) if result else "none")
```

## Complexity

Building is O(total words). Each query costs about the size of the sets involved.

## A sneaky aliasing bug

`result = index[w1]` followed by `result &= index[w2]` changes the index itself, because
`result` is an alias of the stored set. Later queries would then give wrong answers. Copy first
with `set(...)`, or use `a & b`, which builds a new set.
