# Rank students with a tuple key

Write `rank_students(records, *, top=None)`. `records` is a list of `(name, marks)` tuples.
Return a list of **names**:

- highest marks first;
- equal marks in alphabetical order of name, ignoring case;
- if `top` is given, only the first `top` names.

`top` is keyword-only. The input list must not change.

**Examples**

```python
records = [("ravi", 75), ("Asha", 82), ("meena", 91), ("Kiran", 75)]
rank_students(records)          # ['meena', 'Asha', 'Kiran', 'ravi']
rank_students(records, top=2)   # ['meena', 'Asha']
rank_students([])               # []
```
