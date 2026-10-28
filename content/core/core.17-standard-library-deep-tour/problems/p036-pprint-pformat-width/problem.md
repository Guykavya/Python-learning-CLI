# pformat: width, depth, compact and sorting

`print(big_dict)` puts everything on one long line. `pprint.pprint` prints it over several
lines; `pprint.pformat` **returns** that text instead, which is what you need for log messages,
reports and tests. A few keyword arguments control the layout:

| argument | effect |
|---|---|
| `width=80` | the line length to aim for; anything that fits stays on one line |
| `sort_dicts=True` | dict keys are **sorted** by default; `False` keeps insertion order |
| `depth=None` | how many levels of nesting to show; deeper ones become `[...]` / `{...}` |
| `compact=False` | `True` packs several short items of a long list on each line |

Write in `solution.py` (each returns a `str` and prints nothing):

1. `pretty(data, width=40)`: pformat with that width, keys in **insertion order**.
2. `pretty_sorted(data, width=40)`: pformat with that width, keys **sorted**.
3. `outline(data, depth)`: pformat showing only `depth` levels, insertion order (default width).
4. `compact_numbers(numbers, width=30)`: pformat of a list with `compact=True`.
5. `log_block(title, data, width=40)`: the line `"title:"`, then `pretty(data, width)` with
   **every** line indented by 4 spaces, joined with `"\n"` (no newline at the end).

**Example**

```python
cfg = {"name": "learn", "version": 3, "paths": ["content", "my-work", "data"],
       "db": {"file": "progress.db", "timeout": 5}}
print(pretty(cfg))
# {'name': 'learn',
#  'version': 3,
#  'paths': ['content',
#            'my-work',
#            'data'],
#  'db': {'file': 'progress.db',
#         'timeout': 5}}
outline(cfg, 1)   # "{'name': 'learn', 'version': 3, 'paths': [...], 'db': {...}}"
print(log_block("config", {"b": 1, "a": [1, 2]}))
# config:
#     {'b': 1, 'a': [1, 2]}
```
