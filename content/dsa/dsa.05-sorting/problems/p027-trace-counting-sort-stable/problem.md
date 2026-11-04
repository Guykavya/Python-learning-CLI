# Trace a stable counting sort

Counting sort can sort **records** (not only numbers) by a small integer key, and keep it stable. Predict **exactly** what this program prints. Do not run it.

```python
records = [("ann", 2), ("bob", 0), ("cy", 2), ("dee", 1), ("eli", 0), ("fay", 2)]
k = 3
count = [0] * k
for name, key in records:
    count[key] += 1
print("count", count)
start = [0] * k
total = 0
for key in range(k):
    start[key] = total
    total += count[key]
print("start", start)
out = [None] * len(records)
for name, key in records:
    out[start[key]] = name
    start[key] += 1
    print(name, "->", out)
print(out)
```

Write your answer in `answer.txt`, one line per printed line.

## How to work

`count[key]` is how many records have that key. `start[key]` is the first output slot of that key (the sum of all smaller counts).
In the last loop each record goes to `start[key]`, and then that start moves one step right, so the next record with the same key goes right after it.
Records are processed **in input order**. Remember that `out` begins with `None` values and `print` shows them as `None`.

## After you answer

1. Which records have key 2, and in which order do they appear in the output? Why is that stability?
2. What would happen to the order of equal keys if the last loop went from the end of `records` to the start without changing `start`?
3. How would you change the second loop to get a *descending* sort?
