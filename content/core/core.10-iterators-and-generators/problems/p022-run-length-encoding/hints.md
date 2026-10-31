## Hint 1

`groupby(text)` gives pairs `(key, group)`. What is `key`, and what is inside `group`?
How can you count the items in `group`? Remember that `group` is an iterator, not a list.

## Hint 2

For `decode`: what does `"a" * 3` give? How do you glue many small strings together?

## Hint 3

```
encode:
    return [(char, count of items in group) for char, group in groupby(text)]
decode:
    return "".join(char * count for char, count in pairs)
```
