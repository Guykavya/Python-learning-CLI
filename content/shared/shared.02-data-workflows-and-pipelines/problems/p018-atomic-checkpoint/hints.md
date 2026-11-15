## Hint 1

Imagine the power goes out at every single line of `save_checkpoint`. After each possible cut,
what is in `cp.json`? With `path.write_text(...)` there is a moment when it is empty. Which
file could you write into instead, so that `cp.json` only changes in one indivisible step at
the very end?

For `load_checkpoint`, list the ways the file can be bad: missing, empty, cut in half, not
UTF-8, JSON that is not an object. Which exception does each raise, and which ones are
`ValueError`s?

## Hint 2

```
save(path, state):
    path = Path(path); path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(state)                 # a TypeError happens here, before any file is touched
    tmp = path.with_name(path.name + ".tmp")
    write text to tmp (utf-8)
    os.replace(tmp, path)

load(path, default):
    fallback = dict(default) if default is not None else {}
    try read_text(utf-8)   except FileNotFoundError: return fallback
    try json.loads         except ValueError (also catch UnicodeDecodeError from reading)
    if result is a dict: return it
    else: os.replace(path, path + ".corrupt"); logger.warning(... path ...); return fallback
```
