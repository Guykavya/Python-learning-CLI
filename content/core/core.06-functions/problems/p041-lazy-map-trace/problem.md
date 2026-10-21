# Lazy iterators run out

Predict **exactly** what this program prints. Remember that `map` and `filter` produce values
only when something asks for them, and only once.

```python
def noisy(n):
    print("  noisy", n)
    return n * 10

m = map(noisy, [1, 2, 3])
print("created")
print(list(m))
print(list(m))

evens = filter(lambda n: n % 2 == 0, [1, 2, 3, 4, 5, 6])
print(sum(evens), sum(evens))

m2 = map(noisy, [4, 5, 6, 7])
print(any(x > 45 for x in m2))
print(list(m2))

words = ["a", "bb", "ccc"]
lengths = map(len, words)
words.append("dddd")
print(list(lengths))
```

Write your answer in `answer.txt`, one line per printed line.
