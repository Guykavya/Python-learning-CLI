# Trace: lambda, partial and late binding in a loop

A loop builds three lists of functions. They look like they do the same job. Predict the exact
output. The key question: **when** is the value of `e` read, when the function is **made** or
when it is **called**?

```python
from functools import partial


def power(base, exp):
    return base ** exp


lambdas = []
partials = []
defaults = []
for e in range(1, 4):
    lambdas.append(lambda b: power(b, e))
    partials.append(partial(power, exp=e))
    defaults.append(lambda b, e=e: power(b, e))

print([f(2) for f in lambdas])
print([f(2) for f in partials])
print([f(2) for f in defaults])
e = 10
print(lambdas[0](2))
print(partials[0](2))
print(defaults[0](2))
print(partials[0](2, exp=5))
cube_of_3 = partial(power, 3)
print(cube_of_3(2))
print(cube_of_3.func.__name__, cube_of_3.args, cube_of_3.keywords)
```

Write exactly what the program prints, one line for each printed line, in `answer.txt`.
If you think the program stops with an error, the program catches it and prints a line, so you never need to write a traceback.
