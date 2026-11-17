## Hint 1

Model: accounts are vertices, a shared address is an edge. A person is a connected component. Which tool from section 9 builds components while you read the input, without building the graph first?

## Hint 2

1. `owner = {}` maps an address to the index of the first account that had it. For account `i` and each address `e`: if `e` is in `owner`, `union(i, owner[e])`; else `owner[e] = i`.
2. Collect the addresses per root: `groups[find(owner[e])].add(e)`.
3. Build `[name] + sorted(addresses)` for every group, using the name of the root account, and sort the list of results.

## Hint 3

```
parent = list(range(len(accounts)))
owner = {}
for i, acc in enumerate(accounts):
    for e in acc[1:]:
        if e in owner: union(i, owner[e])
        else: owner[e] = i
groups = {}
for e, i in owner.items(): groups.setdefault(find(i), set()).add(e)
result = [[accounts[r][0]] + sorted(es) for r, es in groups.items()]
result.sort(key=lambda acc: (acc[0], acc[1]))
return result
```
