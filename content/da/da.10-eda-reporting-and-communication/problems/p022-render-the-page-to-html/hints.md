## Hint 1

Build a list of strings and `"\n".join` it at the end. Which standard-library functions escape text for HTML and turn bytes into base64 text?

## Hint 2

```text
e = html.escape
parts = ["<!doctype html>", "<html><body>", f"<h1>{e(f.headline)}</h1>", "<h3>Recommendation</h3>", "<ul>", ...]
img: b64 = base64.b64encode((Path(figures_dir) / name).read_bytes()).decode("ascii")
parts.append(f"<img src='data:image/png;base64,{b64}' alt='{e(name, quote=True)}'>")
```
