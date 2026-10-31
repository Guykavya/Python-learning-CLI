# Explain: the total that became zero

Ravi writes a small report for sensor readings:

```python
readings = [12, 15, 11, 18]
big = (r for r in readings if r > 12)

print(sum(big))   # 33
print(sum(big))   # 0
print(max(big))   # ValueError: max() iterable argument is empty
```

He says: "The data did not change. Why is the second total 0? And why does `sum` give a quiet
0 while `max` crashes?"

In `answer.md` (about 150 to 300 words), explain:

1. Why the second `sum(big)` gives `0` and `max(big)` raises `ValueError`. Use the words
   *generator*, *consumed* and *StopIteration*.
2. Why the quiet `0` is **more dangerous** than the error.
3. Two different ways to fix Ravi's code, and when each is the better choice.
4. A short rule: when should you keep data in a **list**, and when is a **generator** better?
   Give at least two reasons for each side.
