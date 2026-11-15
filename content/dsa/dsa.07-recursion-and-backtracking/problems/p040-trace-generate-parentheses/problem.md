# Trace: generate parentheses

This is `generate_parentheses` from chapter section 13, with an extra `show` flag that prints every call: the current string (with `repr`, so the empty string shows as `''`), the number of opened and the number of closed brackets.

Predict **exactly** what the program prints. Do not run it.

```python
def generate_parentheses(n, show=False):
    result, path = [], []

    def go(opened, closed):
        if show:
            print(repr("".join(path)), opened, closed)
        if len(path) == 2 * n:
            result.append("".join(path))
            return
        if opened < n:
            path.append("(")
            go(opened + 1, closed)
            path.pop()
        if closed < opened:
            path.append(")")
            go(opened, closed + 1)
            path.pop()

    go(0, 0)
    return result


print(generate_parentheses(2, show=True))
for s in generate_parentheses(3):
    print(s)
```

Write your answer in `answer.txt`, one printed line per line, for example `'(()' 2 1`.

## How to work

The first part traces `n = 2` call by call; the second part only prints the results for `n = 3`. At each call two branches are tried **in this order**: add `(` if `opened < n`, then add `)` if `closed < opened`. A branch that is not allowed creates no call (and prints nothing).

## After you answer

1. How many calls does `n = 2` make? How many strings of length 4 over `(` and `)` exist in total?
2. Why can `)` never come first?
3. The results for `n = 3` come out in dictionary order (`(` sorts before `)`). Why?
