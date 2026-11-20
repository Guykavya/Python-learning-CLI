## Approach

```python
import sys

data = sys.stdin.read().split()
n = int(data[0])
out = [str(int(x) ** 2) for x in data[1:1 + n]]
sys.stdout.write("\n".join(out) + "\n")
```

The list `out` holds `n` short strings. `"\n".join(out)` builds one string in C; `write` is called once. A final `+ "\n"` makes the last line end with a newline, like `print` would.

## Complexity

`O(n)` time and memory.

## Another way

`print(*out, sep="\n")` also works and is about as fast: `print` receives the elements as arguments and writes them in one call.
