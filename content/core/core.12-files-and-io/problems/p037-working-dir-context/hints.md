## Hint 1

A function with `@contextmanager` runs up to `yield` when the `with` starts, and the rest when it ends. Where must
you store the old folder? What happens to the code after `yield` if the body raises an error, and which keyword
makes the code run in both cases?

## Hint 2

```
@contextmanager
def working_dir(path):
    old = os.getcwd()
    os.chdir(path)
    try:
        yield Path.cwd()
    finally:
        os.chdir(old)
```
