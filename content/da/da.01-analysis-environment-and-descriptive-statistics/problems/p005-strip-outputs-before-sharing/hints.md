## Hint 1

Which standard-library function makes a copy that shares nothing with the original, even the lists and dicts inside it? What goes wrong with `dict(nb)` or `nb.copy()`?

## Hint 2

```text
clean = copy.deepcopy(nb)
for cell in clean["cells"]:
    cell["metadata"].pop("execution", None)
    if cell["cell_type"] == "code":
        cell["outputs"] = []
        cell["execution_count"] = None
return clean
```
