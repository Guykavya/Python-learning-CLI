## Hint 1

All four first functions are one call to `pprint.pformat(data, ...)` with different keyword
arguments. Which one keeps the dict's own key order? (Look at the table: the default *sorts*.)

## Hint 2

For `log_block`, get the pretty text, split it into lines with `.splitlines()`, put four spaces in
front of each, and join everything with `"\n"`, starting with the title line.

## Hint 3

```
pretty:          return pformat(data, width=width, sort_dicts=False)
pretty_sorted:   return pformat(data, width=width)
outline:         return pformat(data, depth=depth, sort_dicts=False)
compact_numbers: return pformat(numbers, width=width, compact=True)
log_block:       lines = [title + ":"] + ["    " + l for l in pretty(data, width).splitlines()]
                 return "\n".join(lines)
```
