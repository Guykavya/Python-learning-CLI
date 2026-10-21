## Hint 1

`funcs` is a list whose items are functions. In a loop, the loop variable is one function. How do you call it?

## Hint 2

```
results = []
for f in funcs:
    results.append(f(value))
return results

CHECKS = [len, str.upper, str.isdigit]     (no parentheses: store the functions)

def describe(value):
    return call_all(CHECKS, value)
```
