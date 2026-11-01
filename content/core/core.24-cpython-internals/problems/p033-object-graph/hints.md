## Hint 1

This is a graph search, like the ones you wrote for mazes: the "neighbours" of an object are
`gc.get_referents(obj)`. What do you need so that a cycle (`a -> b -> a`) does not loop forever?
Why must you remember objects by `id()` and not put them in a set (think of an unhashable list,
or two *equal* but different lists)?

Which neighbours should never enter the queue at all? What happens if you follow the class of an
instance (it is always among the referents)?

## Hint 2

```
kind(obj):
    if type(obj) is dict: return "follow"
    if type(obj) in (list, tuple, set, frozenset): return "count"
    if isinstance(obj, NEVER_FOLLOW) or type(obj).__module__ == "builtins": return None
    return "count"

reachable(root, max_nodes):
    found = []; seen = {id(root)}; queue = deque([root])
    while queue and len(found) < max_nodes:
        obj = queue.popleft()
        k = kind(obj)
        if k is None: continue
        if k == "count": found.append(obj)
        for ref in gc.get_referents(obj):
            if id(ref) not in seen and kind(ref) is not None:
                seen.add(id(ref)); queue.append(ref)      # mark when QUEUED, not when visited
    return found
```
