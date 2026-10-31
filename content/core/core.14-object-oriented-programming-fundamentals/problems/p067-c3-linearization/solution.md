## Approach

C3 (chapter section 12) builds the MRO from the MROs of the bases plus the list of bases itself. The
merge takes, again and again, the first head that does not appear in the tail of any list. That rule
guarantees three things: a class comes before its parents, the order of the bases is kept, and every
parent's own MRO order is kept. If no head qualifies, these promises contradict each other, and Python
refuses to create the class. Its error message names the heads that are stuck, which tells you
exactly which classes disagree about their order.

## Code

```python
def _merge(lists):
    lists = [list(seq) for seq in lists if seq]
    result = []
    while lists:
        for seq in lists:
            head = seq[0]
            if not any(head in other[1:] for other in lists):
                break
        else:
            stuck = []
            for seq in lists:
                if seq[0] not in stuck:
                    stuck.append(seq[0])
            names = ", ".join(stuck)
            raise TypeError(f"Cannot create a consistent method resolution order (MRO) for bases {names}")
        result.append(head)
        for seq in lists:
            if seq[0] == head:
                del seq[0]
        lists = [seq for seq in lists if seq]
    return result


def mro(cls_name, bases_map):
    if cls_name == "object":
        return ["object"]
    bases = list(bases_map[cls_name]) or ["object"]
    for i, base in enumerate(bases):
        if base in bases[:i]:
            raise TypeError(f"duplicate base class {base}")
    parent_mros = [mro(base, bases_map) for base in bases]
    return [cls_name] + _merge(parent_mros + [bases])
```

## Trace of the diamond

```text
mro(D) = [D] + merge([B, A, object], [C, A, object], [B, C])
  head B: not in any tail          -> take B      lists: [A, object] [C, A, object] [C]
  head A: in tail of [C, A, object] -> skip
  head C: not in any tail          -> take C      lists: [A, object] [A, object]
  head A                           -> take A      lists: [object] [object]
  head object                      -> take object
= [D, B, C, A, object]
```

## Complexity

For a class with n classes in its MRO and k lists to merge, each step scans every tail: about O(k · n²)
in the worst case. Real hierarchies are tiny, so this does not matter. The recursion recomputes shared
ancestors; a dict cache (memoization, see `functools.cache`) would compute each class once.

## Another way

Python's own C implementation does the same merge, but it marks heads with a counter of how often each
class appears in tails, so checking "is it in a tail?" is O(1). You can also compare your function
with the real thing in one line: `[c.__name__ for c in type("D", (B, C), {}).__mro__]`.
