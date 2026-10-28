## Hint 1

`shout` gets a function and must give back a function. Which function will you define *inside* `shout`,
and what does it do when it is finally called?

## Hint 2

Inside the wrapper: call the original with everything you received, keep the result, and return the result
changed.

```
def shout(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        return result.upper()
    return wrapper
```
