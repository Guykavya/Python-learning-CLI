# Count the calls

How much work does a notebook save? Count it. Predict **exactly** what this program prints. Do not run it.

**What counts as a call:** one run of the function body. The line `calls += 1` is the first line of the body, so a call that finds its answer in the notebook **still counts** (it runs `calls += 1`, then returns early). This is the same counter as in chapter section 1.

```python
calls = 0

def fib(n):
    global calls
    calls += 1
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

for n in range(7):
    calls = 0
    value = fib(n)
    print("naive", n, value, calls)

calls = 0
notebook = {}

def fib_memo(n):
    global calls
    calls += 1
    if n in notebook:
        return notebook[n]
    if n < 2:
        result = n
    else:
        result = fib_memo(n - 1) + fib_memo(n - 2)
    notebook[n] = result
    return result

print("memo", fib_memo(6), calls, len(notebook))
calls = 0
print("again", fib_memo(6), calls, len(notebook))
calls = 0
print("next", fib_memo(7), calls, len(notebook))
```

Write your answer in `answer.txt`, one printed line per line (10 lines).

## Example of the format

The first line is `naive 0 0 1`: for `n = 0` the value is 0 and the function body ran once.

## How to work

1. For the naive part, do not draw big trees. Call `C(n)` the number of calls for `fib(n)`. One call for `fib(n)` itself, plus all the calls made by `fib(n - 1)`, plus all those made by `fib(n - 2)`. Write that as a formula and fill a small table for `n = 0..6`.
2. For the memo part, follow the order: `fib_memo(6)` calls `fib_memo(5)` **first**, and that goes all the way down before any `fib_memo(4)` on the right side is asked. Which calls on the right side then find their answer already in the notebook?
3. The notebook is **not** cleared between the last three prints.

## After you answer

1. Compare `C(n)` with `F(n)` (the values). Is `C(n) = 2 * F(n + 1) - 1`? Check it for `n = 6`.
2. The memo count for `fib_memo(n)` on an empty notebook is `2n - 1` for `n >= 2`. Why? (Count the misses and the hits separately.)
3. Chapter section 1 prints 49 calls for `fib(25)`. Does that agree with question 2?
