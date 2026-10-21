# Stars in definitions and calls

Predict **exactly** what this program prints. In each call, first rewrite it without stars:
what separate arguments does `*x` or `**d` turn into?

```python
def show(*args, **kw):
    print(len(args), args, kw)

def pair(a, b):
    return f"a={a} b={b}"

nums = [1, 2, 3]
opts = {"sep": "-"}
show(nums)
show(*nums)
show(*nums, *"ok")
show(nums, opts)
show(**opts)
show(*nums[1:], x=0, **opts)
print(pair(*"xy"))
print(pair(**{"b": 1, "a": 2}))
print(pair(*[10], b=20))
print(*nums, sep=opts["sep"])
```

Write your answer in `answer.txt`, one line per printed line.
