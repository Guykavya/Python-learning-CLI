# Trace range() with steps

Predict **exactly** what this program prints. Do not run it.

Remember: `print(x, end=" ")` prints `x` followed by a space and stays on the same line.
A plain `print()` just ends the current line.

```python
print("A:", end=" ")
for i in range(5):
    print(i, end=" ")
print()

print("B:", end=" ")
for i in range(1, 5):
    print(i, end=" ")
print()

print("C:", end=" ")
for i in range(2, 10, 3):
    print(i, end=" ")
print()

print("D:", end=" ")
for i in range(10, 0, -3):
    print(i, end=" ")
print()

print("E:", end=" ")
for i in range(5, 1):
    print(i, end=" ")
print("(nothing)")

print("F:", end=" ")
for i in range(0, 10, 4):
    print(i * i, end=" ")
print()

count = 0
for i in range(3, -4, -2):
    count += 1
print("G:", count, i)
```

Write your answer in `answer.txt`, one line per printed line. Spaces at the end of a line do not matter
(the checker ignores them), but spaces between values do.
