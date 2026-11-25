## Approach

Filter on `cell_type`, then normalise `source` to one string. A list of lines already carries its newlines, so join with `""`, not `"\n"`.

## Code

```python
def code_cells(nb):
    result = []
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        source = cell.get("source", "")
        result.append(source if isinstance(source, str) else "".join(source))
    return result
```

## Complexity

Time O(total size of the source text), space O(the same) for the result.

## Another way

`[c["source"] if isinstance(c["source"], str) else "".join(c["source"]) for c in nb["cells"] if c["cell_type"] == "code"]`. The real `nbformat` library does the same thing for you with `nbformat.reads(...)`, which normalises `source` to a string when it loads a file.
