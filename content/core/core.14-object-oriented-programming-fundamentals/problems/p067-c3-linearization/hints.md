## Hint 1

`mro` is recursive: to compute the MRO of `D`, you first need the MROs of its bases `B` and `C`. What
is the smallest case that needs no recursion? Write that first, then the merge.

In the merge, "the tail of a list" is `seq[1:]`. A head is good if it is in **no** tail. Try the
diamond by hand: `merge([B, A, object], [C, A, object], [B, C])`. Why is `A` not taken right after
`B`?

## Hint 2

Python's `for ... else` is perfect for "try every head; if none was good, fail": the `else` part runs
only when the loop finished **without** `break`.

After choosing a head, remove it only from the **front** of the lists where it is first (it cannot be
anywhere else, or it would not have been good). Then drop the empty lists. Work on copies so you do
not change `bases_map`.

## Hint 3

```text
mro(name, bases_map):
    if name == "object": return ["object"]
    bases = list(bases_map[name]) or ["object"]
    if a base appears twice: TypeError(f"duplicate base class {base}")
    return [name] + merge([mro(b) for b in bases] + [bases])

merge(lists):
    lists = copies of the non-empty lists
    result = []
    while lists:
        for seq in lists:
            head = seq[0]
            if head not in any other[1:]: break
        else:
            stuck = distinct heads of the remaining lists, in order
            raise TypeError("Cannot create ... for bases " + ", ".join(stuck))
        result.append(head)
        remove head from the front of every list that starts with it
        drop empty lists
    return result
```
