# Does the caller's data change?

Predict **exactly** what this program prints. For every line inside a function that touches a
parameter, decide: does it **mutate** the object, or **rebind** the local name? Draw arrows from
names to objects as you go.

```python
def touch(items, n, word, d):
    items.append(1)
    items = items + [0]
    items.append(2)
    n += 1
    word = word.upper()
    d["seen"] = True
    d = {}
    d["lost"] = True
    return items, n

a, b, c, e = [9], 5, "hi", {}
result = touch(a, b, c, e)
print(a, b, c, e)
print(result)

def extend_twice(lst):
    lst += [3]
    lst.extend([4])
    return None

x = [1]
y = x
print(extend_twice(x), x, y)

def reset_rows(grid):
    for row in grid:
        row = [0, 0]
    grid[0] = ["new"]
    grid[1][0] = "changed"

g = [[1, 2], [3, 4]]
inner = g[1]
reset_rows(g)
print(g, inner)

def swap(p, q):
    p, q = q, p
    return p, q

m, k = "left", "right"
print(swap(m, k), m, k)
```

Write your answer in `answer.txt`, one line per printed line.
