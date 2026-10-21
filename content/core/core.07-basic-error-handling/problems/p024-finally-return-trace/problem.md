# Who has the last word: return and finally

Predict **exactly** what this program prints. This is the assessed trace for this module: work
it out on paper using the rules of chapter section 8, then check.

When Python 3.14 compiles this file it also prints a `SyntaxWarning` about the `return` in a
`finally` block (that is the point of `override`). The warning goes to standard error and is
**not** part of the answer: write only what the `print` calls print.

```python
def first(n):
    try:
        if n < 0:
            raise ValueError("negative")
        if n == 0:
            return "zero from try"
    except ValueError:
        return "from except"
    else:
        return "from else"
    finally:
        print("  finally sees", n)

for n in [5, 0, -5]:
    print(first(n))

def build():
    items = ["a"]
    count = 1
    try:
        return items, count
    finally:
        items.append("b")
        count = 2

print(build())

def override(text):
    try:
        return int(text)
    finally:
        return "finally wins"

print(override("5"))
print(override("five"))

for i in range(4):
    try:
        if i == 1:
            continue
        if i == 3:
            break
        print("body", i)
    finally:
        print("finally", i)
print("loop done")
```

Write your answer in `answer.txt`, one line per printed line. Keep the leading spaces that some lines print.
