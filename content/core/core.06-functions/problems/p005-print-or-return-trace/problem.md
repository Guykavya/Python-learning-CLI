# Where did None come from?

Predict **exactly** what this program prints. Do not run it. For each call, ask: does the
function print, return, or both? What does a function return when it has no `return`?

```python
def show(x):
    print(x * 2)

def give(x):
    return x * 2

def maybe(x):
    if x > 0:
        return x
    return

a = show(3)
b = give(3)
print(a, b)
print(show(1))
print(give(give(2)))
print(maybe(5), maybe(-5))
print(give(3) + 1)
```

Write your answer in `answer.txt`, one line per printed line.
