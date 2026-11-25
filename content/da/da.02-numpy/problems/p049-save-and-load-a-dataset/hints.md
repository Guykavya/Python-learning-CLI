## Hint 1

`np.savez(file, **arrays)` already stores keyword arguments under their names. What does it do when `file` is a *name* without `.npz`, and what does it do when `file` is an open file object?

## Hint 2

`np.load` of an `.npz` returns a lazy `NpzFile`: it reads an array only when you index it, and it keeps the file open. How do you read every array (`data.files` lists the names) into a dict **inside** a `with` block, so the file is closed afterwards?

## Hint 3

```text
save: if not arrays -> ValueError
      for each name, value: a = asarray(value); if a.dtype == object -> ValueError naming it
      with open(path, "wb") as f: np.savez(f, **arrays)
load: with np.load(path) as data:            # allow_pickle stays False
          return {name: data[name] for name in data.files}
```
