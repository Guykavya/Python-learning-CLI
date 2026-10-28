## Hint 1

`tomllib.load` wants a file opened in a special mode. Which one? And what happens if you change a list that two dicts share?

## Hint 2

```
config = copy.deepcopy(DEFAULTS)
try:
    with open(path, "rb") as f:
        data = tomllib.load(f)
except FileNotFoundError:
    return config
config.update(data)
return config
```
