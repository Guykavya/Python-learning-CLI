## Approach

Sets do exactly this job: `-` gives "only in the left", `&` gives "in both", and building a set removes repeated keys.
Convert numpy numbers to plain values with `.item()` so the lists hold ordinary ints. Sort at the end, so the output
does not depend on the (arbitrary) order of a set.

## Code

```python
def compare_keys(a, b, name_a="A", name_b="B"):
    sa = {k.item() if hasattr(k, "item") else k for k in a}
    sb = {k.item() if hasattr(k, "item") else k for k in b}
    only_a, only_b, both = sa - sb, sb - sa, sa & sb
    counts = {"a": len(sa), "b": len(sb), "only_a": len(only_a), "only_b": len(only_b), "both": len(both)}
    summary = (f"{name_a}: {len(sa)} | {name_b}: {len(sb)} | in both: {len(both)} | "
               f"only {name_a}: {len(only_a)} | only {name_b}: {len(only_b)}")
    return {"only_a": sorted(only_a), "only_b": sorted(only_b), "both": sorted(both), "counts": counts, "summary": summary}
```

## Complexity

O(len(a) + len(b)) to build the sets and the three set operations; O(k log k) to sort the k keys of the result.

## Another way

With pandas, `a.merge(b, how="outer", indicator=True)` labels every key `left_only`, `right_only` or `both`. It is
useful when the keys come with other columns, but for plain keys the set operators are shorter and clearer.
