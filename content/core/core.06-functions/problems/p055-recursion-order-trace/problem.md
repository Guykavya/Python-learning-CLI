# The order of recursive calls

Predict **exactly** what this program prints. Remember: a call runs to completion, including all
its own recursive calls, before the line after it continues.

```python
def down_up(n):
    if n == 0:
        print("bottom")
        return
    print("down", n)
    down_up(n - 1)
    print("up", n)

def tree(n):
    if n == 0:
        return
    tree(n - 1)
    print("node", n)
    tree(n - 1)

def build(n):
    if n == 0:
        return []
    return build(n - 1) + [n]

down_up(2)
tree(2)
print(build(3))
```

Write your answer in `answer.txt`, one line per printed line.
