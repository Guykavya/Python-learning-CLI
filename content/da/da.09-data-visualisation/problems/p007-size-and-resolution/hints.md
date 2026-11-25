## Hint 1

`fig.savefig` picks the format from the file suffix. What do you have to check before calling it, and what type should you return?

## Hint 2

```text
path = Path(path)
if path.suffix.lower() not in {".png", ".svg"}: raise ValueError("unsupported format")
fig.savefig(path, dpi=dpi)
return path
```
