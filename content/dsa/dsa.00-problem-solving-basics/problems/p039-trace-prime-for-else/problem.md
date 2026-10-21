# Trace a prime finder with for-else

This program looks for the smallest divisor of each number from 1 to 11. It uses a `for` loop with an
`else:` part. Remember the rule: the `else` of a loop runs when the loop **finishes without `break`**.

Predict **exactly** what it prints. Do not run it. Use a trace table on paper.

```python
for x in range(1, 12):
    for d in range(2, x):
        if x % d == 0:
            print(x, "=", d, "*", x // d)
            break
    else:
        print(x, "is prime")
```

Write your answer in `answer.txt`, one line per printed line. `print(x, "=", d, "*", x // d)` puts a single
space between each item, so it prints something like `15 = 3 * 5`.

Then, before you look at the solution, think about two questions:

1. Which line of the output is wrong mathematically, and why does the program print it?
2. Is the `else:` attached to the `if` or to the inner `for`? How can you tell?
