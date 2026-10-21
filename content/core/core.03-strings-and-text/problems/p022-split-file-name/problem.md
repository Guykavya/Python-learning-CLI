# Name and extension

Read a file name (it never starts with a dot). Print its name and extension, where the extension is the part after the **last** dot, shown in lowercase:

```
Name: <everything before the last dot>
Extension: <the part after the last dot, lowercase>
```

If there is no dot, or nothing after the last dot, the name is the whole file name (without a final dot) and the extension line says `(none)`.

**Examples**

| Input | Name | Extension |
|---|---|---|
| `archive.tar.GZ` | `archive.tar` | `gz` |
| `README` | `README` | `(none)` |
| `draft.` | `draft` | `(none)` |

You cannot use `if` yet. Remember from core.02 that `a or b` gives `b` when `a` is empty, and `a and b` gives `a` when `a` is empty.
