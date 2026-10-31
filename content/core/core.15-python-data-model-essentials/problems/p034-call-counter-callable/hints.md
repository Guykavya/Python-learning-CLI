## Hint 1

Python turns `obj(1, 2)` into `type(obj).__call__(obj, 1, 2)`. Which method must the class define? And since the wrapped function can take any arguments, what two parameters should it accept besides `self`?

## Hint 2

```
__init__(func): self.func = func ; self.count = 0
__call__(*args, **kwargs): self.count += 1 ; return self.func(*args, **kwargs)
reset(): self.count = 0
```
Count first, then call: that is why failures are counted.
