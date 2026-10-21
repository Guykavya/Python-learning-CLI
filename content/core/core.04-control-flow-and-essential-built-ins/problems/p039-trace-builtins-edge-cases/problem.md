# Trace built-in edge cases

Predict **exactly** what this program prints. Do not run it.

```python
print(any([]), all([]))
print(any([0, 0.0, ""]), all([1, "x", [0]]))
print(sum([]), sum(range(5), 10))
print(sum([True, True, False]))
print(max("apple", "Banana"), max("apple", "Banana", key=str.lower))
print(min([3, -7, 5], key=abs), max([3, -7, 5], key=abs))
print(max([], default="none"))
print(min("hello"))
print(max(["bb", "a", "cc"], key=len))
print(min(4, 4.0), min(4.0, 4))
print(all(ch.isdigit() for ch in ""), "".isdigit())
print(max(range(0)) if range(0) else "empty range")
```

Write your answer in `answer.txt`, one printed line per line.
