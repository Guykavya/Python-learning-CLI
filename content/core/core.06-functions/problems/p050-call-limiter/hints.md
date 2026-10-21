## Hint 1

The wrapper needs a count that survives between its calls. Where does it live, and which statement lets the wrapper change it?

## Hint 2

The wrapper does not know `func`'s parameters. How does it accept and pass on any arguments?

## Hint 3

```
def limit_calls(func, max_calls):
    used = 0
    def wrapper(*args, **kwargs):
        nonlocal used
        if used >= max_calls: return None
        used += 1
        return func(*args, **kwargs)
    return wrapper
```
