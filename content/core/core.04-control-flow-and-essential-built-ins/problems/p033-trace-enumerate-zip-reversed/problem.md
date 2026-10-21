# Trace enumerate, zip and reversed

Predict **exactly** what this program prints. Do not run it. Remember that `zip`,
`enumerate` and `reversed` return iterators, which can be used up.

```python
word = "spam"
for i, ch in enumerate(word, start=10):
    print(i, ch)
pairs = zip("abc", range(1, 10))
for p in pairs:
    print(p)
print(list(pairs))
for a, b in zip("hello", reversed("hello")):
    if a == b:
        print("mirror", a)
e = enumerate("xy")
print(next(e))
for i, ch in e:
    print("loop", i, ch)
print(list(zip()))
print(list(reversed(range(0, 10, 4))))
for i, (x, y) in enumerate(zip("ab", "cd"), 1):
    print(i, x + y)
```

Write your answer in `answer.txt`, one printed line per line.
