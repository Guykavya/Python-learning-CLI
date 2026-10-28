## Hint 1

What is called when `json.dumps` meets an object it cannot write? What must that function do if it does not know the object either?

## Hint 2

```
def convert(obj):
    if isinstance(obj, set): return sorted(obj)
    if isinstance(obj, (date, datetime)): return obj.isoformat()
    if isinstance(obj, Path): return str(obj)
    raise TypeError(...)
return json.dumps(data, sort_keys=True, default=convert)
```
