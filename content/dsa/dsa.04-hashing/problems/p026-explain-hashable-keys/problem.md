# Explain: what can be a key?

Try these ideas in a Python shell first if you like, then answer in `answer.md` in your own words. Aim for 200 to 350 words.

```python
d = {}
d[(1, 2)] = "tuple"        # works
d[[1, 2]] = "list"         # ???
d[(1, [2])] = "mixed"      # ???
d[1] = "int"
d[1.0] = "float"
d[True] = "bool"
print(len(d))              # ???
```

1. **Lists.** What happens on `d[[1, 2]] = ...`, and why? Why is the same data as a tuple allowed?
2. **A tuple holding a list.** Does `d[(1, [2])]` work? Explain in terms of "is every part hashable?".
3. **Equal keys.** What does the program print for `len(d)` (count only the three int/float/bool lines and the tuple
   line if the others fail), and why? State the rule that connects equality and hashing.
4. **What if it were allowed?** Suppose a list could be a key. Describe a concrete sequence of steps that would make the
   dictionary lose an entry it holds.
5. **Your own data.** You want a dictionary keyed by a `(row, col)` position and another keyed by a set of letters. What do
   you use for each?

Then read `solution.md` and `answer.md`, and rate your answer.
