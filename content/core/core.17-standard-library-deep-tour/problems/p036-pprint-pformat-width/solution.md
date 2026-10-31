## Approach

`pformat` takes the same arguments as `pprint` but returns the text. The layout rule: if the
`repr` of a container fits in the remaining width, it stays on one line; otherwise each item goes
on its own line, aligned under the first one. `sort_dicts=False` keeps insertion order (usually
what you want for config and JSON-like data, because the order carries meaning); `depth` cuts off
deep nesting, handy for a quick overview of a huge structure; `compact=True` packs short items.

For `log_block`, indent line by line: adding four spaces only at the front of the whole string
would indent the first line only.

## Code

```python
import pprint


def pretty(data: object, width: int = 40) -> str:
    return pprint.pformat(data, width=width, sort_dicts=False)


def pretty_sorted(data: object, width: int = 40) -> str:
    return pprint.pformat(data, width=width)


def outline(data: object, depth: int) -> str:
    return pprint.pformat(data, depth=depth, sort_dicts=False)


def compact_numbers(numbers: list[int], width: int = 30) -> str:
    return pprint.pformat(numbers, width=width, compact=True)


def log_block(title: str, data: object, width: int = 40) -> str:
    lines = [title + ":"]
    for line in pretty(data, width).splitlines():
        lines.append("    " + line)
    return "\n".join(lines)
```

## Complexity

O(size of the data) for each call (pformat visits every item once, plus the work of measuring reprs).

## Another way

`textwrap.indent(pretty(data, width), "    ")` indents every line in one call. For many calls
with the same settings, make one `pprint.PrettyPrinter(width=40, sort_dicts=False)` object and
call its `.pformat(data)` method. For data that must be read by another program, use
`json.dumps(data, indent=4)` instead: pprint output is Python syntax, not JSON.
