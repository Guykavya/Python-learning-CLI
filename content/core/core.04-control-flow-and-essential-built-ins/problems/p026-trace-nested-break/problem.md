# Trace break in nested loops

Predict **exactly** what this program prints. Do not run it.

```python
for i in range(1, 4):
    for j in range(1, 4):
        if j == i:
            continue
        if i + j == 5:
            print("stop inner at", i, j)
            break
        print(i, j)
    print("row", i, "done")

count = 0
for a in "ab":
    for b in "xyz":
        count += 1
print("count", count, a, b)
```

Write your answer in `answer.txt`, one printed line per line.
