## Hint 1

Which steps can fail, and after which of them has the real file been touched? In what order must you do:
load, call `fn`, write temp, replace? Where do you clean up the temp file, and for which errors?

## Hint 2

```
data = load or {}
result = fn(data); if result is None: result = data
tmp = path.with_name(path.name + ".tmp")
try:
    with open(tmp, "w") as f: json.dump(result, f)
    os.replace(tmp, path)
except BaseException:
    tmp.unlink(missing_ok=True)
    raise
return result
```
Call `fn` **before** you create the temp file, so a failing `fn` leaves nothing behind.
