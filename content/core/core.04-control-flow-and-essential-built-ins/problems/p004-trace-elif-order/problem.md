# Trace an elif chain

Predict **exactly** what this program prints. Do not run it.

```python
for t in [5, 18, 25, 31, 40]:
    if t > 30:
        print(t, "hot")
    elif t > 20:
        print(t, "warm")
    elif t > 10:
        print(t, "mild")
    else:
        print(t, "cold")
    if t > 20:
        print("fan on")
    if t >= 40:
        print("alert")

code = "b"
if code == "a" or "c":
    print("matched", code)
else:
    print("no match")
```

Write your answer in `answer.txt`, one printed line per line.
