## Approach

One pattern finds every placeholder, and one function decides what each becomes.

```
\{\{  \s*  ([A-Za-z_]\w*)  \s*  \}\}
```

(without the spaces). The braces are escaped because `{` starts a repetition like `{2,3}`.
Python is lenient with a `{` that cannot be a repetition, but escaping says what you mean.

The function receives each Match:

- the name is `m.group(1)`;
- if it is in `values`, return `str(values[name])`;
- otherwise return `m.group(0)`, the whole placeholder exactly as written, so it is unchanged.

Why a function and not a replacement string? In a replacement string, `re.sub` processes
backslashes: `\1` means group 1 and `\n` a newline. A value such as `C:\new\1` would be mangled
or crash with `re.error: invalid group reference`. Text returned from a function is inserted as
it is.

`re.sub` makes a single pass over the template, so a value containing `{{ b }}` is not filled
again.

## Code

```python
import re

PLACEHOLDER_RE = re.compile(r"\{\{\s*([A-Za-z_]\w*)\s*\}\}")


def render(template: str, values: dict) -> str:
    def fill(m: re.Match) -> str:
        name = m.group(1)
        if name in values:
            return str(values[name])
        return m.group(0)

    return PLACEHOLDER_RE.sub(fill, template)
```

## Complexity

O(n + output size): one scan over the template, one dict lookup per placeholder.

## Another way

`fill` can be written with `dict.get` and a default: `return str(values.get(name, m.group(0)))`.
Careful: that also turns a stored `None` into `'None'`, which is what `str(values[name])` does
too, so here the two agree.

The standard library has `string.Template` with `$name` placeholders and `safe_substitute`,
which also leaves missing names alone. Real engines (Jinja2) add loops and filters, which a
single regex cannot handle.
