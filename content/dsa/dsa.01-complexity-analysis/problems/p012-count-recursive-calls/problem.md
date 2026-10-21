# How many calls?

You have not written functions yet, but you can read one. In this program, `def fib(n):` defines a piece of
code named `fib` that receives a number `n`. Writing `fib(5)` runs that code with `n = 5`, and `return` sends a
value back to whoever asked. The function **calls itself** with smaller numbers: that is recursion.
`calls` counts how many times `fib` starts running.

Predict **exactly** what the program prints. Do not run it.

```python
calls = [0]          # a list, so the function can change the number inside it


def fib(n):
    calls[0] += 1
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


for n in [0, 1, 2, 3, 4, 5, 10]:
    calls[0] = 0
    value = fib(n)
    print(n, value, calls[0])
```

Write your answer in `answer.txt`, one line per printed line, three numbers separated by single spaces.

## A start

`fib(2)` runs once itself, then calls `fib(1)` and `fib(0)`, which return straight away. That is 3 calls, and
the value is `1 + 0 = 1`. So the third line is `2 1 3`.

## After you answer

Let `C(n)` be the number of calls for `fib(n)`. Write a rule for `C(n)` in terms of `C(n - 1)` and `C(n - 2)`.
Roughly how does `C(n)` grow when `n` goes up by 1?
