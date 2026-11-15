# Explain: why does this recursion never stop?

Every recursive function needs (1) a **base case** and (2) **progress**: each call must move closer to the base case. Look at the four functions below. For each one, choose **one** label and give a one-line reason and a fix.

| Label | Meaning |
|---|---|
| A | there is no base case at all |
| B | there is a base case, but the steps can **jump over** it for some inputs |
| C | the recursive call does **not shrink** the input (no progress) |
| D | it is fine: it always stops for the inputs described |

```python
# Snippet 1: called with n >= 0
def count(n):
    print(n)
    count(n - 1)


# Snippet 2: called with n >= 0
def evens(n):
    if n == 0:
        return 0
    return n + evens(n - 2)


# Snippet 3: called with any list
def length(xs):
    if not xs:
        return 0
    return 1 + length(xs[:])


# Snippet 4: called with n >= 0
def digits(n):
    if n < 10:
        return 1
    return 1 + digits(n // 10)
```

Write your answer in `answer.md` as four lines like `1: X - reason - fix`, followed by two or three sentences answering:
**What exactly does Python do when a recursion never stops, and why is there a limit at all?**

Then compare with the model answer and rate yourself.
