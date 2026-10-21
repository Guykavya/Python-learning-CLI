# Trace two Fibonacci loops

Both loops below try to step through the Fibonacci numbers (0, 1, 1, 2, 3, 5, 8, ...), where each number is the sum
of the two before it. They differ in only one way: the first updates `a` and `b` in one line, the second in two lines.

Predict **exactly** what the program prints. Do not run it. Keep a trace table for each loop with columns
`step`, `a`, `b`.

```python
a = 0
b = 1
for step in range(5):
    a, b = b, a + b
    print("together", a, b)

a = 0
b = 1
for step in range(5):
    a = b
    b = a + b
    print("one by one", a, b)
```

Write your answer in `answer.txt`, one line per printed line. `print("together", a, b)` prints the label and the two
numbers separated by single spaces, for example `together 1 1`.

Afterwards, explain to yourself in one sentence why the second loop does not produce Fibonacci numbers.
