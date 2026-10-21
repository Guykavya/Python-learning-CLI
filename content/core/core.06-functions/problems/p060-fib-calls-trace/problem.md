# Counting the calls of naive Fibonacci

Predict **exactly** what this program prints. Draw the call tree for `fib(4)` on paper and count
how many times each `n` appears in it.

```python
counts = {}

def fib(n):
    counts[n] = counts.get(n, 0) + 1
    if n < 2:
        return n
    return fib(n - 1) + fib(n - 2)

print(fib(4))
print(sorted(counts.items()))
print(sum(counts.values()))

counts.clear()
fib(10)
print(sum(counts.values()), counts[1], counts[9])

cache = {}
calls = 0

def fast(n):
    global calls
    if n in cache:
        return cache[n]
    calls += 1
    result = n if n < 2 else fast(n - 1) + fast(n - 2)
    cache[n] = result
    return result

print(fast(10), calls)
print(fast(12), calls)
```

Write your answer in `answer.txt`, one line per printed line.
