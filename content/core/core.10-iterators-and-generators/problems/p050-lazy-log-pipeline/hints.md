## Hint 1

Start with `parse_line` only, and make it return `None` early for each rule that fails. Which
string methods help? `strip()`, `split(maxsplit=3)`, `partition(": ")`, `isdigit()`. Small helpers
`_is_date(text)` and `_is_time(text)` keep it readable. Then `parse_lines` is a three-line generator.

## Hint 2

`at_least` must raise **when called**. A function that contains `yield` runs none of its body until
the first `next()`, so the check would come too late. So: check the level, then `return` a
generator expression. To compare levels, use their positions: `LEVELS.index(level)`.

For `count_per_minute`, the key for `groupby` is `record["date"] + " " + record["time"][:5]`. A
group is an iterator, so count it with `sum(1 for _ in group)` (it has no `len`).

## Hint 3

`summarize`: one `for` loop that updates `total`, two count dicts (`by_level`, `by_source`), and
`first` / `last`. After the loop, pick the top source. For the tie rule, `min` with a key
`(-count, name)` works: the largest count gives the smallest `-count`, and on equal counts the
smaller name wins.

`first_messages`: chain the stages and cut with `islice`:

```
records = at_least(parse_lines(lines), min_level)
return ["source: message" for each r in islice(records, n)]
```
