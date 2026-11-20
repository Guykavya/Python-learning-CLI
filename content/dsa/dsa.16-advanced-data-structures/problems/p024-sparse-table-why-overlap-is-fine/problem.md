# Explain: sparse table, why overlap is fine

The sparse table of chapter section 15 answers `[l, r)` with **two** precomputed blocks of length `2**k` that may **overlap**. The same code with `+` instead of `min` gives wrong sums:

```python
a = [5, 3, 8, 6, 2, 7, 4, 1]
# min table, query [1, 7): blocks a[1:5] and a[3:7]
print(min(min(a[1:5]), min(a[3:7])), min(a[1:7]))
# sum table, same blocks
print(sum(a[1:5]) + sum(a[3:7]), sum(a[1:7]))
```
```text
2 2
38 30
```

Write a short explanation (6 to 10 sentences) in `answer.md` that answers:

1. Which positions of `[1, 7)` are covered by **both** blocks here?
2. What property must the operation `f` have so that covering some elements twice changes nothing? Give its name and its equation.
3. Which of these operations have it: `min`, `max`, `gcd`, bitwise `and`, bitwise `or`, `+`, `*`, `xor`? Justify `xor` and `gcd` in one line each.
4. Why exactly is the sum 38 instead of 30?
5. How can a sparse table still answer sums (two ways), and what does each cost per query?

Then compare with the model answer and rate yourself.
