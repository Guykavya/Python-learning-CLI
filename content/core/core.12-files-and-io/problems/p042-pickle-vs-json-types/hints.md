## Hint 1

What mode must you use for `pickle`: text or binary? For `json_loses`: what must you compare, and which error can
`json.dumps` raise for a value it cannot write? How can you make a function return `True` when an error happens?

## Hint 2

```
def save_pickle(obj, path):
    with open(path, "wb") as f: pickle.dump(obj, f)
def load_pickle(path):
    with open(path, "rb") as f: return pickle.load(f)
def json_loses(obj):
    try:
        back = json.loads(json.dumps(obj))
    except TypeError:
        return True
    return back != obj
```
