## Approach

Copy first, then clean the copy. `copy.deepcopy` duplicates the nested lists and dicts; a shallow copy would still share the `cells` list, and clearing outputs would change the caller's notebook.

## Code

```python
import copy

def strip_outputs(nb):
    clean = copy.deepcopy(nb)
    for cell in clean.get("cells", []):
        cell.get("metadata", {}).pop("execution", None)
        if cell.get("cell_type") == "code":
            cell["outputs"] = []
            cell["execution_count"] = None
    return clean
```

## Complexity

Time and space O(size of the notebook).

## Another way

Build a new cell dict for every cell without `deepcopy`, copying only what you keep. That is more code and easier to get wrong; `deepcopy` is the safe default. Real projects use `nbstripout`, a git filter doing exactly this on commit.
