## Hint 1

What are the three steps of every cleanup block: set up, use, tear down? In `with x as y:` which
object does the set-up and the tear-down for you? What does a lock offer so that `with lock:`
works? Does the fake resource in the tests support `with`?

## Hint 2

For `temp_setting` you write the three steps yourself, around one `yield`.

```
read_all : with open_resource(name) as r: return r.read()
copy_text: with open_resource(src) as s, open_resource(dst) as d: ... return len(text)
run_locked: with lock: return func()

@contextmanager
def temp_setting(obj, name, value):
    remember the old value (or "it was missing")
    set the new value
    try:    yield
    finally: put the old value back (or delete the attribute)
```
Why must the restore be in `finally`, not after the `yield`?
