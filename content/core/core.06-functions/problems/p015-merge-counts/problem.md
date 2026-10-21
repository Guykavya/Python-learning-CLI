# Merge any number of count dicts

Shops send their daily sales as dicts from item to quantity. Write `merge_counts(*counts)` that
takes **any number** of such dicts and returns a **new** dict with the totals.

- Keys appear in the order they are first seen (first dict first).
- Items whose total is `0` are left out.
- None of the input dicts may change.
- With no dicts, return `{}`.

**Examples**

```python
merge_counts({"tea": 3, "milk": 1}, {"milk": 2, "bread": 5})
# {'tea': 3, 'milk': 3, 'bread': 5}

merge_counts({"tea": 2}, {"tea": -2, "jam": 1})     # returns
# {'jam': 1}                       tea totals 0, so it is left out

merge_counts()                     # {}
```
