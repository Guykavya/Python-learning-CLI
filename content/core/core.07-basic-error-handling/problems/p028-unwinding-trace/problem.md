# Unwinding through three functions

Predict **exactly** what this program prints. Draw the call stack `a -> b -> c` for each value of
`n`. When `c` raises, follow the exception **up** the stack: at each frame, which `except` clause
(if any) matches, and which `finally` blocks run on the way? (Chapter sections 3 and 8.)

```python
def c(n):
    try:
        print("c start", n)
        if n == 1:
            raise ValueError("bad one")
        if n == 2:
            raise KeyError(n)
        return n * 10
    finally:
        print("c finally", n)

def b(n):
    try:
        result = c(n)
    except KeyError as e:
        print("b caught KeyError", e)
        result = -1
    else:
        print("b else", result)
    print("b returns", result)
    return result

def a(n):
    try:
        return b(n)
    except ValueError as e:
        print("a caught", e)
        return 0
    finally:
        print("a finally", n)

for n in [3, 2, 1]:
    print("result", a(n))
```

Write your answer in `answer.txt`, one line per printed line.
