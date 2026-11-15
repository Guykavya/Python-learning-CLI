# Trace: count the calls of fib(5)

The plain Fibonacci function repeats work: the same value is computed again and again. This program records the argument of **every** call in the list `order`, in the order the calls start.

Predict **exactly** what it prints. Do not run it.

```python
order = []


def fib(n):
    order.append(n)
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)


print(fib(5))
print(len(order))
print(order)
print(order.count(2), order.count(1), order.count(0))
```

Write your answer in `answer.txt`, one printed line per line. The third line is a Python list such as `[5, 4]`.

## How to work

Draw the tree of `fib(5)`. The calls start in **preorder**: a node first, then its whole left sub-tree (`n-1`), then its right sub-tree (`n-2`). Then count how often 2, 1 and 0 appear.

## After you answer

1. How many times is `fib(3)` called? How many times would a memo dictionary let it run?
2. The number of calls satisfies `calls(n) = 1 + calls(n-1) + calls(n-2)`. Check it for `n = 5` using your answer for `n = 4` and `n = 3`.
