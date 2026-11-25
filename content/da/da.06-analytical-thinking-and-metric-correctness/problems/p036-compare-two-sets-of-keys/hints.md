## Hint 1

What Python type answers "is this key in the collection?" and has operators for "in A but not in B", "in both"? What
happens to repeated keys when you build it? Why must the final lists be sorted explicitly?

## Hint 2

```text
sa = set of the keys of a (as plain Python values);  sb = same for b
only_a = sa - sb ;  only_b = sb - sa ;  both = sa & sb
counts = sizes of sa, sb, only_a, only_b, both
summary = f"{name_a}: {len(sa)} | {name_b}: {len(sb)} | in both: ... | only {name_a}: ... | only {name_b}: ..."
return the three sets as sorted lists, plus counts and summary
```
