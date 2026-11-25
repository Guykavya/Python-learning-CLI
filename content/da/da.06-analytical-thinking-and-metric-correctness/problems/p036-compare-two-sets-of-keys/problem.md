# Compare two sets of keys

Chapter section 11.3. When two teams count "February jobs" and get different numbers, the first step is not to compare
the totals but the **sets of keys**: which jobs are only in A, which only in B, which in both. A net difference of 22
can hide 20 jobs leaving and 42 entering.

Write `compare_keys(a, b, name_a="A", name_b="B")`.

- `a` and `b` are any iterables of keys (lists, sets, pandas Series). Repeated keys count once.
- Return a dict with these keys:
  - `"only_a"`: sorted list of keys in `a` but not in `b`
  - `"only_b"`: sorted list of keys in `b` but not in `a`
  - `"both"`: sorted list of keys in both
  - `"counts"`: a dict `{"a": ..., "b": ..., "only_a": ..., "only_b": ..., "both": ...}` with the sizes of those sets
    (`"a"` and `"b"` are the number of **distinct** keys of each input)
  - `"summary"`: the text `"<name_a>: <n> | <name_b>: <n> | in both: <n> | only <name_a>: <n> | only <name_b>: <n>"`
- Do not change the inputs. The keys in the lists are plain Python values (convert numpy numbers with `.item()` or
  `int(...)` if you get them from a Series).

## Example

```python
ops = [101, 102, 103, 103, 105]
fin = [102, 103, 104, 106, 107]
r = compare_keys(ops, fin, "ops", "finance")
print(r["only_a"], r["only_b"], r["both"])
print(r["counts"])
print(r["summary"])
```

```text
[101, 105] [104, 106, 107] [102, 103]
{'a': 4, 'b': 5, 'only_a': 2, 'only_b': 3, 'both': 2}
ops: 4 | finance: 5 | in both: 2 | only ops: 2 | only finance: 3
```
