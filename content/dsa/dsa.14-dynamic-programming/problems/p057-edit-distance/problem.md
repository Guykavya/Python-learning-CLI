# Edit distance

The **edit distance** (Levenshtein distance) between two strings is the fewest operations that turn `a` into `b`. One operation is:

- **insert** one character,
- **delete** one character, or
- **replace** one character by another.

Write `edit_distance(a, b)` (chapter section 15).

## Example

```python
>>> edit_distance("horse", "ros")          # horse -> rorse -> rose -> ros
3
>>> edit_distance("kitten", "sitting")     # k->s, e->i, insert g
3
>>> edit_distance("intention", "execution")
5
>>> edit_distance("", "abc")               # insert 3
3
>>> edit_distance("abc", "abc")
0
```

## Constraints

- `0 <= len(a), len(b) <= 400`.
- Time `O(len(a) * len(b))`. A recursion without a memo is exponential.

## Think about

Look at the last characters of `a[:i]` and `b[:j]`. When they are equal, what does it cost? When they differ, the last step of an optimal edit is a replace, a delete or an insert: which smaller pair of prefixes does each one leave? And what is the distance from a prefix to the **empty** string?
