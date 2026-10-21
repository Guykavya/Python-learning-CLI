# Cells, shared and separate

Predict **exactly** what this program prints. For each closure, ask: which **cell** does it read,
and what does that cell hold **at the moment the closure is called**?

```python
def make_pair():
    n = 0
    def get():
        return n
    def inc():
        nonlocal n
        n += 1
    return get, inc

get1, inc1 = make_pair()
get2, inc2 = make_pair()
inc1(); inc1(); inc2()
print(get1(), get2())

def snapshot():
    value = "early"
    def show():
        return value
    value = "late"
    return show

print(snapshot()())

def loop_funcs():
    funcs = []
    for i in range(3):
        funcs.append(lambda: i * i)
    return funcs

def fixed_funcs():
    return [lambda i=i: i * i for i in range(3)]

print([f() for f in loop_funcs()])
print([f() for f in fixed_funcs()])
print(len(get1.__closure__), get1.__closure__[0].cell_contents)
print(get1.__closure__[0] is inc1.__closure__[0])
```

Write your answer in `answer.txt`, one line per printed line.
